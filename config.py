
import os, sys
import csv
import pandas as pd
import cobra
import logging

# Set up custom logging format
logging.basicConfig(
    format='%(levelname)s: %(message)s',  # Define the format without "root:"
    level=logging.WARNING  # Set the logging level
)


class Config:
    """
    Parses a microbetag configuration file (yaml) to init a microbetag run.
    """
    def __init__(self, conf, config_file):

        # User's group and user id
        file_info = os.stat(config_file)
        self.user_id = file_info.st_uid
        self.group_id = file_info.st_gid
        self.cwd = os.path.dirname(os.path.realpath(__file__))

        self.mount = None
        if self.cwd == "/microbetag":
            self.mount = "/data"

        self.threads = conf["threads"]["value"] if conf["threads"]["value"] else 2

        self.bins_path = (
            os.path.join(self.mount, conf["bins_fasta"]["dir_path"])
            if self.mount and conf["bins_fasta"]["dir_path"]
            else conf["bins_fasta"]["dir_path"]
        )

        # The abundance table is now optional, if no abundance table and no network provided, then it will only run pre-calculations
        abd_tbl_filename = conf.get("abundance_table_file", {}).get("file_path")
        self.abundance_table = os.path.join(self.mount, abd_tbl_filename) if self.mount and abd_tbl_filename else abd_tbl_filename

        output_dir = conf.get("output_directory", {}).get("dir_path")
        self.output_dir = os.path.join(self.mount, output_dir) if self.mount and output_dir else output_dir

        edge_list = conf.get("edge_list", {}).get("file")
        self.network = os.path.join(self.mount, edge_list) if self.mount and edge_list else edge_list

        precalc_only = conf.get("precalulations_only").get("value")
        self.precalc_only = precalc_only if precalc_only in [0,1] else False

        bins = None
        if self.bins_path is None and self.precalc_only:
            raise ValueError("Please provide a path to the bins fasta files.")
        elif self.bins_path is None:
            logging.warn("No bins fasta files provided. microbetag will try to move on with the annotation parts using provided precalculations.")
            self.bin_filenames = None
        else:
            try:
                self.bin_filenames = os.listdir(self.bins_path)
                bins = [ os.path.splitext(gbin)[0] for gbin in self.bin_filenames ]
            except:
                raise ValueError("Please provide a valid path to the bins fasta files.")
            # [TODO] what if precalculations are made and you only need to run the rest of the pipeline ?

        metadata_file = conf.get("metadata_file", {}).get("file_path")
        self.metadata_file = os.path.join(self.mount, metadata_file) if self.mount and metadata_file else metadata_file
        if metadata_file is not None:
            df = pd.read_csv(self.metadata_file, sep="\t", index_col = 0, header=None)
            self.metadata_variables = df.index.to_list()

        # microbetag data product to enable running FlashWeave; the user will never have to worry for it.
        abd_flashweave = "abd_table_for_flashweave.tsv"
        self.flashweave_abd_table = os.path.join(self.mount, abd_flashweave) if self.mount else abd_flashweave

        # Pathway complementarity related
        pcompl = conf.get("pathway_complementarity", {}).get("value")
        self.pathway_complementarity = pcompl if pcompl in [0,1] else True
        if self.pathway_complementarity:

            ko_merged = conf.get("ko_merged_file", {}).get("file_path")
            self.ko_merged = os.path.join(self.mount, ko_merged) if self.mount and ko_merged else ko_merged

            if self.ko_merged is None:

                self.kegg_annotations = os.path.join(self.output_dir, "KEGG_annotations")
                os.makedirs(self.kegg_annotations, exist_ok=True)

                self.kegg_pieces_dir = os.path.join(self.kegg_annotations, 'hmmout')
                os.makedirs(self.kegg_pieces_dir, exist_ok=True)
                kofam_db = conf.get("kofam_database", {}).get("dir_path")
                if kofam_db is None:
                    logging.error(
                        "Please provide path to KOfam database. \
                        If not available in your system, you may download it from ftp://ftp.genome.jp/pub/db/kofam/"
                    )
                self.kegg_db_dir = os.path.join(self.mount, kofam_db) if self.mount and kofam_db else kofam_db

        # Seed complementarity
        self.users_models = False
        scompl = conf.get("seed_complementarity").get("value")
        self.seed_complementarity = scompl if scompl in [0,1] else True
        if self.seed_complementarity:
            input_value = (
                conf["input_type_for_seed_complementarities"]["value"]
                if conf["input_type_for_seed_complementarities"]["value"]
                else logging.error("Please select an input type for the input_type_for_seed_complementarities parameter.") or sys.exit(1)
            )
            allowed_values = conf["input_type_for_seed_complementarities"]["value_from"]
            self.input_for_recon_type = (
                input_value
                if input_value in allowed_values
                else (logging.error("Error: Input value is not among the allowed values:", allowed_values) or sys.exit(1))
            )
            self.users_models = True if conf["input_type_for_seed_complementarities"]["value"] == "models" else False
            if self.input_for_recon_type == "bins_fasta":
                self.for_reconstructions = self.bins_path
            else:
                reconstr_files = conf.get("sequence_files_for_reconstructions", {}).get("dir_path")
                if reconstr_files is None:
                    return ValueError(f"Please provide a type that makes sense.")
                self.for_reconstructions = os.path.join(self.mount, reconstr_files) if self.mount and reconstr_files else reconstr_files

        # Check whether bin names are the same in both abundance and edgelist files
        if self.abundance_table is not None:

            self.delimiter = detect_separator(self.abundance_table)
            df = pd.read_csv(self.abundance_table, sep=self.delimiter)

            # Check if last column, supposed to be the one with the taxonomy, has non-numeric entries
            self.taxonomy_column_name = list(df.columns)[-1]
            non_numeric = pd.to_numeric(df[self.taxonomy_column_name], errors='coerce').isna().any()

            if not non_numeric:
                logging.error("Taxonomy is not provided in the abundance table; at least not in the last column of the file as expected.")
                sys.exit(0)

            self.sequence_id_column_name = list(df.columns)[0]
            bins_in_abundance_file = list(df.iloc[:,0])

            if bins is not None:
                if not all(elem in bins_in_abundance_file for elem in bins):
                    not_in_second_list = set(bins) - set(bins_in_abundance_file)
                    not_in_second_list_str = ', '.join(not_in_second_list)
                    raise ValueError(f"Bin names do not match with those in the abundance table: {not_in_second_list_str}")
            self.seq_ids = bins_in_abundance_file

        if self.network:
            self.flashweave = False
            f = pd.read_csv(self.network, sep="\t")
            bins_in_net = set(list(f.iloc[:,0]) + list(f.iloc[:,1]))
            if self.abundance_table is not None and bins is not None:
                if not all(elem in bins_in_abundance_file for elem in bins_in_net) or not all(elem in bins_in_net for elem in bins):
                    raise ValueError(f"Bin names in the edgelist file do not match with those in the abundance table and/or in the bins.")
            elif self.abundance_table is None:
                self.seq_ids = bins_in_net
        else:
            # self.flashweave_script = os.path.join(self.cwd, "microbetagDB/scripts/flashweave.jl")
            self.network = os.path.join(self.output_dir, "network_output.edgelist")
            self.flashweave = True

        # Build output dir
        os.makedirs(self.output_dir, exist_ok=True)

        self.predictions_path = os.path.join(self.output_dir, "predictions")
        os.makedirs(self.predictions_path, exist_ok=True)

        orfs = conf.get("orfs", {}).get("path")
        if orfs is None:
            self.prodigal = os.path.join(self.output_dir, "ORFs")
            os.makedirs(self.prodigal, exist_ok=True)
        else:
            self.prodigal = os.path.join(self.mount, orfs) if self.mount else orfs

        self.reconstructions = os.path.join(self.output_dir, "reconstructions")
        self.genres = os.path.join(self.reconstructions, "GENREs")
        os.makedirs(self.reconstructions, exist_ok=True)
        os.makedirs(self.genres, exist_ok=True)

        self.gene_predictor = conf["gene_predictor"]["value"]
        self.genre_reconstruction_with = conf["genre_reconstruction_with"]["value"]

        self.seeds = os.path.join(self.output_dir, "seeds_complementarity")
        os.makedirs(self.seeds, exist_ok=True)
        self.seed_complements = os.path.join(self.seeds, "seed_complements.pckl")
        self.module_related_non_seeds = os.path.join(self.seeds, "module_related_non_seeds.pckl")
        self.phylomint_scores = os.path.join(self.seeds, "phylomint_scores.tsv")

        self.pathway_complements_dir = os.path.join(self.output_dir, "pathway_complementarity")
        os.makedirs(self.pathway_complements_dir, exist_ok=True)
        self.alts_file = os.path.join(self.pathway_complements_dir, "alts.json")
        self.compl_file = os.path.join(self.pathway_complements_dir, "pathCompls.json")
        self.pathway_complement_percentage = conf["pathway_complement_percentage"]["value"] if conf["pathway_complement_percentage"]["value"] is not None else 0

        # ModelSEEDpy arguments
        self.gapfill_model = conf["gapfill_model"]["value"]
        self.gapfill_media = conf["gapfill_media"]["value"]

        # Flashweave arguments
        self.metadata = "false" if self.metadata_file == "false" else "true"
        self.flashweave_args = conf["flashweave_args"]

        # Phenotrex
        self.genotypes_file = os.path.join(self.output_dir, "train.genotype")
        self.min_proba = conf["min_proba"]["value"]

        # Mappings
        self.kegg_mappings = os.path.join(self.cwd, "microbetagDB/mappings/kegg_mappings/")
        self.ko_terms_per_module_definition = os.path.join(self.kegg_mappings, "kegg_terms_per_module.tsv")
        self.modules_definitions_json_map = os.path.join(self.kegg_mappings, "module_definition_map.json")
        self.kegg_modules_to_maps = os.path.join(self.kegg_mappings, "module_map_pairs.tsv")
        self.seed_ko_mo = os.path.join(self.kegg_mappings, "seedId_keggId_module.tsv")
        self.module_descriptions = os.path.join(self.kegg_mappings, "module_descriptions")
        self.metanetx_compounds = os.path.join(self.cwd, "microbetagDB/mappings/MetaNetX/chem_xref.tsv")

        # FAPROTAX
        self.faprotax_txt = os.path.join(self.cwd, "microbetagDB/ref-dbs/FAPROTAX_1.2.7/FAPROTAX.txt")
        self.faprotax_script = os.path.join(self.cwd, "microbetagDB/ref-dbs/FAPROTAX_1.2.7/collapse_table.py")
        self.faprotax_output_dir = os.path.join(self.output_dir, "faprotax")
        self.faprotax_funct_table = os.path.join(self.faprotax_output_dir, "functional_otu_table.tsv")
        self.faprotax_sub_tables = os.path.join(self.faprotax_output_dir, "sub_tables")
        os.makedirs(self.faprotax_output_dir, exist_ok=True)
        os.makedirs(self.faprotax_sub_tables, exist_ok=True)

        net_clust = conf.get("network_clustering").get("value")
        self.network_clustering = net_clust if net_clust in [0,1] else False

        self.max_scratch_alt = conf["max_length_for_complement_from_scratch"]["value"] if conf["max_length_for_complement_from_scratch"]["value"] else 1

        self.microbetag_annotated_network_file = os.path.join(self.output_dir, "microbetag_annotated_network.cx")

        self.tinyurl = conf.get("tinyurl", {}).get("value") if conf.get("tinyurl", {}).get("value") else False

        # ==========
        # Init torch
        # ==========
        import torch
        from deepnog.utils import get_weights_path
        from deepnog.utils import set_device
        device = set_device('auto')
        try:
            weights_path = get_weights_path(
                database="eggNOG5",
                level=str(2),
                architecture="deepencoding",
            )
            _ = torch.load(weights_path, map_location=device)
        except:
            logging.warn("Could not load the deepnog weights. Please check the deepnog installation and setup.")
            pass

        # Tests
        if self.users_models:
            random_model = os.path.join(self.for_reconstructions, os.listdir(self.for_reconstructions)[0])
            model = cobra.io.read_sbml_model(random_model)
            if model.metabolites[0].id[:3] == "cpd" and self.genre_reconstruction_with == "carveme":
                logging.info("Based on the genre_reconstruction_with argument, your model are expected to have been built using the BiGG namespace\
                    \nyet, they are using the ModelSEED one. Please make sure you set those arguments in line or use another set of models that use the BiGG namespace indeed.");sys.exit(0)
            elif model.metabolites[0].id[:3] == "cpd" and self.genre_reconstruction_with != "modelseedpy":
                self.genre_reconstruction_with = "modelseedpy"
                logging.warning("WARNING. Var was reset")
            elif model.metabolites[0].id[:3] != "cpd" and self.genre_reconstruction_with == "modelseedpy":
                logging.info("Based on the genre_reconstruction_with argument, your model are expected to have been built\
                      \nusing ModelSEED but their namespace does not aggre. Make sure the genre_reconstruction_with variable aggree with your models format.");sys.exit(0)
            elif model.metabolites[0].id[:3] != "cpd" and self.genre_reconstruction_with != "carveme":
                logging.warning("WARNING! The models are assumed to use the BiGG namespace.")
                self.genre_reconstruction_with = "carveme"

    def export_to_log(self, log_file="parameters.log"):
        logging.basicConfig(filename=log_file, level=logging.INFO, format='%(message)s')
        logging.info("Instance attribute values:")
        for key, value in self.__dict__.items():
            logging.info(f"{key}: {value}")


def detect_separator(file_path):
    with open(file_path, 'r') as file:
        # Use csv.Sniffer to detect the dialect (separator, quote character, etc.)
        sample = file.read(1024)  # Read the first 1024 bytes
        sniffer = csv.Sniffer()
        dialect = sniffer.sniff(sample)
        return dialect.delimiter
