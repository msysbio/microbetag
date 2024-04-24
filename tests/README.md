# Examples of `microbetag`  input files 


We support Silva, GTDB and a GTDB for 16S rRNA gene taxonomy scheme returned by the `microbetag_prep` container. 
Other taxonomy schemes can be used by selecting the `Other` option; in this case `microbetag` will not map but will try to find the most similar taxonomy to the one you provided in NCBI Taxonomy. 

In this folder, you can find example cases of an abundance table that can be used with the `Silva` taxonomy in the parameters settings or the `Other`. 
The `*.tsv` files are the ones you may provide to `microbetag` through the MGG CytoscapeApp.

The two `.json` files are actually in a "list-of-lists" format:

```bash
[ ["ASV_id","KUL001","KUL037","KUL132","KUL156","KUL192","KUL206","KUL218","KUL241","KUL265","KUL307","KUL338","KUL351","taxonomy"],
  ["ASV_1","5203","2931","13582","8516","10476","10103","12179","3269","2433","1772","513","6068","Bacteria;Firmicutes;Thermoanaerobacteria;Thermoanaerobacterales;Family III;Thermoanaerobacterium;Thermoanaerobacterium"],
  ...
]
```

where each inner list represents a line. You can load such a file in Python using the `json` library as follows:

```python
>>> import json 
>>> with open("dada2_use_case.json", "r") as f:
...     data =json.load(f)
```

Then, you may pass the data in the `json_object` that you will send in the server (as discussed in this [tutorial](https://hariszaf.github.io/microbetag/docs/api/#run-microbetag-from-python)):

```python
json_object["data"] = data
```

---------------------------

In the `microbetag_prep_example.tsv`, you may find an example case of the taxonomies returned by the `microbetag_prep` prepartion step. 
For thorough instructions on how to run this, please have a look [here](https://github.com/hariszaf/microbetag/tree/preprocess?tab=readme-ov-file#microbetag-preprocessing) or in the relevant [Tutorial](https://hariszaf.github.io/microbetag/docs/tutorials/prep/).



