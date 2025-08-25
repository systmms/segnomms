"""Enumeration classes for configuration options.

This module contains all enumeration classes used throughout the configuration
system to ensure type safety and provide clear, validated options.
"""

from enum import Enum
from typing import Any


class ConnectivityMode(str, Enum):
    """Module connectivity detection modes.

    Attributes:
        FOUR_WAY: Connect only to orthogonal neighbors (up, down, left, right)
        EIGHT_WAY: Connect to all 8 neighbors including diagonals
    """

    FOUR_WAY = "4-way"
    EIGHT_WAY = "8-way"

    @classmethod
    def _missing_(cls, value: Any) -> "ConnectivityMode":
        """Handle case-insensitive lookup and common aliases."""
        if isinstance(value, str):
            value_lower = value.lower().strip()
            for member in cls:
                if member.value.lower() == value_lower:
                    return member
            # Handle aliases
            aliases = {
                "4way": cls.FOUR_WAY,
                "4-way": cls.FOUR_WAY,
                "four": cls.FOUR_WAY,
                "orthogonal": cls.FOUR_WAY,
                "8way": cls.EIGHT_WAY,
                "8-way": cls.EIGHT_WAY,
                "eight": cls.EIGHT_WAY,
                "diagonal": cls.EIGHT_WAY,
                "all": cls.EIGHT_WAY,
            }
            if value_lower in aliases:
                return aliases[value_lower]
        raise ValueError(f"'{value}' is not a valid {cls.__name__}")


class MergeStrategy(str, Enum):
    """Module merging strategies.

    Attributes:
        NONE: No merging, each module rendered separately
        SOFT: Merge adjacent connected modules with smooth transitions
        AGGRESSIVE: Extensive merging creating flowing organic shapes
    """

    NONE = "none"
    SOFT = "soft"
    AGGRESSIVE = "aggressive"

    @classmethod
    def _missing_(cls, value: Any) -> "MergeStrategy":
        """Handle case-insensitive lookup and common aliases."""
        if isinstance(value, str):
            value_lower = value.lower().strip()
            for member in cls:
                if member.value.lower() == value_lower:
                    return member
            # Handle aliases
            aliases = {
                "no": cls.NONE,
                "off": cls.NONE,
                "false": cls.NONE,
                "disabled": cls.NONE,
                "smooth": cls.SOFT,
                "medium": cls.SOFT,
                "moderate": cls.SOFT,
                "hard": cls.AGGRESSIVE,
                "strong": cls.AGGRESSIVE,
                "max": cls.AGGRESSIVE,
                "maximum": cls.AGGRESSIVE,
                "full": cls.AGGRESSIVE,
            }
            if value_lower in aliases:
                return aliases[value_lower]
        raise ValueError(f"'{value}' is not a valid {cls.__name__}")


class ReserveMode(str, Enum):
    """Reserve area interaction mode enumeration.

    Attributes:
        KNOCKOUT: Clear modules completely from reserve area (default)
        IMPRINT: Overlay centerpiece while preserving modules underneath for scanability
    """

    KNOCKOUT = "knockout"
    IMPRINT = "imprint"

    @classmethod
    def _missing_(cls, value: Any) -> "ReserveMode":
        """Handle case-insensitive lookup and common aliases."""
        if isinstance(value, str):
            value_lower = value.lower().strip()
            for member in cls:
                if member.value.lower() == value_lower:
                    return member
            # Handle aliases
            aliases = {
                "clear": cls.KNOCKOUT,
                "remove": cls.KNOCKOUT,
                "cut": cls.KNOCKOUT,
                "overlay": cls.IMPRINT,
                "preserve": cls.IMPRINT,
                "keep": cls.IMPRINT,
            }
            if value_lower in aliases:
                return aliases[value_lower]
        raise ValueError(f"'{value}' is not a valid {cls.__name__}")


