#!/bin/bash

# Install microbetag's dependencies 

# emojis -- hehe! :)
# ------
       SMILE="\U0001F60A"
        TADA="\U0001F389"
      ROCKET="\U0001F680"
  GREEN_TICK="\U00002705"
   RED_CROSS="\U0000274C"
  RED_CIRCLE="\U0001F534"
   HOURGLASS="\u23F3"
WHITE_CIRCLE="\u26AA"

# Default values
VERSION_ARG=false
   HELP_ARG=false
  KOFAM_ARG=false
 SCRIPT_DIR=$(dirname "$(realpath "$0")")

# Parse options using getopt
PARSED=$(getopt --options kh --long kofam,help -- "$@")
if [[ $? -ne 0 ]]; then
  echo "❌ Failed to parse options." >&2
  exit 1
fi

# Reorder arguments so they can be processed
eval set -- "$PARSED"

# Loop through options
while true; do
  case "$1" in
    -k|--kofam)
      KOFAM_ARG=true
      shift
      ;;
    -h|--help)
      HELP_ARG=true
      shift
      ;;
    --)
      shift
      break
      ;;
    *)
      echo "Unexpected option: $1" >&2
      exit 1
      ;;
  esac
done

# 
echo -e "\n Building conda environment and installing required dependencies to enable microbetag ${ROCKET} \n\n"

if $HELP_ARG; then
  echo "Usage: bash setup_environment.sh [options]"
  echo "  -h, --help     Show this help message"
  echo "  -k, --kofam    kofam database will be downloaded and installed in the ext_data/kofam_database folder"
  echo ""
  echo -e "${RED_CIRCLE} Either conda or miniconda is considered to be available. If not, setup_environment.sh will fail."
  echo -e "${RED_CIRCLE} Make sure you run the script from the root folder of the microbetag repository."
  exit 0
fi


# ====================================
# Step 0: kofam database
# Make sure kofam db is there if needed
# ====================================

if $KOFAM_ARG; then

    cd ext_data/kofam_database &&\
    wget -c ftp://ftp.genome.jp/pub/db/kofam/ko_list.gz &&\
    wget -c ftp://ftp.genome.jp/pub/db/kofam/profiles.tar.gz &&\
    gzip -d ko_list.gz &&\
    tar zxvf profiles.tar.gz 
    cd $SCRIPT_DIR

else

  echo -e "${RED_CIRCLE} The kofam database will not be downloaded."
  echo "Yet, it is required in case you wish to get pathway complementarities using custom genomes."
  echo -e "Thus, you should have already it on your computing system and provide the path to it on the configuration YAML file.\n"
  echo -e "${WHITE_CIRCLE} Otherwise, add argument --kofam when running setup_environment.sh"
  echo ""
  echo -e "bash setup_environment.sh --kofam\n"


fi

# ====================================
# Step 1: Set up Conda environment
# NOTE: PYTHON 3.8 easier to have phenotrex 0.6.0
# ====================================
                                       
# Exit immediately if a command exits with a non-zero status
set -e

# # Print each command before executing it (for debugging purposes)
# set -x

# Check if conda is installed
if ! command -v conda &> /dev/null; then
    echo -e "Error: Conda is not installed or not in the PATH. $RED_CROSS"
    exit 1
fi

# Ensure Conda is initialized for the current shell
eval "$(conda shell.bash hook)"
echo -e "$WHITE_CIRCLE conda is available and ready to go!"

# -----------------------------------------------------------------------------

# Create and activate the phendb environment
ENV_NAME="mtg-phenotrex"

# Check if the environment already exists
if conda info --envs | grep -q "$ENV_NAME"; then
    echo -e "$GREEN_TICK Environment '$ENV_NAME' already exists. Skipping creation."
else
    conda create -n $ENV_NAME python=3.8 -y
    echo -e "$GREEN_TICK A conda environment, named phendb, solely for phenotrex has been built. "
fi

# Install phenotrex
conda activate $ENV_NAME

echo -e "$HOURGLASS Install numpy phenotrex required version...."
pip install --upgrade pip setuptools wheel
pip install --force numpy==1.21.6

echo -e "$HOURGLASS Install phenotrex..."
pip install phenotrex[fasta]  > /dev/null 2>&1


echo -e "$TADA phenotrex was installed successfully."
conda deactivate

# -----------------------------------------------------------------------------

ENV_NAME="mtg-modelseed"

# Check if the environment already exists
if conda info --envs | grep -q "$ENV_NAME"; then
    echo -e "$GREEN_TICK Environment '$ENV_NAME' already exists. Skipping creation."
else
    conda create -n $ENV_NAME python=3.9 -y
    echo -e "$GREEN_TICK A conda environment, named "$ENV_NAME" was built. "
