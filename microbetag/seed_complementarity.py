# System
import os
import json
import gzip
import pickle
import tarfile
from typing import TYPE_CHECKING, List, Dict, Tuple, Union

# Data
import pandas as pd

# Multiprocessing
from tqdm import tqdm
import multiprocessing

# microbetag features
from .utils import mtg_logger
from .PhyloMint.lib import BuildGraphNetX
from .PhyloMint.lib.CalculateIndexes import calculate_scores, extract_complements

if TYPE_CHECKING:
    from .config import Config

# Build logger
_logger_ = mtg_logger(__name__)


def _generate_fixed_pairwise_comparisons(fixed_item: str, patric_ids_of_interest: List):
    """Generate and return two lists: one with the fixed item in the first position and one with it in the second."""

    fixed_seedset_as_A    = set()
    fixed_nonseedset_as_A = set()

    # Generate pairs where fixed_item is in the first position
    for B in patric_ids_of_interest:
        fixed_seedset_as_A.add((fixed_item, B))

    # Generate pairs where fixed_item is in the second position
    for A in patric_ids_of_interest:
        fixed_nonseedset_as_A.add((A, fixed_item))

    return list(fixed_seedset_as_A), list(fixed_nonseedset_as_A)


class ExportSeedComplementarities:
    """
    Computes seed and non-seed sets and then exports complementarities.

    It saves corresponding sets to json files.

    Invokes edited version PhyloMInt modules as edited from microbetag team
    to support parallel calculation of the seed and non seed sets, and to consider reaction reversibility.

    Cite:
        Lam TJ, Stamboulian M, Han W, Ye Y. Model-based and phylogenetically adjusted quantification
        of metabolic interaction between microbial species. PLoS computational biology. 2020 Oct 30;16(10):e1007951.

    Note:
        Thanks to the `prev_conf` and the `prev_nonseeds` attributes of the :class:`Config` class,
        :class:`ExportSeedComplementarities` is able to use pre-calculated seed and non-seed sets.
        This is how the on-the-fly version of `microbetag` runs the seed complementarity step.
    """

    def __init__(self, config: "Config"):

        _logger_.info("Initiating Export Seed Complementarities class with params.")

        self.config = config

        self.api      = getattr(config, 'api', False)
        self.onthefly = getattr(config, 'onthefly', False)

        self.seed_compls_pckl = getattr(config, 'seed_compl_pckl', None)

        self.modules_ms_cpd = get_kegg_module_related(config.seed_ko_mo)

        self.module_related = True
        self.perce_save     = 10

        if not self.api:
            self.scores_outfile   = os.path.join(self.config.seeds_outdir, "phylomint_scores.tsv")

        if self.api or self.onthefly:

            self.get_complements  = getattr(config, 'get_complements', True)
            self.get_scores       = getattr(config, 'get_scores', True)

        else:

            self.user_models = getattr(config, 'user_models', False)
            self.namespace   = getattr(config, 'namespace', "modelseed")
            self.switch      = False if self.namespace == "modelseed" else True

            self.get_scores      = getattr(config, 'get_scores', not os.path.exists(self.scores_outfile))
            self.get_complements = getattr(config, 'get_complements', not os.path.exists(self.seed_compls_pckl))

            if getattr(config, 'genre_reconstruction_with', None) == "carveme":

                self.namespace = "BiGG"
                self.bigg2seed = bigg_to_seed_mapping_df(config.metanetx_compounds)
                self.switch    = getattr(config, 'switch_namespace', True)

            self.compound_prefix = "M"
            self.ex_suffix  = "e" if self.namespace == "BiGG" else "e0"
            self.int_suffix = "c" if self.namespace == "BiGG" else "c0"

        if self.config.skip_sets:

            _logger_.info(
                "Loading default configuration and non-seed sets for running on the fly."
                if self.onthefly or self.api
                else
                "Loading previously computed confidence scores and non-seed sets."
            )

            if self.onthefly or self.api:

                self.ConfidenceDic = load_confidence(self.config.prev_conf, remove_suffix=False)
                self.nonSeedSetDic = load_nonseeds(self.config.prev_nonseeds, remove_suffix=False)

            else:

                try:
                    with open(self.config.prev_conf, "r") as f:
                        raw_conf = json.load(f)
                    with open(self.config.prev_nonseeds, "r") as f:
                        raw_nonseeds = json.load(f)
                except FileExistsError as e:
                    raise e

                self.ConfidenceDic = {k: self._strip_pre_suff_from_dict(v) for k, v in raw_conf.items()}
                self.nonSeedSetDic = {k: self._strip_pre_suff_from_list(v) for k, v in raw_nonseeds.items()}

    def get_sets(self):
        """
        Get seed and non-seed sets for each model
        """
        # Build initial dictionaries
        SeedSetDic    = dict()
        nonSeedSetDic = dict()
        ConfidenceDic = dict()

        # Get all XML files in directory
        _logger_.info("Export seed and non seed sets.")

        sbml_files = [
            os.path.join(self.config.genres, f)
            for f in os.listdir(self.config.genres)
            if f.endswith(".xml")
        ]

        num_threads = min(len(sbml_files), self.config.threads)

        with multiprocessing.Pool(processes=num_threads) as pool:
            with tqdm(
                total=len(sbml_files),
                desc="Processing SBML files to calculate seed and non-seed sets.",
            ) as pbar:

                results = []

                # NOTE (Haris Zafeiropoulos, 2025-05-18): Apply the process_sbml() in parallel
                for result in pool.imap_unordered(self.process_sbml, sbml_files):
                    results.append(result)
                    pbar.update(1)  # Update progress bar as soon as a task completes

        # Unpack the results
        for result in results:
            try:
                sbml_base, SeedSet, nonSeedSet, SeedSetConfidence = result
            except Exception:
                pass

            tmp = {key: None for key in SeedSet}

            SeedSetDic[sbml_base]    = tmp.keys()
            nonSeedSetDic[sbml_base] = nonSeedSet
            ConfidenceDic[sbml_base] = SeedSetConfidence

        pool.close()
        pool.join()

        self.SeedSetDic, self.nonSeedSetDic, self.ConfidenceDic = (
            SeedSetDic,
            nonSeedSetDic,
            ConfidenceDic,
        )

        # ---------------
        # NOTE (Haris Zafeiropoulos, 2025-05-18):
        # Not sure if the save_dics would not be needed under any circumstances

        # if self.save_dics:

        SeedSetDic_serial = self._serialize_dic(
            SeedSetDic, os.path.join(self.config.seeds_outdir, "SeedSetDic.json")
        )
        nonSeedSetDic_serial = self._serialize_dic(
            nonSeedSetDic, os.path.join(self.config.seeds_outdir, "nonSeedSetDic.json")
        )

        with open(os.path.join(self.config.seeds_outdir, "confidenceDic.json"), "w") as out_file:
            json.dump(ConfidenceDic, out_file)

        # ---------------

        # NOTE (Haris Zafeiropoulos, 2025-03-26):
        # In the pickle conversion we keep only the KEGG MODULE related - does not make sense to have that with BiGG
        if not self.switch:
            self._dict_to_pickle(SeedSetDic_serial, self.config.module_seeds)
            self._dict_to_pickle(nonSeedSetDic_serial, self.config.module_nonseeds)

        _logger_.info("Seed and non seed sets have been exported.")

    def get_scores_and_compls(self) -> Union[Tuple[pd.DataFrame, dict], None]:
        """
        Based on the seed and non-seed sets calculated, get all pairwise competition 
        and cooperation scores, and the seed complementarities between the models under study.

        Returns the a dictionary in case of the API or builds the the seed_complements.pckl file in the stand-alone.
        """

        _logger_.info("Exporting seed scores and complementarities.")

        if self.api:
            self.patric_ids_of_interest = [str(q) for q in list(self.config.patric_ids)]

        elif self.onthefly:
            self.patric_ids_of_interest = [str(q) for q in list(self.config.gc_to_patric_ids.values())]

        else:
            self.patric_ids_of_interest = self.ConfidenceDic.keys()

        seed_scores, seed_complements = [], {}

        for species in self.patric_ids_of_interest:

            if self.api:

                scores, compls = self.species_scores_compls(species)
                seed_scores.append(scores)

            else:
                # Score are written in a file
                compls = self.species_scores_compls(species)

            seed_complements[species] = compls

        seed_scores = [s for s in seed_scores if s is not None]

        # Finalize shared dictionary and convert to DataFrame
        compls_dict = {
            k: v
            for k, v in (seed_complements or {}).items()
            if isinstance(v, dict)
        }

        # Save the final DataFrame
        if self.api:

            try:

                scores = [list(entry)[0].strip().split("\t") for entry in seed_scores]

                scores_df = pd.DataFrame(
                    scores,
                    columns=[
                        "PATRIC_A",
                        "PATRIC_B",
                        "CompetitionScore",
                        "CooperationScore",
                    ],
                )

            except Exception:

                _logger_.warning("No seed scores found.")
                scores_df = None

            return scores_df, compls_dict

        else:

            df = pd.DataFrame.from_dict(compls_dict)

            # Identify only the float columns
            float_cols = df.select_dtypes(include="float").columns

            # Replace NaNs with [] only in those columns
            df[float_cols] = df[float_cols].where(df[float_cols].notna(), [[]])

            # NOTE (Haris Zafeiropoulos, 2025-06-02): Attention! We need to get df.T.
            # Otherwise we get the source as target and the other way around !
            with open(self.seed_compls_pckl, "wb") as f:
                pickle.dump(df.T, f)

    def species_scores_compls(self, species: str) -> Union[Tuple[set, dict], Dict]:
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
        species_conf = self.ConfidenceDic.get(species)

        if species_conf is None:
            return None, None

        # Get pairwise
        as_beneficiary, _ = _generate_fixed_pairwise_comparisons(
            species, list(self.patric_ids_of_interest)
        )

        # Get seed set of the other species
        for partner in [pair[1] for pair in as_beneficiary if pair[1] != species]:

            if (conf := self.ConfidenceDic.get(partner)) is not None and (
                non_seed := self.nonSeedSetDic.get(partner)
            ) is not None:

                partner_seedset_confidence, nonSeedB = conf, non_seed

            else:
                continue

            SeedA, SeedB, nonSeedB = (
                set(species_conf.keys()),
                set(partner_seedset_confidence.keys()),
                set(nonSeedB),
            )

            # NOTE (Haris Zafeiropoulos, 2025-04-29):
            # In all cases, in the API and the onthefly version, both scores and complements are computed

            if self.get_scores or self.api:

                mi_coop, mi_comp = calculate_scores(
                    SeedA, species_conf, SeedB, nonSeedB
                )

                scores.add(
                    f"{species}\t{partner}\t{mi_comp}\t{mi_coop}\n"
                )

            if self.get_complements or self.api:

                B_complements_A = extract_complements(SeedA, nonSeedB)

                if self.module_related:
                    B_complements_A = kegg_module_related_intersect(
                        B_complements_A, self.modules_ms_cpd
                    )

                compls[partner] = B_complements_A

        if self.api:

            return scores, compls

        else:
            with open(self.scores_outfile, "a") as f:
                f.writelines(scores)

            return compls

    def process_sbml(self, sbml_path: str, maxcc: int = 2):
        """
        For each SBML model file (.xml) extract seeds, non-seeds and confidence scores
        using the PhyloMint adapted/refined approach of ours, i.e. building a directed graph
        with only the cytosol reactions, considering for the reversibility of a reaction.
        """
        filename  = os.path.basename(sbml_path)
        sbml_base = filename.rstrip(".xml")

        # calculate SeedSets
        try:
            DG_sbml = BuildGraphNetX.buildDG(sbml_path)
        except Exception as e:
            _logger_.error("Failed to run build directional graph for:", sbml_path)
            return e

        # Get sets !
        # SeedSet: a dict_keys  |  nonSeedSet: a list already  |  SeedSetConfidence: a dict
        SeedSetConfidence, SeedSet, nonSeedSet = BuildGraphNetX.getSeedSet(
            DG_sbml, maxComponentSize=maxcc
        )

        # Remove any prefixes-suffixes
        SeedSetConfidence, SeedSet, nonSeedSet = (
            self._strip_pre_suff_from_dict(SeedSetConfidence),
            self._strip_pre_suff_from_list(SeedSet),
            self._strip_pre_suff_from_list(nonSeedSet),
        )

        # If carveme, map compounds to modelseed
        if self.namespace == "BiGG":

            seedSetBigg           = SeedSet.copy()
            nonSeedSetBigg        = nonSeedSet.copy()
            SeedSetConfidenceBigg = SeedSetConfidence.copy()

            if self.switch:

                SeedSet           = _bigg_to_modelseed(seedSetBigg, self.bigg2seed)
                nonSeedSet        = _bigg_to_modelseed(nonSeedSetBigg, self.bigg2seed)
                SeedSetConfidence = _bigg_to_modelseed(
                    SeedSetConfidenceBigg, self.bigg2seed
                )

        return sbml_base, list(SeedSet), nonSeedSet, SeedSetConfidence

    def _strip_pre_suff_from_list(self, terms):
        return [
            term.split("_", 1)[-1] if term.startswith(self.compound_prefix) else term
            for term in (
                (
                    t.rsplit("_", 1)[0]
                    if t.split("_")[-1] in {self.ex_suffix, self.int_suffix}
                    else t
                )
                for t in terms
            )
        ]

    # TODO (Haris Zafeiropoulos, 2025-03-28): check if this could be a static
    def _strip_pre_suff_from_dict(self, d):
        d_tmp = {}
        for k, v in d.items():
            new_k = self._strip_pre_suff_from_list([k])[0]
            d_tmp[new_k] = v
        return d_tmp

    # TODO (Haris Zafeiropoulos, 2025-03-28): like above
    def _serialize_dic(self, dict, json_file):

        dict_serial = {k: list(v) for k, v in dict.items()}
        with open(json_file, "w") as out_file:
            json.dump(dict_serial, out_file)
        return dict_serial

    def _dict_to_pickle(self, dict, pickle_file):
        """
        Saves a dictionary as a pickle file after filtering for KEGG MODULE related cases.
        """
        dict_tmp = {}
        for k, v in dict.items():
            dict_tmp[k] = [
                kegg_module_related_intersect(v, self.modules_ms_cpd)
            ]
        df = pd.DataFrame.from_dict(dict_tmp)
        with open(pickle_file, "wb") as f:
            pickle.dump(df.T, f)

    def _worker_function(self, lock, species, queue, shared_dict):
        """Wrapper function to process a species and signal completion."""
        self.species_scores_compls(species, lock, shared_dict)
        with lock:
            queue.put(1)  # Signal that one task is completed


