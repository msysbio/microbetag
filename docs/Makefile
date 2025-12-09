# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = .
BUILDDIR      = _build

# Python script for preprocessing MyST links
PREPROCESS_SCRIPT = replace_myst_links.py


# Where to copy the nf README
NF_README_SRC = ../nf/README.md
NF_README_DST = tutorials_local/nfREADME.md

# Base URL for converting ./ links
GITHUB_NF   = https://github.com/msysbio/microbetag/nf/

copy_nf_readme:
	@echo "Copying README: $(NF_README_SRC) → $(NF_README_DST)"
	@mkdir -p tutorials_local
	@cp $(NF_README_SRC) $(NF_README_DST)

	@echo "Rewriting relative links in nfREADME.md..."
	@sed -i 's|\.\./nf/|$(GITHUB_NF)|g' $(NF_README_DST)
	@sed -i 's|\.\./|$(GITHUB_NF)|g' $(NF_README_DST)
	@sed -i 's|\./|$(GITHUB_NF)|g' $(NF_README_DST)


# Put it first so that "make" without argument is like "make help".
.PHONY: help clean html

help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS)

html: copy_nf_readme
	@echo "Preprocessing markdown files...\n"
	@find . -name "*.md" -exec python $(PREPROCESS_SCRIPT) {} \;
	@echo "\n\nBuild RTD"
	@$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS)

clean:
	@echo "Cleaning build directory..."
	@rm -rf "$(BUILDDIR)"
