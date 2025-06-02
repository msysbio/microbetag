import os
from typing import TYPE_CHECKING

from .tools import (
    run_prodigal,
    kegg_annotation,
)

from .utils import (
    mtg_logger,
    merge_ko,
    bin_kos_to_file,
    ko_list_parser,
)
from .genres import GEMSReconstruction

if TYPE_CHECKING:
    from .config import Config


_logger_ = mtg_logger(__name__)


def run_otf_prodigal(config: "Config"):
    """
    Wrappper function for running Prodigal.
    """

    if config.bin_filenames is None:
        _logger_.error(
            "Bin files have not been provided."
            "Please set the path to the directory with your bins/MAGs to the `bins_fasta` parameter of"
            "the configuration YAML file."
        )

    for bin_fa in config.bin_filenames:

        bin_filename = os.path.basename(bin_fa)

        bin_id, _ = os.path.splitext(bin_filename)
        bin_id = bin_id.split("/")[-1]

        bin_fa = os.path.join(config.bins_path, bin_fa)

        _logger_.info(f"Running Prodigal for {bin_id}")
        # TODO: check if bin_id is actually only the basename of the whole path until extension

        run_prodigal(bin_fa, bin_id, config.prodigal)


def run_kegg_annotate(config: "Config"):
    """
    Wrapper for the tools.kegg_annotation() for each genome/MAG and the utils.merge_ko().
    """
    ko_list = os.path.join(config.kegg_db_dir, "ko_list")
    ko_dic = ko_list_parser(ko_list)

    hmmout_dir = config.kegg_pieces_dir
    config.ko_merged = os.path.join(config.kegg_annotations, "ko_merged.txt")

    for bn in config.bin_filenames:
        bin_id, _   = os.path.splitext(bn)
        bin_kos_dir = os.path.join(hmmout_dir, bin_id)
        os.makedirs(bin_kos_dir, exist_ok=True)

        for afile in os.listdir(bin_kos_dir):
            if afile.endswith(".hmmout.all"):
                continue

        for bn in config.bin_filenames:

            faa = os.path.join(config.prodigal, bin_id + ".faa")

            # A folder with KO predictions (a single hmmout file for each KO) per bin
            check = kegg_annotation(
                faa, bin_id, config.kegg_pieces_dir, config.kegg_db_dir, ko_dic, config.threads,
            )

            # Out of the 24K hmmout files, make a single one with the predictions as backup
            # and one with the 3-columns
            if check:
                bin_kos_to_file(hmmout_dir=bin_kos_dir, bin_id=bin_id)

    # Make the 3-columns files with all bins and their KOs
    merge_ko(config.kegg_pieces_dir, config.ko_merged)


def build_genres(config: "Config"):
    """
    Wrapper function for GENREs in a microbetag pipeline run.
    """
    # Init reconstruction class
    build_genres = GEMSReconstruction(config)

    # Annotate step
    if config.sc_input_type == "bins_fasta":

        if config.genre_reconstruction_with == "modelseedpy":
            build_genres.rast_annotate_genomes()  # saves under config.reconstructions

        elif config.gene_predictor == "prodigal":
            _logger_.info(
                "DiTing .faa files will be used"
            )  # go to the .faa case, i.e., the ORFs/

        elif config.gene_predictor == "fragGeneScan":
            _logger_.info("Get annotations with FragGeneScan.")
            build_genres.fgs_annotate_genomes()  # saves under config.reconstructions

    elif config.sc_input_type == "coding_regions":
        _logger_.info("CarveMe will be used with the users .ffn-like files.")

    else:
        _logger_.warning(
            f"The combination of gene_predictor: {config.gene_predictor} \
            \nand genre_reconstruction_with: {config.genre_reconstruction_with}, are not supported"
        )

    # Reconstruct step
    if config.genre_reconstruction_with == "modelseedpy":
        _logger_.info("Build draft reconstructions with ModelSEEDpy")
        build_genres.modelseed_reconstructions()

    elif config.genre_reconstruction_with == "carveme":
        _logger_.info("Build draft reconstructions with carveme")
        build_genres.carve_reconstructions()

    else:
        _logger_.info("User models to be used for the seed complementarity step.")
