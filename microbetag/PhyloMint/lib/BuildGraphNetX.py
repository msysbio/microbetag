#!/usr/bin/env python3
import networkx as nx
from libsbml import readSBML

# NOTE (2025-03-08):
# We remove any exchange reaction: 'thm_e <=> '

# NOTE (2025-03-07):
# 1. get reaction and product and construct directed graph ignoring the exchange reactions
# 2. for the reversible reactions, keep both directions as source and target


def buildDG(sbml: str) -> nx.DiGraph:
    """
    Usage: reads SBML file, parses reaction and product list

    Args:
        sbml: Patrh to SBML network file

    Returns:
        A `networkx` directed graph (:class:`networkx.DiGraph`)

    """
    # initate empty directed graph
    DG       = nx.DiGraph()
    document = readSBML(sbml)
    model    = document.getModel()

    for rxn in model.getListOfReactions():

        react_f = [i.getSpecies() for i in rxn.getListOfReactants()]
        prod_f  = [j.getSpecies() for j in rxn.getListOfProducts()]

        # NOTE (2025-03-08):
        # If any non cellular compound is being used in the reaction, skip the reaction
        # This will skip any exchange and periplasm-related reactions, but also reactions that use extracellular compounds in cytosol
        not_cytosol    = False
        all_react_mets = react_f + prod_f

        for met in all_react_mets:
            if met.rsplit("_", 1)[-1] not in ["c", "c0"]:
                # print("Skip reaction:", rxn)
                not_cytosol = True

        if not_cytosol:
            continue

        # Load directed edge on the DG graph
        for r in react_f:
            for p in prod_f:
                DG.add_edge(r, p)

        # NOTE (2025-03-07): In case of reversible reactions, we consider that too
        if rxn.reversible:
            react_r = prod_f
            prod_r  = react_f
            for r in react_r:
                for p in prod_r:
                    DG.add_edge(r, p)
    return DG


# carveme:     dg = buildDG(modelfile)
# modelseedpy: mgt_dg  = buildDG(mgt_modelfile)


def getSeedSet(DG, maxComponentSize=5):
    """
    Usage: takes input networkX directed graph
    Returns: SeedSet dictionary{seedset:confidence score}
    Implementation follows literature description,
    Improves upon NetCooperate module implementation which erroneously discards certian cases of SCCs (where a smaller potential SCC lies within a larger SCC)
    """
    # get SCC
    SCC = nx.strongly_connected_components(DG)
    SeedSetConfidence = dict()
    for cc in SCC:

        # convert set to list
        cc_temp = list(cc)

        # filter out CC larger than threshold
        if len(cc_temp) > maxComponentSize:
            continue

        # check single element SCC
        elif len(cc_temp) == 1:
            if DG.in_degree(cc_temp[0]) == 0:
                SeedSetConfidence[cc_temp[0]] = 1.0

        # check 2 to max threshold SCC
        else:

            # Check if no out nodes
            for node in cc_temp:

                # Check every edge of SCC
                for edge in DG.in_edges(node):

                    # if SCC is not self contained, then it is not considered seed set
                    if edge[0] not in cc_temp:
                        cc_temp = []

            for node in cc_temp:
                SeedSetConfidence[node] = 1 / len(cc_temp)

    SeedSet = set(SeedSetConfidence.keys())
    nonSeedSet = list(set(DG.nodes()) - set(SeedSet))
    return (SeedSetConfidence, SeedSet, nonSeedSet)


#  carveme:      ssc, ss, nss = getSeedSet(dg)
#  modelseedpy:  patric_ssc, patric_ss, patric_nss = getSeedSet(mgt_dg)
