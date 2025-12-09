import os
import unittest
import pandas as pd
import shutil
from pathlib import Path

from microbetag.tools import run_manta
from microbetag.config import load_abundance
from microbetag.helpers import manta_input_net


# Directories
root_dir   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
test_data  = os.path.join(root_dir, "test_data", "test_manta")
outdir = os.path.join(test_data, "output_files")

# Using abundance table to map sequence ids to taxonomies
abd_table_dir = os.path.join(test_data, "input_files", "based_on_abd_table")
abd_table     = os.path.join(abd_table_dir, "thirty_Samples.tsv")  # "plaque_abd_tab.tsv"
net_edgelist  = os.path.join(abd_table_dir, "edgelist.csv")  # "plaque_edgelist.tsv"
outdir_abd    = os.path.join(outdir, "based_on_abd_table")

# Using a sequence to taxonomy file to map sequence ids to taxonomies
input_net_dir    = os.path.join(test_data, "input_files", "based_on_net")
edgelist         = os.path.join(input_net_dir, "edgelist.csv")
seq_tax_map_file = os.path.join(input_net_dir, "seq2taxonomy.tsv")
outdir_net       = os.path.join(outdir, "based_on_net")

# Remove previous output folder
prev_run = Path(outdir)
if prev_run.exists():
    print("Removing output folder from previous run.")
    shutil.rmtree(prev_run)

class NetConfig:
    """Config-like class for the case a network is being used"""

    def __init__(self, outdir):

        os.makedirs(outdir, exist_ok=True)

        # Specify case to use
        seq_tax_map          = pd.read_csv(seq_tax_map_file, sep="\t", names=["sequence_id", "taxonomy"])

        self.outdir      = outdir
        self.network         = edgelist
        self.seq_to_taxon_df = seq_tax_map
        self.seq_ids         = seq_tax_map[seq_tax_map.columns[0]].unique().tolist()

        self.base_network_file = os.path.join(outdir, "basenet.cyjs")

class AbdTableConfig:

    """Config-like class for the case an abundance table is being used"""

    def __init__(self, outdir):

        os.makedirs(outdir, exist_ok=True)
        self.outdir = outdir

        # Specify case to use
        self.abundance_table   = abd_table
        self.network           = net_edgelist

        # Use-case independent but required part of the config
        (
            self.seq_to_taxon_df,
            self.sequence_id_column_name,
            self.taxonomy_column_name,
            _,  # delimeter
        ) = load_abundance(self.abundance_table)

        self.seq_ids = self.seq_to_taxon_df["sequence_id"].unique().tolist()

        # NOTE (Haris Zafeiropoulos, 2025-05-21):
        # Special attention to the suffix, needs to be cyjs - not cyjsn or anything else
        self.base_network_file = os.path.join(outdir, "basenet.cyjs")


class TestManta(unittest.TestCase):
    """Unit-test class to test the two main functions regarding manta"""

    @classmethod
    def setUpClass(cls):
        # This is called once for the entire class before any test runs
        cls.net_config = NetConfig(outdir_net)
        cls.abd_config = AbdTableConfig(outdir_abd)

    def test_manta_inputs(self):
        """Test manta_input_net() with both sequence and abundance configs"""
        for config, label in [(self.net_config, "sequence-to-taxonomy"), (self.abd_config, "abundance-table")]:
            with self.subTest(input_type=label):
                self.assertTrue(manta_input_net(config), f"manta_input_net failed for {label}")

    def test_run_manta(self):
        """Test run_manta() with both input configs"""
        for config, label in [(self.net_config, "sequence-to-taxonomy"), (self.abd_config, "abundance-table")]:
            with self.subTest(input_type=label):
                self.assertTrue(manta_input_net(config), f"manta_input_net failed before run_manta for {label}")
                run_manta(config)


if __name__ == "__main__":

    unittest.main()
