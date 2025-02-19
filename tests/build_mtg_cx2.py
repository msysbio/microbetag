import unittest
import os
import yaml
from microbetag.config import Config
from microbetag.build_mtg_cx2 import build_pseudo_cx
from microbetag.utils import convert_to_json_serializable
from microbetag.build_mtg_cx2 import build_ndex2_net



# Get the directory of the current script
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class TestBuildingCX2(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # This is called once for the entire class before any test runs
        cls.pseudo_cx_serialized = None

    def test_build_pseudo_cx(self):
        """ Building the pseudo cx network with the microbetag annotations """
        # Check if config does have what's necessary for the build_pseudo_cx()
        config_file = os.path.join(root_dir, "ext_data/config_v103_qiita.yml")

        with open(config_file, 'r') as yaml_file:
            config = Config(yaml.safe_load(yaml_file), config_file)

        # Test build_pseudo_cx()
        try:
            annotated_network = build_pseudo_cx(config)
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
            print("This is based on the previous test....")
            build_ndex2_net(TestBuildingCX2.pseudo_cx_serialized)
        else:
            # Use an pseudo cx file
            print("Heck.. this is based on a previous cx.")
            pseudo_cx = os.path.join(root_dir, "ext_data", "input_files", "pseudo_cx_annotated_net.cx")
            build_ndex2_net(pseudo_cx)


if __name__ == "__main__":

    unittest.main()



