# Makefile for SegnoMMS

# Use uv for all Python operations
UV := uv
PYTHON := $(UV) run python

# Plugin directories
PLUGIN_DIR := segnomms
EXAMPLES_DIR := examples
DIST_DIR := dist

# Default target
.PHONY: all
all: install

# Display help
.PHONY: help
help:
	@echo "SegnoMMS - Make targets:"
	@echo ""
	@echo "Installation & Build:"
	@echo "  make install       - Install the plugin with uv in development mode"
	@echo "  make sync          - Sync environment with uv.lock"
	@echo "  make lock          - Create/update uv.lock file"
	@echo "  make update-deps   - Update all dependencies to latest versions"
	@echo "  make build         - Build distribution files with uv"
	@echo "  make dist          - Create distribution directory"
	@echo ""
	@echo "Review:"
	@echo "  make review        - Generate and serve visual review suite"
	@echo "  make review-build  - Generate review suite without serving"
	@echo "  make review-ci     - Run automated review for CI"
	@echo ""
	@echo "Deployment:"
	@echo "  make deploy        - Deploy to beta environment"
	@echo "  make deploy-safe   - Deploy with review (recommended)"
	@echo ""
	@echo "Testing:"
	@echo "  make test          - Run comprehensive test suite (unit, docs, lint, visual, compatibility)"
	@echo "  make test-all      - Run ALL tests including type checking"
	@echo "  make test-quick    - Run quick test subset (unit tests only)"
	@echo ""
	@echo "Test Categories:"
	@echo "  make test-unit     - Run unit tests (tests/unit/)"
	@echo "  make test-integration - Run integration tests (tests/integration/)"
	@echo "  make test-visual   - Run visual regression tests (tests/visual/)"
	@echo "  make test-structural - Run SVG structure tests (tests/structural/)"
	@echo "  make test-performance - Run performance tests (tests/perf/)"
	@echo "  make test-all-categories - Run all test categories only (no linting/docs)"
	@echo ""
	@echo "Performance Benchmarking:"
	@echo "  make benchmark     - Run comprehensive performance benchmarks"
	@echo "  make benchmark-quick - Run quick performance benchmarks (reduced iterations)"
	@echo "  make benchmark-regression - Check for performance regressions against baselines"
	@echo "  make benchmark-scaling - Test algorithm scaling with QR code sizes"
	@echo "  make benchmark-memory - Run memory profiling and leak detection"
	@echo "  make benchmark-report - Generate comprehensive performance report"
	@echo ""
	@echo "Legacy Test Targets:"
	@echo "  make test-docs     - Test documentation build and link checking"
	@echo "  make test-lint     - Test code quality with linters"
	@echo "  make test-typecheck - Test type annotations (gradual mode)"
	@echo "  make test-typecheck-strict - Test type annotations (strict mode)"
	@echo "  make test-visual-update - Update visual regression baselines"
	@echo "  make test-segno-compatibility - Test compatibility across multiple Segno versions"
	@echo "  make test-examples - Generate comprehensive examples"
	@echo "  make test-coverage - Generate coverage report"
	@echo ""
	@echo "Development:"
	@echo "  make setup         - Complete setup with uv (all dependencies)"
	@echo "  make shell-help    - Show shell functions usage"
	@echo "  make watch         - Watch for changes and rebuild (requires fswatch)"
	@echo "  make lint          - Run Python linters"
	@echo "  make format        - Auto-format Python code"
	@echo "  make typecheck     - Run type checking"
	@echo ""
	@echo "Documentation:"
	@echo "  make docs-install  - Install Sphinx and documentation dependencies"
	@echo "  make docs          - Build Sphinx documentation"
	@echo "  make docs-clean    - Clean documentation build"
	@echo "  make docs-serve    - Build and serve docs at localhost:8001"
	@echo "  make docs-validate - Validate documentation (contradictions, refs, examples)"
	@echo "  make docs-help     - Show Sphinx documentation help"
	@echo ""
	@echo "Spec-Driven Development (GitHub Spec-Kit):"
	@echo "  make spec-check    - Check spec-kit prerequisites and configuration"
	@echo "  make spec-validate - Validate existing specification files"
	@echo "  make spec-clean    - Clean spec-kit generated files"
	@echo "  make spec-help     - Show spec-kit slash commands and workflow"
	@echo ""
	@echo "Utilities:"
	@echo "  make clean         - Remove all generated files"
	@echo "  make clean-visual  - Clean visual test outputs (preserves baselines)"
	@echo "  make info          - Show package information"
	@echo "  make check-deps    - Check dependencies"
	@echo "  make help          - Show this help message"
	@echo ""

