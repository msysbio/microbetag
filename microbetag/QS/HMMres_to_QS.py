#!/usr/bin python3

import os
import json
import argparse
import csv

def parse_args():
    parser = argparse.ArgumentParser(
        description="Annotate genomes with QS sending and receiving pathways based on HMMsearch results."
    )
    parser.add_argument("input_dir", type=str,
                        help="Directory containing HMMsearch .tbl result files")
    parser.add_argument("qs_json", type=str,
                        help="Path to QS pathway definition JSON file (map02024_parse_dict.json)")
    parser.add_argument("--evalue", type=float, default=1e-5,
                        help="E-value threshold for KO filtering (default: 1e-5)")
    parser.add_argument("--output", type=str, default="qs_summary.csv",
                        help="Output CSV file path (default: qs_summary.csv)")
    return parser.parse_args()

def load_qs_pathways(json_file):
    with open(json_file, "r") as f:
        raw_data = json.load(f)

    formatted = {}
    for pid, entries in raw_data.items():
        entry_dict = {list(d.keys())[0]: list(d.values())[0] for d in entries}
        formatted[int(pid)] = {
            "Mode species": entry_dict["Mode species"],
            "Signal Compound": entry_dict["Signal Compound"],
            "Signal Type": entry_dict["Signal Type"],
            "Biosynthesis": set(entry_dict["Biosysthesis"]),
            "Transporter": set(entry_dict["Transporter"]),
            "Sensing": set(entry_dict["Sensing"])
        }
    return formatted

def parse_tbl_file(file_path, evalue_threshold):
    ko_set = set()
    with open(file_path, "r") as f:
        for line in f:
            if line.startswith("#") or line.strip() == "":
                continue
            parts = line.strip().split()
            if len(parts) < 5:
                continue
            ko = parts[2]
            evalue = float(parts[4]) if "e" not in parts[4] else float(parts[4].replace("e", "E"))
            if evalue < evalue_threshold:
                ko_set.add(ko)
    return ko_set

def analyze_genome(ko_set, qs_pathways):
    sending = []
    receiving = []
    for pid, info in qs_pathways.items():
        bios = info["Biosynthesis"]
        trans = info["Transporter"]
        sens = info["Sensing"]

        is_sender = not bios or bios.issubset(ko_set)
        is_receiver = trans.issubset(ko_set) and sens.issubset(ko_set)

        if is_sender:
            sending.append(str(pid))
        if is_receiver:
            receiving.append(str(pid))

    return "/".join(sending), "/".join(receiving)

def main():
    args = parse_args()
    qs_pathways = load_qs_pathways(args.qs_json)

    result_rows = []

    for filename in os.listdir(args.input_dir):
        if filename.endswith("_results.tbl"):
            file_path = os.path.join(args.input_dir, filename)
            genome = filename.split("_results.tbl")[0]
            kos = parse_tbl_file(file_path, args.evalue)
            send, receive = analyze_genome(kos, qs_pathways)
            result_rows.append((genome, send, receive))

    with open(args.output, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Genome", "Sending Pathway", "Receiving Pathway"])
        for row in result_rows:
            writer.writerow(row)

    print(f"Summary file saved to: {args.output}")

if __name__ == "__main__":
    main()
