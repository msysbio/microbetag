import os
import time
import cobra
import random
import logging
import subprocess
import multiprocessing

from .utils import split_list, run_until_done, file_exists_and_nonzero, get_library_version, get_tool_location


class GEMSReconstruction():
    """
    Class to first RAST annotate and the build Genome Scale Metabolic Reconstructions
    using modelseedpy
    """
    def __init__(self, config):
        self.config = config

    def rast_annotate_genomes(self):
        """
        Pool for running rast annotations for a list of bins
        """
        if  len(self.config.bin_filenames) > self.config.threads:
            chunk_size = self.config.threads
            bin_chunks = split_list(self.config.bin_filenames, chunk_size)
        else:
            chunk_size = len(self.config.bin_filenames)
            bin_chunks = [self.config.bin_filenames]

        self.chunk_size = chunk_size

        counter = 0
        for chunk in bin_chunks:
            pool = multiprocessing.Pool(self.config.threads)
            pool.map(self.rast_annotate_a_genome, chunk)
            pool.close()
            pool.join()
            counter += chunk_size
            logging.info(
                "We now have annotated %s genomes out of the %s" % (counter, len(self.config.bin_filenames))
            )

    def rast_annotate_a_genome(self, bin_filename):
        """
        RAST annotate a user's bin based on:
        https://www.bv-brc.org/docs/cli_tutorial/rasttk_getting_started.html#the-concept-of-the-genome-typed-object
        """
        bin_file = os.path.join(self.config.bins_path, bin_filename)
        name, _ = os.path.splitext(bin_filename)
        genome = name
        gto_filename = os.path.join(self.config.reconstructions, "".join([name, ".gto"]))

        # rast_create_genome_command: create a GTO for the bin's contig
        rast_create_genome_command = " ".join([
            "rast-create-genome", "--scientific-name", name,
            "--genetic-code", "11", "--domain", "Bacteria",
            "--contigs", bin_file,
            "--genome-id", genome, ">", gto_filename
            ])
        if not file_exists_and_nonzero(gto_filename):
            rast_create_genome_command = ''.join(['\\:' if char == ':' else char for char in rast_create_genome_command])
            logging.info("rast_create_genome_command: %s", rast_create_genome_command)
            run_until_done(rast_create_genome_command)

        # rast-process-genome: run the default RASTtk pipeline tool
        gto_filename_2 = "".join([gto_filename, "_2"])
        rast_process_genome_command = " ".join([
            "rast-process-genome", "<", gto_filename, ">", gto_filename_2
            ])
        if not file_exists_and_nonzero(gto_filename_2):
            rast_process_genome_command = ''.join(['\\:' if char == ':' else char for char in rast_process_genome_command])
            logging.info("rast_process_genome_command: %s", rast_process_genome_command)
            run_until_done(rast_process_genome_command)

        # rast-export-genome protein_fasta: export the genome in a desired format
        faa_filename = "".join([gto_filename[:-4], ".faa"])
        rast_export_genome_command = " ".join([
            "rast-export-genome",
            "protein_fasta",
            "<", gto_filename_2, ">",
            faa_filename
            ])
        if not file_exists_and_nonzero(faa_filename):
            rast_export_genome_command = ''.join(['\\:' if char == ':' else char for char in rast_export_genome_command])
            logging.info("rast_export_genome_command: %s", rast_export_genome_command)
            run_until_done(rast_export_genome_command)

    def modelseed_reconstructions(self):
        """
        Pool for running GENREs reconstruction using the final .faa files from the
        rast_annotate_genomes() function
        [NOTE] Not to be used for now as the RAST server seems not that stable to have several queries..
        """
        # Make sure of the scikit version being used
        if self.config.input_for_recon_type == "proteins_faa":
            faa_files = [
                os.path.join(self.config.for_reconstructions, file)
                for file in os.listdir(self.config.for_reconstructions)
            ]
        else:
            faa_files = [file
                        for file in os.listdir(self.config.reconstructions)
                        if file.endswith(".faa")
                        ]
        if get_library_version("scikit-learn") != "0.24.2":
            os.system("python3 -m pip install scikit-learn==0.24.2")
        for faa_file in faa_files:
            self.reconstruct_a_model(faa_file)

    def reconstruct_a_model(self, annotation_faa):
        """
        Build a Genome Scale reconstruction using ModelSEEDpy and the BIN annotations
        """
        # ModelSEED using the default b.f and complete medium, gapfill with the default algo
        model_id, _ = os.path.splitext(annotation_faa.split("/")[-1])
        annotation_faa_path = os.path.join(self.config.reconstructions, annotation_faa)
        model_filename =  os.path.join(self.config.genres, "".join([model_id, ".xml"]))
        if os.path.exists(model_filename):
            return 1
        logging.info("Model to be reconstructed: %s", model_id)
        model = self.recursive_build(model_id, annotation_faa_path)
        cobra.io.write_sbml_model(cobra_model = model, filename = model_filename)

    def recursive_build(self, model_id, annotation_faa_path, counter=0):
        """
        RAST server usually has issues that lead to fail attempts.
        This recursive function allows the build_metabolic_model() to be performed until the server responses.

        [NOTE] We have observed that when MSGenome is initiated in the same function with the MSBuilder, they behave much better!
        """

        from modelseedpy import MSBuilder, MSGenome
        if counter >= 20:

            # Run the script again with the given arguments   -- TODO:   THIS IS A BIT EXTREME...
            fire_microbetag(yaml_file=self.config.yaml_file)

        counter += 1
        try:
            msgenome = MSGenome.from_fasta(annotation_faa_path, split=' ')
            model = MSBuilder.build_metabolic_model(
                model_id = model_id,
                genome = msgenome,
                index = "0",
                gapfill_model = self.config.gapfill_model,
                gapfill_media = None,
                annotate_with_rast = True,
                allow_all_non_grp_reactions = True
            )
            return model
        except:
            time.sleep(random.randint(1, 20))
            logging.info("Recursive run for model_id: %s", model_id)
            return self.recursive_build(model_id, annotation_faa_path, counter)

    def carve_reconstructions(self):
        """
        Reconstruct a GENRE using CarveMe and a .faa as input.
        You can get such a file after running RAST annotation or after any gene prediction tool such as Prodigal, FragenScan etc.
        """
        if self.config.input_for_recon_type == "bins_fasta":

            gene_predictor_path = self.config.prodigal if self.config.gene_predictor == "prodigal" else self.config.reconstructions
            print(gene_predictor_path)
            faa_files = [
                os.path.join(gene_predictor_path, tfile)
                for tfile in os.listdir(gene_predictor_path)
                if tfile.endswith(".faa")
            ]
            logging.info(faa_files)
            self.run_carve(faa_files)

        elif self.config.input_for_recon_type in ["coding_regions", "proteins_faa"]:
            faa_files = [
                os.path.join(self.config.for_reconstructions, file)
                for file in os.listdir(self.config.for_reconstructions)
            ]
            self.run_carve(faa_files, dna=self.config.input_for_recon_type == "coding_regions")

    def run_carve(self, faa_files, dna=False):
        """
        Build a GEM using carveme for a list of
        """
        for faa in faa_files:
            bin_id = os.path.splitext(os.path.basename(faa))[0]
            xml = os.path.join(self.config.genres, f"{bin_id}.xml")
            carve_params = ["carve", "--solver", "gurobi", "-o", xml]
            if os.path.exists(xml) and os.path.getsize(xml) > 0:
                logging.info("""
                An .xml file for this bin is already available.
                This will be used for seed complementarities and carve step will be skiped."""
                )
                continue
            if dna:
                carve_params.append("--dna")
            carve_params.append(faa)
            carve_command = " ".join(carve_params)

            os.system(carve_command)

    def fgs_annotate_genomes(self):
        """
        Use FragGeneScan to get .faa files.
        """
        cwd = os.getcwd()
        if self.config.mount is not None:
            FGS = "/opt/FragGeneScan/FragGeneScan"
        else:
            FGS = get_tool_location("FragGeneScan")
        COMPLETE = "complete"
        for bin_filename in self.config.bin_filenames:
            bin_file = os.path.join(self.config.bins_path, bin_filename)
            bin_id, _ = os.path.splitext(bin_filename)
            faa = os.path.join(self.config.reconstructions, bin_id)
            if not file_exists_and_nonzero(faa):
                logging.info(f"Bin {bin_filename} is being annotated using FGS.")
                fgs_params = [
                    FGS,
                    "-s",  bin_file,
                    " -o", faa,
                    "-w  1",
                    "-p", str(self.config.threads),
                    "-t", COMPLETE
                ]
                fgs_command = " ".join(fgs_params)
                os.system(fgs_command)
        os.chdir(cwd)


def fire_microbetag(yaml_file):
    import sys
    logging.warning(
        """
        \n\n******
        microbetag kept calling the recursive function for building modelseedpy GEM.
        This function tries to establish a connection with the RAST server that at the moment does not allow it.
        microbetag will exit and restart its execution with the exact same settings.
        Since previous steps are alredy complete, they will be skipped.
        ******\n\n
        """
    )
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    script_path = os.path.join(root_dir, "microbetag.py")
    subprocess.run([sys.executable, script_path, yaml_file])