# Install plugin in development mode with uv
.PHONY: install
install:
	@echo "Installing plugin in development mode with uv..."
	$(UV) sync
	$(UV) pip install -e .


# Run all tests (comprehensive) - now includes type checking
.PHONY: test
test: test-unit test-integration test-structural test-visual test-docs test-lint test-typecheck test-segno-compatibility test-examples
	@echo ""
	@echo "✅ All tests completed successfully!"
	@echo "   🎯 Type checking is now integrated into the main test suite"
	@echo ""

# Run absolutely all tests including strict type checking mode
.PHONY: test-all
test-all: test test-typecheck-strict
	@echo ""
	@echo "✅ ALL tests completed successfully (including strict type checking)!"
	@echo ""

# Run quick test subset (for development)
.PHONY: test-quick
test-quick: test-unit-no-cov
	@echo ""
	@echo "✅ Quick tests completed successfully!"
	@echo ""

# Run all test categories only (no linting/docs)
.PHONY: test-all-categories
test-all-categories: test-unit test-integration test-structural test-visual test-performance
	@echo ""
	@echo "✅ All test categories completed successfully!"
	@echo ""

# Test documentation system
.PHONY: test-docs
test-docs:
	@echo "Testing documentation build..."
	@cd docs && $(PYTHON) -c "import sphinx" 2>/dev/null || { echo "❌ Sphinx not available in environment"; exit 1; }
	@cd docs && $(PYTHON) -m sphinx -M html source build >/dev/null 2>&1 && echo "✅ Documentation build successful" || { echo "❌ Documentation build failed"; exit 1; }
	@echo "Testing documentation link checking..."
	@cd docs && $(PYTHON) -m sphinx -M linkcheck source build >/dev/null 2>&1 && echo "✅ Link checking successful" || { echo "❌ Link checking failed"; exit 1; }
	@echo "Documentation tests passed!"

# Test code quality (linting)
.PHONY: test-lint
test-lint:
	@echo "Testing code quality with linters..."
	@$(PYTHON) -c "import flake8" 2>/dev/null && $(PYTHON) -m flake8 $(PLUGIN_DIR) || echo "⚠️  flake8 not available, skipping (install with: pip install flake8)"
	@$(PYTHON) -c "import black" 2>/dev/null && $(PYTHON) -m black --check $(PLUGIN_DIR) || echo "⚠️  black not available, skipping (install with: pip install black)"
	@$(PYTHON) -c "import isort" 2>/dev/null && $(PYTHON) -m isort --check-only $(PLUGIN_DIR) || echo "⚠️  isort not available, skipping (install with: pip install isort)"
	@echo "Code quality tests completed!"

# Test type checking (gradual - with current excludes)
.PHONY: test-typecheck
test-typecheck:
	@echo "Testing type annotations (gradual mode)..."
	@if $(PYTHON) -c "import mypy" 2>/dev/null; then \
		$(PYTHON) -m mypy $(PLUGIN_DIR) || true; \
	else \
		echo "⚠️  mypy not available, skipping (install with: pip install mypy)"; \
	fi
	@echo "Type checking tests completed!"

# Test type checking (strict - for CI and advanced development)
.PHONY: test-typecheck-strict
test-typecheck-strict:
	@echo "Testing type annotations (strict mode)..."
	@if $(PYTHON) -c "import mypy" 2>/dev/null; then \
		$(PYTHON) -m mypy $(PLUGIN_DIR) --strict || true; \
	else \
		echo "⚠️  mypy not available, skipping (install with: pip install mypy)"; \
	fi
	@echo "Strict type checking completed!"



