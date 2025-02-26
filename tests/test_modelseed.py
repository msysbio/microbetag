"""
Genome scale metabolic model reconstructions are required in the microbetag framework when
the seed complementarity feature is enabled.
The user may provide their own GEMs -- this is strongly suggested as the user's GEMs
can be curated to fix the experiment's specific conditions (e.g. medium composition)
as well as the metabolites and the reactions present in the network themselves.

In case the user does not provide their own GEMs, microbetag provides two approaches to build a GEM:
- using ModelSEEpy
- using CarveMe

Especially when using ModelSEEDpy for the reconstruction, medium can be of utmost importance,
since it's being used by the gapfilling algorithm to fill the gaps in the network.

"""

import os
import yaml
import unittest

from microbetag.config import Config
from microbetag.genres import GEMSReconstruction

root = os.path.dirname(os.path.dirname(__file__))

test_data = os.path.join(root, "test_data", "test_modelseed")

input_dir = os.path.join(test_data, "input_files")
output_dir = os.path.join(test_data, "output_files")



config_file = os.path.join(test_data, "config_v103_modelseed.yml")
with open(config_file, "r") as yaml_file:
    config = Config(yaml.safe_load(yaml_file), config_file)


class TestGEMSReconstruction(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.builder = None


    def test1_set_builder(self):

        # Test the GEMSReconstruction class
        TestGEMSReconstruction.builder = GEMSReconstruction(config)
        print("Test 1 passed")

    def test2_rast_annotate(self):

            self.builder.rast_annotate_genomes()
            print("Test 2 passed")

    def test3_build_modelseed(self):

        self.builder.modelseed_reconstructions()
        print("Test 3 passed")



if __name__ == "__main__":
    unittest.main()
