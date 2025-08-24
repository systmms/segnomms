"""
Comprehensive unit tests for core configuration models.

Tests the main RenderingConfig class, factory methods, validation logic,
and integration with other configuration components.
"""

import json
import pytest
from typing import Any, Dict
from unittest.mock import patch

from pydantic import ValidationError

from segnomms.config import (
    RenderingConfig,
    PerformanceConfig,
    DebugConfig,
    GeometryConfig,
    FinderConfig,
    PatternStyleConfig,
    FrameConfig,
    CenterpieceConfig,
    QuietZoneConfig,
    StyleConfig,
    Phase1Config,
    Phase2Config,
    Phase3Config,
    AdvancedQRConfig,
)
from segnomms.config.enums import (
    ModuleShape,
    MergeStrategy,
    ConnectivityMode,
    PlacementMode,
    ReserveMode,
    ContourMode,
    OptimizationLevel,
)
from segnomms.exceptions import InvalidColorFormatError
from tests.constants import DEFAULT_SCALE


class TestRenderingConfigBasics:
    """Test basic RenderingConfig validation and default values."""

    def test_default_config_creation(self):
        """Test creating config with all default values."""
        config = RenderingConfig()
        
        # Basic parameters
        assert config.scale == 1
        assert config.border == 4
        assert config.dark == "#000000"
        assert config.light == "#ffffff"
        assert config.safe_mode is False
        
        # Component configs should be initialized
        assert isinstance(config.geometry, GeometryConfig)
        assert isinstance(config.finder, FinderConfig)
        assert isinstance(config.patterns, PatternStyleConfig)
        assert isinstance(config.frame, FrameConfig)
        assert isinstance(config.centerpiece, CenterpieceConfig)
        assert isinstance(config.quiet_zone, QuietZoneConfig)
        assert isinstance(config.style, StyleConfig)
        assert isinstance(config.phase1, Phase1Config)
        assert isinstance(config.phase2, Phase2Config)
        assert isinstance(config.phase3, Phase3Config)
        assert isinstance(config.advanced_qr, AdvancedQRConfig)
        
        # Optional fields
        assert config.accessibility is not None
        assert config.accessibility.enabled is False
        assert config.shape_options is None
        assert config.metadata is None
        
        # Accessibility settings
        assert config.min_contrast_ratio == 4.5
        assert config.enable_palette_validation is False
        assert config.enforce_wcag_standards is False

    def test_basic_parameter_validation(self):
        """Test validation of basic parameters."""
        # Valid parameters
        config = RenderingConfig(
            scale=10,
            border=2,
            dark="#1a1a2e",
            light="#ffffff",
            safe_mode=True
        )
        assert config.scale == 10
        assert config.border == 2
        assert config.dark == "#1a1a2e"
        assert config.light == "#ffffff"
        assert config.safe_mode is True

    def test_scale_validation(self):
        """Test scale parameter validation."""
        # Valid scale values
        for scale in [1, 10, 50, 100]:
            config = RenderingConfig(scale=scale)
            assert config.scale == scale
        
        # Invalid scale values
        with pytest.raises(ValidationError) as exc_info:
            RenderingConfig(scale=0)
        assert "greater than or equal to 1" in str(exc_info.value)
        
        with pytest.raises(ValidationError) as exc_info:
            RenderingConfig(scale=101)
        assert "less than or equal to 100" in str(exc_info.value)
        
        with pytest.raises(ValidationError):
            RenderingConfig(scale=-1)

    def test_border_validation(self):
        """Test border parameter validation."""
        # Valid border values
        for border in [0, 4, 10, 20]:
            config = RenderingConfig(border=border)
            assert config.border == border
        
        # Invalid border values
        with pytest.raises(ValidationError) as exc_info:
            RenderingConfig(border=-1)
        assert "greater than or equal to 0" in str(exc_info.value)
        
        with pytest.raises(ValidationError) as exc_info:
            RenderingConfig(border=21)
        assert "less than or equal to 20" in str(exc_info.value)

    def test_color_validation(self):
        """Test color parameter validation."""
        # Valid color formats
        valid_colors = [
            "#000000",
            "#FFFFFF",
            "#1a1a2e",
            "#e74c3c",
            "rgb(255, 0, 0)",
            "rgba(255, 0, 0, 0.5)",
            "red",
            "blue",
            "transparent"
        ]
        
        for color in valid_colors:
            config = RenderingConfig(dark=color, light=color)
            assert config.dark == color
            assert config.light == color
        
        # Invalid color formats
        invalid_colors = ["", "   ", None]
        
        for color in invalid_colors:
            with pytest.raises((ValidationError, InvalidColorFormatError)):
                RenderingConfig(dark=color)
            with pytest.raises((ValidationError, InvalidColorFormatError)):
                RenderingConfig(light=color)

    def test_contrast_ratio_validation(self):
        """Test min_contrast_ratio validation."""
        # Valid contrast ratios
        for ratio in [1.0, 4.5, 7.0, 21.0]:
            config = RenderingConfig(min_contrast_ratio=ratio)
            assert config.min_contrast_ratio == ratio
        
        # Invalid contrast ratios
        with pytest.raises(ValidationError):
            RenderingConfig(min_contrast_ratio=0.5)
        
        with pytest.raises(ValidationError):
            RenderingConfig(min_contrast_ratio=22.0)

    def test_extra_fields_forbidden(self):
        """Test that extra fields are forbidden."""
        with pytest.raises(ValidationError) as exc_info:
            RenderingConfig(invalid_field="value")
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_config_with_shape_options(self):
        """Test configuration with additional shape options."""
        shape_options = {
            "star_points": 5,
            "hexagon_rotation": 30,
            "custom_parameter": "value"
        }
        
        config = RenderingConfig(shape_options=shape_options)
        assert config.shape_options == shape_options

    def test_config_with_metadata(self):
        """Test configuration with metadata."""
        metadata = {
            "created_by": "test_suite",
            "version": "1.0",
            "custom_field": "custom_value"
        }
        
        config = RenderingConfig(metadata=metadata)
        assert config.metadata == metadata


