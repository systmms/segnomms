"""Utility components for SVG generation and manipulation.

This package provides essential utilities for creating interactive
SVG documents with proper structure, styling, and metadata.

Key Components:

    :class:`InteractiveSVGBuilder`: Main builder for creating SVG documents
        with support for CSS styling, backgrounds, and interactive features.

The utilities handle:

* SVG document structure and namespaces
* CSS style injection and management
* Background and foreground layering
* Interactive hover effects and tooltips
* Proper XML formatting and encoding

Example:
    Basic usage of the SVG builder::

        from segnomms.utils import InteractiveSVGBuilder

        builder = InteractiveSVGBuilder()
        svg_root = builder.create_svg_root(200, 200)
        builder.add_styles(svg_root, interactive=True)
        builder.add_background(svg_root, 200, 200, 'white')

See Also:
    :mod:`segnomms.utils.svg_builder`: SVG building implementation
"""

from .svg_builder import InteractiveSVGBuilder

__all__ = ["InteractiveSVGBuilder"]
