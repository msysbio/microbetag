"""
Aim:
    Gets an edgelist as input along with a df mentioning the NCBI Tax ids and the GTDB ids of the corresponding taxa
    and based on the annotation types asked, it build a cx-format graph that is going to be the final return object of microbetag

Author:
    Haris Zafeiropoulos

Based on:
    https://github.com/msysbio/microbetagApp/blob/develop/services/web/microbetag/scripts/buid_cx_annotated_graph.py
"""
import os
import pickle
import json
import logging
import datetime
import ndex2.cx2
import pyshorteners
import pandas as pd
from typing import Dict

from .networks import get_edgelist, read_cyjson
from .utils import extend_complements, extend_faprotax, load_phenotypic_traits
from .seed_complementarity import build_url_with_seed_complements, load_seed_complement_files



def build_pseudo_cx(conf):
    """
    Builds a .cx (version 2) file, the user can then load on Cytoscape and parse it through the MGG app.

    Important! In every case, we need a way to map sequence id to a taxonomy.
    Either an abundance table or a sequence id to taxonomy map (``sequence_id_taxonomy_map``) is required.
    """
    # Load edgelist
    edgelist = get_edgelist(conf)

    # Get pairs of nodes with an association
    unique_associated_pairs = {tuple(row) for _, row in edgelist.iloc[:, :2].iterrows()}

    # Make the map sequence to taxon df a dictionary
    seq_id_to_taxonomy_dic = conf.seq_to_taxon_df.set_index(
        conf.seq_to_taxon_df.columns[0]
        )[ conf.seq_to_taxon_df.columns[1] ].to_dict()

    # Init formatting microbetag annotations
    annotated_cx = []
    init = {}
    init["numberVerification"] = [{"longNumber": 281474976710655}]
    annotated_cx.append(init)

    metadata = {}
    metadata["metaData"] = [
        {"name": "cyTableColumn", "version": "1.0"},
        {"name": "nodes", "version": "1.0"},
        {"name": "edges", "version": "1.0"},
        {"name": "nodeAttributes", "version": "1.0"},
        {"name": "edgeAttributes", "version": "1.0"},
        {"name": "networkAttributes", "version": "1.0"},
        {"name": "cartesianLayout", "version": "1.0"},
    ]
    annotated_cx.append(metadata)

    # ===========
    # GET COLUMN NAMES FOR ALL TABLES
    # ===========
    table_columns = {}
    table_columns["cyTableColumn"] = []
    cyTableColumns = [
        # for node table mandatory
        {"applies_to": "node_table", "n": "@id", "d": "string"},
        {"applies_to": "node_table", "n": "name", "d": "string"},
        # microbetag-oriented columns
        {"applies_to": "node_table", "n": "microbetag::taxon name", "d": "string"},
        {"applies_to": "node_table", "n": "microbetag::namespace"},
        {"applies_to": "node_table", "n": "microbetag::taxonomy", "d": "string"},
        {"applies_to": "node_table", "n": "microbetag::gtdb-genomes", "d": "list_of_string"},
        {"applies_to": "node_table", "n": "microbetag::ncbi-tax-level", "d": "string"},
        # for edge table mandatory
        {"applies_to": "edge_table", "n": "shared name"},
        {"applies_to": "edge_table", "n": "interaction type"},
        {"applies_to": "edge_table", "n": "microbetag::weight", "d": "double"}
    ]

    """Phen traits"""
    # IF PHEND ASKED..?
    logging.info("Loading phenotypic traits")
    bin_phen_traits, phentraits = load_phenotypic_traits(conf)

    for term in phentraits:
        cyTableColumns.extend([
            {"applies_to": "node_table", "n": "::".join(["phendb", term]), "d": "boolean"},
            {"applies_to": "node_table", "n": "::".join(["phendbScore", "".join([term, "Score"])]), "d": "double"}
        ])

    """FAPROTAX traits"""
    bin_faprotax_traits = faprotax_traits = None
    if conf.abundance_table is not None:
        logging.info("Loading FAPROTAX traits")
        bin_faprotax_traits, faprotax_traits = extend_faprotax(conf=conf)
        # Node columns reg. FAPROTAX annotations
        for term in faprotax_traits:
            column = {"applies_to": "node_table", "n": "::".join(["faprotax", term]), "d": "boolean"}
            cyTableColumns.append(column)

    """PATHWAY complements"""
    logging.info("Loading patwhay complementarities")
    complements_dict_ext = None
    if conf.pathway_complementarity:

        complements_dict_ext = extend_complements(
            complements_json=conf.compl_file, descrps_path=conf.module_descriptions,
            max_scratch_alt=conf.max_scratch_alt, pathway_complements_dir=conf.pathway_complements_dir,
            pathway_complement_percentage=conf.pathway_complement_percentage,
        )

        for edge in unique_associated_pairs:
            edge_col = {"applies_to": "edge_table", "n": "".join(["compl::", edge[0], ":", edge[1]]), "d": "list_of_string"}
            cyTableColumns.append(edge_col)

    """SEED complements"""
    logging.info("Loading seeds complementarities")
    kmap = seed_scores = non_seed_sets = seed_complements_dict = None
    if conf.seed_complementarity:

        kmap = load_seed_complement_files(conf.kegg_mappings)

        with open(conf.module_related_non_seeds, "rb") as f:
            non_seed_sets = pickle.load(f)

        with open(conf.seed_complements, "rb") as f:
            seed_complements = pickle.load(f)

        # NOTE: rows of the df from pickle will be keys -- beneficiary ; columns the donor
        seed_complements_dict = seed_complements.to_dict(orient="index")

        for beneficiary, donors in seed_complements_dict.items():
            for donor, complements in donors.items():
                if len(complements) > 0:
                    cyTableColumns.append(
                        {"applies_to": "edge_table",
                            "n": "".join(["seedCompl::", beneficiary, ":", donor]),
                            "d": "list_of_string"}
                    )
        """SEED scores"""
        cyTableColumns.extend([
            {"applies_to": "edge_table", "n": "::".join(["seed", "competition"]), "d": "double"},
            {"applies_to": "edge_table", "n": "::".join(["seed", "cooperation"]), "d": "double"}
        ])
        seed_scores = pd.read_csv(conf.phylomint_scores, sep="\t", header=None, skiprows=1)
        seed_scores.columns = ["A", "B", "Competition", "Complementarity"]

    """MANTA CLUSTERS"""
    manta_annotations = cartesianLayout = None
    if conf.network_clustering:
        cartesianLayout = {}; cartesianLayout["cartesianLayout"] = []
        m1 = {"applies_to": "node_table", "n": "::".join(["manta", "cluster"]), "d": "integer"}
        m2 = {"applies_to": "node_table", "n": "::".join(["manta", "assignment"]), "d": "string"}
        cyTableColumns.append(m1)
        cyTableColumns.append(m2)
        # manta_output_file = conf.manta_net     #  "/".join([conf.output_dir, 'manta_annotated.cyjs'])
        manta_net = read_cyjson(conf.manta_net)
        clusters = list(manta_net.nodes(data="cluster"))
        assignments = list(manta_net.nodes(data="assignment"))
        positions = list(manta_net.nodes(data="position"))
        manta_annotations = {}
        for pair in clusters:
            manta_annotations[pair[0]] = {}
            manta_annotations[pair[0]]["cluster"] = pair[1]
        for pair in assignments:
            manta_annotations[pair[0]]["assignment"] = pair[1]
        for pair in positions:
            manta_annotations[pair[0]]["position"] = pair[1]

    table_columns["cyTableColumn"] = cyTableColumns
    annotated_cx.append(table_columns)

    # ===========
    # NETWORK TABLE
    # ===========
    networkAttributes = {}
    networkAttributes["networkAttributes"] = []
    networkAttributes["networkAttributes"].extend([
        {"n": "network type", "v": "microbetagAnnotated"},
        {"n": "name", "v": "microbetagNetwork"},
        {"n": "uri", "v": "https://hariszaf.github.io/microbetag/"},
        {"n": "version", "v": "1.0"}
    ])
    annotated_cx.append(networkAttributes)

    # NODES TABLE
    nodes, nodeAttributes, seq_to_nodeID, node_counter = build_mtg_nodes(
        conf, edgelist, seq_id_to_taxonomy_dic, bin_phen_traits, bin_faprotax_traits,
        manta_annotations, cartesianLayout
    )
    annotated_cx.append(nodes)
    annotated_cx.append(nodeAttributes)

    # ===========
    # EDGES TABLE
    # ===========
    edges, edgeAttributes = build_mtg_edges(conf, edgelist, seq_to_nodeID, node_counter, complements_dict_ext, seed_scores, seed_complements_dict, non_seed_sets, kmap)

    annotated_cx.append(edges)
    annotated_cx.append(edgeAttributes)

    # POST-metadata
    post_metadata = {}
    post_metadata["metaData"] = []
    post_metadata["metaData"].extend([
        {"name": "nodeAttributes", "elementCount": len(nodeAttributes["nodeAttributes"]), "version": 1.0},
        {"name": "edgeAttributes", "elementCount": len(edgeAttributes["edgeAttributes"]), "version": 1.0},
        {"name": "cyTableColumn", "elementCount": len(table_columns["cyTableColumn"]), "version": 1.0},
        {"name": "edges", "elementCount": len(edges["edges"]), "idCounter": node_counter + 1000, "version": 1.0},
        {"name": "nodes", "elementCount": len(nodes["nodes"]), "idCounter": 1001, "version": 1.0},
        {"name": "networkPropernetworkAttributesties", "elementCount": len(networkAttributes["networkAttributes"]), "version": 1.0},
    ])
    annotated_cx.append(post_metadata)

    # Status
    status = {}; status["status"] = []
    status["status"].append({"error": "", "success": True})
    annotated_cx.append(status)

    return annotated_cx


