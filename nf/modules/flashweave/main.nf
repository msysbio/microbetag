#!/usr/bin/env nextflow

/* Nextflow script to run FlashWeave 

Usage: 

nextflow run modules/flashweave/main.nf -params-file modules/flashweave/flashweave.yaml 

*/

import groovy.json.JsonOutput

jlSingularityOptions = workflow.containerEngine == 'singularity' ? 
    """
        --bind $HOME/julia_depot:$HOME/julia_depot \
        --bind $HOME/julia_tmp:$HOME/juliatmp \
        --env JULIA_DEPOT_PATH=$HOME/julia_depot:/usr/local/share/julia \
        --env TMPDIR=$HOME/julia_tmp
    """.stripIndent().trim() : 
    ""

// ---------------- Processes ----------------

process FORMAT_FW {

    tag "Bring abundance data to a FlashWeave-friendly format"

    container "hariszaf/microbetag-nf:0.1.0"

    input:
        path abundance_file

    output:
        file 'flashweave_abd_table.tsv'

    script:
        """
        format_fw.py ${abundance_file} > flashweave_abd_table.tsv
        """

}

process RUN_FW {

    tag "Network inference using FlashWeave"

    publishDir "${params.outdir}/flashweave", mode: 'copy'
    container "hariszaf/flashweave:0.19.2"
    containerOptions = jlSingularityOptions

    input:
        file formatted_table

    output:
        file 'fw_net.txt'

    script:
        """
        run_fw.jl \
        --input ${formatted_table} \
        --fw_args '${groovy.json.JsonOutput.toJson(params.flashweave_args)}' \
        --output fw_net.edgelist

        tail -n +3 fw_net.edgelist > fw_net.txt
        """
}


process RUN_FW_METADATA {

    tag "Network inference using FlashWeave and the study metadata"

    publishDir "${params.outdir}/flashweave", mode: 'copy'
    container "hariszaf/flashweave:0.19.2"
    containerOptions = jlSingularityOptions

    input:
        file formatted_table
        file metadata_file

    output:
        file 'fw_net.txt'

    script:
        """
        run_fw.jl \
        --input ${formatted_table} \
        --metadata ${metadata_file} \
        --fw_args '${groovy.json.JsonOutput.toJson(params.flashweave_args)}' \
        --output fw_net.edgelist

        tail -n +3 fw_net.edgelist > fw_net.txt
        """   
}

// ---------------- Workflow definition ----------------

workflow {

    abundance_ch = Channel.fromPath(params.abundance_file)

    // Step 1: format input table
    formatted_table = FORMAT_FW(abundance_ch)

    formatted_table.view()

    // Step 2: checl if metadata file 
    metadata_val = params.metadata_file ?: ""

    // Step 3: run FlashWeave on formatted table 
    if (metadata_val) {

        // metadata_val is non-empty → run process that uses metadata
        metadata_ch = Channel.fromPath(metadata_val)
        RUN_FW_METADATA(formatted_table, metadata_ch)

    } else {

        // metadata_val is empty → run process that does not use metadata
        RUN_FW(formatted_table)
    }

}

