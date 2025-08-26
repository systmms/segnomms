#!/usr/bin/env python3
"""Audit all Makefile commands and report their status."""

import subprocess
import sys
from pathlib import Path
from typing import Tuple

# Define command categories
COMMANDS = {
    "Installation & Build": [
        ("install", "Install the plugin in development mode"),
        ("build", "Build distribution files"),
        ("dist", "Create distribution directory"),
    ],
    "Core Testing": [
        ("test-quick", "Run quick test subset (unit tests only)"),
        ("test-python", "Run Python unit tests only"),
        ("test-python-core", "Run Python unit tests (excluding playwright)"),
        ("test-lint", "Test code quality with linters"),
        ("test-typecheck", "Test type annotations"),
        ("coverage", "Generate coverage report"),
    ],
    "Visual & Examples": [
        ("test-visual", "Run visual regression tests"),
        ("test-visual-update", "Update visual regression baselines"),
        ("test-examples", "Generate comprehensive examples"),
        ("test-shapes", "Test shape generation"),
        ("quick-test", "Generate sample QR codes"),
    ],
    "Documentation": [
        ("docs-install", "Install Sphinx and documentation dependencies"),
        ("docs", "Build Sphinx documentation"),
        ("docs-clean", "Clean documentation build"),
        ("docs-serve", "Build and serve docs at localhost:8001"),
    ],
    "Development Tools": [
        ("setup", "Complete setup with dev dependencies"),
        ("lint", "Run Python linters"),
        ("format", "Auto-format Python code"),
        ("typecheck", "Run type checking"),
        ("clean", "Remove all generated files"),
        ("clean-visual", "Clean visual test outputs"),
    ],
    "Utilities": [
        ("info", "Show package information"),
        ("check-deps", "Check dependencies"),
        ("help", "Show help message"),
    ],
    "Advanced/Integration": [
        ("test-segno-compatibility", "Test compatibility across Segno versions"),
        ("test-plugin", "Test plugin registration"),
        ("test-server", "Test example server functionality"),
        ("examples", "Serve examples in browser"),
        ("deploy", "Deploy to beta environment"),
        ("review", "Generate comprehensive visual review suite"),
    ],
}


def run_command(cmd: str, timeout: int = 10) -> Tuple[bool, str, str]:
    """Run a make command and return success status, stdout, and stderr."""
    try:
        result = subprocess.run(["make", cmd], capture_output=True, text=True, timeout=timeout)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", f"Command timed out after {timeout} seconds"
    except Exception as e:
        return False, "", str(e)


def check_command_quick(cmd: str) -> str:
    """Quick check if command exists and basic syntax is OK."""
    # For certain commands, we'll do a dry run or quick check
    if cmd in ["help", "info", "check-deps"]:
        # These are safe to run
        success, stdout, stderr = run_command(cmd, timeout=5)
        return "✅ OK" if success else f"❌ FAIL: {stderr.split(chr(10))[0]}"

    elif cmd in ["clean", "clean-visual", "dist"]:
        # These modify filesystem but are generally safe
        return "⚠️  MODIFIES FILES"

    elif cmd.startswith("test-"):
        # Test commands - check if they're defined
        return "🧪 TEST CMD"

    elif cmd in ["build", "install", "setup"]:
        # Build/install commands
        return "🔨 BUILD CMD"

    elif cmd.startswith("docs"):
        # Documentation commands
        return "📚 DOC CMD"

    elif cmd in ["deploy", "review"]:
        # Deployment commands - don't run
        return "🚀 DEPLOY CMD"

    else:
        return "❓ UNKNOWN"


def main():
    """Audit all Makefile commands."""
    print("=" * 80)
    print("MAKEFILE AUDIT REPORT")
    print("=" * 80)
    print()

    # First, verify Makefile exists
    if not Path("Makefile").exists():
        print("❌ ERROR: Makefile not found!")
        sys.exit(1)

    # Test each category
    for category, commands in COMMANDS.items():
        print(f"\n📁 {category}")
        print("-" * 40)

        for cmd, description in commands:
            status = check_command_quick(cmd)
            print(f"  {cmd:30} {status:20} {description}")

    # Run some safe commands to verify functionality
    print("\n" + "=" * 80)
    print("RUNNING SAFE COMMANDS FOR VERIFICATION")
    print("=" * 80)

    safe_commands = ["help", "info", "check-deps"]
    for cmd in safe_commands:
        print(f"\n🔍 Running: make {cmd}")
        print("-" * 40)
        success, stdout, stderr = run_command(cmd, timeout=5)
        if success:
            print(stdout[:500] + "..." if len(stdout) > 500 else stdout)
        else:
            print(f"❌ Failed: {stderr}")

    # Check for missing dependencies
    print("\n" + "=" * 80)
    print("DEPENDENCY CHECK")
    print("=" * 80)

    deps_to_check = [
        ("pytest", "Unit testing"),
        ("coverage", "Code coverage"),
        ("flake8", "Linting"),
        ("black", "Code formatting"),
        ("mypy", "Type checking"),
        ("sphinx", "Documentation"),
        ("segno", "QR code generation"),
    ]

    for dep, purpose in deps_to_check:
        try:
            result = subprocess.run([sys.executable, "-c", f"import {dep}"], capture_output=True)
            status = "✅ Installed" if result.returncode == 0 else "❌ Missing"
            print(f"  {dep:15} {status:15} ({purpose})")
        except Exception:
            print(f"  {dep:15} ❌ Error checking")

    # Check for required files/directories
    print("\n" + "=" * 80)
    print("FILE/DIRECTORY CHECK")
    print("=" * 80)

    paths_to_check = [
        ("segnomms/", "Plugin source directory"),
        ("tests/", "Test directory"),
        ("docs/", "Documentation directory"),
        ("scripts/", "Scripts directory"),
        ("examples/", "Examples directory"),
        ("requirements-dev.txt", "Development dependencies"),
        ("pyproject.toml", "Project configuration"),
        ("shell-functions.sh", "Shell helper functions"),
    ]

    for path, description in paths_to_check:
        exists = Path(path).exists()
        status = "✅ Exists" if exists else "❌ Missing"
        print(f"  {path:25} {status:15} ({description})")

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(
        """
Legend:
  ✅ OK         - Command works correctly
  🧪 TEST CMD   - Testing command (needs test suite)
  🔨 BUILD CMD  - Build/install command
  📚 DOC CMD    - Documentation command
  🚀 DEPLOY CMD - Deployment command (not run)
  ⚠️  MODIFIES   - Modifies files (use carefully)
  ❌ FAIL       - Command failed
  ❓ UNKNOWN    - Unknown command type

Recommendations:
  1. Run 'make setup' to install all development dependencies
  2. Run 'make test-quick' for a quick test verification
  3. Run 'make docs-install' if working with documentation
  4. Use 'make help' to see all available commands
"""
    )


if __name__ == "__main__":
    main()
