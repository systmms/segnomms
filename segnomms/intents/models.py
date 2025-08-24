"""Pydantic models for intent-based API.

This module defines the data models for the intent-based API, including
payload specification, intent configuration, and rendering results.
"""

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, field_validator, model_validator

# Import existing models for integration


class PayloadConfig(BaseModel):
    """Payload configuration for QR code content.

    Specifies what content should be encoded in the QR code,
    with support for different data types and encoding options.
    """

    text: Optional[str] = Field(default=None, description="Text content to encode")
    url: Optional[str] = Field(default=None, description="URL to encode")
    data: Optional[bytes] = Field(default=None, description="Binary data to encode")
    
    # Common payload types
    email: Optional[str] = Field(default=None, description="Email address to encode")
    phone: Optional[str] = Field(default=None, description="Phone number to encode")
    sms: Optional[str] = Field(default=None, description="SMS content to encode")
    wifi_ssid: Optional[str] = Field(default=None, description="WiFi SSID for network config")
    wifi_password: Optional[str] = Field(default=None, description="WiFi password for network config")

    # Advanced QR features (client requirement)
    eci: Optional[int] = Field(
        default=None, description="ECI mode for international characters"
    )
    error_correction: Optional[Literal["L", "M", "Q", "H"]] = Field(
        default=None, description="Error correction level override"
    )

    model_config = {"extra": "forbid", "validate_default": True}

    @model_validator(mode="after")
    def validate_content_specified(self) -> "PayloadConfig":
        """Ensure at least one content type is specified."""
        if not any([self.text, self.url, self.data, self.email, self.phone, self.sms, self.wifi_ssid]):
            raise ValueError("At least one content type must be specified")
        return self

    @field_validator("error_correction")
    @classmethod
    def uppercase_error_correction(cls, v: str) -> str:
        """Convert error correction to uppercase."""
        return v.upper() if v else v

    def get_content(self) -> str:
        """Get the primary content for encoding."""
        if self.text:
            return self.text
        elif self.url:
            return self.url
        elif self.email:
            return f"mailto:{self.email}"
        elif self.phone:
            return f"tel:{self.phone}"
        elif self.sms:
            return f"sms:{self.sms}"
        elif self.wifi_ssid:
            # Basic WiFi QR format
            password_part = f";P:{self.wifi_password}" if self.wifi_password else ""
            return f"WIFI:T:WPA;S:{self.wifi_ssid}{password_part};;"
        elif self.data:
            return self.data.decode("utf-8", errors="replace")
        else:
            raise ValueError("No content specified")


class StyleIntents(BaseModel):
    """Styling intent configuration."""

    module_shape: Optional[str] = Field(default=None, description="Module shape type")
    merge: Optional[str] = Field(default=None, description="Module merging strategy")
    connectivity: Optional[str] = Field(default=None, description="Connectivity mode")
    corner_radius: Optional[float] = Field(
        default=None, ge=0.0, le=1.0, description="Corner radius"
    )

    # Pattern-specific styling (client requirement)
    patterns: Optional[Dict[str, str]] = Field(
        default=None, description="Pattern-specific shapes (finder, timing, alignment)"
    )

    # Color configuration
    palette: Optional[Dict[str, str]] = Field(
        default=None, description="Color palette (fg, bg, accent)"
    )


class FrameIntents(BaseModel):
    """Frame intent configuration."""

    shape: Optional[str] = Field(default=None, description="Frame shape type")
    clip_mode: Optional[str] = Field(default=None, description="Frame clipping mode")
    corner_radius: Optional[float] = Field(
        default=None, ge=0.0, le=1.0, description="Frame corner radius"
    )
    fade_distance: Optional[int] = Field(
        default=None, ge=0, description="Fade distance for fade mode"
    )
    scale_distance: Optional[int] = Field(
        default=None, ge=0, description="Scale distance for scale mode"
    )


