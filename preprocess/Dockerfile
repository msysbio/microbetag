# microbetagPre: preprocess for running the microbetag annotator of microbial co-occurrence networks
# 
# Aim:   this Docker image will encapsulate all the related  
#        tools, databases and software modules for the microbetag
#        network 
# 
# Usage: docker run --rm -it -v ./test/:/media microbetagpre bash

FROM hariszaf/microbetag_prep:base 

LABEL maintainer = "Haris Zafeiropoulos" 
LABEL contact    = "haris.zafeiropoulos@kuleuven.be"
LABEL build_date = "2023-11-01"
LABEL version    = "v.1.0.0"


WORKDIR /pre_microbetag
COPY prep.py gtdb_16s.RData classify.R flashweave.jl  ./

ENTRYPOINT [ "/usr/bin/python3", "/pre_microbetag/prep.py" ]
