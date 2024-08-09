# microbetag: microbetagDB


`microbetag` is a software ecosystem for annotating microbial co-occurrence networks. 

In this repository you may find:

- in the current `develop` branch, the precalculation steps/scripts to build `microbetagDB`
- in the [`preprocess`](https://github.com/hariszaf/microbetag/tree/preprocess) branch, the `microbetag`-preprocessing stand-alone tool, provided as a Docker image
- in the [`user-bins`](https://github.com/hariszaf/microbetag/tree/user-bins) branch, a stand-alone version of microbetag to use with custom genomes, instead of mapping taxa to the GTDB representative genomes, provided as a Docker image too
- in the [`gh-pages`](https://github.com/hariszaf/microbetag/tree/gh-pages) branch, we build the `microbetag` documentation page

For tutorials on how to use the different parts of the `microbetag` software ecosystem, please go through our [documentation website](https://hariszaf.github.io/microbetag/).

## microbetagDB

In the `develop` branch of this repo, you may find how we came up with the `microbetagDB`. 

`microbetagDB` consists of 34,608 high-quality [Genome Taxonomy DataBase](https://gtdb.ecogenomic.org) genomes, along with their corresponding KEGG annotations and genome-scale metabolic reconstructions. 
*Seed sets* (externally acquired compounds) were retrieved from the latter, supporting the prediction of over 1 billion potential pairwise metabolic interactions. 
Relying on KEGG MODULE definitions, 342,000 unique pathway complements were identified based on pairwise overlaps between the annotated genomes. 
In addition, 33 phenotypic traits (e.g., pH optima, oxygen tolerance etc.) were predicted for the annotated genomes and incorporated in `microbetagDB`. 

`microbetag` maps node taxonomies to their closest genome in `microbetagDB` and annotates them with phenotypic traits and functional potential derived from the literature. 
Edges are then annotated with pathway complements and seed complementarities that may represent cross-feeding relationships.



## Graphical User Interphase (GUI)

To visualise `microbetag`-annotated networks but also to perform `microbetag` for simple cases without any need of running something locally, we provide a 
[Cytoscape app](https://apps.cytoscape.org/apps/mgg). 

The source code for the microbetag GUI can be found [here](https://github.com/ermismd/MGG).


## Contact

For hints on how to use `microbetag`, ideas for new features and bug reports find us on out [Matrix space](https://matrix.to/#/#microbetagcommunity:matrix.org).
If you do not have a Matrix account, it’s only two clicks away! For more, you may check [here](https://matrix.org/docs/chat_basics/matrix-for-im/).


## Cite

In prep.


## Funding

This project is funded by an [EMBO Short-Term Fellowship](https://www.embo.org/funding/fellowships-grants-and-career-support/scientific-exchange-grants/) and 
the [3D’omics](https://3domics.eu) Horizon project (101000309).

## License

*microbetag* is under [GNU General Public License v3.0](https://opensource.org/license/gpl-3-0). For third-party components separate licenses apply. The MGG CytoscapeApp is under [Apache License, Version 2.0](https://opensource.org/license/apache-2-0).