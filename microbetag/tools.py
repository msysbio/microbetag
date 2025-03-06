import os, sys
import glob
import shutil
import logging
import subprocess
import multiprocessing
from typing import List

from .utils import (
    get_files_with_suffixes, get_library_version, get_tool_location,
    ensure_flashweave_format, ensure_same_namespace_after_fw
)



def run_phylomint(config):
    """
    Invoke PhyloMInt as edited from microbetag team to support parallel calculation of the seed and non seed sets
    and save corresponding sets to json files.
    """
    if config.users_models:
        genre_files = [
            os.path.join(config.for_reconstructions, file)
                for file in os.listdir(config.for_reconstructions)
        ]
        for file in genre_files:
            dest_path = os.path.join(config.genres, os.path.basename(file))
            try:
                shutil.copy(file, dest_path)
            except:
                pass
    else:
        all_files = [
            os.path.join(config.reconstructions, file)
            for file in os.listdir(config.reconstructions)
        ]
        genre_files = [file for file in all_files if file.startswith(".xml")]
        for file in genre_files:
            dest_path = os.path.join(config.genres, os.path.basename(file))
            shutil.move(file, dest_path)

    PHYLOMINT = os.path.join(
        os.path.dirname(__file__), "PhyloMint/PhyloMInt"
    )

    phylomint_params = [
        PHYLOMINT,  # "./PhyloMint/PhyloMInt",
        "-d", config.genres,
        "--outdir", config.seeds,
        "-o", "phylomint_scores.tsv",
        "--dics", "True",
        "--threads", str(config.threads)
    ]

    phylomint_cmd = " ".join(phylomint_params)
    print(phylomint_cmd)
    try:
        os.system(phylomint_cmd)
    except:
        logging.warning("Something wrong with running PhyloMint!")


def hmmsearch(params: List):
    """
    Function to invoke hmmsearch software.

    params: list of parameters to be passed to the hmmsearch function.
    """
    (
        threshold_method, threshold, outtype, output, hmm_db, faa
    ) = params

    cmd_para = [
        'hmmsearch',
        threshold_method, threshold,
        '--cpu', '1',
        '-o /dev/null',
        outtype, output,
        hmm_db,
        faa
    ]

    cmd = ' '.join(cmd_para)

    try:
        os.system(cmd)
    except:
        logging.warning("Something wrong with KEGG hmmsearch!")


def run_prodigal(fasta, basename, outdir):
    """
    Function to predict ORFs using Prodigal.
    By default outdir is the ORFs folder
    fna	FASTA nucleic acid	Used generically to specify nucleic acids
    ffn	FASTA nucleotide of gene regions	Contains coding regions for a genome
    """

    faa_file = os.path.join(outdir, basename + '.faa')
    ffn_file = os.path.join(outdir, basename + '.ffn')
    fna_file = os.path.join(outdir, basename + '.fna')
    gbk_file = os.path.join(outdir, basename + '.gbk')

    PRODIGAL = get_tool_location("prodigal")
    cmd_para = [
                PRODIGAL, '-q',
                '-i', fasta,
                '-p', 'meta',
                '-a', faa_file,
                '-d', ffn_file,
                '-o', gbk_file
                ]
    cmd = ' '.join(cmd_para)
    if os.path.exists(faa_file) or os.path.exists(fna_file) or os.path.exists(ffn_file):
        logging.info("ORFs already predicted for bin: %s", basename)
    else:
        logging.info("ORFs to be predicted for bin: %s", basename)
        try:
            os.system(cmd)
            print("ok. ")
        except:
            logging.warning("Something wrong with prodigal annotation!")


