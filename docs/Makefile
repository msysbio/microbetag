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


# Put it first so that "make" without argument is like "make help".
.PHONY: help clean html

help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS)

html:
	@echo "Preprocessing markdown files...\n"
	@find . -name "*.md" -exec python $(PREPROCESS_SCRIPT) {} \;
	@echo "\n\nBuild RTD"
	@$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS)

clean:
	@echo "Cleaning build directory..."
	@rm -rf "$(BUILDDIR)"
