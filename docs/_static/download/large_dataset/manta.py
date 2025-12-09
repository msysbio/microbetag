import unittest
import os
import pandas as pd

from microbetag.helpers import manta_input_net
from microbetag.tools import run_manta
from microbetag.config import load_abundance

# Directories
root_dir = os.path.dirname(os.path.abspath(__file__))
outdir = os.path.join(root_dir, "manta_output")
os.makedirs(outdir, exist_ok=True)

# Using abundance table to map sequence ids to taxonomies ==  USED FOR THE MS // TAKES TOO LONG, REPLACE WITH SHORTER FILES
input_data = os.path.join(root_dir, "prep_output")
abd_table = os.path.join(
    input_data, "GTDB_tax_assigned_abundance_table.tsv"
)  # "plaque_abd_tab.tsv"
net_edgelist = os.path.join(
    input_data, "network_output.edgelist"
)  # "plaque_edgelist.tsv"


class AbdTableConfig:
    def __init__(self):
        """Config-like class for the case an abundance table is being used"""

        # Specify case to use
        self.abundance_table = abd_table
        self.network = net_edgelist
        self.base_network_file = os.path.join(outdir, "manta_basenet.cyjs")

        # Use-case independent but required part of the config
        (
            self.seq_to_taxon_df,
            self.sequence_id_column_name,
            self.taxonomy_column_name,
            _,  # delimeter
        ) = load_abundance(self.abundance_table)

        self.seq_ids = self.seq_to_taxon_df["sequence_id"].unique().tolist()
        self.outdir = outdir


class TestManta(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # This is called once for the entire class before any test runs
        cls.abd_config = AbdTableConfig()

    def testMantaAbdTable(self):

        # The manta_input_net() function will create the basenet.cyjs file
        self.assertTrue(manta_input_net(self.abd_config))

        # Run manta tool
        run_manta(self.abd_config)

        print("Manta ran successfully")


if __name__ == "__main__":

    unittest.main()
