# `microbetag` stand-alone version

## About

`microbetag` annotates microbial co-occurrence networks with phenotypic traits of the taxa present and with potential metabolic interactions among them.

In this branch we have a stand-alone tool to run the software on your own bins.
This module **cannot** be performed directly from the CytoscapeApp as it requires computing resources that our web-service cannot support.
Yet, once you run this stand-alone version, you will still be able to load the annotated network returned (`microbetag_annotated_network.cx`) on Cytoscape and 
investigate the annotations through the MGG CytoscapeApp of ours.
For a step-by-step step tutorial, please refer to the [`microbetag` readTheDocs](hhttps://hariszaf.github.io/microbetag/) site.

This stand-alone tool is distributed as a Docker and a Singularity image. 

## Dependencies


### Running `microbetag` on your host machine



`microbetag` relies on switching `conda envs`; thus `conda` is a strong pre-requisite.
First, make sure you do have `conda` on your host machine.







### Running `microbetag` in a container

- [Docker](https://docs.docker.com/get-docker/) or [Singularity](https://docs.sylabs.io/guides/3.1/user-guide/installation.html) / [Apptainer](https://apptainer.org/admin-docs/master/installation.html#installation-on-linux)
- kofam_database

You can do this by running the following chunk of code:
```bash
mkdir kofam_database &&\
    cd kofam_database &&\
    wget -c ftp://ftp.genome.jp/pub/db/kofam/ko_list.gz &&\
    wget -c ftp://ftp.genome.jp/pub/db/kofam/profiles.tar.gz &&\
    gzip -d ko_list.gz &&\
    tar zxvf profiles.tar.gz 
```
- A Web License Service (WLS) [Gurobi license](https://www.gurobi.com/downloads/) in case you are about to use `carveme`.
    You may find the following [link](https://support.gurobi.com/hc/en-us/community/posts/4406485885841-Installing-Gurobi-on-a-Docker-container-Ubuntu) useful on how to do that.
















## Input files

To run microbetag with your own bins, there is a number of required and some optional input files to provide. 
Through the [`config.yml`](./tests/dev_io_microbetag/config.yml) file you may set all the relevant arguments. 
You will have to follow the instructions for each variable. 
For example, 
```yaml
abundance_table_file: 
  fileName: thirty_Samples.tsv
  description: Filename of the abundance table file. \
    The taxonomy scheme in this case is irrelevant. \
    However, you need to make sure that the sequence identifiers used in this table, are the same \
    with those in your network (if one provided) as well as with those in your bins/faa/xml files, again if such provdied.
  required: True
  examples: 
    - thirty_Samples.tsv
    - counts_genomes_taxonomies.tsv
  type: string
```

The `abundance_table_file` variable is required as the `required` field is `True`. 
It also needs to be a string as mentioned in the `type` field. 
The value of the variable needs to be set in the `fileName` field. 

Accordingly, you will need to set all the required and any optional variables. 

Keep in mind that the seed complementarity step is the most challenging as it requires metabolic networks, 
most specifically metabolic Genome-Scale Network Reconstructions (GENREs), 
to be built first.
Therefore, this step is optional.
`microbetag` supports two ways for GENREs reconstruction:

- using [`modelseedpy`](https://github.com/ModelSEED/ModelSEEDpy), that is based on the [ModelSEED](https://modelseed.org) resource, and
- using the [`carveme`](https://carveme.readthedocs.io/en/latest/) tool, that currently supports only the [BiGG](http://bigg.ucsd.edu) identifiers 
    and requires a Gurobi or CPLEX license.

In case you have already protein-annotated your bins, i.e., you have .faa files, or you already have reconstructions, you can provide those to `microbetag` as input files; 
see arguments `input_type_for_seed_complementarities` and `sequence_files_for_reconstructions`. 

**Important**

Besides the `config.yml` file, the abundance table and the folder with the bins sequences, you need always to mount 
a copy of the `kofam_database` and always pointing to the `/microbetag/microbetagDB/ref-dbs/kofam_database/` path.
If `carveme` is to be performed, a WLS Gurobi license is also required to be mounted.


> This stand-alone version of microbetag does not depend on microbetagDB, and thus it is independent of the taxonomy used. 


## Using Docker

```bash
docker pull hariszaf/microbetag:v1.0.0
```

By running `docker images` you will see `microbetag:v1.0.0` among your images. 

You may perform a microbetag analysis by running:

```bash
docker run --rm -it  \
    --volume=./tests/dev_io_microbetag/:/data \
    --volume=./microbetagDB/ref-dbs/kofam_database/:/microbetag/microbetagDB/ref-dbs/kofam_database/ \
    --volume=$PWD/gurobi.lic:/opt/gurobi/gurobi.lic:ro \
    microbetag:v1.0.0
```

In this case, we mount the [`dev_io_microbetag`](./tests/dev_io_microbetag/) and all its contents from our host system,
to the `/data` directory of the container. 
Also, we mount a copy of the kofam database that we downloaded locally to the 
`/microbetag/microbetagDB/ref-dbs/kofam_database/` path of the container. 


You can also fire a Docker container and interact with that using the `--entrypoint` flag:

```bash
docker run --rm -it  \
    --volume=./tests/dev_io_microbetag/:/data \
    --volume=./microbetagDB/ref-dbs/kofam_database/:/microbetag/microbetagDB/ref-dbs/kofam_database/ \
    --volume=$PWD/gurobi.lic:/opt/gurobi/gurobi.lic:ro \
    --entrypoint /bin/bash  \
    microbetag:v1.0.0
```

In the `output_directory` you have set in your `config.yml` file, all the intermediate (annotation) files will be returned. 

> The annotated network you may load to Cytoscape is the file called `microbetag_annotated_network.cx`.



## Using Singularity 

You need to first build your Singularity image based on a [Docker version of microbetag](https://hub.docker.com/repository/docker/hariszaf/microbetag/tags?page=1&ordering=last_updated):

```bash
sudo singularity build microbetag_v101.simg docker://hariszaf/microbetag:v1.0.1
```

You will need to have `sudo` rights to do that, so in case you are working on an HPC this will not be the case:
You can either as your admin to do so or run the build command in a similar environment and move it to the HPC. 


```bash
singularity exec 
    -B tests/dev_io_microbetag/:/data  
    -B microbetagDB/ref-dbs/kofam_database/:/microbetag/microbetagDB/ref-dbs/kofam_database/
    -B $PWD/gurobi.lic:/opt/gurobi/gurobi.lic:ro  
    microbetag_v101.simg 
    python3 /microbetag/microbetag.py /data/config.yml
```


Please make sure that both your input files (abundance table and bin sequences, but also protein sequences and models if provided), the `kofam_database` and your Gurobi license if provided, are parts of the 


<!-- Issue where different findings from carveme using cplex and gurobi is mentioned:
https://github.com/cdanielmachado/carveme/issues/141#issuecomment-912309490 -->



## Graphical User Interphase (GUI)

Once `microbetag` has been performed successfully, and the `microbetag_annotated_network.cx` has been built,
and assuming you have [installed the MGG CytoscapeApp](https://hariszaf.github.io/microbetag/docs/cytoApp/), 
you can now load the `.cx` file in Cytoscape (`File > Import network from file`) and go through the annotations the same way as you would do when running microbetag from within the app. 


## Unit-tests

Remember, `unittest`:

  - requires the testing function to start with the `test_` prefix, e.g. `test_run_flashweave()`
  - will run your tests in alphabetical order
  - `setUpClass` is called with the class as the only argument and must be decorated as a `classmethod()`

:warning: Remember also that `microbetag` will use the directory where the configuration files you provide 
as the base working directory. 
Therefore, you should place your input/output files within the confi file directory as in the `ext_data/tests_*`.



## Funding

This project is funded by: 
- the [3D' omics](https://www.3domics.eu) Horizon project (101000309).
- an [EMBO Short-Term Fellowship](https://www.embo.org/funding/fellowships-grants-and-career-support/scientific-exchange-grants/)

