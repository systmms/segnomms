#!/usr/bin/env python3
"""Test the improvements made to the QR code plugin."""

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
    sys.exit(1)

def test_improvements():
    """Test all the improvements we made."""
    print("🔍 Testing QR Code Plugin Improvements")
    print("=" * 50)
    
    # Test 1: Squircle shape should now work
    print("\n1️⃣ Testing squircle shape:")
    try:
        qr = segno.make("Testing squircle shape improvement")
        svg_path = "/tmp/test_squircle_improved.svg"
        segnomms.write(qr, svg_path, shape='squircle', scale=8, border=2)
        print("   ✅ Squircle shape generated successfully!")
    except Exception as e:
        print(f"   ❌ Squircle test failed: {e}")
    
    # Test 2: Connected shapes should now work
    print("\n2️⃣ Testing connected shapes:")
    connected_shapes = [
        'connected',
        'connected-extra-rounded',
        'connected-classy',
        'connected-classy-rounded'
    ]
    
    for shape in connected_shapes:
        try:
            qr = segno.make(f"Testing {shape} improvement")
            svg_path = f"/tmp/test_{shape.replace('-', '_')}_improved.svg"
            segnomms.write(qr, svg_path, shape=shape, scale=8, border=2,
                          enable_phase1=True, enable_phase2=True)
            print(f"   ✅ {shape} generated successfully!")
        except Exception as e:
            print(f"   ❌ {shape} test failed: {e}")
    
    # Test 3: Interactive features should include data attributes
    print("\n3️⃣ Testing interactive features:")
    try:
        qr = segno.make("Testing interactive features improvement")
        svg_path = "/tmp/test_interactive_improved.svg"
        segnomms.write(qr, svg_path, 
                      shape='rounded',
                      scale=8, 
                      border=2,
                      interactive=True,
                      tooltips=True)
        
        # Check if data attributes are present
        with open(svg_path, 'r') as f:
            svg_content = f.read()
        
        has_data_row = 'data-row=' in svg_content
        has_data_col = 'data-col=' in svg_content
        has_data_type = 'data-type=' in svg_content
        has_tooltips = '<title>' in svg_content
        
        print(f"   ✅ Interactive SVG generated")
        print(f"   {'✅' if has_data_row else '❌'} data-row attributes: {has_data_row}")
        print(f"   {'✅' if has_data_col else '❌'} data-col attributes: {has_data_col}")
        print(f"   {'✅' if has_data_type else '❌'} data-type attributes: {has_data_type}")
        print(f"   {'✅' if has_tooltips else '❌'} tooltips: {has_tooltips}")
        
    except Exception as e:
        print(f"   ❌ Interactive test failed: {e}")
    
    # Test 4: Safe mode with advanced shapes
    print("\n4️⃣ Testing safe mode improvements:")
    try:
        # Test with safe mode ON
        qr = segno.make("Testing safe mode ON improvement")
        svg_path = "/tmp/test_safe_mode_on_improved.svg"
        segnomms.write(qr, svg_path, 
                      shape='star',
                      safe_mode=True,
                      scale=8, 
                      border=2)
        
        # Test with safe mode OFF
        qr = segno.make("Testing safe mode OFF improvement")
        svg_path2 = "/tmp/test_safe_mode_off_improved.svg"
        segnomms.write(qr, svg_path2, 
                      shape='star',
                      safe_mode=False,
                      scale=8, 
                      border=2)
        
        print("   ✅ Safe mode ON generated successfully")
        print("   ✅ Safe mode OFF generated successfully")
        
        # Compare the two files to see differences
        with open(svg_path, 'r') as f:
            safe_on_content = f.read()
        with open(svg_path2, 'r') as f:
            safe_off_content = f.read()
        
        # Count element types
        safe_on_rects = safe_on_content.count('<rect')
        safe_on_polygons = safe_on_content.count('<polygon')
        safe_off_rects = safe_off_content.count('<rect')
        safe_off_polygons = safe_off_content.count('<polygon')
        
        print(f"   📊 Safe mode ON: {safe_on_rects} rects, {safe_on_polygons} polygons")
        print(f"   📊 Safe mode OFF: {safe_off_rects} rects, {safe_off_polygons} polygons")
        
    except Exception as e:
        print(f"   ❌ Safe mode test failed: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Improvement testing complete!")
    print("Generated test files in /tmp/")

if __name__ == "__main__":
    test_improvements()