import csv
import argparse
from multiprocessing import Pool, cpu_count
from collections import defaultdict

def parse_pathway_string(pw_str):
    return set(pw_str.split("/")) if pw_str else set()

def load_genome_data(input_csv):
    genome_data = {}
    with open(input_csv, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            genome = row["Genome"]
            genome_data[genome] = {
                "send": parse_pathway_string(row["Sending Pathway"]),
                "recv": parse_pathway_string(row["Receiving Pathway"])
            }
    return genome_data

def compare_sender_with_all(args):
    sender, send_set, genome_data = args
    rows = []
    for receiver, recv_dict in genome_data.items():
        recv_set = recv_dict["recv"]
        common = send_set & recv_set
        if common:
            rows.append((sender, receiver, "/".join(sorted(common, key=int))))
    return rows

def generate_pathway_pairs_parallel(genome_data, output_csv, n_processes=None):
    senders = [(s, d["send"], genome_data) for s, d in genome_data.items() if d["send"]]
    with Pool(processes=n_processes or cpu_count()) as pool:
        all_rows_nested = pool.map(compare_sender_with_all, senders)

    all_rows = [row for sublist in all_rows_nested for row in sublist]

    with open(output_csv, "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Sender", "Receiver", "Pathways"])
        writer.writerows(all_rows)

def generate_pathway_pairs_serial(genome_data, output_csv):
    genomes = list(genome_data)
    rows = []
    for sender in genomes:
        send_set = genome_data[sender]["send"]
        if not send_set:
            continue
        for receiver in genomes:
            recv_set = genome_data[receiver]["recv"]
            common = send_set & recv_set
            if common:
                rows.append((sender, receiver, "/".join(sorted(common, key=int))))
    with open(output_csv, "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Sender", "Receiver", "Pathways"])
        writer.writerows(rows)

def main():
    parser = argparse.ArgumentParser(
        description="Generate sender–receiver–pathway table from QS summary file."
    )
    parser.add_argument("-i", "--input", required=True, help="Input CSV: qs_sending_receiving_summary.csv")
    parser.add_argument("-o", "--output", required=True, help="Output CSV: sender_receiver_pathway_table.csv")
    parser.add_argument("--force-parallel", action="store_true", help="Force use of parallel processing")
    parser.add_argument("--no-parallel", action="store_true", help="Disable parallel processing")
    parser.add_argument("--threshold", type=int, default=1000, help="Genome count threshold to enable parallel mode")

    args = parser.parse_args()

    genome_data = load_genome_data(args.input)
    genome_count = len(genome_data)

    if args.no_parallel:
        print("Running in serial mode (manual override).")
        generate_pathway_pairs_serial(genome_data, args.output)
    elif args.force_parallel or genome_count > args.threshold:
        print(f"Running in parallel mode (genome count = {genome_count}).")
        generate_pathway_pairs_parallel(genome_data, args.output)
    else:
        print(f"Running in serial mode (genome count = {genome_count}).")
        generate_pathway_pairs_serial(genome_data, args.output)

if __name__ == "__main__":
    main()
