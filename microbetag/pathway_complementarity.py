"""
This script aims at calculating and exporting patwhay complementarities in case of
running microbetag locally, with user-provided genomes.
"""
import os
import json
import ast  # process trees of the Python abstract syntax grammar.

import itertools
import pyshorteners
import pandas as pd
from tqdm import tqdm

from .utils import SetEncoder, flatten, mtg_logger

logger = mtg_logger(__name__)


def build_kegg_url(kegg_map, clean_path, missing_kos, shortener=None):
    """
    Build url to colorify the related to the module kegg map based on the KO terms
    of the beneficiary (pink) and those it gets from the donor (green)
    """
    # Load the dictionary with the kegg modules and their corresponding maps
    color_mapp_base_url = "https://www.kegg.jp/kegg-bin/show_pathway?"
    present_kos_color   = "%09%23EAD1DC/"
    complemet_kos_color = "%09%2300A898/"

    # Make a url pointing at a colored kegg map based on what's on the beneficiary's genome
    # and what it gets as complement from the donor
    beneficiarys_kos = ""
    complements_kos  = ""
    for ko_term in clean_path:
        if ko_term not in missing_kos:
            beneficiarys_kos = "".join([beneficiarys_kos, ko_term, present_kos_color])
        else:
            complements_kos = "".join([complements_kos, ko_term, complemet_kos_color])
    try:
        # [NOTE] In rare cases, the module might not have a related map, thus kegg_map would be of NoneType
        # and the join() would return an error.
        url_ko_map_colored = "".join(
            [color_mapp_base_url, kegg_map, "/", beneficiarys_kos, complements_kos]
        )
        if shortener is not None:
            logger.info("Shortening the URL.")
            url_ko_map_colored = shortener.tinyurl.short(url_ko_map_colored)
    except Exception:
        url_ko_map_colored = "N/A"

    return url_ko_map_colored


def all_complements(
    bin_kos_per_module,
    bins_alternatives,
    module_to_map,
    compl_output_file,
    tinyurl=False,
):
    """
    Extract potential complementarities from other bins

    Inputs:
        bin_kos_per_module
        bins_alternatives
        module_to_map
    """
    logger.info("Build pathCompls.json file.")
    unique_url_input = {}

    # Init shortener
    shortener = pyshorteners.Shortener() if tinyurl else None

    # Parse KO annotations
    complements = {}
    for beneficiary_bin_id, all_bin_module_alternatives in tqdm(
        bins_alternatives.items(), desc="Processing bins", unit="bin"
    ):
        complements[beneficiary_bin_id] = {}
        for donor_bin_id in bin_kos_per_module:
            complements[beneficiary_bin_id][donor_bin_id] = []
            for module, alts in all_bin_module_alternatives.items():
                donors_kos_relativ_to_module = bin_kos_per_module[donor_bin_id][module]
                for alternative, missing_kos_for_alternative in alts.items():
                    is_subset = set(missing_kos_for_alternative).issubset(
                        set(donors_kos_relativ_to_module)
                    )
                    if is_subset:
                        alternative = ast.literal_eval(alternative)
                        pc_comb = (
                            module,
                            tuple(missing_kos_for_alternative),
                            tuple(alternative),
                        )
                        if pc_comb not in unique_url_input:
                            try:
                                module_map = module_to_map[module]
                                url = build_kegg_url(
                                    module_map,
                                    list(alternative),
                                    list(set(missing_kos_for_alternative)),
                                    shortener,
                                )
                            except Exception:
                                url = ""
                                pass
                            unique_url_input[pc_comb] = url

                        # Build list with the complete complement
                        pot_compl = [
                            module,
                            missing_kos_for_alternative,
                            alternative,
                            unique_url_input[pc_comb],
                        ]
                        complements[beneficiary_bin_id][donor_bin_id].append(pot_compl)
    # Write the pathCompls.json file
    with open(compl_output_file, "w") as file:
        json.dump(complements, file, cls=SetEncoder)
    logger.info(
        "Step 3, the potential complementarities among the bins were enumerated."
    )

    return complements


def a_modules_maps(kegg_modules_to_maps):
    """Get the KEGG maps in which a module takes part in"""
    # maps = open(kegg_modules_to_maps, "r")
    with open(kegg_modules_to_maps, "r") as f:
        maps = f.readlines()
    module_to_map = {}
    for line in maps:
        module, mmap = line.split("\t")
        module_to_map[module[:-1]] = mmap[1:-1]
    return module_to_map


