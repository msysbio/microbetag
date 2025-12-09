#!/usr/bin/env python3

import yaml
import argparse
import traceback
import pandas as pd
from pathlib import Path
from microbetag.config import load_abundance
from microbetag.networks import get_edgelist
from microbetag.utils import detect_separator
from microbetag.build_mtg_cx2 import mtg_annotate_network


class Config:
    def __init__(self, yaml_path: str):
        with open(yaml_path, "r") as f:
            data = yaml.safe_load(f)

        if not isinstance(data, dict):
            raise ValueError(f"YAML file {yaml_path} is not valid.")

        for key, value in data.items():
            setattr(self, key, value)

        self.kegg_mappings       = Path("/workspace/microbetag/mtg_maps_models/kegg_mappings/")
        self.module_descriptions = self.kegg_mappings / "module_descriptions"

    def __repr__(self):
        # __repr__ is a special method (a dunder method, short for double underscore) that defines how an object is represented as a string — primarily for developers (not end users).
        # It’s what you see when you type an object’s name in a Python shell or print it inside a list/dict.
        attrs = ", ".join(f"{k}={v!r}" for k, v in self.__dict__.items())
        return f"{self.__class__.__name__}({attrs})"


def load_data(config):

    # IMPORTANT: Sequence id to taxonomy map
    if config.network is None and config.abundance_file:
        (
            config.seq_to_taxon_df,
            config.sequence_id_column_name,
            config.taxonomy_column_name,
            config.delimiter,

        ) = load_abundance(config.abundance_file)

        config.seq_ids = config.seq_to_taxon_df["sequence_id"].unique().tolist()

    elif config.abundance_file is None and config.network:

        config.delimiter = detect_separator(config.sequence_taxonomy_map)

        seq_to_taxon_df         = pd.read_csv(config.sequence_taxonomy_map, sep=config.delimiter)
        seq_to_taxon_df.columns = ["sequence_id", "taxonomy"]
        config.seq_to_taxon_df    = seq_to_taxon_df
        config.seq_ids            = config.seq_to_taxon_df["sequence_id"].unique().tolist()

    elif config.abundance_file and config.network:

        # -------
        # NOTE: Not all sequence ids in the seq_ids need to have a taxonomy in this case --
        # only those coming from the abundance table
        # Yet, in case that the network has taxa not present in the abundance table, it will lead to errors.
        # -------

        network_df  = get_edgelist(config.network)
        net_seq_ids = (
            pd.concat([network_df.iloc[:, 0], network_df.iloc[:, 1]])
            .unique()
            .tolist()
        )

        (
            config.seq_to_taxon_df,
            config.sequence_id_column_name,
            config.taxonomy_column_name,
            config.delimiter,

        ) = load_abundance(config.abundance_file)

        abd_seq_ids = config.seq_to_taxon_df["sequence_id"].unique().tolist()
        config.seq_ids   = net_seq_ids + abd_seq_ids

    return config


def parse_args(args=None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="MicrobeTag Network Annotation Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,

    )
    # Required arguments
    parser.add_argument(
        '--config_file', '-c',
        type=str,
        required=True,
        help='Path to YAML configuration file (required)'
    )

    # Network-related arguments
    parser.add_argument(
        '--network', '-n',
        type=str,
        required=True,
        help='Path to network file (required)'
    )

    parser.add_argument(
        '--faprotax', '-f',
        type=str,
        required=False,
        help='Path to FAPROTAX subtables (optional)'
    )

    parser.add_argument(
        '--clustered', '-m',
        type=str,
        required=False,
        help='Path to FAPROTAX subtables (optional)'
    )

    return parser.parse_args(args)


# Usage with simple args
if __name__ == "__main__":

    """Main entry point."""

    args = parse_args()

    try:

        # Load configuration from YAML
        c = Config(args.config_file)
        c.network = args.network

        if args.faprotax:
            c.faprotax_sub_tables = args.faprotax

        if args.clustered:
            c.manta_net = args.clustered

        cd = load_data(c)

        # Annotate
        mtg_net = mtg_annotate_network(c)

    except Exception as e:

        print(f"❌ Unexpected error: {e}")
        traceback.print_exc()
