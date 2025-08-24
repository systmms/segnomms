Main Functions
==============

This module contains the primary functions for generating interactive SVG QR codes.

.. automodule:: segnomms.plugin.interface
   :members:
   :undoc-members:
   :show-inheritance:

Write Function
--------------

.. autofunction:: segnomms.write

The ``write`` function is the main entry point for using the plugin. It accepts
a Segno QR code object and writes it to the specified output with custom shapes
and styling options.

Parameters Reference
--------------------

Shape Parameters
~~~~~~~~~~~~~~~~

Different shapes accept different parameters:

.. list-table:: Shape-Specific Parameters
   :header-rows: 1

   * - Shape
     - Parameter
     - Type
     - Default
     - Description
   * - circle
     - size_ratio
     - float
     - 0.9
     - Circle size relative to module
   * - dot
     - size_ratio
     - float
     - 0.6
     - Dot size relative to module
   * - star
     - star_points
     - int
     - 5
     - Number of star points
   * - star
     - inner_ratio
     - float
     - 0.5
     - Inner to outer radius ratio
   * - triangle
     - direction
     - str
     - 'up'
     - Direction: up, down, left, right
   * - hexagon
     - size_ratio
     - float
     - 0.9
     - Hexagon size relative to module
   * - cross
     - thickness
     - float
     - 0.2
     - Cross arm thickness
   * - cross
     - sharp
     - bool
     - False
     - Use tapered arms

Core Parameters
~~~~~~~~~~~~~~~

.. list-table:: Core Rendering Parameters
   :header-rows: 1

   * - Parameter
     - Type
     - Default
     - Description
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
   * - merge
     - str
     - 'none'
     - Merging strategy: 'none', 'soft', 'aggressive'

Phase 4 Parameters
~~~~~~~~~~~~~~~~~~

Frame Shape Parameters
^^^^^^^^^^^^^^^^^^^^^^

.. list-table:: Frame Shape Configuration
   :header-rows: 1

   * - Parameter
     - Type
     - Default
     - Description
   * - frame_shape
     - str
     - 'square'
     - Frame type: 'square', 'circle', 'rounded-rect', 'squircle', 'custom'
   * - frame_corner_radius
     - float
     - 0.0
     - Corner radius for rounded-rect (0.0-1.0)
   * - frame_clip_mode
     - str
     - 'clip'
     - Edge treatment: 'clip' (sharp) or 'fade' (gradient)
   * - frame_custom_path
     - str
     - None
     - Custom SVG path for 'custom' frame shape

Centerpiece Parameters
^^^^^^^^^^^^^^^^^^^^^^

.. list-table:: Centerpiece Logo Area Configuration
   :header-rows: 1

   * - Parameter
     - Type
     - Default
     - Description
   * - centerpiece_enabled
     - bool
     - False
     - Enable centerpiece area clearing
   * - centerpiece_shape
     - str
     - 'rect'
     - Logo area shape: 'rect', 'circle', 'squircle'
   * - centerpiece_size
     - float
     - 0.0
     - Size as fraction of QR code (0.0-0.5)
   * - centerpiece_offset_x
     - float
     - 0.0
     - X offset from center (-0.5 to 0.5)
   * - centerpiece_offset_y
     - float
     - 0.0
     - Y offset from center (-0.5 to 0.5)
   * - centerpiece_margin
     - int
     - 2
     - Module margin around centerpiece (0-10)

Quiet Zone Parameters
^^^^^^^^^^^^^^^^^^^^^

.. list-table:: Enhanced Quiet Zone Configuration
   :header-rows: 1

   * - Parameter
     - Type
     - Default
     - Description
   * - quiet_zone_style
     - str
     - 'none'
     - Background style: 'none', 'solid', 'gradient'
   * - quiet_zone_color
     - str
     - 'transparent'
     - Color for solid quiet zone
   * - quiet_zone_gradient
     - dict
     - None
     - Gradient config with type, colors, positions

Examples
--------

Basic usage::

    import segno
    from segnomms import write
    
    qr = segno.make("Hello, World!")
    with open('output.svg', 'w') as f:
        write(qr, f)

With custom shape and colors::

    with open('styled.svg', 'w') as f:
        write(qr, f,
              shape='connected',
              scale=20,
              dark='#1e40af',
              light='#dbeafe')

Star shape with parameters::

    with open('star.svg', 'w') as f:
        write(qr, f,
              shape='star',
              star_points=8,
              inner_ratio=0.3)

Phase 4 Examples
~~~~~~~~~~~~~~~~~

Circle frame with centerpiece::

    with open('circle_frame.svg', 'w') as f:
        write(qr, f,
              frame_shape='circle',
              centerpiece_enabled=True,
              centerpiece_shape='circle',
              centerpiece_size=0.15,
              border=6)

Professional business card style::

    with open('business_card.svg', 'w') as f:
        write(qr, f,
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
              merge='soft')

Event poster with vibrant styling::

    with open('event_poster.svg', 'w') as f:
        write(qr, f,
              scale=25,
              border=8,
              frame_shape='circle',
              frame_clip_mode='fade',
              centerpiece_enabled=True,
              centerpiece_size=0.16,
              centerpiece_offset_x=0.1,
              quiet_zone_style='gradient',
              quiet_zone_gradient={
                  'type': 'linear',
                  'x1': '0%', 'y1': '0%',
                  'x2': '100%', 'y2': '100%',
                  'colors': ['#7c3aed', '#c084fc']
              },
              shape='star',
              dark='#ffffff')