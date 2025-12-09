"""
Aim:
    Builds a microbetag-annotated network in a CX2 format, using the `ndex2`
    (https://ndex2.readthedocs.io/) library.

Note:
    In case of the on-the-fly version, the annotated network is returned as a jsonifi-ed Flask Response.
    In the stand-alone version, the annotated network is saved (mtg-timestamp.cx2)
    and the user has to load it on Cytoscape to be able to visualize it
    and further exploit the MGG Cytoscape App (https://apps.cytoscape.org/apps/mgg)
    to parse and analyze the network.
"""
import os
import pickle
import ndex2.cx2

import datetime
import pyshorteners

import statistics
import numpy as np
import pandas as pd

from typing import TYPE_CHECKING, Dict, List, Tuple
from collections import defaultdict

from .networks import get_edgelist, read_cyjson

from .utils import (
    mtg_logger,
    load_phenotypic_traits,
    extend_faprotax,
    extend_complements,
)
from .seed_complementarity import (
    load_seed_complement_files,
    build_url_with_seed_complements,
)

if TYPE_CHECKING:
    from .config import Config

_COMPLEMENTARITY_TYPE_, _COMPLEMENTING_ = "complementarity", "(completed by)"
_COOCCURRENCE_, _COOCCURYING_           = "co-occurrence", "(cooccurs with)"
_DEPLETION_, _DEPLETING_                = "co-exclusion", "(negatively correlated with)"
_COOCCURENCE_DEPLETION_                 = "co-occurrence/co-exclusion"

_MTG_NAMESPACE  = "microbetag"
_M_TAXONOMY     = "::".join([_MTG_NAMESPACE, "taxonomy"])
_M_TAXON        = "::".join([_MTG_NAMESPACE, "taxon"])
_M_TAX_LEVEL    = "::".join([_MTG_NAMESPACE, "ncbi-tax-level"])
_M_TAXON_ID     = "::".join([_MTG_NAMESPACE, "ncbi-tax-id"])
_M_GTDB_GENOMES = "::".join([_MTG_NAMESPACE, "gtdb-genomes"])
_M_WEIGHT       = "::".join([_MTG_NAMESPACE, "weight"])

_TAXONOMY = "taxonomy"
_STD = "-std"

_PATH_NAMEPSACE = "compl"

_SEED_NAMESPACE = "seed"
_SEED_COMPL     = f"{_SEED_NAMESPACE}Compl"
_SEED_COOP      = "::".join([_SEED_NAMESPACE, "cooperation"])
_SEED_COMP      = "::".join([_SEED_NAMESPACE, "competition"])

_PHEN_NAMESPACE = "phendb"
_PHEN_SCORE     = f"{_PHEN_NAMESPACE}Score"

_FAPROTAX_NAMESPACE = "faprotax"

_MANTA_NAMESPACE  = "manta"
_MANTA_CLUSTER    = "::".join([_MANTA_NAMESPACE, "cluster"])
_MANTA_ASSIGNMENT = "::".join([_MANTA_NAMESPACE, "assignment"])

_logger_ = mtg_logger(__name__)
__RANKS__ = ["domain", "phylum", "class", "order", "family", "genus", "species"]


# -----------------------------
# NODES
# -----------------------------
def taxonomy_levels_sa(node: Dict) -> None:
    """
    Updates a node's attributes by splitting taxonomy to the 7-levels scheme (:attr:`__RANKS__`)
    and giving their values to the corresponding ones. For stand-alone version.

    Arguments:
        node: A ndex2-oriented node's dictionary; keys should be sequence ids

    Note:
        Edits the `node` dictionary by adding a new key:value pair for each (of the 7) taxonomic level.
        Used only in the case of the stand-alone tool.
    """
    try:

        levels = node["v"][_M_TAXONOMY].split(";")

        if len(levels) == 7:

            levels = [lvl.strip() for lvl in levels]

            for rank, value in zip(__RANKS__, levels):
                node["v"][f"{_TAXONOMY}::{rank}"] = value

            # Find last non-empty level
            for i in reversed(range(7)):
                if levels[i] and levels[i].split("_")[-1].strip():
                    node["v"][_M_TAX_LEVEL] = __RANKS__[i]
                    break

    except Exception as e:
        _logger_.warning(e)
        pass


