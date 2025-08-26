"""Pydantic models for utility components.

This module provides data models for utility classes using Pydantic
for automatic validation and type safety.
"""

from typing import Any, Dict, List, Literal, Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationInfo,
    field_validator,
    model_validator,
)


class SVGElementConfig(BaseModel):
    """Configuration for SVG root element creation.

    This model validates parameters for creating SVG root elements
    with proper dimensions, viewBox, and attributes.

    Example:
        >>> config = SVGElementConfig(
        ...     width=200,
        ...     height=200,
        ...     id="my-qr-code",
        ...     css_class="qr-svg"
        ... )
        >>> svg = builder.create_svg_root(**config.model_dump())
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    width: int = Field(..., gt=0, le=10000, description="SVG width in pixels")

    height: int = Field(..., gt=0, le=10000, description="SVG height in pixels")

    id: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        pattern=r"^[a-zA-Z][a-zA-Z0-9\-_]*$",
        description="SVG element ID (must start with letter)",
    )

    css_class: Optional[str] = Field(
        None, alias="class", min_length=1, max_length=200, description="CSS class names"
    )

    @model_validator(mode="before")
    @classmethod
    def handle_css_class_aliases(cls, values: Any) -> Any:
        """Handle both 'css_class' and 'class' parameter names."""
        if isinstance(values, dict):
            # If both css_class and class are provided, class takes precedence
            if "css_class" in values and "class" not in values:
                values["class"] = values.pop("css_class")
        return values

    @field_validator("width", "height")
    @classmethod
    def validate_dimensions(cls, v: int) -> int:
        """Validate reasonable SVG dimensions."""
        if v > 5000:
            # Allow but warn about very large SVGs
            pass
        return v


class BackgroundConfig(BaseModel):
    """Configuration for SVG background elements.

    This model validates parameters for adding background rectangles
    to SVG documents.
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    width: int = Field(..., gt=0, description="Background width in pixels")

    height: int = Field(..., gt=0, description="Background height in pixels")

    color: str = Field(..., min_length=1, description="CSS color string")

    @field_validator("color")
    @classmethod
    def validate_color(cls, v: str) -> str:
        """Basic validation for CSS color values."""
        # Allow common CSS color formats
        v = v.strip()
        if not v:
            raise ValueError("Color cannot be empty")

        # Basic patterns for common color formats
        import re

        patterns = [
            r"^#[0-9a-fA-F]{3}$",  # #RGB
            r"^#[0-9a-fA-F]{6}$",  # #RRGGBB
            r"^#[0-9a-fA-F]{8}$",  # #RRGGBBAA
            r"^rgb\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*\)$",  # rgb(r,g,b)
            r"^rgba\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*,\s*[\d.]+\s*\)$",  # rgba(r,g,b,a)
            r"^hsl\(\s*\d+\s*,\s*\d+%\s*,\s*\d+%\s*\)$",  # hsl(h,s,l)
            r"^hsla\(\s*\d+\s*,\s*\d+%\s*,\s*\d+%\s*,\s*[\d.]+\s*\)$",  # hsla(h,s,l,a)
        ]

        # Check common color names
        common_colors = {
            "black",
            "white",
            "red",
            "green",
            "blue",
            "yellow",
            "cyan",
            "magenta",
            "orange",
            "purple",
            "pink",
            "brown",
            "gray",
            "grey",
            "transparent",
            "inherit",
            "currentColor",
        }

        if v.lower() in common_colors or any(
            re.match(pattern, v) for pattern in patterns
        ):
            return v

        # Allow other values but don't validate strictly
        return v


