#!/bin/bash
# Script: repo/validate_release_status.sh
# Purpose: Evaluate release validation results from multiple jobs
# Usage: ./validate_release_status.sh --test-matrix=STATUS --package=STATUS [options]
# GitHub Actions Integration: Used by .github/workflows/validate-release.yml

set -euo pipefail

# Configuration
VERBOSE=false

# Job status variables
TEST_MATRIX_STATUS=""
PACKAGE_STATUS=""
INSTALL_STATUS=""
QUALITY_STATUS=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --test-matrix=*)
            TEST_MATRIX_STATUS="${1#*=}"
            shift
            ;;
        --package=*)
            PACKAGE_STATUS="${1#*=}"
            shift
            ;;
        --validate-package=*)
            PACKAGE_STATUS="${1#*=}"
            shift
            ;;
        --install=*)
            INSTALL_STATUS="${1#*=}"
            shift
            ;;
        --test-install=*)
            INSTALL_STATUS="${1#*=}"
            shift
            ;;
        --quality=*)
            QUALITY_STATUS="${1#*=}"
            shift
            ;;
        --quality-checks=*)
            QUALITY_STATUS="${1#*=}"
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --help)
            echo "Usage: $0 [options]"
            echo ""
            echo "Required options:"
            echo "  --test-matrix=STATUS       Cross-platform test matrix result"
            echo "  --package=STATUS           Package validation result"
            echo "  --install=STATUS           Package installation test result"
            echo ""
            echo "Optional options:"
            echo "  --quality=STATUS           Quality checks result"
            echo ""
            echo "Flags:"
            echo "  --verbose                  Enable verbose output"
            echo "  --help                     Show this help message"
            echo ""
            echo "Status values:"
            echo "  success    - Job completed successfully"
            echo "  failure    - Job failed"
            echo "  cancelled  - Job was cancelled"
            echo "  skipped    - Job was skipped"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Run '$0 --help' for usage information"
            exit 1
            ;;
    esac
done

# Logging functions
log_info() {
    echo "ℹ️  $1"
}

log_success() {
    echo "✅ $1"
}

log_error() {
    echo "❌ $1" >&2
}

log_warn() {
    echo "⚠️  $1"
}

log_verbose() {
    if [[ "$VERBOSE" == "true" ]]; then
        echo "🔍 $1"
    fi
}

# Validate required parameters
validate_parameters() {
    local missing_params=()

    if [[ -z "$TEST_MATRIX_STATUS" ]]; then
        missing_params+=(--test-matrix)
    fi

    if [[ -z "$PACKAGE_STATUS" ]]; then
        missing_params+=(--package)
    fi


    if [[ -z "$INSTALL_STATUS" ]]; then
        missing_params+=(--install)
    fi

    if [[ ${#missing_params[@]} -gt 0 ]]; then
        log_error "Missing required parameters: ${missing_params[*]}"
        log_error "Run '$0 --help' for usage information"
        return 1
    fi

    log_verbose "All required parameters provided"
    return 0
}

# Get status emoji
get_status_emoji() {
    local status="$1"

    case "$status" in
        success)   echo "✅" ;;
        failure)   echo "❌" ;;
        cancelled) echo "🚫" ;;
        skipped)   echo "⏭️" ;;
        *)         echo "❓" ;;
    esac
}

# Get status description
get_status_description() {
    local status="$1"

    case "$status" in
        success)   echo "Success" ;;
        failure)   echo "Failed" ;;
        cancelled) echo "Cancelled" ;;
        skipped)   echo "Skipped" ;;
        *)         echo "Unknown" ;;
    esac
}

