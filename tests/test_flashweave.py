import os
import copy
import yaml
import unittest

from microbetag.config import Config
from microbetag.tools import run_flashweave


root_dir    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
test_data   = os.path.join(root_dir, "test_data", "test_flashweave")
config_file = os.path.join(test_data, "config_test_fw.yml")

# Initially the configuration mentions a metadata file
with open(config_file, "r") as yaml_file:
    config_meta         = Config(yaml.safe_load(yaml_file), config_file)
    config_meta.network = os.path.join(config_meta.output_dir, "network_metadata.edgelist")

# We make a second config and we shut down the metadata file part
with open(config_file, "r") as yaml_file:
    config               = Config(yaml.safe_load(yaml_file), config_file)
    config.metadata      = "false"
    config.metadata_file = None


class TestRunFlashweave(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        cls.config      = config
        cls.config_meta = config_meta

    def test_run_flashweave(self):

        run_flashweave(config=self.config)

    def test_run_flashweave_metadata(self):

        run_flashweave(config=self.config_meta)


if __name__ == "__main__":

    unittest.main()
