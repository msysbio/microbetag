import os
import shutil
import unittest
from pathlib import Path

from microbetag.utils import ko_list_parser, bin_kos_to_file, merge_ko
from microbetag.tools import kegg_annotation

# Project root directory
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Test data paths
test_data_dir = os.path.join(root, "test_data", "test_kegg_annotation")

# Input files
input_dir = os.path.join(test_data_dir, "input_files")
faas      = [
    os.path.join(input_dir, f)
    for f in os.listdir(input_dir)
    if f.endswith(".faa")
]
bin_ids   = [
    os.path.splitext(os.path.basename(faa))[0]
    for faa in faas
]
threads   = 2

# KEGG database paths
kegg_db_dir = os.path.join(root, "ext_data", "kofam_database")
ko_list     = os.path.join(kegg_db_dir, "ko_list_tests")  # Subset used for faster testing

# Output files
output_dir = os.path.join(test_data_dir, "output_files")
hmmout_dir = os.path.join(output_dir, "hmmout")
ko_merged  = os.path.join(output_dir, "ko_merged.txt")

# Remove ouput dir from previous run, if any
prev_run = Path(output_dir)
if prev_run.exists():
    print("Removing output folder from previous run.")
    shutil.rmtree(prev_run)

os.makedirs(output_dir, exist_ok=True)
os.makedirs(hmmout_dir, exist_ok=True)


class testKEGGAnnotation(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        cls.ko_dic = None

    def test1_list_parser(self):

        ko_dic = ko_list_parser(ko_list)
        testKEGGAnnotation.ko_dic = ko_dic

    def test2_kegg_annotation(self):

        for faa, bin_id in zip(faas, bin_ids):

            bin_kos_dir = os.path.join(hmmout_dir, bin_id)

            os.makedirs(bin_kos_dir, exist_ok=True)

            _ = kegg_annotation(
                faa, bin_id, hmmout_dir, kegg_db_dir, self.ko_dic, threads
            )

            bin_kos_to_file(hmmout_dir=bin_kos_dir, bin_id=bin_id)

    def test3_merge_ko(self):

        merge_ko(hmmout_dir, ko_merged)

        # Check whether ko_merged exists and has a non-zero size
        self.assertTrue(os.path.exists(ko_merged), f"File {ko_merged} does not exist.")
        self.assertTrue(os.stat(ko_merged).st_size > 0, f"File {ko_merged} is empty.")


if __name__ == "__main__":
    unittest.main()
