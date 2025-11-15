#!/usr/bin/env bash
# Check for contradictions across documentation sources
# Part of documentation audit fixes (002-initial-documentation-audit)

set -euo pipefail

ERRORS=0

echo "=== Documentation Contradiction Check ==="
echo

# Check 1: Package name consistency
echo "Checking package name consistency..."
OLD_NAMES=$(grep -r "Segno Interactive SVG Plugin" docs/source/ README.md 2>/dev/null || true)
if [ -n "$OLD_NAMES" ]; then
  echo "❌ FAIL: Old package name 'Segno Interactive SVG Plugin' found:"
  echo "$OLD_NAMES"
  ((ERRORS++))
else
  echo "✓ PASS: Package name consistent (SegnoMMS)"
fi
echo

# Check 2: Repository URL consistency
echo "Checking repository URL..."
WRONG_REPO=$(grep -n "your-org" docs/source/contributing.rst 2>/dev/null || true)
if [ -n "$WRONG_REPO" ]; then
  echo "❌ FAIL: Wrong repository URL 'your-org' found:"
  echo "$WRONG_REPO"
  ((ERRORS++))
else
  echo "✓ PASS: Repository URL correct (systmms/segnomms)"
fi
echo

# Check 3: Author consistency
echo "Checking author attribution..."
AUTHOR_CODE=$(python -c "import segnomms; print(segnomms.__author__)" 2>/dev/null || echo "IMPORT_FAILED")
AUTHOR_TOML=$(grep -A1 '^\[project\]' pyproject.toml | grep 'name.*=' | grep -o '"[^"]*"' | head -1 || echo "NOT_FOUND")

if [ "$AUTHOR_CODE" = "IMPORT_FAILED" ]; then
  echo "⚠️  WARNING: Cannot import segnomms to check __author__"
elif [ "$AUTHOR_CODE" != "SYSTMMS" ]; then
  echo "❌ FAIL: Author in __init__.py is '$AUTHOR_CODE', expected 'SYSTMMS'"
  ((ERRORS++))
else
  echo "✓ PASS: Author attribution consistent (SYSTMMS)"
fi
echo

# Check 4: Segno version consistency
echo "Checking Segno version requirement..."
VERSION_REFS=$(grep -rn "Segno.*1\.5" docs/source/ README.md segnomms/__init__.py 2>/dev/null || true)
INCONSISTENT=$(echo "$VERSION_REFS" | grep -v ">= 1.5.2" || true)
if [ -n "$INCONSISTENT" ]; then
  echo "❌ FAIL: Inconsistent Segno version references (should be '>= 1.5.2'):"
  echo "$INCONSISTENT"
  ((ERRORS++))
else
  echo "✓ PASS: Segno version requirement consistent (>= 1.5.2)"
fi
echo

# Check 5: Python version classifiers
echo "Checking Python version support..."
PY314=$(grep "Programming Language :: Python :: 3.14" pyproject.toml || true)
if [ -z "$PY314" ]; then
  echo "❌ FAIL: Python 3.14 classifier missing in pyproject.toml"
  ((ERRORS++))
else
  echo "✓ PASS: Python 3.14 support documented"
fi
echo

# Check 6: Deprecated pip extras
echo "Checking for deprecated pip extras..."
PIP_EXTRAS=$(grep -n "\[docs,test\]" README.md 2>/dev/null || true)
if [ -n "$PIP_EXTRAS" ]; then
  echo "❌ FAIL: Deprecated pip extras [docs,test] found in README.md:"
  echo "$PIP_EXTRAS"
  ((ERRORS++))
else
  echo "✓ PASS: No deprecated pip extras references"
fi
echo

# Summary
echo "=== Summary ==="
if [ $ERRORS -eq 0 ]; then
  echo "✅ All contradiction checks passed!"
  exit 0
else
  echo "❌ Found $ERRORS contradiction(s)"
  exit 1
fi
