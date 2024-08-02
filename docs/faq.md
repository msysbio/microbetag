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


## I fail getting an annotated network even my input files are in the right format and my parameters are well-tuned

This may be caused because of the time limit of our server for a single run. 
Thus, there are cases for which even the number of sequence identifiers is less than 1000, combinations of other factors can lead to time-consuming runs, causing an error in the end. 
For example, you have set taxonomy to `other` and you have also chosen `sensitive` as a parameter for the network inference. 
Such a scenario can easily lead to time-errors. 
In this case, you should first run the [`microbetag-prep`](./tutorials/prep.md) step and use its output as your input files. 



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




