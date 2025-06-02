"""
Handlers classes allowing the different steps
"""

import os
import sys
import json
import pandas as pd
from typing import TYPE_CHECKING

from .utils import (
    mtg_logger,
    detect_separator,
    safe_literal_eval,
    resolve_file_path,
    convert_to_json_serializable,
)
from .networks import build_base_graph, get_edgelist

if TYPE_CHECKING:
    from .config import Config

class Emojis:
    def __init__(self) -> None:
        self.WARNING_EMOJI     = "\u2757"
        self.TADA_EMOJI        = '"\U0001f389"'
        self.RED_CROSS_EMOJI   = "\u274c"
        self.GREEN_CHECK_EMOJI = "\u2705"
        self.ANNOUNCEMET       = "\u1f4e3"

_logger_ = mtg_logger(__name__)
emojis   = Emojis()


class PathwayComplementarity:
    """
    Sets variables regarding pathway complementarity tasks based on user's config (.yml) file

    Args:
        config: An instance of the :class:`.config.Config` class.

    Note:
        From the :class:`.config.Config` class, the following attributes are being used:
            - `base_dir`
            - `ouput_dir`
            - `prev_path_compl`
            - `kofam_database`
            - `complement_max_length`
            - `ko_merged_file`
            - `pc_percentage`
    """

    def __init__(self, config: "Config"):
        self.conf       = config
        self.base_dir   = config.base_dir
        self.output_dir = config.output_dir

        # Init
        self.initialize(config)

    def setup_kegg_annotations(self):
        """Sets up KEGG annotations and directories."""
        self.kegg_annotations = os.path.join(self.output_dir, "KEGG_annotations")
        os.makedirs(self.kegg_annotations, exist_ok=True)

        self.kegg_pieces_dir = os.path.join(self.kegg_annotations, "hmmout")
        os.makedirs(self.kegg_pieces_dir, exist_ok=True)

    def get_kofam_db_path(self):
        """Returns the KOfam database path."""
        kofam_db = self.conf.yaml.get("kofam_database", {}).get("dir_path")
        if kofam_db is None:
            return self.handle_missing_kofam_db()
        else:
            return os.path.join(self.base_dir, kofam_db)

    def handle_missing_kofam_db(self):
        """Handles the case when the KOfam database path is missing."""
        container_kofam_db = "/microbetag/microbetag/mtg_maps_models/kofam_database/"
        if not os.path.exists(container_kofam_db):
            _logger_.error(
                "Please provide the path to the KOfam database. \n"
                "If not available, download it from ftp://ftp.genome.jp/pub/db/kofam/. \n"
                "If running microbetag through a container, mount kofam_db under "
                "/microbetag/microbetag/mtg_maps_models/kofam_database/."
            )
            sys.exit(0)
        else:
            return container_kofam_db

    def initialize(self, conf):
        """Main function to initialize pathway complementarity settings."""

        # Get pathways
        self.output_dirs()

        # Set up KEGG annotations 3-column file
        self.ko_merged = None
        if not self.prev_path_compl:

            ko_merged = self.conf.yaml.get("ko_merged_file", {}).get("file_path")

            if ko_merged:

                self.ko_merged = resolve_file_path(self.base_dir, ko_merged)

            else:

                if not conf.onthefly:

                    self.setup_kegg_annotations()
                    self.kegg_db_dir = self.get_kofam_db_path()

    def output_dirs(self):
        """Paths to output folders and files"""

        compl_file            = self.conf.yaml.get("prev_calc_path_compl", {}).get("file_path")
        self.path_compl_dir   = os.path.join(self.output_dir, "pathway_complementarity")
        self.path_compl_perce = self.conf.yaml.get("pc_percentage", {}).get("value", 1)

        os.makedirs(self.path_compl_dir, exist_ok=True)

        if compl_file:

            self.compl_file      = resolve_file_path(self.base_dir, compl_file)
            self.prev_path_compl = True

        else:

            self.prev_path_compl = False
            self.compl_file      = os.path.join(self.path_compl_dir, "pathCompls.json")
            self.alts_file       = os.path.join(self.path_compl_dir, "alts.json")


