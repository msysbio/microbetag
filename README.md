# `microbetag` stand-alone version

## About

`microbetag` annotates microbial co-occurrence networks:
  - on the **node** level: with phenotypic traits of the representing taxa
  - on the **edge** level: with potential metabolic interactions among the co-occurrying or mutual exclusive taxa.


The simplest way to use `microbetag` is through its Cytoscape App, called `MGG`.
You can [download `MGG`](https://apps.cytoscape.org/apps/mgg) directly from the Cytoscape ApppStore.

`MGG` allows both to run `microbetag` on-the-fly and visualize the returned annotated network.
However, using the on-the-fly version, means `microbetag` will try to match your taxa to their closest GTDB representative genomes.
Then, it will annotate your network based on pre-calculations of those GTDB genomes available on `microbetagDB`.

In case, you prefer to annotate your network using information from a local/custom set of genomes, then you can go ahead
and install `microbetag` locally, since pre-calculations are computationally expensive tasks making it impossible to run on a web-server.

Once you install and run `microbetag` locally, you end up with an annotated network in CX2 format on your output directory, 
e.g. `mtag_net_2025-05-08_17-47.cx2`.
All you need to do then, is to load this file on Cytoscape and you are ready to go through its annotations as in the on-the-fly version. 


For more on how to use `microbetag`, `MGG` and their features, feel free to have a look 
at [`microbetag`'s documentation page](https://microbetag.readthedocs.io/en/v1.0.3/).


## Installation: Running `microbetag`..

### Option 1: On-the-fly 

To use `microbetag` on-the-fly, all you have to do is to make sure you have Cytoscape on your computing system and add the `MGG` app.

* **You can [install Cytoscape](https://cytoscape.org/) from their website.**

* **After firing Cytoscape you can [add `MGG` by downloading it from the Cytoscape AppStore](https://apps.cytoscape.org/apps/mgg).**


### Option 2: On your host machine

To run `microbetag` locally, you need to install a great range of software and dependencies. 
To make this easier, we provide the [`setup_environment.sh`](./setup_environment.sh) script. 

**The `setup_environment.sh` expects `conda` is available on your computing system!**

If `conda` (or `Miniconda`) is not installed, then you may get it by following the instructions you may find 
[here](https://www.anaconda.com/docs/getting-started/miniconda/install).

After cloning the `microbetag` GitHub repository locally in a directory of your choice

```bash
git clone https://github.com/hariszaf/microbetag.git
```

you can build its required environments by running:

```bash
cd microbetag
bash setup_environment.sh
```

Once `conda` environments and required tools and databases are installed, you can install the `microbetag` package by running:

```bash
python setup.py sdist bdist_wheel
pip install .
```
In case you get the strip_trailing_zero error
```bash
pip install --upgrade setuptools packaging
```

You are ready to go! 🚀

Feel free to go through the [`tests`](./tests/) folder to check on how you can run specific modules or a complete pipeline of `microbetag`.
A detailed description of those tests can be found [here](./test_data/README.md).

For more, you can also check [on `microbetag`'s documentation page](https://microbetag.readthedocs.io/en/v1.0.3/advanced_use/local.html).



### Option 3: In a container

To run `microbetag` as a [Docker](https://docs.docker.com/get-docker/) container, you can directly get it from DockerHub:

```bash
docker pull hariszaf/microbetag:<version>
```

Contrary, if you are interested in running it as a [Singularity](https://docs.sylabs.io/guides/3.1/user-guide/installation.html) 
or an [Apptainer](https://apptainer.org/admin-docs/master/installation.html#installation-on-linux) container,
you need to first build its corresponding image based on a [Docker version of microbetag](https://hub.docker.com/repository/docker/hariszaf/microbetag/tags?page=1&ordering=last_updated).
To do so, you can run:

```bash
sudo singularity build microbetag_v101.simg docker://hariszaf/microbetag:<version>
```

🔴 To execute the `singularity build` command, you will (probably) need to have `sudo` rights.
Thus, in case you are working on an HPC, you will have to:
- either ask your admin to do so, or 
- run the build command in a similar environment and move it to the HPC. 

Both in the Docker and Singularity cases, you will need to first get the kofam database 
in case you are interested in pathway complementarities and kofam is not already available on your computing system.  
You can get kofam database by running the following chunk of code:

```bash
cd ext_data/kofam_database &&\
wget -c ftp://ftp.genome.jp/pub/db/kofam/ko_list.gz &&\
wget -c ftp://ftp.genome.jp/pub/db/kofam/profiles.tar.gz &&\
gzip -d ko_list.gz &&\
tar zxvf profiles.tar.gz 
```

Also, if you are about to reconstruct Genome Scale Models, necessary for inferring seed complementarities, using CarveMe
you would also need to get a Web License Service (WLS) [Gurobi license](https://www.gurobi.com/downloads/).
To do so, you may find the following [link](https://support.gurobi.com/hc/en-us/community/posts/4406485885841-Installing-Gurobi-on-a-Docker-container-Ubuntu) useful on how to do that.
Like the kofam case, this applies for both Docker and Singularity.

To run `microbetag` in a container, you will need to ***pass*** kofam and/or the Gurobi license 
(in case you do need them for the steps you wish `microbetag` to go for) to the running container, as well as your **input data** themselves. 

Here is how you can do this in these two technologies.

#### Docker

We **mount** the [`test_microbetag`](./test_data/test_microbetag/) and all its contents from our host system, 
to the `/data` directory of the container. 
**The `test_microbetag` folder should contain all our genomes/bins, abundance table, metadata or network (edge list) files.**
**Anything `microbetag` will consider as input files. For example, in case you already have GEMs for your genomes, they should also be mounted.**

Remember to **mount** the kofam database to the `/microbetag/microbetagDB/ref-dbs/kofam_database/` path of the container and the Gurobi license,
if necessary.

> Your configuration YAML in case of running on a container, needs to provide **the paths of your data in the container**,
> not those on your host system.

```bash
docker run --rm -it  \
    --volume=./test_data/test_microbetag/:/data \
    --volume=./ext_data/kofam_database/:/microbetag/microbetagDB/ref-dbs/kofam_database/ \
    --volume=$PWD/gurobi.lic:/opt/gurobi/gurobi.lic:ro \
    microbetag:<version>
```

You can also start an **interactive shell** inside the container by using the `--entrypoint` flag and setting it to `/bin/bash`. 
This allows you to explore and work inside the container environment manually.



#### Singularity

Like in the Docker case, you need to mount data and related files.

```bash
singularity exec 
    -B tests/dev_io_microbetag/:/data  
    -B microbetagDB/ref-dbs/kofam_database/:/microbetag/microbetagDB/ref-dbs/kofam_database/
    -B $PWD/gurobi.lic:/opt/gurobi/gurobi.lic:ro  
    microbetag_v101.simg 
    python3 /microbetag/microbetag.py /data/config.yml
```


### Tricky parts for running locally

`microbetag` makes use of a range of external software, some of which have conflicting dependencies.
This is why `microbetag` builds for example **two environments** through the [`setup_environment.sh`](./setup_environment.sh),
one called `microbetag` and a second one called `phendb`. 
Similarly, it switches from a `scikit-learn` version to another while running. 
This is not optional, and we hope in the future to find a better way.



## Further `microbetag` links

Overall, `microbetag` is a software ecosystem composed of a collection of modular code components:

- `microbetagDB` : `db` branch on current [GitHub repo](https://github.com/hariszaf/microbetag/tree/db)
- `microbetag_prep`: `preprocess` branch on current [GitHub repo](https://github.com/hariszaf/microbetag/tree/preprocess)
- `microbetagApp`: individual [GitHub repo](https://github.com/msysbio/microbetagApp-public)
- `MGG` source code: individual [GitHub repo](https://github.com/hariszaf/MGG)
- pre-calculations: Seed and non-seed sets for GTDB representative genomes available in `microbetag`, their corresponding GEMs, models for `phenotrex`-based predictions and KEGG annotations of each of those genomes are available on [Zenodo](https://zenodo.org/records/15102937).
  
For potential issues when running `microbetag`, or ideas for further features, 
please feel free to join us on [`Matrix`](https://matrix.to/#/#microbetagcommunity:matrix.org).



## How to run `microbetag`

### On-the-fly

In case you are about to run `microbetag` using the on-the-fly option, you need to only provide you actual input data files, i.e.:
- an abundance file (mandatory)
- a co-occurrence network (optional)
- metadata file for inferring the co-occurrence network (optional)

For thorough descriptions on the format of each of these files, 
[continue on the `MGG` tutorials](https://microbetag.readthedocs.io/en/latest/basic_usage/mgg_totorials.html).


### Locally

If you are about to use `microbetag` locally, then besides the input files mentioned in the on-the-fly case,
you have, apparently, several other input data files. 
For example, you may have a set of genomes, or already annotated genomes. You may also have your own GEMs or not etc. 
All these files are *optional*. 

🔴 Yet, **a `config.yml` file is mandatory!** Each `microbetag` **version** comes with **its own template** configuration file,
that you can find in the [`config_files`](./config_files/) folder.

❗ Properly filling in the configuration file is crucial for the successful operation of `microbetag`.

To do so, take your time and read each argument's description; also check on their allowed values if provided and/or 
when an argument is required. For example:

```yaml
kofam_database:
  path: /home/user/kofam_database
  description: >
    Provide the path to the kofam directory_database directory.
    This variable is not required unless `pathway_complementarity` is set to true
    and `ko_merged_file` is not provided.
  required: 
    value: false
    when: >
      pc_percentage is true and ko_merged_file is null
  type: Path
```

The `kofam_database` variable is **not always required** as the `required` field is `false`.  
It also needs to be a string pointing to a directory (`path`) as mentioned in the `type` field. 
The value of the variable needs to be set in the `path` field. 


For more specific examples, you may have a look on [`tests`](./tests/) and their corresponding [`test_data`](./test_data/), 
and of course on the [**running `microbetag` locally**](https://microbetag.readthedocs.io/en/latest/advanced_use/local.html) tutorial.


❗ The configuration files are considered **templates** since you can use them partially, including only the variables required for the tasks 
you wish to go for. This is shown in several [`tests`](./tests/).

<!-- Issue where different findings from carveme using cplex and gurobi is mentioned:
https://github.com/cdanielmachado/carveme/issues/141#issuecomment-912309490 -->


---

🚀 Once setting `microbetag` locally, you can use it as a Python library to a great extent, meaning you can perform a great range 
of specific tasks out of the main pipeline concept. 
For example, given you have a set of GEMs, you may [get their seed complementarities](./tests/test_seed_compl.py), 
without an abundance table or network. 


## RTD

`microbetag` uses ReadTheDocs and Sphinx for its documentation (see `docs/`).

> **For contributors**
>
> To test changes locally first, run:
> ```
> sphinx-build -b html -d _build/doctrees -D language=en . _build/html -v
> ```
> from within the `docs/` directory.
> 

A new RTD is being produced every time a new _microbetag_ `tag` is released automatically.



## Cite

If you use `microbetag`, please consider citing us:

Zafeiropoulos H, Michail Delopoulos EI, Erega A, Schneider A, Geirnaert A, Morris J, Faust K. 
microbetag: simplifying microbial network interpretation through annotation, enrichment tests and metabolic complementarity analysis. 
*bioRxiv*. 2024:2024-10. DOI: [10.1101/2024.10.01.616208 ](https://doi.org/10.1101/2024.10.01.616208 )


## Funding

This project is funded by: 
- the [3D' omics](https://www.3domics.eu) Horizon project (101000309).
- an [EMBO Short-Term Fellowship](https://www.embo.org/funding/fellowships-grants-and-career-support/scientific-exchange-grants/)

