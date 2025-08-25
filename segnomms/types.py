"""Shared type definitions and TypedDict patterns for SegnoMMS.

This module provides type-safe patterns for **kwargs usage throughout the codebase,
following Pydantic v2 + MyPy best practices.
"""

from __future__ import annotations

from typing import Callable, TypedDict

from typing_extensions import NotRequired


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
