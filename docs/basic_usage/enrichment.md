---
title: Enrichment analysis
layout: default
parent: Basic usage
nav_order: 4
description: "how to perform an enrichment test on MGG"
---


Enrichment analysis 
===================

The `MGG` Cytoscape App of ours enables enrichment/depletion analysis of the `microbetag` annotated network 
at the nodes level. 
This means that you can test whether the nodes (taxa) of a cluster are enriched with phenotypic traits assigned to them based on
[phendb models](../modules/phen-traits.md), and or [FAPROTAX](../modules/faprotax-functions.md).

In this tutorial, we use the *microbetag*-annotated network derived from the example case for [running *microbetag* with big datasets](../advanced_use/large_data.md).

After performing `microbetag` having enabled the network clustering step (using `manta`), you end up with a network that 
besides the FAPROTAX and phenDB-like annotations, it also includes a `manta::cluster` column.

![cols](../_static/img/app/enrichment/manta_columns.png)

[`manta`](https://github.com/ramellose/manta) uses a diffusion-based proccess to carry out network clustering, and you may find 
more on how it works and its findings at this [demo case](https://ramellose.github.io/manta/demo_manta.html). 
However, there is a great range of network clustering algorithms you could go for. 

Once you cluster your network, each node will be assigned to a cluster. 
To proceed to the `MGG` enrichment/depletion analysis, you need to **rename** your cluster-assigned column so it is under the `microbetag` namespace.
For example, assuming you wish to use the `manta` clusters as returned from running `microbetag`, you would rename the `manta::cluster` column (as shown in the figure above), to `microbetag::cluster`. 

![rename-cols](../_static/img/app/enrichment/rename_col.png)



```{image} ../_static/img/app/enrichment/rename_col.png
```

This means that 


 


https://qiita.ucsd.edu/study/description/1928








