# Configuration file

All config files per microbetag stand-alone version. 

Consider these configuration files as templates and set the parameters described there properly to 
best describe what you wish to do. 

> Attention! 
>
> It is **essential** to use the correct version of `config.yml` file with the one of `microbetag`.
> It is most likely `microbetag` will fail if you use different versions of the stand-alone version and the configuration file.

Keep in mind that microbetag will not override or remove any files of those built so it's always a good practice 
to use the same output directory if you have an error, edit your config and run again

microbetag may get several starting points, either abundance table, or a network or both 
also, it may start having KEGG annotations or not, GEMs already built or not and so on and so forth.

We try to keep this as flexible as possible but for now, microbetag does has some constraints on the intermediate folders built. 
So **please never change the architecture** of its output folder as it allows to microbetag to start over again when something fails.
An example of this architecture is here:

```bash
tests/dev_io_microbetag/microbetag_run_carve/
├── faprotax
│   ├── functional_otu_table.tsv
│   └── sub_tables
│       ├── aerobic_chemoheterotrophy.txt
│       ├── aerobic_nitrite_oxidation.txt
│       ├── animal_parasites_or_symbionts.txt
│       ├── arsenite_oxidation_energy_yielding.txt
│       ├── chemoheterotrophy.txt
..
├── KEGG_annotations
│   ├── hmmout
│   └── ko_merged.txt
├── microbetag_annotated_network.cx
├── ORFs
│   └── README.md
├── pathway_complementarity
│   ├── alts.json
│   ├── pathCompls.json
│   └── pathway_complements_extended.json
├── predictions
│   ├── ac.prediction.tsv
│   ├── aerobe.prediction.tsv
│   ├── anaerobe.prediction.tsv
│   ├── AOB.prediction.tsv
│   ├── a_saccharolytic.prediction.tsv
│   ├── auto_co2.prediction.tsv
..
├── reconstructions
│   ├── bin_101.faa
│   ├── bin_101.ffn
│   ├── bin_101.out
│   ├── bin_101.tsv
│   ├── bin_151.faa
│   ├── bin_151.ffn
│   ├── bin_151.out
│   ├── bin_151.tsv
│   ├── bin_19.faa
│   ├── bin_19.ffn
│   ├── bin_19.out
│   ├── bin_19.tsv
│   ├── bin_38.faa
│   ├── bin_38.ffn
│   ├── bin_38.out
│   ├── bin_38.tsv
│   ├── bin_41.faa
│   ├── bin_41.ffn
│   ├── bin_41.out
│   ├── bin_41.tsv
│   ├── bin_45.faa
│   ├── bin_45.ffn
│   ├── bin_45.out
│   ├── bin_45.tsv
│   ├── bin_48.faa
│   ├── bin_48.ffn
│   ├── bin_48.out
│   ├── bin_48.tsv
│   └── GENREs
│       ├── bin_101.xml
│       ├── bin_151.xml
│       ├── bin_19.xml
│       ├── bin_38.xml
│       ├── bin_41.xml
│       ├── bin_45.xml
│       └── bin_48.xml
├── seeds_complementarity
│   ├── confidenceDic.json
│   ├── log.tsv
│   ├── nonSeedSetDic.json
│   ├── phylomint_scores.tsv
│   ├── SeedSetDic.json
│   ├── updatedBiggNonSeedsDic.json
│   ├── updatedBiggSeedsDic.json
│   ├── updated_nonSeedsDic.json
│   └── updated_SeedsDic.json
└── train.genotype
```
