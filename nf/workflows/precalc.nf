#!/usr/bin/env nextflow

/* Nextflow script to run microbetag precalculations for a genome catalogue

Usage: 

nextflow run precalc.nf  -params-file params/precalc.yaml -entry MICROBETAG_PRECALC

*/

include { PHENOTREX } from '../modules/phenotrex/'
include { PRODIGAL } from '../modules/prodigal/'
include { PATHWAY_COMPLEMENTARITY } from '../subworkflows/pathway_complementarity/'
include { SEED_COMPLEMENTARITY } from '../subworkflows/seed_complementarity/'


workflow MICROBETAG_PRECALC {

    if ( params.phenotrex ) {

        PHENOTREX()

    }

    // Both complementarity modules require .faa files at some point. 
    // Make sure either user already provided them from config file, 
    // or microbetag runs Prodigal to get them, before firing the sub-workflows for the complementarities


    // Helper booleans
    def do_compl     = params.pathway_compl || params.seed_compl
    def gems_dir_ok  = params.gems && file(params.gems).exists()
    def faa_dir_ok   = params.faa_dir && file(params.faa_dir).exists()
    def faa_exists   = faa_dir_ok && file(params.faa_dir).list().any { 
        it.endsWith('.faa')  || it.endsWith('.faa.gz')
    }
    def gems_exist   = gems_dir_ok && file(params.gems).list().any { 
        it.endsWith('.xml')  || it.endsWith('.xml.gz') 
    }
    def genomes_ch
    def prodigal_out
    def faa_ch
    def gems_ch

    if (do_compl) {

        // If only seed_compl and valid GEMs exist → skip annotation & FAA
        if (!params.pathway_compl && params.seed_compl && gems_exist) {
            log.info "✓ Using GEMs provided by the user. No genome annotation needed."
            check = false
            gems_ch = Channel.fromPath("${params.gems}/*.xml",  checkIfExists: true)
        } else {
            check = true
        }

        if (check) {

            if (faa_exists) {
 
                // Use FAA files
                log.info "✓ Using existing FAA files in: ${params.faa_dir}"
 
                faa_ch = Channel.fromPath("${params.faa_dir}/*.{faa,faa.gz}", checkIfExists: true)

            } else {
                // Run Prodigal
                log.info "○ Running genome annotation (Prodigal) to generate ORFs"

                genomes_ch   = Channel.fromPath("${params.genomes}/*.{fa,fasta,fa.gz,fasta.gz}", checkIfExists: true)
                prodigal_out = PRODIGAL(genomes_ch)
 
                faa_ch = prodigal_out.faa
            }
        }
    }

    if (params.pathway_compl ) {

        PATHWAY_COMPLEMENTARITY(faa_ch)
    }

    if ( params.seed_compl) {

        if (gems_exist) {
            log.info"Firing SEED_COMPLEMENTARITY sub-workflow with gems_ch."
            SEED_COMPLEMENTARITY(gems_ch)
        } else {
            SEED_COMPLEMENTARITY(faa_ch)
        }

    }

}
