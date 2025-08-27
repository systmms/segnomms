#!/usr/bin/env python3
"""
Check documentation dependencies are properly installed.

This script verifies that all required documentation dependencies
(Sphinx, themes, etc.) are available and functioning correctly.

Used by GitHub Actions workflow to validate documentation build environment.
"""

import sys


def main():
    """Check documentation dependencies."""
    print("🔍 Checking documentation dependencies...")

    try:
        import sphinx

        print(f"   ✅ Sphinx: {sphinx.__version__}")
    except ImportError as e:
        print(f"   ❌ Sphinx not found: {e}")
        return False

    try:
        import sphinx_rtd_theme  # noqa: F401

        print("   ✅ Read the Docs theme: Available")
    except ImportError as e:
        print(f"   ❌ Read the Docs theme not found: {e}")
        return False

    try:
        import myst_parser  # noqa: F401

        print("   ✅ MyST Parser: Available")
    except ImportError as e:
        print(f"   ❌ MyST Parser not found: {e}")
        return False

    print("✅ Documentation dependencies installed successfully")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
