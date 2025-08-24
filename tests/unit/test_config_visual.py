"""
Comprehensive unit tests for visual configuration models.

Tests PatternStyleConfig, FrameConfig, CenterpieceConfig, QuietZoneConfig,
and StyleConfig validation, interactions, and complex scenarios.
"""

import pytest
from pydantic import ValidationError

from segnomms.config.models.visual import (
    PatternStyleConfig,
    FrameConfig,
    CenterpieceConfig,
    QuietZoneConfig,
    StyleConfig,
)
from segnomms.config.enums import PlacementMode, ReserveMode


class TestPatternStyleConfig:
    """Test PatternStyleConfig validation and functionality."""

    def test_default_pattern_style_config(self):
        """Test default pattern style configuration."""
        config = PatternStyleConfig()
        
        assert config.enabled is False
        assert config.finder is None
        assert config.finder_inner is None
        assert config.timing is None
        assert config.alignment is None
        assert config.format is None
        assert config.version is None
        assert config.data is None
        
        # Color fields
        assert config.finder_color is None
        assert config.finder_inner_color is None
        assert config.timing_color is None
        assert config.alignment_color is None
        assert config.format_color is None
        assert config.version_color is None
        assert config.data_color is None
        
        # Scale fields
        assert config.finder_scale is None
        assert config.timing_scale is None
        assert config.alignment_scale is None
        
        # Effects fields
        assert config.finder_effects is None
        assert config.timing_effects is None
        assert config.alignment_effects is None

    def test_pattern_shape_overrides(self):
        """Test pattern-specific shape overrides."""
        config = PatternStyleConfig(
            enabled=True,
            finder="circle",
            finder_inner="square",
            timing="dot",
            alignment="rounded",
            format="diamond",
            version="star",
            data="squircle"
        )
        
        assert config.enabled is True
        assert config.finder == "circle"
        assert config.finder_inner == "square"
        assert config.timing == "dot"
        assert config.alignment == "rounded"
        assert config.format == "diamond"
        assert config.version == "star"
        assert config.data == "squircle"

    def test_pattern_color_overrides(self):
        """Test pattern-specific color overrides."""
        config = PatternStyleConfig(
            enabled=True,
            finder_color="#e74c3c",
            finder_inner_color="#3498db",
            timing_color="#2ecc71",
            alignment_color="#f39c12",
            format_color="#9b59b6",
            version_color="#e67e22",
            data_color="#1abc9c"
        )
        
        assert config.enabled is True
        assert config.finder_color == "#e74c3c"
        assert config.finder_inner_color == "#3498db"
        assert config.timing_color == "#2ecc71"
        assert config.alignment_color == "#f39c12"
        assert config.format_color == "#9b59b6"
        assert config.version_color == "#e67e22"
        assert config.data_color == "#1abc9c"

    def test_pattern_scale_overrides(self):
        """Test pattern-specific scale overrides."""
        config = PatternStyleConfig(
            enabled=True,
            finder_scale=1.2,
            timing_scale=0.8,
            alignment_scale=1.5
        )
        
        assert config.enabled is True
        assert config.finder_scale == 1.2
        assert config.timing_scale == 0.8
        assert config.alignment_scale == 1.5

    def test_pattern_scale_validation(self):
        """Test pattern scale validation constraints."""
        # Valid scale values
        valid_scales = [0.1, 0.5, 1.0, 1.5, 2.0]
        
        for scale in valid_scales:
            config = PatternStyleConfig(enabled=True, finder_scale=scale)
            assert config.finder_scale == scale
        
        # Invalid scale values
        invalid_scales = [0.05, 2.1, -0.1, 3.0]
        
        for scale in invalid_scales:
            with pytest.raises(ValidationError) as exc_info:
                PatternStyleConfig(enabled=True, finder_scale=scale)
            assert "finder_scale" in str(exc_info.value).lower()

    def test_pattern_effects_overrides(self):
        """Test pattern-specific effects overrides."""
        finder_effects = {"glow": True, "shadow": "2px 2px 4px rgba(0,0,0,0.3)"}
        timing_effects = {"animation": "pulse", "duration": "1s"}
        alignment_effects = {"border": "2px solid #000", "background": "gradient"}
        
        config = PatternStyleConfig(
            enabled=True,
            finder_effects=finder_effects,
            timing_effects=timing_effects,
            alignment_effects=alignment_effects
        )
        
        assert config.enabled is True
        assert config.finder_effects == finder_effects
        assert config.timing_effects == timing_effects
        assert config.alignment_effects == alignment_effects

    def test_enabled_patterns_validation(self):
        """Test validation requiring overrides when enabled."""
        # Should fail when enabled but no overrides specified
        with pytest.raises(ValidationError) as exc_info:
            PatternStyleConfig(enabled=True)
        
        error_message = str(exc_info.value)
        assert "at least one pattern override" in error_message.lower()
        
        # Should pass when enabled with at least one override
        config = PatternStyleConfig(enabled=True, finder="circle")
        assert config.enabled is True
        assert config.finder == "circle"

    def test_pattern_shape_validation(self):
        """Test validation of pattern shape values."""
        # Valid shapes
        valid_shapes = [
            "square", "circle", "rounded", "dot", "diamond",
            "star", "hexagon", "triangle", "squircle", "cross",
            "connected", "connected-extra-rounded",
            "connected-classy", "connected-classy-rounded"
        ]
        
        for shape in valid_shapes:
            config = PatternStyleConfig(enabled=True, finder=shape)
            assert config.finder == shape
        
        # Invalid shapes
        invalid_shapes = ["invalid", "pentagon", "octagon", ""]
        
        for shape in invalid_shapes:
            with pytest.raises(ValidationError) as exc_info:
                PatternStyleConfig(enabled=True, finder=shape)
            assert "invalid shape" in str(exc_info.value).lower()

    def test_complex_pattern_configuration(self):
        """Test complex pattern configuration with multiple overrides."""
        config = PatternStyleConfig(
            enabled=True,
            finder="circle",
            finder_color="#e74c3c",
            finder_scale=1.3,
            finder_effects={"glow": True},
            timing="dot",
            timing_color="#3498db",
            timing_scale=0.7,
            alignment="rounded",
            alignment_color="#2ecc71",
            data="connected-classy-rounded",
            data_color="#f39c12"
        )
        
        assert config.enabled is True
        assert config.finder == "circle"
        assert config.finder_color == "#e74c3c"
        assert config.finder_scale == 1.3
        assert config.finder_effects == {"glow": True}
        assert config.timing == "dot"
        assert config.timing_color == "#3498db"
        assert config.timing_scale == 0.7
        assert config.alignment == "rounded"
        assert config.alignment_color == "#2ecc71"
        assert config.data == "connected-classy-rounded"
        assert config.data_color == "#f39c12"

    def test_disabled_patterns_with_overrides(self):
        """Test that overrides are allowed even when patterns are disabled."""
        # Should allow overrides even when disabled
        config = PatternStyleConfig(
            enabled=False,
            finder="circle",
            finder_color="#e74c3c"
        )
        
        assert config.enabled is False
        assert config.finder == "circle"
        assert config.finder_color == "#e74c3c"