class ReserveIntents(BaseModel):
    """Reserve area intent configuration."""

    area_pct: Optional[float] = Field(
        default=None, ge=0.0, le=50.0, description="Reserve area percentage"
    )
    shape: Optional[str] = Field(default=None, description="Reserve area shape")
    placement: Optional[str] = Field(default=None, description="Placement mode")
    mode: Optional[Literal["knockout", "imprint"]] = Field(
        default=None, description="Reserve area mode"
    )

    # Position overrides
    offset_x: Optional[float] = Field(
        default=None, ge=-0.5, le=0.5, description="X offset"
    )
    offset_y: Optional[float] = Field(
        default=None, ge=-0.5, le=0.5, description="Y offset"
    )


class AccessibilityIntents(BaseModel):
    """Accessibility intent configuration."""

    ids: Optional[bool] = Field(default=None, description="Enable stable ID generation")
    id_prefix: Optional[str] = Field(default=None, description="ID prefix for elements")
    title: Optional[str] = Field(default=None, description="SVG title")
    desc: Optional[str] = Field(default=None, description="SVG description")
    aria: Optional[bool] = Field(default=None, description="Enable ARIA attributes")


class ValidationIntents(BaseModel):
    """Validation intent configuration."""

    enforce_scanability: Optional[bool] = Field(
        default=None, description="Enforce scanability validation"
    )
    min_contrast: Optional[float] = Field(
        default=None, ge=1.0, le=21.0, description="Minimum contrast ratio"
    )
    quiet_zone: Optional[int] = Field(default=None, ge=0, description="Quiet zone size")


class InteractivityIntents(BaseModel):
    """Interactivity intent configuration."""

    hover_effects: Optional[bool] = Field(
        default=None, description="Enable hover effects on modules"
    )
    hover_scale: Optional[float] = Field(
        default=None, ge=1.0, le=2.0, description="Hover scale factor"
    )
    hover_brightness: Optional[float] = Field(
        default=None, ge=0.5, le=2.0, description="Hover brightness adjustment"
    )
    click_handlers: Optional[bool] = Field(
        default=None, description="Enable click event handlers"
    )
    tooltips: Optional[bool] = Field(default=None, description="Enable module tooltips")
    tooltip_template: Optional[str] = Field(
        default=None, description="Tooltip content template"
    )
    cursor_style: Optional[str] = Field(
        default=None, description="Cursor style on hover"
    )


class AnimationIntents(BaseModel):
    """Animation intent configuration."""

    fade_in: Optional[bool] = Field(
        default=None, description="Enable fade-in animation"
    )
    fade_duration: Optional[float] = Field(
        default=None, ge=0.1, le=5.0, description="Fade duration in seconds"
    )
    stagger_animation: Optional[bool] = Field(
        default=None, description="Stagger module animations"
    )
    stagger_delay: Optional[float] = Field(
        default=None, ge=0.01, le=0.5, description="Delay between module animations"
    )
    pulse_effect: Optional[bool] = Field(
        default=None, description="Enable pulse effect on special patterns"
    )
    transition_timing: Optional[str] = Field(
        default=None, description="CSS transition timing function"
    )


class PerformanceIntents(BaseModel):
    """Performance optimization intent configuration."""

    optimize_for: Optional[Literal["size", "quality", "balanced"]] = Field(
        default=None, description="Optimization priority"
    )
    max_svg_size_kb: Optional[int] = Field(
        default=None, ge=1, le=1000, description="Maximum SVG file size in KB"
    )
    simplify_paths: Optional[bool] = Field(
        default=None, description="Simplify complex paths for smaller files"
    )
    inline_styles: Optional[bool] = Field(
        default=None, description="Inline CSS vs external styles"
    )
    precision: Optional[int] = Field(
        default=None, ge=0, le=6, description="Decimal precision for coordinates"
    )
    lazy_rendering: Optional[bool] = Field(
        default=None, description="Enable progressive rendering hints"
    )


class BrandingIntents(BaseModel):
    """Branding and customization intent configuration."""

    logo_url: Optional[str] = Field(
        default=None, description="Logo URL for centerpiece"
    )
    logo_padding: Optional[float] = Field(
        default=None, ge=0.0, le=0.5, description="Padding around logo"
    )
    brand_colors: Optional[Dict[str, str]] = Field(
        default=None, description="Brand color palette"
    )
    watermark: Optional[str] = Field(
        default=None, description="Watermark text or pattern"
    )
    custom_patterns: Optional[Dict[str, Dict[str, Any]]] = Field(
        default=None, description="Custom pattern definitions"
    )
    theme_preset: Optional[str] = Field(
        default=None, description="Predefined theme name"
    )


