"""
Test suite for the graceful degradation system.
"""

from segnomms.config import (
    CenterpieceConfig,
    FrameConfig,
    GeometryConfig,
    PatternStyleConfig,
    RenderingConfig,
)
from segnomms.degradation import (
    DegradationManager,
    DegradationResult,
    DegradationWarning,
    WarningLevel,
)


class TestDegradationModels:
    """Test the degradation data models."""

    def test_degradation_warning_creation(self):
        """Test creating a degradation warning."""
        warning = DegradationWarning(
            level=WarningLevel.WARNING,
            feature="shape",
            message="Complex shape with small scale",
            original_value="star",
            degraded_value="square",
            reason="Complex shapes need larger modules",
            suggestion="Increase scale to at least 8px",
        )

        assert warning.level == WarningLevel.WARNING
        assert warning.feature == "shape"
        assert "star" in str(warning.original_value)
        assert "square" in str(warning.degraded_value)
        assert warning.suggestion is not None

    def test_degradation_warning_string_representation(self):
        """Test warning string representation."""
        warning = DegradationWarning(
            level=WarningLevel.CRITICAL,
            feature="colors",
            message="Low contrast detected",
            original_value={"dark": "gray", "light": "lightgray"},
            degraded_value={"dark": "black", "light": "white"},
            reason="QR codes need high contrast",
        )

        str_repr = str(warning)
        assert "🚨" in str_repr  # Critical emoji
        assert "Low contrast detected" in str_repr

    def test_degradation_result_creation(self):
        """Test creating a degradation result."""
        result = DegradationResult()

        assert result.warning_count == 0
        assert result.critical_count == 0
        assert not result.has_critical
        assert not result.degradation_applied

    def test_degradation_result_with_warnings(self):
        """Test degradation result with warnings."""
        result = DegradationResult()

        # Add warnings
        result.warnings.append(
            DegradationWarning(
                level=WarningLevel.INFO,
                feature="test",
                message="Info message",
                original_value="a",
                degraded_value="b",
                reason="test",
            )
        )

        result.warnings.append(
            DegradationWarning(
                level=WarningLevel.CRITICAL,
                feature="test2",
                message="Critical message",
                original_value="c",
                degraded_value="d",
                reason="test",
            )
        )

        assert result.warning_count == 2
        assert result.critical_count == 1
        assert result.has_critical

        # Test filtering
        critical_warnings = result.get_warnings_by_level(WarningLevel.CRITICAL)
        assert len(critical_warnings) == 1

        test_warnings = result.get_warnings_by_feature("test")
        assert len(test_warnings) == 1


