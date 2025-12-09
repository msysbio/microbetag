"""
Aim:
    Establishing connection and query on microbetagDB.
    Useful for the API and the on-the-fly version of microbetag, more specifically for the 
    phenotrex-based phenotypic traits and the pathway complementarity steps. 

Notes:
    Needs a hidden file called .env_dev.json with the database credentials.
"""

import os
import json
import pickle
import random
import pandas as pd
import mysql.connector
from mysql.connector import pooling
from typing import Dict, Set, Tuple, TYPE_CHECKING
from collections import defaultdict

from .utils import mtg_logger, convert_to_json_serializable
if TYPE_CHECKING:
    from microbetag.config import Config

_logger_ = mtg_logger(__file__)
_KEGG_MAPPINGS_ = os.path.join(
    os.path.dirname(__file__), "mtg_maps_models", "kegg_mappings"
)

DB_CREDENTIALS = {}


# -----------
# Database
# -----------


def execute(phrase: str) -> list[tuple]:
    """
    Establish a database connection and perform an action
    """
    cnx    = mysql.connector.connect(**DB_CREDENTIALS)
    cursor = cnx.cursor()

    cursor.execute(phrase)

    rows = cursor.fetchall()

    cursor.close()
    cnx.commit()
    cnx.close()

    return rows


def execute_in_a_pool(cursor: mysql.connector, query: str):
    """
    Executes a query using a connection from the connection pool.
    """
    try:
        cursor.execute(query)
        result = [row for row in cursor]
        return result
    except mysql.connector.Error as err:
        print("Something went wrong: {}".format(err))
        print(query)


def init_connection_pool() -> mysql.connector.pooling.MySQLConnectionPool:
    """
    Initiates a connection pool.
    A pool opens a number of connections and handles thread safety when providing connections to requesters.
    For more see: https://dev.mysql.com/doc/connector-python/en/connector-python-connection-pooling.html
    """
    connection_pool = pooling.MySQLConnectionPool(  # noqa: E203
        pool_name = "microbetagDB_pool",
        pool_size = 5,
        user      = DB_CREDENTIALS["user"],
        password  = DB_CREDENTIALS["password"],
        host      = DB_CREDENTIALS["host"],
        database  = DB_CREDENTIALS["database"],
    )
    return connection_pool


# --------
# Mapping
# --------
def gc_unify(gc_list):
    """
    Removes duplicates of a genome that has entries both as GCA and GCF in the db.
    """
    return list(set([x.replace("GCA", "GCF") for x in gc_list]))


def alt_genome_prefix(gc):
    """
    Switches GCA prefic of a genome accession id to GCF and vice-versa.
    """
    if gc.startswith("GCA_"):
        gc_alt = gc.replace("GCA_", "GCF_")
    elif gc.startswith("GCF_"):
        gc_alt = gc.replace("GCF_", "GCA_")
    else:
        return 0
    return gc_alt


def get_genomes_for_ncbi_tax_id(ncbi_tax_id: int):
    """
    Get the genome IDs corresponding to a given NCBI Taxonomy ID from the microbetagDB.

    Example: 1281578
    """

    query = f"""
        SELECT genomeId
        FROM genome2taxNcbiId
        WHERE ncbiTaxId = {ncbi_tax_id};
    """.strip()

    genome_ids = execute(query)

    return {ncbi_tax_id: gc_unify([x[0] for x in genome_ids])}


def get_ncbi_tax_id_for_genome(gc_id: str):
    # "GCA_018819265.1"

    query = f"""
        SELECT ncbiTaxId
        FROM genome2taxNcbiId
        WHERE genomeId = '{gc_id}';
    """.strip()

    ncbi_tax_ids = execute(query)

    return {gc_id: list(ncbi_tax_ids)}


