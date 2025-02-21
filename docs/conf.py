# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'microbetag'
copyright = '2025, Lab of Microbial Systems Biology'
author = 'Lab of Microbial Systems Biology'
release = '1.0.3'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [

    # To link to pyqt5 docs
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.mathjax",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "sphinx.ext.autosummary",
    "sphinx_qt_documentation",

    "nbsphinx",
    "autoapi.extension",
    "sphinx_search.extension",

    # For using CONTRIBUTING.md.
    "myst_parser",

    # # Local packages.
    # "youtube",
    # "trello",
    # "variables",
    # "tags",
    # "links",
    # "hacks",
    # "notfound.extension",    ## not in the bac_Growt

]

autoapi_dirs = ["../microbetag"]

autoapi_ignore = [ "*PhyloMint*", "*FAPROTAX*", "*get_kegg*", "*kegg_ids_to_ncbi*"]  # "*mtg_maps_models*",

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# myst_enable_extensions = ["colon_fence"]
myst_enable_extensions = ["amsmath", "dollarmath"]  # for latex and to enable download files    "frontmatter"

# --------------
# Skip class attributes
autoapi_options = [
    "members",
    "undoc-members",
    "show-inheritance",
]

def autoapi_skip_member(app, what, name, obj, skip, options):
    # Skip all attributes globally
    if what == "attribute":
        return True
    return None

def setup(app):
    app.connect("autoapi-skip-member", autoapi_skip_member)

# ------------------

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'furo'
html_static_path = ['_static']
html_css_files = ["custom.css"]

html_theme_options = {
    "light_logo": "img/microbetag_logo.png",
    "dark_logo": "img/microbetag_logo_dark.png"
}

html_title = "annotating microbial networks"
html_short_title = "microbetag"
# html_logo = '_static/img/microbetag_logo.png'
html_favicon = '_static/img/microbetag_logo.ico'



intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "numpy": ("https://docs.scipy.org/doc/numpy/", None),
    "pandas": ("https://pandas.pydata.org/pandas-docs/stable/", None),
    'sklearn': ('http://scikit-learn.org/stable', None)
}

# No need to manually register .md, as myst_parser handles it
source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',  # This is registered automatically by myst_parser
}

