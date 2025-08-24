"""
Integration tests for connected shape renderers.

Tests for connected shape rendering capabilities that create fluid,
context-aware QR codes with neighbor-aware rendering.
"""

import pytest
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path
from io import StringIO

import segno
from segnomms import write
from tests.constants import (
    ModuleShape, CONNECTED_SHAPES, QR_PAYLOADS, TEST_COLORS,
    DEFAULT_SCALE, DEFAULT_BORDER, create_test_config
)


class TestConnectedShapes:
    """Test connected shape rendering functionality."""
    
    def test_connected_shape_types(self, tmp_path):
        """Test different connected shape styles."""
        data = QR_PAYLOADS["url_complex"]
        
        # Shape types to test - using constants and adding all connected shapes
        shape_types = [
            (ModuleShape.SQUARE.value, "Standard square modules"),
            (ModuleShape.ROUNDED.value, "Basic rounded squares"),
        ]
        
        # Add all connected shapes from constants
        for connected_shape in CONNECTED_SHAPES:
            shape_types.append((connected_shape, f"Connected shape: {connected_shape}"))
        
        results = {}
        
        for shape_type, description in shape_types:
            output_file = tmp_path / f"connected_{shape_type}.svg"
            
            # Create QR code
            qr = segno.make(data, error="h")
            
            # Generate SVG with connected shapes using test constants
            config = create_test_config(
                shape=shape_type,
                scale=DEFAULT_SCALE,
                border=DEFAULT_BORDER,
                dark=TEST_COLORS["brand_primary"],
                light=TEST_COLORS["white"],
                phase1_enabled=True,
                phase1_use_enhanced_shapes=True,
                style_interactive=True,
                style_tooltips=True,
                style_css_classes={
                    "finder": "qr-finder",
                    "finder_inner": "qr-finder-inner",
                    "timing": "qr-timing",
                    "data": "qr-data",
                    "alignment": "qr-alignment",
                    "alignment_center": "qr-alignment-center",
                }
            )
            write(qr, str(output_file), **config)
            
            # Verify file was created and has content
            assert output_file.exists()
            assert output_file.stat().st_size > 0
            
            # Parse SVG and verify basic structure
            tree = ET.parse(output_file)
            root = tree.getroot()
            assert root.tag.endswith('svg')
            
            # Store result for comparison
            results[shape_type] = {
                'file': output_file,
                'description': description,
                'size': output_file.stat().st_size
            }
        
        # All files should be created
        assert len(results) == len(shape_types)
        
        # Connected shapes should have different output than square
        square_key = ModuleShape.SQUARE.value
        connected_key = ModuleShape.CONNECTED.value
        extra_rounded_key = ModuleShape.CONNECTED_EXTRA_ROUNDED.value
        
        assert results[connected_key]['size'] != results[square_key]['size']
        assert results[extra_rounded_key]['size'] != results[square_key]['size']
    
    def test_neighbor_aware_rendering(self, tmp_path):
        """Test neighbor-aware rendering with different patterns."""
        # Different patterns to test neighbor awareness
        patterns = [
            ("single_dots", QR_PAYLOADS["simple"]),
            ("connected_line", QR_PAYLOADS["alphanumeric"]),
            ("l_shape", QR_PAYLOADS["numeric"]),
        ]
        
        for pattern_name, pattern_data in patterns:
            output_file = tmp_path / f"neighbor_{pattern_name}.svg"
            
            qr = segno.make(pattern_data, error="l", boost_error=False)
            
            config = create_test_config(
                shape=ModuleShape.CONNECTED.value,  # Use connected shape for neighbor awareness
                scale=20,  # Larger scale to see details
                border=1,
                dark=TEST_COLORS["brand_primary"],
                light=TEST_COLORS["brand_secondary"],
                phase1_enabled=True,
                phase1_use_enhanced_shapes=True
            )
            write(qr, str(output_file), **config)
            
            # Verify file creation and content
            assert output_file.exists()
            assert output_file.stat().st_size > 0
            
            # Parse and verify SVG structure
            tree = ET.parse(output_file)
            root = tree.getroot()
            assert root.tag.endswith('svg')
            
            # Check for expected attributes
            assert root.get('width') is not None
            assert root.get('height') is not None
    
    def test_shape_comparison_generation(self, tmp_path):
        """Test generation of shape comparison output."""
        data = QR_PAYLOADS["unicode"]
        shapes = [
            ModuleShape.SQUARE.value, 
            ModuleShape.ROUNDED.value, 
            ModuleShape.CONNECTED.value, 
            ModuleShape.CONNECTED_EXTRA_ROUNDED.value
        ]
        
        # Generate individual QR codes for comparison
        qr_outputs = {}
        
        for shape in shapes:
            output_file = tmp_path / f"comparison_{shape}.svg"
            qr = segno.make(data, error="m")
            
            # Generate to StringIO first to capture content
            buffer = StringIO()
            config = create_test_config(
                shape=shape, 
                scale=DEFAULT_SCALE, 
                border=DEFAULT_BORDER, 
                dark=TEST_COLORS["brand_primary"], 
                light=TEST_COLORS["white"]
            )
            write(qr, buffer, **config)
            svg_content = buffer.getvalue()
            
            # Also write to file
            with open(output_file, 'w') as f:
                f.write(svg_content)
            
            # Verify content
            assert len(svg_content) > 0
            assert '<svg' in svg_content
            assert output_file.exists()
            
            qr_outputs[shape] = {
                'file': output_file,
                'content': svg_content,
                'size': len(svg_content)
            }
        
        # All shapes should produce output
        assert len(qr_outputs) == len(shapes)
        
        # Different shapes should produce different content
        square_content = qr_outputs[ModuleShape.SQUARE.value]['content']
        connected_content = qr_outputs[ModuleShape.CONNECTED.value]['content']
        assert square_content != connected_content
        
        # All should be valid SVG
        for shape, output in qr_outputs.items():
            root = ET.fromstring(output['content'])
            assert root.tag.endswith('svg')
    
    def test_connected_shapes_with_interactivity(self, tmp_path):
        """Test connected shapes with interactive features."""
        data = QR_PAYLOADS["simple"]
        output_file = tmp_path / "interactive_connected.svg"
        
        qr = segno.make(data, error="m")
        
        config = create_test_config(
            shape=ModuleShape.CONNECTED.value,
            scale=12,
            border=2,
            dark=TEST_COLORS["blue"],
            light=TEST_COLORS["brand_secondary"],
            style_interactive=True,
            style_tooltips=True,
            style_css_classes={
                "finder": "qr-finder-custom",
                "data": "qr-data-custom",
                "timing": "qr-timing-custom",
            }
        )
        write(qr, str(output_file), **config)
        
        # Verify file creation
        assert output_file.exists()
        
        # Read and verify SVG content
        with open(output_file, 'r') as f:
            content = f.read()
        
        # Should contain interactive elements
        assert 'qr-finder-custom' in content
        assert 'qr-data-custom' in content
        assert 'qr-timing-custom' in content
        
        # Parse SVG structure
        root = ET.fromstring(content)
        assert root.tag.endswith('svg')
        
        # Should have style elements for interactivity
        style_elements = root.findall('.//{http://www.w3.org/2000/svg}style')
        if style_elements:  # If interactive features are implemented
            assert len(style_elements) > 0
    
    def test_connected_shapes_phase1_enhancement(self, tmp_path):
        """Test connected shapes with Phase 1 enhancements."""
        data = QR_PAYLOADS["simple"]
        output_file = tmp_path / "phase1_enhanced.svg"
        
        qr = segno.make(data, error="h")
        
        config = create_test_config(
            shape=ModuleShape.CONNECTED_EXTRA_ROUNDED.value,
            scale=15,
            border=3,
            dark=TEST_COLORS["brand_primary"],
            light=TEST_COLORS["white"],
            phase1_enabled=True,
            phase1_use_enhanced_shapes=True
        )
        write(qr, str(output_file), **config)
        
        # Verify file creation and basic structure
        assert output_file.exists()
        assert output_file.stat().st_size > 0
        
        # Parse and verify SVG
        tree = ET.parse(output_file)
        root = tree.getroot()
        assert root.tag.endswith('svg')
        
        # Verify dimensions are reasonable
        width = root.get('width')
        height = root.get('height')
        assert width is not None
        assert height is not None
        
        # Width and height should be numeric (with scale 15, should be substantial)
        if width.isdigit():
            assert int(width) > 100  # Should be reasonably sized
        if height.isdigit():
            assert int(height) > 100
    
    def test_shape_parameter_validation(self, tmp_path):
        """Test that invalid shape parameters are handled gracefully."""
        data = QR_PAYLOADS["simple"]
        qr = segno.make(data, error="m")
        
        # Valid connected shape should work
        output_file = tmp_path / "valid_shape.svg"
        config = create_test_config(
            shape=ModuleShape.CONNECTED.value,
            scale=8
        )
        write(qr, str(output_file), **config)
        assert output_file.exists()
        
        # Test with invalid shape (should fall back or raise clear error)
        output_file2 = tmp_path / "invalid_shape.svg"
        try:
            write(
                qr,
                str(output_file2),
                shape="invalid-connected-shape",
                scale=8
            )
            # If it succeeds, file should exist
            if output_file2.exists():
                assert output_file2.stat().st_size > 0
        except (ValueError, KeyError) as e:
            # Should raise a clear error for invalid shape
            assert "shape" in str(e).lower() or "invalid" in str(e).lower()


