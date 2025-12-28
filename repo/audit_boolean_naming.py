#!/usr/bin/env python3
"""Audit boolean configuration options for naming convention compliance.

This script scans all Pydantic config models in segnomms for boolean fields
and checks that they follow the documented naming conventions:

- Bare name: Segno-inherited concepts (eci, boost_error)
- *_enabled suffix: State booleans (centerpiece_enabled)
- use_* prefix: Strategy selection (use_marching_squares)
- Bare name: UI behaviors (interactive, tooltips)

Deprecated: enable_* prefix (action verb, not state descriptor)

Usage:
    python repo/audit_boolean_naming.py [--strict]

Exit codes:
    0: All fields comply with conventions (or only known exceptions)
    1: Violations found
"""

from __future__ import annotations

import argparse
import ast
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

# Known exceptions - existing fields that don't follow conventions
# but are documented or have valid reasons to keep
KNOWN_EXCEPTIONS: dict[str, str] = {
    # Segno-inherited concepts using bare names (correct)
    "eci": "Segno-inherited concept",
    "boost_error": "Segno-inherited concept",
    "micro": "Segno-inherited concept",
    "auto_mask": "Segno-inherited concept - automatic mask pattern selection",
    "structured_append": "Segno-inherited concept - multi-symbol QR linking",
    # Nested phase configs use .enabled (correct pattern)
    "enabled": "Nested phase config field",
    # UI behaviors using bare names (correct)
    "interactive": "UI behavior",
    "tooltips": "UI behavior",
    # Legacy fields that predate conventions
    "eci_enabled": "Legacy field - maps Segno concept to *_enabled pattern",
    "safe_mode": "Legacy field - predates *_enabled convention",
    # Debug/development fields - bare names for clarity
    "debug_mode": "Debug flag - bare name for clarity",
    "debug_timing": "Debug flag - bare name for clarity",
    "debug_stroke": "Debug flag - bare name for clarity",
    "verbose_logging": "Debug flag - bare name for clarity",
    "save_intermediate_results": "Debug flag - descriptive bare name",
    # Standards compliance
    "enforce_wcag_standards": "Standards compliance flag - descriptive bare name",
}

# Patterns that are correct
VALID_PATTERNS = [
    re.compile(r"^use_\w+$"),  # use_* prefix
    re.compile(r"^\w+_enabled$"),  # *_enabled suffix
]

# Deprecated pattern
DEPRECATED_PATTERN = re.compile(r"^enable_\w+$")


@dataclass
class BooleanField:
    """Represents a boolean field found in a Pydantic model."""

    file_path: Path
    line_number: int
    class_name: str
    field_name: str
    is_exception: bool = False
    exception_reason: Optional[str] = None
    is_deprecated_pattern: bool = False


def is_valid_convention(field_name: str) -> bool:
    """Check if a field name follows valid naming conventions."""
    # Known exceptions are valid
    if field_name in KNOWN_EXCEPTIONS:
        return True

    # Check against valid patterns
    for pattern in VALID_PATTERNS:
        if pattern.match(field_name):
            return True

    return False


def is_deprecated_pattern(field_name: str) -> bool:
    """Check if field uses the deprecated enable_* pattern."""
    return bool(DEPRECATED_PATTERN.match(field_name))


