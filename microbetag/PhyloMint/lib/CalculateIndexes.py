"""
Based on the PhyloMInt implementation

DOI: https://doi.org/10.1371/journal.pcbi.1007951 

GitHub: https://github.com/mgtools/PhyloMint
"""

def calculate_scores(SeedA, SeedSetAConfidence, SeedB, nonSeedB):

    # get intersects
    intersectAB = SeedA.intersection(SeedB)

    # store weighted sum
    normIntersect = 0.0

    # get weighted total
    sumA = sum(SeedSetAConfidence.values())

    # count intersect of confidence scores
    for seed in intersectAB:
        normIntersect += SeedSetAConfidence[seed]

    # Calculate normalized weighted sum
    MetabolicCompetitionIdx = normIntersect / sumA

    # Get the union set using the union (|) operator
    SetB = SeedB | nonSeedB

    # Get intersects intersect (A n nonB) &! B
    intersect_seedA_nonseedB = SeedA.intersection(nonSeedB)
    intersect_seedA_setB     = SeedA.intersection(SetB)

    # calculate normalized weighted sum
    MetabolicCooperationIdx = len(intersect_seedA_nonseedB) / len(intersect_seedA_setB)

    return round(MetabolicCooperationIdx, 2), round(MetabolicCompetitionIdx, 2)


def extract_complements(SeedA, nonSeedB):

    complementerarities = SeedA.intersection(nonSeedB)
    return complementerarities
