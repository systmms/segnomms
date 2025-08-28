#!/bin/bash
# Script: repo/setup_spell_checker.sh
# Purpose: Install spell checking tools (aspell) with fallback when cache actions fail
# Usage: ./setup_spell_checker.sh [options]
# GitHub Actions Integration: Used by .github/workflows/docs.yml

set -euo pipefail

# Configuration
VERBOSE=false
PACKAGES=("aspell" "aspell-en")

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --verbose)
            VERBOSE=true
            shift
            ;;
        --help)
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  --verbose     Enable verbose output"
            echo "  --help        Show this help message"
            echo ""
            echo "Purpose:"
            echo "  Installs aspell and aspell-en for documentation spell checking"
            echo "  Provides fallback installation when APT cache actions fail"
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

log_verbose() {
    if [[ "$VERBOSE" == "true" ]]; then
        local timestamp=$(date '+%H:%M:%S')
        echo "[$timestamp] 🔍 $1"
    fi
}

# Check if aspell is already available
check_aspell_availability() {
    if command -v aspell &> /dev/null; then
        local version=$(aspell --version | head -1)
        log_success "aspell is already available: $version"
        return 0
    else
        log_info "aspell not found, installation required"
        return 1
    fi
}

# Install spell checker with fallback
install_spell_checker() {
    log_info "Installing spell checker packages: ${PACKAGES[*]}"

    # Use the existing APT fallback script
    if [[ -f "./repo/setup_apt_fallback.sh" ]]; then
        log_verbose "Using APT fallback script for installation"
        if [[ "$VERBOSE" == "true" ]]; then
            ./repo/setup_apt_fallback.sh --verbose "${PACKAGES[@]}"
        else
            ./repo/setup_apt_fallback.sh "${PACKAGES[@]}"
        fi
    else
        # Direct installation as fallback
        log_verbose "APT fallback script not found, using direct installation"

        if [[ $EUID -eq 0 ]]; then
            SUDO_CMD=""
        else
            SUDO_CMD="sudo"
        fi

        $SUDO_CMD apt-get update -qq
        $SUDO_CMD apt-get install -y -qq "${PACKAGES[@]}"
    fi
}

# Verify installation
verify_installation() {
    log_info "Verifying spell checker installation..."

    if command -v aspell &> /dev/null; then
        local version=$(aspell --version | head -1)
        log_success "aspell verification passed: $version"

        # Show available dictionaries
        log_verbose "Available dictionaries:"
        local available_dicts=$(aspell dicts 2>/dev/null || echo "none")
        if [[ "$VERBOSE" == "true" ]]; then
            echo "   $available_dicts"
        fi

        # Test English dictionary
        if aspell dicts | grep -q "en"; then
            log_success "English dictionary verified"

            # Test actual spell checking functionality
            local test_result=$(echo "test hello wrold" | aspell list 2>/dev/null || echo "test_failed")
            if [[ "$test_result" == "wrold" ]]; then
                log_success "Spell checking functionality verified"
            elif [[ "$test_result" == "test_failed" ]]; then
                log_error "Spell checking test failed - dictionary may not be properly configured"
                log_error "This may cause spell checking to fail in applications"
                return 1
            else
                log_warn "Spell checking test gave unexpected result: '$test_result'"
                log_warn "Expected 'wrold' (the misspelled word)"
            fi
        else
            log_error "English dictionary not found in available dictionaries: $available_dicts"
            log_error "This will cause spell checking to fail"
            return 1
        fi

        return 0
    else
        log_error "aspell verification failed - command not found"
        return 1
    fi
}

# Main function
main() {
    log_info "=== Spell Checker Installation ==="

    # Check if already installed
    if check_aspell_availability; then
        log_success "Spell checker already available, no installation needed"
        return 0
    fi

    # Install packages
    if ! install_spell_checker; then
        log_error "Spell checker installation failed"
        exit 1
    fi

    # Verify installation
    if ! verify_installation; then
        log_error "Spell checker verification failed"
        exit 1
    fi

    log_success "=== Spell checker installation completed successfully! ==="
}

# Trap errors for better debugging
trap 'log_error "Script failed at line $LINENO"' ERR

# Entry point
main "$@"
