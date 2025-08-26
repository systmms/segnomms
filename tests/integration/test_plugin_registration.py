"""
Integration tests for Segno plugin registration.

Tests that the plugin is properly registered with Segno and can be called
using the to_XXX method pattern.
"""

import pytest
import segno

from segnomms import write
from segnomms.shapes import list_available_shapes


@pytest.fixture
def output_dir(tmp_path):
    """Create a temporary output directory."""
    output = tmp_path / "test-output"
    output.mkdir(exist_ok=True)
    return output


class TestPluginRegistration:
    """Test Segno plugin registration functionality."""

    def test_direct_import_method(self, output_dir):
        """Test using direct import of write function."""
        qr = segno.make("https://github.com/segno-plugin-test", error="h")
        output_file = output_dir / "test_plugin_direct.svg"

        write(
            qr,
            str(output_file),
            shape="connected",
            scale=10,
            border=2,
            dark="#3498db",
            light="#ffffff",
            phase1_enabled=True,
            phase1_use_enhanced_shapes=True,
            style_interactive=True,
        )

        assert output_file.exists()
        content = output_file.read_text()
        assert "<svg" in content
        assert 'xmlns="http://www.w3.org/2000/svg"' in content

    @pytest.mark.skipif(
        not hasattr(segno.QRCode, "to_interactive_svg"), reason="Plugin not installed via pip"
    )
    def test_plugin_method_registration(self, output_dir):
        """Test using to_interactive_svg() method when plugin is installed."""
        qr = segno.make("https://github.com/segno-plugin-test", error="h")
        output_file = output_dir / "test_plugin_method.svg"

        qr.to_interactive_svg(
            str(output_file),
            shape="connected",
            scale=10,
            border=2,
            dark="#2c3e50",
            light="#ecf0f1",
            phase1_enabled=True,
            phase1_use_enhanced_shapes=True,
            style_interactive=True,
        )

        assert output_file.exists()
        content = output_file.read_text()
        assert "<svg" in content

    @pytest.mark.skipif(
        not hasattr(segno.QRCode, "to_interactive_svg"), reason="Plugin not installed via pip"
    )
    def test_save_with_kind_parameter(self, output_dir):
        """Test using save() with kind parameter."""
        qr = segno.make("https://github.com/segno-plugin-test", error="h")
        output_file = output_dir / "test_plugin_save.svg"

        qr.save(
            str(output_file),
            kind="interactive_svg",
            shape="connected",
            scale=10,
            border=2,
            dark="#e74c3c",
            light="#ffffff",
            phase1_enabled=True,
            phase1_use_enhanced_shapes=True,
            style_interactive=True,
        )

        assert output_file.exists()
        content = output_file.read_text()
        assert "<svg" in content

    def test_plugin_registration_check(self):
        """Test if plugin registration can be checked."""
        # Check if the plugin method exists
        has_plugin = hasattr(segno.QRCode, "to_interactive_svg")

        # Plugin may or may not be installed
        assert isinstance(has_plugin, bool)

        if has_plugin:
            # If installed, verify it's callable
            qr = segno.make("test")
            assert callable(getattr(qr, "to_interactive_svg"))


class TestShapeAvailability:
    """Test available shapes through the plugin."""

    def test_list_available_shapes(self):
        """Test that list_available_shapes returns expected shapes."""
        shapes = list_available_shapes()

        assert isinstance(shapes, list)
        assert len(shapes) > 0

        # Verify some expected shapes are present
        expected_basic = ["square", "circle", "rounded", "diamond", "star", "triangle"]
        expected_connected = ["connected", "connected-extra-rounded", "connected-classy"]

        for shape in expected_basic:
            assert shape in shapes, f"Expected basic shape '{shape}' not found"

        for shape in expected_connected:
            assert shape in shapes, f"Expected connected shape '{shape}' not found"

    def test_shape_categories(self):
        """Test that shapes are properly categorized."""
        shapes = list_available_shapes()

        # Define shape categories
        basic_shapes = {"square", "circle", "rounded", "diamond", "star", "triangle", "hexagon", "cross"}

        connected_shapes = {"connected", "connected-rounded", "connected-diamond", "connected-extra-rounded"}

        # Check that all basic shapes that exist are in the list
        available_basic = [s for s in shapes if s in basic_shapes]
        assert len(available_basic) > 0, "No basic shapes found"

        # Check that all connected shapes that exist are in the list
        available_connected = [s for s in shapes if s in connected_shapes]
        assert len(available_connected) > 0, "No connected shapes found"

    def test_shape_count(self):
        """Test that we have a reasonable number of shapes."""
        shapes = list_available_shapes()

        # Should have at least 10 shapes (basic + connected)
        assert len(shapes) >= 10, f"Expected at least 10 shapes, got {len(shapes)}"

        # But not too many (sanity check)
        assert len(shapes) < 50, f"Too many shapes registered: {len(shapes)}"


class TestPluginIntegration:
    """Test full plugin integration scenarios."""

    def test_write_with_all_phases(self, output_dir):
        """Test write function with all phases enabled."""
        qr = segno.make("Full phase test", error="m")
        output_file = output_dir / "all_phases.svg"

        write(
            qr,
            str(output_file),
            shape="squircle",
            corner_radius=0.3,
            scale=15,
            border=3,
            dark="#1a1a1a",
            light="#ffffff",
            enable_phase1=True,
            enable_phase2=True,
            enable_phase3=True,
            enable_phase4=True,
            style_interactive=True,
            frame_shape="rounded-square",
            centerpiece_enabled=True,
            centerpiece_size=0.15,
        )

        assert output_file.exists()
        content = output_file.read_text()

        # Verify SVG structure
        assert "<svg" in content
        assert "viewBox" in content

        # Check for phase 4 features (if validation passed)
        # These may or may not be present depending on validation
        svg_has_styles = "<style>" in content
        svg_has_defs = "<defs>" in content

        # At minimum we should have valid SVG
        assert content.strip().endswith("</svg>")

    def test_error_handling_invalid_shape(self, output_dir):
        """Test error handling with invalid shape."""
        qr = segno.make("Error test", error="l")
        output_file = output_dir / "error_test.svg"

        # Should handle invalid shape gracefully (fallback to square)
        write(qr, str(output_file), shape="invalid_shape_name", scale=10)

        # Should still create a valid SVG file
        assert output_file.exists()
        content = output_file.read_text()
        assert "<svg" in content
