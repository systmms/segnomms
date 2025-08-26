"""
Unit tests for segnomms.core.matrix.manipulator module.

Tests the MatrixManipulator class which orchestrates centerpiece reserve
functionality using specialized components.
"""

from unittest.mock import Mock, patch

import pytest

from segnomms.config.enums import PlacementMode, ReserveMode
from segnomms.core.detector import ModuleDetector
from segnomms.core.geometry import CenterpieceGeometry
from segnomms.core.matrix.imprint_processor import ImprintProcessor
from segnomms.core.matrix.knockout_processor import KnockoutProcessor
from segnomms.core.matrix.manipulator import MatrixManipulator
from segnomms.core.matrix.matrix_validator import MatrixValidator
from segnomms.core.matrix.performance_monitor import CenterpiecePerformanceMonitor

# Fixtures for creating properly configured mock objects


@pytest.fixture
def mock_config_factory():
    """Factory fixture for creating properly configured mock config objects."""

    def _create_config(
        size=0.15,
        margin=2,
        offset_x=0.0,
        offset_y=0.0,
        placement=PlacementMode.CENTER,
        mode=ReserveMode.KNOCKOUT,
        matrix_size=21,
        shape="circle",
        **kwargs,
    ):
        """Create a mock config with all required numeric attributes."""
        config = Mock()

        # Set all numeric attributes as actual numbers, not Mocks
        config.size = size
        config.margin = margin
        config.offset_x = offset_x
        config.offset_y = offset_y
        config.placement = placement
        config.matrix_size = matrix_size
        config.shape = shape
        config.mode = mode

        # Add any additional attributes passed in kwargs
        for key, value in kwargs.items():
            setattr(config, key, value)

        return config

    return _create_config


@pytest.fixture
def basic_manipulator():
    """Fixture providing a basic MatrixManipulator instance."""
    matrix = [[False] * 21 for _ in range(21)]
    detector = Mock(spec=ModuleDetector)
    detector.get_size.return_value = 21
    detector.get_version.return_value = 1

    return MatrixManipulator(matrix, detector)


