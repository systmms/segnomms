"""
Configuration components for the plugin.

This package contains configuration schemas and management utilities
for the interactive SVG plugin.
"""

# Import all enums for backward compatibility
from .enums import (
    ConnectivityMode,
    ContourMode,
    FinderShape,
    MergeStrategy,
    ModuleShape,
    OptimizationLevel,
    PlacementMode,
    ReserveMode,
)

# Import all models for backward compatibility
from .models import (
    AdvancedQRConfig,
    CenterpieceConfig,
    DebugConfig,
    FinderConfig,
    FrameConfig,
    GeometryConfig,
    PatternStyleConfig,
    PerformanceConfig,
    Phase1Config,
    Phase2Config,
    Phase3Config,
    QuietZoneConfig,
    RenderingConfig,
    StyleConfig,
)

# Import presets
from .presets import ConfigPresets

__all__ = [
    # Enums
    "ConnectivityMode",
    "MergeStrategy",
    "ReserveMode",
    "PlacementMode",
    "ModuleShape",
    "FinderShape",
    "ContourMode",
    "OptimizationLevel",
    # Core models
    "RenderingConfig",
    "PerformanceConfig",
    "DebugConfig",
    # Component models
    "GeometryConfig",
    "FinderConfig",
    "PatternStyleConfig",
    "FrameConfig",
    "CenterpieceConfig",
    "QuietZoneConfig",
    "StyleConfig",
    "Phase1Config",
    "Phase2Config",
    "Phase3Config",
    "AdvancedQRConfig",
    # Presets
    "ConfigPresets",
]
