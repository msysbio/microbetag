# microbetag : a software suite to annotate microbial co-occurrence networks

# Copyright (c) 2025 Haris Zafeiropoulos

# Licensed under GNU LGPL.3, see LICENCE file

"""
Utility functions to be used across the `microbetag` library.
"""

import os
import re
import sys
import csv
import ast
import json
import time
import copy
import glob
import shutil
import random
import logging
import colorlog
import numpy as np
import pandas as pd
import pkg_resources
from pathlib import Path
from multiprocessing import Pool, cpu_count
from typing import TYPE_CHECKING, Any, Dict, List, Tuple, Set, Union

if TYPE_CHECKING:
    from .config import Config


# Handling data related
def get_library_version(library_name: str) -> str:
    """
    Returns the version of a Python library
    """

    try:
        version = pkg_resources.get_distribution(library_name).version
        return version

    except pkg_resources.DistributionNotFound:
        return "Library not found"

    except Exception as e:
        return str(f"lala{e}")


def resolve_relative_path(base_dir: str, file_path: str) -> str:
    """
    Resolves a relative file path into an absolute file path based on a given base directory.

    This function processes a relative `file_path` (which may contain one or more `../` 
    segments) and resolves it into an absolute path by moving back the corresponding 
    number of directory levels from `base_dir`. It returns the resulting absolute file path.

    Parameters
    ----------
    base_dir : str
        The base directory from which to resolve the relative `file_path`. This should
        be an absolute path to a directory.

    file_path : str
        The relative file path to be resolved. It may contain `../` to navigate up the 
        directory hierarchy.

    Returns
    -------
    str
        The resolved absolute file path.

    Examples
    --------
    >>> resolve_relative_path("/home/user/docs", "../files/report.txt")
    '/home/user/files/report.txt'

    """

    return str(Path(base_dir).resolve().joinpath(file_path).resolve())


def resolve_file_path(base_dir: str, file_path: str) -> str:
    """
    Resolves a file path relative to a given base directory and returns the absolute file path.

    If the provided `file_path` is relative, it is resolved using the `base_dir`. The function
    handles absolute paths, user directory expansion (e.g., `~`), and relative paths (e.g., `../`).

    Parameters
    ----------
    base_dir : str
        The base directory to resolve relative paths from.

    file_path : str
        The file path to resolve. It can be absolute, relative, or use `~` for the home directory.

    Returns
    -------
    str
        The resolved absolute file path.

    Raises
    ------
    FileNotFoundError
        If the resolved file path does not exist.

    Examples
    --------
    >>> resolve_file_path("/home/user/docs", "~/file.txt")
    '/home/user/file.txt'
    """

    _logger_.info(f">> file_path: {file_path}")

    if file_path is None:
        return None  # Return None if the file path is None

    # Handle absolute paths and ~ expansion
    if file_path.startswith("/"):
        path = Path(file_path).resolve()

    elif file_path.startswith("~"):
        path = Path(os.path.expanduser(file_path)).resolve()

    elif file_path.startswith("../"):
        # Resolve relative path using the base_dir
        path = Path(resolve_relative_path(base_dir, file_path)).resolve()

    else:
        # Relative path with respect to base_dir
        path = (Path(base_dir) / file_path).resolve()

    # Check if the file exists
    if path.exists():
        return str(path)
    else:
        raise FileNotFoundError(f"File not found: {path}")


class SetEncoder(json.JSONEncoder):
    """
    Custom JSON encoder that handles serialization of Python sets.

    This encoder extends the functionality of the standard JSONEncoder to support
    serializing Python sets. JSON does not have a native representation for sets,
    so this encoder converts sets to lists before serializing them.

    Usage:
        When serializing data to JSON using json.dump() or json.dumps(), specify
        cls=SetEncoder to use this custom encoder.

    References:
        - json.JSONEncoder: https://docs.python.org/3/library/json.html#json.JSONEncoder
    """

    def default(self, obj):
        """
        Override the default method of JSONEncoder to handle serialization of sets.
        Notes:
            If the object is a set, it is converted to a list before serialization.
            Otherwise, the default behavior of JSONEncoder.default() is used.        Notes:
            If the object is a set, it is converted to a list before serialization.
            Otherwise, the default behavior of JSONEncoder.default() is used.
        """
        if isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)


