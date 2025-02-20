import os
import unittest

import microbetag
from microbetag.helpers import Faprotax
from microbetag.tools import run_faprotax

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
test_data = os.path.join(root_dir, "test_data", "run_faprotax_test")
input_dir = os.path.join(test_data, "input_files")
output_dir = os.path.join(test_data, "output_files")

abundance_table = os.path.join(input_dir, "thirty_Samples.tsv")

class Config:
    def __init__(self):

        self.abundance_table = abundance_table
        self.taxonomy_column_name = "taxonomy"

        self.cwd = microbetag.__path__[0]
        self.output_dir = output_dir

        # This is actually a test on its own since it assumnes Faprotax class behave as it should
        faprotax = Faprotax(config=self)
        self.__dict__.update(vars(faprotax))

class TestFaprotax(unittest.TestCase):

    @classmethod
    def setUpClass(cls):  # \* https://docs.python.org/3/library/unittest.html#unittest.TestCase.setUpClass
        cls.conf = Config()

    def test_run_faprotax(self):

        run_faprotax(config=self.conf)


if __name__ == "__main__":

    unittest.main()



