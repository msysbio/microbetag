"""
Handlers classes allowing the different steps
"""
import os, sys
import json
import pickle
import logging
import pandas as pd

from .utils import resolve_file_path, convert_to_json_serializable
from .networks import build_base_graph

class PathwayComplementarity:
    """
    Sets variables regarding pathway complementarity tasks based on user's config (.yml) file
    """
    def __init__(self, config):
        self.conf = config
        self.base_dir = config.base_dir
        self.output_dir = config.output_dir

        # KEGG related paths to be filled based on user's settings
        self.ko_merged = None
        self.kegg_db_dir = None
        self.kegg_annotations = None
        self.kegg_pieces_dir = None
        self.initialize(config)

    def setup_kegg_annotations(self):
        """Sets up KEGG annotations and directories."""
        self.kegg_annotations = os.path.join(self.output_dir, "KEGG_annotations")
        os.makedirs(self.kegg_annotations, exist_ok=True)

        self.kegg_pieces_dir = os.path.join(self.kegg_annotations, 'hmmout')
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
            logging.error(
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
        if conf.pathway_complementarity:

            # Get pathways
            self.output_dirs(conf)

            # Maximum length of compl
            max_scratch_alt = conf.yaml.get("max_length_for_complement_from_scratch", {}).get("value")
            self.max_scratch_alt = (
                max_scratch_alt if max_scratch_alt is not None
                else 1
            )
            # Set up KEGG annotations 3-column file
            ko_merged = self.conf.yaml.get("ko_merged_file", {}).get("file_path")
            ko_merged = resolve_file_path(self.base_dir, ko_merged)
            self.ko_merged = ko_merged

            if self.ko_merged is None:
                self.setup_kegg_annotations()
                self.kegg_db_dir = self.get_kofam_db_path()

    def setup_ko_merged(self):
        """Sets up the KO merged file."""
        ko_merged = self.conf.yaml.get("ko_merged_file", {}).get("file_path")
        if ko_merged:
            self.ko_merged = os.path.join(self.base_dir, ko_merged)

    def output_dirs(self, config):
        """Paths to output folders and files"""
        self.pathway_complements_dir = os.path.join(self.output_dir, "pathway_complementarity")
        os.makedirs(self.pathway_complements_dir, exist_ok=True)
        self.alts_file = os.path.join(self.pathway_complements_dir, "alts.json")
        self.compl_file = os.path.join(self.pathway_complements_dir, "pathCompls.json")
        self.pathway_complement_percentage = (
            config.yaml["pathway_complement_percentage"]["value"]
            if config.yaml["pathway_complement_percentage"]["value"] is not None
            else 0
        )


class MappingPaths:
    """
    Sets paths to mapping files
    """
    def __init__(self, config):
        mtg = os.path.dirname(__file__)
        kegg_mappings = os.path.join(mtg, "mtg_maps_models/kegg_mappings/")
        self.kegg_mappings = kegg_mappings
        self.metanetx_compounds = os.path.join(mtg, "mtg_maps_models/MetaNetX/chem_xref.tar.gz")

        self.ko_terms_per_module_definition = os.path.join(kegg_mappings, "kegg_terms_per_module.tsv")
        self.modules_definitions_json_map = os.path.join(kegg_mappings, "module_definition_map.json")
        self.kegg_modules_to_maps = os.path.join(kegg_mappings, "module_map_pairs.tsv")
        self.seed_ko_mo = os.path.join(self.kegg_mappings, "seedId_keggId_module.tsv")
        self.module_descriptions = os.path.join(kegg_mappings, "module_descriptions")


class Faprotax:
    def __init__(self, config):
        """
        Sets paths to files to be used when running FAPROTAX
        """
        self.faprotax_txt = os.path.join(config.cwd, "mtg_maps_models/FAPROTAX_1.2.10/FAPROTAX.txt")
        self.faprotax_script = os.path.join(config.cwd, "mtg_maps_models/FAPROTAX_1.2.10/collapse_table.py")
        self.faprotax_output_dir = os.path.join(config.output_dir, "faprotax")
        self.faprotax_funct_table = os.path.join(self.faprotax_output_dir, "functional_otu_table.tsv")
        self.faprotax_sub_tables = os.path.join(self.faprotax_output_dir, "sub_tables")
        os.makedirs(self.faprotax_output_dir, exist_ok=True)
        os.makedirs(self.faprotax_sub_tables, exist_ok=True)


class NetworkHandler:
    def __init__(self, config):
        """
        Set network related configuration variables based on whether a network is already available or not
        and check whether all the sequence identifiers present in the network as nodes, are also among those
        of the abundance table
        """
        self.flashweave = False

        if config.network:
            self.process_network(config)
        else:
            self.network = os.path.join(config.output_dir, "network_output.edgelist")
            self.flashweave = True

    def process_network(self, config):
        """Process network edgelist and check bin consistency."""
        f = pd.read_csv(config.network, sep="\t")
        logging.info(f.head())

        bins_in_net = set(f.iloc[:, 0]).union(f.iloc[:, 1])  # Get unique bin names

        if config.abundance_table is not None and config.bins_ids is not None:

            bins_in_abundance_file = set(config.bins_ids)  # Assuming bins is a list or set

            if not bins_in_net.issubset(bins_in_abundance_file):
                missing_bins = bins_in_net - bins_in_abundance_file
                logging.warn(f"These bins are nodes on your provided network but not in your provided list of bins: {missing_bins}")

        elif config.abundance_table is None:
            self.seq_ids = bins_in_net  # Store sequence IDs if no abundance table is provided


class AbdTableHandler():

    def __init__(self, config):
        """
        Handles processing and validation of the abundance table.

        :param abundance_table: Path to the abundance table file.
        :param bins (optional): List of bin names to validate against the abundance table.

        Raises:
            ValueError: in case

        """
        if config.abundance_table is not None:
            self.load_abundance_table(config)
            self.load_metadata_file(config)

    def load_abundance_table(self, config):
        """Reads and validates the abundance table."""
        df = pd.read_csv(config.abundance_table, sep=config.delimiter)

        # Identify last column as taxonomy column
        self.taxonomy_column_name = df.columns[-1]
        non_numeric = pd.to_numeric(df[self.taxonomy_column_name], errors='coerce').isna().any()

        if not non_numeric:
            logging.error(
                "Taxonomy is not provided in the abundance table; "
                "at least not in the last column of the file as expected."
            )
            sys.exit(0)

        # First column is assumed to contain sequence IDs (bins)
        self.sequence_id_column_name = df.columns[0]
        self.seq_ids = df.iloc[:, 0].tolist()

        # Validate bin names if provided
        if config.bins_ids is not None:
            missing_bins = set(config.bins_ids) - set(self.seq_ids)
            missing_seq_ids = set(self.seq_ids) - set(config.bins_ids)

            if missing_seq_ids:
                for c in missing_seq_ids:
                    if not isinstance(c, str):
                        missing_seq_ids.remove(c) ; missing_seq_ids.add(str(c))
                missing_seq_ids_str = ', '.join(missing_seq_ids)
                logging.warn(
                    "There are sequence ids on your abundance table for which there are no"
                    f"bins provided in the `bins_fasta` folder: {missing_seq_ids_str}"
                )

            elif missing_bins:
                missing_bins_str = ', '.join(missing_bins)
                logging.warn(f"Bin names do not match with those in the abundance table: {missing_bins_str}")

    def load_metadata_file(self, config):
        """Load metadata file if provided"""
        # Metadata file
        metadata_file = config.yaml.get("metadata_file", {}).get("file_path")
        self.metadata_file = (
            os.path.join(config.base_dir, metadata_file)
            if metadata_file
            else None
        )
        if metadata_file is not None:
            df = pd.read_csv(self.metadata_file, sep="\t", index_col = 0, header=None)
            self.metadata_variables = df.index.to_list()

        # microbetag data product to enable running FlashWeave; the user will never have to worry for it.
        abd_flashweave = "abd_table_for_flashweave.tsv"
        self.flashweave_abd_table = os.path.join(config.base_dir, abd_flashweave)


class BinsHandler:
    def __init__(self, config):
        """
        Handles bin files management.
        """
        self.bins_ids = None
        self.bin_filenames = None
        self._validate_and_load_bins(config)

    def _validate_and_load_bins(self, config):
        """Validates bin file paths and loads bin filenames."""
        if config.bins_path is None:

            if config.precalc_only:
                raise ValueError("Please provide a path to the bins FASTA files.")

            logging.warning(
                "No bins FASTA files provided. microbetag will proceed with annotation using precalculated data."
            )

        # Try loading filenames from the given path
        try:
            self.bin_filenames = os.listdir(config.bins_path)
            self.bins_ids = [os.path.splitext(fname)[0] for fname in self.bin_filenames]

        except FileNotFoundError:
            raise ValueError("Invalid path provided for the bins FASTA files.")


class SeedComplementarityHandler():

    def __init__(self, config):
        """
        Handles genre reconstruction method validation based on user-provided models.

        :param config: Configuration object containing user preferences and paths.
        """

        self.base_dir = config.base_dir
        self.bins_path = config.bins_path

        # Get seed complementarity value, defaulting to True if invalid
        scompl = config.yaml.get("seed_complementarity", {}).get("value")
        if not isinstance(scompl, bool):
            scompl = False
            logging.warning(
                "Value for 'seed_complementarity' was not provided properly (true|false)."
                f"microbetag will proceed without seed complementarity. {WARNING_EMOJI}"
            )
        self.seed_complementarity = scompl

        self._validate_input_type(config)

        self._set_reconstruction_files(config)

        self.seeds_paths(config)
        self._validate_model_namespace(config)


    def _validate_input_type(self, config):
        """Validates and sets the input type for seed complementarity reconstructions."""
        input_value = config.yaml.get("input_type_for_seed_complementarities", {}).get("value")

        if not input_value:
            logging.error("Please select an input type for 'input_type_for_seed_complementarities'.")
            sys.exit(1)

        allowed_values = config.yaml.get("input_type_for_seed_complementarities", {}).get("value_from", [])
        if input_value not in allowed_values:
            logging.error(f"Error: Input value '{input_value}' is not among the allowed values: {allowed_values}")
            sys.exit(1)

        self.input_for_recon_type = input_value
        self.users_models = input_value == "models"


    def _set_reconstruction_files(self, config):
        """Determines the correct path for sequence files needed for reconstructions."""
        if self.input_for_recon_type == "bins_fasta":
            self.for_reconstructions = self.bins_path
        else:
            reconstr_files = config.yaml.get("sequence_files_for_reconstructions", {}).get("dir_path")
            if reconstr_files is None:
                raise ValueError("Please provide a valid path for sequence files for reconstructions.")
            self.for_reconstructions = os.path.join(self.base_dir, reconstr_files)


    def _validate_model_namespace(self, config):
        """Validates whether the model namespace matches the selected reconstruction tool."""
        import cobra
        if not self.users_models:
            return  # No user models provided, no need to check

        # Select a random model file from the directory
        try:
            model_files = os.listdir(self.for_reconstructions)
            if not model_files:
                raise ValueError("No models found in the provided reconstruction directory.")

            random_model = os.path.join(self.for_reconstructions, model_files[0])
            model = cobra.io.read_sbml_model(random_model)

        except FileNotFoundError:
            raise ValueError(f"Invalid path: {self.for_reconstructions}")

        except Exception as e:
            raise ValueError(f"Error loading model: {str(e)}")

        first_metabolite_id = model.metabolites[0].id[:3]

        # Check namespace compatibility
        if first_metabolite_id == "cpd":
            if self.genre_reconstruction_with == "carveme":
                raise ValueError(
                    "Your models appear to use the ModelSEED namespace (prefix 'cpd'), "
                    "but the selected reconstruction tool ('carveme') expects BiGG namespace."
                )
            elif self.genre_reconstruction_with != "modelseedpy":
                logging.warning("WARNING: Namespace mismatch detected. Switching to 'modelseedpy'.")
                self.genre_reconstruction_with = "modelseedpy"

        else:  # Models are expected to use BiGG namespace
            if self.genre_reconstruction_with == "modelseedpy":
                raise ValueError(
                    "Your models appear to use the BiGG namespace, but 'modelseedpy' "
                    "expects ModelSEED namespace (prefix 'cpd'). Please check your configuration."
                )
            elif self.genre_reconstruction_with != "carveme":
                logging.warning("WARNING: Assuming BiGG namespace. Switching to 'carveme'.")
                self.genre_reconstruction_with = "carveme"

    def seeds_paths(self, config):
        """Set pathways for seeds related files and folders"""

        self.gene_predictor = config.yaml.get("gene_predictor", {}).get("value")
        self.genre_reconstruction_with = config.yaml.get("genre_reconstruction_with", {}).get("value")

        if self.users_models is False:
            # Directory for tmp reconstruction files
            self.reconstructions = os.path.join(config.output_dir, "reconstructions")
            # Directory for final reconstructions
            self.genres = os.path.join(self.reconstructions, "GENREs")
            os.makedirs(self.reconstructions, exist_ok=True)
            os.makedirs(self.genres, exist_ok=True)
        else:
            self.reconstructions = self.for_reconstructions
            self.genres = self.for_reconstructions

        # Directory for seeds complementarity
        seedset_dir = config.yaml.get("prev_calc_seed_sets", {}).get("dir_path")
        print(seedset_dir)
        self.seeds = seedset_dir or os.path.join(config.output_dir, "seeds_complementarity")
        print(self.seeds)
        os.makedirs(self.seeds, exist_ok=True)
        self.seed_complements = os.path.join(self.seeds, "seed_complements.pckl")
        self.module_related_non_seeds = os.path.join(self.seeds, "module_related_non_seeds.pckl")
        self.phylomint_scores = os.path.join(self.seeds, "phylomint_scores.tsv")


def manta_input_net(config):
    """ Build intermediate network file as input for manta """

    manta_input = build_base_graph(config)
    manta_input_serial = convert_to_json_serializable(manta_input)
    with open(config.base_network_file, "w") as f:
        json.dump(manta_input_serial, f, indent=4)
    return True


class Emojis:
    def __init__(self) -> None:
        self.WARNING_EMOJI = "\u2757"
        self.TADA_EMOJI = "\"\U0001F389\""
        self.RED_CROSS_EMOJI = "\u274C"
        self.GREEN_CHECK_EMOJI = "\u2705"
        self.ANNOUNCEMET = "\u1F4E3"


# [NOTE] OUT OF SCOPE BUT CURRENTLY USEFUL
def local_seed_url():
    """
    Builds KEGG urls for seed complements.
    Function to be used out of the pipeline

    """
    from .utils import load_seed_complement_files, build_url_with_seed_complements
    kmap = load_seed_complement_files("/microbetag/mtg_maps_models/mappings/kegg_mappings/")

    output_folder = "/data/entero_klebsiella/seeds_complementarity/"

    seed_complements = os.path.join(output_folder, "seed_complements.pckl")
    with open(seed_complements, "rb") as f:
        seed_complements = pickle.load(f)
    seed_complements_dict = seed_complements.to_dict(orient="index")

    module_related_non_seeds = os.path.join(output_folder, "module_related_non_seeds.pckl")
    with open(module_related_non_seeds, "rb") as f:
        non_seed_sets = pickle.load(f)

    for id_x in seed_complements.index:
        for id_y in seed_complements.columns:
            # V
            complements = seed_complements_dict[id_x][id_y]
            print(complements)
            complements_map = kmap[kmap['modelseed'].isin(complements)]
            # S
            maps_in = list(kmap[kmap['modelseed'].isin(complements)]["map"].unique())
            # SDA
            for kegg_map in maps_in:
                #
                beneficiarys_nonseed = non_seed_sets.loc[id_x].to_list()[0]
                beneficiarys_nonseeds_map = kmap[kmap['modelseed'].isin(beneficiarys_nonseed)]
                # Run
                ksc = list(complements_map[complements_map["map"] == kegg_map]["kegg_compound"])
                msc = ";".join(set(complements_map[complements_map["map"] == kegg_map]["modelseed"]))
                ns = list(beneficiarys_nonseeds_map[beneficiarys_nonseeds_map["map"] == kegg_map]["kegg_compound"])
                surl = build_url_with_seed_complements(ksc, ns, kegg_map)
                print(surl)
            print("====")