def mtg_logger(filename: str) -> logging.getLogger:
    """
    Creates and returns a configured logger instance. This logger:

    - Logs messages to stdout with colored formatting using `colorlog`
    - Avoids adding duplicate handlers if called multiple times
    - Uses the given `filename` as the logger's name
    - Logs messages with level INFO and above

    Arguments:
        script: The filename of the script where the logger will be applied to.

    Returns:
        The logger instance.
    """
    logger = logging.getLogger(filename)
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        sh = logging.StreamHandler(sys.stdout)
        sh.setLevel(logging.INFO)
        formatter = colorlog.ColoredFormatter(
            "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            log_colors={
                "DEBUG": "cyan",
                "INFO": "blue",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "bold_red",
            },
        )
        sh.setFormatter(formatter)
        logger.addHandler(sh)
        logger.propagate = False  # Prevent duplicate logging
    return logger


def get_files_with_suffixes(directory: str, suffixes: List[str]) -> list[str]:
    """
    Recursively retrieves files from a specified directory and its subdirectories
    that have extensions matching a given list of suffixes.

    Arguments:
        directory: The root directory to start the search.
        suffixes: A list of file suffixes (extensions) to match.
                  Each suffix should include the dot (e.g., '.txt', '.csv').

    Returns:
    ---------
        A list of full paths to files that match any of the specified suffixes.

    Example:
    >>> get_files_with_suffixes('/path/to/directory', ['.txt', '.csv'])
    ['/path/to/directory/file1.txt', '/path/to/directory/subdir/file2.csv']
    """
    matching_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if any(file.endswith(suffix) for suffix in suffixes):
                matching_files.append(os.path.join(root, file))
    return matching_files


def safe_literal_eval(value: Any):
    """
    Safely evaluates a string that may represent a Python literal (e.g., list, dict, int).

    This function attempts to parse a string using :class:`ast.literal_eval`, which only evaluates
    Python literals (e.g., strings, numbers, tuples, lists, dicts, booleans, and None),
    avoiding the security risks of `eval()`*.
    If `value` is not a string or if evaluation fails,
    the original value is returned unchanged.

    Args
    ----------
    value : Any
        The input to be evaluated. If it's a string that looks like a literal (e.g., "[1, 2]"), 
        it will be parsed. Otherwise, it's returned as is.

    Returns
    ----------
        The evaluated literal if successful, or the original value if evaluation fails.

    Examples
    ----------
    >>> safe_literal_eval("[1, 2, 3]")
    [1, 2, 3]

    >>> safe_literal_eval("{'a': 1}")
    {'a': 1}

    Note:
        * Security risks of `eval`:
        https://www.adventuresinmachinelearning.com/safe-and-secure-eval-in-python-how-to-minimize-security-risks/
    """
    try:
        # Attempt to evaluate the value if it's a string that looks like a list
        return ast.literal_eval(value) if isinstance(value, str) else value
    except (ValueError, SyntaxError):
        # If it's not a valid list string, return the original value
        return value


def flatten(list_of_lists: List) -> List:
    """
    Recursively flattens a nested list into a single-level list.

    This function handles arbitrarily nested lists and returns a new list
    containing all the leaf elements in the original order.

    Arguments:
        lst : A list that may contain other nested lists.

    Returns:
    -------
        A flat list containing all non-list elements in the original order.

    Examples:
    --------
    >>> flatten([1, [2, [3, 4]], 5])
    [1, 2, 3, 4, 5]
    """
    if len(list_of_lists) == 0:
        return list_of_lists
    if isinstance(list_of_lists[0], list):
        return flatten(list_of_lists[0]) + flatten(list_of_lists[1:])
    return list_of_lists[:1] + flatten(list_of_lists[1:])


def flatten_list(lst: List, flat_list: List = None) -> set:
    """
    Recursively flattens a nested list and returns a set of unique elements.

    This function traverses all nested lists and collects elements into a set,
    removing any duplicates. The final result is unordered.

    Parameters:
    ----------
    lst: A list that may contain other nested lists.
    flat_list : Optional list. Used internally during recursion. Should not be set manually.

    Returns:
    -------
        A set containing all unique elements from the nested list.

    Examples:
    --------
    >>> flatten_list([1, [2, [2, 3]], 4, 1])
    {1, 2, 3, 4}
    """
    if flat_list is None:
        flat_list = []

    for i in lst:
        if isinstance(i, list):
            flatten_list(i, flat_list)
        else:
            flat_list.append(i)

    return set(flat_list)


