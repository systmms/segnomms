#!/bin/bash
# Script: repo/validate_conventional_commits.sh
# Purpose: Validate that commits follow conventional commit format
# Usage: ./validate_conventional_commits.sh [--base-ref=main] [--verbose]
# GitHub Actions Integration: Used by .github/workflows/conventional-commits.yml

set -euo pipefail

# Configuration
BASE_REF="main"
VERBOSE=false
EXIT_ON_FAIL=true
LOCAL_MODE=false
COMMIT_MSG_FILE=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --base-ref=*)
            BASE_REF="${1#*=}"
            shift
            ;;
        --commit-msg=*)
            COMMIT_MSG_FILE="${1#*=}"
            LOCAL_MODE=true
            shift
            ;;
        --local-mode)
            LOCAL_MODE=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --no-exit)
            EXIT_ON_FAIL=false
            shift
            ;;
        --help)
            echo "Usage: $0 [options]"
            echo ""
            echo "Modes:"
            echo "  CI Mode (default):     Validate commits in PR against base branch"
            echo "  Local Mode:            Validate single commit message file"
            echo ""
            echo "Options:"
            echo "  --base-ref=BRANCH      Base branch to compare against (default: main)"
            echo "  --commit-msg=FILE      Commit message file to validate (enables local mode)"
            echo "  --local-mode           Enable local mode without commit message file"
            echo "  --verbose              Enable verbose output"
            echo "  --no-exit              Don't exit on validation failure (for testing)"
            echo "  --help                 Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0 --base-ref=develop --verbose               # CI mode"
            echo "  $0 --commit-msg=.git/COMMIT_EDITMSG           # Local mode (git hook)"
            echo "  $0 --local-mode --verbose                     # Local mode (manual)"
            echo ""
            echo "Conventional Commit Format:"
            echo "  <type>(<scope>): <description>"
            echo ""
            echo "Valid types:"
            echo "  feat, fix, perf, deps, docs, test, build, ci, chore, style, refactor, revert"
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
    local timestamp=$(date '+%H:%M:%S')
    echo "[$timestamp] ℹ️  $1"
}

log_success() {
    local timestamp=$(date '+%H:%M:%S')
    echo "[$timestamp] ✅ $1"
}

log_error() {
    local timestamp=$(date '+%H:%M:%S')
    echo "[$timestamp] ❌ $1" >&2
}

log_warn() {
    local timestamp=$(date '+%H:%M:%S')
    echo "[$timestamp] ⚠️  $1"
}

log_verbose() {
    if [[ "$VERBOSE" == "true" ]]; then
        local timestamp=$(date '+%H:%M:%S')
        echo "[$timestamp] 🔍 $1"
    fi
}

# Conventional commit configuration
get_commit_pattern() {
    # Conventional commit regex pattern
    # Supports: type(scope): description
    # Types: feat, fix, perf, deps, docs, test, build, ci, chore, style, refactor, revert
    # Scope is optional
    echo '^(feat|fix|perf|deps|docs|test|build|ci|chore|style|refactor|revert)(\(.+\))?: .+'
}

get_valid_types() {
    echo "feat, fix, perf, deps, docs, test, build, ci, chore, style, refactor, revert"
}

# Get commits in the current branch compared to base
get_commits() {
    local base_ref="origin/$BASE_REF"

    log_info "Getting commits from $base_ref to HEAD..."

    # Check if base ref exists
    if ! git rev-parse --verify "$base_ref" >/dev/null 2>&1; then
        log_error "Base reference '$base_ref' not found"
        log_error "Make sure you have fetched the latest changes: git fetch origin"
        return 1
    fi

    # Get commit messages
    local commits
    commits=$(git log --format="%s" "$base_ref..HEAD")

    if [[ -z "$commits" ]]; then
        log_warn "No commits found between $base_ref and HEAD"
        return 2
    fi

    local commit_count
    commit_count=$(echo "$commits" | wc -l)
    log_info "Found $commit_count commit(s) to validate"

    if [[ "$VERBOSE" == "true" ]]; then
        log_verbose "Commits to validate:"
        echo "$commits" | while IFS= read -r commit; do
            log_verbose "  - $commit"
        done
    fi

    echo "$commits"
}

# Validate a single commit message
validate_commit() {
    local commit_msg="$1"
    local pattern="$2"

    if echo "$commit_msg" | grep -qE "$pattern"; then
        return 0
    else
        return 1
    fi
}

# Analyze commit message and provide specific feedback
analyze_commit() {
    local commit_msg="$1"

    # Check if it starts with a valid type
    if echo "$commit_msg" | grep -qE '^(feat|fix|perf|deps|docs|test|build|ci|chore|style|refactor|revert)'; then
        # Valid type, check format
        if echo "$commit_msg" | grep -qE '^[^:]*: '; then
            # Has colon separator
            if echo "$commit_msg" | grep -qE '^[^:]*: .+'; then
                # Has description
                echo "✅ Valid format"
            else
                echo "❌ Missing description after colon"
            fi
        else
            echo "❌ Missing colon separator and description"
        fi
    else
        # Invalid or missing type
        echo "❌ Invalid or missing type (should be one of: $(get_valid_types))"
    fi
}