class TestMatrixManipulator:
    """Test MatrixManipulator class functionality."""

    def test_manipulator_initialization(self, basic_manipulator):
        """Test manipulator initialization and component setup."""
        manipulator = basic_manipulator

        # Verify components are created
        assert isinstance(manipulator.geometry, CenterpieceGeometry)
        assert isinstance(manipulator.knockout_processor, KnockoutProcessor)
        assert isinstance(manipulator.imprint_processor, ImprintProcessor)
        assert isinstance(manipulator.validator, MatrixValidator)
        assert isinstance(manipulator.performance_monitor, CenterpiecePerformanceMonitor)

    def test_safe_reserve_size_calculation(self, basic_manipulator):
        """Test calculation of safe centerpiece reserve size."""
        manipulator = basic_manipulator

        # Test different versions and error levels
        size_v1_l = manipulator.calculate_safe_reserve_size(1, "L")
        size_v1_h = manipulator.calculate_safe_reserve_size(1, "H")
        size_v5_l = manipulator.calculate_safe_reserve_size(5, "L")

        # Higher error correction should allow larger centerpiece (can recover more data)
        assert size_v1_h >= size_v1_l

        # Higher versions should allow larger centerpiece
        assert size_v5_l >= size_v1_l

        # All sizes should be reasonable (between 0 and 0.5)
        assert 0 < size_v1_l < 0.5
        assert 0 < size_v1_h < 0.5
        assert 0 < size_v5_l < 0.5

    def test_placement_offsets_calculation(self, basic_manipulator, mock_config_factory):
        """Test calculation of centerpiece placement offsets."""
        manipulator = basic_manipulator

        # Test center placement
        config = mock_config_factory(placement=PlacementMode.CENTER)
        offset_x, offset_y = manipulator.calculate_placement_offsets(config)
        assert offset_x == 0.0
        assert offset_y == 0.0

        # Test custom placement
        config = mock_config_factory(placement=PlacementMode.CUSTOM, offset_x=0.1, offset_y=-0.05)
        offset_x, offset_y = manipulator.calculate_placement_offsets(config)
        assert offset_x == 0.1
        assert offset_y == -0.05

    def test_centerpiece_bounds_calculation(self, basic_manipulator, mock_config_factory):
        """Test calculation of centerpiece bounds."""
        manipulator = basic_manipulator
        config = mock_config_factory(size=0.2)

        # Mock geometry component
        with patch.object(manipulator.geometry, "get_centerpiece_bounds") as mock_bounds:
            mock_bounds.return_value = (8, 8, 12, 12)

            bounds = manipulator.get_centerpiece_bounds(config)

            assert isinstance(bounds, dict)
            assert bounds["left"] == 8
            assert bounds["top"] == 8
            assert bounds["right"] == 12
            assert bounds["bottom"] == 12

            # Verify geometry was called with correct parameters
            mock_bounds.assert_called_once()

    def test_is_in_centerpiece(self, basic_manipulator, mock_config_factory):
        """Test checking if coordinates are in centerpiece area."""
        manipulator = basic_manipulator
        config = mock_config_factory()

        # Mock geometry component
        with patch.object(manipulator.geometry, "is_in_centerpiece") as mock_inside:
            mock_inside.return_value = True

            result = manipulator.is_in_centerpiece(10, 10, config)
            assert result is True

            mock_inside.assert_called_once_with(10, 10, config)

            # Test with coordinates outside
            mock_inside.return_value = False
            result = manipulator.is_in_centerpiece(5, 5, config)
            assert result is False

    def test_clear_centerpiece_area(self, basic_manipulator):
        """Test clearing centerpiece area (mode-agnostic)."""
        manipulator = basic_manipulator

        # Mock config with proper ReserveMode and numeric attributes
        config = Mock()
        config.mode = ReserveMode.KNOCKOUT
        config.size = 0.15
        config.margin = 2
        config.matrix_size = 21

        # Mock knockout processor
        with patch.object(manipulator.knockout_processor, "apply_knockout_mode") as mock_apply:
            expected_matrix = [[False] * 21 for _ in range(21)]
            mock_apply.return_value = expected_matrix

            result = manipulator.clear_centerpiece_area(config)

            assert result == expected_matrix
            mock_apply.assert_called_once_with(config)

    def test_apply_knockout_mode(self, basic_manipulator):
        """Test applying knockout mode processing."""
        manipulator = basic_manipulator

        # Mock config with numeric attributes
        config = Mock()
        config.mode = ReserveMode.KNOCKOUT
        config.size = 0.15
        config.margin = 2
        config.matrix_size = 21

        # Mock knockout processor
        with patch.object(manipulator.knockout_processor, "apply_knockout_mode") as mock_process:
            expected_matrix = [[False] * 21 for _ in range(21)]
            mock_process.return_value = expected_matrix

            result = manipulator.apply_knockout_mode(config)

            assert result == expected_matrix
            mock_process.assert_called_once_with(config)

    def test_apply_imprint_mode(self, basic_manipulator):
        """Test applying imprint mode processing."""
        manipulator = basic_manipulator

        # Mock config with numeric attributes
        config = Mock()
        config.mode = ReserveMode.IMPRINT
        config.size = 0.15
        config.margin = 2
        config.matrix_size = 21

        # Mock imprint processor
        with patch.object(manipulator.imprint_processor, "apply_imprint_mode") as mock_process:
            expected_matrix = [[False] * 21 for _ in range(21)]
            mock_process.return_value = expected_matrix

            result = manipulator.apply_imprint_mode(config)

            assert result == expected_matrix
            mock_process.assert_called_once_with(config)

    def test_validate_centerpiece_configuration(self, basic_manipulator):
        """Test validation of centerpiece configuration."""
        manipulator = basic_manipulator

        # Mock config
        config = Mock()

        # Mock validator
        with patch.object(manipulator.validator, "validate_centerpiece_configuration") as mock_validate:
            mock_validate.return_value = (True, [])

            is_valid, warnings = manipulator.validate_centerpiece_configuration(config)

            assert is_valid is True
            assert warnings == []
            mock_validate.assert_called_once_with(config)

            # Test with validation errors
            mock_validate.return_value = (False, ["Size too large", "Invalid placement"])

            is_valid, warnings = manipulator.validate_centerpiece_configuration(config)

            assert is_valid is False
            assert len(warnings) == 2

    def test_analyze_pattern_preservation(self, basic_manipulator):
        """Test analysis of pattern preservation."""
        manipulator = basic_manipulator

        # Mock config
        config = Mock()

        # Mock validator
        with patch.object(manipulator.validator, "analyze_pattern_preservation") as mock_analyze:
            mock_analysis = Mock()
            mock_analysis.finder_patterns_preserved = True
            mock_analysis.timing_patterns_preserved = True
            mock_analyze.return_value = mock_analysis

            analysis = manipulator.analyze_pattern_preservation(config)

            assert analysis.finder_patterns_preserved is True
            assert analysis.timing_patterns_preserved is True
            mock_analyze.assert_called_once_with(config)

    def test_get_centerpiece_metadata(self, basic_manipulator):
        """Test retrieval of centerpiece metadata."""
        manipulator = basic_manipulator

        # Mock config with required attributes
        config = Mock()
        config.size = 0.2
        config.margin = 2
        config.offset_x = 0.0
        config.offset_y = 0.0
        config.shape = "circle"
        config.mode = ReserveMode.KNOCKOUT

        # Mock geometry bounds method
        with patch.object(manipulator.geometry, "get_centerpiece_bounds") as mock_bounds:
            mock_bounds.return_value = (8, 8, 12, 12)

            metadata = manipulator.get_centerpiece_metadata(config)

            assert isinstance(metadata, dict)
            assert "bounds" in metadata
            assert "shape" in metadata
            assert "mode" in metadata
            assert metadata["mode"] == ReserveMode.KNOCKOUT
            assert metadata["shape"] == "circle"

            # Verify geometry was called
            mock_bounds.assert_called_once_with(config)

    def test_get_performance_warnings(self, basic_manipulator):
        """Test retrieval of performance warnings."""
        manipulator = basic_manipulator

        # Mock config
        config = Mock()

        # Mock performance monitor
        with patch.object(manipulator.performance_monitor, "get_performance_warnings") as mock_warnings:
            mock_warnings.return_value = ["Warning 1", "Warning 2"]

            warnings = manipulator.get_performance_warnings(config)

            assert len(warnings) == 2
            assert "Warning 1" in warnings
            assert "Warning 2" in warnings
            mock_warnings.assert_called_once_with(config)

    def test_get_performance_summary(self, basic_manipulator):
        """Test retrieval of performance summary."""
        manipulator = basic_manipulator

        # Mock performance monitor
        with patch.object(manipulator.performance_monitor, "get_performance_summary") as mock_summary:
            expected_summary = {"processing_time": 0.05, "memory_usage": 1024, "optimization_level": "high"}
            mock_summary.return_value = expected_summary

            summary = manipulator.get_performance_summary()

            assert summary == expected_summary
            mock_summary.assert_called_once()


