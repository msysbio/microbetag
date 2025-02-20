import os
import unittest

from microbetag.utils import ko_list_parser, bin_kos_to_file, merge_ko
from microbetag.tools import kegg_annotation   # Import the function to be tested

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

test_data = os.path.join(root, "test_data")
test_data = os.path.join(test_data, "run_kegg_annotation")

# Input files
input_dir = os.path.join(test_data, "input_files")
faas = [ os.path.join(input_dir, x) for x in os.listdir(input_dir) if x.endswith(".faa") ]
bin_ids = [os.path.splitext(faa)[0].split("/")[-1] for faa in faas ]
threads = 2

# Database files
kegg_db_dir = os.path.join(test_data, "kofam_database")
ko_list = os.path.join(kegg_db_dir, 'ko_list_tests')  # Part of the ko_list file to be used for testing

# Output files
kegg_annotations = os.path.join(test_data, "output_files")
hmmout_dir = os.path.join(kegg_annotations, 'hmmout')
os.makedirs(hmmout_dir, exist_ok=True)
ko_merged = os.path.join(kegg_annotations, 'ko_merged.txt')


class testKEGGAnnotation(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        cls.ko_dic = None


    def test_alist_parser(self):

        ko_dic = ko_list_parser(ko_list)
        testKEGGAnnotation.ko_dic = ko_dic


    def test_bkegg_annotation(self):

        for faa, bin_id in zip(faas, bin_ids):
            os.makedirs(os.path.join(hmmout_dir, bin_id), exist_ok=True)
            _ = kegg_annotation(
                faa,
                bin_id,
                hmmout_dir,
                kegg_db_dir,
                self.ko_dic,
                threads
            )

            bin_kos_dir = os.path.join(hmmout_dir, bin_id)
            os.makedirs(bin_kos_dir, exist_ok=True)

            bin_kos_to_file(hmmout_dir=bin_kos_dir , bin_id=bin_id)

    def test_cmerge_ko(self):
        merge_ko(hmmout_dir, ko_merged)



if __name__ == "__main__":
    unittest.main()
