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
LABEL version    = "v1.0.4"

# Add lib
RUN pip install pyshorteners ndex2 

# Copy microbetag utils 
WORKDIR /microbetag
ADD ext_data/kofam_database/ko_list ./microbetag/mtg_maps_models/kofam_database/ko_list

# Add source code 
ADD microbetag/ ./microbetag/

# Add addtional 
ADD tests/ ./tests
ADD LICENSE ./

ENTRYPOINT [ "python3", "microbetag.py", "/data/*.yml" ]
