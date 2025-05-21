# Tests for `microbetag` basic modules

  
- [Tests for `microbetag` basic modules](#tests-for-microbetag-basic-modules)
  - [For this `README` file](#for-this-readme-file)
  - [Infer co-occurrence network with FlashWeave (`test_flashweave` | IO)](#infer-co-occurrence-network-with-flashweave-test_flashweave--io)
  - [Literature based node annotation with FAPROTAX (`test_faprotax.py` | IO)](#literature-based-node-annotation-with-faprotax-test_faprotaxpy--io)
  - [Genome based node annotations using `phenotrex` predictions (`test_phenotrex.py` | IO)](#genome-based-node-annotations-using-phenotrex-predictions-test_phenotrexpy--io)
  - [Gene prediction using Prodigal (`test_prodigal.py` | IO)](#gene-prediction-using-prodigal-test_prodigalpy--io)
  - [KEGG ORTHOLOGY annotation (`test_kegg_annotation.py` | IO)](#kegg-orthology-annotation-test_kegg_annotationpy--io)
  - [Pathway complementarity extraction (`test_path_compl.py` | IO)](#pathway-complementarity-extraction-test_path_complpy--io)
  - [Genome-scale metabolic reconstruction with ModelSEED (`test_modelseed.py` | IO)](#genome-scale-metabolic-reconstruction-with-modelseed-test_modelseedpy--io)
  - [Genome-scale metabolic reconstruction with CarveMe (`test_carve.py` | IO)](#genome-scale-metabolic-reconstruction-with-carveme-test_carvepy--io)
  - [Seed complementarity extraction (`test_seed_compl.py` | IO)](#seed-complementarity-extraction-test_seed_complpy--io)
  - [Network clustering using `manta` (`test_manta.py` | IO)](#network-clustering-using-manta-test_mantapy--io)
  - [Building a CX2 `microbetag`-annotated network (`test_build_cx2.py` | IO)](#building-a-cx2-microbetag-annotated-network-test_build_cx2py--io)
  - [Complete `microbetag` run (`test_microbetag` | IO)](#complete-microbetag-run-test_microbetag--io)


## For this `README` file

  Under the [`tests`](../tests/) folder, there is a series of test files for the different `microbetag` features/modules.

  Under[`test_data`](../test_data/), you can find the input/output files of each test.
  In this README file, we explain what every test is supposed to test, what kind of input it expects and what it returns.

  Some tests have a pseudo-configuration file, **part of the one used when running the whole pipeline.**
  Yet, not all tests have such a YAML file in their input data.
  In some cases we just build a partial `Config` class on spot, i.e. on the test script. 

  > **Attention!** 
  > 
  > Configuration YAML files in these tests are **not following the `microbetag` versioning scheme**; only partially.
  > Changes from version to version will be fixed on those only if needed.
  > The `microbetag` version specific YAML files can be found under the [`config_files`](../config_files/) folder.

  Also, `unittest` performs test functions **alphabetically** not in the order on the script.


## Infer co-occurrence network with FlashWeave ([`test_flashweave`](../tests/test_flashweave.py) | [IO](./test_flashweave/))

  Runs FlashWeave with and without a metadata file. 

  Check input files of this test to make sure you give `microbetag` you data in the proper format.


## Literature based node annotation with FAPROTAX ([`test_faprotax.py`](../tests/test_faprotax.py) | [IO](./test_faprotax/))

  Builds the merged `functional_otu_table.tsv` and the `sub_tables` folder with the `.tsv` files per trait found, 
  as FAPROTAX does.


## Genome based node annotations using `phenotrex` predictions ([`test_phenotrex.py`](../tests/test_phenotrex.py) | [IO](./test_phenotrex/))

  Runs both`phenotrex` programs used in `microbetag`:

    - `genotype`

    This builds a single file called `train.genotype`; a tab-separated file with a header line and a single line 
    for each genome/bin to be analyzed, with its name in the first column 
    and the Clusters of Orthologous Groups of proteins (COGs) assigned to it in the second one:
    ```
    feature_type:eggNOG5-tax-2
    bin_101.fa      COG1432 COG0716 COG1381 COG2239 COG0010 COG0639 COG0738 COG1404 COG4430 COG2217 
    ```
    - `prediction` 

    This program returns a file for each of the [classes available](https://microbetag.readthedocs.io/en/v1.0.3/modules/phen-traits.html); 
    each file has a header line mentioning the trait under study; then it is a 3-column tab separated:
    ```
    # Trait: ac
    Identifier      Trait present   Confidence
    bin_101.fa      YES     0.6504
    ```

## Gene prediction using Prodigal ([`test_prodigal.py`](../tests/test_prodigal.py) | [IO](./test_prodigal))

  Runs the Prodigal gene predictor on a single bin (`.fa`) to build 3 files:
      - `.faa`
      - `.ffn`
      - `.gbk`


## KEGG ORTHOLOGY annotation ([`test_kegg_annotation.py`](../tests/test_kegg_annotation.py) | [IO](./test_kegg_annotation/))

  Takes as input a list of `.faa` files, as returned by the [gene prediction step](#gene-prediction-using-prodigal-test_prodigal)
  and also, a very small part of the `ko_list` file of the `kofam_database` ([ko_list_tests](../ext_data/kofam_database/ko_list_tests))
  that looks like:
  ```
  (microbetag) u0156635@gbw-l-l0074:kofam_database$ head ko_list_tests 
  knum    threshold       score_type      profile_type    F-measure       nseq    nseq_used       alen    mlen    eff_nseq        re/pos  definition
  K00001  363.33  domain  all     0.312178        2773    2310    2080    519     14.06   0.590   alcohol dehydrogenase [EC:1.1.1.1]
  K00002  438.50  domain  all     0.418181        2762    2642    6996    484     7.63    0.590   alcohol dehydrogenase (NADP+) [EC:1.1.1.2]
  ```
  and the actual Hidden Markov Models (HMMs) of the kofam database, called [`profiles`](../ext_data/kofam_database/profiles/). 
  In 


## Pathway complementarity extraction ([`test_path_compl.py`](../tests/test_path_compl.py) | [IO](./test_path_compl/))

  Only input for this test is a `ko_merged`-like file, based on the 7 bins we've been using across all the tests, 
  namely: `bin_101`, `bin_151`, `bin_19`, `bin_38`, `bin_41`, `bin_45`, `bin_48`.

  This file is the output of the `merge_ko()` you may check on the [`utils.py`](../microbetag/utils.py) function,
  and it looks like:

  ```bash
  (microbetag) u0156635@gbw-l-l0074:input_files$ head ko_merged_7bins.txt 
  bin_id  contig_id       ko_term
  bin_41  SCN18_26_2_15_R1_F_scaffold_115_57      K07586

  ```
  Then, the test will run actually 3 tests, and finally it will build 2 files:

  - `alternatives.json`: all different ways to have a KEGG MODULE
  - `complementarities.json`: potential complementarities between a beneficiary and a donor genome

  For example:
  ```bash
  {"bin_101": 
      {"bin_151": [
          ["md:M00019", ["K00826"], ["K01652", "K01653", "K00053", "K01687", "K00826"], "https://www.kegg.jp/kegg-bin/show_pathway?map00290/K01652%09%23EAD1DC/K01653%09%23EAD1DC/K00053%09%23EAD1DC/K01687%09%23EAD1DC/K00826%09%2300A898/"], .. 
      ], .. # more complements from donor bin_151
      }, .. # more donors
  # more beneficiaries
  }
  ```
  where `bin_101` is the beneficiary, `bin_151` the donor and the entry shown is the first of their list of potential complementarities:

  - `md:M00019`: the KEGG MODULE under study
  - `["K00826"]`: list of KOs provided by the donor
  - `["K01652", "K01653", "K00053", "K01687", "K00826"]`: the beneficiary's alternative being completed
  - `URL`: URL to the KEGG MAP that the module under study is part of with colored nodes the terms coming from the beneficiary and the complements


## Genome-scale metabolic reconstruction with ModelSEED ([`test_modelseed.py`](../tests/test_modelseed.py) | [IO](./test_modelseed/))

  In this test case, the `microbetag.genres.TestGEMSReconstruction` class takes as input a `.fasta` file, to build the following 
  files:

  - `bin_6.gto`: intermediate ModelSEED file standing for first step of the RAST annotation of the bin
  - `bin_6.gto_2`: like previous for the next step of the RAST annotation
  - `bin_6.faa`: RAST annotated genome
  - `GENRES/bin_6.xml`: draft ModelSEED reconstruction (final outcome)

  > `TestGEMSReconstruction` needs to have the `seed_complementarity` argument on the configuration file as `true` to initiate 
  > necessary variables for the class. This result to an empty directory called `seeds_complementarity` in the output directory.


## Genome-scale metabolic reconstruction with CarveMe ([`test_carve.py`](../tests/test_carve.py) | [IO](./test_carve/))

  Similar to the previous test, we provide 2 `.faa` files this time, and build GENREs using CarveMe.

  The test will result 2 `.xml` files in `reconstructions/GENRES` folder. 

  Like in the previous case, an empty folder called `seeds_complementarity` is part of the output directory because of the necessary 
  `seed_complementarity` argument in the configuration file.


## Seed complementarity extraction ([`test_seed_compl.py`](../tests/test_seed_compl.py) | [IO](./test_seed_compl/))

  Here we give a set of GEMs as input files, and we build a pseudo `Config`-like class on the test. 

  Using this pseudo `Config` class, we build 3 instances to run 3 tests: 

  - Case 1: calculating seed and non-seed sets and extracting complements
  - Case 2: using previously calculated seed, non-seed sets (from Case 1) to infer complements
  - Case 3: calculating seed and non-seed sets only, keeping the BiGG namespace that our GEMs use 

  ❗ By default, in case of GEMs using the BiGG namespace, `microbetag` attempts to map seed and non-seed compounds to ModelSEED identifiers 
  in order to retrieve the KEGG MODULES they participate in.

  ❗ You can see that the pseudo `Config` class sets among other fields the `genre_reconstruction_with` argument, equal to `carveme`.
  This is not to reconstruct GENRES here, but to let `microbetag` know that the namespace to be used is BiGG.

  The test script will then return a set of files: 

  - `SeedSetDic.json`: A JSON file with models basename (supposed to be the same with the sequence identifier in a complete pipeline run) with the list of its seeds as value. Example:
    ```
    {"GPB:bin_000083": ["glucan4", "cpd00709", "lmn2", "2agpe181",..],  }
    ```
      ❗ You may notice that some compounds have the `cpd` prefix, standing for ModelSEED compounds, 
      while others not, i.e. being in the BiGG namespace. 
      This is because our input models were built with CarveMe, thus using the BiGG namespace, and because `microbetag` 
      applied a filter to map them to ModelSEED. You 

  - `nonSeedSetDic.json`: A JSON file exactly like the `SeedSetDic.json` but with the non-seed sets of each model.

  - `confidenceDic.json`: A JSON file where keys are again the sequence identifiers and values are also dictionaries, where a seed compound 
    is the key and its value is the confidence level ($C$), ranging from 0 to 1. 
    A confidence level of 0 would correspond to a non-seed node, while a 1 would correspond to a seed that cannot be activated by another node.
    For more you may check 
    [here](https://microbetag.readthedocs.io/en/latest/modules/modules.html#seed-scores-and-complements-based-on-genome-scale-draft-reconstructions-gems).



  - `kegg_module_related_seeds.pckl`: A pickle file with all the seeds of the models under study found related to at least one KEGG MODULE.
    ```python 
    >>> import pickle
    >>> with open("kegg_module_related_seeds.pckl","rb") as f:
    ...     kegg_seeds = pickle.load(f)
    >>> kegg_seeds
                                                                  0
    GPB:bin_000083  [cpd00220, cpd00156, cpd01695, cpd00322, cpd00...
    ```

  - `kegg_module_related_nonseeds.pckl`: A similar pickle file but with the non-seed sets of the GEMs under study.


  - `seed_complements.pckl`: A pickle file with all pairwise seed complementarities among the input GEMs.

    ```python
    # After loading the pickle file as in the kegg_omdule_related_seeds.pckl case above
    >>> seed_compls
                                      GPB:bin_000083                      bin_101
    bin_101         [cpd00065, cpd00051, cpd01695...                          NaN
    GPB:bin_000083                               NaN     [cpd00724, cpd00134, ...]
    ```

  - `phylomint_scores.tsv`: A 4-column tab separated file (`.tsv`) with the $species_A$, $species_B$, Competition and Cooperation scores.
    ```bash
    (microbetag) myuser@localhost:output_files$ head phylomint_scores.tsv 
    GPB:bin_000083  bin_101 0.58    0.28
    bin_101 GPB:bin_000083  0.5     0.22
    ```


## Network clustering using `manta` ([`test_manta.py`](../tests/./test_manta.py) | [IO](./test_manta/))


  We run two tests, one using an abundance table as input data and a second one using a network. 

  In both cases, we get two output files:

  - `basenet.cyjs` : The initial network, before applying any clustering, in CYJSON version
    ([here](https://manual.graphspace.org/en/latest/GraphSpace_Network_Model.html#cyjs-format) a toy example).
    `microbetag` uses this as an intermediate file to fire clustering with `manta`.
  - `manta_annotated.cyjs`: This is the `manta`-clustered network. You can load it to Cytoscape directly.
    `microbetag` loads it when building the annotated network to assign clusters as node attributes.


## Building a CX2 `microbetag`-annotated network ([`test_build_cx2.py`](../tests/test_build_cx2.py) | [IO](./test_build_cx2/))


  This test expects a complete annotation set from `microbetag`, i.e.
    - `faprotax`
    - `phenotrex`
    - pathway and seed complementarities
    - `manta` clusters

  and parses them to build and save a CX2 network using the `ndex2` library.

  
  > **ATTENTION**
  >
  > This network will have all the annotations, but not the NCBI taxonomy level column required from `MGG` to recognize sequence IDs that 
  > have at least a genome mapped.


## Complete `microbetag` run ([`test_microbetag`](../tests/./test_microbetag.py) | [IO](./test_microbetag/))

  This test run the total `microbetag` pipeline with a set of 7 custom genomes -- **not on-the-fly**!

  This test takes hours when run completely from scratch, since it will try to predict genes over the genomes,
  perform KEGG, COG ANNOTATION on the genes, build GENRES and more. 

  To this end, this test **is not supposed to be part of any GitHub workflow for continuous integration tests or so.**

  However, it is strongly suggested for contributors, to run the test before opening a PR. 

  For the users, it is a fair example of how to run `microbetag` with your own data. 
  Also, you can have a thorough overview of the total `microbetag` data products! 