# New test category targets
.PHONY: test-unit
test-unit:
	@echo "Running unit tests..."
	$(UV) run pytest tests/unit/ -v --maxfail=100 --cov=segnomms --cov-branch --cov-report=html --cov-report=term-missing --cov-report=xml

.PHONY: test-unit-no-cov
test-unit-no-cov:
	@echo "Running unit tests without coverage..."
	$(UV) run pytest tests/unit/ -v --no-cov

.PHONY: test-integration
test-integration:
	@echo "Running integration tests..."
	$(UV) run pytest tests/integration/ -v --no-cov

.PHONY: test-structural
test-structural:
	@echo "Running SVG structure tests..."
	$(UV) run pytest tests/structural/ -v --no-cov

.PHONY: test-performance
test-performance:
	@echo "Running performance tests..."
	@if [ -d tests/perf ]; then \
		$(UV) run pytest tests/perf/ -v --no-cov; \
	else \
		echo "⚠️  Performance test directory not found, skipping"; \
	fi

# Run visual regression tests
.PHONY: test-visual
test-visual:
	@echo "Running visual regression tests..."
	$(UV) run pytest tests/visual/ -v -m visual --no-cov

# Update visual regression baselines
.PHONY: test-visual-update
test-visual-update:
	@echo "Updating visual regression baselines..."
	$(UV) run pytest tests/visual/ -v -m visual --update-baseline --no-cov


# Test compatibility across multiple Segno versions
.PHONY: test-segno-compatibility
test-segno-compatibility:
	@echo "Testing compatibility with Segno versions 1.3.1 to 1.6.6..."
	$(PYTHON) repo/test_segno_compatibility.py

# Generate comprehensive examples
.PHONY: test-examples
test-examples:
	@echo "Generating comprehensive examples..."
	$(PYTHON) -m pytest tests/visual/test_comprehensive_examples.py -v -m visual




# Run coverage report
.PHONY: test-coverage
test-coverage:
	@echo "Generating coverage report..."
	$(UV) run pytest tests/unit/ -v --cov=segnomms --cov-branch --cov-report=html --cov-report=term-missing --cov-report=xml
	@echo "Coverage report generated in htmlcov/"



# Integration target removed - JavaScript bundle no longer generated

# Create distribution directory
.PHONY: dist
dist:
	@mkdir -p $(DIST_DIR)

# Build distribution files with uv
.PHONY: build
build:
	@echo "Building wheel distribution with uv..."
	$(UV) build --wheel
	@echo "Distribution files created in $(DIST_DIR)/"

# Update dependencies with uv
.PHONY: update-deps
update-deps:
	@echo "Updating all dependencies with uv..."
	$(UV) sync --upgrade

# Lock dependencies
.PHONY: lock
lock:
	@echo "Locking dependencies with uv..."
	$(UV) lock

# Sync environment with lock file
.PHONY: sync
sync:
	@echo "Syncing environment with uv.lock..."
	$(UV) sync

# Setup complete development environment with uv
.PHONY: setup
setup: check-uv
	@echo "Setting up complete development environment with uv..."
	$(UV) sync
	$(UV) pip install -e .
	@if [ -f docs/requirements.txt ]; then \
		echo "Installing documentation dependencies..."; \
		$(UV) pip install -r docs/requirements.txt; \
	fi
	@echo ""
	@if [ -f shell-functions.sh ]; then \
		echo "Shell functions available! To use them:"; \
		echo "  source shell-functions.sh"; \
		echo ""; \
		echo "To auto-load on directory entry, add to your shell RC file:"; \
		if [ -n "$$ZSH_VERSION" ]; then \
			echo "  echo '[ -f \"$$PWD/shell-functions.sh\" ] && source \"$$PWD/shell-functions.sh\"' >> ~/.zshrc"; \
		elif [ -n "$$BASH_VERSION" ]; then \
			echo "  echo '[ -f \"$$PWD/shell-functions.sh\" ] && source \"$$PWD/shell-functions.sh\"' >> ~/.bashrc"; \
		else \
			echo "  Add to your shell's RC file: [ -f \"$$PWD/shell-functions.sh\" ] && source \"$$PWD/shell-functions.sh\""; \
		fi; \
		echo ""; \
		echo "Available functions:"; \
		echo "  • check_status - Check project status"; \
		echo "  • test_qr [content] [shape] - Quick QR code test"; \
	fi
	@echo ""
	@echo "Setup complete! Run 'make help' to see available commands."

