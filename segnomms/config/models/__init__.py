"""Configuration models package.

This package contains all Pydantic configuration models organized by functional area.
All models are re-exported from this module for easy access.
"""

# Advanced QR feature models
from .advanced import AdvancedQRConfig

# Core configuration models
from .core import DebugConfig, PerformanceConfig, RenderingConfig

# Geometry and shape models
from .geometry import FinderConfig, GeometryConfig

# Phase processing models
from .phases import Phase1Config, Phase2Config, Phase3Config

# Visual styling models
from .visual import (
    CenterpieceConfig,
    FrameConfig,
    PatternStyleConfig,
    QuietZoneConfig,
    StyleConfig,
)

__all__ = [
    # Core models
    "RenderingConfig",
    "PerformanceConfig",
    "DebugConfig",
    # Geometry models
    "GeometryConfig",
    "FinderConfig",
    # Visual models
    "PatternStyleConfig",
    "FrameConfig",
    "CenterpieceConfig",
    "QuietZoneConfig",
    "StyleConfig",
    # Phase models
    "Phase1Config",
    "Phase2Config",
    "Phase3Config",
    # Advanced models
    "AdvancedQRConfig",
]
