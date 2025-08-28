#!/bin/bash
# Script: repo/setup_cspell.sh
# Purpose: Install cspell (Code Spell Checker) for documentation spell checking
# Usage: ./setup_cspell.sh [options]
# GitHub Actions Integration: Used by .github/workflows/docs.yml

set -euo pipefail

# Configuration
VERBOSE=false
NODE_MIN_VERSION="16"

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
            echo "  Installs cspell (Code Spell Checker) for documentation spell checking"
            echo "  Provides modern code-aware spell checking with better accuracy than aspell"
            echo ""
            echo "Requirements:"
            echo "  - Node.js >= 16.0.0"
            echo "  - npm package manager"
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

# Check Node.js availability and version
check_node_availability() {
    if ! command -v node &> /dev/null; then
        log_error "Node.js not found"
        return 1
    fi

    if ! command -v npm &> /dev/null; then
        log_error "npm not found"
        return 1
    fi

    local node_version=$(node --version | sed 's/v//')
    local major_version=$(echo "$node_version" | cut -d. -f1)

    log_verbose "Found Node.js version: $node_version"

    if [[ "$major_version" -lt "$NODE_MIN_VERSION" ]]; then
        log_error "Node.js version $node_version is too old. Minimum required: $NODE_MIN_VERSION"
        return 1
    fi

    log_success "Node.js $node_version and npm are available"
    return 0
}

# Check if cspell is already available
check_cspell_availability() {
    # Check npx cspell (preferred method)
    if command -v npx &> /dev/null; then
        if npx cspell --version &> /dev/null; then
            local version=$(npx cspell --version 2>/dev/null)
            log_success "cspell is available via npx: $version"
            return 0
        fi
    fi

    # Check global cspell installation
    if command -v cspell &> /dev/null; then
        local version=$(cspell --version 2>/dev/null)
        log_success "cspell is globally installed: $version"
        return 0
    fi

    log_info "cspell not found, installation required"
    return 1
}

# Install Node.js if not available (Linux only)
install_node_linux() {
    log_info "Attempting to install Node.js on Linux..."

    if command -v apt-get &> /dev/null; then
        # Ubuntu/Debian
        log_verbose "Using apt-get to install Node.js"

        # Add NodeSource repository for latest Node.js LTS
        curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
        sudo apt-get install -y nodejs

    elif command -v yum &> /dev/null; then
        # RHEL/CentOS/Fedora
        log_verbose "Using yum to install Node.js"

        curl -fsSL https://rpm.nodesource.com/setup_lts.x | sudo bash -
        sudo yum install -y nodejs npm

    else
        log_error "Unable to install Node.js automatically on this Linux distribution"
        log_error "Please install Node.js manually: https://nodejs.org/"
        return 1
    fi
}

# Install cspell using npm
install_cspell() {
    log_info "Installing cspell..."

    # First ensure we have package.json and can install dependencies
    if [[ -f "package.json" ]]; then
        log_verbose "Installing from package.json dependencies"

        if [[ "$VERBOSE" == "true" ]]; then
            npm install
        else
            npm install --silent
        fi

        log_success "npm install completed"
    else
        # Fallback to global installation if no package.json
        log_verbose "No package.json found, installing cspell globally"

        if [[ "$VERBOSE" == "true" ]]; then
            npm install -g cspell
        else
            npm install -g cspell --silent
        fi

        log_success "cspell installed globally"
    fi
}

# Verify cspell installation and functionality
verify_installation() {
    log_info "Verifying cspell installation..."

    local cspell_cmd=""
    local version=""

    # Determine how to run cspell
    if command -v npx &> /dev/null && npx cspell --version &> /dev/null; then
        cspell_cmd="npx cspell"
        version=$(npx cspell --version 2>/dev/null)
        log_success "cspell verification passed (via npx): $version"
    elif command -v cspell &> /dev/null; then
        cspell_cmd="cspell"
        version=$(cspell --version 2>/dev/null)
        log_success "cspell verification passed (global): $version"
    else
        log_error "cspell verification failed - command not found"
        return 1
    fi

    # Test cspell functionality with a simple spell check
    log_verbose "Testing cspell functionality..."

    local test_file=$(mktemp)
    echo "This is a test with a mispelled word: wrold" > "$test_file"

    if $cspell_cmd --no-progress "$test_file" &> /dev/null; then
        # cspell returns 0 for no errors, 1 for spelling errors
        # We expect errors in our test, so exit code 1 is success
        log_verbose "cspell test completed - no errors detected in test file"
    else
        log_success "cspell functionality verified - correctly detected spelling errors"
    fi

    rm -f "$test_file"

    # Verify project configuration exists
    if [[ -f "cspell.json" ]]; then
        log_success "Found cspell.json configuration"

        if [[ "$VERBOSE" == "true" ]]; then
            log_verbose "Configuration validation:"
            if $cspell_cmd --config cspell.json --show-config &> /dev/null; then
                log_verbose "cspell configuration is valid"
            else
                log_error "cspell configuration validation failed"
                return 1
            fi
        fi
    else
        log_error "cspell.json configuration not found"
        log_error "This may cause spell checking to use default settings"
        return 1
    fi

    # Check project dictionary
    if [[ -f "project-words.txt" ]]; then
        local word_count=$(wc -l < project-words.txt)
        log_success "Found project dictionary with $word_count words"
    else
        log_error "project-words.txt dictionary not found"
        log_error "Custom project terms will not be available"
        return 1
    fi

    return 0
}

# Main function
main() {
    log_info "=== cspell (Code Spell Checker) Installation ==="

    # Check if Node.js is available
    if ! check_node_availability; then
        if [[ "$OSTYPE" == "linux-gnu"* ]]; then
            log_info "Attempting to install Node.js automatically..."
            if ! install_node_linux; then
                log_error "Failed to install Node.js automatically"
                exit 1
            fi

            # Re-check after installation
            if ! check_node_availability; then
                log_error "Node.js installation verification failed"
                exit 1
            fi
        else
            log_error "Please install Node.js manually:"
            log_error "  • macOS: brew install node"
            log_error "  • Windows: Download from https://nodejs.org/"
            log_error "  • Linux: Use your distribution's package manager"
            exit 1
        fi
    fi

    # Check if cspell is already installed
    if check_cspell_availability; then
        log_success "cspell already available, skipping installation"
    else
        # Install cspell
        if ! install_cspell; then
            log_error "cspell installation failed"
            exit 1
        fi
    fi

    # Verify installation
    if ! verify_installation; then
        log_error "cspell verification failed"
        exit 1
    fi

    log_success "=== cspell installation completed successfully! ==="
    log_info "Usage: npx cspell '**/*' or npm run spell-check"
}

# Trap errors for better debugging
trap 'log_error "Script failed at line $LINENO"' ERR

# Entry point
main "$@"
