"""Visual and style-related configuration models.

This module contains configuration classes for visual styling, frames,
centerpieces, quiet zones, and pattern-specific styling.
"""

from typing import Any, Dict, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from typing_extensions import Self

from ..enums import PlacementMode, ReserveMode


class PatternStyleConfig(BaseModel):
    """Pattern-specific styling configuration.

    Allows different shapes and styles for specific QR code patterns
    (finder, timing, alignment, etc.) independent of data modules.

    Attributes:
        enabled: Whether to enable pattern-specific styling
        finder: Custom styling for finder patterns (corners)
        timing: Custom styling for timing patterns (grid lines)
        alignment: Custom styling for alignment patterns
        format: Custom styling for format information modules
        version: Custom styling for version information modules
        data: Custom styling for data modules (can override global setting)
    """

    model_config = ConfigDict(validate_default=True, extra="forbid")

    enabled: bool = Field(default=False, description="Enable pattern-specific styling")

    # Pattern-specific shape overrides
    finder: Optional[str] = Field(default=None, description="Custom shape for finder patterns")
    finder_inner: Optional[str] = Field(default=None, description="Custom shape for finder inner regions")
    timing: Optional[str] = Field(default=None, description="Custom shape for timing patterns")
    alignment: Optional[str] = Field(default=None, description="Custom shape for alignment patterns")
    format: Optional[str] = Field(default=None, description="Custom shape for format information")
    version: Optional[str] = Field(default=None, description="Custom shape for version information")
    data: Optional[str] = Field(default=None, description="Custom shape for data modules")

    # Pattern-specific colors
    finder_color: Optional[str] = Field(default=None, description="Custom color for finder patterns")
    finder_inner_color: Optional[str] = Field(
        default=None, description="Custom color for finder inner regions"
    )
    timing_color: Optional[str] = Field(default=None, description="Custom color for timing patterns")
    alignment_color: Optional[str] = Field(default=None, description="Custom color for alignment patterns")
    format_color: Optional[str] = Field(default=None, description="Custom color for format information")
    version_color: Optional[str] = Field(default=None, description="Custom color for version information")
    data_color: Optional[str] = Field(default=None, description="Custom color for data modules")

    # Pattern-specific sizing/effects
    finder_scale: Optional[float] = Field(
        default=None, ge=0.1, le=2.0, description="Scale factor for finder patterns"
    )
    timing_scale: Optional[float] = Field(
        default=None, ge=0.1, le=2.0, description="Scale factor for timing patterns"
    )
    alignment_scale: Optional[float] = Field(
        default=None, ge=0.1, le=2.0, description="Scale factor for alignment patterns"
    )

    # Advanced pattern effects
    finder_effects: Optional[Dict[str, Any]] = Field(
        default=None, description="Custom effects for finder patterns"
    )
    timing_effects: Optional[Dict[str, Any]] = Field(
        default=None, description="Custom effects for timing patterns"
    )
    alignment_effects: Optional[Dict[str, Any]] = Field(
        default=None, description="Custom effects for alignment patterns"
    )

    @model_validator(mode="after")
    def validate_enabled_patterns(self) -> Self:
        """Validate that at least one pattern override is specified when enabled."""
        if self.enabled:
            pattern_overrides = [
                # Shape overrides
                self.finder,
                self.finder_inner,
                self.timing,
                self.alignment,
                self.format,
                self.version,
                self.data,
                # Color overrides
                self.finder_color,
                self.finder_inner_color,
                self.timing_color,
                self.alignment_color,
                self.format_color,
                self.version_color,
                self.data_color,
                # Scale overrides
                self.finder_scale,
                self.timing_scale,
                self.alignment_scale,
                # Effects overrides
                self.finder_effects,
                self.timing_effects,
                self.alignment_effects,
            ]
            if not any(override is not None for override in pattern_overrides):
                raise ValueError(
                    "At least one pattern override must be specified when pattern styling is enabled"
                )
        return self

    @model_validator(mode="after")
    def validate_pattern_shapes(self) -> Self:
        """Validate that pattern shapes are valid shape types."""
        # List of valid shapes (could be imported from shapes module in production)
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

        # Check each pattern shape
        shape_fields = [
            ("finder", self.finder),
            ("finder_inner", self.finder_inner),
            ("timing", self.timing),
            ("alignment", self.alignment),
            ("format", self.format),
            ("version", self.version),
            ("data", self.data),
        ]

        for field_name, shape_value in shape_fields:
            if shape_value is not None and shape_value not in valid_shapes:
                raise ValueError(
                    f"Invalid shape '{shape_value}' for {field_name}. "
                    f"Valid shapes are: {', '.join(valid_shapes)}"
                )

        return self