def init_nodes_and_edges(
    edgelist    : pd.DataFrame,
    seqId_to_tax: Dict[str, str],
    onthefly       = False,
    metadata       = None,
    otf_seq_tax_df = None
) -> Tuple[List[dict], List[str], List[dict]]:
    """
    Initiates the nodes and edges of the network as dictionaries, in a ndex2-oriented format.

    Args:
        edgelist: DataFrame containing 'node_A', 'node_B', and 'microbetag::weight'.
        seqId_to_tax: Mapping dictionary for sequence ids: taxonomy.

    Returns:
        tuple: A tuple containing:
            - nodes: A list of dictionaries with the nodes of the network
            - seq_ids_lst: A list with the sequence ids (of the abundance table) that are part of the network
            - edges: A list of dictionaries with the edges of the network
    """
    # Extract unique node names efficiently -- sequence ids
    seq_ids_lst = sorted(set(edgelist["node_A"]).union(edgelist["node_B"]))

    kwargs = {}

    if metadata:
        metavars  = pd.read_csv(metadata, sep="\t", header=None, index_col=0).index.tolist()
        kwargs['metavars'] = metavars

    # Create nodes
    if not onthefly:
        nodes = [
            {
                "id": i,
                "v": get_node_attributes(seq_id, seqId_to_tax, **kwargs)
            }
            for i, seq_id in enumerate(seq_ids_lst)
        ]

        for node in nodes:
            taxonomy_levels_sa(node)

    else:

        # NOTE (Haris Zafeiropoulos, 2025-05-04):
        # the otf_seq_tax_df is built on the app.py and not on the config.py - onthefly version only

        kwargs["ncbi_ids_dict"] = load_otf_seq_map(otf_seq_tax_df)

        nodes = [
            {
                "id": i,
                "v": get_node_attributes(seq_id, seqId_to_tax, **kwargs)
            }
            for i, seq_id in enumerate(seq_ids_lst)
        ]
    # Create edges
    edges = [
        {
            "id": i,
            "s" : seq_ids_lst.index(node_a),
            "t" : seq_ids_lst.index(node_b),
            "v" : {
                "interaction type"  : _COOCCURRENCE_ if weight > 0 else _DEPLETION_,
                "interaction"       : _COOCCURENCE_DEPLETION_,
                "shared name"       : f"{node_a} {_COOCCURYING_ if weight > 0 else _DEPLETING_} {node_b}",
                _M_WEIGHT: weight,
            },
        }
        for i, node_a, node_b, weight in edgelist.itertuples(index=True, name=None)
    ]

    return nodes, seq_ids_lst, edges


def get_node_attributes(seq_id: str, seqId_to_tax: Dict, ncbi_ids_dict: Dict = None, metavars=None) -> Dict:
    """
    Using the sequence mapping to their corresponding taxonomies objects, builds a dictionary with the
    node's taxonomy and mapped genomes (in case of on-the-fly) attributes, in a ndex2 and MGG-oriented way.

    Args:
        seq_id: Sequence id of the node
        seqId_to_tax: Dictionary with sequence ids keys and their corresponding taxonomies as value
        config: Instance of the :class:`Config` class

    Returns:
        A dictionary with the a node's attributes regarding the `microbetag` namespace of the MGG
    """
    node_tax = seqId_to_tax.get(seq_id, "Unknown").rstrip(";")

    attrs = {
        "name"     : seq_id,
        _M_TAXONOMY: node_tax,
        _M_TAXON   : node_tax.split(";")[-1]
    }

    if ncbi_ids_dict:

        ncbi_info = ncbi_ids_dict.get(seq_id, {})

        # NCBI Taxon ID
        attrs[_M_TAXON_ID] = (
            ncbi_info.get("ncbi-tax-id")
            if ncbi_info.get("ncbi-tax-id") not in [None, "", []]
            else ["-"]
        )

        # TAXONOMY LEVEL
        tax_level = ncbi_info.get("ncbi-tax-level")
        if tax_level not in [None, "", []]:
            attrs[_M_TAX_LEVEL] = tax_level
        elif metavars and any(seq_id.startswith(prefix) for prefix in metavars):
            attrs[_M_TAX_LEVEL] = ["metavar"]
        else:
            attrs[_M_TAX_LEVEL] = ["-"]

        # GENOMES ASSIGNED
        attrs[_M_GTDB_GENOMES] = (
            ncbi_info.get("gtdb-genomes")
            if ncbi_info.get("gtdb-genomes") not in [None, "", []]
            else ["-"]
        )

        for rank in __RANKS__:
            attrs[f"{_TAXONOMY}::{rank}"] = ncbi_info.get(rank)

    return attrs


