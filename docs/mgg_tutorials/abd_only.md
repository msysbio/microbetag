---
title: Using abundance data
layout: default
parent: Cytoscape tutorials
nav_order: 1
description: "tutorial using only an abundance table as input"
---


## .. starting from an abundance table

{: .important-title}
> INPUT FILES USED IN THIS TUTORIAL
>
> In this example, we will use the [`testAbund.tsv`][3] file to showcase how to use microbetag without a network being already available.



In case that a co-occurrence network is not available, *microbetag* can come up with one using [FlashWeave](https://doi.org/10.1016/j.cels.2019.08.002).

{: .important-title}
> UP LIMIT FOR ABUNDANCE TABLE RECORDS
> 
> When using the online *microbetag* version, it will build a co-occurrence network only for abundance tables with less than 1000 of records.
> In case your abundance table is larger, you will have to run the [`microbetag` preprocess](../tutorials/prep.md) step locally.
> Otherwise, you can always run any algorithm for network inference locally and use their findings with microbetag.


<!-- The on-the fly creation of the co-occurrence network is supported only for abundance tables with **up to 1000 records**.
If your data include more sequencing records, then you will have to use the [`microbetag` preprocess](./tutorials/prep.md) step. -->

Once clicking on *Import Data* you currently see only the *Import Abundance Data* option.

<!-- ![load_data](../assets/images/app/importData.png)  -->
![import_abundance](../../assets/images/app/importAbundData.png)


By clicking on it, a pop-up box will ask you to provide your abundance table.
Select it with you mouse and then open it. 

<!-- ![open_data](../assets/images/app/openFile.png) -->
![open_data](../../assets/images/app/Open_abund.png)

You can view the imported data by clicking on the *Check Data Files* feature, for the case of the abundance table:

![check_abund_option](../../assets/images/app/checkOptionAbundData.png)

Once clicking that, a table will pop up where you can go through the data you have imported as the abundance table. 
Keep in mind that in case you have more than a few samples, or your abundaces have a long number of digirs, you will need to double-click to a column at a time to be able to see its values. 


<!--  -->

You can now ask for a *microbetag-*annotated network by clicking on the corresponding feature:

![get_annotated_network](../../assets/images/app/getaAnnotatedNet.png)

Once clicking on that, a parameter-setting box will pop up, asking for values on a number of parameters **essential** for the successful network inference and their corresponding annotation.

![settings](../../assets/images/app/parameters_no_net.png)


Please make sure you set the input type as `abundance_table` and you select the correct [taxonomy scheme](../input.md#input-files).
It is crucial to also set the [FlashWeave related parameters](../faq.md#when-to-enable-the-sensitive-and-heterogeneous-arguments) in a way they address your abundance table idiosyncrasy.


{: .important}
We suggest you do the network inference step as well as the mapping to the GTDB taxonomy before using *microbetag* through the Cytoscape App as this would provide you extra freedom on they network inference and gain dramatically in computing time on the server.


Once you set the parameters of your choice, you are ready to sent your query to the server by clicking *ok*. 
In this case, we need `microbetag` to come up with a network as we only provide an abundance table; thus, we set the `Choose input type` to `abundance_table`. 
Also, since our taxonomy scheme was Silva we choose this to map our taxa against. 
Last but not least, we set the `Sensitive` parameter as `True` since we have a relatively low number of sequences; 
this way FlashWeave may detect more subtle associations because it considers the full range of abundance variations. 
However, this also makes the computation more intensive and slower, especially with large datasets.
See [FAQ](../faq.md) for more. 

![send_data](../../assets/images/app/sendingDataToServer.png)



After a few minutes (based on your data and the steps you have asked for) a *microbetag-*annotated network will pop up automatically on your Cytoscape instance.

![annotated_net](../../assets/images/app/annotated_net_no_net.png)


{: .important-title}
> HELP
>
> There are several reasons you may either get a network with only a few nodes/edges annotated or get an error message from the server. 
> Both scenarios are related to either the format of your input data or the parameters you have selected. 
> Please, follow the guidelines you can find in the [*Input files*](../input.md) tab and check our [*FAQ*](../faq.md) for common errors. 
> If you still need some help, please go ahead and ask the `microbetag` community on our [Matrix community](https://matrix.to/#/#microbetagcommunity:matrix.org).



[3]:{{ site.url }}/microbetag/download/mgg/testAbund.tsv

