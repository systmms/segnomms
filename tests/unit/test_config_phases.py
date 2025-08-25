"""
Comprehensive unit tests for processing phase configuration models.

Tests Phase1Config, Phase2Config, and Phase3Config validation, parameters,
constraints, and complex processing pipeline scenarios.
"""

import pytest
from pydantic import ValidationError

from segnomms.config.models.phases import Phase1Config, Phase2Config, Phase3Config
from segnomms.config.enums import ContourMode, OptimizationLevel


class TestPhase1Config:
    """Test Phase1Config validation and functionality."""

    def test_default_phase1_config(self):
        """Test default phase1 configuration."""
        config = Phase1Config()
        
        assert config.enabled is False
        assert config.use_enhanced_shapes is False
        assert config.roundness == 0.3
        assert config.size_ratio == 0.9
        
        # Check default flow weights
        expected_flow_weights = {
            "finder": 0.5,
            "finder_inner": 0.3,
            "timing": 0.8,
            "data": 1.0,
            "alignment": 0.6,
            "format": 0.7,
        }
        assert config.flow_weights == expected_flow_weights

    def test_phase1_enabled_configuration(self):
        """Test enabled phase1 configuration."""
        config = Phase1Config(
            enabled=True,
            use_enhanced_shapes=True,
            roundness=0.5,
            size_ratio=0.8
        )
        
        assert config.enabled is True
        assert config.use_enhanced_shapes is True
        assert config.roundness == 0.5
        assert config.size_ratio == 0.8

    def test_roundness_validation(self):
        """Test roundness parameter validation."""
        # Valid roundness values
        valid_roundness = [0.0, 0.2, 0.5, 0.8, 1.0]
        
        for roundness in valid_roundness:
            config = Phase1Config(roundness=roundness)
            assert config.roundness == roundness
        
        # Invalid roundness values
        invalid_roundness = [-0.1, 1.1, 2.0, -1.0]
        
        for roundness in invalid_roundness:
            with pytest.raises(ValidationError) as exc_info:
                Phase1Config(roundness=roundness)
            assert "roundness" in str(exc_info.value).lower()

    def test_size_ratio_validation(self):
        """Test size_ratio parameter validation."""
        # Valid size_ratio values
        valid_ratios = [0.1, 0.3, 0.5, 0.9, 1.0]
        
        for ratio in valid_ratios:
            config = Phase1Config(size_ratio=ratio)
            assert config.size_ratio == ratio
        
        # Invalid size_ratio values
        invalid_ratios = [0.05, 1.1, 2.0, -0.1, 0.0]
        
        for ratio in invalid_ratios:
            with pytest.raises(ValidationError) as exc_info:
                Phase1Config(size_ratio=ratio)
            assert "size_ratio" in str(exc_info.value).lower()

    def test_flow_weights_customization(self):
        """Test custom flow weights configuration."""
        custom_weights = {
            "finder": 0.8,
            "finder_inner": 0.6,
            "timing": 0.9,
            "data": 1.0,
            "alignment": 0.7,
            "format": 0.8,
        }
        
        config = Phase1Config(flow_weights=custom_weights)
        assert config.flow_weights == custom_weights

    def test_flow_weights_partial_override(self):
        """Test partial flow weights override."""
        partial_weights = {
            "finder": 0.9,
            "data": 0.8,
        }
        
        config = Phase1Config(flow_weights=partial_weights)
        assert config.flow_weights == partial_weights

    def test_flow_weights_additional_types(self):
        """Test flow weights with additional module types."""
        extended_weights = {
            "finder": 0.5,
            "finder_inner": 0.3,
            "timing": 0.8,
            "data": 1.0,
            "alignment": 0.6,
            "format": 0.7,
            "custom_type": 0.9,
            "special_pattern": 0.4,
        }
        
        config = Phase1Config(flow_weights=extended_weights)
        assert config.flow_weights == extended_weights

    def test_flow_weights_validation_ranges(self):
        """Test flow weight value ranges."""
        # Flow weights should accept 0.0 to 1.0+ values
        valid_weights = {
            "data": 0.0,
            "finder": 1.0,
            "timing": 1.5,  # Values > 1.0 should be allowed for emphasis
        }
        
        config = Phase1Config(flow_weights=valid_weights)
        assert config.flow_weights == valid_weights

    def test_complex_phase1_configuration(self):
        """Test complex phase1 configuration."""
        config = Phase1Config(
            enabled=True,
            use_enhanced_shapes=True,
            roundness=0.7,
            size_ratio=0.85,
            flow_weights={
                "finder": 0.9,
                "finder_inner": 0.7,
                "timing": 1.0,
                "data": 1.2,
                "alignment": 0.8,
                "format": 0.9,
                "custom": 0.6,
            }
        )
        
        assert config.enabled is True
        assert config.use_enhanced_shapes is True
        assert config.roundness == 0.7
        assert config.size_ratio == 0.85
        assert config.flow_weights["finder"] == 0.9
        assert config.flow_weights["data"] == 1.2
        assert config.flow_weights["custom"] == 0.6

    def test_phase1_boundary_values(self):
        """Test phase1 boundary values."""
        # Minimum boundary values
        config = Phase1Config(
            roundness=0.0,
            size_ratio=0.1
        )
        assert config.roundness == 0.0
        assert config.size_ratio == 0.1
        
        # Maximum boundary values
        config = Phase1Config(
            roundness=1.0,
            size_ratio=1.0
        )
        assert config.roundness == 1.0
        assert config.size_ratio == 1.0

    def test_extra_fields_forbidden_phase1(self):
        """Test that extra fields are forbidden in Phase1Config."""
        with pytest.raises(ValidationError) as exc_info:
            Phase1Config(invalid_field="value")
        assert "Extra inputs are not permitted" in str(exc_info.value)