class PlacementMode(str, Enum):
    """Reserve area placement mode enumeration.

    Attributes:
        CUSTOM: Use custom offset_x and offset_y values (default)
        CENTER: Center of QR code
        TOP_LEFT: Top-left corner
        TOP_RIGHT: Top-right corner
        BOTTOM_LEFT: Bottom-left corner
        BOTTOM_RIGHT: Bottom-right corner
        TOP_CENTER: Top edge center
        BOTTOM_CENTER: Bottom edge center
        LEFT_CENTER: Left edge center
        RIGHT_CENTER: Right edge center
    """

    CUSTOM = "custom"
    CENTER = "center"
    TOP_LEFT = "top-left"
    TOP_RIGHT = "top-right"
    BOTTOM_LEFT = "bottom-left"
    BOTTOM_RIGHT = "bottom-right"
    TOP_CENTER = "top-center"
    BOTTOM_CENTER = "bottom-center"
    LEFT_CENTER = "left-center"
    RIGHT_CENTER = "right-center"

    @classmethod
    def _missing_(cls, value: Any) -> "PlacementMode":
        """Handle case-insensitive lookup and common aliases."""
        if isinstance(value, str):
            value_lower = value.lower().strip().replace("_", "-")
            for member in cls:
                if member.value.lower() == value_lower:
                    return member
            # Handle aliases with underscores/spaces
            aliases = {
                "topleft": cls.TOP_LEFT,
                "top_left": cls.TOP_LEFT,
                "topright": cls.TOP_RIGHT,
                "top_right": cls.TOP_RIGHT,
                "bottomleft": cls.BOTTOM_LEFT,
                "bottom_left": cls.BOTTOM_LEFT,
                "bottomright": cls.BOTTOM_RIGHT,
                "bottom_right": cls.BOTTOM_RIGHT,
                "topcenter": cls.TOP_CENTER,
                "top_center": cls.TOP_CENTER,
                "bottomcenter": cls.BOTTOM_CENTER,
                "bottom_center": cls.BOTTOM_CENTER,
                "leftcenter": cls.LEFT_CENTER,
                "left_center": cls.LEFT_CENTER,
                "rightcenter": cls.RIGHT_CENTER,
                "right_center": cls.RIGHT_CENTER,
                "middle": cls.CENTER,
            }
            if value_lower in aliases:
                return aliases[value_lower]
        raise ValueError(f"'{value}' is not a valid {cls.__name__}")


class ModuleShape(str, Enum):
    """Base module shape types.

    Attributes:
        SQUARE: Traditional square modules
        CIRCLE: Circular modules (may have gaps)
        ROUNDED: Square with rounded corners
        DOT: Small circular dots
        DIAMOND: 45-degree rotated square
        STAR: 5-pointed star modules
        HEXAGON: Hexagonal modules
        TRIANGLE: Triangular modules
        SQUIRCLE: Superellipse shape (between square and circle)
        CROSS: Cross/plus shaped modules
        CONNECTED: Basic connected style with rounded corners
        CONNECTED_EXTRA_ROUNDED: Extra smooth curves using quadratic beziers
        CONNECTED_CLASSY: Boundary-focused styling with strategic rounding
        CONNECTED_CLASSY_ROUNDED: Classy style with extra-rounded corners
    """

    SQUARE = "square"
    CIRCLE = "circle"
    ROUNDED = "rounded"
    DOT = "dot"
    DIAMOND = "diamond"
    STAR = "star"
    HEXAGON = "hexagon"
    TRIANGLE = "triangle"
    SQUIRCLE = "squircle"
    CROSS = "cross"
    CONNECTED = "connected"
    CONNECTED_EXTRA_ROUNDED = "connected-extra-rounded"
    CONNECTED_CLASSY = "connected-classy"
    CONNECTED_CLASSY_ROUNDED = "connected-classy-rounded"

    @classmethod
    def _missing_(cls, value: Any) -> "ModuleShape":
        """Handle case-insensitive lookup and common aliases."""
        if isinstance(value, str):
            value_lower = value.lower().strip().replace("_", "-")
            for member in cls:
                if member.value.lower() == value_lower:
                    return member
            # Handle aliases
            aliases = {
                "rect": cls.SQUARE,
                "rectangle": cls.SQUARE,
                "round": cls.CIRCLE,
                "circular": cls.CIRCLE,
                "smooth": cls.ROUNDED,
                "round-corner": cls.ROUNDED,
                "round_corner": cls.ROUNDED,
                "point": cls.DOT,
                "pixel": cls.DOT,
                "rhombus": cls.DIAMOND,
                "hex": cls.HEXAGON,
                "tri": cls.TRIANGLE,
                "plus": cls.CROSS,
                "flow": cls.CONNECTED,
                "smooth-connected": cls.CONNECTED_EXTRA_ROUNDED,
                "smooth_connected": cls.CONNECTED_EXTRA_ROUNDED,
                "extra-rounded": cls.CONNECTED_EXTRA_ROUNDED,
                "extra_rounded": cls.CONNECTED_EXTRA_ROUNDED,
                "classy": cls.CONNECTED_CLASSY,
                "elegant": cls.CONNECTED_CLASSY,
                "classy-rounded": cls.CONNECTED_CLASSY_ROUNDED,
                "classy_rounded": cls.CONNECTED_CLASSY_ROUNDED,
            }
            if value_lower in aliases:
                return aliases[value_lower]
        raise ValueError(f"'{value}' is not a valid {cls.__name__}")


