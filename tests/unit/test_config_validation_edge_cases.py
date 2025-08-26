"""
Comprehensive edge case tests for configuration validation.

Tests complex validation scenarios, cross-field validation, integration
constraints, and boundary conditions across all configuration models.
"""

import pytest
from pydantic import ValidationError

from segnomms.config import (
    AdvancedQRConfig,
    CenterpieceConfig,
    DebugConfig,
    FinderConfig,
    FrameConfig,
    GeometryConfig,
    PatternStyleConfig,
    PerformanceConfig,
    Phase1Config,
    Phase2Config,
    Phase3Config,
    QuietZoneConfig,
    RenderingConfig,
    StyleConfig,
)
from segnomms.config.enums import (
    ModuleShape,
    ReserveMode,
)


class TestCrossFieldValidation:
    """Test cross-field validation scenarios across configuration models."""

    def test_frame_custom_path_validation(self):
        """Test frame custom path cross-field validation."""
        # Custom shape requires custom_path
        with pytest.raises(ValidationError) as exc_info:
            FrameConfig(shape="custom")

        error_message = str(exc_info.value)
        assert "custom_path required" in error_message.lower()

        # Custom shape with path should work
        config = FrameConfig(shape="custom", custom_path="M0,0 L100,100 Z")
        assert config.shape == "custom"
        assert config.custom_path == "M0,0 L100,100 Z"

        # Non-custom shapes don't need custom_path
        config = FrameConfig(shape="circle", custom_path=None)
        assert config.shape == "circle"
        assert config.custom_path is None

    def test_quiet_zone_gradient_validation(self):
        """Test quiet zone gradient cross-field validation."""
        # Gradient style requires gradient definition
        with pytest.raises(ValidationError) as exc_info:
            QuietZoneConfig(style="gradient")

        error_message = str(exc_info.value)
        assert "gradient definition required" in error_message.lower()

        # Gradient style with definition should work
        gradient_def = {"type": "linear", "stops": []}
        config = QuietZoneConfig(style="gradient", gradient=gradient_def)
        assert config.style == "gradient"
        assert config.gradient == gradient_def

        # Non-gradient styles don't need gradient definition
        config = QuietZoneConfig(style="solid", gradient=None)
        assert config.style == "solid"
        assert config.gradient is None

    def test_centerpiece_enabled_size_validation(self):
        """Test centerpiece enabled size cross-field validation."""
        # Enabled centerpiece with size 0 should fail
        with pytest.raises(ValidationError) as exc_info:
            CenterpieceConfig(enabled=True, size=0.0)

        error_message = str(exc_info.value)
        assert "centerpiece size must be > 0" in error_message.lower()

        # Enabled centerpiece with positive size should work
        config = CenterpieceConfig(enabled=True, size=0.2)
        assert config.enabled is True
        assert config.size == 0.2

        # Disabled centerpiece can have size 0
        config = CenterpieceConfig(enabled=False, size=0.0)
        assert config.enabled is False
        assert config.size == 0.0

    def test_pattern_styling_enabled_validation(self):
        """Test pattern styling enabled cross-field validation."""
        # Enabled patterns require at least one override
        with pytest.raises(ValidationError) as exc_info:
            PatternStyleConfig(enabled=True)

        error_message = str(exc_info.value)
        assert "at least one pattern override" in error_message.lower()

        # Enabled patterns with override should work
        config = PatternStyleConfig(enabled=True, finder="circle")
        assert config.enabled is True
        assert config.finder == "circle"

        # Disabled patterns can have no overrides
        config = PatternStyleConfig(enabled=False)
        assert config.enabled is False

    def test_advanced_qr_mask_pattern_auto_mask_consistency(self):
        """Test advanced QR mask pattern and auto_mask consistency."""
        # Manual mask pattern should disable auto_mask
        config = AdvancedQRConfig(mask_pattern=3, auto_mask=True)
        assert config.mask_pattern == 3
        assert config.auto_mask is False  # Should be overridden

        # No mask pattern should preserve auto_mask setting
        config = AdvancedQRConfig(mask_pattern=None, auto_mask=True)
        assert config.mask_pattern is None
        assert config.auto_mask is True

    def test_advanced_qr_structured_append_consistency(self):
        """Test advanced QR structured append consistency."""
        # Structured append enabled without symbol_count should default to 2
        config = AdvancedQRConfig(structured_append=True)
        assert config.structured_append is True
        assert config.symbol_count == 2

        # Structured append disabled with symbol_count should warn but work
        config = AdvancedQRConfig(structured_append=False, symbol_count=4)
        assert config.structured_append is False
        assert config.symbol_count == 4

    def test_advanced_qr_eci_encoding_consistency(self):
        """Test advanced QR ECI and encoding consistency."""
        # ECI enabled without encoding should default to UTF-8
        config = AdvancedQRConfig(eci_enabled=True)
        assert config.eci_enabled is True
        assert config.encoding == "UTF-8"

        # Encoding without ECI should work but may log info
        config = AdvancedQRConfig(eci_enabled=False, encoding="ISO-8859-1")
        assert config.eci_enabled is False
        assert config.encoding == "ISO-8859-1"