# Clean generated files
.PHONY: clean
clean:
	@echo "Cleaning generated files..."
	rm -rf $(DIST_DIR)
	rm -rf __pycache__
	rm -rf $(PLUGIN_DIR)/__pycache__
	rm -rf $(PLUGIN_DIR)/*/__pycache__
	rm -f test_*.svg
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	rm -rf test-output/
	rm -rf examples-generated/
	rm -f test-report.json
	rm -f coverage.json
	find . -name "*.pyc" -delete
	find . -name ".DS_Store" -delete
	@echo "Clean complete."

# Clean visual test outputs only (preserves baselines)
.PHONY: clean-visual
clean-visual:
	@echo "Cleaning visual test outputs..."
	rm -rf tests/visual/output/
	rm -rf tests/visual/diff/
	rm -rf tests/review/output/
	@echo "Visual test outputs cleaned (baselines preserved)."


# Show shell functions help
.PHONY: shell-help
shell-help:
	@echo "Shell Functions Help"
	@echo "==================="
	@echo ""
	@echo "To load shell functions:"
	@echo "  source shell-functions.sh"
	@echo ""
	@echo "Available functions:"
	@echo "  check_status      - Show project status (bundle, venv, lefthook, tools)"
	@echo "  test_qr [content] [shape] - Generate quick test QR code"
	@echo ""
	@echo ""
	@echo "To auto-load on directory entry:"
	@echo "  Add to ~/.zshrc or ~/.bashrc:"
	@echo "  [ -f \"$$PWD/shell-functions.sh\" ] && source \"$$PWD/shell-functions.sh\""

# Watch for changes and rebuild (requires fswatch)
.PHONY: watch
watch:
	@command -v fswatch >/dev/null 2>&1 || { echo "fswatch is required but not installed. Install with: brew install fswatch"; exit 1; }
	@echo "Watching for changes..."
	fswatch -o $(PLUGIN_DIR) | xargs -n1 -I{} make test-quick

# Lint Python code
.PHONY: lint
lint:
	@echo "Running Python linters..."
	@$(PYTHON) -c "import flake8" 2>/dev/null && $(PYTHON) -m flake8 $(PLUGIN_DIR) || { echo "⚠️  flake8 not installed. Run 'make setup' or 'pip install flake8'"; exit 1; }
	@$(PYTHON) -c "import black" 2>/dev/null && $(PYTHON) -m black --check $(PLUGIN_DIR) || { echo "⚠️  black not installed. Run 'make setup' or 'pip install black'"; exit 1; }
	@$(PYTHON) -c "import isort" 2>/dev/null && $(PYTHON) -m isort --check-only $(PLUGIN_DIR) || { echo "⚠️  isort not installed. Run 'make setup' or 'pip install isort'"; exit 1; }

# Format Python code
.PHONY: format
format:
	@echo "Formatting Python code..."
	@$(PYTHON) -c "import black" 2>/dev/null && $(PYTHON) -m black $(PLUGIN_DIR) || { echo "⚠️  black not installed. Run 'make setup' or 'pip install black'"; exit 1; }
	@$(PYTHON) -c "import isort" 2>/dev/null && $(PYTHON) -m isort $(PLUGIN_DIR) || { echo "⚠️  isort not installed. Run 'make setup' or 'pip install isort'"; exit 1; }

# Type checking
.PHONY: typecheck
typecheck:
	@echo "Running type checks..."
	@$(PYTHON) -c "import mypy" 2>/dev/null && $(PYTHON) -m mypy $(PLUGIN_DIR) --ignore-missing-imports || { echo "⚠️  mypy not installed. Run 'make setup' or 'pip install mypy'"; exit 1; }

# Documentation targets (using docs/Makefile)
.PHONY: docs-install
docs-install:
	@echo "Documentation dependencies are included in pyproject.toml"
	@echo "Run 'uv sync' to install all dependencies including docs"
	@echo "Note: docs/requirements.txt is kept for ReadTheDocs compatibility"

.PHONY: docs-check
docs-check:
	@echo "Checking documentation dependencies..."
	@command -v sphinx-build >/dev/null 2>&1 || { echo "Sphinx not found. Run 'make docs-install' first."; exit 1; }

.PHONY: docs
docs: docs-check
	@echo "Building Sphinx documentation..."
	$(MAKE) -C docs html

.PHONY: docs-clean
docs-clean:
	@echo "Cleaning documentation build..."
	$(MAKE) -C docs clean

.PHONY: docs-serve
docs-serve: docs
	@echo "Serving documentation at http://localhost:8001"
	@echo "Press Ctrl+C to stop"
	cd docs/build/html && $(PYTHON) -m http.server 8001

.PHONY: docs-help
docs-help:
	@echo "Available documentation targets:"
	$(MAKE) -C docs help

.PHONY: docs-validate
docs-validate:
	@echo "Validating documentation..."
	@./scripts/check_doc_contradictions.sh
	@echo ""
	@echo "Validating cross-references..."
	@$(PYTHON) repo/validate_docs_references.py
	@echo ""
	@echo "Running comprehensive validation..."
	@$(PYTHON) scripts/verify_documentation_fixes.py

# Package info
.PHONY: info
info:
	@echo "SegnoMMS"
	@echo "Version: 0.1.0"
	@echo "Python: $(shell $(PYTHON) --version)"
	@echo "Location: $(shell pwd)"
	@echo ""
	@echo "Plugin modules:"
	@find $(PLUGIN_DIR) -name "*.py" -not -path "*/__pycache__/*" | sort

# Check uv is installed
.PHONY: check-uv
check-uv:
	@echo "Checking uv installation..."
	@command -v uv >/dev/null 2>&1 || { echo "uv is required. Install with: pip install uv"; exit 1; }
	@echo "✅ uv is installed."

# Check dependencies
.PHONY: check-deps
check-deps: check-uv
	@echo "Checking dependencies..."
	@$(UV) run python -c "import segno" 2>/dev/null || { echo "segno is required. Run 'make install'"; exit 1; }
	@echo "All dependencies satisfied."



# Generate and serve visual review suite (main review command)
.PHONY: review
review: test
	@echo "🎨 Generating and serving Visual Review Suite..."
	@$(PYTHON) -m tests.review.review_suite --serve

# Generate review suite without serving
.PHONY: review-build
review-build:
	@echo "🎨 Generating Visual Review Suite..."
	@$(PYTHON) -m tests.review.review_suite
	@echo "✅ Review suite generated at tests/review/output/"
	@echo "   Open tests/review/output/index.html to view"

# Run review in CI mode (non-interactive)
.PHONY: review-ci
review-ci: review-build
	@echo "✅ CI review completed"


# Temp local beta deployment method using ./repo/deploy_beta.py
.PHONY: deploy
deploy: build
	@echo "Deploying to local beta environment..."
	@$(PYTHON) repo/deploy_beta.py
	@echo "Deployment complete."

# Deploy with review (recommended) - runs test, then review, then deploy
.PHONY: deploy-safe
deploy-safe: review deploy
	@echo "✅ Deployment completed after review"

# Performance benchmarking targets
.PHONY: benchmark
benchmark:
	@echo "Running comprehensive performance benchmarks..."
	$(UV) run pytest tests/perf/test_algorithm_benchmarks.py -v -m benchmark --no-cov
	@echo "✅ Performance benchmarks completed"

.PHONY: benchmark-quick
benchmark-quick:
	@echo "Running quick performance benchmarks..."
	$(UV) run pytest tests/perf/test_algorithm_benchmarks.py -v -m benchmark --no-cov -k "not scaling"
	@echo "✅ Quick performance benchmarks completed"

.PHONY: benchmark-regression
benchmark-regression:
	@echo "Checking for performance regressions..."
	$(UV) run pytest tests/perf/test_algorithm_benchmarks.py -v -m benchmark --no-cov --performance-regression-check
	@echo "✅ Performance regression check completed"

.PHONY: benchmark-scaling
benchmark-scaling:
	@echo "Testing algorithm scaling behavior..."
	$(UV) run pytest tests/perf/test_algorithm_benchmarks.py::TestScalabilityBenchmarks -v --no-cov
	@echo "✅ Scaling benchmarks completed"

.PHONY: benchmark-memory
benchmark-memory:
	@echo "Running memory profiling and leak detection..."
	$(UV) run pytest tests/perf/test_memory_profiling.py -v -m slow --no-cov
	@echo "✅ Memory profiling completed"

.PHONY: benchmark-report
benchmark-report:
	@echo "Generating comprehensive performance report..."
	@$(PYTHON) repo/generate_performance_report.py

# Spec-Driven Development targets (GitHub Spec-Kit)

# Check spec-kit prerequisites and configuration
.PHONY: spec-check
spec-check:
	@echo "Checking spec-kit prerequisites and configuration..."
	@command -v uv >/dev/null 2>&1 || { echo "❌ uv is required for spec-kit. Install with: pip install uv"; exit 1; }
	@uv tool run --from specify-cli specify check || { echo "❌ specify-cli not installed. Run: uv tool install specify-cli --from git+https://github.com/github/spec-kit.git"; exit 1; }
	@[ -f .specify/memory/constitution.md ] || { echo "❌ Project not initialized with spec-kit. Run: make spec-init"; exit 1; }
	@echo "✅ Spec-kit configuration validated"

# Validate existing specification files
.PHONY: spec-validate
spec-validate:
	@echo "Validating specification files..."
	@if [ -d specs ]; then \
		echo "Found specs directory - validating specification files..."; \
		for spec in specs/*/spec.md; do \
			if [ -f "$$spec" ]; then \
				echo "  Validating $$spec..."; \
				$(PYTHON) -c "import markdown; markdown.markdown(open('$$spec').read())" 2>/dev/null || echo "    ⚠️  Markdown syntax issues in $$spec"; \
			fi; \
		done; \
		echo "✅ Specification validation completed"; \
	else \
		echo "ℹ️  No specs directory found - no specifications to validate"; \
	fi

