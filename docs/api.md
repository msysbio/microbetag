---
layout: default
title: API documentation
nav_order: 4
---

# API documentation
{: .no_toc }

## Table of contents
{: .no_toc .text-delta }

1. TOC
{:toc}


---



microbetagDB API provides programmatic access to the data. 

The base address to the API is https://msysbio.gbiomed.kuleuven.be/.

Below you may find the syntax to retrieve the various data and/or annotations included.

Remember that microbetag is a NCBI Taxonomy oriented resource. That means that a "species" of interest is a NCBI Taxonomy Id.
For example, if you are interested in *Bifidobacterium animalis*, you first need to go to the [NCBI Taxonomy portal](https://www.ncbi.nlm.nih.gov/taxonomy/) and get its corresponding id.
However, once you do so you get a list of subspecies and strains available. 
You can either use the species id or one of a specific strain in your queries. 

microbetag has a special feature called "include species' strains" as in some cases there is no genomic information for the species level but there is at lower levels. 
For example, in case of *Bifidobacterium animalis*, microbetagDB has no genomes for its corresponding NCBI Taxonomy Id (28025) but it does have for the *Bifidobacterium animalis* subsp. animalis ATCC 25527 (703613). 
<!-- This example highlights the issues derived from the current taxonomy schemes as 
Even more interestingly, according to GTDB 
*Bifidobacterium canis* -->



## Get genome ids for a NCBI Taxonoy Id

To check whether a species is present on microbetag, one may find its corresponding **NCBI Taxonomy Id** and search for related genomes present on the microbetag DB. 

For example, assuming we are interested in the *Blautia hansenii* DSM 20583 strain, we find from NCBI Taxonomy that its corresponding id is [537007](https://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?id=537007).

Using the `ncbiTaxId-to-genomeId` route we may get the related genomes on microbetag DB:

```bash
curl -X GET https://msysbio.gbiomed.kuleuven.be/ncbiTaxId-to-genomeId/537007
```

that returns a list of genomes used in microbetag annotations:

```bash
{
  "537007": [
    "GCF_002222595.2"
  ]
}
```

In this case there is a genome available for this NCBI Taxonomy id (GCF_002222595.2).

If no genome is available, then you get an empty value. 

For example, for the *Bifidobacterium animalis* subsp. animalis IM386 (NCBI Tax id: 1402194) there is no genome in microbetagDB:

```bash
curl -X GET https://msysbio.gbiomed.kuleuven.be/ncbiTaxId-to-genomeId/1402194
{
  "1402194": []
}
```



## PhenDB-like traits

### Get phenotypic traits of a GTDB genome 

Once you have identified the genomes related to your NCBI Taxonomy id under study using the ``ncbiTaxId-to-genomeId` route, you may get the corresponding phenotypic traits of that genome(s) using the `/phen-traits/` route and the corresponding **genome id**.

For example, in case of *Blautia hansenii* DSM 20583 (NCBI Taxonomy id: 537007) we saw there is a genome on microbetagDB; to get its phenotypic traits we can simply run:

```bash
curl -X GET https://msysbio.gbiomed.kuleuven.be/phen-traits/GCF_002222595.2
```

this would return (we show only a part of the outcome)

```bash
{
  "NOB": "NO",
  "NOBScore": "0.8078",
  "T3SS": "NO",
  "T3SSScore": "0.8391",
  "T6SS": "NO",
  "T6SSScore": "0.7836",
  "aSaccharolytic": "NO",
  "aSaccharolyticScore": "0.8672",
   ...
}
```

{: .note}
For a thorough description of the abbreviations used, have a look in the microbetag's [modules tab](modules.md#based-on-phendb).


{: .warning }
> 1. Currently, microbetag has annotations only for the GTDB representative genomes. Thus, genomes returned by the `ncbiTaxId-to-genomeId` route that come from other resources (e.g., MGnify, KEGG) do not have phenotypic tratis.
> 2. In case a GTDB genome returns an "Internal Server Error", please try again replacing the "GCA" with "GCF". 


In case a genome id is provided for which there are no phenotypic traits on microbetagDB, you will get a message explaining this:

```bash
No Phen traits for the genome id asked.         
Make sure you are asking for a GTDB v202 representative genome.
```


## Get pathway complementarities

### Get pathway complementarities for a pair of genomes 

In case you are interested in the complementarities of a specific pair of GTDB representative genomes, where `genome_A` is the beneficiary and `genome_B` the donor, 
one may use the `genome-complements` route, followed by `genome_A`, followed by `genome_B`. 

Here is an example: we are interested in the pathway complementarities of a Desulfurococcaceae archeon genome (GCA_011364525.1) with on of the Gram-negative bacterium *Malikia spinosa* (GCA_002980625.1) as its potential donor:


```bash
curl -X GET https://msysbio.gbiomed.kuleuven.be/genome-complements/GCA_011364525.1/GCA_002980625.1
```

Here is its partial output:

```bash
{
  "beneficiary-genome": "GCA_011364525.1",
  "complements": {
    "0": {
      "coloured-map": "https://www.kegg.jp/kegg-bin/show_pathway?map00010/K25026%09%23EAD1DC/K15916%09%23EAD1DC/K00150%09%23EAD1DC/K00927%09%23EAD1DC/K15635%09%23EAD1DC/K01689%09%23EAD1DC/K00873%09%23EAD1DC/K21071%09%2300A898/K01624%09%2300A898/K01803%09%2300A898/",
      "complement": "K01803;K21071;K01624",
      "complete-alternative": "K25026;K15916;K21071;K01624;K01803;K00150;K00927;K15635;K01689;K00873",
      "module": "M00001"
    },
    "1": {
      "coloured-map": "https://www.kegg.jp/kegg-bin/show_pathway?map00010/K00150%09%23EAD1DC/K00927%09%23EAD1DC/K15635%09%23EAD1DC/K01689%09%23EAD1DC/K00873%09%23EAD1DC/K01803%09%2300A898/",
      "complement": "K01803",
      "complete-alternative": "K01803;K00150;K00927;K15635;K01689;K00873",
      "module": "M00002"
    },
    "2": {
      "coloured-map": "https://www.kegg.jp/kegg-bin/show_pathway?map00010/K01596%09%23EAD1DC/K01689%09%23EAD1DC/K15635%09%23EAD1DC/K00927%09%23EAD1DC/K00150%09%23EAD1DC/K01622%09%23EAD1DC/K01803%09%2300A898/",
      "complement": "K01803",
      "complete-alternative": "K01596;K01689;K15635;K00927;K00150;K01803;K01622",
      "module": "M00003"
    },
    ...
  },
  "donor-genome": "GCA_002980625.1"
}
```

Let us now describe its meaning. 
Each entry of the above output stands for a specific KEGG module



### Get complements for pair of species 

microbetag can provide the complements between all the genomes related to a species using the `complements` route. 

In this case, NCBI Taxonomy Ids are provided; microbetag gets their corresponding genomes available on microbetagDB and returns their corresponding complements.

For example, 


```bash 
curl -X GET https://msysbio.gbiomed.kuleuven.be/complements/1281578/146891 
```


```bash
{
  "GCA_003184265.1": {
    "GCA_000015645.1": [
      [
        [
          "M00010",
          "K01682",
          "K01647;K01682;K00031",
          "https://www.kegg.jp/kegg-bin/show_pathway?map00020/K01647%09%23EAD1DC/K00031%09%23EAD1DC/K01682%09%2300A898/"
        ]
      ],
```






## Get seed scores and seed complements


### Get competition and complementarity score between a pair of GEMs

`seed-scores` route `genome_A` is the beneficiary and `genome_B` the donor, 
one may use the `genome-complements` route


```bash
curl -X GET https://msysbio.gbiomed.kuleuven.be/seed-scores/1379686/883079
```


### Get competition and complementarity score between a pair of NCBI Ids

Like in the complements case, seed scores using all the corresponding genomes between 2 species/strains can be retrieved using the `genomes-seed-scores` route.

For example:

```bash
curl -X GET https://msysbio.gbiomed.kuleuven.be/genomes-seed-scores/GCF_000470535.1/GCF_000336555.1
```

returns 

```bash
[
  [
    "GCF_000470535.1",
    "GCF_000336555.1",
    "0.596",
    "0.209"
  ],
  [
    "GCF_000470535.1",
    "GCF_000336555.1",
    "0.647",
    "0.131"
  ]
]
```

The function returns pairs of seed scores, the first genome provided is considered as genome A for the seed metrics (see ["microbetag Modules"](modules/modules.md#seed-scores-based-on-genome-scale-draft-reconstructions-gems) for more) and the second one as genome B.



### Get seed complements between a pair of NCBI Taxonomy, NCBI Genome or PATRIC ids


Seed complements can be retrieved for pairs of 3 different categories of ids: 
- NCBI Taxonomy ids (`type_of_ids: ncbiTaxonomyIds`)
- NCBI Genome accession ids (`type_of_ids: ncbiGenomeIds`) and
- PATRIC ids (`type_of_ids: patricGenomeIds`)

The main route of this feature is 
```bash
https://msysbio.gbiomed.kuleuven.be/seed-complements/<beneficiary_id>/<donor_id>/<type_of_ids>
```

For example, one might get seed complements for a pair of NCBI Taxonomy ids like this:

```bash
curl -X GET https://msysbio.gbiomed.kuleuven.be/seed-complements/1379686/883079/ncbiTaxonomyIds
```


{: note}
> This route has no default for your id type! If not provided by the user, the API will fail.




## Common errors

There are three possible types of client errors on API calls:

- 400 Bad requests.

- 404 Not found.





## Run `microbetag` from Python 

One may use the API routes described through Python. 
For example, to get the microbetagDB genomes related species with NCBI Taxonomy id 853:

```python
import requests
url = "https://msysbio.gbiomed.kuleuven.be/ncbiTaxId-to-genomeId/853"
r = requests.get(url)
r.status_code
200
r.json()
{"537007": ["GCA_002222595.2"]}
```


Furthermore, one may run microbetag directly and not through the CytoscapeApp by simply converting their abundance table or co-occurrence network in a JSON object.
They would also need to provide the following arguments as part of the JSON obect:

```python
arguments_list = ["input_category", "taxonomy", "phenDB", "faprotax", "pathway_complement", "seed_scores"]
```

Here is an example using an ASV abundance table as input, asking
for all microbetag annotations supported:

```python

import requests
import json

# Init a json object
json_object = {}

# Load the abundance table and after removing any blanks load it as lines in the json object
data = open("my_abundance_table.tsv","r")
data = data.readlines()
data = [line.rstrip("\n").split("\t") for line in data]
json_object["data"] = data

# Likewise, in case you already have a network of your own 
edgelist =  open("edgelist.csv","r")
edgelist = edgelist.readlines()
edgelist = [line.rstrip("\n").split("\t") for line in edgelist]
json_object["network"] = edgelist


# Make a dictionary with your arguments settings
args = {
  "taxonomy":"Silva", 
  "delimiter": ";", 
  "faprotax": True, 
  "phenDB": True, 
  "pathway_complement": True,
  "seed_scores": True,
  "manta": False,
} 
json_object["inputParameters"] = args

# Load your metadata file like in the data case; if no metadata you can skip this
# json_object["metadata"] =

# Set the url to the microbetag server
url = "https://msysbio.gbiomed.kuleuven.be/upload-abundance-table-dev"

# Run microbetag
r = requests.post(url, json = json_object)

# Save your annotated network to a json file that cytoscape can load
response_dict = r.json()
with open('new_microbetag.cx', 'w') as f:
	json.dump(response_dict, f, indent=4, sort_keys=True)
```


Apparently, the `my_abundance_table.tsv` and the `edgelist.csv` files can be in any format initially.
Yet, they need to be converted in a way so eventually what you send to the `microbetag` server is in the form of `data` and `network` in the above chunk. These look like this:

```python
>>> data
[
  ['seqId', 'sample1', 'sample2', 'taxonomy'],
  ['bin_100', '77', '1', 'd__Bacteria;p__Bacteroidota;c__Bacteroidia;o__Chitinophagales;f__Chitinophagaceae;g__Terrimonas;s__Terrimonas ferruginea'], ...
]
>>>edgelist
[
  ['nodeA', 'nodeB', 'weight'], 
  ['bin_45', 'bin_28', '0.471'], ...
]
```



{: .important-title}
> POSSIBLE ARGUMENT'S VALUES
>
> `input_category`: [`abundance_table` \| `network`]
>
> `taxonomy`: [`GTDB` \| `Silva` \| `microbetag_prep` \| `other`]
>
> `phenDB`, `faprotax`, `pathway_complement`, `seed_scores`: [`True` \| `False`], `get_children`

{: .warning}
>You `arguments` dictionary needs to include all the arguments mentioned above. If any is not provided , microbetag will eventually fail and won't return an annotated network. 
>
> Syntax common error: make sure you do not have a `/` in the end of the url. If so, microbetag will never start. 