def patric_from_gc_list(gc_accession_list: list):
    """
    Gets a list of GC accession ids and returns a dictionary where the GC ids are the keys
    and their corresponding PATRIC ids are the values.

    ["GCA_003184265.1"]
    """
    gc_to_patric_dict = {}
    for gc in gc_accession_list:

        gc_alt = alt_genome_prefix(gc)

        if gc_alt != 0:

            query = f"""
                SELECT patricId
                FROM patricId2genomeId
                WHERE gtdbGenomeAccession = '{gc}'
                OR gtdbGenomeAccession = '{gc_alt}';
            """.strip()

            patricId = execute(query)

            # NOTE (Haris Zafeiropoulos, 2025-05-08): Some PATRIC ids have a different suffix in the metadata file
            # than in their corresponding assembies used for the seed complementarity step.
            # Yet, keeping the part before the dot (.) - using int(patricId[0][0]) cannot be a solution since in
            # many cases we have several strains for the same species, meaning, several after the dot parts.
            gc_to_patric_dict[gc] = patricId[0][0] if patricId and patricId[0] else None

    return gc_to_patric_dict


def update_for_patric(module_nonseeds_pkl, gc_to_patric):
    """
    Arguments:
        module_nonseeds_pkl: path to nonseeds KEGG MODULE related pickle file
        gc_to_patric       : a dictionary with GTDB representative genomes as key
                        and their corresponding PATRIC id as value.
    """

    with open(module_nonseeds_pkl, "rb") as f:
        nonseeds = pickle.load(f)

    # Group patric IDs by prefix (before dot)
    pre_to_compl = defaultdict(list)
    for patric_id in nonseeds.index:
        prefix = patric_id.split(".")[0]
        pre_to_compl[prefix].append(patric_id)

    updated_gc_to_patric = {}

    for gtdb, patric in gc_to_patric.items():
        patric = str(patric)
        if patric in nonseeds.index:
            updated_gc_to_patric[gtdb] = patric
        else:
            trunc_patric = patric.split(".")[0]
            candidates = pre_to_compl.get(trunc_patric, [])
            if len(candidates) >= 5:
                continue  # Optional: skip if too many candidates?
            if candidates:
                updated_gc_to_patric[gtdb] = random.choice(candidates)
            else:
                # Optional: log or handle the case where no candidates are found
                continue

    return updated_gc_to_patric

# --------
# Phen related
# --------

class GetPhenotrexTraits:

    def __init__(self, config=None):

        if config is not None:
            self.config = config

    def get_phen_traits(self):
        """
        Returns predictions for a list of genomes

        repr_genomes_present, config.phen_traits_dir
        """
        # Get predictions for each trait, for all genomes matched to the taxonomies given from the user.
        traits_per_genome = {
            genome: self.get_phendb_traits(genome)
            for genome in self.config.repr_genomes_present
        }

        # Build a df from the predictions dictionary
        df = pd.DataFrame(traits_per_genome)

        # Drop 'gtdbId' only if it exists in the index to avoid errors
        df = df.drop("gtdbId", errors="ignore")  # drop to make it safe if "gtdbId" isn't present.

        # Export predictions per trait to a 3-col file.
        GetPhenotrexTraits.to_csv(df, self.config.phen_traits_dir)

    def get_phendb_traits(self, gtdb_genome_id: str):
        """
        Get phenotypical traits based on phenDB classes based on its GTDB representative genome
        "GCA_018819265.1"
        """
        gtdb_id = gtdb_genome_id.strip()

        rows = execute(GetPhenotrexTraits.phen_query(gtdb_id))

        if len(rows) == 0:
            alt_gtdb_id = alt_genome_prefix(gtdb_genome_id)
            rows        = execute(GetPhenotrexTraits.phen_query(alt_gtdb_id))

        if len(rows) == 0:
            # _logger_.info(f"Genome {gtdb_genome_id} is not available in microbetagDB.")
            return 0

        query          = "SHOW COLUMNS FROM phenDB;"
        colnames       = [list(x)[0] for x in execute(query)]
        genomes_traits = {i: j for i, j in zip(colnames, rows[0])}

        return genomes_traits  # gtdb_genome_id

    @staticmethod
    def phen_query(gtdb_id):
        """ Builds query for microbetagDB """

        query = f"""
            SELECT * FROM phenDB
            WHERE SUBSTRING_INDEX(gtdbId, '.', 1) = SUBSTRING_INDEX('{gtdb_id}', '.', 1);
        """.strip()

        return query

    @staticmethod
    def to_csv(df, outdir=None):
        """
        Saves phenotypic trait predictions of a trait for a set of genomes in a file, in a 3-column format.
        Identifier, Trait present, Confidence
        The values the 'Trait present' column may get, is 'YES, 'NO', and 'N/A'.
        """
        if outdir is None:
            outdir = os.getcwd()

        # Loop through traits (every 2 rows)
        for i in range(0, df.shape[0], 2):

            trait = df.index[i]

            presence, score = df.iloc[i], df.iloc[i + 1]

            output = pd.DataFrame({
                'Identifier'   : presence.index,
                'Trait present': presence.values,
                'Confidence'   : score.values
            })

            # Write to .tsv
            trait    = f"{trait}.prediction.tsv"

            with open(os.path.join(outdir, trait), "w") as f:

                f.write(f"# Trait: {trait}\n")

                f.write("Identifier\tTrait present\tConfidence\n")

                output.to_csv(f, sep="\t", index=False, header=False)


