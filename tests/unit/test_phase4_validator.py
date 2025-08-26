"""Test suite for Phase4Validator class."""

import pytest

from segnomms.config import (
    CenterpieceConfig,
    FrameConfig,
    MergeStrategy,
    ModuleShape,
    QuietZoneConfig,
    RenderingConfig,
)
from segnomms.validation.phase4 import Phase4Validator


class TestPhase4Validator:
    """Test cases for the Phase4Validator class."""

    @pytest.fixture
    def validator_small(self):
        """Create validator for small QR code."""
        return Phase4Validator(qr_version=1, error_level="L", matrix_size=21)

    @pytest.fixture
    def validator_medium(self):
        """Create validator for medium QR code."""
        return Phase4Validator(qr_version=5, error_level="M", matrix_size=37)

    @pytest.fixture
    def validator_large(self):
        """Create validator for large QR code."""
        return Phase4Validator(qr_version=10, error_level="H", matrix_size=57)

    def test_validate_frame_safety_square(self, validator_medium):
        """Test square frame validation (should always pass)."""
        frame_config = FrameConfig(shape="square")
        warnings = validator_medium.validate_frame_safety(frame_config, border_modules=2)

        assert len(warnings) == 0

    def test_validate_frame_safety_non_square_small_border(self, validator_medium):
        """Test non-square frame with insufficient border."""
        frame_config = FrameConfig(shape="circle")
        warnings = validator_medium.validate_frame_safety(frame_config, border_modules=2)

        assert len(warnings) > 0
        assert any("4-module quiet zone" in w for w in warnings)

    def test_validate_frame_safety_circle_small_qr(self, validator_small):
        """Test circle frame with small QR code."""
        frame_config = FrameConfig(shape="circle")
        warnings = validator_small.validate_frame_safety(frame_config, border_modules=4)

        assert len(warnings) > 0
        assert any("clip important corner areas" in w for w in warnings)

    def test_validate_frame_safety_fade_custom(self, validator_medium):
        """Test fade mode with custom shape warning."""
        frame_config = FrameConfig(shape="custom", clip_mode="fade", custom_path="M0,0 L10,10")
        warnings = validator_medium.validate_frame_safety(frame_config, border_modules=4)

        assert len(warnings) > 0
        assert any("unexpected results" in w for w in warnings)

    def test_validate_frame_safety_rounded_rect_high_radius(self, validator_medium):
        """Test rounded rectangle with large corner radius."""
        frame_config = FrameConfig(shape="rounded-rect", corner_radius=0.6)
        warnings = validator_medium.validate_frame_safety(frame_config, border_modules=4)

        assert len(warnings) > 0
        assert any("Large corner radius" in w for w in warnings)

    def test_validate_centerpiece_safety_disabled(self, validator_medium):
        """Test disabled centerpiece (should pass)."""
        config = CenterpieceConfig(enabled=False)
        errors = validator_medium.validate_centerpiece_safety(config)

        assert len(errors) == 0

    def test_validate_centerpiece_safety_within_limits(self, validator_large):
        """Test centerpiece within safe limits."""
        config = CenterpieceConfig(
            enabled=True, size=0.2, shape="circle"  # 20% for H level is safe (30% * 0.8 = 24%)
        )
        errors = validator_large.validate_centerpiece_safety(config)

        assert len(errors) == 0

    def test_validate_centerpiece_safety_exceeds_limits(self, validator_medium):
        """Test centerpiece exceeding safe limits."""
        config = CenterpieceConfig(
            enabled=True, size=0.15, shape="rect"  # 15% exceeds M level (15% * 0.8 = 12%)
        )
        errors = validator_medium.validate_centerpiece_safety(config)

        assert len(errors) > 0
        assert any("exceeds safe limit" in e for e in errors)

    def test_validate_centerpiece_safety_offset_bounds(self, validator_medium):
        """Test centerpiece with invalid offsets."""
        config = CenterpieceConfig(enabled=True, size=0.2, offset_x=0.4)  # Would put edge beyond bounds
        errors = validator_medium.validate_centerpiece_safety(config)

        assert len(errors) > 0
        assert any("would extend beyond QR bounds" in e for e in errors)

    def test_validate_centerpiece_safety_small_version(self, validator_small):
        """Test centerpiece on small QR version."""
        config = CenterpieceConfig(enabled=True, size=0.15)
        errors = validator_small.validate_centerpiece_safety(config)

        assert len(errors) > 0
        assert any("too small for centerpiece" in e for e in errors)

    def test_validate_combined_features_circle_large_centerpiece(self, validator_medium):
        """Test problematic combination: circle frame + large centerpiece."""
        config = RenderingConfig()
        config.frame.shape = "circle"
        config.centerpiece.enabled = True
        config.centerpiece.size = 0.35

        warnings = validator_medium.validate_combined_features(config)

        assert len(warnings) > 0
        assert any("Large centerpiece with circle frame" in w for w in warnings)

    def test_validate_combined_features_aggressive_merge_centerpiece(self, validator_medium):
        """Test aggressive merging with centerpiece."""
        config = RenderingConfig()
        config.geometry.merge = MergeStrategy.AGGRESSIVE
        config.centerpiece.enabled = True
        config.centerpiece.size = 0.1

        warnings = validator_medium.validate_combined_features(config)

        assert len(warnings) > 0
        assert any("Aggressive module merging with centerpiece" in w for w in warnings)

    def test_validate_combined_features_low_error_multiple_features(self, validator_small):
        """Test low error correction with multiple advanced features."""
        config = RenderingConfig()
        config.frame.shape = "circle"
        config.centerpiece.enabled = True
        config.geometry.merge = MergeStrategy.SOFT

        warnings = validator_small.validate_combined_features(config)

        assert len(warnings) > 0
        assert any("Low error correction" in w for w in warnings)
        assert any("advanced features" in w for w in warnings)

    def test_validate_combined_features_centerpiece_star_shape(self, validator_medium):
        """Test centerpiece with problematic module shape."""
        config = RenderingConfig()
        config.centerpiece.enabled = True
        config.geometry.shape = "star"

        warnings = validator_medium.validate_combined_features(config)

        assert len(warnings) > 0
        assert any("visual conflicts" in w for w in warnings)

    def test_get_recommendations_large_circle(self, validator_large):
        """Test recommendations for large QR with circle frame."""
        config = RenderingConfig()
        config.frame.shape = "circle"

        # Create validator with large matrix
        large_validator = Phase4Validator(qr_version=15, error_level="H", matrix_size=77)
        recommendations = large_validator.get_recommendations(config)

        assert len(recommendations) > 0
        assert any("rounded-rect" in r or "squircle" in r for r in recommendations)

    def test_get_recommendations_centerpiece_error_level(self, validator_small):
        """Test recommendations for centerpiece with low error level."""
        config = RenderingConfig()
        config.centerpiece.enabled = True
        config.centerpiece.size = 0.2

        recommendations = validator_small.get_recommendations(config)

        assert len(recommendations) > 0
        assert any("error level 'Q' or 'H'" in r for r in recommendations)

    def test_get_recommendations_shape_harmony(self, validator_medium):
        """Test recommendations for shape harmony."""
        config = RenderingConfig()
        config.frame.shape = "circle"
        config.centerpiece.enabled = True
        config.centerpiece.shape = "rect"

        recommendations = validator_medium.get_recommendations(config)

        assert len(recommendations) > 0
        assert any("circular centerpiece" in r for r in recommendations)

    def test_validate_all_success(self, validator_medium):
        """Test complete validation with valid configuration."""
        config = RenderingConfig()
        config.frame.shape = "rounded-rect"
        config.frame.corner_radius = 0.2
        config.centerpiece.enabled = True
        config.centerpiece.size = 0.1
        config.border = 4

        result = validator_medium.validate_all(config)

        assert result.valid is True
        assert len(result.errors) == 0
        assert isinstance(result.warnings, list)
        assert isinstance(result.recommendations, list)

    def test_validate_all_with_errors(self, validator_small):
        """Test complete validation with invalid configuration."""
        config = RenderingConfig()
        config.frame.shape = "invalid_shape"  # This will cause validation error
        config.centerpiece.enabled = True
        config.centerpiece.size = 0.5  # Too large

        result = validator_small.validate_all(config)

        assert result.valid is False
        assert len(result.errors) > 0
        assert any("Centerpiece size" in e for e in result.errors)

    def test_frame_config_validation(self):
        """Test FrameConfig validation methods."""
        # Valid config
        config = FrameConfig(shape="circle", corner_radius=0.3)
        assert config.shape == "circle"

        # Note: Invalid configurations now raise ValidationError at creation time
        # These are handled by Pydantic's automatic validation

        # Valid rounded-rect config
        config = FrameConfig(shape="rounded-rect", corner_radius=0.3)
        assert config.shape == "rounded-rect"

        # Custom shape with path
        config = FrameConfig(shape="custom", custom_path="M0,0 L10,10")
        assert config.shape == "custom"

    def test_centerpiece_config_validation(self):
        """Test CenterpieceConfig validation methods."""
        # Valid disabled config
        config = CenterpieceConfig(enabled=False)
        assert config.enabled is False

        # Valid enabled config
        config = CenterpieceConfig(enabled=True, shape="circle", size=0.2)
        assert config.enabled is True
        assert config.shape == "circle"

        # Valid shape config
        config = CenterpieceConfig(enabled=True, shape="rect", size=0.2)
        assert config.shape == "rect"

        # Valid size config
        config = CenterpieceConfig(enabled=True, size=0.3)
        assert config.size == 0.3

        # Valid offset config
        config = CenterpieceConfig(enabled=True, size=0.2, offset_x=0.1, offset_y=0.1)
        assert config.offset_x == 0.1

    def test_quiet_zone_config_validation(self):
        """Test QuietZoneConfig validation methods."""
        # Valid config
        config = QuietZoneConfig(style="solid", color="#ffffff")
        assert config.style == "solid"
        assert config.color == "#ffffff"

        # Gradient with definition
        config = QuietZoneConfig(
            style="gradient", gradient={"type": "radial", "colors": ["#ffffff", "#cccccc"]}
        )
        assert config.style == "gradient"
        assert config.gradient is not None