def update_with_phen_traits(nodes: List[dict], node_names: List[str], phen_traits_dir: str, onthefly: bool) -> None:
    """
    Updates nodes with phenotypic traits.

    Args:
        config: Configuration for loading phenotypic traits.
        nodes (List[Dict]): List of node dictionaries.
        node_names (List[str]): List of node names corresponding to node IDs.

    Note:
        Like all functions applied in the nodes and edges, it does not return an object,
        it rather updates entries of the `nodes` dictionary.

    Note:

        1. The `node_names` list is a mapping object where order is essential.
        It includes the sequence ids of the nodes present in the network, in the order they will be introduced
        in the ndex2 network constructor.

        2. Initial `phen_traits` has the genome ids present in the phenotrex prediction files.
    """

    phen_traits, _ = load_phenotypic_traits(phen_traits_dir)

    if onthefly:

        gtdb_to_seqid = defaultdict(set)

        for node in nodes:

            for gc in node["v"].get(_M_GTDB_GENOMES, []):

                gtdb_to_seqid[
                    gc.split(".")[0]
                ].add(
                    (node["v"]["name"],
                     node["id"])
                )

    for genome_id, phen_attributes in phen_traits.items():

        if onthefly:
            node_indices = [entry[1] for entry in gtdb_to_seqid.get(genome_id, [])]

        else:
            try:
                node_indices = [node_names.index(genome_id)]
            except ValueError:
                # genome_id is not among the in node names
                continue

        for node_index in node_indices:

            node = nodes[node_index]

            for trait, values in phen_attributes.items():

                trait_key  = f"{_PHEN_NAMESPACE}::{trait}"
                score_key  = f"{_PHEN_SCORE}::{trait}"
                presence   = values["presence"].strip().upper() == "YES"
                confidence = values["confidence"]

                if trait_key in node["v"]:

                    if presence == node["v"][trait_key]:
                        _logger_.info("Update confidence score.")
                        node["v"][score_key] += confidence

                    else:
                        # NOTE (Haris Zafeiropoulos, 2025-05-28):
                        # In case the two predictions are differennt
                        _logger_.info(f"Several genomes for a node with controversial prediction for trait {trait}.")
                        node["v"][trait_key] = node["v"][score_key] = None
                else:

                    node["v"][trait_key] = presence
                    node["v"][score_key] = confidence

    if onthefly:

        for node in nodes:

            genomes = node["v"].get(_M_GTDB_GENOMES, [])

            if len(genomes) == 0:
                continue

            for key in list(node["v"].keys()):
                if key.startswith(_PHEN_SCORE) and node["v"][key] is not None:
                    node["v"][key] /= len(genomes)


def update_with_faprotax_traits(nodes: List[dict], node_names: List[str], fapr_tables, seq_col) -> None:
    """
    Updates nodes with FAPROTAX traits.

    Args:
        config    : Configuration for loading FAPROTAX traits.
        nodes     : List of node dictionaries.
        node_names: List of node names corresponding to node IDs.
    """
    bin_faprotax_traits, _ = extend_faprotax(fapr_tables, seq_col)

    for seq_id, faprotax_attributes in bin_faprotax_traits.items():

        try:
            node_index = node_names.index(seq_id)

        except ValueError:
            _logger_.warning(f"Warning: {seq_id} not found in node names.")
            # Skip if seq_id is not in node_names
            continue

        node = nodes[node_index]

        for trait in faprotax_attributes:
            node["v"][f"{_FAPROTAX_NAMESPACE}::{trait}"] = True


def update_with_manta(nodes: List[dict], node_names: List[str], manta_net) -> Dict:
    """
    Updates nodes with `manta` network cluster, assignment, and position data.

    Returns:
        A list of dictionaries representing the `manta` layout with node positions.

    Note:
        Besides updating the entries of the `nodes` list, it also returns a `ndex2.layout`.

    Attention:
        Currently, `microbetag` does not apply the `manta` layout returned. We could/should consider doing so
        by editing the `ndex2` object.
    """
    manta_net = read_cyjson(manta_net)

    # Update nodes with cluster and assignment data
    node_index = {name: idx for idx, name in enumerate(node_names)}

    for seq_id, attrs in manta_net.nodes(data=True):

        idx = node_index.get(seq_id)
        if idx is not None:

            if 'cluster' in attrs:
                nodes[idx]["v"][_MANTA_CLUSTER] = int(attrs['cluster'])
            if 'assignment' in attrs:
                nodes[idx]["v"][_MANTA_ASSIGNMENT] = attrs['assignment']

    # Store MANTA layout (node positions)
    manta_layout = [
        {"node": seq_id, "x": position["x"], "y": position["y"]}
        for seq_id, position in manta_net.nodes(data="position")
    ]

    return manta_layout


# -----------------------------
# EDGES - PATHWAY COMPLEMENTARITY
# -----------------------------

def pathway_complement_edge(
    edge_id    : int,
    beneficiary: str,
    donor      : str,
    complement : Dict,
    node_names : List[str],
    beneficiary_genome = None,
    donor_genome       = None,
    update             = False,
    cx_edges           = None
) -> Dict:
    """
    Creates or updates an edge carrying pathway complementarities between a donor and a beneficiary node.

    Note:
        Conceptually, the donor is the `source` of the `edge`, since a compound would be **secreted from** it
        and **drive to** the beneficiary (`target`).

    Arguments:
        edge_id          (int)      : ID of the edge
        beneficiary      (str)      : The recipient of the complement. It is considered as the target of the edge in microbetag.
        donor            (str)      : The source of the complement. It is considered as the donor of the edege.
        complement       (any)      : The complement value.
        node_names       (list[str]): List of node names to determine node indices.
        interaction_type (str)      : Type of interaction (e.g., "complementarity").
        interacting      (str)      : Descriptor of the interaction.

    Returns:
            A dictionary with a pathway complementari edge representation.
    """
    beneficiary_genome = _set_none_genome(beneficiary_genome, beneficiary)
    donor_genome       = _set_none_genome(donor_genome, donor)

    if update:
        edge = cx_edges[edge_id]
    else:
        # interacting = "".join(["(", _COMPLEMENTING_, ")"])
        edge = {
            "id": edge_id,  # Unique ID
            "s": node_names.index(donor),  # Source (donor)
            "t": node_names.index(beneficiary),  # Target (beneficiary)
            "v": {
                "interaction type": _COMPLEMENTARITY_TYPE_,
                "shared name": f"{beneficiary} {_COMPLEMENTING_} {donor}",
            },
        }

    column = f"{_PATH_NAMEPSACE}::{beneficiary_genome}:{donor_genome}"

    edge["v"].update({column: _hat_complement(complement)})

    return edge


