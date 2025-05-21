import os
import unittest

# Main microbetag script
root_dir        = os.path.dirname(os.path.dirname(__file__))
microbetag_main = os.path.join(root_dir, "microbetag/microbetag.py")

# Input/output directories
test_data  = os.path.join(root_dir, "test_data", "test_microbetag")
output_dir = os.path.join(test_data, "mtg_complete_output")

# Config file
config_file = os.path.join(test_data, "config_mtg.yml")

# If input files are compressed - github
input_dir = os.path.join(test_data, "input_files")

if not os.path.isdir(input_dir):

    input_tar = ".".join([input_dir, "tar.gz"])

    if os.path.exists(input_tar):
        os.system(f"tar -zxvf {input_tar} -C {test_data}")

# Path to ko_merged.txt - decompress if needed
ko_merged = os.path.join(input_dir, "ko_merged.txt")

if not os.path.exists(ko_merged):

    ko_merged_gz = ".".join([ko_merged, "gz"])
    os.system(f"gunzip {ko_merged_gz}")


# Test
class testMicrobetag(unittest.TestCase):

    def testMicrobetagRun(self):

        params = ["microbetag", "--config", config_file]
        cmd    = " ".join(params)

        os.system(cmd)

        self.assertTrue(any(x for x in os.listdir(output_dir) if x.endswith(".cx2")))


if __name__ == "__main__":

    unittest.main()
