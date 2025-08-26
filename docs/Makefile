# Makefile for Sphinx documentation and documentation testing
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = source
BUILDDIR      = build
PYTHON        = python3

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
	@echo ""
	@echo "Documentation testing targets:"
	@echo "  test-examples     Test README.md code examples"
	@echo "  coverage-report   Generate documentation coverage report"
	@echo "  spell-check       Check spelling in documentation files"
	@echo "  test-all          Run all documentation tests"
	@echo "  serve             Serve documentation locally (requires python -m http.server)"

.PHONY: help Makefile test-examples coverage-report spell-check test-all serve

# Documentation testing targets
test-examples:
	@echo "📖 Testing README examples..."
	@$(PYTHON) ../repo/test_readme_examples.py

coverage-report:
	@echo "📊 Generating documentation coverage report..."
	@$(PYTHON) ../repo/generate_doc_coverage.py

spell-check:
	@echo "📝 Checking documentation spelling..."
	@$(PYTHON) ../repo/spell_check_docs.py

test-all: test-examples coverage-report spell-check
	@echo ""
	@echo "✅ All documentation tests completed"

# Local development target
serve: html
	@echo "🌐 Serving documentation at http://localhost:8000"
	@echo "Press Ctrl+C to stop the server"
	@cd $(BUILDDIR)/html && $(PYTHON) -m http.server 8000

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
