"""Color analysis and palette management subsystem.

This package provides comprehensive color handling capabilities including
contrast analysis, palette validation, and color space management for
QR code generation.

Key Components:

    Color Analysis:
        - Contrast ratio calculations (WCAG standards)
        - Luminance calculations
        - Color parsing from various formats

    Palette Management:
        - Color palette validation
        - Multi-color space support
        - Accessibility compliance checking

The color subsystem handles:

* Color contrast validation for scanability
* WCAG accessibility compliance
* Color space conversions
* Palette optimization
* Color parsing (hex, rgb, named colors)
* Luminance calculations

Example:
    Basic color analysis::

        from segnomms.color import calculate_contrast_ratio, parse_color

        dark = parse_color("#1a1a2e")
        light = parse_color("#ffffff")
        ratio = calculate_contrast_ratio(dark, light)

    Palette validation::

        from segnomms.color import ColorPalette, ContrastStandard

        palette = ColorPalette(
            foreground="#1a1a2e",
            background="#ffffff",
            standard=ContrastStandard.AA_NORMAL
        )
        is_valid = palette.validate_contrast()

See Also:
    :mod:`segnomms.color.color_analysis`: Color analysis utilities
    :mod:`segnomms.color.palette`: Palette management
"""

from .color_analysis import (
    calculate_contrast_ratio,
    calculate_luminance,
    parse_color,
)
from .palette import (
    ColorSpace,
    ContrastStandard,
    PaletteConfig,
    PaletteType,
    PaletteValidationResult,
)

__all__ = [
    # Color analysis
    "calculate_contrast_ratio",
    "calculate_luminance",
    "parse_color",
    # Palette management
    "PaletteConfig",
    "PaletteType",
    "ColorSpace",
    "ContrastStandard",
    "PaletteValidationResult",
]
