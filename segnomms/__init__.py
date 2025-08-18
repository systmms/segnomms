"""Segno Interactive SVG Plugin.

A modular plugin for generating interactive SVG QR codes with custom shapes,
advanced clustering, and dynamic styling capabilities.

This plugin extends Segno's SVG output capabilities with:

* Multiple shape renderers (square, circle, star, connected shapes, etc.)
* Context-aware shapes that adapt based on neighboring modules
* Safe mode to preserve QR code scannability
* CSS classes for styling and interactivity
* Modular architecture for easy extension

Example:
    Basic usage with the write function::

        import segno
        from segnomms import write

        qr = segno.make("Hello, World!")
        with open('output.svg', 'w') as f:
            write(qr, f, shape='connected', scale=10)

Note:
    This plugin requires Segno 1.5.0 or higher.

"""

from .algorithms.clustering import ConnectedComponentAnalyzer
from .config.schema import Phase1Config, Phase2Config, Phase3Config, RenderingConfig
from .core.detector import ModuleDetector
from .core.interfaces import AlgorithmProcessor, RendererFactory, ShapeRenderer

# Import the main write function
from .plugin import generate_interactive_svg, write
from .shapes.factory import (
    create_shape_renderer,
    get_shape_factory,
    register_custom_renderer,
)
from .utils.svg_builder import InteractiveSVGBuilder

# Version information
__version__ = "0.0.0-beta001"
__author__ = "QRCodeMMS"

# Export main functionality
__all__ = [
    # Main functions
    "write",
    "generate_interactive_svg",
    # Core classes
    "ModuleDetector",
    "RenderingConfig",
    "InteractiveSVGBuilder",
    # Configuration classes
    "Phase1Config",
    "Phase2Config",
    "Phase3Config",
    # Factory functions
    "get_shape_factory",
    "create_shape_renderer",
    "register_custom_renderer",
    # Algorithm classes
    "ConnectedComponentAnalyzer",
    # Interfaces for extension
    "ShapeRenderer",
    "AlgorithmProcessor",
    "RendererFactory",
]

# Plugin metadata for segno registration
PLUGIN_NAME = "interactive_svg"
PLUGIN_VERSION = __version__