def run_until_done(command: str):
    """
    Function to run recursively a command until
    """
    if os.system(command) == 0:
        return 1
    else:
        time.sleep(random.randint(2, 10))
        _logger_.warning("recurscive run of: %s", command)
        run_until_done(command)


def file_exists_and_nonzero(filename: str) -> bool:
    """
    Check if a file exists and its size is nonzero.

    Args:
        filename (str): The path to the file.

    Returns:
        bool: True if the file exists and its size is nonzero, False otherwise.
    """
    return os.path.exists(filename) and os.path.getsize(filename) > 0


def split_list(input_list: list, chunk_size: int) -> list:
    """
    Split a list to sublists of a user defined size (`chunk_size`).
    """
    return [
        input_list[i: i + chunk_size] for i in range(0, len(input_list), chunk_size)
    ]


def many_to_one_files(dir_with_files: str, merged_file: str) -> None:
    """
    Makes a single file out of all files in a directory by concatenating having rows of one after the other

    Arguments:
        dir_with_files: Path of the directory the files of which to be merged
        merged_file: Path to merged output file
    """
    command = " ".join(
        [
            "find",
            dir_with_files,
            "-type",
            "f",
            "-name",
            "K*",
            "-print0",
            "|",
            "xargs",
            "-0",
            "cat",
            ">",
            merged_file,
        ]
    )
    os.system(command)


def ko_list_parser(ko_list: str) -> Dict:
    """
    Parses ko_list file into a dict object - based on DiTing

    Arguments
    ----------
        ko_list: path to the `ko_list` file that comes from the kofam database https://www.genome.jp/ftp/db/kofam/

    Returns
    ---------
        A dictionary mapping knum to threshold and score_type
    """
    # { knum : [threshold, score_type] }
    ko_dic = {}
    with open(ko_list) as fi:
        # skip the first line (header)
        next(fi)
        for line in fi:
            knum, threshold, score_type = line.split("\t")[0:3]
            if threshold == "-":
                continue
            else:
                ko_dic[knum] = [threshold, score_type]
    return ko_dic


def merge_ko(hmmout_dir: str, output: str) -> None:
    """
    Parses the KO<>.<bin>.hmmout files produced by the kegg_annotation() function
    to create a single 3-column file (output) with the bin_id, the corresponding conting 
    and the KO that was mapped to it.
    The function then returns a dictionary with the bin ids as the keys and the set of KOs found to each as the value.

    Args:
        hmmout_dir: path to the .hmmout files
        output: Path/filename to save the output file
    """
    hmmout_dir = Path(hmmout_dir)
    output     = Path(output)

    # Under any circumstances microbetag will overwrite the ko_merged.txt file
    with open(output, "w") as fo:
        fo.write("bin_id\tcontig_id\tko_term\n")

    for bin_id in hmmout_dir.iterdir():
        if not bin_id.is_dir():
            continue

        bin_file = Path(bin_id) / f"{bin_id.name}_kos.tsv"
        if not bin_file.exists():
            continue

        # Append file contents
        with output.open("ab") as out_f, bin_file.open("rb") as in_f:
            # The copyfileobj() efficiently appends the contents of each KO file, to the merged file.
            shutil.copyfileobj(in_f, out_f)


def bin_kos_to_file(hmmout_dir: str, bin_id: str) -> None:
    """
    Builds a 3-col file for a bin and removes the KO-specific output files of `hmmsearch`

    Arguments:
        hmmout_dir: Directory to the hmmout files
        bin_id: Name of the sequence id under study
    """
    # Write 3-cols entries in tmp file
    bin_kos_file = os.path.join(hmmout_dir, "".join([bin_id, "_kos.tsv"]))
    if not os.path.exists(bin_kos_file):
        open(bin_kos_file, "w").close()

    for hmmout_file in os.listdir(hmmout_dir):
        try:
            basename, gene_id, k_number = parse_hmmout(hmmout_file, hmmout_dir)
            with open(bin_kos_file, "a") as fo:
                fo.write(basename + "\t" + gene_id + "\t" + k_number + "\n")
        except Exception:
            # Ignore non-informative lines
            pass

    # Remove .hmmout files
    bin_hmmout = os.path.join(hmmout_dir, ".".join([bin_id, "hmmout.all"]))
    many_to_one_files(hmmout_dir, bin_hmmout)
    for p in glob.glob(hmmout_dir, recursive=True):
        if os.path.isfile(p) and p.endswith(".hmmout"):
            os.remove(p)


