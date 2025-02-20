import os
import unittest
from microbetag.tools import run_prodigal

cwd = os.getcwd()
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

test_data = os.path.join(root_dir, "test_data", "test_prodigal")
input_files = os.path.join(test_data, "input_files")
output_dir = os.path.join(test_data, "output_files")

bin_fa = os.path.join(input_files, "bin_101.fa")
bin_id, extension = os.path.splitext(bin_fa)
bin_id = os.path.basename(bin_id)    # bin_101


class testProdigal(unittest.TestCase):

    def testProdigal(self):

        run_prodigal(bin_fa, bin_id, output_dir)

        self.assertTrue(os.path.exists(os.path.join(output_dir, bin_id + ".faa")))



if __name__ == "__main__":

    unittest.main()


