Before running the prediiction step of phenotrex for the GTDB reference genomes,
classes were calculated from scratch using the training genomes set as provided by PhenDB as there was a conflict between the eggNOG version phenotrex uses at the prediction step and the one during the training of the classes as provided in the PhenDB site.

This process was perfromed at the Genius HPC of KU Leuven.

To make easier the matching of the accession ids, all the GCF prefixes. were turned into GCA.

phenotrex predict --genotype gtdb_genotypes/merged/all_gtdb.genotype --classifier RE_TRAINED_CLASSES/new_AOB.pkl > PHEN_PREDICTIONS/all_gtdb_AOB.csv
phenotrex predict --genotype gtdb_genotypes/merged/all_gtdb.genotype --classifier RE_TRAINED_CLASSES/new_ac.pkl > PHEN_PREDICTIONS/all_gtdb_ac.csv
phenotrex predict --genotype gtdb_genotypes/merged/all_gtdb.genotype --classifier RE_TRAINED_CLASSES/new_a_saccharolytic.pkl > PHEN_PREDICTIONS/all_gtdb_a_saccharolytics.csv
phenotrex predict --genotype gtdb_genotypes/merged/all_gtdb.genotype --classifier RE_TRAINED_CLASSES/new_auto_co2.pkl > PHEN_PREDICTIONS/all_gtdb_co2.csv
phenotrex predict --genotype gtdb_genotypes/merged/all_gtdb.genotype --classifier RE_TRAINED_CLASSES/new_butanol.pkl > PHEN_PREDICTIONS/all_gtdb_butanol.csv
phenotrex predict --genotype gtdb_genotypes/merged/all_gtdb.genotype --classifier RE_TRAINED_CLASSES/new_butyric_acid.pkl > PHEN_PREDICTIONS/all_gtdb_butyric.csv
phenotrex predict --genotype gtdb_genotypes/merged/all_gtdb.genotype --classifier RE_TRAINED_CLASSES/new_d_glucose.pkl > PHEN_PREDICTIONS/all_gtdb_d_glucose.csv
phenotrex predict --genotype gtdb_genotypes/merged/all_gtdb.genotype --classifier RE_TRAINED_CLASSES/new_d_lactic_acid.pkl > PHEN_PREDICTIONS/all_gtdb_d_lactic.csv
phenotrex predict --genotype gtdb_genotypes/merged/all_gtdb.genotype --classifier RE_TRAINED_CLASSES/new_ethanol.pkl > PHEN_PREDICTIONS/all_gtdb_ethanol.csv
phenotrex predict --genotype gtdb_genotypes/merged/all_gtdb.genotype --classifier RE_TRAINED_CLASSES/new_fermentative.pkl > PHEN_PREDICTIONS/all_gtdb_fermentative.csv
phenotrex predict --genotype gtdb_genotypes/merged/all_gtdb.genotype --classifier RE_TRAINED_CLASSES/new_fixing_n2.pkl > PHEN_PREDICTIONS/all_gtdb_fixinigN2.csv
phenotrex predict --genotype gtdb_genotypes/merged/all_gtdb.genotype --classifier RE_TRAINED_CLASSES/new_formic_acid.pkl > PHEN_PREDICTIONS/all_gtdb_formicAcid.csv
phenotrex predict --genotype gtdb_genotypes/merged/all_gtdb.genotype --classifier RE_TRAINED_CLASSES/new_halophilic.pkl > PHEN_PREDICTIONS/all_gtdb_halophilic.csv
phenotrex predict --genotype gtdb_genotypes/merged/all_gtdb.genotype --classifier RE_TRAINED_CLASSES/new_hydrogen.pkl > PHEN_PREDICTIONS/all_gtdb_hydrogen.csv
phenotrex predict --genotype gtdb_genotypes/merged/all_gtdb.genotype --classifier RE_TRAINED_CLASSES/new_indole.pkl > PHEN_PREDICTIONS/all_gtdb_indole.csv
phenotrex predict --genotype gtdb_genotypes/merged/all_gtdb.genotype --classifier RE_TRAINED_CLASSES/new_isobut.pkl > PHEN_PREDICTIONS/all_gtdb_isobut.csv
phenotrex predict --genotype gtdb_genotypes/merged/all_gtdb.genotype --classifier RE_TRAINED_CLASSES/new_l_lactic_acid.pkl > PHEN_PREDICTIONS/all_gtdb_l_lactic_acid.csv
phenotrex predict --genotype gtdb_genotypes/merged/all_gtdb.genotype --classifier RE_TRAINED_CLASSES/new_NOB.pkl > PHEN_PREDICTIONS/all_gtdb_nob.csv
phenotrex predict --genotype gtdb_genotypes/merged/all_gtdb.genotype --classifier RE_TRAINED_CLASSES/new_phototrophy.pkl > PHEN_PREDICTIONS/all_gtdb_phototrophy.csv
phenotrex predict --genotype gtdb_genotypes/merged/all_gtdb.genotype --classifier RE_TRAINED_CLASSES/new_r_acetoin.pkl > PHEN_PREDICTIONS/all_gtdb_r_acetoin.csv
phenotrex predict --genotype gtdb_genotypes/merged/all_gtdb.genotype --classifier RE_TRAINED_CLASSES/new_succinic_acid.pkl > PHEN_PREDICTIONS/all_gtdb_succinic_acid.csv
phenotrex predict --genotype gtdb_genotypes/merged/all_gtdb.genotype --classifier RE_TRAINED_CLASSES/new_symbiont.pkl > PHEN_PREDICTIONS/all_gtdb_symbiont.csv
phenotrex predict --genotype gtdb_genotypes/merged/all_gtdb.genotype --classifier RE_TRAINED_CLASSES/new_T6SS.pkl > PHEN_PREDICTIONS/all_gtdb_T6SS.csv
phenotrex predict --genotype gtdb_genotypes/merged/all_gtdb.genotype --classifier RE_TRAINED_CLASSES/new_isovaleric_acid.pkl > PHEN_PREDICTIONS/all_gtdb_isovaleric_acid.csv
phenotrex predict --genotype gtdb_genotypes/merged/all_gtdb.genotype --classifier RE_TRAINED_CLASSES/new_methanotroph.pkl > PHEN_PREDICTIONS/all_gtdb_methanotroph.csv
phenotrex predict --genotype gtdb_genotypes/merged/all_gtdb.genotype --classifier RE_TRAINED_CLASSES/new_non_fermentative.pkl > PHEN_PREDICTIONS/all_gtdb_non_fermentative.csv
phenotrex predict --genotype gtdb_genotypes/merged/all_gtdb.genotype --classifier RE_TRAINED_CLASSES/new_psychrophilic.pkl > PHEN_PREDICTIONS/all_gtdb_phsychotrophilic.csv
phenotrex predict --genotype gtdb_genotypes/merged/all_gtdb.genotype --classifier RE_TRAINED_CLASSES/new_saccharolytic.pkl > PHEN_PREDICTIONS/all_gtdb_saccharolytic.csv
phenotrex predict --genotype gtdb_genotypes/merged/all_gtdb.genotype --classifier RE_TRAINED_CLASSES/new_sulfate_reducer.pkl > PHEN_PREDICTIONS/all_gtdb_sulfate_reducer.csv
phenotrex predict --genotype gtdb_genotypes/merged/all_gtdb.genotype --classifier RE_TRAINED_CLASSES/new_T3SS.pkl > PHEN_PREDICTIONS/all_gtdb_T3SS.csv
phenotrex predict --genotype gtdb_genotypes/merged/all_gtdb.genotype --classifier RE_TRAINED_CLASSES/new_thermophylic.pkl > PHEN_PREDICTIONS/all_gtdb_thermophylic.csv

