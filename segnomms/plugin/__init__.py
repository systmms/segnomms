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

# Import main API functions
from .interface import register_with_segno, write, write_advanced
from .rendering import MAX_QR_SIZE, generate_interactive_svg

# Public API only - internal functions are still importable via direct import
# from their respective modules (e.g., from segnomms.plugin.export import _export_configuration)
__all__ = [
    "write",
    "write_advanced",
    "register_with_segno",
    "generate_interactive_svg",
    "MAX_QR_SIZE",
]
