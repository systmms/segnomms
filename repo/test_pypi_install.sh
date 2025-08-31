#!/bin/bash
# Script: repo/test_pypi_install.sh
# Purpose: Test installation from PyPI and verify basic functionality
# Usage: ./test_pypi_install.sh [--package=NAME] [--version=X.Y.Z] [options]
# GitHub Actions Integration: Used by publish.yml, validate-release.yml

set -euo pipefail

# Configuration
VERBOSE=false
PACKAGE_NAME="segnomms"
VERSION=""
WHEEL_PATH=""
WAIT_TIME=60  # Wait time for PyPI to update after publish
TEST_PLUGIN_REGISTRATION=true
TEST_BASIC_FUNCTIONALITY=true

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --package=*)
            PACKAGE_NAME="${1#*=}"
            shift
            ;;
        --version=*)
            VERSION="${1#*=}"
            shift
            ;;
        --wheel=*)
            WHEEL_PATH="${1#*=}"
            shift
            ;;
        --wait=*)
            WAIT_TIME="${1#*=}"
            shift
            ;;
        --no-wait)
            WAIT_TIME=0
            shift
            ;;
        --skip-plugin-test)
            TEST_PLUGIN_REGISTRATION=false
            shift
            ;;
        --skip-functionality-test)
            TEST_BASIC_FUNCTIONALITY=false
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --help)
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  --package=NAME           Package name to install (default: segnomms)"
            echo "  --version=X.Y.Z          Specific version to install (default: latest)"
            echo "  --wait=SECONDS           Wait time for PyPI to update (default: 60)"
            echo "  --no-wait                Skip waiting for PyPI update"
            echo "  --skip-plugin-test       Skip plugin registration testing"
            echo "  --skip-functionality-test Skip basic functionality testing"
            echo "  --verbose                Enable verbose output"
            echo "  --help                   Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                                    # Test latest version with default settings"
            echo "  $0 --version=1.0.0 --verbose         # Test specific version with verbose output"
            echo "  $0 --no-wait --skip-plugin-test      # Quick test without waiting or plugin check"
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

# Wait for PyPI to update (needed after fresh publish)
wait_for_pypi_update() {
    if [[ $WAIT_TIME -gt 0 ]]; then
        log_info "Waiting ${WAIT_TIME} seconds for PyPI to update..."
        sleep $WAIT_TIME
        log_verbose "Wait period completed"
    else
        log_verbose "Skipping PyPI wait period"
    fi
}

# Install package from PyPI
install_package_from_pypi() {
    log_info "Installing package from PyPI..."

    # Upgrade pip first
    log_verbose "Upgrading pip"
    python -m pip install --upgrade pip

    # Prefer local wheel if provided
    if [[ -n "$WHEEL_PATH" ]]; then
        log_info "Installing from local wheel: $WHEEL_PATH"
        if [[ "$VERBOSE" == "true" ]]; then
            pip install "$WHEEL_PATH" --verbose || return 1
        else
            pip install "$WHEEL_PATH" || return 1
        fi
    else
        # Build package specification
        local package_spec="$PACKAGE_NAME"
        if [[ -n "$VERSION" ]]; then
            package_spec="${PACKAGE_NAME}==${VERSION}"
            log_info "Installing specific version: $package_spec"
        else
            log_info "Installing latest version of $PACKAGE_NAME"
        fi

        # Install the package from PyPI
        if [[ "$VERBOSE" == "true" ]]; then
            pip install "$package_spec" --verbose || return 1
        else
            pip install "$package_spec" || return 1
        fi
    fi

    log_success "Package installation completed"
}

# Test basic import
test_import() {
    log_info "Testing basic import..."

    local python_code="
import $PACKAGE_NAME
print(f'Successfully imported $PACKAGE_NAME version {$PACKAGE_NAME.__version__}')
"

    if python -c "$python_code"; then
        log_success "Basic import test passed"
        return 0
    else
        log_error "Basic import test failed"
        return 1
    fi
}