class MappingPaths:
    """
    Sets paths to mapping files
    """

    def __init__(self):
        mtg                     = os.path.dirname(__file__)
        kegg_mappings           = os.path.join(mtg, "mtg_maps_models/kegg_mappings/")
        self.kegg_mappings      = kegg_mappings
        self.metanetx_compounds = os.path.join(mtg, "mtg_maps_models/MetaNetX/chem_xref.tar.gz")

        self.ref_ko_per_module = os.path.join(
            kegg_mappings, "kegg_terms_per_module.tsv"
        )
        self.modules_definitions_json_map = os.path.join(
            kegg_mappings, "module_definition_map.json"
        )
        self.kegg_modules_to_maps = os.path.join(kegg_mappings, "module_map_pairs.tsv")
        self.seed_ko_mo           = os.path.join(self.kegg_mappings, "seedId_keggId_module.tsv")
        self.module_descriptions  = os.path.join(kegg_mappings, "module_descriptions")


class Faprotax:
    """Paths to FAPROTAX `collapse_table.py` script and database"""

    def __init__(self, config):
        """
        Sets paths to files to be used when running FAPROTAX
        """
        self.faprotax_txt = os.path.join(
            config.cwd, "mtg_maps_models/FAPROTAX_1.2.10/FAPROTAX.txt"
        )
        self.faprotax_script = os.path.join(
            config.cwd, "mtg_maps_models/FAPROTAX_1.2.10/collapse_table.py"
        )
        self.faprotax_output_dir  = os.path.join(config.output_dir, "faprotax")
        self.faprotax_funct_table = os.path.join(
            self.faprotax_output_dir, "functional_otu_table.tsv"
        )
        self.faprotax_sub_tables = os.path.join(self.faprotax_output_dir, "sub_tables")
        os.makedirs(self.faprotax_output_dir, exist_ok=True)
        os.makedirs(self.faprotax_sub_tables, exist_ok=True)


class NetworkHandler:
    """
    Set network-related configuration variables based on whether a network is already available or not.
    Check whether all the sequence identifiers present in the network as nodes, are also among those
    of the abundance table.
    """

    def __init__(self, config):

        self.flashweave = False

        if config.network:
            self.process_network(config)
        else:
            self.network    = os.path.join(config.output_dir, "network_output.edgelist")
            self.flashweave = True

    def process_network(self, config):
        """Process network edgelist and check bin consistency."""

        f = pd.read_csv(config.network, sep="\t")

        bins_in_net = set(f.iloc[:, 0]).union(f.iloc[:, 1])  # Get unique bin names

        if config.abundance_table is not None and config.bins_ids is not None:

            bins_in_abundance_file = set(
                config.bins_ids
            )  # Assuming bins is a list or set

            if not bins_in_net.issubset(bins_in_abundance_file):
                missing_bins = bins_in_net - bins_in_abundance_file
                _logger_.warn(
                    "These bins are nodes on your provided network"
                    f"but not in your provided list of bins: {missing_bins}"
                )

        elif config.abundance_table is None:
            self.seq_ids = (
                bins_in_net  # Store sequence IDs if no abundance table is provided
            )


