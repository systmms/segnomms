#!/usr/bin/env python3
"""Spell check documentation files with technical terms dictionary.

This script performs spell checking on documentation files using aspell
with a custom dictionary of technical terms commonly used in the project.
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List, Optional


def get_project_dictionary_path(project_root: Path) -> Path:
    """Get the path to the project-specific aspell dictionary.

    Args:
        project_root: Root directory of the project

    Returns:
        Path to the project dictionary file
    """
    return project_root / "repo" / "aspell_project_dict.txt"


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

    if not dictionary_path.exists():
        print(f"⚠️  Dictionary not found: {dictionary_path}")
        return None

    try:
        # Run aspell to get list of potentially misspelled words
        # Use --add-extra-dicts to include project dictionary alongside system dictionary
        result = subprocess.run(
            ["aspell", f"--add-extra-dicts={dictionary_path}", "--list"],
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


def spell_check_documentation(project_root: Path, specific_files: Optional[List[Path]] = None) -> int:
    """Spell check documentation files.

    Args:
        project_root: Root directory of the project
        specific_files: Optional list of specific files to check (for git hooks)

    Returns:
        Number of files with spelling errors
    """
    if specific_files:
        # Use the specific files provided (for git hooks)
        files_to_check = [f for f in specific_files if f.exists()]
    else:
        # Default: check all documentation files
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

    # Get project dictionary path
    dictionary_path = get_project_dictionary_path(project_root)
    if not dictionary_path.exists():
        print(f"⚠️  Project dictionary not found: {dictionary_path}")
        print("   Proceeding with system dictionary only")
        dictionary_path = None

    files_with_errors = 0
    total_errors = 0

    for file_path in sorted(files_to_check):
        print(f"🔍 Checking spelling in {file_path.name}...")

        if dictionary_path:
            misspelled = spell_check_file(file_path, dictionary_path)
        else:
            # Fallback to basic aspell without project dictionary
            try:
                result = subprocess.run(
                    ["aspell", "--list"],
                    input=file_path.read_text(encoding="utf-8"),
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                misspelled = (
                    [word.strip() for word in result.stdout.split("\n") if word.strip()]
                    if result.returncode == 0
                    else None
                )
            except Exception:
                misspelled = None

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


def main() -> int:
    """Main function to spell check documentation.

    Returns:
        Exit code: 0 for success, 1 for errors or missing dependencies
    """
    parser = argparse.ArgumentParser(
        description="Spell check documentation files using aspell with technical terms dictionary"
    )
    parser.add_argument(
        "--files",
        nargs="*",
        type=Path,
        help="Specific files to check (for git hooks). If not provided, checks all documentation files.",
    )
    parser.add_argument("--quiet", action="store_true", help="Reduce output verbosity")

    args = parser.parse_args()

    if not args.quiet:
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
    if not args.quiet:
        print(f"📁 Project root: {project_root}")
        print()

    # Determine which files to check
    specific_files = None
    if args.files:
        # Convert relative paths to absolute paths relative to project root
        specific_files = []
        for file_path in args.files:
            if file_path.is_absolute():
                specific_files.append(file_path)
            else:
                # Assume relative to project root
                specific_files.append(project_root / file_path)

        if not args.quiet:
            print(f"📝 Checking {len(specific_files)} specified files:")
            for f in specific_files:
                if f.exists():
                    print(f"   ✓ {f.relative_to(project_root)}")
                else:
                    print(f"   ⚠️  {f.relative_to(project_root)} (not found)")
            print()

    # Perform spell checking
    files_with_errors = spell_check_documentation(project_root, specific_files)

    # Report results
    if not args.quiet:
        print("=" * 35)

    if files_with_errors == 0:
        if not args.quiet:
            print("✅ All documentation files passed spell check!")
        return 0
    else:
        print(f"⚠️  {files_with_errors} file(s) have potential spelling errors")
        if not args.quiet:
            print()
            print("💡 Tips:")
            print("   • Review the reported words for actual typos")
            print("   • Technical terms may need to be added to the dictionary")
            print("   • Consider context - some 'errors' might be intentional")
        return 0  # Don't fail CI for spelling warnings


if __name__ == "__main__":
    sys.exit(main())