def build_mtg_nodes(conf, edgelist, seq_id_to_taxonomy, phen_traits, faprotax_traits, manta_annotations=None, cartesian_layout=None):
    """
    Builds the nodes and attributes for the pseudo-CX Microbetag network.
    """
    def add_node_attribute(attributes, node_id, name, value, dtype):
        """Helper function to add a node attribute."""
        attributes.append({"po": node_id, "n": name, "v": value, "d": dtype})

    def handle_phen_traits(node_id, seq_id, phen_traits, attributes):
        """Handles phenotypic traits for a node."""
        if seq_id in phen_traits:
            for trait, data in phen_traits[seq_id].items():
                presence = data.get("presence") == "YES"
                confidence = data.get("confidence", 0.0)
                add_node_attribute(attributes, node_id, f"phendb::{trait}", presence, "boolean")
                add_node_attribute(attributes, node_id, f"phendbScore::{trait}Score", str(confidence), "double")
            return True
        return False

    def handle_faprotax_traits(node_id, seq_id, faprotax_traits, attributes):
        """Handles FAPROTAX traits for a node."""
        if seq_id in faprotax_traits:
            for term in faprotax_traits[seq_id]:
                add_node_attribute(attributes, node_id, f"faprotax::{term}", True, "boolean")

    def handle_manta_annotations(node_id, seq_id, manta_annotations, layout, attributes):
        """Handles manta cluster annotations and Cartesian layout."""
        if seq_id in manta_annotations:
            annotation = manta_annotations[seq_id]
            add_node_attribute(attributes, node_id, "manta::cluster", int(annotation["cluster"]), "integer")
            add_node_attribute(attributes, node_id, "manta::assignment", annotation["assignment"], "string")
            layout["cartesianLayout"].append({
                "node": node_id,
                "x": annotation["position"]["x"],
                "y": annotation["position"]["y"]
            })

    set_of_nodes = set(edgelist.iloc[:, :2].values.ravel())
    nodes = {"nodes": []}
    node_attributes = {"nodeAttributes": []}
    seq_to_node_id = {}
    node_counter = 1000

    for node_name in set_of_nodes:
        node_counter += 1
        node_id = node_counter
        seq_to_node_id[node_name] = node_id

        # Add basic node information
        nodes["nodes"].append({"@id": node_id, "n": node_name})
        add_node_attribute(node_attributes["nodeAttributes"], node_id, "@id", node_name, "string")
        add_node_attribute(node_attributes["nodeAttributes"], node_id, "name", node_name, "string")

        if node_name in conf.seq_ids:
            check_mspecies = False

            # Handle phenotypic traits
            if handle_phen_traits(node_id, node_name, phen_traits, node_attributes["nodeAttributes"]):
                check_mspecies = True

            # Handle FAPROTAX traits
            if conf.abundance_table is not None:
                handle_faprotax_traits(node_id, node_name, faprotax_traits, node_attributes["nodeAttributes"])

            # Add taxonomy information
            tax_level = "mspecies" if check_mspecies else "other"
            add_node_attribute(node_attributes["nodeAttributes"], node_id, "microbetag::ncbi-tax-level", tax_level, "string")
            taxonomy = seq_id_to_taxonomy.get(node_name)
            if taxonomy:
                add_node_attribute(node_attributes["nodeAttributes"], node_id, "microbetag::taxonomy", taxonomy, "string")
            else:
                logging.info(f"No taxonomy found for node {node_name}")

        # Handle manta annotations if clustering is enabled
        if conf.network_clustering and manta_annotations:
            handle_manta_annotations(node_id, node_name, manta_annotations, cartesian_layout, node_attributes["nodeAttributes"])

        # Assign metavariables if metadata is provided
        if conf.metadata_file is not None and node_name not in conf.seq_ids:
            add_node_attribute(node_attributes["nodeAttributes"], node_id, "microbetag::ncbi-tax-level", "metavar", "string")

    return nodes, node_attributes, seq_to_node_id, node_counter


