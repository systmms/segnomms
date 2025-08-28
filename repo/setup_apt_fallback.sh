#!/bin/bash
# Script: repo/setup_apt_fallback.sh
# Purpose: Install APT packages with fallback when cache actions fail
# Usage: ./setup_apt_fallback.sh package1 [package2 ...]
# GitHub Actions Integration: Used by multiple workflows for librsvg2-bin, aspell, etc.

set -euo pipefail

# Configuration
VERBOSE=false
UPDATE_CACHE=true
VERIFY_INSTALLATION=true

# Parse command line arguments
PACKAGES=()
while [[ $# -gt 0 ]]; do
    case $1 in
        --verbose)
            VERBOSE=true
            shift
            ;;
        --no-update)
            UPDATE_CACHE=false
            shift
            ;;
        --no-verify)
            VERIFY_INSTALLATION=false
            shift
            ;;
        --help)
            echo "Usage: $0 [options] package1 [package2 ...]"
            echo ""
            echo "Options:"
            echo "  --verbose     Enable verbose output"
            echo "  --no-update   Skip apt-get update (use existing cache)"
            echo "  --no-verify   Skip installation verification"
            echo "  --help        Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0 librsvg2-bin                    # Install rsvg-convert"
            echo "  $0 aspell aspell-en                # Install spell checker"
            echo "  $0 --verbose --no-update git       # Install git without updating cache"
            exit 0
            ;;
        -*)
            echo "Unknown option: $1"
            echo "Run '$0 --help' for usage information"
            exit 1
            ;;
        *)
            PACKAGES+=("$1")
            shift
            ;;
    esac
done

# Check if packages were provided
if [[ ${#PACKAGES[@]} -eq 0 ]]; then
    echo "Error: No packages specified"
    echo "Run '$0 --help' for usage information"
    exit 1
fi

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

# Check if running on Ubuntu/Debian
check_apt_availability() {
    if ! command -v apt-get >/dev/null 2>&1; then
        log_error "apt-get not found - this script requires Ubuntu/Debian"
        return 1
    fi

    log_verbose "apt-get is available"
    return 0
}

# Check if running as root or with sudo
check_permissions() {
    if [[ $EUID -eq 0 ]]; then
        log_verbose "Running as root"
        SUDO_CMD=""
    elif command -v sudo >/dev/null 2>&1; then
        log_verbose "Using sudo for package installation"
        SUDO_CMD="sudo"
    else
        log_error "Neither running as root nor sudo available"
        return 1
    fi

    return 0
}

# Check if packages are already installed
check_existing_packages() {
    local packages_to_install=()
    local already_installed=()

    log_info "Checking existing package installation..."

    for package in "${PACKAGES[@]}"; do
        if dpkg -l "$package" >/dev/null 2>&1; then
            already_installed+=("$package")
            log_verbose "$package is already installed"
        else
            packages_to_install+=("$package")
            log_verbose "$package needs to be installed"
        fi
    done

    if [[ ${#already_installed[@]} -gt 0 ]]; then
        log_info "Already installed: ${already_installed[*]}"
    fi

    if [[ ${#packages_to_install[@]} -eq 0 ]]; then
        log_success "All requested packages are already installed"
        return 1  # Nothing to install
    fi

    # Update the global PACKAGES array with only packages that need installation
    PACKAGES=("${packages_to_install[@]}")
    log_info "Packages to install: ${PACKAGES[*]}"

    return 0
}

# Update package cache
update_package_cache() {
    if [[ "$UPDATE_CACHE" != "true" ]]; then
        log_info "Skipping package cache update (--no-update specified)"
        return 0
    fi

    log_info "Updating package cache..."

    if $SUDO_CMD apt-get update -qq; then
        log_success "Package cache updated successfully"
        return 0
    else
        log_error "Failed to update package cache"
        return 1
    fi
}

# Install packages
install_packages() {
    log_info "Installing packages: ${PACKAGES[*]}"

    # Build apt-get command
    local apt_cmd=("$SUDO_CMD" "apt-get" "install" "-y")

    # Add quiet flags if not verbose
    if [[ "$VERBOSE" != "true" ]]; then
        apt_cmd+=("-qq")
    fi

    # Add packages
    apt_cmd+=("${PACKAGES[@]}")

    log_verbose "Executing: ${apt_cmd[*]}"

    if "${apt_cmd[@]}"; then
        log_success "All packages installed successfully"
        return 0
    else
        log_error "Package installation failed"
        return 1
    fi
}

# Verify installation by checking if expected commands are available
verify_installation() {
    if [[ "$VERIFY_INSTALLATION" != "true" ]]; then
        log_info "Skipping installation verification (--no-verify specified)"
        return 0
    fi

    log_info "Verifying package installation..."

    local verification_failed=false

    # Define command mappings for common packages
    declare -A package_commands=(
        ["librsvg2-bin"]="rsvg-convert"
        ["aspell"]="aspell"
        ["aspell-en"]="aspell"  # aspell-en doesn't add new commands
        ["git"]="git"
        ["curl"]="curl"
        ["wget"]="wget"
        ["build-essential"]="gcc"
        ["pkg-config"]="pkg-config"
    )

    for package in "${PACKAGES[@]}"; do
        local expected_command="${package_commands[$package]:-}"

        if [[ -n "$expected_command" ]]; then
            if command -v "$expected_command" >/dev/null 2>&1; then
                log_success "$package verified (command: $expected_command)"
            else
                log_error "$package verification failed (command not found: $expected_command)"
                verification_failed=true
            fi
        else
            # For packages without known commands, just check if they're installed
            if dpkg -l "$package" >/dev/null 2>&1; then
                log_success "$package verified (package installed)"
            else
                log_error "$package verification failed (package not found)"
                verification_failed=true
            fi
        fi
    done

    if [[ "$verification_failed" == "true" ]]; then
        log_error "Some package verifications failed"
        return 1
    else
        log_success "All packages verified successfully"
        return 0
    fi
}

# Clean up package cache (optional)
cleanup_cache() {
    if [[ "$VERBOSE" == "true" ]]; then
        log_info "Cleaning up package cache..."
        $SUDO_CMD apt-get clean >/dev/null 2>&1 || true
        log_verbose "Package cache cleaned"
    fi
}

# Main installation function
main() {
    log_info "=== APT Package Installation with Fallback ==="
    log_info "Requested packages: ${PACKAGES[*]}"

    # Pre-installation checks
    if ! check_apt_availability; then
        exit 1
    fi

    if ! check_permissions; then
        exit 1
    fi

    # Check existing packages
    if ! check_existing_packages; then
        # All packages already installed
        exit 0
    fi

    # Update package cache
    if ! update_package_cache; then
        log_warn "Package cache update failed, continuing with existing cache"
        # Don't exit, continue with installation
    fi

    # Install packages
    if ! install_packages; then
        log_error "Package installation failed"
        exit 1
    fi

    # Verify installation
    if ! verify_installation; then
        log_error "Package verification failed"
        exit 1
    fi

    # Cleanup
    cleanup_cache

    log_success "=== APT package installation completed successfully! ==="

    if [[ "$VERBOSE" == "true" ]]; then
        log_verbose "Installation summary:"
        for package in "${PACKAGES[@]}"; do
            local version=$(dpkg-query -W -f='${Version}' "$package" 2>/dev/null || echo "unknown")
            log_verbose "  $package: $version"
        done
    fi
}

# Trap errors for better debugging
trap 'log_error "Script failed at line $LINENO"' ERR

# Entry point
main "$@"
