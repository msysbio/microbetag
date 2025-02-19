#!/bin/bash

# # Step 1: Set up Conda environment     ---    NOTE: PYTHON 3.8 easier to have phenotrex 0.6.0
                                       

# conda create -n phenodb python=3.8
# conda activate phenodb 
# pip install phenotrex[fasta]
# conda deactivate 


# conda create -n microbetag python=3.10
# pip install -r requirements.txt





# # Step 2: Activate Conda environment
# conda activate microbetag

# Step 3: Install non-Conda dependencies


# NOTE: SUPER IMPORTANT 
# WE NEED TO EDIT THE SKLEARN VERSION
# WORKDIR /usr/local/lib/python3.8/dist-packages/sklearn
# RUN find . -type f -name "*.py" -exec sed -i 's/np\.float)/float)/g; s/np\.float,/float,/g' {} +

# emojis
# ------
SMILE="\U0001F60A"
TADA="\U0001F389"
ROCKET="\U0001F680"
GREEN_TICK="\U00002705"
RED_CROSS="\U0000274C"
HOURGLASS="\u23F3"

# NOTE: Remember the spaces between the brackets and the text in the if statements -- they are required!

# Check if the script is being executed as root or with sudo
if [ "$EUID" -eq 0 ]; then
    echo "The script is being executed as root (or with sudo)."
    sudo_user=True
    INSTALL_DIR="/usr/local/"
else
    echo "The script is NOT being executed as root (or with sudo)."
    sudo_uer=False
    mkdir -p $HOME/.microbetag/
    INSTALL_DIR=$HOME/.microbetag/
fi


# Make sure Julia is installed -- used by FlashWeave
if command -v julia >/dev/null 2>&1  || [ -x "$INSTALL_DIR/julia" ]; then
    echo -e "Julia is already installed. $GREEN_TICK"
else
    echo "Julia is not installed. Installing Julia... $HOURGLASS"
    cd $INSTALL_DIR
    wget https://julialang-s3.julialang.org/bin/linux/x64/1.7/julia-1.7.1-linux-x86_64.tar.gz
    tar -xvzf julia-1.7.1-linux-x86_64.tar.gz
    export PATH=$(pwd)/julia-1.7.1/bin/:$PATH
    PATH="/usr/local/julia-1.7.1/bin:${PATH}"
fi
julia -e 'using Pkg;Pkg.add("PyCall")'


# Make sure Prodigal is installed -- to get ORFs
if command -v prodigal >/dev/null 2>&1  || [ -x "$INSTALL_DIR/prodigal" ]; then
    echo -e "Prodigal is already installed. $GREEN_TICK"
else
    echo "Prodigal is not installed. Installing Prodigal... $HOURGLASS"
    cd $INSTALL_DIR
    git clone https://github.com/hyattpd/Prodigal.git 
    cd Prodigal &&\ 
      make install INSTALLDIR=$INSTALL_DIR && \
      echo -e "Prodigal was installed. $TADA"
fi

# Make sure FragGeneScan is installed -- alternative to Prodigal -- NOTE: UP TO NOW, WE ACTUALLY DON'T NEED THIS
if command -v FragGeneScan > /dev/null 2>&1 || [ -x "$INSTALL_DIR/FragGeneScan" ]; then
    echo -e "FragGeneScan is already installed. $GREEN_TICK"
else
    echo -e "FragGeneScan is not installed. Installing FragGeneScan... $HOURGLASS"
    cd $INSTALL_DIR
    git clone https://github.com/gaberoo/FragGeneScan.git &&\
    mv FragGeneScan FragGeneScanDir &&\
    cd FragGeneScanDir/ &&\
    make &&\
    make fgs
    mv FragGeneScan ../
    echo -e "FragGeneScan was installed. $TADA"
fi

# Make sure tRNAscan-SE is installed  -- on Docker we re using 1.4 so far -- TODO: DO WE ACTUALLY NEED THIS?
if command -v trnascan-1.4 >/dev/null 2>&1  || [ -x "$INSTALL_DIR/trnascan-1.4" ]; then
    echo -e "tRNAscan-SE is already installed. $GREEN_TICK"
else
    echo -e "tRNAscan-SE is not installed. Installing tRNAscan-SE... $HOURGLASS"
    cd $INSTALL_DIR
    wget --no-check-certificate http://lowelab.ucsc.edu/software/trnascan-se-2.0.12.tar.gz
    gunzip trnascan-se-2.0.12.tar.gz 
    tar xf trnascan-se-2.0.12.tar
    cd tRNAscan-SE-2.0/
    ./configure --prefix=$INSTALL_DIR --bindir=$INSTALL_DIR 
    make 
    make install
    echo -e "tRNAscan-SE was installed. \U0001F389 "
fi


# Make sure MMseqs is installed -- TODO: DO WE ACTUALLY NEED THIS?
if command -v mmseqs >/dev/null 2>&1 || [ -x "$INSTALL_DIR/mmseqs" ]; then
    echo -e "MMseqs is already installed. $GREEN_TICK"