class TestPhase2Config:
    """Test Phase2Config validation and functionality."""

    def test_default_phase2_config(self):
        """Test default phase2 configuration."""
        config = Phase2Config()
        
        assert config.enabled is False
        assert config.use_cluster_rendering is False
        assert config.cluster_module_types == ["data"]
        assert config.min_cluster_size == 3
        assert config.density_threshold == 0.5
        assert config.aspect_ratio_tolerance == 0.3

    def test_phase2_enabled_configuration(self):
        """Test enabled phase2 configuration."""
        config = Phase2Config(
            enabled=True,
            use_cluster_rendering=True,
            cluster_module_types=["data", "timing"],
            min_cluster_size=5,
            density_threshold=0.7,
            aspect_ratio_tolerance=0.4
        )
        
        assert config.enabled is True
        assert config.use_cluster_rendering is True
        assert config.cluster_module_types == ["data", "timing"]
        assert config.min_cluster_size == 5
        assert config.density_threshold == 0.7
        assert config.aspect_ratio_tolerance == 0.4

    def test_cluster_module_types_validation(self):
        """Test cluster module types configuration."""
        # Single module type
        config = Phase2Config(cluster_module_types=["data"])
        assert config.cluster_module_types == ["data"]
        
        # Multiple module types
        config = Phase2Config(cluster_module_types=["data", "timing", "alignment"])
        assert config.cluster_module_types == ["data", "timing", "alignment"]
        
        # All standard module types
        all_types = ["finder", "finder_inner", "timing", "data", "alignment", "format"]
        config = Phase2Config(cluster_module_types=all_types)
        assert config.cluster_module_types == all_types

    def test_min_cluster_size_validation(self):
        """Test min_cluster_size parameter validation."""
        # Valid cluster sizes
        valid_sizes = [1, 3, 5, 10, 50]
        
        for size in valid_sizes:
            config = Phase2Config(min_cluster_size=size)
            assert config.min_cluster_size == size
        
        # Invalid cluster sizes
        invalid_sizes = [0, -1, -5]
        
        for size in invalid_sizes:
            with pytest.raises(ValidationError) as exc_info:
                Phase2Config(min_cluster_size=size)
            assert "min_cluster_size" in str(exc_info.value).lower()

    def test_density_threshold_validation(self):
        """Test density_threshold parameter validation."""
        # Valid density thresholds
        valid_thresholds = [0.0, 0.3, 0.5, 0.8, 1.0]
        
        for threshold in valid_thresholds:
            config = Phase2Config(density_threshold=threshold)
            assert config.density_threshold == threshold
        
        # Invalid density thresholds
        invalid_thresholds = [-0.1, 1.1, 2.0, -1.0]
        
        for threshold in invalid_thresholds:
            with pytest.raises(ValidationError) as exc_info:
                Phase2Config(density_threshold=threshold)
            assert "density_threshold" in str(exc_info.value).lower()

    def test_aspect_ratio_tolerance_validation(self):
        """Test aspect_ratio_tolerance parameter validation."""
        # Valid aspect ratio tolerances
        valid_tolerances = [0.0, 0.1, 0.3, 0.7, 1.0]
        
        for tolerance in valid_tolerances:
            config = Phase2Config(aspect_ratio_tolerance=tolerance)
            assert config.aspect_ratio_tolerance == tolerance
        
        # Invalid aspect ratio tolerances
        invalid_tolerances = [-0.1, 1.1, 2.0, -1.0]
        
        for tolerance in invalid_tolerances:
            with pytest.raises(ValidationError) as exc_info:
                Phase2Config(aspect_ratio_tolerance=tolerance)
            assert "aspect_ratio_tolerance" in str(exc_info.value).lower()

    def test_comprehensive_clustering_configuration(self):
        """Test comprehensive clustering configuration."""
        config = Phase2Config(
            enabled=True,
            use_cluster_rendering=True,
            cluster_module_types=["data", "timing", "alignment"],
            min_cluster_size=4,
            density_threshold=0.6,
            aspect_ratio_tolerance=0.25
        )
        
        assert config.enabled is True
        assert config.use_cluster_rendering is True
        assert "data" in config.cluster_module_types
        assert "timing" in config.cluster_module_types
        assert "alignment" in config.cluster_module_types
        assert config.min_cluster_size == 4
        assert config.density_threshold == 0.6
        assert config.aspect_ratio_tolerance == 0.25

    def test_phase2_boundary_values(self):
        """Test phase2 boundary values."""
        # Minimum boundary values
        config = Phase2Config(
            min_cluster_size=1,
            density_threshold=0.0,
            aspect_ratio_tolerance=0.0
        )
        assert config.min_cluster_size == 1
        assert config.density_threshold == 0.0
        assert config.aspect_ratio_tolerance == 0.0
        
        # Maximum boundary values
        config = Phase2Config(
            density_threshold=1.0,
            aspect_ratio_tolerance=1.0
        )
        assert config.density_threshold == 1.0
        assert config.aspect_ratio_tolerance == 1.0

    def test_empty_cluster_module_types(self):
        """Test empty cluster module types list."""
        config = Phase2Config(cluster_module_types=[])
        assert config.cluster_module_types == []

    def test_extra_fields_forbidden_phase2(self):
        """Test that extra fields are forbidden in Phase2Config."""
        with pytest.raises(ValidationError) as exc_info:
            Phase2Config(invalid_field="value")
        assert "Extra inputs are not permitted" in str(exc_info.value)


