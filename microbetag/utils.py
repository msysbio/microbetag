"""
Utils supporting tasks for file parsing and formating
"""
import os, re
import json, csv
import time
import copy
import glob
import shutil
import random
import logging
import subprocess
import pandas as pd
from typing import List



# Handling data related
def get_library_version(library_name):
    import pkg_resources
    try:
        version = pkg_resources.get_distribution(library_name).version
        return version
    except pkg_resources.DistributionNotFound:
        return "Library not found"
    except Exception as e:
        return str(e)

def resolve_relative_path(base_dir, file_path):
    # Count the number of "../" at the beginning
    steps_back = 0
    while file_path.startswith('../'):
        steps_back += 1
        file_path = file_path[3:]  # Remove the leading "../"

    # Move back "steps_back" levels from base_dir
    for _ in range(steps_back):
        base_dir = os.path.dirname(base_dir)

    # Combine the modified base_dir with the remaining file_path
    return os.path.join(base_dir, file_path)


def resolve_file_path(base_dir, file_path):

    # If the file_path is None, return None
    if file_path is None:
        return None

    # Otherwise, resolve the file path based on the base directory and the user's input
    if file_path.startswith('/'):
        path = file_path

    if file_path.startswith('~'):
        path = os.path.expanduser(file_path)

    if file_path.startswith('../'):
        path = resolve_relative_path(base_dir, file_path)

    else:
        path = os.path.join(base_dir, file_path)

    # Check if the file exists
    if os.path.exists(path):
        return path
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


