import os
import yaml
import unittest
from pathlib import Path

# from microbetag.config import Config
from microbetag.tools import run_prodigal
from microbetag.wrappers import build_genres


# root_dir  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
root_dir  = Path(".").parent.resolve()
test_data = root_dir / "test_data" / "test_carve"

# Get configuration based on the config YAML file
config_file = test_data / "config_carve.yml"

class Config:
    def __init__(self, config_dict):
        for key, val in config_dict.items():
            # Prefer "value" over "dir_path"
            if isinstance(val, dict):
                if "value" in val:
                    setattr(self, key, val["value"])
                elif "dir_path" in val:
                    setattr(self, key, test_data / val["dir_path"])
                else:
                    setattr(self, key, None)
            else:
                setattr(self, key, val)

    def __repr__(self):
        attrs = ", ".join(f"{k}={v!r}" for k, v in self.__dict__.items())
        return f"Config({attrs})"


with open(config_file, "r") as yaml_file:
    c = yaml.safe_load(yaml_file)

config = Config(c)
config.bin_filenames = [
    os.path.join(config.for_reconstructions, file) for file in os.listdir(config.for_reconstructions)
]

# Remove any .xml file that may be in the output folder from previous tests
for file_path in Path(config.genres).glob("*.xml"):
    file_path.unlink()  # This deletes the file


class testBuildGemWithCarve(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.config = config

    def test_carve_fraggenescan(self):

        build_genres(self.config)

    def test_carve_prodigal(self):

        self.config.gene_predictor = "prodigal"

    #     run_prodigal(bin_fa, bin_id, outdir)

    def test_carve_aminoacid(self):

        # self.config.sequence_files_for_reconstructions = "input_files/faa"
        self.config.sc_input_type = "proteins_faa"
        self.config.for_reconstructions = self.config.reconstructions = test_data / "input_files" / "faa"
        self.config.bin_filenames = [
            os.path.join(config.for_reconstructions, file) for file in os.listdir(config.for_reconstructions)
        ]

        build_genres(self.config)


if __name__ == "__main__":
    unittest.main()
