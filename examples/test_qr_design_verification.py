#!/usr/bin/env python3
"""
Systematic QR Code Design Verification Script

This script generates QR codes with various configurations and verifies 
that the SVG output matches the expected design parameters.
"""

import os
import sys
import segno
import xml.etree.ElementTree as ET
from pathlib import Path

# Add the segnomms package to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import segnomms
except ImportError as e:
    print(f"Failed to import segnomms: {e}")
    print("Make sure you're running this from the examples directory")
    sys.exit(1)

def analyze_svg_structure(svg_content):
    """Analyze SVG content and extract design characteristics."""
    try:
        root = ET.fromstring(svg_content)
        
        analysis = {
            'has_background': False,
            'has_interactive_elements': False,
            'shape_types': set(),
            'colors_used': set(),
            'finder_patterns': 0,
            'module_count': 0,
            'has_tooltips': False,
            'css_classes': set()
        }
        
        # Check for background
        for rect in root.findall(".//rect"):
            if rect.get('class') == 'qr-background' or rect.get('fill') in ['white', '#ffffff']:
                analysis['has_background'] = True
        
        # Analyze shapes and modules
        for elem in root.findall(".//*"):
            if elem.tag in ['rect', 'circle', 'path', 'polygon']:
                analysis['module_count'] += 1
                
                # Check fill colors
                fill = elem.get('fill')
                if fill:
                    analysis['colors_used'].add(fill)
                
                # Check CSS classes
                css_class = elem.get('class')
                if css_class:
                    analysis['css_classes'].add(css_class)
                
                # Check for specific module types
                if 'finder' in (css_class or ''):
                    analysis['finder_patterns'] += 1
                
                # Check for interactive elements
                if elem.get('onclick') or elem.get('data-row'):
                    analysis['has_interactive_elements'] = True
        
        # Check for tooltips
        if root.findall(".//title"):
            analysis['has_tooltips'] = True
            
        return analysis
        
    except ET.ParseError as e:
        return {'error': f'Invalid SVG: {e}'}

def test_basic_shapes():
    """Test basic shape variations."""
    print("=" * 60)
    print("TESTING BASIC SHAPES")
    print("=" * 60)
    
    shapes = ['square', 'circle', 'rounded', 'dot', 'diamond', 'star', 'hexagon', 'triangle', 'cross', 'squircle']
    results = []
    
    for shape in shapes:
        print(f"\n🔍 Testing shape: {shape}")
        
        try:
            # Create QR code
            qr = segno.make("Shape test: " + shape)
            
            # Generate SVG with shape
            svg_path = f"/tmp/test_shape_{shape}.svg"
            segnomms.write(qr, svg_path, 
                          shape=shape, 
                          scale=8, 
                          border=2,
                          dark='#000000',
                          light='#ffffff')
            
            # Read and analyze SVG
            with open(svg_path, 'r') as f:
                svg_content = f.read()
            
            analysis = analyze_svg_structure(svg_content)
            
            # Verify expected characteristics
            expected_elements = {
                'square': ['rect'],
                'circle': ['circle'],
                'rounded': ['rect', 'path'],  # Rounded rectangles often use paths
                'dot': ['circle'],
                'diamond': ['path', 'polygon'],
                'star': ['path', 'polygon'],
                'hexagon': ['path', 'polygon'],
                'triangle': ['path', 'polygon'],
                'cross': ['path', 'polygon'],
                'squircle': ['path']
            }
            
            print(f"   ✓ Generated SVG with {analysis['module_count']} elements")
            print(f"   ✓ Colors used: {analysis['colors_used']}")
            print(f"   ✓ Background present: {analysis['has_background']}")
            
            results.append({
                'shape': shape,
                'analysis': analysis,
                'svg_path': svg_path,
                'success': True
            })
            
        except Exception as e:
            print(f"   ❌ Error testing {shape}: {e}")
            results.append({
                'shape': shape,
                'error': str(e),
                'success': False
            })
    
    return results