# --------
# Pathway complementarity
# --------

def get_path_compls_otf(config):
    """
    On the fly way to get pathway complementarities. Builds the pathCompls.json and
    the pathway_complements_extended.json files.

    The first file, in the stand-alone version lools like this:
    {"bin_101": {
        "bin_101": [],
        "bin_151": [["md:M00019", ["K00826"], ["K01652", "K01653", "K00053", "K01687", "K00826"],
                    "https://www.kegg.jp/kegg-bin/show_pathway?map00290/K00826%09%23EAD1DC/K01687%09%2300A898/"], ..]
        },..
    }
    where the elements regarding the complement and the alternative are actually lists, and not strings, while the latter:
    {"bin_101": {
        "bin_101": [],
        "bin_151": {"0": ["M00019", "Valine/isoleucine biosynthesis", "Branched-chain amino acid metabolism",
                            "K00826", "K01652;K01653;K00053;K01687;K00826", "https://...]
        }
    }

    To build those files for the on-the-fly version (otf), this function makes use of the config.otf_seq_tax_df
    attribute of the config, as returned by the taxonomy.py script.

    It creates a list of tuples with the NCBI Taxonomy Ids of found related taxa (in the edgelist)
    and using their corresponding GTDB representative genomes gets their complements.

    Arguments:
        config: Insance of the microbetat'g config class but as edited in the app.py script where the otf_seq_tax_df
                attribute is added

    Returns:
        mspecies_map_df: A pd.DataFrame with nodes names, NCBI Taxonomy ids and GTDB representative genomes for those
                        edges of the network that were both mapped to at least a GTDB genome.
    """

    # Ge the complements!
    compls = get_path_compls_for_ncbi_ids(config.relative_genomes, config.pairs_of_interest)

    # NOTE (Haris Zafeiropoulos, 2025-05-05):
    # Fix complements in the format set for the MGG
    # We will use the genome id here, even if the same file in the stand-alone has the sequence ids.
    compls_format = {}
    for _, j in compls.items():
        for k, v in j.items():
            ben_genome, don_genome = k
            if ben_genome not in compls_format:
                compls_format[ben_genome] = {}
            new_cases = []
            for case in v:                       # case is like [[...]]
                sub = case[0]
                formatted = [
                    sub[0],                      # module_id
                    sub[1].split(";"),           # essential_kos wrapped in list
                    sub[2].split(";"),           # all_kos wrapped in list
                    sub[3]                       # status
                ]
                new_cases.append(formatted)
            compls_format[ben_genome][don_genome] = new_cases

    # Serialize the formatted complements dictionary
    compls_serial = convert_to_json_serializable(compls_format)

    with open(config.pc_file, "w") as f:
        json.dump(compls_serial, f)


