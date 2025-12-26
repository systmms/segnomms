#!/usr/bin/env python3
"""
Extract and test code examples from documentation
Part of documentation audit fixes (002-initial-documentation-audit)
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple


def extract_python_imports(file_path: Path) -> List[Tuple[int, str]]:
    """Extract all Python import statements from a file."""
    imports = []

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Match import statements in code blocks
    # Look for .. code-block:: python followed by import statements
    code_blocks = re.findall(
        r"```python(.*?)```|.. code-block:: python(.*?)(?=\n\S|\n\n\S|\Z)", content, re.DOTALL
    )

    line_num = 1
    for markdown_block, rst_block in code_blocks:
        block = markdown_block if markdown_block else rst_block
        if block:
            # Extract import lines
            for line in block.split("\n"):
                stripped = line.strip()
                if stripped.startswith(("from ", "import ")):
                    imports.append((line_num, stripped))
                line_num += 1

    return imports


# Optional dependencies used in documentation examples
# These are framework integrations that readers should install separately
OPTIONAL_DEPENDENCIES = frozenset(
    {
        "django",
        "fastapi",
        "flask",
        "starlette",
        "uvicorn",
        "pydub",  # Audio processing
        "qrcode",  # Alternative QR library
        "pyzbar",  # QR code decoder library
    }
)


def is_optional_import(import_statement: str) -> bool:
    """Check if import is for an optional framework dependency."""
    # Extract module name from import statement
    # "from django.http import HttpResponse" -> "django"
    # "import fastapi" -> "fastapi"
    stmt = import_statement.lower()
    if stmt.startswith("from "):
        module = stmt.split()[1].split(".")[0]
    elif stmt.startswith("import "):
        module = stmt.split()[1].split(".")[0].split(",")[0]
    else:
        return False
    return module in OPTIONAL_DEPENDENCIES


def is_incomplete_import(import_statement: str) -> bool:
    """Check if import statement is incomplete (multiline continuation)."""
    # Incomplete if ends with ( or , or \ without closing
    stripped = import_statement.strip()
    if stripped.endswith(("(", ",", "\\")):
        return True
    # Incomplete if has unbalanced parentheses
    if stripped.count("(") > stripped.count(")"):
        return True
    return False


def test_import(import_statement: str) -> bool:
    """Test if an import statement works."""
    try:
        # Using exec to dynamically test Python import statements
        exec(import_statement, {})  # noqa: S102 - exec needed for dynamic import testing
        return True
    except SyntaxError as e:
        print(f"  Error (syntax): {e}")
        return False
    except Exception as e:
        print(f"  Error: {e}")
        return False


def main() -> int:
    """Extract and test all imports from documentation."""
    docs_dir = Path("docs/source")
    readme = Path("README.md")

    if not docs_dir.exists():
        print("Error: docs/source directory not found")
        sys.exit(1)

    print("=== Code Example Extraction and Testing ===\n")

    all_imports = []
    files_checked = []

    # Check Sphinx docs
    for rst_file in docs_dir.rglob("*.rst"):
        imports = extract_python_imports(rst_file)
        if imports:
            all_imports.extend([(rst_file, line, stmt) for line, stmt in imports])
            files_checked.append(rst_file)

    # Check README
    if readme.exists():
        imports = extract_python_imports(readme)
        if imports:
            all_imports.extend([(readme, line, stmt) for line, stmt in imports])
            files_checked.append(readme)

    print(f"Files checked: {len(files_checked)}")
    print(f"Import statements found: {len(all_imports)}\n")

    if not all_imports:
        print("No import statements found in documentation")
        return 0

    # Test each unique import
    unique_imports: Dict[str, List[Tuple[Path, int]]] = {}
    for file_path, line, stmt in all_imports:
        if stmt not in unique_imports:
            unique_imports[stmt] = []
        unique_imports[stmt].append((file_path, line))

    passed = 0
    failed = 0
    skipped_optional = 0
    skipped_incomplete = 0
    skipped_tests = 0

    print("Testing imports:\n")
    for stmt, locations in sorted(unique_imports.items()):
        print(f"Testing: {stmt}")
        print(f"  Found in {len(locations)} location(s)")

        if is_incomplete_import(stmt):
            print("  ⊘ SKIP (incomplete multiline import)")
            skipped_incomplete += 1
        elif is_optional_import(stmt):
            print("  ⊘ SKIP (optional framework dependency)")
            skipped_optional += 1
        elif stmt.startswith("from tests."):
            print("  ⊘ SKIP (internal test helper)")
            skipped_tests += 1
        elif test_import(stmt):
            print("  ✓ PASS")
            passed += 1
        else:
            print("  ❌ FAIL")
            for file_path, line in locations:
                print(f"    {file_path}:{line}")
            failed += 1
        print()

    # Summary
    total_skipped = skipped_optional + skipped_incomplete + skipped_tests
    print("=== Summary ===")
    print(f"Total unique imports: {len(unique_imports)}")
    print(f"Passed: {passed}")
    print(f"Skipped: {total_skipped}")
    if skipped_optional > 0:
        print(f"  - Optional framework dependencies: {skipped_optional}")
    if skipped_incomplete > 0:
        print(f"  - Incomplete multiline imports: {skipped_incomplete}")
    if skipped_tests > 0:
        print(f"  - Internal test helpers: {skipped_tests}")
    print(f"Failed: {failed}")

    if failed > 0:
        print(f"\n❌ {failed} import(s) failed")
        return 1
    else:
        print("\n✅ All required imports passed!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