fi

# Install ModelSEEDpy
conda activate $ENV_NAME


pip install -r requirements/modelseedpy.txt

# -----------------------------------------------------------------------------


ENV_NAME="mtg-dnngior"

# Check if the environment already exists
if conda info --envs | grep -q "$ENV_NAME"; then
    echo -e "$GREEN_TICK Environment '$ENV_NAME' already exists. Skipping creation."
else
    conda create -n $ENV_NAME python=3.9 -y
    echo -e "$GREEN_TICK A conda environment, named "$ENV_NAME" was built. "
fi

# Install ModelSEEDpy
conda activate $ENV_NAME

pip install -r requirements/dnngior.txt


# -----------------------------------------------------------------------------

ENV_NAME="microbetag"

if conda info --envs | grep -q "$ENV_NAME"; then
    echo -e "$GREEN_TICK Environment '$ENV_NAME' already exists. Skipping creation."
else

    # Create the microbetag environment and install dependencies
    echo -e "$HOURGLASS The primary conda environment for running microbetag, " 
    echo -e "which shares the same name, is currently under constructio.."

    conda env create -f environment.yml

    echo -e "$TADA microbetag conda environent was built successfully"
fi


# Install microbetag python library dependencies
conda activate microbetag

# TODO: DO WE NEED THIS ? 
echo -e "$HOURGLASS Install further Python library dependencies"
pip install -r requirements.txt  > /dev/null 2>&1
echo -e "$TADA All environments and installations are complete!"


# -----------------------------------------------------------------------------

# ====================================
# Step 2: Install non-Conda dependencies
# ====================================

# NOTE: Remember the spaces between the brackets and the text in the if statements -- they are required!


# Check if the script is being executed as root or with sudo
if [ "$EUID" -eq 0 ]; then
    echo -e "$WHITE_CIRCLE The script is being executed as root (or with sudo)."
    sudo_user=True
    INSTALL_DIR="/usr/local/"
else
    echo -e "$WHITE_CIRCLE The script is NOT being executed as root (or with sudo)."
    echo -e "$WHITE_CIRCLE A hidden folder called `.microbetag` will be built under your `HOME` directory, where all required software will be installed."
    sudo_uer=False
    mkdir -p $HOME/.microbetag/
    INSTALL_DIR=$HOME/.microbetag/
    echo -e "export PATH=\$PATH:$INSTALL_DIR" >> ~/.bashrc
    source ~/.bashrc
fi

# Make sure Julia is installed -- used by FlashWeave
if command -v julia >/dev/null 2>&1  || [ -x "$INSTALL_DIR/julia" ]; then
    echo -e "$GREEN_TICK Julia is already installed."
else
    echo -e "$HOURGLASS Julia is not installed. Installing Julia..."
    cd $INSTALL_DIR

    if [ -f "julia-1.7.1-linux-x86_64.tar.gz" ]; then
        echo "Julia tarball already exists."
    else
        echo "Downloading Julia tarball..."
        wget https://julialang-s3.julialang.org/bin/linux/x64/1.7/julia-1.7.1-linux-x86_64.tar.gz
        tar -xvzf julia-1.7.1-linux-x86_64.tar.gz  > /dev/null 2>&1
    fi
    echo PATH=$(pwd)/julia-1.7.1/bin/:$PATH >> ~/.bashrc
    source ~/.bashrc
    conda activate microbetag
fi
julia -e 'using Pkg; Pkg.add("PyCall"); Pkg.add("FlashWeave")'


# Make sure Prodigal is installed -- to get ORFs
if command -v prodigal >/dev/null 2>&1  || [ -x "$INSTALL_DIR/prodigal" ]; then
    echo -e "$GREEN_TICK Prodigal is already installed."
else
    echo -e "$HOURGLASS Prodigal is not installed. Installing Prodigal... "
    cd $INSTALL_DIR
    if [ -d "Prodigal/.git" ]; then
        echo "Prodigal repository already exists."
    else
        echo "Cloning Prodigal repository..."
        git clone https://github.com/hyattpd/Prodigal.git  > /dev/null 2>&1
    fi
    cd Prodigal
    make install INSTALLDIR=$INSTALL_DIR 
    echo -e "$TADA Prodigal was installed. "
fi


# Make sure FragGeneScan is installed -- alternative to Prodigal -- NOTE: UP TO NOW, WE ACTUALLY DON'T NEED THIS
if command -v FragGeneScan > /dev/null 2>&1 || [ -x "$INSTALL_DIR/FragGeneScan" ]; then
    echo -e "$GREEN_TICK FragGeneScan is already installed."
