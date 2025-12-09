#!/usr/bin/env python3

import os
import sys
from pathlib import Path
import microbetag
from microbetag.utils import extend_complements


class Config:
    kegg_mappings       = Path(microbetag._KEGG_MAPPINGS)
    module_descriptions = kegg_mappings / "module_descriptions"
    pc_file    = sys.argv[1]
    pc_percent = float(sys.argv[2])
    threads    = int(sys.argv[3])


config = Config()

extend_complements(
    complements_json = config.pc_file,
    descrps_path     = config.module_descriptions.as_posix(),
    pc_percent       = config.pc_percent,
    pc_dir           = Path(config.pc_file).parent.absolute(),
    n_workers        = config.threads
)