# Evaluate release validation results
evaluate_release_validation() {
    echo "Release Validation Results:"
    echo "=========================="
    echo ""

    # Display all job results
    local test_emoji package_emoji install_emoji quality_emoji
    test_emoji=$(get_status_emoji "$TEST_MATRIX_STATUS")
    package_emoji=$(get_status_emoji "$PACKAGE_STATUS")
    install_emoji=$(get_status_emoji "$INSTALL_STATUS")

    echo "$test_emoji Test Matrix: $(get_status_description "$TEST_MATRIX_STATUS")"
    echo "$package_emoji Package Validation: $(get_status_description "$PACKAGE_STATUS")"
    echo "$install_emoji Install Tests: $(get_status_description "$INSTALL_STATUS")"

    if [[ -n "$QUALITY_STATUS" ]]; then
        quality_emoji=$(get_status_emoji "$QUALITY_STATUS")
        echo "$quality_emoji Quality Checks: $(get_status_description "$QUALITY_STATUS")"
    fi

    echo ""

    # Evaluate critical jobs (must succeed for release)
    local critical_failures=0
    local required_jobs=(
        "Test Matrix:$TEST_MATRIX_STATUS"
        "Package Validation:$PACKAGE_STATUS"
        "Install Tests:$INSTALL_STATUS"
    )

    log_info "Evaluating critical jobs..."

    for job_status in "${required_jobs[@]}"; do
        local job_name="${job_status%%:*}"
        local status="${job_status##*:}"

        if [[ "$status" != "success" ]]; then
            ((critical_failures++))
            log_error "$job_name failed - Release validation CRITICAL FAILURE"
        else
            log_verbose "$job_name passed"
        fi
    done

    # Evaluate optional jobs (quality checks)
    local warning_count=0

    if [[ -n "$QUALITY_STATUS" ]] && [[ "$QUALITY_STATUS" != "success" ]]; then
        log_warn "Quality checks failed - Review recommended"
        log_info "Quality check failures are informational and don't block release"
        ((warning_count++))
    fi

    # Generate summary
    echo ""
    echo "=========================="
    echo "Release Validation Summary"
    echo "=========================="
    echo "Critical Failures: $critical_failures"
    echo "Warnings: $warning_count"
    echo ""

    if [[ "$VERBOSE" == "true" ]]; then
        echo "Validation Details:"
        echo "  Required Jobs (must pass):"
        echo "    - Test Matrix: $(get_status_description "$TEST_MATRIX_STATUS")"
        echo "    - Package Validation: $(get_status_description "$PACKAGE_STATUS")"
        echo "    - Install Tests: $(get_status_description "$INSTALL_STATUS")"
        if [[ -n "$QUALITY_STATUS" ]]; then
            echo "  Optional Jobs (informational):"
            echo "    - Quality Checks: $(get_status_description "$QUALITY_STATUS")"
        fi
        echo ""
    fi

    # Determine final result
    if [[ $critical_failures -gt 0 ]]; then
        log_error "Release validation FAILED - One or more critical checks failed"
        echo ""
        echo "📋 Failed validation means:"
        echo "   - The package is not ready for release"
        echo "   - Critical functionality or compatibility issues exist"
        echo "   - Fix the issues before attempting release"
        return 1
    elif [[ $warning_count -gt 0 ]]; then
        log_warn "Release validation PASSED with warnings - Review recommended"
        echo ""
        echo "📋 Warnings indicate:"
        echo "   - The package is functional and ready for release"
        echo "   - Quality check issues should be reviewed"
        echo "   - Consider fixing warnings before release"
        return 0
    else
        log_success "Release validation PASSED - All checks successful! 🚀"
        echo ""
        echo "📋 Successful validation means:"
        echo "   - Cross-platform compatibility verified"
        echo "   - Package build and metadata validated"
        echo "   - Installation and basic functionality working"
        echo "   - Ready for production release!"
        return 0
    fi
}

# Main function
main() {
    # Validate parameters
    if ! validate_parameters; then
        exit 1
    fi

    # Run release validation evaluation
    if evaluate_release_validation; then
        exit 0
    else
        exit 1
    fi
}

# Entry point
main "$@"