def taxon_kos_per_module(bins_kos_df, ref_ko_per_module):
    """Keep track of the KOs related to a module present on each bin
    Input:
        bins_kos_df (pd.DataFrame):

    Returns:
        bin_kos_per_module (Dict):
    """
    d = pd.read_csv(ref_ko_per_module, sep="\t")
    d.columns = ["module_id", "ko_term"]
    d.loc[:, "presence"] = 1
    definitions_df = d.pivot_table(
        index="ko_term", columns="module_id", values="presence", fill_value=0
    )
    ind = definitions_df.index.str.replace("ko:", "")
    definitions_df.index = ind

    bin_kos_per_module = {}
    # Iterate over each column in the second dataframe
    logger.info("Step 1, KOs related to a module present on each bin.")
    for bin_id in bins_kos_df.columns:
        bin_kos_per_module[bin_id] = {}  # Initialize inner dictionary for each bin
        for module, definition_ko_terms in definitions_df.items():
            # Get KOs of the module definition
            definition_ko_terms = definition_ko_terms[definition_ko_terms != 0]
            # Get KOs present on the bin
            bins_kos = bins_kos_df[bins_kos_df[bin_id] == 1][bin_id]
            # Get intersection and add the module: kos_present to the dict
            bin_kos_per_module[bin_id][module] = bins_kos.index.intersection(
                definition_ko_terms.index
            ).tolist()

    return bin_kos_per_module


def export_pathway_complementarities(config, bins_kos_df):
    """
    Function to get all the KEGG pathway complements among a set of bins

    Input:
        config (Config): instance of the microbetag Config class with settings
        bins_kos_df (pd.DataFrame): dictionary with bin id as a key and the KOs found in the bin as the value

    Returns:
    {beneficiary_bin: {donor_bin_A: {module_a: [], module_b: [],.. }}}
    """

    # Keep track of the KOs related to a module present on each bin
    bin_kos_per_module = taxon_kos_per_module(
        bins_kos_df, config.ref_ko_per_module
    )

    # If alts.json not available
    if not os.path.exists(config.alts_file):

        bins_alternatives = all_alternatives(
            bin_kos_per_module,
            config.modules_definitions_json_map,
            config.alts_file,
            n_workers=config.threads  # or use os.cpu_count() for max parallelism
        )

    else:

        with open(config.alts_file, "r") as h:
            bins_alternatives = json.load(h)

    # If compl.json not available
    if not os.path.exists(config.pc_file):

        module_to_map = a_modules_maps(config.kegg_modules_to_maps)
        complements = all_complements(
            bin_kos_per_module,
            bins_alternatives,
            module_to_map,
            config.pc_file,
            config.tinyurl,
        )

    else:

        with open(config.pc_file, "r") as h:
            complements = json.load(h)

    return bins_alternatives, complements


def process_bin(bin_id, kos_per_module, mo_map, structurals):
    complete_modules = set()
    alternatives_to_gap = {}

    for module, kos_on_its_own in kos_per_module.items():
        if module in structurals:
            continue
        list_of_kos_present = set(kos_on_its_own)
        definition_under_study = mo_map[module]["steps"]
        definition_under_study_proc = [
            term if isinstance(term, list) else [term]
            for term in definition_under_study.values()
        ]
        potential_compl_paths = [list(tup) for tup in itertools.product(*definition_under_study_proc)]
        flat_potent_compl_paths = [flatten(path) for path in potential_compl_paths]

        for path in flat_potent_compl_paths:
            if all(item in list_of_kos_present for item in path):
                complete_modules.add(module)
            else:
                gaps = set(x for x in set(path) if x not in list_of_kos_present)
                alternatives_to_gap.setdefault(module, {})[str(path)] = gaps

    for key in complete_modules:
        alternatives_to_gap.pop(key, None)

    # Get shortest alternatives
    for module, path_gaps in alternatives_to_gap.items():
        tmp = tmp2 = path_gaps.copy()
        min_val = min([len(gaps) for gaps in path_gaps.values()])
        values = list(tmp2.values())
        shortest_alternatives = [
            list(tmp2.keys())[values.index(s)]
            for s in values
            if not any(s.issuperset(i) and len(s) > len(i) for i in values)
        ]
        for path, gaps in path_gaps.items():
            if len(gaps) > min_val + 1 or path not in shortest_alternatives:
                tmp.pop(path)
        alternatives_to_gap[module] = tmp

    return bin_id, alternatives_to_gap

def all_alternatives(
    bin_kos_per_module,
    modules_definitions_json_map,
    alts_output_file,
    n_workers=4
):
    """
    Build the alts.json file
    list alternatives for a bin's modules to be completed

    Inputs:
        bin_kos_per_module (Dict):
        modules_definitions_json_map (str): path to

    """
    from concurrent.futures import ProcessPoolExecutor, as_completed

    with open(modules_definitions_json_map, "r") as f:
        mo_map = json.load(f)

    structurals = [
        "md:M00144","md:M00149","md:M00151","md:M00152","md:M00154","md:M00155",
        "md:M00153","md:M00156","md:M00158","md:M00160"
    ]

    bins_alternatives = {}
    with ProcessPoolExecutor(max_workers=n_workers) as executor:
        futures = {
            executor.submit(process_bin, bin_id, kos_per_module, mo_map, structurals): bin_id
            for bin_id, kos_per_module in bin_kos_per_module.items()
        }
        for future in as_completed(futures):
            bin_id, alternatives = future.result()
            bins_alternatives[bin_id] = alternatives

    with open(alts_output_file, "w") as file:
        json.dump(bins_alternatives, file, cls=SetEncoder)

    return bins_alternatives
