#!/usr/bin/env bash
set -euo pipefail

# Run comprehensive test coverage analysis
# Used by: .github/workflows/coverage.yml

echo "🧪 Running comprehensive test coverage..."

# Run all tests with coverage
uv run pytest tests/ \
  --cov=segnomms \
  --cov-report=html \
  --cov-report=xml \
  --cov-report=term-missing \
  --cov-fail-under=75 \
  --cov-branch \
  -v

echo "✅ Comprehensive coverage analysis completed"
