#!/usr/bin/env nextflow

/* Nextflow script to perform Pathway complementarity precalculations 

Usage (from root microbetag/nf:): 

nextflow run modules/pathway_compl/main.nf -params-file modules/pathway_compl/pathway_compl.yaml
*/


process PC_PRECALC {
    tag "Pathway complementarity precalculations"

    publishDir "${params.outdir}/pathway_compl", mode: 'copy'
    container "hariszaf/microbetag-nf:0.1.0"

    input:
    path ko_merged_ch

    output:
    path "alternatives.json", emit: alts
    path "pcompls.json", emit: pcompls

    script:
    """
    pcompl.py \
        alternatives.json \
        pcompls.json \
        ${ko_merged_ch} \
        ${params.tinyurl} \
        ${params.threads}
    """
}


process PC_EXTEND {
    tag "Extend pathway complementarities with URls to KEGG maps"

    publishDir "${params.outdir}/pathway_compl", mode: 'copy'
    container "hariszaf/microbetag-nf:0.1.0"

    input:
    path pcompls

    output:
    path "${pcompls.baseName}_ext.json", emit: pcompls_ext

    script:
    """
    pcompl_ext.py \
        ${pcompls} \
        ${params.pc_percent} \
        ${params.threads}

    mv pathway_complements_extended.json ${pcompls.baseName}_ext.json
    """

}


workflow {

    def alts_file
    def pc_file
    def ko_merged_ch = Channel.fromPath(params.ko_merged, checkIfExists: true)

    // Check if we can skip PC_PRECALC
    def skip_precalc = params.alts_file && params.pc_file && 
                      file(params.alts_file).exists() && 
                      file(params.pc_file).exists()
    
    if (skip_precalc) {
        alts_file = Channel.fromPath(params.alts_file, checkIfExists: true)
        pc_file   = Channel.fromPath(params.pc_file, checkIfExists: true)
        log.info "✓ Using existing files, skipping PC_PRECALC"
    } else {
        PC_PRECALC(ko_merged_ch)
        alts_file = PC_PRECALC.out.alts
        pc_file   = PC_PRECALC.out.pcompls
        log.info "○ Running PC_PRECALC to generate files"
    }
    
    // Continue pipeline
    PC_EXTEND(pc_file)
}