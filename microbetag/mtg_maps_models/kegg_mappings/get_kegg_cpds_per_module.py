"""
Aim:
    This script gets the KEGG compounds for each KEGG module
    and then maps them to their corresponding ModelSEED compound ids.
    Last, it writes a 3-column file called `` whith the KEGG module id, the
    KEGG compound id and its corresponding ModelSEED id.

Author:
    Haris Zafeiropoulos

Notes:

    Run using the modelseed conda env in Genius

    For the following KEGG modules, no KEGG compound involved was mapped to a ModelSEED compound
    "M00065",  # Glycan biosynthesis:  GPI-anchor biosynthesis
    "M00068",  # Glycan biosynthesis:  Glycosphingolipid biosynthesis: globo-series
    "M00069",  # Glycan biosynthesis:  Glycosphingolipid biosynthesis: ganglio series
    "M00070",  # Glycan biosynthesis:  Glycosphingolipid biosynthesis: lacto-series
    "M00071",  # Glycan biosynthesis:  Glycosphingolipid biosynthesis: neolacto-series
    "M00831",  # Biosynthesis of terpenoids and polyketides:  Kedarcidin 2-hydroxynaphthoate moiety biosynthesis
    "M00832",  # Biosynthesis of terpenoids and polyketides:  Kedarcidin 2-aza-3-chloro-beta-tyrosine moiety biosynthesis
    "M00867"   # Lipopolysaccharide metabolism:  KDO2-lipid A modification pathway

    mean_non_seedset_length: 752.8452673677974
    mean_seedset_length: 341.1272404088283
"""
import time
import requests
import gzip

"""
Part A:
    Map KEGG terms to their corresponding ModelSEED compounds.
"""

modelseedId_to_keggId = {}
keggId_to_modelSeedId = {}
counter = 0
all_lines = 0

compressed_file = "modelseedDB_compounds.tsv.gz"
with gzip.open(compressed_file, "rt") as f:
    for line in f:
        all_lines += 1
        modelseedId = line.split("\t")[0]
        keggId_parts = line.split("\t")[18].split("KEGG")
        if len(keggId_parts) > 1:
            keggId = keggId_parts[1][2:]
            if "|" in keggId:
                keggId = keggId.split("|")[0]
            if ";" in keggId:
                modelseedId_to_keggId[modelseedId] = keggId
                keggIds = keggId.split(";")
                for keggId in keggIds:
                    if keggId not in keggId_to_modelSeedId:
                        keggId_to_modelSeedId[keggId] = modelseedId
                    else:
                        keggId_to_modelSeedId[keggId] += ";" + modelseedId
            else:
                if keggId not in keggId_to_modelSeedId:
                    keggId_to_modelSeedId[keggId] = modelseedId
                else:
                    keggId_to_modelSeedId[keggId] += ";" + modelseedId
                modelseedId_to_keggId[modelseedId] = keggId
        else:
            counter += 1

print("ModelSEED compounds with not a corresponding KEGG one:", str(counter))
print("ModelSEED compound ids in total:", all_lines)


"""
Part B:
    - For the KEGG modules of interest, get the KEGG terms that participate in it and map them to their corresponding ModelSEED ids
    ModelSEED   KEGG COMPOUND   KEGG MODULE
    cpd00020        C00022      M00001
    cpd00061        C00074      M00001
"""
modules_file = open("module_map_pairs.tsv", "r")
modules = [x.split("\t")[0][3:] for x in modules_file.readlines() ]
base_url = "https://rest.kegg.jp/link/cpd/"
f = open("seedId_keggId_module.tsv", "w")
counter2 = 0
for module in modules:
    print("Processing module...", module)
    counter2 += 1
    if counter2 % 10 == 0:
        print(counter2, " out of ", str(len(modules)), " modules.")
    time.sleep(1)
    url = "".join([base_url, module])
    r = requests.get(url)
    modules_kegg_compounds = r.text.split("\n")
    for line in modules_kegg_compounds:
        try:
            kegg_compound = line.split("\t")[1][4:]
        except:
            pass
        print(kegg_compound)
        if kegg_compound in keggId_to_modelSeedId:
            modelseed_compound = keggId_to_modelSeedId[kegg_compound]
            if ";" in modelseed_compound:
                modelseed_compounds = modelseed_compound.split(";")
                for modelseed_compound in modelseed_compounds:
                    f.write("\t".join( [modelseed_compound, kegg_compound, module]))
                    f.write("\n")
            else:
                f.write("\t".join( [modelseed_compound, kegg_compound, module]))
                f.write("\n")
