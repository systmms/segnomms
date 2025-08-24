"""Custom exception hierarchy for SegnoMMS.

This module provides a comprehensive exception hierarchy for better error handling,
debugging, and user experience throughout the SegnoMMS library.
"""

from typing import Any, Dict, List, Optional


class SegnoMMSError(Exception):
    """Base exception for all SegnoMMS errors.

    Provides structured error information with:
    - Error codes for programmatic handling
    - Detailed messages for debugging
    - Suggestions for resolution
    - Additional context data
    """

    def __init__(
        self,
        message: str,
        code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        suggestion: Optional[str] = None,
    ):
        """Initialize SegnoMMS error.

        Args:
            message: Human-readable error message
            code: Stable error code for programmatic handling
            details: Additional error context
            suggestion: Suggestion for resolving the error
        """
        super().__init__(message)
        self.message = message
        self.code = code or self.__class__.__name__
        self.details = details or {}
        self.suggestion = suggestion

    def __str__(self) -> str:
        """String representation of the error."""
        parts = [f"[{self.code}] {self.message}"]
        if self.suggestion:
            parts.append(f"Suggestion: {self.suggestion}")
        return " ".join(parts)

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for API responses."""
        return {
            "error": self.code,
            "message": self.message,
            "details": self.details,
            "suggestion": self.suggestion,
        }


# Configuration Errors
class ConfigurationError(SegnoMMSError):
    """Base class for configuration-related errors."""

    pass


class ValidationError(ConfigurationError):
    """Configuration validation error.

    Used when configuration values fail validation rules.
    """

    def __init__(
        self,
        field: str,
        value: Any,
        message: str,
        suggestion: Optional[str] = None,
    ):
        """Initialize validation error.

        Args:
            field: Configuration field that failed validation
            value: The invalid value
            message: Description of validation failure
            suggestion: How to fix the validation error
        """
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            details={"field": field, "value": value},
            suggestion=suggestion,
        )
        self.field = field
        self.value = value


class IntentValidationError(ConfigurationError):
    """Intent-specific validation error.

    Used when intent configurations are invalid or incompatible.
    """

    def __init__(
        self,
        intent_path: str,
        message: str,
        original_value: Any = None,
        suggestion: Optional[str] = None,
    ):
        """Initialize intent validation error.

        Args:
            intent_path: Path to the invalid intent (e.g., "style.module_shape")
            message: Description of the validation failure
            original_value: The original intent value
            suggestion: How to fix the intent
        """
        super().__init__(
            message=message,
            code="INTENT_VALIDATION_ERROR",
            details={
                "intent_path": intent_path,
                "original_value": original_value,
            },
            suggestion=suggestion,
        )
        self.intent_path = intent_path
        self.original_value = original_value


class PresetNotFoundError(ConfigurationError):
    """Raised when a requested preset doesn't exist."""

    def __init__(self, preset_name: str, available_presets: List[str]):
        """Initialize preset not found error.

        Args:
            preset_name: Name of the missing preset
            available_presets: List of available preset names
        """
        super().__init__(
            message=f"Preset '{preset_name}' not found",
            code="PRESET_NOT_FOUND",
            details={
                "preset": preset_name,
                "available": available_presets[:10],  # First 10
            },
            suggestion=f"Use one of: {', '.join(available_presets[:5])}...",
        )
        self.preset_name = preset_name
        self.available_presets = available_presets


class IncompatibleConfigError(ConfigurationError):
    """Raised when configuration options are incompatible."""

    def __init__(
        self,
        option1: str,
        option2: str,
        message: str,
        suggestion: Optional[str] = None,
    ):
        """Initialize incompatible configuration error.

        Args:
            option1: First conflicting option
            option2: Second conflicting option
            message: Description of the conflict
            suggestion: How to resolve the conflict
        """
        super().__init__(
            message=message,
            code="INCOMPATIBLE_CONFIG",
            details={
                "option1": option1,
                "option2": option2,
            },
            suggestion=suggestion,
        )
        self.option1 = option1
        self.option2 = option2