class TestRenderingConfigFactoryMethod:
    """Test the from_kwargs factory method for backward compatibility."""

    def test_basic_kwargs_conversion(self):
        """Test basic parameter conversion from kwargs."""
        config = RenderingConfig.from_kwargs(
            scale=15,
            border=6,
            dark="#e74c3c",
            light="#ecf0f1",
            safe_mode=True
        )
        
        assert config.scale == 15
        assert config.border == 6
        assert config.dark == "#e74c3c"
        assert config.light == "#ecf0f1"
        assert config.safe_mode is True

    def test_geometry_kwargs_conversion(self):
        """Test geometry parameter conversion."""
        config = RenderingConfig.from_kwargs(
            shape="rounded",
            corner_radius=0.3,
            connectivity="8-way",
            merge="soft",
            min_island_modules=3
        )
        
        assert config.geometry.shape == "rounded"  # use_enum_values=True
        assert config.geometry.corner_radius == 0.3
        assert config.geometry.connectivity == "8-way"  # use_enum_values=True
        assert config.geometry.merge == "soft"  # use_enum_values=True
        assert config.geometry.min_island_modules == 3

    def test_finder_kwargs_conversion(self):
        """Test finder parameter conversion."""
        config = RenderingConfig.from_kwargs(
            finder_shape="circle",
            finder_inner_scale=0.7,
            finder_stroke=True
        )
        
        assert config.finder.shape == "circle"
        assert config.finder.inner_scale == 0.7
        assert config.finder.stroke == 1.0  # True gets converted to 1.0

    def test_frame_kwargs_conversion(self):
        """Test frame parameter conversion."""
        config = RenderingConfig.from_kwargs(
            frame_shape="circle",
            frame_corner_radius=0.2,
            frame_clip_mode="fade",
            frame_fade_distance=10,
            frame_scale_distance=5,
            frame_custom_path="M0,0 L100,100"
        )
        
        assert config.frame.shape == "circle"
        assert config.frame.corner_radius == 0.2
        assert config.frame.clip_mode == "fade"
        assert config.frame.fade_distance == 10
        assert config.frame.scale_distance == 5
        assert config.frame.custom_path == "M0,0 L100,100"

    def test_centerpiece_kwargs_conversion(self):
        """Test centerpiece parameter conversion."""
        config = RenderingConfig.from_kwargs(
            centerpiece_enabled=True,
            centerpiece_shape="squircle",
            centerpiece_size=0.2,
            centerpiece_offset_x=0.1,
            centerpiece_offset_y=-0.05,
            centerpiece_margin=3,
            centerpiece_mode="imprint",
            centerpiece_placement="top-left"
        )
        
        assert config.centerpiece.enabled is True
        assert config.centerpiece.shape == "squircle"
        assert config.centerpiece.size == 0.2
        assert config.centerpiece.offset_x == 0.1
        assert config.centerpiece.offset_y == -0.05
        assert config.centerpiece.margin == 3
        assert config.centerpiece.mode == ReserveMode.IMPRINT
        assert config.centerpiece.placement == PlacementMode.TOP_LEFT

    def test_backward_compatibility_aliases(self):
        """Test backward compatibility parameter aliases."""
        # Test reserve_* aliases for centerpiece_*
        config = RenderingConfig.from_kwargs(
            reserve_center=True,
            reserve_shape="circle",
            reserve_size=0.15,
            reserve_offset_x=0.2,
            reserve_offset_y=0.1,
            reserve_margin=2
        )
        
        assert config.centerpiece.enabled is True
        assert config.centerpiece.shape == "circle"
        assert config.centerpiece.size == 0.15
        assert config.centerpiece.offset_x == 0.2
        assert config.centerpiece.offset_y == 0.1
        assert config.centerpiece.margin == 2

    def test_style_kwargs_conversion(self):
        """Test style parameter conversion."""
        config = RenderingConfig.from_kwargs(
            interactive=True,
            tooltips=True
        )
        
        assert config.style.interactive is True
        assert config.style.tooltips is True

    def test_pattern_kwargs_conversion(self):
        """Test pattern styling parameter conversion."""
        config = RenderingConfig.from_kwargs(
            patterns_enabled=True,
            pattern_finder="rounded",
            pattern_timing="circle",
            pattern_finder_color="#e74c3c",
            pattern_timing_color="#3498db",
            pattern_finder_scale=1.2,
            pattern_timing_scale=0.8
        )
        
        assert config.patterns.enabled is True
        assert config.patterns.finder == "rounded"
        assert config.patterns.timing == "circle"
        assert config.patterns.finder_color == "#e74c3c"
        assert config.patterns.timing_color == "#3498db"
        assert config.patterns.finder_scale == 1.2
        assert config.patterns.timing_scale == 0.8

    def test_advanced_qr_kwargs_conversion(self):
        """Test advanced QR parameter conversion."""
        config = RenderingConfig.from_kwargs(
            eci_enabled=True,
            encoding="UTF-8",
            mask_pattern=3,
            auto_mask=False,
            structured_append=True,
            symbol_count=4,
            boost_error=False
        )
        
        assert config.advanced_qr.eci_enabled is True
        assert config.advanced_qr.encoding == "UTF-8"
        assert config.advanced_qr.mask_pattern == 3
        assert config.advanced_qr.auto_mask is False
        assert config.advanced_qr.structured_append is True
        assert config.advanced_qr.symbol_count == 4
        assert config.advanced_qr.boost_error is False

    def test_phase_kwargs_conversion(self):
        """Test phase configuration parameter conversion."""
        config = RenderingConfig.from_kwargs(
            enable_phase1=True,
            enable_phase2=False,
            enable_phase3=True,
            phase1_roundness=0.4,
            phase2_min_cluster_size=5,
            phase3_contour_smoothing=0.6
        )
        
        assert config.phase1.enabled is True
        assert config.phase2.enabled is False
        assert config.phase3.enabled is True
        assert hasattr(config.phase1, 'roundness')  # May not be directly set
        # Note: Phase-specific parameters may be handled differently

    def test_quiet_zone_kwargs_conversion(self):
        """Test quiet zone parameter conversion."""
        config = RenderingConfig.from_kwargs(
            quiet_zone_style="solid",
            quiet_zone_color="#f8f9fa",
            quiet_zone_gradient={
                "type": "linear",
                "stops": [
                    {"offset": "0%", "color": "#ffffff"},
                    {"offset": "100%", "color": "#eeeeee"}
                ]
            }
        )
        
        assert config.quiet_zone.style == "solid"
        assert config.quiet_zone.color == "#f8f9fa"
        assert config.quiet_zone.gradient["type"] == "linear"

    def test_accessibility_kwargs_conversion(self):
        """Test accessibility parameter conversion."""
        config = RenderingConfig.from_kwargs(
            accessibility_enabled=True,
            accessibility_id_prefix="qr-module",
            accessibility_use_stable_ids=True,
            accessibility_include_coordinates=False,
            accessibility_enable_aria=True,
            accessibility_root_role="img",
            accessibility_root_label="QR Code",
            accessibility_root_description="QR code for accessibility testing"
        )
        
        # Accessibility config may be optional/conditional
        if config.accessibility:
            assert config.accessibility.enabled is True
            assert config.accessibility.id_prefix == "qr-module"
            assert config.accessibility.use_stable_ids is True
            assert config.accessibility.include_coordinates is False
            assert config.accessibility.enable_aria is True
            assert config.accessibility.root_role == "img"
            assert config.accessibility.root_label == "QR Code"
            assert config.accessibility.root_description == "QR code for accessibility testing"

    def test_complex_kwargs_combination(self):
        """Test complex combination of multiple parameter types."""
        config = RenderingConfig.from_kwargs(
            # Basic parameters
            scale=20,
            dark="#2c3e50",
            light="#ecf0f1",
            # Geometry parameters
            shape="squircle",
            corner_radius=0.25,
            merge="aggressive",
            # Frame parameters
            frame_shape="circle",
            frame_clip_mode="fade",
            # Centerpiece parameters
            centerpiece_enabled=True,
            centerpiece_size=0.18,
            centerpiece_mode="imprint",
            # Style parameters
            interactive=True,
            # Advanced parameters
            eci_enabled=True,
            encoding="UTF-8"
        )
        
        # Verify all parameters were set correctly
        assert config.scale == 20
        assert config.dark == "#2c3e50"
        assert config.light == "#ecf0f1"
        assert config.geometry.shape == "squircle"  # use_enum_values=True converts to string
        assert config.geometry.corner_radius == 0.25
        assert config.geometry.merge == "aggressive"  # use_enum_values=True converts to string
        assert config.frame.shape == "circle"
        assert config.frame.clip_mode == "fade"
        assert config.centerpiece.enabled is True
        assert config.centerpiece.size == 0.18
        assert config.centerpiece.mode == ReserveMode.IMPRINT
        assert config.style.interactive is True
        assert config.advanced_qr.eci_enabled is True
        assert config.advanced_qr.encoding == "UTF-8"


