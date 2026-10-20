#!/bin/bash

## This script downloads the KEGG Orthology HMM database,
## extracts HMMs related to KEGG pathway m02024 (quorum sensing),
## builds an HMMsearch database, and keeps only the final outputs in the current directory.

# Exit on any error
set -e

# Step 0: Check for m02024_genes.txt in current directory
if [[ ! -f m02024_genes.txt ]]; then
    echo "[ERROR] File 'm02024_genes.txt' not found in the current directory."
    echo "Please make sure 'm02024_genes.txt' is placed in the same directory as this script."
    exit 1
fi

# Step 1: Create temporary working directory
workdir=$(mktemp -d)

# Step 2: Download KEGG HMM database
echo "[INFO] Downloading KEGG HMM profiles (around 1Gb, this may take a while) ..."
#wget https://www.genome.jp/ftp/db/kofam/profiles.tar.gz -O "$workdir/profiles.tar.gz"
curl -o "$workdir/profiles.tar.gz" https://www.genome.jp/ftp/db/kofam/profiles.tar.gz
tar -xzf "$workdir/profiles.tar.gz" -C "$workdir"
rm "$workdir/profiles.tar.gz"

# Step 3: Copy required HMMs
mkdir "$workdir/required_hmm"
xargs -a m02024_genes.txt -I {} sh -c 'cp "'"$workdir"'/profiles/{}.hmm" "'"$workdir"'/required_hmm/" 2>/dev/null || echo "[WARNING] File not found: {}.hmm"'

# Step 4: Build HMM database
cat "$workdir"/required_hmm/*.hmm > m02024_genes.hmm
hmmpress m02024_genes.hmm

# Step 5: Clean up all temporary files and folders
rm -rf "$workdir"

echo "[INFO] HMM database successfully built:"
ls m02024_genes.hmm*