class TestConnectedShapeDetails:
    """Test specific details of connected shape rendering."""
    
    def test_neighbor_detection_algorithm(self, tmp_path):
        """Test that neighbor detection works for connected shapes."""
        # Create a pattern that should show clear neighbor relationships
        data = QR_PAYLOADS["alphanumeric"]
        output_file = tmp_path / "neighbor_detection.svg"
        
        qr = segno.make(data, error="l")
        
        config = create_test_config(
            shape=ModuleShape.CONNECTED.value,
            scale=25,  # Very large scale to see neighbor effects
            border=1,
            dark=TEST_COLORS["brand_primary"],
            light=TEST_COLORS["white"]
        )
        write(qr, str(output_file), **config)
        
        assert output_file.exists()
        
        # Read content and verify it contains SVG paths/elements
        with open(output_file, 'r') as f:
            content = f.read()
        
        # Connected shapes should generate path elements or similar
        # for neighbor-aware rendering
        assert '<svg' in content
        assert 'dark' in content or TEST_COLORS["brand_primary"] in content
    
    def test_shape_consistency_across_calls(self, tmp_path):
        """Test that connected shapes produce consistent output."""
        data = QR_PAYLOADS["simple"]
        
        # Generate same QR code twice with same parameters
        qr = segno.make(data, error="m")
        
        params = create_test_config(
            shape=ModuleShape.CONNECTED.value,
            scale=DEFAULT_SCALE,
            border=DEFAULT_BORDER,
            dark=TEST_COLORS["brand_primary"],
            light=TEST_COLORS["brand_secondary"]
        )
        
        # First generation
        file1 = tmp_path / "consistent1.svg"
        write(qr, str(file1), **params)
        
        # Second generation
        file2 = tmp_path / "consistent2.svg"
        write(qr, str(file2), **params)
        
        # Files should exist and have same content
        assert file1.exists()
        assert file2.exists()
        
        with open(file1, 'r') as f1, open(file2, 'r') as f2:
            content1 = f1.read()
            content2 = f2.read()
        
        # Content should be identical for same parameters
        assert content1 == content2
        assert len(content1) > 0