def get_compl_maps(mspecies_map_df: pd.DataFrame, genome_ids_in_nodes: List) -> Tuple[pd.DataFrame, Dict[str, set]]:
    """
    Builds mapping objects to properly pass pathway/seed complementarities to their corresponding edges.

    Arguments:
        config:
        genomes_ids_in_nodes:  A list of GC ids found in complementarities (pathCompls.json)

    Returns:
        A tuple consisting of:
        - nodes_in_compls: A pd.Series with the sequence ids of the nodes that participate
                           in pathway complementarity drive edges.
        - node_to_gtdb: A dictionary with sequence ids as key and the set of their corresponding
                        GTDB representative as value{seq_id: {gtdb_ids}}
    """
    df = mspecies_map_df
    gc_list = list(genome_ids_in_nodes.copy())

    # Filter rows where GC is in gtdb_gen_repr_A and get corresponding node_A
    mask_A = df["gtdb_gen_repr_A"].isin(gc_list)
    nodes_from_A = df.loc[mask_A, "node_A"]

    # Filter rows where GC is in gtdb_gen_repr_B and get corresponding node_B
    mask_B = df["gtdb_gen_repr_B"].isin(gc_list)
    nodes_from_B = df.loc[mask_B, "node_B"]

    # Combine and get unique values if needed
    nodes_in_compls = pd.concat([nodes_from_A, nodes_from_B]).unique()

    # Initialize a defaultdict of sets (or use list if you prefer duplicates)
    node_to_gtdb = defaultdict(set)

    # Map node_A to gtdb_gen_repr_A
    for node, gtdb in zip(df["node_A"], df["gtdb_gen_repr_A"]):
        node_to_gtdb[node].add(gtdb)

    # Map node_B to gtdb_gen_repr_B
    for node, gtdb in zip(df["node_B"], df["gtdb_gen_repr_B"]):
        node_to_gtdb[node].add(gtdb)

    # Convert sets to lists (optional)
    node_to_gtdb = {node: list(gtdbs) for node, gtdbs in node_to_gtdb.items()}

    return nodes_in_compls, node_to_gtdb


def pathway_complements(
    config: "Config",
    edgelist_df: pd.DataFrame,
    node_names: List,
    cx_edges: Dict
):

    _logger_.info("Extend pathway complements format.")

    _logger_.info(f"pc_file: {config.pc_file}")

    complements_dict = extend_complements(
        complements_json = config.pc_file,
        descrps_path     = config.module_descriptions,
        pc_percent       = config.pc_percent,
        pc_dir           = config.pc_dir,
    )

    nodes_in_compls = set()
    for outer_id, inner_dict in complements_dict.items():
        nodes_in_compls.add(outer_id)  # The 'add' function adds a single element to the set.
        # If you pass a list, tuple, or set, it treats the entire object as one element.
        nodes_in_compls.update(inner_dict.keys())  # Adds multiple elements (from an iterable) to the set.

    if config.onthefly:

        # NOTE (Haris Zafeiropoulos, 2025-05-07): In this case the nodes_in_compls does not
        # have sequence identifiers, as in the stand-alone version, but GC ids. So we need to map them to seq ids.
        nodes_in_compls, node_to_gtdb = get_compl_maps(config.mspecies_map_df, nodes_in_compls)

    for _, link in edgelist_df.iterrows():
        node_a, node_b, _ = link

        if node_a not in nodes_in_compls or node_b not in nodes_in_compls:
            continue

        for beneficiary, donor in [(node_a, node_b), (node_b, node_a)]:
            ben_ids = node_to_gtdb[beneficiary] if config.onthefly else [beneficiary]
            don_ids = node_to_gtdb[donor] if config.onthefly else [donor]

            for ben_genome in ben_ids:
                for don_genome in don_ids:
                    if ben_genome not in complements_dict or don_genome not in complements_dict[ben_genome]:
                        continue

                    complement = complements_dict[ben_genome][don_genome]

                    edge_id, update = _get_edge_id(
                        beneficiary, donor, node_names, cx_edges, _COMPLEMENTARITY_TYPE_
                    )

                    pe = pathway_complement_edge(
                        edge_id            = edge_id,
                        beneficiary        = beneficiary,                             # target
                        donor              = donor,                                   # source
                        complement         = complement,
                        node_names         = node_names,
                        beneficiary_genome = ben_genome if config.onthefly else None,
                        donor_genome       = don_genome if config.onthefly else None,
                        update             = update,
                        cx_edges           = cx_edges,
                    )

                    _update_or_append(cx_edges, edge_id, pe, update)