# Format validation results
format_results() {
    local invalid_commits="$1"

    if [[ -n "$invalid_commits" ]]; then
        echo ""
        echo "❌ The following commits don't follow conventional commit format:"
        echo ""

        while IFS=$'\n' read -r commit; do
            if [[ -n "$commit" ]]; then
                echo "  📝 $commit"
                if [[ "$VERBOSE" == "true" ]]; then
                    local analysis
                    analysis=$(analyze_commit "$commit")
                    echo "     $analysis"
                fi
            fi
        done <<< "$invalid_commits"

        echo ""
        echo "📝 Expected format: <type>(<scope>): <description>"
        echo "   Example: feat(shapes): add hexagon shape renderer"
        echo ""
        echo "📚 Valid types: $(get_valid_types)"
        echo ""
        echo "ℹ️  Scope is optional but recommended for better categorization"
        echo "ℹ️  Description should be lowercase and not end with a period"

        return 1
    else
        echo ""
        log_success "All commits follow conventional commit format! 🎉"
        return 0
    fi
}

# Main validation function
validate_commits() {
    log_info "=== Conventional Commit Validation ==="

    # Get commits to validate
    local commits
    if ! commits=$(get_commits); then
        if [[ $? -eq 2 ]]; then
            log_success "No commits to validate - validation passed"
            return 0
        else
            return 1
        fi
    fi

    # Get validation pattern
    local pattern
    pattern=$(get_commit_pattern)
    log_verbose "Using pattern: $pattern"

    # Validate each commit
    local invalid_commits=""
    local total_commits=0
    local valid_commits=0

    while IFS= read -r commit; do
        if [[ -n "$commit" ]]; then
            ((total_commits++))

            if validate_commit "$commit" "$pattern"; then
                ((valid_commits++))
                log_verbose "✅ Valid: $commit"
            else
                invalid_commits="${invalid_commits}${commit}\n"
                log_verbose "❌ Invalid: $commit"
            fi
        fi
    done <<< "$commits"

    log_info "Validation summary: $valid_commits/$total_commits commits valid"

    # Format and display results
    if format_results "$invalid_commits"; then
        log_success "=== Validation completed successfully ==="
        return 0
    else
        log_error "=== Validation failed ==="
        return 1
    fi
}

# Git environment check
check_git_environment() {
    # Check if we're in a git repository
    if ! git rev-parse --git-dir >/dev/null 2>&1; then
        log_error "Not in a git repository"
        return 1
    fi

    # Check if we have commits
    if ! git rev-parse --verify HEAD >/dev/null 2>&1; then
        log_error "No commits found in repository"
        return 1
    fi

    log_verbose "Git environment check passed"
    return 0
}

# Validate single commit message for local mode
validate_commit_message() {
    local commit_msg=""

    if [[ -n "$COMMIT_MSG_FILE" ]]; then
        if [[ ! -f "$COMMIT_MSG_FILE" ]]; then
            log_error "Commit message file not found: $COMMIT_MSG_FILE"
            return 1
        fi

        # Read first line of commit message file
        commit_msg=$(head -n 1 "$COMMIT_MSG_FILE")
        log_verbose "Read commit message from file: $COMMIT_MSG_FILE"
    else
        # Read from stdin if no file specified
        log_info "Enter commit message to validate:"
        read -r commit_msg
    fi

    if [[ -z "$commit_msg" ]]; then
        log_error "Empty commit message"
        return 1
    fi

    log_verbose "Validating commit message: $commit_msg"

    # Get validation pattern
    local pattern
    pattern=$(get_commit_pattern)
    log_verbose "Using pattern: $pattern"

    # Validate the commit message
    if [[ $commit_msg =~ $pattern ]]; then
        log_success "✅ Commit message follows conventional commit format!"

        if [[ "$VERBOSE" == "true" ]]; then
            local analysis
            analysis=$(analyze_commit "$commit_msg")
            echo "   $analysis"
        fi

        return 0
    else
        log_error "❌ Commit message does not follow conventional commit format:"
        echo "   Message: $commit_msg"
        echo ""

        if [[ "$VERBOSE" == "true" ]]; then
            local analysis
            analysis=$(analyze_commit "$commit_msg")
            echo "   Analysis: $analysis"
            echo ""
        fi

        echo "📝 Expected format: <type>(<scope>): <description>"
        echo "   Example: feat(shapes): add hexagon shape renderer"
        echo ""
        echo "📚 Valid types: $(get_valid_types)"
        echo ""
        echo "ℹ️  Scope is optional but recommended for better categorization"
        echo "ℹ️  Description should be lowercase and not end with a period"

        return 1
    fi
}

# Main function
main() {
    if [[ "$LOCAL_MODE" == "true" ]]; then
        log_info "=== Local Commit Message Validation ==="

        # Run local validation
        if validate_commit_message; then
            exit 0
        else
            if [[ "$EXIT_ON_FAIL" == "true" ]]; then
                exit 1
            else
                log_warn "Validation failed but continuing due to --no-exit flag"
                exit 0
            fi
        fi
    else
        # Check git environment for CI mode
        if ! check_git_environment; then
            exit 1
        fi

        # Run CI validation
        if validate_commits; then
            exit 0
        else
            if [[ "$EXIT_ON_FAIL" == "true" ]]; then
                exit 1
            else
                log_warn "Validation failed but continuing due to --no-exit flag"
                exit 0
            fi
        fi
    fi
}

# Trap errors for better debugging
trap 'log_error "Script failed at line $LINENO"' ERR

# Entry point
main "$@"
