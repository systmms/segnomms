"""SegnoMMS Plugin Module.

This module provides the main interface for the Segno Interactive SVG Plugin.
The plugin has been refactored into modular components for better maintainability.

Main API functions:
    - write(): Generate interactive SVG from QR code
    - write_advanced(): Generate QR code with advanced features
    - register_with_segno(): Register plugin with Segno

Modules:
    - interface: Main API functions
    - config: Configuration processing and validation
    - export: File export and naming utilities
    - rendering: SVG generation orchestration
    - patterns: Pattern-specific processing utilities
"""

# Import utility functions that were previously exposed
from .export import _export_configuration, _generate_config_hash

# Import main API functions for backward compatibility
from .interface import register_with_segno, write, write_advanced
from .patterns import _get_pattern_specific_render_kwargs, _get_pattern_specific_style
from .rendering import (
    MAX_QR_SIZE,
    _detect_and_remove_islands,
    _format_svg_string,
    _get_enhanced_render_kwargs,
    _render_cluster,
    generate_interactive_svg,
)

# Keep the same public API
__all__ = [
    "write",
    "write_advanced",
    "register_with_segno",
    "generate_interactive_svg",
    "_export_configuration",
    "_generate_config_hash",
    "_get_pattern_specific_style",
    "_get_pattern_specific_render_kwargs",
    "_render_cluster",
    "_get_enhanced_render_kwargs",
    "_format_svg_string",
    "_detect_and_remove_islands",
    "MAX_QR_SIZE",
]
