Configuration
=============

This module handles configuration and parameter validation for the plugin.

Configuration Models
--------------------

.. automodule:: segnomms.config.models.core
   :members:
   :undoc-members:
   :show-inheritance:

Main Configuration Class
------------------------

.. autoclass:: segnomms.config.models.core.RenderingConfig
   :members:
   :undoc-members:
   :show-inheritance:

The ``RenderingConfig`` class is the main configuration object that controls
all aspects of QR code rendering.

Example Usage
~~~~~~~~~~~~~

.. code-block:: python

   from segnomms.config import RenderingConfig

   # Create configuration from kwargs
   config = RenderingConfig.from_kwargs(
       shape='connected',
       scale=20,
       dark='#1e40af',
       light='#dbeafe',
       safe_mode=False
   )

   # Access configuration values
   print(config.shape)      # 'connected'
   print(config.scale)      # 20
   print(config.dark)       # '#1e40af'

Configuration Parameters
------------------------

Core Parameters
~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 20 15 15 50

   * - Parameter
     - Type
     - Default
     - Description
   * - shape
     - str
     - 'square'
     - Shape type for QR modules
   * - scale
     - int
     - 10
     - Size of each module in pixels
   * - border
     - int
     - 4
     - Quiet zone size in modules
   * - dark
     - str
     - 'black'
     - Color for dark modules
   * - light
     - str
     - 'white'
     - Color for light modules
   * - safe_mode
     - bool
     - True
     - Use simple shapes for special patterns

SVG Parameters
~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 20 15 15 50

   * - Parameter
     - Type
     - Default
     - Description
   * - xmldecl
     - bool
     - True
     - Include XML declaration
   * - svgclass
     - str
     - 'interactive-qr'
     - CSS class for SVG element
   * - lineclass
     - str
     - None
     - CSS class for path elements
   * - title
     - str
     - 'Interactive QR Code'
     - SVG title element
   * - desc
     - str
     - Auto
     - SVG description element
   * - svgid
     - str
     - 'qr-code'
     - ID for SVG element

Phase Configuration
-------------------

The plugin uses a three-phase processing pipeline for QR code rendering:

Phase 1 - Enhanced Context Detection
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Enhanced 8-neighbor context detection for context-aware shape selection.
This phase analyzes the connectivity of each module with its 8 surrounding
neighbors to determine optimal shape rendering.

.. autoclass:: segnomms.config.models.phases.Phase1Config
   :members:
   :undoc-members:

Phase 2 - Connected Component Clustering
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Connected component clustering for unified module group rendering.
This phase groups adjacent modules into clusters that can be rendered
as unified shapes rather than individual modules.

.. autoclass:: segnomms.config.models.phases.Phase2Config
   :members:
   :undoc-members:

Phase 3 - Marching Squares Contour Generation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Marching squares algorithm with Bezier curve smoothing for organic contours.
This phase generates smooth, organic contours around clustered modules using
the marching squares algorithm combined with Bezier curve interpolation.

.. autoclass:: segnomms.config.models.phases.Phase3Config
   :members:
   :undoc-members:

Plugin Configuration
--------------------

.. autoclass:: segnomms.config.models.core.DebugConfig
   :members:
   :undoc-members:

Composition Validation
----------------------

The ``CompositionValidator`` class validates the composition of QR code visual
elements including frames, centerpieces, and their interactions. Unlike the
three processing phases above, the composition validator is a validation system
that ensures your configuration choices maintain QR code scannability.

.. note::

   The ``CompositionValidator`` was previously named ``Phase4Validator``. The old
   name is retained as a deprecated alias for backward compatibility.

.. autoclass:: segnomms.validation.composition.CompositionValidator
   :members: validate_all, validate_frame_safety, validate_centerpiece_safety
   :undoc-members:

Frame and Centerpiece Configuration
------------------------------------

This section describes the configuration options for advanced visual features.

Frame Configuration
~~~~~~~~~~~~~~~~~~~

.. autoclass:: segnomms.config.models.visual.FrameConfig
   :members:
   :undoc-members:

Controls the outer boundary shape of QR codes. Available frame shapes:

* **square**: Standard rectangular boundary (default)
* **circle**: Circular boundary with automatic radius calculation
* **rounded-rect**: Rectangle with customizable corner radius
* **squircle**: Modern superellipse shape (between square and circle)
* **custom**: User-defined SVG path for unique shapes

Centerpiece Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: segnomms.config.models.visual.CenterpieceConfig
   :members:
   :undoc-members:

Manages logo area reservation in the center of QR codes. The centerpiece area
is automatically cleared of QR modules while preserving critical patterns like
finder patterns and timing patterns.

**Size Guidelines by Error Correction Level:**

* **L Level (7% recovery)**: Max 5% centerpiece - very conservative
* **M Level (15% recovery)**: Max 8% centerpiece - good for small logos
* **Q Level (25% recovery)**: Max 15% centerpiece - medium logos
* **H Level (30% recovery)**: Max 20% centerpiece - large logos

Quiet Zone Configuration
~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: segnomms.config.models.visual.QuietZoneConfig
   :members:
   :undoc-members:

Enhances the quiet zone (border area) around QR codes with solid colors
or gradient backgrounds for improved visual appeal and branding.

Shape Options
-------------

Shape-specific parameters can be passed through ``shape_options``:

.. code-block:: python

   config = RenderingConfig.from_kwargs(
       shape='star',
       shape_options={
           'star_points': 8,
           'inner_ratio': 0.3
       }
   )

Or passed directly as kwargs:

.. code-block:: python

   config = RenderingConfig.from_kwargs(
       shape='star',
       star_points=8,
       inner_ratio=0.3
   )

Phase 4 Configuration Examples
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Circle frame with centerpiece::

   config = RenderingConfig.from_kwargs(
       frame_shape='circle',
       centerpiece_enabled=True,
       centerpiece_shape='circle',
       centerpiece_size=0.15,
       border=6
   )

Professional business card configuration::

   config = RenderingConfig.from_kwargs(
       scale=20,
       border=6,
       frame_shape='rounded-rect',
       frame_corner_radius=0.2,
       centerpiece_enabled=True,
       centerpiece_shape='circle',
       centerpiece_size=0.12,
       quiet_zone_style='gradient',
       quiet_zone_gradient={
           'type': 'radial',
           'colors': ['#ffffff', '#f8f9fa']
       },
       shape='squircle',
       merge='soft'
   )

Direct configuration object creation::

   from segnomms.config import (
       RenderingConfig, FrameConfig, CenterpieceConfig, QuietZoneConfig
   )

   # Create individual config objects
   frame_config = FrameConfig(
       shape='squircle',
       clip_mode='fade'
   )

   centerpiece_config = CenterpieceConfig(
       enabled=True,
       shape='circle',
       size=0.14,
       margin=3
   )

   quiet_zone_config = QuietZoneConfig(
       style='gradient',
       gradient={
           'type': 'linear',
           'colors': ['#f8f9fa', '#e9ecef']
       }
   )

   # Combine into main config
   config = RenderingConfig(
       scale=18,
       border=5,
       frame=frame_config,
       centerpiece=centerpiece_config,
       quiet_zone=quiet_zone_config
   )