class TestDegradationRules:
    """Test individual degradation rules."""

    def test_complex_shape_with_high_error_rule(self):
        """Test complex shape detection."""
        from segnomms.degradation.rules import ComplexShapeWithHighErrorRule

        rule = ComplexShapeWithHighErrorRule()

        # Should trigger - complex shape with small scale
        config = RenderingConfig(geometry=GeometryConfig(shape="star"), scale=5, safe_mode=False)
        warning = rule.check(config)
        assert warning is not None
        assert warning.level == WarningLevel.WARNING
        assert "star" in warning.message

        # Apply fallback
        degraded = rule.apply_fallback(config)
        assert degraded.geometry.shape == "square"

        # Should not trigger - large scale
        config.scale = 10
        warning = rule.check(config)
        assert warning is None

        # Should not trigger - safe mode enabled
        config.scale = 5
        config.safe_mode = True
        warning = rule.check(config)
        assert warning is None

    def test_low_contrast_rule(self):
        """Test low contrast detection."""
        from segnomms.degradation.rules import LowContrastRule

        rule = LowContrastRule()

        # Should trigger - low contrast
        config = RenderingConfig(dark="yellow", light="white")
        warning = rule.check(config)
        assert warning is not None
        assert warning.level == WarningLevel.CRITICAL
        assert "contrast" in warning.message.lower()

        # Apply fallback
        degraded = rule.apply_fallback(config)
        assert degraded.dark == "black"
        assert degraded.light == "white"

        # Should not trigger - high contrast
        config.dark = "black"
        config.light = "white"
        warning = rule.check(config)
        assert warning is None

    def test_tiny_modules_with_complexity_rule(self):
        """Test tiny module detection."""
        from segnomms.degradation.rules import TinyModulesWithComplexityRule

        rule = TinyModulesWithComplexityRule()

        # Should trigger - tiny modules with complex features
        config = RenderingConfig(
            scale=3,
            geometry=GeometryConfig(shape="hexagon", corner_radius=0.5),
            patterns=PatternStyleConfig(enabled=True, finder_color="red"),  # Need at least one override
        )
        warning = rule.check(config)
        assert warning is not None
        assert warning.level == WarningLevel.WARNING
        assert "small module size" in warning.message.lower()

        # Apply fallback
        degraded = rule.apply_fallback(config)
        assert degraded.geometry.shape == "square"
        assert degraded.geometry.corner_radius == 0.0
        assert degraded.patterns.enabled == False

    def test_fade_frame_with_pattern_styling_rule(self):
        """Test fade frame conflict detection."""
        from segnomms.degradation.rules import FadeFrameWithPatternStylingRule

        rule = FadeFrameWithPatternStylingRule()

        # Should trigger - fade with pattern colors
        config = RenderingConfig(
            frame=FrameConfig(clip_mode="fade"), patterns=PatternStyleConfig(enabled=True, finder_color="red")
        )
        warning = rule.check(config)
        assert warning is not None
        assert warning.level == WarningLevel.WARNING
        assert "fade" in warning.message.lower()

        # Apply fallback
        degraded = rule.apply_fallback(config)
        assert degraded.frame.clip_mode == "clip"

    def test_excessive_merging_rule(self):
        """Test excessive merging detection."""
        from segnomms.degradation.rules import ExcessiveMergingRule

        rule = ExcessiveMergingRule()

        # Should trigger - aggressive merge with small islands
        config = RenderingConfig(geometry=GeometryConfig(merge="aggressive", min_island_modules=1))
        warning = rule.check(config)
        assert warning is not None
        assert "aggressive merging" in warning.message.lower()

        # Apply fallback
        degraded = rule.apply_fallback(config)
        assert degraded.geometry.merge == "soft"
        assert degraded.geometry.min_island_modules == 3

    def test_centerpiece_too_large_rule(self):
        """Test large centerpiece detection."""
        from segnomms.degradation.rules import CenterpieceTooLargeRule

        rule = CenterpieceTooLargeRule()

        # Should trigger - centerpiece too large
        config = RenderingConfig(centerpiece=CenterpieceConfig(enabled=True, size=0.4))
        warning = rule.check(config)
        assert warning is not None
        assert warning.level == WarningLevel.CRITICAL
        assert "40%" in warning.message

        # Apply fallback
        degraded = rule.apply_fallback(config)
        assert degraded.centerpiece.size == 0.2