class TestConfigurationIntegrationConstraints:
    """Test integration constraints between different configuration models."""

    def test_geometry_phase_auto_enabling_integration(self):
        """Test geometry configuration auto-enabling phases."""
        # Non-square shape should auto-enable Phase 1
        config = RenderingConfig.from_kwargs(shape="circle")
        assert config.phase1.enabled is True
        assert config.phase1.use_enhanced_shapes is True

        # Corner radius > 0 should auto-enable Phase 1
        config = RenderingConfig.from_kwargs(corner_radius=0.3)
        assert config.phase1.enabled is True
        assert config.phase1.roundness == 0.3

        # Soft merge should auto-enable Phase 2
        config = RenderingConfig.from_kwargs(merge="soft")
        assert config.phase2.enabled is True
        assert config.phase2.use_cluster_rendering is True

        # Aggressive merge should auto-enable Phase 2 and 3
        config = RenderingConfig.from_kwargs(merge="aggressive")
        assert config.phase2.enabled is True
        assert config.phase3.enabled is True
        assert config.phase3.use_marching_squares is True

    def test_explicit_phase_settings_override_auto_enabling(self):
        """Test that explicit phase settings override auto-enabling."""
        # Explicitly disable Phase 1 even with non-square shape
        config = RenderingConfig.from_kwargs(shape="circle", enable_phase1=False)
        assert config.phase1.enabled is False

        # Explicitly disable Phase 2 even with soft merge
        config = RenderingConfig.from_kwargs(merge="soft", enable_phase2=False)
        assert config.phase2.enabled is False

    def test_phase_module_type_consistency(self):
        """Test module type consistency across phases."""
        # Configure phases to work on consistent module types
        config = RenderingConfig(
            phase2=Phase2Config(enabled=True, cluster_module_types=["data", "timing"]),
            phase3=Phase3Config(enabled=True, contour_module_types=["data", "timing"]),
        )

        assert config.phase2.cluster_module_types == ["data", "timing"]
        assert config.phase3.contour_module_types == ["data", "timing"]

    def test_performance_debug_interaction(self):
        """Test performance and debug configuration interaction."""
        # Development mode with extensive debugging (separate configs)
        performance_config = PerformanceConfig(
            enable_caching=False, debug_timing=True  # Disable for consistent debugging
        )
        debug_config = DebugConfig(debug_mode=True, verbose_logging=True, save_intermediate_results=True)

        assert performance_config.enable_caching is False
        assert performance_config.debug_timing is True
        assert debug_config.debug_mode is True
        assert debug_config.verbose_logging is True

        # Production mode with optimized performance (separate configs)
        performance_config = PerformanceConfig(
            enable_caching=True,
            max_cache_size=10000,
            enable_parallel_processing=True,
            debug_timing=False,
        )
        debug_config = DebugConfig(debug_mode=False, verbose_logging=False, save_intermediate_results=False)

        assert performance_config.enable_caching is True
        assert performance_config.enable_parallel_processing is True
        assert debug_config.debug_mode is False

    def test_style_pattern_integration(self):
        """Test style and pattern configuration integration."""
        # Interactive styling with pattern overrides
        config = RenderingConfig(
            style=StyleConfig(
                interactive=True,
                css_classes={
                    "qr_finder": "interactive-finder",
                    "qr_timing": "interactive-timing",
                    "qr_data": "interactive-data",
                },
            ),
            patterns=PatternStyleConfig(
                enabled=True,
                finder="circle",
                finder_color="#e74c3c",
                timing="dot",
                timing_color="#3498db",
                data="connected-classy-rounded",
                data_color="#2ecc71",
            ),
        )

        assert config.style.interactive is True
        assert "qr_finder" in config.style.css_classes
        assert config.patterns.enabled is True
        assert config.patterns.finder_color == "#e74c3c"
        assert config.patterns.data == "connected-classy-rounded"

    def test_frame_centerpiece_shape_coordination(self):
        """Test frame and centerpiece shape coordination."""
        # Coordinated circular frame and centerpiece
        config = RenderingConfig(
            frame=FrameConfig(shape="circle", clip_mode="fade", fade_distance=15.0),
            centerpiece=CenterpieceConfig(enabled=True, shape="circle", size=0.25, mode="imprint"),
        )

        assert config.frame.shape == "circle"
        assert config.centerpiece.shape == "circle"
        assert config.frame.clip_mode == "fade"
        assert config.centerpiece.mode == ReserveMode.IMPRINT


