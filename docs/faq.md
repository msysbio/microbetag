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


