"""
This test will check:

1. The taxon_kos_per_module() function that returns a dictionary with taxa as keys (via their conrresponding sequence id)
   and the KEGG ORTHOLOGY terms present in their genomes per KEGG MODULE (https://www.genome.jp/kegg/module.html)
2. The all_alternatives() function that builds a JSON file with all
3. The all_complements() function that

These 3 function are used by the export_pathway_complementarities() function which wraps them to be used in the main microbetag.py script.

"""

import os
import unittest

import microbetag

from microbetag.helpers import MappingPaths
from microbetag.utils import load_merged_ko_file
from microbetag.pathway_complementarity import (
    taxon_kos_per_module,
    a_modules_maps,
    all_alternatives,
    all_complements,
)

# Get the directory of the current script and the test_data directory
root_dir  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
test_data = os.path.join(root_dir, "test_data", "test_path_compl")

# Input
input_dir = os.path.join(test_data, "input_files")
# ko_merged.txt is the output of the merge_ko() function; run_kegg_annotation.py test
ko_merged = os.path.join(input_dir, "ko_merged_7bins.txt")

if not os.path.exists(ko_merged):
    try:
        os.system(f"gunzip {ko_merged}")
    except Exception:
        raise ("ko_merged (3-column KO annotation file, is not provided)")

# Output
output_dir = os.path.join(test_data, "output_files")
alts_file  = os.path.join(output_dir, "alternatives.json")
compl_file = os.path.join(output_dir, "complementarities.json")
os.makedirs(output_dir, exist_ok=True)

# In this test, we use two approaches for the same thing: getting the paths to the mapping files:
#
# 1. using the MappingPaths class; a wrapper for the microbetag module.
#   To this end, we make the Config class that has the root working directory as an attribute.
#
# 2.using the microbetag module directly and its attributes

class Config:
    def __init__(self):
        self.cwd = root_dir


class testPathCompl(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.map_paths          = MappingPaths()
        cls.pivot_df           = load_merged_ko_file(ko_merged)
        cls.bin_kos_per_module = None
        cls.bins_alternatives  = None

    def test1_taxon_kos_per_module(self):

        bin_kos_per_module = taxon_kos_per_module(
            bins_kos_df                    = self.pivot_df,
            ref_ko_per_module = self.map_paths.ref_ko_per_module,  # microbetag.KEGG_TERMS_PER_MODULE
        )

        self.assertTrue(len(bin_kos_per_module.keys()) == 7)

        testPathCompl.bin_kos_per_module = bin_kos_per_module

        print("Test 1: taxon_kos_per_module() PASSED")

    def test2_all_alternatives(self):

        bins_alternatives = all_alternatives(
            bin_kos_per_module           = self.bin_kos_per_module,
            modules_definitions_json_map = self.map_paths.modules_definitions_json_map,
            alts_output_file             = alts_file,
        )

        testPathCompl.bins_alternatives = bins_alternatives

        print("Test 2: all_alternatives() PASSED")

    def test3_all_complements(self):

        module_to_map = a_modules_maps(
            microbetag._KEGG_MODULES_TO_MAPS
        )  # self.map_paths.kegg_modules_to_maps

        complements = all_complements(
            self.bin_kos_per_module,
            self.bins_alternatives,
            module_to_map,
            compl_file,
            tinyurl=False,
        )

        self.assertTrue(len(complements.keys()) == 7)
        print("Test 3: all_complements() PASSED")


if __name__ == "__main__":

    unittest.main()