class TestPhase3Config:
    """Test Phase3Config validation and functionality."""

    def test_default_phase3_config(self):
        """Test default phase3 configuration."""
        config = Phase3Config()
        
        assert config.enabled is False
        assert config.use_marching_squares is False
        assert config.contour_module_types == ["data"]
        assert config.contour_mode == "bezier"  # use_enum_values=True converts to string
        assert config.contour_smoothing == 0.3
        assert config.bezier_optimization == "medium"  # use_enum_values=True converts to string
        assert config.tension == 0.3
        assert config.point_reduction == 0.7

    def test_phase3_enabled_configuration(self):
        """Test enabled phase3 configuration."""
        config = Phase3Config(
            enabled=True,
            use_marching_squares=True,
            contour_module_types=["data", "timing"],
            contour_mode="combined",
            contour_smoothing=0.5,
            bezier_optimization="high",
            tension=0.4,
            point_reduction=0.8
        )
        
        assert config.enabled is True
        assert config.use_marching_squares is True
        assert config.contour_module_types == ["data", "timing"]
        assert config.contour_mode == "combined"
        assert config.contour_smoothing == 0.5
        assert config.bezier_optimization == "high"
        assert config.tension == 0.4
        assert config.point_reduction == 0.8

    def test_contour_mode_validation(self):
        """Test contour mode validation."""
        # Valid contour modes
        valid_modes = ["bezier", "combined", "overlay"]
        
        for mode in valid_modes:
            config = Phase3Config(contour_mode=mode)
            assert config.contour_mode == mode

    def test_bezier_optimization_validation(self):
        """Test bezier optimization level validation."""
        # Valid optimization levels
        valid_levels = ["low", "medium", "high"]
        
        for level in valid_levels:
            config = Phase3Config(bezier_optimization=level)
            assert config.bezier_optimization == level

    def test_contour_module_types_validation(self):
        """Test contour module types configuration."""
        # Single module type
        config = Phase3Config(contour_module_types=["data"])
        assert config.contour_module_types == ["data"]
        
        # Multiple module types
        config = Phase3Config(contour_module_types=["data", "timing", "alignment"])
        assert config.contour_module_types == ["data", "timing", "alignment"]
        
        # All standard module types
        all_types = ["finder", "finder_inner", "timing", "data", "alignment", "format"]
        config = Phase3Config(contour_module_types=all_types)
        assert config.contour_module_types == all_types

    def test_contour_smoothing_validation(self):
        """Test contour_smoothing parameter validation."""
        # Valid smoothing values
        valid_smoothing = [0.0, 0.2, 0.5, 0.8, 1.0]
        
        for smoothing in valid_smoothing:
            config = Phase3Config(contour_smoothing=smoothing)
            assert config.contour_smoothing == smoothing
        
        # Invalid smoothing values
        invalid_smoothing = [-0.1, 1.1, 2.0, -1.0]
        
        for smoothing in invalid_smoothing:
            with pytest.raises(ValidationError) as exc_info:
                Phase3Config(contour_smoothing=smoothing)
            assert "contour_smoothing" in str(exc_info.value).lower()

    def test_tension_validation(self):
        """Test tension parameter validation."""
        # Valid tension values
        valid_tensions = [0.0, 0.1, 0.3, 0.7, 1.0]
        
        for tension in valid_tensions:
            config = Phase3Config(tension=tension)
            assert config.tension == tension
        
        # Invalid tension values
        invalid_tensions = [-0.1, 1.1, 2.0, -1.0]
        
        for tension in invalid_tensions:
            with pytest.raises(ValidationError) as exc_info:
                Phase3Config(tension=tension)
            assert "tension" in str(exc_info.value).lower()

    def test_point_reduction_validation(self):
        """Test point_reduction parameter validation."""
        # Valid point reduction values
        valid_reductions = [0.0, 0.3, 0.5, 0.9, 1.0]
        
        for reduction in valid_reductions:
            config = Phase3Config(point_reduction=reduction)
            assert config.point_reduction == reduction
        
        # Invalid point reduction values
        invalid_reductions = [-0.1, 1.1, 2.0, -1.0]
        
        for reduction in invalid_reductions:
            with pytest.raises(ValidationError) as exc_info:
                Phase3Config(point_reduction=reduction)
            assert "point_reduction" in str(exc_info.value).lower()

    def test_comprehensive_marching_squares_configuration(self):
        """Test comprehensive marching squares configuration."""
        config = Phase3Config(
            enabled=True,
            use_marching_squares=True,
            contour_module_types=["data", "timing"],
            contour_mode="bezier",
            contour_smoothing=0.4,
            bezier_optimization="high",
            tension=0.5,
            point_reduction=0.8
        )
        
        assert config.enabled is True
        assert config.use_marching_squares is True
        assert "data" in config.contour_module_types
        assert "timing" in config.contour_module_types
        assert config.contour_mode == "bezier"
        assert config.contour_smoothing == 0.4
        assert config.bezier_optimization == "high"
        assert config.tension == 0.5
        assert config.point_reduction == 0.8

    def test_phase3_boundary_values(self):
        """Test phase3 boundary values."""
        # Minimum boundary values
        config = Phase3Config(
            contour_smoothing=0.0,
            tension=0.0,
            point_reduction=0.0
        )
        assert config.contour_smoothing == 0.0
        assert config.tension == 0.0
        assert config.point_reduction == 0.0
        
        # Maximum boundary values
        config = Phase3Config(
            contour_smoothing=1.0,
            tension=1.0,
            point_reduction=1.0
        )
        assert config.contour_smoothing == 1.0
        assert config.tension == 1.0
        assert config.point_reduction == 1.0

    def test_empty_contour_module_types(self):
        """Test empty contour module types list."""
        config = Phase3Config(contour_module_types=[])
        assert config.contour_module_types == []

    def test_extra_fields_forbidden_phase3(self):
        """Test that extra fields are forbidden in Phase3Config."""
        with pytest.raises(ValidationError) as exc_info:
            Phase3Config(invalid_field="value")
        assert "Extra inputs are not permitted" in str(exc_info.value)


