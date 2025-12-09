import org.yaml.snakeyaml.Yaml
import groovy.yaml.YamlSlurper


//---------
// FUNCTIONS
//---------

def readParamsFile(defaultFile) {

    // 1. Determine which params file to load
    def paramsFile = params.get('paramsFile', "${defaultFile}")

    // 2. Parse YAML file
    def yaml = new YamlSlurper().parse(new File(paramsFile))
    println "--> ${yaml}"

    // 3. Assign YAML values to params (only if not already specified via CLI)
    yaml.each { k, v ->
        // Check if parameter is null or empty string
        if (!params.containsKey(k) || params[k] == null || params[k].toString().trim().isEmpty()) {
            params[k] = v
        }
    }
    println ">>> ${params}"
    return params
}

def isChannel(obj) {
    return obj.getClass().name.contains('Channel') || 
           obj.getClass().name.contains('Dataflow')
}

def sanitize(name) {
    return name.bytes.encodeBase64().toString() //.replace('+','-').replace('/','_').replaceAll('=+$','')
}

def unsanitize(name) {
    return new String(name.decodeBase64())
}


def sanitizeChannel(fileList) {    
    return Channel.fromList(fileList)
        .map { file ->
            def orig_name = file.getName() 
            def safe_name = sanitize(orig_name)
            tuple(orig_name, safe_name, file)
        }
}

// Helper function to check file existence
def fileExists(param_name) {
    return params[param_name] && file(params[param_name]).exists()
}


def getInputFiles(String inputDir) {
    // Detects and sanitizes sequencing (FASTA) files 

    def input_files = file(inputDir)
    def faa_files   = input_files.listFiles().findAll { it.name =~ /\.(faa|faa\.gz)$/ }
    def nucl_files  = input_files.listFiles().findAll { it.name =~ /\.(fa|fna|fasta|fa\.gz|fna\.gz|fasta\.gz)$/ }
    
    if (faa_files && !nucl_files) {
        log.info "Detected protein FASTA files (*.faa or *.faa.gz)"
        def pattern = "${inputDir}/*.{faa,faa.gz}"
        return [
            pattern: pattern,
            is_faa: true,
            files_ch: sanitizeChannel(faa_files)
        ]
    } else if (nucl_files && !faa_files) {
        log.info "Detected nucleotide FASTA files (*.fa, *.fna, *.fasta, etc.)"
        def pattern = "${inputDir}/*.{fa,fasta,fna,fa.gz,fasta.gz,fna.gz}"
        return [
            pattern: pattern,
            is_faa: false,
            files_ch: sanitizeChannel(nucl_files)
        ]
    } else if (faa_files && nucl_files) {
        error "Mixed FASTA file types detected (both nucleotide and protein). Please separate them."
    } else {
        error "No input FASTA files found in ${inputDir}"
    }
}


def chunkFiles(fileChannel, maxForks) {
    def collected_ch = fileChannel.collect()
    
    return collected_ch.flatMap { files ->
        log.info "Number of input files found: ${files.size()}"
        def chunk_size = Math.ceil(files.size() / maxForks) as int
        log.info "Chunk size = $chunk_size"
        
        def chunks = []
        for (i = 0; i < files.size(); i += chunk_size) {
            chunks << files[i..Math.min(i+chunk_size-1, files.size()-1)]
        }
        return chunks
    }
}


//---------
// PROCESSES 
//---------

process SAFENAME_FILES {

    tag "Copy of the input files with sanitized names"
    if (params.debug_decompress) {
        publishDir "${params.outdir}/data", mode: 'copy', overwrite: true
    }
    container "hariszaf/microbetag-nf:0.1.0"

    input:
    tuple val(orig_name), val(safe_name), path(file)

    output:
    tuple val(orig_name), path("${safe_name}")

    script:
    """
    # Always operate on the real file ($file)
    cp $file ${safe_name}
    chmod 644 ${safe_name}
    """
}


process GUNZIP {

    tag "Gunzip files"

    if (params.debug_decompress) {
        publishDir "${params.outdir}/decompr", mode: 'copy', overwrite: true
    }
    container "hariszaf/microbetag-nf:0.1.0"

    input:
    tuple val(orig_name), val(orig_name_decomp), path(file)

    output:
    path orig_name_decomp

    script:
    """
    if file -L "${file}" | grep -q 'gzip compressed data'; then
        gunzip -c "${file}" > "${orig_name_decomp}"
    else
        cp "${file}" "${orig_name_decomp}"
    fi
    """
}

