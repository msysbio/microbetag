

<!-- :warning: 
:eyes: Look here! -->

## :red_circle: Output folder architecture required

The `build_pseudo_cx()` function parses all the intermediate data products of `microbetag` to build the annotated network. 
To this end, it **requires** the architecture of the output folder that `microbetag` builds, to run. 

>Therefore, in this test case, **your input, is the `microbetag`'s output folder**. :eyes:
>
> And thus, the `output_files` folder of this test, is also used as **input** for the test.
> 
> The returned `microbetag`-annotated file will be also saved there.


:white_circle: The content of the intermediate folders needs to be in line with the parameters you have set. 
For example, if you have set `pathway_complementarity` to `true`, you need to make sure the corresponding output folder 
**and its data products** (e.g., `alts.json`) they are all included. Otherwise, `microbetag` will fail.
For example in this test case, if we set the `network_clustering` as `true`, and at the same time, we don't provide a
`manta_network`, the test would fail.


:eyes: In this test case we are using the 7bins dev dataset and its data products.
For this dataset, no clustering was performed due to its small size.




