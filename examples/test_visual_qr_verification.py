#!/usr/bin/env python3
"""
Visual QR Code Design Verification Script

This script generates QR codes with different configurations and provides
visual verification of the designs by creating both SVG and PNG outputs.
"""

import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import segno

# Add the segnomms package to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import segnomms
except ImportError as e:
    print(f"Failed to import segnomms: {e}")
    sys.exit(1)


def create_test_qr_with_verification(test_name, qr_data, config, expected_features):
    """Create a QR code and verify it matches expected features."""
    print(f"\n🔍 Testing: {test_name}")
    print(f"   Data: {qr_data}")
    print(f"   Config: {config}")

    try:
        # Create QR code with longer text to ensure minimum size
        qr = segno.make(qr_data)
        print(f"   ✓ QR Version: {qr.version} ({qr.symbol_size()[0]}x{qr.symbol_size()[1]})")

        # Generate SVG
        svg_path = f"/tmp/visual_test_{test_name.replace(' ', '_').replace('/', '_')}.svg"
        segnomms.write(qr, svg_path, **config)

        # Analyze SVG
        with open(svg_path, "r") as f:
            svg_content = f.read()

        # Parse SVG and analyze structure
        root = ET.fromstring(svg_content)
        analysis = analyze_svg_detailed(svg_content, root)

        # Verify expected features
        verification_results = verify_expected_features(analysis, expected_features)

        print(f"   ✓ SVG generated: {svg_path}")
        print(f"   ✓ Total modules: {analysis['total_modules']}")
        print(f"   ✓ Element types: {analysis['element_types']}")
        print(f"   ✓ Colors found: {analysis['colors']}")
        print(f"   ✓ CSS classes: {', '.join(list(analysis['css_classes'])[:5])}...")

        # Display verification results
        for feature, result in verification_results.items():
            status = "✅" if result["passed"] else "⚠️ "
            print(f"   {status} {feature}: {result['message']}")

        return {
            "test_name": test_name,
            "svg_path": svg_path,
            "analysis": analysis,
            "verification": verification_results,
            "success": all(r["passed"] for r in verification_results.values()),
        }

    except Exception as e:
        print(f"   ❌ Error: {e}")
        return {"test_name": test_name, "error": str(e), "success": False}


def analyze_svg_detailed(svg_content, root):
    """Perform detailed analysis of SVG structure."""
    analysis = {
        "total_modules": 0,
        "element_types": {},
        "colors": set(),
        "css_classes": set(),
        "has_background": False,
        "has_interactive": False,
        "has_tooltips": False,
        "svg_dimensions": {},
        "rounded_elements": 0,
        "stroke_elements": 0,
        "path_with_curves": 0,
    }

    # Get SVG dimensions
    analysis["svg_dimensions"] = {
        "width": root.get("width", ""),
        "height": root.get("height", ""),
        "viewBox": root.get("viewBox", ""),
    }

    # Analyze all elements
    for elem in root.iter():
        tag = elem.tag
        if tag in ["rect", "circle", "path", "polygon", "ellipse"]:
            analysis["total_modules"] += 1
            analysis["element_types"][tag] = analysis["element_types"].get(tag, 0) + 1

            # Check colors
            fill = elem.get("fill")
            stroke = elem.get("stroke")
            if fill:
                analysis["colors"].add(fill)
            if stroke:
                analysis["colors"].add(stroke)

            # Check CSS classes
            css_class = elem.get("class")
            if css_class:
                for cls in css_class.split():
                    analysis["css_classes"].add(cls)

            # Check for rounded elements
            if tag == "rect" and (elem.get("rx") or elem.get("ry")):
                analysis["rounded_elements"] += 1

            # Check for stroke elements
            if elem.get("stroke-width") or elem.get("stroke"):
                analysis["stroke_elements"] += 1

            # Check for curved paths
            if tag == "path":
                d = elem.get("d", "")
                if any(curve in d for curve in ["C", "S", "Q", "T", "A"]):
                    analysis["path_with_curves"] += 1

            # Check for interactive elements
            if elem.get("onclick") or elem.get("data-row") or elem.get("id"):
                analysis["has_interactive"] = True

        # Check for tooltips
        if elem.tag == "title":
            analysis["has_tooltips"] = True

        # Check for background
        if "background" in (elem.get("class") or ""):
            analysis["has_background"] = True

    return analysis