def kegg_annotation(faa, basename, out_dir, db_dir, ko_dic, threads):
    """
    Function to perform KEGG annotation.
    The function invokes hmmsearch.

    Inputs:
        faa (str): Path to the .faa file of the bin in process
        basename (str): Bin id
        out_dir (str): Path to output directory where .hmmout files will be stored
        db_dir (str): Path to KEGG database directory
        ko_dic (Dict):
        threads (int): Number of threads to be used
    """
    logging.info('KEGG annotation for %s', basename)
    params = []

    if not os.path.exists(faa):
        logging.warn(f"A .faa file for {basename} is not availavle. microbetag will skip it.")
        return False

    for knum, info in ko_dic.items():

        # Check if hmmout for particular KO of a certain bin is already there
        hmmout_filename = ".".join([knum, str(basename), 'hmmout'])
        output = os.path.join(out_dir, basename, hmmout_filename)
        if os.path.exists(output):
            continue

        # Get hmm for KO under consideration
        hmm_db = os.path.join(db_dir, 'profiles', knum + '.hmm')
        if not os.path.exists(hmm_db):
            continue

        # Set params for hmmsearch based on the ko_list annotation
        if info[1] == 'full':
            threshold_method = '-T'
            outtype = '--tblout'

        elif info[1] == 'domain':
            threshold_method = '--domT'
            outtype = '--domtblout'

        elif info[1] == 'custom':
            threshold_method = '-E'
            outtype = '--tblout'

        params.append((threshold_method, info[0], outtype, output, hmm_db, faa))

    logging.info("Number of KEGG processes to be performed: %s", str(len(params)))
    process = multiprocessing.Pool(threads)
    process.map(hmmsearch, params)

    return True


def phenotrex_genotype(config):
    """
    Get COGs present in your genomes
    """

    if not os.path.exists(config.genotypes_file):

        logging.info("Get phenotrex predictions")
        suffixes = [".fa", ".fasta", ".gz"]
        bin_files = get_files_with_suffixes(config.bins_path, suffixes)
        bin_files_in_a_row = " ".join(bin_files)

        # Build genotypes
        compute_genotype_params = []
        if config.cwd != "/microbetag":
            compute_genotype_params += ["conda run -n phendb"]

        compute_genotype_params += [
            "phenotrex",
            "compute-genotype",
            "--out",
            config.genotypes_file,
            "--threads",
            str(config.threads),
            bin_files_in_a_row
        ]
        # Container - case
        if config.cwd == "/microbetag":

            sk_init_version = get_library_version("scikit-learn")
            pheno_init_version = get_library_version("phenotrex")

            sk_required_version = "1.3.2"
            if sk_init_version != sk_required_version:
                # os.system("python3 -m pip install scikit-learn==1.3.2")
                get_sklearn_v = "==".join(["scikit-learn", sk_required_version])
                subprocess.run([sys.executable, "-m", "pip", "install", get_sklearn_v])

            pheno_required_version = "0.6.0"
            if pheno_init_version != pheno_required_version:
                get_pheno_v = "==".join(["phenotrex[fasta]", pheno_required_version])
                subprocess.run([sys.executable, "-m", "pip", "install", get_pheno_v])

            # Run the command
            compute_genotype_command = " ".join(compute_genotype_params)
            if os.system(compute_genotype_command) != 0:
                logging.info("Try phenotrex genotype for the second time.")
                if os.system(compute_genotype_command) != 0:
                    logging.error("asda")
                    sys.exit(0)
        # Local case
        else:
            compute_genotype_command = " ".join(compute_genotype_params)
            try:
                subprocess.run(compute_genotype_command, shell=True, check=True)
            except Exception as e:
                logging.error(e)
                sys.exit(1)


def phenotrex_predict(config):
    """
    """
    import subprocess
    # Get predictions
    phen_models = [os.path.join(config.phen_classes, model) for model in os.listdir(config.phen_classes)]

    # Parse through the phen models (classes)
    for model in phen_models:
        model_name =  os.path.basename(model)
        model_predictions_output = "".join([
            config.predictions_path, "/", model_name[:-4], ".prediction.tsv"
        ])

        # Skip if predictions already computed
        if os.path.exists(model_predictions_output):
            logging.info("Predictions already exist for model: %s", model_name)

        else:

            predict_traits_params = []
            # Local case
            if config.cwd != "/microbetag":
                predict_traits_params = ["conda run -n phendb"]
            # All cases: local and container
            predict_traits_params += [
                "phenotrex",
                "predict",
                "--genotype",
                config.genotypes_file,
                "--classifier",
                model,
                "--min_proba",
                str(config.min_proba),
                "--verb >",
                model_predictions_output
            ]

            predict_trait_command = " ".join(predict_traits_params)

            try:
                subprocess.run(predict_trait_command, shell=True, check=True)

            except subprocess.CalledProcessError as e:
                logging.warn(f"Command execution failed with return code {e}")

    # If no predictions file is present for any classes, probably something went off.
    if not any(glob.glob(os.path.join(config.predictions_path, "*.prediction.tsv"))):
        logging.error("No prediction was able to be retrieved with phenotrex. Check your input files.")
        sys.exit(0)

    # IN CASE OF CONTAINER CONSIDER..
    # if sk_init_version != sk_required_version:
    #     cmd = "".join(["python3 -m pip install scikit-learn==", sk_init_version])
    #     os.system(cmd)


