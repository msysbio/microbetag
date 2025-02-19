import logging
import json
import pandas as pd
import networkx as nx

from .utils import detect_separator, find_three_column_format

# Base .cx  -- TODO : CHECK ID DEPRECATED
def build_edge_list(edgelist, metadata_file=None):
    """
    Read an edge list and build a dataframe with the corresponding NCBI IDs for each pair,
    if and only if both OTUs have been mapped to an NCBI tax ID.
    NOTE: edge_list_of_ncbi_ids() on microbetagApp

    Parameters:
    - edgelist (str): Path to the edge list file.
    - metadata_file (str, optional): Path to the metadata file containing elements to exclude.

    Returns:
    - pd.DataFrame: Filtered edge list with NCBI tax IDs.
    - pd.DataFrame (optional): Edges that were excluded based on metadata.
    """
    # Read the edge list into a DataFrame
    pd_edgelist = pd.read_csv(edgelist, sep="\t", header=None, names=["node_a", "node_b", "score"])  # skiprows=

    if metadata_file:
        # Read the metadata file and create a list of elements to exclude
        elements_to_exclude = pd.read_csv(metadata_file, sep="\t", header=None, index_col=0).index.to_list()

        # Define a mask to filter out rows with nodes in the exclusion list
        mask = ~pd_edgelist.apply(lambda row: any(env in row['node_a'] or env in row['node_b'] for env in elements_to_exclude), axis=1)

        # Separate DataFrame based on the mask
        pd_filtered_edgelist = pd_edgelist[mask].copy()
        pd_metadata_edges = pd_edgelist[~mask].copy()

        # Create 'pair-of-taxa' column for filtered edges
        pd_filtered_edgelist["pair-of-taxa"] = pd_filtered_edgelist['node_a'] + ":" + pd_filtered_edgelist["node_b"]

        return pd_filtered_edgelist, pd_metadata_edges
    else:
        # Return the original edge list if no metadata file is provided
        pd_edgelist["pair-of-taxa"] = pd_edgelist['node_a'].astype(str) + ":" + pd_edgelist["node_b"]
        return pd_edgelist


# Annotated .cx network related
def read_cyjson(filename, direction=False):
    """
    Function based on the corresponding of the manta library:
    https://github.com/ramellose/manta/blob/master/manta/cyjson.py

    Small utility function for reading Cytoscape json files generated with CoNet.
    In our case, it also gets the layout and adds it as part of the node data.

    Parameters
    ----------
    :param filename: Filepath to location of cyjs file.
    :param direction: If true, graph is imported as a NetworkX DiGraph
    :return: NetworkX graph.
    """
    with open(filename) as f:
        data = json.load(f)
    name = 'name'
    ident = 'id'
    if len(set([ident, name])) < 2:
        raise nx.NetworkXError('Attribute names are not unique.')
    if direction:
        graph = nx.DiGraph()
    else:
        graph = nx.Graph()
    graph.graph = dict(data.get('data'))
    i = 0
    for d in data["elements"]["nodes"]:
        # only modification: 'value' key is not included in CoNet output
        # now graph only needs ID and name values
        node_data = d["data"].copy()
        position = d["position"]
        node_data["position"] = position
        try:
            node = d["data"].get(ident)
        except KeyError:
            # if no index is found, one is generated
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


def get_edgelist(conf):
    """ Loads a 3-column network file as pd.DataFrame"""
    delimiter = detect_separator(conf.network)
    line_num, header = find_three_column_format(conf.network, delimiter)
    edgelist = pd.read_csv(conf.network, sep=delimiter, skiprows=line_num-1, header=header)

    return edgelist


def build_base_graph(conf):  # edgelist_as_a_list_of_dicts, microb_id_taxonomy,
    """
    Runs if manta has been asked for from the user.
    manta gets a .cyjs input file.
    This function builds an non-annotated graph using only the scores and the taxonomies of the taxa of the network.
    It get a list of dictionaries where each dictionary is an edge and returns the basenetwork in a .cyjs format.
    """

    edgelist = get_edgelist(conf)
    edgelist.columns = ["node_a", "node_b", "microbetag::weight"]
    edgelist_as_a_list_of_dicts = edgelist.to_dict(orient="records")

    base_network = {}
    base_network["elements"] = {}
    nodes = []
    edges = []
    processed_nodes = set()
    counter = 1

    for edge in edgelist_as_a_list_of_dicts:
        # Node A
        node_name_a = edge["node_a"]
        is_taxon = False
        if node_name_a in conf.seq_ids:
            is_taxon = True
        if node_name_a not in processed_nodes:
            processed_nodes.add(node_name_a)
            node_a = build_a_base_node(node_name_a, conf.seq_to_taxon_df, is_taxon)
            nodes.append(node_a)

        # Node B
        node_name_b = edge["node_b"]
        is_taxon = False
        if node_name_b in conf.seq_ids:
            is_taxon = True
        if node_name_b not in processed_nodes:
            processed_nodes.add(node_name_b)
            node_b = build_a_base_node(node_name_b, conf.seq_to_taxon_df, is_taxon)
            nodes.append(node_b)

        # Edge A-B
        new_edge = {}
        new_edge["data"] = {}
        new_edge["data"]["id"] = str(counter)
        new_edge["data"]["source"] = node_name_a
        new_edge["data"]["target"] = node_name_b
        new_edge["data"]["selected"] = False

        new_edge["data"]["shared_name"] = node_name_a.split(";")[-1] + "-" + node_name_b.split(";")[-1]

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
    base_network["data"]["title"] = "microbetag annotated microbial co-occurrence network"
    base_network["data"]["tags"] = ["v1.0"]
    return base_network


def build_a_base_node(node_name, map_seq, is_taxon: bool):
    """
    Builds a node for the base network.
    [TODO] Remove not necessary entries.
    """
    node = {}
    node["data"] = {}
    node["data"]["id"] = node_name
    node["data"]["selected"] = False

    if is_taxon:
        case = map_seq[map_seq["sequence_id"] == node_name]
        node["data"]["taxonomy"] = case["taxonomy"].item()
        node["data"]["name"] = case["taxonomy"].item().split(";")[-1]
        try:
            node["data"]["GTDB-representative"] = case["gtdb_gen_repr"]
        except:
            logging.info("Custom genome, thus no GTDB one used for predictions.")
            pass

    return node
