#!/usr/bin/env bash

# -----------------------------------------------------------------------------
# Description:
#   Parses all the .hmmout files produced from hmmsearch of all genomes, to 
#   generate a 3-column table (bin_id, contig_id, ko_term). 
#   Intended to be used after running KO annotation
#   tools, where downstream steps expect a headered TSV file.
#
# Usage:
#   ./build_ko_table.sh <threads> <output_file>
#
# Arguments:
#   threads       Number of threads available for downstream processing.
#                 This script itself only stores the value; it may be used
#                 by subsequent commands in the workflow.
#
#   output_file   Path to the output TSV file. The script creates this file
#                 and writes the header:
#                   bin_id    contig_id    ko_term
#
# Output:
#   A tab-separated file at <output_file> containing the header line.
#
# Example:
#   ./build_ko_table.sh 8 results/ko_table.tsv
# -----------------------------------------------------------------------------

    threads="$1"
output_file="$2"

# Build the 3-column file 
echo -e "bin_id\tcontig_id\tko_term" > $output_file

find -L hmmout_* -name "*.hmmout" -print0 | parallel -0 -j $threads --bar --no-notice '
      f={}

      # Skip file if it has no non-comment lines
      if ! grep -q "^[^#]" "$f"; then
          exit 0
      fi

      fname=$(basename "$f")                  # e.g., K00099_bin_48.hmmout
      dir=$(dirname "$f")                     # e.g., hmmout_bin_48
      dirbase=$(basename "$dir")              # e.g., hmmout_bin_48
      genome=${dirbase#hmmout_}                  # e.g., bin_48
      ko=${fname%%_*}                          # e.g., K00099

      # Process non-comment lines
      grep "^[^#]" "$f" | awk -F" " -v genome="$genome" -v ko="$ko" '\''{print genome "\t" $1 "\t" ko}'\''
  ' >> $output_file

# Build a tarball with all the hmmout profiles of each bin
find hmmout_*/ -name "*.hmmout" -type f -print | tar -zcvf hmmout.tar.gz -T -