```bash
sed -i '1,2d' < <class>_predictions.csv
```


```bash
paste \
<(cut -f 1,2,3 all_gtdb_ac.csv) \
<(cut -f 2,3 all_gtdb_AOB.csv) \
<(cut -f 2,3 all_gtdb_a_saccharolytics.csv) \
<(cut -f 2,3 all_gtdb_auto_co2.csv) \
<(cut -f 2,3 all_gtdb_butanol.csv) \
<(cut -f 2,3 all_gtdb_butyric.csv) \
<(cut -f 2,3 all_gtdb_d_glucose.csv) \
<(cut -f 2,3 all_gtdb_d_lactic.csv) \
<(cut -f 2,3 all_gtdb_ethanol.csv) \
<(cut -f 2,3 all_gtdb_fermentative.csv) \
<(cut -f 2,3 all_gtdb_fixinigN2.csv) \
<(cut -f 2,3 all_gtdb_formicAcid.csv) \
<(cut -f 2,3 all_gtdb_halophilic.csv) \
<(cut -f 2,3 all_gtdb_hydrogen.csv) \
<(cut -f 2,3 all_gtdb_indole.csv) \
<(cut -f 2,3 all_gtdb_isobut.csv) \
<(cut -f 2,3 all_gtdb_isovaleric_acid.csv) \
<(cut -f 2,3 all_gtdb_l_lactic_acid.csv) \
<(cut -f 2,3 all_gtdb_methanotroph.csv) \
<(cut -f 2,3 all_gtdb_nob.csv) \
<(cut -f 2,3 all_gtdb_non_fermentative.csv) \
<(cut -f 2,3 all_gtdb_phototrophy.csv) \
<(cut -f 2,3 all_gtdb_psychotrophilic.csv) \
<(cut -f 2,3 all_gtdb_r_acetoin.csv) \
<(cut -f 2,3 all_gtdb_saccharolytic.csv) \
<(cut -f 2,3 all_gtdb_succinic_acid.csv) \
<(cut -f 2,3 all_gtdb_sulfate_reducer.csv) \
<(cut -f 2,3 all_gtdb_symbiont.csv) \
<(cut -f 2,3 all_gtdb_T3SS.csv) \
<(cut -f 2,3 all_gtdb_T6SS.csv) \
<(cut -f 2,3 all_gtdb_thermophylic.csv) > gtdb_phen_predictions.tsv
```
