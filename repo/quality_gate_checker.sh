#!/bin/bash
# Script: repo/quality_gate_checker.sh
# Purpose: Evaluate quality gate results from multiple CI jobs
# Usage: ./quality_gate_checker.sh --test=STATUS --docs=STATUS [options]
# GitHub Actions Integration: Used by .github/workflows/ci.yml

set -euo pipefail

# Configuration
VERBOSE=false
FAIL_ON_WARNINGS=false

# Job status variables
TEST_STATUS=""
DOCS_STATUS=""
COMPATIBILITY_STATUS=""
VISUAL_STATUS=""
EXAMPLES_STATUS=""
SECURITY_STATUS=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --test=*)
            TEST_STATUS="${1#*=}"
            shift
            ;;
        --docs=*)
            DOCS_STATUS="${1#*=}"
            shift
            ;;
        --documentation=*)
            DOCS_STATUS="${1#*=}"
            shift
            ;;
        --compatibility=*)
            COMPATIBILITY_STATUS="${1#*=}"
            shift
            ;;
        --visual=*)
            VISUAL_STATUS="${1#*=}"
            shift
            ;;
        --visual-regression=*)
            VISUAL_STATUS="${1#*=}"
            shift
            ;;
        --examples=*)
            EXAMPLES_STATUS="${1#*=}"
            shift
            ;;
        --security=*)
            SECURITY_STATUS="${1#*=}"
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
            echo "  --test=STATUS              Test suite result (success/failure/cancelled/skipped)"
            echo "  --docs=STATUS              Documentation build result"
            echo "  --compatibility=STATUS     Compatibility test result"
            echo ""
            echo "Optional options:"
            echo "  --visual=STATUS            Visual regression test result"
            echo "  --examples=STATUS          Example generation result"
            echo "  --security=STATUS          Security scan result"
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

    if [[ -z "$TEST_STATUS" ]]; then
        missing_params+=("--test")
    fi

    if [[ -z "$DOCS_STATUS" ]]; then
        missing_params+=("--docs")
    fi

    if [[ -z "$COMPATIBILITY_STATUS" ]]; then
        missing_params+=("--compatibility")
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

# Check critical jobs (must succeed)
check_critical_jobs() {
    local critical_failures=0
    local critical_jobs=(
        "Test Suite:$TEST_STATUS"
        "Documentation Build:$DOCS_STATUS"
        "Segno Compatibility:$COMPATIBILITY_STATUS"
    )

    log_info "Checking critical jobs..."

    for job_status in "${critical_jobs[@]}"; do
        local job_name="${job_status%%:*}"
        local status="${job_status##*:}"
        local emoji
        emoji=$(get_status_emoji "$status")
        local description
        description=$(get_status_description "$status")

        echo "$emoji $job_name: $description"

        if [[ "$status" != "success" ]]; then
            ((critical_failures++))
            log_error "$job_name failed - Quality gate CRITICAL FAILURE"
        fi
    done

    return $critical_failures
}

# Check optional jobs (warnings only)
check_optional_jobs() {
    local warning_count=0
    local optional_jobs=()

    # Add optional jobs if provided
    if [[ -n "$VISUAL_STATUS" ]]; then
        optional_jobs+=("Visual Regression:$VISUAL_STATUS")
    fi

    if [[ -n "$EXAMPLES_STATUS" ]]; then
        optional_jobs+=("Example Generation:$EXAMPLES_STATUS")
    fi

    if [[ -n "$SECURITY_STATUS" ]]; then
        optional_jobs+=("Security Scan:$SECURITY_STATUS")
    fi

    if [[ ${#optional_jobs[@]} -gt 0 ]]; then
        log_info "Checking optional jobs..."

        for job_status in "${optional_jobs[@]}"; do
            local job_name="${job_status%%:*}"
            local status="${job_status##*:}"
            local emoji
            emoji=$(get_status_emoji "$status")
            local description
            description=$(get_status_description "$status")

            echo "$emoji $job_name: $description"

            if [[ "$status" != "success" ]]; then
                ((warning_count++))

                case "$job_name" in
                    "Visual Regression")
                        log_warn "Visual regression tests failed - review required"
                        log_info "Visual differences may be intentional changes"
                        ;;
                    "Example Generation")
                        log_warn "Example generation failed"
                        log_info "This may affect documentation but not core functionality"
                        ;;
                    "Security Scan")
                        log_warn "Security scan encountered issues"
                        log_info "Review security findings in the scan report"
                        ;;
                esac
            fi
        done
    else
        log_verbose "No optional jobs to check"
    fi

    return $warning_count
}

