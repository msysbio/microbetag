"""
Genome scale metabolic model reconstructions are required in the microbetag framework when
the seed complementarity feature is enabled.
The user may provide their own GEMs -- this is strongly suggested as the user's GEMs
can be curated to fix the experiment's specific conditions (e.g. medium composition)
as well as the metabolites and the reactions present in the network themselves.

In case the user does not provide their own GEMs, microbetag provides two approaches to build a GEM:
- using ModelSEEpy
- using CarveMe

Especially when using ModelSEEDpy for the reconstruction, medium can be of utmost importance,
since it's being used by the gapfilling algorithm to fill the gaps in the network.

"""

import os
import shutil
import unittest
from pathlib import Path

from microbetag.genres import GEMSReconstruction

root      = os.path.dirname(os.path.dirname(__file__))
test_data = os.path.join(root, "test_data", "test_modelseed")

input_dir  = os.path.join(test_data, "input_files")
output_dir = os.path.join(test_data, "output_files")

input_fasta, input_faa = os.path.join(input_dir, "fasta"), os.path.join(input_dir, "faa")

output_faa = os.path.join(output_dir, "faa")
os.makedirs(output_faa, exist_ok=True)
faa_genres = os.path.join(output_faa, "GENREs")
os.makedirs(faa_genres, exist_ok=True)

output_fasta = os.path.join(output_dir, "fasta")
os.makedirs(output_fasta, exist_ok=True)
fasta_genres = os.path.join(output_fasta, "GENREs")
# shutil.rmtree(fasta_genres)
os.makedirs(fasta_genres, exist_ok=True)


bin_filenames = [f.name for f in Path(input_fasta).iterdir() if f.is_file()]


class ConfigFasta:
    threads             = 2
    bin_filenames       = bin_filenames
    bins_path           = input_fasta
    reconstructions     = output_fasta     # main output directory for all GENRE-related files built ("reconstructions")
    sc_input_type       = "bins_fasta"
    genres              = os.path.join(output_fasta, "GENREs")       # output dir for GENREs (.xml files) built to be saved ("GENREs")
    gapfill_model       = True           # bool
    gapfill_media       = None           # file or noen
    # for_reconstructions =    # dir to input files to be used for GENREs

class ConfigFaa:
    # dir to input files to be used for GENREs
    for_reconstructions = output_dir
    # output dir for GENREs (.xml files) built to be saved ("GENREs")
    genres        = os.path.join(output_dir, "GENREs")
    gapfill_model = True           # bool
    gapfill_media = None           # file or noen
    threads       = 2
    sc_input_type = "proteins_faa"

class TestGEMSReconstruction(unittest.TestCase):

    def testFromFaa(self):

        # Test the GEMSReconstruction class
        builder = GEMSReconstruction(ConfigFaa())
        builder.modelseed_reconstructions()

        print("Test 1 passed")

    def testFromFasta(self):

        builder = GEMSReconstruction(ConfigFasta())
        builder.rast_annotate_genomes()
        builder.modelseed_reconstructions()

        print("Test 2 passed")


if __name__ == "__main__":

    unittest.main()
