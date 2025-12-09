#!/usr/bin/env python3

"""
SBML to SEED Complementarity Processor

This script processes SBML metabolic models to identify SEED-compatible and non-SEED compounds
using the microbetag library. It takes an SBML file and namespace as input, performs compound
mapping between different database identifiers (BiGG, ModelSEED), and generates a JSON output
with the analysis results.

The script handles:
- SBML file parsing and compound extraction
- Database namespace conversion (BiGG ↔ ModelSEED)
- SEED database complementarity analysis
- Confidence scoring for SEED-compatible compounds

Usage:
    python seed_sets.py <sbml_path> <namespace> <output_file>

Arguments:
    sbml_path (str): Path to the SBML model file
    namespace (str): Database namespace - either "BiGG" or "modelseed"
    outfile (str): Path for the JSON output file

Output:
    JSON file containing:
    - base_name: Base name of the processed model
    - seed_set: List of SEED-compatible compounds
    - non_seed_set: List of non-SEED compounds  
    - seed_set_confidence: Confidence scores for SEED compounds
"""

import sys
import json
from microbetag.seed_complementarity import process_sbml, bigg_to_seed_mapping_df, Ixes

sbml_path = sys.argv[1]
namespace = sys.argv[2]
outfile   = sys.argv[3]

compound_prefix = "M"
ex_suffix  = "e" if namespace == "BiGG" else "e0"
int_suffix = "c" if namespace == "BiGG" else "c0"

switch = False if namespace == "modelseed" else True

metanetx_compounds = "/workspace/microbetag/mtg_maps_models/MetaNetX/chem_xref.tar.gz"
bigg2seed          = bigg_to_seed_mapping_df(metanetx_compounds)

ixes = Ixes(compound_prefix, ex_suffix, int_suffix)

args = sbml_path, namespace, switch, bigg2seed, ixes

base_name, seed_set, non_seed_set, seed_set_confidence  = process_sbml(args)

result = {
    "base_name"          : base_name,
    "seed_set"           : seed_set,
    "non_seed_set"       : non_seed_set,
    "seed_set_confidence": seed_set_confidence
}

# Write per-file JSON output
with open(outfile, "w") as f:
    json.dump(result, f, indent=2)
