---
title: Run microbetag in large datasets
layout: default
parent: Advanced usage
nav_order: 4
description: "how to run microbetag when MGG is not big enough"
---

Large dataset
===================

```{Note}
We define a dataset as large if it is intended for use with `microbetagDB` and contains several thousand taxa (sequence IDs). While the number of samples also influences microbetag's runtime, its impact is significantly smaller.

If you want to annotate a dataset of any size using your own genomes, bins, or MAGs, follow the corresponding tutorial [here](local.md).

```

In case of large datasets, `microbetag` full on-the-fly run is probably not an option, even if you do run the preprocessing step. 

For example, imagine you have a 16S rRNA marker-gene dataset and a couple of hundreds of samples. 

Based on the [`microbetag_prep` tutorial](prep.md), you have taxonomically annotated them with the GTDB-oriented 16S reference database, and you built a co-occurrence network using FlashWeave. 

Now, let's say you wish to perform network clustering on your network. 
Asking for this on the on-the-fly version of `microbetag` will lead to a `RuntimeError` and your session will probably fail. 

```{important}
When working with large datasets, it is strongly suggested you run as many steps as possible locally. 

In its current version, the `microbetag` stand-alone tool does not support making API queries on `microbetagDB`
but this is on [top of our to-do list](https://github.com/hariszaf/microbetag/issues/20).
```

In this tutorial, we show how we handled such a large dataset.


## 16S rRNA data of hundreds of sub-gingival plaque samples from a Qiita project

<div style="display: flex; gap: 10px;">
   <a href="https://github.com/hariszaf/microbetag/tree/ms/examined_cases/enrichment" class="btn-purple"> Tutorial files </a>
</div>


From its record on [Qiita](https://qiita.ucsd.edu/study/description/1928) and with the 
[`get_biom.R`](../_static/download/large_dataset/get_biom.R) script, 
we were able to build the [`Subgingival_plaque.txt`](../_static/download/large_dataset/Subgingival_plaque.txt) file. 

In Qiita, the first column corresponds to Silva sequence identifiers in which the OTUs of the study were mapped against. 
Since we cannot get directly the OTUs of the study, we used those identifiers to get their Silva closest ones. 


I downloaded biom file and sample description file from the Qiita url given above, then selected the latest version (69750).
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



Using the [`Subgingival_plaque_taxonomy_Silva_seq.csv`]()
we used the Docker `microbetag_prep` tool to get a GTDB-based taxonomy assignment and a FlashWeave network. 

To this end, we first created a folder called `subgingival_plaque` where we moved the 
`Subgingival_plaque_taxonomy_Silva_seq.csv` file. 
We then downloaded the [`config.yml`](../_static/download/large_dataset/config.yml) file for the `microbetag_prep` tool, 
and we set its parameters accordingly.
In this case, we set the `sensitive` parameter as `false`, since the number of taxa present would lead to a vast number of associations.
The `heterogeneous` parameter was also set to `false`. 

We then ran:
```bash
    docker run --rm -it --entrypoint /bin/bash -v ./subgingival_plaque:/media hariszaf/microbetag_prep:v1.0.1
```

and this entered us on a container where our input data would be under `/media`.

```bash
    root@50a101bce75f:/pre_microbetag# ls /media/
    Subgingival_plaque_Silva_seq.csv  config.yml
```

we then ran the `microbetag_prep`, which resulted in the `prep_output` folder, in the mounted `/media` folder:

```bash
    python 
```



```{attention}
**CONFIGURATION FILE VERSIONING**

Make sure that you always use the configuration file version that matches the tool version you are using.

```



Thus, `microbetag_prep` returned [GTDB_tax_assigned_abundance_table.tsv](../_static/download/large_dataset/prep_output/GTDB_tax_assigned_abundance_table.tsv) that keeps the same sequence identifiers as the original but now the taxonomy has been replaced and instead of 
the Silva one, we have the GTDB. 
Also, the [network_output.edgelist](../_static/download/large_dataset/prep_output/network_output.edgelist)
is the result of FlashWeave




(Qiita context: Pick_closed-reference_OTUs-SILVA-LS454-16S-V4-100nt-cb8fea)
To exploit `microbetag`'s full potential, instead of using the taxonomies directly, we got 