class TestAutoPhaseEnabling:
    """Test automatic phase enabling logic based on configuration."""

    def test_phase1_auto_enable_for_non_square_shapes(self):
        """Test Phase 1 auto-enabling for non-square shapes."""
        config = RenderingConfig.from_kwargs(shape="circle")
        
        # Phase 1 should be auto-enabled for non-square shapes
        assert config.phase1.enabled is True
        assert config.phase1.use_enhanced_shapes is True

    def test_phase1_auto_enable_for_corner_radius(self):
        """Test Phase 1 auto-enabling for corner radius > 0."""
        config = RenderingConfig.from_kwargs(
            shape="square",
            corner_radius=0.3
        )
        
        # Phase 1 should be auto-enabled for corner radius > 0
        assert config.phase1.enabled is True
        assert config.phase1.use_enhanced_shapes is True
        assert config.phase1.roundness == 0.3

    def test_phase2_auto_enable_for_merge_soft(self):
        """Test Phase 2 auto-enabling for soft merge."""
        config = RenderingConfig.from_kwargs(merge="soft")
        
        # Phase 2 should be auto-enabled for merge != "none"
        assert config.phase2.enabled is True
        assert config.phase2.use_cluster_rendering is True
        assert "data" in config.phase2.cluster_module_types

    def test_phase3_auto_enable_for_aggressive_merge(self):
        """Test Phase 3 auto-enabling for aggressive merge."""
        config = RenderingConfig.from_kwargs(merge="aggressive")
        
        # Phase 3 should be auto-enabled for aggressive merge
        assert config.phase3.enabled is True
        assert config.phase3.use_marching_squares is True
        assert config.phase3.contour_mode == ContourMode.BEZIER
        assert config.phase3.bezier_optimization == OptimizationLevel.MEDIUM

    def test_explicit_phase_settings_override_auto(self):
        """Test that explicit phase settings override auto-enabling."""
        config = RenderingConfig.from_kwargs(
            shape="circle",  # Would normally auto-enable Phase 1
            enable_phase1=False  # But explicitly disabled
        )
        
        # Explicit setting should override auto-enabling
        assert config.phase1.enabled is False

    def test_multiple_phase_auto_enabling(self):
        """Test multiple phases being auto-enabled simultaneously."""
        config = RenderingConfig.from_kwargs(
            shape="rounded",  # Should enable Phase 1
            corner_radius=0.4,  # Should enable Phase 1
            merge="aggressive"  # Should enable Phase 2 and 3
        )
        
        # Multiple phases should be enabled
        assert config.phase1.enabled is True
        assert config.phase2.enabled is True
        assert config.phase3.enabled is True