class AbdTableHandler:
    """
    Handles processing and validation of the abundance table related variables.

    Args:
        config: Instance of the :class:`Config` class
    """

    def __init__(self, config):

        if config.abundance_table is not None:
            self.load_abundance_table(config)
            self.load_metadata_file(config)

    def load_abundance_table(self, config):
        """Reads and validates the abundance table."""
        df = pd.read_csv(config.abundance_table, sep=config.delimiter)

        # Identify last column as taxonomy column
        self.taxonomy_column_name = df.columns[-1]
        non_numeric = (
            pd.to_numeric(df[self.taxonomy_column_name], errors="coerce").isna().any()
        )

        if not non_numeric:
            _logger_.error(
                "Taxonomy is not provided in the abundance table; "
                "at least not in the last column of the file as expected."
            )
            sys.exit(0)

        # First column is assumed to contain sequence IDs (bins)
        self.sequence_id_column_name = df.columns[0]
        self.seq_ids                 = df.iloc[:, 0].tolist()

        # Validate bin names if provided
        if config.bins_ids is not None:
            missing_bins    = set(config.bins_ids) - set(self.seq_ids)
            missing_seq_ids = set(self.seq_ids) - set(config.bins_ids)

            if missing_seq_ids:
                for c in missing_seq_ids:
                    if not isinstance(c, str):
                        missing_seq_ids.remove(c)
                        missing_seq_ids.add(str(c))
                missing_seq_ids_str = ", ".join(missing_seq_ids)
                _logger_.warn(
                    "There are sequence ids on your abundance table for which there are no"
                    f"bins provided in the `bins_fasta` folder: {missing_seq_ids_str}"
                )

            elif missing_bins:
                missing_bins_str = ", ".join(missing_bins)
                _logger_.warn(
                    f"Bin names do not match with those in the abundance table: {missing_bins_str}"
                )

        # microbetag data product to enable running FlashWeave; the user will never have to worry for it.
        abd_flashweave            = "abd_table_for_flashweave.tsv"
        self.flashweave_abd_table = os.path.join(config.base_dir, abd_flashweave)

    def load_metadata_file(self, config):
        """Load metadata file if provided"""
        # Metadata file
        metadata_file      = config.yaml.get("metadata_file", {}).get("file_path")
        self.metadata_file = (
            os.path.join(config.base_dir, metadata_file) if metadata_file else None
        )
        if metadata_file is not None:
            df                      = pd.read_csv(self.metadata_file, sep="\t", index_col=0, header=None)
            self.metadata_variables = df.index.to_list()


class BinsHandler:
    """
    Handles bin/genomes/MAGs related variables in case of using microbetag with local/custom genomes.
    """

    def __init__(self, config):

        self.bins_ids      = None
        self.bin_filenames = None
        self._validate_and_load_bins(config)

    def _validate_and_load_bins(self, config):
        """Validates bin file paths and loads bin filenames."""

        if config.bins_path is None:

            if config.precalc_only:
                raise ValueError("Please provide a path to the bins FASTA files.")

            _logger_.warning(
                "No bins FASTA files provided. microbetag will proceed with annotation using precalculated data."
            )

        # Try loading filenames from the given path
        try:
            self.bin_filenames = os.listdir(config.bins_path)
            self.bins_ids      = [os.path.splitext(fname)[0] for fname in self.bin_filenames]

        except FileNotFoundError:
            raise ValueError("Invalid path provided for the bins FASTA files.")