# Rendering Errors
class RenderingError(SegnoMMSError):
    """Base class for rendering-related errors."""

    pass


class MatrixError(RenderingError):
    """Base class for QR matrix-related errors."""

    pass


class MatrixSizeError(MatrixError):
    """Raised when QR matrix has invalid size."""

    def __init__(self, size: int, message: Optional[str] = None):
        """Initialize matrix size error.

        Args:
            size: The invalid matrix size
            message: Custom error message
        """
        if message is None:
            if size < 11:
                message = f"Matrix size {size}x{size} is too small"
                suggestion = "Minimum QR code size is 11x11"
            else:
                message = f"Invalid QR matrix size {size}x{size}"
                suggestion = (
                    "QR codes must be 21x21 or larger with size = 4*version + 17"
                )
        else:
            suggestion = None

        super().__init__(
            message=message,
            code="MATRIX_SIZE_ERROR",
            details={"size": size},
            suggestion=suggestion,
        )
        self.size = size


class MatrixBoundsError(MatrixError):
    """Raised when accessing matrix out of bounds."""

    def __init__(self, row: int, col: int, size: int):
        """Initialize matrix bounds error.

        Args:
            row: Row index that was out of bounds
            col: Column index that was out of bounds
            size: Matrix size
        """
        super().__init__(
            message=f"Position ({row}, {col}) out of bounds for {size}x{size} matrix",
            code="MATRIX_BOUNDS_ERROR",
            details={
                "row": row,
                "col": col,
                "size": size,
            },
            suggestion=f"Valid range is (0, 0) to ({size-1}, {size-1})",
        )
        self.row = row
        self.col = col
        self.matrix_size = size


