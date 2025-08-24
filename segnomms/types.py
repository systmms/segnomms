"""Centralized type definitions for SegnoMMS.

This module provides common type definitions used throughout the SegnoMMS
codebase to improve type safety and reduce code duplication.
"""

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Protocol, Union

if TYPE_CHECKING:
    from .config.models.core import RenderingConfig
    from .config.models.visual import CenterpieceConfig

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
OptionalCenterpieceConfigType = Optional[Union[CenterpieceConfigProtocol, Dict[str, Any]]]