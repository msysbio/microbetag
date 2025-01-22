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
LABEL build_date = "2024-08-06"
LABEL version    = "v.1.1"


# Copy microbetag utils 
WORKDIR /microbetag
ADD microbetagDB/mappings/kegg_mappings/*  ./microbetagDB/mappings/kegg_mappings/
ADD microbetagDB/mappings/MetaNetX/chem_xref.tsv ./microbetagDB/mappings/MetaNetX/chem_xref.tsv
#ADD microbetagDB/scripts/flashweave.jl ./microbetagDB/scripts/flashweave.jl
ADD microbetagDB/ref-dbs/kofam_database/ko_list ./microbetagDB/ref-dbs/kofam_database/ko_list
ADD utils.py ./
ADD microbetag.py  ./
ADD config.py ./
ADD build_cx_annotated_graph.py ./
ADD LICENSE ./

RUN pip install pyshorteners ndex2 

ENTRYPOINT [ "python3", "microbetag.py", "/data/config.yml" ]