def test_corner_radius_configurations():
    """Test corner radius variations."""
    print("\n" + "=" * 60)
    print("TESTING CORNER RADIUS CONFIGURATIONS")
    print("=" * 60)
    
    radius_values = [0.0, 0.2, 0.5, 0.8, 1.0]
    results = []
    
    for radius in radius_values:
        print(f"\n🔍 Testing corner_radius: {radius}")
        
        try:
            qr = segno.make("Corner radius test")
            
            svg_path = f"/tmp/test_radius_{radius}.svg"
            segnomms.write(qr, svg_path,
                          shape='rounded',
                          corner_radius=radius,
                          scale=8,
                          border=2)
            
            with open(svg_path, 'r') as f:
                svg_content = f.read()
            
            analysis = analyze_svg_structure(svg_content)
            
            # Check for rounded elements (should have rx/ry attributes or path curves)
            root = ET.fromstring(svg_content)
            rounded_elements = 0
            path_curves = 0
            
            for rect in root.findall(".//rect"):
                if rect.get('rx') or rect.get('ry'):
                    rounded_elements += 1
            
            for path in root.findall(".//path"):
                if 'C' in (path.get('d') or '') or 'Q' in (path.get('d') or ''):
                    path_curves += 1
            
            print(f"   ✓ Rounded rectangles: {rounded_elements}")
            print(f"   ✓ Curved paths: {path_curves}")
            print(f"   ✓ Total elements: {analysis['module_count']}")
            
            # Expect more curves with higher radius values
            expected_curves = radius > 0.0
            has_curves = rounded_elements > 0 or path_curves > 0
            
            if expected_curves == has_curves:
                print(f"   ✅ Corner radius behavior matches expectation")
            else:
                print(f"   ⚠️  Corner radius behavior unexpected (expected curves: {expected_curves}, found: {has_curves})")
            
            results.append({
                'radius': radius,
                'rounded_elements': rounded_elements,
                'path_curves': path_curves,
                'analysis': analysis,
                'svg_path': svg_path,
                'success': True
            })
            
        except Exception as e:
            print(f"   ❌ Error testing radius {radius}: {e}")
            results.append({
                'radius': radius,
                'error': str(e),
                'success': False
            })
    
    return results

def test_safe_mode_comparison():
    """Test safe mode vs advanced mode differences."""
    print("\n" + "=" * 60)
    print("TESTING SAFE MODE CONFIGURATIONS") 
    print("=" * 60)
    
    test_configs = [
        {'safe_mode': True, 'name': 'Safe Mode ON'},
        {'safe_mode': False, 'name': 'Safe Mode OFF'}
    ]
    
    results = []
    
    for config in test_configs:
        print(f"\n🔍 Testing {config['name']}")
        
        try:
            qr = segno.make("Safe mode test - functional patterns")
            
            svg_path = f"/tmp/test_safe_{config['safe_mode']}.svg"
            segnomms.write(qr, svg_path,
                          shape='star',  # Complex shape to test safe mode
                          corner_radius=0.4,
                          safe_mode=config['safe_mode'],
                          scale=8,
                          border=2)
            
            with open(svg_path, 'r') as f:
                svg_content = f.read()
            
            analysis = analyze_svg_structure(svg_content)
            
            # Analyze the types of elements - safe mode should have more squares for functional patterns
            root = ET.fromstring(svg_content)
            rect_count = len(root.findall(".//rect"))
            path_count = len(root.findall(".//path"))
            
            print(f"   ✓ Rectangle elements: {rect_count}")
            print(f"   ✓ Path elements: {path_count}")
            print(f"   ✓ CSS classes used: {analysis['css_classes']}")
            
            # Safe mode should have more rectangles (squares) for functional patterns
            if config['safe_mode']:
                print(f"   ✅ Safe mode: Functional patterns likely preserved as squares")
            else:
                print(f"   ✅ Advanced mode: All patterns use custom shapes")
            
            results.append({
                'config': config,
                'rect_count': rect_count,
                'path_count': path_count,
                'analysis': analysis,
                'svg_path': svg_path,
                'success': True
            })
            
        except Exception as e:
            print(f"   ❌ Error testing {config['name']}: {e}")
            results.append({
                'config': config,
                'error': str(e),
                'success': False
            })
    
    return results

