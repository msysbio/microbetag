import os
import unittest

from microbetag.utils import ko_list_parser, bin_kos_to_file, merge_ko
from microbetag.tools import kegg_annotation

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

test_data = os.path.join(root, "test_data")
test_data = os.path.join(test_data, "test_kegg_annotation")

# Input files
input_dir = os.path.join(test_data, "input_files")
faas      = [os.path.join(input_dir, x) for x in os.listdir(input_dir) if x.endswith(".faa")]
bin_ids   = [os.path.splitext(faa)[0].split("/")[-1] for faa in faas]
threads   = 2

# Database files
# NOTE (Haris Zafeiropoulos, 2025-05-17):
# The `ko_list_tests` is part of the original `ko_list` file and is being used here for time-efficiency
kegg_db_dir = os.path.join(root, "ext_data/kofam_database")
ko_list     = os.path.join(kegg_db_dir, "ko_list_tests")

# Output files
kegg_annotations = os.path.join(test_data, "output_files")
hmmout_dir       = os.path.join(kegg_annotations, "hmmout")

os.makedirs(hmmout_dir, exist_ok=True)

ko_merged = os.path.join(kegg_annotations, "ko_merged.txt")


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

        self.assertTrue(os.stat(ko_merged).st_size == 0)


if __name__ == "__main__":
    unittest.main()
