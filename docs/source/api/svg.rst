SVG Generation
==============

This module handles SVG document generation and manipulation for QR codes.

SVG Builder System
------------------

.. automodule:: segnomms.svg
   :members:
   :undoc-members:
   :show-inheritance:

Main SVG Builder
----------------

.. autoclass:: segnomms.svg.InteractiveSVGBuilder
   :members:
   :undoc-members:
   :show-inheritance:

The ``InteractiveSVGBuilder`` is the main composite builder that orchestrates
all specialized builders to create complete interactive SVG documents.

Core SVG Builder
----------------

.. autoclass:: segnomms.svg.CoreSVGBuilder
   :members:
   :undoc-members:
   :show-inheritance:

Path Clipping
-------------

.. autoclass:: segnomms.svg.PathClipper
   :members:
   :undoc-members:
   :show-inheritance:

SVG Models
----------

.. automodule:: segnomms.svg.models
   :members:
   :undoc-members:
   :show-inheritance:

These models provide type-safe configuration for SVG generation parameters.

Example Usage
-------------

Basic SVG generation::

    from segnomms.svg import InteractiveSVGBuilder
    
    builder = InteractiveSVGBuilder()
    svg_root = builder.create_svg_root(200, 200)
    builder.add_styles(svg_root, interactive=True)
    builder.add_background(svg_root, 200, 200, 'white')

Path clipping for frames::

    from segnomms.svg import PathClipper
    
    clipper = PathClipper(
        frame_shape='circle',
        width=200,
        height=200,
        border=20
    )
    clipped_path = clipper.clip_path_to_frame(original_path)