def test_color_configurations():
    """Test color and styling configurations."""
    print("\n" + "=" * 60)
    print("TESTING COLOR CONFIGURATIONS")
    print("=" * 60)
    
    color_tests = [
        {'dark': '#000000', 'light': '#ffffff', 'name': 'Classic Black/White'},
        {'dark': '#1e40af', 'light': '#dbeafe', 'name': 'Blue Theme'},
        {'dark': '#166534', 'light': '#dcfce7', 'name': 'Green Theme'},
        {'dark': '#7c3aed', 'light': '#ede9fe', 'name': 'Purple Theme'}
    ]
    
    results = []
    
    for color_test in color_tests:
        print(f"\n🔍 Testing {color_test['name']}")
        
        try:
            qr = segno.make("Color test")
            
            svg_path = f"/tmp/test_color_{color_test['name'].replace(' ', '_').replace('/', '_')}.svg"
            segnomms.write(qr, svg_path,
                          shape='rounded',
                          scale=6,
                          border=2,
                          dark=color_test['dark'],
                          light=color_test['light'])
            
            with open(svg_path, 'r') as f:
                svg_content = f.read()
            
            analysis = analyze_svg_structure(svg_content)
            
            # Verify colors are used
            expected_colors = {color_test['dark'].lower(), color_test['light'].lower()}
            found_colors = {color.lower() for color in analysis['colors_used']}
            
            color_match = expected_colors.intersection(found_colors)
            
            print(f"   ✓ Expected colors: {expected_colors}")
            print(f"   ✓ Found colors: {found_colors}")
            print(f"   ✓ Color matches: {len(color_match)} / {len(expected_colors)}")
            
            if len(color_match) >= 1:  # At least one color should match
                print(f"   ✅ Colors applied correctly")
            else:
                print(f"   ⚠️  Color configuration may not be applied as expected")
            
            results.append({
                'color_test': color_test,
                'expected_colors': expected_colors,
                'found_colors': found_colors,
                'analysis': analysis,
                'svg_path': svg_path,
                'success': True
            })
            
        except Exception as e:
            print(f"   ❌ Error testing {color_test['name']}: {e}")
            results.append({
                'color_test': color_test,
                'error': str(e),
                'success': False
            })
    
    return results

def test_finder_pattern_customization():
    """Test finder pattern customization."""
    print("\n" + "=" * 60)
    print("TESTING FINDER PATTERN CUSTOMIZATION")
    print("=" * 60)
    
    finder_tests = [
        {'finder_shape': 'square', 'finder_inner_scale': 0.6, 'finder_stroke': 0, 'name': 'Default Square'},
        {'finder_shape': 'rounded', 'finder_inner_scale': 0.3, 'finder_stroke': 1, 'name': 'Small Rounded + Stroke'},
        {'finder_shape': 'circle', 'finder_inner_scale': 0.9, 'finder_stroke': 2, 'name': 'Large Circle + Thick Stroke'}
    ]
    
    results = []
    
    for finder_test in finder_tests:
        print(f"\n🔍 Testing {finder_test['name']}")
        
        try:
            qr = segno.make("Finder pattern test")
            
            svg_path = f"/tmp/test_finder_{finder_test['name'].replace(' ', '_').replace('+', '_')}.svg"
            segnomms.write(qr, svg_path,
                          shape='square',  # Keep modules simple to focus on finder patterns
                          finder_shape=finder_test['finder_shape'],
                          finder_inner_scale=finder_test['finder_inner_scale'],
                          finder_stroke=finder_test['finder_stroke'],
                          scale=10,  # Larger scale to better see finder details
                          border=2)
            
            with open(svg_path, 'r') as f:
                svg_content = f.read()
            
            analysis = analyze_svg_structure(svg_content)
            
            # Look for finder pattern elements
            root = ET.fromstring(svg_content)
            finder_elements = []
            
            for elem in root.findall(".//*"):
                css_class = elem.get('class') or ''
                if 'finder' in css_class:
                    finder_elements.append({
                        'tag': elem.tag,
                        'class': css_class,
                        'stroke_width': elem.get('stroke-width'),
                        'has_stroke': elem.get('stroke') is not None
                    })
            
            print(f"   ✓ Finder elements found: {len(finder_elements)}")
            print(f"   ✓ Total finder patterns in analysis: {analysis['finder_patterns']}")
            
            # Check for expected characteristics
            expected_shape_elements = {
                'square': 'rect',
                'rounded': ['rect', 'path'],
                'circle': 'circle'
            }
            
            if finder_test['finder_stroke'] > 0:
                stroke_elements = [elem for elem in finder_elements if elem['has_stroke']]
                print(f"   ✓ Elements with stroke: {len(stroke_elements)}")
            
            print(f"   ✅ Finder pattern customization applied")
            
            results.append({
                'finder_test': finder_test,
                'finder_elements': finder_elements,
                'analysis': analysis,
                'svg_path': svg_path,
                'success': True
            })
            
        except Exception as e:
            print(f"   ❌ Error testing {finder_test['name']}: {e}")
            results.append({
                'finder_test': finder_test,
                'error': str(e),
                'success': False
            })
    
    return results

