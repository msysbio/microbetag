import os
import shutil
import unittest
from pathlib import Path

from microbetag.tools import run_prodigal

cwd      = os.getcwd()
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

test_data   = os.path.join(root_dir, "test_data", "test_prodigal")
input_files = os.path.join(test_data, "input_files")
outdir  = os.path.join(test_data, "output_files")

# Remove previous output folder
if Path(outdir).exists():
    print("Removing output folder from previous run.")
    shutil.rmtree(Path(outdir))

# Get new i/o points
bin_fa    = os.path.join(input_files, "bin_101.fa")
bin_id, _ = os.path.splitext(bin_fa)
bin_id    = os.path.basename(bin_id)  # bin_101

os.makedirs(outdir, exist_ok=True)


class testProdigal(unittest.TestCase):

    def testProdigal(self):

        run_prodigal(bin_fa, bin_id, outdir)

        self.assertTrue(os.path.exists(os.path.join(outdir, bin_id + ".faa")))


if __name__ == "__main__":

    unittest.main()