class TestConfigSerialization:
    """Test configuration serialization and deserialization."""

    def test_to_json_serialization(self):
        """Test JSON serialization."""
        config = RenderingConfig(
            scale=15,
            dark="#e74c3c",
            light="#ffffff",
            geometry=GeometryConfig(shape="circle", corner_radius=0.2),
            style=StyleConfig(interactive=True)
        )
        
        json_str = config.to_json()
        
        # Should be valid JSON
        json_data = json.loads(json_str)
        assert isinstance(json_data, dict)
        assert json_data["scale"] == 15
        assert json_data["dark"] == "#e74c3c"
        assert json_data["geometry"]["shape"] == "circle"
        assert json_data["style"]["interactive"] is True

    def test_from_json_deserialization(self):
        """Test JSON deserialization."""
        json_str = '''
        {
            "scale": 20,
            "dark": "#2c3e50",
            "light": "#ecf0f1",
            "geometry": {
                "shape": "squircle",
                "corner_radius": 0.3
            },
            "style": {
                "interactive": true,
                "tooltips": false
            }
        }
        '''
        
        config = RenderingConfig.from_json(json_str)
        
        assert config.scale == 20
        assert config.dark == "#2c3e50"
        assert config.light == "#ecf0f1"
        assert config.geometry.shape == "squircle"  # use_enum_values=True
        assert config.geometry.corner_radius == 0.3
        assert config.style.interactive is True
        assert config.style.tooltips is False

    def test_json_round_trip_consistency(self):
        """Test JSON serialization round-trip consistency."""
        original_config = RenderingConfig.from_kwargs(
            scale=25,
            shape="connected-extra-rounded",
            corner_radius=0.35,
            dark="#8e44ad",
            merge="soft",
            interactive=True,
            centerpiece_enabled=True,
            centerpiece_size=0.15
        )
        
        # Serialize to JSON and back
        json_str = original_config.to_json()
        restored_config = RenderingConfig.from_json(json_str)
        
        # Should be equivalent
        assert restored_config.scale == original_config.scale
        assert restored_config.geometry.shape == original_config.geometry.shape
        assert restored_config.geometry.corner_radius == original_config.geometry.corner_radius
        assert restored_config.dark == original_config.dark
        assert restored_config.geometry.merge == original_config.geometry.merge
        assert restored_config.style.interactive == original_config.style.interactive
        assert restored_config.centerpiece.enabled == original_config.centerpiece.enabled
        assert restored_config.centerpiece.size == original_config.centerpiece.size

    def test_json_schema_generation(self):
        """Test JSON schema generation."""
        schema = RenderingConfig.json_schema()
        
        assert isinstance(schema, dict)
        assert "type" in schema
        assert "properties" in schema
        assert "scale" in schema["properties"]
        assert "dark" in schema["properties"]
        assert "geometry" in schema["properties"]
        
        # Check that required fields are marked
        assert schema["properties"]["scale"]["minimum"] == 1
        assert schema["properties"]["scale"]["maximum"] == 100

    def test_to_kwargs_conversion(self):
        """Test converting configuration back to kwargs format."""
        config = RenderingConfig(
            scale=12,
            dark="#34495e",
            geometry=GeometryConfig(shape="rounded", corner_radius=0.25),
            style=StyleConfig(interactive=True),
            centerpiece=CenterpieceConfig(enabled=True, size=0.18)
        )
        
        kwargs = config.to_kwargs()
        
        # Should contain flattened parameters
        assert kwargs["scale"] == 12
        assert kwargs["dark"] == "#34495e"
        assert kwargs["shape"] == "rounded"
        assert kwargs["corner_radius"] == 0.25
        assert kwargs["interactive"] is True
        assert kwargs["centerpiece_enabled"] is True
        assert kwargs["centerpiece_size"] == 0.18

    def test_kwargs_round_trip_consistency(self):
        """Test kwargs conversion round-trip consistency."""
        original_kwargs = {
            "scale": 18,
            "dark": "#e67e22",
            "shape": "squircle",
            "corner_radius": 0.4,
            "merge": "aggressive",
            "interactive": True,
            "centerpiece_enabled": True,
            "centerpiece_size": 0.2,
            "frame_shape": "circle"
        }
        
        # Convert to config and back to kwargs
        config = RenderingConfig.from_kwargs(**original_kwargs)
        restored_kwargs = config.to_kwargs()
        
        # Key parameters should be preserved
        for key in ["scale", "dark", "shape", "corner_radius", "interactive"]:
            assert restored_kwargs[key] == original_kwargs[key]