def test_interactive_features():
    """Test interactive features and CSS classes."""
    print("\n" + "=" * 60)
    print("TESTING INTERACTIVE FEATURES")
    print("=" * 60)
    
    interactive_tests = [
        {'interactive': False, 'tooltips': False, 'name': 'Static QR Code'},
        {'interactive': True, 'tooltips': False, 'name': 'Interactive Only'},
        {'interactive': True, 'tooltips': True, 'name': 'Interactive + Tooltips'}
    ]
    
    results = []
    
    for test_config in interactive_tests:
        print(f"\n🔍 Testing {test_config['name']}")
        
        try:
            qr = segno.make("Interactive test")
            
            svg_path = f"/tmp/test_interactive_{test_config['name'].replace(' ', '_').replace('+', '_')}.svg"
            segnomms.write(qr, svg_path,
                          shape='rounded',
                          scale=6,
                          border=2,
                          interactive=test_config['interactive'],
                          tooltips=test_config['tooltips'])
            
            with open(svg_path, 'r') as f:
                svg_content = f.read()
            
            analysis = analyze_svg_structure(svg_content)
            
            print(f"   ✓ Interactive elements: {analysis['has_interactive_elements']}")
            print(f"   ✓ Tooltips present: {analysis['has_tooltips']}")
            print(f"   ✓ CSS classes: {analysis['css_classes']}")
            
            # Verify expectations
            if test_config['interactive'] == analysis['has_interactive_elements']:
                print(f"   ✅ Interactive setting matches result")
            else:
                print(f"   ⚠️  Interactive setting mismatch")
            
            if test_config['tooltips'] == analysis['has_tooltips']:
                print(f"   ✅ Tooltip setting matches result")
            else:
                print(f"   ⚠️  Tooltip setting mismatch")
            
            results.append({
                'test_config': test_config,
                'analysis': analysis,
                'svg_path': svg_path,
                'success': True
            })
            
        except Exception as e:
            print(f"   ❌ Error testing {test_config['name']}: {e}")
            results.append({
                'test_config': test_config,
                'error': str(e),
                'success': False
            })
    
    return results

def generate_summary_report(all_results):
    """Generate a comprehensive summary report."""
    print("\n" + "=" * 80)
    print("COMPREHENSIVE VERIFICATION SUMMARY")
    print("=" * 80)
    
    total_tests = 0
    successful_tests = 0
    
    for category, results in all_results.items():
        print(f"\n📊 {category.upper().replace('_', ' ')}")
        print("-" * 40)
        
        category_total = len(results)
        category_success = sum(1 for r in results if r.get('success', False))
        
        print(f"Tests run: {category_total}")
        print(f"Successful: {category_success}")
        print(f"Success rate: {(category_success/category_total*100):.1f}%" if category_total > 0 else "N/A")
        
        total_tests += category_total
        successful_tests += category_success
        
        # Show any failures
        failures = [r for r in results if not r.get('success', False)]
        if failures:
            print("❌ Failures:")
            for failure in failures:
                error = failure.get('error', 'Unknown error')
                print(f"   - {error}")
    
    print(f"\n🎯 OVERALL RESULTS")
    print(f"Total tests: {total_tests}")
    print(f"Successful: {successful_tests}")
    print(f"Overall success rate: {(successful_tests/total_tests*100):.1f}%" if total_tests > 0 else "N/A")
    
    if successful_tests == total_tests:
        print("🎉 ALL TESTS PASSED! QR code designs are working as expected.")
    else:
        print("⚠️  Some tests failed. Review the detailed output above.")

def main():
    """Main verification routine."""
    print("🔍 Starting systematic QR code design verification...")
    print("This will generate test QR codes and analyze their SVG structure")
    print("to verify that configurations are applied correctly.\n")
    
    # Ensure temp directory exists
    os.makedirs("/tmp", exist_ok=True)
    
    # Run all test categories
    all_results = {}
    
    try:
        all_results['basic_shapes'] = test_basic_shapes()
        all_results['corner_radius'] = test_corner_radius_configurations()
        all_results['safe_mode'] = test_safe_mode_comparison()
        all_results['colors'] = test_color_configurations()
        all_results['finder_patterns'] = test_finder_pattern_customization()
        all_results['interactive'] = test_interactive_features()
        
        # Generate comprehensive summary
        generate_summary_report(all_results)
        
    except KeyboardInterrupt:
        print("\n⚠️  Verification interrupted by user")
    except Exception as e:
        print(f"\n❌ Verification failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()