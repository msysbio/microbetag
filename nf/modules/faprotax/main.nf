#!/usr/bin/env nextflow

/* Nextflow script to run FAPROTAX

Usage: 

nextflow run modules/faprotax/main.nf -params-file modules/faprotax/faprotax.yaml 

*/

process FAPROTAX {

    tag "Annotate abundance table with FAPROTAX functional groups"

    publishDir "${params.outdir}/faprotax", mode: 'copy'
    container "hariszaf/microbetag-nf:0.1.0"

    input:
        path abundance_table
    
    output:
        path "functional_otu_table.tsv", emit: fapro_table
        path "sub_tables",               emit: fapro_subtables
    
    script:
        """
        python /workspace/microbetag/mtg_maps_models/FAPROTAX_1.2.10/collapse_table.py \
            -i ${abundance_table} \
            -o functional_otu_table.tsv \
            -g /workspace/microbetag/mtg_maps_models/FAPROTAX_1.2.10/FAPROTAX.txt \
            --table_delimiter ${params.delimiter} \
            -c "#" \
            -d ${params.taxonomy_colname} \
            -v \
            --force \
            -s sub_tables
        """
}


workflow{

    // Create a channel from input abundance table
    def abundance_ch = Channel.fromPath("${params.abundance_table}")

    // Run process 
    FAPROTAX(abundance_ch)

}



