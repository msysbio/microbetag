
# Run `microbetag` as a Nextflow workflow 


## Overview with an example dataset

This tutorial will guide you through running `microbetag` as a [Nextflow](https://www.nextflow.io/) pipeline. 

We provide an example dataset under the [`data/genomes`](./data/genomes) folder, which contains 3 genomes in FASTA format; this is what we call a _genome catalogue_.

* The `precalc.nf` workflow of `microbetag` computes all pairwise relationships between genomes of a catalogue. 

* Then, the `annotate.nf` workflow, infers a network, if one is not provided, and uses these pre-calculations to annotate the network.

Under the [`test-precalc`](./test-precalc/) folder, you will find the pre-calculations obtained after running the `precalc.nf` workflow on the example genomes,
while under the [`test-annotate`](./test-annotate/) folder, you will find the results obtained after running the `annotate.nf` workflow using these pre-calculations and an example abundance table.

The [`test.cx2`](./test-annotate/test.cx2) file contains the annotated network in CX2 format and you may load it to Cytoscape and parse it using the MGG app.

In the following sections, we will guide you through the requirements needed to run `microbetag` as a Nextflow pipeline.

Take extra care in the [Nextflow configuration](#nextflow-configuration) section, since you may need to edit this part based on your computing environment.


## Requirements

Both modules, sub-workflows and workflows, they can all be performed either using [Docker](https://www.docker.com/) or [Singularity](https://sylabs.io/singularity/)/[Apptainer](https://apptainer.org/).


To run `microbetag` this way, you need to install: 

1. [Nextflow](https://www.nextflow.io/docs/latest/install.html)
2. One of the containerization methods mentioned, usually based on the computing system to be used:

     - Local PC/laptop: [Docker](https://www.docker.com/get-started/)
     - HPC: [Singularity](https://docs.sylabs.io/guides/3.0/user-guide/installation.html)/[Apptainer](https://apptainer.org/docs/admin/main/installation.html)


If you are interested in [Pathway Complementarity](https://microbetag.readthedocs.io/en/latest/modules/modules.html#pathway-complementarity), and you do not have KEGG ORTHOLOGY annotation for your genomes already, 
you would have to get the KOFAM database on your computing environment. 

To do so, you may run:

    wget -c ftp://ftp.genome.jp/pub/db/kofam/ko_list.gz 
    gzip -d ko_list.gz

    wget -c ftp://ftp.genome.jp/pub/db/kofam/profiles.tar.gz     
    tar zxvf profiles.tar.gz 

Last, if you are interested in [Seed Complementarity](https://microbetag.readthedocs.io/en/latest/modules/modules.html), and you do not have already Genome-Scale Metabolic Models (GEMs) for your genomes,
you would have to get a [Gurobi Web License Service (WLS) license](https://www.gurobi.com/features/academic-wls-license/), if you ask `microbetag` to use CarveMe to reconstruct them, or (optionally) CPLEX. 


### The HPC case

If you are about to run this on an HPC, we suggest you download first the images you will need. 
To do this, make sure you have access to Singularity/Apptainer. 
For example, if these are on a [module](https://hpc-wiki.info/hpc/Modules), you may need to load the corresponding module first. 

Then, you need to choose where to store the images. For this, you may need to advise from your admin, or you may set one of your choice. 

For example, in your personal account, the 
`${HOME}/.singularity/mtg-images`

Then, you may run 

```
./get_sif.sh 
```
which, by default, will use `${HOME}/.singularity/mtg-images`. 

Otherwise, you may specify where with the `-sif-dir` flag: 

```
./get_sif.sh --sif-dir /opt/sing/mtg-images
```

Once you have the images, you will have to set the containerization method to Singularity or Apptainer 
as shown in the [Nextflow configuration](#nextflow-configuration) section.
Moreover, you may need to specify extra environmental variables about either Singularity/Apptainer or Nextflow. 
For example, 

    SINGULARITY_TMPDIR
    SINGULARITY_CACHEDIR
    NXF_SINGULARITY_CACHEDIR
    NXF_TEMP

Make sure you follow your admin's instructions for how to use Nextflow and Singularity/Apptainer. 

Last, please run: 

    mkdir $HOME/julia_depot $HOME/julia_tmp

This is needed for the Julia installation inside the Singularity/Apptainer containers to work properly.



## Workflows

Two main [**workflows**](./workflows/): 

1. catalog pre-calculations ([`precalc.nf`](./workflows/precalc.nf))
2. network annotation using a selected pre-calculation folder ([`annotate.nf`](./workflows/annotate.nf))


These workflows are built on [**modules**](./modules/) and [**sub-workflows**](./subworkflows/), which one may run individually. 


### `precalc` workflow: One-time Precalculation

Run the `precalc` workflow once to compute all pairwise relationships between genomes in your genomes catalog.

This generates a comprehensive database of precomputed results (similarities, interactions, etc.)

### `annotate` workflow: Multiple Annotation Sessions

Reuse the precalculated database to annotate multiple networks from different abundance tables

> It is essential that the species present in your abundance table or network, to be among those of the catalog!


## Configuration 

When running `microbetag` through Nextflow, there are **two** configuration levels, corresponding to **two** different files: 

- nextflow configuration, through the [`nextflow.config`](./nextflow.config) file
- `microbetag` configuration, through the [`precalc.yaml`](./workflows/precalc.yaml) and the [`annotate.yaml`](./workflows/annotate.yaml) files correspondingly 
 


### Nextflow configuration 

In the Nextflow configuration level, one need to make sure that Nextflow will use the containerization technology (container engine)
available in their system. 

You can edit this, by setting to `true` and/or `false` the `enabled` flag of theirs.
For example, in this case here, we have selected to use Docker:

```
docker.enabled    = true
apptainer.enabled = false
singularity {
    enabled    = false
    autoMounts = true
    cacheDir   = "${HOME}/.singularity/mtg-images/"
    runOptions = getHPCBinds()
}
```

**Attention!** 

In the [HPC case](#the-hpc-case), we set the `--sif-dir`;
which, by default, is `${HOME}/.singularity/mtg-images/`.

If you have used another one, please make sure you update the `cacheDir` argument over here too!


### `microbetag` configuration 

At this level, you are interested in setting things right so `microbetag` goes for the steps you wish to, 
uses your own input data and so on. 

In the [`precalc.yaml`](./workflows/precalc.yaml), one may set the name of the output directory with all the 
pre-calculations to be returned, specify the directory to their genomes or their protein annotation files (`.faa`)
and the number of threads the workflow is able to use. 

Then, they can set as `true` or `false` the three different pre-calculation types `microbetag` currently supports:

- genome-based phenotypic predictions (`phenotrex`)
- pathway complementarity (`pathway_compl`)
- seed complementarity (`seed_compl`)

to specify which pre-calculations you wish to go for.


Each of those come with some intermediate files, that the user may already have from previous `microbetag` runs, 
or from other annotation tools. 

For example, `phenotrex` has the `genotype_file`, which consists of the genome id in the first column,
and the COG ids found in the genome in the second one:
```
#feature_type:eggNOG5-tax-2
D300443:bin_000002.fa   COG1040 COG0329 COG4636 COG1373 COG4461 COG2202 COG2084 COG3600 COG3449 COG1715 COG3645 COG1246 COG0803 COG3437 COG0270 COG0657 COG2309 COG4123 COG0154 COG1454 COG0561 COG1284 COG2984 COG3613 COG3711 COG0624 COG4
```

If you already have this, you may provide the path to it, otherwise leave the parameter blank. 

In case you wish to go for `seed_compl`, you need to make sure you have a [Gurobi Web License Service (WLS) license](https://www.gurobi.com/features/academic-wls-license/), have a copy of it on your system and provide the path to it in the `gurobi_lic` parameter.
Since we can have up to 5 parallel sessions with the WLS license of Gurobi, which is the only way to go on with a Docker container, we set by defalt max_forks to 5.
Then, our input files will be split in chunks of max_forks size for parallel processing.


## Run..

### .. workflows

We have completed the [`precalc.yaml`](./workflows/precalc.yaml) file assuming you have:
- your genomes under the [`data/genomes`](./data/genomes/) folder 
- the KOFAM database under [`data/kofam_database/`](./data/kofam_database/), and 
- a Gurobi LWS license in this folder

Now, you can run the workflow with the following command: 

```
nextflow run workflows/precalc.nf \
    -params-file workflows/precalc.yaml \
    -entry MICROBETAG_PRECALC
```

> **Attention**
> 
> Like before, in case you are using a HPC, you need to make sure you have access to Nextflow and to Singularity/Apptainer. 
> That means that if you write an SBATCH script for example, you may need to load their corresponding modules before the nextflow command. 


Similarly, one may run the network annotation workflow with the follwoing:

```
nextflow run workflows/annotate.nf \
    -params-file workflows/annotate.yaml \
    -entry MICROBETAG_ANNOTATE 
```

In this case, we have filled in the [`annotate.yaml`](./workflows/annotate.yaml) file, 
assuming we are using the pre-calculations built from the command above, i.e. the `test-precalc` folder as our `precalculations`, and using a `test_catalogue.tsv` that as our `abundance table`, expected to be under `data/abd_data/`.

Again, the
- `faprotax`
- `phen_traits`
- `path_compl`, and
- `seed_compl`
can be set as `true` or `false` based on whether you wish to annotate your co-occurrence network with that annotation type or not. 

When you set one of those as `true`, then you need to also provide its corresponding parameters; 
for example, in case you set `faprotax` as `true`, you should provide the `taxonomy_colname` and the `delimiter` arguments as well. 
Otherwise, you may leave the corresponding parameters blank.


### .. sub-workflows

Similarly, one may run our sub-workflows. Make sure you edit their corresponding parameter files [`pc.yaml`](./subworkflows/pathway_complementarity/pc.yaml) and [`sc.yaml`](./subworkflows/seed_complementarity/sc.yaml) files accordingly.

```
nextflow run subworkflows/pathway_complementarity/main.nf \
    -params-file subworkflows/pathway_complementarity/pc.yaml \
    -entry PATHWAY_COMPLEMENTARITY
```

```
nextflow run subworkflows/seed_complementarity/main.nf \
    -params-file subworkflows/seed_complementarity/sc.yaml \
    -entry SEED_COMPLEMENTARITY
```


## .. modules

Last, one may run modules individual [modules](./modules/). For example:

```
nextflow run modules/faprotax/main.nf -params-file modules/faprotax/faprotax.yaml 
```

You may notice that in this case we do not specify an `-entry`, like in the (sub-)workflows.

The only module that would require an `-entry` would be phenotrex:

```
nextflow run modules/phenotrex/main.nf -params-file params/phenotrex.yaml -entry PHENOTREX
```

> In case of the [`mtg_annotate`](./modules/mtg_annotate/mtg_annotate.nf), use only the `-config` case. 

You can edit the parameters file you will find under [`params`](./params) accordingly, to better tune modules based on the needs of your data.




<!-- 

## Notes

Inside a workflow/process scope, `def x = ...` is interpreted as:

> Declare a local variable named `ko_list_ch` AND also shadow/override `Channel` symbol resolution.

Then `Channel.fromPath` is misinterpreted as:

> There is a variable named `Channel` defined here -->