class ShapeRenderingError(RenderingError):
    """Raised when shape rendering fails."""

    def __init__(
        self,
        shape: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        """Initialize shape rendering error.

        Args:
            shape: The shape that failed to render
            message: Error description
            details: Additional error context
        """
        super().__init__(
            message=message,
            code="SHAPE_RENDERING_ERROR",
            details={"shape": shape, **(details or {})},
            suggestion="Try a simpler shape or check shape parameters",
        )
        self.shape = shape


class SVGGenerationError(RenderingError):
    """Raised when SVG generation fails."""

    def __init__(self, message: str, phase: Optional[str] = None):
        """Initialize SVG generation error.

        Args:
            message: Error description
            phase: Phase where error occurred (e.g., "shape_generation", "style_application")
        """
        super().__init__(
            message=message,
            code="SVG_GENERATION_ERROR",
            details={"phase": phase} if phase else {},
        )
        self.phase = phase


class PerformanceError(RenderingError):
    """Raised when performance limits are exceeded."""

    def __init__(
        self,
        metric: str,
        value: Any,
        limit: Any,
        message: Optional[str] = None,
    ):
        """Initialize performance error.

        Args:
            metric: Performance metric that was exceeded
            value: Actual value
            limit: Limit that was exceeded
            message: Custom error message
        """
        if message is None:
            message = f"Performance limit exceeded: {metric}={value} (limit={limit})"

        super().__init__(
            message=message,
            code="PERFORMANCE_ERROR",
            details={
                "metric": metric,
                "value": value,
                "limit": limit,
            },
            suggestion="Consider simplifying configuration or reducing complexity",
        )
        self.metric = metric
        self.value = value
        self.limit = limit


# Intent Processing Errors
class IntentProcessingError(SegnoMMSError):
    """Base class for intent processing errors."""

    pass


class UnsupportedIntentError(IntentProcessingError):
    """Raised when an intent is not supported."""

    def __init__(
        self,
        intent_path: str,
        feature: str,
        alternatives: Optional[List[str]] = None,
        planned_version: Optional[str] = None,
    ):
        """Initialize unsupported intent error.

        Args:
            intent_path: Path to unsupported intent
            feature: Description of unsupported feature
            alternatives: Alternative approaches
            planned_version: Version when support is planned
        """
        details: Dict[str, Any] = {
            "intent_path": intent_path,
            "feature": feature,
        }
        if alternatives:
            details["alternatives"] = alternatives
        if planned_version:
            details["planned_version"] = planned_version

        suggestion = None
        if alternatives:
            suggestion = f"Try: {alternatives[0]}"
        elif planned_version:
            suggestion = f"Feature planned for version {planned_version}"

        super().__init__(
            message=f"Unsupported intent: {feature}",
            code="UNSUPPORTED_INTENT",
            details=details,
            suggestion=suggestion,
        )
        self.intent_path = intent_path
        self.feature = feature
        self.alternatives = alternatives or []
        self.planned_version = planned_version


class IntentDegradationError(IntentProcessingError):
    """Raised when intent degradation fails."""

    def __init__(
        self,
        intent_path: str,
        requested: Any,
        reason: str,
        applied: Optional[Any] = None,
    ):
        """Initialize intent degradation error.

        Args:
            intent_path: Path to degraded intent
            requested: What was requested
            reason: Why degradation was necessary
            applied: What was applied instead (if anything)
        """
        super().__init__(
            message=f"Intent degradation required: {reason}",
            code="INTENT_DEGRADATION",
            details={
                "intent_path": intent_path,
                "requested": requested,
                "applied": applied,
                "reason": reason,
            },
        )
        self.intent_path = intent_path
        self.requested = requested
        self.applied = applied
        self.reason = reason


class IntentTransformationError(IntentProcessingError):
    """Raised when intent transformation fails."""

    def __init__(
        self,
        intent_path: str,
        message: str,
        original_value: Any = None,
        error_details: Optional[str] = None,
    ):
        """Initialize intent transformation error.

        Args:
            intent_path: Path to the intent
            message: Error description
            original_value: Original intent value
            error_details: Detailed error information
        """
        super().__init__(
            message=message,
            code="INTENT_TRANSFORMATION_ERROR",
            details={
                "intent_path": intent_path,
                "original_value": original_value,
                "error_details": error_details,
            },
        )
        self.intent_path = intent_path
        self.original_value = original_value


# Color Errors
class ColorError(SegnoMMSError):
    """Base class for color-related errors."""

    pass


class InvalidColorFormatError(ColorError):
    """Raised when color format is invalid."""

    def __init__(self, color: str, accepted_formats: Optional[List[str]] = None):
        """Initialize invalid color format error.

        Args:
            color: The invalid color value
            accepted_formats: List of accepted color formats
        """
        if accepted_formats is None:
            accepted_formats = ["hex (#RRGGBB)", "rgb(r,g,b)", "named colors"]

        super().__init__(
            message=f"Invalid color format: '{color}'",
            code="INVALID_COLOR_FORMAT",
            details={
                "color": color,
                "accepted_formats": accepted_formats,
            },
            suggestion=f"Use one of: {', '.join(accepted_formats)}",
        )
        self.color = color
        self.accepted_formats = accepted_formats


class ContrastRatioError(ColorError):
    """Raised when color contrast is insufficient."""

    def __init__(
        self,
        foreground: str,
        background: str,
        ratio: float,
        required_ratio: float,
        standard: str = "WCAG AA",
    ):
        """Initialize contrast ratio error.

        Args:
            foreground: Foreground color
            background: Background color
            ratio: Actual contrast ratio
            required_ratio: Required minimum ratio
            standard: Accessibility standard
        """
        super().__init__(
            message=f"Insufficient contrast ratio: {ratio:.2f} < {required_ratio} ({standard})",
            code="CONTRAST_RATIO_ERROR",
            details={
                "foreground": foreground,
                "background": background,
                "ratio": ratio,
                "required_ratio": required_ratio,
                "standard": standard,
            },
            suggestion="Choose colors with higher contrast for better scanability",
        )
        self.foreground = foreground
        self.background = background
        self.ratio = ratio
        self.required_ratio = required_ratio
        self.standard = standard


class PaletteValidationError(ColorError):
    """Raised when color palette validation fails."""

    def __init__(
        self,
        message: str,
        invalid_colors: Optional[List[str]] = None,
        validation_errors: Optional[List[str]] = None,
    ):
        """Initialize palette validation error.

        Args:
            message: Error description
            invalid_colors: List of invalid colors
            validation_errors: List of validation error messages
        """
        details = {}
        if invalid_colors:
            details["invalid_colors"] = invalid_colors
        if validation_errors:
            details["validation_errors"] = validation_errors

        super().__init__(
            message=message,
            code="PALETTE_VALIDATION_ERROR",
            details=details,
        )
        self.invalid_colors = invalid_colors or []
        self.validation_errors = validation_errors or []


# Capability Errors
class CapabilityError(SegnoMMSError):
    """Base class for capability-related errors."""

    pass


class FeatureNotSupportedError(CapabilityError):
    """Raised when a feature is not supported."""

    def __init__(
        self,
        feature: str,
        category: Optional[str] = None,
        min_version: Optional[str] = None,
    ):
        """Initialize feature not supported error.

        Args:
            feature: The unsupported feature
            category: Feature category
            min_version: Minimum version required
        """
        details = {"feature": feature}
        if category:
            details["category"] = category
        if min_version:
            details["min_version"] = min_version

        suggestion = None
        if min_version:
            suggestion = f"Upgrade to version {min_version} or later"

        super().__init__(
            message=f"Feature not supported: {feature}",
            code="FEATURE_NOT_SUPPORTED",
            details=details,
            suggestion=suggestion,
        )
        self.feature = feature
        self.category = category
        self.min_version = min_version


class CapabilityManifestError(CapabilityError):
    """Raised when capability manifest has issues."""

    def __init__(self, message: str, manifest_path: Optional[str] = None):
        """Initialize capability manifest error.

        Args:
            message: Error description
            manifest_path: Path to manifest file
        """
        details = {}
        if manifest_path:
            details["manifest_path"] = manifest_path

        super().__init__(
            message=message,
            code="CAPABILITY_MANIFEST_ERROR",
            details=details,
        )
        self.manifest_path = manifest_path


# Dependency Errors
class DependencyError(SegnoMMSError):
    """Base class for dependency-related errors."""

    pass


class MissingDependencyError(DependencyError):
    """Raised when a required dependency is missing."""

    def __init__(
        self,
        dependency: str,
        feature: Optional[str] = None,
        install_command: Optional[str] = None,
    ):
        """Initialize missing dependency error.

        Args:
            dependency: Name of missing dependency
            feature: Feature that requires this dependency
            install_command: Command to install dependency
        """
        message = f"Missing required dependency: {dependency}"
        if feature:
            message += f" (required for {feature})"

        suggestion = None
        if install_command:
            suggestion = f"Install with: {install_command}"
        elif dependency.lower() in ["pyzbar", "cv2", "opencv-python"]:
            suggestion = "Install with: pip install pyzbar opencv-python"

        super().__init__(
            message=message,
            code="MISSING_DEPENDENCY",
            details={
                "dependency": dependency,
                "feature": feature,
            },
            suggestion=suggestion,
        )
        self.dependency = dependency
        self.feature = feature
        self.install_command = install_command


class OptionalFeatureUnavailableError(DependencyError):
    """Raised when an optional feature is unavailable."""

    def __init__(
        self,
        feature: str,
        reason: str,
        dependencies: Optional[List[str]] = None,
    ):
        """Initialize optional feature unavailable error.

        Args:
            feature: The unavailable feature
            reason: Why it's unavailable
            dependencies: Required dependencies
        """
        details: Dict[str, Any] = {
            "feature": feature,
            "reason": reason,
        }
        if dependencies:
            details["dependencies"] = dependencies

        suggestion = None
        if dependencies:
            suggestion = f"Install: {' '.join(dependencies)}"

        super().__init__(
            message=f"Optional feature '{feature}' is unavailable: {reason}",
            code="OPTIONAL_FEATURE_UNAVAILABLE",
            details=details,
            suggestion=suggestion,
        )
        self.feature = feature
        self.reason = reason
        self.dependencies = dependencies or []