def build_mtg_edges(conf, edgelist, seq_to_nodeID, node_counter, complements_dict_ext, seed_scores, seed_complements_dict, non_seed_sets, kmap):

    edges = {}; edges["edges"] = []
    edgeAttributes = {}; edgeAttributes["edgeAttributes"] = []
    edge_counter = node_counter + 1000

    shortener = pyshorteners.Shortener() if conf.tinyurl else None

    logging.info("Shortener in the main build_cx function is %s" % shortener)

    for case in edgelist.iterrows():
        id_a = case[1][0]
        id_b = case[1][1]
        net_id_a = seq_to_nodeID[id_a]  # get the bin_id and then get its corresponding id on the net
        net_id_b = seq_to_nodeID[id_b]
        score = case[1][2]
        # NOTE: In this case, we do not care about the source and the target since it is actually undirectional
        edge = {"@id": edge_counter, "s": net_id_a, "t": net_id_b, "i": "cooccurrence/depletion"}
        edges["edges"].append(edge)

        edgeAttributes["edgeAttributes"].append({"po": edge_counter, "n": "microbetag::weight", "v": str(score), "d": "double"})
        if score > 0:
            edgeAttributes["edgeAttributes"].extend([
                {"po": edge_counter, "n": "shared name", "v": " ".join([id_a, "(cooccurss with)", id_b]), "d": "string"},
                {"po": edge_counter, "n": "interaction type", "v": "cooccurrence", "d": "string"}
            ])
        else:
            edgeAttributes["edgeAttributes"].extend([
                {"po": edge_counter, "n": "shared name", "v": " ".join([id_a, "(depletes)", id_b]), "d": "string"},
                {"po": edge_counter, "n": "interaction type", "v": "depletion", "d": "string"}
            ])

        edge_counter += 1

        """
        Edge for A -> B
        NOTE: we want as source of the edge the DONOR taxo -- since it is the one providing to the BENEFICIARY (target)
        """
        check1 = False
        if conf.pathway_complementarity:
            # Potential pathway compl edge
            pot_edge = {"@id": (edge_counter), "t": net_id_a, "s": net_id_b, "i": "comp_coop"}
            # Path complements A -> B
            check1 = add_edge_pathway_complements(id_a, id_b, complements_dict_ext, edges, edgeAttributes, pot_edge, edge_counter)

        check2 = False
        if conf.seed_complementarity:

            # Seed complements A -> B
            check2 = add_edge_seed_complements(
                id_a, id_b, seed_complements_dict,
                edges, edgeAttributes, pot_edge, edge_counter, kmap, non_seed_sets, shortener
            )

            # Seed scores A -> B
            add_seed_edge_attributes(id_a, id_b, seed_scores, edgeAttributes, edge_counter)

        if check1 or check2:
            edge_counter += 1

        """
        Edge for B -> A
        """
        if conf.pathway_complementarity:
            pot_edge = {"@id": (edge_counter), "t": net_id_b, "s": net_id_a, "i": "comp_coop"}

        # Path complements B -> A
        check1 = False
        if conf.pathway_complementarity:
            check1 = add_edge_pathway_complements(id_b, id_a, complements_dict_ext, edges, edgeAttributes, pot_edge, edge_counter)

        check2 = False
        if conf.seed_complementarity:

            # Seed complements B -> A
            check2 = add_edge_seed_complements(id_b, id_a, seed_complements_dict, edges, edgeAttributes, pot_edge, edge_counter, kmap, non_seed_sets, shortener)

            # Seed scores B -> A
            add_seed_edge_attributes(id_b, id_a, seed_scores, edgeAttributes, edge_counter)

        if check1 or check2:
            edge_counter += 1

    return edges, edgeAttributes


