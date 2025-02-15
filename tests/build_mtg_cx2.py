import unittest
import os, sys
import json
import yaml

# Get the directory of the current script
repo_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# # Add the directory to the system path
# sys.path.append(repo_dir)

from microbetag.config import Config
from microbetag.build_mtg_cx2 import build_cx_annotated_graph
from microbetag.utils import convert_to_json_serializable
from microbetag.build_mtg_cx2 import build_ndex2_net



if __name__ == "__main__":
    """
    Build an annotated .cx using already build objects
    """

    config_file = os.path.join(repo_dir, "ext_data/config_v103.yml")

    with open(config_file, 'r') as yaml_file:
        config = Config(yaml.safe_load(yaml_file), config_file)

    annotated_network = build_cx_annotated_graph(config)

    with open("pseudo.cx", "w") as f:
            annotated_network2file = convert_to_json_serializable(annotated_network)
            json.dump(annotated_network2file, f)

    build_ndex2_net("pseudo.cx")





