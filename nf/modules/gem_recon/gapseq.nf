

def cplexBind = workflow.containerEngine == 'singularity' ?
    "-B ${params.cplex}:/opt/CPLEX" :
    "-v ${params.cplex}:/opt/CPLEX"


process GAPSEQ_FIND {

    tag "gapseq find"
    
    container "hariszaf/gapseq:1.4.0"
    publishDir "${params.outdir}/reconstructions/${base}", mode: 'copy', overwrite: true

    input:
    tuple val(base), path(genome)

    output:
    tuple val(base), path("*-Reactions.tbl"), path("*-Pathways.tbl"), emit: find

    script:
    """
    base=\$(basename "${genome}")
    base="\${base%.*}"

    rxn_tbl=\${base}-${params.gapseq.find.p}-Reactions.tbl
    ptw_tbl=\${base}-${params.gapseq.find.p}-Pathways.tbl

    if [[ -f "\${rxn_tbl}" && -f "\${ptw_tbl}" ]]; then
        echo "[GAPSEQ FIND] Both -Reactions and -Pathways files were provided by the user. Skip gapseq find step." >> find.log
    else
        gapseq find \
            -p ${params.gapseq.find.p} \
            -t ${params.gapseq.find.t} \
            -b ${params.gapseq.find.b} \
            -i ${params.gapseq.find.i} \
            -c ${params.gapseq.find.c} \
            "${genome}"
        echo "[GAPSEQ FIND] Gapseq find completed for genome: \${base}." >> find.log
    fi 

    """
}


process GAPSEQ_FIND_TRANSPORTER {
    tag "gapseq find transporters"

    container "hariszaf/gapseq:1.4.0"
    publishDir "${params.outdir}/reconstructions/${base}", mode: 'copy', overwrite: true

    input:
    tuple val(base), path(genome)

    output:
    tuple val(base), path("*-Transporter.tbl"), emit: trp_tbl
    path "transporter.log"

    script:
    """
    base=\$(basename "${genome}")
    base="\${base%.*}"

    echo -e "[GAPSEQ FIND-TRANSPORT] Run the find-transport script of gapseq -- searching for transporters... "  >> transporter.log

    trp_tbl=\${base}-Transporter.tbl

    if [[ -f "\${trp_tbl}" ]]; then 
        echo "[GAPSEQ FIND-TRANSPORT] Transporters file was provided by the user. Skip gapseq find-transporter step.." >> transporter.log

    else 
        gapseq find-transport \
            -b ${params.gapseq.find_transport.b} \
            -i ${params.gapseq.find_transport.i} \
            -c ${params.gapseq.find_transport.c} \
            "${genome}"
        echo "[GAPSEQ FIND-TRANSPORT] Gapseq find-transporters completed for genome: \${base}." >> transporter.log
    fi
    """
}


process GAPSEQ_DRAFT {

    tag "gapseq draft reconstruction"

    container "hariszaf/gapseq:1.4.0"
    containerOptions = cplexBind

    publishDir "${params.outdir}/reconstructions/${base}", mode: 'copy', overwrite: true
    

    input:
    tuple val(base),
        path(genome),
        path(rxn_tbl), // "*-Reactions.tbl"
        path(pwt_tbl), 
        path(trp_tbl)

    output:
    tuple val(base), 
        path("*-draft.RDS"), 
        path("*-rxnWeights.RDS"), 
        path("*-rxnXgenes.RDS"), 
        emit: draft_recon_files
    path("*-draft.xml"), emit: draft_xml

    script:
    """
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


    echo "[GAPSEQ DRAFT]: Starting draft reconstruction" > draft.log

    if [[ ${params.gapseq.draft.b} == "" || ${params.gapseq.draft.b} == "auto" ]]; then 
        gapseq draft \
            -r ${rxn_tbl} \
            -p ${pwt_tbl} \
            -t ${trp_tbl} \
            -c "${genome}" \
            -u ${params.gapseq.draft.u} \
            -l ${params.gapseq.draft.l}
    else
        gapseq draft \
            -r ${rxn_tbl} \
            -p ${pwt_tbl} \
            -t ${trp_tbl} \
            -b ${params.gapseq.draft.b} \
            -u ${params.gapseq.draft.u} \
            -l ${params.gapseq.draft.l}
    fi
    """
}


process GAPSEQ_FILL {

    tag "gapseq gapfill"
    
    container "hariszaf/gapseq:1.4.0"
    containerOptions = cplexBind

    publishDir "${params.outdir}/reconstructions/${base}", mode: 'copy', overwrite: true

    input:
    tuple val(base),
        path(draft_rds),
        path(rxn_wghts),
        path(rxn_genes),
        path(medium)

    output:
    path "${base}.RDS", emit: filled_rds
    path "${base}.xml", emit: filled_xml

    script:
    """
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

    echo "[GAPSEQ FILL]: Starting gapfilling" > fill.log

    gapseq fill \
        -m ${draft_rds} \
        -c ${rxn_wghts} \
        -g ${rxn_genes} \
        -n ${medium} \
        -b ${params.gapseq.medium.b}

    """
}


