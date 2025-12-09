#!/usr/bin/env nextflow

/* Nextflow script to perform seed complementarity precalculations 

Usage: 

nextflow run seed_compl/seed_compl.nf -c seed_compl/seed_compl.config

or

nextflow run seed_compl/seed_compl.nf -params-file params/seed_compl.yaml
*/

include  { getInputFiles; sanitizeChannel; chunkFiles; SAFENAME_FILES; GUNZIP } from '../helpers.nf'
include {GAPSEQ_FIND; GAPSEQ_FIND_TRANSPORTER; GAPSEQ_DRAFT; GAPSEQ_FILL} from './gapseq'


def gurobiBind = workflow.containerEngine == 'singularity' ?
    "-B ${params.gurobi_lic}:/opt/gurobi/gurobi.lic" :
    "-v ${params.gurobi_lic}:/opt/gurobi/gurobi.lic"

def cplexBind = workflow.containerEngine == 'singularity' ?
    "-B ${params.cplex}:/opt/CPLEX" :
    "-v ${params.cplex}:/opt/CPLEX"


process CARVE {

    tag "GEM reconstruction with CarveMe"

    publishDir "${params.outdir}/reconstructions", mode: 'copy', overwrite: true
    container "hariszaf/carveme:1.6.6"
    containerOptions = gurobiBind

    input:
        path in_chunk
        val is_faa

    // Optional: uncomment to enable conditional execution
    when:
        params.recon_with == "carveme"

    output:
        path "*.xml", emit: carve_model

    script:
        """
        export GRB_LICENSE_FILE=/opt/gurobi/gurobi.lic

        # Create a clean file list to safely iterate
        for f in ${in_chunk}; do
            echo "\$f" >> chunk.list
        done

        while read f; do
            base=\$(basename "\$f")
            base="\${base%.*}"

            if [ ${is_faa} == "true" ]; then
                echo "Running CarveMe on \$f (FAA mode)" >&2
                carve --solver gurobi --output "\${base}.xml" "\$f"
            else
                echo "Running CarveMe on \$f (DNA mode)" >&2
                carve --dna --solver gurobi --output "\${base}.xml" "\$f"
            fi

        done < chunk.list
        """
}

