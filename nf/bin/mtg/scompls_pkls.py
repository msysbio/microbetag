#!/usr/bin/env python3

import sys
import json
import pickle
import pandas as pd

compls_js_outfile  = sys.argv[1]
compls_pkl_outfile = sys.argv[2]

with open(compls_js_outfile) as f:
    compls_dict = json.load(f)

df = pd.DataFrame.from_dict(compls_dict)

# Identify only the float columns
float_cols = df.select_dtypes(include="float").columns

# Replace NaNs with [] only in those columns
df[float_cols] = df[float_cols].where(df[float_cols].notna(), [[]])

# Attention! We need to get df.T. Otherwise we get the source as target and the other way around !
with open(compls_pkl_outfile, "wb") as f:
    pickle.dump(df.T, f)