def seqId_faprotax_functions_assignment(path_to_subtables):
    """
    Parse the sub tables of the faprotax analysis
    to assign the biological processes related to each sequence id
    """
    seqId_faprotax_assignments = {}
    for subtable_file in os.listdir(path_to_subtables):
        f = os.path.join(path_to_subtables, subtable_file)
        process_name = subtable_file.split(".")[0].replace("_", " ")
        table_file = open(f, "r")
        table_file = table_file.readlines()
        for line in table_file[2:]:
            seqId = line.split("\t")[1]
            if seqId not in seqId_faprotax_assignments:
                seqId_faprotax_assignments[seqId] = [process_name]
            else:
                seqId_faprotax_assignments[seqId].append(process_name)
    return seqId_faprotax_assignments


def add_edge_pathway_complements(id_x, id_y, complements_dict_ext, edges, edgeAttributes, pot_edge, edge_counter):
    """
    id_x beneficiary
    id_y donor
    """
    check = False
    if id_x in complements_dict_ext and id_y in complements_dict_ext[id_x]:
        pathway_complements = complements_dict_ext[id_x][id_y]
        if not isinstance(pathway_complements, Dict):
            logging.info(f"Taxa {id_x} and {id_y} found to have not pathway complements")
            return check
        edges["edges"].append(pot_edge)
        edgeAttributes["edgeAttributes"].extend([
            {"po": edge_counter, "n": "shared name", "v": f"{id_x} (completes/competes with) {id_y}", "d": "string"},
            {"po": edge_counter, "n": "interaction type", "v": "completes/competes with", "d": "string"}
        ])
        attr = f"compl::{id_x}:{id_y}"
        merged_compl = ["^".join(gcompl) for gcompl in pathway_complements.values()]
        edgeAttributes["edgeAttributes"].append({"po": edge_counter, "n": attr, "v": merged_compl, "d": "list_of_string"})
        check = True
    return check


