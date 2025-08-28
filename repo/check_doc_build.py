#!/usr/bin/env python3
"""
Lightweight documentation build test for git hooks.

This script performs a quick syntax and build validation of Sphinx documentation
without generating full HTML output. Designed to be fast for git hooks.

Used by: lefthook pre-commit hook (optional)
"""

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path


def check_sphinx_availability() -> bool:
    """Check if Sphinx is available.

    Returns:
        True if Sphinx is available, False otherwise
    """
    try:
        import sphinx  # noqa: F401

        return True
    except ImportError:
        return False


def check_docs_syntax(docs_dir: Path, quiet: bool = False) -> bool:
    """Check documentation syntax using Sphinx.

    Args:
        docs_dir: Path to the documentation directory
        quiet: Reduce output verbosity

    Returns:
        True if syntax check passed, False otherwise
    """
    source_dir = docs_dir / "source"
    if not source_dir.exists():
        if not quiet:
            print(f"❌ Documentation source directory not found: {source_dir}")
        return False

    # Use temporary directory for build output
    with tempfile.TemporaryDirectory() as temp_dir:
        build_dir = Path(temp_dir) / "build"

        try:
            # Run Sphinx in syntax check mode (no output generation)
            # Don't use -W (warnings as errors) for git hooks - too strict
            cmd = [
                "python",
                "-m",
                "sphinx",
                "-b",
                "dummy",  # Use dummy builder (syntax check only)
                "-E",  # Don't use cached environment (force fresh build)
                "-q" if quiet else "-v",  # Quiet or verbose
                str(source_dir),
                str(build_dir),
            ]

            if not quiet:
                print("🔍 Running Sphinx syntax validation...")

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)  # 30 second timeout

            if result.returncode == 0:
                if not quiet:
                    print("✅ Documentation syntax validation passed!")
                return True
            else:
                print("❌ Documentation syntax validation failed:")
                if result.stderr:
                    print("Errors:")
                    print(result.stderr)
                if result.stdout:
                    print("Output:")
                    print(result.stdout)
                return False

        except subprocess.TimeoutExpired:
            print("⚠️  Documentation build test timed out (30s)")
            return False
        except Exception as e:
            print(f"⚠️  Error during documentation build test: {e}")
            return False


def main() -> int:
    """Main function for documentation build test.

    Returns:
        Exit code: 0 for success, 1 for failure or missing dependencies
    """
    parser = argparse.ArgumentParser(description="Quick documentation build syntax validation for git hooks")
    parser.add_argument("--docs-dir", type=Path, help="Documentation directory (default: docs/)")
    parser.add_argument("--quiet", action="store_true", help="Reduce output verbosity")
    parser.add_argument(
        "--skip-if-missing-deps",
        action="store_true",
        help="Skip test if Sphinx dependencies are missing (for optional use in git hooks)",
    )

    args = parser.parse_args()

    # Determine docs directory
    if args.docs_dir:
        docs_dir = args.docs_dir
    else:
        # Default: docs/ relative to project root
        project_root = Path(__file__).parent.parent
        docs_dir = project_root / "docs"

    if not args.quiet:
        print("📖 Documentation Build Test")
        print("=" * 28)

    # Check if Sphinx is available
    if not check_sphinx_availability():
        if args.skip_if_missing_deps:
            if not args.quiet:
                print("⏭️  Skipping documentation build test (Sphinx not installed)")
                print("   💡 Install documentation dependencies: uv sync --extra docs")
            return 0  # Skip, don't fail
        else:
            print("❌ Sphinx not found. Install documentation dependencies:")
            print("   • uv sync --extra docs")
            print("   • pip install sphinx sphinx-rtd-theme myst-parser")
            return 1

    if not docs_dir.exists():
        print(f"❌ Documentation directory not found: {docs_dir}")
        return 1

    if not args.quiet:
        print(f"📁 Documentation directory: {docs_dir}")

    # Run syntax check
    if check_docs_syntax(docs_dir, args.quiet):
        if not args.quiet:
            print("=" * 28)
            print("✅ Documentation build test passed!")
        return 0
    else:
        if not args.quiet:
            print("=" * 28)
            print("❌ Documentation build test failed!")
            print("💡 Fix syntax errors before committing documentation changes")
        return 1


if __name__ == "__main__":
    sys.exit(main())
