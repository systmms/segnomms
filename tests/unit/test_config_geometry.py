"""
Comprehensive unit tests for geometry configuration models.

Tests GeometryConfig and FinderConfig validation, shape handling,
parameter constraints, and shape-specific logic.
"""

import pytest
from pydantic import ValidationError

from segnomms.config.enums import (
    ConnectivityMode,
    FinderShape,
    MergeStrategy,
    ModuleShape,
)
from segnomms.config.models.geometry import FinderConfig, GeometryConfig


class TestGeometryConfig:
    """Test GeometryConfig validation and functionality."""

    def test_default_geometry_config(self):
        """Test default geometry configuration values."""
        config = GeometryConfig()

        assert (
            config.shape == ModuleShape.SQUARE
        )  # use_enum_values=True converts to string
        assert config.corner_radius == 0.0
        assert config.connectivity == "4-way"  # use_enum_values=True converts to string
        assert config.merge == "none"  # use_enum_values=True converts to string
        assert config.min_island_modules == 1

    def test_all_module_shapes_validation(self):
        """Test validation of all ModuleShape enum values."""
        valid_shapes = [
            "square",
            "circle",
            "rounded",
            "dot",
            "diamond",
            "star",
            "hexagon",
            "triangle",
            "squircle",
            "cross",
            "connected",
            "connected-extra-rounded",
            "connected-classy",
            "connected-classy-rounded",
        ]

        for shape in valid_shapes:
            config = GeometryConfig(shape=shape)
            assert config.shape == shape

    def test_shape_string_conversion(self):
        """Test shape string input conversion to enum objects."""
        # Test string inputs are converted to enum objects (no more use_enum_values=True)
        config = GeometryConfig(shape="circle")
        assert config.shape == ModuleShape.CIRCLE

        config = GeometryConfig(shape="squircle")
        assert config.shape == ModuleShape.SQUIRCLE

        config = GeometryConfig(shape="connected-extra-rounded")
        assert config.shape == ModuleShape.CONNECTED_EXTRA_ROUNDED

    def test_invalid_shape_validation(self):
        """Test invalid shape rejection."""
        invalid_shapes = ["invalid_shape", "pentagon", "octagon", "", None, 123]

        for invalid_shape in invalid_shapes:
            with pytest.raises(ValidationError) as exc_info:
                GeometryConfig(shape=invalid_shape)
            assert "shape" in str(exc_info.value).lower()

    def test_corner_radius_validation(self):
        """Test corner radius parameter validation."""
        # Valid corner radius values
        valid_radii = [0.0, 0.1, 0.5, 1.0]

        for radius in valid_radii:
            config = GeometryConfig(corner_radius=radius)
            assert config.corner_radius == radius

        # Invalid corner radius values
        invalid_radii = [-0.1, 1.1, 2.0, -1.0]

        for radius in invalid_radii:
            with pytest.raises(ValidationError) as exc_info:
                GeometryConfig(corner_radius=radius)
            assert "corner_radius" in str(exc_info.value).lower()

    def test_connectivity_mode_validation(self):
        """Test connectivity mode validation."""
        # Valid connectivity modes
        config = GeometryConfig(connectivity="4-way")
        assert config.connectivity == ConnectivityMode.FOUR_WAY

        config = GeometryConfig(connectivity="8-way")
        assert config.connectivity == ConnectivityMode.EIGHT_WAY

    def test_merge_strategy_validation(self):
        """Test merge strategy validation."""
        # Valid merge strategies
        config = GeometryConfig(merge="none")
        assert config.merge == MergeStrategy.NONE

        config = GeometryConfig(merge="soft")
        assert config.merge == MergeStrategy.SOFT

        config = GeometryConfig(merge="aggressive")
        assert config.merge == MergeStrategy.AGGRESSIVE

    def test_min_island_modules_validation(self):
        """Test minimum island modules validation."""
        # Valid values (constraint is ge=1, le=10)
        valid_values = [1, 2, 5, 10]

        for value in valid_values:
            config = GeometryConfig(min_island_modules=value)
            assert config.min_island_modules == value

        # Invalid values
        invalid_values = [0, -1, -5, 11, 100]

        for value in invalid_values:
            with pytest.raises(ValidationError) as exc_info:
                GeometryConfig(min_island_modules=value)
            assert "min_island_modules" in str(exc_info.value).lower()

    def test_complex_geometry_configuration(self):
        """Test complex geometry configuration combinations."""
        config = GeometryConfig(
            shape="connected-classy-rounded",
            corner_radius=0.35,
            connectivity="8-way",
            merge="aggressive",
            min_island_modules=3,
        )

        assert config.shape == "connected-classy-rounded"
        assert config.corner_radius == 0.35
        assert config.connectivity == ConnectivityMode.EIGHT_WAY
        assert config.merge == MergeStrategy.AGGRESSIVE
        assert config.min_island_modules == 3

    def test_shape_specific_parameter_logic(self):
        """Test logic specific to different shape types."""
        # Test that connected shapes work with merge strategies
        connected_shapes = [
            "connected",
            "connected-extra-rounded",
            "connected-classy",
            "connected-classy-rounded",
        ]

        for shape in connected_shapes:
            config = GeometryConfig(shape=shape, merge="soft", connectivity="8-way")

            assert config.shape == shape
            assert config.merge == MergeStrategy.SOFT
            assert config.connectivity == ConnectivityMode.EIGHT_WAY

    def test_corner_radius_shape_interactions(self):
        """Test corner radius with different shapes."""
        # Corner radius should work with shapes that support it
        shapes_with_corners = [
            "square",
            "rounded",
            "connected",
            "connected-extra-rounded",
        ]

        for shape in shapes_with_corners:
            config = GeometryConfig(shape=shape, corner_radius=0.3)

            assert config.shape == shape
            assert config.corner_radius == 0.3

    def test_connectivity_merge_combinations(self):
        """Test different connectivity and merge combinations."""
        combinations = [
            ("4-way", "none"),
            ("4-way", "soft"),
            ("8-way", "soft"),
            ("8-way", "aggressive"),
        ]

        for connectivity, merge in combinations:
            config = GeometryConfig(connectivity=connectivity, merge=merge)

            assert config.connectivity == connectivity
            assert config.merge == merge

    def test_extra_fields_forbidden(self):
        """Test that extra fields are forbidden in GeometryConfig."""
        with pytest.raises(ValidationError) as exc_info:
            GeometryConfig(invalid_field="value")
        assert "Extra inputs are not permitted" in str(exc_info.value)


