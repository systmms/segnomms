# Quickstart: Documentation Audit Fixes

**Feature**: 002-initial-documentation-audit
**Type**: Documentation-only maintenance
**Complexity**: LOW

## Overview

This feature fixes 27 documentation issues identified in comprehensive audit across 4 priority levels. All changes are direct file edits with no code modifications.

## Workflow Organization

### Priority 1: Critical Fixes (Must Fix First)
Issues that block installation or cause immediate user confusion.

**Files**:
- `docs/source/index.rst` - Package name consistency
- `docs/source/contributing.rst` - Repository URL
- `segnomms/__init__.py` - Author attribution
- `docs/source/installation.rst`, `README.md`, `docs/source/conf.py` - Segno version alignment

**Validation**:
```bash
# Check package name consistency
grep -r "Segno Interactive SVG Plugin" docs/source/ README.md

# Check repository URL
grep "your-org" docs/source/contributing.rst

# Check author consistency
python -c "import segnomms; print(segnomms.__author__)"
grep "author" pyproject.toml

# Check Segno version consistency
grep -r "Segno.*1.5" docs/source/ README.md segnomms/__init__.py
```

### Priority 2: High Priority Fixes
Issues affecting development setup and API usage.

**Files**:
- `pyproject.toml` - Python 3.14 classifier
- `README.md` - Python 3.14 support, dev dependencies, Makefile commands
- `docs/source/installation.rst` - uv prerequisites
- `docs/source/quickstart.rst`, `README.md` - Import path standardization
- `docs/source/contributing.rst` - Lefthook documentation
- `docs/source/api/constants.rst` - NEW: Constants module API docs

**Validation**:
```bash
# Check Python version classifiers
grep "Programming Language :: Python :: 3.14" pyproject.toml

# Test import paths work
python -c "from segnomms.config import RenderingConfig"
python -c "from segnomms.a11y.accessibility import AccessibilityConfig"

# Check constants module docs exist
ls docs/source/api/constants.rst

# Build Sphinx docs
make docs
```

### Priority 3: Medium Priority Enhancements
Completeness and navigation improvements.

**Files**:
- `docs/source/contributing.rst` - Spec-kit workflow, test script policy
- `docs/source/shapes.rst` - Safe mode scope, cross-references
- `docs/source/decoder_compatibility.rst` - ECC level table
- `docs/source/examples.rst` - Complete FastAPI example, decoder test script
- `README.md` - Beta status notice, development commands section

**Validation**:
```bash
# Extract and test code examples
python docs/extract_examples.py  # (create if needed)

# Check cross-references resolve
python repo/validate_docs_references.py

# Verify Sphinx build has no warnings
make docs 2>&1 | grep -i warning
```

### Priority 4: Low Priority Polish
Formatting consistency and minor improvements.

**Files**:
- All `.rst` files - Code block language tags
- All `.rst` files - Sphinx cross-references (`:doc:`, `:ref:`)
- `docs/source/contributing.rst` - Test script policy

**Validation**:
```bash
# Check code block language tags
grep -n ".. code-block::" docs/source/*.rst | grep -v "python\|bash\|css\|json"

# Build final docs and check
make docs
```

## Validation Strategy

### 1. Contradiction Check
```bash
# Run comprehensive grep for contradictions
scripts/check_doc_contradictions.sh  # Create script with searches for:
# - Package names
# - Repository URLs
# - Author names
# - Version requirements
# - Import paths
```

### 2. Code Example Testing
```bash
# Extract all code examples
python scripts/extract_code_examples.py docs/source/ > test_examples.py

# Run extracted examples
python test_examples.py

# Verify all imports work
python -c "$(grep 'from segnomms' docs/source/*.rst | cut -d: -f2 | sort -u)"
```

### 3. Sphinx Build Validation
```bash
# Clean build
rm -rf docs/build/
make docs

# Check for warnings or errors
make docs 2>&1 | tee build.log
grep -i "warning\|error" build.log
```

### 4. Cross-Reference Validation
```bash
# Existing validation script
python repo/validate_docs_references.py
```

## Testing Checklist

Before marking feature complete:

- [ ] All 27 functional requirements addressed (FR-001 through FR-027)
- [ ] Zero contradictions across documentation sources
- [ ] All code examples execute successfully
- [ ] Sphinx build completes with zero warnings
- [ ] All cross-references resolve correctly
- [ ] Lefthook pre-commit hooks pass
- [ ] SUCCESS CRITERIA met:
  - [ ] SC-001: Zero contradictions verified
  - [ ] SC-002: 100% code examples work
  - [ ] SC-003: Install time <5 minutes (verify README clarity)
  - [ ] SC-004: All API symbols documented
  - [ ] SC-005: Dev setup time <10 minutes (verify contributing.rst)
  - [ ] SC-006: Sphinx builds without warnings
  - [ ] SC-007: All test scripts have Makefile targets

## Commit Strategy

Group changes by priority for reviewability:

```bash
# Commit 1: Critical fixes (P1)
git add docs/source/index.rst docs/source/contributing.rst segnomms/__init__.py docs/source/installation.rst README.md docs/source/conf.py
git commit -m "docs: fix critical contradictions (package name, repo URL, author, Segno version)"

# Commit 2: High priority fixes (P2)
git add pyproject.toml README.md docs/source/installation.rst docs/source/quickstart.rst docs/source/contributing.rst docs/source/api/constants.rst
git commit -m "docs: add Python 3.14 support, fix import paths, add constants API docs"

# Commit 3: Medium priority enhancements (P3)
git add docs/source/contributing.rst docs/source/shapes.rst docs/source/decoder_compatibility.rst docs/source/examples.rst README.md
git commit -m "docs: add spec-kit workflow, complete examples, enhance navigation"

# Commit 4: Low priority polish (P4)
git add docs/source/*.rst
git commit -m "docs: improve code blocks, cross-references, formatting consistency"
```

## Success Criteria Verification

Run after all changes complete:

```bash
# Automated verification script
python scripts/verify_documentation_fixes.py

# Manual verification
make docs && open docs/build/html/index.html

# Final Lefthook validation
git add -A && git commit --dry-run  # Check hooks pass
```

## Next Steps

After completing this quickstart:

1. Run `/speckit.tasks` to generate detailed task breakdown
2. Implement tasks following priority order (P1 → P2 → P3 → P4)
3. Validate each priority level before proceeding to next
4. Create PR when all 27 issues resolved and tests pass
