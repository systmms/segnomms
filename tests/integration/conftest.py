"""
Integration tests conftest.py - imports from parent conftest.

This file ensures integration tests can access the svg_to_png function
and other fixtures from the main test conftest.py.
"""

# Import other commonly used fixtures
# Import the svg_to_png function from parent conftest
from ..conftest import (
    RENDER_PARAMS,
    examples_generated_dir,
    generate_diff_html,
    image_snapshot,
    normalize_svg,
    svg_to_png,
    test_output_dir,
    visual_baseline_dir,
    visual_diff_dir,
    visual_output_dir,
    visual_regression_tester,
)

# Make svg_to_png available for direct import
__all__ = [
    "svg_to_png",
    "visual_regression_tester",
    "test_output_dir",
    "visual_baseline_dir",
    "visual_output_dir",
    "visual_diff_dir",
    "examples_generated_dir",
    "image_snapshot",
    "RENDER_PARAMS",
    "normalize_svg",
    "generate_diff_html",
]
