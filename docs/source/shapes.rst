Shape Reference
===============

This plugin supports a variety of shape types for QR code modules, from simple geometric shapes
to sophisticated connected patterns that adapt based on neighboring modules.

.. contents:: Table of Contents
   :local:
   :depth: 2

Shape Categories
----------------

Basic Shapes
~~~~~~~~~~~~

Basic shapes are simple geometric forms that render each module independently:

* **square** - Traditional square modules (default)
* **circle** - Circular modules
* **dot** - Small circular dots
* **diamond** - Diamond/rhombus shapes
* **star** - Star shapes with configurable points
* **triangle** - Triangular modules with directional options
* **hexagon** - Six-sided polygons
* **cross** - Plus/cross shapes

Connected Shapes
~~~~~~~~~~~~~~~~

Connected shapes are context-aware and change appearance based on neighboring modules:

* **connected** - Basic connected style with rounded corners
* **connected-extra-rounded** - Extra smooth connected curves
* **connected-classy** - Sophisticated boundary styling
* **connected-classy-rounded** - Elegant rounded boundary styling

Shape Details
-------------

Square
~~~~~~

.. code-block:: python

   write(qr, f, shape='square')

The default shape providing maximum compatibility and scannability.

**Parameters:** None

Circle
~~~~~~

.. code-block:: python

   write(qr, f, shape='circle', size_ratio=0.9)

Circular modules for a softer appearance.

**Parameters:**

* ``size_ratio`` (float, 0.1-1.0): Circle diameter relative to module size (default: 0.9)

Dot
~~~

.. code-block:: python

   write(qr, f, shape='dot', size_ratio=0.6)

Small dots for minimalist designs.

**Parameters:**

* ``size_ratio`` (float, 0.1-1.0): Dot diameter relative to module size (default: 0.6)

Diamond
~~~~~~~

.. code-block:: python

   write(qr, f, shape='diamond')

Diamond-shaped modules for geometric patterns.

**Parameters:** None

Star
~~~~

.. code-block:: python

   write(qr, f, shape='star', star_points=5, inner_ratio=0.5)

Configurable star shapes for decorative designs.

**Parameters:**

* ``star_points`` (int, 3-12): Number of star points (default: 5)
* ``inner_ratio`` (float, 0.1-0.9): Ratio of inner to outer radius (default: 0.5)

Triangle
~~~~~~~~

.. code-block:: python

   write(qr, f, shape='triangle', direction='up')

Directional triangular modules.

**Parameters:**

* ``direction`` (str): Triangle direction - 'up', 'down', 'left', 'right' (default: 'up')

Hexagon
~~~~~~~

.. code-block:: python

   write(qr, f, shape='hexagon', size_ratio=0.9)

Hexagonal modules for honeycomb patterns.

**Parameters:**

* ``size_ratio`` (float, 0.1-1.0): Hexagon size relative to module (default: 0.9)

Cross
~~~~~

.. code-block:: python

   write(qr, f, shape='cross', thickness=0.2, sharp=False)

Cross/plus shaped modules.

**Parameters:**

* ``thickness`` (float, 0.1-0.5): Thickness of cross arms (default: 0.2)
* ``sharp`` (bool): Use tapered arms for sharper appearance (default: False)

Rounded
~~~~~~~

.. code-block:: python

   write(qr, f, shape='rounded', roundness=0.3)

Square modules with rounded corners for a softer appearance.

**Parameters:**

* ``roundness`` (float, 0.0-0.5): Corner radius as fraction of module size (default: 0.3)

Squircle
~~~~~~~~

.. code-block:: python

   write(qr, f, shape='squircle', corner_radius=0.35)

Superellipse shape - a sophisticated blend between square and circle.

**Parameters:**

* ``corner_radius`` (float, 0.0-1.0): Corner radius as fraction of module size (default: 0.35)

Connected
~~~~~~~~~

.. code-block:: python

   write(qr, f, shape='connected')

Basic connected style that creates smooth paths between adjacent modules.

**Behavior:**

