
import os
import yaml
import unittest
from microbetag.config import Config
from microbetag.seed_complementarity import ExportSeedComplementarities

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
test_data = os.path.join(root_dir, "test_data", "test_seed_compl")
output_dir = os.path.join(test_data, "output_files")

config_file = os.path.join(test_data, "config_v103_test_seed_compl.yml")
with open(config_file, 'r') as yaml_file:
    config = Config(yaml.safe_load(yaml_file), config_file)



seed_complements = ExportSeedComplementarities(config)

seed_complements.update()

print("updated ok")

seed_complements.map_carveme_seeds()

seed_complements.module_related_seeds()

seed_complements.export_seed_complements()


# class TestSeedComplementarity(unittest.TestCase):


#     @classmethod
#     def setUpClass(cls):

#         cls.config = config


#     def TestWithCarvemeModels(self):

#         seed_complements = ExportSeedComplementarities(self.config)
#         print("...... wtf")
#         seed_complements.update()

#         print("updated ok")

#         seed_complements.map_carveme_seeds()

#         seed_complements.module_related_seeds()

#         seed_complements.export_seed_complements()




# if __name__ == "__main__":


    # unittest.main()


