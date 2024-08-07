---
title: Using abundance & metadata
layout: default
parent: Cytoscape tutorials
nav_order: 2
description: "tutorial using an abundance table and a metadata file as input"
---




## .. starting from an abundance table and a metadata file


In this case, you follow the exact steps as in the previous scenario and once you have loaded your abundance table, you import also the one with your metadata. 

![metadata_menu](../../assets/images/app/import_metadata_menu.png)

![select_metadata_file](../../assets/images/app/open_metadata_file.png)

You can check the metadata file, similar to how you check the abundance data, through the `MGG` menu:

![check_metadata_menu](../../assets/images/app/check_metadata.png)

{: important}
Your metadata need to be as rows having their values per sample in their columns. See also on the [input files](./input.md#metadata-file) section. 


![metadata_view](../../assets/images/app/imported_metadata.png)

{: .warning}
Remember to set the parameters as in the [previous example](abd_only.md), i.e. your taxonomy is Silva and FlashWeave needs to run using the `sensitive` approach. 


Here is the annotated network returned:

![annotated_net_metadata](../../assets/images/app/annotated_net_with_met_env.png)






