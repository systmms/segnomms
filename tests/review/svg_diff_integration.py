"""
Integration module for SVG diff functionality with the review suite.

This module bridges the TestOutputManager with the review suite to provide
SVG structural comparison alongside visual PNG comparison.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from tests.helpers.test_case_generator import TestCaseGenerator
from tests.helpers.test_output_manager import OutputManager


class SVGDiffIntegration:
    """Integrates SVG diff functionality with the review suite."""

    def __init__(self, output_manager: Optional[OutputManager] = None):
        """
        Initialize SVG diff integration.

        Args:
            output_manager: TestOutputManager instance, creates one if not provided
        """
        self.output_manager = output_manager or OutputManager()
        self.review_dir = self.output_manager.review_dir

    def collect_svg_comparisons(self) -> List[Dict[str, Any]]:
        """
        Collect all available SVG files for comparison.

        Returns:
            List of comparison data dictionaries
        """
        comparisons = []

        # Get all test cases that have both baseline and output SVGs
        baseline_svgs = list(self.output_manager.baseline_dir.glob("*.svg"))
        output_svgs = list(self.output_manager.output_dir.glob("*.svg"))

        # Create a mapping of test IDs to file paths
        baseline_map = {svg.stem: svg for svg in baseline_svgs}
        output_map = {svg.stem: svg for svg in output_svgs}

        # Find matching pairs
        for test_id in set(baseline_map.keys()) & set(output_map.keys()):
            baseline_path = baseline_map[test_id]
            output_path = output_map[test_id]

            # Get corresponding PNG and config files
            baseline_png = self.output_manager.get_baseline_path(test_id, "png")
            output_png = self.output_manager.get_output_path(test_id, "png")
            config_path = self.output_manager.get_output_path(test_id, "config")

            comparison_data = {
                "test_id": test_id,
                "svg": {
                    "baseline": self._relative_path(baseline_path),
                    "actual": self._relative_path(output_path),
                    "has_changes": self._compare_svg_files(baseline_path, output_path),
                },
                "png": {
                    "baseline": self._relative_path(baseline_png) if baseline_png.exists() else None,
                    "actual": self._relative_path(output_png) if output_png.exists() else None,
                    "has_changes": self._compare_png_files(baseline_png, output_png),
                },
                "config": self._relative_path(config_path) if config_path.exists() else None,
                "metadata": self._get_test_metadata(test_id),
            }

            comparisons.append(comparison_data)

        # Sort by test ID for consistent ordering
        return sorted(comparisons, key=lambda x: x["test_id"])

    def generate_diff_data(self, test_id: str) -> Optional[Dict[str, Any]]:
        """
        Generate structured diff data for a specific test.

        Args:
            test_id: Test case identifier

        Returns:
            Dictionary with diff data or None if files not found
        """
        baseline_svg = self.output_manager.get_baseline_path(test_id, "svg")
        actual_svg = self.output_manager.get_output_path(test_id, "svg")

        if not baseline_svg.exists() or not actual_svg.exists():
            return None

        try:
            baseline_content = baseline_svg.read_text()
            actual_content = actual_svg.read_text()

            return {
                "test_id": test_id,
                "baseline_content": baseline_content,
                "actual_content": actual_content,
                "baseline_path": str(baseline_svg),
                "actual_path": str(actual_svg),
                "changes_detected": baseline_content != actual_content,
                "structural_analysis": self._analyze_svg_structure(baseline_content, actual_content),
            }

        except Exception as e:
            return {"test_id": test_id, "error": str(e), "changes_detected": False}

    def create_diff_summary(self) -> Dict[str, Any]:
        """
        Create a summary of all SVG diffs for the review dashboard.

        Returns:
            Summary statistics and data
        """
        comparisons = self.collect_svg_comparisons()

        total_tests = len(comparisons)
        svg_changes = sum(1 for c in comparisons if c["svg"]["has_changes"])
        png_changes = sum(1 for c in comparisons if c["png"]["has_changes"])

        # Categorize by type of changes
        both_changed = sum(1 for c in comparisons if c["svg"]["has_changes"] and c["png"]["has_changes"])
        svg_only = sum(1 for c in comparisons if c["svg"]["has_changes"] and not c["png"]["has_changes"])
        png_only = sum(1 for c in comparisons if not c["svg"]["has_changes"] and c["png"]["has_changes"])

        return {
            "total_tests": total_tests,
            "svg_changes": svg_changes,
            "png_changes": png_changes,
            "change_breakdown": {
                "both_changed": both_changed,
                "svg_only": svg_only,
                "png_only": png_only,
                "no_changes": total_tests - both_changed - svg_only - png_only,
            },
            "change_rate": {
                "svg": (svg_changes / total_tests * 100) if total_tests > 0 else 0,
                "png": (png_changes / total_tests * 100) if total_tests > 0 else 0,
            },
            "comparisons": comparisons,
        }

    def export_diff_data(self, output_file: Path) -> None:
        """
        Export diff data to JSON for use by the review interface.

        Args:
            output_file: Path to write JSON data
        """
        diff_summary = self.create_diff_summary()

        with open(output_file, "w") as f:
            json.dump(diff_summary, f, indent=2, sort_keys=True)

    def _relative_path(self, path: Path) -> str:
        """Convert absolute path to relative from review directory."""
        try:
            return str(path.relative_to(self.review_dir))
        except ValueError:
            # If path is not relative to review_dir, try from project root
            try:
                return str(path.relative_to(self.output_manager.base_dir))
            except ValueError:
                return str(path)

    def _compare_svg_files(self, baseline: Path, actual: Path) -> bool:
        """
        Compare two SVG files for structural differences.

        Args:
            baseline: Baseline SVG file path
            actual: Actual SVG file path

        Returns:
            True if files differ structurally
        """
        if not baseline.exists() or not actual.exists():
            return True  # Missing file counts as a change

        try:
            baseline_content = baseline.read_text()
            actual_content = actual.read_text()

            # Normalize whitespace for comparison
            baseline_normalized = self._normalize_svg(baseline_content)
            actual_normalized = self._normalize_svg(actual_content)

            return baseline_normalized != actual_normalized

        except Exception:
            return True  # Error reading files counts as a change

    def _compare_png_files(self, baseline: Path, actual: Path) -> bool:
        """
        Compare two PNG files for differences.

        Args:
            baseline: Baseline PNG file path
            actual: Actual PNG file path

        Returns:
            True if files differ
        """
        if not baseline.exists() or not actual.exists():
            return True

        try:
            # Simple byte comparison for now
            # Could be enhanced with image similarity algorithms
            return baseline.read_bytes() != actual.read_bytes()
        except Exception:
            return True

    def _normalize_svg(self, svg_content: str) -> str:
        """
        Normalize SVG content for comparison.

        Args:
            svg_content: Raw SVG content

        Returns:
            Normalized SVG content
        """
        # Remove extra whitespace and normalize line endings
        normalized = " ".join(svg_content.split())

        # Could add more normalization here:
        # - Sort attributes
        # - Remove formatting-only differences
        # - Normalize numeric precision

        return normalized

    def _analyze_svg_structure(self, baseline: str, actual: str) -> Dict[str, Any]:
        """
        Analyze structural differences between two SVG files.

        Args:
            baseline: Baseline SVG content
            actual: Actual SVG content

        Returns:
            Analysis results
        """
        try:
            from xml.etree import ElementTree as ET

            baseline_root = ET.fromstring(baseline)
            actual_root = ET.fromstring(actual)

            baseline_elements = self._count_elements(baseline_root)
            actual_elements = self._count_elements(actual_root)

            return {
                "baseline_elements": baseline_elements,
                "actual_elements": actual_elements,
                "element_differences": {
                    tag: actual_elements.get(tag, 0) - baseline_elements.get(tag, 0)
                    for tag in set(baseline_elements.keys()) | set(actual_elements.keys())
                    if actual_elements.get(tag, 0) != baseline_elements.get(tag, 0)
                },
            }

        except Exception as e:
            return {
                "error": f"Failed to analyze structure: {e}",
                "baseline_length": len(baseline),
                "actual_length": len(actual),
            }

    def _count_elements(self, root) -> Dict[str, int]:
        """Count elements by tag name in an XML tree."""
        counts = {}
        for elem in root.iter():
            tag = elem.tag.split("}")[-1]  # Remove namespace
            counts[tag] = counts.get(tag, 0) + 1
        return counts

    def _get_test_metadata(self, test_id: str) -> Dict[str, Any]:
        """
        Get metadata for a test case.

        Args:
            test_id: Test case identifier

        Returns:
            Test metadata
        """
        # Try to find the test case in our generator
        all_cases = TestCaseGenerator.get_all_test_cases()

        for test_case in all_cases:
            if test_case.id == test_id:
                return {
                    "description": test_case.description,
                    "category": test_case.category.value,
                    "tags": test_case.tags,
                    "qr_data": (
                        test_case.qr_data[:50] + "..." if len(test_case.qr_data) > 50 else test_case.qr_data
                    ),
                }

        # Fallback metadata
        return {
            "description": f"Test case: {test_id}",
            "category": "unknown",
            "tags": [],
            "qr_data": "unknown",
        }


def generate_review_with_svg_diffs(output_dir: Path) -> None:
    """
    Generate review suite with SVG diff integration.

    Args:
        output_dir: Directory to write review files
    """
    integration = SVGDiffIntegration()

    # Export diff data for JavaScript consumption
    diff_data_file = output_dir / "svg_diff_data.json"
    integration.export_diff_data(diff_data_file)

    print(f"SVG diff data exported to {diff_data_file}")

    # Create summary report
    summary = integration.create_diff_summary()

    print(f"SVG Diff Summary:")
    print(f"  Total tests: {summary['total_tests']}")
    print(f"  SVG changes: {summary['svg_changes']} ({summary['change_rate']['svg']:.1f}%)")
    print(f"  PNG changes: {summary['png_changes']} ({summary['change_rate']['png']:.1f}%)")

    breakdown = summary["change_breakdown"]
    print(f"  Change breakdown:")
    print(f"    Both changed: {breakdown['both_changed']}")
    print(f"    SVG only: {breakdown['svg_only']}")
    print(f"    PNG only: {breakdown['png_only']}")
    print(f"    No changes: {breakdown['no_changes']}")


if __name__ == "__main__":
    # Example usage
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    generate_review_with_svg_diffs(output_dir)
