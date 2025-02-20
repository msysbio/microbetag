import os
import unittest
import subprocess
from microbetag.tools import phenotrex_genotype, phenotrex_predict

cwd = os.getcwd()
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
phen_classes = os.path.join(root_dir, "microbetag/mtg_maps_models/phenDB/classes/")

test_data  = os.path.join(root_dir, "test_data", "test_phenotrex")
output_dir = os.path.join(test_data, "output_files")
bins       = os.path.join(test_data, "input_files")

class Config:

    def __init__(self):

        os.makedirs(output_dir, exist_ok=True)

        self.bins_path = bins
        self.phen_classes = phen_classes

        self.output_dir = output_dir
        self.predictions_path = output_dir
        self.genotypes_file = os.path.join(self.output_dir, "train.genotype")
        self.threads = 2
        self.min_proba = 0.6
        self.cwd = cwd


class TestPhenotrex(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        cls.config = Config()

    def testGenotype(self):

        phenotrex_genotype(config=self.config)

        genotype = os.path.join(self.config.output_dir, "train.genotype")
        cmd = " ".join(["wc -l", genotype])
        result = subprocess.check_output(cmd, shell=True, text=True)
        nlines = int(result.split(" ")[0])

        self.assertTrue( nlines == 2 )

    def  testPredict(self):

        phenotrex_predict(config=self.config)


if __name__ == "__main__":

    # NOTE: They will be performed alphabetically
    unittest.main()
