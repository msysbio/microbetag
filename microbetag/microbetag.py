"""
Aim:
    Perform the microbetag () approach annotating user's bins instead of mapping taxonomies against the
    microbetagDB representative genomes.

Input:
    - A folder with .fasta files of the corresponding bins
    - The abundance table of the bins across the samples
    - (optional) a co-occurrence network in a three-columns format

Output:
    - An annotated network in .cx2 format
"""

import os
import sys
import yaml
import argparse

from .utils import (
    mtg_logger,
    load_merged_ko_file,
)
from .tools import (
    run_flashweave,
    run_faprotax,
    phenotrex_genotype,
    phenotrex_predict,
    run_seed_complementarity,
    run_manta,
)

from .wrappers import (
    build_genres,
    run_kegg_annotate,
    run_otf_prodigal,
)

from .config import Config

from .build_mtg_cx2 import mtg_annotate_network
from .helpers import manta_input_net

from .pathway_complementarity import export_pathway_complementarities


logger = mtg_logger(__name__)


def run_microbetag(config: Config):
    """
    Main function for running the microbetag workflow.
    Based on the Config provided, it will apply several pre-calculation and/or annotation steps.

    Returns:
        mtg_net: A microbetag-annotated network in CX2 format. CX2 is a JSON-based format, so it is
                easy to use for the response of the on-the-fly version to the query from MGG.
    Note:
        The mtg_net returned, is also saved as a .cx2 file in the output_directory using a timestamp
        on its filename, e.g. mtag_net_2025-05-08_17-47.cx2.
    """

    if config.onthefly or config.api:

        from . import db
        from .helpers import otf_seqid_ncbi_gtdb_map

        db.DB_CREDENTIALS = config.db_config

        # onthefly confing brings the db credentials on it

    # ----------------
    # Build network if not available
    # ----------------
    if config.precalc_only:

        logger.info(
            "microbetag is about to perform the precalculations for your list of bins/MAGs only."
            "No network will be built."
        )

    elif not os.path.exists(config.network) or os.path.getsize(config.network) == 0:

        logger.info(
            "[STEP] NETWORK INFERENCE WITH FLASHWEAVE. "
            "Using the abundance table provided, microbetag is about to build a co-occurrence network.\n"
        )

        run_flashweave(config)

    # ----------------
    # FAPROTAX
    # ----------------
    if config.abundance_table is not None and config.faprotax:

        logger.info("[STEP] LITERATURE ANNOTATION WITH FAPROTAX")

        try:

            run_faprotax(config)

        except Exception:

            error_msg = "FAPROTAX failed."
            logger.error(error_msg)
            raise RuntimeError(error_msg)

    # ----------------
    # phen annotations
    # ----------------
    if config.phen_traits:

        logger.info("[STEP] PREDICTING PHENOTYPIC TRAITS")

        if config.bins_ids is not None and not config.onthefly:

            try:

                phenotrex_genotype(config)
                phenotrex_predict(config)

            except Exception:

                error_msg = "Running phenotrex on your genomes/bins failed."
                logger.error(error_msg)
                raise RuntimeError(error_msg)

        elif config.onthefly:

            try:

                # get_phen_traits(config.repr_genomes_present, config.predictions_path)
                t = db.GetPhenotrexTraits(config)
                t.get_phen_traits()

            except Exception:

                error_msg = (
                    "Phenotypic traits for the genomes under study failed to be exported from microbetagDB."
                )
                logger.error(error_msg)
                raise RuntimeError(error_msg)

    # ----------------
    # Prodigal - ORF prediction
    # ----------------
    if (
        config.path_compl or config.seed_compl
    ) and not config.onthefly:

        if (
            config.ko_merged is None and
            len(os.listdir(config.prodigal)) != len(config.bins_ids)
        ):

            logger.info("[INTERMEDIATE STEP] PREDICTING ORFs WITH PRODIGAL THROUGH DiTing")

            try:

                run_otf_prodigal(config)

            except Exception:

                error_msg = "Prodigal failed to run on your genomes/bins."
                logger.error(error_msg)
                raise RuntimeError(error_msg)

    # ----------------
    # Maps required for otf in case of complementaritites
    # ----------------
    if (config.path_compl or config.seed_compl) and config.onthefly:

        (
            config.pairs_of_interest,
            config.relative_genomes,
            config.mspecies_map_df

        ) = otf_seqid_ncbi_gtdb_map(config)

    # ----------------
    # Pathway complementarity
    # ----------------
    if config.path_compl:

        logger.info("[STEP] EXTRACTING PATHWAY COMPLEMENTARITIES.")

        # ----------------
        # KEGG annotation - based on the DiTing implementation
        # ----------------

        if (
            not config.prev_path_compl and
            not config.ko_merged and
            not config.onthefly
        ):

            logger.info("[INTERMEDIATE STEP] KEGG ANNOTATION OF THE ORFs \n")

            run_kegg_annotate(config)

            # NOTE (Haris Zafeiropoulos, 2025-05-20):
            # In the stand-alone version, 'else' suggests a 3-col KEGG annotation file already available

        # ----------------
        # Extract pathway complementarities
        # ----------------

        if config.onthefly:

            db.get_path_compls_otf(config)

        else:

            if not config.prev_path_compl:

                pivot_df = load_merged_ko_file(config.ko_merged)  # Load ko_merged.txt

                if not os.path.exists(config.alts_file) or not os.path.exists(
                    config.compl_file
                ):

                    _, _ = export_pathway_complementarities(config, pivot_df)

    # ----------------
    # Seed complementarity
    # ----------------
    if config.seed_compl:

        logger.info("[STEP] EXTRACTING SEED COMPLEMENTARITIES.")

        # ----------------
        # Build GENREs
        # ----------------
        if not config.onthefly and not config.user_models:

            logger.info("[INTERMEDIATE STEP] GENOME-SCALE METABOLIC NETWORK RECONSTRUCTIONS")

            build_genres(config)

        # ----------------
        # microbetag implementation of Phylomint
        # ----------------
        logger.info("[INTERMEDIATE STEP] COMPUTING SEED SETS AND SCORES")

        if config.onthefly:

            config.get_scores      = True
            config.get_complements = True

            # Get dictionary with GTDB accession ids to their correspoding PATRIC
            gc_to_patric_ids        = db.patric_from_gc_list(config.repr_genomes_present)
            config.gc_to_patric_ids = db.update_for_patric(config.module_nonseeds, gc_to_patric_ids)

        run_seed_complementarity(config)

    # ----------------
    # Network clustering
    # ----------------
    if config.net_cluster and config.prev_manta_net is None:

        logger.info("[STEP] network clustering using manta and the abundance table")

        # Build original input file in cyjs format
        manta_input_net(config)

        logger.info(
            "Base network has been built and saved."
            "manta is now clustering your network..."
        )

        # Run manta on the cyjs network
        run_manta(config)

        logger.info("Base network has been built and saved.")

    # ----------------
    # Annotate network in .cx format
    # ----------------
    if config.precalc_only is False:
        logger.info("[STEP] ANNOTATE NETWORK ")
        mtg_net = mtg_annotate_network(config)

    # ----------------
    # Keep arguments
    # ----------------
    config.export_to_log()
    logger.info("A parameters.log file with the parameters used in this run was built.")

    logger.info("microbetag completed.")

    return mtg_net


