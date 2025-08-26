#!/usr/bin/env python3
"""
Test: Visual Regression Testing Techniques

This test demonstrates and validates visual regression testing techniques
for QR code generation, including SVG vs PNG comparison methods.
"""

import io
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from segnomms.plugin import write_segno_mms

# Import test utilities if available
try:
    from tests.conftest import svg_to_png

    PNG_CONVERSION_AVAILABLE = True
except ImportError:
    PNG_CONVERSION_AVAILABLE = False
    print("⚠️  PNG conversion not available - install test dependencies")


def test_svg_vs_png_comparison():
    """Test that demonstrates SVG vs PNG comparison reliability."""

    print("🧪 Testing SVG vs PNG comparison methods")
    print("=" * 50)

    # Generate identical QR codes
    buffer1 = io.StringIO()
    write_segno_mms(
        "Test Content",
        buffer1,
        scale=10,
        shape="squircle",
        corner_radius=0.3,
        dark="#1a1a2e",
        light="#ffffff",
    )
    svg1 = buffer1.getvalue()

    buffer2 = io.StringIO()
    write_segno_mms(
        "Test Content",
        buffer2,
        scale=10,
        shape="squircle",
        corner_radius=0.3,
        dark="#1a1a2e",
        light="#ffffff",
    )
    svg2 = buffer2.getvalue()

    # Test SVG comparison
    svg_identical = svg1 == svg2
    print(f"   SVG text comparison: {'PASS' if svg_identical else 'FAIL'}")

    if PNG_CONVERSION_AVAILABLE:
        # Test PNG comparison
        png1 = svg_to_png(svg1, return_bytes=True)
        png2 = svg_to_png(svg2, return_bytes=True)
        png_identical = png1 == png2
        print(f"   PNG visual comparison: {'PASS' if png_identical else 'FAIL'}")

        # Test with formatting differences
        svg2_formatted = svg2.replace("<rect", "\n    <rect")  # Different whitespace
        png2_formatted = svg_to_png(svg2_formatted, return_bytes=True)

        svg_formatted_identical = svg1 == svg2_formatted
        png_formatted_identical = png1 == png2_formatted

        print(f"\n   With formatting differences:")
        print(f"   SVG comparison: {'PASS' if svg_formatted_identical else 'FAIL'} (should fail)")
        print(f"   PNG comparison: {'PASS' if png_formatted_identical else 'FAIL'} (should pass)")

        # Validate test expectations
        assert not svg_formatted_identical, "SVG should be different with formatting changes"
        assert png_formatted_identical, "PNG should be identical despite formatting changes"

        print(f"   ✅ Test validates PNG comparison is more reliable")
        return True
    else:
        print(f"   ⚠️  Cannot test PNG comparison - missing dependencies")
        return False


def test_visual_change_detection():
    """Test that visual changes are properly detected."""

    print(f"\n🎯 Testing visual change detection")
    print("=" * 40)

    # Generate baseline QR
    buffer_baseline = io.StringIO()
    write_segno_mms(
        "Change Detection Test",
        buffer_baseline,
        scale=10,
        shape="rounded",
        corner_radius=0.3,
        dark="#000000",
        light="#ffffff",
    )
    svg_baseline = buffer_baseline.getvalue()

    # Test cases with different types of changes
    test_cases = [
        {
            "name": "Color change",
            "params": {"dark": "#ff0000"},  # Red instead of black
            "should_detect": True,
        },
        {
            "name": "Shape change",
            "params": {"shape": "circle"},  # Circle instead of rounded
            "should_detect": True,
        },
        {
            "name": "Corner radius change",
            "params": {"corner_radius": 0.5},  # 0.5 instead of 0.3
            "should_detect": True,
        },
        {"name": "Scale change", "params": {"scale": 8}, "should_detect": True},  # 8 instead of 10
        {"name": "Identical parameters", "params": {}, "should_detect": False},  # No changes
    ]

    if PNG_CONVERSION_AVAILABLE:
        png_baseline = svg_to_png(svg_baseline, return_bytes=True)

        for test_case in test_cases:
            print(f"\n   Testing: {test_case['name']}")

            # Generate test QR with modified parameters
            base_params = {
                "scale": 10,
                "shape": "rounded",
                "corner_radius": 0.3,
                "dark": "#000000",
                "light": "#ffffff",
            }
            base_params.update(test_case["params"])

            buffer_test = io.StringIO()
            write_segno_mms("Change Detection Test", buffer_test, **base_params)
            svg_test = buffer_test.getvalue()
            png_test = svg_to_png(svg_test, return_bytes=True)

            # Check if change is detected
            change_detected = png_baseline != png_test
            expected_detection = test_case["should_detect"]

            if change_detected == expected_detection:
                print(f"     ✅ {'Change detected' if change_detected else 'No change detected'} (correct)")
            else:
                print(f"     ❌ {'Change detected' if change_detected else 'No change detected'} (incorrect)")
                return False

        print(f"\n   ✅ All visual change detection tests passed")
        return True
    else:
        print(f"   ⚠️  Cannot test visual change detection - missing dependencies")
        return False


