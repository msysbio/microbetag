# Perfrom HMMER search using kofam profiles and thresholds
# ko_dic["$knum"]="$threshold,$score_type"

         faa="$1"
     ko_list="$2"
profiles_dir="$3"

# Extract gebine bane from filename
genome_name=$(basename "$faa" .faa)

# Parse the ko_kist file and perform hmmsearch for each KO with defined threshold
# The trailing _ catches any extra columns beyond the third (and discards them).
tail -n +2 ${ko_list} | while IFS=$'\t' read -r knum threshold score_type _; do

    if [[ "$threshold" != "-" ]]; then

        case "$score_type" in
            full)
                thres_meth="-T"
                outtype="--tblout"
                ;;
            domain)
                thres_meth="--domT"
                outtype="--domtblout"
                ;;
            custom)
                thres_meth="-E"
                outtype="--tblout"
                ;;
        esac
        
        output="${knum}_${genome_name}.hmmout"
        hmm_db="${profiles_dir}/${knum}.hmm"

        echo -e "Processing KO: ${knum} with threshold: ${threshold} (${score_type})"
        echo -e "Profiles dir: ${profiles_dir}"
        echo -e "hmmsearch -T $threshold --cpu 1 -o /dev/null --tblout $output $hmm_db $faa"

        hmmsearch \
            ${thres_meth} \
            ${threshold} \
            --cpu 1 \
            -o /dev/null \
            ${outtype} \
            ${output} \
            ${hmm_db} \
            ${faa}
    fi

done
