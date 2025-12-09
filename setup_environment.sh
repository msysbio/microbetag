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
        SKIP="\u23E9"
        BACT="\U1F9A0"

# Default values
 VERSION_ARG=false
    HELP_ARG=false
   KOFAM_ARG=false
   PHENO_ARG=false
MODESEED_ARG=false
 DNNGIOR_ARG=false
  SCRIPT_DIR=$(dirname "$(realpath "$0")")

# Versions
     JULIA_V=1.9.4  # 1.7.1
     HMMER_V=3.4
 NUMPY_PHENO=1.21.6
PYTHON_PHENO=3.8
   PYTHON_MS=3.9
  PYTHON_DNN=3.9
   DIAMOND_V=2.1.9
    RASTTK_V=1.040

# Parse options using getopt -- list with all the potential arguments
PARSED=$(getopt --options kmdph --long kofam,modelseed,dnngior,phenotrex,help -- "$@")
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
    -m|--modelseed)
      MODESEED_ARG=true
      shift
      ;;
    -d|--dnngior)
      DNNGIOR_ARG=true
      shift
      ;;
    -p|--phenotrex)
      PHENO_ARG=true
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

# Help message
if $HELP_ARG; then
  echo -e "$BACT Installation script for microbetag's requirements.\n"
  echo "Usage: bash setup_environment.sh [options]"
  echo "  -h, --help        Show this help message"
  echo "  -k, --kofam       kofam database will be downloaded and installed in the ext_data/kofam_database folder (.gz file ~1.5G)"
  echo "  -m, --modelseed   Install dependencies for GEM reconstruction using ModeSEEDpy (https://modelseedpy.readthedocs.io)."
  echo "  -p, --phenotrex   Install dependencies for trait prediction with Phenotrex (https://phenotrex.readthedocs.io)."
  echo "  -d, --dnngior     Install dependencies for gap-filling GEMs using DNNGIOR (DOI: https://doi.org/10.1016/j.isci.2024.111349)"
  echo ""
  echo -e "${RED_CIRCLE} Either conda or miniconda is considered to be available. If not, setup_environment.sh will fail."
  echo -e "${RED_CIRCLE} Make sure you run the script from the root folder of the microbetag repository."
  exit 0
fi

echo -e "\n\n This is the installation setup for microbetag. In case you have trouble running this, feel free to join our Matrix community and share your troubles: https://matrix.to/#/#microbetagcommunity:matrix.org \n\n"

# ====================================
# Step 0: kofam database
# Make sure kofam db is there if needed
# ====================================

if $KOFAM_ARG; then

    cd ext_data/kofam_database
    wget -c ftp://ftp.genome.jp/pub/db/kofam/ko_list.gz 
    wget -c ftp://ftp.genome.jp/pub/db/kofam/profiles.tar.gz 
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

# --- Detect Conda binary ---
if [ -x "/opt/miniconda/bin/conda" ]; then
    CONDA_BIN="/opt/miniconda/bin/conda"
elif [ -x "$HOME/miniconda3/bin/conda" ]; then
    CONDA_BIN="$HOME/miniconda3/bin/conda"
elif command -v conda >/dev/null 2>&1; then
    CONDA_BIN="$(command -v conda)"
else
    echo -e "Error: Conda is not installed. $RED_CROSS"
    exit 1
fi

# --- Initialize Conda for this shell ---
echo -e "Run conda eval"
eval "$(conda shell.bash hook)"
echo -e "$WHITE_CIRCLE conda is available and ready to go!"

# echo -e "Accept conda TOS"
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r

# echo -e "Source conda profile"
# source "$HOME/miniconda/etc/profile.d/conda.sh"
conda init

# -----------------------------------------------------------------------------

if $PHENO_ARG; then

    # Create and activate the phendb environment
    ENV_NAME="mtg-phenotrex"

    # Check if the environment already exists
    if conda info --envs | grep -q "$ENV_NAME"; then
        echo -e "$GREEN_TICK Environment '$ENV_NAME' already exists. Skipping creation."
    else
        conda create -n $ENV_NAME python=${PYTHON_PHENO} -y
        echo -e "$GREEN_TICK A conda environment, named phendb, solely for phenotrex has been built. "
    fi

    # Install phenotrex
    conda activate $ENV_NAME

    echo -e "$HOURGLASS Install numpy phenotrex required version..."
    pip install --upgrade pip setuptools wheel
    pip install --force numpy==${NUMPY_PHENO}

    echo -e "$HOURGLASS Install phenotrex..!."
    pip --default-timeout=120 install phenotrex[fasta] # > /dev/null 2>&1


    echo -e "$TADA phenotrex was installed successfully."
    conda deactivate

