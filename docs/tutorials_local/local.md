---
title: On your own genomes
layout: default
parent: Additional tutorials
nav_order: 3
description: "an example case of how to run microbetag using your own bins/MAGs"
---


# `microbetag` using custom genomes


This is the main versioning scheme for `microbetag`. 
The version of this tutorial is in line with the one of the documentation page.

<div style="display: flex; gap: 10px;">
   <a href="https://hub.docker.com/r/hariszaf/microbetag" class="btn-green"> Docker image </a>
   <a href="https://github.com/hariszaf/microbetag/tree/user-bins/tests/dev_io_microbetag" class="btn-purple"> Tutorial files </a>
</div>



```{note}
This tutorial is for advanced users that have some basic experience working on a terminal. 
 
Contrary to previous cases, this scenario is not performed from within the CytoscapeApp.

The user needs to run `microbetag` first on their computing environment (personal computer, HPC etc.) and then load the returned annotated network to Cytoscape.
```

<!-- > You may find the input files we are using for this tutorial in the `user-bins` branch of `microbetag`s GitHub repo, under the [`tests/dev_io_microbetag` folder](https://github.com/hariszaf/microbetag/tree/user-bins/tests/dev_io_microbetag).
>  -->

In the [Cytoscape App tutorial](../basic_usage//abd_only.md), our sequences were already taxonomically assigned before running `microbetag` and their taxonomies were mapped to representative GTDB genomes.
`microbetag` then used these genomes for the annotation steps.

However, in case of shotgun metagenomics one may end up with their own bins while further refinement of the latter can lead to Metagenome-Assembled Genomes (MAGs).
In case of high quality MAGs, i.e. high completeness and low contamination, they can be used directly for the annotation steps of `microbetag`. 
Yet, this requires computing resources and time much higher than those that our web-server can support.

Thus, we provide a version of `microbetag` as a stand-alone, containerized tool so that users can annotate a co-occurrence network using their own bins/MAGs.
To do that, you need first to make sure you have either [Docker](https://docs.docker.com/get-docker/) or [Singularity](https://docs.sylabs.io/guides/3.0/user-guide/installation.html)/[Apptainer](https://apptainer.org/docs/user/latest/quick_start.html) in the computing system to be used for running `microbetag`.
The last is common in HPC systems and if you are about to use such a system, you should ask your admin for more information.

On top of the abundance table and your genomes/bins/MAGs, to go for this case you need:
* Docker / Singularity (containerization technology)
* the `microbetag` image based on the containerization technology you are using (see below for how to get `microbetag` as a [Docker](#using-docker) or a [Singularity](#using-singularityapptainer) image)
* the `config.yml` file where you set the parameters for how to run `microbetag`
 <!-- that you may get from our [GitHub repo](https://github.com/hariszaf/microbetag/blob/user-bins/tests/dev_io_microbetag/config.yml) or download it directly from [here][1] -->

Running `microbetag` using your own genomes/bins/MAGs requires **significant** computing time and/or resources.
In this tutorial, we will use a very short number of bins (7) to showcase the various steps `microbetag` implements. 
Yet, it still gets more than a couple of hours to go through all the different steps to get all the possible supported annotations.
In our experience, memory (RAM) requirements should not be a challenge; memory would be an issue only with really large networks. 
`microbetag` is more often than not thread-limited, i.e. it needs computing power to go through the annotation steps. 

```{important}
**INPUT FILES USED IN THIS TUTORIAL**

 A complete example of running `microbetag` locally using the `modelseedpy` library for GEM reconstruction with all the intermediate files produced can be found in the [`dev_io_microbetag`](https://github.com/hariszaf/microbetag/tree/user-bins/tests/dev_io_microbetag) folder of the `user-bins` branch on the GitHub repo.
 
In the initial run, there are only 3 input files:
 - the <a href="{{ site.url }}/microbetag/download/local/config.yml" download="config.yml"><code>config.yml</code></a> file; allows you to set all the relative parameters for `microbetag` to run
<!-- [`config.yml`][1] file; allows you to set all the relative parameters for `microbetag` to run -->
 - an **abundance table** (following the format of the Cytoscape app tutorial) called [`thirty_Samples.tsv`][2], and
 - its corresponding edge list ([`edgelist.csv`][3])

 **Remember!**

 The config and the abundance table files are **mandatory**. 
 Always keep those (and the edge list if available) in the root of your input/output folder; i.e. in the path you set as your `io_path` in the `config.yml` file.
```

## Input and `config.yml` files

The `config.yml` file is rather important as it is the one that allows you to set your `microbetag` run.
A number of the parameters there correspond to tools that are invoked while others have to do with alternative routes that `microbetag` can follow for the annotation of the network. 
Read **carefully** the `description` of each argument before setting a value. 
Here, we highlight some of them. 


- `abundance_table_file`: path to your abundance table; the abundance table needs to follow the instructions for any abundance table to be used with `microbetag`, i.e., sequence identifier in the first column, sample names in the first row and a 7-level taxonomy in the last column; of course, you may provide the output of the[ `microbetag` preprocessing step](./prep.md) as an abundance table. 

- `input_type_for_seed_complementarities`: This is a **key parameter** for running `microbetag` locally; based on whether you already have annotated your genomes (either using other software or from previous runs of `microbetag`) you can use different input files as the starting point for getting the seed complementarities. The `sequence_files_for_reconstructions` parameter is strongly related to this. 
For example, if you have already GEMs reconstructed based on your genomes, you may set this to `input_type_for_seed_complementarities` to `models` and then, provide the folder name with your GEMs in the `sequence_files_for_reconstructions` parameter (e.g. `my_xmls`). Likewise, if you do not have GEMs, but you already have RAST annotations, you may set `input_type_for_seed_complementarities` to `proteins_faa` and give the path to those in the `sequence_files_for_reconstructions` parameter.

- `seed_complementarity`: since this is the most time and resource consuming step, the user may choose not to go for it. By setting this to `Fasle`, none of the steps for GEMs reconstruction or seed complementarity inference will be performed.


- `flashweave_args`: all the arguments under this umbrella term are related to how `FlashWeave` will perform, check on the [FAQs](../faq.md#when-to-enable-the-sensitive-and-heterogeneous-arguments) but also the [FlashWeave GitHub repo](https://github.com/meringlab/FlashWeave.jl) for more.

```{note}
Please, go through the parameters of the `config.yml` file carefully and make sure you keep this file in your `io_path`.
```

## Output 

In the `config.yml` file, you can set the location of your input files using the `io_path` parameter. 
Additionally, you can specify the `output_directory`, which is the name of the folder that will be created within the `io_path` to store all the output files generated by `microbetag`.
Here we discuss the folders and the files you will find under the `output_directory`.
We dot not always follow the order with which the files are generated. 



### The annotated `.cx` network file

The main output file (end proudct) of `microbetag` can be found in the `output_directory` you set in your `config.yml` file; the `microbetag`-annotated network called `microbetag_annotated_network.cx`.
This is the file you need to [load in your Cytoscape](./load.md) and then after enabling the MGG visual style and the MGG results panel you can investigate your annotated network! 
This file is in [`.cx2`](https://cytoscape.org/cx/cx2/specification/cytoscape-exchange-format-specification-(version-2)/) format. 



### FAPROTAX
A folder called `faprotax` is made where there is a subfolder, called `sub_tables` and a file whith the sum of the abundances of the taxa found with a specific process in each sample , called `functional_otu_table.tsv`. 
In the `sub_tables` folder, a file for each process is available mentioning the genomes/bins found related with the process udner study and their relative abundance per sample. 

For example, the `aerobic_nitrite_oxidation.txt` looks like: 

| record |  seqId |   sample1 | sample2 | sample4 | sample5 | sample6 | sample7 | sample8 | sample9 | sample10 | sample11 | sample12 | sample13 |
| :----:|:-------:|:---------:|:-------:|:--------:|:-------:|:------:|:--------:|:------:|:-------:|:--------:|:--------:|:---------:|:-------:|
| d__Bacteria;p__Proteobacteria;c__Alphaproteobacteria;o__Rhizobiales;f__Xanthobacteraceae;g__Nitrobacter;s__Nitrobacter sp001896955 | bin_32  | 43 |  10 | 56  | 73 | 9 | 58 | 54 | 46 | 9  | 40 | 42 | 81 |
| d__Bacteria;p__Proteobacteria;c__Alphaproteobacteria;o__Rhizobiales;f__Xanthobacteraceae;g__Nitrobacter;s__Nitrobacter sp001897285 | bin_223 | 47 |  87 | 69  | 64 | 25| 95 | 40 | 71 | 16 | 78 | 52 | 40 |



### phenDB-like

- `train.genotype` file: this is the output of the `phenotrex` program annotating your genomes/bins with COG families using the latest 

- `predictions` folder: within this folder, a file with the predictions for presence/absence of each trait in each of our genomes along with a confidence score are available. For example, the `symbiont.prediction.tsv ` file, in our test case looks like: 

|# Trait: Symbiont|             |             |   
|:---------------:|:-----------:|:-----------:|
|Identifier	      |Trait present|	Confidence|
|bin_101.fa	      | NO	        | 0.643      |
|bin_151.fa	      | NO	        |  0.6395    |
|bin_19.fa	      | NO          |  0.869     |
|bin_38.fa        | NO	        |  0.8678    |
|bin_41.fa	      | NO	        |  0.7842    |
|bin_45.fa	      | YES	        |  0.7954   |
|bin_48.fa	      | NO	        |  0.8545   |



### ORFs

`microbetag` invokes `prodigal` to extract Open Reading Frames (ORFs). 
It creates a folder called `ORFs` in the `output_directory` and for each genome/bin it returns 3 files: 
- `.gbk`: Genbank-like format (for more information check [here](https://www.insdc.org/submitting-standards/feature-table/))
- `.faa`: the reading frames as aminoacid sequences
- `.ffn`: the reading frames as nucleic acid sequences


```{note}
**SKIP THE ORFs PREDICTION (`prodigal`) STEP**
 
If you have already calculated the ORFs of your genomes before start using `microbetag`, you can create a folder within your `output_directory` called `ORFs` and move there all your `.faa` files.
 This way, `microbetag` will be using those instead of running `prodigal`.

 You `.faa` files should look like this:


    >c_000000001749_1 # 2 # 913 # 1 # ID=1_1;partial=10;start_type=Edge;rbs_motif=None;rbs_spacer=None;gc_cont=0.479
    DDSKIHQLGWDAFQAGTKVAKEEGLYGAGQDLLSDAFSGNVKGLGPAVAELSFEERPSEP
    FLFFMADKTEPGAYNLPFYLSYADPMYNPGLMLSPKMGKGFVFTVMDVENTENDRIIELT
    TPEDIYDLACLLRDNGRFVVESIRSAKTGETTAVCSTTRLNKIAGEYVGKDDPVALARVQ

```


### KEGG annotations 

`microbetag` makes use of the `hmmsearch` tool and the `kofam_database` profiles to check which KOs are present in each of your genomes.
In the `output_directory`, `microbetag` creates a folder called `KEGG_annotations` and there it builds a folder called `hmmout`, where it keeps all the 24.728 `.hmmout` files for each genome.  
Once all the `.hmmout` files are there for all the genomes/bins under study, `microbetag` builds a file called `ko_merged.txt` based on the DiTing implementation, that looks like this:

| bin_id	|    contig_id                       |	ko_term     |
|:---------:|:----------------------------------:|:------------:|
| bin_41	| SCN18_26_2_15_R1_F_scaffold_115_57 |	K07586      |
| bin_48	| SCN18_26_2_15_R4_B_scaffold_93_80	 |  K08086      |
| bin_41	| SCN18_26_2_15_R1_F_scaffold_206_63 |	K03503      |

This file is the main component for `microbetag` to proceed with the pathway complementarity step. 


```{tip}
**SKIP THE KEGG ANNOTATION (`HMMSEARCH`) STEP**
 
If you have already hmm profiles either from analysis before using `microbetag` or from previous `microbetag` runs of your genomes, you can create a folder called `hmmout` within the `KEGG_annotations` folder of your `output_directory` and move all the `.hmmout` profiles of your bins there. 
An `.hmmout` file would looks like:

    root@8649bd465c24:/data/microbetag_local/KEGG_annotations/hmmout# more K00005.bin_101.hmmout 
    #                                                               --- full sequence ---- --- best 1 domain ---- --- domain number estimation ----
    ># target name        accession  query name           accession    E-value  score  bias   E-value  score  bias   exp reg clu  ov env dom rep inc description of target
    #------------------- ---------- -------------------- ---------- --------- ------ ----- --------- ------ -----   --- --- --- --- --- --- --- --- ---------------------
    c_000000006615_9     -          K00005               -            1.2e-98  327.2   0.0   1.4e-98  327.0   0.0   1.0   1   0   0   1   1   1   1 # 14663 # 15772 # 1 # ID=74_9;partial=00;start_type=TTG;rbs_motif=AGGAGG;rbs_spacer=5-10bp;gc_cont=0.449
    #
    # Program:         hmmsearch
    # Version:         3.4 (Aug 2023)
    # Pipeline mode:   SEARCH
    # Query file:      /microbetag/microbetagDB/ref-dbs/kofam_database/profiles/K00005.hmm
    # Target file:     /data/microbetag_local/ORFs/bin_101.faa
    # Option settings: hmmsearch -o /dev/null --tblout /data/microbetag_local/KEGG_annotations/hmmout/K00005.bin_101.hmmout -T 324.27 --cpu 1 /microbetag/microbetagDB/ref-dbs/kofam_database/profiles/K00005.hmm /data/microbetag_local/ORFs/bin_101.faa 
    # Current dir:     /microbetag
    # Date:            Mon Aug  5 11:06:08 2024
    # [ok]

 If you already have the `ko_merged.txt` file, you can only add a copy of it in the `KEGG_annotations` folder (the `hmmout` files are not necessary in this case) and `microbetag` will use this directly skipping the `hmmsearch` step. 
```




```{hint}
**COMPUTING TIME, RESOURCES AND STORAGE**

Running `microbetag` locally using your own genomes/bins/MAGs can take significant computing time and resources.
In this tutorial, we use only a short number of bins that has almost no biological significance.
What we want to accomplish here is to make sure that you can run `microbetag` locally.
Indicatively, using a Linux machine and allocating 2 CPUs it took more than 1 hour for the KO annotation of just those 7 bins.
Running the complete workflow could get up to 6-7 hours based on the approach you will choose to reconstruct your GEMs. 
 
`carveme` is much more robust in running smoothly and faster since it does not require a RAST connection (see following paragraph). 
```


## GEM reconstruction step

`microbetag` supports 2 ways to reconstruct GEMs based on the user's genomes/bins: 
1. using the [`modelseedpy`](https://github.com/ModelSEED/ModelSEEDpy) Python library
2. using the [`CarveMe`](https://carveme.readthedocs.io/en/latest/) tool 


In the first case, `modelseedpy` requires [RAST](https://rast.nmpdr.org)-annotated genomes.
`microbetag` can do that on its own starting from your genome sequences; alternative, you may provide these to be used for the GEM reconstruction directly if you already have them
(either from previous `microbetag` runs or from other software).

```{note}
`modelseedpy` needs to establish a connection to the RAST server (`RastClient()`)
In some cases, based on the status of the RAST server, we have observed that time errors may occur. 
In this case, `microbetag` will exit and force a restart of its running on its own! 
Yet, it is a good practice to also check its status when the `modelseed` reconstruction step is running.
```
In the following paragraphs, we highlight how to go for different scenarios of GEMs reconstruction using different file types as initial starting points. 
One need to combine 2 parameters of the `config.yml` file to specify those scenarios: the `input_type_for_seed_complementarities` where one specifies the file type and the `sequence_files_for_reconstructions` that points to the directory where the files to be used are located.



### using `modelseedpy` and your bins 

in this case, you have set 

- `input_type_for_seed_complementarities` as `bins_fasta`, and 
- `sequence_files_for_reconstructions` is blank
- `genre_reconstruction_with` as `modelseedpy`

Then, `microbetag` will use [`RASTtk` programs](https://www.bv-brc.org/docs///cli_tutorial/rasttk_getting_started.html) to RAST annotate the original genomes/bins. 
In the `output_directory`, a folder called `reconstructions` has been built and in this case, 3 files for each genome/bin are now available:

- `.gto` and `.gto_2`: these are genome typed object, i.e. JSON files that are compatible with KBase. The `.gto_2` is a second genome typed object with all the RAST annotation data.
- `.faa` includes the same information as the `.gto_2` file, but we export the protein translations in `.fasta` format

```{note}
For our 7 genomes/bins this step may take about 1 hour depending on your computing system
```



### using `modelseedpy` and your already RAST annotated genomes

Assuming you already have the `.faa` files coming from the `rast-tk` package, you may use them directly by setting 

- `input_type_for_seed_complementarities` as `proteins_faa`, and 
- `sequence_files_for_reconstructions` as the path to the folder with your `.faa` files
- `genre_reconstruction_with` as `modelseedpy`

In this case, `microbetag` will have to establish connections with the RAST client like before. 

```{note}
If your annotated genomes include the DNA sequences instead of the protein ones (`.fna` files) you may use them by setting the 
`input_type_for_seed_complementarities` as `coding_regions`.
```


### using `carveme`

- `input_type_for_seed_complementarities` as `bins_fasta`
- `sequence_files_for_reconstructions` is blank
- `genre_reconstruction_with` as `carveme`

In this case, under the `reconstructions` file, we have a `.tsv` file for each genome/bin with the findings of the `diamond` against the internal database of `carveme` with the BiGG reactions. 

|              |                 |       |     |      |     |     |      |    |      |            |        |
|:------------:|----------------:|------:|----:|-----:|----:|----:|-----:|---:|-----:|-----------:|-------:|
| bin_151.peg.3 |  iLJ478.TM0057 |  57.9 | 309 | 125  |  3  |  6  | 310  | 2  | 309  | 2.72e-128  |  369   |
| bin_151.peg.3 |  iLJ478.TM1063 |  55.9 | 311 | 130  |  3  |  7  | 310  | 3  | 313  | 5.36e-124  |  358   |

For a thorough description of each column, you may check this [here](https://github.com/bbuchfink/diamond_docs/blob/master/1%20Tutorial.MD).




### GEMs already available

In this case, you may use your GEMs directly for the seed complementarities inference by setting:

- `input_type_for_seed_complementarities` as `models`
- `sequence_files_for_reconstructions` pointing to directory with the `.xml` files
- `genre_reconstruction_with` can be left blank or any value; it will not be considered




### PhyloMInt post process

After `microbetag` performs `PhyloMInt`, it runs a step to post-process the seed and the non seed sets as initially returned by:
- removing compounds from seed sets that are related to environmental metabolites that can be produced in several ways within the cell.
- removing from non seed sets compounds that cannot be produced in any other way than from entering the cell from the environment.

The numbers of this post process are recorded in the `log.tsv` file that can be found under the `seed_complementarity` folder that looks like this:

|model_id | environmental_initial_seeds | non_environmental_initial_seeds | total_initial_seeds | updated_seeds | initial_non_seeds | updated_non_seeds |
|:-------:|:---------------------------:|:-------------------------------:|:-------------------:|:-------------:|:-----------------:|:-----------------:|
| bin_151 |            173              |                57               |            230      |      230      |        879        |       879         |
| bin_38  |            177              |                54               |            231      |      231      |       1211        |      1211         |
| bin_101 |            152              |                51               |            203      |      203      |        845        |       845         |

This post process step is necessary since we use a complete medium to gapfill the model. 

```{note}
One may come with alternative procedures on how to gap fill in terms of minimising the missing potential cross-feedings, but at the same time not over-predicting such cases.
```



## Using Docker 

Once you have installed Docker locally, you may run 

```bash
docker pull hariszaf/microbetag:v1.0.2
```

to get microbetag locally.

```{important}
**Version is essential!**
 
Please, make sure you are aware of the version you are using. 
Latest versions may fix reported bugs or have new features. 
It is important to always be aware of the version you are using and report it when you are about to submit any issues. 

```
Then, you need to get a copy of the `kofam` database to allow the annotation of your sequences with KEGG ORTHOLOGY terms. 
You may get this by running the following chunk of code: 


```bash 
mkdir kofam_database &&\
    cd kofam_database &&\
    wget -c ftp://ftp.genome.jp/pub/db/kofam/ko_list.gz &&\
    wget -c ftp://ftp.genome.jp/pub/db/kofam/profiles.tar.gz &&\
    gzip -d ko_list.gz &&\
    tar zxvf profiles.tar.gz 
```


Now, you need to [download][1] the `config.yml` file that accompanies `microbetag`, to set the values to the required and optional arguments of your choice. 

In this file, each argument has a `required` field that denotes whether it is mandatory to be set or not. 

One may provide just an abundance table and the corresponding bins/MAGs sequence files.

```{hint}
**FILENAMES**

The filenames of your bins/MAGs need to have the same name, like those in your abundance table.
For example, if in the abundance table you have bin101, then the corresponding filename of the bin should be bin101.fa or bin101.fasta etc.
This will soon be changed so a mapping file can be used instead. 
Until then though `microbetag` will fail if that is not the case. 
```


In case you do not already have GENREs for your bins/MAGs, `microbetag` supports two ways for the reconstruction of metabolic networks: 
- using `modelseedpy` that required RAST annotation of your bins and are based on the [ModelSEED resource](https://modelseed.org) and identifiers, 
- using `carveme` that can be performed in both DNA and protein sequences, make use of the [BiGG identifiers](http://bigg.ucsd.edu) and required a Gurobi license (see section [GEM reconstruction step](./local.md#gem-reconstruction-step))
This can be a rather time-consuming step, especially using `modelseedpy`.

As you may already have gene predictions for your bins/MAGs, or even protein annotations, you may also provide them to `microbetag`, so those steps can be skipped. 
If you have already built metabolic networks, then in case they are based on either ModelSEED or BiGG identifiers, you may provide them so seed scores and seed complementarities can be 
computed directly on them.



```{hint}
**Input folder**

To conclude, your input folder to be mounted will look like this:

    u0156635@gbw-l-l0074:microbetag$ ls 
    config.yml
    my_bins/
    my_abundance_table.tsv


where in the `my_bins` folder you have:


    u0156635@gbw-l-l0074:microbetag$ ls bins/
    bin_101.fa
    bin_151.fa
    bin_19.fa

```

Once your input folder is ready, you can mount it on your Docker container and run `microbetag`: 

```bash
docker run --rm -it  \
    --volume=./tests/dev_io_microbetag/:/data \
    --volume=./microbetagDB/ref-dbs/kofam_database/:/microbetag/microbetagDB/ref-dbs/kofam_database/ \
    --volume=$PWD/gurobi.lic:/opt/gurobi/gurobi.lic:ro \
    --entrypoint /bin/bash  \
    hariszaf/microbetag:v1.0.2
```

The `--volume` flag allows you to mount a local directory to a specific path in the container.
It is **essential** that the **right** parts of the volumes are kept as above! 
For example, when using `carveme`, a gurobi license is required; `microbetag` expects the license unde the `/opt/gurobi` path, so you need to make sure all the right parts of the volumes are as above and that the left parts point to your local paths. 

```{important}
**Remember!** It is strongly suggested all the files and folders you mount to be part of your root path; meaning the directory from which you initiate your Docker container. 

For example, if you observe the last chunk of code, you will notice that both `kofam_database` and `gurobi.lic` and the input-output folder called `dev_io_microbetag` they are all within my root folder
`~/github_repos/KU/microbetag` from where I run the `docker run` command.

```

```{note}
A Web License Service (WLS) [Gurobi license](https://www.gurobi.com/downloads/) in case you are about to use `carveme`.
You may find the following [link](https://support.gurobi.com/hc/en-us/community/posts/4406485885841-Installing-Gurobi-on-a-Docker-container-Ubuntu) useful on how to do that.
```

Once you have fired a container, you can now run `microbetag` using the following command:

```bash
root@20510f8400f1:/microbetag# python3 microbetag.py /data/config.yml 
```



## Using Singularity/Apptainer

These technologies are widely used in High Performance Computing (HPC) systems. 
In case you are about to use `microbetag` in such a system, you first need to build a Singularity image (`.simg`) based on the Docker one:

```bash
sudo singularity build microbetag_v102.simg docker://hariszaf/microbetag:v1.0.2
```

You will need to have sudo rights to run this command. 
If you do not have `sudo` rights, you can either ask your admin to do so or run the build command in a similar environment, e.g. your own Linux based laptop and move it to the HPC with a single `scp` command.
Also, you can ask your admin or check your HPC documentation site how they deal with Docker images and follow their lead. 

Once a `.simg` image is available, you may run `microbetag` again by mounting the necessary paths:

```bash
singularity exec 
    -B tests/dev_io_microbetag/:/data  
    -B microbetagDB/ref-dbs/kofam_database/:/microbetag/microbetagDB/ref-dbs/kofam_database/
    -B $PWD/gurobi.lic:/opt/gurobi/gurobi.lic:ro  
    microbetag_v101.simg 
    python3 /microbetag/microbetag.py /data/config.yml
```

[1]:../_static/download/local/config.yml
[2]:../_static/download/local/thirty_Samples.tsv
[3]:../_static//download/local/edgelist.csv

