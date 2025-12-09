---
title: Install microbetag
layout: default
nav_order: 3
description: "Installation approaches"
---


# Install `microbetag`

`microbetag` consists of several, independent tools, 
to allow users to get an annotated co-occurrence network based on their needs. 

Have a look at the [Usage modes](./modes.md) section regarding the different modules supported.

Here we provide instructions for installing the required components for each module across various computing environments.

<!-- Its basic features are the following: 

- *microbetag* Cytoscape App called MGG: no matter how you will actually run `microbetag`, 
  you will need `MGG` to visualize the annotated network. 
  Through MGG, you can upload your input data and directly call `microbetag` which will run on-the-fly on our server. 
  `microbetag` will first try to map the taxa present on the data to their corresponding GTDB genomes 
  based on their **taxonomies**. 
  This case is rather straight forward for the user, but it is limited in datasets with less than 1_000 taxa. 

- *microbetagDB* hosted at KU Leuven, it consists of all the pairwise GTDB reference genomes annotations. 
  You can directly access its contents using its corresponding [API](api).

- `microbetag_prep` a Docker image that allows you to run only two specific preprocessing steps: 
  - in case of 16S rRNA data, you can provide an abundance table with the ASV/OTU on its last column and your data will be taxonomically assigned using a GTDB-oriented 16S reference database.
  - for datasets with more than 1000 taxa, you can perform the network inference using this image and the `FlashWeave` tool. 
  After, you run this pre-process image, you may provide your findings on MGG instead of your original data. This way, you can run the streamiline on-the-fly version of `microbetag` for bigger datasets. 

- `microbetag` stand-alone tool. This is the most elevated way to access `microbetag`'s features. It is the one allowing you to move beyond the precalculations of the GTDB reference genomes and the `microbetagDB`, and instead, implement our approach on your own genomes, bins/MAGs, genome annotations or even Genome Scale Models. 
 -->

## Where to get what

  - `MGG` app: 
    - The app <a href="https://apps.cytoscape.org/apps/mgg" target="_blank">on your Cytoscape</a>
    - <a href="https://github.com/ermismd/MGG" target="_blank">Source code</a> for the app

  - `microbetag_prep` tool:
    - The tool <a href="https://hub.docker.com/r/hariszaf/microbetag_prep" target="_blank">on DockerHub</a>
    - <a href="https://github.com/hariszaf/microbetag/tree/preprocess" target="_blank">Source code</a>

  - `microbetag` stand alone: 
    - The tool <a href="https://hub.docker.com/r/hariszaf/microbetag" target="_blank">on DockerHub</a>
    - <a href="https://github.com/hariszaf/microbetag/" target="_blank">Source code</a>

  - `microbetagDB`: 
    - <a href="https://github.com/hariszaf/microbetag/tree/microbetagdb" target="_blank">Source code</a>
    - Key data products <a href="https://zenodo.org/records/10562677" target="_blank">on Zenodo</a>