class TestPhaseConfigIntegration:
    """Test integration between different phase configurations."""

    def test_coordinated_phase_configuration(self):
        """Test coordinated multi-phase configuration."""
        # Configure all phases for a comprehensive rendering pipeline
        phase1 = Phase1Config(
            enabled=True,
            use_enhanced_shapes=True,
            roundness=0.4,
            size_ratio=0.85
        )
        
        phase2 = Phase2Config(
            enabled=True,
            use_cluster_rendering=True,
            cluster_module_types=["data", "timing"],
            min_cluster_size=4,
            density_threshold=0.6
        )
        
        phase3 = Phase3Config(
            enabled=True,
            use_marching_squares=True,
            contour_module_types=["data"],
            contour_mode="bezier",
            bezier_optimization="high",
            tension=0.4
        )
        
        # Verify all phases are configured
        assert phase1.enabled is True
        assert phase2.enabled is True
        assert phase3.enabled is True
        
        # Verify coordinated settings
        assert phase1.use_enhanced_shapes is True
        assert phase2.use_cluster_rendering is True
        assert phase3.use_marching_squares is True

    def test_progressive_phase_enabling(self):
        """Test progressive phase enabling for different complexity levels."""
        # Basic enhancement (Phase 1 only)
        basic_phases = {
            "phase1": Phase1Config(enabled=True, roundness=0.3),
            "phase2": Phase2Config(enabled=False),
            "phase3": Phase3Config(enabled=False),
        }
        
        assert basic_phases["phase1"].enabled is True
        assert basic_phases["phase2"].enabled is False
        assert basic_phases["phase3"].enabled is False
        
        # Clustering enhancement (Phase 1 + 2)
        cluster_phases = {
            "phase1": Phase1Config(enabled=True, roundness=0.4),
            "phase2": Phase2Config(enabled=True, min_cluster_size=3),
            "phase3": Phase3Config(enabled=False),
        }
        
        assert cluster_phases["phase1"].enabled is True
        assert cluster_phases["phase2"].enabled is True
        assert cluster_phases["phase3"].enabled is False
        
        # Full enhancement (All phases)
        full_phases = {
            "phase1": Phase1Config(enabled=True, roundness=0.5),
            "phase2": Phase2Config(enabled=True, min_cluster_size=5),
            "phase3": Phase3Config(enabled=True, contour_mode="bezier"),
        }
        
        assert full_phases["phase1"].enabled is True
        assert full_phases["phase2"].enabled is True
        assert full_phases["phase3"].enabled is True

    def test_module_type_consistency_across_phases(self):
        """Test module type consistency across different phases."""
        # Configure phases to work on the same module types
        shared_module_types = ["data", "timing"]
        
        phase2 = Phase2Config(
            enabled=True,
            cluster_module_types=shared_module_types,
            min_cluster_size=3
        )
        
        phase3 = Phase3Config(
            enabled=True,
            contour_module_types=shared_module_types,
            contour_mode="bezier"
        )
        
        # Verify consistent module types
        assert phase2.cluster_module_types == shared_module_types
        assert phase3.contour_module_types == shared_module_types

    def test_optimization_level_progression(self):
        """Test optimization level progression across phases."""
        # Low optimization for speed
        low_opt_phase3 = Phase3Config(
            enabled=True,
            bezier_optimization="low",
            point_reduction=0.5
        )
        
        # Medium optimization for balance
        med_opt_phase3 = Phase3Config(
            enabled=True,
            bezier_optimization="medium",
            point_reduction=0.7
        )
        
        # High optimization for quality
        high_opt_phase3 = Phase3Config(
            enabled=True,
            bezier_optimization="high",
            point_reduction=0.9
        )
        
        assert low_opt_phase3.bezier_optimization == "low"
        assert med_opt_phase3.bezier_optimization == "medium"
        assert high_opt_phase3.bezier_optimization == "high"
        
        assert low_opt_phase3.point_reduction == 0.5
        assert med_opt_phase3.point_reduction == 0.7
        assert high_opt_phase3.point_reduction == 0.9

    def test_complex_pipeline_configuration(self):
        """Test complex multi-phase pipeline configuration."""
        # Configure a sophisticated rendering pipeline
        phase1 = Phase1Config(
            enabled=True,
            use_enhanced_shapes=True,
            roundness=0.6,
            size_ratio=0.9,
            flow_weights={
                "finder": 0.8,
                "timing": 1.0,
                "data": 1.2,
                "alignment": 0.7,
            }
        )
        
        phase2 = Phase2Config(
            enabled=True,
            use_cluster_rendering=True,
            cluster_module_types=["data", "timing", "alignment"],
            min_cluster_size=5,
            density_threshold=0.7,
            aspect_ratio_tolerance=0.2
        )
        
        phase3 = Phase3Config(
            enabled=True,
            use_marching_squares=True,
            contour_module_types=["data"],
            contour_mode="bezier",
            contour_smoothing=0.5,
            bezier_optimization="high",
            tension=0.4,
            point_reduction=0.8
        )
        
        # Verify complex configuration
        assert phase1.flow_weights["data"] == 1.2  # Emphasis on data modules
        assert phase2.min_cluster_size == 5  # Larger clusters
        assert phase3.bezier_optimization == OptimizationLevel.HIGH  # Maximum quality
        assert phase3.point_reduction == 0.8  # Aggressive optimization


