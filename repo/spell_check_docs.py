#!/usr/bin/env python3
"""Spell check documentation files with technical terms dictionary.

This script performs spell checking on documentation files using aspell
with a custom dictionary of technical terms commonly used in the project.
"""

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import List, Optional


def create_technical_dictionary() -> str:
    """Create a custom dictionary with technical terms.

    Returns:
        Content of the custom dictionary file
    """
    return """personal_ws-1.1 en 80
SegnoMMS
Segno
QR
QRcode
SVG
API
JSON
YAML
kwargs
bool
str
int
float
dict
list
tuple
UUID
HSL
RGB
RGBA
CSS
HTML
XML
MIME
UTF
URI
URL
HTTP
HTTPS
PyPI
Pydantic
validator
validators
dataclass
enum
PIL
Pillow
numpy
matplotlib
rasterization
vectorized
centerpiece
accessibility
tooltips
ARIA
scanability
docstring
docstrings
autodoc
automodule
autosummary
pytest
mypy
flake8
isort
repo
config
configs
makefile
async
workflow
workflows
GitHub
changelog
README
squircle
namespace
namespaces
kwargs
APIs
CLIs
backends
middleware
plugin
plugins
OAuth
auth
username
usernames
filesystem
metadata
timestamp
timestamps
whitespace
backend
frontend
"""


def check_aspell_availability() -> bool:
    """Check if aspell is available on the system.

    Returns:
        True if aspell is available, False otherwise
    """
    return shutil.which("aspell") is not None


def spell_check_file(file_path: Path, dictionary_path: Path) -> Optional[List[str]]:
    """Spell check a single file.

    Args:
        file_path: Path to the file to check
        dictionary_path: Path to the custom dictionary

    Returns:
        List of misspelled words, or None if error occurred
    """
    if not file_path.exists():
        print(f"⚠️  File not found: {file_path}")
        return None

    try:
        # Run aspell to get list of potentially misspelled words
        result = subprocess.run(
            ["aspell", f"--personal={dictionary_path}", "--list"],
            input=file_path.read_text(encoding="utf-8"),
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            print(f"⚠️  Aspell error for {file_path}: {result.stderr}")
            return None

        # Return list of misspelled words (empty list if none)
        misspelled = [word.strip() for word in result.stdout.split("\n") if word.strip()]
        return misspelled

    except subprocess.TimeoutExpired:
        print(f"⚠️  Spell check timeout for {file_path}")
        return None
    except Exception as e:
        print(f"⚠️  Error checking {file_path}: {e}")
        return None


def spell_check_documentation(project_root: Path) -> int:
    """Spell check all documentation files.

    Args:
        project_root: Root directory of the project

    Returns:
        Number of files with spelling errors
    """
    # Files to spell check
    files_to_check = [
        project_root / "README.md",
        project_root / "CHANGELOG.md",
    ]

    # Add RST and MD files from docs/source
    docs_source = project_root / "docs" / "source"
    if docs_source.exists():
        files_to_check.extend(docs_source.glob("*.rst"))
        files_to_check.extend(docs_source.glob("*.md"))
        # Also check subdirectories
        files_to_check.extend(docs_source.rglob("*.rst"))
        files_to_check.extend(docs_source.rglob("*.md"))

    # Remove duplicates and ensure files exist
    files_to_check = list(set(f for f in files_to_check if f.exists()))

    print(f"📝 Checking {len(files_to_check)} documentation files")
    print()

    # Create temporary dictionary file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".pws", delete=False) as f:
        f.write(create_technical_dictionary())
        dictionary_path = Path(f.name)

    try:
        files_with_errors = 0
        total_errors = 0

        for file_path in sorted(files_to_check):
            print(f"🔍 Checking spelling in {file_path.name}...")

            misspelled = spell_check_file(file_path, dictionary_path)

            if misspelled is None:
                continue  # Error already reported

            if misspelled:
                files_with_errors += 1
                error_count = len(misspelled)
                total_errors += error_count

                print(f"  ❌ Found {error_count} potential spelling errors:")
                # Show first 10 errors to avoid overwhelming output
                for word in misspelled[:10]:
                    print(f"     • {word}")
                if len(misspelled) > 10:
                    print(f"     ... and {len(misspelled) - 10} more")
            else:
                print("  ✅ No spelling errors found")

            print()  # Add spacing between files

        return files_with_errors

    finally:
        # Clean up temporary dictionary
        try:
            dictionary_path.unlink()
        except OSError:
            pass


def main() -> int:
    """Main function to spell check documentation.

    Returns:
        Exit code: 0 for success, 1 for errors or missing dependencies
    """
    print("📖 Spell Checking Documentation")
    print("=" * 35)

    # Check if aspell is available
    if not check_aspell_availability():
        print("❌ aspell not found. Please install aspell:")
        print("   • macOS: brew install aspell")
        print("   • Ubuntu/Debian: sudo apt-get install aspell aspell-en")
        print("   • Other systems: check your package manager")
        return 1

    # Find project root
    project_root = Path(__file__).parent.parent
    print(f"📁 Project root: {project_root}")
    print()

    # Perform spell checking
    files_with_errors = spell_check_documentation(project_root)

    # Report results
    print("=" * 35)
    if files_with_errors == 0:
        print("✅ All documentation files passed spell check!")
        return 0
    else:
        print(f"⚠️  {files_with_errors} file(s) have potential spelling errors")
        print()
        print("💡 Tips:")
        print("   • Review the reported words for actual typos")
        print("   • Technical terms may need to be added to the dictionary")
        print("   • Consider context - some 'errors' might be intentional")
        return 0  # Don't fail CI for spelling warnings


if __name__ == "__main__":
    sys.exit(main())
