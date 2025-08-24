"""SVG generation and manipulation subsystem.

This package provides comprehensive SVG document creation, styling,
and manipulation capabilities for QR code generation.

Key Components:

    :class:`InteractiveSVGBuilder`: Main builder for creating SVG documents
        with support for CSS styling, backgrounds, and interactive features.

    :class:`PathClipper`: Utilities for clipping SVG paths to frame boundaries.

The SVG subsystem handles:

* SVG document structure and namespaces
* CSS style injection and management
* Background and foreground layering
* Interactive hover effects and tooltips
* Proper XML formatting and encoding
* Path manipulation and clipping
* Frame boundary enforcement

Example:
    Basic usage of the SVG builder::

        from segnomms.svg import InteractiveSVGBuilder

        builder = InteractiveSVGBuilder()
        svg_root = builder.create_svg_root(200, 200)
        builder.add_styles(svg_root, interactive=True)
        builder.add_background(svg_root, 200, 200, 'white')

See Also:
    :mod:`segnomms.svg.core`: Core SVG building implementation
    :mod:`segnomms.svg.interactivity`: Interactive features
    :mod:`segnomms.svg.path_clipper`: Path clipping utilities
"""

from .accessibility import AccessibilityBuilder
from .composite import InteractiveSVGBuilder
from .core import CoreSVGBuilder
from .definitions import DefinitionsBuilder
from .frame_visual import FrameVisualBuilder
from .interactivity import InteractivityBuilder
from .models import (
    BackgroundConfig,
    CenterpieceMetadataConfig,
    FrameDefinitionConfig,
    GradientConfig,
    InteractionConfig,
    LayerStructureConfig,
    SVGElementConfig,
    TitleDescriptionConfig,
)
from .path_clipper import PathClipper

__all__ = [
    "InteractiveSVGBuilder",  # Main composite builder
    "CoreSVGBuilder",
    "DefinitionsBuilder",
    "InteractivityBuilder",
    "FrameVisualBuilder",
    "AccessibilityBuilder",
    "PathClipper",
    # SVG Models
    "SVGElementConfig",
    "BackgroundConfig",
    "GradientConfig",
    "TitleDescriptionConfig",
    "InteractionConfig",
    "FrameDefinitionConfig",
    "LayerStructureConfig",
    "CenterpieceMetadataConfig",
]