def find_boolean_fields(file_path: Path) -> list[BooleanField]:
    """Find all boolean fields in Pydantic models in a Python file."""
    fields: list[BooleanField] = []

    try:
        content = file_path.read_text()
        tree = ast.parse(content)
    except (SyntaxError, OSError) as e:
        print(f"Warning: Could not parse {file_path}: {e}", file=sys.stderr)
        return []

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            # Look for Pydantic model classes
            base_names = [getattr(base, "id", getattr(base, "attr", None)) for base in node.bases]
            is_pydantic_model = any(name in ("BaseModel", "BaseSettings") for name in base_names if name)

            if not is_pydantic_model:
                continue

            # Find annotated assignments (field definitions)
            for item in node.body:
                if isinstance(item, ast.AnnAssign) and item.target:
                    field_name = getattr(item.target, "id", None)
                    if not field_name:
                        continue

                    # Check if annotation is bool
                    annotation = item.annotation
                    is_bool = False

                    if isinstance(annotation, ast.Name) and annotation.id == "bool":
                        is_bool = True
                    elif isinstance(annotation, ast.Subscript):
                        # Handle Optional[bool], etc.
                        if isinstance(annotation.slice, ast.Name):
                            is_bool = annotation.slice.id == "bool"

                    if is_bool:
                        exception_reason = KNOWN_EXCEPTIONS.get(field_name)
                        fields.append(
                            BooleanField(
                                file_path=file_path,
                                line_number=item.lineno,
                                class_name=node.name,
                                field_name=field_name,
                                is_exception=exception_reason is not None,
                                exception_reason=exception_reason,
                                is_deprecated_pattern=is_deprecated_pattern(field_name),
                            )
                        )

    return fields


def audit_directory(directory: Path) -> tuple[list[BooleanField], list[BooleanField]]:
    """Audit all Python files in a directory for naming convention violations.

    Returns:
        Tuple of (violations, deprecated_usages)
    """
    violations: list[BooleanField] = []
    deprecated_usages: list[BooleanField] = []

    config_path = directory / "config"
    if not config_path.exists():
        print(f"Warning: Config directory not found: {config_path}", file=sys.stderr)
        return violations, deprecated_usages

    for py_file in config_path.rglob("*.py"):
        fields = find_boolean_fields(py_file)

        for field in fields:
            if field.is_deprecated_pattern:
                deprecated_usages.append(field)
            elif not field.is_exception and not is_valid_convention(field.field_name):
                violations.append(field)

    return violations, deprecated_usages


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Audit boolean configuration fields for naming convention compliance"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat deprecated patterns as errors",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show all fields, not just violations",
    )
    args = parser.parse_args()

    # Find segnomms directory
    script_dir = Path(__file__).parent
    segnomms_dir = script_dir.parent / "segnomms"

    if not segnomms_dir.exists():
        print(f"Error: segnomms directory not found at {segnomms_dir}", file=sys.stderr)
        return 1

    print(f"Auditing boolean fields in {segnomms_dir}/config/...")
    violations, deprecated = audit_directory(segnomms_dir)

    if args.verbose:
        print("\nAll boolean fields found:")
        config_path = segnomms_dir / "config"
        for py_file in config_path.rglob("*.py"):
            fields = find_boolean_fields(py_file)
            for field in fields:
                status = "OK"
                if field.is_exception:
                    status = f"EXCEPTION: {field.exception_reason}"
                elif field.is_deprecated_pattern:
                    status = "DEPRECATED"
                elif not is_valid_convention(field.field_name):
                    status = "VIOLATION"
                print(
                    f"  {field.file_path.relative_to(segnomms_dir.parent)}:"
                    f"{field.line_number} {field.class_name}.{field.field_name} - {status}"
                )

    if violations:
        print(f"\n{len(violations)} violation(s) found:")
        for v in violations:
            print(
                f"  {v.file_path.relative_to(segnomms_dir.parent)}:{v.line_number} "
                f"{v.class_name}.{v.field_name}"
            )
        print("\nRefer to docs/source/developer/naming-conventions.rst for guidance.")

    if deprecated:
        label = "error(s)" if args.strict else "warning(s)"
        print(f"\n{len(deprecated)} deprecated pattern {label}:")
        for d in deprecated:
            print(
                f"  {d.file_path.relative_to(segnomms_dir.parent)}:{d.line_number} "
                f"{d.class_name}.{d.field_name} (uses deprecated enable_* pattern)"
            )

    if not violations and not deprecated:
        print("\nAll boolean fields comply with naming conventions.")
        return 0
    elif not violations and deprecated and not args.strict:
        print(f"\nNo violations. {len(deprecated)} deprecated pattern(s) found (use --strict to fail).")
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
