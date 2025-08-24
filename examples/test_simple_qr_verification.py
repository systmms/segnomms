#!/usr/bin/env python3
"""
Simple QR Code Design Verification

Direct verification of QR code generation and visual characteristics
using text analysis of SVG files.
"""

import os
import sys
import segno
import re
from pathlib import Path

# Add the segnomms package to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import segnomms
except ImportError as e:
    print(f"Failed to import segnomms: {e}")
    sys.exit(1)

def analyze_svg_content(svg_content, test_name):
    """Analyze SVG content using direct text analysis."""
    print(f"\n🔍 Analyzing: {test_name}")
    
    # Count different element types
    rect_count = len(re.findall(r'<rect[^>]*>', svg_content))
    circle_count = len(re.findall(r'<circle[^>]*>', svg_content))  
    path_count = len(re.findall(r'<path[^>]*>', svg_content))
    polygon_count = len(re.findall(r'<polygon[^>]*>', svg_content))
    
    # Check for specific attributes
    has_rounded = bool(re.search(r'rx=|ry=', svg_content))
    has_curves = bool(re.search(r'[CQT]', svg_content))  # SVG curve commands
    has_stroke = bool(re.search(r'stroke-width=', svg_content))
    has_interactive = bool(re.search(r'data-row=|onclick=', svg_content))
    has_tooltips = bool(re.search(r'<title>', svg_content))
    
    # Extract colors
    colors = set(re.findall(r'fill="([^"]*)"', svg_content))
    colors.update(re.findall(r'stroke="([^"]*)"', svg_content))
    
    # Extract CSS classes
    css_classes = set()
    for match in re.findall(r'class="([^"]*)"', svg_content):
        css_classes.update(match.split())
    
    total_elements = rect_count + circle_count + path_count + polygon_count
    
    print(f"   📊 Element counts:")
    print(f"      Rectangles: {rect_count}")
    print(f"      Circles: {circle_count}")
    print(f"      Paths: {path_count}")
    print(f"      Polygons: {polygon_count}")
    print(f"      Total: {total_elements}")
    
    print(f"   🎨 Visual features:")
    print(f"      Rounded elements: {has_rounded}")
    print(f"      Curved paths: {has_curves}")  
    print(f"      Stroke elements: {has_stroke}")
    print(f"      Interactive: {has_interactive}")
    print(f"      Tooltips: {has_tooltips}")
    
    print(f"   🌈 Colors: {colors}")
    print(f"   🎯 Key CSS classes: {list(css_classes)[:5]}")
    
    return {
        'rect_count': rect_count,
        'circle_count': circle_count,
        'path_count': path_count,
        'polygon_count': polygon_count,
        'total_elements': total_elements,
        'has_rounded': has_rounded,
        'has_curves': has_curves,
        'has_stroke': has_stroke,
        'has_interactive': has_interactive,
        'has_tooltips': has_tooltips,
        'colors': colors,
        'css_classes': css_classes
    }

def test_shape_variations():
    """Test basic shape variations with direct verification."""
    print("=" * 60)
    print("🎨 TESTING SHAPE VARIATIONS")
    print("=" * 60)
    
    shapes_to_test = [
        ('square', 'rect'),
        ('circle', 'circle'),  
        ('rounded', 'rect'),
        ('dot', 'circle'),
        ('diamond', 'polygon'),  # Uses polygon, not path
        ('star', 'polygon'),     # Uses polygon, not path
        ('hexagon', 'polygon'),  # Uses polygon, not path
        ('triangle', 'polygon'), # Uses polygon, not path
        ('cross', 'path')
    ]
    
    results = []
    
    for shape, expected_primary in shapes_to_test:
        try:
            # Create QR with enough content 
            qr = segno.make(f"Testing {shape} shape with comprehensive content for adequate QR code size and verification")
            
            # Generate SVG
            svg_path = f"/tmp/shape_test_{shape}.svg"
            segnomms.write(qr, svg_path,
                          shape=shape,
                          scale=8,
                          border=2,
                          dark='#000000',
                          light='#ffffff')
            
            # Read and analyze
            with open(svg_path, 'r') as f:
                svg_content = f.read()
            
            analysis = analyze_svg_content(svg_content, f"{shape.title()} Shape")
            
            # Verify primary element type
            element_counts = {
                'rect': analysis['rect_count'],
                'circle': analysis['circle_count'], 
                'path': analysis['path_count'],
                'polygon': analysis['polygon_count']
            }
            
            primary_element = max(element_counts.items(), key=lambda x: x[1])[0]
            
            success = (analysis['total_elements'] > 50 and  # Reasonable number of elements
                      primary_element == expected_primary and  # Correct element type
                      '#000000' in analysis['colors'])  # Correct color
            
            print(f"   ✅ Primary element: {primary_element} (expected: {expected_primary})")
            print(f"   ✅ Verification: {'PASSED' if success else 'FAILED'}")
            
            results.append({
                'shape': shape,
                'analysis': analysis,
                'primary_element': primary_element,
                'expected_primary': expected_primary,
                'success': success,
                'svg_path': svg_path
            })
            
        except Exception as e:
            print(f"   ❌ Error testing {shape}: {e}")
            results.append({
                'shape': shape,
                'error': str(e),
                'success': False
            })
    
    return results

