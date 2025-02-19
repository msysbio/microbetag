import unittest
import os
import pandas as pd

from microbetag.helpers import manta_net
from microbetag.tools import run_manta
from microbetag.config import load_abundance

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ext_data = os.path.join(root_dir, "ext_data")
input_dir = os.path.join(ext_data, "input_files")
output_dir = os.path.join(ext_data, "microbetag_run_carve")

class NetConfig:
    """ Config-like class for the case a network is being used """
    def __init__(self):

        # Specify case to use
        seq_tax_map_file = os.path.join(input_dir, "seq2taxonomy.tsv")
        self.base_network_file = os.path.join(output_dir, "basenet.cyjs")
        self.network = os.path.join(input_dir, "edgelist.csv")

        # Use-case independent but required part of the config
        seq_tax_map = pd.read_csv(seq_tax_map_file, sep="\t")
        seq_tax_map.columns = ["sequence_id", "taxonomy"]
        self.output_dir = output_dir
        self.seq_to_taxon_df = seq_tax_map
        self.seq_ids = seq_tax_map[seq_tax_map.columns[0]].unique().tolist()

class AbdTableConfig:
    """ Config-like class for the case an abundance tabele is being used """
    def __init__(self):

        # Specify case to use
        self.abundance_table = os.path.join(input_dir, "plaque_abd_tab.tsv")
        self.network = os.path.join(input_dir, "plaque_edgelist.tsv")
        self.base_network_file = os.path.join(output_dir, "plaque_basenet.cyjs")

        # Use-case independent but required part of the config
        self.seq_to_taxon_df, self.sequence_id_column_name, self.taxonomy_column_name = load_abundance(self.abundance_table)
        self.seq_ids = self.seq_to_taxon_df["sequence_id"].unique().tolist()
        self.output_dir = output_dir


class TestManta(unittest.TestCase):
    """Unit-test class to test the two main functions regarding manta"""

    @classmethod
    def setUpClass(cls):
        # This is called once for the entire class before any test runs
        cls.net_config = NetConfig()
        cls.abd_config = AbdTableConfig()

    def testMantaNet(self):
        """Test with a user's network as input fille"""
        self.assertTrue(manta_net(self.net_config))
        run_manta(self.net_config)

    def testMantaAbdTable(self):
        """
        Test with an abundance table as input fille;
        A network is again required but not a sequence to taxonomy map file, since the abundance table is provided.
        """
        self.assertTrue(manta_net(self.abd_config))
        run_manta(self.abd_config)



if __name__ == "__main__":

    unittest.main()