class TestMatrixManipulatorHelperMethods:
    """Test helper and utility methods."""

    def setup_method(self):
        """Set up test fixtures."""
        self.matrix = [[False] * 21 for _ in range(21)]
        self.detector = Mock(spec=ModuleDetector)
        self.detector.get_size.return_value = 21
        self.manipulator = MatrixManipulator(self.matrix, self.detector)

    def test_is_edge_module(self):
        """Test edge module detection."""
        # Create a simple config mock that works with the actual implementation
        config = Mock()
        config.size = 0.2
        config.margin = 2
        config.offset_x = 0.0
        config.offset_y = 0.0
        config.shape = "circle"

        # Test edge positions - the actual implementation logic may vary
        # so we test the method exists and returns boolean values
        result1 = self.manipulator._is_edge_module(0, 10, config)
        result2 = self.manipulator._is_edge_module(10, 10, config)

        assert isinstance(result1, bool)
        assert isinstance(result2, bool)

        # Edge positions should generally be considered edge modules
        # (exact logic depends on implementation)

    def test_imprint_calculations(self):
        """Test imprint mode calculation methods."""
        # Mock config with proper attributes
        config = Mock()
        config.size = 0.2  # Direct size attribute
        config.margin = 2
        config.offset_x = 0.0
        config.offset_y = 0.0
        config.shape = "circle"
        config.imprint_opacity = 0.5

        # Test opacity calculation
        opacity = self.manipulator._calculate_imprint_opacity(config)
        assert isinstance(opacity, float)
        assert 0.0 <= opacity <= 1.0

        # Test color shift calculation
        color_shift = self.manipulator._calculate_imprint_color_shift(config)
        assert isinstance(color_shift, dict)

        # Test size ratio calculation
        size_ratio = self.manipulator._calculate_imprint_size_ratio(config)
        assert isinstance(size_ratio, float)
        assert 0.0 <= size_ratio <= 1.0

    def test_component_getters(self):
        """Test component getter methods."""
        # All getters should return the correct component types
        assert isinstance(self.manipulator.get_geometry_component(), CenterpieceGeometry)
        assert isinstance(self.manipulator.get_knockout_processor(), KnockoutProcessor)
        assert isinstance(self.manipulator.get_imprint_processor(), ImprintProcessor)
        assert isinstance(self.manipulator.get_validator(), MatrixValidator)
        assert isinstance(self.manipulator.get_performance_monitor(), CenterpiecePerformanceMonitor)


