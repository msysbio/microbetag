
import os
import logging
from .helpers import *

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

        # Pass loaded yaml object
        self.yaml = conf

        # User's group and user id
        file_info = os.stat(config_file)
        self.user_id = file_info.st_uid
        self.group_id = file_info.st_gid
        config_wd = os.path.dirname(os.path.realpath(__file__))
        self.cwd = os.path.dirname(config_wd)

        # Check if microbetag runs as a container
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
        if self.abundance_table is not None:
            self.delimiter = detect_separator(self.abundance_table)

        output_dir = conf.get("output_directory", {}).get("dir_path")
        self.output_dir = os.path.join(self.mount, output_dir) if self.mount and output_dir else output_dir

        edge_list = conf.get("edge_list", {}).get("file_path")
        self.network = os.path.join(self.mount, edge_list) if self.mount and edge_list else edge_list

        precalc_only = conf.get("precalulations_only").get("value")
        self.precalc_only = precalc_only if precalc_only in [0,1] else False

        # Set bins
        bn = BinsHandler(config=self)
        self.__dict__.update(vars(bn))

        # Get pathway complementarity related variables
        pcompl = conf.get("pathway_complementarity", {}).get("value")
        self.pathway_complementarity = pcompl if pcompl in [0,1] else True
        pc = PathwayComplementarity(config=self)
        self.__dict__.update(vars(pc))

        # Seed complementarity
        sc = SeedComplementarityHandler(config=self)
        self.__dict__.update(vars(sc))

        # Load abundance table with taxonomy
        nsc = AbdTableHandler(config=self)
        self.__dict__.update(vars(nsc))

        # Check whether bin names are the same in both abundance and edgelist files
        nh = NetworkHandler(config=self)
        self.__dict__.update(vars(nh))

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

        # ModelSEEDpy arguments
        self.gapfill_model = conf["gapfill_model"]["value"]
        self.gapfill_media = conf["gapfill_media"]["value"]

        # Flashweave arguments
        self.metadata_file = conf.get("metadata_file").get("file_path")
        self.metadata = "false" if self.metadata_file == "false" else "true"
        self.flashweave_args = conf["flashweave_args"]

        # Phenotrex
        self.genotypes_file = os.path.join(self.output_dir, "train.genotype")
        min_proba = conf.get("min_proba", {}).get("value") ; self.min_proba = min_proba if not None else 0.6

        # Mappings
        mappings = MappingPaths(config=self)
        self.__dict__.update(vars(mappings))

        # FAPROTAX
        faprotax = Faprotax(config=self)
        self.__dict__.update(vars(faprotax))

        # Manta
        net_clust = conf.get("network_clustering").get("value")
        self.network_clustering = (
            net_clust
            if net_clust in [0,1]
            else False
        )

        self.microbetag_annotated_network_file = os.path.join(self.output_dir, "microbetag_annotated_network.cx")
        self.tinyurl = (
            conf.get("tinyurl", {}).get("value")
            if conf.get("tinyurl", {}).get("value")
            else False
        )
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

        # Set variables regarding GENREs provided
        genres = GenresHandler(config=self)
        self.__dict__.update(vars(genres))


    def export_to_log(self, log_file="parameters.log"):
        logging.basicConfig(filename=log_file, level=logging.INFO, format='%(message)s')
        logging.info("Instance attribute values:")
        for key, value in self.__dict__.items():
            logging.info(f"{key}: {value}")

