---
layout: default
title: Input files
nav_order: 6
---

# Input files
{: .no_toc }

---


## Input files

| File            | Description                                                    | requirement_status        |
|-----------------|----------------------------------------------------------------|---------------------------|
| abundance_table | An abundance table (in `.tsv` or `.csv` format)                | mandatory                 | 
| metadata_file   | File describing the sequencing data; for examples see [here]() | optional; using FlashWeave| 
| network_file    | if already built                                               | optional                  |


Please, make sure in case you provide your abundance table as a `.tsv` or `.csv` file where: 
- in the **first column** you have always the **sequence identifier**
- in the **first row** the **samples names** 
- in the **last column** you keep a complete **7-level taxonomy**

If `microbetag` requires for a 7-level taxonomy scheme; for example:

```bash
Bacteria;Firmicutes;Thermoanaerobacteria;Thermoanaerobacterales;Thermoanaerobacteraceae;Caldanaerobius;Caldanaerobius polysaccharolyticus
```

in case an entry reaches only to a higher taxonomic level, `microbetag` fills the entry with NA values

for example

```bash
Bacteria;Firmicutes;Thermoanaerobacteria;Thermoanaerobacterales;Thermoanaerobacteraceae
```

would become

```bash
Bacteria;Firmicutes;Thermoanaerobacteria;Thermoanaerobacterales;Thermoanaerobacteraceae;NA;NA;NA
```


<!-- fuzzywuzzy uses a threshold - that is set relatively high (90) so there are no false positives. 
in order not to loose species level annotations, please have a look so you do not any unessary characters on your taxonomies, e.g. `[Salmonella] infantis` 
would get a lower score that `Salmonella infantis`, so removing `[` and `]` characters would benefit.  -->




{: .important-title}
> Curate your taxonomies! 
> 
> If you have a taxonomy that "skips" a level, or another one that has more levels, microbetag will fail. 
> You need to curate those taxonomies manually and make sure you always have a 7-level scheme for all the entries on your table.




For input file examples, please have a look [here](https://github.com/hariszaf/microbetag/tree/develop/tests).


{: .warning } 
> Do not use numeric characters only for labeling your samples and/or the sequences mentioned in your abundance table. 
> For example, `324` as a sample id will lead microbetag to fail. 



### Case 1: all you have is your abundance table and your taxonomies 

For up to a few thousands of sequences entries, microbetag can be a one-stop-shop application performing both taxonomy annotation, network generation and annotation. 

Moving on with microbetag's taxonomy annotation is always a best practice as it makes sure that the sequences assigned to the species/strain level, they will all be annotated from microbetag. 

Further, one can keep both the taxonomies assigned from `microbetag` and from any other software. 

However, if you would like to move on with your taxonomy scheme, microbet`ag enables that, but you should know that there's a big chance of loosing some annotations. 

In case 1, one may also have some metadata describing the sequencing data. FlashWeave, the software `microbetag` invokes to build the co-occurrence network, can exploit metadata. 

{: .important-title}
> THE `PHYLOSEQ` CASE
>
> In case you start from a `phyloseq` object, you may get a `.tsv` file using the 
> [`tax_table`](https://www.rdocumentation.org/packages/phyloseq/versions/1.16.2/topics/tax_table) and the
> [`otu_table`](https://www.rdocumentation.org/packages/phyloseq/versions/1.16.2/topics/otu_table) functions of the `phyloseq` library. 
> 
> ```
> # In an R environment, assuming `physeq` is a `phyloseq` object.
> OTU_TAX <- cbind(
>    data.frame(otu_table(physeq)), 
>    data.frame(tax_table(physeq))
>)
>write.table(OTU_TAX, "OTU_TAX.txt", 
>            row.names = TRUE, col.names = TRUE, sep = "\t", quote=FALSE)
>```


{: .important-title}
> THE `.BIOM` CASE
>
> In case you start from a `biom` file, you may get a `.tsv` file using the 
> 
> ```bash 
> biom convert -i otu_table.biom -o otu_table.csv --to-tsv --header-key taxonomy
> ```
> Make sure you have the `biom` tools installed; if not, you may follow the instructions you can find [here](https://biom-format.org/index.html) to get them.
<!-- https://www.metagenomics.wiki/tools/16s/qiime/otu-biom-table -->





If you want to run FlashWeave with a metadata file, you need to remember that FlashWeave considers as variables both the sequence ids (i.e., ASVs/OTUs/bins) and the metavariables (e.g. pH, sex, any 
variable on your metadata file). Thus, you need to have both of them as **rows**, contrary to what we do in most microbiome analyses. 

Here is a toy example of how your files should look like: 

```bash
(base) u23423@localhost:microbetag$ head  `abundance_file.txt`
seqId    sample_1    sample_2    sample_3
asv_1    10        0        3
asv_2     0       21       43
asv_3    32       31        2
asv_4     0        0       12

(base) u23423@localhost:microbetag$ head  metadata_file.tsv
Metadata_1      0.2     1.7       0
Metadata_2      Yes      No       Yes 
```

As shown, the sample names are omitted from the `metadata_file.tsv`. 
You need to make sure that their corresponding values are in the exact same order as in the `abundance_file.txt`. 
In case the files are not provided like this, microbetag and/or the Docker image of microbetag preprocess, will fail.



{: .important-title}
> ADVANCED USAGE
>
>If you would like to have extra arguments for FlashWeave, then all you need to do is to run the `prep` image interactively and edit the `flashweave.jl` script accordingly (see [below](#the-preparation)). 


### Case 2: you already have a co-occurrence network 

In this case, you need to provide microbetag with both your abundance table and the co-occurrence network file. 
The latter can be of any form if microbetag is performed through the CytoscapeApp.
Otherwise, please make sure you provide the network as an edge file, for instance: 

{: .note}
>ASV_963239	ASV_4372091	0.3769868016242981
>
>ASV_4480529	ASV_4472202	0.4468387961387634
>
>ASV_4472202	ASV_4374302	0.4154910147190094
>
>ASV_4480529	ASV_4439469	0.39721810817718506


### Case 3: you like things the `microbetag` way

To get the optimal annotations in the more robust way, we **strongly suggest** you first prepare your data using the `microbetag_prep` Docker/Singularity image.
That will be almost always the case when you have large datasets with more than a few thousands of sequences and no network for them. 
Yet, even if you have a network, we still **strongly suggest** running the *taxonomy assignment* step, so `microbetag` can map more efficiently the taxa present to their corresponding GTDB genomes. 

Have a look at the ["preparation"](./tutorials/prep.md) section for how to do so! 






