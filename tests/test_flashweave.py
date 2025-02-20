import os
import yaml
import unittest

from microbetag.config import Config
from microbetag.tools import run_flashweave


root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

test_data = os.path.join(root_dir, "test_data", "run_flashweave_test/")

config_file = os.path.join(test_data, "config_v103_test_fw.yml")
with open(config_file, 'r') as yaml_file:
    config = Config(yaml.safe_load(yaml_file), config_file)


class TestRunFlashweave(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        cls.config = config


    def test_run_flashweave(self):

        run_flashweave(config=self.config)



if __name__ == "__main__":

    unittest.main()
