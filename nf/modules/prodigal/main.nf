#!/usr/bin/env nextflow

/* Nextflow script to run Prodigal

Usage: 

nextflow run modules/prodigal/main.nf -params-file modules/prodigal/prodigal.yaml 

*/

include { readParamsFile } from '../helpers.nf'

// ORIGINAL
process PRODIGAL {

    publishDir "${params.outdir}/prodigal", mode: 'copy'
    container "biocontainers/prodigal:v1-2.6.3-4-deb_cv1"
    containerOptions = workflow.containerEngine == 'docker' ? '-u $(id -u):$(id -g)' : ''


    input:
        path genome

    output:
        // Returns 3 channales that you need to specify
        path "*.faa", emit: faa
        path "*.ffn", emit: ffn
        path "*.gbk", emit: gbk

    script:
        def genome_name = genome.name.replaceFirst(/\.[^.]+$/, '')
        """
        prodigal -i ${genome} -p meta -a ${genome_name}.faa -d ${genome_name}.ffn -o ${genome_name}.gbk
        """
}


workflow {

    // Create a channel from input genomes
    def genomes_ch = Channel.fromPath("${params.genomes}/*")

    // PRODIGAL(genomes_ch) | view { message -> "I say... $message" }

    // Run annotation process
    def annotations = PRODIGAL(genomes_ch) 

    // Get only faa files
    def faa_ch = annotations.faa

    // Return only the *.faa channel
    return faa_ch

}
