---
layout: default
title: Additional tutorials
nav_order: 4
has_children: true
usemath: true
---

# Additional tutorials

To use `microbetag` there are two main approaches: 
* with `microbetagDB` through Cytoscape; in this case, your taxa will be mapped to a GTDB representative genome if possible and pre-calculations will be used for the annotation step. However, if you have an abundance table with more than 1000 sequences, you will have to provide a network. 
To enable this and at the same time to support the taxonomy annotation of 16S rRNA sequences directly with GTDB, if that is your case, we provide a containerized image, called [`microbetag_prep`](https://hub.docker.com/r/hariszaf/microbetag_prep), for what the [*preparation step*](./prep.md). This is only required if you have more than 1000 sequences and your taxonomy is neither Silva nor GTDB.
* applying the `microbetag` workflow to your own bin/MAGs [locally](./local.md) and then visualize the annotated network through Cytoscape; in this case, you will use another [Docker/Singularity image](https://hub.docker.com/r/hariszaf/microbetag) we provide to annotate your genomes locally. This, based on the number of genomes/MAGs you have, may take several hours and thus, cannot be performed on-the-fly as a web-service, so you will have to run it locally. Once you get the annotated network, then you can use the CytoscapeApp we provide to visualize it. 


The simplest case is you are about to use the first approach where your sequences are less than 1000 (up limit for the server to build a network).
In this case, you may follow directly the instructions described in the [Cytoscape tutorials](../mgg_tutorials/mgg_totorials.md). 
If you have a more complex data set, then you need to:
* either perform the `microbetag_prep` step, where you get a network again using FlashWeave and/or a GTDB-based taxonomy assignment of your amplicon sequences (if that is your case), or
* perform `microbetag` locally, in case you have your own genomes to use instead of the GTDB representative ones


> In the *Advanced use*, we provide tutorials addressing common cases where more sophisticated implementations of the `microbetag` features are required to get an annotated network. 

For any issues, bugs, questions, feel free to contact us on [Matrix](https://matrix.to/#/#microbetagcommunity:matrix.org) or 
just open an issue on our [GitHub repo](https://github.com/msysbio/microbetagApp-public/issues/new).



```{toctree}
:maxdepth: 2
:caption: Tutorials - advanced use

prep
local
large_data
python

