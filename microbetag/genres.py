import os
import cobra

import subprocess
import multiprocessing
from pathlib import Path


from .utils import (
    split_list,
    run_until_done,
    file_exists_and_nonzero,
    get_tool_location,
    mtg_logger,
)

_logger_ = mtg_logger(__name__)

_MSGENRE_SCRIPT_ = Path(os.path.abspath(__file__)).parent.joinpath("msgenre.py")

class GEMSReconstruction:
    """
    Class for Genome Scale Metabolic Network Reconstruction (GENRE).
    It makes use of either ModelSEEDpy or CarvMe, two well established methods for building GENRES.

    Args:
        config: Instance of the :class:`Config` class.

    - `threads`
    - `bin_filenames`
    - `bins_path`
    - `reconstructions`
    - `sc_input_type`
    - `for_reconstructions`
    - `genres`
    - `gapfill_model`
    - `gapfill_media`

    Note:
       CarveMe:

       Machado D, Andrejev S, Tramontano M, Patil KR. 
       Fast automated reconstruction of genome-scale metabolic models for microbial species and communities. 
       Nucleic acids research. 2018 Sep 6;46(15):7542-53. DOI: https://doi.org/10.1093/nar/gky537

       ModelSEEDpy:

       Faria JP, Liu F, Edirisinghe JN, Gupta N, Seaver SM, Freiburger AP, Zhang Q, Weisenhorn P, Conrad N, Zarecki R, Song HS. 
       ModelSEED v2: High-throughput genome-scale metabolic model reconstruction with enhanced energy biosynthesis pathway prediction. 
       bioRxiv. 2023 Oct 6:2023-10. DOI: https://doi.org/10.1101/2023.10.04.556561 

       Henry CS, DeJongh M, Best AA, Frybarger PM, Linsay B, Stevens RL. 
       High-throughput generation, optimization and analysis of genome-scale metabolic models. 
       Nature biotechnology. 2010 Sep;28(9):977-82. DOI: https://doi.org/10.1038/nbt.1672 

    """

    def __init__(self, config):
        self.config = config

    def rast_annotate_genomes(self):
        """
        Pool for running rast annotations for a list of bins
        """
        if len(self.config.bin_filenames) > self.config.threads:
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

            _logger_.info(
                "We now have annotated %s genomes out of the %s"
                % (counter, len(self.config.bin_filenames))
            )

    def rast_annotate_a_genome(self, bin_filename):
        """
        RAST annotate a user's bin based on:
        https://www.bv-brc.org/docs/cli_tutorial/rasttk_getting_started.html#the-concept-of-the-genome-typed-object
        """
        bin_file     = os.path.join(self.config.bins_path, bin_filename)
        name, _      = os.path.splitext(bin_filename)
        genome       = name
        gto_filename = os.path.join(
            self.config.reconstructions, "".join([name, ".gto"])
        )

        # rast_create_genome_command: create a GTO for the bin's contig
        rast_create_genome_command = " ".join(
            [
                "rast-create-genome",
                "--scientific-name",
                name,
                "--genetic-code",
                "11",
                "--domain",
                "Bacteria",
                "--contigs",
                bin_file,
                "--genome-id",
                genome,
                ">",
                gto_filename,
            ]
        )
        if not file_exists_and_nonzero(gto_filename):
            rast_create_genome_command = "".join(
                ["\\:" if char == ":" else char for char in rast_create_genome_command]
            )
            _logger_.info("rast_create_genome_command: %s", rast_create_genome_command)
            run_until_done(rast_create_genome_command)

        # rast-process-genome: run the default RASTtk pipeline tool
        gto_filename_2 = "".join([gto_filename, "_2"])
        rast_process_genome_command = " ".join(
            ["rast-process-genome", "<", gto_filename, ">", gto_filename_2]
        )
        if not file_exists_and_nonzero(gto_filename_2):
            rast_process_genome_command = "".join(
                ["\\:" if char == ":" else char for char in rast_process_genome_command]
            )
            _logger_.info("rast_process_genome_command: %s", rast_process_genome_command)
            run_until_done(rast_process_genome_command)

        # rast-export-genome protein_fasta: export the genome in a desired format
        faa_filename = "".join([gto_filename[:-4], ".faa"])
        rast_export_genome_command = " ".join(
            [
                "rast-export-genome",
                "protein_fasta",
                "<",
                gto_filename_2,
                ">",
                faa_filename,
            ]
        )
        if not file_exists_and_nonzero(faa_filename):
            rast_export_genome_command = "".join(
                ["\\:" if char == ":" else char for char in rast_export_genome_command]
            )
            _logger_.info("rast_export_genome_command: %s", rast_export_genome_command)
            run_until_done(rast_export_genome_command)

    def modelseed_reconstructions(self):
        """
        Pool for running GENREs reconstruction using the final .faa files from the
        rast_annotate_genomes() function

        Note:
            Currently is not being as the RAST server seems not that stable to have several queries.
        """
        # Make sure of the scikit version being used
        if self.config.sc_input_type == "proteins_faa":
            faa_files = [
                os.path.join(self.config.for_reconstructions, file)
                for file in os.listdir(self.config.for_reconstructions)
                if file.endswith(".faa")
            ]
        else:
            faa_files = [
                os.path.join(self.config.reconstructions, file)
                for file in os.listdir(self.config.reconstructions)
                if file.endswith(".faa")
            ]

        _logger_.info(faa_files)

        for faa_file in faa_files:

            draft_genre = ms_reconstruct(faa_file, self.config.genres)

            if self.config.gapfill_model:

                dnngior_gapfill(
                    draft_genre,
                    outdir = self.config.genres,
                    medium = self.config.gapfill_media
                )

    def carve_reconstructions(self):
        """
        Reconstruct a GENRE using CarveMe and a .faa as input.
        You can get such a file after running RAST annotation or after any gene prediction tool such as Prodigal, FragenScan etc.
        """
        if self.config.sc_input_type == "bins_fasta":

            gene_predictor_path = (
                self.config.prodigal
                if self.config.gene_predictor == "prodigal"
                else self.config.reconstructions
            )

            faa_files = [
                os.path.join(gene_predictor_path, tfile)
                for tfile in os.listdir(gene_predictor_path)
                if tfile.endswith(".faa")
            ]

            run_carve(
                faa_files,
                output_dir=self.config.genres
            )

        elif self.config.sc_input_type in ["coding_regions", "proteins_faa"]:

            faa_files = [
                os.path.join(self.config.for_reconstructions, file)
                for file in os.listdir(self.config.for_reconstructions)
            ]

            run_carve(
                faa_files,
                output_dir=self.config.genres,
                dna=self.config.sc_input_type == "coding_regions"
            )

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
                _logger_.info(f"Bin {bin_filename} is being annotated using FGS.")
                fgs_params = [
                    FGS,
                    "-s",
                    bin_file,
                    "-o",
                    faa,
                    "-w",
                    "1",
                    "-p",
                    str(self.config.threads),
                    "-t",
                    COMPLETE,
                ]
                try:
                    _ = subprocess.run(
                        fgs_params, capture_output=True, text=True, check=True
                    )
                except subprocess.CalledProcessError as e:
                    _logger_.error(
                        f"FGS annotation failed for {bin_filename}. Error:\n{e.stderr}"
                    )

        os.chdir(cwd)