else
    echo -e "MMseqs is not installed. Installing MMseqs... $HOURGLASS"
    cd $INSTALL_DIR

    FILE="mmseqs-linux-avx2.tar.gz"

    if [ ! -f "$FILE" ]; then
        echo "File not found, downloading..."
        wget https://mmseqs.com/latest/mmseqs-linux-avx2.tar.gz
    else
        echo "File already exists."
    fi

    tar xvfz mmseqs-linux-avx2.tar.gz
    mv mmseqs mmseqs-linux-avx2
    mv mmseqs-linux-avx2/bin/mmseqs .

    echo -e "MMseqs was installed. $TADA"
fi


# Make sure HMMER is installed -- hmmseach used to annotate KEGG orthologs with kofamscan
if command -v hmmscan >/dev/null 2>&1 || [ -x "$INSTALL_DIR/hmmscan" ]; then
    echo -e "HMMER is already installed. $GREEN_TICK"
else
    echo "HMMER is not installed. Installing HMMER... $HOURGLASS"
    cd $INSTALL_DIR
    wget http://eddylab.org/software/hmmer/hmmer-3.4.tar.gz 
    tar xf hmmer-3.4.tar.gz 
    cd hmmer-3.4 
    ./configure 
    make 
    make install
    echo -e "HMMER was installed. $TADA"
fi


# Make sure DIAMOND is installed -- used by carveme
if command -v diamond >/dev/null 2>&1 || [ -x "$INSTALL_DIR/diamond" ]; then
    echo -e "DIAMOND is already installed. $GREEN_TICK"
else
    echo "DIAMOND is not installed. Installing HMMER... $HOURGLASS"
    cd $INSTALL_DIR
    wget http://github.com/bbuchfink/diamond/releases/download/v2.1.9/diamond-linux64.tar.gz 
    tar xzf diamond-linux64.tar.gz
    echo -e "DIAMOND was installed. $TADA"
fi


# Make sure RAST tools is installed -- used to reconstruct GEMs with modelseedpy
if command rast-create-genome >/dev/null 2>&1 || [ -x "$INSTALL_DIR/rast-create-genome" ]; then
    echo -e "RAST tools is already installed. $GREEN_TICK"
else
    echo "RAST tools is not installed. Installing RAST tools... $HOURGLASS"
    cd $INSTALL_DIR

    curl -O -L https://github.com/BV-BRC/BV-BRC-CLI/releases/download/1.040/bvbrc-cli-1.040.deb &&\
        yes | gdebi bvbrc-cli-1.040.deb

    echo -e "RAST tools was installed. $TADA"
fi
# 




# # Make sure Gapseq is installed
# if type gapfill &> /dev/null; then
#     echo "Gapfill is installed."
# else
#     echo "Gapfill is not installed. Installing Gapfill..."

#     # List of required packages
#     dependencies=(
#       "ncbi-blast+"
#       "git"
#       "libglpk-dev"
#       "r-base-core"
#       "exonerate"
#       "bedtools"
#       "barrnap"
#       "bc"
#       "parallel"
#       "curl"
#       "libcurl4-openssl-dev"
#       "libssl-dev"
#       "libsbml5-dev"
#     )
#     missing=false
#     # Function to check if a package is installed
#     check_package() {
#         if dpkg -l | grep -qw "$1"; then
#             echo "$1 is installed."
#         else
#             echo "$1 is missing! Please contact the admin to install it."
#             missing=true
#         fi
#     }
#     # Iterate over each dependency and check
#     for pkg in "${dependencies[@]}"; do
#         check_package "$pkg"
#     done

#     if [ "$missing" = true ]; then
#         echo "One or more dependencies are missing. Exiting."
#         exit 1
#     else
#         echo "All dependencies are installed. Proceeding with the script."
#     fi

#     # Install R packages
#     R -e 'install.packages(c("data.table", "stringr", "getopt", "doParallel", "foreach", "R.utils", "stringi", "glpkAPI", "CHNOSZ", "jsonlite", "httr"))' 

#     wget https://cran.r-project.org/src/contrib/Archive/sybil/sybil_2.2.0.tar.gz
#     wget https://cran.r-project.org/src/contrib/Archive/sybilSBML/sybilSBML_3.1.2.tar.gz

#     apt install -y ncbi-blast+ git libglpk-dev r-base-core exonerate bedtools barrnap bc parallel curl libcurl4-openssl-dev libssl-dev  libsbml5-dev bc

#     R CMD INSTALL sybil_2.2.0.tar.gz
#     RUN R CMD INSTALL sybilSBML_3.1.2.tar.gz



echo $PATH
echo "export PATH=\$PATH:$INSTALL_DIR" >> ~/.bashrc
source ~/.bashrc
echo $PATH


# # this should be ONLY for sudo and not sure if it is not necessary
# rm -rf /var/lib/apt/lists/*





# # Step 3: Install non-Conda dependencies
# # Install barrnap, bedtools, etc., via apt or other package managers
# sudo apt-get update && sudo apt-get install -y \
#   infernal infernal-doc \
#   barrnap bedtools exonerate ncbi-blast+

# # Install Python-specific tools
# pip install git+https://github.com/hariszaf/manta.git@scipy-version 

# pip install julia
# /opt/julia-1.7.1/bin/julia -e 'using Pkg;Pkg.add("PyCall")'


# # Install R-specific tools
# R CMD INSTALL sybilSBML_3.1.2.tar.gz



