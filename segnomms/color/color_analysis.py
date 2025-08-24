"""Color analysis utilities for QR code scanability validation.

This module provides tools for analyzing color contrast ratios and other
color-related scanability factors.
"""

import re
from math import sqrt
from typing import Optional, Tuple


def parse_color(color_str: str) -> Optional[Tuple[int, int, int]]:
    """Parse a color string into RGB components.

    Supports:
    - Hex colors: #RGB, #RRGGBB
    - RGB function: rgb(r, g, b)
    - Named colors: black, white, red, green, blue, etc.

    Args:
        color_str: Color string to parse

    Returns:
        RGB tuple (r, g, b) with values 0-255, or None if unparseable
    """
    if not color_str:
        return None

    color_str = color_str.strip().lower()

    # Named colors
    named_colors = {
        "black": (0, 0, 0),
        "white": (255, 255, 255),
        "red": (255, 0, 0),
        "green": (0, 128, 0),
        "blue": (0, 0, 255),
        "yellow": (255, 255, 0),
        "cyan": (0, 255, 255),
        "magenta": (255, 0, 255),
        "gray": (128, 128, 128),
        "grey": (128, 128, 128),
        "orange": (255, 165, 0),
        "purple": (128, 0, 128),
        "brown": (165, 42, 42),
        "pink": (255, 192, 203),
        "lime": (0, 255, 0),
        "navy": (0, 0, 128),
        "olive": (128, 128, 0),
        "maroon": (128, 0, 0),
        "teal": (0, 128, 128),
        "silver": (192, 192, 192),
        "gold": (255, 215, 0),
        "darkgray": (169, 169, 169),
        "darkgrey": (169, 169, 169),
        "lightgray": (211, 211, 211),
        "lightgrey": (211, 211, 211),
    }

    if color_str in named_colors:
        return named_colors[color_str]

    # Hex colors
    if color_str.startswith("#"):
        hex_color = color_str[1:]

        # #RGB format
        if len(hex_color) == 3:
            try:
                r = int(hex_color[0] * 2, 16)
                g = int(hex_color[1] * 2, 16)
                b = int(hex_color[2] * 2, 16)
                return (r, g, b)
            except ValueError:
                return None

        # #RRGGBB format
        elif len(hex_color) == 6:
            try:
                r = int(hex_color[0:2], 16)
                g = int(hex_color[2:4], 16)
                b = int(hex_color[4:6], 16)
                return (r, g, b)
            except ValueError:
                return None

    # RGB function format
    rgb_match = re.match(r"rgb\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)", color_str)
    if rgb_match:
        try:
            r, g, b = map(int, rgb_match.groups())
            # Clamp values to 0-255
            r = max(0, min(255, r))
            g = max(0, min(255, g))
            b = max(0, min(255, b))
            return (r, g, b)
        except ValueError:
            return None

    return None


def calculate_luminance(rgb: Tuple[int, int, int]) -> float:
    """Calculate relative luminance of a color.

    Uses the W3C formula for relative luminance calculation.

    Args:
        rgb: RGB color tuple (r, g, b) with values 0-255

    Returns:
        Relative luminance value 0.0-1.0
    """
    r, g, b = rgb

    # Convert to 0-1 range
    r_norm = r / 255.0
    g_norm = g / 255.0
    b_norm = b / 255.0

    # Apply gamma correction
    def gamma_correct(channel: float) -> float:
        if channel <= 0.03928:
            return channel / 12.92
        else:
            return float(pow((channel + 0.055) / 1.055, 2.4))

    r_linear = gamma_correct(r_norm)
    g_linear = gamma_correct(g_norm)
    b_linear = gamma_correct(b_norm)

    # Calculate luminance using sRGB weights
    luminance = 0.2126 * r_linear + 0.7152 * g_linear + 0.0722 * b_linear

    return luminance