def _set_none_genome(genome, sequence):
    return genome or sequence


def _hat_complement(complements: Dict) -> list:
    """
    Joins parts of each complementarity as returned from API in a single string devided by ^,
    so MGG can get a list of strings.
    """
    hat_compl = []
    if isinstance(complements, dict):
        for compl in complements.values():
            hat_compl.append("^".join(compl))
    else:
        _logger_.warning(f"complements is not in a dictionary type: {complements}")
    return hat_compl


def _get_edge_id(
    beneficiary: str, donor: str, node_names: List, edges: List, interaction_type: str
) -> Tuple[int, bool]:
    """
    Checks if an edge is already there of a specific source - target -interaction type.
    If yes, it returns the index of the edge in the edges list.
    Remember! Source and target are always the sequence identifiers.
    """
    target, source = node_names.index(beneficiary), node_names.index(donor)
    for idx, e in enumerate(edges):
        if e["s"] == source and e["t"] == target and e["v"]["interaction type"] == interaction_type:
            return idx, True
    return -1, False


def _update_or_append(lst: List, index: int, item: Dict, update: bool) -> None:
    """
    Either adds or updates entries of the list of edges (`lst`) with a new edge or a new set of attributes accordingly.

    Attention:
        Essential function for getting edge ids properly.

    Note:
        Does not return anything but **updates** the `lst`
    """
    if update:
        lst[index]['v'].update(item['v'])  # 👈 preserves other parts of edge
    else:
        lst.append(item)


# -----------------------------
# EDGES - SEED COMPLEMENTARITY
# -----------------------------
def _verbose_seed_complement(complements, beneficiarys_nonseed, kmap, shortener) -> List[list[str]]:
    """
    Appends the seed complementarities between two taxa as attributes to their corresponding edge
    id_x:
    id_y:
    """
    maps_in                   = list(kmap[kmap["modelseed"].isin(complements)]["map"].unique())
    complements_map           = kmap[kmap["modelseed"].isin(complements)]
    beneficiarys_nonseeds_map = kmap[kmap["modelseed"].isin(beneficiarys_nonseed)]

    complements_verbose = [
        [
            kmap.loc[kmap["map"] == kegg_map, "category"]
            .unique()
            .item(),  # KEGG metabolism category
            kmap.loc[kmap["map"] == kegg_map, "description"]
            .unique()
            .item(),  # category description
            ";".join(
                set(
                    complements_map.loc[complements_map["map"] == kegg_map, "modelseed"]
                )
            ),  # seed coomplements in modelseed
            ";".join(
                set(
                    complements_map.loc[
                        complements_map["map"] == kegg_map, "kegg_compound"
                    ]
                )
            ),  # seed complements in kegg
            build_url_with_seed_complements(  # URL
                list(
                    complements_map.loc[
                        complements_map["map"] == kegg_map, "kegg_compound"
                    ]
                ),
                list(
                    beneficiarys_nonseeds_map.loc[
                        beneficiarys_nonseeds_map["map"] == kegg_map, "kegg_compound"
                    ]
                ),
                kegg_map,
                shortener,
            ),
        ]
        for kegg_map in maps_in
    ]

    merged_compl = ["^".join(gcompl) for gcompl in complements_verbose]

    return merged_compl


def seed_complement_edge(
    edge_id,
    beneficiary,
    donor,
    complement,
    competition,
    cooperation,
    node_names,
    ben_patric   = None,
    donor_patric = None,
    update       = False,
    cx_edges     = None,
):
    """
    Conceptually, the donor is the source, since a compound would be secreted from it
    and drive to the beneficiary (target).
    This holds for the scores as well - for node_A in scores, we consider its seeds.
    Thus, the A of the score should be the beneficiary, i.e. target
    """

    ben_patric   = _set_none_genome(ben_patric, beneficiary)
    donor_patric = _set_none_genome(donor_patric, donor)

    if update:

        edge = cx_edges[edge_id]
        for x in [_SEED_COMP, _SEED_COOP]:
            if x not in edge["v"]:
                edge["v"][x] = set()

    else:

        edge = {
            "id": len(cx_edges),
            "s" : node_names.index(donor),
            "t" : node_names.index(beneficiary),
            "v" : {
                "interaction type": _COMPLEMENTARITY_TYPE_,
                "shared name"     : f"{beneficiary} {_COMPLEMENTING_} {donor}",
                _SEED_COMP: set(),
                _SEED_COOP: set()
            },
        }

    # Edge attributes
    edge["v"][_SEED_COMP].add(competition)
    edge["v"][_SEED_COOP].add(cooperation)

    complement_column = f"{_SEED_COMPL}::{ben_patric}:{donor_patric}"
    if complement is not None:
        edge["v"].update({complement_column: complement})

    return edge


