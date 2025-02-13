import os
import shutil
import logging
import multiprocessing
from typing import List



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
            shutil.copy(file, dest_path)
    else:
        all_files = [
            os.path.join(config.reconstructions, file)
            for file in os.listdir(config.reconstructions)
        ]
        genre_files = [file for file in all_files if file.startswith(".xml")]
        for file in genre_files:
            dest_path = os.path.join(config.genres, os.path.basename(file))
            shutil.move(file, dest_path)

    phylomint_params = [
        "./PhyloMint/PhyloMInt",
        "-d", config.genres,
        "--outdir", config.seeds,
        "-o", "phylomint_scores.tsv",
        "--dics", "True",
        "--threads", str(config.threads)
    ]

    phylomint_cmd = " ".join(phylomint_params)
    try:
        os.system(phylomint_cmd)
    except:
        logging.warning("Something wrong with running PhyloMint!")


def hmmsearch(params: List):
    """
    Function to invoke hmmsearch software.

    params: list of parameters to be passed to the hmmsearch function.
    """
    (threshold_method, threshold, outtype, output, hmm_db, faa) = params
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

    cmd_para = [
                'prodigal', '-q',
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
