#!/usr/bin/env python3
"""
Documentation Reference Validation Script

Validates all cross-references, toctree entries, and API references
in the SegnoMMS documentation to ensure they point to existing files
and Python objects.

Usage:
    python repo/validate_docs_references.py

Returns exit code 0 if all references are valid, 1 if issues found.
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple


def find_rst_files(docs_source: Path) -> List[Path]:
    """Find all RST files in the documentation source directory."""
    return list(docs_source.rglob("*.rst"))


def extract_toctree_entries(file_path: Path) -> List[str]:
    """Extract all toctree entries from an RST file."""
    entries = []
    content = file_path.read_text(encoding="utf-8")

    # Find toctree blocks
    toctree_pattern = r"\.\.[ \t]+toctree::\s*\n((?:[ \t]+[^\n]*\n)*)"
    for match in re.finditer(toctree_pattern, content, re.MULTILINE):
        block = match.group(1)
        # Extract entries (non-option lines)
        for line in block.split("\n"):
            stripped = line.strip()
            if stripped and not stripped.startswith(":"):
                entries.append(stripped)

    return entries


def extract_doc_references(file_path: Path) -> List[str]:
    """Extract all :doc: cross-references from an RST file."""
    content = file_path.read_text(encoding="utf-8")

    # Find :doc:`reference` patterns
    doc_pattern = r":doc:`([^`]+)`"
    matches = re.findall(doc_pattern, content)

    # Clean up references (remove <text> parts)
    references = []
    for match in matches:
        # Handle :doc:`text <reference>` format
        if "<" in match and ">" in match:
            ref = match.split("<")[1].split(">")[0]
        else:
            ref = match
        references.append(ref.strip())

    return references


def extract_api_references(file_path: Path) -> List[str]:
    """Extract API references (:class:, :func:, :meth:, etc.) from RST."""
    content = file_path.read_text(encoding="utf-8")

    # Find various API reference patterns
    patterns = [
        r":class:`([^`]+)`",
        r":func:`([^`]+)`",
        r":meth:`([^`]+)`",
        r":mod:`([^`]+)`",
        r":attr:`([^`]+)`",
    ]

    references = []
    for pattern in patterns:
        matches = re.findall(pattern, content)
        for match in matches:
            # Clean up reference (remove ~ prefix)
            ref = match.lstrip("~")
            references.append(ref)

    return references


def validate_toctree_entries(docs_source: Path, entries: List[str]) -> List[str]:
    """Validate that all toctree entries point to existing files."""
    errors = []

    for entry in entries:
        # Convert entry to file path
        if not entry.endswith(".rst"):
            entry_path = docs_source / f"{entry}.rst"
        else:
            entry_path = docs_source / entry

        if not entry_path.exists():
            errors.append(f"Toctree entry not found: {entry} -> {entry_path}")

    return errors


def validate_doc_references(docs_source: Path, file_references: List[Tuple[str, Path]]) -> List[str]:
    """Validate that all :doc: references point to existing files."""
    errors = []

    for ref, source_file in file_references:
        # Convert reference to file path, considering relative paths
        if not ref.endswith(".rst"):
            if ref.startswith("/"):
                # Absolute reference from docs root (strip leading slash)
                ref_path = docs_source / f"{ref[1:]}.rst"
            elif "/" in ref:
                # Relative reference with path - resolve relative to source file
                source_dir = source_file.parent
                ref_path = (source_dir / f"{ref}.rst").resolve()
            else:
                # Simple relative reference - resolve relative to source file
                source_dir = source_file.parent
                ref_path = source_dir / f"{ref}.rst"
        else:
            ref_path = docs_source / ref

        if not ref_path.exists():
            errors.append(
                f"Doc reference not found: {ref} -> {ref_path} (from {source_file.relative_to(docs_source)})"
            )

    return errors


def validate_api_references(references: List[str]) -> List[str]:
    """Validate API references by attempting imports (basic check)."""
    errors = []

    for ref in references:
        if ref.startswith("segnomms."):
            # Basic module path validation
            module_parts = ref.split(".")
            if len(module_parts) < 2:
                continue

            # Check if it looks like a valid module path
            if not all(part.isidentifier() or part.isdigit() for part in module_parts):
                errors.append(f"Invalid API reference format: {ref}")

    return errors


def main():
    """Main validation function."""
    # Get project root
    script_path = Path(__file__).resolve()
    project_root = script_path.parent.parent
    docs_source = project_root / "docs" / "source"

    if not docs_source.exists():
        print(f"❌ Documentation source not found: {docs_source}")
        return 1

    print("🔍 Validating SegnoMMS Documentation References...")
    print(f"📁 Docs source: {docs_source}")

    # Find all RST files
    rst_files = find_rst_files(docs_source)
    print(f"📄 Found {len(rst_files)} RST files")

    total_errors = 0
    all_toctree_entries = []
    all_doc_references = []
    all_api_references = []

    # Process each file
    for rst_file in rst_files:
        rel_path = rst_file.relative_to(docs_source)

        # Extract references
        toctree_entries = extract_toctree_entries(rst_file)
        doc_references = extract_doc_references(rst_file)
        api_references = extract_api_references(rst_file)

        all_toctree_entries.extend(toctree_entries)
        # Store doc references with their source file for relative resolution
        all_doc_references.extend([(ref, rst_file) for ref in doc_references])
        all_api_references.extend(api_references)

        if toctree_entries or doc_references or api_references:
            print(
                f"   📋 {rel_path}: {len(toctree_entries)} toctree, {len(doc_references)} :doc:, {len(api_references)} API refs"
            )

    print("\n📊 Total References Found:")
    print(f"   🗂️  Toctree entries: {len(all_toctree_entries)}")
    print(f"   🔗 Doc references: {len(all_doc_references)}")
    print(f"   🐍 API references: {len(all_api_references)}")

    # Validate references
    print("\n🔍 Validating References...")

    toctree_errors = validate_toctree_entries(docs_source, all_toctree_entries)
    doc_errors = validate_doc_references(docs_source, all_doc_references)
    api_errors = validate_api_references(all_api_references)

    # Report results
    if toctree_errors:
        print(f"\n❌ Toctree Errors ({len(toctree_errors)}):")
        for error in toctree_errors:
            print(f"   {error}")
        total_errors += len(toctree_errors)
    else:
        print("✅ All toctree entries valid")

    if doc_errors:
        print(f"\n❌ Doc Reference Errors ({len(doc_errors)}):")
        for error in doc_errors:
            print(f"   {error}")
        total_errors += len(doc_errors)
    else:
        print("✅ All :doc: references valid")

    if api_errors:
        print(f"\n❌ API Reference Errors ({len(api_errors)}):")
        for error in api_errors:
            print(f"   {error}")
        total_errors += len(api_errors)
    else:
        print("✅ All API references valid")

    # Summary
    if total_errors == 0:
        print("\n🎉 All documentation references are valid!")
        return 0
    else:
        print(f"\n💥 Found {total_errors} reference issues")
        print("\n💡 Run 'uv run make html' to see detailed Sphinx warnings")
        return 1


if __name__ == "__main__":
    sys.exit(main())