class GradientConfig(BaseModel):
    """Configuration for SVG gradient definitions.

    This model validates gradient parameters for creating
    linear and radial gradients in SVG definitions.
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    gradient_id: str = Field(
        ...,
        min_length=1,
        max_length=50,
        pattern=r"^[a-zA-Z][a-zA-Z0-9\-_]*$",
        description="Unique gradient ID",
    )

    gradient_type: Literal["linear", "radial"] = Field(
        ..., description="Type of gradient"
    )

    colors: List[str] = Field(
        ...,
        min_length=2,
        max_length=10,
        description="List of colors for gradient stops",
    )

    stops: Optional[List[float]] = Field(
        None, description="Optional gradient stop positions (0.0-1.0)"
    )

    x1: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Linear gradient start X"
    )
    y1: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Linear gradient start Y"
    )
    x2: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Linear gradient end X"
    )
    y2: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Linear gradient end Y"
    )

    cx: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Radial gradient center X"
    )
    cy: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Radial gradient center Y"
    )
    r: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Radial gradient radius"
    )

    @field_validator("stops")
    @classmethod
    def validate_stops(
        cls, v: Optional[List[float]], info: ValidationInfo
    ) -> Optional[List[float]]:
        """Validate gradient stops match color count."""
        if v is not None and "colors" in info.data:
            if len(v) != len(info.data["colors"]):
                raise ValueError("Number of stops must match number of colors")

            # Check stops are in ascending order
            for i in range(1, len(v)):
                if v[i] < v[i - 1]:
                    raise ValueError("Gradient stops must be in ascending order")

        return v


class TitleDescriptionConfig(BaseModel):
    """Configuration for SVG title and description elements.

    This model validates accessibility metadata for SVG documents.
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(
        ..., min_length=1, max_length=100, description="SVG title for accessibility"
    )

    description: Optional[str] = Field(
        None, max_length=500, description="Optional detailed description"
    )


class InteractionConfig(BaseModel):
    """Configuration for SVG interactivity features.

    This model validates parameters for enabling interactive
    features like hover effects and tooltips.
    """

    model_config = ConfigDict(validate_default=True)

    interactive: bool = Field(
        default=False, description="Enable interactive hover effects"
    )

    tooltips: bool = Field(default=False, description="Enable tooltip display on hover")

    hover_effects: bool = Field(default=False, description="Enable CSS hover effects")

    click_handlers: bool = Field(
        default=False, description="Enable JavaScript click handlers"
    )


class FrameDefinitionConfig(BaseModel):
    """Configuration for SVG frame shape definitions.

    This model validates parameters for creating frame shapes
    in SVG definition sections.
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    frame_shape: Literal["square", "circle", "rounded-rect", "squircle", "custom"] = (
        Field(..., description="Type of frame shape")
    )

    width: int = Field(..., gt=0, description="Frame width in pixels")

    height: int = Field(..., gt=0, description="Frame height in pixels")

    border_pixels: int = Field(..., ge=0, description="Border size in pixels")

    corner_radius: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Corner radius for rounded frames"
    )

    custom_path: Optional[str] = Field(
        None, min_length=1, description="SVG path string for custom frames"
    )


class LayerStructureConfig(BaseModel):
    """Configuration for SVG layer organization.

    This model defines the structure of layered SVG elements
    for proper rendering order and organization.
    """

    model_config = ConfigDict(frozen=True)

    background_layer: bool = Field(default=True, description="Include background layer")

    quiet_zone_layer: bool = Field(default=True, description="Include quiet zone layer")

    frame_layer: bool = Field(default=True, description="Include frame layer")

    modules_layer: bool = Field(default=True, description="Include modules layer")

    centerpiece_layer: bool = Field(
        default=True, description="Include centerpiece layer"
    )

    overlay_layer: bool = Field(
        default=False, description="Include overlay layer for additional elements"
    )

    @property
    def layer_names(self) -> List[str]:
        """Get ordered list of enabled layer names."""
        layers = []
        if self.background_layer:
            layers.append("background")
        if self.quiet_zone_layer:
            layers.append("quiet-zone")
        if self.frame_layer:
            layers.append("frame")
        if self.modules_layer:
            layers.append("modules")
        if self.centerpiece_layer:
            layers.append("centerpiece")
        if self.overlay_layer:
            layers.append("overlay")
        return layers


class CenterpieceMetadataConfig(BaseModel):
    """Configuration for centerpiece metadata in SVG.

    This model validates parameters for adding centerpiece
    positioning metadata to SVG documents.
    """

    model_config = ConfigDict(frozen=True)

    x: float = Field(..., description="Centerpiece X position")
    y: float = Field(..., description="Centerpiece Y position")
    width: float = Field(..., gt=0, description="Centerpiece width")
    height: float = Field(..., gt=0, description="Centerpiece height")
    scale: int = Field(..., gt=0, description="Module scale factor")
    border: int = Field(..., ge=0, description="Border size in modules")

    @property
    def bounds_dict(self) -> Dict[str, float]:
        """Get bounds as dictionary."""
        return {"x": self.x, "y": self.y, "width": self.width, "height": self.height}
