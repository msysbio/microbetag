---
layout: default
title: Input files
nav_order: 6
---

# Input files and mandatory parameters

Here is a list with `microbetag` input files along with typical examples of how they need to be like:

| File            | Description                                                    | requirement_status        |
|-----------------|----------------------------------------------------------------|---------------------------|
| abundance table | An abundance table (in `.tsv` or `.csv` format) ([example][1]) | mandatory                 | 
| metadata file   | File describing the sequencing data ([example][2])             | optional; using FlashWeave| 
| network file    | A 3-column edge list ([example][3])                            | optional                  |


## Abundance table

Please, make sure in case you provide your abundance table as a `.tsv` or `.csv` file where: 
- in the **first column** you have always the **sequence identifier**
- in the **first row** the **samples names** 
- in the **last column** you keep a complete **7-level taxonomy**

```{warning} 
Do not use numeric characters only for labeling your samples and/or the sequences mentioned in your abundance table. 
For example, `324` as a sample id will lead microbetag to fail. 
```

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

```{note}
You may notice that the `GTDB_tax_assigned_abundance_table.tsv` abundance table returned by `microbetag_prep` has an 8-level taxonomy (including a `Root` level)
That is why you need to make sure you denote `microbetag_prep` as the taxonomy database in the parameters settings, otherwise `microbetag` will fail.
```

```{warning}
**Taxonomy curation**

If you have a taxonomy scheme that "skips" a level, or another one that has more levels, microbetag will either return **fewer annotations** or **fail**.
You need to make sure you always have a 7-level scheme for all the entries on your table and that the species/strain level if available is in the 7th field.
Again, it is always a good practice to use the [`microbetag` preparation step](../advanced_use/prep.md) to get the most suited taxonomies for `microbetag`
```


### The `phyloseq` case

In case you start from a `phyloseq` object, you may get a `.tsv` file using the 
<a href="https://www.rdocumentation.org/packages/phyloseq/versions/1.16.2/topics/tax_table" target="_blank">`tax_table`</a> and the
<a href="https://www.rdocumentation.org/packages/phyloseq/versions/1.16.2/topics/otu_table" target="_blank">`otu_table`</a> 
functions of the `phyloseq` library. 

```R
# In an R environment, assuming `physeq` is a `phyloseq` object.
OTU_TAX <- cbind(
   data.frame(otu_table(physeq)), 
   data.frame(tax_table(physeq))
)
write.table(OTU_TAX, "OTU_TAX.txt", 
            row.names = TRUE, col.names = TRUE, sep = "\t", quote=FALSE)
```


### The `.biom` case

In case you start from a `biom` file, you may get a `.tsv` file using the 

```bash 
biom convert -i otu_table.biom -o otu_table.csv --to-tsv --header-key taxonomy
```
Make sure you have the `biom` tools installed; if not, you may follow the instructions you can find 
<a href="https://biom-format.org/index.html" target="_blank">here</a>
how to get them.
<!-- https://www.metagenomics.wiki/tools/16s/qiime/otu-biom-table -->



```{important}
To get the optimal annotations in the more robust way, we **strongly suggest** you first prepare your data using the `microbetag_prep` Docker/Singularity image.
That will be almost always the case when you have large datasets with more than a few thousands of sequences and no network for them. 
Yet, even if you have a network, we still **strongly suggest** running the *taxonomy assignment* step, so `microbetag` can map more efficiently the taxa present to their corresponding GTDB genomes. 

Have a look at the ["preparation"](../advanced_use/prep.md) section for how to do so! 
```


### Running `microbetag_prep` 

In case you are about to use the `microbetag_prep` to taxonomically assign your OTUs/ASVs using GTDB, your abundance table file should be exactly as before only this time, in the last column, 
instead of having a 7-level taxonomy, you need to provide the sequence. 

[Here][4] is an example file.



## Metadata file
 
FlashWeave, the software `microbetag` invokes to build the co-occurrence network, can exploit metadata.
If you want to run FlashWeave with a metadata file, you need to remember that FlashWeave considers as variables both the sequence ids (i.e., ASVs/OTUs/bins) and the metavariables (e.g. pH, sex, any variable on your metadata file). 
Thus, you need to provide them as **rows**, contrary to what we do in most microbiome analyses.

Here is a toy example of how your files should look like: 

- `abundance_file.txt`

|seqId  |  sample_1  |  sample_2  |  sample_3 |
|:-----:|:----------:|:----------:|:---------:|
|asv_1  |  10   |     0   |     3|
|asv_2  |   0   |    21   |    43|
|asv_3  |  32   |    31   |     2|
|asv_4  |   0   |     0   |    12|

- `metadata_file.tsv`


