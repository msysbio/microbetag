---
layout: default
title: Tutorials
nav_order: 6
has_children: true
permalink: /docs/tutorialas
usemath: true
---

# Tutorials

To use `microbetag` there are two main approaches: 
* with `microbetagDB` through Cytoscape; in this case, your taxa will be mapped to a GTDB representative genome if possible and pre-calculations will be used for the annotation step. However, if you have an abundance table with more than 1000 sequences, you will have to provide a network. 
To enable this and at the same time to support the taxonomy annotation of 16S rRNA sequences, if that is your case, directly with GTDB, we provide a Docker for what we call *preparation step*. This is only required if you have more than 1000 sequences and your taxonomy is neither Silva nor GTDB.
* applying the `microbetag` workflow to your own bin/MAGs locally and then visualize the annotated network through Cytoscape; in this case, you will use a Docker/Singularity image we provide to annotate your genomes locally. This, based on the number of genomes/MAGs you have, may take several hours and thus, cannot be performed on-the-fly as a web-service, so you will have to run it locally. Once you get the annotated network, then you can use the CytoscapeApp we provide to visualize it. 

 

Here, we provide two tutorials, one for each case:
* [`microbetag` on-the-fly](./on_the_fly.md), and 
* [`microbetag` locally](./local.md)

For any issues, bugs, questions, feel free to contact us on [Matrix](https://matrix.to/#/#microbetagcommunity:matrix.org) or just open an issue on our [GitHub repo](https://github.com/msysbio/microbetagApp/issues).