def test_corner_radius():
    """Test corner radius configurations."""
    print("\n" + "=" * 60)
    print("🔄 TESTING CORNER RADIUS")
    print("=" * 60)
    
    radius_values = [0.0, 0.3, 0.7, 1.0]
    results = []
    
    for radius in radius_values:
        try:
            qr = segno.make(f"Corner radius test {radius} with sufficient content")
            
            svg_path = f"/tmp/radius_test_{radius}.svg"
            segnomms.write(qr, svg_path,
                          shape='rounded',
                          corner_radius=radius,
                          scale=8,
                          border=2)
            
            with open(svg_path, 'r') as f:
                svg_content = f.read()
            
            analysis = analyze_svg_content(svg_content, f"Corner Radius {radius}")
            
            # For radius > 0, we should see either rounded rectangles or curved paths
            expected_curves = radius > 0.0
            has_curves = analysis['has_rounded'] or analysis['has_curves']
            
            success = (analysis['total_elements'] > 50 and
                      has_curves == expected_curves)
            
            print(f"   ✅ Curves expected: {expected_curves}, found: {has_curves}")
            print(f"   ✅ Verification: {'PASSED' if success else 'FAILED'}")
            
            results.append({
                'radius': radius,
                'analysis': analysis,
                'expected_curves': expected_curves,
                'found_curves': has_curves,
                'success': success,
                'svg_path': svg_path
            })
            
        except Exception as e:
            print(f"   ❌ Error testing radius {radius}: {e}")
            results.append({
                'radius': radius,
                'error': str(e),
                'success': False
            })
    
    return results

def test_colors():
    """Test color configurations."""
    print("\n" + "=" * 60)
    print("🌈 TESTING COLOR CONFIGURATIONS")
    print("=" * 60)
    
    color_tests = [
        ('#000000', '#ffffff', 'Classic'),
        ('#1e40af', '#dbeafe', 'Blue'),
        ('#166534', '#dcfce7', 'Green'),
        ('#7c3aed', '#ede9fe', 'Purple')
    ]
    
    results = []
    
    for dark, light, name in color_tests:
        try:
            qr = segno.make(f"Color test {name.lower()} theme with custom styling")
            
            svg_path = f"/tmp/color_test_{name.lower()}.svg"
            segnomms.write(qr, svg_path,
                          shape='square',
                          scale=6,
                          border=2,
                          dark=dark,
                          light=light)
            
            with open(svg_path, 'r') as f:
                svg_content = f.read()
            
            analysis = analyze_svg_content(svg_content, f"{name} Color Theme")
            
            # Verify colors are applied
            has_dark_color = dark.lower() in {c.lower() for c in analysis['colors']}
            has_light_color = light.lower() in {c.lower() for c in analysis['colors']}
            
            success = (analysis['total_elements'] > 50 and
                      has_dark_color)  # At least dark color should be present
            
            print(f"   ✅ Dark color ({dark}): {'found' if has_dark_color else 'not found'}")
            print(f"   ✅ Light color ({light}): {'found' if has_light_color else 'not found'}")
            print(f"   ✅ Verification: {'PASSED' if success else 'FAILED'}")
            
            results.append({
                'name': name,
                'dark': dark,
                'light': light,
                'analysis': analysis,
                'has_dark_color': has_dark_color,
                'has_light_color': has_light_color,
                'success': success,
                'svg_path': svg_path
            })
            
        except Exception as e:
            print(f"   ❌ Error testing {name}: {e}")
            results.append({
                'name': name,
                'error': str(e),
                'success': False
            })
    
    return results