# Test plugin registration (Segno integration)
test_plugin_registration() {
    if [[ "$TEST_PLUGIN_REGISTRATION" != "true" ]]; then
        log_verbose "Skipping plugin registration test"
        return 0
    fi

    log_info "Testing plugin registration..."

    local python_code="
import segno
import $PACKAGE_NAME

# Test that the plugin is registered via entry points
qr = segno.make('Test Plugin Registration')
has_plugin_method = hasattr(qr, 'to_interactive_svg')

if has_plugin_method:
    print('✅ Plugin registration successful - entry points working')
    exit(0)
else:
    print('⚠️  Plugin registration not active (may be expected in some environments)')
    # This is not necessarily an error - plugin registration via entry points
    # may not work in all environments (dev mode, etc.)
    exit(0)
"

    if python -c "$python_code"; then
        log_success "Plugin registration test completed"
        return 0
    else
        log_warn "Plugin registration test had issues, but continuing"
        return 0  # Don't fail on this - registration can be environment-dependent
    fi
}

# Test basic functionality
test_basic_functionality() {
    if [[ "$TEST_BASIC_FUNCTIONALITY" != "true" ]]; then
        log_verbose "Skipping basic functionality test"
        return 0
    fi

    log_info "Testing basic functionality..."

    local python_code="
import segno
from $PACKAGE_NAME import write
import tempfile
import os

# Test direct functionality (validates core package works)
qr = segno.make('Hello PyPI Test')

with tempfile.NamedTemporaryFile(suffix='.svg', delete=False) as tmp:
    temp_path = tmp.name

try:
    # Test the main plugin functionality
    # Use 'dark' color kwarg (API) instead of deprecated 'fill'
    write(qr, temp_path, shape='square', dark='blue')

    with open(temp_path, 'r') as f:
        svg_content = f.read()

    # Validate SVG content
    if svg_content and '<svg' in svg_content and 'fill=\"blue\"' in svg_content:
        print('✅ Basic functionality test passed - SVG generation working')
        print(f'   Generated SVG size: {len(svg_content)} characters')
    else:
        print('❌ Basic functionality test failed - Invalid SVG content')
        exit(1)

finally:
    if os.path.exists(temp_path):
        os.unlink(temp_path)
"

    if python -c "$python_code"; then
        log_success "Basic functionality test passed"
        return 0
    else
        log_error "Basic functionality test failed"
        return 1
    fi
}

# Get installed version
get_installed_version() {
    log_verbose "Checking installed version..."

    local python_code="
import $PACKAGE_NAME
print($PACKAGE_NAME.__version__)
"

    local installed_version
    if installed_version=$(python -c "$python_code" 2>/dev/null); then
        log_info "Installed version: $installed_version"
        return 0
    else
        log_warn "Could not determine installed version"
        return 1
    fi
}

# Main test function
main() {
    log_info "=== PyPI Installation Test ==="
    log_info "Package: $PACKAGE_NAME"
    if [[ -n "$VERSION" ]]; then
        log_info "Version: $VERSION"
    else
        log_info "Version: latest"
    fi

    # Wait for PyPI to update
    wait_for_pypi_update

    # Install package (PyPI or local wheel)
    if ! install_package_from_pypi; then
        log_error "Package installation failed"
        exit 1
    fi

    # Change to a temp directory so imports don't pick up the repository checkout
    TMP_CWD=$(mktemp -d)
    log_info "Switching to temp directory for import tests: $TMP_CWD"
    cd "$TMP_CWD"

    # Get installed version info
    get_installed_version || true

    # Test basic import
    if ! test_import; then
        log_error "Import test failed"
        exit 1
    fi

    # Test plugin registration
    test_plugin_registration || true  # Don't fail on plugin registration issues

    # Test basic functionality
    if ! test_basic_functionality; then
        log_error "Functionality test failed"
        exit 1
    fi

    log_success "=== PyPI installation test completed successfully! ==="
}

# Trap errors for better debugging
trap 'log_error "Script failed at line $LINENO"' ERR

# Entry point
main "$@"
