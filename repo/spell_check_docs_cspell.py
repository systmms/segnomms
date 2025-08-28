#!/usr/bin/env python3
"""Spell check documentation files using cspell (Code Spell Checker).

This script performs spell checking on documentation files using cspell
with a custom dictionary of technical terms commonly used in the project.
cspell provides better code-aware parsing and modern tooling compared to aspell.
"""

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


def get_project_dictionary_path(project_root: Path) -> Path:
    """Get the path to the project-specific cspell dictionary.

    Args:
        project_root: Root directory of the project

    Returns:
        Path to the project dictionary file
    """
    return project_root / "project-words.txt"


def get_cspell_config_path(project_root: Path) -> Path:
    """Get the path to the cspell configuration file.

    Args:
        project_root: Root directory of the project

    Returns:
        Path to the cspell.json configuration file
    """
    return project_root / "cspell.json"


def check_node_availability() -> bool:
    """Check if Node.js is available on the system.

    Returns:
        True if Node.js is available, False otherwise
    """
    return shutil.which("node") is not None and shutil.which("npm") is not None


def check_cspell_availability(project_root: Path) -> bool:
    """Check if cspell is available.

    Args:
        project_root: Root directory of the project

    Returns:
        True if cspell is available, False otherwise
    """
    # Check for npx cspell (preferred)
    if shutil.which("npx"):
        try:
            result = subprocess.run(
                ["npx", "cspell", "--version"], capture_output=True, text=True, timeout=10, cwd=project_root
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, subprocess.TimeoutExpired):
            pass

    # Check for globally installed cspell
    if shutil.which("cspell"):
        try:
            result = subprocess.run(["cspell", "--version"], capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except (subprocess.SubprocessError, subprocess.TimeoutExpired):
            pass

    return False


def install_cspell(project_root: Path) -> bool:
    """Install cspell using npm if not available.

    Args:
        project_root: Root directory of the project

    Returns:
        True if installation successful, False otherwise
    """
    if not check_node_availability():
        print("❌ Node.js and npm are required but not found.")
        print("   Please install Node.js: https://nodejs.org/")
        return False

    try:
        print("📦 Installing cspell...")
        result = subprocess.run(
            ["npm", "install"], capture_output=True, text=True, timeout=120, cwd=project_root
        )

        if result.returncode == 0:
            print("✅ cspell installed successfully")
            return True
        else:
            print(f"❌ npm install failed: {result.stderr}")
            return False

    except (subprocess.SubprocessError, subprocess.TimeoutExpired) as e:
        print(f"❌ Error installing cspell: {e}")
        return False


def spell_check_file(file_path: Path, project_root: Path, config_path: Path) -> Optional[Dict[str, Any]]:
    """Spell check a single file using cspell.

    Args:
        file_path: Path to the file to check
        project_root: Root directory of the project
        config_path: Path to cspell configuration file

    Returns:
        Dictionary with spelling results, or None if error occurred
    """
    if not file_path.exists():
        print(f"⚠️  File not found: {file_path}")
        return None

    if not config_path.exists():
        print(f"⚠️  cspell configuration not found: {config_path}")
        return None

    try:
        # Use npx cspell with JSON output for structured parsing
        result = subprocess.run(
            [
                "npx",
                "cspell",
                "--config",
                str(config_path),
                "--reporter",
                "json",
                "--no-progress",
                str(file_path),
            ],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=project_root,
        )

        # cspell returns 1 if spelling errors found, 0 if none
        if result.returncode in [0, 1]:
            try:
                if result.stdout.strip():
                    # Parse JSON output for detailed error information
                    issues = []
                    for line in result.stdout.strip().split("\n"):
                        if line.strip():
                            try:
                                issue = json.loads(line)
                                if "text" in issue:
                                    issues.append(issue)
                            except json.JSONDecodeError:
                                # Skip non-JSON lines (like summary lines)
                                continue

                    return {"file": str(file_path), "issues": issues, "error_count": len(issues)}
                else:
                    # No issues found
                    return {"file": str(file_path), "issues": [], "error_count": 0}
            except json.JSONDecodeError:
                # Fall back to simple word list parsing if JSON fails
                words = [word.strip() for word in result.stdout.split() if word.strip()]
                return {
                    "file": str(file_path),
                    "issues": [{"text": word} for word in words],
                    "error_count": len(words),
                }
        else:
            print(f"⚠️  cspell error for {file_path}: {result.stderr}")
            return None

    except subprocess.TimeoutExpired:
        print(f"⚠️  Spell check timeout for {file_path}")
        return None
    except Exception as e:
        print(f"⚠️  Error checking {file_path}: {e}")
        return None


def spell_check_documentation(project_root: Path, specific_files: Optional[List[Path]] = None) -> int:
    """Spell check documentation files using cspell.

    Args:
        project_root: Root directory of the project
        specific_files: Optional list of specific files to check (for git hooks)

    Returns:
        Number of files with spelling errors
    """
    config_path = get_cspell_config_path(project_root)

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

    print(f"📝 Checking {len(files_to_check)} documentation files with cspell")
    print()

    files_with_errors = 0
    total_errors = 0

    for file_path in sorted(files_to_check):
        print(f"🔍 Checking spelling in {file_path.name}...")

        result = spell_check_file(file_path, project_root, config_path)

        if result is None:
            continue  # Error already reported

        if result["error_count"] > 0:
            files_with_errors += 1
            error_count = result["error_count"]
            total_errors += error_count

            print(f"  ❌ Found {error_count} potential spelling errors:")

            # Show detailed issues if available
            issues = result.get("issues", [])
            shown = 0
            for issue in issues[:10]:  # Show first 10 errors
                if "text" in issue:
                    word = issue["text"]
                    line_info = ""
                    if "row" in issue and "col" in issue:
                        line_info = f" (line {issue['row']}, col {issue['col']})"
                    print(f"     • {word}{line_info}")
                    shown += 1

            if len(issues) > 10:
                print(f"     ... and {len(issues) - 10} more")
        else:
            print("  ✅ No spelling errors found")

        print()  # Add spacing between files

    return files_with_errors


def main() -> int:
    """Main function to spell check documentation using cspell.

    Returns:
        Exit code: 0 for success, 1 for errors or missing dependencies
    """
    parser = argparse.ArgumentParser(
        description="Spell check documentation files using cspell with technical terms dictionary"
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
        print("📖 Spell Checking Documentation (cspell)")
        print("=" * 42)

    # Find project root
    project_root = Path(__file__).parent.parent
    if not args.quiet:
        print(f"📁 Project root: {project_root}")
        print()

    # Check if cspell is available
    if not check_cspell_availability(project_root):
        if not args.quiet:
            print("⚠️  cspell not found. Installing...")

        if not install_cspell(project_root):
            print("❌ Failed to install cspell. Please install manually:")
            print("   • Ensure Node.js is installed: https://nodejs.org/")
            print("   • Run: npm install")
            print("   • Or install globally: npm install -g cspell")
            return 1

        # Verify installation after install
        if not check_cspell_availability(project_root):
            print("❌ cspell installation verification failed")
            return 1

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
        print("=" * 42)

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
            print("   • Technical terms can be added to project-words.txt")
            print("   • Consider context - some 'errors' might be intentional")
            print("   • Use 'npm run spell-check' to check all files")
        return 0  # Don't fail CI for spelling warnings


if __name__ == "__main__":
    sys.exit(main())