def ms_reconstruct(faa, outdir = None):
    """
    Running ModelSEEDpy on its own conda environment
    """
    faa_path  = Path(faa)
    outdir    = Path(outdir) if outdir else faa_path.parent
    modelId   = faa_path.stem
    modelname = ".".join([modelId, "draft.xml"])
    modelfile = os.path.join(outdir, modelname)

    if not os.path.exists(modelfile):

        subprocess.run([
            "conda",
            "run",
            "-n", "mtg-modelseed",
            "python", _MSGENRE_SCRIPT_,
            "--reconstruct",
            "--faa", faa,
            "--outdir", outdir
        ])

    return modelfile


def dnngior_gapfill(draft_model, medium=None, outdir=None):
    """
    draft_model: Path to draft .xml
    medium: path to tab-separated file .tsv
    """

    if not os.path.exists(str(draft_model).replace(".draft", "")):

        # _MSGENRE_SCRIPT_ is a Path object; this would
        command = [
            "conda",
            "run",
            "-n", "mtg-dnngior",
            "python", str(_MSGENRE_SCRIPT_),
            "--gapfill",
            "--draft-model", draft_model,
            "--outdir", outdir,
        ]

        if medium is not None:
            command += ["--medium", medium]

        subprocess.run(command)


def run_carve(faa_files, output_dir, dna=False):
    """
    Build a GEM using carveme for a list of
    """
    for faa in faa_files:
        bin_id = os.path.splitext(os.path.basename(faa))[0]
        xml = os.path.join(output_dir, f"{bin_id}.xml")
        carve_params = ["carve", "--solver", "gurobi", "-o", xml]
        if os.path.exists(xml) and os.path.getsize(xml) > 0:
            _logger_.info(
                f"""A GEM (.xml) based on {faa} is already available to be used for seed complementarities; carve step will be skiped."""
            )
            continue
        if dna:
            carve_params.append("--dna")
        carve_params.append(faa)
        carve_command = " ".join(carve_params)

        os.system(carve_command)
