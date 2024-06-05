# microbetag

`microbetagDB` consists of 34,608 high-quality [Genome Taxonomy DataBase](https://gtdb.ecogenomic.org) genomes, along with their corresponding KEGG annotations and genome-scale metabolic reconstructions. 
*Seed sets* (externally acquired compounds) were retrieved from the latter, supporting the prediction of over 1 billion potential pairwise metabolic interactions. 
Relying on KEGG MODULE definitions, 342,000 unique pathway complements were identified based on pairwise overlaps between the annotated genomes. 
In addition, 33 phenotypic traits (e.g., pH optima, oxygen tolerance etc.) were predicted for the annotated genomes and incorporated in `microbetagDB`. 

`microbetag` maps node taxonomies to their closest genome in `microbetagDB` and annotates them with phenotypic traits and functional potential derived from the literature. 
Edges are then annotated with pathway complements and seed complementarities that may represent cross-feeding relationships.


In this repository you may find:

- in the current `develop` branch, the precalculation steps/scripts to build `microbetagDB`
- in the [`preprocess`](https://github.com/hariszaf/microbetag/tree/preprocess) branch, the microbetag-preprocessing stand-alone tool, provided as a Docker image
- in the [`user-bins`](https://github.com/hariszaf/microbetag/tree/user-bins) branch, a stand-alone version of microbetag to use with custom genomes, instead of mapping taxa to the GTDB representative genomes, provided as a Docker image too


For tutorials on how to use the different parts of the `microbetag` software ecosystem, please go through our [documentation website](https://hariszaf.github.io/microbetag/).
For any issues, feel free to [open an issue](https://github.com/hariszaf/microbetag/issues/new) here on GitHub or contact us on the [Matrix microbetag community](https://matrix.to/#/#microbetagcommunity:matrix.org).

## Graphical User Interphase (GUI)

To visualise `microbetag`-annotated networks but also to perform `microbetag` for simple cases without any need of running something locally, we provide a 
[Cytoscape app](https://apps.cytoscape.org/apps/mgg). 

The source code for the microbetag GUI can be found [here](https://github.com/ermismd/MGG).

## Funding

This project is funded by an [EMBO Short-Term Fellowship](https://www.embo.org/funding/fellowships-grants-and-career-support/scientific-exchange-grants/) and 
the [3D’omics](https://3domics.eu) Horizon project (101000309).
