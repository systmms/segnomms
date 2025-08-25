"""Centralized type definitions for SegnoMMS.

This module provides common type definitions used throughout the SegnoMMS
codebase to improve type safety and reduce code duplication.

This includes both legacy type definitions and modern TypedDict patterns
for type-safe **kwargs usage following Pydantic v2 + MyPy best practices.
"""

from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Protocol,
    TypedDict,
    Union,
)

from typing_extensions import NotRequired

if TYPE_CHECKING:
    from .config.models.core import RenderingConfig
    from .config.models.visual import CenterpieceConfig

# ============================================================================
# LEGACY TYPE DEFINITIONS
# ============================================================================

# Type aliases for common configuration objects
ConfigType = Union["RenderingConfig", Dict[str, Any], None]
CenterpieceConfigType = Union["CenterpieceConfig", Dict[str, Any], None]

# Matrix and geometry types
MatrixType = List[List[Optional[int]]]
CoordinateType = tuple[int, int]
BoundingBoxType = tuple[int, int, int, int]  # (min_x, min_y, max_x, max_y)

# SVG and path types
SVGPathType = str
SVGAttributesType = Dict[str, Union[str, int, float]]

# Performance and validation types
PerformanceMetricsType = Dict[str, Union[str, float, int, List[str]]]
ValidationResultType = Dict[str, Union[bool, str, List[str]]]


class ConfigProtocol(Protocol):
    """Protocol for configuration objects."""

    def model_dump(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        ...


class CenterpieceConfigProtocol(Protocol):
    """Protocol for centerpiece configuration objects."""

    enabled: bool
    size: Optional[float]
    shape: Optional[str]

    def model_dump(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        ...


# Union types for common parameter patterns
OptionalConfigType = Optional[Union[ConfigProtocol, Dict[str, Any]]]
OptionalCenterpieceConfigType = Optional[
    Union[CenterpieceConfigProtocol, Dict[str, Any]]
]


# ============================================================================
# TYPEDDICT PATTERNS FOR TYPE-SAFE **KWARGS
# ============================================================================


# Base kwargs for SVG elements
class BaseRenderKwargs(TypedDict, total=False):
    """Base kwargs for all SVG element rendering."""

    css_class: str
    id: str
    fill: str
    stroke: str
    stroke_width: float
    opacity: float
    transform: str


# Data attribute kwargs (for interactive features)
class DataAttributeKwargs(TypedDict, total=False):
    """Data attributes for interactive SVG elements."""

    data_row: str
    data_col: str
    data_type: str
    data_index: str


# Shape-specific parameter kwargs
class SquareRenderKwargs(BaseRenderKwargs, DataAttributeKwargs, total=False):
    """Kwargs for square/rectangle rendering."""

    rx: float  # Border radius
    ry: float  # Border radius


class CircleRenderKwargs(BaseRenderKwargs, DataAttributeKwargs, total=False):
    """Kwargs for circle rendering."""

    cx: NotRequired[float]  # Center x (usually calculated)
    cy: NotRequired[float]  # Center y (usually calculated)
    r: NotRequired[float]  # Radius (usually calculated)


class RoundedRenderKwargs(BaseRenderKwargs, DataAttributeKwargs, total=False):
    """Kwargs for rounded shapes."""

    roundness: float  # Corner roundness factor
    corner_radius: float


class StarRenderKwargs(BaseRenderKwargs, DataAttributeKwargs, total=False):
    """Kwargs for star shape rendering."""

    star_points: int
    inner_ratio: float
    rotation: float


class ConnectedRenderKwargs(BaseRenderKwargs, DataAttributeKwargs, total=False):
    """Kwargs for connected shape rendering."""

    get_neighbor: Callable[[int, int], bool]  # Neighbor detection function
    corner_radius: float
    size_ratio: float
    roundness: float
    merge_threshold: float


class DotRenderKwargs(BaseRenderKwargs, DataAttributeKwargs, total=False):
    """Kwargs for dot rendering."""

    size_ratio: float  # Dot size relative to module


class DiamondRenderKwargs(BaseRenderKwargs, DataAttributeKwargs, total=False):
    """Kwargs for diamond shape rendering."""

    # No specific parameters beyond base


class TriangleRenderKwargs(BaseRenderKwargs, DataAttributeKwargs, total=False):
    """Kwargs for triangle shape rendering."""

    direction: str  # Triangle direction ('up', 'down', 'left', 'right')


class HexagonRenderKwargs(BaseRenderKwargs, DataAttributeKwargs, total=False):
    """Kwargs for hexagon rendering."""

    size_ratio: float  # Hexagon size relative to module


class CrossRenderKwargs(BaseRenderKwargs, DataAttributeKwargs, total=False):
    """Kwargs for cross shape rendering."""

    thickness: float  # Cross arm thickness ratio
    sharp: bool  # Use tapered arms for sharper look


class SquircleRenderKwargs(BaseRenderKwargs, DataAttributeKwargs, total=False):
    """Kwargs for squircle rendering."""

    corner_radius: float  # Override corner radius (0.0-1.0)
