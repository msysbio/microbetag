import os
import unittest
import pandas as pd

from microbetag.tools import run_manta
from microbetag.config import load_abundance
from microbetag.helpers import manta_input_net


# Directories
root_dir   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
test_data  = os.path.join(root_dir, "test_data", "test_manta")
output_dir = os.path.join(test_data, "output_files")

# Using abundance table to map sequence ids to taxonomies ==  USED FOR THE MS // TAKES TOO LONG, REPLACE WITH SHORTER FILES
abd_table_dir = os.path.join(test_data, "input_files", "based_on_abd_table")
abd_table     = os.path.join(abd_table_dir, "thirty_Samples.tsv")  # "plaque_abd_tab.tsv"
net_edgelist  = os.path.join(abd_table_dir, "edgelist.csv")  # "plaque_edgelist.tsv"
outdir_abd    = os.path.join(output_dir, "based_on_abd_table")

# Using a sequence to taxonomy file to map sequence ids to taxonomies
input_net_dir    = os.path.join(test_data, "input_files", "based_on_net")
edgelist         = os.path.join(input_net_dir, "edgelist.csv")
seq_tax_map_file = os.path.join(input_net_dir, "seq2taxonomy.tsv")
outdir_net       = os.path.join(output_dir, "based_on_net")

class NetConfig:
    """Config-like class for the case a network is being used"""

    def __init__(self, outdir):

        os.makedirs(outdir, exist_ok=True)
        self.output_dir = outdir

        # Specify case to use
        self.network = edgelist

        seq_tax_map          = pd.read_csv(seq_tax_map_file, sep="\t")
        seq_tax_map.columns  = ["sequence_id", "taxonomy"]
        self.seq_to_taxon_df = seq_tax_map
        self.seq_ids         = seq_tax_map[seq_tax_map.columns[0]].unique().tolist()


class AbdTableConfig:

    """Config-like class for the case an abundance table is being used"""

    def __init__(self, outdir):

        os.makedirs(outdir, exist_ok=True)
        self.output_dir = outdir

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


class TestManta(unittest.TestCase):
    """Unit-test class to test the two main functions regarding manta"""

    @classmethod
    def setUpClass(cls):
        # This is called once for the entire class before any test runs
        cls.net_config = NetConfig(outdir_net)
        cls.abd_config = AbdTableConfig(outdir_abd)

    def test1MantaS2T(self):
        """Test with a user's sequence to taxonomy file"""

        # This function will create the basenet.cyjs file, which will be then used by the run_manta() function
        self.assertTrue(manta_input_net(self.net_config))

        run_manta(self.net_config)
        print("Manta test using sequence to taxonomy file ran successfully")

    def test2MantaAbdTable(self):
        """
        Test with an abundance table as input fille;
        A network is again required but not a sequence to taxonomy map file, since the abundance table is provided.
        """

        # Again, the manta_input_net() function will create the basenet.cyjs file
        self.assertTrue(manta_input_net(self.abd_config))

        run_manta(self.abd_config)

        print(
            "Manta test using abundance table to map sequence id to taxonomy ran successfully"
        )


if __name__ == "__main__":

    unittest.main()
