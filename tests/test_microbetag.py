import os
import unittest

# Main microbetag script
root_dir = os.path.dirname(os.path.dirname(__file__))
microbetag_main = os.path.join(root_dir, "microbetag.py")

# Input test files
test_data = os.path.join(root_dir, "test_data", "test_microbetag")

# Config file
config_file = os.path.join(test_data, "config_v103.yml")

# If input files are compressed - github
input_dir = os.path.join(test_data, "input_files")
if not os.path.isdir(input_dir):
    input_tar = ".".join([input_dir, "tar.gz"])
    if os.path.exists(input_tar):
        os.system(f"tar -zxvf {input_tar} -C {test_data}")

output_dir = os.path.join(test_data, "mtg_complete_output")


class testMicrobetag(unittest.TestCase):

    def testMicrobetagRun(self):

        params = ["python", microbetag_main, config_file]
        cmd = " ".join(params)
        os.system(
            cmd
        )

        output_files = os.listdir(output_dir)
        self.assertTrue(
            any(x for x in output_files if x.endswith(".cx2"))
        )



if __name__ == "__main__":

    unittest.main()