class SeedComplementarityHandler:
    """
    Handles variables related to building GENRES and the seed complementarity module.

    Args:
        config: Instance of the :class:`Config` class
    """

    def __init__(self, config):

        self.base_dir  = config.base_dir
        self.bins_path = config.bins_path

        # Get seed complementarity value, defaulting to True if invalid
        scompl = config.yaml.get("seed_complementarity", {}).get("value", True)
        if not isinstance(scompl, bool):
            error_msg = (
                "Value for 'seed_complementarity' was not provided properly (true|false)."
                f"microbetag will proceed without seed complementarity. {emojis.WARNING_EMOJI}"
            )
            raise error_msg

        self.seed_compl = scompl

        if not config.onthefly:
            self._validate_input_type(config)
            self._set_reconstruction_files(config)
            self.reconstrucion_paths(config)
            self._validate_model_namespace()

        self.seeds_paths(config)

    def _validate_input_type(self, config):
        """Validates and sets the input type for seed complementarity reconstructions."""

        sc_input_type = config.yaml.get("sc_input_type", {}).get(
            "value"
        )

        if not sc_input_type:
            _logger_.error(
                "Please select an input type for 'sc_input_type'."
            )
            sys.exit(1)

        allowed_values = config.yaml.get(
            "sc_input_type", {}
        ).get("value_from", [])

        if sc_input_type not in allowed_values:
            _logger_.error(
                f"Error: Input value '{sc_input_type}' is not among the allowed values: {allowed_values}"
            )
            sys.exit(1)

        self.sc_input_type = sc_input_type
        self.user_models   = sc_input_type == "models"

    def _set_reconstruction_files(self, config):
        """Determines the correct path for sequence files needed for reconstructions."""
        if self.sc_input_type == "bins_fasta":
            self.for_reconstructions = self.bins_path
        else:
            reconstr_files = config.yaml.get(
                "sequence_files_for_reconstructions", {}
            ).get("dir_path")
            if reconstr_files is None:
                raise ValueError(
                    "Please provide a valid path for sequence files for reconstructions."
                )
            self.for_reconstructions = os.path.join(self.base_dir, reconstr_files)

    def _validate_model_namespace(self):
        """Validates whether the model namespace matches the selected reconstruction tool."""
        import cobra

        if not self.user_models:
            return  # No user models provided, no need to check

        # Select a random model file from the directory
        try:
            model_files = os.listdir(self.for_reconstructions)
            if not model_files:
                raise ValueError(
                    "No models found in the provided reconstruction directory."
                )

            random_model = os.path.join(self.for_reconstructions, model_files[0])
            model        = cobra.io.read_sbml_model(random_model)

        except FileNotFoundError:
            raise ValueError(f"Invalid path: {self.for_reconstructions}")

        except Exception as e:
            raise ValueError(f"Error loading model: {str(e)}")

        first_metabolite_id = model.metabolites[0].id[:3]

        # Check namespace compatibility
        if first_metabolite_id == "cpd":
            self.namespace = "modelseed"
            if self.genre_reconstruction_with == "carveme":
                raise ValueError(
                    "Your models appear to use the ModelSEED namespace (prefix 'cpd'), "
                    "but the selected reconstruction tool ('carveme') expects BiGG namespace."
                )
            elif self.genre_reconstruction_with != "modelseedpy":
                _logger_.warning(
                    "WARNING: Namespace mismatch detected. Switching to 'modelseedpy'."
                )
                self.genre_reconstruction_with = "modelseedpy"

        else:  # Models are expected to use BiGG namespace
            self.namespace = "BiGG"
            if self.genre_reconstruction_with == "modelseedpy":
                raise ValueError(
                    "Your models appear to use the BiGG namespace, but 'modelseedpy' "
                    "expects ModelSEED namespace (prefix 'cpd'). Please check your configuration."
                )
            elif self.genre_reconstruction_with != "carveme":
                _logger_.warning(
                    "WARNING: Assuming BiGG namespace. Switching to 'carveme'."
                )
                self.genre_reconstruction_with = "carveme"

    def reconstrucion_paths(self, config):
        """Set pathways for seeds related files and folders"""

        self.gene_predictor            = config.yaml.get("gene_predictor", {}).get("value")
        self.genre_reconstruction_with = config.yaml.get("genre_reconstruction_with", {}).get("value")

        if self.genre_reconstruction_with == "modelseedpy":

            # ModelSEEDpy arguments
            self.gapfill_model = config.yaml.get("gapfill_model", {}).get("value", True)

            gapfill_media = config.yaml.get("gapfill_media", {}).get("file_path", None)
            if gapfill_media:
                delimiter = detect_separator(gapfill_media)
                gf = pd.read_csv(gapfill_media, sep=delimiter)
                # NOTE (Haris Zafeiropoulos, 2025-05-20):  NOT DONE !!

        if self.user_models is False:

            # Directory for tmp reconstruction files
            self.reconstructions = os.path.join(config.output_dir, "reconstructions")

            # Directory for final reconstructions
            self.genres = os.path.join(self.reconstructions, "GENREs")
            os.makedirs(self.reconstructions, exist_ok=True)
            os.makedirs(self.genres, exist_ok=True)

        else:
            self.reconstructions = self.for_reconstructions
            self.genres = self.for_reconstructions

    def seeds_paths(self, config):

        # Directory for seeds complementarity
        self.seeds_outdir  = os.path.join(config.output_dir, "seeds_complementarity")
        os.makedirs(self.seeds_outdir, exist_ok=True)

        # NOTE (Haris Zafeiropoulos, 2025-04-29): These 2 are supposed to be the .json files.
        self.prev_conf     = config.yaml.get("prev_conf", {}).get("file_path")
        self.prev_nonseeds = config.yaml.get("prev_nonseeds", {}).get("file_path")

        self.skip_sets     = self.prev_conf is not None and self.prev_nonseeds is not None

        self.seed_compl_pckl  = os.path.join(self.seeds_outdir, "seed_complements.pckl")
        self.phylomint_scores = os.path.join(self.seeds_outdir, "phylomint_scores.tsv")

        # NOTE (Haris Zafeiropoulos, 2025-05-07):
        # If prev_conf and prev_nonseeds are None, then module_seeds and module_nonseeds will be built during the run
        # Otherwise, these neeed to
        self.module_seeds    = os.path.join(self.seeds_outdir, "kegg_module_related_seeds.pckl")

        if config.onthefly:
            self.module_nonseeds = config.yaml.get("prev_nonseeds_module", {}).get("file_path")
        else:
            self.module_nonseeds = os.path.join(
                self.seeds_outdir, "kegg_module_related_nonseeds.pckl"
            )


