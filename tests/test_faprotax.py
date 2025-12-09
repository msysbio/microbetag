import os
import unittest

import shutil
from pathlib import Path

from microbetag.helpers import Faprotax
from microbetag.tools import run_faprotax

root_dir        = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
test_data       = root_dir / "test_data" / "test_faprotax"
input_dir       = test_data / "input_files"

outdir      = test_data / "output_files"
abundance_table = input_dir / "thirty_Samples.tsv"
taxonomy_col    = "taxonomy"
delimiter       = ","

# Make sure output folder exists
os.makedirs(outdir, exist_ok=True)

# Remove previous test outputs if any
folder = Path(outdir) / "faprotax"
if folder.exists():
    shutil.rmtree(folder)


# Psuedo config class
class Config:

    def __init__(self):

        self.cwd = os.path.join(root_dir, "microbetag")  # This points to what is going to be packaged in the setup.py
        # so microbetag can access the mtg_map_models folder
        self.outdir           = outdir.as_posix()
        self.abundance_table      = abundance_table.as_posix()
        self.taxonomy_column_name = taxonomy_col
        self.delimiter            = delimiter
        self.__dict__.update(
            vars(Faprotax(config=self))
        )

class TestFaprotax(unittest.TestCase):

    @classmethod
    def setUpClass(cls):       # https://docs.python.org/3/library/unittest.html#unittest.TestCase.setUpClass
        cls.conf = Config()

    def test_run_faprotax(self):

        run_faprotax(config=self.conf)


if __name__ == "__main__":

    unittest.main()