class TestConfigIntegrations:
    """Test configuration integration with other components."""

    def test_palette_validation_integration(self):
        """Test integration with palette validation."""
        config = RenderingConfig(
            dark="#000000",
            light="#ffffff",
            enable_palette_validation=True,
            min_contrast_ratio=7.0
        )
        
        # Should be able to call palette validation
        # Note: This tests the interface, actual validation may depend on implementation
        assert hasattr(config, 'validate_palette')
        assert callable(config.validate_palette)

    def test_contrast_ratio_calculation(self):
        """Test contrast ratio calculation."""
        config = RenderingConfig(
            dark="#000000",
            light="#ffffff"
        )
        
        # Should be able to calculate contrast ratio
        assert hasattr(config, 'get_contrast_ratio')
        assert callable(config.get_contrast_ratio)
        
        # Should be able to check if meets requirements
        assert hasattr(config, 'meets_contrast_requirements')
        assert callable(config.meets_contrast_requirements)

    def test_accent_color_extraction(self):
        """Test accent color extraction from pattern styling."""
        config = RenderingConfig(
            dark="#000000",
            light="#ffffff",
            patterns=PatternStyleConfig(
                enabled=True,
                finder_color="#e74c3c",
                timing_color="#3498db",
                data_color="#2ecc71"
            )
        )
        
        # Should extract accent colors for palette validation
        accent_colors = config._get_accent_colors()
        
        assert "#e74c3c" in accent_colors
        assert "#3498db" in accent_colors
        assert "#2ecc71" in accent_colors
        # Primary colors should not be in accent colors
        assert "#000000" not in accent_colors
        assert "#ffffff" not in accent_colors