* Single modules: Rounded square
* Lines: Connected with rounded ends
* Corners: Smooth rounded transitions
* Complex patterns: Adaptive connections

Connected Extra Rounded
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   write(qr, f, shape='connected-extra-rounded')

Enhanced connected style with extra smooth curves and transitions.

**Behavior:**

* More pronounced rounding than basic connected
* Smoother transitions at intersections
* Organic, flowing appearance

Connected Classy
~~~~~~~~~~~~~~~~

.. code-block:: python

   write(qr, f, shape='connected-classy')

Sophisticated style that emphasizes boundaries of larger shapes.

**Behavior:**

* Isolated modules: Jewel-like shape with opposite corners rounded
* Outer corners: Single rounded corner
* Inner positions: Solid squares
* Creates elegant boundary definition

Connected Classy Rounded
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   write(qr, f, shape='connected-classy-rounded')

Like connected-classy but with extra-rounded drawing for smoother appearance.

**Behavior:**

* Same logic as connected-classy
* Uses quadratic bezier curves for ultra-smooth corners
* Most sophisticated appearance

Safe Mode
---------

The ``safe_mode`` parameter (default: True) affects how shapes are applied:

.. code-block:: python

   # Safe mode ON - special patterns use simple squares
   write(qr, f, shape='star', safe_mode=True)

   # Safe mode OFF - all modules use the selected shape
   write(qr, f, shape='star', safe_mode=False)

When ``safe_mode=True``:

* Finder patterns use simple squares
* Timing patterns use simple squares
* Alignment patterns use simple squares
* Format information uses simple squares
* Only data modules use the selected shape

This ensures maximum scannability while still providing visual interest.

Safe Mode Scope Reference
~~~~~~~~~~~~~~~~~~~~~~~~~

**Protected Patterns (always use simple squares when safe_mode=True):**

* **Finder patterns** - Three large corner squares essential for QR detection
* **Timing patterns** - Alternating modules that help determine grid alignment
* **Alignment patterns** - Small squares for correcting distortion (larger QR codes)
* **Format information** - Encodes error correction level and mask pattern

**Unprotected Patterns (use selected shape regardless of safe_mode):**

* **Data modules** - The payload-carrying modules that encode your content
* **Version information** - Encodes QR version number (for versions 7+)

**Why These Patterns Are Protected:**

The protected patterns are critical for QR code detection and decoding. Finder patterns
must maintain their distinctive appearance for scanners to locate the QR code. Timing
patterns help calculate module positions. Altering these with non-standard shapes can
significantly impact scannability, especially with older or less sophisticated decoders.

Visual Examples
---------------

To generate visual examples of all shapes for comparison:

.. code-block:: bash

   # Generate example QR codes with different shapes
   python -c "
   import segno
   from segnomms import write

   shapes = ['square', 'circle', 'dot', 'diamond', 'rounded', 'connected']
   for shape in shapes:
       qr = segno.make('https://example.com')
       write(qr, f'{shape}_example.svg', shape=shape, scale=10)
       print(f'Generated {shape}_example.svg')
   "

This will create SVG files for each shape type that you can view in your browser
to compare their visual appearance.

.. note::
   For production use, test your specific shape configuration with target QR code
   scanners to ensure compatibility. See :doc:`decoder_compatibility` for detailed
   testing guidance.

Shape Selection Guide
---------------------

**Maximum Compatibility**
   Use ``square`` with ``safe_mode=True``

**Modern, Clean Look**
   Try ``circle``, ``dot``, or ``connected``

**Decorative/Artistic**
   Consider ``star``, ``diamond``, or ``hexagon``

**Sophisticated Branding**
   Use ``connected-classy`` or ``connected-classy-rounded``

**Organic, Natural**
   Choose ``connected-extra-rounded``

**Technical/Minimal**
   Try ``cross`` with ``sharp=True``

Related Documentation
---------------------

- :doc:`quickstart` - Getting started guide with basic shape usage
- :doc:`decoder_compatibility` - How different shapes affect scanner compatibility
- :doc:`examples` - Advanced usage patterns and integration examples
- :doc:`api/index` - Complete API reference for shape parameters
