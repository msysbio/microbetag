#!/usr/bin/env bash

set -euo pipefail

# Default irectory to store pulled SIFs
SIF_DIR="${HOME}/.singularity/mtg-images/"

# Parse optional arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -s|--sif-dir)
            SIF_DIR="$2"
            shift 2
            ;;
        *)
            echo "Unknown parameter: $1"
            exit 1
            ;;
    esac
done

mkdir -p "$SIF_DIR"
cd "$SIF_DIR"

# Make a map of working-fine Docker to Singularity names 
declare -A IMAGES=(
               [hariszaf-microbetag-nf-0.1.0]="hariszaf/microbetag-nf:0.1.0"
                     [hariszaf-carveme-1.6.6]="hariszaf/carveme:1.6.6"
                 [hariszaf-flashweave-0.19.2]="hariszaf/flashweave:0.19.2"
                   [hariszaf-phenotrex-0.6.0]="hariszaf/phenotrex:0.6.0"
  [biocontainers-prodigal-v1-2.6.3-4-deb_cv1]="biocontainers/prodigal:v1-2.6.3-4-deb_cv1"
                           [staphb-hmmer-3.4]="staphb/hmmer:3.4"
)

# Pull Singularity images from DockerHub, if not already in the SIF_DIR
for name in "${!IMAGES[@]}"; do
  sif="${name}.img"  
  image="docker://${IMAGES[$name]}"
  if [[ -s "$sif" ]]; then
    echo "✅ $sif already exists, skipping."
  else
    echo "⬇️  Pulling $image as $sif..."
    singularity pull --name "$sif" "$image"
  fi
done
