Color Analysis
==============

This module provides color analysis and palette management capabilities.

Color Analysis Functions
-------------------------

.. automodule:: segnomms.color
   :members:
   :undoc-members:
   :show-inheritance:

Core Functions
--------------

.. autofunction:: segnomms.color.calculate_contrast_ratio
   :no-index:

.. autofunction:: segnomms.color.calculate_luminance
   :no-index:

.. autofunction:: segnomms.color.parse_color
   :no-index:

Palette Management
------------------

.. autoclass:: segnomms.color.PaletteConfig
   :no-index:
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: segnomms.color.PaletteValidationResult
   :no-index:
   :members:
   :undoc-members:
   :show-inheritance:

Color Standards
---------------

.. autoclass:: segnomms.color.ContrastStandard
   :no-index:
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: segnomms.color.ColorSpace
   :no-index:
   :members:
   :undoc-members:
   :show-inheritance:

Example Usage
-------------

Color contrast analysis::

    from segnomms.color import calculate_contrast_ratio, parse_color

    dark = parse_color("#1a1a2e")
    light = parse_color("#ffffff")
    ratio = calculate_contrast_ratio(dark, light)
    print(f"Contrast ratio: {ratio:.2f}:1")

Palette validation::

    from segnomms.color import PaletteConfig, ContrastStandard

    palette = PaletteConfig(
        foreground="#1a1a2e",
        background="#ffffff",
        standard=ContrastStandard.AA_NORMAL
    )
    is_valid = palette.validate_contrast()