def verify_expected_features(analysis, expected_features):
    """Verify that the analysis matches expected features."""
    results = {}

    for feature, expectation in expected_features.items():
        if feature == "min_modules":
            passed = analysis["total_modules"] >= expectation
            results[feature] = {
                "passed": passed,
                "message": f"Expected ≥{expectation}, got {analysis['total_modules']}",
            }
        elif feature == "has_curves":
            has_curves = analysis["rounded_elements"] > 0 or analysis["path_with_curves"] > 0
            passed = has_curves == expectation
            results[feature] = {
                "passed": passed,
                "message": f"Expected curves: {expectation}, found: {has_curves} (rounded: {analysis['rounded_elements']}, curved paths: {analysis['path_with_curves']})",
            }
        elif feature == "primary_element_type":
            most_common = (
                max(analysis["element_types"].items(), key=lambda x: x[1])[0]
                if analysis["element_types"]
                else "none"
            )
            passed = most_common == expectation
            results[feature] = {"passed": passed, "message": f"Expected {expectation}, got {most_common}"}
        elif feature == "contains_color":
            passed = expectation.lower() in {c.lower() for c in analysis["colors"]}
            results[feature] = {
                "passed": passed,
                "message": f"Expected color {expectation}, found: {analysis['colors']}",
            }
        elif feature == "has_interactive":
            passed = analysis["has_interactive"] == expectation
            results[feature] = {
                "passed": passed,
                "message": f"Expected interactive: {expectation}, got {analysis['has_interactive']}",
            }
        elif feature == "has_tooltips":
            passed = analysis["has_tooltips"] == expectation
            results[feature] = {
                "passed": passed,
                "message": f"Expected tooltips: {expectation}, got {analysis['has_tooltips']}",
            }
        elif feature == "contains_css_class":
            passed = expectation in analysis["css_classes"]
            results[feature] = {
                "passed": passed,
                "message": f"Expected CSS class {expectation}, found: {list(analysis['css_classes'])[:10]}",
            }

    return results


def run_comprehensive_visual_tests():
    """Run comprehensive visual tests with verification."""
    print("🎨 Starting Visual QR Code Design Verification")
    print("=" * 60)

    # Ensure output directory
    os.makedirs("/tmp", exist_ok=True)

    test_results = []

    # Test 1: Basic Shape Variations
    print(f"\n📐 TESTING BASIC SHAPES")
    print("=" * 40)

    basic_shapes = [
        ("square", "rect"),
        ("circle", "circle"),
        ("rounded", "rect"),
        ("dot", "circle"),
        ("diamond", "polygon"),  # Corrected: uses polygon
        ("star", "polygon"),  # Corrected: uses polygon
        ("hexagon", "polygon"),  # Corrected: uses polygon
        ("triangle", "polygon"),  # Corrected: uses polygon
        ("cross", "path"),
    ]

    for shape, expected_element in basic_shapes:
        result = create_test_qr_with_verification(
            f"Basic Shape - {shape.title()}",
            f"Testing {shape} shape with sufficient content for proper QR code generation",
            {"shape": shape, "scale": 8, "border": 2, "dark": "#000000", "light": "#ffffff"},
            {
                "min_modules": 100,  # Expect reasonable number of modules
                "primary_element_type": expected_element,
                "contains_color": "#000000",
            },
        )
        test_results.append(result)

    # Test 2: Corner Radius Effects
    print(f"\n🔄 TESTING CORNER RADIUS EFFECTS")
    print("=" * 40)

    radius_tests = [(0.0, False), (0.3, True), (0.7, True), (1.0, True)]

    for radius, expect_curves in radius_tests:
        result = create_test_qr_with_verification(
            f"Corner Radius - {radius}",
            f"Testing corner radius {radius} with curve detection",
            {"shape": "rounded", "corner_radius": radius, "scale": 8, "border": 2},
            {"min_modules": 100, "has_curves": expect_curves, "primary_element_type": "rect"},
        )
        test_results.append(result)

    # Test 3: Color Configurations
    print(f"\n🎨 TESTING COLOR CONFIGURATIONS")
    print("=" * 40)

    color_tests = [
        ("#000000", "#ffffff", "Classic"),
        ("#1e40af", "#dbeafe", "Blue"),
        ("#166534", "#dcfce7", "Green"),
        ("#7c3aed", "#ede9fe", "Purple"),
    ]

    for dark, light, name in color_tests:
        result = create_test_qr_with_verification(
            f"Color Theme - {name}",
            f"Testing {name.lower()} color theme with custom colors",
            {"shape": "square", "scale": 6, "border": 2, "dark": dark, "light": light},
            {"min_modules": 100, "contains_color": dark, "primary_element_type": "rect"},
        )
        test_results.append(result)

    # Test 4: Safe Mode Comparison
    print(f"\n🛡️  TESTING SAFE MODE")
    print("=" * 40)

    safe_mode_tests = [(True, "Safe Mode ON"), (False, "Safe Mode OFF")]

    for safe_mode, name in safe_mode_tests:
        result = create_test_qr_with_verification(
            f"Safety - {name}",
            f"Testing safe mode configuration to protect functional patterns",
            {
                "shape": "star",  # Complex shape to test safe mode
                "corner_radius": 0.4,
                "safe_mode": safe_mode,
                "scale": 8,
                "border": 2,
            },
            {"min_modules": 100, "primary_element_type": "rect" if safe_mode else "path"},
        )
        test_results.append(result)

    # Test 5: Interactive Features
    print(f"\n🖱️  TESTING INTERACTIVE FEATURES")
    print("=" * 40)

    interactive_tests = [
        (False, False, "Static"),
        (True, False, "Interactive Only"),
        (True, True, "Interactive + Tooltips"),
    ]

    for interactive, tooltips, name in interactive_tests:
        result = create_test_qr_with_verification(
            f"Interactive - {name}",
            f"Testing interactive features and tooltip generation",
            {"shape": "rounded", "scale": 6, "border": 2, "interactive": interactive, "tooltips": tooltips},
            {
                "min_modules": 100,
                "has_interactive": interactive,
                "has_tooltips": tooltips,
                "primary_element_type": "rect",
            },
        )
        test_results.append(result)

    # Test 6: Advanced Connected Shapes
    print(f"\n🔗 TESTING CONNECTED SHAPES")
    print("=" * 40)

    connected_shapes = [
        "connected",
        "connected-extra-rounded",
        "connected-classy",
        "connected-classy-rounded",
    ]

    for shape in connected_shapes:
        result = create_test_qr_with_verification(
            f"Connected - {shape}",
            f"Testing connected shape rendering with advanced algorithms",
            {"shape": shape, "scale": 8, "border": 2, "enable_phase1": True, "enable_phase2": True},
            {"min_modules": 100, "primary_element_type": "path"},  # Connected shapes usually use paths
        )
        test_results.append(result)

    return test_results


