import os

from .config import Config

from .helpers import (
    MappingPaths,
    PathwayComplementarity,
    Faprotax,
    NetworkHandler,
    AbdTableHandler,
    SeedComplementarityHandler,
    BinsHandler,
    manta_input_net,
    otf_seqid_ncbi_gtdb_map
)

from .utils import (
    mtg_logger,
    ko_list_parser,
    merge_ko,
    extend_complements,
    load_phenotypic_traits,
    extend_faprotax,
)

from .pathway_complementarity import (
    export_pathway_complementarities,
    all_complements,
    all_alternatives,
    build_kegg_url,
)

from .seed_complementarity import (
    ExportSeedComplementarities,
    load_seed_complement_files,
    build_url_with_seed_complements,
    kegg_module_related_intersect,
)

try:
    from .db import (
        GetPhenotrexTraits,
        get_genomes_for_ncbi_tax_id,
        get_ncbi_tax_id_for_genome,
        patric_from_gc_list,
        get_path_compls_for_ncbi_ids
    )
except Exception:
    print(
        "mysql-connector-python is not installed in the running environment."
        "Dependency and microbetag features required only for on-the-fly version."
    )
    pass


from .genres import (
    GEMSReconstruction
)

from .networks import (
    get_edgelist,
    build_base_graph,
    read_cyjson
)

from .tools import (
    run_faprotax,
    run_flashweave,
    run_manta,
    phenotrex_predict,
    phenotrex_genotype,
    kegg_annotation,
    run_prodigal,
    hmmsearch,
    run_seed_complementarity,
)

from .build_mtg_cx2 import mtg_annotate_network

from .microbetag import (
    run_microbetag
)


_KEGG_MAPPINGS         = os.path.join(os.path.dirname(__file__), "mtg_maps_models", "kegg_mappings")
_KEGG_TERMS_PER_MODULE = os.path.join(_KEGG_MAPPINGS, "kegg_terms_per_module.tsv")
_MODULE_DEFINITION_MAP = os.path.join(_KEGG_MAPPINGS, "module_definition_map.json")
_KEGG_MODULES_TO_MAPS  = os.path.join(_KEGG_MAPPINGS, "module_map_pairs.tsv")

_MTG_PHEN_ENV      = "mtg-phenotrex"
_MTG_MODELSEED_ENV = "mtg-modelseed"

__version__ = "1.0.4"
__license__ = "GNU GPL3"
__authors__ = ["Haris Zafeiropoulos <haris.zafeiropoulos@kuleuven.be>"]
__cite__    = (
    "Zafeiropoulos H, Michail Delopoulos EI, Erega A, Schneider A, Geirnaert A, Morris J, Faust K."
    "microbetag: simplifying microbial network interpretation through annotation, enrichment tests and metabolic complementarity analysis."
    "bioRxiv. 2024:2024-10."
)
