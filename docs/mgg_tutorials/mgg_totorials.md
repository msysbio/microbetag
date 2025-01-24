---
layout: default
title: Cytoscape tutorials
nav_order: 3
has_children: true
version: latest
permalink: /docs/mgg_tutorials
usemath: true
---

![microbetag CyApp]({{ site.baseurl }}/assets/images/cyApp.png){: width=25% }



# Run `microbetag` Cytoscape app

microbetag v1.0.1
{: .label .label-green }

MGG v1.0.0
{: .label .label-green }


[microbetag web-app](https://github.com/msysbio/microbetagApp-public/releases/tag/v1.0.1){: .btn .btn-green .fs-5 .mb-4 .mb-md-0 }
[MGG source code](https://github.com/ermismd/MGG){: .btn .btn-green .fs-5 .mb-4 .mb-md-0 }
[Tutorial files](https://github.com/hariszaf/microbetag/tree/gh-pages/download/mgg){: .btn .btn-purple .fs-5 .mb-4 .mb-md-0 }


{: .important-title}
> INPUT FILES AND PARAMETERS SETTING
>
> Please, download the files required for the different cases and **set the parameters as shown in this tutorial**. 
> Parameters are essential especially for the online version of `microbetag` as they can lead either to non-optimal annotations or even failures of the software.
> You may check the [FAQs](../faq.md) section for rules of thumb on how to set your parameters and you are always welcome to [join us on Matrix](https://matrix.to/#/#microbetagcommunity:matrix.org) and ask us directly.



We show how to install and use the microbetag Cytoscape app (called `MGG`) and use it with your data to get `microbetag`-annotated networks 
using the `micrbetagDB` and the online version of `microbetag`.
We also highlight the `MGG` features that allow you to go through the nodes and the edges annotations returned. 


To start using *microbetag* you need first, to make sure you have **Cytoscape** on your system; if not, go ahead and [download Cytoscape](https://cytoscape.org/download.html). 
Then, you need to install the *microbetag* app (`MGG`) from [Cytoscape App store](https://apps.cytoscape.org/apps/mgg).
Make sure **you first lunch Cytoscape** and then visit Cytoscape Appstore.
If you have already visited the MGG page on Cytoscape Appstore, **lunch Cytoscape and refresh the Cytoscape Appstore page**.
You should now see an **Install** button.

![mgg install]({{ site.baseurl }}/assets/images/install_button_mgg.png)

By clicking it, it will be automatically integrated on your Cytoscape. 
If you visit Cytoscape Appstore and you have not lunched Cytoscape, you will see a *Download* button instead of the *Install*.
As already mentioned, we suggest you lunch Cytoscape and refresh the page. 
Otherwise, you can click the **Download** button and move manually the `.jar` file to the apps folder of your Cytoscape.

You can also get `MGG` from within Cytoscape by clicking on the `Apps` tab of the main bar and then `App  Store > Show App Store` and typing `microbetag` on the box that pops up.

Once the app is installed, you may click on the `Apps` tab, and you will find *MGG* there.

![mgg_overall]({{ site.baseurl }}/assets/images/app/mainMenu.png)



From the main menu box, you will have access to all features of the app. 
As you see, the *Get Annotated Network* is currently not a clickable option. 
That is because *microbetag* has no input yet. 

You need first to feed the app with your abundance table and, if available, your co-occurrence network.
In both cases though, the **abundance table** will be **required**. 

Please, make sure your taxonomy fits the criteria for `microbetag` to run. 
You may find more on that issue on the [*Input files*](../input.md#input-files) section.

Then, as you will see in the following two cases, you will have to set the values to a set of parameters to describe your input data but also what annotation steps you would like `microbetag` to perform.


|Parameter | Variable      | Description                       | Value |
|----------|---------------|-----------------------------------|-------|
|Choose input type         |`input_category`| In case you already have a network, set it as `network` and load it; otherwise set it as `abundance_table`. In both cases you need to provide the abundance table though| [`abundance_table` \| `network`] |
|Choose taxonomy database| `taxonomy` | In case a user's taxonomy is to be used, denotes which taxonomy scheme to be used from microbetag | [`GTDB` \| `dada2` \| `qiime2`] |
|phenDB annotations         | `phenDB`            | return phenotypic traits based on phen models  | bool |
|FAPROTAX annotations       | `faprotax`          | return annotations using the FAPROTAX database | bool |
|Pathway Complementarity    | `pathway_complement`| return pathway complementarities between associated nodes | bool |
|Seed scores and complements| `seed_scores`       | return complementarity and cooperation scores based on metabolic reconstructions seed sets | bool |
|Network clustering         | `manta`             | return clusters of nodes on the network using the manta package | bool | 
|Consider children taxa     | `get_children`      | use genomes of children taxa of the taxa in the abundance table based on the NCBI Taxonomy scheme, relevant only if you use `Other` taxonomy | bool |
|heterogeneous              | `heterogeneous`     | (FlashWeave) enable heterogeneous mode for multi-habitat or -protocol data with at least thousands of samples (FlashWeaveHE) | bool | 
|sensitive                  | `sensitive`     | (FlashWeave) enable fine-grained associations (FlashWeave-S, FlashWeaveHE-S), sensitive=false results in the fast modes FlashWeave-F or FlashWeaveHE-F | bool | 


The column `Variables` in the above table provides the variable names you need to use in case you are about to use `microbetag` from Python (see [tutorial](../tutorials/python.md)).

The datasets to be used in all cases except of the [*Using a network*](./from_net.md) tutorial, are subsets of abundance tables with no special biological meaning.
However, in the *Using a network* case, we do use the network of [Hessler et *al.* (2023)](https://doi.org/10.1038/s41467-023-40360-4) who we would like to thank for sharing their data.