def test_interactive_features():
    """Test interactive features."""
    print("\n" + "=" * 60)
    print("🖱️ TESTING INTERACTIVE FEATURES")
    print("=" * 60)
    
    interactive_tests = [
        (False, False, 'Static'),
        (True, False, 'Interactive Only'),
        (True, True, 'Interactive + Tooltips')
    ]
    
    results = []
    
    for interactive, tooltips, name in interactive_tests:
        try:
            qr = segno.make(f"Interactive test {name.lower()} configuration")
            
            svg_path = f"/tmp/interactive_test_{name.lower().replace(' ', '_').replace('+', '_')}.svg"
            segnomms.write(qr, svg_path,
                          shape='rounded',
                          scale=6,
                          border=2,
                          interactive=interactive,
                          tooltips=tooltips)
            
            with open(svg_path, 'r') as f:
                svg_content = f.read()
            
            analysis = analyze_svg_content(svg_content, f"{name} Interactive")
            
            success = (analysis['total_elements'] > 50 and
                      analysis['has_interactive'] == interactive and
                      analysis['has_tooltips'] == tooltips)
            
            print(f"   ✅ Interactive: expected {interactive}, found {analysis['has_interactive']}")
            print(f"   ✅ Tooltips: expected {tooltips}, found {analysis['has_tooltips']}")
            print(f"   ✅ Verification: {'PASSED' if success else 'FAILED'}")
            
            results.append({
                'name': name,
                'interactive': interactive,
                'tooltips': tooltips,
                'analysis': analysis,
                'success': success,
                'svg_path': svg_path
            })
            
        except Exception as e:
            print(f"   ❌ Error testing {name}: {e}")
            results.append({
                'name': name,
                'error': str(e),
                'success': False
            })
    
    return results

def test_safe_mode():
    """Test safe mode configurations."""
    print("\n" + "=" * 60)
    print("🛡️ TESTING SAFE MODE")
    print("=" * 60)
    
    safe_mode_tests = [
        (True, 'Safe Mode ON - Functional patterns as squares'),
        (False, 'Safe Mode OFF - All patterns use custom shapes')
    ]
    
    results = []
    
    for safe_mode, description in safe_mode_tests:
        try:
            qr = segno.make(f"Safe mode test {description}")
            
            svg_path = f"/tmp/safe_mode_test_{safe_mode}.svg"
            segnomms.write(qr, svg_path,
                          shape='star',  # Complex shape to test safe mode  
                          corner_radius=0.4,
                          safe_mode=safe_mode,
                          scale=8,
                          border=2)
            
            with open(svg_path, 'r') as f:
                svg_content = f.read()
            
            analysis = analyze_svg_content(svg_content, description)
            
            # In safe mode, we should see more rectangles (for functional patterns)
            # In non-safe mode, we should see more paths (for star shapes)
            rect_ratio = analysis['rect_count'] / max(analysis['total_elements'], 1)
            path_ratio = analysis['path_count'] / max(analysis['total_elements'], 1)
            
            if safe_mode:
                # Safe mode: functional patterns should be rectangles
                success = analysis['total_elements'] > 50 and rect_ratio > 0.3
                print(f"   ✅ Rectangle ratio: {rect_ratio:.2f} (expected > 0.3 for safe mode)")
            else:
                # Non-safe mode: more complex shapes (paths) expected
                success = analysis['total_elements'] > 50 and path_ratio > 0.1
                print(f"   ✅ Path ratio: {path_ratio:.2f} (expected > 0.1 for custom shapes)")
            
            print(f"   ✅ Verification: {'PASSED' if success else 'FAILED'}")
            
            results.append({
                'safe_mode': safe_mode,
                'description': description,
                'analysis': analysis,
                'rect_ratio': rect_ratio,
                'path_ratio': path_ratio,
                'success': success,
                'svg_path': svg_path
            })
            
        except Exception as e:
            print(f"   ❌ Error testing safe mode {safe_mode}: {e}")
            results.append({
                'safe_mode': safe_mode,
                'error': str(e),
                'success': False
            })
    
    return results

