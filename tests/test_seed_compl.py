import os
import unittest

from microbetag.seed_complementarity import ExportSeedComplementarities
from microbetag.helpers import MappingPaths

maps = MappingPaths()

root_dir   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
test_data  = os.path.join(root_dir, "test_data/test_seed_compl")
models_dir = os.path.join(test_data, "input_files")

# NOTE (Haris Zafeiropoulos, 2025-05-29):
# Outfiles will be overwritten, so no need to remove previous run outputs in this case.
out_dir         = os.path.join(test_data, "output_files")
out_dir_wt_sets = os.path.join(test_data, "output_files_wt_sets")
out_dir_bigg    = os.path.join(test_data, "output_files_bigg")

previous_nonseeds   = os.path.join(out_dir, "nonSeedSetDic.json")
previous_confidence = os.path.join(out_dir, "confidenceDic.json")


class Config:

    def __init__(self, out_dir):

        # Directory where GENREs are stored
        self.genres = self.for_reconstructions = models_dir

        # By default, microbetag will check whether both scores and complements files have been previously built.
        # If not, it will try to calculate them, except if you ask not to,
        # i.e. having ge_scors and/or get_complements as False
        self.get_scores      = True
        self.get_complements = True

        # Directory where to save seed complementarity - related files
        os.makedirs(out_dir, exist_ok=True)

        self.seeds_outdir    = out_dir
        self.seed_compl_pckl = os.path.join(out_dir, "seed_complements.pckl")
        self.module_seeds    = os.path.join(self.seeds_outdir, "kegg_module_related_seeds.pckl")
        self.module_nonseeds = os.path.join(
            self.seeds_outdir, "kegg_module_related_nonseeds.pckl"
        )

        self.seed_ko_mo                = maps.seed_ko_mo
        self.genre_reconstruction_with = "carveme"
        self.metanetx_compounds        = maps.metanetx_compounds

        # By default, this argument is True and not part of the complete pipeline YAML template.
        # We only provide the option in case you need BiGG seed sets,
        # non-seed sets out of the seed complemenarity concept.
        self.switch_namespace = True

        self.threads       = 2
        self.skip_sets     = False
        self.prev_conf     = None
        self.prev_nonseeds = None


# Case 1: getting seed complementarities after calculating seed and non-seed sets
c = Config(out_dir=out_dir)

# Case 2: geting complementarities by using previously computed seed and non-seed sets,
# in this case those computed in Case 1.
c_wt_sets               = Config(out_dir=out_dir_wt_sets)
c_wt_sets.skip_sets     = True
c_wt_sets.prev_conf     = previous_confidence
c_wt_sets.prev_nonseeds = previous_nonseeds

# Case 3: getting just the seed and non-seed sets - no complementarities - without mapping BiGG to ModelSEED
c_bigg                  = Config(out_dir=out_dir_bigg)
c_bigg.get_complements  = False
c_bigg.switch_namespace = False


class TestSeedComplementarity(unittest.TestCase):

    def test1WihtoutSets(self):

        ss = ExportSeedComplementarities(config=c)
        ss.get_sets()
        ss.get_scores_and_compls()

        print("Case 1 is now completed.")

    def test2WithUsersModelsAndSets(self):

        ss = ExportSeedComplementarities(config=c_wt_sets)
        ss.get_sets()
        ss.get_scores_and_compls()

        print("Case 2 is now completed.")

    def test3BiggSets(self):

        ss = ExportSeedComplementarities(config=c_bigg)
        ss.get_sets()

        print("Case 3 is now completed.")


if __name__ == "__main__":

    unittest.main()
