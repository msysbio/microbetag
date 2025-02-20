"""
We will use the 7-bins dev data set and its data products for this test.
"""
import unittest
import os
import yaml
from microbetag.config import Config
from microbetag.build_mtg_cx2 import build_pseudo_cx
from microbetag.utils import convert_to_json_serializable
from microbetag.build_mtg_cx2 import build_ndex2_net

# Get the directory of the current script
root_dir    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
test_data   = os.path.join(root_dir, "test_data", "test_build_cx2")
config_file = os.path.join(test_data, "config_v103.yml")


class TestBuildingCX2(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # This is called once for the entire class before any test runs
        cls.pseudo_cx_serialized = None

        # Check if config does have what's necessary for the build_pseudo_cx()
        with open(config_file, 'r') as yaml_file:
            cls.config = Config(yaml.safe_load(yaml_file), config_file)


    def test_build_pseudo_cx(self):
        """ Building the pseudo cx network with the microbetag annotations """


        # Test build_pseudo_cx()
        try:
            annotated_network = build_pseudo_cx(self.config)
        except Exception as e:
            print(f"Exception occurred: {e}")

        # Test serialization of the pseudo cx object
        try:
            pseudo_cx_serialized = convert_to_json_serializable(annotated_network)
        except Exception as e:
            print(f"Exception occurred: {e}")

        TestBuildingCX2.pseudo_cx_serialized = pseudo_cx_serialized
        self.assertTrue(len(annotated_network) == 10)


    def test_convert_pseudo_cx_with_ndex2(self):
        """ Converting the pseudo cx microbetag annotated network to an actual CX2 format """

        if TestBuildingCX2.pseudo_cx_serialized:
            # Use a pseudo cx object (list) as returned by the previous test
            build_ndex2_net(
                TestBuildingCX2.pseudo_cx_serialized,
                outfile=os.path.join(self.config.output_dir, "unittest_output_on_the_fly.cx2")
            )
        else:
            # Use an pseudo cx file
            pseudo_cx = os.path.join(root_dir, "ext_data", "input_files", "pseudo_cx_annotated_net.cx")
            build_ndex2_net(pseudo_cx, outfile=os.path.join(self.config.output_dir, "unittest_output_on_prev_built_pseudo.cx2"))


if __name__ == "__main__":

    unittest.main()



