import os
import unittest
from microbetag.tools import phenotrex_genotype, phenotrex_predict

cwd = os.getcwd()
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
phen_classes = os.path.join(root_dir, "microbetag/mtg_maps_models/phenDB/classes/")

test_data  = os.path.join(root_dir, "ext_data", "run_phenotrex_test")
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
        self.assertTrue(
            len(os.listdir(self.config.output_dir)) == 1
        )

    def  testPredict(self):

        phenotrex_predict(config=self.config)


if __name__ == "__main__":

    # NOTE: They will be performed alphabetically
    unittest.main()