else

    echo -e "$SKIP Skip phenotrex dependencies."

fi

# -----------------------------------------------------------------------------


if $MODESEED_ARG; then

    ENV_NAME="mtg-modelseed"

    # Check if the environment already exists
    if conda info --envs | grep -q "$ENV_NAME"; then
        echo -e "$GREEN_TICK Environment '$ENV_NAME' already exists. Skipping creation."
    else
        conda create -n $ENV_NAME python=${PYTHON_MS} -y
        echo -e "$GREEN_TICK A conda environment, named "$ENV_NAME" was built. "
    fi

    # Install ModelSEEDpy
    conda activate $ENV_NAME

    pip install --timeout 120 --retries 10 --resume-retries 5 -r requirements/modelseedpy.txt

    echo -e "Requirements for modelseedpy environment have been installed sucessfully $TADA"

    conda deactivate

else 
    echo -e "$SKIP Skip ModeSEEDpy dependencies."
fi


# -----------------------------------------------------------------------------

if $DNNGIOR_ARG; then

    ENV_NAME="mtg-dnngior"

    # Check if the environment already exists
    if conda info --envs | grep -q "$ENV_NAME"; then
        echo -e "$GREEN_TICK Environment '$ENV_NAME' already exists. Skipping creation."
    else
        conda create -n $ENV_NAME python=${PYTHON_DNN} -y
        echo -e "$GREEN_TICK A conda environment, named "$ENV_NAME" was built. "
    fi

    # Install ModelSEEDpy
    conda activate $ENV_NAME

    pip install --timeout 120 --retries 10 --resume-retries 5 -r requirements/dnngior.txt

else

    echo -e "$SKIP Skip installing dependencies regarding DNNGIOR gap-filler."

fi

# -----------------------------------------------------------------------------

ENV_NAME="microbetag"

if conda info --envs | grep -q "$ENV_NAME"; then

    echo -e "$GREEN_TICK Environment '$ENV_NAME' already exists. Skipping creation."

else

    # Create the microbetag environment and install dependencies
    echo -e "$HOURGLASS The primary conda environment for running microbetag is currently under construction.." 

    conda env create -n "$ENV_NAME" -f environment.yml

    echo -e "$TADA microbetag conda environent was built successfully"
fi

conda activate $ENV_NAME

# Install microbetag python library
echo -e "$HOURGLASS Install microbetag library... "
pip install --timeout 120 --retries 10 . 

echo -e "$TADA microbetag library has been installed!"

# ====================================
# Step 2: Install non-Conda dependencies
# ====================================

# NOTE: Remember the spaces between the brackets and the text in the if statements -- they are required!

# Check if the script is being executed as root or with sudo
if [ "$EUID" -eq 0 ]; then
    printf "%b The script is being executed as root (or with sudo).\n" "$WHITE_CIRCLE"
    sudo_user=True
    INSTALL_DIR="/usr/local/"

else
    echo -e "$WHITE_CIRCLE The script is NOT being executed as root (or with sudo)."
    echo -e "$WHITE_CIRCLE A hidden folder called `.microbetag` will be built under your `HOME` directory, where all required software will be installed."
    sudo_user=False
    mkdir -p $HOME/.microbetag/
    INSTALL_DIR=$HOME/.microbetag/
    echo -e "export PATH=\$PATH:$INSTALL_DIR" >> ~/.bashrc
    source ~/.bashrc

fi

# Make sure Julia is installed -- used by FlashWeave
JULIA_BIN="$INSTALL_DIR/julia-${JULIA_V}/bin/julia"
if command -v julia >/dev/null 2>&1 || [ -x "$JULIA_BIN" ]; then
    echo -e "$GREEN_TICK Julia is already installed."
    echo -e "Installing FlashWeave via Julia..."
