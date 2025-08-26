#!/usr/bin/env python3
"""Test code examples from README.md for documentation validation.

This script extracts Python code blocks from README.md and validates that they
execute successfully, ensuring that documentation examples remain current and functional.
"""

import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path


def extract_python_code_blocks(readme_path: str) -> list[str]:
    """Extract Python code blocks from README.md.

    Args:
        readme_path: Path to the README.md file

    Returns:
        List of Python code block contents
    """
    try:
        with open(readme_path, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"❌ README.md not found at {readme_path}")
        return []

    # Extract Python code blocks using proper regex pattern
    code_blocks = re.findall(r"```python\n(.*?)\n```", content, re.DOTALL)
    return code_blocks


def test_code_block(code: str, block_number: int) -> bool:
    """Test a single Python code block.

    Args:
        code: Python code to test
        block_number: Block number for reporting

    Returns:
        True if code executes successfully, False otherwise
    """
    print(f"Testing code block {block_number}...")

    # Skip blocks that are just imports or incomplete examples
    if "import" in code and len(code.strip().split("\n")) < 3:
        print(f"  Skipping import-only block {block_number}")
        return True

    # Create temporary file for the code
    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            temp_file = f.name

        # Execute the code with timeout
        result = subprocess.run([sys.executable, temp_file], capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            print(f"  ✅ Code block {block_number} executed successfully")
            return True
        else:
            print(f"  ❌ Code block {block_number} failed:")
            # Show first few lines of error for debugging
            error_lines = result.stderr.strip().split("\n")[:3]
            for line in error_lines:
                print(f"     {line}")
            return False

    except subprocess.TimeoutExpired:
        print(f"  ⏰ Code block {block_number} timed out")
        return False
    except Exception as e:
        print(f"  ❌ Code block {block_number} error: {e}")
        return False
    finally:
        # Clean up temporary file
        if "temp_file" in locals():
            try:
                os.unlink(temp_file)
            except OSError:
                pass


def main() -> int:
    """Main function to test all README examples.

    Returns:
        Exit code: 0 for success, 1 for failures
    """
    print("📖 Testing README.md Code Examples")
    print("=" * 40)

    # Find README.md (should be in project root)
    readme_path = Path(__file__).parent.parent / "README.md"

    if not readme_path.exists():
        print(f"❌ README.md not found at {readme_path}")
        return 1

    # Extract code blocks
    code_blocks = extract_python_code_blocks(str(readme_path))

    if not code_blocks:
        print("⚠️  No Python code blocks found in README.md")
        return 0

    print(f"Found {len(code_blocks)} Python code blocks in README")
    print()

    # Test each code block
    success_count = 0
    total_count = len(code_blocks)

    for i, code in enumerate(code_blocks, 1):
        if test_code_block(code, i):
            success_count += 1
        print()  # Add spacing between blocks

    # Report results
    print("=" * 40)
    print(f"📊 Results: {success_count}/{total_count} code blocks passed")

    if success_count == total_count:
        print("✅ All README examples are working!")
        return 0
    else:
        failed_count = total_count - success_count
        print(f"❌ {failed_count} README examples need attention")
        return 1


if __name__ == "__main__":
    sys.exit(main())