class FinderShape(str, Enum):
    """Finder pattern shape types.

    Attributes:
        SQUARE: Traditional square finder patterns
        ROUNDED: Rounded square finder patterns
        CIRCLE: Circular finder patterns
    """

    SQUARE = "square"
    ROUNDED = "rounded"
    CIRCLE = "circle"

    @classmethod
    def _missing_(cls, value: Any) -> "FinderShape":
        """Handle case-insensitive lookup and common aliases."""
        if isinstance(value, str):
            value_lower = value.lower().strip()
            for member in cls:
                if member.value.lower() == value_lower:
                    return member
            # Handle aliases
            aliases = {
                "rect": cls.SQUARE,
                "rectangle": cls.SQUARE,
                "smooth": cls.ROUNDED,
                "round-corner": cls.ROUNDED,
                "round_corner": cls.ROUNDED,
                "round": cls.CIRCLE,
                "circular": cls.CIRCLE,
            }
            if value_lower in aliases:
                return aliases[value_lower]
        raise ValueError(f"'{value}' is not a valid {cls.__name__}")


class ContourMode(str, Enum):
    """Contour rendering modes for Phase 3.

    Attributes:
        BEZIER: Use Bezier curves for smooth contours
        COMBINED: Combine multiple contour strategies
        OVERLAY: Overlay contours on existing shapes
    """

    BEZIER = "bezier"
    COMBINED = "combined"
    OVERLAY = "overlay"

    @classmethod
    def _missing_(cls, value: Any) -> "ContourMode":
        """Handle case-insensitive lookup and common aliases."""
        if isinstance(value, str):
            value_lower = value.lower().strip()
            for member in cls:
                if member.value.lower() == value_lower:
                    return member
            # Handle aliases
            aliases = {
                "curve": cls.BEZIER,
                "curves": cls.BEZIER,
                "smooth": cls.BEZIER,
                "multi": cls.COMBINED,
                "multiple": cls.COMBINED,
                "mixed": cls.COMBINED,
                "hybrid": cls.COMBINED,
                "layer": cls.OVERLAY,
                "layered": cls.OVERLAY,
                "over": cls.OVERLAY,
            }
            if value_lower in aliases:
                return aliases[value_lower]
        raise ValueError(f"'{value}' is not a valid {cls.__name__}")


class OptimizationLevel(str, Enum):
    """Optimization levels for Bezier curve generation.

    Attributes:
        LOW: Minimal optimization, fastest rendering
        MEDIUM: Balanced optimization (default)
        HIGH: Maximum optimization, smallest file size
    """

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

    @classmethod
    def _missing_(cls, value: Any) -> "OptimizationLevel":
        """Handle case-insensitive lookup and common aliases."""
        if isinstance(value, str):
            value_lower = value.lower().strip()
            for member in cls:
                if member.value.lower() == value_lower:
                    return member
            # Handle aliases
            aliases = {
                "min": cls.LOW,
                "minimal": cls.LOW,
                "fast": cls.LOW,
                "fastest": cls.LOW,
                "none": cls.LOW,
                "med": cls.MEDIUM,
                "balanced": cls.MEDIUM,
                "normal": cls.MEDIUM,
                "default": cls.MEDIUM,
                "max": cls.HIGH,
                "maximum": cls.HIGH,
                "best": cls.HIGH,
                "full": cls.HIGH,
            }
            if value_lower in aliases:
                return aliases[value_lower]
        raise ValueError(f"'{value}' is not a valid {cls.__name__}")
