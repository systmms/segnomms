"""
Enhanced palette support for SegnoMMS.

This module provides comprehensive color palette management, validation,
and analysis capabilities for QR code generation.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from pydantic import BaseModel, ConfigDict, Field, field_validator

from ..exceptions import (
    ContrastRatioError,
    InvalidColorFormatError,
    PaletteValidationError,
)
from .color_analysis import calculate_contrast_ratio, calculate_luminance, parse_color


class ColorSpace(str, Enum):
    """Supported color spaces for palette validation."""

    SRGB = "sRGB"
    DISPLAY_P3 = "Display-P3"
    REC2020 = "Rec.2020"


class ContrastStandard(str, Enum):
    """WCAG contrast standards."""

    AA_NORMAL = "AA-normal"  # 4.5:1
    AA_LARGE = "AA-large"  # 3:1
    AAA_NORMAL = "AAA-normal"  # 7:1
    AAA_LARGE = "AAA-large"  # 4.5:1
    QR_OPTIMAL = "QR-optimal"  # 8:1 (recommended for QR codes)


class PaletteType(str, Enum):
    """Types of color palettes."""

    MONOCHROME = "monochrome"
    COMPLEMENTARY = "complementary"
    ANALOGOUS = "analogous"
    TRIADIC = "triadic"
    CUSTOM = "custom"


@dataclass
class ColorInfo:
    """Information about a parsed color."""

    original: str
    rgb: Tuple[int, int, int]
    hex: str
    luminance: float
    is_dark: bool

    @classmethod
    def from_string(cls, color_str: str) -> Optional["ColorInfo"]:
        """Create ColorInfo from a color string."""
        rgb = parse_color(color_str)
        if rgb is None:
            return None

        luminance = calculate_luminance(rgb)
        hex_color = f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
        is_dark = luminance < 0.18  # More accurate threshold for dark colors

        return cls(
            original=color_str,
            rgb=rgb,
            hex=hex_color,
            luminance=luminance,
            is_dark=is_dark,
        )


@dataclass
class ContrastAnalysis:
    """Analysis of contrast between two colors."""

    ratio: float
    meets_aa_normal: bool
    meets_aa_large: bool
    meets_aaa_normal: bool
    meets_aaa_large: bool
    meets_qr_optimal: bool
    grade: str  # "AAA", "AA", "FAIL"

    @classmethod
    def analyze(cls, color1: str, color2: str) -> Optional["ContrastAnalysis"]:
        """Analyze contrast between two colors."""
        ratio = calculate_contrast_ratio(color1, color2)
        if ratio is None:
            return None

        meets_aa_normal = ratio >= 4.5
        meets_aa_large = ratio >= 3.0
        meets_aaa_normal = ratio >= 7.0
        meets_aaa_large = ratio >= 4.5
        meets_qr_optimal = ratio >= 8.0

        if meets_aaa_normal:
            grade = "AAA"
        elif meets_aa_normal:
            grade = "AA"
        else:
            grade = "FAIL"

        return cls(
            ratio=ratio,
            meets_aa_normal=meets_aa_normal,
            meets_aa_large=meets_aa_large,
            meets_aaa_normal=meets_aaa_normal,
            meets_aaa_large=meets_aaa_large,
            meets_qr_optimal=meets_qr_optimal,
            grade=grade,
        )


class PaletteConfig(BaseModel):
    """Enhanced palette configuration."""

    model_config = ConfigDict(validate_default=True, extra="forbid")

    # Core colors
    dark: str = Field(default="black", description="Primary dark color")
    light: str = Field(default="white", description="Primary light color")

    # Optional accent colors
    accent_colors: List[str] = Field(
        default_factory=list, description="Additional accent colors for pattern styling"
    )

    # Palette settings
    palette_type: PaletteType = Field(
        default=PaletteType.CUSTOM, description="Type of color palette"
    )

    min_contrast_ratio: float = Field(
        default=4.5, ge=1.0, le=21.0, description="Minimum required contrast ratio"
    )

    color_space: ColorSpace = Field(
        default=ColorSpace.SRGB, description="Target color space"
    )

    enforce_standards: bool = Field(
        default=True, description="Enforce WCAG contrast standards"
    )

    # Validation settings
    validate_accessibility: bool = Field(
        default=True, description="Validate colors for accessibility"
    )

    allow_similar_colors: bool = Field(
        default=False, description="Allow colors that are too similar"
    )

    max_colors: int = Field(
        default=10, ge=2, le=50, description="Maximum number of colors in palette"
    )

    @field_validator("dark", "light")
    @classmethod
    def validate_color_format(cls, v: str) -> str:
        """Validate that color can be parsed."""
        if not v:
            raise InvalidColorFormatError(
                color="",
                accepted_formats=["hex (#RRGGBB)", "rgb(r,g,b)", "named colors"],
            )

        rgb = parse_color(v)
        if rgb is None:
            raise InvalidColorFormatError(
                color=v,
                accepted_formats=["hex (#RRGGBB)", "rgb(r,g,b)", "named colors"],
            )

        return v

    @field_validator("accent_colors")
    @classmethod
    def validate_accent_colors(cls, v: List[str]) -> List[str]:
        """Validate accent colors."""
        invalid_colors = []
        for color in v:
            rgb = parse_color(color)
            if rgb is None:
                invalid_colors.append(color)

        if invalid_colors:
            raise PaletteValidationError(
                message=f"Invalid accent color format(s): {', '.join(invalid_colors)}",
                invalid_colors=invalid_colors,
                validation_errors=[
                    f"Cannot parse color: {color}" for color in invalid_colors
                ],
            )

        return v

    def get_primary_contrast(self) -> Optional[ContrastAnalysis]:
        """Get contrast analysis for primary dark/light colors."""
        return ContrastAnalysis.analyze(self.dark, self.light)

    def get_all_colors(self) -> List[str]:
        """Get all colors in the palette."""
        colors = [self.dark, self.light]
        colors.extend(self.accent_colors)
        return colors

    def validate_palette(self) -> "PaletteValidationResult":
        """Validate the entire palette."""
        return validate_palette(self)


class PaletteValidationResult(BaseModel):
    """Result of palette validation."""

    model_config = ConfigDict(validate_default=True, extra="forbid")

    is_valid: bool = Field(description="Whether palette passes validation")

    primary_contrast: Optional[ContrastAnalysis] = Field(
        default=None, description="Contrast analysis for primary colors"
    )

    issues: List[str] = Field(
        default_factory=list, description="List of validation issues"
    )

    warnings: List[str] = Field(
        default_factory=list, description="List of validation warnings"
    )

    suggestions: List[str] = Field(
        default_factory=list, description="Suggestions for improvement"
    )

    color_info: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict, description="Detailed information about each color"
    )

    contrast_matrix: Dict[str, Dict[str, float]] = Field(
        default_factory=dict, description="Contrast ratios between all color pairs"
    )


def validate_palette(palette: PaletteConfig) -> PaletteValidationResult:
    """
    Comprehensive palette validation.

    Args:
        palette: Palette configuration to validate

    Returns:
        Detailed validation result
    """
    issues: List[str] = []
    warnings: List[str] = []
    suggestions: List[str] = []
    color_info: Dict[str, Dict[str, Any]] = {}
    contrast_matrix: Dict[str, Dict[str, float]] = {}

    all_colors = palette.get_all_colors()

    # Validate individual colors
    parsed_colors = {}
    for color in all_colors:
        info = ColorInfo.from_string(color)
        if info is None:
            issues.append(f"Cannot parse color: {color}")
            continue

        parsed_colors[color] = info
        color_info[color] = {
            "rgb": info.rgb,
            "hex": info.hex,
            "luminance": info.luminance,
            "is_dark": info.is_dark,
        }

    # Check if we have too few colors
    if len(parsed_colors) < 2:
        issues.append("Palette must have at least 2 valid colors")
        return PaletteValidationResult(
            is_valid=False,
            issues=issues,
            warnings=warnings,
            suggestions=suggestions,
            color_info=color_info,
            contrast_matrix=contrast_matrix,
        )

    # Analyze primary contrast
    primary_contrast = ContrastAnalysis.analyze(palette.dark, palette.light)

    if primary_contrast:
        if primary_contrast.ratio < palette.min_contrast_ratio:
            issues.append(
                f"Primary contrast ratio {primary_contrast.ratio:.2f} is below "
                f"minimum requirement {palette.min_contrast_ratio:.2f}"
            )

        if palette.enforce_standards:
            if not primary_contrast.meets_aa_normal:
                issues.append("Primary colors do not meet WCAG AA standards (4.5:1)")
            elif not primary_contrast.meets_qr_optimal:
                warnings.append("Primary colors do not meet optimal QR contrast (8:1)")
                suggestions.append(
                    "Consider using higher contrast colors for better scanability"
                )

    # Build contrast matrix for all color pairs
    for i, color1 in enumerate(all_colors):
        if color1 not in contrast_matrix:
            contrast_matrix[color1] = {}

        for j, color2 in enumerate(all_colors):
            if i != j:
                ratio = calculate_contrast_ratio(color1, color2)
                if ratio is not None:
                    contrast_matrix[color1][color2] = ratio

    # Check for similar colors
    if not palette.allow_similar_colors:
        similar_pairs = []
        for color1 in all_colors:
            for color2 in all_colors:
                if (
                    color1 != color2
                    and color1 in contrast_matrix
                    and color2 in contrast_matrix[color1]
                ):
                    ratio = contrast_matrix[color1][color2]
                    if ratio is not None and ratio < 2.0:  # Very similar colors
                        pair = tuple(sorted([color1, color2]))
                        if pair not in similar_pairs:
                            similar_pairs.append(pair)
                            warnings.append(
                                f"Colors '{color1}' and '{color2}' are very similar "
                                f"(ratio: {ratio:.2f})"
                            )

    # Check palette size
    if len(all_colors) > palette.max_colors:
        issues.append(
            f"Palette has {len(all_colors)} colors, maximum is {palette.max_colors}"
        )

    # Color distribution analysis
    dark_colors = [c for c, info in parsed_colors.items() if info.is_dark]
    light_colors = [c for c, info in parsed_colors.items() if not info.is_dark]

    if len(dark_colors) == 0:
        warnings.append("Palette has no dark colors")
        suggestions.append("Add at least one dark color for better contrast")

    if len(light_colors) == 0:
        warnings.append("Palette has no light colors")
        suggestions.append("Add at least one light color for better contrast")

    # Accessibility recommendations
    if palette.validate_accessibility and primary_contrast:
        if primary_contrast.meets_aaa_normal:
            suggestions.append("Excellent contrast! Colors meet AAA standards")
        elif primary_contrast.meets_aa_normal:
            suggestions.append("Good contrast, meets AA standards")

    # Final validation
    result = PaletteValidationResult(
        is_valid=len(issues) == 0,
        primary_contrast=primary_contrast,
        issues=issues,
        warnings=warnings,
        suggestions=suggestions,
        color_info=color_info,
        contrast_matrix=contrast_matrix,
    )

    return result


def generate_palette_suggestions(
    base_color: str, palette_type: PaletteType = PaletteType.COMPLEMENTARY
) -> List[str]:
    """
    Generate palette suggestions based on a base color.

    Args:
        base_color: Base color to build palette around
        palette_type: Type of palette to generate

    Returns:
        List of suggested colors
    """
    suggestions: List[str] = []

    info = ColorInfo.from_string(base_color)
    if info is None:
        return suggestions

    r, g, b = info.rgb

    if palette_type == PaletteType.MONOCHROME:
        # Generate monochrome variations
        suggestions.extend(
            [
                f"rgb({r//4}, {g//4}, {b//4})",  # Darker
                f"rgb({min(255, r*2)}, {min(255, g*2)}, {min(255, b*2)})",  # Lighter
                "white" if info.is_dark else "black",  # Opposite
            ]
        )

    elif palette_type == PaletteType.COMPLEMENTARY:
        # Generate complementary color (opposite on color wheel)
        comp_r = 255 - r
        comp_g = 255 - g
        comp_b = 255 - b
        suggestions.append(f"rgb({comp_r}, {comp_g}, {comp_b})")
        suggestions.append("white" if info.is_dark else "black")

    elif palette_type == PaletteType.ANALOGOUS:
        # Generate analogous colors (adjacent on color wheel)
        # Simplified approach - shift hue
        suggestions.extend(
            [
                f"rgb({g}, {b}, {r})",  # Rotate RGB
                f"rgb({b}, {r}, {g})",  # Rotate RGB
                "white" if info.is_dark else "black",
            ]
        )

    elif palette_type == PaletteType.TRIADIC:
        # Generate triadic colors (120 degrees apart)
        suggestions.extend(
            [
                f"rgb({b}, {r}, {g})",
                f"rgb({g}, {b}, {r})",
                "white" if info.is_dark else "black",
            ]
        )

    # Remove duplicates and invalid colors
    valid_suggestions = []
    for color in suggestions:
        if parse_color(color) is not None and color not in valid_suggestions:
            valid_suggestions.append(color)

    return valid_suggestions


def get_safe_color_alternatives(
    problematic_color: str, target_luminance: Optional[float] = None
) -> List[str]:
    """
    Get safer alternatives for a problematic color.

    Args:
        problematic_color: Color that has issues
        target_luminance: Target luminance (0.0-1.0), if None will use opposite

    Returns:
        List of safer color alternatives
    """
    info = ColorInfo.from_string(problematic_color)
    if info is None:
        return ["black", "white"]

    alternatives = []

    # If no target luminance specified, aim for opposite
    if target_luminance is None:
        target_luminance = 0.2 if info.luminance > 0.5 else 0.8

    # Generate variations with target luminance
    r, g, b = info.rgb

    # Adjust brightness while maintaining hue
    current_luminance = info.luminance
    if current_luminance > 0:
        factor = target_luminance / current_luminance
        factor = max(0.1, min(2.0, factor))  # Clamp factor

        new_r = max(0, min(255, int(r * factor)))
        new_g = max(0, min(255, int(g * factor)))
        new_b = max(0, min(255, int(b * factor)))

        alternatives.append(f"rgb({new_r}, {new_g}, {new_b})")

    # Add standard safe colors
    if target_luminance < 0.5:
        alternatives.extend(["black", "#333333", "#1a1a1a"])
    else:
        alternatives.extend(["white", "#f0f0f0", "#e0e0e0"])

    return alternatives
