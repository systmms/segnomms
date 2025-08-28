#!/bin/bash
# Script: repo/setup_cairo_macos.sh
# Purpose: Install Cairo graphics library on macOS with architecture detection
# Usage: ./setup_cairo_macos.sh [--verbose]
# GitHub Actions Integration: Used by .github/workflows/test.yml

set -euo pipefail

# Configuration
VERBOSE=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --verbose)
            VERBOSE=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--verbose]"
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

# Detect macOS architecture and set paths
detect_architecture() {
    local arch=$(uname -m)
    log_info "Detecting macOS architecture: $arch"

    if [[ "$arch" == "arm64" ]]; then
        # Apple Silicon (M1/M2) - Homebrew uses /opt/homebrew
        HOMEBREW_PREFIX="/opt/homebrew"
        PKG_CONFIG_PREFIX="/opt/homebrew"
        log_info "Detected Apple Silicon (ARM64) architecture"
    else
        # Intel Macs - Homebrew uses /usr/local
        HOMEBREW_PREFIX="/usr/local"
        PKG_CONFIG_PREFIX="/usr/local"
        log_info "Detected Intel (x86_64) architecture"
    fi

    # Set derived paths
    HOMEBREW_BIN="${HOMEBREW_PREFIX}/bin"
    PKG_CONFIG_PATH="${PKG_CONFIG_PREFIX}/lib/pkgconfig:${PKG_CONFIG_PREFIX}/share/pkgconfig"
    DYLD_LIBRARY_PATH="${PKG_CONFIG_PREFIX}/lib"

    log_verbose "Homebrew prefix: $HOMEBREW_PREFIX"
    log_verbose "PKG_CONFIG_PATH will be: $PKG_CONFIG_PATH"
    log_verbose "DYLD_LIBRARY_PATH will be: $DYLD_LIBRARY_PATH"
}

# Check if Homebrew is installed
check_homebrew() {
    log_info "Checking Homebrew installation..."

    if command -v brew >/dev/null 2>&1; then
        local brew_version=$(brew --version | head -n1)
        log_success "Homebrew is installed: $brew_version"
        return 0
    else
        log_error "Homebrew is not installed!"
        log_error "Please install Homebrew first: https://brew.sh"
        return 1
    fi
}

# Install Cairo and related libraries
install_cairo_packages() {
    log_info "Installing Cairo and related libraries via Homebrew..."

    local packages=(
        "cairo"
        "pkg-config"
        "gobject-introspection"
    )

    for package in "${packages[@]}"; do
        log_info "Installing $package..."
        if brew install "$package"; then
            log_success "$package installed successfully"
        else
            log_error "Failed to install $package"
            return 1
        fi
    done

    log_success "All Cairo packages installed successfully"
}

# Set environment variables for GitHub Actions
set_github_environment() {
    log_info "Setting environment variables for GitHub Actions..."

    # Extend existing PATH variables by appending to them
    local current_pkg_config_path="${PKG_CONFIG_PATH}:${PKG_CONFIG_PATH:-}"
    local current_dyld_library_path="${DYLD_LIBRARY_PATH}:${DYLD_LIBRARY_PATH:-}"

    # Set environment variables for GitHub Actions
    echo "PKG_CONFIG_PATH=${current_pkg_config_path}" >> "$GITHUB_ENV"
    echo "DYLD_LIBRARY_PATH=${current_dyld_library_path}" >> "$GITHUB_ENV"

    log_success "Environment variables set in GITHUB_ENV"

    if [[ "$VERBOSE" == "true" ]]; then
        log_verbose "PKG_CONFIG_PATH = ${current_pkg_config_path}"
        log_verbose "DYLD_LIBRARY_PATH = ${current_dyld_library_path}"
    fi
}

# Verify Cairo installation
verify_cairo_installation() {
    log_info "Verifying Cairo installation..."

    # Check if pkg-config can find Cairo
    if pkg-config --exists cairo; then
        local cairo_version=$(pkg-config --modversion cairo)
        log_success "Cairo verification successful"
        log_info "Cairo version: $cairo_version"

        if [[ "$VERBOSE" == "true" ]]; then
            log_verbose "Cairo compilation flags:"
            log_verbose "  CFLAGS: $(pkg-config --cflags cairo)"
            log_verbose "  LIBS: $(pkg-config --libs cairo)"
        fi

        return 0
    else
        log_error "Cairo verification failed - pkg-config cannot find Cairo"
        log_error "This might indicate an installation or PATH issue"
        return 1
    fi
}

# Run system update (optional but recommended)
update_homebrew() {
    log_info "Updating Homebrew (this may take a moment)..."

    if brew update; then
        log_success "Homebrew updated successfully"
    else
        log_warn "Homebrew update failed, continuing with existing version"
        # Don't fail the script for update issues
    fi
}

# Main installation function
main() {
    log_info "=== macOS Cairo Installation Script ==="
    log_info "Starting Cairo installation process..."

    # Step 1: Detect architecture and set paths
    detect_architecture

    # Step 2: Check Homebrew
    if ! check_homebrew; then
        log_error "Cannot proceed without Homebrew"
        exit 1
    fi

    # Step 3: Update Homebrew (optional)
    update_homebrew

    # Step 4: Install Cairo packages
    if ! install_cairo_packages; then
        log_error "Failed to install Cairo packages"
        exit 1
    fi

    # Step 5: Set environment variables
    set_github_environment

    # Step 6: Verify installation
    if ! verify_cairo_installation; then
        log_error "Cairo installation verification failed"
        exit 1
    fi

    log_success "=== Cairo installation completed successfully! ==="

    if [[ "$VERBOSE" == "true" ]]; then
        log_verbose "Installation summary:"
        log_verbose "  Architecture: $(uname -m)"
        log_verbose "  Homebrew prefix: $HOMEBREW_PREFIX"
        log_verbose "  Cairo version: $(pkg-config --modversion cairo)"
        log_verbose "  Installation path: $(brew --prefix cairo)"
    fi
}

# Trap errors for better debugging
trap 'log_error "Script failed at line $LINENO"' ERR

# Entry point
main "$@"
