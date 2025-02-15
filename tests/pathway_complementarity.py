import unittest
import os
import sys

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Add the directory to the system path
sys.path.append(script_dir)


import yaml
from ..microbetag.config import Config

config_file = sys.argv[1]

with open(config_file, 'r') as yaml_file:
    try:
        config = Config(yaml.safe_load(yaml_file), config_file)
    except yaml.YAMLError as exc:
        raise exc


