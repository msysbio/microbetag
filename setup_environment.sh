#!/bin/bash


# emojis -- hehe! :)
# ------
SMILE="\U0001F60A"
TADA="\U0001F389"
ROCKET="\U0001F680"
GREEN_TICK="\U00002705"
RED_CROSS="\U0000274C"
HOURGLASS="\u23F3"
WHITE_CIRCLE="\26AA"

# ====================================
# Step 1: Set up Conda environment
# NOTE: PYTHON 3.8 easier to have phenotrex 0.6.0
# ====================================
                                       
# Exit immediately if a command exits with a non-zero status
set -e

# Print each command before executing it (for debugging purposes)
set -x

# Check if conda is installed
if ! command -v conda &> /dev/null; then
    echo "Error: Conda is not installed or not in the PATH. $RED_CROSS"
    exit 1
fi

# Ensure Conda is initialized for the current shell
eval "$(conda shell.bash hook)"
echo "$WHITE_CIRCLE conda is available and ready to go!"

# Create and activate the phenodb environment


# Name of the environment
ENV_NAME="phendb"

# Check if the environment already exists
if conda info --envs | grep -q "$ENV_NAME"; then
    echo "$GREEN_TICK Environment '$ENV_NAME' already exists. Skipping creation."
else
    conda create -n phenodb python=3.8 -y
    echo "$GREEN_TICK A conda environment, named phendb, solely for phenotrex has been built. "
fi

# Install phenotrex
conda activate phenodb
echo "$HOURGLASS Install phenotrex..."
pip install phenotrex[fasta]
echo "$TADA phenotrex was installed successfully."
conda deactivate


ENV_NAME="microbetag"

if conda info --envs | grep -q "$ENV_NAME"; then
    echo "$GREEN_TICK Environment '$ENV_NAME' already exists. Skipping creation."
else

    # Create the microbetag environment and install dependencies
    echo "$HOURGLASS The primary Conda environment for running microbetag, which shares the same name, is currently under constructio.."
    # conda create -n microbetag python=3.10 -y
    conda env create -f environment.yml
    echo "$TADA microbetag conda environent was built successfully"
fi


# Install microbetag python library dependencies
conda activate microbetag
echo "$HOURGLASS Install further Python library dependencies"
pip install -r requirements.txt
echo "$TADA All environments and installations are complete!"


# ====================================
# Step 2: Install non-Conda dependencies
# ====================================

# NOTE: Remember the spaces between the brackets and the text in the if statements -- they are required!

# Check if the script is being executed as root or with sudo
if [ "$EUID" -eq 0 ]; then
    echo "$WHITE_CIRCLE The script is being executed as root (or with sudo)."
    sudo_user=True
    INSTALL_DIR="/usr/local/"
else
    echo "$WHITE_CIRCLE The script is NOT being executed as root (or with sudo)."
    echo "$WHITE_CIRCLE A hidden folder called `.microbetag` will be built under your `HOME` directory, where all required software will be installed."
    sudo_uer=False
    mkdir -p $HOME/.microbetag/
    INSTALL_DIR=$HOME/.microbetag/
fi


# Make sure Julia is installed -- used by FlashWeave
if command -v julia >/dev/null 2>&1  || [ -x "$INSTALL_DIR/julia" ]; then
    echo -e "$GREEN_TICK Julia is already installed."
else
    echo "$HOURGLASS Julia is not installed. Installing Julia..."
    cd $INSTALL_DIR
    wget https://julialang-s3.julialang.org/bin/linux/x64/1.7/julia-1.7.1-linux-x86_64.tar.gz
    tar -xvzf julia-1.7.1-linux-x86_64.tar.gz
    export PATH=$(pwd)/julia-1.7.1/bin/:$PATH
    PATH="/usr/local/julia-1.7.1/bin:${PATH}"
fi
julia -e 'using Pkg;Pkg.add("PyCall")'


# Make sure Prodigal is installed -- to get ORFs
if command -v prodigal >/dev/null 2>&1  || [ -x "$INSTALL_DIR/prodigal" ]; then
    echo -e "$GREEN_TICK Prodigal is already installed."
else
    echo "$HOURGLASS Prodigal is not installed. Installing Prodigal... "
    cd $INSTALL_DIR
    git clone https://github.com/hyattpd/Prodigal.git 
    cd Prodigal &&\ 
      make install INSTALLDIR=$INSTALL_DIR && \
      echo -e "$TADA Prodigal was installed. "
fi