process GAPSEQ {

    tag "GEM reconstruction with gapseq"

    publishDir "${params.outdir}/reconstructions", mode: 'copy', overwrite: true
    container "hariszaf/gapseq:1.4.0"

    containerOptions = cplexBind

    input:
        path genome
        path prev_tbl
        path medium

    when:
        params.recon_with == "gapseq"

    output:
        path "emm"
        path "*.tbl", emit: tbl, optional: true
        path "*.xml", emit: gapseq_model  //, optional: true

    script:
        """
        base=\$(basename "${genome}")
        base="\${base%.*}"

        # ---------
        # Check if CPLEX is available, and if so, install cobrarCPLEX
        # ---------

        if [ -d /opt/CPLEX ] && [ "\$(ls -A /opt/CPLEX)" ]; then
            echo ">>>>> /opt/CPLEX is mounted and not empty. Let us nstall cobrarCPLEX .. " >> emm
            unzip /opt/Rsrc/cobrarCPLEX.zip -d /opt/Rsrc/
            R CMD INSTALL /opt/Rsrc/cobrarCPLEX-main --configure-args="--with-cplex-dir=/opt/CPLEX/cplex"
        else
            echo ">>>>> /opt/CPLEX is missing or empty, skipping cobrarCPLEX installation" >> emm
        fi

        # ---------
        # Run gapseq
        # ---------

        echo -e "[GAPSEQ FIND]: gapseq will be searching for metabolic pathways... "  >> emm

        rxn_tbl=\${base}-all-Reactions.tbl
        ptw_tbl=\${base}-all-Pathways.tbl

        if [[ -f "\${rxn_tbl}" && -f "\${ptw_tbl}" ]]; then
            echo "[GAPSEQ FIND] Both all-Reactions and all-Pathways files were provided by the user. Skip gapseq find step." >> emm
        else
            gapseq find \
                -p ${params.gapseq.find.p} \
                -t ${params.gapseq.find.t} \
                -b ${params.gapseq.find.b} \
                -i ${params.gapseq.find.i} \
                -c ${params.gapseq.find.c} \
                "${genome}"
        fi 

        echo -e "[GAPSEQ FIND-TRANSPORT] Run the find-transport script of gapseq -- searching for transporters... "  >> emm

        trp_tbl=\${base}-Transporter.tbl

        if [[ -f "\${trp_tbl}" ]]; then 
            echo "[GAPSEQ FIND-TRANSPORT] Transporters file was provided by the user. Skip gapseq find-transporter step.." >> emm

        else 
            gapseq find-transport \
                -b ${params.gapseq.find_transport.b} \
                -i ${params.gapseq.find_transport.i} \
                -c ${params.gapseq.find_transport.c} \
                "${genome}"
        fi

        echo -e "Run gapseq draft reconstruction step.."

        draft_rds=\${base}-draft.RDS     ; draft_xml=\${base}-draft.xml
        rxn_genes=\${base}-rxnXgenes.RDS ; rxn_wght=\${base}-rxnWeights.RDS

        if [[ -f "\${draft_rds}" && -f "\${rxn_wght}" && -f "\${rxn_genes}" && -f "\${draft_xml}" ]]; then

            echo "Draft model is already available"  >> emm 
        
        else

            # If biomass is not specified, then use the genome to get it 
            if [[ ${params.gapseq.draft.b} == "" || ${params.gapseq.draft.b} == "auto" ]]; then 

                gapseq draft \
                    -r \${rxn_tbl} \
                    -p \${ptw_tbl} \
                    -t \${trp_tbl} \
                    -c "${genome}" \
                    -u ${params.gapseq.draft.u} \
                    -l ${params.gapseq.draft.l} 
            else

                # Otherwise, use the one the user suggests
                gapseq draft \
                    -r \${rxn_tbl} \
                    -p \${ptw_tbl} \
                    -t \${trp_tbl} \
                    -b ${params.gapseq.draft.b} \
                    -u ${params.gapseq.draft.u} \
                    -l ${params.gapseq.draft.l} 
            fi
        fi

        # GAPFILL
        if [[ -f "${medium}}" ]]; then
 
            echo -e "Gapfill with gapseq using user's medium file.." >>  emm
 
            gapseq fill \
                -m \${base}-draft.RDS \
                -c \${base}-rxnWeights.RDS \
                -g \${base}-rxnXgenes.RDS \
                -n ${medium} \
                -b ${params.gapseq.medium.b}
        else
            echo "No medium was provided in order to gap-fill using that." >> emm
        fi

        """
}


workflow {

    def recon_in; def prep; def decomp
    def mapped_files;  def infiles_chunk_ch

    // sanitize filenames if for example filenames like BATCH:set1.fastq
    recon_in = getInputFiles(params.recon_files)
    prep     = SAFENAME_FILES(recon_in.files_ch)

    // Add a separate mapping step
    mapped_files = prep.map { orig_name, file ->
        def orig_name_decomp = orig_name.endsWith(".gz") ? orig_name[0..-4] : orig_name
        tuple(orig_name, orig_name_decomp, file)
    }

    decomp = GUNZIP(mapped_files)
    decomp_ch = decomp.collect()


    if (params.recon_with == "carveme") {
        // Use the COLLECTED channel for chunking, not the original decomp channel
        infiles_chunk_ch = chunkFiles(decomp_ch, params.max_forks)

        // Pass chunks to your carve process
        CARVE(infiles_chunk_ch, recon_in.is_faa)

    } else if (params.recon_with == "gapseq") {
        
        def gapseq_prev_ch = params.gapseq.prev_tbl ? 
            Channel.fromPath("${params.gapseq.prev_tbl}/*")
                .ifEmpty { Channel.value([]) }
                .collect() :
            Channel.value([])

        def med_ch = params.gapseq.medium.file ?
            Channel.fromPath(params.gapseq.medium.file).ifEmpty { Channel.value([]) } :
            Channel.value([])

        // Pass chunks to your gapseq process
        GAPSEQ(decomp_ch, gapseq_prev_ch, med_ch)

    }

}
