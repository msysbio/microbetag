
import os
import unittest

from microbetag.tools import run_phylomint

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
test_data = os.path.join(root_dir, "test_data")
output_dir = os.path.join(test_data, "test_phylomint/output_files")
models_dir = os.path.join(test_data, "test_carve/output_files/reconstructions/GENREs/")


class Config:

    def __init__(self):
        self.users_models = True
        self.genres = models_dir
        self.for_reconstructions =  models_dir  #[os.path.join(models_dir, x) for x in os.listdir(models_dir)]
        self.seeds = output_dir
        self.threads = 2


class TestPhylomint(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.config = Config()

    def testWithUsersModels(self):

        run_phylomint(config=self.config)



if __name__ == "__main__":

    unittest.main()