def get_files_with_suffixes(directory, suffixes):
    """
    Recursively retrieves files from a specified directory and its subdirectories
    that have extensions matching a given list of suffixes.

    Parameters:
    directory (str): The root directory to start the search.
    suffixes (list of str): A list of file suffixes (extensions) to match.
                            Each suffix should include the dot (e.g., '.txt', '.csv').

    Returns:
    list of str: A list of full paths to files that match any of the specified suffixes.

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


def flatten(list_of_lists: List):
   """
   This function takes a list of lists and flattens it until it returns a list with
   all the components of the initial one.
   """
   if len(list_of_lists) == 0:
      return list_of_lists
   if isinstance(list_of_lists[0], list):
      return flatten(list_of_lists[0]) + flatten(list_of_lists[1:])
   return list_of_lists[:1] + flatten(list_of_lists[1:])


def run_until_done(command: str):
    """
    Function to run recursively a command until
    """
    if os.system(command) == 0:
        return 1
    else:
        time.sleep(random.randint(2, 10))
        logging.warning("recurscive run of: %s", command)
        run_until_done(command)


def file_exists_and_nonzero(filename: str):
    """
    Check if a file exists and its size is nonzero.

    Args:
        filename (str): The path to the file.

    Returns:
        bool: True if the file exists and its size is nonzero, False otherwise.
    """
    return os.path.exists(filename) and os.path.getsize(filename) > 0


def split_list(input_list: List, chunk_size: int):
    """
    Split a list to sublists of a size.
    """
    return [input_list[i:i + chunk_size] for i in range(0, len(input_list), chunk_size)]


def many_to_one_files(dir_with_files, merged_file):
    """
    Makes a single file out of all files in a directory by concatenating having rows of one after the other

    """
    command = " ".join([
        "find", dir_with_files,
        "-type", "f",
        "-name", 'K*',
        "-print0",
        "|",
        "xargs", "-0", "cat", ">", merged_file
    ])
    os.system(command)


def ko_list_parser(ko_list: str):
    """
    Parses ko_list file into a dict object - based on DiTing

    :param ko_list: path to the ko_list file that comes from the kofam database https://www.genome.jp/ftp/db/kofam/
    :return: a dictionary mapping knum to threshold and score_type
    :rtype: dict
    """
    ko_dic = {}  # { knum : [threshold, score_type] }
    with open(ko_list) as fi:
        next(fi)  # skip the first line (header)
        for line in fi:
            knum, threshold, score_type = line.split('\t')[0:3]
            if threshold == '-':
                continue
            else:
                ko_dic[knum] = [threshold, score_type]
    return ko_dic


def merge_ko(hmmout_dir, output):
    """
    Parses the KO<>.<bin>.hmmout files produced by the kegg_annotation() function
    to create a single 3-column file (output) with the bin_id, the corresponding conting and the KO that wa mapped to it.
    The function then returns a dictionary with the bin ids as the keys and the set of KOs found to each as the value.

    :param hmmout_dir (str): path to the .hmmout files
    :param output (str): path/filename to save the output file
    """
    # Under any circumstances microbetag will overwrite the ko_merged.txt file
    with open(output, 'w') as fo:
        fo.write('bin_id\tcontig_id\tko_term\n')
    # Iterate through the bin folders in the hmmout folder
    for bin_id in os.listdir(hmmout_dir):
        bin_folder = os.path.join(hmmout_dir, bin_id)
        bin_file = "_".join([bin_id, "kos.tsv"])
        bin_kos_file = os.path.join(bin_folder, bin_file)
        # Append
        os.system(
            " ".join([
                "cat", bin_kos_file, ">>", output
            ])
        )


def bin_kos_to_file(hmmout_dir, bin_id):
    """
    Builds a 3-col file for a bin and remove the KO-specific output files of hmmsearch

    :param hmmout_dir: Directory to the hmmout files
    :param ko_tmp:
    """
    # Write 3-cols entries in tmp file
    bin_kos_file = os.path.join(hmmout_dir, "".join([bin_id, "_kos.tsv"]))
    if not os.path.exists(bin_kos_file):
        open(bin_kos_file, 'w').close()

    for hmmout_file in os.listdir(hmmout_dir):
        try:
            basename, gene_id, k_number = parse_hmmout(hmmout_file, hmmout_dir)
            with open(bin_kos_file, 'a') as fo:
                fo.write(basename + '\t' + gene_id + '\t' + k_number + '\n')
        except:
            # Ignore non-informative lines
            pass

    # Remove .hmmout files
    bin_hmmout = os.path.join(hmmout_dir, ".".join([bin_id, "hmmout.all"]))
    print(bin_hmmout)
    many_to_one_files(hmmout_dir, bin_hmmout)
    for p in glob.glob(hmmout_dir, recursive=True):
        print(p)
        if os.path.isfile(p) and p.endswith(".hmmout"):
            os.remove(p)


def parse_hmmout(hmmout_file, hmmout_dir):
    """
    Parses the output of the hmmsearch

    :param hmmout_file (str): Filename of the .hmmout file
    :param hmmout_dir (str): Directory where hmmout_file is located
    :return basename (str): Bin id
    :return gene_id (str): Gene id
    :retrun k_number (str): KEGG ORTHOLOGY term found
    """
    if hmmout_file.endswith('.hmmout'):
        kobasename = hmmout_file.rsplit('.', 1)[0]
        basename = kobasename.split('.', 1)[1]
        hmmout_file_path = os.path.join(hmmout_dir, hmmout_file)
        with open(hmmout_file_path, 'r') as fi:
            for line in fi:
                if not line.startswith('#'):
                    gene_id, _ = line.split()[0:2]  # under _ the accession
                    lines = line.split()
                    if re.match(r'[0-9]+$', lines[2]):
                        k_number = lines[3]
                    else:
                        k_number = lines[2]
                    return basename, gene_id, k_number


def load_merged_ko_file(merged_ko):
    """
    Load the 3-columns KEGG annotations file as built from the merge_ko()

    Input:
        merged_ko (str): path to 3-columns output file of the merge_ko()

    Returns:
        pivot_df (pd.DataFrame): a presence-absence (1/0) df where KOs are the rows and bin_ids the columns

    """
    if merged_ko.endswith('.gz'):
        os.system(f"gunzip {merged_ko}")
        merged_ko = merged_ko.rsplit('.gz', 1)[0]

    df = pd.read_csv(merged_ko, sep="\t")
    column_names = df.columns.tolist()
    bin_id, _, ko = column_names[:3]

    # Pivot the DataFrame to have 'kegg_id' as rows and 'bin_id' as columns
    unique_combinations = df.drop_duplicates().copy()
    unique_combinations.loc[:, 'presence'] = 1
    pivot_df = unique_combinations.pivot_table(index=ko, columns=bin_id, values='presence', fill_value=0)

    os.system(f"gzip {merged_ko}")

    return pivot_df  # keep one | used to alse return the bins_kos


def convert_to_json_serializable(obj):
    """
    Recursively serializes entries of an object, i.e. a set is converted to a list, a list is split to its items
    and a dictionary keeps its key and their values get serialized
    """
    if isinstance(obj, (int, float, str, bool, type(None))):
        return obj
    elif isinstance(obj, set):
        return list(obj)
    elif isinstance(obj, list):
        return [convert_to_json_serializable(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: convert_to_json_serializable(value) for key, value in obj.items()}
    else:
        try:
            return json.dumps(obj)
        except TypeError:
            return str(obj)


def ensure_flashweave_format(conf):
    """
    Build an OTU table that will be in a FlashWeave-based format.
    """

    flashweave_table = pd.read_csv(conf.abundance_table, sep=conf.delimiter).iloc[:, :-1]
    float_col = flashweave_table.select_dtypes(include=['float64'])

    try:
        for col in float_col.columns.values:
            flashweave_table[col] = flashweave_table[col].astype('int64')
        flashweave_table.iloc[:, 0] = flashweave_table.iloc[:, 0].astype(str)
        flashweave_table.to_csv(conf.flashweave_abd_table, sep='\t', index=False)
        return 1

    except Exception as e:
        logging.error(
            """Error in ensuring FlashWeave format: %s.
            Please check your FlashWeave parameters, especially `n_obs_min` and `k_max`.""",
            e
        )
        return 0


def ensure_same_namespace_after_fw(conf):
    """
    [TODO] can be removed but let's wait
    Inconsistencies from D300244:bin_000023 in the abundance table to D300244.bin_000023 in FlashWeave.
    Keep the routine in general along with the find_id_differences().

    Apparently, the conf.network is a FlashWeave network file - thus the skip 2 rows
    """
    import difflib

    # Function to find the closest match and its index
    def find_closest_match_with_index(element, list2, cutoff=0.6):
        matches = difflib.get_close_matches(element, list2, n=1, cutoff=cutoff)
        if matches:
            closest_match = matches[0]
            index = list2.index(closest_match)
            return closest_match, index
        return None, None


    abd_df = pd.read_csv(conf.flashweave_abd_table, sep="\t")
    abd_df_seqids = abd_df[abd_df.columns[0]].tolist()

    net_df = pd.read_csv(conf.network, sep="\t", skiprows=2, header = None)
    net_df.columns = ["bin_a", "bind_b", "weight"]

    col1 = net_df["bin_a"].tolist()
    col2 = net_df["bind_b"].tolist()
    weight = net_df["weight"].tolist()

    # Replace closest match in both col1 and col2 with the element from abd_df_seqids
    for element in abd_df_seqids:
        for col in [col1, col2]:  # Iterate over both columns
            closest_match, index = find_closest_match_with_index(element, col)
            if closest_match:
                # Replace the closest match in the current column
                col[index] = element

    net_df = pd.DataFrame(list(zip(col1, col2, weight)), columns=["bin_a", "bind_b", "microbetag::weight"])

    net_df.to_csv(conf.network, sep="\t", index=False, header=False)

    return 1


def extend_complements(complements_json,
                       descrps_path,
                       max_scratch_alt,
                       pathway_complement_percentage,
                       pathway_complements_dir):
    """
    Extends pathway complement annotations based on given settings and descriptions.

    Parameters:
        - complements_json: Path to the complements JSON file.
        - descrps_path: Path to the KEGG MODULES description file.
        - max_scratch_alt: Maximum number of alternative complements allowed.
        - pathway_complement_percentage: Maximum allowable percentage of required KOs that must be present.
        - pathway_complements_dir: Directory to save the extended complements JSON file.
        complements_dict (dict): Dictionary of complements loaded from a JSON file.
        descrps_path (str): Path to the module descriptions file (tab-separated file with no header).

    Returns:
        dict: Pathway Complementarities in a dictionary to be assigned in the mgg format

    Builds:
        pathway_complements_extended: JSON file with the dictionary returned
    """
    # Load and process module descriptions
    descrps = pd.read_csv(descrps_path, sep="\t", header=None)
    descrps.columns = ["category", "moduleId", "description"]
    column_order = ["moduleId", "description", "category"]
    descrps = descrps[column_order]

    # Deep copy the complements dictionary
    with open(complements_json, 'r') as file:
        complements_dict = json.load(file)
    # complements_dict = json.load(open(complements_json))
    complements_dict_ext = copy.deepcopy(complements_dict)

    # Process complements
    for beneficiary_bin, potential_donors in complements_dict.items():
        for potential_donor, compls in potential_donors.items():
            if compls:
                complements_dict_ext[beneficiary_bin][potential_donor] = {}
                for compl in compls:
                    module_id = compl[0][3:]  # Extract module ID
                    kos_to_get = compl[1]     # KOs required to complete the pathway
                    complet_alt = compl[2]   # Alternative complements

                    # Skip if the complement is too complex based on settings
                    if len(complet_alt) == len(kos_to_get) > max_scratch_alt:
                        continue

                    # Skip if the percentage exceeds the threshold
                    perce = len(kos_to_get) / len(complet_alt)
                    if perce > pathway_complement_percentage:
                        continue

                    # Prepare the complement string
                    compl_str = [x if isinstance(x, str) else ";".join(x) for x in compl[1:]]

                    # Fetch module description details
                    triplet = descrps[descrps["moduleId"] == module_id].values.tolist()[0]

                    # Add extended complement details
                    complements_dict_ext[beneficiary_bin][potential_donor][
                        len(complements_dict_ext[beneficiary_bin][potential_donor])
                        ] = triplet + compl_str

    # Save extended complements to JSON
    extended_path_compl_json = os.path.join(pathway_complements_dir, "pathway_complements_extended.json")
    with open(extended_path_compl_json, "w") as f:
        json.dump(complements_dict_ext, f)

    return complements_dict_ext


def extend_faprotax(conf):

    bin_faprotax_traits = {}
    fapro_sub_tables = [os.path.join(conf.faprotax_sub_tables, file) for file in os.listdir(conf.faprotax_sub_tables)]
    for file in fapro_sub_tables:
        trait_name, _ = os.path.splitext(os.path.basename(file))
        trait = pd.read_csv(file, sep="\t", skiprows=1)
        bins_with_trait = trait[conf.sequence_id_column_name].dropna()
        for bin_id in bins_with_trait:
            bin_faprotax_traits.setdefault(bin_id, []).append(trait_name)

    faprotax_traits = list(flatten_list(bin_faprotax_traits.values()))

    return bin_faprotax_traits, faprotax_traits


def load_phenotypic_traits(conf):
    """PhenDB-like traits"""
    logging.info("Loading phenotypic traits")
    bin_phen_traits = {}
    phentraits = set()

    all_phen_df = os.path.join(conf.predictions_path, "phen_traits.tsv")    # TODO: consider giving this also as an argument in the config -- MAKE SURE THEY GIVE SEQUENCE ID AND NOT GTDB ID !!
    if os.path.exists(all_phen_df):
        df = pd.read_csv(all_phen_df, sep="\t")
        df = df.drop(["NCBI_ID", "gtdb_id"], axis=1)
        phentraits = {x for x in df.columns if "Score" not in x}
        phentraits.remove("sequence_id")
        list_of_dics = df.to_dict(orient="records")

        for entry in list_of_dics:
            bin_phen_traits[entry["sequence_id"]] = {}
            for trait in phentraits:
                bin_phen_traits[entry["sequence_id"]][trait] = {
                    "presence": entry[trait],
                    "confidence": entry["".join([trait, "Score"])]
                }
    else:
        prediction_files = [os.path.join(conf.predictions_path, file) for file in os.listdir(conf.predictions_path)]
        for file in prediction_files:
            if os.path.getsize(file) == 0:
                continue

            trait = pd.read_csv(file, sep="\t", skiprows=1)
            trait_name = os.path.basename(file).split(".prediction.tsv")[0]
            trait_filtered = trait[trait['Trait present'].notna()]
            trait_dict = trait_filtered.to_dict(orient="records")

            for case in trait_dict:
                bin_id, _ = os.path.splitext(case["Identifier"])
                if bin_id not in bin_phen_traits:
                    bin_phen_traits[bin_id] = {}
                phentraits.add(trait_name)
                bin_phen_traits[bin_id][trait_name] = {
                    "presence": case["Trait present"],
                    "confidence": case["Confidence"]
                }
    return bin_phen_traits, phentraits


def flatten_list(lista, flat_list=[]):
    """
    Recursive function taking as input a nested list and returning a flatten one.
    E.g. ['GCF_003252755.1', 'GCF_900638025.1', 'GCF_003252725.1', 'GCF_003253005.1', 'GCF_003252795.1', ['GCF_000210895.1'], ['GCF_000191405.1']]
    becomes ['GCF_003252755.1', 'GCF_900638025.1', 'GCF_003252725.1', 'GCF_003253005.1', 'GCF_003252795.1'].
    """
    for i in lista:
        if isinstance(i, list):
            flatten_list(i, flat_list)
        else:
            flat_list.append(i)
    return set(flat_list)


def detect_separator(file_path):
    """
    Detect the separator used in a text file, i.e `\t`,  `,` , `;` etc.
    """
    try:
        with open(file_path, 'r') as file:

            # Get the total file size
            file.seek(0, 2)  # Move to the end of the file
            file_size = file.tell()

            # Calculate 1% of the file size: 1e6 is 1MB
            percent_size = (
                file_size if file_size < 1e5 else
                int(file_size * 0.2) if file_size < 1e6 else
                int(file_size * 0.1) if 1e7 < file_size < 1e8 else
                int(file_size * 0.01)
            )
            percent_size = max(percent_size, int(1e5))

            # Log sizes
            logging.info(f"file_size of {file_path}: {file_size}") ; logging.info(f"percent_size:  {percent_size}")

            # # Move to the start of the file
            file.seek(0)
            sample = file.read(percent_size)

            # Use csv.Sniffer to detect the dialect
            sniffer = csv.Sniffer()
            dialect = sniffer.sniff(sample)
            return dialect.delimiter

    except:
        raise TypeError(f"Cannot get delimiter for file {file_path}")


def find_three_column_format(file_path, delimiter):
    with open(file_path, 'r') as f:
        for line_num, line in enumerate(f, start=1):
            # Split by tab and check the number of columns
            columns = line.strip().split(delimiter)
            if len(columns) == 3:
                if isinstance(columns[-1], float):
                    return line_num, None
                else:
                    return line_num, 0
    raise ValueError(f"The network file {file_path} is not in the 3-columns format required.")


def get_tool_location(software):
    """
    Check if a software is available in the system path or in the alternative location.
    Will return either the sofware name itself which will then be ok to run as is
    or the full path to the software if it's found in the alternative location.
    In both cases, the return value will allow running the software.
    """

    # Try running prodigal and check if it exists
    # NOTE: This does not meat that the software is not installed under ~/.microbetag
    # If ~/.microbetag was added in PATH, it's gonna still be in this case
    if shutil.which(software) is not None:
        print("Case 1")
        return software
    else:
        print(f"No {software} system-wide installation found.")

    # If software is not found, check the alternative location
    HOME = os.path.expanduser("~")
    microbetag_installation = os.path.join(HOME, ".microbetag")
    software_path = os.path.join(microbetag_installation, software)

    # Try running prodigal from the alternative location
    if shutil.which(software_path) is not None:
        print("Case 2")  # e.g. ~/.microbetag/prodigal
        return software_path

    elif shutil.which(os.path.join(software_path, software)) is not None:
        print("Case 3")  # e.g. ~/.microbetag/prodigal/prodigal
        return os.path.join(software_path, software)

    elif shutil.which(os.path.join(software_path, "bin", software)) is not None:
        print("Case 4")  # e.g. ~/.microbetag/prodigal/bin/prodigal
        return os.path.join(software_path, "bin", software)

    else:
        # If neither path works
        logging.error(f"{software} is not available. Please install it first.")
        raise SystemExit(f"{software} is not available. Please install it first.")
