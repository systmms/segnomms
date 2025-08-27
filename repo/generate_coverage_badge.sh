#!/usr/bin/env bash
set -euo pipefail

# Generate coverage badge and environment variables for GitHub Actions
# Used by: .github/workflows/coverage.yml

echo "🏷️ Generating coverage badge..."

# Extract coverage percentage
COVERAGE=$(uv run coverage report --format=total)
echo "Coverage: ${COVERAGE}%"

# Create badge color based on coverage
if [ "${COVERAGE}" -ge 90 ]; then
  COLOR="brightgreen"
elif [ "${COVERAGE}" -ge 80 ]; then
  COLOR="green"
elif [ "${COVERAGE}" -ge 70 ]; then
  COLOR="yellowgreen"
elif [ "${COVERAGE}" -ge 60 ]; then
  COLOR="yellow"
elif [ "${COVERAGE}" -ge 50 ]; then
  COLOR="orange"
else
  COLOR="red"
fi

# Generate badge URL and set environment variables
BADGE_URL="https://img.shields.io/badge/coverage-${COVERAGE}%25-${COLOR}"

# Output environment variables for GitHub Actions
echo "COVERAGE_BADGE=${BADGE_URL}" >> "${GITHUB_ENV}"
echo "COVERAGE_PERCENT=${COVERAGE}" >> "${GITHUB_ENV}"

echo "✅ Coverage badge generated: ${COVERAGE}% (${COLOR})"
