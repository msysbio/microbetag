---
title      : Using abundance & metadata
layout     : default
parent     : Cytoscape tutorials
nav_order  : 2
description: "tutorial using an abundance table and a metadata file as input"
---

# .. using an abundance table and a metadata file


```{note}
**INPUT FILES USED IN THIS TUTORIAL**

We will also do the same but this time considering also metadata ([`metadata.tsv`][4]) accompanying a shorter version of our abundance table ([`testAbundMeta.tsv`][5])
```

In this case, you follow the exact steps as in the previous scenario and once you have loaded your abundance table, you import also the one with your metadata. 

![metadata_menu](../_static/img/app/import_metadata_menu.png)

![select_metadata_file](../_static/img/app/open_metadata_file.png)

You can check the metadata file, similar to how you check the abundance data, through the `MGG` menu:

![check_metadata_menu](../_static/img/app/check_metadata.png)

```{important}
Your metadata need to be as rows having their values per sample in their columns. 
See also on the [input files](../tutorials_core/input.md#metadata-file) section. 
```

![metadata_view](../_static/img/app/imported_metadata.png)

```{warning}
Remember to set the parameters as in the [previous example](./abd_only.md), i.e. your taxonomy is `Silva`, 
and FlashWeave needs to run using the `sensitive` approach. 
```

Here is the annotated network returned:

![annotated_net_metadata](../_static/img/app/annotated_net_with_met_env.png)



[4]:../_static/download/mgg/metadata.tsv
[5]:../_static/download/mgg/testAbundMeta.tsv




