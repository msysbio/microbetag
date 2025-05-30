import os
import unittest

import shutil
from pathlib import Path

from microbetag.helpers import Faprotax
from microbetag.tools import run_faprotax

root_dir        = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
test_data       = os.path.join(root_dir, "test_data", "test_faprotax")
input_dir       = os.path.join(test_data, "input_files")
output_dir      = os.path.join(test_data, "output_files")
abundance_table = os.path.join(input_dir, "thirty_Samples.tsv")

# Make sure output folder exists
os.makedirs(output_dir, exist_ok=True)

# Remove previous test outputs if any
folder = Path(output_dir) / "faprotax"
if folder.exists():
    shutil.rmtree(folder)


# Psuedo config class
class Config:

    def __init__(self):

        self.cwd = os.path.join(root_dir, "microbetag")  # This points to what is going to be packaged in the setup.py
        # so microbetag can access the mtg_map_models folder
        self.output_dir           = output_dir
        self.abundance_table      = abundance_table
        self.taxonomy_column_name = "taxonomy"
        self.__dict__.update(
            vars(Faprotax(config=self))
        )

class TestFaprotax(unittest.TestCase):

    @classmethod
    def setUpClass(cls):  # \* https://docs.python.org/3/library/unittest.html#unittest.TestCase.setUpClass
        cls.conf = Config()

    def test_run_faprotax(self):

        run_faprotax(config=self.conf)


if __name__ == "__main__":

    unittest.main()