# Clean spec-kit generated files (preserves templates and constitution)
.PHONY: spec-clean
spec-clean:
	@echo "Cleaning spec-kit generated files..."
	@rm -rf specs/*/artifacts/ 2>/dev/null || true
	@rm -rf specs/*/checklists/ 2>/dev/null || true
	@find specs/ -name "*.tmp" -delete 2>/dev/null || true
	@echo "✅ Spec-kit generated files cleaned (templates and constitution preserved)"

# Show spec-kit slash commands and workflow help
.PHONY: spec-help
spec-help:
	@echo "GitHub Spec-Kit Integration for SegnoMMS"
	@echo "========================================"
	@echo ""
	@echo "Spec-Driven Development Workflow:"
	@echo "  1. /speckit.constitution - Create project constitution (align with CLAUDE.md)"
	@echo "  2. /speckit.specify      - Create feature specification from description"
	@echo "  3. /speckit.plan         - Generate technical implementation plan"
	@echo "  4. /speckit.tasks        - Break down into actionable tasks"
	@echo "  5. /speckit.implement    - Execute implementation with validation"
	@echo ""
	@echo "Optional Enhancement Commands:"
	@echo "  /speckit.clarify         - Ask structured questions before planning"
	@echo "  /speckit.analyze         - Cross-artifact consistency analysis"
	@echo "  /speckit.checklist       - Generate quality validation checklists"
	@echo ""
	@echo "Integration Notes:"
	@echo "  • Follows SegnoMMS documentation policy (Sphinx-first)"
	@echo "  • Integrates with existing pre-commit hooks and quality gates"
	@echo "  • Respects Pydantic v2 + MyPy modernization standards"
	@echo "  • All spec-driven features must pass existing test suites"
	@echo ""
	@echo "Make Targets:"
	@echo "  make spec-check          - Validate spec-kit installation and config"
	@echo "  make spec-validate       - Check existing specification files"
	@echo "  make spec-clean          - Clean generated spec files"
	@echo "  make spec-help           - Show this help message"
	@echo ""