def kegg_module_related_intersect(intersect, modules_ms_cpd):
    """Check if KEGG MODULE related"""
    intersect = list(intersect)
    tmp_intersect = intersect.copy()
    for compl in tmp_intersect:
        if compl not in modules_ms_cpd:
            intersect.remove(compl)
    return intersect


def get_kegg_module_related(seed_ko_mo):
    """Load map file with KEGG modules and their terms and return a set with all the KOs there"""
    modules_compounds = pd.read_csv(seed_ko_mo, sep="\t")
    modules_compounds.columns = ["modelseed", "kegg", "module"]
    return set(modules_compounds["modelseed"].unique().tolist())


def _bigg_to_modelseed(bigg_obj, bigg2seed):
    """
    bigg2seed (pd.DataFrame)
    """
    if isinstance(bigg_obj, list):
        modelseed_seed_list = []
        for seed_BiggId in bigg_obj:
            if seed_BiggId not in bigg2seed:
                # seed_BiggId not found, this should be almost impossible..
                continue
            else:
                # NOTE (Haris Zafeiropoulos, 2025-03-24):
                # The bigg2seed dictionary has lists for values; if more than 1 modelseed compounds hit to the same BiGG
                # we keep the one with the lowest cpd since it's probably more involved to key processes
                mapped_ids = bigg2seed[seed_BiggId]
                mapped_ids = [x for x in mapped_ids if not isinstance(x, float)]
                if len(mapped_ids) > 0:
                    modelseed_ids = sorted(mapped_ids)
                    modelseed_seed_list.append(modelseed_ids[0])
                else:
                    # seed_BiggId not found
                    modelseed_seed_list.append(seed_BiggId)
        return modelseed_seed_list

    elif isinstance(bigg_obj, dict):
        modelseed_seed_dict = {}
        for seed_BiggId, value in bigg_obj.items():
            if seed_BiggId not in bigg2seed:
                # logging.warning("not found in dictionary case: %s", seed_BiggId)
                continue
            else:
                mapped_ids = bigg2seed[seed_BiggId]
                mapped_ids = [x for x in mapped_ids if not isinstance(x, float)]
                if len(mapped_ids) > 0:
                    modelseed_ids = sorted(mapped_ids)
                    modelseed_seed_dict[modelseed_ids[0]] = value
                else:
                    # seed_BiggId not found in dictionary case
                    modelseed_seed_dict[seed_BiggId] = value
        return modelseed_seed_dict


