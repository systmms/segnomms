"""Test helpers and utilities for SegnoMMS testing."""

from .scanning_harness import QRScanabilityHarness, get_scanability_harness
from .test_case_generator import TestCaseGenerator, Category, Case
from .test_output_manager import OutputManager
from .custom_assertions import (
    # Core assertion functions
    assert_svg_structure,
    assert_svg_elements_present,
    assert_svg_attributes,
    assert_svg_css_classes,
    assert_svg_color_format,
    assert_qr_scannable,
    assert_qr_timing_patterns,
    assert_accessibility_compliance,
    assert_svg_performance,
    # Convenience combination functions
    assert_complete_svg_validation,
    assert_qr_code_complete,
    # Exception classes
    SVGValidationError,
    QRValidationError,
    AccessibilityValidationError
)

__all__ = [
    "QRScanabilityHarness", 
    "get_scanability_harness",
    "TestCaseGenerator",
    "Category", 
    "Case",
    "OutputManager",
    # Custom assertions
    "assert_svg_structure",
    "assert_svg_elements_present", 
    "assert_svg_attributes",
    "assert_svg_css_classes",
    "assert_svg_color_format",
    "assert_qr_scannable",
    "assert_qr_timing_patterns",
    "assert_accessibility_compliance", 
    "assert_svg_performance",
    "assert_complete_svg_validation",
    "assert_qr_code_complete",
    "SVGValidationError",
    "QRValidationError", 
    "AccessibilityValidationError"
]