def parse_hmmout(hmmout_file: str, hmmout_dir: str) -> Tuple[str, str, str]:
    """
    Parses the output of the hmmsearch to return the the sequence id along with the
    a gene and its corresponding KEGG ORTHOLOGY term as mentioned in the `hmmout_file`.

    Arguments:
        hmmout_file: Filename of the .hmmout file
        hmmout_dir: Directory where hmmout_file is located

    Returns:
        A tuple consisting of:
            - basename: Sequence id
            - gene_id: Gene id
            - k_number: KEGG ORTHOLOGY term found
    """
    if hmmout_file.endswith(".hmmout"):

        kobasename       = hmmout_file.rsplit(".", 1)[0]
        basename         = kobasename.split(".", 1)[1]
        hmmout_file_path = os.path.join(hmmout_dir, hmmout_file)

        with open(hmmout_file_path, "r") as fi:
            for line in fi:
                if not line.startswith("#"):
                    gene_id, _ = line.split()[0:2]  # under _ the accession
                    lines = line.split()
                    if re.match(r"[0-9]+$", lines[2]):
                        k_number = lines[3]
                    else:
                        k_number = lines[2]
                    return basename, gene_id, k_number


def load_merged_ko_file(merged_ko: str) -> pd.DataFrame:
    """
    Load the 3-columns KEGG annotations file as built from the merge_ko()

    Input:
        merged_ko: path to 3-columns output file of the merge_ko()

    Returns:
        pivot_df: a presence-absence (1/0) df where KOs are the rows and bin_ids the columns
    """
    p = Path(merged_ko)

    # Handle gzipped file
    if p.suffix == ".gz":
        decompressed = p.with_suffix("")  # remove .gz
        if not decompressed.exists():
            import gzip
            _logger_.info(f"Decompressing {p.name} -> {decompressed.name}")
            with gzip.open(p, 'rb') as f_in, open(decompressed, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        merged_ko = decompressed
    else:
        # Compress if uncompressed version found and no .gz exists
        gz_path = p.with_suffix(p.suffix + ".gz")
        if not gz_path.exists():
            os.system(f"gzip {p}")
        merged_ko = p

    # Load the (decompressed) file
    df = pd.read_csv(merged_ko, sep="\t")

    # Build presence/absence pivot table
    bin_id, _, ko = df.columns[:3]  # The second column of the file corresponds to the contig id.
    unique   = df.drop_duplicates().assign(presence=1)
    pivot_df = unique.pivot_table(index=ko, columns=bin_id, values="presence", fill_value=0)

    return pivot_df  # keep one | used to alse return the bins_kos


def convert_to_json_serializable(obj: Any) -> Any:
    """
    Recursively serializes entries of an object
    A set is converted to a list, a list is flattened to its items
    and a dictionary keeps its key and their values get serialized.

    Note:
        This is essential step both for allowing a jsonified response and to be able
        to dump a dictionary as a JSON file.
    """
    if isinstance(obj, (int, float, str, bool, type(None))):
        return obj

    elif isinstance(obj, set):
        return list(obj)

    elif isinstance(obj, list):
        return [convert_to_json_serializable(item) for item in obj]

    elif isinstance(obj, dict):
        new_dict = {}
        for key, value in obj.items():
            if not isinstance(key, (str, int, float, bool, type(None))):
                key = str(key)  # or use "|".join(key) if you want to preserve tuple structure better
            new_dict[key] = convert_to_json_serializable(value)
        return new_dict

    else:
        try:
            return json.dumps(obj)
        except TypeError:
            return str(obj)


def ensure_flashweave_format(conf: "Config") -> None:
    """
    Build an OTU table that will be in a FlashWeave-based format.

    Note:
        Saves abundance data to be used with FlashWeave in the output directory.
    """

    flashweave_table = pd.read_csv(
        conf.abundance_table, sep=conf.delimiter
    ).iloc[:, :-1]

    float_col = flashweave_table.select_dtypes(include=["float64"])

    try:

        for col in float_col.columns.values:
            flashweave_table[col] = flashweave_table[col].astype("int64")

        flashweave_table.iloc[:, 0] = flashweave_table.iloc[:, 0].astype(str)
        flashweave_table.to_csv(conf.flashweave_abd_table, sep="\t", index=False)

    except Exception as e:
        _logger_.error(
            """Error in ensuring FlashWeave format: %s.
            Please check your FlashWeave parameters, especially `n_obs_min` and `k_max`.""",
            e,
        )
        raise Exception


def ensure_same_namespace_after_fw(conf: "Config") -> None:
    """
    Reads FlashWeave edgelist file and tries to map sequence ids of node columns of the edgelist
    to their corresponding in the abundance table.

    Attention:
        The need of this was first met with a local data set where sequence ids were like:
        D300244:bin_000023 in the abundance table
        and then in the edgelist returned by FlashWeave, those idsz to D300244.bin_000023 in FlashWeave.

        # NOTE (Haris Zafeiropoulos, 2025-05-16):
        After a few changes this behavior changed but I am not sure why.
        Thus, maybe this step is not necessary anymore and it could be removed.
        Yet, tests are required.

    Note:
        Apparently, the conf.network in this case is in the format FlashWeave networks, thus the `skiprows=2`
    """
    import difflib

    # Function to find the closest match and its index
    def _find_closest_match_with_index(element, list2, cutoff=0.6):
        matches = difflib.get_close_matches(element, list2, n=1, cutoff=cutoff)
        if matches:
            closest_match = matches[0]
            index         = list2.index(closest_match)
            return closest_match, index
        return None, None

    abd_df        = pd.read_csv(conf.flashweave_abd_table, sep="\t")
    abd_df_seqids = abd_df[abd_df.columns[0]].tolist()

    net_df         = pd.read_csv(conf.network, sep="\t", skiprows=2, header=None)
    net_df.columns = ["bin_a", "bind_b", "weight"]

    col1   = net_df["bin_a"].tolist()
    col2   = net_df["bind_b"].tolist()
    weight = net_df["weight"].tolist()

    # Replace closest match in both col1 and col2 with the element from abd_df_seqids
    for element in abd_df_seqids:
        for col in [col1, col2]:  # Iterate over both columns
            closest_match, index = _find_closest_match_with_index(element, col)
            if closest_match:
                # Replace the closest match in the current column
                col[index] = element

    net_df = pd.DataFrame(
        list(zip(col1, col2, weight)), columns=["bin_a", "bind_b", "microbetag::weight"]
    )

    net_df.to_csv(conf.network, sep="\t", index=False, header=False)


def _extend_for_pair(args):
    beneficiary_bin, potential_donor, compls, descrps, pc_percent = args
    local_out = {}

    if not compls:
        return (beneficiary_bin, potential_donor, local_out)

    for compl in compls:
        module_id   = compl[0][3:] if compl[0].startswith("md") else compl[0]
        kos_to_get  = compl[1]
        complet_alt = compl[2]

        if len(kos_to_get) / len(complet_alt) > pc_percent:
            continue

        compl_str = [x if isinstance(x, str) else ";".join(x) for x in compl[1:]]
        triplet   = descrps[descrps["moduleId"] == module_id].values.tolist()[0]

        local_out[len(local_out)] = triplet + compl_str

    return (beneficiary_bin, potential_donor, local_out)


def extend_complements(
    complements_json: str,
    descrps_path: str,
    pc_percent: int,
    pc_dir: str,
    n_workers: int = None
):
    """
    Extends pathway complement annotations based on given settings and descriptions.

    Parameters:
        - complements_json: Path to the complements JSON file.
        - descrps_path: Path to the KEGG MODULES description file.
        - pc_percent: Maximum allowable percentage of required KOs that must be present.
        - pc_dir: Directory to save the extended complements JSON file.
        complements_dict (dict): Dictionary of complements loaded from a JSON file.
        descrps_path (str): Path to the module descriptions file (tab-separated file with no header).

    Returns:
        A dictionary with pathway complementarities to be assigned in the MGG format

    Note:
        Here we build the `pathway_complements_extended.json` a JSON file with the dictionary returned
    """

    if n_workers is None:
        n_workers = max(cpu_count() - 1, 1)

    descrps         = pd.read_csv(descrps_path, sep="\t", header=None)
    descrps.columns = ["category", "moduleId", "description"]
    descrps         = descrps[["moduleId", "description", "category"]]

    out_json = os.path.join(pc_dir, "pathway_complements_extended.json")
    if os.path.exists(out_json):
        return json.load(open(out_json))

    complements_dict = json.load(open(complements_json))
    complements_dict_ext = copy.deepcopy(complements_dict)

    tasks = []
    for beneficiary_bin, donors in complements_dict.items():
        for donor, compls in donors.items():
            tasks.append((beneficiary_bin, donor, compls, descrps, pc_percent))

    with Pool(n_workers) as pool:
        results = pool.map(_extend_for_pair, tasks)

    # merge
    for bin, donor, data in results:
        complements_dict_ext[bin][donor] = data

    json.dump(complements_dict_ext, open(out_json, "w"))
    return complements_dict_ext


def extend_faprotax(faprotax_sub_tables, sequence_id_column_name) -> Tuple[dict[str, list], list[str]]:
    """
    Parses the sub tables of the faprotax analysis
    to assign the biological processes related to each sequence id

    Returns:
        A tuple consisting of:
        - bin_faprotax_traits: A dictionary with the sequence id as key and a list of FAPROTAX trais a value
        - faprotax_traits: A list with the unique set of the FAPROTAX traits found across all taxa of the study
    """
    bin_faprotax_traits = {}

    fapro_sub_tables = [
        os.path.join(faprotax_sub_tables, file)
        for file in os.listdir(faprotax_sub_tables)
    ]

    for file in fapro_sub_tables:
        _logger_.info(f"File: {file}")
        # NOTE (Haris Zafeiropoulos, 2025-05-20):
        # We replace '_' with a space for user's convenience in the MGG
        # Also, this needs to be synced with the MGG.MUtils code for the grouping in the node panel
        trait_name, _ = os.path.splitext(os.path.basename(file))
        trait         = pd.read_csv(file, sep=",", skiprows=1)

        bins_with_trait = trait[sequence_id_column_name].dropna()

        for bin_id in bins_with_trait:
            bin_faprotax_traits.setdefault(bin_id, []).append(trait_name.replace("_", " "))

    faprotax_traits = list(flatten_list(bin_faprotax_traits.values()))

    return bin_faprotax_traits, faprotax_traits


def load_phenotypic_traits(phen_outdir) -> Tuple[Dict[str, Dict[str, Union[str, float]]], Set[str]]:
    """
    Load phenotrex-based trait files and assignm them per genome.

    Returns:
        A tuple consisting of:
            - bin_phen_traits: A dictionary with genome id as key and a dictionary as value, 
                                with each phenotrex-based trait as value and their presence/absence
                                and scores as value
        phentraits: A set with the traits presentt

    Note:
        Example of a `bin_phen_traits`:
        ```
        bin_phen_traits[bin_id][trait_name] = {
            "presence": case["Trait present"],
            "confidence": case["Confidence"],
        }
        ```
    """
    bin_phen_traits = {}
    phentraits      = set()

    prediction_files = [
        os.path.join(phen_outdir, file)
        for file in os.listdir(phen_outdir)
    ]

    for file in prediction_files:

        if os.path.getsize(file) == 0:
            continue

        trait          = pd.read_csv(file, sep="\t", skiprows=1)
        trait_name     = os.path.basename(file).split(".prediction.tsv")[0]
        trait_filtered = trait[trait["Trait present"].notna()]
        trait_dict     = trait_filtered.to_dict(orient="records")

        for case in trait_dict:
            bin_id, _ = os.path.splitext(case["Identifier"])
            if bin_id not in bin_phen_traits:
                bin_phen_traits[bin_id] = {}
            phentraits.add(trait_name)
            bin_phen_traits[bin_id][trait_name] = {
                "presence": case["Trait present"],
                "confidence": case["Confidence"],
            }

    return bin_phen_traits, phentraits


def is_any_nan(x) -> bool:
    """
    Checks whether the input value is NaN (Not a Number).

    It first tries to use `numpy.isnan()` for numerical or array-like inputs. 
    If that fails (e.g., for non-numeric types), it falls back to checking if the string
    representation of `x` is equal to 'nan' (case-insensitive).

    Returns:
        bool
    """
    try:
        return np.isnan(x)
    except Exception:
        return str(x).lower() == 'nan'


def remove_nan_from_list(lst: List) -> List:
    """Removes Nan from a list using the :class:`is_any_nan`."""
    return [x for x in lst if not is_any_nan(x)]


from typing import Optional


def detect_separator(file_path: str) -> Optional[str]:
    """
    Detects the separator used in a text file.
    Tries csv.Sniffer first, falls back to common delimiters.

    Returns:
        Detected delimiter as a string or None if undetectable.
    """

    # Common delimiters to check if csv.Sniffer fails
    fallback_delimiters = ['\t', ',', ';', ' ']

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            f.seek(0, 2)
            file_size = f.tell()

            if file_size == 0:
                raise ValueError("File is empty")

            # Use a simpler and safer sampling logic
            sample_size = max(min(file_size, int(file_size * 0.1)), 2000)
            f.seek(0)
            sample = f.read(sample_size)

            if not sample.strip():
                raise ValueError("File contains only whitespace")

            # Try Sniffer first
            try:
                sniffer = csv.Sniffer()
                dialect = sniffer.sniff(sample)
                return dialect.delimiter
            except Exception:
                pass  # Fall through to manual detection

            # Manual heuristic: test fallback delimiters
            first_line = sample.splitlines()[0]
            for delim in fallback_delimiters:
                if delim in first_line:
                    return delim

            # Last resort: try Sniffer again on smaller chunk
            try:
                dialect = csv.Sniffer().sniff(sample[:1000])
                return dialect.delimiter
            except Exception:
                return None

    except Exception as exc:
        raise TypeError(
            f"Could not detect delimiter for file: {file_path}. "
            f"Reason: {exc}"
        ) from exc


def find_three_column_format(file_path: str, delimiter: str) -> tuple[int, Union[None, int]]:
    """
    Checks if a file is in a three-column format and whether the third column is a float.
    If not, it skips row and goes to the next one checking for the 3-colummn format.
    Once met, it returns the line number, if that is neve the case raises an Exception.

    Args:
        file_path (str): Path to the file to be checked.
        delimiter (str): The delimiter used to separate columns (e.g., '\t' for tab-separated values).

    Returns:
        tuple: (line_number, None) if the third column is a float, (line_number, 0) otherwise.
    """
    with open(file_path, "r") as f:
        for line_num, line in enumerate(f, start=1):
            columns = line.strip().split(delimiter)
            if len(columns) == 3:
                try:
                    float(columns[-1])
                    return line_num, None
                except (ValueError, TypeError):
                    pass
    raise TypeError(
        f"The network file {file_path} is not in the 3-columns format required with a numeric weight column."
    )


def get_tool_location(software: str) -> str:
    """
    Check if a software program is available in the system path or in the alternative location.

    Will return either the sofware name itself which will then be ok to run as is (globally)
    or the full path to the software if it's found in the alternative location.
    In both cases, the return value will allow running the software.

    If software not available, it will reaise a SystemExit() error with a message about the missing software.

    Arguments:
        software: Name of the software program to be found

    """

    # Try running prodigal and check if it exists
    # NOTE: This does not meat that the software is not installed under ~/.microbetag
    # If ~/.microbetag was added in PATH, it's gonna still be in this case
    if shutil.which(software) is not None:
        return software
    else:
        _logger_.info(f"No {software} system-wide installation found.")

    # If software is not found, check the alternative location
    HOME = os.path.expanduser("~")
    microbetag_installation = os.path.join(HOME, ".microbetag")
    software_path = os.path.join(microbetag_installation, software)

    # Try running prodigal from the alternative location
    if shutil.which(software_path) is not None:
        # e.g. ~/.microbetag/prodigal
        return software_path

    elif shutil.which(os.path.join(software_path, software)) is not None:
        # e.g. ~/.microbetag/prodigal/prodigal
        return os.path.join(software_path, software)

    elif shutil.which(os.path.join(software_path, "bin", software)) is not None:
        # e.g. ~/.microbetag/prodigal/bin/prodigal
        return os.path.join(software_path, "bin", software)

    else:
        # If neither path works
        _logger_.error(f"{software} is not available. Please install it first.")
        raise SystemExit(f"{software} is not available. Please install it first.")


_logger_ = mtg_logger(__name__)


def is_inside(path, root):
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False