def test_rendering_consistency():
    """Test that rendering is consistent across multiple generations."""

    print(f"\n🔄 Testing rendering consistency")
    print("=" * 35)

    # Generate same QR multiple times
    test_params = {
        "scale": 10,
        "shape": "squircle",
        "corner_radius": 0.4,
        "dark": "#2563eb",
        "light": "#eff6ff",
    }

    svgs = []
    for i in range(5):
        buffer = io.StringIO()
        write_segno_mms("Consistency Test", buffer, **test_params)
        svgs.append(buffer.getvalue())

    # Check SVG consistency
    all_svg_identical = all(svg == svgs[0] for svg in svgs[1:])
    print(f"   SVG consistency: {'PASS' if all_svg_identical else 'FAIL'}")

    if PNG_CONVERSION_AVAILABLE:
        # Check PNG consistency
        pngs = [svg_to_png(svg, return_bytes=True) for svg in svgs]
        all_png_identical = all(png == pngs[0] for png in pngs[1:])
        print(f"   PNG consistency: {'PASS' if all_png_identical else 'FAIL'}")

        assert all_png_identical, "Multiple generations should produce identical PNGs"
        print(f"   ✅ Rendering is consistent across multiple generations")
        return True
    else:
        print(f"   ⚠️  Cannot test PNG consistency - missing dependencies")
        return all_svg_identical


def test_save_regression_artifacts():
    """Generate and save artifacts for manual inspection."""

    print(f"\n💾 Saving test artifacts for inspection")
    print("=" * 40)

    output_dir = Path("test-visual-regression-artifacts")
    output_dir.mkdir(exist_ok=True)

    # Generate various test cases
    test_configs = [
        ("baseline", {"shape": "rounded", "corner_radius": 0.3}),
        ("color_change", {"shape": "rounded", "corner_radius": 0.3, "dark": "#ff0000"}),
        ("shape_change", {"shape": "circle", "corner_radius": 0.3}),
        ("radius_change", {"shape": "rounded", "corner_radius": 0.5}),
    ]

    for config_name, params in test_configs:
        # Generate SVG
        buffer = io.StringIO()
        write_segno_mms("Visual Regression Test", buffer, scale=10, dark="#000000", light="#ffffff", **params)
        svg = buffer.getvalue()

        # Save SVG
        svg_path = output_dir / f"test_{config_name}.svg"
        svg_path.write_text(svg)

        # Save PNG if possible
        if PNG_CONVERSION_AVAILABLE:
            png = svg_to_png(svg, return_bytes=True)
            png_path = output_dir / f"test_{config_name}.png"
            png_path.write_bytes(png)
            print(f"   ✓ Saved {config_name}: SVG + PNG")
        else:
            print(f"   ✓ Saved {config_name}: SVG only")

    print(f"   📁 Artifacts saved to: {output_dir}")
    return True


def main():
    """Run all visual regression testing technique tests."""

    print("🧪 Visual Regression Testing Techniques")
    print("Testing the reliability and accuracy of visual comparison methods")
    print("=" * 70)

    test_results = []

    try:
        # Run all tests
        test_results.append(("SVG vs PNG comparison", test_svg_vs_png_comparison()))
        test_results.append(("Visual change detection", test_visual_change_detection()))
        test_results.append(("Rendering consistency", test_rendering_consistency()))
        test_results.append(("Save test artifacts", test_save_regression_artifacts()))

        # Summary
        print(f"\n📊 Test Results Summary")
        print("=" * 30)

        passed = sum(1 for _, result in test_results if result)
        total = len(test_results)

        for test_name, result in test_results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"   {status} {test_name}")

        print(f"\n🎯 Overall: {passed}/{total} tests passed")

        if passed == total:
            print(f"🎉 All visual regression testing techniques validated!")
            return True
        else:
            print(f"⚠️  Some tests failed - check results above")
            return False

    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
