# microbetag: annotating microbial co-occurrence networks
# 
# Aim:   this Docker image will encapsulate all the related  
#        tools, databases and software modules for the microbetag
#        network annotator
# 
# Usage: docker build -t hariszaf/microbetag:<tag> .

FROM microbetag_base:latest

LABEL maintainer = "Haris Zafeiropoulos" 
LABEL contact    = "haris.zafeiropoulos@kuleuven.be"
LABEL build_date = "2025-02-06"
LABEL version    = "v1.0.3"


# Copy microbetag utils 
WORKDIR /microbetag
ADD microbetagDB/mappings/kegg_mappings/*  ./microbetagDB/mappings/kegg_mappings/
ADD microbetagDB/mappings/MetaNetX/chem_xref.tsv ./microbetagDB/mappings/MetaNetX/chem_xref.tsv

ADD microbetagDB/ref-dbs/kofam_database/ko_list ./microbetagDB/ref-dbs/kofam_database/ko_list

RUN pip install pyshorteners ndex2 

ADD microbetag/ ./microbetag/
ADD microbetag.py  ./

ADD tests/ ./tests

ADD LICENSE ./

ENTRYPOINT [ "python3", "microbetag.py", "/data/config.yml" ]