def get_path_compls_for_ncbi_ids(
    relative_genomes: Dict[str, Set[str]], pairs_of_interest: Set[Tuple[str, str]]
) -> dict:
    """

    Arguments:

        relative_genomes: A dictionary {"1260918": {"GCF_002102185.1"}, "1819566": {"GCF_009711525.1"}}

        pairs_of_interest={("1260918", "1819566")}
    """

    _logger_.info("===> Building queries for genome pairs...")

    complements_ids_queries = build_complement_queries(
        relative_genomes,
        pairs_of_interest
    )

    _logger_.info("===> Executing unique queries...")

    unique_queries = {
        q for genome_pairs in complements_ids_queries.values()
        for q in genome_pairs.values()
    }
    unique_queries2comples = get_complement_ids(unique_queries)

    _logger_.info("===> Mapping complement IDs to genome pairs...")

    pairs_to_compl_ids = map_queries_to_pairs(
        complements_ids_queries,
        unique_queries2comples
    )

    _logger_.info("===> Fetching full complement metadata...")

    all_compl_ids2coloured_compls = get_coloured_complements(pairs_to_compl_ids)

    _logger_.info("===> Assembling final result...")

    return build_pairs_complements(pairs_to_compl_ids, all_compl_ids2coloured_compls)


def query_for_getting_compl_ids(beneficiary="GCA_003184265.1", donor="GCA_000015645.1"):
    """
    Gets 2 gc accession ids and returns a query for their pathway complementarities
    """
    beneficiary_alt = alt_genome_prefix(beneficiary)
    donor_alt       = alt_genome_prefix(donor)

    return "".join(
        [
            'SELECT complmentId FROM pathwayComplementarity WHERE (beneficiaryGenome = "',
            str(beneficiary),
            '" or beneficiaryGenome = "',
            str(beneficiary_alt),
            '") AND (donorGenome = "',
            str(donor),
            '" OR donorGenome = "',
            str(donor_alt),
            '");',
        ]
    )


def build_complement_queries(relative_genomes, pairs_of_interest):

    complements_ids_queries = {}

    for ncbi_a, ncbi_b in pairs_of_interest:
        for genome_a in relative_genomes[ncbi_a]:
            for genome_b in relative_genomes[ncbi_b]:
                query = query_for_getting_compl_ids(genome_a, genome_b)
                complements_ids_queries.setdefault((ncbi_a, ncbi_b), {})[(genome_a, genome_b)] = query

    return complements_ids_queries


def get_complement_ids(unique_queries):

    cnx_pool      = init_connection_pool()
    my_connection = cnx_pool.get_connection()
    cursor        = my_connection.cursor()

    query_results = {}
    for query in unique_queries:
        result = execute_in_a_pool(cursor, query)
        if result:
            query_results[query] = result[0][0].split(",")
    return query_results


def map_queries_to_pairs(complements_ids_queries, unique_queries2comples):
    pairs_to_compl_ids = {}
    for ncbi_pair, genome_query_map in complements_ids_queries.items():
        for genome_pair, query in genome_query_map.items():
            if query in unique_queries2comples:
                pairs_to_compl_ids.setdefault(ncbi_pair, {})[genome_pair] = unique_queries2comples[query]
    return pairs_to_compl_ids


