---
title: Run from Python
layout: default
parent: Additional tutorials
nav_order: 4
description: "how to run microbetag from Python"
---


# Run `microbetag` from Python 

## Use `microbetag`'s features as a library

Assuming you have [installed `microbetag` locally](../installation.md#from-source-code), you can now use `microbetag`'s features independently. 

To go through them, you may have a look at the [API Reference](../autoapi) but also on the [`unittests` of ours](https://github.com/hariszaf/microbetag/tree/user-bins-nfl/tests).
You may run individual genome annotation steps, build your own GENREs, as well as the routines allowing you to export pathway and/or seed complementarities. 

Feel free to contact on our [Matrix community](https://matrix.to/#/#microbetagcommunity:matrix.org) in case you face any trouble.



For example, one can easily run the whole microbetag pipeline using the corresponding `config.yml` template to the `microbetag` version to be used, running:

```python
from microbetag.config import Config
from microbetag.microbetag import run_microbetag

with open("config.yml", "r") as yaml_file:
	config = Config(yaml.safe_load(yaml_file), "config.yml")

run_microbetag(config)
```

```{important}
Remember that `microbetag` will use all files that have been produced from a previous run, given the output directory stays the same! 
That means that if you wish to re-calculate a part for any reason, e.g. run FlashWeave again with a different set of parameters, you need to make sure
that you first **delete** the previous output files of this step! 
```


## Use `microbetag` API programmatically

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
arguments_list = [
  "input_category", 
  "taxonomy", 
  "phenDB", 
  "faprotax", 
  "pathway_complement", 
  "seed_scores"
]
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



```{important}
**POSSIBLE ARGUMENT'S VALUES**

`input_category`: [`abundance_table` \| `network`]

`taxonomy`: [`GTDB` \| `Silva` \| `microbetag_prep` \| `other`]

`phenDB`, `faprotax`, `pathway_complement`, `seed_scores`: [`True` \| `False`], `get_children`

```

```{warning}
You `arguments` dictionary needs to include all the arguments mentioned above. If any is not provided , microbetag will eventually fail and won't return an annotated network. 

Syntax common error: make sure you do not have a `/` in the end of the url. If so, microbetag will never start. 
```