class TestFrameConfig:
    """Test FrameConfig validation and functionality."""

    def test_default_frame_config(self):
        """Test default frame configuration."""
        config = FrameConfig()
        
        assert config.shape == "square"
        assert config.corner_radius == 0.0
        assert config.clip_mode == "clip"
        assert config.custom_path is None
        assert config.fade_distance == 10.0
        assert config.scale_distance == 5.0

    def test_frame_shape_validation(self):
        """Test frame shape validation."""
        valid_shapes = ["square", "circle", "rounded-rect", "squircle"]
        
        for shape in valid_shapes:
            config = FrameConfig(shape=shape)
            assert config.shape == shape
        
        # Test custom shape separately (requires custom_path)
        config = FrameConfig(shape="custom", custom_path="M0,0 L100,100")
        assert config.shape == "custom"

    def test_frame_clip_mode_validation(self):
        """Test frame clip mode validation."""
        valid_modes = ["clip", "fade", "scale"]
        
        for mode in valid_modes:
            config = FrameConfig(clip_mode=mode)
            assert config.clip_mode == mode

    def test_corner_radius_validation(self):
        """Test corner radius validation."""
        # Valid corner radius values
        valid_radii = [0.0, 0.3, 0.5, 1.0]
        
        for radius in valid_radii:
            config = FrameConfig(corner_radius=radius)
            assert config.corner_radius == radius
        
        # Invalid corner radius values
        invalid_radii = [-0.1, 1.1, 2.0]
        
        for radius in invalid_radii:
            with pytest.raises(ValidationError):
                FrameConfig(corner_radius=radius)

    def test_fade_distance_validation(self):
        """Test fade distance validation."""
        # Valid fade distance values
        valid_distances = [0.0, 10.0, 25.0, 50.0]
        
        for distance in valid_distances:
            config = FrameConfig(fade_distance=distance)
            assert config.fade_distance == distance
        
        # Invalid fade distance values
        invalid_distances = [-1.0, 51.0, 100.0]
        
        for distance in invalid_distances:
            with pytest.raises(ValidationError):
                FrameConfig(fade_distance=distance)

    def test_scale_distance_validation(self):
        """Test scale distance validation."""
        # Valid scale distance values
        valid_distances = [0.0, 5.0, 12.5, 25.0]
        
        for distance in valid_distances:
            config = FrameConfig(scale_distance=distance)
            assert config.scale_distance == distance
        
        # Invalid scale distance values
        invalid_distances = [-1.0, 26.0, 50.0]
        
        for distance in invalid_distances:
            with pytest.raises(ValidationError):
                FrameConfig(scale_distance=distance)

    def test_custom_path_validation(self):
        """Test custom path validation."""
        # Custom shape requires custom_path
        with pytest.raises(ValidationError) as exc_info:
            FrameConfig(shape="custom")
        
        assert "custom_path required" in str(exc_info.value).lower()
        
        # Custom shape with path should work
        config = FrameConfig(
            shape="custom",
            custom_path="M0,0 L100,0 L100,100 L0,100 Z"
        )
        assert config.shape == "custom"
        assert config.custom_path == "M0,0 L100,0 L100,100 L0,100 Z"

    def test_complex_frame_configuration(self):
        """Test complex frame configuration."""
        config = FrameConfig(
            shape="rounded-rect",
            corner_radius=0.3,
            clip_mode="fade",
            fade_distance=15.0,
            scale_distance=8.0
        )
        
        assert config.shape == "rounded-rect"
        assert config.corner_radius == 0.3
        assert config.clip_mode == "fade"
        assert config.fade_distance == 15.0
        assert config.scale_distance == 8.0

    def test_custom_svg_path_frame(self):
        """Test custom SVG path frame configuration."""
        svg_path = "M50,0 C22.4,0 0,22.4 0,50 C0,77.6 22.4,100 50,100 C77.6,100 100,77.6 100,50 C100,22.4 77.6,0 50,0 Z"
        
        config = FrameConfig(
            shape="custom",
            custom_path=svg_path,
            clip_mode="clip"
        )
        
        assert config.shape == "custom"
        assert config.custom_path == svg_path
        assert config.clip_mode == "clip"