def get_coloured_complements(
    pairs_to_compl_ids: Dict[Tuple[str, str], dict[Tuple[str, str], list[str]]]
):
    """
    Gets thes actual complement using its unique complementId and builds its KEGG url.

    Arguments:
        pairs_to_compl_ids: {('1260918', '1819566'): {('GCA_002102185.1', 'GCA_009711525.1'): ['180131', ..']}}

    Returns:
        pairs_complements: []
    """
    unique_compl_ids = list({
        compl_id
        for genome_map in pairs_to_compl_ids.values()
        for compl_list in genome_map.values()
        for compl_id in compl_list
    })
    if not unique_compl_ids:
        return {}

    uqids = "','".join(unique_compl_ids)
    field_args = ",".join(f"'{id}'" for id in unique_compl_ids)

    _logger_.info("-----------------")
    _logger_.info(uqids)
    _logger_.info(field_args)
    _logger_.info("-----------------")

    query = f"""
        SELECT KoModuleId, complement, pathway
        FROM uniqueComplements
        WHERE complementId IN ('{uqids}')
        ORDER BY FIELD(complementId, {field_args});
    """.strip()

    _logger_.info(f"WQUER: {query}")

    cnx_pool                 = init_connection_pool()
    my_connection            = cnx_pool.get_connection()
    cursor                   = my_connection.cursor()

    query_result             = execute_in_a_pool(cursor, query)

    _logger_.info(f"QWUERY result: {query_result}")

    query_result_list        = [[r] for r in query_result]

    colored_complements_list = build_kegg_urls(query_result_list)

    return dict(zip(unique_compl_ids, colored_complements_list))


def build_pairs_complements(pairs_to_compl_ids, all_compl_ids2coloured_compls):
    pairs_complements = {}
    for ncbi_pair, genome_map in pairs_to_compl_ids.items():
        for genome_pair, compl_ids in genome_map.items():
            for compl_id in compl_ids:
                colored = all_compl_ids2coloured_compls.get(compl_id)
                if colored:
                    pairs_complements.setdefault(ncbi_pair, {}).setdefault(genome_pair, []).append(colored)
    return pairs_complements


def build_kegg_urls(genome_pair_compls):
    """
    Takes as input the complements list between two genomes and
    build urls to colorify the related to the module kegg map based on the KO terms of the beneficiary (pink)
    and those it gets from the donor (green).

    Notes:
        Some modules do not belong to any map, e.g. https://www.kegg.jp/module/M00705. In these cases, we will have a N/A value in the url.
    """

    # NOTE (Haris Zafeiropoulos, 2025-05-05):
    # The stand-alone version has a similar function on the pathway_complementarity.py, consider making a consensus one.

    # Constants
    color_map_base_url   = "https://www.kegg.jp/kegg-bin/show_pathway?"
    present_kos_color    = "%09%23EAD1DC/"
    complement_kos_color = "%09%2300A898/"

    # Load module-to-map mappings
    module_map_file = os.path.join(_KEGG_MAPPINGS_, "module_map_pairs.tsv")
    df              = pd.read_csv(module_map_file, sep="\t", header=None, names=["module", "map"])
    df["module"]    = df["module"].str.replace("md:", "", regex=False).str.strip()
    df["map"]       = df["map"].str.strip()

    #
    module_map = dict(zip(df["module"], df["map"]))
    updated_complements = []
    for [module_id, complement_str, ko_terms_str] in [list(c[0]) for c in genome_pair_compls]:
        beneficiary_kos    = []
        complement_kos     = []
        complement_kos_set = set(complement_str.split(";"))
        ko_terms           = ko_terms_str.split(";")

        #
        for ko in ko_terms:
            if ko in complement_kos_set:
                complement_kos.append(ko + complement_kos_color)
            else:
                beneficiary_kos.append(ko + present_kos_color)

        # Construct URL or fallback
        url    = "N/A"
        map_id = module_map.get(module_id)
        if map_id:
            url = f"{color_map_base_url}{map_id}/" + "".join(beneficiary_kos + complement_kos)

        # Append new colored URL to the record
        updated_complements.append([[module_id, complement_str, ko_terms_str, url]])

    return updated_complements