else
    echo -e "$HOURGLASS FragGeneScan is not installed. Installing FragGeneScan... "
    cd $INSTALL_DIR

    if [ -d "FragGeneScan/.git" ]; then
        echo "FragGeneScan repository already exists."
    else
        echo "Cloning FragGeneScan repository..."
        git clone https://github.com/gaberoo/FragGeneScan.git   > /dev/null 2>&1
    fi

    cd FragGeneScan/  
    make  > /dev/null 2>&1
    make fgs  > /dev/null 2>&1
    echo -e "$TADA FragGeneScan was installed. "
fi


# Make sure HMMER is installed -- hmmseach used to annotate KEGG orthologs with kofamscan
if command -v hmmscan >/dev/null 2>&1 || [ -x "$INSTALL_DIR/hmmscan" ]; then
    echo -e "$GREEN_TICK HMMER is already installed."
else
    echo -e "$HOURGLASS HMMER is not installed. Installing HMMER... "
    cd $INSTALL_DIR

    if [ -f "hmmer-3.4.tar.gz" ]; then
        echo "HMMER 3.4 tarball already exists."
    else
        echo "Downloading HMMER 3.4 tarball..."
        wget http://eddylab.org/software/hmmer/hmmer-3.4.tar.gz   > /dev/null 2>&1
        tar xf hmmer-3.4.tar.gz   > /dev/null 2>&1
    fi
    cd hmmer-3.4 
    ./configure --prefix=$INSTALL_DIR  > /dev/null 2>&1
    make  > /dev/null 2>&1
    make install  > /dev/null 2>&1
    echo -e "$TADA HMMER was installed. "
fi


# Make sure DIAMOND is installed -- used by carveme
if command -v diamond >/dev/null 2>&1 || [ -x "$INSTALL_DIR/diamond" ]; then
    echo -e "$GREEN_TICK DIAMOND is already installed. "
else
    echo -e "$HOURGLASS DIAMOND is not installed. Installing HMMER... "
    cd $INSTALL_DIR

    if [ -f "diamond-linux64.tar.gz" ]; then
        echo "DIAMOND tarball already exists."
    else
        echo "Downloading DIAMOND tarball..."
        wget http://github.com/bbuchfink/diamond/releases/download/v2.1.9/diamond-linux64.tar.gz   > /dev/null 2>&1
        tar xf diamond-linux64.tar.gz  > /dev/null 2>&1
    fi
    echo -e "$TADA DIAMOND was installed. "
fi


# Make sure RAST tools is installed -- used to reconstruct GEMs with modelseedpy
if command rast-create-genome >/dev/null 2>&1 || [ -x "$INSTALL_DIR/rast-create-genome" ]; then
    echo -e "$GREEN_TICK RAST tools is already installed. "
else
    echo -e "$HOURGLASS RAST tools is not installed. Installing RAST tools... "
    echo -e "WHITE_CIRCLE To download RAST tools, a set of system-wide libraries are required."
    echo "First, gdebi: a simple tool to install deb files "
    echo "Then, a set of Perl-related libraries"
    echo "The setup_environment.sh script will let you know which Perl libraries are missing, but you will need your admin (sudo rights) to set them."
    echo -e "$EYES In case this step is failing, you may install RAST tools using the instructions you may find here:
     https://www.bv-brc.org/docs///cli_tutorial/cli_installation.html"

    cd $INSTALL_DIR

    if [ -f "bvbrc-cli-1.040.deb" ]; then
        echo "RAST tools tarball exists."
    else
        echo "Downloading RAST tools deb..."
        curl -O -L https://github.com/BV-BRC/BV-BRC-CLI/releases/download/1.040/bvbrc-cli-1.040.deb
    fi

    dpkg --instdir=. -i bvbrc-cli-1.040.deb

    # gdebi bvbrc-cli-1.040.deb
    echo -e "$TADA RAST tools was installed. "
fi

# Install microbetag lib
cd $SCRIPT_DIR

# Install Python-specific tools
pip install .

# Get MetaNetX namespace
META_DIR="$SCRIPT_DIR/microbetag/mtg_maps_models/MetaNetX"
TAR_FILE="$META_DIR/chem_xref.tar.gz"

# Create folder if it doesn't exist
if [ ! -d "$META_DIR" ]; then
    mkdir -p "$META_DIR"
fi

# Download the file only if it's not already there
if [ ! -f "$TAR_FILE" ]; then
    echo "Downloading chem_xref.tar.gz..."
    wget -O "$TAR_FILE" https://zenodo.org/records/15102937/files/chem_xref.tar.gz
else
    echo "File already exists: $TAR_FILE"
fi


# Good bye! :)
echo "microbetag is now good to go! $TADA $ROCKET"