def progress_tracker(queue, total):
    """Progress bar updater."""
    with tqdm(
        total=total,
        desc="Calculate cooperation and competition scores as well as complementarities.",
    ) as pbar:
        for _ in range(total):
            queue.get()  # Wait for a task to finish
            pbar.update(1)


def generate_fixed_pairwise_comparisons(fixed_item, reconstruction_filenames):
    """Generate and return two lists: one with the fixed item in the first position and one with it in the second."""

    fixed_seedset_as_A = set()
    fixed_nonseedset_as_A = set()

    # Generate pairs where fixed_item is in the first position
    for B in reconstruction_filenames:
        fixed_seedset_as_A.add((fixed_item, B))

    # Generate pairs where fixed_item is in the second position
    for A in reconstruction_filenames:
        fixed_nonseedset_as_A.add((A, fixed_item))

    return list(fixed_seedset_as_A), list(fixed_nonseedset_as_A)


def bigg_to_seed_mapping_df(metanetx_compounds):

    # Open the tar.gz file
    with tarfile.open(metanetx_compounds, "r:gz") as tar:

        # List files in the archive to identify the one you want to read
        file_names = tar.getnames()  # Returns a list of files in the tar.gz

        # Extract the file of interest as a file-like object
        file_to_read = tar.extractfile(file_names[0])

        if file_to_read:
            metanetx = pd.read_csv(
                file_to_read, delimiter="\t", skiprows=353, header=None
            )  # Adjust delimiter as needed

    metanetx.columns = ["source", "id", "description"]

    metanetx[["source_namespace", "source_id"]] = metanetx["source"].str.split(
        pat=":", n=1, expand=True
    )
    metanetx.drop(columns=["source"], inplace=True)
    metanetx = metanetx[
        metanetx["source_namespace"].isin(["bigg.metabolite", "seed.compound"])
    ]

    metanetx_bigg_metabolite = metanetx[
        metanetx["source_namespace"] == "bigg.metabolite"
    ]
    metanetx_seed_compound = metanetx[metanetx["source_namespace"] == "seed.compound"]

    merged_df = pd.merge(
        metanetx_bigg_metabolite, metanetx_seed_compound, on="id", how="left"
    )
    bigg2seed = merged_df.groupby("source_id_x")["source_id_y"].apply(list).to_dict()

    return bigg2seed