# Generate summary
generate_summary() {
    local critical_failures="$1"
    local warning_count="$2"
    local total_jobs=$((3 + $(([[ -n "$VISUAL_STATUS" ]] && echo 1) || echo 0) + $(([[ -n "$EXAMPLES_STATUS" ]] && echo 1) || echo 0) + $(([[ -n "$SECURITY_STATUS" ]] && echo 1) || echo 0)))
    local successful_jobs=$((total_jobs - critical_failures - warning_count))

    echo ""
    echo "=========================="
    echo "Quality Gate Summary"
    echo "=========================="
    echo "Total Jobs: $total_jobs"
    echo "Successful: $successful_jobs"
    echo "Critical Failures: $critical_failures"
    echo "Warnings: $warning_count"
    echo ""

    if [[ "$VERBOSE" == "true" ]]; then
        echo "Job Details:"
        echo "  Critical Jobs (must pass):"
        echo "    - Test Suite: $(get_status_description "$TEST_STATUS")"
        echo "    - Documentation Build: $(get_status_description "$DOCS_STATUS")"
        echo "    - Segno Compatibility: $(get_status_description "$COMPATIBILITY_STATUS")"

        if [[ -n "$VISUAL_STATUS" ]] || [[ -n "$EXAMPLES_STATUS" ]] || [[ -n "$SECURITY_STATUS" ]]; then
            echo "  Optional Jobs (warnings only):"
            [[ -n "$VISUAL_STATUS" ]] && echo "    - Visual Regression: $(get_status_description "$VISUAL_STATUS")"
            [[ -n "$EXAMPLES_STATUS" ]] && echo "    - Example Generation: $(get_status_description "$EXAMPLES_STATUS")"
            [[ -n "$SECURITY_STATUS" ]] && echo "    - Security Scan: $(get_status_description "$SECURITY_STATUS")"
        fi
        echo ""
    fi
}

# Main quality gate evaluation
evaluate_quality_gate() {
    echo "Quality Gate Evaluation:"
    echo "=================================="
    echo ""

    # Validate all provided statuses
    validate_status "$TEST_STATUS" "Test Suite" || return 1
    validate_status "$DOCS_STATUS" "Documentation Build" || return 1
    validate_status "$COMPATIBILITY_STATUS" "Compatibility" || return 1

    [[ -n "$VISUAL_STATUS" ]] && { validate_status "$VISUAL_STATUS" "Visual Regression" || return 1; }
    [[ -n "$EXAMPLES_STATUS" ]] && { validate_status "$EXAMPLES_STATUS" "Example Generation" || return 1; }
    [[ -n "$SECURITY_STATUS" ]] && { validate_status "$SECURITY_STATUS" "Security Scan" || return 1; }

    # Check critical jobs
    local critical_failures
    check_critical_jobs
    critical_failures=$?

    echo ""

    # Check optional jobs
    local warning_count
    check_optional_jobs
    warning_count=$?

    # Generate summary
    generate_summary "$critical_failures" "$warning_count"

    # Determine final result
    if [[ $critical_failures -gt 0 ]]; then
        log_error "Quality gate FAILED - Critical job failures detected"
        return 1
    elif [[ $warning_count -gt 0 ]] && [[ "$FAIL_ON_WARNINGS" == "true" ]]; then
        log_error "Quality gate FAILED - Warnings detected and --fail-on-warnings is enabled"
        return 1
    elif [[ $warning_count -gt 0 ]]; then
        log_warn "Quality gate PASSED with warnings - Review recommended"
        return 0
    else
        log_success "Quality gate PASSED - All jobs successful! 🎉"
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
    if evaluate_quality_gate; then
        exit 0
    else
        exit 1
    fi
}

# Entry point
main "$@"