def add_edge_seed_complements(
    id_x, id_y, complements_dict, edges, edgeAttributes,
    pot_edge, edge_counter, kmap, non_seed_sets, shortener
    ):
    """
    Appends the seed complementarities between two taxa as attributes to their corresponding edge
    id_x:
    id_y:
    """
    check = False
    if id_x in complements_dict and id_y in complements_dict[id_x]:
        if pot_edge not in edges["edges"]:
            edges["edges"].append(pot_edge)
            edgeAttributes["edgeAttributes"].extend([
                {"po": edge_counter, "n": "shared name", "v": f"{id_x} (completes/competes with) {id_y}", "d": "string"},
                {"po": edge_counter, "n": "interaction type", "v": "completes/competes with", "d": "string"}
            ])

        complements = complements_dict[id_x][id_y]
        complements_map = kmap[kmap['modelseed'].isin(complements)]
        maps_in = list(kmap[kmap['modelseed'].isin(complements)]["map"].unique())

        beneficiarys_nonseed = non_seed_sets.loc[id_x].to_list()[0]
        beneficiarys_nonseeds_map = kmap[kmap['modelseed'].isin(beneficiarys_nonseed)]

        complements_verbose = []
        for kegg_map in maps_in:
            ksc = list(complements_map[complements_map["map"] == kegg_map]["kegg_compound"])
            msc = ";".join(set(complements_map[complements_map["map"] == kegg_map]["modelseed"]))
            ns = list(beneficiarys_nonseeds_map[beneficiarys_nonseeds_map["map"] == kegg_map]["kegg_compound"])
            surl = build_url_with_seed_complements(ksc, ns, kegg_map, shortener)
            des = kmap[kmap["map"] == kegg_map]["description"].unique().item()
            cat = kmap[kmap["map"] == kegg_map]["category"].unique().item()
            ksc = ";".join(set(ksc))
            complements_verbose.append([cat, des, msc, ksc, surl])

        attr = f"seedCompl::{id_x}:{id_y}"
        merged_compl = ["^".join(gcompl) for gcompl in complements_verbose]
        edgeAttributes["edgeAttributes"].append({"po": edge_counter, "n": attr, "v": merged_compl, "d": "list_of_string"})
        check = True
    return check


