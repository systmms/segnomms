Constants Module
================

The constants module provides convenient access to commonly used enums, constants,
and utilities for working with SegnoMMS configurations.

.. currentmodule:: segnomms.constants

Enums
-----

ModuleShape
~~~~~~~~~~~

.. autoclass:: segnomms.config.enums.ModuleShape
   :members:
   :undoc-members:
   :member-order: bysource

Available module shapes:

* ``SQUARE`` - Classic square modules
* ``CIRCLE`` - Circular dots
* ``ROUNDED`` - Rounded squares
* ``DOT`` - Small dots with gaps
* ``DIAMOND`` - Diamond shapes
* ``STAR`` - Star shapes
* ``HEXAGON`` - Hexagonal modules
* ``TRIANGLE`` - Triangle shapes
* ``SQUIRCLE`` - Superellipse shapes
* ``CROSS`` - Plus/cross shapes
* ``CONNECTED`` - Connected shapes with pill-style merging
* ``CONNECTED_EXTRA_ROUNDED`` - Extra rounded connected shapes
* ``CONNECTED_CLASSY`` - Classy connected shapes
* ``CONNECTED_CLASSY_ROUNDED`` - Classy rounded connected shapes

Example:

.. code-block:: python

   from segnomms.constants import ModuleShape
   from segnomms import write
   import segno

   qr = segno.make("Hello World")
   with open('output.svg', 'w') as f:
       write(qr, f, shape=ModuleShape.CIRCLE.value, scale=10)

FinderShape
~~~~~~~~~~~

.. autoclass:: segnomms.config.enums.FinderShape
   :members:
   :undoc-members:
   :member-order: bysource

Available finder pattern shapes:

* ``SQUARE`` - Square finder patterns
* ``ROUNDED`` - Rounded finder patterns
* ``CIRCLE`` - Circular finder patterns

Constants
---------

Shape Collections
~~~~~~~~~~~~~~~~~

.. py:data:: VALID_SHAPES
   :type: list[ModuleShape]

   List of all valid module shapes available in SegnoMMS.

.. py:data:: CONNECTED_SHAPES
   :type: list[ModuleShape]

   List of connected shape variants (CONNECTED, CONNECTED_EXTRA_ROUNDED,
   CONNECTED_CLASSY, CONNECTED_CLASSY_ROUNDED).

.. py:data:: BASIC_SHAPES
   :type: list[ModuleShape]

   List of basic (non-connected) module shapes.

.. py:data:: FINDER_SHAPES
   :type: list[FinderShape]

   List of available finder pattern shapes.

Default Values
~~~~~~~~~~~~~~

.. py:data:: DEFAULT_SCALE
   :type: int
   :value: 10

   Default scale factor for QR code modules (pixels per module).

.. py:data:: DEFAULT_BORDER
   :type: int
   :value: 4

   Default border size in modules (quiet zone around QR code).

.. py:data:: DEFAULT_DARK
   :type: str
   :value: "#000000"

   Default dark module color (black).

.. py:data:: DEFAULT_LIGHT
   :type: str
   :value: "#FFFFFF"

   Default light module color (white).

Test Constants
~~~~~~~~~~~~~~

.. py:data:: TEST_COLORS
   :type: dict[str, str]

   Common colors for examples and testing. Contains predefined colors:

   * ``black`` - #000000
   * ``white`` - #FFFFFF
   * ``red`` - #FF0000
   * ``green`` - #00FF00
   * ``blue`` - #0000FF
   * ``transparent`` - transparent
   * ``brand_primary`` - #1a1a2e
   * ``brand_secondary`` - #f5f5f5

   Example:

   .. code-block:: python

      from segnomms.constants import TEST_COLORS
      from segnomms import write
      import segno

      qr = segno.make("Blue QR Code")
      with open('blue.svg', 'w') as f:
          write(qr, f, dark=TEST_COLORS["blue"], scale=10)

.. py:data:: QR_PAYLOADS
   :type: dict[str, str]

   Common QR code payloads for examples and testing. Contains:

   * ``simple`` - "Hello World"
   * ``url`` - "https://example.com"
   * ``url_complex`` - "https://example.com/path?param1=value1&param2=value2"
   * ``email`` - "mailto:test@example.com"
   * ``phone`` - "tel:+1234567890"
   * ``wifi`` - WiFi configuration string
   * ``unicode`` - Unicode text example
   * ``numeric`` - Numeric-only payload
   * ``alphanumeric`` - Alphanumeric payload

   Example:

   .. code-block:: python

      from segnomms.constants import QR_PAYLOADS
      import segno

      # Create QR codes for different payload types
      for name, payload in QR_PAYLOADS.items():
          qr = segno.make(payload)
          qr.save(f'{name}.svg')

Utility Functions
-----------------

.. autofunction:: get_shape_enum

   Convert a shape string to ModuleShape enum.

   Example:

   .. code-block:: python

      from segnomms.constants import get_shape_enum

      shape = get_shape_enum("circle")
      print(shape)  # ModuleShape.CIRCLE

.. autofunction:: create_config

   Create a configuration dictionary with sensible defaults.

   Example:

   .. code-block:: python

      from segnomms.constants import create_config, ModuleShape

      config = create_config(
          shape=ModuleShape.CIRCLE.value,
          scale=15,
          dark="#0066cc"
      )
      # Returns: {'scale': 15, 'border': 4, 'dark': '#0066cc',
      #           'light': '#FFFFFF', 'shape': 'circle'}

Complete Example
----------------

Combining multiple constants for a complete workflow:

.. code-block:: python

   from segnomms.constants import (
       ModuleShape,
       TEST_COLORS,
       QR_PAYLOADS,
       DEFAULT_SCALE,
       create_config
   )
   from segnomms import write
   import segno

   # Generate QR codes with different shapes and colors
   shapes = [ModuleShape.CIRCLE, ModuleShape.ROUNDED, ModuleShape.SQUIRCLE]
   colors = ["blue", "red", "brand_primary"]

   for shape, color_name in zip(shapes, colors):
       qr = segno.make(QR_PAYLOADS["url"])
       config = create_config(
           shape=shape.value,
           dark=TEST_COLORS[color_name],
           scale=DEFAULT_SCALE
       )

       filename = f'qr_{shape.value}_{color_name}.svg'
       with open(filename, 'w') as f:
           write(qr, f, **config)
