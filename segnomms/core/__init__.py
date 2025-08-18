"""
Core components for the segno interactive SVG plugin.

This package contains the fundamental interfaces and base classes
that define the plugin's architecture.
"""

from .detector import ModuleDetector
from .interfaces import (
    AlgorithmProcessor,
    ConfigurationProvider,
    ModuleAnalyzer,
    QRCodeAnalyzer,
    RendererFactory,
    ShapeRenderer,
    SVGBuilder,
)

__all__ = [
    "ModuleAnalyzer",
    "ShapeRenderer",
    "AlgorithmProcessor",
    "ConfigurationProvider",
    "RendererFactory",
    "SVGBuilder",
    "QRCodeAnalyzer",
    "ModuleDetector",
]
