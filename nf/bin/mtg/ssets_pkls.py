#!/usr/bin/env python3
"""
KEGG Module Compound Analysis Script

Input files:
- seeds.json: JSON file containing SEED compound sets keyed by model names
- nonseeds.json: JSON file containing non-SEED compound sets keyed by model names

Output files:
- keggm_seeds.pkl: Pickled DataFrame of SEED compounds intersecting with KEGG modules
- keggm_nonseeds.pkl: Pickled DataFrame of non-SEED compounds intersecting with KEGG modules

"""

import json
import pickle
import pandas as pd
from microbetag.seed_complementarity import get_kegg_module_related, kegg_module_related_intersect

seed_ko_mo      = "/workspace/microbetag/mtg_maps_models/kegg_mappings/seedId_keggId_module.tsv"
module_seeds    = "keggm_seeds.pkl"
module_nonseeds = "keggm_nonseeds.pkl"

modules_ms_cpd = get_kegg_module_related(seed_ko_mo)


for files in [("nonseeds.json", module_nonseeds), ("seeds.json", module_seeds)]:

    json_file, pickle_file = files

    with open(json_file, "r") as f:
        dict = json.load(f)

    dict_tmp = {}
    for k, v in dict.items():
        dict_tmp[k] = [
            kegg_module_related_intersect(v, modules_ms_cpd)
        ]
    df = pd.DataFrame.from_dict(dict_tmp)

    with open(pickle_file, "wb") as f:
        pickle.dump(df.T, f)