def generate_final_report(all_results):
    """Generate comprehensive final report."""
    print("\n" + "=" * 80)
    print("🎯 COMPREHENSIVE QR CODE VERIFICATION REPORT")
    print("=" * 80)
    
    total_tests = sum(len(results) for results in all_results.values())
    successful_tests = sum(len([r for r in results if r.get('success', False)]) 
                          for results in all_results.values())
    
    print(f"\n📊 Overall Results:")
    print(f"   Total tests run: {total_tests}")
    print(f"   Successful tests: {successful_tests}")
    print(f"   Overall success rate: {(successful_tests/total_tests*100):.1f}%")
    
    print(f"\n📈 Results by Category:")
    
    for category, results in all_results.items():
        successful = [r for r in results if r.get('success', False)]
        print(f"\n   🔍 {category.upper().replace('_', ' ')}:")
        print(f"      Tests: {len(results)}")  
        print(f"      Successful: {len(successful)}")
        print(f"      Success rate: {(len(successful)/len(results)*100):.1f}%")
        
        # Show specific insights for each category
        if category == 'shapes' and successful:
            shapes_working = [r['shape'] for r in successful]
            print(f"      Working shapes: {', '.join(shapes_working)}")
        
        elif category == 'corner_radius' and successful:
            radius_working = [f"{r['radius']}" for r in successful]
            print(f"      Working radius values: {', '.join(radius_working)}")
        
        elif category == 'colors' and successful:
            colors_working = [r['name'] for r in successful]
            print(f"      Working color themes: {', '.join(colors_working)}")
    
    # Show any failures
    all_failures = []
    for results in all_results.values():
        all_failures.extend([r for r in results if not r.get('success', False)])
    
    if all_failures:
        print(f"\n❌ Failed Tests ({len(all_failures)}):")
        for failure in all_failures[:5]:  # Show first 5 failures
            error = failure.get('error', 'Verification criteria not met')
            name = failure.get('shape') or failure.get('name') or failure.get('description', 'Unknown')
            print(f"   - {name}: {error}")
        if len(all_failures) > 5:
            print(f"   ... and {len(all_failures) - 5} more")
    
    print(f"\n📁 Generated Files:")
    all_svg_files = []
    for results in all_results.values():
        all_svg_files.extend([r.get('svg_path') for r in results if r.get('svg_path')])
    
    print(f"   {len(all_svg_files)} SVG files generated in /tmp/")
    if all_svg_files:
        print(f"   Example: {all_svg_files[0]}")
    
    # Final assessment
    if successful_tests >= total_tests * 0.8:  # 80% success rate
        print("\n🎉 QR CODE DESIGN VERIFICATION: EXCELLENT!")
        print("✅ Most configurations are working correctly")
        print("✅ Visual designs match expected parameters")
        print("✅ Plugin functionality is operating as intended")
    elif successful_tests >= total_tests * 0.6:  # 60% success rate
        print("\n👍 QR CODE DESIGN VERIFICATION: GOOD")
        print("✅ Many configurations are working correctly")
        print("⚠️ Some issues detected - review failed tests")
    else:
        print("\n⚠️ QR CODE DESIGN VERIFICATION: NEEDS ATTENTION")
        print("❌ Multiple configuration issues detected")
        print("❌ Review implementation and test results")

def main():
    """Main verification routine."""
    print("🔍 Simple QR Code Design Verification")
    print("Direct analysis of generated SVG files to verify design configurations\n")
    
    os.makedirs("/tmp", exist_ok=True)
    
    try:
        all_results = {}
        
        # Run all test categories
        all_results['shapes'] = test_shape_variations()
        all_results['corner_radius'] = test_corner_radius()
        all_results['colors'] = test_colors()
        all_results['interactive'] = test_interactive_features()
        all_results['safe_mode'] = test_safe_mode()
        
        # Generate comprehensive report
        generate_final_report(all_results)
        
    except KeyboardInterrupt:
        print("\n⚠️ Verification interrupted by user")
    except Exception as e:
        print(f"\n❌ Verification failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()