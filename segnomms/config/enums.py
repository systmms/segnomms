"""Enumeration classes for configuration options.

This module contains all enumeration classes used throughout the configuration
system to ensure type safety and provide clear, validated options.
"""

from enum import Enum


class ConnectivityMode(Enum):
    """Module connectivity detection modes.

    Attributes:
        FOUR_WAY: Connect only to orthogonal neighbors (up, down, left, right)
        EIGHT_WAY: Connect to all 8 neighbors including diagonals
    """

    FOUR_WAY = "4-way"
    EIGHT_WAY = "8-way"


class MergeStrategy(Enum):
    """Module merging strategies.

    Attributes:
        NONE: No merging, each module rendered separately
        SOFT: Merge adjacent connected modules with smooth transitions
        AGGRESSIVE: Extensive merging creating flowing organic shapes
    """

    NONE = "none"
    SOFT = "soft"
    AGGRESSIVE = "aggressive"


class ReserveMode(Enum):
    """Reserve area interaction mode enumeration.

    Attributes:
        KNOCKOUT: Clear modules completely from reserve area (default)
        IMPRINT: Overlay centerpiece while preserving modules underneath for scanability
    """

    KNOCKOUT = "knockout"
    IMPRINT = "imprint"


class PlacementMode(Enum):
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


class ModuleShape(Enum):
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


class FinderShape(Enum):
    """Finder pattern shape types.

    Attributes:
        SQUARE: Traditional square finder patterns
        ROUNDED: Rounded square finder patterns
        CIRCLE: Circular finder patterns
    """

    SQUARE = "square"
    ROUNDED = "rounded"
    CIRCLE = "circle"


class ContourMode(Enum):
    """Contour rendering modes for Phase 3.

    Attributes:
        BEZIER: Use Bezier curves for smooth contours
        COMBINED: Combine multiple contour strategies
        OVERLAY: Overlay contours on existing shapes
    """

    BEZIER = "bezier"
    COMBINED = "combined"
    OVERLAY = "overlay"


class OptimizationLevel(Enum):
    """Optimization levels for Bezier curve generation.

    Attributes:
        LOW: Minimal optimization, fastest rendering
        MEDIUM: Balanced optimization (default)
        HIGH: Maximum optimization, smallest file size
    """

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