def _seqids_to_gcs(mspecies_map_df):

    node_to_gtdb = defaultdict(set)

    for _, row in mspecies_map_df.iterrows():

        for node_col, gtdb_col in [
            ('node_A', 'gtdb_gen_repr_A'), ('node_B', 'gtdb_gen_repr_B')
        ]:

            node = row[node_col]
            gtdb = row[gtdb_col]

            if pd.notnull(gtdb):  # Skip NaNs
                node_to_gtdb[node].add(gtdb)

    # Optionally convert sets to sorted lists
    node_to_gtdb = {node: sorted(gtdbs) for node, gtdbs in node_to_gtdb.items()}

    return node_to_gtdb


def _assign_avg_std(edge, key):
    """Helper function to calculate average and standard deviation for seed scores"""

    if key not in edge["v"]:
        return

    values = [v for v in edge["v"][key] if v is not None]

    if not values:
        avg, std = None, None
    else:
        avg = statistics.mean(values)
        std = round(statistics.stdev(values), 3) if len(values) > 1 else None

    edge["v"][key] = avg
    edge["v"][f"{key}{_STD}"] = std


def process_se_edge(
    beneficiary,
    donor,
    ben_genome,
    don_genome,
    node_names,
    cx_edges,
    seed_scores,
    seed_complements_dict,
    non_seed_sets,
    kmap,
    shortener,

):
    # Get the id of the edge under study
    edge_id, update = _get_edge_id(
        beneficiary,
        donor,
        node_names,
        cx_edges,
        _COMPLEMENTARITY_TYPE_,
    )

    # Get competition and cooperation scores
    scores = seed_scores.query("A == @ben_genome and B == @don_genome")
    if not scores.empty:
        competAB, cooperAB = scores.iloc[0][["Competition", "Cooperation"]]
    else:
        competAB, cooperAB = None, None

    # Get complement data
    seed_complementAB = seed_complements_dict.get(ben_genome, {}).get(don_genome, None)
    if seed_complementAB is None or (
        hasattr(seed_complementAB, "__len__") and not len(seed_complementAB)
    ) or (
        isinstance(seed_complementAB, (list, np.ndarray)) and pd.isna(seed_complementAB).all()
    ):
        _logger_.warning(f"None complement for beneficiary: {beneficiary} and donor {donor}")
        return None

    # Get non-seed set for beneficiary
    if ben_genome in non_seed_sets.index:
        beneficiarys_nonseed = non_seed_sets.loc[ben_genome].to_list()[0]
    else:
        _logger_.info(f"Skip beneficiary {ben_genome} for {beneficiary} since no nonseed set.")
        return None

    # Verbose seed complement transformation
    try:
        seed_complementAB = (
            _verbose_seed_complement(seed_complementAB, beneficiarys_nonseed, kmap, shortener)
            if seed_complementAB is not None
            else []
        )
    except Exception as e:
        _logger_.error(f"Error processing seed complement for {beneficiary}–{donor}: {e}")
        return None

    # Create the edge
    se = seed_complement_edge(
        edge_id      = edge_id,
        beneficiary  = beneficiary,
        donor        = donor,
        complement   = seed_complementAB,
        competition  = competAB,
        cooperation  = cooperAB,
        node_names   = node_names,
        ben_patric   = ben_genome,
        donor_patric = don_genome,
        update       = update,
        cx_edges     = cx_edges,
    )

    return edge_id, se, update


