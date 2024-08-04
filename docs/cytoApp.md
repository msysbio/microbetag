---
layout: default
title: Cytoscape App Tutorial
nav_order: 3
---

# `microbetag` on Cytoscape
{: .no_toc }

---

![microbetag CyApp](../assets/images/cyApp.png){: width=25% }



In this page we show how to install and use the microbetag Cytoscape app (called `MGG`) and use it with your data to get `microbetag`-annotated networks 
using the `micrbetagDB` and the online version of `microbetag`.
We also highlight the `MGG` features that allow you to go through the nodes and the edges annotations returned. 


## Table of contents
{: .no_toc .text-delta }

1. TOC
{:toc}



## Run `microbetag` Cytoscape app

To start using *microbetag* you need first, to make sure you have **Cytoscape** on your system; if not, go ahead and [download Cytoscape](https://cytoscape.org/download.html). 
Then, you need to install the *microbetag* app (`MGG`) from [Cytoscape App store](https://apps.cytoscape.org/apps/mgg).
Make sure **you first lunch Cytoscape** and then visit Cytoscape Appstore.
If you have already visited the MGG page on Cytoscape Appstore, **lunch Cytoscape and refresh the Cytoscape Appstore page**.
You should now see an **Install** button.
![mgg install](../assets/images/install_button_mgg.png)
By clicking it, it will be automatically integrated on your Cytoscape. 
If you visit Cytoscape Appstore and you have not lunched Cytoscape, you will see a *Download* button instead of the *Install*.
As already mentioned, we suggest you lunch Cytoscape and refresh the page. 
Otherwise, you can click the **Download** button and move manually the `.jar` file to the apps folder of your Cytoscape.

You can also get `MGG` from within Cytoscape by clicking on the `Apps` tab of the main bar and then `App  Store > Show App Store` and typing `microbetag` on the box that pops up.

Once the app is installed, you may click on the `Apps` tab, and you will find *MGG* there.

![mgg_overall](../assets/images/app/mainMenu.png)



{: .important-title}
> INPUT FILES USED IN THIS TUTORIAL
>
> In this example, we will use the [`testAbund.tsv`][3] file to showcase how to use microbetag without a network being already available.
> 
> In the second case, where a network is already available, we will use the [`vitAbund.tsv`][1] as our abundance file and the [`edgelist.tsv`][2] file as our network file.


From the main menu box, you will have access to all features of the app. 
As you see, the *Get Annotated Network* is currently not a clickable option. 
That is because *microbetag* has no input yet. 

You need first to feed the app with your abundance table and, if available, your co-occurrence network.
In both cases though, the **abundance table** will be **required**. 

Please, make sure your taxonomy fits the criteria for `microbetag` to run. 
You may find more on that issue on the [*Input files*](./input.md#input-files) section.

Then, as you will see in the following two cases, you will have to set the values to a set of parameters to describe your input data but also what annotation steps you would like `microbetag` to perform.


| Variable      | Description                       | Value |
|---------------|-----------------------------------|-------|
|`input_category`| In case you already have a network, set it as `network` and load it; otherwise set it as `abundance_table`. In both cases you need to provide the abundance table though| `abundance_table` \| `network` |
| `taxonomy` | In case a user's taxonomy is to be used, denotes which taxonomy scheme to be used from microbetag | [`GTDB` \| `dada2` \| `qiime2`]
| `phenDB`            | return phenotypic traits based on phen models  | bool |
| `faprotax`          | return annotations using the FAPROTAX database | bool |
| `pathway_complement`| return pathway complementarities between associated nodes | bool |
| `seed_scores`       | return complementarity and cooperation scores based on metabolic reconstructions seed sets | bool |
| `manta`             | return clusters of nodes on the network using the manta package | bool | 
| `get_children`      | use genomes of children taxa of the taxa in the abundance table based on the NCBI Taxonomy scheme | bool |
| `heterogeneous`     | (FlashWeave) enable heterogeneous mode for multi-habitat or -protocol data with at least thousands of samples (FlashWeaveHE)| bool | 
| `sensitive`     | (FlashWeave) enable fine-grained associations (FlashWeave-S, FlashWeaveHE-S), sensitive=false results in the fast modes FlashWeave-F or FlashWeaveHE-F | bool | 









## .. starting from an abundance table

In case that a co-occurrence network is not available, *microbetag* can come up with one using [FlashWeave](https://doi.org/10.1016/j.cels.2019.08.002).

{: .important-title}
> UP LIMIT FOR ABUNDANCE TABLE RECORDS
> 
> When using the online *microbetag* version, it will build a co-occurrence network only for abundance tables with less than 1000 of records.
> In case your abundance table is larger, you will have to run the [`microbetag` preprocess](./tutorials/prep.md) step locally.
> Otherwise, you can always run any algorithm for network inference locally and use their findings with microbetag.


<!-- The on-the fly creation of the co-occurrence network is supported only for abundance tables with **up to 1000 records**.
If your data include more sequencing records, then you will have to use the [`microbetag` preprocess](./tutorials/prep.md) step. -->

Once clicking on *Import Data* you currently see only the *Import Abundance Data* option.

<!-- ![load_data](../assets/images/app/importData.png)  -->
![import_abundance](../assets/images/app/importAbundData.png)


By clicking on it, a pop-up box will ask you to provide your abundance table.
Select it with you mouse and then open it. 

<!-- ![open_data](../assets/images/app/openFile.png) -->
![open_data](../assets/images/app/Open_abund.png)

You can view the imported data by clicking on the *Check Data Files* feature, for the case of the abundance table:

![check_abund_option](../assets/images/app/checkOptionAbundData.png)

Once clicking that, a table will pop up where you can go through the data you have imported as the abundance table. 

<!--  -->

You can now ask for a *microbetag-*annotated network by clicking on the corresponding feature:

![get_annotated_network](../assets/images/app/getaAnnotatedNet.png)

Once clicking on that, a parameter-setting box will pop up, asking for values on a number of parameters **essential** for the successful network inference and their corresponding annotation.

![settings](../assets/images/app/parameters_no_net.png)


Please make sure you set the input type as `abundance_table` and you select the correct [taxonomy scheme](./input.md#input-files).
It is crucial to also set the [FlashWeave related parameters](./faq.md#what-is-sensitive-and-heterogeneous-in-flashweave) in a way they address your abundance table idiosyncrasy.


{: .important}
We suggest you do the network inference step as well as the mapping to the GTDB taxonomy before using *microbetag* through the Cytoscape App as this would provide you extra freedom on they network inference and gain dramatically in computing time on the server.


Once you set the parameters of your choice, you are ready to sent your query to the server by clicking *ok*. 
In this case, we need `microbetag` to come up with a network as we only provide an abundance table; thus, we set the `Choose input type` to `abundance_table`. 
Also, since our taxonomy scheme was Silva we choose this to map our taxa against. 
Last but not least, we set the `Sensitive` parameter as `True` since we have a relatively low number of sequences; 
this way FlashWeave may detect more subtle associations because it considers the full range of abundance variations. 
However, this also makes the computation more intensive and slower, especially with large datasets.
See [FAQ](./faq.md) for more. 

![send_data](../assets/images/app/sendingDataToServer.png)



After a few minutes (based on your data and the steps you have asked for) a *microbetag-*annotated network will pop up automatically on your Cytoscape instance.

![annotated_net](../assets/images/app/annotated_net_no_net.png)


{: .important-title}
> HELP
>
> There are several reasons you may either get a network with only a few nodes/edges annotated or get an error message from the server. 
> Both scenarios are related to either the format of your input data or the parameters you have selected. 
> Please, follow the guidelines you can find in the [*Input files*](./input.md) tab and check our [*FAQ*](./faq.md) for common errors. 
> If you still need some help, please go ahead and ask the `microbetag` community on our [Matrix community](https://matrix.to/#/#microbetagcommunity:matrix.org).



## .. starting from a co-occurrence network

If you already have a network, then you need to provide **both the network and the abundance table** and **make sure that the sequence identifiers in those two files are the same**; 
meaning that the *node ids of the network are present in the abundance table in the column representing the sequence identifier*.

For example, a toy model of a network file would be: 

| node_A | node_B | weight  | 
|:-------:|:-----:|:-------:|
| bin_1 | bin_2 | 0.84 |

then, the corresponding abundance table would have, among other records, to have the following two lines:

| sequenceIdentifier | sample_1 | sample_2| sample_3| taxonomy | 
|:------------------:|:--------:|:-------:|:-------:|:-------:|
|bin_1|  234 | 42 | 43| g__Devosia;s__Devosia sp001899045
|bin_2 | 324| 54 | 43 | g__Pseudonocardia;s__Pseudonocardia sp001899645


{: .note}
> Taxonomy here is only partial. 
> Make sure you always have a 7-level taxonomy, e.g. 
> d__Bacteria;p__Proteobacteria;c__Alphaproteobacteria;o__Rhizobiales;f__Devosiaceae;g__Devosia_A;s__Devosia_A sp001899075


So, this time we will load the [`vitAbund.tsv`][1] file. 
Here how this looks like:

![check_abundance](../assets/images/app/checkAbudanceData.png)


Then, you need to import your network **first** *on Cytoscape* through the main `File` tab:

![import_network](../assets/images/app/loadNetworkFromFile.png)


Cytoscape will display your network and on the bottom of your screen you will have the core tables of a Cytoscape network. 
As your network may have several edges, you need to make clear which edge attribute you would like `microbetag` to use; this is essential in cases network clustering will be performed. 
To do so, you need to move on the *Edge table* by clicking on the arrow next to the *Node table* that is displayed by default, and then **rename** the column of your choice to `microbetag::weight`. 

![rename](../assets/images/app/renameWeight.png)


Now you are ready to import your network *to MGG* though its main menu on the `Apps` tab:

![import_network](../assets/images/app/importNetwork.png)

Finally, you can again check your network as loaded on MGG through the `Check Data Files` tab:

![check_network](../assets/images/app/Loaded_Network_Data.png)



{: .important }
If the node names of the network are not included in the sequence identifiers of the abundance table, you will not be able to import your network to MGG.


Once both your abundance file and your network are imported, you can proceed as in the [*Starting from an abundance table*](cytoApp.md#starting-from-an-abundance-table) case by clicking on `Get Annotated Network` on the main menu of the `MGG` app on the `Apps` tab and setting the parameters required.

![settings](../assets/images/app/inputNet.png)

Make sure that you set the `Choose Input Type` as `network` this time, otherwise `microbetag` will ignore your network and try to build on of their own. 


This will take significantly less time and here is the returned network: 


![annotated_net](../assets/images/app/annotatedNetwork.png)











## *"Roaming"* across annotated nodes and edges

Once an annotated network is returned (or loaded), you have all Cytoscape features (e.g., annotation, filtering, selecting etc.) plus those coming from the microbetag App facilitating a user-friendly way to go through the annotations returned.
We will use the `microbetag`-annogated network of the [last example-case](cytoApp.md#starting-from-a-co-occurrence-network).

Color-coding of the nodes (taxa) denoted the taxonomic level that a certain sequence was able to be mapped on *microbetag*.

- <p style="color : Green">green</p> node was mapped to a genome (i.e. species/strain) and annotations are available for it 
- <p style="color : Magenta">pink</p> node was mapped to the genus level; annotations limited to literature-oriented (FAPROTAX) 
- <p style="color : Purple">purple</p> node was mapped to the family level; likewise, only FAPROTAX annotations occasionaly
- <p style="color : Red">red</p> node was mapped to higher taxonomic level and no annotations were returned


If you edit the style of your *microbetag-*annotated network, you can always bring back its original style through the MGG main menu.

![style](../assets/images/app/visualStyle.png)


By clicking on the *Show Species* button, all nodes that were not mapped to a genome will be masked. 

![show_species](../assets/images/app/showSpecies.png)


Or you can choose/click directly any node on the network and check the `Nodes` Panel 

![selcted_node](../assets/images/app/nodePanel.png)


or several at the same time

![selcted_nodes](../assets/images/app/nodePanelMultiNodes.png)



Further, you may select among a list of annotations under the `PhenDb/FAPROTAX filters` with `AND` and `OR` relationships.
For example, I was curious about the Nitrite-oxidizing bacteria (NOB) on my network

![NOB](../assets/images/app/NOB.png)



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

![pathway_compl](../assets/images/app/pathwayCompl.png)

In the final column a link to a related KEGG map is provided where KO available in the beneficiary species are colored with pink and those provided by the donor in the scenario of the potential metabolic interaction with green.
The screenshot below illustrates the highlighted complementarity in the biosynthesis of methionine.

![methionine_kegg_map](../assets/images/app/keggMap.png)



Moreover, *microbetag* may also return seed complements. 
Like in the case of the pathway complementarities, a new panel is displayed when seed complements are available for an edge.
Here is an example:

![kegg_seed_map](../assets/images/app/seedComplPanel.png)


[*Seed scores*](./modules/modules.md#seed-scores-based-on-genome-scale-draft-reconstructions-gems) between the two genomes are also shown here. 
Remember that like the edge under study, seed scores have also *directionality*; seed score for competition between $genome_A$ and $genome_B$ is not necessarily the same with the one between $genome_B$ and $genome_A$.
Those scores are only indicative, and they should not be considered as fact of observed cooperation/competition. 
Seed complements are then recorded in the same way as pathway complementarities.
However, there is no *Complement* column as this time it is not a specific KEGG MODULE that is supported, rather a potential range of functions that can be viewer through the colored url. 
Also, a new column provides the ModelSEED compound id that was actually found as a complement and was then mapped to their KEGG corresponding one. 

![kegg_seed_map](../assets/images/app/seedKeggMap.png)



[1]:{{ site.url }}/microbetag/download/vitAbund.tsv
[2]:{{ site.url }}/microbetag/download/edgelist.tsv
[3]:{{ site.url }}/microbetag/download/testAbund.tsv


<!-- 
To check 


Sensitive vs fast mode
• Implementation of
conditional independence:
– Sensitive mode: partial
correlations on abundances,
assumes multivariate normal
distribution (weak assumption)
– Fast mode: mutual information
on presence/absences


HE mode
• FlashWeave can optionally ignore
zeros (‘structural zeros’) to deal
with heterogeneous samples 


multi-habitat or -protocol data sets with ideally at least thousands of samples;

sensitive=false for faster, but more coarse-grained associations

## example
Here we need a step-by-step with screenshots and/or videos of the features of 
 -->