def add_seed_edge_attributes(id_x, id_y, seed_scores, edgeAttributes, edge_counter):
    matching_rows = seed_scores[(seed_scores['A'] == id_x) & (seed_scores['B'] == id_y)]
    if not matching_rows.empty:
        comp = matching_rows["Competition"].item()
        coop = matching_rows["Complementarity"].item()
        edgeAttributes["edgeAttributes"].extend([
            {"po": edge_counter, "n": "seed::competition", "v": str(comp), "d": "double"},
            {"po": edge_counter, "n": "seed::cooperation", "v": str(coop), "d": "double"}
        ])


class UpdateCX2Netork():
    """
    Convert the initial microbetag-annotated network to a .cx2 format file.
    """
    def __init__(self, microbetag_cx, outfile=None):
        """
        Initializes a cx2 microbetag-network converter.

        Attributes
        -----------
        microbetag_cx (list): microbetag-annotated network in initial format
        """

        self.graphml_file = None
        self.outfile = outfile

        if not isinstance(microbetag_cx, list):

            print("microbetag_cx:", microbetag_cx)

            try:
                with open(microbetag_cx, "r") as f:
                    self.initial_cx = json.load(f)

                # base, _ = os.path.splitext(os.path.basename(microbetag_cx))
                edir = os.path.dirname(microbetag_cx)
                self.graphml_file = edir

            except:
                raise ValueError("Please provide either a path to a initial cx file or the list returned when this is loaded")
        else:
            self.initial_cx = microbetag_cx

        try:
            # Build nodes
            self.cx2_nodes = self.get_nodes()
            # Build edges
            self.cx2_edges = self.get_edges()
        except:
            raise TypeError("File provided is not a valid json.")


    def get_nodes(self):
        """
        Builds cx2-like nodes based on the initial network

        Returns
        -------
        nodes (list): List with cx2-like nodes after the ndex2 library
        """
        nodes = []
        for nid in self.initial_cx[4]["nodes"]:
            node = {}
            node["id"] = nid["@id"]
            node["v"] = {}
            for attribute in self.initial_cx[5]["nodeAttributes"]:
                if attribute["po"] == node["id"]:
                    node["v"].update({attribute["n"]: attribute["v"]})
            try:
                node["v"]["name"] = node["v"]["display name"]
                node["v"].pop("display name")
            except:
                logging.info("No display name found for node %s" % node["id"])
                pass
            try:
                if len(node["v"]["microbetag::taxonomy"].split(";") ) == 7:
                    (node["v"]["taxonomy::domain"],
                    node["v"]["taxonomy::phylum"],
                    node["v"]["taxonomy::class"],
                    node["v"]["taxonomy::oder"],
                    node["v"]["taxonomy::family"],
                    node["v"]["taxonomy::genus"],
                    node["v"]["taxonomy::species"]) = node["v"]["microbetag::taxonomy"].split(";")
            except:
                logging.info("No taxonomy found for node %s" % node["id"])
                pass
            nodes.append(node)
        return nodes

    def get_edges(self):
        """
        Builds cx2-like edges based on the initial network

        Returns
        -------
        edges (list): List with cx2-like edges after the ndex2 library
        """
        edges = []
        for edgeid in self.initial_cx[6]["edges"]:
            edge = {}
            edge["id"] = edgeid["@id"]
            edge["s"] = edgeid["s"]
            edge["t"] = edgeid["t"]
            edge["v"] = {}
            edge["v"]["interaction type"] = edgeid["i"]
            for attribute in self.initial_cx[7]["edgeAttributes"]:
                if attribute["po"] == edge["id"]:
                    edge["v"].update({attribute["n"]:attribute["v"]})
            edges.append(edge)
        return edges


    def build_cx(self):
        """
        Writes a .cx2 network using the nodes and edges returned by the get_nodes() and get_edges() attributes
        """
        # Create an empty net cx
        net_cx = ndex2.cx2.CX2Network()

        # Add nodes on the net_cx
        mggId2netid = {}
        for node in self.cx2_nodes:
            node_attributes = node["v"]

            # Add node
            autoincr = net_cx.add_node(attributes=node_attributes)

            # Keep track of the ids on the inital mgg net
            mggId2netid[node["id"]] = autoincr

        # Add edges on the net_cx
        for edge in self.cx2_edges:

            source = mggId2netid[edge["s"]]
            target = mggId2netid[edge["t"]]
            attributes = edge["v"].copy()

            if attributes["interaction type"] in ["depletion", "cooccurrence"]:
                attributes['microbetag::weight'] = float(edge["v"]['microbetag::weight'])

            filtered_attributes = {key: value for key, value in attributes.items() if not (isinstance(value, list) and len(value) == 0)}

            # create an edge connecting the nodes, id of edge is returned
            _ = net_cx.add_edge(source=source, target=target, attributes=filtered_attributes)

        if self.outfile is None:
            # Basename
            timepoint = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
            netfile = "_".join(["mbtag_net", timepoint])
            netfile = ".".join([netfile, "cx2"])
            if self.graphml_file is not None:
                graphml_file = os.path.join(self.graphml_file, netfile)
            else:
                graphml_file = netfile
        else:
            graphml_file = self.outfile
        net_cx.set_network_attributes({'name': 'microbetag annotated network'})
        net_cx.write_as_raw_cx2(graphml_file)


def build_ndex2_net(microbetag_pseudo_cx, outfile=None):
    """
    Wrapper to fire an instance of UpdateCX2Netork class aiming to export a microbetag-annotated network file to .cx2 format

    Arguments
    ---------
    microbetag_net_file (str | list): path to initial microbetag-annotated network file

    Returns
    --------
    (boolean): A .cx2 format file was successfully saved or not
    """

    try:
        build_cx2 = UpdateCX2Netork(microbetag_pseudo_cx, outfile)
        build_cx2.build_cx()
        return True

    except Exception as e:
        logging.error('Error occurred when building cx2. %s' % str(e))
        return False