class TestCenterpieceConfig:
    """Test CenterpieceConfig validation and functionality."""

    def test_default_centerpiece_config(self):
        """Test default centerpiece configuration."""
        config = CenterpieceConfig()
        
        assert config.enabled is False
        assert config.shape == "rect"
        assert config.size == 0.0
        assert config.offset_x == 0.0
        assert config.offset_y == 0.0
        assert config.margin == 2
        assert config.mode == ReserveMode.KNOCKOUT
        assert config.placement == PlacementMode.CENTER

    def test_centerpiece_shape_validation(self):
        """Test centerpiece shape validation."""
        valid_shapes = ["rect", "circle", "squircle"]
        
        for shape in valid_shapes:
            config = CenterpieceConfig(shape=shape)
            assert config.shape == shape

    def test_centerpiece_size_validation(self):
        """Test centerpiece size validation."""
        # Valid size values
        valid_sizes = [0.0, 0.1, 0.25, 0.5]
        
        for size in valid_sizes:
            config = CenterpieceConfig(size=size)
            assert config.size == size
        
        # Invalid size values
        invalid_sizes = [-0.1, 0.6, 1.0, 2.0]
        
        for size in invalid_sizes:
            with pytest.raises(ValidationError):
                CenterpieceConfig(size=size)

    def test_centerpiece_offset_validation(self):
        """Test centerpiece offset validation."""
        # Valid offset values
        valid_offsets = [-0.5, -0.2, 0.0, 0.3, 0.5]
        
        for offset in valid_offsets:
            config = CenterpieceConfig(offset_x=offset, offset_y=offset)
            assert config.offset_x == offset
            assert config.offset_y == offset
        
        # Invalid offset values
        invalid_offsets = [-0.6, 0.6, 1.0, -1.0]
        
        for offset in invalid_offsets:
            with pytest.raises(ValidationError):
                CenterpieceConfig(offset_x=offset)
            with pytest.raises(ValidationError):
                CenterpieceConfig(offset_y=offset)

    def test_centerpiece_margin_validation(self):
        """Test centerpiece margin validation."""
        # Valid margin values
        valid_margins = [0, 1, 2, 5, 10]
        
        for margin in valid_margins:
            config = CenterpieceConfig(margin=margin)
            assert config.margin == margin
        
        # Invalid margin values
        invalid_margins = [-1, -5]
        
        for margin in invalid_margins:
            with pytest.raises(ValidationError):
                CenterpieceConfig(margin=margin)

    def test_centerpiece_mode_validation(self):
        """Test centerpiece mode validation."""
        config = CenterpieceConfig(mode="knockout")
        assert config.mode == ReserveMode.KNOCKOUT
        
        config = CenterpieceConfig(mode="imprint")
        assert config.mode == ReserveMode.IMPRINT

    def test_centerpiece_placement_validation(self):
        """Test centerpiece placement validation."""
        valid_placements = [
            ("custom", PlacementMode.CUSTOM),
            ("center", PlacementMode.CENTER),
            ("top-left", PlacementMode.TOP_LEFT),
            ("top-right", PlacementMode.TOP_RIGHT),
            ("bottom-left", PlacementMode.BOTTOM_LEFT),
            ("bottom-right", PlacementMode.BOTTOM_RIGHT),
            ("top-center", PlacementMode.TOP_CENTER),
            ("bottom-center", PlacementMode.BOTTOM_CENTER),
            ("left-center", PlacementMode.LEFT_CENTER),
            ("right-center", PlacementMode.RIGHT_CENTER)
        ]
        
        for placement_str, placement_enum in valid_placements:
            config = CenterpieceConfig(placement=placement_str)
            assert config.placement == placement_enum

    def test_enabled_centerpiece_validation(self):
        """Test validation when centerpiece is enabled."""
        # Enabled centerpiece with size 0 should fail
        with pytest.raises(ValidationError) as exc_info:
            CenterpieceConfig(enabled=True, size=0.0)
        
        assert "centerpiece size must be > 0" in str(exc_info.value).lower()
        
        # Enabled centerpiece with positive size should work
        config = CenterpieceConfig(enabled=True, size=0.2)
        assert config.enabled is True
        assert config.size == 0.2

    def test_complex_centerpiece_configuration(self):
        """Test complex centerpiece configuration."""
        config = CenterpieceConfig(
            enabled=True,
            shape="circle",
            size=0.25,
            offset_x=0.1,
            offset_y=-0.05,
            margin=3,
            mode="imprint",
            placement="custom"
        )
        
        assert config.enabled is True
        assert config.shape == "circle"
        assert config.size == 0.25
        assert config.offset_x == 0.1
        assert config.offset_y == -0.05
        assert config.margin == 3
        assert config.mode == ReserveMode.IMPRINT
        assert config.placement == PlacementMode.CUSTOM

    def test_centerpiece_placement_modes(self):
        """Test different centerpiece placement modes."""
        placements = [
            "center", "top-left", "top-right", "bottom-left", "bottom-right",
            "top-center", "bottom-center", "left-center", "right-center"
        ]
        
        placement_mappings = {
            "center": PlacementMode.CENTER,
            "top-left": PlacementMode.TOP_LEFT,
            "top-right": PlacementMode.TOP_RIGHT,
            "bottom-left": PlacementMode.BOTTOM_LEFT,
            "bottom-right": PlacementMode.BOTTOM_RIGHT,
            "top-center": PlacementMode.TOP_CENTER,
            "bottom-center": PlacementMode.BOTTOM_CENTER,
            "left-center": PlacementMode.LEFT_CENTER,
            "right-center": PlacementMode.RIGHT_CENTER
        }
        
        for placement_str, placement_enum in placement_mappings.items():
            config = CenterpieceConfig(
                enabled=True,
                size=0.15,
                placement=placement_str
            )
            assert config.placement == placement_enum

    def test_knockout_vs_imprint_modes(self):
        """Test knockout vs imprint reserve modes."""
        # Knockout mode
        knockout_config = CenterpieceConfig(
            enabled=True,
            size=0.2,
            mode="knockout"
        )
        assert knockout_config.mode == ReserveMode.KNOCKOUT
        
        # Imprint mode
        imprint_config = CenterpieceConfig(
            enabled=True,
            size=0.2,
            mode="imprint"
        )
        assert imprint_config.mode == ReserveMode.IMPRINT


