import json
import pandas as pd
import networkx as nx
from typing import TYPE_CHECKING

from .utils import detect_separator, find_three_column_format, mtg_logger
if TYPE_CHECKING:
    from .config import Config

_logger_ = mtg_logger(__name__)


# Annotated .cx network related
def read_cyjson(filename: str, direction: bool = False) -> nx.Graph:
    """
    Function based on the corresponding of the manta library:
    https://github.com/ramellose/manta/blob/master/manta/cyjson.py

    Small utility function for reading Cytoscape json files generated with CoNet.
    In our case, it also gets the layout and adds it as part of the node data.

    Args:
        filename: Filepath to `.cyjs` network file.
        direction: If True, graph is imported as a :class:`networkx.DiGraph`

    Returns:
        A :class:`networkx.Graph` object.
        In the microbetag framework, it is being used to load the `manta` output.
    """
    with open(filename) as f:
        data = json.load(f)
    name = "name"
    ident = "id"
    if len(set([ident, name])) < 2:
        raise nx.NetworkXError("Attribute names are not unique.")
    if direction:
        graph = nx.DiGraph()
    else:
        graph = nx.Graph()
    graph.graph = dict(data.get("data"))
    i = 0
    for d in data["elements"]["nodes"]:
        # only modification: 'value' key is not included in CoNet output
        # now graph only needs ID and name values
        node_data = d["data"].copy()
        position  = d["position"]
        node_data["position"] = position
        try:
            node = d["data"].get(ident)
        except KeyError:
            # If no index is found, one is generated
            node = i
            i += 1
        if d["data"].get(name):
            node_data[name] = d["data"].get(name)

        graph.add_node(node)
        graph.nodes[node].update(node_data)
    for d in data["elements"]["edges"]:
        edge_data = d["data"].copy()
        sour = d["data"].pop("source")
        targ = d["data"].pop("target")
        graph.add_edge(sour, targ)
        graph.edges[sour, targ].update(edge_data)
    return graph


def get_edgelist(network_file: str) -> pd.DataFrame:
    """
    Loads a 3-column network file as pd.DataFrame

    Args:
        network_file: Filepath to the edgelist.
    Returns:
        A 3-column pandas.DataFrame
    """

    delimiter        = detect_separator(network_file)
    line_num, header = find_three_column_format(network_file, delimiter)

    edgelist = pd.read_csv(
        network_file, sep=delimiter, skiprows=line_num - 1, header=header
    )
    edgelist.columns = ["node_A", "node_B", "microbetag::weight"]

    return edgelist


def build_base_graph(conf: "Config") -> dict:  # edgelist_as_a_list_of_dicts, microb_id_taxonomy,
    """
    Builds a non-annotated graph in a .cyjs format, 
    using only the scores and the taxonomies of the taxa of the network.
    To be used only when manta clustering has been asked.

    Args:
        conf: A utils.Config instance.

    Returns:
        The base network as a dictionary.

    Note:
        Runs if network clustering has been asked for from the user, 
        converting the initial .csv edgelist to .cyjs
        since `manta` gets a .cyjs input file.
    """

    edgelist = get_edgelist(conf.network)
    edgelist.columns = ["node_A", "node_B", "microbetag::weight"]
    edgelist_as_a_list_of_dicts = edgelist.to_dict(orient="records")

    base_network = {}
    base_network["elements"] = {}
    nodes = []
    edges = []
    processed_nodes = set()
    counter = 1

    for edge in edgelist_as_a_list_of_dicts:
        # Node A
        node_name_a = edge["node_A"]
        is_taxon = False
        if node_name_a in conf.seq_ids:
            is_taxon = True
        if node_name_a not in processed_nodes:
            processed_nodes.add(node_name_a)
            node_a = _build_a_base_node(node_name_a, conf.seq_to_taxon_df, is_taxon)
            nodes.append(node_a)

        # Node B
        node_name_b = edge["node_B"]
        is_taxon = False
        if node_name_b in conf.seq_ids:
            is_taxon = True
        if node_name_b not in processed_nodes:
            processed_nodes.add(node_name_b)
            node_b = _build_a_base_node(node_name_b, conf.seq_to_taxon_df, is_taxon)
            nodes.append(node_b)

        # Edge A-B
        new_edge = {}
        new_edge["data"] = {}
        new_edge["data"]["id"] = str(counter)
        new_edge["data"]["source"] = node_name_a
        new_edge["data"]["target"] = node_name_b
        new_edge["data"]["selected"] = False

        new_edge["data"]["shared_name"] = (
            node_name_a.split(";")[-1] + "-" + node_name_b.split(";")[-1]
        )

        new_edge["data"]["SUID"] = str(counter)
        new_edge["data"]["name"] = "co-occurrence"
        new_edge["data"]["weight"] = float(edge["microbetag::weight"])
        new_edge["selected"] = False
        edges.append(new_edge)
        counter += 1

    # Ensure .cyjs format
    base_network["elements"]["nodes"] = nodes
    base_network["elements"]["edges"] = edges
    base_network["data"] = {}
    base_network["data"][
        "title"
    ] = "microbetag annotated microbial co-occurrence network"
    base_network["data"]["tags"] = ["v1.0"]
    return base_network


def _build_a_base_node(node_name, map_seq, is_taxon: bool) -> dict:
    """    Builds a node for the base network.    """
    node = {}
    node["data"] = {}
    node["data"]["id"] = node_name
    node["data"]["selected"] = False

    return node