def seed_complements(
    config,
    edgelist_df,
    node_names,
    cx_edges
):

    shortener = pyshorteners.Shortener() if config.tinyurl else None
    kmap      = load_seed_complement_files(config.kegg_mappings)

    seed_scores = pd.read_csv(
        config.seed_scores,
        sep      = "\t",
        header   = None,
        skiprows = 1,
        names    = ["A", "B", "Competition", "Cooperation"]
    )
    seed_scores['A'] = seed_scores['A'].astype(str)
    seed_scores['B'] = seed_scores['B'].astype(str)

    # NOTE (Haris Zafeiropoulos, 2025-03-26):
    # Remember we only focus on the KEGG MODULES related seeds, nonseeds and compls
    _logger_.info(f"~ module_nonseeds: {config.module_nonseeds}")
    with open(config.module_nonseeds, "rb") as f:
        non_seed_sets = pickle.load(f)

    _logger_.info(f"~ sc_pkl: {config.sc_pkl}")
    with open(config.sc_pkl, "rb") as f:
        seed_complements = pickle.load(f)

    seed_complements_dict = seed_complements.to_dict(orient="index")
    nodes_in_compls       = set(seed_complements_dict.keys())

    # On the on the fly versioin, we need to further build a map for a sequence iid and its genomes
    if config.onthefly:

        # Get dictionary with sequence identifiers to their mapped GTDB genomes
        seqids_to_gc = _seqids_to_gcs(config.mspecies_map_df)

        # Get dictionary with sequence identifiers to their corresponding PATRIC ids
        node_to_patric = {
            node: list({
                str(config.gc_to_patric_ids.get(gtdb))
                for gtdb in gtdbs
                if config.gc_to_patric_ids.get(gtdb) is not None
            })
            for node, gtdbs in seqids_to_gc.items()
        }

        # Keep a set with sequence identifiers that do have a PATRIC id
        nodes_in_compls = set(x for x in node_to_patric.keys())

    # NOTE (Haris Zafeiropoulos, 2025-05-27):
    # Each link is a co-occurrence edge on the network
    for _, link in edgelist_df.iterrows():

        node_a, node_b, _ = link

        if node_a not in nodes_in_compls or node_b not in nodes_in_compls:
            continue

        # NOTE (Haris Zafeiropoulos, 2025-05-27):
        # Each of the two cases of the following loop, corresponds to one directed edge on the network
        for beneficiary, donor in [(node_a, node_b), (node_b, node_a)]:

            ben_ids = node_to_patric[beneficiary] if config.onthefly else [beneficiary]
            don_ids = node_to_patric[donor] if config.onthefly else [donor]

            for ben_genome in ben_ids:

                for don_genome in don_ids:

                    if (res := process_se_edge(
                        beneficiary, donor,
                        ben_genome, don_genome,
                        node_names, cx_edges,
                        seed_scores, seed_complements_dict,
                        non_seed_sets, kmap, shortener,
                    )) is not None:

                        edge_id, se, update = res
                        _update_or_append(cx_edges, edge_id, se, update)

    # Average seed scores
    for edge in cx_edges:
        for key in [_SEED_COMP, _SEED_COOP]:
            _assign_avg_std(edge, key)


# -----------------------------
# NETWORK
# -----------------------------
def build_cx2(nodes: Dict[str, dict], edges: Dict[str, dict]) -> ndex2.cx2.CX2Network:
    """
    Builds the microbetag annotated network in a CX2 format (https://cytoscape.org/cx/).

    To this end, the function exploits the ndex2 Python library (https://ndex2.readthedocs.io/) while the MGG
    Java app, needs to specify that the expected response from microbetag, is in CX2.
    -- See CreateNetworkTask.java and the cytoscapeAPIURL.

    """
    # Create an empty net cx
    cx2 = ndex2.cx2.CX2Network()

    # Add nodes on the cx2
    # -- we sort alphabetically the keys of the attributes so, they are displayed together in the Nodes panel
    node_attributes = [dict(sorted(node["v"].items())) for node in nodes]  # node["v"]

    for node_attributes in node_attributes:

        cx2.add_node(attributes=node_attributes)

    # Add edges on the cx2
    for edge in edges:

        source, target = edge["s"], edge["t"]

        # Like in the nodes case, we sort keys of the attributes alphabetically
        attributes = dict(sorted(edge["v"].items())).copy()

        if attributes["interaction type"] in ["depletion", "cooccurrence"]:
            attributes[_M_WEIGHT] = float(edge["v"][_M_WEIGHT])

        filtered_attributes = {
            key: value
            for key, value in attributes.items()
            if not (isinstance(value, list) and len(value) == 0)
        }

        # create an edge connecting the nodes, id of edge is returned
        _ = cx2.add_edge(
            source     = source,
            target     = target,
            attributes = filtered_attributes
        )

    return cx2


def load_otf_seq_map(df: pd.DataFrame) -> Dict:
    """
    Gets the df from the taxonomy.py returned when ran through the app.py and returns the equivalent
    seqId_taxonomy of the stand-alone case.

    Args:
        df:

    Returns:
        seq_map_dict: A dictionary with sequence id (seqId) as key and the NCBI Taxonomy ids found along with their
                      corresponding taxonomic ranks and in case of genomes found those as well.
                      Different NCBI Tax Ids and levels are split by ',' while genomes of the same case, split by ';'
    Example:
        'ASV0005': {'ncbi_tax_id': '411903,74426', 'ncbi_tax_level': 'mspecies,mspecies',
                    'gtdb_genomes': ['GCA_010509075.1', 'GCA_001404695.1']}
         'ASV0021': {'ncbi_tax_id': '1121308,1496', 'ncbi_tax_level': 'mspecies,mspecies',
                    'gtdb_genomes': ["GCA_001077535.2';'GCA_001077535.1", 'GCA_001299635.1']}
    """
    seq_map_dict = {}
    for seq_id, group in df.groupby('seqId'):
        tax_ids      = []
        tax_levels   = []
        gtdb_genomes = []
        all_levels   = []

        for _, row in group.iterrows():

            # Handle NaNs in ncbi_tax_id
            tax_id     = row.get('ncbi_tax_id')
            tax_id_str = '' if pd.isna(tax_id) else str(int(tax_id)) if isinstance(tax_id, float) else str(tax_id)
            tax_ids.append(tax_id_str)

            # Handle tax level
            tax_level = row.get('ncbi_tax_level', '')
            tax_levels.append('-' if pd.isna(tax_level) else str(tax_level))

            # Handle genomes: split comma-separated string, then rejoin with ';' if multiple
            genomes = row.get('gtdb_gen_repr')

            if pd.isna(genomes):
                gtdb_genomes.append('')
            else:
                gtdb_genomes.append(";".join(genomes))

            all_levels.append([row.get(x) for x in __RANKS__])

        seq_map_dict[seq_id] = {
            'ncbi-tax-id'   : tax_ids if not all(x == "" for x in tax_ids) else ["NA"],
            'ncbi-tax-level': tax_levels if not all(x == "" for x in tax_levels) else ["NA"],
            'gtdb-genomes'  : gtdb_genomes if not all(x == "" for x in gtdb_genomes) else ["NA"]
        }

        levels = [
            col[0]
            if all(x == col[0] for x in col)
            else ""
            for col in zip(*all_levels)
        ] if len(all_levels) > 1 else all_levels[0]

        for rank, tax_level in zip(__RANKS__, levels):
            seq_map_dict[seq_id][rank] = tax_level

    return seq_map_dict