class FrameConfig(BaseModel):
    """Frame shape configuration for QR codes.

    Attributes:
        shape: Frame shape type ('square', 'circle', 'rounded-rect', 'squircle', 'custom')
        corner_radius: Corner radius for rounded-rect (0.0-1.0)
        clip_mode: How to apply frame ('clip' for hard edge, 'fade' for gradient)
        custom_path: SVG path string for custom frame shapes
    """

    model_config = ConfigDict(validate_default=True, extra="forbid")

    shape: Literal["square", "circle", "rounded-rect", "squircle", "custom"] = "square"
    corner_radius: float = Field(default=0.0, ge=0.0, le=1.0, description="Corner radius for rounded-rect")
    clip_mode: Literal["clip", "fade", "scale"] = "clip"
    custom_path: Optional[str] = Field(default=None, description="SVG path string for custom frame shapes")

    # Clip mode parameters
    fade_distance: float = Field(
        default=10.0,
        ge=0.0,
        le=50.0,
        description="Distance in pixels for fade transition",
    )
    scale_distance: float = Field(
        default=5.0,
        ge=0.0,
        le=25.0,
        description="Distance in modules for scale transition",
    )

    @model_validator(mode="after")
    def validate_custom_path(self) -> Self:
        """Validate that custom_path is provided for custom frame shapes."""
        if self.shape == "custom" and not self.custom_path:
            raise ValueError("custom_path required for custom frame shape")
        return self


class CenterpieceConfig(BaseModel):
    """Centerpiece reserve area configuration.

    Attributes:
        enabled: Whether to reserve center area
        shape: Shape of reserved area ('rect', 'circle', 'squircle')
        size: Size relative to QR code (0.0-0.5)
        offset_x: Horizontal offset (-0.5 to 0.5) - used when placement is 'custom'
        offset_y: Vertical offset (-0.5 to 0.5) - used when placement is 'custom'
        margin: Module margin around reserved area
        mode: Reserve area interaction mode (knockout or imprint)
        placement: Placement mode for positioning (custom, center, corners, edges)
    """

    model_config = ConfigDict(validate_default=True, extra="forbid")

    enabled: bool = False
    shape: Literal["rect", "circle", "squircle"] = "rect"
    size: float = Field(default=0.0, ge=0.0, le=0.5, description="Size relative to QR code")
    offset_x: float = Field(
        default=0.0,
        ge=-0.5,
        le=0.5,
        description="Horizontal offset (custom placement only)",
    )
    offset_y: float = Field(
        default=0.0,
        ge=-0.5,
        le=0.5,
        description="Vertical offset (custom placement only)",
    )
    margin: int = Field(default=2, ge=0, description="Module margin around reserved area")
    mode: ReserveMode = Field(default=ReserveMode.KNOCKOUT, description="Reserve area interaction mode")
    placement: PlacementMode = Field(
        default=PlacementMode.CENTER, description="Placement mode for positioning"
    )

    @model_validator(mode="after")
    def validate_enabled_fields(self) -> Self:
        """Additional validation when centerpiece is enabled."""
        if self.enabled and self.size == 0.0:
            raise ValueError("centerpiece size must be > 0 when enabled")
        return self


class QuietZoneConfig(BaseModel):
    """Quiet zone styling configuration.

    Attributes:
        color: Fill color for quiet zone
        style: Style type ('solid', 'gradient', 'none')
        gradient: Gradient definition for style='gradient'
    """

    model_config = ConfigDict(validate_default=True, extra="forbid")

    color: str = Field(default="#ffffff", description="Fill color for quiet zone")
    style: Literal["solid", "gradient", "none"] = "solid"
    gradient: Optional[Dict[str, Any]] = Field(
        default=None, description="Gradient definition for style='gradient'"
    )

    @model_validator(mode="after")
    def validate_gradient_required(self) -> Self:
        """Validate that gradient is provided for gradient style."""
        if self.style == "gradient" and not self.gradient:
            raise ValueError("gradient definition required for gradient style")
        return self


class StyleConfig(BaseModel):
    """General styling configuration.

    Controls CSS classes, interactive features, tooltips, and other visual styling.

    Attributes:
        interactive: Enable interactive hover effects
        tooltips: Show tooltips on module hover
        css_classes: Custom CSS classes for different QR elements
    """

    model_config = ConfigDict(validate_default=True, extra="forbid")

    interactive: bool = Field(default=False, description="Enable interactive hover effects")
    tooltips: bool = Field(default=False, description="Show tooltips on module hover")
    css_classes: Optional[Dict[str, str]] = Field(
        default=None, description="Custom CSS classes for different QR elements"
    )

    @field_validator("css_classes")
    @classmethod
    def validate_css_classes(cls, v: Optional[Dict[str, str]]) -> Optional[Dict[str, str]]:
        """Validate CSS class names."""
        if v is not None:
            # Valid keys with qr_ prefix (new format)
            prefixed_keys = [
                "qr_module",
                "qr_finder",
                "qr_finder_inner",
                "qr_timing",
                "qr_alignment",
                "qr_alignment_center",
                "qr_format",
                "qr_version",
                "qr_data",
                "qr_cluster",
            ]
            # Valid keys without prefix (legacy format for backward compatibility)
            unprefixed_keys = [
                "module",
                "finder",
                "finder_inner",
                "timing",
                "alignment",
                "alignment_center",
                "format",
                "version",
                "data",
                "cluster",
            ]
            valid_keys = prefixed_keys + unprefixed_keys

            for key in v.keys():
                if key not in valid_keys:
                    raise ValueError(f"Invalid CSS class key '{key}'. Valid keys: {', '.join(valid_keys)}")
        return v
