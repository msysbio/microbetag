#!/usr/bin/env python3

import os
import sys
from pathlib import Path
from microbetag.utils import load_merged_ko_file
from microbetag.pathway_complementarity import export_pathway_complementarities


class Config:

    kegg_mappings                = Path("/workspace/microbetag/mtg_maps_models/kegg_mappings/")
    kegg_modules_to_maps         = kegg_mappings / "module_map_pairs.tsv"
    ref_ko_per_module            = kegg_mappings / "kegg_terms_per_module.tsv"
    modules_definitions_json_map = kegg_mappings / "module_definition_map.json"
    module_descriptions          = kegg_mappings / "module_descriptions"
    # User's args
    alts_file  = sys.argv[1]
    pc_file    = sys.argv[2]
    ko_merged  = sys.argv[3]
    tinyurl    = sys.argv[4]
    threads    = int(sys.argv[5])


config = Config()

# Load 3-col file with KEGG ORTHOLOGY terms for each genome
pivot_df = load_merged_ko_file(config.ko_merged)

# Export path compls
_, _ = export_pathway_complementarities(config, pivot_df)
