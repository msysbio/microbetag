#!/usr/bin/env nextflow

/* Nextflow script to perform KEGG ORTHOLOGY annotation using HMMER and kofam_scan

Usage: 

nextflow run modules/kofam/main.nf -params-file modules/kofam/kofam.yaml

*/

// Add missing defaults
if (!params.containsKey('parts_dir') || params.parts_dir == null) {
    params.parts_dir = "hmmout"
}


process HMMSEARCH{

    tag "Running HMMER search on over a list of .faa files}"

    container "staphb/hmmer:3.4"

    input:
        tuple path(faa), path(hmmsearch_sc), path(ko_list), path(hmm_profiles)

    output:
        path "hmmout_${faa.baseName}"
    
    script:
        """
        mkdir -p hmmout_${faa.baseName}
        bash ${hmmsearch_sc} ${faa} ${ko_list} ${hmm_profiles}
        mv *.hmmout hmmout_${faa.baseName}
        """
}


process MERGE_HMMOUT {

    tag "Merging hmmout files of each bin/genome to build 3-col ko_merged file"

    publishDir { "${params.outdir}/hmmsearch" }, mode: 'copy'
    container "hariszaf/microbetag-nf:0.1.1"

    input: 
        path hmmout_dirs
    
    output:
        path "ko_merged.txt", emit: ko2contig
        path "hmmout.tar.gz", emit: hmmout_tar

    script:
        """
        merge_hmm.sh ${params.threads} ko_merged.txt
        """
}


workflow {

    // Channel for .faa files from path provided 
    def faa_ch
    if( params.faa_dir && params.faa_dir != '' ) {
        def faa_dir = file(params.faa_dir)

        if( !faa_dir.exists() ) {
            error "Directory not found: ${params.faa_dir}"
        } else {
            faa_ch = Channel.fromPath("${params.faa_dir}/*.faa", checkIfExists: false)
        }
    } else {
        error "No FAA directory specified (params.faa_dir is null or empty)."
    }

    // KOFAM db
    ko_list_ch  = Channel.fromPath("${params.kegg_list}")
    hmm_prof_ch = Channel.fromPath("${params.hmm_profiles}")

    // Create a channel from input faa_dir
    hmmsearch_sc_ch = Channel.fromPath('modules/kofam/kofam.sh')

    // Combine the single channels with all faa_dir
    def inputs_ch
    inputs_ch = faa_ch
        .combine(hmmsearch_sc_ch)
        .combine(ko_list_ch)
        .combine(hmm_prof_ch)

    // Run HMMSEARCH for each genome/bin
    hmmout_ch = HMMSEARCH(inputs_ch)

    // Collect all emitted hmmout dirs (waits for all tasks to finish)
    merged_input_ch = hmmout_ch.collect()

    // Merge all hmmout results into a single file
    MERGE_HMMOUT(merged_input_ch)

}

