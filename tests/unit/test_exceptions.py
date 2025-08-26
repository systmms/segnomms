"""Tests for custom exception hierarchy."""

import pytest

from segnomms.exceptions import (
    CapabilityError,
    CapabilityManifestError,
    ColorError,
    ConfigurationError,
    ContrastRatioError,
    DependencyError,
    FeatureNotSupportedError,
    IncompatibleConfigError,
    IntentDegradationError,
    IntentProcessingError,
    IntentTransformationError,
    IntentValidationError,
    InvalidColorFormatError,
    MatrixBoundsError,
    MatrixError,
    MatrixSizeError,
    MissingDependencyError,
    OptionalFeatureUnavailableError,
    PaletteValidationError,
    PerformanceError,
    PresetNotFoundError,
    RenderingError,
    SegnoMMSError,
    ShapeRenderingError,
    SVGGenerationError,
    UnsupportedIntentError,
    ValidationError,
)


class TestBaseException:
    """Test base SegnoMMSError functionality."""

    def test_basic_error(self):
        """Test basic error creation."""
        error = SegnoMMSError("Test error")
        assert str(error) == "[SegnoMMSError] Test error"
        assert error.message == "Test error"
        assert error.code == "SegnoMMSError"
        assert error.details == {}
        assert error.suggestion is None

    def test_error_with_all_fields(self):
        """Test error with all fields populated."""
        error = SegnoMMSError(
            message="Test error",
            code="TEST_ERROR",
            details={"key": "value"},
            suggestion="Try this instead",
        )
        assert str(error) == "[TEST_ERROR] Test error Suggestion: Try this instead"
        assert error.code == "TEST_ERROR"
        assert error.details == {"key": "value"}
        assert error.suggestion == "Try this instead"

    def test_to_dict(self):
        """Test converting error to dictionary."""
        error = SegnoMMSError(
            message="Test error",
            code="TEST_ERROR",
            details={"key": "value"},
            suggestion="Try this",
        )
        result = error.to_dict()
        assert result == {
            "error": "TEST_ERROR",
            "message": "Test error",
            "details": {"key": "value"},
            "suggestion": "Try this",
        }


class TestConfigurationErrors:
    """Test configuration-related exceptions."""

    def test_validation_error(self):
        """Test ValidationError."""
        error = ValidationError(
            field="scale",
            value=-1,
            message="Scale must be positive",
            suggestion="Use a value >= 1",
        )
        assert error.code == "VALIDATION_ERROR"
        assert error.field == "scale"
        assert error.value == -1
        assert error.details == {"field": "scale", "value": -1}

    def test_intent_validation_error(self):
        """Test IntentValidationError."""
        error = IntentValidationError(
            intent_path="style.module_shape",
            message="Invalid shape",
            original_value="invalid",
            suggestion="Use 'square' or 'circle'",
        )
        assert error.code == "INTENT_VALIDATION_ERROR"
        assert error.intent_path == "style.module_shape"
        assert error.original_value == "invalid"
        assert error.details["intent_path"] == "style.module_shape"

    def test_preset_not_found_error(self):
        """Test PresetNotFoundError."""
        available = ["minimal", "standard", "premium"]
        error = PresetNotFoundError("custom", available)
        assert error.code == "PRESET_NOT_FOUND"
        assert error.preset_name == "custom"
        assert error.available_presets == available
        assert "Use one of: minimal, standard, premium" in str(error)

    def test_incompatible_config_error(self):
        """Test IncompatibleConfigError."""
        error = IncompatibleConfigError(
            option1="merge='aggressive'",
            option2="safe_mode=True",
            message="Aggressive merge not allowed in safe mode",
            suggestion="Use merge='soft' or disable safe mode",
        )
        assert error.code == "INCOMPATIBLE_CONFIG"
        assert error.option1 == "merge='aggressive'"
        assert error.option2 == "safe_mode=True"