class TestBoundaryConditionEdgeCases:
    """Test boundary conditions and extreme values across configurations."""

    def test_numeric_parameter_boundaries(self):
        """Test numeric parameters at exact boundaries."""
        # Scale boundaries
        config = RenderingConfig(scale=1)  # Minimum
        assert config.scale == 1

        config = RenderingConfig(scale=100)  # Maximum
        assert config.scale == 100

        # Border boundaries
        config = RenderingConfig(border=0)  # Minimum
        assert config.border == 0

        config = RenderingConfig(border=20)  # Maximum
        assert config.border == 20

        # Corner radius boundaries
        config = GeometryConfig(corner_radius=0.0)  # Minimum
        assert config.corner_radius == 0.0

        config = GeometryConfig(corner_radius=1.0)  # Maximum
        assert config.corner_radius == 1.0

    def test_floating_point_precision_boundaries(self):
        """Test floating point precision at boundaries."""
        # Very small positive values
        config = Phase1Config(roundness=0.001)
        assert config.roundness == 0.001

        # Very close to upper boundary
        config = Phase3Config(tension=0.999)
        assert config.tension == 0.999

        # Exact boundary values
        config = CenterpieceConfig(size=0.5)  # Exact maximum
        assert config.size == 0.5

        config = FinderConfig(inner_scale=0.1)  # Exact minimum
        assert config.inner_scale == 0.1

    def test_integer_parameter_boundaries(self):
        """Test integer parameters at boundaries."""
        # Cache size boundaries
        config = PerformanceConfig(max_cache_size=1)  # Minimum
        assert config.max_cache_size == 1

        # Symbol count boundaries
        config = AdvancedQRConfig(structured_append=True, symbol_count=2)  # Minimum
        assert config.symbol_count == 2

        config = AdvancedQRConfig(structured_append=True, symbol_count=16)  # Maximum
        assert config.symbol_count == 16

        # Cluster size boundaries
        config = Phase2Config(min_cluster_size=1)  # Minimum
        assert config.min_cluster_size == 1

    def test_out_of_bounds_validation(self):
        """Test validation for out-of-bounds values."""
        # Scale out of bounds
        with pytest.raises(ValidationError):
            RenderingConfig(scale=0)

        with pytest.raises(ValidationError):
            RenderingConfig(scale=101)

        # Corner radius out of bounds
        with pytest.raises(ValidationError):
            GeometryConfig(corner_radius=-0.1)

        with pytest.raises(ValidationError):
            GeometryConfig(corner_radius=1.1)

        # Centerpiece size out of bounds
        with pytest.raises(ValidationError):
            CenterpieceConfig(size=-0.1)

        with pytest.raises(ValidationError):
            CenterpieceConfig(size=0.6)

    def test_extreme_list_and_dict_sizes(self):
        """Test extremely large lists and dictionaries."""
        # Very large flow weights dictionary
        large_flow_weights = {f"type_{i}": float(i % 10) / 10.0 for i in range(1000)}
        config = Phase1Config(flow_weights=large_flow_weights)
        assert len(config.flow_weights) == 1000

        # Very large module type list
        large_module_types = [f"module_type_{i}" for i in range(500)]
        config = Phase2Config(cluster_module_types=large_module_types)
        assert len(config.cluster_module_types) == 500

        # Very large debug colors dictionary
        large_debug_colors = {f"component_{i}": f"#{'%06x' % i}" for i in range(100)}
        config = DebugConfig(debug_colors=large_debug_colors)
        assert len(config.debug_colors) == 100

    def test_memory_limit_extreme_values(self):
        """Test extreme memory limit values."""
        # Very large memory limits
        config = PerformanceConfig(memory_limit_mb=1048576)  # 1 TB
        assert config.memory_limit_mb == 1048576

        # Minimum memory limit
        config = PerformanceConfig(memory_limit_mb=1)
        assert config.memory_limit_mb == 1