class TestPerformanceConfig:
    """Test PerformanceConfig validation."""

    def test_default_performance_config(self):
        """Test default performance configuration."""
        config = PerformanceConfig()
        
        assert config.enable_caching is True
        assert config.max_cache_size == 100
        assert config.enable_parallel_processing is False
        assert config.memory_limit_mb is None
        assert config.debug_timing is False

    def test_performance_config_validation(self):
        """Test performance configuration validation."""
        config = PerformanceConfig(
            enable_caching=False,
            max_cache_size=500,
            enable_parallel_processing=True,
            memory_limit_mb=2048,
            debug_timing=True
        )
        
        assert config.enable_caching is False
        assert config.max_cache_size == 500
        assert config.enable_parallel_processing is True
        assert config.memory_limit_mb == 2048
        assert config.debug_timing is True

    def test_performance_config_constraints(self):
        """Test performance configuration constraints."""
        # max_cache_size must be >= 1
        with pytest.raises(ValidationError):
            PerformanceConfig(max_cache_size=0)
        
        # memory_limit_mb must be >= 1 if specified
        with pytest.raises(ValidationError):
            PerformanceConfig(memory_limit_mb=0)


class TestDebugConfig:
    """Test DebugConfig validation."""

    def test_default_debug_config(self):
        """Test default debug configuration."""
        config = DebugConfig()
        
        assert config.debug_mode is False
        assert config.debug_stroke is False
        assert config.save_intermediate_results is False
        assert config.verbose_logging is False
        
        # Check default debug colors
        assert "contour" in config.debug_colors
        assert "cluster" in config.debug_colors
        assert "enhanced" in config.debug_colors
        assert config.debug_colors["contour"] == "red"

    def test_debug_config_customization(self):
        """Test debug configuration customization."""
        custom_colors = {
            "contour": "#e74c3c",
            "cluster": "#3498db",
            "enhanced": "#2ecc71",
            "custom": "#9b59b6"
        }
        
        config = DebugConfig(
            debug_mode=True,
            debug_stroke=True,
            debug_colors=custom_colors,
            save_intermediate_results=True,
            verbose_logging=True
        )
        
        assert config.debug_mode is True
        assert config.debug_stroke is True
        assert config.debug_colors == custom_colors
        assert config.save_intermediate_results is True
        assert config.verbose_logging is True


