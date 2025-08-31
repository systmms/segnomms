Frame Shapes
============

This module provides frame shape generators for Phase 4 QR code rendering.

Frame Shape Generator
---------------------

.. automodule:: segnomms.shapes.frames
   :members:
   :undoc-members:
   :show-inheritance:

The ``FrameShapeGenerator`` class provides static methods for generating
SVG clipping paths and masks for various frame shapes.

Available Frame Shapes
----------------------

.. autoclass:: segnomms.shapes.frames.FrameShapeGenerator
   :members:
   :undoc-members:
   :show-inheritance:

Supported frame shapes include:

* **square**: Standard rectangular QR code (default)
* **circle**: Circular boundary with equal radius
* **rounded-rect**: Rectangle with customizable corner radius
* **squircle**: Modern superellipse shape (between square and circle)
* **custom**: User-defined SVG path

Examples
--------

Circular Frame::

    from segnomms.shapes.frames import FrameShapeGenerator

    # Generate circular clipping path
    circle_clip = FrameShapeGenerator.generate_circle_clip(200, 200)
    print(circle_clip)  # <circle cx="100" cy="100" r="100"/>

Rounded Rectangle::

    # Generate rounded rectangle with 20% corner radius
    rounded_clip = FrameShapeGenerator.generate_rounded_rect_clip(
        200, 200, border=10, corner_radius=0.2
    )

Custom Frame Shape::

    # Use with a custom SVG path via the main write() API
    diamond_path = "M 100 0 L 200 100 L 100 200 L 0 100 Z"
    # See usage with QR codes below for passing frame_custom_path

Usage with QR Codes
-------------------

Frame shapes are typically used through the main ``write`` function::

    import segno
    from segnomms import write

    qr = segno.make("https://example.com", error='h')

    # Circle frame
    with open('circle_frame.svg', 'w') as f:
        write(qr, f, frame_shape='circle', border=6)

    # Rounded rectangle frame
    with open('rounded_frame.svg', 'w') as f:
        write(qr, f,
              frame_shape='rounded-rect',
              frame_corner_radius=0.3,
              border=5)

    # Custom diamond frame
    with open('diamond_frame.svg', 'w') as f:
        write(qr, f,
              frame_shape='custom',
              frame_custom_path="M 100 0 L 200 100 L 100 200 L 0 100 Z",
              border=8)
