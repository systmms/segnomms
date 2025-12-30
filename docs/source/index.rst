.. SegnoMMS documentation master file

Welcome to SegnoMMS
===================

SegnoMMS extends `Segno <https://segno.readthedocs.io/>`_ with advanced SVG rendering capabilities, providing various shape options and interactive features for QR codes.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   quickstart
   api/index
   shapes
   visual-gallery
   examples
   testing/index
   decoder_compatibility
   developer/index
   migration/index
   contributing

Features
--------

* **Intent-Based API**: High-level, declarative QR generation with :doc:`error handling <api/exceptions>` and :doc:`graceful degradation <api/degradation>`
* **Type-Safe Configuration**: Pydantic-powered configuration with automatic validation and JSON Schema generation
* **Multiple Shape Types**: 14+ different module shapes including squares, circles, stars, and more
* **Connected Shapes**: Context-aware shapes that adapt based on neighboring modules
* **Safe Mode**: Preserves QR code scannability by using simple shapes for critical patterns
* **Customizable**: Full control over colors, sizes, and shape-specific parameters
* **Interactive SVG**: CSS classes for styling and animation
* **CSS Animations**: Fade-in, staggered reveals, and pulse effects with accessibility support
* **Phase 4 Features**: Custom frame shapes, centerpiece logo areas, and gradient backgrounds
* **Production Ready**: Comprehensive :doc:`error handling <api/exceptions>` and :doc:`testing framework <testing/index>`

Quick Example
-------------

Modern Intent-Based API:

.. code-block:: python

   from segnomms.intents import render_with_intents
   from segnomms.intents.models import PayloadConfig, IntentsConfig, StyleIntents

   # Define your intentions declaratively
   intents = IntentsConfig(
       style=StyleIntents(
           module_shape="squircle",
           palette={"fg": "#1a1a2e", "bg": "#ffffff"}
       )
   )

   # Generate with automatic error handling and degradation
   payload = PayloadConfig(text="Hello, World!")
   result = render_with_intents(payload, intents)

   # Check for any warnings
   if result.has_warnings:
       for warning in result.warnings:
           print(f"Notice: {warning.detail}")

   with open('modern-qr.svg', 'w') as f:
       f.write(result.svg_content)

Traditional Write API (for simple cases):

.. code-block:: python

   import segno
   from segnomms import write

   # Create a QR code
   qr = segno.make("Hello, World!")

   # Basic connected shape
   with open('basic.svg', 'w') as f:
       write(qr, f, shape='connected', scale=10, border=2)

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
