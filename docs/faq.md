---
layout: default
title: FAQs
nav_order: 7
description: "Frequently Asked Questions on how to use and interprete microbetag"
---

# Frequently Asked Questions
{: .no_toc }


## Table of contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---


## I can't get an annotated network, despite having correct input files and well-tuned parameters

This may be caused because of the time limit of our server for a single run. 
Thus, there are cases for which even the number of sequence identifiers is less than 1000, combinations of other factors can lead to time-consuming runs, causing an error in the end. 
For example, you have set taxonomy to `other` and you have also chosen `sensitive` as a parameter for the network inference. 
Such a scenario often leads to time-errors. 
In this case, you should first run the [`microbetag-prep`](./tutorials/prep.md) step and use its output as your input files. 
Also, you may have a short number of taxa but a vast amount of samples. 
In this case, you will also get a time error in case you enable the `sensitive` parameter of FlashWeave.
It is always a good practice to run the preparation step locally, so you also have a better overview of the network you will then ask `microbetag` to annotate. 
Remember that `microbetag` focus is in annotating a network, not building one. 

## Frozen `Sending data to server` pop-up

In cases where a time error has occurred, we have observed that from time to time the pop-up box with the progress of your query keeps showing that your data are in process.
If that happens, you need to kill the process of the Cytoscape instance.
For example, in a Linux system, you would have to check on your `htop` panel which is the `PID` for Cytoscape and then run `kill <PID>`.


## GTDB versioning

GTDB releases a new version once a year, most of the time in April increasing its number of genomes to a great extent from version to version. 
Yet, the number of high quality genomes is not increasing that fast.
In addition, as the number of high quality genomes increases, the pairs for `microbetagDB` to store increases exponentially. 
Thus, every year, `microbetag` makes sure it integrates the new genomes that are members of the genome clusters already there. 
Yet, new calculations will be performed only once a finer way to store the billions of complements is developed.


## What is sensitive and heterogeneous in FlashWeave? 

![four_cases](../assets/images/flashweave_cases.png)

heterogeneity of these cross-study data sets, such as variation in habitats, measurement conditions, and sequencing technology, can lead to confounding associations, typically not addressed by current methods

Sensitive modes (`-S`) of FlashWeave uses full abundance information ("continuous"), while fast modes (`-F`) work on discretized abundances. In contrast to FlashWeave, FlashWeaveHE excludes samples in which one partner is absent (colored gray). 
However, it still includes absences of OTUs within the conditioning sets.

Meta variables (MVs) are by default not normalized for FlashWeave-S and FlashWeaveHE-S and should thus, if necessary, be provided in a sensible pre-normalized format by the user. 
For FlashWeave-F and FlashWeaveHE-F, continuous meta-variables are by default discretized into two bins separated by their median.


## How to choose a taxonomy scheme ? 

For microbetag to return the best annotations it could come up with, it is essential to map as best as possible the sequences described in your abundance table to
corresponding GTDB genomes. 
There are 4 taxonomy schemes supported:
- `GTDB`: in case you have used GTDB-tk to taxonomically annotate your bins
- `Silva`: in case you have used DADA2 along with the 7-level version of Silva they support
- `microbetag_prep`: in case you have amplicon data and would like to use our implementation for mapping your OTUs/ASVs to GTDB genomes directly by using the `idataxa` algorithm of the DECIPHER package and the 16S genes of the GTDB genomes as a reference database. For large datasets (>1000 sequences) see also 
- `other`: in case you want to use your taxonomies and get the closest NCBI Taxonomy names included in the microbetagDB (using the `fuzzywuzzy` Python library)


<!-- ## Why using the `get_children` feature? 

## Positive associations with high competitions seed score ?  -->




## How to read a KEGG map with pathway complementarities ? 

Complementarities need to always be considered as **potential**.
There is no evidence that just because a complementarity could be occurring based on the genomes of a species pair that is actually happening. 
To argue about such a case, one would have to get experimental data. 

Regarding the pathway complementarities, one need to consider that one pathway does not take into account what is happening to the others. 
Thus, in cases where both $$ pathway_A $$ and $$ pathway_B $$ perform processes that come up with the same end-products, and $$ species_A $$ has a complete alternative for 
$$ pathway_A $$ but not for $$ pathway_B $$ and $$ species_B $$ could potentially complete $$ pathway_B $$, then `microbetag` would return this potential complementarity, 
even if it is not necessary for $$ species_A $$ as it gets what it needs on its own, using $$ pathway_A $$.

The number of the KOs required for a complementarity to happen (number of KO in the `Complement` column) is also indicative for its likelihood. 
If only one KO term needs to be provided by the donor species to the beneficiary, complementarity is more likely to occur compared to a situation where several KOs are required. 
Also, in case there are also *seed complementarities* available for a species pair, you can combine information from both types of complementarities. 
If a *seed* is close to the pathway mentioned from your pathway complementarities, this adds some extra confidence for the latter to occur. 



## I am trying to run `microbetag` locally, but.. 

When running `microbetag` locally (see [relative tutorial](./tutorials/local.md)) one may have a wide range of different input files as starting points.
You may start with nothing but your bins; i.e., sequencing files, one for each bin mentioned in your abundance table. 
Otherwise, you may have already annotated them with KEGG ORTHOLOGY terms. 
You may as well have reconstructed GEMs on your own already. 
You can adapt your `microbetag` run by pointing to these files through the [`config.yml`](https://github.com/hariszaf/microbetag/blob/user-bins/tests/dev_io_microbetag/config.yml) file you have to provide as input.
However, we cannot say for sure that no matter the software you used to annotate for example your bins will suit what `microbetag` expects.
If you have a large number of bins, and you would prefer to avoid annotating them again using `microbetag` this time, you may check the format of the annotations provided in the example case and see if you can edit your format to that. 
In any case, we strongly suggest you reach out the [`microbetag`'s community on Matrix](https://matrix.to/#/#microbetagcommunity:matrix.org) with any specific questions of yours.


## I have a really large 16S-oriented network. What can I do? 

There are three things you could do in this case.
First, you can try to build a database with the closest genomes you can find for the strains present in you data. 
If you do so, then you could run `microbetag` locally using those genomes as they were your bins. 

Second, you could build a local instance of `microbetagDB` locally. 
This would require a storage of $$ ~700GB $$.
<!-- REMEMBER! Edit next phrase once coplete -->
We are now working on an efficient way to go for that. 

Third, you can get the annotations per species pairs using the `microbetag` API. 
However, in this case, you will not have a `.cx` file as an end product, i.e. you will not have a single file you can then load on Cytoscape and view through the `MGG` features. 


## Reconstructing GEMs locally 

There is a great chance when you are trying to reconstruct Genome Scale Models (GEMs) using your own genomes/bins/MAGs and the `modelseedpy` library, as shown in the relative [tutorial](./tutorials/local.md), to keep getting messages like:
```bash
Recursive run for model_id: /data/my_faa/bin_101
```
This can lead to excessive time, especially as the number of your genomes increases.
This is because `modelseedpy` requires RAST annotated genomes and thus it needs to establish a connection to the RAST server.
Unfortunately, we have observed that this is not always stable.