class TestDegradationManager:
    """Test the degradation manager."""

    def test_manager_initialization(self):
        """Test manager initialization."""
        manager = DegradationManager()
        assert len(manager.rules) > 0
        assert manager.enabled

        # Custom rules
        from segnomms.degradation.rules import LowContrastRule

        custom_manager = DegradationManager(rules=[LowContrastRule()])
        assert len(custom_manager.rules) == 1

    def test_apply_degradation_no_issues(self):
        """Test degradation with no issues."""
        manager = DegradationManager()
        config = RenderingConfig()  # Default safe config

        degraded, result = manager.apply_degradation(config)

        assert degraded.model_dump() == config.model_dump()
        assert result.warning_count == 0
        assert not result.degradation_applied

    def test_apply_degradation_with_warnings(self):
        """Test degradation with warnings but no critical issues."""
        manager = DegradationManager()

        # Config with warnings but not critical
        config = RenderingConfig(
            scale=7, geometry=GeometryConfig(shape="star"), safe_mode=False  # Small but not tiny
        )

        degraded, result = manager.apply_degradation(config)

        # Should have warnings but no changes (not critical)
        assert result.warning_count > 0
        assert not result.degradation_applied
        assert degraded.geometry.shape == "star"  # Not changed

    def test_apply_degradation_with_critical(self):
        """Test degradation with critical issues."""
        manager = DegradationManager()

        # Config with critical issue
        config = RenderingConfig(dark="yellow", light="white")

        degraded, result = manager.apply_degradation(config)

        # Should have changes
        assert result.warning_count > 0
        assert result.has_critical
        assert result.degradation_applied
        assert degraded.dark == "black"
        assert degraded.light == "white"

        # Check changes tracking
        assert "dark" in result.changes_made
        assert result.changes_made["dark"]["before"] == "yellow"
        assert result.changes_made["dark"]["after"] == "black"

    def test_apply_degradation_safe_mode(self):
        """Test that safe mode applies all degradations."""
        manager = DegradationManager()

        # Config with non-critical warning but safe mode on
        config = RenderingConfig(
            scale=4,  # Changed from 7 to 4 to trigger the rule (< 5)
            geometry=GeometryConfig(shape="star"),
            safe_mode=True,  # Force degradation
        )

        degraded, result = manager.apply_degradation(config)

        # Should apply degradation even for warnings
        assert result.warning_count > 0
        assert result.degradation_applied
        assert degraded.geometry.shape == "square"

    def test_check_only(self):
        """Test checking without applying degradation."""
        manager = DegradationManager()

        config = RenderingConfig(dark="yellow", light="white", scale=3, geometry=GeometryConfig(shape="star"))

        warnings = manager.check_only(config)

        # Should have multiple warnings
        assert len(warnings) >= 2

        # Config should not be modified
        assert config.dark == "yellow"
        assert config.geometry.shape == "star"

    def test_multiple_degradations(self):
        """Test multiple degradations applied together."""
        manager = DegradationManager()

        # Config with multiple issues
        config = RenderingConfig(
            dark="yellow", light="white", centerpiece=CenterpieceConfig(enabled=True, size=0.5)
        )

        degraded, result = manager.apply_degradation(config)

        # Should fix both issues
        assert degraded.dark == "black"
        assert degraded.light == "white"
        assert degraded.centerpiece.size == 0.2

        # Should have multiple warnings
        assert result.warning_count >= 2
        assert result.critical_count >= 2

        # Should track all changes
        assert "dark" in result.changes_made
        assert "centerpiece.size" in result.changes_made

    def test_manager_disable_enable(self):
        """Test disabling/enabling the manager."""
        manager = DegradationManager()

        config = RenderingConfig(dark="yellow", light="white")

        # Disable and test
        manager.disable()
        degraded, result = manager.apply_degradation(config)
        assert not result.degradation_applied
        assert degraded.dark == "yellow"  # Not changed

        # Re-enable and test
        manager.enable()
        degraded, result = manager.apply_degradation(config)
        assert result.degradation_applied
        assert degraded.dark == "black"  # Changed

    def test_get_rule_summary(self):
        """Test getting rule summary."""
        manager = DegradationManager()
        summary = manager.get_rule_summary()

        assert isinstance(summary, dict)
        assert len(summary) > 0

        # Check that rules are categorized
        for incomp_type, rule_names in summary.items():
            assert isinstance(rule_names, list)
            assert len(rule_names) > 0
            assert all(isinstance(name, str) for name in rule_names)

    def test_result_to_dict(self):
        """Test result serialization."""
        manager = DegradationManager()

        config = RenderingConfig(dark="yellow", light="white")

        _, result = manager.apply_degradation(config)
        result_dict = result.to_dict()

        assert "degradation_applied" in result_dict
        assert "warning_count" in result_dict
        assert "critical_count" in result_dict
        assert "warnings" in result_dict
        assert "changes_made" in result_dict

        # Warnings should be serialized
        assert isinstance(result_dict["warnings"], list)
        if result_dict["warnings"]:
            assert isinstance(result_dict["warnings"][0], dict)
