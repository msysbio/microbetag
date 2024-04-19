---
layout: default
title: Tutorials
nav_order: 6
has_children: true
permalink: /docs/tutorialas
usemath: true
---



To use `microbetag` there are two main approaches: 
* using it with `microbetagDB` through Cytoscape
* applying the `microbetag` workflow annotation to your own bin/MAGs locally and then visualize the annotated network through Cytoscape


In the first case, if you have an abundance table with more than 1000 sequences, you will have to provide a network. 
To enable this and at the same time to support the taxonomy annotation of 16S rRNA sequences, if that is your case, directly with GTDB, we provide a Docker for what we call *preparation step*. This is only required if you have more than 1000 sequences and your taxonomy is neither Silva nor GTDB. 

Here, we provide two tutorials, one for each case:
* [`microbetag` on-the-fly](), and 
* [`microbetag` locally]()

For any issues, bugs, questions, feel free to contact us on [Matrix](https://matrix.to/#/#microbetagcommunity:matrix.org) or just open an issue on our [GitHub repo](https://github.com/msysbio/microbetagApp/issues).