class AdvancedIntents(BaseModel):
    """Advanced intent configuration."""

    mask_pattern: Optional[int] = Field(
        default=None, ge=0, le=7, description="QR mask pattern"
    )
    structured_append: Optional[Dict[str, Any]] = Field(
        default=None, description="Structured append configuration"
    )
    micro_qr: Optional[bool] = Field(
        default=None, description="Use Micro QR format if possible"
    )
    force_version: Optional[int] = Field(
        default=None, ge=1, le=40, description="Force specific QR version"
    )
    boost_ecc: Optional[bool] = Field(
        default=None, description="Boost error correction for damaged codes"
    )


class IntentsConfig(BaseModel):
    """Complete intent configuration.

    Structured intent specification that gets processed with graceful
    degradation. Unknown keys are ignored, unsupported values generate
    warnings and fall back to safe defaults.
    """

    style: Optional[StyleIntents] = Field(default=None, description="Styling intents")
    frame: Optional[FrameIntents] = Field(default=None, description="Frame intents")
    reserve: Optional[ReserveIntents] = Field(
        default=None, description="Reserve area intents"
    )
    accessibility: Optional[AccessibilityIntents] = Field(
        default=None, description="Accessibility intents"
    )
    validation: Optional[ValidationIntents] = Field(
        default=None, description="Validation intents"
    )
    interactivity: Optional[InteractivityIntents] = Field(
        default=None, description="Interactivity intents"
    )
    animation: Optional[AnimationIntents] = Field(
        default=None, description="Animation intents"
    )
    performance: Optional[PerformanceIntents] = Field(
        default=None, description="Performance optimization intents"
    )
    branding: Optional[BrandingIntents] = Field(
        default=None, description="Branding and customization intents"
    )
    advanced: Optional[AdvancedIntents] = Field(
        default=None, description="Advanced intents"
    )

    model_config = {"extra": "ignore", "validate_default": True}  # Ignore unknown keys


class TransformationStep(BaseModel):
    """Single transformation step in intent processing."""

    intent_path: str = Field(description="Path to the intent being transformed")
    original_value: Any = Field(description="Original intent value")
    transformed_value: Any = Field(description="Transformed/degraded value")
    transformation_type: Literal["accepted", "degraded", "rejected", "modified"] = (
        Field(description="Type of transformation applied")
    )
    reason: Optional[str] = Field(default=None, description="Reason for transformation")
    confidence: Optional[float] = Field(
        default=None, ge=0.0, le=1.0, description="Confidence in transformation"
    )

    model_config = {"frozen": True}


class DegradationDetail(BaseModel):
    """Detailed information about intent degradation."""

    intent_path: str = Field(description="Path to degraded intent")
    requested_feature: str = Field(description="Feature that was requested")
    applied_feature: Optional[str] = Field(
        default=None, description="Feature that was applied instead"
    )
    degradation_reason: str = Field(description="Why degradation was necessary")
    alternatives: List[str] = Field(
        default_factory=list, description="Alternative approaches available"
    )
    impact_level: Literal["minor", "moderate", "major"] = Field(
        description="Impact level of the degradation"
    )

    model_config = {"frozen": True}


class CompatibilityInfo(BaseModel):
    """Compatibility information for an intent."""

    intent_path: str = Field(description="Path to the intent")
    support_level: Literal["full", "partial", "unsupported", "experimental"] = Field(
        description="Current support level"
    )
    available_since: Optional[str] = Field(
        default=None, description="Version when feature became available"
    )
    planned_support: Optional[str] = Field(
        default=None, description="When full support is planned"
    )
    workarounds: List[str] = Field(
        default_factory=list, description="Available workarounds"
    )

    model_config = {"frozen": True}


