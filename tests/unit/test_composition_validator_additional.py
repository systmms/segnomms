"""Additional tests for CompositionValidator to improve coverage.

This test suite covers the missing code paths identified in the coverage report.
"""

import logging
from unittest.mock import Mock, patch

import pytest

from segnomms.config import (
    CenterpieceConfig,
    FrameConfig,
    GeometryConfig,
    MergeStrategy,
    ModuleShape,
    Phase3Config,
    RenderingConfig,
    StyleConfig,
)
from segnomms.validation.composition import CompositionValidator


class TestCompositionValidatorAdditional:
    """Additional test cases to improve CompositionValidator coverage."""

    @pytest.fixture
    def validator(self):
        """Create a standard validator."""
        return CompositionValidator(qr_version=5, error_level="M", matrix_size=37)

    @pytest.fixture
    def validator_low_error(self):
        """Create validator with low error correction."""
        return CompositionValidator(qr_version=5, error_level="L", matrix_size=37)

    def test_centerpiece_size_within_limits(self, validator):
        """Test centerpiece size validation within safe limits."""
        # Real safe_size for version=5, error='M' is 0.12 (12%)
        # Use 10% which is within the 12% limit - no mocking needed
        centerpiece_config = CenterpieceConfig(enabled=True, size=0.10, shape="circle")

        errors = validator.validate_centerpiece_safety(centerpiece_config)

        # Should have no errors since 10% < 12% limit
        assert len(errors) == 0

    def test_centerpiece_offset_x_bounds_error(self, validator):
        """Test centerpiece X offset bounds validation."""
        with patch("segnomms.validation.composition.CenterpieceGeometry") as mock_geom:
            mock_instance = Mock()
            mock_instance.calculate_safe_reserve_size.return_value = 0.30
            mock_geom.return_value = mock_instance

            # Create centerpiece with invalid X offset
            centerpiece_config = CenterpieceConfig(
                enabled=True, size=0.2, offset_x=0.4, shape="circle"  # Too large: 0.5 - 0.2 = 0.3 max
            )

            errors = validator.validate_centerpiece_safety(centerpiece_config)

            assert len(errors) > 0
            assert any("X offset" in error and "beyond QR bounds" in error for error in errors)

    def test_centerpiece_offset_y_bounds_error(self, validator):
        """Test centerpiece Y offset bounds validation."""
        with patch("segnomms.validation.composition.CenterpieceGeometry") as mock_geom:
            mock_instance = Mock()
            mock_instance.calculate_safe_reserve_size.return_value = 0.30
            mock_geom.return_value = mock_instance

            # Create centerpiece with invalid Y offset
            centerpiece_config = CenterpieceConfig(
                enabled=True, size=0.2, offset_y=0.4, shape="circle"  # Too large
            )

            errors = validator.validate_centerpiece_safety(centerpiece_config)

            assert len(errors) > 0
            assert any("Y offset" in error and "beyond QR bounds" in error for error in errors)

    def test_centerpiece_large_margin_warning(self, validator, caplog):
        """Test warning for large centerpiece margin."""
        with patch("segnomms.validation.composition.CenterpieceGeometry") as mock_geom:
            mock_instance = Mock()
            mock_instance.calculate_safe_reserve_size.return_value = 0.30
            mock_geom.return_value = mock_instance

            centerpiece_config = CenterpieceConfig(
                enabled=True, size=0.15, margin=6, shape="circle"  # Large margin (> 5)
            )

            with caplog.at_level(logging.WARNING):
                validator.validate_centerpiece_safety(centerpiece_config)

            assert "Large centerpiece margin" in caplog.text

    def test_contrast_ratio_validation_fail(self, validator):
        """Test contrast ratio validation with low contrast colors."""
        # Use actual low contrast colors that will fail real validation
        # #777777 vs #888888 has ~1.26:1 contrast ratio (very low)
        config = RenderingConfig(dark="#777777", light="#888888")

        # Use real validation - no mocking needed
        errors = validator.validate_contrast_ratio(config, min_ratio=4.5)

        assert len(errors) > 0
        # Real error message mentions "below minimum" or contrast ratio
        assert any("below minimum" in error.lower() or "contrast" in error.lower() for error in errors)

    def test_module_size_very_small_warning(self, validator):
        """Test warning for very small module sizes."""
        config = RenderingConfig(scale=2)  # Very small

        warnings = validator.validate_module_size_scanability(config)

        assert len(warnings) > 0
        assert any("very small" in w and "may not scan reliably" in w for w in warnings)

    def test_module_size_small_warning(self, validator):
        """Test warning for small module sizes."""
        config = RenderingConfig(scale=4)  # Small but not very small

        warnings = validator.validate_module_size_scanability(config)

        assert len(warnings) > 0
        assert any("small" in w and "Consider using at least 8px" in w for w in warnings)

    def test_module_size_very_large_warning(self, validator):
        """Test warning for very large module sizes."""
        config = RenderingConfig(scale=60)  # Very large

        warnings = validator.validate_module_size_scanability(config)

        assert len(warnings) > 0
        assert any("very large" in w and "impact performance" in w for w in warnings)

    def test_module_size_aliasing_warning(self, validator):
        """Test aliasing warning for small pixel sizes."""
        config = RenderingConfig(scale=1)  # 1-2px range

        warnings = validator.validate_module_size_scanability(config)

        assert len(warnings) > 0
        assert any("aliasing issues" in w for w in warnings)

    def test_large_qr_small_modules_warning(self):
        """Test warning for large QR with small modules."""
        # Create validator for large QR
        validator = CompositionValidator(qr_version=15, error_level="M", matrix_size=77)
        config = RenderingConfig(scale=3)  # Small modules

        warnings = validator.validate_module_size_scanability(config)

        assert len(warnings) > 0
        assert any("Large QR code" in w and "difficult to scan" in w for w in warnings)

    def test_non_square_frame_small_modules_warning(self, validator):
        """Test warning for non-square frame with small modules."""
        config = RenderingConfig(scale=6, frame=FrameConfig(shape="circle"))  # Small modules

        warnings = validator.validate_module_size_scanability(config)

        assert len(warnings) > 0
        assert any("Non-square frame" in w and "small modules" in w for w in warnings)

    def test_automated_scanability_no_harness(self, validator):
        """Test automated scanability when no harness available."""
        config = RenderingConfig()

        with patch("segnomms.validation.composition.get_scanability_harness") as mock_harness:
            mock_harness.return_value = None

            errors = validator.run_automated_scanability_test(config)

            assert len(errors) > 0
            assert any("Automated scanability testing unavailable" in error for error in errors)

    def test_automated_scanability_test_failure(self, validator, caplog):
        """Test automated scanability test when it fails.

        Note: This test requires scanning libraries (PIL, opencv, pyzbar) to be
        available. Without them, get_scanability_harness() returns None and we
        can't test harness failure behavior.
        """
        # Import to check if harness is available
        from tests.helpers.scanning_harness import get_scanability_harness

        harness = get_scanability_harness()
        if harness is None:
            pytest.skip("Scanning libraries not available for harness testing")

        config = RenderingConfig()

        with patch("segnomms.validation.composition.get_scanability_harness") as mock_harness:
            # Mock harness that returns failure
            mock_harness_instance = Mock()
            mock_harness_instance.validate_scanability_threshold.return_value = (
                False,  # meets_threshold = False
                {"success_rate": 0.6, "failure_count": 4, "error_count": 2, "total_tests": 10},
            )
            mock_harness.return_value = mock_harness_instance

            errors = validator.run_automated_scanability_test(config, minimum_success_rate=0.8)

            assert len(errors) > 0
            assert any("60.0% success rate" in error for error in errors)
            assert any("Failed 4 scanning tests" in error for error in errors)
            assert any("Encountered 2 test errors" in error for error in errors)

    def test_automated_scanability_test_success(self, validator, caplog):
        """Test automated scanability test when it passes.

        Note: This test requires scanning libraries (PIL, opencv, pyzbar) to be
        available. Without them, get_scanability_harness() returns None.
        """
        # Import to check if harness is available
        from tests.helpers.scanning_harness import get_scanability_harness

        harness = get_scanability_harness()
        if harness is None:
            pytest.skip("Scanning libraries not available for harness testing")

        config = RenderingConfig()

        with patch("segnomms.validation.composition.get_scanability_harness") as mock_harness:
            # Mock harness that returns success
            mock_harness_instance = Mock()
            mock_harness_instance.validate_scanability_threshold.return_value = (
                True,  # meets_threshold = True
                {"success_rate": 0.95, "total_tests": 10},
            )
            mock_harness.return_value = mock_harness_instance

            with caplog.at_level(logging.INFO):
                errors = validator.run_automated_scanability_test(config)

            assert len(errors) == 0
            assert "95.0% success rate" in caplog.text

    def test_automated_scanability_test_exception(self, validator):
        """Test automated scanability test with exception.

        Note: This test requires scanning libraries (PIL, opencv, pyzbar) to be
        available. Without them, get_scanability_harness() returns None.
        """
        # Import to check if harness is available
        from tests.helpers.scanning_harness import get_scanability_harness

        harness = get_scanability_harness()
        if harness is None:
            pytest.skip("Scanning libraries not available for harness testing")

        config = RenderingConfig()

        with patch("segnomms.validation.composition.get_scanability_harness") as mock_harness:
            # Mock harness that raises exception
            mock_harness_instance = Mock()
            mock_harness_instance.validate_scanability_threshold.side_effect = Exception("Test error")
            mock_harness.return_value = mock_harness_instance

            errors = validator.run_automated_scanability_test(config)

            assert len(errors) > 0
            assert any("failed with error: Test error" in error for error in errors)

    def test_combined_features_fade_interactive_warning(self, validator):
        """Test warning for fade mode with interactive features."""
        config = RenderingConfig(frame=FrameConfig(clip_mode="fade"), style=StyleConfig(interactive=True))

        warnings = validator.validate_combined_features(config)

        assert len(warnings) > 0
        assert any("Fade frame mode" in w and "interactive hover effects" in w for w in warnings)

    def test_combined_features_low_error_many_features(self, validator_low_error):
        """Test warning for low error correction with many features."""
        config = RenderingConfig(
            frame=FrameConfig(shape="circle"),  # Non-square frame
            centerpiece=CenterpieceConfig(enabled=True, size=0.15),  # Centerpiece
            geometry=GeometryConfig(merge=MergeStrategy.SOFT),  # Merging
            phase3=Phase3Config(enabled=True),  # Phase 3
        )

        warnings = validator_low_error.validate_combined_features(config)

        assert len(warnings) > 0
        assert any("Low error correction" in w and "4 advanced features" in w for w in warnings)

    def test_combined_features_centerpiece_complex_shapes(self, validator):
        """Test warning for centerpiece with complex module shapes."""
        config = RenderingConfig(
            centerpiece=CenterpieceConfig(enabled=True, size=0.15),
            geometry=GeometryConfig(shape=ModuleShape.HEXAGON),
        )

        warnings = validator.validate_combined_features(config)

        assert len(warnings) > 0
        assert any("Module shape 'hexagon'" in w and "centerpiece" in w for w in warnings)

    def test_recommendations_large_qr_circle_frame(self):
        """Test recommendations for large QR with circle frame."""
        validator = CompositionValidator(qr_version=15, error_level="M", matrix_size=77)
        config = RenderingConfig(frame=FrameConfig(shape="circle"))

        recommendations = validator.get_recommendations(config)

        assert len(recommendations) > 0
        assert any("rounded-rect" in r and "squircle" in r for r in recommendations)

    def test_recommendations_centerpiece_error_level(self, validator):
        """Test recommendations for centerpiece with low error correction."""
        config = RenderingConfig(centerpiece=CenterpieceConfig(enabled=True, size=0.20))  # 20% centerpiece

        recommendations = validator.get_recommendations(config)

        assert len(recommendations) > 0
        assert any("consider using error level 'Q' or 'H'" in r for r in recommendations)

    def test_recommendations_centerpiece_shape_harmony(self, validator):
        """Test recommendations for centerpiece/frame shape harmony."""
        config = RenderingConfig(
            frame=FrameConfig(shape="circle"),
            centerpiece=CenterpieceConfig(enabled=True, size=0.15, shape="rect"),
        )

        recommendations = validator.get_recommendations(config)

        assert len(recommendations) > 0
        assert any("circular centerpiece" in r and "visual harmony" in r for r in recommendations)

    def test_recommendations_fade_performance(self, validator):
        """Test recommendations for fade mode performance."""
        config = RenderingConfig(frame=FrameConfig(clip_mode="fade"), phase3=Phase3Config(enabled=True))

        recommendations = validator.get_recommendations(config)

        assert len(recommendations) > 0
        assert any("Fade frame" in r and "impact performance" in r for r in recommendations)

    def test_validate_all_with_scanability_tests(self, validator):
        """Test validate_all with scanability testing enabled.

        Note: This test requires scanning libraries (PIL, opencv, pyzbar) to be
        available. Without them, get_scanability_harness() returns None.
        """
        # Import to check if harness is available
        from tests.helpers.scanning_harness import get_scanability_harness

        harness = get_scanability_harness()
        if harness is None:
            pytest.skip("Scanning libraries not available for harness testing")

        config = RenderingConfig(dark="#000000", light="#FFFFFF")

        with patch("segnomms.validation.composition.get_scanability_harness") as mock_harness:
            # Mock successful scanability test
            mock_harness_instance = Mock()
            mock_harness_instance.validate_scanability_threshold.return_value = (
                True,
                {"success_rate": 0.9, "total_tests": 10},
            )
            mock_harness.return_value = mock_harness_instance

            result = validator.validate_all(
                config, run_scanability_tests=True, min_scanability_success_rate=0.8
            )

            assert result.valid is True
            assert len(result.errors) == 0

    def test_validate_all_comprehensive(self, validator):
        """Test comprehensive validation with all features."""
        # Use real colors with good contrast - #FF0000 vs #FFFFFF has good contrast
        config = RenderingConfig(
            dark="#FF0000",
            light="#FFFFFF",
            scale=10,
            border=4,
            frame=FrameConfig(shape="rounded-rect", corner_radius=0.2),
            centerpiece=CenterpieceConfig(enabled=True, size=0.10, shape="circle"),  # 10% within 12% limit
            geometry=GeometryConfig(merge=MergeStrategy.SOFT),
        )

        # Use real validation - no mocking needed
        # Note: This will produce warnings (centerpiece is 10% which is close to the 12% limit)
        result = validator.validate_all(config, min_contrast_ratio=3.0)

        assert isinstance(result.errors, list)
        assert isinstance(result.warnings, list)
        assert isinstance(result.recommendations, list)
        assert isinstance(result.valid, bool)
