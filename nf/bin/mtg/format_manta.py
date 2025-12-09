#!/usr/bin/env python3

"""
Script to apply transformation from 3-col edgelist to .cyjs using microbetag's corresponding function (manta_input_net)
"""

import sys
from pathlib import Path
from mtg_annotate import load_data
from microbetag.helpers import manta_input_net

class Config:
    def __init__(self):

        abd_data = sys.argv[1]
        org_net  = sys.argv[2]

        self.abundance_file    = abd_data
        self.network           = org_net
        # Name of the formatted network file (output)
        self.base_network_file = Path(org_net).with_suffix(".cyjs")

c = Config()
cd = load_data(c)
manta_input_net(cd)
