"""
Public constants and convenience imports for SegnoMMS.

This module provides convenient access to commonly used enums, constants,
and utilities that are helpful for working with SegnoMMS configurations
in documentation examples and user code.

Example:
    Basic usage with constants::

        from segnomms.constants import ModuleShape, TEST_COLORS, DEFAULT_SCALE
        from segnomms import write
        import segno

        qr = segno.make("Hello, World!")
        with open('example.svg', 'w') as f:
            write(qr, f,
                  shape=ModuleShape.CIRCLE.value,
                  dark=TEST_COLORS["blue"],
                  scale=DEFAULT_SCALE)

    Using configuration helpers::

        from segnomms.constants import create_config, BASIC_SHAPES

        for shape in BASIC_SHAPES:
            config = create_config(shape=shape.value, scale=15)
            # Use config...

Note:
    This module re-exports the same convenience constants that were
    previously available in the tests module, making them publicly
    accessible for documentation and user code.
"""

from typing import Any

from segnomms.config.enums import (
    ConnectivityMode,
    ContourMode,
    FinderShape,
    MergeStrategy,
    ModuleShape,
    OptimizationLevel,
    PlacementMode,
    ReserveMode,
)

# Re-export enums for convenience
__all__ = [
    # Enums
    "ModuleShape",
    "FinderShape",
    "ConnectivityMode",
    "MergeStrategy",
    "ReserveMode",
    "PlacementMode",
    "ContourMode",
    "OptimizationLevel",
    # Shape collections
    "VALID_SHAPES",
    "CONNECTED_SHAPES",
    "BASIC_SHAPES",
    "FINDER_SHAPES",
    # Common values
    "DEFAULT_SCALE",
    "DEFAULT_BORDER",
    "DEFAULT_DARK",
    "DEFAULT_LIGHT",
    "TEST_COLORS",
    "QR_PAYLOADS",
    # Utilities
    "create_config",
    "get_shape_enum",
]


# ============================================================================
# SHAPE COLLECTIONS
# ============================================================================

# Valid module shapes for use in examples
VALID_SHAPES = [
    ModuleShape.SQUARE,
    ModuleShape.CIRCLE,
    ModuleShape.ROUNDED,
    ModuleShape.DOT,
    ModuleShape.DIAMOND,
    ModuleShape.STAR,
    ModuleShape.HEXAGON,
    ModuleShape.TRIANGLE,
    ModuleShape.SQUIRCLE,
    ModuleShape.CROSS,
    ModuleShape.CONNECTED,
    ModuleShape.CONNECTED_EXTRA_ROUNDED,
    ModuleShape.CONNECTED_CLASSY,
    ModuleShape.CONNECTED_CLASSY_ROUNDED,
]

# Connected shape variants
CONNECTED_SHAPES = [
    ModuleShape.CONNECTED,
    ModuleShape.CONNECTED_EXTRA_ROUNDED,
    ModuleShape.CONNECTED_CLASSY,
    ModuleShape.CONNECTED_CLASSY_ROUNDED,
]

# Basic shapes (non-connected)
BASIC_SHAPES = [
    ModuleShape.SQUARE,
    ModuleShape.CIRCLE,
    ModuleShape.ROUNDED,
    ModuleShape.DOT,
    ModuleShape.DIAMOND,
    ModuleShape.STAR,
    ModuleShape.HEXAGON,
    ModuleShape.TRIANGLE,
    ModuleShape.SQUIRCLE,
    ModuleShape.CROSS,
]

# Finder shapes
FINDER_SHAPES = [
    FinderShape.SQUARE,
    FinderShape.ROUNDED,
    FinderShape.CIRCLE,
]


# ============================================================================
# COMMON DEFAULTS
# ============================================================================

# Standard default values for examples
DEFAULT_SCALE = 10
DEFAULT_BORDER = 4
DEFAULT_DARK = "#000000"
DEFAULT_LIGHT = "#FFFFFF"

# Common colors for examples and testing
TEST_COLORS = {
    "black": "#000000",
    "white": "#FFFFFF",
    "red": "#FF0000",
    "green": "#00FF00",
    "blue": "#0000FF",
    "transparent": "transparent",
    "brand_primary": "#1a1a2e",
    "brand_secondary": "#f5f5f5",
}

# Common QR payloads for examples and testing
QR_PAYLOADS = {
    "simple": "Hello World",
    "url": "https://example.com",
    "url_complex": "https://example.com/path?param1=value1&param2=value2",
    "email": "mailto:test@example.com",
    "phone": "tel:+1234567890",
    "wifi": "WIFI:T:WPA;S:MyNetwork;P:MyPassword;;",
    "unicode": "Hello 世界 🌍",
    "numeric": "1234567890",
    "alphanumeric": "HELLO123",
}


# ============================================================================
# UTILITIES
# ============================================================================


def get_shape_enum(shape_string: str) -> ModuleShape:
    """Convert a shape string to ModuleShape enum.

    Args:
        shape_string: Shape name as string

    Returns:
        ModuleShape enum value

    Raises:
        ValueError: If shape string is not valid

    Example:
        >>> from segnomms.constants import get_shape_enum
        >>> shape = get_shape_enum("circle")
        >>> print(shape)
        ModuleShape.CIRCLE
    """
    for shape in ModuleShape:
        if shape.value == shape_string:
            return shape
    raise ValueError(f"Invalid shape: {shape_string}")


def create_config(**overrides: Any) -> dict[str, Any]:
    """Create a configuration dictionary with sensible defaults.

    Args:
        **overrides: Keyword arguments to override defaults

    Returns:
        Dictionary configuration suitable for write() function

    Example:
        >>> from segnomms.constants import create_config, ModuleShape
        >>> config = create_config(
        ...     shape=ModuleShape.CIRCLE.value,
        ...     scale=15,
        ...     dark="#0066cc"
        ... )
        >>> print(config)
        {'scale': 15, 'border': 4, 'dark': '#0066cc', 'light': '#FFFFFF', 'shape': 'circle'}
    """
    config = {
        "scale": DEFAULT_SCALE,
        "border": DEFAULT_BORDER,
        "dark": DEFAULT_DARK,
        "light": DEFAULT_LIGHT,
    }
    config.update(overrides)
    return config