class TestComplexValidationScenarios:
    """Test complex validation scenarios involving multiple constraints."""

    def test_comprehensive_rendering_configuration(self):
        """Test comprehensive rendering configuration with all components."""
        config = RenderingConfig(
            scale=25,
            border=6,
            dark="#2c3e50",
            light="#ecf0f1",
            geometry=GeometryConfig(
                shape="connected-classy-rounded",
                corner_radius=0.4,
                connectivity="8-way",
                merge="aggressive",
                min_island_modules=3,
            ),
            finder=FinderConfig(shape="circle", inner_scale=0.6, stroke=2.0),
            patterns=PatternStyleConfig(
                enabled=True,
                finder="circle",
                finder_color="#e74c3c",
                timing="dot",
                timing_color="#3498db",
                data="connected-classy-rounded",
                data_color="#2ecc71",
                finder_scale=1.2,
                timing_scale=0.8,
            ),
            frame=FrameConfig(
                shape="squircle",
                corner_radius=0.3,
                clip_mode="fade",
                fade_distance=20.0,
            ),
            centerpiece=CenterpieceConfig(
                enabled=True,
                shape="squircle",
                size=0.25,
                mode="imprint",
                placement="center",
                margin=3,
            ),
            quiet_zone=QuietZoneConfig(
                color="#f8f9fa",
                style="gradient",
                gradient={
                    "type": "radial",
                    "stops": [
                        {"offset": "0%", "color": "#ffffff"},
                        {"offset": "100%", "color": "#f8f9fa"},
                    ],
                },
            ),
            style=StyleConfig(
                interactive=True,
                tooltips=True,
                css_classes={
                    "qr_module": "qr-module animated",
                    "qr_finder": "qr-finder primary",
                    "qr_timing": "qr-timing secondary",
                    "qr_data": "qr-data accent",
                },
            ),
            phase1=Phase1Config(enabled=True, use_enhanced_shapes=True, roundness=0.5, size_ratio=0.9),
            phase2=Phase2Config(
                enabled=True,
                use_cluster_rendering=True,
                cluster_module_types=["data", "timing"],
                min_cluster_size=4,
                density_threshold=0.7,
            ),
            phase3=Phase3Config(
                enabled=True,
                use_marching_squares=True,
                contour_module_types=["data"],
                contour_mode="bezier",
                bezier_optimization="high",
                tension=0.4,
                point_reduction=0.8,
            ),
            advanced_qr=AdvancedQRConfig(
                eci_enabled=True,
                encoding="UTF-8",
                structured_append=True,
                symbol_count=4,
                boost_error=True,
            ),
        )

        # Verify all major components are configured correctly
        assert config.scale == 25
        assert config.geometry.shape == ModuleShape.CONNECTED_CLASSY_ROUNDED
        assert config.patterns.enabled is True
        assert config.frame.shape == "squircle"
        assert config.centerpiece.enabled is True
        assert config.quiet_zone.style == "gradient"
        assert config.style.interactive is True
        assert config.phase1.enabled is True
        assert config.phase2.enabled is True
        assert config.phase3.enabled is True
        assert config.advanced_qr.eci_enabled is True

    def test_minimal_valid_configuration(self):
        """Test minimal valid configuration with all defaults."""
        config = RenderingConfig()

        # Should have all default values
        assert config.scale == 1
        assert config.border == 4
        assert config.dark == "#000000"
        assert config.light == "#ffffff"
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

    def test_conflicting_configuration_resolution(self):
        """Test resolution of potentially conflicting configurations."""
        # Test mask pattern vs auto_mask conflict resolution
        config = AdvancedQRConfig(mask_pattern=5, auto_mask=True)
        assert config.mask_pattern == 5
        assert config.auto_mask is False  # Should be resolved to False

        # Test structured append vs symbol count conflict
        config = AdvancedQRConfig(structured_append=True)
        assert config.structured_append is True
        assert config.symbol_count == 2  # Should default to 2

        # Test ECI enabled vs encoding conflict
        config = AdvancedQRConfig(eci_enabled=True)
        assert config.eci_enabled is True
        assert config.encoding == "UTF-8"  # Should default to UTF-8

    def test_invalid_nested_configuration_combinations(self):
        """Test invalid nested configuration combinations."""
        # Invalid frame with custom shape but no path
        with pytest.raises(ValidationError):
            RenderingConfig(frame=FrameConfig(shape="custom"))  # Missing custom_path

        # Invalid centerpiece enabled with zero size
        with pytest.raises(ValidationError):
            RenderingConfig(centerpiece=CenterpieceConfig(enabled=True, size=0.0))

        # Invalid quiet zone gradient style without gradient
        with pytest.raises(ValidationError):
            RenderingConfig(quiet_zone=QuietZoneConfig(style="gradient"))  # Missing gradient

        # Invalid patterns enabled without overrides
        with pytest.raises(ValidationError):
            RenderingConfig(patterns=PatternStyleConfig(enabled=True))  # No overrides