class WarningInfo(BaseModel):
    """Structured warning information."""

    code: str = Field(description="Stable warning code")
    path: Optional[str] = Field(
        default=None, description="JSON path to problematic intent"
    )
    detail: str = Field(description="Human-readable warning message")
    suggestion: Optional[str] = Field(
        default=None, description="Suggested fix or alternative"
    )
    severity: Optional[Literal["info", "warning", "error"]] = Field(
        default="warning", description="Warning severity level"
    )

    model_config = {"frozen": True}


class PerformanceMetrics(BaseModel):
    """Performance metrics for rendering operation."""

    rendering_time_ms: Optional[float] = Field(
        default=None, description="Total rendering time"
    )
    validation_time_ms: Optional[float] = Field(
        default=None, description="Validation time"
    )
    svg_generation_time_ms: Optional[float] = Field(
        default=None, description="SVG generation time"
    )

    estimated_scanability: Optional[str] = Field(
        default=None, description="Scanability assessment"
    )
    min_module_px: Optional[int] = Field(
        default=None, description="Minimum module size in pixels"
    )
    contrast_ratio: Optional[float] = Field(
        default=None, description="Actual contrast ratio"
    )
    actual_quiet_zone: Optional[int] = Field(
        default=None, description="Actual quiet zone size"
    )

    model_config = {"frozen": True}


class IntentTranslationReport(BaseModel):
    """Detailed report of how intents were translated."""

    transformation_steps: List[TransformationStep] = Field(
        default_factory=list, description="All transformation steps applied"
    )
    degradation_details: List[DegradationDetail] = Field(
        default_factory=list, description="Details of all degradations"
    )
    compatibility_info: List[CompatibilityInfo] = Field(
        default_factory=list, description="Compatibility information for intents"
    )
    intent_summary: Dict[str, str] = Field(
        default_factory=dict, description="Summary of intent processing"
    )

    model_config = {"frozen": True}


class RenderingResult(BaseModel):
    """Comprehensive rendering result.

    Complete result from intent-based rendering including SVG output,
    warnings, performance metrics, and tracking of used vs. requested options.
    """

    svg_content: str = Field(description="Generated SVG content")
    warnings: List[WarningInfo] = Field(
        default_factory=list, description="Warnings generated during processing"
    )
    metrics: PerformanceMetrics = Field(description="Performance and quality metrics")
    used_options: Dict[str, Any] = Field(
        description="Actually used configuration options"
    )

    # Client requirement fields
    degradation_applied: bool = Field(
        default=False, description="Whether graceful degradation was applied"
    )
    unsupported_intents: List[str] = Field(
        default_factory=list, description="List of unsupported intent paths"
    )

    # Enhanced feedback fields
    translation_report: Optional[IntentTranslationReport] = Field(
        default=None, description="Detailed intent translation report"
    )
    requested_options: Optional[Dict[str, Any]] = Field(
        default=None, description="Originally requested options for comparison"
    )
    feature_impact: Optional[Dict[str, str]] = Field(
        default=None, description="Performance/quality impact of features"
    )
    scanability_prediction: Optional[str] = Field(
        default=None, description="Predicted scanability level"
    )

    model_config = {"frozen": True}

    @property
    def has_warnings(self) -> bool:
        """Check if any warnings were generated."""
        return len(self.warnings) > 0

    @property
    def warning_count(self) -> int:
        """Get total warning count."""
        return len(self.warnings)

    def get_warnings_by_code(self, code: str) -> List[WarningInfo]:
        """Get warnings filtered by code."""
        return [w for w in self.warnings if w.code == code]

    def to_client_format(self) -> Dict[str, Any]:
        """Convert to client-expected format.

        Returns result in the format specified by client requirements:
        {
            "svg": "<svg ...>...</svg>",
            "warnings": [...],
            "metrics": {...},
            "usedOptions": {...}
        }
        """
        return {
            "svg": self.svg_content,
            "warnings": [
                {
                    "code": w.code,
                    "path": w.path,
                    "detail": w.detail,
                    "suggestion": w.suggestion,
                }
                for w in self.warnings
            ],
            "metrics": self.metrics.model_dump(exclude_none=True),
            "usedOptions": self.used_options,
        }