def manta_input_net(config: "Config") -> bool:
    """Wrapper for building the intermediate network CYJSON file; input for manta"""

    manta_input        = build_base_graph(config)
    manta_input_serial = convert_to_json_serializable(manta_input)
    with open(config.base_network_file, "w") as f:
        json.dump(manta_input_serial, f, indent=4)
    return True


def otf_seqid_ncbi_gtdb_map(config: "Config") -> tuple[dict, dict, pd.DataFrame]:
    """
    Builds a dataframe with sequence ids of nodes A and B found associated in the
    co-occurrence network followed by their corresponding NCBI Taxonomy ids and the
    representative GTDB genomes.

    Returns:
        A tuple containing:
            - pairs_of_interest: {("",""). ("","")}
            - relative_genomes: {ncbi_id: [gc, gc, gc], ..}
            - mspecies_map_df: A data frame with the sequence ids of the abundance data and
                their mapped NCBI Taxonomy IDs and their corresponding GTDB representative genomes.
    Note:
        Strictly for the on-the-fly version
    """
    edgelist_df = get_edgelist(config.network)
    seq_map_df  = config.otf_seq_tax_df.dropna(subset=["species_ncbi_id"]).copy()

    merged = edgelist_df.merge(seq_map_df[['microbetag_id', 'species_ncbi_id', 'gtdb_gen_repr']],
                               left_on='node_A', right_on='microbetag_id', how='left') \
        .rename(columns={'species_ncbi_id': 'species_ncbi_id_A',
                         'gtdb_gen_repr': 'gtdb_gen_repr_A'}) \
        .drop(columns='microbetag_id')

    # Merge again to get info for nodeB
    merged = merged.merge(seq_map_df[['microbetag_id', 'species_ncbi_id', 'gtdb_gen_repr']],
                          left_on='node_B', right_on='microbetag_id', how='left') \
        .rename(columns={'species_ncbi_id': 'species_ncbi_id_B',
                         'gtdb_gen_repr': 'gtdb_gen_repr_B'}) \
        .drop(columns='microbetag_id')

    # Clean and apply transformations
    filtered = merged.dropna(subset=['gtdb_gen_repr_A', 'gtdb_gen_repr_B']).copy()

    filtered[['gtdb_gen_repr_A', 'gtdb_gen_repr_B']] = filtered[
        ['gtdb_gen_repr_A', 'gtdb_gen_repr_B']].applymap(safe_literal_eval)

    filtered[["species_ncbi_id_A", "species_ncbi_id_B"]] = filtered[
        ["species_ncbi_id_A", "species_ncbi_id_B"]].astype(int)

    # Explode and drop duplicates
    exploded        = filtered.explode('gtdb_gen_repr_A').explode('gtdb_gen_repr_B').reset_index(drop=True)
    mspecies_map_df = exploded.drop_duplicates(subset=['gtdb_gen_repr_A', 'gtdb_gen_repr_B'])

    # Build pairs of interest and relative genomes
    pairs_of_interest = {
        (str(row['species_ncbi_id_A']), str(row['species_ncbi_id_B']))
        for _, row in mspecies_map_df.iterrows()
    }
    pairs_of_interest.update({(b, a) for a, b in pairs_of_interest})
    relative_genomes = {
        str(row['species_ncbi_id_A']): {str(row['gtdb_gen_repr_A'])}
        for _, row in mspecies_map_df.iterrows()
    }
    relative_genomes.update(
        {str(row['species_ncbi_id_B']): {str(row['gtdb_gen_repr_B'])}
         for _, row in mspecies_map_df.iterrows()}
    )

    outfile = os.path.join(config.output_dir, "edge_map.tsv")
    mspecies_map_df.to_csv(outfile)

    return pairs_of_interest, relative_genomes, mspecies_map_df