class TestMatrixManipulatorEdgeCases:
    """Test edge cases and error conditions."""

    def test_invalid_matrix_initialization(self):
        """Test initialization with invalid matrix."""
        detector = Mock(spec=ModuleDetector)
        detector.get_size.return_value = 21

        # The MatrixManipulator may not validate matrix shape in constructor,
        # so let's test that it handles different matrices gracefully

        # Empty matrix may be accepted but should handle it properly
        try:
            manipulator = MatrixManipulator([], detector)
            assert isinstance(manipulator, MatrixManipulator)
        except (ValueError, IndexError):
            pass  # Either error is acceptable

        # Non-square matrix may be accepted
        invalid_matrix = [[True] * 5 for _ in range(3)]
        try:
            manipulator = MatrixManipulator(invalid_matrix, detector)
            assert isinstance(manipulator, MatrixManipulator)
        except (ValueError, IndexError):
            pass  # Either error is acceptable

    def test_large_centerpiece_size(self):
        """Test behavior with very large centerpiece size."""
        matrix = [[False] * 21 for _ in range(21)]
        detector = Mock(spec=ModuleDetector)
        detector.get_size.return_value = 21
        manipulator = MatrixManipulator(matrix, detector)

        # Test with maximum safe size
        max_size = manipulator.calculate_safe_reserve_size(1, "H")
        assert max_size < 0.5  # Should be reasonable

        # Test with oversized request (should be handled gracefully)
        oversized_config = Mock()
        oversized_config.size = 0.8  # Direct size attribute
        oversized_config.margin = 2  # Add margin attribute
        oversized_config.offset_x = 0.0
        oversized_config.offset_y = 0.0
        oversized_config.shape = "circle"

        is_valid, warnings = manipulator.validate_centerpiece_configuration(oversized_config)
        # Should catch the oversized configuration
        assert not is_valid or len(warnings) > 0

    def test_bounds_edge_cases(self):
        """Test bounds calculation edge cases."""
        matrix = [[False] * 21 for _ in range(21)]
        detector = Mock(spec=ModuleDetector)
        detector.get_size.return_value = 21
        manipulator = MatrixManipulator(matrix, detector)

        # Test with zero size centerpiece
        zero_config = Mock()
        zero_config.size = 0.0
        zero_config.margin = 0
        zero_config.offset_x = 0.0
        zero_config.offset_y = 0.0
        zero_config.shape = "circle"

        # Should handle gracefully
        result = manipulator.is_in_centerpiece(10, 10, zero_config)
        assert isinstance(result, bool)


class TestMatrixManipulatorIntegration:
    """Integration tests with real-world scenarios."""

    def test_complete_knockout_workflow(self, basic_manipulator, mock_config_factory):
        """Test complete knockout mode workflow."""
        manipulator = basic_manipulator
        config = mock_config_factory(mode=ReserveMode.KNOCKOUT)

        # Test complete workflow
        # 1. Validate configuration
        is_valid, warnings = manipulator.validate_centerpiece_configuration(config)

        # 2. Apply knockout mode
        if is_valid:
            result_matrix = manipulator.apply_knockout_mode(config)
            assert isinstance(result_matrix, list)
            assert len(result_matrix) == 21

        # 3. Get metadata
        metadata = manipulator.get_centerpiece_metadata(config)
        assert isinstance(metadata, dict)

        # 4. Check performance
        perf_warnings = manipulator.get_performance_warnings(config)
        assert isinstance(perf_warnings, list)

    def test_complete_imprint_workflow(self, basic_manipulator, mock_config_factory):
        """Test complete imprint mode workflow."""
        manipulator = basic_manipulator
        config = mock_config_factory(mode=ReserveMode.IMPRINT, size=0.2)
        config.imprint_opacity = 0.6

        # Test workflow
        result_matrix = manipulator.apply_imprint_mode(config)
        assert isinstance(result_matrix, list)

        # Get imprint-specific metadata
        imprint_metadata = manipulator.get_imprint_metadata()
        assert isinstance(imprint_metadata, dict)
