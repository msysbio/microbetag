---
title: Investigating the annotations
layout: default
parent: Cytoscape tutorials
nav_order: 4
description: "tutorial on how to parse the annotated network using the MGG app"
---


## *"Roaming"* across annotated nodes and edges

Once an annotated network is returned (or [loaded](../tutorials/load.md)), you have all Cytoscape features (e.g., annotation, filtering, selecting etc.) plus those coming from the microbetag App facilitating a user-friendly way to go through the annotations returned.
We will use the `microbetag`-annogated network of the 
[last example-case](./from_net.md).

Color-coding of the nodes (taxa) denoted the taxonomic level that a certain sequence was able to be mapped on *microbetag*.

- <p style="color : Green">green</p> node was mapped to a genome (i.e. species/strain) and annotations are available for it 
- <p style="color : Magenta">pink</p> node was mapped to the genus level; annotations limited to literature-oriented (FAPROTAX) 
- <p style="color : Purple">purple</p> node was mapped to the family level; likewise, only FAPROTAX annotations occasionaly
- <p style="color : Red">red</p> node was mapped to higher taxonomic level and no annotations were returned


If you edit the style of your *microbetag-*annotated network, you can always bring back its original style through the MGG main menu.

![style](../../assets/images/app/visualStyle.png)


By clicking on the *Show Species* button, all nodes that were not mapped to a genome will be masked. 

![show_species](../../assets/images/app/showSpecies.png)


Or you can choose/click directly any node on the network and check the `Nodes` Panel 

![selcted_node](../../assets/images/app/nodePanel.png)


or several at the same time

![selcted_nodes](../../assets/images/app/nodePanelMultiNodes.png)



Further, you may select among a list of annotations under the `PhenDb/FAPROTAX filters` with `AND` and `OR` relationships.
For example, I was curious about the Nitrite-oxidizing bacteria (NOB) on my network

![NOB](../../assets/images/app/NOB.png)



Likewise, you may go through the annotations on the edges of the network.

<!-- <p style="color: rgb(135,206,235)">Welcome to freeCodeCamp!</p> -->
Edges are either
 - <p style="color : Green">green</p> mentioning co-occurrences
 - <p style="color : Red">red</p> suggesting mutual exclusion of the two taxa
 - <p style="color : Black">black</p> representing ***directed*** potential metabolic interactions. 



One may select from the two top buttons on the `Edges` panel to show only edges with pathway complementarities or seed complementarities.


By clinking on a potential metabolic interaction edge, 
the donor and the beneficiary species, along with their corresponding sequence identifiers will be displayed
highlighting who potentially benefits from the other.

Then, for cases where pathway complementarities have been returned for this association, a panel will be available for each pair of genomes that were mapped to those two taxa. 
For each pair of genomes, a list with the potential metabolic complementarities is then returned. 
In the first column the KEGG MODULE id of the corresponding complementarity is provided, and in the second and third column their description and metabolism category. 
In the fourth column, called *"Complement"* the KO that need to be provided to the beneficiary species to support the module are given and in the next column, the complete alternative that would then facilitate the module is shown; i.e., assuming the complement is provided.

![pathway_compl](../../assets/images/app/pathwayCompl.png)

In the final column a link to a related KEGG map is provided where KO available in the beneficiary species are colored with pink and those provided by the donor in the scenario of the potential metabolic interaction with green.
The screenshot below illustrates the highlighted complementarity in the biosynthesis of methionine.

![methionine_kegg_map](../../assets/images/app/keggMap.png)



Moreover, *microbetag* may also return seed complements. 
Like in the case of the pathway complementarities, a new panel is displayed when seed complements are available for an edge.
Here is an example:

![kegg_seed_map](../../assets/images/app/seedComplPanel.png)


[*Seed scores*](../modules/modules.md#seed-scores-and-complements-based-on-genome-scale-draft-reconstructions-gems) between the two genomes are also shown here. 
Remember that like the edge under study, seed scores have also *directionality*; seed score for competition between $genome_A$ and $genome_B$ is not necessarily the same with the one between $genome_B$ and $genome_A$.
Those scores are only indicative, and they should not be considered as fact of observed cooperation/competition. 
Seed complements are then recorded in the same way as pathway complementarities.
However, there is no *Complement* column as this time it is not a specific KEGG MODULE that is supported, rather a potential range of functions that can be viewer through the colored url. 
Also, a new column provides the ModelSEED compound id that was actually found as a complement and was then mapped to their KEGG corresponding one. 

![kegg_seed_map](../../assets/images/app/seedKeggMap.png)