# ---- Utils not related to the extaction but to the assignment of the complements or scores to the net


def load_seed_complement_files(path_to_kegg_seed_mappings):
    """
    Loads mapping files to be used for the building of the cx2 network.

    """
    kmap = pd.read_csv(
        os.path.join(path_to_kegg_seed_mappings, "seedId_keggId_module.tsv"),
        sep="\t",
        header=None,
    )
    kmap.columns = ["modelseed", "kegg_compound", "kegg_module"]

    module_to_map = pd.read_csv(
        os.path.join(path_to_kegg_seed_mappings, "module_map_pairs.tsv"),
        sep="\t",
        header=None,
    )
    module_to_map.columns = ["module", "map"]
    module_to_map["module"] = module_to_map["module"].str.replace("md:", "")
    module_to_map["map"] = module_to_map["map"].str.strip()

    module_map_dict = module_to_map.set_index("module")["map"].to_dict()
    kmap["map"] = kmap["kegg_module"].map(module_map_dict)
    maps_cat_descrs = pd.read_csv(
        os.path.join(path_to_kegg_seed_mappings, "related_kegg_maps_descriptions.tsv"),
        sep="\t",
        header=None,
    )
    maps_cat_descrs.columns = ["map", "description", "category"]
    kmap = pd.merge(kmap, maps_cat_descrs, on="map", how="left")

    return kmap


