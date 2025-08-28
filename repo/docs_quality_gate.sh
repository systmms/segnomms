#!/bin/bash
# Script: repo/docs_quality_gate.sh
# Purpose: Evaluate documentation quality gate results
# Usage: ./docs_quality_gate.sh --build=STATUS --examples=STATUS --spell=STATUS [options]
# GitHub Actions Integration: Used by .github/workflows/docs.yml

set -euo pipefail

# Configuration
VERBOSE=false
FAIL_ON_WARNINGS=false

# Job status variables
BUILD_STATUS=""
EXAMPLES_STATUS=""
SPELL_STATUS=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --build=*)
            BUILD_STATUS="${1#*=}"
            shift
            ;;
        --build-docs=*)
            BUILD_STATUS="${1#*=}"
            shift
            ;;
        --examples=*)
            EXAMPLES_STATUS="${1#*=}"
            shift
            ;;
        --test-examples=*)
            EXAMPLES_STATUS="${1#*=}"
            shift
            ;;
        --spell=*)
            SPELL_STATUS="${1#*=}"
            shift
            ;;
        --spell-check=*)
            SPELL_STATUS="${1#*=}"
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --fail-on-warnings)
            FAIL_ON_WARNINGS=true
            shift
            ;;
        --help)
            echo "Usage: $0 [options]"
            echo ""
            echo "Required options:"
            echo "  --build=STATUS             Documentation build result (success/failure/cancelled/skipped)"
            echo "  --examples=STATUS          Examples testing result"
            echo "  --spell=STATUS             Spell check result"
            echo ""
            echo "Flags:"
            echo "  --verbose                  Enable verbose output"
            echo "  --fail-on-warnings         Fail quality gate on warnings (default: false)"
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

    if [[ -z "$BUILD_STATUS" ]]; then
        missing_params+=(--build)
    fi

    if [[ -z "$EXAMPLES_STATUS" ]]; then
        missing_params+=(--examples)
    fi

    if [[ -z "$SPELL_STATUS" ]]; then
        missing_params+=(--spell)
    fi

    if [[ ${#missing_params[@]} -gt 0 ]]; then
        log_error "Missing required parameters: ${missing_params[*]}"
        log_error "Run '$0 --help' for usage information"
        return 1
    fi

    log_verbose "All required parameters provided"
    return 0
}

# Validate status values
validate_status() {
    local status="$1"
    local job_name="$2"

    case "$status" in
        success|failure|cancelled|skipped)
            return 0
            ;;
        *)
            log_error "Invalid status '$status' for $job_name"
            log_error "Valid statuses: success, failure, cancelled, skipped"
            return 1
            ;;
    esac
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

# Evaluate documentation quality gate
evaluate_documentation_quality() {
    echo "Documentation Quality Gate Evaluation:"
    echo "=================================="
    echo ""

    # Validate all provided statuses
    validate_status "$BUILD_STATUS" "Documentation Build" || return 1
    validate_status "$EXAMPLES_STATUS" "Examples Testing" || return 1
    validate_status "$SPELL_STATUS" "Spell Check" || return 1

    # Display job results
    local build_emoji examples_emoji spell_emoji
    build_emoji=$(get_status_emoji "$BUILD_STATUS")
    examples_emoji=$(get_status_emoji "$EXAMPLES_STATUS")
    spell_emoji=$(get_status_emoji "$SPELL_STATUS")

    echo "$build_emoji Documentation Build: $(get_status_description "$BUILD_STATUS")"
    echo "$examples_emoji Examples Testing: $(get_status_description "$EXAMPLES_STATUS")"
    echo "$spell_emoji Spell Check: $(get_status_description "$SPELL_STATUS")"
    echo ""

    # Evaluate critical jobs (documentation build must succeed)
    local critical_failures=0
    local warning_count=0

    if [[ "$BUILD_STATUS" != "success" ]]; then
        log_error "Documentation build failed - Quality gate FAILED"
        critical_failures=1
    fi

    # Evaluate optional jobs (warnings only)
    if [[ "$EXAMPLES_STATUS" != "success" ]]; then
        log_warn "Examples testing failed - Quality gate WARNING"
        log_info "Examples testing issues may affect documentation quality but not core functionality"
        ((warning_count++))
    fi

    if [[ "$SPELL_STATUS" != "success" ]]; then
        log_warn "Spell check issues detected - Quality gate WARNING"
        log_info "Spelling issues should be reviewed but won't block documentation"
        ((warning_count++))
    fi

    # Generate summary
    echo ""
    echo "=========================="
    echo "Documentation Quality Gate Summary"
    echo "=========================="
    echo "Critical Failures: $critical_failures"
    echo "Warnings: $warning_count"
    echo ""

    if [[ "$VERBOSE" == "true" ]]; then
        echo "Job Details:"
        echo "  Critical Jobs (must pass):"
        echo "    - Documentation Build: $(get_status_description "$BUILD_STATUS")"
        echo "  Optional Jobs (warnings only):"
        echo "    - Examples Testing: $(get_status_description "$EXAMPLES_STATUS")"
        echo "    - Spell Check: $(get_status_description "$SPELL_STATUS")"
        echo ""
    fi

    # Determine final result
    if [[ $critical_failures -gt 0 ]]; then
        log_error "Documentation quality gate FAILED - Critical job failures detected"
        return 1
    elif [[ $warning_count -gt 0 ]] && [[ "$FAIL_ON_WARNINGS" == "true" ]]; then
        log_error "Documentation quality gate FAILED - Warnings detected and --fail-on-warnings is enabled"
        return 1
    elif [[ $warning_count -gt 0 ]]; then
        log_warn "Documentation quality gate PASSED with warnings - Review recommended"
        return 0
    else
        log_success "Documentation quality gate PASSED - All jobs successful! 📚✨"
        return 0
    fi
}

# Main function
main() {
    # Validate parameters
    if ! validate_parameters; then
        exit 1
    fi

    # Run quality gate evaluation
    if evaluate_documentation_quality; then
        exit 0
    else
        exit 1
    fi
}

# Entry point
main "$@"