def apply_layout(net_cx2, manta_layout):

    # Build name -> ID mapping using dict comprehension
    node_name_to_id = {net_cx2.get_node(n)["v"]["name"]: n for n in net_cx2.get_nodes()}

    # Set x and y layout attributes for nodes present in the layout
    for node in manta_layout:
        node_id = node_name_to_id.get(node["node"])
        if node_id is not None:
            net_cx2.set_node_attribute(node_id=node_id, attribute="x", value=node["x"])
            net_cx2.set_node_attribute(node_id=node_id, attribute="y", value=node["y"])


def mtg_annotate_network(config: "Config") -> ndex2.cx2.CX2Network:
    """
    Wrapper function for getting the various annotations previously made for a microbetag run
    and building a microbetag annotated network in a CX2 format.

    Arguments:
        config: An instance of the microbetag configuration :class:`Config` class.

    Returns:
        A :class:`ndex2.cx2.CX2Network()` object for the microbetag-annotated network in CX2 format.
    """

    # Get the non-annotated network as dataframe
    edgelist_df = get_edgelist(config.network)

    # e.g.  'bin_31':
    # 'd__Bacteria;p__Proteobacteria;c__Alphaproteobacteria;o__Reyranellales;f__Reyranellaceae;g__Reyranella;s__',
    df             = config.seq_to_taxon_df
    seqId_taxonomy = df.set_index(df.columns[0])[df.columns[1]].to_dict()

    # Initialize non-annotated nodes and edges of the network in a format
    # that can be used as input for the ndex2 library
    nodes, node_names, edges = init_nodes_and_edges(
        edgelist_df,
        seqId_taxonomy,
        config.onthefly,
        getattr(config, 'metadata_file', None),
        getattr(config, 'otf_seq_tax_df', None)
    )

    # PHENOTREX ANNOTATIONS
    if config.phen_traits and os.listdir(getattr(config, "phen_traits_dir", [])):
        _logger_.info("-- Loading phenotrex-based traits\n")
        update_with_phen_traits(
            nodes            = nodes,
            node_names       = node_names,
            phen_traits_dir = config.phen_traits_dir,
            onthefly         = config.onthefly
        )

    # FAPROTAX
    if config.faprotax and os.listdir(getattr(config, "faprotax_sub_tables", [])):
        _logger_.info("-- Loading FAPROTAX traits\n")
        update_with_faprotax_traits(
            nodes       = nodes,
            node_names  = node_names,
            fapr_tables = config.faprotax_sub_tables,
            seq_col     = config.sequence_id_column_name
        )

    # CLUSTERING
    manta_layout = None
    if config.net_cluster:

        if os.path.exists(config.manta_net):
            _logger_.info("-- Loading manta clusters\n")
            manta_layout = update_with_manta(
                nodes      = nodes,
                node_names = node_names,
                manta_net  = config.manta_net
            )
        else:
            _logger_.warning("! manta was not able to run successfully.")

    # PATHWAY COMPL
    if config.path_compl:

        _logger_.info("-- Loading pathway complements\n")
        pathway_complements(config, edgelist_df, node_names, edges)

    # SEED COMPL
    if config.seed_compl:

        _logger_.info("-- Loading seed complements\n")
        seed_complements(config, edgelist_df, node_names, edges)

    # Build cx2
    net_cx2 = build_cx2(nodes, edges)

    if manta_layout:
        apply_layout(net_cx2, manta_layout)

    timepoint   = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
    default_cx2 = os.path.join(config.outdir, f"mtag_net_{timepoint}.cx2")
    cx2_file    = getattr(config, "mtg_net", default_cx2)

    net_cx2.set_network_attributes({"name": f"microbetag network @ {timepoint}"})
    net_cx2.write_as_raw_cx2(cx2_file)

    return net_cx2
