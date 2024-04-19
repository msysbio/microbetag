---
title: load networks to Cytoscape and use them with microbetag
layout: default
parent: Tutorials
nav_order: 2
description: "an example case of how to load a previously microbetag-annotated network on cytoscape"
---


# Load networks to Cytoscape to use them with `microbetag`


## ..coming from the preparation step

The preparation step should have provided you with the `GTDB_tax_assigned_abundance_table.tsv` and/or the `network_output.edgelist` files. 
Now, we can get those two files returned and jump into Cytoscape. 
Open Cytoscape and then click on `File > Import > Network from file` and browse on the pop-up box to your `network_output.edgelist` file. 

You will then see another pop up box like this: 

![init](../../assets/images/app/prep_import_Network.png) 

Cytoscape needs always to have a *source* and a *target* node, even in cases of undirected graphs, such as the co-occurrence networks.
Therefore, click on the first two column headers and set one as the source and the other as the target by clicking on the corresponding symbols: 

![source](../../assets/images/app/source.png)

![target](../../assets/images/app/target.png)


Finally, you need to always set the column that `microbetag` will consider as your weight column, in this case, we have only one column with a weight however in cases that a network is not built like that, may have several. 
Thus, you need to click on the corresponding column header and set it as `microbetag::weight`.
Now `microbetag` is able to recognize which column to handle as the *weight* of your network.
By clicking `OK` your network will be shown on Cytoscape's main panel. 

![weight](../../assets/images/app/weight.png)

Now you are ready to import your abundance table. 
Go to `Apps > MGG > Import Data > Import Abundance Data` and browse to the `GTDB_tax_assigned_abundance_table.tsv` file returned from the `microbetag_prep` running.
Load the network data to the app by clicking `Apps > MGG > Import Data > Import Current Network`.

{: .note}
> The order here is important! `microbetag` will not allow you to import first your network and then your abundance table. 

You can check on the imported date by clicking `Apps > MGG > Import Data > Check Data Files`.
Once you make sure you have loaded what you wanted, you are ready to ask `microbetag` to annotate your network! 
Just click `Apps > MGG > Get Annotated Network`.
Set the parameters as discussed in the [*Run `microbetag` from a co-occurrence network*](../cytoApp.md#starting-from-a-co-occurrence-network) section.

![params](../../assets/images/app/prepSettings.png)


Then, click `OK`. 
Then a *Sending data to the server* loading bar will appear. 
After a few moments, a new network will pop up on your Cytoscape main panel! 

That's it! 
You may now [*"roam"* across your annotated network](../cytoApp.md#roaming-acrross-annotated-nodes-and-edges).



## Any other network 

In this case, you can load your network as you would do in Cytoscape in general. 

If your network is not already `microbetag`-annotated, you need first to load in on Cytoscape and then import it to the `microbetag` input;
you may follow the instructions [here](https://hariszaf.github.io/microbetag/docs/cytoApp/#-starting-from-a-co-occurrence-network). 

{: .note}
Remember, you need always to call the column to be used as weight of the network as `microbetag::weight`.


If you have already a `microbetag`-annotated network, that will be a `.cx` file which you can load as any other network on Cytoscape, i.e., by clicking 
on `File > Import > Network from file`. 

Make sure you enable the MGG style and cyPanels:

![style](../../assets/images/app/visualStyle.png)
![panels](../../assets/images/app/show_panels.png)