class TestFinderConfig:
    """Test FinderConfig validation and functionality."""

    def test_default_finder_config(self):
        """Test default finder configuration values."""
        config = FinderConfig()

        assert config.shape == ModuleShape.SQUARE  # use_enum_values=True
        assert config.inner_scale == 0.6  # Default is 0.6, not 0.5
        assert config.stroke == 0.0  # Default is 0.0, not None

    def test_finder_shape_validation(self):
        """Test finder shape validation."""
        # Valid finder shapes
        valid_shapes = [
            "square",
            "rounded",
            "circle",
        ]

        for shape in valid_shapes:
            config = FinderConfig(shape=shape)
            assert config.shape == shape

    def test_finder_shape_string_conversion(self):
        """Test finder shape string conversion."""
        config = FinderConfig(shape="square")
        assert config.shape == ModuleShape.SQUARE

        config = FinderConfig(shape="rounded")
        assert config.shape == ModuleShape.ROUNDED

        config = FinderConfig(shape="circle")
        assert config.shape == ModuleShape.CIRCLE

    def test_invalid_finder_shape(self):
        """Test invalid finder shape rejection."""
        invalid_shapes = ["triangle", "hexagon", "invalid", "", None, 123]

        for invalid_shape in invalid_shapes:
            with pytest.raises(ValidationError) as exc_info:
                FinderConfig(shape=invalid_shape)
            assert "shape" in str(exc_info.value).lower()

    def test_inner_scale_validation(self):
        """Test inner scale parameter validation."""
        # Valid inner scale values (based on actual constraints: ge=0.1, le=1.0)
        valid_scales = [0.1, 0.3, 0.5, 0.7, 1.0]

        for scale in valid_scales:
            config = FinderConfig(inner_scale=scale)
            assert config.inner_scale == scale

        # Invalid inner scale values
        invalid_scales = [0.0, 1.1, -0.1, 2.0]

        for scale in invalid_scales:
            with pytest.raises(ValidationError) as exc_info:
                FinderConfig(inner_scale=scale)
            assert "inner_scale" in str(exc_info.value).lower()

    def test_stroke_parameter(self):
        """Test stroke parameter handling."""
        # Test numeric values
        config = FinderConfig(stroke=1.0)
        assert config.stroke == 1.0

        config = FinderConfig(stroke=2.5)
        assert config.stroke == 2.5

        # Test default value
        config = FinderConfig()
        assert config.stroke == 0.0

        # Test boundary values
        config = FinderConfig(stroke=0.0)
        assert config.stroke == 0.0

        config = FinderConfig(stroke=5.0)
        assert config.stroke == 5.0

    def test_complete_finder_configuration(self):
        """Test complete finder configuration."""
        config = FinderConfig(shape="circle", inner_scale=0.6, stroke=2.0)

        assert config.shape == ModuleShape.CIRCLE
        assert config.inner_scale == 0.6
        assert config.stroke == 2.0

    def test_finder_shape_inner_scale_combinations(self):
        """Test different shape and inner scale combinations."""
        combinations = [
            ("square", 0.3),
            ("rounded", 0.4),
            ("circle", 0.6),
        ]

        for shape, scale in combinations:
            config = FinderConfig(shape=shape, inner_scale=scale)

            assert config.shape == shape
            assert config.inner_scale == scale

    def test_finder_config_with_stroke_variations(self):
        """Test finder configuration with different stroke options."""
        stroke_options = [0.0, 1.0, 2.5, 5.0]

        for stroke in stroke_options:
            config = FinderConfig(shape="rounded", inner_scale=0.5, stroke=stroke)

            assert config.shape == ModuleShape.ROUNDED
            assert config.inner_scale == 0.5
            assert config.stroke == stroke

    def test_extra_fields_forbidden_finder(self):
        """Test that extra fields are forbidden in FinderConfig."""
        with pytest.raises(ValidationError) as exc_info:
            FinderConfig(invalid_field="value")
        assert "Extra inputs are not permitted" in str(exc_info.value)