class TestTypeCoercionEdgeCases:
    """Test type coercion edge cases and limitations."""

    def test_numeric_string_coercion(self):
        """Test numeric string coercion boundaries."""
        # Valid string to int coercion
        config = PerformanceConfig(max_cache_size="1000")
        assert config.max_cache_size == 1000
        assert isinstance(config.max_cache_size, int)

        # Valid string to float coercion
        config = GeometryConfig(corner_radius="0.5")
        assert config.corner_radius == 0.5
        assert isinstance(config.corner_radius, float)

        # Invalid string to numeric coercion
        with pytest.raises(ValidationError):
            PerformanceConfig(max_cache_size="not-a-number")

    def test_boolean_coercion_edge_cases(self):
        """Test boolean coercion edge cases."""
        # Integer to boolean coercion
        config = DebugConfig(debug_mode=1)
        assert config.debug_mode is True

        config = DebugConfig(debug_mode=0)
        assert config.debug_mode is False

        # String to boolean coercion works in Pydantic
        config = DebugConfig(debug_mode="true")
        assert config.debug_mode is True

        config = DebugConfig(debug_mode="false")
        assert config.debug_mode is False

    def test_list_and_dict_coercion(self):
        """Test list and dictionary coercion scenarios."""
        # Single value to list coercion (depends on field definition)
        # Most fields expect explicit lists, so this may not work

        # Empty collections
        config = Phase2Config(cluster_module_types=[])
        assert config.cluster_module_types == []

        config = DebugConfig(debug_colors={})
        assert config.debug_colors == {}

    def test_none_value_coercion(self):
        """Test None value handling and coercion."""
        # None values for optional fields
        config = AdvancedQRConfig(encoding=None, mask_pattern=None, symbol_count=None)
        assert config.encoding is None
        assert config.mask_pattern is None
        assert config.symbol_count is None

        # None values for fields with defaults
        config = PerformanceConfig(memory_limit_mb=None)
        assert config.memory_limit_mb is None