class TestQuietZoneConfig:
    """Test QuietZoneConfig validation and functionality."""

    def test_default_quiet_zone_config(self):
        """Test default quiet zone configuration."""
        config = QuietZoneConfig()
        
        assert config.color == "#ffffff"
        assert config.style == "solid"
        assert config.gradient is None

    def test_quiet_zone_color_validation(self):
        """Test quiet zone color validation."""
        valid_colors = ["#ffffff", "#000000", "#e74c3c", "rgb(255,0,0)", "red", "transparent"]
        
        for color in valid_colors:
            config = QuietZoneConfig(color=color)
            assert config.color == color

    def test_quiet_zone_style_validation(self):
        """Test quiet zone style validation."""
        # Test solid and none styles (don't require gradient)
        valid_styles = ["solid", "none"]
        
        for style in valid_styles:
            config = QuietZoneConfig(style=style)
            assert config.style == style
        
        # Test gradient style separately (requires gradient definition)
        gradient_def = {"type": "linear", "stops": []}
        config = QuietZoneConfig(style="gradient", gradient=gradient_def)
        assert config.style == "gradient"

    def test_gradient_validation(self):
        """Test gradient validation."""
        # Gradient style requires gradient definition
        with pytest.raises(ValidationError) as exc_info:
            QuietZoneConfig(style="gradient")
        
        assert "gradient definition required" in str(exc_info.value).lower()
        
        # Gradient style with definition should work
        gradient_def = {
            "type": "linear",
            "stops": [{"offset": "0%", "color": "#fff"}, {"offset": "100%", "color": "#eee"}]
        }
        
        config = QuietZoneConfig(style="gradient", gradient=gradient_def)
        assert config.style == "gradient"
        assert config.gradient == gradient_def

    def test_complex_quiet_zone_configuration(self):
        """Test complex quiet zone configuration."""
        gradient_def = {
            "type": "radial",
            "center": "50% 50%",
            "stops": [
                {"offset": "0%", "color": "#ffffff"},
                {"offset": "50%", "color": "#f8f9fa"},
                {"offset": "100%", "color": "#e9ecef"}
            ]
        }
        
        config = QuietZoneConfig(
            color="#f8f9fa",
            style="gradient",
            gradient=gradient_def
        )
        
        assert config.color == "#f8f9fa"
        assert config.style == "gradient"
        assert config.gradient == gradient_def

    def test_solid_style_without_gradient(self):
        """Test solid style doesn't require gradient."""
        config = QuietZoneConfig(
            color="#e74c3c",
            style="solid"
        )
        
        assert config.color == "#e74c3c"
        assert config.style == "solid"
        assert config.gradient is None


