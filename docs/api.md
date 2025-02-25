---
layout: default
title: Access *microbetagDB* through its API
---

# *microbetagDB* API

*microbetagDB* API provides programmatic access to the data.
Using the Application Programming Interface (API) you can access the *microbetagDB* directly to get information about PhenDB-like traits of a specific taxon, potential pathway complementarities of a taxa pair etc. 

The base address to the API is [https://msysbio.gbiomed.kuleuven.be/](https://msysbio.gbiomed.kuleuven.be/).

Below you may find the syntax to retrieve the various data and/or annotations included.

Remember that *microbetag* is a NCBI Taxonomy oriented resource. That means that a "species" of interest is a NCBI Taxonomy Id.
For example, if you are interested in *Bifidobacterium animalis*, you first need to go to the [NCBI Taxonomy portal](https://www.ncbi.nlm.nih.gov/taxonomy/) and get its corresponding id.
However, once you do so you get a list of subspecies and strains available. 
You can either use the species id or one of a specific strain in your queries. 

*microbetag* has a special feature called `get_children` as in some cases there is no genomic information for the species level, but there is at lower levels. 
For example, in case of *Bifidobacterium animalis*, *microbetagDB* has no genomes for its corresponding NCBI Taxonomy Id (28025) but it does have for the *Bifidobacterium animalis* subsp. animalis ATCC 25527 (703613). 
<!-- This example highlights the issues derived from the current taxonomy schemes as 
Even more interestingly, according to GTDB 
*Bifidobacterium canis* -->



## Get genome ids for a NCBI Taxonoy Id

To check whether a species is present on *microbetag*, one may find its corresponding **NCBI Taxonomy Id** and search for related genomes present on the *microbetagDB*. 

For example, assuming we are interested in the *Blautia hansenii* DSM 20583 strain, we find from NCBI Taxonomy that its corresponding id is [537007](https://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?id=537007).

Using the `ncbiTaxId-to-genomeId` route we may get the related genomes on *microbetagDB*:

```bash
curl -X GET https://msysbio.gbiomed.kuleuven.be/ncbiTaxId-to-genomeId/537007
```

that returns a list of genomes used in *microbetag* annotations:

```bash
{
  "537007": [
    "GCF_002222595.2"
  ]
}
```

In this case there is a genome available for this NCBI Taxonomy id (GCF_002222595.2).

If no genome is available, then you get an empty value. 

For example, for the *Bifidobacterium animalis* subsp. animalis IM386 (NCBI Tax id: 1402194) there is no genome in *microbetagDB*:

```bash
curl -X GET https://msysbio.gbiomed.kuleuven.be/ncbiTaxId-to-genomeId/1402194
{
  "1402194": []
}
```



## PhenDB-like traits

### Get phenotypic traits of a GTDB genome 

Once you have identified the genomes related to your NCBI Taxonomy id under study using the `ncbiTaxId-to-genomeId` route, you may get the corresponding phenotypic traits of that genome(s) using the `/phen-traits/` route and the corresponding **genome id**.

For example, in case of *Blautia hansenii* DSM 20583 (NCBI Taxonomy id: 537007) we saw there is a genome on *microbetagDB*; to get its phenotypic traits we can simply run:

```bash
curl -X GET https://msysbio.gbiomed.kuleuven.be/phen-traits/GCF_002222595.2
```

this would return (we show only a part of the outcome)

```bash
{
  "NOB": "NO",
  "NOBScore": "0.8078",
  "T3SS": "NO",
  "T3SSScore": "0.8391",
  "T6SS": "NO",
  "T6SSScore": "0.7836",
  "aSaccharolytic": "NO",
  "aSaccharolyticScore": "0.8672",
   ...
}
```

```{note}
For a thorough description of the abbreviations used, have a look in the *microbetag*'s [modules tab](modules/modules.md#based-on-phendb).
```

```{warning}
1. Currently, microbetag has annotations only for the GTDB representative genomes. Thus, genomes returned by the `ncbiTaxId-to-genomeId` route that come from other resources (e.g., MGnify, KEGG) do not have phenotypic tratis.
2. All genomes have a 3-letter prefix that is either GCA or GCG. In case a GTDB genome you are querying returns an "Internal Server Error", try again replacing that prefix; e.g. if you initially had "GCA_002222595.2", try again with "GCF_002222595.2". 
```

In case a genome id is provided for which there are no phenotypic traits on *microbetagDB*, you will get a message explaining this:

```bash
No Phen traits for the genome id asked.         
Make sure you are asking for a GTDB v202 representative genome.
```


## Get pathway complementarities

### Get pathway complementarities for a pair of genomes 

In case you are interested in the complementarities of a specific pair of GTDB representative genomes, where `genome_A` is the beneficiary and `genome_B` the donor, 
one may use the `genome-complements` route, followed by `genome_A`, followed by `genome_B`. 

Here is an example: we are interested in the pathway complementarities of a Desulfurococcaceae archeon genome (GCA_011364525.1) with on of the Gram-negative bacterium *Malikia spinosa* (GCA_002980625.1) as its potential donor:


```bash
curl -X GET https://msysbio.gbiomed.kuleuven.be/genome-complements/GCA_011364525.1/GCA_002980625.1
```

Here is its partial output:

```bash
{
  "beneficiary-genome": "GCA_011364525.1",
  "complements": {
    "0": {
      "coloured-map": "https://www.kegg.jp/kegg-bin/show_pathway?map00010/K25026%09%23EAD1DC/K15916%09%23EAD1DC/K00150%09%23EAD1DC/K00927%09%23EAD1DC/K15635%09%23EAD1DC/K01689%09%23EAD1DC/K00873%09%23EAD1DC/K21071%09%2300A898/K01624%09%2300A898/K01803%09%2300A898/",
      "complement": "K01803;K21071;K01624",
      "complete-alternative": "K25026;K15916;K21071;K01624;K01803;K00150;K00927;K15635;K01689;K00873",
      "module": "M00001"
    },
    "1": {
      "coloured-map": "https://www.kegg.jp/kegg-bin/show_pathway?map00010/K00150%09%23EAD1DC/K00927%09%23EAD1DC/K15635%09%23EAD1DC/K01689%09%23EAD1DC/K00873%09%23EAD1DC/K01803%09%2300A898/",
      "complement": "K01803",
      "complete-alternative": "K01803;K00150;K00927;K15635;K01689;K00873",
      "module": "M00002"
    },
    "2": {
      "coloured-map": "https://www.kegg.jp/kegg-bin/show_pathway?map00010/K01596%09%23EAD1DC/K01689%09%23EAD1DC/K15635%09%23EAD1DC/K00927%09%23EAD1DC/K00150%09%23EAD1DC/K01622%09%23EAD1DC/K01803%09%2300A898/",
      "complement": "K01803",
      "complete-alternative": "K01596;K01689;K15635;K00927;K00150;K01803;K01622",
      "module": "M00003"
    },
    ...
  },
  "donor-genome": "GCA_002980625.1"
}
```

Let us now describe its meaning. 
The `donor-genome` points to the genome of the potential donor species being processed.
Similarly, the `beneficiary-genome` points to the genome of the potentially beneficiary species. 
Under the `complements` key, you can find the different potential complements between those two genomes. 
In the above chunk we only show the first two. 
Each complement refers to a specific KEGG module, denoted in the `module` key.
Each complement entry, has also a `complement` key with the exact KO terms that the donor would have to provide, so the donor would have a complete alternative of the module. 
In the `complete-alternative` you can find all the KOs (both those the beneficiary carries on its own and those it would get from the donor) to have a complete alternative of the module under study. 
Last, the `coloured-map` key provides you the link to the KEGG map showing the module under study and the KO terms to be used; beneficiary's KOs are coloured with pink while those to get from the donor with green.



### Get complements for a pair of species 

You can get the complements between two taxa using their corresponding NCBI Taxonomy ids.

```
https://msysbio.gbiomed.kuleuven.be/complements/<BENEFICIARY_NCBI_TAX_ID>/<DONOR_NCBI_TAX_ID>
```

In this case, *microbetag* will use the corresponding GTDB genomes for the NCBI Taxonomy Ids you provide.
There are cases, where an NCBI Taxonomy Id may map to more than one GTDB genomes.

In the following example we use *Alcaligenes faecalis* (NCBI TaxId: 511) as the potential beneficiary and 
*Prochlorococcus marinus* str. AS9601 (NCBI TaxId: 146891) as the potential donor. 
In *microbetagDB* there are four genomes for *A. faecalis* but only one for the case of *P. marinus* str. AS9601. 
By running:

```bash 
curl -X GET https://msysbio.gbiomed.kuleuven.be/complements/511/146891
```

we get:

```bash
{
 "GCF_002443155.1": {
    "GCF_000015645.1": [
      [
        [
          "M00004",
          "K00033;K00036;K01057",
          "K00036;K01057;K00033;K01783;K01807;K00615;K00616;K01810",
          "https://www.kegg.jp/kegg-bin/show_pathway?map00030/K01783%09%23EAD1DC/K01807%09%23EAD1DC/K00615%09%23EAD1DC/K00616%09%23EAD1DC/K01810%09%23EAD1DC/K00036%09%2300A898/K01057%09%2300A898/K00033%09%2300A898/"
        ]
      ],
      ...
    ],
  
  },
  "GCF_004319585.1": {
    "GCF_000015645.1": [
      [
        [
          "M00002",
          "K00927",
          "K01803;K00134;K00927;K01834;K01689;K00873",
          "https://www.kegg.jp/kegg-bin/show_pathway?map00010/K01803%09%23EAD1DC/K00134%09%23EAD1DC/K01834%09%23EAD1DC/K01689%09%23EAD1DC/K00873%09%23EAD1DC/K00927%09%2300A898/"
        ]
      ],
      ...
}
```

As you may already noticed, `GCF_000015645` genome appears more than once.
That is since *microbetag* returns the complements between all the combinations of the genomes mapped to the NCBI Taxonomy Ids of the beneficiary (outer genome) and the potential donor (inner genome).
Therefore, in this case, since we have four genomes for the potential beneficiary, the outer genome changes but the inner (donor) stays the same in all four combinations returned. 

```{note}
*microbetagDB* has also a number of non-GTDB genomes (e.g. `afa`) in this example, which you may ignore. 
```


## Get seed scores and seed complements

### Get competition and complementarity score between a pair of NCBI Ids

When we calculate the seed scores, we consider both taxa as $species_A$ and $species_B$ 
(see on the [Modules tab](./modules/modules.md#seed-scores-and-complements-based-on-genome-scale-draft-reconstructions-gems) for more).


Like in the complements case, seed scores using all the corresponding genomes between 2 species/strains can be retrieved using their NCBI Taxonomy Ids and the `seed-scores` route:
```bash
https://msysbio.gbiomed.kuleuven.be/seed-scores/<NCBI_Taxonomy_Id_A>/<NCBI_Taxonomy_Id_B>
```

For example, let's check the scores between *Streptomyces* sp. AW19M42 (NCBI Taxonomy Id: 1379686) and *Afipia clevelandensis* ATCC 49720 (NCBI Taxonomy Id: 883079). By running:

```bash
curl -X GET https://msysbio.gbiomed.kuleuven.be/seed-scores/1379686/883079
```

we get

```bash
  "0": {
    "A": "1379686",
    "B": "883079",
    "scores": {
      "0": {
        "competition": "0.596",
        "cooperatiom": "0.209",
        "genome_A": "GCF_000470535.1",
        "genome_B": "GCF_000336555.1"
      }
    }
  },
  "1": {
    "A": "883079",
    "B": "1379686",
    "scores": {
      "0": {
        "competition": "0.647",
        "cooperatiom": "0.131",
        "genome_A": "GCF_000470535.1",
        "genome_B": "GCF_000336555.1"
      }
    }
  }
}
```
where, in the first case `[0]`, *Streptomyces* is considered as $$ speciesA $$ and *Afpia* as $$ speciesB $$, and in case `[1]` the other way around. 


If I run the same with the reverse order on the Tax Ids,
```bash
https://msysbio.gbiomed.kuleuven.be/seed-scores/883079/1379686/
```
then I get the same output only with a different order. 

Again, in case where a NCBI Taxonomy Id maps to several GTDB genomes, all combinations will be returned.

<!-- 
To get seed scores of a pair of GEMs, 
`seed-scores` route 

`genome_A` is the beneficiary and `genome_B` the donor, 
one may use the `genome-complements` route
 -->

### Get competition and complementarity scores between a pair of GEMs

In case you need the seed scores between two specific GEMs, meaning between the metabolic reconstruction that emerged from two specific GTDB reference genomes, you may run:


```bash
curl -X GET https://msysbio.gbiomed.kuleuven.be/genomes-seed-scores/GCF_000470535.1/GCF_000336555.1
```

which returns 

```bash
[
  [
    "GCF_000470535.1",
    "GCF_000336555.1",
    "0.596",
    "0.209"
  ],
  [
    "GCF_000470535.1",
    "GCF_000336555.1",
    "0.647",
    "0.131"
  ]
]
```

The function returns pairs of seed scores, the first genome provided is considered as $$ speciesA $$ for the seed metrics and the second one as $$ speciesB $$.

```{warning}
In its current version, our API is not clear enough, and you need to remember that the first entry considers the first genome as $$ speciesA $$ and the second genome as $$ speciesB $$, while in the second entry it is the other way around. This will be fixed in a future release. 
```

### Get seed complements between a pair of NCBI Taxonomy Ids, NCBI Genome or PATRIC ids

Seed complements can be retrieved for pairs of 3 different categories of ids: 
- NCBI Taxonomy ids (`type_of_ids: ncbiTaxonomyIds`)
- NCBI Genome accession ids (`type_of_ids: ncbiGenomeIds`) and
- PATRIC ids (`type_of_ids: patricGenomeIds`)

The main route of this feature is 
```bash
https://msysbio.gbiomed.kuleuven.be/seed-complements/<beneficiary_id>/<donor_id>/<type_of_ids>
```

For example, one might get seed complements for a pair of NCBI Taxonomy ids like this:

```bash
curl -X GET https://msysbio.gbiomed.kuleuven.be/seed-complements/1379686/883079/ncbiTaxonomyIds
```


```{note}
> This route has no default for your id type! If not provided by the user, the API will fail.
```



## Common errors

There are two common types of client errors on API calls:

- 400 Bad requests.

In this case, you most probably are asking a malformed request syntax, invalid request message framing, or deceptive request routing.
Check again your query and make sure you are u sing the right syntax.

- 404 Not found.

In this case, the server cannot find the requested resource. 

You can have such errors also in cases you are asking for a genome/species/pair of such that is not part of the *microbetagDB*. 

Keep in mind that you can always contact us through our [Matrix community](https://matrix.to/#/#microbetagcommunity:matrix.org) for more.
