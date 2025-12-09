#!/usr/bin/env nextflow

process PREP_NETWORK {

    tag "Based on a 3-column edgelist, prepare the .cyjs format base network for running manta "

    container "hariszaf/microbetag-nf:0.1.0"

    input:
    path abd_file
    path network

    output:
        path "*.cyjs", emit: cyjs_net

    script: 
        """
        format_manta.py ${abd_file} ${network}
        """
}


process RUN_MANTA {

    tag "Cluster network using the manta software"

    publishDir "${params.outdir}/manta", mode: 'copy'
    container "hariszaf/microbetag-nf:0.1.0"

    input:
        path cyjs_net

    output:
        path "${params.manta_prefix ?: 'manta_net'}*", emit: manta_net

    script:
        """
        manta -i ${cyjs_net} \
        -f cyjs \
        -o ${params.manta_prefix ?: 'manta_net'} \
        --layout
        """
}


workflow {

    orig_net = Channel.fromPath(params.network)

    def format_net
    if( params.cyjs_net && params.cyjs_net != '' ) {

        def cyjs_net = file(params.cyjs_net)

        if( !cyjs_net.exists() ) {
            error "The ${params.cyjs_net} cyjs network does not exist."
        } else {
            log.info "A network in .cyjs format was provided and will be used as input for manta."
            format_net = Channel.fromPath( params.cyjs_net, checkIfExists: false)
        }

    } else {

        log.info "Original network not in .cyjs version. Needs to be converted to that for manta."

        abd_data = Channel.fromPath(params.abundance_file)
    
        f = PREP_NETWORK(abd_data, orig_net)

        format_net = f.cyjs_net
    }

    log.info "Run manta.."

    RUN_MANTA(format_net)

}