class TestStyleConfig:
    """Test StyleConfig validation and functionality."""

    def test_default_style_config(self):
        """Test default style configuration."""
        config = StyleConfig()
        
        assert config.interactive is False
        assert config.tooltips is False
        assert config.css_classes is None

    def test_interactive_features(self):
        """Test interactive features configuration."""
        config = StyleConfig(interactive=True, tooltips=True)
        
        assert config.interactive is True
        assert config.tooltips is True

    def test_css_classes_validation(self):
        """Test CSS classes validation."""
        valid_css_classes = {
            "qr_module": "custom-module",
            "qr_finder": "custom-finder",
            "qr_timing": "custom-timing",
            "qr_alignment": "custom-alignment",
            "qr_format": "custom-format",
            "qr_version": "custom-version",
            "qr_data": "custom-data",
            "qr_cluster": "custom-cluster"
        }
        
        config = StyleConfig(css_classes=valid_css_classes)
        assert config.css_classes == valid_css_classes

    def test_css_classes_validation_invalid_keys(self):
        """Test CSS classes validation with invalid keys."""
        invalid_css_classes = {
            "invalid_key": "custom-class",
            "qr_module": "valid-class"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            StyleConfig(css_classes=invalid_css_classes)
        
        error_message = str(exc_info.value)
        assert "invalid css class key" in error_message.lower()
        assert "invalid_key" in error_message

    def test_partial_css_classes(self):
        """Test partial CSS classes configuration."""
        partial_css_classes = {
            "qr_module": "module-class",
            "qr_finder": "finder-class"
        }
        
        config = StyleConfig(css_classes=partial_css_classes)
        assert config.css_classes == partial_css_classes

    def test_complex_style_configuration(self):
        """Test complex style configuration."""
        css_classes = {
            "qr_module": "qr-mod animated",
            "qr_finder": "qr-find highlighted",
            "qr_data": "qr-data interactive"
        }
        
        config = StyleConfig(
            interactive=True,
            tooltips=True,
            css_classes=css_classes
        )
        
        assert config.interactive is True
        assert config.tooltips is True
        assert config.css_classes == css_classes

    def test_empty_css_classes(self):
        """Test empty CSS classes configuration."""
        config = StyleConfig(css_classes={})
        assert config.css_classes == {}


class TestVisualConfigIntegration:
    """Test integration between visual configuration models."""

    def test_coordinated_visual_styling(self):
        """Test coordinated visual styling across multiple configs."""
        # Coordinated color scheme
        primary_color = "#e74c3c"
        secondary_color = "#3498db"
        accent_color = "#2ecc71"
        
        pattern_config = PatternStyleConfig(
            enabled=True,
            finder_color=primary_color,
            timing_color=secondary_color,
            data_color=accent_color
        )
        
        quiet_zone_config = QuietZoneConfig(
            color="#ffffff",
            style="solid"
        )
        
        style_config = StyleConfig(
            interactive=True,
            css_classes={
                "qr_finder": "primary-element",
                "qr_timing": "secondary-element",
                "qr_data": "accent-element"
            }
        )
        
        assert pattern_config.finder_color == primary_color
        assert pattern_config.timing_color == secondary_color
        assert pattern_config.data_color == accent_color
        assert quiet_zone_config.color == "#ffffff"
        assert style_config.interactive is True

    def test_frame_centerpiece_interaction(self):
        """Test frame and centerpiece configuration interaction."""
        frame_config = FrameConfig(
            shape="circle",
            clip_mode="fade",
            fade_distance=20.0
        )
        
        centerpiece_config = CenterpieceConfig(
            enabled=True,
            shape="circle",
            size=0.3,
            mode="imprint"
        )
        
        # Both use circular shapes for consistency
        assert frame_config.shape == "circle"
        assert centerpiece_config.shape == "circle"
        assert frame_config.clip_mode == "fade"
        assert centerpiece_config.mode == ReserveMode.IMPRINT

    def test_interactive_styling_combination(self):
        """Test interactive styling with multiple visual elements."""
        style_config = StyleConfig(
            interactive=True,
            tooltips=True,
            css_classes={
                "qr_module": "interactive-module",
                "qr_cluster": "hover-cluster"
            }
        )
        
        pattern_config = PatternStyleConfig(
            enabled=True,
            finder_effects={"hover": "scale(1.1)", "transition": "0.3s"},
            timing_effects={"animation": "pulse 2s infinite"}
        )
        
        assert style_config.interactive is True
        assert style_config.tooltips is True
        assert pattern_config.finder_effects["hover"] == "scale(1.1)"
        assert pattern_config.timing_effects["animation"] == "pulse 2s infinite"

    def test_complex_visual_configuration_scenario(self):
        """Test complex visual configuration scenario."""
        # Create a comprehensive visual configuration
        pattern_config = PatternStyleConfig(
            enabled=True,
            finder="circle",
            finder_color="#e74c3c",
            finder_scale=1.2,
            timing="dot",
            timing_color="#3498db",
            data="connected-classy-rounded",
            data_color="#2ecc71"
        )
        
        frame_config = FrameConfig(
            shape="squircle",
            corner_radius=0.3,
            clip_mode="fade",
            fade_distance=15.0
        )
        
        centerpiece_config = CenterpieceConfig(
            enabled=True,
            shape="squircle",
            size=0.25,
            mode="imprint",
            placement="center",
            margin=3
        )
        
        quiet_zone_config = QuietZoneConfig(
            color="#f8f9fa",
            style="gradient",
            gradient={
                "type": "linear",
                "direction": "to bottom",
                "stops": [
                    {"offset": "0%", "color": "#ffffff"},
                    {"offset": "100%", "color": "#f8f9fa"}
                ]
            }
        )
        
        style_config = StyleConfig(
            interactive=True,
            tooltips=True,
            css_classes={
                "qr_module": "qr-module animated",
                "qr_finder": "qr-finder primary",
                "qr_timing": "qr-timing secondary",
                "qr_data": "qr-data accent"
            }
        )
        
        # Verify all configurations are valid
        assert pattern_config.enabled is True
        assert frame_config.shape == "squircle"
        assert centerpiece_config.enabled is True
        assert quiet_zone_config.style == "gradient"
        assert style_config.interactive is True
        
        # Verify coordinated elements
        assert frame_config.shape == centerpiece_config.shape  # Both squircle
        assert frame_config.corner_radius == 0.3
        assert centerpiece_config.mode == ReserveMode.IMPRINT


class TestVisualConfigEdgeCases:
    """Test edge cases for visual configuration models."""

    def test_pattern_config_boundary_values(self):
        """Test pattern config boundary values."""
        # Minimum scale values
        config = PatternStyleConfig(
            enabled=True,
            finder_scale=0.1,
            timing_scale=0.1,
            alignment_scale=0.1
        )
        assert config.finder_scale == 0.1
        assert config.timing_scale == 0.1
        assert config.alignment_scale == 0.1
        
        # Maximum scale values
        config = PatternStyleConfig(
            enabled=True,
            finder_scale=2.0,
            timing_scale=2.0,
            alignment_scale=2.0
        )
        assert config.finder_scale == 2.0
        assert config.timing_scale == 2.0
        assert config.alignment_scale == 2.0

    def test_frame_config_boundary_values(self):
        """Test frame config boundary values."""
        # Minimum values
        config = FrameConfig(
            corner_radius=0.0,
            fade_distance=0.0,
            scale_distance=0.0
        )
        assert config.corner_radius == 0.0
        assert config.fade_distance == 0.0
        assert config.scale_distance == 0.0
        
        # Maximum values
        config = FrameConfig(
            corner_radius=1.0,
            fade_distance=50.0,
            scale_distance=25.0
        )
        assert config.corner_radius == 1.0
        assert config.fade_distance == 50.0
        assert config.scale_distance == 25.0

    def test_centerpiece_config_boundary_values(self):
        """Test centerpiece config boundary values."""
        # Minimum values
        config = CenterpieceConfig(
            size=0.0,
            offset_x=-0.5,
            offset_y=-0.5,
            margin=0
        )
        assert config.size == 0.0
        assert config.offset_x == -0.5
        assert config.offset_y == -0.5
        assert config.margin == 0
        
        # Maximum values
        config = CenterpieceConfig(
            size=0.5,
            offset_x=0.5,
            offset_y=0.5
        )
        assert config.size == 0.5
        assert config.offset_x == 0.5
        assert config.offset_y == 0.5

    def test_none_value_handling(self):
        """Test handling of None values in optional fields."""
        # All None values should be allowed for optional fields
        pattern_config = PatternStyleConfig(
            enabled=False,
            finder=None,
            finder_color=None,
            finder_scale=None,
            finder_effects=None
        )
        
        assert pattern_config.finder is None
        assert pattern_config.finder_color is None
        assert pattern_config.finder_scale is None
        assert pattern_config.finder_effects is None
        
        frame_config = FrameConfig(custom_path=None)
        assert frame_config.custom_path is None
        
        quiet_zone_config = QuietZoneConfig(gradient=None)
        assert quiet_zone_config.gradient is None
        
        style_config = StyleConfig(css_classes=None)
        assert style_config.css_classes is None

    def test_type_coercion(self):
        """Test type coercion for numeric fields."""
        # Integer to float coercion
        pattern_config = PatternStyleConfig(enabled=True, finder_scale=1)
        assert pattern_config.finder_scale == 1.0
        assert isinstance(pattern_config.finder_scale, float)
        
        # String to float coercion
        frame_config = FrameConfig(corner_radius="0.5")
        assert frame_config.corner_radius == 0.5
        assert isinstance(frame_config.corner_radius, float)
        
        # Float to int coercion for margin
        centerpiece_config = CenterpieceConfig(margin=3.0)
        assert centerpiece_config.margin == 3
        assert isinstance(centerpiece_config.margin, int)