class TestValidationErrorQuality:
    """Test the quality and usefulness of validation error messages."""

    def test_single_field_validation_errors(self):
        """Test single field validation error message quality."""
        # Scale validation error
        with pytest.raises(ValidationError) as exc_info:
            RenderingConfig(scale=150)

        error_message = str(exc_info.value)
        assert "scale" in error_message.lower()
        assert "100" in error_message  # Maximum value

        # Corner radius validation error
        with pytest.raises(ValidationError) as exc_info:
            GeometryConfig(corner_radius=2.0)

        error_message = str(exc_info.value)
        assert "corner_radius" in error_message.lower()
        assert "1" in error_message  # Maximum value

    def test_multiple_field_validation_errors(self):
        """Test multiple field validation error aggregation."""
        with pytest.raises(ValidationError) as exc_info:
            RenderingConfig(scale=150, border=-1)  # Invalid  # Invalid

        error_message = str(exc_info.value)
        # Should contain information about invalid fields
        assert "scale" in error_message.lower()
        assert "border" in error_message.lower()

        # Test nested validation error separately
        with pytest.raises(ValidationError) as exc_info:
            GeometryConfig(corner_radius=2.0)  # Invalid nested

        error_message = str(exc_info.value)
        assert "corner_radius" in error_message.lower()

    def test_nested_validation_error_context(self):
        """Test nested validation error context information."""
        with pytest.raises(ValidationError) as exc_info:
            RenderingConfig(frame=FrameConfig(shape="custom"))  # Missing custom_path

        error_message = str(exc_info.value)
        assert "frame" in error_message.lower()
        assert "custom_path" in error_message.lower()

    def test_cross_field_validation_error_context(self):
        """Test cross-field validation error context."""
        with pytest.raises(ValidationError) as exc_info:
            PatternStyleConfig(enabled=True)  # No overrides provided

        error_message = str(exc_info.value)
        assert "pattern override" in error_message.lower()
        assert "enabled" in error_message.lower()

    def test_enum_validation_error_suggestions(self):
        """Test enum validation error message suggestions."""
        with pytest.raises(ValidationError) as exc_info:
            GeometryConfig(shape="invalid_shape")

        error_message = str(exc_info.value)
        # Should suggest valid enum values
        assert "square" in error_message.lower() or "circle" in error_message.lower()


class TestConfigurationStateConsistency:
    """Test configuration state consistency across operations."""

    def test_configuration_immutability_after_creation(self):
        """Test that configurations maintain consistent state after creation."""
        config = RenderingConfig(scale=20, geometry=GeometryConfig(shape="circle", corner_radius=0.3))

        # Configuration should maintain its state
        assert config.scale == 20
        assert config.geometry.shape == ModuleShape.CIRCLE
        assert config.geometry.corner_radius == 0.3

        # Accessing fields shouldn't change state
        _ = config.dark
        _ = config.geometry.merge
        assert config.scale == 20  # Should remain unchanged

    def test_nested_configuration_independence(self):
        """Test that nested configurations are independent."""
        config1 = RenderingConfig(geometry=GeometryConfig(corner_radius=0.3))
        config2 = RenderingConfig(geometry=GeometryConfig(corner_radius=0.7))

        # Should have independent geometry configurations
        assert config1.geometry.corner_radius == 0.3
        assert config2.geometry.corner_radius == 0.7

        # Modifying one shouldn't affect the other
        # (Note: These are immutable, but we're testing the concept)
        assert config1.geometry.corner_radius != config2.geometry.corner_radius

    def test_configuration_serialization_consistency(self):
        """Test configuration consistency through serialization."""
        original_config = RenderingConfig(
            scale=15,
            dark="#e74c3c",
            geometry=GeometryConfig(shape="squircle", corner_radius=0.4),
            style=StyleConfig(interactive=True),
        )

        # Serialize and deserialize
        json_str = original_config.to_json()
        restored_config = RenderingConfig.from_json(json_str)

        # Should maintain consistency
        assert restored_config.scale == original_config.scale
        assert restored_config.dark == original_config.dark
        assert restored_config.geometry.shape == original_config.geometry.shape
        assert restored_config.geometry.corner_radius == original_config.geometry.corner_radius
        assert restored_config.style.interactive == original_config.style.interactive

    def test_factory_method_consistency(self):
        """Test factory method consistency with direct construction."""
        # Create config using factory method
        factory_config = RenderingConfig.from_kwargs(
            scale=20, shape="circle", corner_radius=0.3, interactive=True
        )

        # Create equivalent config using direct construction
        direct_config = RenderingConfig(
            scale=20,
            geometry=GeometryConfig(shape="circle", corner_radius=0.3),
            style=StyleConfig(interactive=True),
        )

        # Should have equivalent key properties
        assert factory_config.scale == direct_config.scale
        assert factory_config.geometry.shape == direct_config.geometry.shape
        assert factory_config.geometry.corner_radius == direct_config.geometry.corner_radius
        assert factory_config.style.interactive == direct_config.style.interactive
