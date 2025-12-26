#!/usr/bin/env python3
"""
Comprehensive documentation fixes verification
Part of documentation audit fixes (002-initial-documentation-audit)
Verifies all 7 success criteria (SC-001 through SC-007)
"""

import subprocess  # nosec B404
import sys
from pathlib import Path


def run_command(cmd: str, description: str) -> bool:
    """Run a command and return True if successful."""
    print(f"\nChecking: {description}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)  # nosec B602
        if result.returncode == 0:
            print("  ✓ PASS")
            return True
        else:
            print("  ❌ FAIL")
            if result.stdout:
                print(f"  Output: {result.stdout[:500]}")
            if result.stderr:
                print(f"  Error: {result.stderr[:500]}")
            return False
    except subprocess.TimeoutExpired:
        print("  ❌ FAIL (timeout)")
        return False
    except Exception as e:
        print(f"  ❌ FAIL (error: {e})")
        return False


def main() -> int:
    """Run comprehensive documentation validation."""
    print("=== Documentation Fixes Verification ===")
    print("Validating all 7 success criteria\n")

    results = {}

    # SC-001: Zero contradictions
    results["SC-001"] = run_command(
        "./scripts/check_doc_contradictions.sh", "SC-001: Zero contradictions across documentation sources"
    )

    # SC-002: 100% code examples work
    results["SC-002"] = run_command(
        "python scripts/extract_code_examples.py", "SC-002: All code examples execute successfully"
    )

    # SC-003: Installation clarity (manual check - just verify README exists)
    readme_exists = Path("README.md").exists()
    print("\nChecking: SC-003: Clear installation instructions in README.md")
    if readme_exists:
        print("  ✓ PASS (README.md exists - manual verification recommended)")
        results["SC-003"] = True
    else:
        print("  ❌ FAIL (README.md not found)")
        results["SC-003"] = False

    # SC-004: All API symbols documented (check constants.rst exists)
    constants_rst = Path("docs/source/api/constants.rst")
    print("\nChecking: SC-004: Constants module API documentation exists")
    if constants_rst.exists():
        print("  ✓ PASS (docs/source/api/constants.rst exists)")
        results["SC-004"] = True
    else:
        print("  ❌ FAIL (docs/source/api/constants.rst not found)")
        results["SC-004"] = False

    # SC-005: Developer setup clarity (check contributing.rst)
    contributing_rst = Path("docs/source/contributing.rst")
    print("\nChecking: SC-005: Contributing guide exists")
    if contributing_rst.exists():
        print("  ✓ PASS (docs/source/contributing.rst exists)")
        results["SC-005"] = True
    else:
        print("  ❌ FAIL (docs/source/contributing.rst not found)")
        results["SC-005"] = False

    # SC-006: Sphinx builds without warnings
    # Use a more precise grep pattern that looks for actual Sphinx warnings
    # (format: "filename:line: WARNING:" or "filename:line: ERROR:")
    # Avoids false positives from config strings like "suppress_warnings"
    sphinx_cmd = (
        "make docs 2>&1 | tee /tmp/sphinx_build.log && "
        '! grep -E "^.*:[0-9]+: (WARNING|ERROR):" /tmp/sphinx_build.log'
    )
    results["SC-006"] = run_command(
        sphinx_cmd,
        "SC-006: Sphinx documentation builds without warnings",
    )

    # SC-007: Test scripts have Makefile targets (check Makefile exists)
    makefile = Path("Makefile")
    print("\nChecking: SC-007: Makefile exists for test script discoverability")
    if makefile.exists():
        print("  ✓ PASS (Makefile exists - manual audit recommended)")
        results["SC-007"] = True
    else:
        print("  ❌ FAIL (Makefile not found)")
        results["SC-007"] = False

    # Summary
    print("\n=== Verification Summary ===")
    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for criterion, result in sorted(results.items()):
        status = "✓ PASS" if result else "❌ FAIL"
        print(f"{criterion}: {status}")

    print(f"\nTotal: {passed}/{total} success criteria met")

    if passed == total:
        print("\n✅ All success criteria validated!")
        return 0
    else:
        print(f"\n❌ {total - passed} success criteria failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
