"""
Script to build GENREs using:
- ModelSEEDpy (https://modelseedpy.readthedocs.io/en/latest/, https://github.com/ModelSEED/ModelSEEDpy), and 
- DNNGIOR (https://doi.org/10.1016/j.isci.2024.111349)

ModelSEEDpy v0.4.2 comes with a hard constraint, it needs scikit-learn 0.24.2 
which is compatible only with Python < 3.10
Also, numpy needs to be 1.26.4

Thus, this script needs to be performed with Python 3.9.
"""
import os
import cobra
import argparse
from pathlib import Path


def reconstruct(faa, outdir = None):

    from modelseedpy import MSBuilder, MSGenome

    # Set modelId
    faa_path = Path(faa)
    modelId  = faa_path.stem

    # Init a MSGenome instance
    msGenome = MSGenome.from_fasta(faa, split=' ')

    # Build your GEM
    model = MSBuilder.build_metabolic_model(
        model_id                    = modelId,
        genome                      = msGenome,
        index                       = "0",
        classic_biomass             = True,
        gapfill_model               = False,
        gapfill_media               = None,
        annotate_with_rast          = True,
        allow_all_non_grp_reactions = True
    )

    # Save the GEM as a .sbml file
    modelname = ".".join([modelId, "draft.xml"])
    modelfile = os.path.join(outdir, modelname)
    cobra.io.write_sbml_model(cobra_model = model, filename = modelfile)

    return modelname


def gapfill(draft_model, outdir=None, medium = None):
    """
    draft_model: Path to draft .xml
    medium: path to tab-separated file .tsv
    """

    import dnngior

    draft_model_path = Path(draft_model)
    outdir           = Path(outdir) if outdir is not None else Path(outdir)
    model_id         = draft_model_path.stem.replace(".draft", "")

    dng_gf = dnngior.Gapfill(
        draftModel    = draft_model,
        medium        = medium,
        objectiveName = 'bio1'
    )

    print("Number of reactions added:", len(dng_gf.added_reactions))

    gapfilled_model = dng_gf.gapfilledModel.copy()
    modelfile       = str(outdir / f"{model_id}.xml")

    try:
        cobra.io.write_sbml_model(cobra_model=gapfilled_model, filename=modelfile)
        print("✅ SBML successfully written:", modelfile)
    except Exception as e:
        print("❌ Failed to write SBML:", e)

    draft_model_path.unlink()


def main():

    parser = argparse.ArgumentParser(
        description = "Reconstruct a genome-scale metabolic network with ModelSEEDpy and DNNGIOR"
    )
    parser.add_argument(
        "--reconstruct", "-r",
        action = "store_true",
        help   = "Reconstruct with ModelSEEDpy"
    )
    parser.add_argument(
        "--gapfill", "-g", action = "store_true",
        help = "Set true if you wish to gap-fill the draft reconstruction using DNNGIOR."
    )

    parser.add_argument("--faa", "-f", help="Path to the protein file to be used.")
    parser.add_argument("--draft-model", "-d", help="Path to the draft model to be gapfilled.")
    parser.add_argument("--outdir", "-o", help="Path to directory where models will be saved.")

    parser.add_argument(
        "--medium", "-m",
        help = "Path to 3-column tab separated file describing medium to be used for the gap-filling step."
    )
    args = parser.parse_args()

    if args.reconstruct:
        _ = reconstruct(args.faa, args.outdir)

    if args.gapfill:
        gapfill(args.draft_model, args.outdir, args.medium)


if __name__ == "__main__":

    main()