```{list-table}
:widths: auto
:header-rows: 0

* - Metadata_1
  - 0.2
  - 1.7
  - 0
* - Metadata_2
  - Yes
  - No
  - Yes
```

As shown, the sample names are omitted from the `metadata_file.tsv`. 
You need to make sure that their corresponding values are in the exact same order as in the `abundance_file.txt`. 
In case the files are not provided like this, microbetag and/or the Docker image of microbetag preprocess, will fail.



<!-- {: .important-title}
> ADVANCED USAGE
>
>If you would like to have extra arguments for FlashWeave, then all you need to do is to run the `microbetag_prep` image interactively and edit the `flashweave.jl` script accordingly. -->



## Network file

There is a great range of formats for networks. 
When you are using `microbetag` through Cytoscape then, to the best of our knowledge, you can start from any network format of your choice.
That is because you first import then network on Cytoscape and only then you load it on the `MGG` app that will allow its transferring to the `microbetag` server. 

```{note}
Make sure to rename the column `microbetag` should treat as the weight of your edges to `microbetag::weight` (see relative [tutorial](load.md#load-already-microbetag-annotated-networks)).
```

However, in case you are using `microbetag` locally, and you already have a network to annotate, then you will have to provide it as a 3-column file (see [example file][2]):

| node_a |  node_b | microbetag::weight | 
|:------:|:--------:|:-----------------:|
|ASV_963239	 | ASV_4372091 | 0.3769868016242981
|ASV_4480529 | ASV_4472202 | 0.4468387961387634
|ASV_4472202 | ASV_4374302 | 0.4154910147190094
|ASV_4480529 | ASV_4439469 | 0.39721810817718506

```{note}
Cytoscape asks for a `source` and a `target` column in your network. 
Since a co-occurrence network does not have directed edges, you can set any node column as `source` or `target`.
In our example, `node_a` could be `source` and then, `node_b` would be the `target` or the other way around. 
```





## Basic parameters


You need first to feed the app with your abundance table and, if available, your co-occurrence network.
In both cases though, the **abundance table** will be **required**. 

Please, make sure your taxonomy fits the criteria for `microbetag` to run. 
You may find more on that issue on the [*Input files*](../input.md#input-files) section.

Then, as you will see in the following two cases, you will have to set the values to a set of parameters to describe your input data but also what annotation steps you would like `microbetag` to perform.


|Parameter | Variable      | Description                       | Value |
|----------|---------------|-----------------------------------|-------|
|Choose input type         |`input_type`| In case you already have a network, set it as `network` and load it; otherwise set it as `abundance_table`. In both cases you need to provide the abundance table though| [`abundance_table` \| `network`] |
|Choose taxonomy database| `taxonomy` | In case a user's taxonomy is to be used, denotes which taxonomy scheme to be used from microbetag | [`GTDB` \| `dada2` \| `qiime2`] |
|phenDB annotations         | `phen_traits`            | return phenotypic traits based on phen models  | bool |
|FAPROTAX annotations       | `faprotax`          | return annotations using the FAPROTAX database | bool |
|Pathway Complementarity    | `pathway_complementarity`| return pathway complementarities between associated nodes | bool |
|Seed scores and complements| `seed_complementarity`       | return complementarity and cooperation scores based on metabolic reconstructions seed sets | bool |
|Network clustering         | `network_clustering`             | return clusters of nodes on the network using the manta package | bool | 
|Consider children taxa     | `get_children`      | use genomes of children taxa of the taxa in the abundance table based on the NCBI Taxonomy scheme, relevant only if you use `Other` taxonomy | bool |
|heterogeneous              | `heterogeneous`     | (FlashWeave) enable heterogeneous mode for multi-habitat or -protocol data with at least thousands of samples (`FlashWeaveHE`) | bool | 
|sensitive                  INPUT FILES USED IN THIS TUTORIAL| `sensitive`         | (FlashWeave) enable fine-grained associations (`FlashWeave-S`, `FlashWeaveHE-S`), sensitive=false results in the fast modes `FlashWeave-F` or `FlashWeaveHE-F` | bool | 


The column `Variables` in the above table provides the variable names you need to use 
in case you are about to use `microbetag` from Python (see [tutorial](../tutorials_local/python.md)).

The datasets to be used in all cases except of the [*Using a network*](../tutorials_otf/from_net.md) tutorial, 
are subsets of abundance tables with no special biological meaning.
However, in the *Using a network* case, we do use the network of 
Hessler et *al.* (2023) {cite:p}`hessler2023vitamin` who we would like to thank for sharing their data.










[1]:../_static/download/mgg/testAbund.tsv
[2]:../_static/download/mgg/metadata.tsv
[3]:../_static/download/mgg/edgelist.tsv
[4]:../_static/download/prep/seq_ab_tab.tsv

