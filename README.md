# microbetag: preprocessing

`microbetag` attempts to be a microbial interactions co-occurrence network annotator.
To support the analysis of large datasets (i.e., with more than 1,000 sequence identifiers - ASVs, OTUs, bins etc.)
we provide a Docker image (`microbetag_prep`) so the user can run the computational expensive steps of the analysis locally and then ask from microbetag to annotate the network returned. 

The `microbetag_prep` supports 2 tasks:
 - `16s_gtdb_taxonomy_assign`: the classification of their amplicons (OTUs, ASVs) using the 16S GTDB sequences as reference database. This will allow `microbetag` to get the best matches possible between the user's data and the genomes available on microbetagDB 
 - `build_network`: the building of a co-occurrence network using FlashWeave. In this case, the user needs also to set their parameters; see [here](https://hariszaf.github.io/microbetag/docs/faq/#what-is-sensitive-and-heterogeneous-in-flashweave) what they stand for.

> IMPORTANT!
>
> For the case of less than 1,000 sequence identifiers, `microbetag` would annotate a network even if their taxonomy scheme was not GTDB-like. 
> However, this is not the case for large datasets. 
> To this end, please make sure you always have a GTDB taxonomy when you are about to perform a `microbetag` analysis with large datasets.
> This taxonomy annotation is possible thanks to a [dada2 formatted file](https://zenodo.org/records/6655692) including GTDB reference sequences of 31,319 bacteria and 1,565 archaea full 16S rRNA gene sequences


A tutorial on how to use the `microbetag_prep` is available on `microbetag`'s [documentation page](https://hariszaf.github.io/microbetag/docs/tutorials/prep/).



## Prepare your data for `microbetag`!

### Installation

If [Docker](https://docs.docker.com/get-docker/) is not already in your system, you need to get it!

Once Docker is installed, you can get the `microbetag_prep` by running: 

```bash
docker pull hariszaf/microbetag_prep:<version_tag>
```

If `<version_tag>` is empty, then you are about to pull the latest version of the image. 
If you like a specific version, you need to specify it by replacing `<version_tag>` with the version of your choice, e.g. `v1.0.1`.




### Run `microbetag_prep`

You need to create a folder (let's call it `test` folder) that will be mounted in your running container. 

> Background tip
>
> A running Docker container can be considered as a virtual machine. In this case, you need to make sure that your machine, your computer, is able to reach this virtual machine so it can provide it your input files and get back its outcome. You are able to do that by *mounting* a local directory to one in the container. 

In your `test` folder the user need to include a `config.yml` file, a template of that can be found [here](./test/config.yml).
The user needs to describe what they need through the `config.yml` file. 
Thus, give the filename of their abundance table, set which tasks need to be performed and set their according parameters if any. 

In case you would like to provide a metadata file to be considered for building the co-occurrence network, please have a look [here](https://hariszaf.github.io/microbetag/docs/input/#input-files).

Once you have a valid `test` folder, you are ready to run the preprocessing:

```bash
docker run --rm -it -v /<users_input_folder>/:/media hariszaf/prep_microbetag
```

This command will fire a container and the preprocessing will start instantly. 
When it is completed, in the `test` directory you will find a new folder with the name you set in the `output_directory` argument of the `config.yml` file. 
Based on the tasks asked, you will find:
- `GTDB_tax_assigned_abundance_table.tsv`: your abundance table with their corresponding GTDB taxonomies
- `network_output.edgelist`: a 3-column tab delimited file


Alternatively, you can fire a container in an **interactive** way by running instead: 
```bash
docker run --entrypoint /usr/bin/bash  \
            --rm -it -v /<users_input_folder>/:/media hariszaf/prep_microbetag
```

You can have a look around:
```bash
root@81ae5787c526:/pre_microbetag# pwd
/pre_microbetag
root@81ae5787c526:/pre_microbetag# ls
classify.R  flashweave.jl  gtdb_16s.RData  prep.py
root@81ae5787c526:/pre_microbetag# ls /media
config.yml  prep_output  test.csv  test.tsv
```

and you can also edit the scripts there. For example

```bash
vim flashweave.jl
```
would open the file so you can edit it. 
**Remember!** If you edit something within the container, your edits will be lost once you exit the container!



## Contact

For hints on how to use `microbetag`, ideas for new features and bug reports find us on out [Matrix space](https://matrix.to/#/#microbetagcommunity:matrix.org).
If you do not have a Matrix account, it’s only two clicks away! For more, you may check [here](https://matrix.org/docs/chat_basics/matrix-for-im/).


## Cite

In prep.


## Funding

This project is funded by an [EMBO Short-Term Fellowship](https://www.embo.org/funding/fellowships-grants-and-career-support/scientific-exchange-grants/) and 
the [3D’omics](https://3domics.eu) Horizon project (101000309).

## License

*microbetag* is under [GNU General Public License v3.0](https://opensource.org/license/gpl-3-0). For third-party components separate licenses apply. The MGG CytoscapeApp is under [Apache License, Version 2.0](https://opensource.org/license/apache-2-0).

<!-- docker run --rm -it -v ./test:/media --entrypoint  /usr/bin/bash hariszaf/microbetag_prep -->