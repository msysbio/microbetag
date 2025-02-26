"""
Genome scale metabolic model reconstructions are required in the microbetag framework when
the seed complementarity feature is enabled.
The user may provide their own GEMs -- this is strongly suggested as the user's GEMs
can be curated to fix the experiment's specific conditions (e.g. medium composition)
as well as the metabolites and the reactions present in the network themselves.

In case the user does not provide their own GEMs, microbetag provides two approaches to build a GEM:
- using ModelSEEpy
- using CarveMe
"""

import unittest
import os, yaml

from microbetag.config import Config
from microbetag.genres import GEMSReconstruction

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
test_data = os.path.join(root_dir, "test_data", "test_build_genres")

# Get configuration based on the config YAML file
config_file = os.path.join(test_data, "config_v103_test_carve.yml")
with open(config_file, 'r') as yaml_file:
    config = Config(yaml.safe_load(yaml_file), config_file)

"""
NOTE: through the configuration file (.yml) the user may set
on how to build the GEMs and what input files to use
This is rather important for GENREs reconstruction, as the user may use their own annotation files
or from previous runs.
In this example, the user is using the carveme to build the GEMs, along with the Prodigal annotation files.
"""



class testBuildGemWithCarve(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        cls.config = config
        cls.GEMSReconstruction = None

    def test1_GEMSReconstruction(self):
        """
        GEMSReconstruction() inits by setting a set of arguments based on the user's configuration file.
        """
        testBuildGemWithCarve.GEMSReconstruction = GEMSReconstruction(self.config)


    def test2_runCarveme(self):

        self.GEMSReconstruction.carve_reconstructions()



if __name__ == '__main__':
    unittest.main()
