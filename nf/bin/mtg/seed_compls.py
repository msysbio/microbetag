#!/usr/bin/env python3

"""
For a single, beneficiary species, it extracts seed complementarities
with all other species on the dataset and calculates its seed scores
with the species under study as node A.
"""

import sys
import json
from microbetag.seed_complementarity import get_kegg_module_related, \
    generate_fixed_pairwise_comparisons, kegg_module_related_intersect
from microbetag.PhyloMint.lib.CalculateIndexes import calculate_scores, extract_complements

species      = sys.argv[1]
nonseeds_dic = sys.argv[2]
conf_dic     = sys.argv[3]

# Filter complements based on KEGG modules
module_related = sys.argv[4].lower() == "true"

# Output files
scores_outfile = sys.argv[5]  # f"{species}_scores.tsv"
compls_outfile = sys.argv[6]  # f"{species}_complements.json"

# Load KEGG module related compounds if needed
seed_ko_mo     = "/workspace/microbetag/mtg_maps_models/kegg_mappings/seedId_keggId_module.tsv"
modules_ms_cpd = get_kegg_module_related(seed_ko_mo)


def species_scores_compls(species, conf_dic, nonseeds_dic) :
    """
    Get scores and complements for a specific model (species).
    In the stand-alone version, it writes the seed scores file.

    Note:
        Since, we get all pairwise combinations, we do not care of using the as_donor case for a species,
        since it's gonna be calculated when the other species is the beneficiary
    """

    # Init compls and scores
    scores, compls = set(), {}

    # Get beneficiary's seed set
    species_conf = conf_dic.get(species)

    if species_conf is None:
        return None, None

    # Get pairwise
    as_beneficiary, _ = generate_fixed_pairwise_comparisons(species, list(conf_dic.keys()))

    # Get seed set of the other species
    for partner in [pair[1] for pair in as_beneficiary if pair[1] != species]:

        if (conf := conf_dic.get(partner)) is not None and \
                (non_seed := nonseeds_dic.get(partner)) is not None:

            partner_seedset_confidence, nonSeedB = conf, non_seed

        else:
            continue

        SeedA, SeedB, nonSeedB = (
            set(species_conf.keys()),
            set(partner_seedset_confidence.keys()),
            set(nonSeedB),
        )

        mi_coop, mi_comp = calculate_scores(
            SeedA, species_conf, SeedB, nonSeedB
        )

        scores.add(
            f"{species}\t{partner}\t{mi_comp}\t{mi_coop}\n"
        )

        B_complements_A = extract_complements(SeedA, nonSeedB)

        if module_related:
            B_complements_A = kegg_module_related_intersect(
                B_complements_A, modules_ms_cpd
            )

        compls[partner] = B_complements_A

    # with open(scores_outfile, "a") as f:
    #     f.writelines(scores)

    with open(scores_outfile, "a") as f:
        f.writelines(f"{s}" for s in sorted(scores))

    with open(compls_outfile, "w") as f:
        json.dump(compls, f, indent=2)


species_scores_compls(
    species,
    json.load(open(conf_dic)),
    json.load(open(nonseeds_dic))
)