def build_url_with_seed_complements(seed_complements, nonseeds, kmap, shortener=None):
    """ """
    base_url = "https://www.kegg.jp/kegg-bin/show_pathway?"
    url = "".join([base_url, kmap]) + "/"

    present_compounds_color = "%20skyblue%2Cblue/"
    complemet_compounds_color = "%09%23ff0000/"

    for compound in nonseeds:
        url += compound + present_compounds_color
    for compound in seed_complements:
        url += compound + complemet_compounds_color
    if shortener is not None:
        _logger_.info("Shortening the URL.")
        url = shortener.tinyurl.short(url)
    return url


def load_confidence(confidence, remove_suffix=False):
    """

    """
    # confidence: all_conf.json.gz
    with gzip.open(confidence, "rt", encoding="utf-8") as f:
        seeds = json.load(f)
    if remove_suffix:
        seeds = {k.split(".")[0]: v for k, v in seeds.items()}
    return seeds


def load_nonseeds(nonseeds, remove_suffix=False):
    # nonseeds: all_nonseeds.json.gz
    with gzip.open(nonseeds, "rt", encoding="utf-8") as f:
        nonseeds = json.load(f)
    if remove_suffix:
        nonseeds = {k.split(".")[0]: v for k, v in nonseeds.items()}
    return nonseeds
