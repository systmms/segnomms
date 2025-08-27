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

    dependencies_status = []
    overall_success = True

    # Check Sphinx
    try:
        import sphinx

        print(f"   ✅ Sphinx: {sphinx.__version__}")
        dependencies_status.append(("Sphinx", True, sphinx.__version__))
    except ImportError as e:
        print(f"   ❌ Sphinx not found: {e}")
        print("   💡 Install with: uv pip install -r docs/requirements.txt")
        dependencies_status.append(("Sphinx", False, str(e)))
        overall_success = False

    # Check Read the Docs theme
    try:
        import sphinx_rtd_theme  # noqa: F401

        print("   ✅ Read the Docs theme: Available")
        dependencies_status.append(("sphinx_rtd_theme", True, "Available"))
    except ImportError as e:
        print(f"   ❌ Read the Docs theme not found: {e}")
        print("   💡 Install with: uv pip install sphinx-rtd-theme")
        dependencies_status.append(("sphinx_rtd_theme", False, str(e)))
        overall_success = False

    # Check MyST Parser
    try:
        import myst_parser  # noqa: F401

        print("   ✅ MyST Parser: Available")
        dependencies_status.append(("myst_parser", True, "Available"))
    except ImportError as e:
        print(f"   ❌ MyST Parser not found: {e}")
        print("   💡 Install with: uv pip install myst-parser")
        dependencies_status.append(("myst_parser", False, str(e)))
        overall_success = False

    # Print summary
    print()
    if overall_success:
        print("✅ All documentation dependencies installed successfully")
        print(f"   📊 Dependencies checked: {len(dependencies_status)}")
    else:
        failed_deps = [name for name, status, _ in dependencies_status if not status]
        print(f"❌ {len(failed_deps)} dependencies missing: {', '.join(failed_deps)}")
        print("   🛠️  Run: uv pip install -r docs/requirements.txt")

    return overall_success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