class TestRenderingErrors:
    """Test rendering-related exceptions."""

    def test_matrix_size_error(self):
        """Test MatrixSizeError."""
        # Test too small
        error = MatrixSizeError(5)
        assert error.code == "MATRIX_SIZE_ERROR"
        assert error.size == 5
        assert "too small" in error.message
        assert "Minimum QR code size is 11x11" in str(error)

        # Test invalid size
        error = MatrixSizeError(22)
        assert "Invalid QR matrix size" in error.message

        # Test custom message
        error = MatrixSizeError(100, "Custom error message")
        assert error.message == "Custom error message"
        assert error.suggestion is None

    def test_matrix_bounds_error(self):
        """Test MatrixBoundsError."""
        error = MatrixBoundsError(row=25, col=30, size=21)
        assert error.code == "MATRIX_BOUNDS_ERROR"
        assert error.row == 25
        assert error.col == 30
        assert error.matrix_size == 21
        assert "Position (25, 30) out of bounds" in error.message
        assert "Valid range is (0, 0) to (20, 20)" in str(error)

    def test_shape_rendering_error(self):
        """Test ShapeRenderingError."""
        error = ShapeRenderingError(
            shape="complex-pattern",
            message="Failed to render complex pattern",
            details={"phase": "path_generation"},
        )
        assert error.code == "SHAPE_RENDERING_ERROR"
        assert error.shape == "complex-pattern"
        assert error.details["shape"] == "complex-pattern"
        assert error.details["phase"] == "path_generation"

    def test_svg_generation_error(self):
        """Test SVGGenerationError."""
        error = SVGGenerationError("Failed to generate SVG", phase="style_application")
        assert error.code == "SVG_GENERATION_ERROR"
        assert error.phase == "style_application"
        assert error.details == {"phase": "style_application"}

    def test_performance_error(self):
        """Test PerformanceError."""
        error = PerformanceError(
            metric="rendering_time_ms",
            value=5000,
            limit=2000,
        )
        assert error.code == "PERFORMANCE_ERROR"
        assert error.metric == "rendering_time_ms"
        assert error.value == 5000
        assert error.limit == 2000
        assert "rendering_time_ms=5000 (limit=2000)" in error.message


class TestIntentProcessingErrors:
    """Test intent processing exceptions."""

    def test_unsupported_intent_error(self):
        """Test UnsupportedIntentError."""
        error = UnsupportedIntentError(
            intent_path="animation.fade_in",
            feature="CSS fade-in animation",
            alternatives=["Use static SVG", "Add animations post-processing"],
            planned_version="1.0.0",
        )
        assert error.code == "UNSUPPORTED_INTENT"
        assert error.intent_path == "animation.fade_in"
        assert error.feature == "CSS fade-in animation"
        assert error.alternatives == ["Use static SVG", "Add animations post-processing"]
        assert error.planned_version == "1.0.0"
        assert "Try: Use static SVG" in str(error)

    def test_intent_degradation_error(self):
        """Test IntentDegradationError."""
        error = IntentDegradationError(
            intent_path="style.merge",
            requested="ultra-aggressive",
            reason="Not a valid merge strategy",
            applied="aggressive",
        )
        assert error.code == "INTENT_DEGRADATION"
        assert error.intent_path == "style.merge"
        assert error.requested == "ultra-aggressive"
        assert error.applied == "aggressive"
        assert error.reason == "Not a valid merge strategy"

    def test_intent_transformation_error(self):
        """Test IntentTransformationError."""
        error = IntentTransformationError(
            intent_path="branding.logo_url",
            message="Failed to process logo URL",
            original_value="https://example.com/logo.png",
            error_details="URL fetch failed: 404",
        )
        assert error.code == "INTENT_TRANSFORMATION_ERROR"
        assert error.intent_path == "branding.logo_url"
        assert error.original_value == "https://example.com/logo.png"
        assert error.details["error_details"] == "URL fetch failed: 404"


class TestColorErrors:
    """Test color-related exceptions."""

    def test_invalid_color_format_error(self):
        """Test InvalidColorFormatError."""
        error = InvalidColorFormatError("not-a-color")
        assert error.code == "INVALID_COLOR_FORMAT"
        assert error.color == "not-a-color"
        assert "hex (#RRGGBB)" in str(error)

        # Test with custom formats
        error = InvalidColorFormatError(
            "xyz(1,2,3)",
            accepted_formats=["hex", "rgb", "hsl"],
        )
        assert error.accepted_formats == ["hex", "rgb", "hsl"]

    def test_contrast_ratio_error(self):
        """Test ContrastRatioError."""
        error = ContrastRatioError(
            foreground="#333333",
            background="#444444",
            ratio=1.5,
            required_ratio=4.5,
            standard="WCAG AA",
        )
        assert error.code == "CONTRAST_RATIO_ERROR"
        assert error.foreground == "#333333"
        assert error.background == "#444444"
        assert error.ratio == 1.5
        assert error.required_ratio == 4.5
        assert error.standard == "WCAG AA"
        assert "1.50 < 4.5 (WCAG AA)" in error.message

    def test_palette_validation_error(self):
        """Test PaletteValidationError."""
        error = PaletteValidationError(
            message="Invalid palette configuration",
            invalid_colors=["not-a-color", "xyz"],
            validation_errors=["Cannot parse color: not-a-color", "Cannot parse color: xyz"],
        )
        assert error.code == "PALETTE_VALIDATION_ERROR"
        assert error.invalid_colors == ["not-a-color", "xyz"]
        assert len(error.validation_errors) == 2


