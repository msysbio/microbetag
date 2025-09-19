# Command for using QS database to annotate quorum sensing functions in users' genome

for genome in ../genome_dir/*.faa;do
    genome_name=$(basename "$genome" .faa)
    hmmsearch --tblout "kegg_hmm_results/${genome_name}_results.tbl" m02024_genes.hmm "$genome" > "kegg_hmm_results/${genome_name}_log.txt"
done