class TestPhaseConfigEdgeCases:
    """Test edge cases and boundary conditions for phase configurations."""

    def test_extreme_flow_weight_values(self):
        """Test extreme flow weight values."""
        # Very low weights
        low_weights = {
            "data": 0.0,
            "finder": 0.01,
        }
        
        config = Phase1Config(flow_weights=low_weights)
        assert config.flow_weights["data"] == 0.0
        assert config.flow_weights["finder"] == 0.01
        
        # Very high weights
        high_weights = {
            "data": 5.0,
            "finder": 10.0,
        }
        
        config = Phase1Config(flow_weights=high_weights)
        assert config.flow_weights["data"] == 5.0
        assert config.flow_weights["finder"] == 10.0

    def test_maximum_cluster_size_values(self):
        """Test very large cluster size values."""
        # Large cluster size should be allowed
        config = Phase2Config(min_cluster_size=1000)
        assert config.min_cluster_size == 1000

    def test_precision_boundary_values(self):
        """Test high-precision boundary values."""
        # Very precise decimal values at boundaries
        config = Phase3Config(
            contour_smoothing=0.0001,
            tension=0.9999,
            point_reduction=0.5000
        )
        
        assert config.contour_smoothing == 0.0001
        assert config.tension == 0.9999
        assert config.point_reduction == 0.5000

    def test_type_coercion_edge_cases(self):
        """Test type coercion for numeric parameters."""
        # String to float coercion
        config = Phase1Config(
            roundness="0.5",
            size_ratio="0.8"
        )
        assert config.roundness == 0.5
        assert isinstance(config.roundness, float)
        assert config.size_ratio == 0.8
        assert isinstance(config.size_ratio, float)
        
        # Integer to float coercion
        config = Phase3Config(
            contour_smoothing=1,
            tension=0
        )
        assert config.contour_smoothing == 1.0
        assert config.tension == 0.0

    def test_none_value_handling(self):
        """Test handling of None values where not allowed."""
        # None should not be allowed for required fields
        with pytest.raises(ValidationError):
            Phase1Config(roundness=None)
        
        with pytest.raises(ValidationError):
            Phase2Config(min_cluster_size=None)
        
        with pytest.raises(ValidationError):
            Phase3Config(tension=None)

    def test_list_parameter_edge_cases(self):
        """Test edge cases for list parameters."""
        # Very long module type lists
        long_type_list = [f"type_{i}" for i in range(100)]
        
        config = Phase2Config(cluster_module_types=long_type_list)
        assert len(config.cluster_module_types) == 100
        assert config.cluster_module_types[0] == "type_0"
        assert config.cluster_module_types[-1] == "type_99"
        
        # Duplicate module types should be preserved
        duplicate_types = ["data", "data", "timing", "data"]
        config = Phase3Config(contour_module_types=duplicate_types)
        assert config.contour_module_types == duplicate_types

    def test_dict_parameter_edge_cases(self):
        """Test edge cases for dictionary parameters."""
        # Empty flow weights
        config = Phase1Config(flow_weights={})
        assert config.flow_weights == {}
        
        # Single flow weight
        config = Phase1Config(flow_weights={"data": 1.0})
        assert config.flow_weights == {"data": 1.0}
        
        # Flow weights with special characters in keys
        special_weights = {
            "data_module": 1.0,
            "finder-pattern": 0.8,
            "type.special": 0.6,
        }
        
        config = Phase1Config(flow_weights=special_weights)
        assert config.flow_weights == special_weights


