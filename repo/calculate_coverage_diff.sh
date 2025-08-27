#!/usr/bin/env bash
set -euo pipefail

# Calculate coverage difference between current and base branch
# Used by: .github/workflows/coverage.yml

echo "📈 Calculating coverage difference..."

# Validate environment variables are set
if [[ -z "${CURRENT_COVERAGE:-}" ]] || [[ -z "${BASE_COVERAGE:-}" ]]; then
  echo "❌ Error: CURRENT_COVERAGE and BASE_COVERAGE environment variables must be set"
  exit 1
fi

# Calculate difference
DIFF=$((CURRENT_COVERAGE - BASE_COVERAGE))
echo "Coverage difference: ${DIFF}%"

# Set difference environment variable
echo "COVERAGE_DIFF=${DIFF}" >> "${GITHUB_ENV}"

# Set icon and color based on difference
if [ "${DIFF}" -gt 0 ]; then
  echo "DIFF_ICON=📈" >> "${GITHUB_ENV}"
  echo "DIFF_COLOR=green" >> "${GITHUB_ENV}"
  echo "✅ Coverage improved by ${DIFF}%"
elif [ "${DIFF}" -lt 0 ]; then
  echo "DIFF_ICON=📉" >> "${GITHUB_ENV}"
  echo "DIFF_COLOR=red" >> "${GITHUB_ENV}"
  echo "⚠️ Coverage decreased by ${DIFF}%"
else
  echo "DIFF_ICON=➡️" >> "${GITHUB_ENV}"
  echo "DIFF_COLOR=gray" >> "${GITHUB_ENV}"
  echo "ℹ️ Coverage unchanged"
fi

echo "✅ Coverage difference calculated successfully"