def run_manta(config):
    import time
    # Build the manta command
    logging.info("Running manta clustering algorithm.")
    manta_output_file = "/".join([config.output_dir, 'manta_annotated'])
    manta_params = [
        "manta",
        "-i", config.base_network_file,
        "-f", "cyjs",
        "-o", manta_output_file,
        "--layout"
    ]
    manta_command = " ".join(manta_params)

    # Run manta
    try:
        m1 = time.time()
        if os.system(manta_command) != 0:
            e = """\
                The manta clustering algorithm failed.
                Most likely this is because clusters could not be grouped based on the provided network and the parameters setup of manta.
                Yet, microbetag will continue to the following steps without considering for clusters.
            """
            logging.warning(e)
            # Changed cfg so the buld_cx_annotated_graph function will not fail.
            config.network_clustering = False
        else:
            logging.info("""manta ran fine.""")
        m2 = time.time()
        time = " ".join(["Network clustering with manta took:", str(m2 - m1), "sec"])
        logging.info(time)

    except Exception as e:
        logging.warning(e)
        config.network_clustering = False


def run_flashweave(config):

    # Checking for format support.
    ensure_flashweave_format(conf=config)

    # Run FlashWeave
    from julia.api import Julia
    logging.info("Fix FlashWeave arguments from config.")
    pair_args = set()
    for arg, values in config.flashweave_args.items():
        if values["required"]:
            if isinstance(values["value"], bool):
                pair_args.add( ( arg, str(values["value"]).lower()) )
            else:
                logging.error(f'You need to provide values for "{arg}" argument of FlashWeave.') ; sys.exit(0)
        else:
            if values["value"] is not None:
                if values["type"] == "Bool":
                    pair_args.add( (arg, str(values["value"]).lower()) )
                else:
                    pair_args.add( (arg, values["value"]) )

    pair_args.add(("transposed", "true"))
    learn_in = ",".join(f"{arg[0]}={arg[1]}" for arg in pair_args)

    logging.info("Init Julia through Python")
    jl = Julia(compiled_modules=False)
    jl.using("FlashWeave")

    # Run FlashWeave based on presence/absence of a metadata file
    if config.metadata_file:
        logging.info("Running FlashWeaeve along with a metadata file.")
        logging.info(
            f'save_network("{config.network}", learn_network("{config.flashweave_abd_table}", "{config.metadata_file}", {learn_in}))'
        )
        jl.eval(f'save_network("{config.network}", learn_network("{config.flashweave_abd_table}", "{config.metadata_file}", {learn_in}))')
    else:
        logging.info("Running FlashWeaeve.")
        logging.info(
            f'save_network("{config.network}", learn_network("{config.flashweave_abd_table}", {learn_in}))'
        )
        jl.eval(f'save_network("{config.network}", learn_network("{config.flashweave_abd_table}", {learn_in}))')

    ensure_same_namespace_after_fw(config)


def run_faprotax(config):
    """ Run FAPROTAX collapse_table.py script """
    faprotax_params = [
        "python3", config.faprotax_script,
        "-i", config.abundance_table,
        "-o", config.faprotax_funct_table,
        "-g", config.faprotax_txt,
        "-c", '"' + "#" + '"',
        "-d", '"' + config.taxonomy_column_name + '"',
        "-v",
        "--force",
        "-s", config.faprotax_sub_tables,
    ]
    faprotax_command = " ".join(faprotax_params)
    try:
        process = subprocess.Popen(faprotax_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
    except:
        raise TypeError(f"Something went wrong when running FAPROTAX with your abuandance table: {config.abundance_table}")
