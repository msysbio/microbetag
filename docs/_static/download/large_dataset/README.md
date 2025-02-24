# Use case for enrichment tests with `microbetag`


From its record on [Qiita](https://qiita.ucsd.edu/study/description/1928) and with the `get_biom.R` we were able to build the `Subgingival_plaque.txt` file. 

To exploit `microbetag`'s full potential, instead of using the taxonomies directly, we got 



(Qiita context: Pick_closed-reference_OTUs-SILVA-LS454-16S-V4-100nt-cb8fea)



I downloaded biom file and sample description file from the quiita url given above, then selected the latest version (69750).
Then I got an OTU table like this:

```bash
biom convert -i otu_table.biom -o hmp_otu_table.txt --to-tsv --header-key taxonomy
```

Then I removed the comment symbol in front of OTU. 
Then some R to only collect subgingival plaque samples and get rid of zero abundance taxa (see below).

Then I added “id” as identifier column name. 
This could be loaded into MGG without problem, but microbetag failed (error 500), likely because the lineages are not in the expected format. 
I can deal with the lineages, but maybe lineage parsing can be more flexible on microbetag’s end, since the biom format is very popular and to be user-friendly, it would be good if microbetag accepts tables generated from biom files.



and based on our study's metadata 
https://qiita.ucsd.edu/study/description/1928

Based on the `seqs_otus.log` file, we noticed that 
`silva_119_Silva_119_rep_set97 ` 
was used for the taxonomy assignment of the OTUs inferred in the study. 

Thus, from 
https://www.arb-silva.de/download/archive/qiime
we were able to download `Silva_119_release.zip` 


```awk
awk -F, '
NR==FNR {
    if($0 ~ /^>/) { 
        id=substr($1, 2);  # Remove ">" from the ID in the FASTA header
        getline;            # Move to the sequence line
        seq[id]=$0;         # Store the sequence in the array with ID as the key
    } 
    next;                   # Skip further processing for the FASTA file
} 
{
    id=$1;                    # Keep the full ID from the first column of the abundance table (up to the comma)
    if(id in seq) {           # Check if the ID exists in the seq array
        $0=$0","seq[id];      # Append the matching sequence to the current line
        print $1, $0;         # Print the full ID from the abundance table and the updated line
    }
}' Silva_119_rep_set97.fna Subgingival_plaque.txt > Subgingival_plaque_taxonomy_Silva_seq.csv
```

after that, we added the column names row and removed the empty column added before the taxonomy.







