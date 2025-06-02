# microbetag : a software suite to annotate microbial co-occurrence networks

# Copyright (c) 2025 Haris Zafeiropoulos

# Licensed under GNU LGPL.3, see LICENCE file

import os
import json
import pandas as pd

from .helpers import (
    Emojis,
    Faprotax,
    BinsHandler,
    MappingPaths,
    NetworkHandler,
    AbdTableHandler,
    PathwayComplementarity,
    SeedComplementarityHandler,
)
from .networks import get_edgelist
from .utils import (
    mtg_logger,
    detect_separator,
    resolve_file_path,
    convert_to_json_serializable
)


_logger_ = mtg_logger(__name__)


class Config:
    """
    Parses a microbetag configuration file (yaml) to init a microbetag run.

    Args:
        conf: A dictionary where the YAML configuration file has been loaded
        config_file: Filepath to the configuration YAML file.

    Attention:
        It is essential to use the corresponding to the microbetag version you are using configuration template file.
        Otherwise, the Config class will fail to create an instance and microbetag will exit.
        You may find microbetag configuration templates by version at:
        https://github.com/hariszaf/microbetag/tree/fix-phylomint/config_files

    Example:
        >>> with open(args.config, "r") as yaml_file:
                yaml_conf = yaml.safe_load(yaml_file)
        >>> conf = Config(yaml_conf, args.config)
    """

    def __init__(self, conf: dict, config_file: str = None):

        # Pass loaded yaml object
        self.yaml = conf

        # Load emojis
        emojis = Emojis()

        # User's group and user id
        if config_file is not None:
            self.yaml_file = os.stat(config_file)
            self.user_id   = self.yaml_file.st_uid
            self.group_id  = self.yaml_file.st_gid

        self.cwd = os.path.dirname(os.path.realpath(__file__))

        # Check if microbetag runs as a container
        self.mount = None
        if self.cwd == "/microbetag":
            self.mount    = "/data"
            self.base_dir = self.mount
        else:
            self.base_dir = os.path.dirname(config_file)

        # Output dir
        output_dir = conf.get("output_directory", {}).get("dir_path")
        if output_dir:
            self.output_dir = os.path.join(self.base_dir, output_dir)
        else:
            raise ValueError("Output directory needs to be specified.")

        # Build output dir
        os.makedirs(self.output_dir, exist_ok=True)

        # Mappings
        mappings = MappingPaths()
        self.__dict__.update(vars(mappings))

        # Checks whether microbetag is running on the on-the-fly version, by default False
        self.onthefly = conf.get("onthefly", {}).get("value", False)
        self.api      = conf.get("api", {}).get("value", False)

        # Threads to be used
        self.threads = conf.get("threads",{}).get("value", 2)

        # Steps
        self.faprotax    = conf.get("faprotax_annotation", {}).get("value", False)
        self.phen_traits = conf.get("phenotrex_traits", {}).get("value", False)
        self.path_compl  = conf.get("pathway_complementarity", {}).get("value", False)
        self.seed_compl  = conf.get("seed_complementarity", {}).get("value", False)
        self.net_cluster = conf.get("network_clustering", {}).get("value", False)

        # Bins/MAGs/genomes
        bins_fasta     = conf.get("bins_fasta", {}).get("dir_path")
        self.bins_path = resolve_file_path(self.base_dir, bins_fasta)

        _logger_.warn("No genomes/bins were provided as input files.")

        # The abundance table is now optional, if no abundance table and no network provided,
        # then it will only run pre-calculations
        abd_tbl_filename     = conf.get("abundance_table_file", {}).get("file_path")
        self.abundance_table = resolve_file_path(self.base_dir, abd_tbl_filename)

        # Edgelist of provided network
        edge_list    = conf.get("edge_list", {}).get("file_path")
        self.network = resolve_file_path(
            self.base_dir, edge_list
        )

        # -------
        # NOTE: Setting precalculations only as true allows to get a Config instance
        # without providing an abundance table or network, meaning you can use the Config instance
        # for partial/specific tasks of microbetag.
        # -------

        precalc_only      = conf.get("precalculations_only", {}).get("value")
        self.precalc_only = precalc_only if precalc_only in [0, 1] else False

        if (
            self.abundance_table is None and self.network is None and precalc_only is False
        ):
            raise ValueError(
                "You need to provide at least one between an abundance table"
                "and a network's edgelist in 3-column format."
            )

        # IMPORTANT: Sequence to taxonomy map -- required if no abundance table is needed
        sequence_taxonomy_map      = conf.get("sequence_id_taxonomy_map", {}).get("file_path")
        self.sequence_taxonomy_map = resolve_file_path(
            self.base_dir, sequence_taxonomy_map
        )

        if (
            self.abundance_table is None and self.sequence_taxonomy_map is None and precalc_only is False
        ):
            raise ValueError(
                "Since an abundance table is not provided, you need to provide a 2-column file "
                "with the sequence id (e.g bin ids) and their corresponding taxonomy or taxon name."
            )

        # IMPORTANT: Sequence id to taxonomy map
        if self.network is None and self.abundance_table:
            (
                self.seq_to_taxon_df,
                self.sequence_id_column_name,
                self.taxonomy_column_name,
                self.delimiter,

            ) = load_abundance(self.abundance_table)

            self.seq_ids = self.seq_to_taxon_df["sequence_id"].unique().tolist()

        elif self.abundance_table is None and self.network:

            self.delimiter = detect_separator(self.sequence_taxonomy_map)

            seq_to_taxon_df         = pd.read_csv(self.sequence_taxonomy_map, sep=self.delimiter)
            seq_to_taxon_df.columns = ["sequence_id", "taxonomy"]
            self.seq_to_taxon_df    = seq_to_taxon_df
            self.seq_ids            = self.seq_to_taxon_df["sequence_id"].unique().tolist()

        elif self.abundance_table and self.network:

            # -------
            # NOTE: Not all sequence ids in the seq_ids need to have a taxonomy in this case --
            # only those coming from the abundance table
            # Yet, in case that the network has taxa not present in the abundance table, it will lead to errors.
            # -------

            network_df  = get_edgelist(self.network)
            net_seq_ids = (
                pd.concat([network_df.iloc[:, 0], network_df.iloc[:, 1]])
                .unique()
                .tolist()
            )

            (
                self.seq_to_taxon_df,
                self.sequence_id_column_name,
                self.taxonomy_column_name,
                self.delimiter,

            ) = load_abundance(self.abundance_table)

            abd_seq_ids = self.seq_to_taxon_df["sequence_id"].unique().tolist()
            self.seq_ids = net_seq_ids + abd_seq_ids

        else:
            _logger_.warning(
                f"{emojis.WARNING_EMOJI}Neither an abundance table nor a network was procided.\n"
                "microbetag will only run some pre-calculations not requiring them.\n"
            )

        # Set bins
        self.bins_ids = None
        if self.bins_path is not None:
            bn = BinsHandler(config=self)
            self.__dict__.update(vars(bn))

        # Load abundance table with taxonomy
        nsc = AbdTableHandler(config=self)
        self.__dict__.update(vars(nsc))

        # Check whether bin names are the same in both abundance and edgelist files
        nh = NetworkHandler(config=self)
        self.__dict__.update(vars(nh))

        # Flashweave arguments
        self.flashweave_args = conf.get("flashweave_args", {})

        metadata_file      = conf.get("metadata_file", {}).get("file_path")
        self.metadata_file = resolve_file_path(self.base_dir, metadata_file)
        self.metadata      = "false" if self.metadata_file in ("false", None) else "true"

        # Update conf variables for pathway complementarity module
        if self.path_compl:
            pc = PathwayComplementarity(config=self)
            self.__dict__.update(vars(pc))

        # Open Reading Frames
        if not self.onthefly and self.path_compl:
            orfs = conf.get("orfs", {}).get("path")
            if orfs is None:
                self.prodigal = os.path.join(self.output_dir, "ORFs")
                os.makedirs(self.prodigal, exist_ok=True)
            else:
                self.prodigal = os.path.join(self.base_dir, orfs)

        # ModelSEEDpy arguments
        self.gapfill_model = conf.get("gapfill_model", {}).get("value")
        self.gapfill_media = conf.get("gapfill_media", {}).get("value")

        # Phenotrex
        if self.phen_traits:

            self.predictions_path = os.path.join(self.output_dir, "phen_predictions")
            self.phen_classes     = os.path.join(self.cwd, "mtg_maps_models/phenDB/classes/")
            self.genotypes_file   = os.path.join(self.output_dir, "train.genotype")
            self.min_proba        = conf.get("min_proba", {}).get("value", 0.75)

            os.makedirs(self.predictions_path, exist_ok=True)

        # FAPROTAX
        if self.abundance_table is not None and self.faprotax:
            faprotax = Faprotax(config=self)
            self.__dict__.update(vars(faprotax))

        # Manta
        # net_clust = conf.get("network_clustering").get("value")
        # self.net_cluster = net_clust if net_clust in [0, 1] else False
        if self.net_cluster:

            self.prev_manta_net = conf.get("prev_clustered_network", {}).get("file_path", None)

            if self.prev_manta_net:
                self.manta_net = resolve_file_path(self.base_dir, self.prev_manta_net)
            else:
                self.base_network_file = os.path.join(self.output_dir, "basenet.cyjs")
                self.manta_net         = os.path.join(self.output_dir, "manta_annotated.cyjs")

        # Seed complementarity
        if self.seed_compl:
            sc = SeedComplementarityHandler(config=self)
            self.__dict__.update(vars(sc))

        # Intermediate annoteted network file name
        self.microbetag_annotated_network_file = os.path.join(
            self.output_dir, "pseudo_cx_annotated_net.cx"
        )
        self.tinyurl = (
            conf.get("tinyurl", {}).get("value")
            if conf.get("tinyurl", {}).get("value")
            else False
        )
        # ==========
        # Init torch -- machine learning library
        # ==========
        if not self.onthefly and self.phen_traits:

            import torch
            from deepnog.utils import get_weights_path
            from deepnog.utils import set_device

            device = set_device("auto")
            try:
                weights_path = get_weights_path(
                    database="eggNOG5",
                    level=str(2),
                    architecture="deepencoding",
                )
                _ = torch.load(weights_path, map_location=device)
            except Exception:
                _logger_.warn(
                    "Could not load the deepnog weights. Please check the deepnog installation and setup."
                )
                pass

        _logger_.info("Configuration file loaded successfully.")

    def export_to_log(self, log_file="parameters.log"):
        """Dumps the Config instance in a JSON file."""
        args = convert_to_json_serializable(self.__dict__)
        with open(log_file, "w") as f:
            json.dump(args, f)


def load_abundance(abd_file: str) -> tuple[pd.DataFrame, str, str, str]:
    """
    Load a tsv/csv format abundance table assuming the sequence id is procided in the first column
    and the taxonomy in the last one

    Args:
        abd_file: Filepath to abundance table file.

    Returns:
        A tuple including:
            - seq_id2tax: A :class:`pandas.DataFrame` with the sequence id and their corresponding taxonomy
            - seq_id_col: The name of the column with the sequence identifier (e.g. ``seqId``)
            - tax_col: The name of the column with the taxonomy
    """

    delimiter          = detect_separator(abd_file)
    abd_tab_df         = pd.read_csv(abd_file, sep=delimiter)
    seq_id_col         = abd_tab_df.columns[0]
    tax_col            = abd_tab_df.columns[-1]
    seq_id2tax         = abd_tab_df[[seq_id_col, tax_col]]
    seq_id2tax.columns = ["sequence_id", "taxonomy"]

    return seq_id2tax, seq_id_col, tax_col, delimiter