class TestPhaseConfigValidationMessages:
    """Test quality of validation error messages for phase configurations."""

    def test_phase1_validation_error_messages(self):
        """Test Phase1Config validation error message quality."""
        # Test roundness validation error
        with pytest.raises(ValidationError) as exc_info:
            Phase1Config(roundness=2.0)
        
        error_message = str(exc_info.value)
        assert "roundness" in error_message.lower()
        assert "1" in error_message  # Maximum value mentioned
        
        # Test size_ratio validation error
        with pytest.raises(ValidationError) as exc_info:
            Phase1Config(size_ratio=0.05)
        
        error_message = str(exc_info.value)
        assert "size_ratio" in error_message.lower()

    def test_phase2_validation_error_messages(self):
        """Test Phase2Config validation error message quality."""
        # Test min_cluster_size validation error
        with pytest.raises(ValidationError) as exc_info:
            Phase2Config(min_cluster_size=0)
        
        error_message = str(exc_info.value)
        assert "min_cluster_size" in error_message.lower()
        assert "greater" in error_message.lower()

    def test_phase3_validation_error_messages(self):
        """Test Phase3Config validation error message quality."""
        # Test contour_mode validation error
        with pytest.raises(ValidationError) as exc_info:
            Phase3Config(contour_mode="invalid_mode")
        
        error_message = str(exc_info.value)
        assert "contour_mode" in error_message.lower()
        # Should mention valid options
        assert "bezier" in error_message.lower() or "combined" in error_message.lower()

    def test_multiple_validation_errors(self):
        """Test handling of multiple validation errors."""
        with pytest.raises(ValidationError) as exc_info:
            Phase3Config(
                contour_smoothing=2.0,  # Invalid: > 1.0
                tension=-0.5,  # Invalid: < 0.0
                point_reduction=1.5  # Invalid: > 1.0
            )
        
        error_message = str(exc_info.value)
        # Should contain information about multiple fields
        assert "contour_smoothing" in error_message.lower()
        assert "tension" in error_message.lower()
        assert "point_reduction" in error_message.lower()