# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import os
import re
project = "microbetag"
copyright = "2025, Lab of Microbial Systems Biology"
author = "Lab of Microbial Systems Biology"
release = "1.0.3"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

# --------------


extensions = [
    "sphinx_design",
    "sphinxcontrib.lightbox2",
    "sphinxcontrib.plantuml",
    "sphinxcontrib.mermaid",
    # # To link to pyqt5 docs
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",  # i had it muted; this is related to the .inv files (intersphinx_mapping) to have the links to types
                               # when i enable it though, it breaks the lightbox popup
    "sphinx.ext.mathjax",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",  # NOTE (Haris Zafeiropoulos, 2025-05-13): Napoleon supports Google-style and NumPy-style docstrings out of the box.
    "sphinx.ext.autosummary",
    # "sphinx_qt_documentation",         # i had it muted
    # "nbsphinx",                        # i had it muted;  when i enable this lighbox fails and no latex good
    # "sphinx_autoapi.extension",        # i had it muted
    "autoapi.extension",
    # "sphinx_search.extension",         # i had it muted
    # For using CONTRIBUTING.md.
    "myst_parser",

    "sphinxcontrib.bibtex"
]


# Skip class attributes
autoapi_options = [
    "members",
    "undoc-members",
    "show-inheritance",
    "show-module-summary",      # NOTE (Haris Zafeiropoulos, 2025-05-13): This is essential to have the table on top!!
    "special-members"
]

# Refs
bibtex_bibfiles = ["references.bib"]

def autoapi_skip_member(app, what, name, obj, skip, options):
    # Skip all attributes globally
    if what == "attribute":
        return True
    return None


def setup(app):
    app.connect("autoapi-skip-member", autoapi_skip_member)


autoapi_dirs   = ["../microbetag"]
autoapi_ignore = [
    "*PhyloMint*",
    "*FAPROTAX*",
    "*get_kegg*",
    "*kegg_ids_to_ncbi*",
]  # "*mtg_maps_models*",

templates_path   = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# ------------------

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme       = "furo"
html_static_path = ["_static"]
html_css_files   = ["custom.css"]

html_theme_options = {
    "light_logo": "img/microbetag_logo.png",
    "dark_logo" : "img/microbetag_logo_dark.png",
}

html_title       = "annotating microbial networks"
html_short_title = "microbetag"
html_favicon     = "_static/img/microbetag_logo.ico"

# No need to manually register .md, as myst_parser handles it
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",  # This is registered automatically by myst_parser
}

# -- Options for myst-parser -------------------------------------------------
# https://myst-parser.readthedocs.io/en/latest/configuration.html


# myst_enable_extensions = ["colon_fence"]
myst_enable_extensions = [
    "amsmath",
    "dollarmath",
    "colon_fence",
]  # for latex and to enable download files    "frontmatter"


# -- Options for sphinxcontrib.lightbox2 -------------------------------------

# The time it takes for the Lightbox container and overlay to fade in and out, in milliseconds
lightbox2_fade_duration = 100
lightbox2_image_fade_duration = 100

# -- Options for sphinxcontrib-mermaid ---------------------------------------
mermaid_output_format = "png"

mermaid_params = []

if "READTHEDOCS" in os.environ:
    # Required to build with sphinxcontrib-mermaid on readthedocs
    mermaid_params.extend(["-p" "puppeteer-config.json"])

# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {
    'pandas': ('https://pandas.pydata.org/pandas-docs/stable/', None),
    # 'python': ('http://docs.python.org/', None),
    'python': ('https://docs.python.org/3', 'https://docs.python.org/3/objects.inv'),
    'numpy': ("http://docs.scipy.org/doc/numpy/", None),
    'scipy': ("http://docs.scipy.org/doc/scipy/reference", None),
    'networkx': ("https://networkx.org/documentation/stable/", None),
    # 'mysql': ('https://dev.mysql.com/doc/', None),  # NOTE (Haris Zafeiropoulos, 2025-05-13): does not work
    'dash_cytoscape': ("https://dash.plotly.com/cytoscape/reference", None)
}

intersphinx_cache_limit = 10  # days to keep the cached inventories
