#!/usr/bin/env nextflow

/* Nextflow script to perform seed complementarity analysis on GEMs

Usage: 

nextflow run seed_compl/seed_compl.nf -c seed_compl/seed_compl.config
*/

include { readParamsFile } from '../helpers.nf'

// Only read default YAML if user didn't specify a params-file
if (!workflow.commandLine.contains('-params-file')) {
    def new_params = readParamsFile(params.paramsFile)
    params.putAll(new_params)
}


process GET_SEED_SETS {

    tag "Calculate seed and non-seed sets based on GEM reconstructions."

    publishDir "${params.outdir}/seed_compl/sets", mode: 'copy'
    container "hariszaf/microbetag-nf:0.1.0"

    input:
    path gem

    output:
    path "${gem.baseName}_sets.json", emit: seed_sets_json

    script:
    """
    seed_sets.py ${gem} ${params.namespace} "${gem.baseName}_sets.json"
    """
}


process AGGREGATE_SEED_SETS {

    tag "Aggregate seed and non-seed sets, as JSON files, and filter them based on KEGG modules, pickle files."

    publishDir "${params.outdir}/seed_compl", mode: 'copy'
    container "hariszaf/microbetag-nf:0.1.0"

    input:
    path seed_sets_json

    output:
    path "seeds.json", emit: seeds_json
    path "nonseeds.json", emit: nonseeds_json
    path "confidence.json", emit: confidence_json
    path "keggm_seeds.pkl", emit: module_related_seeds
    path "keggm_nonseeds.pkl", emit: module_related_nonseeds

    script:
    """
    jq -s '.' ${seed_sets_json.join(' ')} > all_seed_sets.json
    jq 'map({ (.base_name): .seed_set }) | add' all_seed_sets.json > seeds.json
    jq 'map({ (.base_name): .non_seed_set }) | add' all_seed_sets.json > nonseeds.json
    jq 'map({ (.base_name): .seed_set_confidence }) | add' all_seed_sets.json > confidence.json

    ssets_pkls.py
    """
}

process SCORES_COMPLS_PRECALC {

    tag "Calculate seed complementarity scores and extract complements."

    publishDir "${params.outdir}/seed_compl/per_species", mode: 'copy'
    container "hariszaf/microbetag-nf:0.1.0"

    input:
    tuple val(species), path(nonseeds_json), path(confidence_json)

    output:
    path "${species}_scores.tsv", emit: sp_seed_scores_json
    path "${species}_compls.json", emit: sp_seed_compl_json

    script:
    """
    seed_compls.py \
        "${species}" \
        "${nonseeds_json}" \
        "${confidence_json}" \
        "${params.kegg_modules_only}" \
        "${species}_scores.tsv" \
        "${species}_compls.json"
    """
}


process AGGREGATE_SCORES_COMPLS {
    
    tag "Aggregate the per species seed scores and complements to global files"

    publishDir "${params.outdir}/seed_compl", mode: 'copy'
    container "hariszaf/microbetag-nf:0.1.0"

    input:
    path sp_seed_scores_json
    path sp_seed_compl_json

    output:
    path compls_js_outfile,  emit: tmp_compls
    path compls_pkl_outfile, emit: seed_compls
    path scores_outfile,     emit: seed_scores

    script:
    compls_js_outfile  = "all_compls.json"
    compls_pkl_outfile = "seed_compls.pkl"
    scores_outfile     = "seed_scores.tsv"
    """ 
    jq -n '
      reduce inputs as \$f ({}; . + {(\$f|input_filename|capture("(?<key>[^/]+)_compls\\\\.json\$").key): \$f})
    ' *_compls.json > ${compls_js_outfile}

    echo -e 'nodeA\\tnodeB\\tCompetitionScore\\tCooperationScore' > header
    cat *.tsv >> scores
    cat header scores > ${scores_outfile}
    
    scompls_pkls.py ${compls_js_outfile} ${compls_pkl_outfile}
    """
}



workflow {

    // Channels for species GEMs and species names
    gems_ch    = Channel.fromPath("${params.gems}/*.xml")
    species_ch = Channel
        .fromPath("${params.gems}/*.xml")
        .map { file -> file.baseName }


    // Get seed and non-seed sets
    s = GET_SEED_SETS(gems_ch)

    // Aggregate seed and non-seed sets
    a = AGGREGATE_SEED_SETS(s.collect())

    // Combine scirpt and seed data for each species
    species_data_ch = species_ch
        .combine(a.nonseeds_json)
        .combine(a.confidence_json)

    // Calculate seed complementarity scores and extract complements
    e = SCORES_COMPLS_PRECALC(species_data_ch)

    // Aggregate compls and scores
    AGGREGATE_SCORES_COMPLS(e[0].collect(), e[1].collect())
}