class TestCapabilityErrors:
    """Test capability-related exceptions."""

    def test_feature_not_supported_error(self):
        """Test FeatureNotSupportedError."""
        error = FeatureNotSupportedError(
            feature="Advanced animations",
            category="animations",
            min_version="2.0.0",
        )
        assert error.code == "FEATURE_NOT_SUPPORTED"
        assert error.feature == "Advanced animations"
        assert error.category == "animations"
        assert error.min_version == "2.0.0"
        assert "Upgrade to version 2.0.0 or later" in str(error)

    def test_capability_manifest_error(self):
        """Test CapabilityManifestError."""
        error = CapabilityManifestError(
            "Failed to load capability manifest",
            manifest_path="/path/to/manifest.json",
        )
        assert error.code == "CAPABILITY_MANIFEST_ERROR"
        assert error.manifest_path == "/path/to/manifest.json"
        assert error.details["manifest_path"] == "/path/to/manifest.json"


class TestDependencyErrors:
    """Test dependency-related exceptions."""

    def test_missing_dependency_error(self):
        """Test MissingDependencyError."""
        error = MissingDependencyError(
            dependency="pyzbar",
            feature="QR code scanning",
            install_command="pip install pyzbar",
        )
        assert error.code == "MISSING_DEPENDENCY"
        assert error.dependency == "pyzbar"
        assert error.feature == "QR code scanning"
        assert error.install_command == "pip install pyzbar"
        assert "required for QR code scanning" in error.message
        assert "Install with: pip install pyzbar" in str(error)

        # Test auto-suggestion for known packages
        error = MissingDependencyError("opencv-python")
        assert "pip install pyzbar opencv-python" in str(error)

    def test_optional_feature_unavailable_error(self):
        """Test OptionalFeatureUnavailableError."""
        error = OptionalFeatureUnavailableError(
            feature="Visual regression testing",
            reason="ImageMagick not installed",
            dependencies=["imagemagick", "wand"],
        )
        assert error.code == "OPTIONAL_FEATURE_UNAVAILABLE"
        assert error.feature == "Visual regression testing"
        assert error.reason == "ImageMagick not installed"
        assert error.dependencies == ["imagemagick", "wand"]
        assert "Install: imagemagick wand" in str(error)


class TestExceptionHierarchy:
    """Test exception inheritance and relationships."""

    def test_inheritance_chain(self):
        """Test that exceptions inherit properly."""
        # All exceptions should inherit from SegnoMMSError
        error = ValidationError("field", "value", "message")
        assert isinstance(error, ConfigurationError)
        assert isinstance(error, SegnoMMSError)
        assert isinstance(error, Exception)

        # Matrix errors should inherit from RenderingError
        error = MatrixSizeError(5)
        assert isinstance(error, MatrixError)
        assert isinstance(error, RenderingError)
        assert isinstance(error, SegnoMMSError)

        # Intent errors should inherit properly
        error = UnsupportedIntentError("path", "feature")
        assert isinstance(error, IntentProcessingError)
        assert isinstance(error, SegnoMMSError)

    def test_exception_catching(self):
        """Test that exceptions can be caught at different levels."""
        # Should be able to catch specific exception
        with pytest.raises(MatrixSizeError):
            raise MatrixSizeError(5)

        # Should be able to catch parent exception
        with pytest.raises(MatrixError):
            raise MatrixBoundsError(10, 10, 5)

        # Should be able to catch at rendering level
        with pytest.raises(RenderingError):
            raise ShapeRenderingError("circle", "Failed")

        # Should be able to catch at base level
        with pytest.raises(SegnoMMSError):
            raise InvalidColorFormatError("not-a-color")

    def test_error_codes_are_stable(self):
        """Test that error codes are consistent."""
        # Each error type should have a stable code
        assert ValidationError("f", "v", "m").code == "VALIDATION_ERROR"
        assert IntentValidationError("p", "m").code == "INTENT_VALIDATION_ERROR"
        assert MatrixSizeError(5).code == "MATRIX_SIZE_ERROR"
        assert UnsupportedIntentError("p", "f").code == "UNSUPPORTED_INTENT"

        # Custom codes should override
        error = SegnoMMSError("message", code="CUSTOM_CODE")
        assert error.code == "CUSTOM_CODE"