# Make sure FragGeneScan is installed -- alternative to Prodigal -- NOTE: UP TO NOW, WE ACTUALLY DON'T NEED THIS
if command -v FragGeneScan > /dev/null 2>&1 || [ -x "$INSTALL_DIR/FragGeneScan" ]; then
    echo -e "$GREEN_TICK FragGeneScan is already installed."
else
    echo -e "$HOURGLASS FragGeneScan is not installed. Installing FragGeneScan... "
    cd $INSTALL_DIR
    git clone https://github.com/gaberoo/FragGeneScan.git &&\
    cd FragGeneScan/ &&\
    make &&\
    make fgs
    echo -e "$TADA FragGeneScan was installed. "
fi


# Make sure HMMER is installed -- hmmseach used to annotate KEGG orthologs with kofamscan
if command -v hmmscan >/dev/null 2>&1 || [ -x "$INSTALL_DIR/hmmscan" ]; then
    echo -e "$GREEN_TICK HMMER is already installed."
else
    echo "$HOURGLASS HMMER is not installed. Installing HMMER... "
    cd $INSTALL_DIR
    wget http://eddylab.org/software/hmmer/hmmer-3.4.tar.gz 
    tar xf hmmer-3.4.tar.gz 
    cd hmmer-3.4 
    ./configure 
    make 
    make install
    echo -e "$TADA HMMER was installed. "
fi


# Make sure DIAMOND is installed -- used by carveme
if command -v diamond >/dev/null 2>&1 || [ -x "$INSTALL_DIR/diamond" ]; then
    echo -e "$GREEN_TICK DIAMOND is already installed. "
else
    echo "$HOURGLASS DIAMOND is not installed. Installing HMMER... "
    cd $INSTALL_DIR
    wget http://github.com/bbuchfink/diamond/releases/download/v2.1.9/diamond-linux64.tar.gz 
    tar xzf diamond-linux64.tar.gz
    echo -e "$TADA DIAMOND was installed. "
fi


# Make sure RAST tools is installed -- used to reconstruct GEMs with modelseedpy
if command rast-create-genome >/dev/null 2>&1 || [ -x "$INSTALL_DIR/rast-create-genome" ]; then
    echo -e "$GREEN_TICK RAST tools is already installed. "
else
    echo "$HOURGLASS RAST tools is not installed. Installing RAST tools... "
    cd $INSTALL_DIR

    curl -O -L https://github.com/BV-BRC/BV-BRC-CLI/releases/download/1.040/bvbrc-cli-1.040.deb &&\
        yes | gdebi bvbrc-cli-1.040.deb

    echo -e "$TADA RAST tools was installed. "
fi






# # Make sure tRNAscan-SE is installed  -- on Docker we re using 1.4 so far -- TODO: DO WE ACTUALLY NEED THIS?
# if command -v trnascan-1.4 >/dev/null 2>&1  || [ -x "$INSTALL_DIR/trnascan-1.4" ]; then
#     echo -e "tRNAscan-SE is already installed. $GREEN_TICK"
# else
#     echo -e "tRNAscan-SE is not installed. Installing tRNAscan-SE... $HOURGLASS"
#     cd $INSTALL_DIR
#     wget --no-check-certificate http://lowelab.ucsc.edu/software/trnascan-se-2.0.12.tar.gz
#     gunzip trnascan-se-2.0.12.tar.gz 
#     tar xf trnascan-se-2.0.12.tar
#     cd tRNAscan-SE-2.0/
#     ./configure --prefix=$INSTALL_DIR --bindir=$INSTALL_DIR 
#     make 
#     make install
#     echo -e "tRNAscan-SE was installed. \U0001F389 "
# fi


# # Make sure MMseqs is installed -- TODO: DO WE ACTUALLY NEED THIS?
# if command -v mmseqs >/dev/null 2>&1 || [ -x "$INSTALL_DIR/mmseqs" ]; then
#     echo -e "MMseqs is already installed. $GREEN_TICK"
# else
#     echo -e "MMseqs is not installed. Installing MMseqs... $HOURGLASS"
#     cd $INSTALL_DIR

#     FILE="mmseqs-linux-avx2.tar.gz"

#     if [ ! -f "$FILE" ]; then
#         echo "File not found, downloading..."
#         wget https://mmseqs.com/latest/mmseqs-linux-avx2.tar.gz
#     else
#         echo "File already exists."
#     fi

#     tar xvfz mmseqs-linux-avx2.tar.gz
#     mv mmseqs mmseqs-linux-avx2
#     mv mmseqs-linux-avx2/bin/mmseqs .

#     echo -e "MMseqs was installed. $TADA"
# fi



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



