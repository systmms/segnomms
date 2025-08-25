"""
Shared constants and test data for SegnoMMS tests.

This module provides centralized constants to reduce brittle string literals
in tests and ensure consistency across the test suite.
"""

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
    # Test data
    "VALID_SHAPES",
    "CONNECTED_SHAPES",
    "BASIC_SHAPES",
    "DEFAULT_TEST_CONFIG",
    "SHAPE_TEST_CASES",
    "COLOR_TEST_CASES",
    "FRAME_TEST_CASES",
    "QR_PAYLOADS",
    "ERROR_LEVELS",
    # Common values
    "DEFAULT_SCALE",
    "DEFAULT_BORDER",
    "DEFAULT_DARK",
    "DEFAULT_LIGHT",
    "TEST_SCALES",
    "TEST_BORDERS",
    "TEST_COLORS",
]


# ============================================================================
# SHAPE CONSTANTS
# ============================================================================

# Valid module shapes for testing
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
# DEFAULT VALUES
# ============================================================================

DEFAULT_SCALE = 10
DEFAULT_BORDER = 4
DEFAULT_DARK = "#000000"
DEFAULT_LIGHT = "#FFFFFF"

# Common test scales
TEST_SCALES = [1, 5, 10, 20]

# Common test borders
TEST_BORDERS = [0, 1, 2, 4, 8]

# Common test colors
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


# ============================================================================
# TEST DATA SETS
# ============================================================================

# Shape test cases with expected behaviors
SHAPE_TEST_CASES = [
    {
        "shape": ModuleShape.SQUARE,
        "corner_radius": 0,
        "supports_merging": True,
        "supports_safe_mode": True,
        "description": "Traditional square modules",
    },
    {
        "shape": ModuleShape.CIRCLE,
        "corner_radius": 0,
        "supports_merging": False,
        "supports_safe_mode": True,
        "description": "Circular modules with gaps",
    },
    {
        "shape": ModuleShape.SQUIRCLE,
        "corner_radius": 0.3,
        "supports_merging": True,
        "supports_safe_mode": False,
        "description": "Superellipse shape",
    },
    {
        "shape": ModuleShape.CONNECTED,
        "corner_radius": 0.2,
        "supports_merging": True,
        "supports_safe_mode": False,
        "description": "Connected modules with rounded corners",
    },
]

# Color test cases
COLOR_TEST_CASES = [
    {"dark": "#000000", "light": "#FFFFFF", "name": "Classic B&W"},
    {"dark": "#1a1a2e", "light": "#eef2f5", "name": "Brand colors"},
    {"dark": "#e74c3c", "light": "transparent", "name": "Red on transparent"},
    {"dark": "#2D3748", "light": "#F7FAFC", "name": "Gray scale"},
]

# Frame configuration test cases
FRAME_TEST_CASES = [
    {
        "shape": ModuleShape.SQUARE,
        "clip_mode": "hard",
        "corner_radius": 0,
        "description": "Square frame (default)",
    },
    {
        "shape": ModuleShape.CIRCLE,
        "clip_mode": "fade",
        "fade_start": 0.7,
        "fade_end": 0.9,
        "description": "Circle frame with fade",
    },
    {
        "shape": ModuleShape.ROUNDED,
        "clip_mode": "scale",
        "corner_radius": 0.2,
        "scale_distance": 0.1,
        "description": "Rounded frame with scaling",
    },
]

# Common QR payloads for testing
QR_PAYLOADS = {
    "simple": "Hello World",
    "url": "https://example.com",
    "url_complex": "https://example.com/path?param1=value1&param2=value2",
    "email": "mailto:test@example.com",
    "phone": "tel:+1234567890",
    "wifi": "WIFI:T:WPA;S:MyNetwork;P:MyPassword;;",
    "unicode": "Hello 世界 🌍",
    "long": "A" * 1000,  # Long text for stress testing
    "numeric": "1234567890",
    "alphanumeric": "HELLO123",
    "special": "!@#$%^&*()",
}

# Error correction levels
ERROR_LEVELS = ["L", "M", "Q", "H"]


# ============================================================================
# DEFAULT TEST CONFIGURATIONS
# ============================================================================

DEFAULT_TEST_CONFIG = {
    "scale": DEFAULT_SCALE,
    "border": DEFAULT_BORDER,
    "dark": DEFAULT_DARK,
    "light": DEFAULT_LIGHT,
    "shape": ModuleShape.SQUARE,
    "error": "M",
}

# Minimal config for basic tests
MINIMAL_CONFIG = {
    "scale": DEFAULT_SCALE,
}

# Full config for comprehensive tests
FULL_TEST_CONFIG = {
    "scale": 10,
    "border": 4,
    "dark": "#1a1a2e",
    "light": "#f5f5f5",
    "shape": ModuleShape.SQUIRCLE,
    "corner_radius": 0.3,
    "merge": MergeStrategy.SOFT,
    "connectivity": ConnectivityMode.EIGHT_WAY,
    "safe_mode": False,
    "interactive": True,
    "tooltips": True,
    "frame": {
        "shape": ModuleShape.CIRCLE,
        "clip_mode": "fade",
        "fade_start": 0.7,
        "fade_end": 0.9,
    },
    "centerpiece": {
        "enabled": True,
        "size": 0.2,
        "shape": ModuleShape.CIRCLE,
        "mode": ReserveMode.KNOCKOUT,
    },
    "patterns": {
        "enabled": True,
        "finder": {
            "shape": FinderShape.ROUNDED,
            "color": "#FF6B6B",
        },
        "data": {
            "shape": ModuleShape.DOT,
            "size_ratio": 0.8,
        },
    },
}


# ============================================================================
# TEST UTILITIES
# ============================================================================


def get_shape_enum(shape_string: str) -> ModuleShape:
    """Convert a shape string to ModuleShape enum.

    Args:
        shape_string: Shape name as string

    Returns:
        ModuleShape enum value

    Raises:
        ValueError: If shape string is not valid
    """
    for shape in ModuleShape:
        if shape.value == shape_string:
            return shape
    raise ValueError(f"Invalid shape: {shape_string}")


def get_all_shape_combinations():
    """Generate all valid shape combinations for testing.

    Returns:
        List of (module_shape, finder_shape) tuples
    """
    combinations = []
    for module_shape in VALID_SHAPES:
        for finder_shape in FINDER_SHAPES:
            combinations.append((module_shape, finder_shape))
    return combinations


def get_safe_mode_compatible_shapes():
    """Get shapes that are compatible with safe mode.

    Returns:
        List of shape strings that work with safe_mode=True
    """
    return [
        ModuleShape.SQUARE,
        ModuleShape.CIRCLE,
        ModuleShape.ROUNDED,
        ModuleShape.DOT,
        ModuleShape.DIAMOND,
    ]


def create_test_config(**overrides):
    """Create a test configuration with defaults and overrides.

    Args:
        **overrides: Keyword arguments to override defaults

    Returns:
        Dictionary configuration for testing
    """
    config = DEFAULT_TEST_CONFIG.copy()
    config.update(overrides)
    return config