class TestGeometryFinderIntegration:
    """Test integration between GeometryConfig and FinderConfig."""

    def test_geometry_finder_shape_independence(self):
        """Test that geometry and finder shapes are independent."""
        # Geometry can be circle while finder is square
        geometry_config = GeometryConfig(shape="circle")
        finder_config = FinderConfig(shape="square")

        assert geometry_config.shape == ModuleShape.CIRCLE
        assert finder_config.shape == FinderShape.SQUARE

        # And vice versa
        geometry_config = GeometryConfig(shape="square")
        finder_config = FinderConfig(shape="circle")

        assert geometry_config.shape == ModuleShape.SQUARE
        assert finder_config.shape == FinderShape.CIRCLE

    def test_coordinated_geometric_styling(self):
        """Test coordinated geometric styling between geometry and finder."""
        # Test consistent rounded styling
        geometry_config = GeometryConfig(shape="rounded", corner_radius=0.3)
        finder_config = FinderConfig(shape="rounded", inner_scale=0.5)

        assert geometry_config.shape == ModuleShape.ROUNDED
        assert geometry_config.corner_radius == 0.3
        assert finder_config.shape == FinderShape.ROUNDED
        assert finder_config.inner_scale == 0.5

    def test_contrasting_geometric_styles(self):
        """Test contrasting styles between geometry and finder patterns."""
        # Sharp data modules with soft finder patterns
        geometry_config = GeometryConfig(shape="square", corner_radius=0.0)
        finder_config = FinderConfig(shape="circle", inner_scale=0.7)

        assert geometry_config.shape == ModuleShape.SQUARE
        assert geometry_config.corner_radius == 0.0
        assert finder_config.shape == FinderShape.CIRCLE
        assert finder_config.inner_scale == 0.7

    def test_complex_geometry_configurations(self):
        """Test complex multi-parameter geometry configurations."""
        # High-complexity configuration
        geometry_config = GeometryConfig(
            shape="connected-classy-rounded",
            corner_radius=0.4,
            connectivity="8-way",
            merge="aggressive",
            min_island_modules=2,
        )

        finder_config = FinderConfig(shape="circle", inner_scale=0.6, stroke=2.0)

        # Verify all parameters
        assert geometry_config.shape == ModuleShape.CONNECTED_CLASSY_ROUNDED
        assert geometry_config.corner_radius == 0.4
        assert geometry_config.connectivity == ConnectivityMode.EIGHT_WAY
        assert geometry_config.merge == MergeStrategy.AGGRESSIVE
        assert geometry_config.min_island_modules == 2

        assert finder_config.shape == FinderShape.CIRCLE
        assert finder_config.inner_scale == 0.6
        assert finder_config.stroke == 2.0


