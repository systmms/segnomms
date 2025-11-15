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


def test_import(import_statement: str) -> bool:
    """Test if an import statement works."""
    try:
        exec(import_statement, {})
        return True
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

    print("Testing imports:\n")
    for stmt, locations in sorted(unique_imports.items()):
        print(f"Testing: {stmt}")
        print(f"  Found in {len(locations)} location(s)")

        if test_import(stmt):
            print("  ✓ PASS")
            passed += 1
        else:
            print("  ❌ FAIL")
            for file_path, line in locations:
                print(f"    {file_path}:{line}")
            failed += 1
        print()

    # Summary
    print("=== Summary ===")
    print(f"Total unique imports: {len(unique_imports)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")

    if failed > 0:
        print(f"\n❌ {failed} import(s) failed")
        return 1
    else:
        print("\n✅ All imports passed!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