else
    echo -e "$HOURGLASS Julia is not installed. Installing Julia..."
    cd "$INSTALL_DIR" || exit

    if [ -f "julia-${JULIA_V}-linux-x86_64.tar.gz" ]; then
        echo "Julia tarball already exists."
    else
        echo "Downloading Julia tarball..."
        wget -c --tries=10 --timeout=30 \
            "https://julialang-s3.julialang.org/bin/linux/x64/${JULIA_V%.*}/julia-${JULIA_V}-linux-x86_64.tar.gz"
        tar -xvzf "julia-${JULIA_V}-linux-x86_64.tar.gz" > /dev/null 2>&1
    fi

    # Add Julia to PATH if not already present
    if ! grep -q "$INSTALL_DIR/julia-${JULIA_V}/bin" ~/.bashrc; then
        echo "export PATH=\"$INSTALL_DIR/julia-${JULIA_V}/bin:\$PATH\"" >> ~/.bashrc
        source ~/.bashrc
    fi

    # Clear executable stack if patchelf is available
    if command -v patchelf >/dev/null 2>&1; then
        patchelf --clear-execstack "$INSTALL_DIR/julia-${JULIA_V}/lib/julia/libopenlibm.so"
    else
        echo "patchelf not found, skipping execstack patch"
    fi

    # Install FlashWeave via Julia
    "$JULIA_BIN" -e 'using Pkg; Pkg.add("PyCall"); Pkg.add("FlashWeave")'
fi

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

# Make sure HMMER is installed -- hmmseach used to annotate KEGG orthologs with kofamscan
if command -v hmmscan >/dev/null 2>&1 || [ -x "$INSTALL_DIR/hmmscan" ]; then
    echo -e "$GREEN_TICK HMMER is already installed."
else
    echo -e "$HOURGLASS HMMER is not installed. Installing HMMER... "
    cd $INSTALL_DIR

    if [ -f "hmmer-${HMMER_V}.tar.gz" ]; then
        echo "HMMER ${HMMER_V} tarball already exists."
    else
        echo "Downloading HMMER ${HMMER_V} tarball..."
        wget http://eddylab.org/software/hmmer/hmmer-${HMMER_V}.tar.gz   > /dev/null 2>&1
        tar xf hmmer-${HMMER_V}.tar.gz   > /dev/null 2>&1
    fi
    cd hmmer-${HMMER_V} 
    ./configure --prefix=$INSTALL_DIR  > /dev/null 2>&1
    make  > /dev/null 2>&1
    make install  > /dev/null 2>&1

    echo -e "Add hmmer to PATH"
    echo "export PATH=\"$INSTALL_DIR/hmmer-${HMMER_V}/bin:\$PATH\"" >> ~/.bashrc
    source ~/.bashrc

    echo -e "$TADA HMMER was installed. \n\n"
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
        wget http://github.com/bbuchfink/diamond/releases/download/v${DIAMOND_V}/diamond-linux64.tar.gz   > /dev/null 2>&1
        tar xf diamond-linux64.tar.gz  > /dev/null 2>&1
    fi
    echo -e "$TADA DIAMOND was installed. "
fi


# Make sure RAST tools is installed -- used to reconstruct GEMs with modelseedpy
if $MODESEED_ARG; then

    if command rast-create-genome >/dev/null 2>&1 || [ -x "$INSTALL_DIR/rast-create-genome" ]; then
        echo -e "$GREEN_TICK RAST tools is already installed. "

    else
        echo -e "$HOURGLASS RAST tools is not installed. Installing RAST tools... "
        echo -e "$WHITE_CIRCLE To download RAST tools, a set of system-wide libraries are required."
        echo "First, gdebi: a simple tool to install deb files "
        echo "Then, a set of Perl-related libraries"
        echo "The setup_environment.sh script will let you know which Perl libraries are missing, but you will need your admin (sudo rights) to set them."
        echo -e "$EYES In case this step is failing, you may install RAST tools using the instructions you may find here:
        https://www.bv-brc.org/docs///cli_tutorial/cli_installation.html"

        cd $INSTALL_DIR

        if [ -f "bvbrc-cli-${RASTTK_V}.deb" ]; then
            echo "RAST tools tarball exists."
        else
            echo "Downloading RAST tools deb..."
            curl -O -L https://github.com/BV-BRC/BV-BRC-CLI/releases/download/${RASTTK_V}/bvbrc-cli-${RASTTK_V}.deb
        fi

        sudo dpkg --instdir=. -i bvbrc-cli-${RASTTK_V}.deb

        # gdebi bvbrc-cli-${RASTTK_V}.deb
        echo -e "$TADA RAST tools was installed. "
    fi

else 

    echo "$SKIP Using ModelSEEDpy to reconstruct GEMs will not be an option in this microbetag isntallation, so skip installing RAST tools."

fi

# ====================================
# Step 3: Get Zenodo data
# ====================================

cd $SCRIPT_DIR

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
    wget -q --show-progress -O "$TAR_FILE" "https://zenodo.org/records/15102937/files/chem_xref.tar.gz" || {
        echo "❌ Download failed!"
        exit 1
    }
else
    echo "File already exists: $TAR_FILE"
fi


# Good bye! :)
echo "microbetag is now good to go! $TADA $ROCKET"