class TestGeometryConfigEdgeCases:
    """Test edge cases and boundary conditions for geometry configuration."""

    def test_boundary_corner_radius_values(self):
        """Test boundary values for corner radius."""
        # Exact boundary values
        config = GeometryConfig(corner_radius=0.0)
        assert config.corner_radius == 0.0

        config = GeometryConfig(corner_radius=1.0)
        assert config.corner_radius == 1.0

        # Just outside boundaries should fail
        with pytest.raises(ValidationError):
            GeometryConfig(corner_radius=-0.001)

        with pytest.raises(ValidationError):
            GeometryConfig(corner_radius=1.001)

    def test_boundary_inner_scale_values(self):
        """Test boundary values for finder inner scale."""
        # Exact boundary values (based on actual constraints: ge=0.1, le=1.0)
        config = FinderConfig(inner_scale=0.1)
        assert config.inner_scale == 0.1

        config = FinderConfig(inner_scale=1.0)
        assert config.inner_scale == 1.0

        # Values outside boundaries should fail
        with pytest.raises(ValidationError):
            FinderConfig(inner_scale=0.099)

        with pytest.raises(ValidationError):
            FinderConfig(inner_scale=1.001)

    def test_minimum_island_modules_edge_cases(self):
        """Test edge cases for minimum island modules."""
        # Minimum valid value
        config = GeometryConfig(min_island_modules=1)
        assert config.min_island_modules == 1

        # Maximum valid value (based on actual constraint: le=10)
        config = GeometryConfig(min_island_modules=10)
        assert config.min_island_modules == 10

        # Invalid values
        with pytest.raises(ValidationError):
            GeometryConfig(min_island_modules=0)

        with pytest.raises(ValidationError):
            GeometryConfig(min_island_modules=11)

    def test_shape_enum_case_sensitivity(self):
        """Test shape enum case sensitivity and variations."""
        # Test exact case
        config = GeometryConfig(shape="square")
        assert config.shape == ModuleShape.SQUARE  # use_enum_values=True

        # Test that invalid cases fail
        with pytest.raises(ValidationError):
            GeometryConfig(shape="SQUARE")

        with pytest.raises(ValidationError):
            GeometryConfig(shape="Square")

    def test_hyphenated_shape_names(self):
        """Test hyphenated shape names."""
        hyphenated_shapes = [
            "connected-extra-rounded",
            "connected-classy",
            "connected-classy-rounded",
        ]

        for shape_str in hyphenated_shapes:
            config = GeometryConfig(shape=shape_str)
            assert config.shape == shape_str  # use_enum_values=True converts to string

    def test_merge_connectivity_logical_combinations(self):
        """Test logical combinations of merge and connectivity."""
        # Aggressive merge typically works better with 8-way connectivity
        config = GeometryConfig(merge="aggressive", connectivity="8-way")
        assert config.merge == MergeStrategy.AGGRESSIVE
        assert config.connectivity == ConnectivityMode.EIGHT_WAY

        # But 4-way should also work
        config = GeometryConfig(merge="aggressive", connectivity="4-way")
        assert config.merge == MergeStrategy.AGGRESSIVE
        assert config.connectivity == "4-way"

    def test_type_coercion_edge_cases(self):
        """Test type coercion edge cases."""
        # Float to int coercion for min_island_modules
        config = GeometryConfig(min_island_modules=5.0)
        assert config.min_island_modules == 5
        assert isinstance(config.min_island_modules, int)

        # String to float coercion for corner_radius
        config = GeometryConfig(corner_radius="0.5")
        assert config.corner_radius == 0.5
        assert isinstance(config.corner_radius, float)

    def test_none_value_handling(self):
        """Test handling of None values where not allowed."""
        # None should not be allowed for required fields
        with pytest.raises(ValidationError):
            GeometryConfig(shape=None)

        with pytest.raises(ValidationError):
            GeometryConfig(corner_radius=None)

        # stroke in FinderConfig requires float, not None
        with pytest.raises(ValidationError):
            FinderConfig(stroke=None)


class TestConfigurationValidationMessages:
    """Test quality of validation error messages."""

    def test_shape_validation_error_message(self):
        """Test shape validation error message quality."""
        with pytest.raises(ValidationError) as exc_info:
            GeometryConfig(shape="invalid_shape")

        error_message = str(exc_info.value)
        assert "shape" in error_message.lower()
        # Should mention valid options
        assert "square" in error_message.lower() or "circle" in error_message.lower()

    def test_corner_radius_validation_error_message(self):
        """Test corner radius validation error message quality."""
        with pytest.raises(ValidationError) as exc_info:
            GeometryConfig(corner_radius=2.0)

        error_message = str(exc_info.value)
        assert "corner_radius" in error_message.lower()
        assert "1" in error_message  # Maximum value mentioned

    def test_inner_scale_validation_error_message(self):
        """Test inner scale validation error message quality."""
        with pytest.raises(ValidationError) as exc_info:
            FinderConfig(inner_scale=1.5)

        error_message = str(exc_info.value)
        assert "inner_scale" in error_message.lower()
        # Should mention the valid range
        assert "0.9" in error_message or "less than" in error_message.lower()

    def test_multiple_validation_errors(self):
        """Test handling of multiple validation errors."""
        with pytest.raises(ValidationError) as exc_info:
            GeometryConfig(shape="invalid", corner_radius=2.0, min_island_modules=-1)

        error_message = str(exc_info.value)
        # Should contain information about multiple fields
        assert "shape" in error_message.lower()
        assert "corner_radius" in error_message.lower()
        assert "min_island_modules" in error_message.lower()