def generate_summary_report(test_results):
    """Generate comprehensive summary report."""
    print("\n" + "=" * 80)
    print("🎯 VISUAL VERIFICATION SUMMARY REPORT")
    print("=" * 80)

    total_tests = len(test_results)
    successful_tests = sum(1 for r in test_results if r.get("success", False))

    print(f"\n📊 Overall Results:")
    print(f"   Total tests: {total_tests}")
    print(f"   Successful: {successful_tests}")
    print(f"   Success rate: {(successful_tests / total_tests * 100):.1f}%")

    # Group by category
    categories = {}
    for result in test_results:
        if not result.get("success", False):
            continue

        test_name = result["test_name"]
        category = test_name.split(" - ")[0]
        if category not in categories:
            categories[category] = []
        categories[category].append(result)

    print(f"\n📈 Results by Category:")
    for category, results in categories.items():
        print(f"\n   {category}:")
        for result in results:
            test_name = result["test_name"]
            analysis = result.get("analysis", {})
            verification = result.get("verification", {})

            passed_checks = sum(1 for v in verification.values() if v["passed"])
            total_checks = len(verification)

            status = "✅" if result["success"] else "❌"
            print(f"     {status} {test_name}: {passed_checks}/{total_checks} checks passed")
            print(
                f"        Modules: {analysis.get('total_modules', 0)}, "
                f"Elements: {analysis.get('element_types', {})}"
            )

    # Show failures
    failures = [r for r in test_results if not r.get("success", False)]
    if failures:
        print(f"\n❌ Failed Tests:")
        for failure in failures:
            print(f"   - {failure['test_name']}: {failure.get('error', 'Unknown error')}")

    # Show generated files
    print(f"\n📁 Generated Files:")
    svg_files = [r["svg_path"] for r in test_results if r.get("svg_path")]
    print(f"   {len(svg_files)} SVG files generated in /tmp/")
    print(f"   Example: {svg_files[0] if svg_files else 'None'}")

    if successful_tests == total_tests:
        print("\n🎉 ALL VISUAL TESTS PASSED!")
        print("✓ QR code designs are generating correctly")
        print("✓ Shape configurations are working as expected")
        print("✓ Color and styling options are being applied")
        print("✓ Interactive features are functioning properly")
    else:
        print("\n⚠️  Some tests failed - review details above")


def main():
    """Main verification routine."""
    print("🔍 Visual QR Code Design Verification")
    print("This creates QR codes with different configurations and verifies")
    print("that the visual output matches the expected design parameters.\n")

    try:
        test_results = run_comprehensive_visual_tests()
        generate_summary_report(test_results)

    except KeyboardInterrupt:
        print("\n⚠️  Verification interrupted by user")
    except Exception as e:
        print(f"\n❌ Verification failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