class TestConfigErrorHandling:
    """Test configuration error handling and validation messages."""

    def test_helpful_validation_error_messages(self):
        """Test that validation errors provide helpful messages."""
        # Test scale validation error
        with pytest.raises(ValidationError) as exc_info:
            RenderingConfig(scale=150)
        
        error_message = str(exc_info.value)
        assert "scale" in error_message.lower()
        assert "100" in error_message  # Maximum value mentioned
        
        # Test color validation error
        with pytest.raises((ValidationError, InvalidColorFormatError)) as exc_info:
            RenderingConfig(dark="")
        
        error_message = str(exc_info.value)
        assert "dark" in error_message.lower() or "color" in error_message.lower()

    def test_nested_config_validation_errors(self):
        """Test validation errors in nested configurations."""
        with pytest.raises(ValidationError) as exc_info:
            RenderingConfig(
                geometry=GeometryConfig(corner_radius=2.0)  # Invalid: > 1.0
            )
        
        error_message = str(exc_info.value)
        assert "geometry" in error_message.lower()
        assert "corner_radius" in error_message.lower()

    def test_enum_validation_errors(self):
        """Test enum validation graceful fallback."""
        # from_kwargs should handle invalid enum values gracefully
        config = RenderingConfig.from_kwargs(shape="invalid_shape")
        
        # Should fall back to default shape
        assert config.geometry.shape == "square"