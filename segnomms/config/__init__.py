"""
Configuration components for the plugin.

This package contains configuration schemas and management utilities
for the interactive SVG plugin.
"""

from .schema import (
    ContourMode,
    DebugConfig,
    OptimizationLevel,
    PerformanceConfig,
    Phase1Config,
    Phase2Config,
    Phase3Config,
    RenderingConfig,
    StyleConfig,
)

__all__ = [
    "ContourMode",
    "OptimizationLevel",
    "Phase1Config",
    "Phase2Config",
    "Phase3Config",
    "StyleConfig",
    "RenderingConfig",
    "PerformanceConfig",
    "DebugConfig",
]
