#!/usr/bin/env bash
set -euo pipefail

# Generate coverage summary markdown for GitHub Actions
# Used by: .github/workflows/coverage.yml

echo "📊 Generating coverage summary..."

# Create coverage summary markdown file
{
  echo "## 📊 Coverage Report"
  echo ""
  echo "**Overall Coverage: ${COVERAGE_PERCENT}%**"
  echo ""
  echo "![Coverage Badge](${COVERAGE_BADGE})"
  echo ""
  echo "### Module Coverage Details"
  echo ""
  echo "| Module | Coverage | Missing Lines |"
  echo "|--------|----------|---------------|"
} > coverage-summary.md

# Add detailed module coverage (allow to fail gracefully)
uv run coverage report --format=markdown >> coverage-summary.md || true

echo "✅ Coverage summary generated: coverage-summary.md"