def _print_help():
    help_message = """
    Usage: microbetag --config <path_to_config_yml>

    Other options:
    -h        Display this help message.
    -v        Display version.
    """
    print(help_message)


def _print_version():

    from . import __version__

    print(f"microbetag version: {__version__}")


def _print_config_message():
    """Error message for failure during parsing the configuration YAML file."""

    conf_message = """
    The config file you provided cannot be parsed properly.
    Please make sure you follow the instructions on the documentation site:
    https://hariszaf.github.io/microbetag/docs/tutorials/local/#input-and-configyml-files.
    Also, make sure that the configuration template you are using is the right one 
    for the microbetag version you are running.
    """
    logger.error(conf_message)


def main():
    """
    Loads and parses a configuration YAML file 
    and invokes the main function for running the microbetag pipeline.
    """
    parser = argparse.ArgumentParser(description="Microbetag CLI")

    parser.add_argument("--config", "-c", help="Path to the configuration yaml file.")
    parser.add_argument(
        "-v", "--version", action="store_true", help="Show Microbetag version"
    )

    args = parser.parse_args()

    if args.version:
        _print_version()
        sys.exit()

    elif args.config is None:
        _print_help()
        sys.exit(0)

    try:

        with open(args.config, "r") as yaml_file:
            yaml_conf = yaml.safe_load(yaml_file)

        config = Config(yaml_conf, args.config)

    except yaml.YAMLError:
        _print_config_message()
        sys.exit(1)

    # Run microbetag pipeline
    run_microbetag(config=config)


if __name__ == "__main__":

    main()
