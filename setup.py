# microbetag : a python library for metabolic networks sampling and analysis
# microbetag is developed and maintained by the Lab of microbial systems biology

# Copyright (c) 2024 Haris Zafeiropoulos

# Licensed under GNU LGPL.3, see LICENCE file

# This is the setup Python script for building the microbetag library

"""
Script to install the microbetag library locally.

To do so, you may run:

python setup.py sdist bdist_wheel
pip install .

    In case you get the strip_trailing_zero error
pip install --upgrade setuptools packaging

Attention!
For the seed complementarity module to work fine, you need to make sure
you have downloaded the MetaNetX reference file for chemical compounds chem_xref.tar.gz
and place it in `microbetag/mtg_maps_models/MetaNetX`

This should be already done when running `setup_environment.sh`.
"""
import os
import re
import sys
import ast
import subprocess

from setuptools import setup, find_packages
from setuptools.command.install import install

# Read the requirements.txt file
with open("requirements/requirements.txt") as f:
    requirements = f.read().splitlines()


def get_records():
    init_path = os.path.join("microbetag", "__init__.py")
    with open(init_path) as f:
        content = f.read()

    version_match = re.search(r'__version__\s*=\s*"([^"]+)"', content)
    version = version_match.group(1) if version_match else None

    authors_match = re.search(r'__authors__\s*=\s*(\[.*?\])', content, re.DOTALL)
    authors = ast.literal_eval(authors_match.group(1)) if authors_match else []

    license_match = re.search(r'__license__\s*=\s*"([^"]+)"', content)
    license = license_match.group(1) if license_match else None

    cite_match = re.search(r'__cite__\s*=\s*"([^"]+)"', content)
    cite = cite_match.group(1) if cite_match else None

    return {
        "version": version,
        "authors": authors,
        "license": license,
        "cite": cite
    }


records = get_records()


class CustomInstallCommand(install):
    def run(self):

        install.run(self)

        # NOTE (Haris Zafeiropoulos, 2025-05-22):
        # The package pyshorteners==1.0.1 does not support modern PEP 517/518 builds and
        # tries to use a deprecated setup.py egg_info process,
        # which fails in current Python environments
        # (especially in isolated or conda environments with modern setuptools and pip).
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyshorteners==1.0.1"])


setup(
    name                 = "microbetag",
    description          = "A library for microbial co-occurrencce network annotation.",
    documentation        = "https://microbetag.readthedocs.io/",
    version              = records["version"],
    authors              = records["authors"],
    license              = records["license"],
    cite                 = records["cite"],
    packages             = find_packages(include=["microbetag", "microbetag.*"]),
    include_package_data = True,
    entry_points         = {
        "console_scripts": [
            "microbetag = microbetag.microbetag:main",
        ],
    },
    package_data = {
        "microbetag": ["mtg_maps_models/*", "PhyloMint/*", "PhyloMint/lib/*"]
    },
    install_requires = requirements,
    dependency_links = [
        "git+https://github.com/hariszaf/manta.git@scipy-version#egg=manta"
    ],
    cmdclass={
        'install': CustomInstallCommand,
    },
)


# NOTE (Haris Zafeiropoulos, 2025-06-01):
# Python 3.9.19 does support dict[str, str] and other generic built-ins, yet it does not support the | (union) operator for types — that was only introduced in Python 3.10.
# phenotrex runs in Python 3.8
# Consider Python 3.8 as basis
