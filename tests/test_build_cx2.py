"""
We will use the 7-bins dev data set and its data products for this test.
"""
import unittest
import os
import yaml

from microbetag.config import Config
from microbetag.build_mtg_cx2 import mtg_annotate_network


# Get the directory of the current script
root_dir    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
test_data   = os.path.join(root_dir, "test_data", "test_build_cx2")
config_file = os.path.join(test_data, "config_buildCX2.yml")


class TestBuildingCX2(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        # # This is called once for the entire class before any test runs
        # cls.pseudo_cx_serialized = None

        # Check if config does have what's necessary for the build_pseudo_cx()
        with open(config_file, "r") as yaml_file:
            cls.config = Config(yaml.safe_load(yaml_file), config_file)

    def test_build_pseudo_cx(self):
        """Tests building the CX2 network with the microbetag annotations"""

        mtg_annotate_network(self.config)


if __name__ == "__main__":

    unittest.main()
