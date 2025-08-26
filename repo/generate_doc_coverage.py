#!/usr/bin/env python3
"""Generate documentation coverage report for the SegnoMMS project.

This script analyzes the project structure and documentation to provide
coverage metrics and generate reports for documentation completeness.
"""

import sys
from pathlib import Path
from typing import Tuple


def count_python_modules(project_root: Path) -> int:
    """Count total Python modules in the project.

    Args:
        project_root: Root directory of the project

    Returns:
        Number of Python modules (excluding __init__.py files)
    """
    segnomms_dir = project_root / "segnomms"

    if not segnomms_dir.exists():
        print(f"❌ SegnoMMS source directory not found at {segnomms_dir}")
        return 0

    # Find all Python files, excluding __init__.py
    python_files = list(segnomms_dir.rglob("*.py"))
    modules = [f for f in python_files if f.name != "__init__.py"]

    return len(modules)


def count_documented_modules(docs_source_dir: Path) -> int:
    """Count modules that have documentation.

    Args:
        docs_source_dir: Documentation source directory

    Returns:
        Number of documented modules
    """
    if not docs_source_dir.exists():
        print(f"❌ Documentation source directory not found at {docs_source_dir}")
        return 0

    documented_count = 0

    # Search for automodule directives in RST files
    for rst_file in docs_source_dir.rglob("*.rst"):
        try:
            with open(rst_file, "r", encoding="utf-8") as f:
                content = f.read()
                # Count automodule directives
                documented_count += content.count(".. automodule::")
        except Exception as e:
            print(f"⚠️  Error reading {rst_file}: {e}")

    return documented_count


def calculate_coverage(total_modules: int, documented_modules: int) -> Tuple[float, str]:
    """Calculate documentation coverage percentage and status.

    Args:
        total_modules: Total number of Python modules
        documented_modules: Number of documented modules

    Returns:
        Tuple of (coverage_percentage, status_emoji)
    """
    if total_modules == 0:
        return 0.0, "❓"

    coverage = (documented_modules / total_modules) * 100

    if coverage >= 90:
        return coverage, "🟢"
    elif coverage >= 70:
        return coverage, "🟡"
    else:
        return coverage, "🔴"


def generate_coverage_report(
    output_file: Path,
    total_modules: int,
    documented_modules: int,
    coverage: float,
    status_emoji: str,
) -> None:
    """Generate markdown coverage report.

    Args:
        output_file: Path to write the report
        total_modules: Total number of modules
        documented_modules: Number of documented modules
        coverage: Coverage percentage
        status_emoji: Status indicator
    """
    report_content = f"""## 📚 Documentation Coverage

- **Total Python modules:** {total_modules}
- **Documented modules:** {documented_modules}
- **Documentation coverage:** {status_emoji} {coverage:.1f}%

### Coverage Status
{status_emoji} **{coverage:.1f}%** - {"Excellent" if coverage >= 90 else "Good" if coverage >= 70 else "Needs Improvement"}

### Recommendations
"""

    if coverage < 70:
        report_content += """
- 🎯 **Priority:** Increase documentation coverage to at least 70%
- 📝 **Focus:** Add automodule directives for core modules
- 🔍 **Review:** Check which modules are missing from docs/source/api/
"""
    elif coverage < 90:
        report_content += """
- 🎯 **Goal:** Aim for 90%+ coverage for comprehensive documentation
- 📝 **Focus:** Document remaining utility and helper modules
- ✨ **Enhancement:** Add examples and usage guides
"""
    else:
        report_content += """
- ✅ **Excellent coverage!** Documentation is comprehensive
- 🚀 **Maintain:** Keep documentation updated with code changes
- 📖 **Enhance:** Consider adding more examples and tutorials
"""

    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(report_content)
        print(f"📄 Coverage report saved to {output_file}")
    except Exception as e:
        print(f"❌ Error saving report to {output_file}: {e}")


def main() -> int:
    """Main function to generate documentation coverage report.

    Returns:
        Exit code: 0 for success, 1 for errors
    """
    print("📊 Generating Documentation Coverage Report")
    print("=" * 45)

    # Determine project structure
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    docs_dir = project_root / "docs"
    docs_source_dir = docs_dir / "source"

    print(f"📁 Project root: {project_root}")
    print(f"📁 Docs source: {docs_source_dir}")
    print()

    # Count modules and documentation
    total_modules = count_python_modules(project_root)
    documented_modules = count_documented_modules(docs_source_dir)

    if total_modules == 0:
        print("❌ No Python modules found. Check project structure.")
        return 1

    # Calculate coverage
    coverage, status_emoji = calculate_coverage(total_modules, documented_modules)

    # Display results
    print("📈 Documentation Coverage Analysis:")
    print(f"   Total modules: {total_modules}")
    print(f"   Documented modules: {documented_modules}")
    print(f"   Coverage: {status_emoji} {coverage:.1f}%")
    print()

    # Generate report file
    if script_dir.parent.name == "repo":
        # Script is in repo/, save report to docs/
        output_file = docs_dir / "doc-coverage.md"
    else:
        # Fallback to current directory
        output_file = Path("doc-coverage.md")

    generate_coverage_report(output_file, total_modules, documented_modules, coverage, status_emoji)

    print("✅ Documentation coverage report generated successfully!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
