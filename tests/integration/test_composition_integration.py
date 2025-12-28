"""Integration tests for composition features (frames and centerpieces)."""

import xml.etree.ElementTree as ET

import pytest
import segno

from segnomms import write
from segnomms.config import RenderingConfig
from segnomms.plugin import generate_interactive_svg


class TestCompositionIntegration:
    """Integration tests for frame and centerpiece features."""

    @pytest.fixture
    def test_qr(self):
        """Create a test QR code."""
        return segno.make("https://github.com/segnomms/phase4-test", error="h")

    def find_element_by_id(self, root, element_id):
        """Helper to find element by id regardless of namespace."""
        for elem in root.iter():
            if elem.get("id") == element_id:
                return elem
        return None

    def find_element_by_tag_name(self, root, tag_name):
        """Helper to find element by tag name regardless of namespace."""
        for elem in root.iter():
            if elem.tag == tag_name or elem.tag.endswith("}" + tag_name):
                return elem
        return None

    def find_element_by_partial_tag(self, root, partial_tag):
        """Helper to find element by partial tag name."""
        for elem in root.iter():
            if partial_tag in elem.tag:
                return elem
        return None

    def test_circle_frame_generation(self, test_qr, tmp_path):
        """Test circle frame SVG generation."""
        output_file = tmp_path / "circle_frame.svg"

        write(test_qr, str(output_file), scale=10, border=4, frame_shape="circle")

        # Verify file was created
        assert output_file.exists()

        # Parse SVG and verify structure
        svg_content = output_file.read_text()
        root = ET.fromstring(svg_content)

        # Check for frame clip path
        defs = self.find_element_by_tag_name(root, "defs")
        assert defs is not None

        clip_path = self.find_element_by_id(defs, "frame-clip-circle-clip")
        assert clip_path is not None

        circle = self.find_element_by_tag_name(clip_path, "circle")
        assert circle is not None

        # Check modules group has clipping applied
        modules = self.find_element_by_id(root, "segnomms-modules")
        assert modules is not None
        assert modules.get("clip-path") == "url(#frame-clip-circle-clip)"

    def test_centerpiece_generation(self, test_qr, tmp_path):
        """Test centerpiece reserve functionality."""
        output_file = tmp_path / "centerpiece.svg"

        write(
            test_qr,
            str(output_file),
            scale=12,
            border=5,
            centerpiece_enabled=True,
            centerpiece_shape="circle",
            centerpiece_size=0.15,
            centerpiece_margin=2,
        )

        assert output_file.exists()

        svg_content = output_file.read_text()
        root = ET.fromstring(svg_content)

        # Check for centerpiece metadata
        metadata = self.find_element_by_tag_name(root, "metadata")
        assert metadata is not None

        # Find centerpiece info
        centerpiece_info = self.find_element_by_partial_tag(metadata, "centerpiece")
        assert centerpiece_info is not None

        # Find bounds
        bounds = self.find_element_by_partial_tag(centerpiece_info, "bounds")
        assert bounds is not None
        assert bounds.get("width") is not None
        assert bounds.get("height") is not None

    def test_gradient_quiet_zone(self, test_qr, tmp_path):
        """Test gradient quiet zone generation."""
        output_file = tmp_path / "gradient_quiet_zone.svg"

        write(
            test_qr,
            str(output_file),
            scale=10,
            border=4,
            quiet_zone_style="gradient",
            quiet_zone_gradient={"type": "radial", "colors": ["#ffffff", "#e0e0e0"]},
        )

        assert output_file.exists()

        svg_content = output_file.read_text()
        root = ET.fromstring(svg_content)

        # Check for gradient definition
        defs = self.find_element_by_tag_name(root, "defs")
        assert defs is not None

        gradient = self.find_element_by_id(defs, "quiet-zone-gradient")
        assert gradient is not None

        # Check gradient has stops
        stops = [elem for elem in gradient.iter() if "stop" in elem.tag]
        assert len(stops) >= 2

        # Check quiet zone rect uses gradient
        quiet_zone = None
        for elem in root.iter():
            if "rect" in elem.tag and elem.get("class") == "segnomms-quiet-zone":
                quiet_zone = elem
                break
        assert quiet_zone is not None
        assert "url(#quiet-zone-gradient)" in quiet_zone.get("fill")

    def test_combined_features(self, test_qr, tmp_path):
        """Test combination of all Phase 4 features."""
        output_file = tmp_path / "combined_features.svg"

        write(
            test_qr,
            str(output_file),
            scale=15,
            border=5,
            frame_shape="rounded-rect",
            frame_corner_radius=0.3,
            centerpiece_enabled=True,
            centerpiece_shape="squircle",
            centerpiece_size=0.12,
            quiet_zone_style="gradient",
            quiet_zone_gradient={
                "type": "linear",
                "x1": "0%",
                "y1": "0%",
                "x2": "100%",
                "y2": "100%",
                "colors": ["#f8f9fa", "#e9ecef"],
            },
            merge="soft",
            shape="circle",
        )

        assert output_file.exists()

        svg_content = output_file.read_text()
        root = ET.fromstring(svg_content)

        # Verify all features are present
        defs = self.find_element_by_tag_name(root, "defs")
        assert defs is not None

        # Frame clip path
        clip_path = self.find_element_by_id(defs, "frame-clip-rounded-rect-clip")
        assert clip_path is not None

        # Gradient
        gradient = self.find_element_by_id(defs, "quiet-zone-gradient")
        assert gradient is not None

        # Centerpiece metadata
        metadata = self.find_element_by_tag_name(root, "metadata")
        assert metadata is not None

        centerpiece = self.find_element_by_partial_tag(metadata, "centerpiece")
        assert centerpiece is not None

    def test_frame_clipping_with_clustering(self, test_qr, tmp_path):
        """Test frame clipping works with clustering."""
        output_file = tmp_path / "frame_clustering.svg"

        write(
            test_qr,
            str(output_file),
            scale=8,
            border=3,
            frame_shape="circle",
            merge="aggressive",  # Enable clustering
            min_island_modules=3,
        )

        assert output_file.exists()

        svg_content = output_file.read_text()
        root = ET.fromstring(svg_content)

        # Check clipping is applied to modules group
        modules = self.find_element_by_id(root, "segnomms-modules")
        assert modules is not None
        assert "clip-path" in modules.attrib

        # Should contain either paths or other shape elements (rects, circles)
        # depending on the shape and clustering behavior
        shape_elements = [
            elem
            for elem in modules.iter()
            if any(shape in elem.tag for shape in ["path", "rect", "circle", "ellipse"])
        ]
        assert len(shape_elements) > 0  # Should have some QR modules

    def test_custom_frame_path(self, test_qr, tmp_path):
        """Test custom frame path."""
        output_file = tmp_path / "custom_frame.svg"

        # Create a simple diamond path
        custom_path = "M 100 0 L 200 100 L 100 200 L 0 100 Z"

        write(
            test_qr, str(output_file), scale=10, border=4, frame_shape="custom", frame_custom_path=custom_path
        )

        assert output_file.exists()

        svg_content = output_file.read_text()
        root = ET.fromstring(svg_content)

        # Check custom path is used in clip path
        defs = self.find_element_by_tag_name(root, "defs")
        clip_path = self.find_element_by_id(defs, "frame-clip-custom-clip")
        assert clip_path is not None

        path_elem = self.find_element_by_tag_name(clip_path, "path")
        assert path_elem is not None
        assert custom_path in path_elem.get("d")

    def test_validation_warnings_logged(self, test_qr, caplog):
        """Test that validation warnings are properly logged."""
        config = RenderingConfig.from_kwargs(
            frame_shape="circle",
            border=2,  # Too small for circle
            centerpiece_enabled=True,
            centerpiece_size=0.3,  # Large centerpiece
        )

        # Generate SVG (should log warnings)
        svg_content = generate_interactive_svg(test_qr, config)
        assert "<svg" in svg_content  # Validate SVG was generated

        # Check warnings were logged
        warning_messages = [record.message for record in caplog.records if record.levelname == "WARNING"]

        assert len(warning_messages) > 0
        assert any("4-module quiet zone" in msg for msg in warning_messages)

    def test_error_handling_invalid_config(self, test_qr):
        """Test error handling with invalid configuration."""
        # This should not raise an exception, but log errors
        config = RenderingConfig()
        config.frame.shape = "invalid_shape"

        # Should complete without raising exception
        svg_content = generate_interactive_svg(test_qr, config)
        assert svg_content is not None
        assert len(svg_content) > 0

    def test_fade_frame_mode(self, test_qr, tmp_path):
        """Test fade frame mode."""
        output_file = tmp_path / "fade_frame.svg"

        write(test_qr, str(output_file), scale=12, border=4, frame_shape="circle", frame_clip_mode="fade")

        assert output_file.exists()

        svg_content = output_file.read_text()
        root = ET.fromstring(svg_content)

        # Check for mask attribute (fade mode uses mask, not clip-path)
        modules = self.find_element_by_id(root, "segnomms-modules")
        assert modules is not None
        assert "mask" in modules.attrib
        assert modules.attrib["mask"] == "url(#fade-mask-circle)"

    def test_centerpiece_offset(self, test_qr, tmp_path):
        """Test centerpiece with offset positioning."""
        output_file = tmp_path / "centerpiece_offset.svg"

        write(
            test_qr,
            str(output_file),
            scale=12,
            border=4,
            centerpiece_enabled=True,
            centerpiece_size=0.1,
            centerpiece_offset_x=0.2,
            centerpiece_offset_y=-0.1,
        )

        assert output_file.exists()

        svg_content = output_file.read_text()
        root = ET.fromstring(svg_content)

        # Check metadata includes offset information
        metadata = self.find_element_by_tag_name(root, "metadata")
        centerpiece = self.find_element_by_partial_tag(metadata, "centerpiece")
        config = self.find_element_by_partial_tag(centerpiece, "config")

        offset_x = self.find_element_by_partial_tag(config, "offset-x")
        offset_y = self.find_element_by_partial_tag(config, "offset-y")

        assert offset_x is not None
        assert offset_y is not None
        assert offset_x.text == "0.2"
        assert offset_y.text == "-0.1"

    def test_layered_svg_structure(self, test_qr, tmp_path):
        """Test proper SVG layering structure."""
        output_file = tmp_path / "layered_structure.svg"

        write(
            test_qr,
            str(output_file),
            scale=10,
            border=4,
            frame_shape="circle",
            centerpiece_enabled=True,
            centerpiece_size=0.1,
            quiet_zone_style="gradient",
            quiet_zone_gradient={"type": "radial", "colors": ["#fff", "#eee"]},
        )

        assert output_file.exists()

        svg_content = output_file.read_text()
        root = ET.fromstring(svg_content)

        # Check proper element ordering
        children = list(root)
        element_tags = [child.tag for child in children]

        # Should have defs early, then quiet zone, then modules
        assert any("defs" in tag for tag in element_tags)
        assert any("rect" in child.tag and "quiet-zone" in child.get("class", "") for child in children)
        assert any(child.get("id") == "segnomms-modules" for child in children)

    def test_no_phase4_features_baseline(self, test_qr, tmp_path):
        """Test that SVG without Phase 4 features still works correctly."""
        output_file = tmp_path / "baseline.svg"

        write(test_qr, str(output_file), scale=10, border=4, shape="square")  # No Phase 4 features

        assert output_file.exists()

        svg_content = output_file.read_text()
        root = ET.fromstring(svg_content)

        # Should not have frame clip paths
        defs = self.find_element_by_tag_name(root, "defs")
        if defs is not None:
            clip_paths = [elem for elem in defs.iter() if "clipPath" in elem.tag]
            frame_clips = [cp for cp in clip_paths if "frame-clip" in cp.get("id", "")]
            assert len(frame_clips) == 0

        # Should not have centerpiece metadata
        metadata = self.find_element_by_tag_name(root, "metadata")
        if metadata is not None:
            centerpiece = self.find_element_by_partial_tag(metadata, "centerpiece")
            assert centerpiece is None
