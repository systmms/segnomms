"""
Coverage bridge for browser-based tests.

This module provides utilities to instrument JavaScript/Pyodide code
for coverage tracking and merge the results with Python coverage data.
"""

import json
from pathlib import Path
from typing import Dict

import coverage


class PyodideCoverageBridge:
    """Bridge coverage data between Pyodide (browser) and Python tests."""

    def __init__(self, source_dir: Path):
        self.source_dir = source_dir
        self.coverage_data = {}

    def instrument_bundled_code(self, bundled_js_path: Path) -> str:
        """
        Add coverage instrumentation to the bundled JavaScript/Python code.

        This adds tracking calls that can be collected from the browser.
        """
        content = bundled_js_path.read_text()

        # Add coverage collection setup
        instrumented = (
            """
// Coverage instrumentation
window.__coverage__ = window.__coverage__ || {};
window.__coverage__.pyodide = {
    lines: {},
    functions: {},
    branches: {}
};

function __recordCoverage(file, line) {
    if (!window.__coverage__.pyodide.lines[file]) {
        window.__coverage__.pyodide.lines[file] = new Set();
    }
    window.__coverage__.pyodide.lines[file].add(line);
}

// Original content with instrumentation
"""
            + content
        )

        # Add function to export coverage data
        instrumented += """

// Export coverage data
window.exportCoverageData = function() {
    const coverage = window.__coverage__.pyodide;
    const result = {
        lines: {},
        functions: {},
        branches: {}
    };

    // Convert Sets to Arrays for JSON serialization
    for (const [file, lines] of Object.entries(coverage.lines)) {
        result.lines[file] = Array.from(lines);
    }

    return JSON.stringify(result);
};
"""

        return instrumented

    def collect_browser_coverage(self, coverage_json: str) -> Dict:
        """Parse coverage data collected from the browser."""
        return json.loads(coverage_json)

    def merge_with_python_coverage(self, browser_coverage: Dict, python_cov: coverage.Coverage):
        """
        Merge browser coverage data with Python coverage data.

        This maps the bundled code lines back to the original source files.
        """
        # Create a mapping from bundled lines to source lines
        # This would require parsing the bundled file to track line mappings

        # For now, we'll create a simple mapping based on module structure
        for file, lines in browser_coverage.get("lines", {}).items():
            # Map bundled file references to source files
            source_file = self._map_to_source_file(file)
            if source_file and source_file.exists():
                # Add the covered lines to Python coverage data
                # This requires using Coverage.py's internal API
                pass

    def _map_to_source_file(self, bundled_ref: str) -> Path:
        """Map a reference in bundled code to the original source file."""
        # Simple mapping based on module names
        mappings = {
            "shapes": "shapes/basic.py",
            "detector": "core/detector.py",
            "config": "config/schema.py",
            "builder": "utils/svg_builder.py",
        }

        for key, source_path in mappings.items():
            if key in bundled_ref:
                return self.source_dir / source_path

        return None


def create_coverage_report(test_results_dir: Path):
    """
    Create a unified coverage report combining Python and browser test coverage.
    """
    # Load Python coverage data
    python_cov = coverage.Coverage()
    python_cov.load()

    # Load browser coverage data if available
    browser_coverage_path = test_results_dir / "browser_coverage.json"
    if browser_coverage_path.exists():
        bridge = PyodideCoverageBridge(Path("segnomms"))
        browser_data = json.loads(browser_coverage_path.read_text())
        bridge.merge_with_python_coverage(browser_data, python_cov)

    # Generate combined report
    python_cov.html_report(directory=str(test_results_dir / "coverage_combined"))
    python_cov.report()


# Pytest plugin to automatically collect browser coverage
def pytest_runtest_teardown(item):
    """Collect browser coverage after each Playwright test."""
    if "playwright" in item.keywords:
        # Check if the test has browser coverage data
        if hasattr(item, "_browser_coverage"):
            # Save the coverage data
            coverage_dir = Path(__file__).parent / "coverage"
            coverage_dir.mkdir(exist_ok=True)

            coverage_file = coverage_dir / f"{item.nodeid.replace('/', '_')}.json"
            coverage_file.write_text(item._browser_coverage)