workflow GAPSEQ {

    def genome_ch
    def genomes_with_base
    def updated_tbl_ch
    def draft_input
    def gf_input
    def med_ch

    genome_ch = Channel.fromPath("${params.recon_files}/*")

    // ${params.gapseq.find.p} genomes, with their base name -- genome is a Path object from the previous channel.
    genomes_with_base = genome_ch.map { genome -> [genome.getBaseName(), genome] }

    // Genomes with existing tbls
    def existing_tbl_ch = genomes_with_base.filter { base, genome ->
        new File("${params.gapseq.prev_tbl}/${base}-${params.gapseq.find.p}-Reactions.tbl").exists() &&
        new File("${params.gapseq.prev_tbl}/${base}-${params.gapseq.find.p}-Pathways.tbl").exists()
    }.map { base, genome ->
        def rxn_tbl = file("${params.gapseq.prev_tbl}/${base}-${params.gapseq.find.p}-Reactions.tbl")
        def pwt_tbl = file("${params.gapseq.prev_tbl}/${base}-${params.gapseq.find.p}-Pathways.tbl")
        [base, rxn_tbl, pwt_tbl]
    }

    // Genomes missing tbls → need to run process
    def missing_genomes_ch = genomes_with_base.filter { base, genome ->
        !(
            new File("${params.gapseq.prev_tbl}/${base}-${params.gapseq.find.p}-Reactions.tbl").exists() &&
            new File("${params.gapseq.prev_tbl}/${base}-${params.gapseq.find.p}-Pathways.tbl").exists()
        )
    }

    // Run the find step for those missing Reactions and Pathways tbs files for the -p under study
    pathways = GAPSEQ_FIND(missing_genomes_ch)

    // All genomes' find-related files
    updated_tbl_ch = existing_tbl_ch.concat(pathways.find)

    // Genomes with existing tbls
    def existing_trp_ch = genomes_with_base.filter { base, genome ->
        new File("${params.gapseq.prev_tbl}/${base}-Transporter.tbl").exists()
    }.map { base, genome ->
        def trp_tbl = file("${params.gapseq.prev_tbl}/${base}-Transporter.tbl")
        [base, trp_tbl]
    }

    // Genomes missing tbls → need to run process
    def missing_trp_ch = genomes_with_base.filter { base, genome ->
        !(
            new File("${params.gapseq.prev_tbl}/${base}-Transporter.tbl").exists()
        )
    }

    // Run the find step for those missing Reactions and Pathways tbs files for the -p under study
    transporters = GAPSEQ_FIND_TRANSPORTER(missing_trp_ch)

    all_trp_tbl_ch = existing_trp_ch.concat(transporters.trp_tbl)


    // Genomes with existing tbls
    def existing_xml_ch = genomes_with_base.filter { base, genome ->
        new File("${params.gapseq.prev_tbl}/${base}-draft.xml").exists()
        new File("${params.gapseq.prev_tbl}/${base}-rxnXgenes.RDS").exists()
        new File("${params.gapseq.prev_tbl}/${base}-rxnWeights.RDS").exists()
    }.map { base, genome ->
        def draft_xml = file("${params.gapseq.prev_tbl}/${base}-draft.RDS")
        def rxn_genes = file("${params.gapseq.prev_tbl}/${base}-rxnXgenes.RDS")
        def rxn_wghts = file("${params.gapseq.prev_tbl}/${base}-rxnWeights.RDS")
        [base, draft_xml, rxn_genes, rxn_wghts]
    }

    def missing_xml_ch = genomes_with_base.filter { base, genome ->
        !(
            new File("${params.gapseq.prev_tbl}/${base}-draft.xml").exists()
        )
    }

    // Input tuple for cases whith missing draft reconstruction 
    draft_input = missing_xml_ch.combine(updated_tbl_ch, by: 0).combine(all_trp_tbl_ch, by: 0)

    // DRAFT RECONSTRUCTIONS
    draft = GAPSEQ_DRAFT(draft_input)


    // Now run GAPSEQ_FILL only when the channel is not empty
    def med_file = params.gapseq?.medium?.file ?: null
    def has_medium = (med_file && file(med_file).exists())
    
    if( has_medium ) {
        println "GO FOR GAP-FILLING WITH MEDIUM FILE"
        med_ch   = Channel.value(file(med_file))
        gf_input = existing_xml_ch.concat(draft.draft_recon_files).combine(med_ch)
        gf_input.view{ base, xml_rds, rxn_wghts, rxn_genes, medim -> 
        """
        xml_rds: ${xml_rds}
        """
        }
        gapfilled = GAPSEQ_FILL(gf_input)
    } else {
        println "No medium file provided - skipping GAPSEQ_FILL"
    }
}
