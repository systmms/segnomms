"""Test suite for FrameShapeGenerator class."""

import xml.etree.ElementTree as ET

from segnomms.shapes.frames import FrameShapeGenerator


class TestFrameShapeGenerator:
    """Test cases for the FrameShapeGenerator class."""

    def test_generate_circle_clip(self):
        """Test circle clipping path generation."""
        svg_str = FrameShapeGenerator.generate_circle_clip(200, 200, 10)

        # Parse the SVG string
        elem = ET.fromstring(svg_str)

        assert elem.tag == "circle"
        assert elem.get("cx") == "100.0"
        assert elem.get("cy") == "100.0"
        assert elem.get("r") == "100.0"

    def test_generate_circle_clip_non_square(self):
        """Test circle clip for non-square dimensions."""
        svg_str = FrameShapeGenerator.generate_circle_clip(300, 200, 0)

        elem = ET.fromstring(svg_str)

        # Should use the smaller dimension for radius
        assert elem.get("cx") == "150.0"
        assert elem.get("cy") == "100.0"
        assert elem.get("r") == "100.0"  # min(300, 200) / 2

    def test_generate_rounded_rect_clip(self):
        """Test rounded rectangle clipping path generation."""
        svg_str = FrameShapeGenerator.generate_rounded_rect_clip(200, 200, 10, 0.2)

        elem = ET.fromstring(svg_str)

        assert elem.tag == "rect"
        assert elem.get("x") == "0"
        assert elem.get("y") == "0"
        assert elem.get("width") == "200"
        assert elem.get("height") == "200"
        assert elem.get("rx") == "20.0"  # 0.2 * 200 / 2
        assert elem.get("ry") == "20.0"

    def test_generate_rounded_rect_clip_max_radius(self):
        """Test rounded rect with corner radius exceeding limits."""
        # Corner radius of 1.0 should be clamped to half the dimension
        svg_str = FrameShapeGenerator.generate_rounded_rect_clip(200, 100, 0, 1.0)

        elem = ET.fromstring(svg_str)

        # Should be clamped to min dimension / 2
        assert elem.get("rx") == "50.0"  # min(200, 100) / 2
        assert elem.get("ry") == "50.0"

    def test_generate_squircle_clip(self):
        """Test squircle clipping path generation."""
        svg_str = FrameShapeGenerator.generate_squircle_clip(200, 200, 0)

        elem = ET.fromstring(svg_str)

        assert elem.tag == "path"
        path_data = elem.get("d")

        # Check path starts with move command
        assert path_data.startswith("M")

        # Check path contains cubic bezier curves
        assert "C" in path_data

        # Check path is closed
        assert path_data.endswith("Z")

        # Verify it has the expected structure (4 curves for 4 sides)
        assert path_data.count("C") == 4

    def test_generate_fade_mask_circle(self):
        """Test fade mask generation for circle."""
        svg_str = FrameShapeGenerator.generate_fade_mask(200, 200, "circle", 0.1)

        # Should contain radial gradient and circle
        assert "radialGradient" in svg_str
        assert 'id="fade-gradient-circle"' in svg_str
        assert "<circle" in svg_str
        assert 'fill="url(#fade-gradient-circle)"' in svg_str

        # Check gradient stops exist (actual percentage depends on calculation)
        assert 'stop offset="' in svg_str
        assert 'stop-opacity="1"' in svg_str
        assert 'stop-opacity="0"' in svg_str
        assert "100%" in svg_str

    def test_generate_fade_mask_rounded_rect(self):
        """Test fade mask generation for rounded rectangle."""
        svg_str = FrameShapeGenerator.generate_fade_mask(200, 200, "rounded-rect", 0.15)

        # Should use radial gradient for now
        assert "radialGradient" in svg_str
        assert "<rect" in svg_str
        # Check gradient stops exist (actual percentage depends on calculation)
        assert 'stop offset="' in svg_str
        assert 'stop-opacity="1"' in svg_str
        assert 'stop-opacity="0"' in svg_str
        assert "100%" in svg_str

    def test_validate_custom_path_valid(self):
        """Test validation of valid custom SVG paths."""
        # Valid closed path
        is_valid, error = FrameShapeGenerator.validate_custom_path(
            "M 0 0 L 100 0 L 100 100 L 0 100 Z", 100, 100
        )
        assert is_valid is True
        assert error == ""

        # Path with curves
        is_valid, error = FrameShapeGenerator.validate_custom_path(
            "M 50 0 C 100 0 100 50 100 50 L 100 100 L 0 100 L 0 0 Z", 100, 100
        )
        assert is_valid is True
        assert error == ""

    def test_validate_custom_path_empty(self):
        """Test validation of empty path."""
        is_valid, error = FrameShapeGenerator.validate_custom_path("", 100, 100)
        assert is_valid is False
        assert error == "Path cannot be empty"

    def test_validate_custom_path_invalid_commands(self):
        """Test validation of path with invalid commands."""
        is_valid, error = FrameShapeGenerator.validate_custom_path("M 0 0 X 100 100 Z", 100, 100)
        assert is_valid is False
        assert "Invalid path commands" in error
        assert "X" in error

    def test_validate_custom_path_not_closed(self):
        """Test validation of unclosed path."""
        is_valid, error = FrameShapeGenerator.validate_custom_path("M 0 0 L 100 0 L 100 100", 100, 100)
        assert is_valid is False
        assert "should be closed" in error

    def test_validate_custom_path_no_move(self):
        """Test validation of path without move command."""
        is_valid, error = FrameShapeGenerator.validate_custom_path("L 100 0 L 100 100 Z", 100, 100)
        assert is_valid is False
        assert "should start with M" in error

    def test_scale_path_to_fit(self):
        """Test path scaling (placeholder functionality)."""
        original_path = "M 0 0 L 50 0 L 50 50 L 0 50 Z"
        scaled = FrameShapeGenerator.scale_path_to_fit(original_path, (0, 0, 50, 50), 200, 200)

        # Currently returns original path (placeholder)
        assert scaled == original_path

    def test_create_frame_group_circle(self):
        """Test creating a complete frame group for circle."""
        elem = FrameShapeGenerator.create_frame_group("circle", 200, 200)

        assert elem.tag == "circle"
        assert elem.get("cx") == "100.0"
        assert elem.get("cy") == "100.0"
        assert elem.get("r") == "100.0"

    def test_create_frame_group_rounded_rect(self):
        """Test creating a complete frame group for rounded rectangle."""
        config = {"corner_radius": 0.3}
        elem = FrameShapeGenerator.create_frame_group("rounded-rect", 200, 200, config)

        assert elem.tag == "rect"
        assert elem.get("rx") == "30.0"  # 0.3 * 200 / 2
        assert elem.get("ry") == "30.0"

    def test_create_frame_group_squircle(self):
        """Test creating a complete frame group for squircle."""
        elem = FrameShapeGenerator.create_frame_group("squircle", 200, 200)

        assert elem.tag == "path"
        assert elem.get("d") is not None
        assert elem.get("d").endswith("Z")

    def test_create_frame_group_custom(self):
        """Test creating a complete frame group for custom shape."""
        config = {"custom_path": "M 0 0 L 200 0 L 200 200 L 0 200 Z"}
        elem = FrameShapeGenerator.create_frame_group("custom", 200, 200, config)

        assert elem.tag == "path"
        assert elem.get("d") == config["custom_path"]

    def test_create_frame_group_custom_fallback(self):
        """Test custom shape fallback when no path provided."""
        elem = FrameShapeGenerator.create_frame_group("custom", 200, 200)

        # Should fall back to rectangle
        assert elem.tag == "rect"
        assert elem.get("width") == "200"
        assert elem.get("height") == "200"

    def test_create_frame_group_unknown(self):
        """Test unknown shape type falls back to square."""
        elem = FrameShapeGenerator.create_frame_group("unknown", 200, 200)

        assert elem.tag == "rect"
        assert elem.get("width") == "200"
        assert elem.get("height") == "200"