## Install `MGG` Cytoscape 


  To start using *microbetag* and/or to visualize *microbetag*-annotated networks, you need first, to make sure you have **Cytoscape** on your system; if not, go ahead and [download Cytoscape](https://cytoscape.org/download.html). 

  Then, you need to install the *microbetag* app (`MGG`) from [Cytoscape App store](https://apps.cytoscape.org/apps/mgg).
  Make sure **you first launch Cytoscape** and then visit Cytoscape Appstore.
  If you have already visited the MGG page on Cytoscape Appstore, **launch Cytoscape and refresh the Cytoscape Appstore page**.
  You should now see the **Install** button.

  ![mgg install](_static/img/install_button_mgg.png)

  By clicking it, it will be automatically integrated on your Cytoscape. 
  If you visit Cytoscape Appstore and you have not lunched Cytoscape, you will see a *Download* button instead of the *Install*.
  As already mentioned, we suggest you lunch Cytoscape and refresh the page. 
  Otherwise, you can click the **Download** button and move manually the `.jar` file to the apps folder of your Cytoscape.

  You can also get `MGG` from within Cytoscape by clicking on the `Apps` tab of the main bar and then `App  Store > Show App Store` and typing `microbetag` on the box that pops up.

  Once the app is installed, you may click on the `Apps` tab, and you will find *MGG* there.

  ![mgg_overall](_static/img/app/mainMenu.png)



## Install stand-alone `microbetag`

  If you are interested in running `microbetag` with your own genomes, or if you would like to go for any 
  of its features independently, you need to install the actual `microbetag` pipeline, and its several dependencies. 

  To this end, you may build its Python library from its [source code](#locally) or its [containerized versions](#as-a-container). 
  Yet, you may also access `microbetag` through a [Nextflow pipeline](#as-a-nextflow-pipeline).

  In all cases, you need to make sure that besides `microbetag` itself, you also have access to:

  - KOFAM database for KEGG Orthology annotations -- if you plan to run the KEGG annotation step
  
  In case you build `microbetag` from source code locally, you may add the `--kofam` in the `setup_environment.sh` script call,
  and it will automatically download the KOFAM database for you.
  Otherwise, you may download it manually by running the following commands:

  ```
    cd ext_data/kofam_database
    wget -c ftp://ftp.genome.jp/pub/db/kofam/ko_list.gz 
    wget -c ftp://ftp.genome.jp/pub/db/kofam/profiles.tar.gz 
    gzip -d ko_list.gz &&\
    tar zxvf profiles.tar.gz 
  ```
  - A [Gurobi license](#install-gurobi-license) -- if you plan to run the GEM reconstruction step using `carveme`
  - (optional) [a CPLEX license](#install-cplex) -- if you plan to run the GEM reconstruction step using `gapseq` with CPLEX solver


### .. as a Nextflow pipeline

  The easiest, most straight-forward approach to access the stand-alone version of `microbetag` is as a Nextflow pipeline. 

  To get started, you need first to make sure you have [Nextflow](https://www.nextflow.io/) installed on your system.
  If not already available, you may follow instructions 
  <a href="https://www.nextflow.io/docs/latest/getstarted.html#installation" target="_blank">here</a>.

  Then, you need to make sure you have `Docker` or `Singularity/Apptainer` installed on your system.
  If not already available, you may follow instructions 
  <a href="https://docs.docker.com/get-docker/" target="_blank">here</a> 
  for `Docker` or 
  <a href="https://docs.sylabs.io/guides/3.0/user-guide/installation.html" target="_blank">here</a> 
  for `Singularity` and <a href="https://apptainer.org/docs/admin/main/installation.html" target="_blank">here</a> for `Apptainer`.

  In case you are working on a HPC system, `Singularity` and/or `Apptainer` most likely would already be available, while Docker would not be an option.


  After you have `Nextflow` and a containerization technology installed, you may get the `microbetag` Nextflow pipeline by running: 

  ```bash
      git clone https://github.com/msysbio/microbetag
  ```

  Then, you may run `microbetag` by executing either the `precalc.nf` or the `net_annotate.nf` workflow, located under the `nf/workflows/` folder of the cloned repository, following instructions [here](./tutorials_local/nf.md).




### .. locally

  To install the `microbetag` stand-alone tool locally, you need first to make sure you have `conda` or `miniconda`.
  If not already available, you may follow instructions 
  <a href="https://docs.anaconda.com/miniconda/" target="_blank">here</a>.


  Then, you need to clone or download _microbetag_'s source code locally and fire a bash script 
  that will build the required environments for the different _microbetag_ modules: 

  ```bash
      git clone https://github.com/hariszaf/microbetag.git

      cd microbetag

      bash setup_environment.sh
  ```


  _microbetag_ depends on several software packages that often have co-exclusive depdencies. 
  To address this challenge, _microbetag_ makes use of different `conda` environmets for each of these packages. 
  Therefore, once the `setup_environment.sh` script is complete, you should have the folllowing list of `conda envs`:

  * `microbetag`       : a Python 3.10 based environment; the basic environment for the _microbetag_ pipeline 
  * `mtg-phenotrex`    : for predicting genome-based phenotypic traits with <a href="https://phenotrex.readthedocs.io/en/latest/usage.html" target="_blank">`phenotrex`</a>
  * `mtg-modelseedpy`  : for genome-scale metabolic network reconstruction with [ModelSEEDpy] (https://modelseedpy.readthedocs.io/en/latest/){target="_blank"}
  * `mtg-dnngior`      : for gap-filling draft reconstructions with <a href="https://github.com/MGXlab/DNNGIOR/" target="_blank">DNNGIOR</a>


  Even most of the dependencies can be installed at the user level, 
  to enable the 
  <a href="https://www.bv-brc.org/docs///cli_tutorial/rasttk_getting_started.html" target="_blank">RASTtk</a>, 
  there are some Perl requirements that if not already available, they do require to be installed by your admin, 
  i.e. requiring sudo rights.
  Also, <a href="https://itsfoss.com/gdebi-default-ubuntu-software-center/" target="_blank">gdebi</a> 
  is required for installing `RASTtk`.

  ```{note}
  The `setup_environment.sh` script will build two `conda` environments:
  - one for running the phenotrex tool alone, called `phendb`
  - a second for all the rest requirements and the main `microbetag` features, called `microbetag`

  The software installed, e.g. Prodigal, HMMER etc, will be installed under your `$HOME`:

      cd
      ls .microbetag
      /home/my_user/.microbetag

  ```


  ```{danger}
  We have noticed a weird behavior on MacOS when installing `phenotrex` locally. 
  In case the `setup_environment.sh` script fails, you may try to install dependecies required 
  on MacOS for `phenotrex` based on the error message you get,
  and then try to continue the `microbetag` installation. 
  **Remember** to install phenotrex in the `phendb` conda environment.
  ```

### .. as a container

  A Docker image for `microbetag` is available, and we have successfully tested it using Singularity as well.
  For installing either of those, check the [below](#containerization-technologies-docker-and-singularityapptainer) for more.

  Assuming Docker is available, you may get `microbetag` simply by running: 

    docker pull hariszaf/microbetag:<version>

  In case `<version>` is blank, Docker will pull the latest version of `microbetag`.

  ```{note}
  As discussed in the tutorial for running [`microbetag` locally](./tutorials_local/local.md), a **configuration 
  YAML file** is required. 
  Make sure to obtain this from the 
  <a href="https://github.com/msysbio/microbetag/tree/develop/config_files" target="_blank">`microbetag` GitHub repository</a> 
  and ensure it matches the version of `microbetag` you are using.
  ```



## Install `microbetag_prep` tool

  In case of **amplicon** datasets that cannot be analyzed directly on-the-fly, you can perform the 
  computationally heavy task of:

  - the network inference through FlashWeave as well as 
    
  - the taxonomy annotation against 
  <a href="https://zenodo.org/records/6655692" target="_blank">a GTDB-specific (v.207) 16S rRNA database</a>

  locally, using the `microbetag_prep` tool.

  The latter, makes optimizes the matching of a taxonomy to a genome on `microbetag`. 


  Then, download the `microbetag_prep` image either by running: 


  ```bash
      docker pull hariszaf/microbetag_prep:<version>
  ```


  or 
  ```bash
      singularity pull docker://hariszaf/microbetag_prep:<version>
  ```


## Further dependencies 

### Containerization technologies: Docker and Singularity/Apptainer


Most of `microbetag`'s modules are available as containers too. 

So far, we have tested them using:

* 🐳 [Docker](https://docs.docker.com/get-docker/) 

* ⚡[Singularity](https://docs.sylabs.io/guides/3.0/user-guide/installation.html): specified for HPC systems


### Install `gurobi` license

  If you are about to run `microbetag` locally and reconstruct Genome Scale Reconstructions (GENREs) 
  based on your own genomes/bins/MAGs, `microbetag` wraps two widely used approaches: 

  - **using `modelseedpy`:** 

    this approach requires a RAST annotation of your bins which depends on a successful connection to the RAST server. 
    It makes use of the 
    <a href="https://modelseed.org" target="_blank">ModelSEED resource</a> 
    and its identifiers,
    but so-far it can be a rather time-consuming step and quite often unsuccessful, due to RAST-related issues.
    
    ```{note}
    `moodelseedpy` is currently under active development, and we anticipate that this approach will become 
    more robust in the near future.
    ```
    

  - **using `carveme`:** 
    
    that can be performed in both DNA and protein sequences, make use of the 
    <a href="http://bigg.ucsd.edu" target="_blank">BiGG identifiers</a> 
    and required a Gurobi license (see section [GEM reconstruction step](advanced_use/local.md#gem-reconstruction-step))

  Both approaches benefit a lot from solvers, such as `gurobi`; `carve` actually requires one to run 
  (either Gurobi or CPLEX).

  In the following sections we provide some links on how to get a Gurobi license (for academics): 

    - locally

    - for using it on a container

#### .. on a local system

  We found 
  <a href="https://www.youtube.com/watch?v=oW6ma8rdZk8" target="_blank">this video</a> 
  (released on 2022) quite helpful on how to get a Gurobi license. 

  Your license is a `gurobi.lic` file. To check that your Python can actually use the license, you may run:

  ```bash
      conda activate microbetag
      python
  ```

  and then 

  ```python
      >>> import gurobipy as gbp
      >>> m = gurobipy.Model()
      Set parameter Username
      Academic license - for non-commercial use only - expires 2025-04-15
  ```

#### .. on a container

  When you are using `microbetag` stand-alone tool as a container, 
  you will need a different kind of Gurobi license, 
  one called 
  <a href="https://www.gurobi.com/downloads/" target="_blank">**Web License Service (WLS)**</a>
  Gurobi license.

  You may find the following 
  <a href="https://support.gurobi.com/hc/en-us/community/posts/4406485885841-Installing-Gurobi-on-a-Docker-container-Ubuntu" target="_blank">link</a> 
  useful on how to do that.


  After you get your WLS, it will be again be a `gurobi.lic` file, you need to **mount** it on the `microbetag` container.
  For example, assuming you have the `gurobi.lic` file in the folder you are running the following `docker` command from:

  ```bash
      docker run --rm -it  \
          --volume=./tests/dev_io_microbetag/:/data \
          --volume=./microbetagDB/ref-dbs/kofam_database/:/microbetag/microbetagDB/ref-dbs/kofam_database/ \
          --volume=gurobi.lic:/opt/gurobi/gurobi.lic:ro \
          --entrypoint /bin/bash  \
          hariszaf/microbetag:v1.0.2
  ```

  Note that `microbetag` is looking for the license under `/opt/gurobi/`.
  

### Install CPLEX

[IBM ILOG CPLEX Optimization Studio](https://www.ibm.com/products/ilog-cplex-optimization-studio)

Jump to [IBM login](https://login.ibm.com/) page. 
If you do not have an account already, create one by clicking on the _Create an IBMid_


![alt text](image.png)



https://academic.ibm.com/a2mt/downloads/data_science#/


https://ronennir.medium.com/installing-cplex-optimization-studio-on-ubuntu-20-04-53e234ca4ec2


https://www.youtube.com/watch?v=o8plELhkazU


