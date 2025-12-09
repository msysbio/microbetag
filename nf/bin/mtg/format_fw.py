#!/usr/bin/env python3

import os
import sys
import pandas as pd

# TODO (Haris Zafeiropoulos, 2025-11-10): do we need those two lines now?
os.environ["COBRAPY_CACHE_DIR"] = "/tmp/cobrapy_cache"
os.makedirs("/tmp/cobrapy_cache", exist_ok=True)

# temporarily redirect stdout
sys.stdout = open(os.devnull, 'w')
from microbetag.utils import detect_separator
sys.stdout = sys.__stdout__

if len(sys.argv) < 2:
    sys.exit("Usage: format_flashweave.py <abundance_file>")

abd_file = sys.argv[1]
print(f"Input abundance file: {abd_file}", file=sys.stderr)

delimiter        = detect_separator(abd_file)
flashweave_table = pd.read_csv(abd_file, sep=delimiter).iloc[:, :-1]

float_cols = flashweave_table.select_dtypes(include=["float64"]).columns
for col in float_cols:
    flashweave_table[col] = flashweave_table[col].astype("int64")

flashweave_table.iloc[:, 0] = flashweave_table.iloc[:, 0].astype(str)
flashweave_table.to_csv("flashweave_abd_table.tsv", sep="\t", index=False)

print("Output written to flashweave_abd_table.tsv", file=sys.stderr)