def calculate_contrast_ratio(color1: str, color2: str) -> Optional[float]:
    """Calculate WCAG contrast ratio between two colors.

    Args:
        color1: First color string
        color2: Second color string

    Returns:
        Contrast ratio (1.0-21.0), or None if colors can't be parsed
    """
    rgb1 = parse_color(color1)
    rgb2 = parse_color(color2)

    if rgb1 is None or rgb2 is None:
        return None

    lum1 = calculate_luminance(rgb1)
    lum2 = calculate_luminance(rgb2)

    # Ensure lighter color is in numerator
    lighter = max(lum1, lum2)
    darker = min(lum1, lum2)

    # WCAG contrast ratio formula
    contrast_ratio = (lighter + 0.05) / (darker + 0.05)

    return contrast_ratio


def validate_qr_contrast(
    dark_color: str, light_color: str, min_ratio: float = 3.0
) -> Tuple[bool, float, str]:
    """Validate QR code color contrast for scanability.

    Args:
        dark_color: Dark module color
        light_color: Light module color
        min_ratio: Minimum acceptable contrast ratio

    Returns:
        Tuple of (is_valid, actual_ratio, message)
    """
    ratio = calculate_contrast_ratio(dark_color, light_color)

    if ratio is None:
        return False, 0.0, f"Could not parse colors: '{dark_color}' and '{light_color}'"

    is_valid = ratio >= min_ratio

    if is_valid:
        if ratio >= 7.0:
            level = "excellent"
        elif ratio >= 4.5:
            level = "good"
        else:
            level = "adequate"
        message = f"Contrast ratio {ratio:.1f}:1 is {level} for QR scanning"
    else:
        message = f"Contrast ratio {ratio:.1f}:1 is below minimum {min_ratio:.1f}:1 for reliable scanning"

    return is_valid, ratio, message


def get_color_distance(color1: str, color2: str) -> Optional[float]:
    """Calculate Euclidean distance between two colors in RGB space.

    Useful for checking if colors are too similar even if contrast is adequate.

    Args:
        color1: First color string
        color2: Second color string

    Returns:
        Color distance (0-441.67), or None if colors can't be parsed
    """
    rgb1 = parse_color(color1)
    rgb2 = parse_color(color2)

    if rgb1 is None or rgb2 is None:
        return None

    r1, g1, b1 = rgb1
    r2, g2, b2 = rgb2

    # Euclidean distance in RGB space
    distance = sqrt((r2 - r1) ** 2 + (g2 - g1) ** 2 + (b2 - b1) ** 2)

    return distance


def suggest_color_improvements(dark_color: str, light_color: str) -> list[str]:
    """Suggest improvements for better QR code contrast.

    Args:
        dark_color: Dark module color
        light_color: Light module color

    Returns:
        List of improvement suggestions
    """
    suggestions = []

    ratio = calculate_contrast_ratio(dark_color, light_color)
    if ratio is None:
        suggestions.append(
            "Use standard color formats like #000000, rgb(0,0,0), or 'black'"
        )
        return suggestions

    if ratio < 3.0:
        suggestions.append(
            "Increase contrast - use darker dark color or lighter light color"
        )

        # Parse colors for specific suggestions
        dark_rgb = parse_color(dark_color)
        light_rgb = parse_color(light_color)

        if dark_rgb and light_rgb:
            dark_avg = sum(dark_rgb) // 3
            light_avg = sum(light_rgb) // 3

            if dark_avg > 100:
                suggestions.append(
                    "Consider using a darker color like #000000 (black) for dark modules"
                )

            if light_avg < 200:
                suggestions.append(
                    "Consider using a lighter color like #FFFFFF (white) for light modules"
                )

    elif ratio < 4.5:
        suggestions.append(
            "Good contrast, but consider increasing for better reliability in poor lighting"
        )

    # Check color distance
    distance = get_color_distance(dark_color, light_color)
    if distance and distance < 100:
        suggestions.append(
            "Colors are very similar - increase difference for better scanner detection"
        )

    return suggestions
