---
title: On your own genomes
layout: default
parent: Tutorials
nav_order: 1
description: "an example case of how to run microbetag using your own bins/MAGs"
---





## Using your own bins/MAGs 

{: .note}
> For advanced users. Contrary to the previous scenario, this case is not performed from within the CytoscapeApp.
>
> The user needs to run microbetag first on their computing environment (personal computer, HPC etc.) and then load the returned annotated network to Cytoscape. 


In the first tutorial, our taxonomically assigned sequences were mapped to representative GTDB genomes and microbetag used those for the annotation steps. 

However, in case of shotgun metagenomics binning of the contigs and further refinement can lead to Metagenome-Assembled Genomes (MAGs). 
In case of high quality MAGs, i.e. high completeness and low contamination, they can be used directly for the annotation steps of microbetag. 
Yet, this requires computing resources and time much higher than those that a web-server can support. 

Thus, we provide a version of microbetag as a stand-alone, containerized tool so that users can annotate a co-occurrence network using their own sequences. 
To do that, you need first to make sure you have either [Docker](https://docs.docker.com/get-docker/) or [Singularity](https://docs.sylabs.io/guides/3.0/user-guide/installation.html)/[Apptainer]() in the computing system to be used for running microbetag. 
The last is common in HPC systems and if you are about to use such a system, you should ask your admin for more information.


### Using Docker 


Once you have installed Docker locally, you may run 

```bash
docker pull hariszaf/microbetag:v1.0.0
```

to get microbetag locally.


Then, you need to get a copy of the kofam database to allow the annotation of your sequences with KEGG ORTHOLOGY terms. 
You may get this by running the following chunk of code: 


```bash 
mkdir kofam_database &&\
    cd kofam_database &&\
    wget -c ftp://ftp.genome.jp/pub/db/kofam/ko_list.gz &&\
    wget -c ftp://ftp.genome.jp/pub/db/kofam/profiles.tar.gz &&\
    gzip -d ko_list.gz &&\
    tar zxvf profiles.tar.gz 
```


Now, you need to [download][2] the `config.yml` file that accompanies microbetag, to set the values to the required and optional arguments of your choice. 

In this file, each argument has a `required` field that denotes whether it is mandatory to be set or not. 

One may provide just an abundance table and the corresponding bins/MAGs sequence files.

{: .important-title}
> FILENAMES
>
> The filenames of your bins/MAGs need to have the same name like those in your abundance table.
> For example, if in the abundance table you have bin101, then the corresponding filename of the bin should be bin101.fa or bin101 fasta etc.
> This will soon be changed so a mapping file can be used instead. 
> Until then though microbetag will fail if that is not the case. 


The most time-consuming step is the reconstruction of metabolic networks. 
Thus, the *seed complementarity* step is optional, and you can skip it. 
Also, there are two ways to go for it: 
- using `modelseedpy` that required RAST annotation of your bins and are based on the [ModelSEED resource](https://modelseed.org) and identifiers, 
- using `carveme` that can be performed in both DNA and protein sequences, make use of the [BiGG identifiers](http://bigg.ucsd.edu) and required a Gurobi license (see section []())


As you may already have gene predictions for your bins/MAGs, or even protein annotations, you may also provide them to microbetag, so those steps can be skipped. 
If you have already built metabolic networks, then in case they are based on either ModelSEED or BiGG identifiers, you may provide them so seed scores and seed complementarity can be 
computed directly on the, 


To conclude, your input folder to be mounted will look like this:

```bash 
u0156635@gbw-l-l0074:microbetag$ ls 
config.yml
my_bins/
my_abundance_table.tsv
```

where in the `my_bins` folder you have:

```bash 
u0156635@gbw-l-l0074:microbetag$ ls bins/
bin_101.fa
bin_151.fa
bin_19.fa
..
```

### Using Singularity/Apptainer

These technologies are widely used in High Performance Computing (HPC) systems. 
In case you are about to use microbetag in such a system, you may 


[1]:{{ site.url }}/microbetag/download/seq_ab_tab.tsv

[2]:{{ site.url }}/microbetag/download/config.yml


