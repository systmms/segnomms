Quick Start Guide
=================

This guide will help you get started with SegnoMMS.

Getting Started
---------------

SegnoMMS offers two primary APIs: the **Intent-Based API** (recommended for modern applications) and the **Legacy Write API** (for simple use cases).

Modern Intent-Based API (Recommended)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The intent-based API provides high-level, declarative QR code generation with built-in error handling and graceful degradation:

.. code-block:: python

   from segnomms.intents import render_with_intents
   from segnomms.intents.models import PayloadConfig, IntentsConfig, StyleIntents

   # Define your intentions
   intents = IntentsConfig(
       style=StyleIntents(
           module_shape="squircle",
           palette={"fg": "#1a1a2e", "bg": "#ffffff"},
           corner_radius=0.3
       )
   )

   # Generate QR with comprehensive error handling
   result = render_with_intents(PayloadConfig(text="Hello, World!"), intents)

   # Check results and handle any issues
   if result.has_warnings:
       for warning in result.warnings:
           print(f"Notice: {warning.detail}")

   # Save the result
   with open('modern-qr.svg', 'w') as f:
       f.write(result.svg_content)

Legacy Write API (Simple Cases)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For simple use cases, the traditional write function is still available:

.. code-block:: python

   import segno
   from segnomms import write

   # Create a QR code
   qr = segno.make("Hello, World!")

   # Save as SVG with default settings
   with open('simple.svg', 'w') as f:
       write(qr, f)

Type-Safe Configuration with Pydantic
--------------------------------------

SegnoMMS uses Pydantic for type-safe configuration with automatic validation:

.. code-block:: python

   from segnomms.config import RenderingConfig
   from pydantic import ValidationError

   # Type-safe configuration with validation
   try:
       config = RenderingConfig.from_kwargs(
           shape='squircle',
           corner_radius=0.3,
           scale=15,
           dark='#1a1a2e',
           light='#ffffff',
           interactive=True
       )
       print("Configuration is valid!")
   except ValidationError as e:
       print(f"Configuration error: {e}")

   # Use with legacy API
   qr = segno.make("Type-safe QR!")
   with open('validated.svg', 'w') as f:
       write(qr, f, **config.to_kwargs())

Intent-Based Shape Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The modern intent-based API makes shape configuration more intuitive:

.. code-block:: python

   from segnomms.intents.models import PayloadConfig, StyleIntents, FrameIntents, IntentsConfig
   from segnomms.intents import render_with_intents

   # Different shapes with intents
   circle_intents = IntentsConfig(
       style=StyleIntents(module_shape="circle")
   )

   connected_intents = IntentsConfig(
       style=StyleIntents(
           module_shape="connected",
           patterns={"finder": "rounded", "data": "connected"}
       )
   )

   star_intents = IntentsConfig(
       style=StyleIntents(
           module_shape="star",
           corner_radius=0.4  # Star-specific parameters
       )
   )

   # Generate with different configurations
   for name, intents in [("circle", circle_intents), ("connected", connected_intents), ("star", star_intents)]:
       result = render_with_intents(PayloadConfig(text="Hello!"), intents)
       with open(f'{name}.svg', 'w') as f:
           f.write(result.svg_content)

Legacy Shape API
~~~~~~~~~~~~~~~~~

For backward compatibility, the write function also supports various shape types:

.. code-block:: python

   # Circle shape
   with open('circle.svg', 'w') as f:
       write(qr, f, shape='circle')

   # Connected shape with smooth corners
   with open('connected.svg', 'w') as f:
       write(qr, f, shape='connected')

   # Star shape with custom parameters
   with open('star.svg', 'w') as f:
       write(qr, f, shape='star', star_points=8, inner_ratio=0.3)

Customizing Colors
------------------

Intent-Based Color Configuration (Recommended)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The intent-based API provides color palette configuration with automatic validation:

.. code-block:: python

   from segnomms.intents.models import PayloadConfig, IntentsConfig, StyleIntents
   from segnomms.intents import render_with_intents

   # Professional color palette
   professional_intents = IntentsConfig(
       style=StyleIntents(
           module_shape="squircle",
           palette={
               "fg": "#1e40af",    # Professional blue
               "bg": "#f8fafc"     # Light background
           }
       )
   )

   # High contrast for accessibility
   accessible_intents = IntentsConfig(
       style=StyleIntents(
           module_shape="rounded",
           palette={
               "fg": "#000000",    # Pure black
               "bg": "#ffffff"     # Pure white
           }
       )
   )

   # Brand colors with validation
   try:
       brand_intents = IntentsConfig(
           style=StyleIntents(
               palette={
                   "fg": "#invalid-color",  # This will raise validation error
                   "bg": "#ffffff"
               }
           )
       )
   except ValidationError as e:
       print(f"Color validation failed: {e}")

Legacy Color API
~~~~~~~~~~~~~~~~

For simple cases, you can still use the write function directly:

.. code-block:: python

   # Blue QR code on light background
   with open('colored.svg', 'w') as f:
       write(qr, f,
             shape='dot',
             dark='#1e40af',    # Dark blue
             light='#dbeafe')   # Light blue

   # Transparent background
   with open('transparent.svg', 'w') as f:
       write(qr, f,
             shape='connected',
             dark='#000000',
             light='transparent')

Safe Mode
---------

By default, the plugin uses "safe mode" which ensures maximum scannability:

.. code-block:: python

   # Safe mode ON (default) - special patterns use simple shapes
   with open('safe.svg', 'w') as f:
       write(qr, f, shape='star', safe_mode=True)

   # Safe mode OFF - all modules use the selected shape
   with open('unsafe.svg', 'w') as f:
       write(qr, f, shape='star', safe_mode=False)

Advanced Example
----------------

Here's a more complex example combining various features:

.. code-block:: python

   import segno
   from segnomms import write

   # Create a QR code with high error correction
   qr = segno.make("https://example.com", error='h')

   # Save with custom styling
   with open('advanced.svg', 'w') as f:
       write(qr, f,
             shape='connected-classy',      # Sophisticated connected shape
             scale=20,                      # Larger modules
             border=2,                      # Smaller quiet zone
             dark='#059669',               # Green
             light='#f0fdf4',              # Light green
             safe_mode=False,              # Apply shape to all modules
             svgclass='my-qr-code',        # Custom CSS class
             title='Scan Me!',             # Custom title
             xmldecl=False)                # No XML declaration

Working with Different QR Types
-------------------------------

The plugin works with all Segno QR code types:

.. code-block:: python

   # Regular QR code
   qr1 = segno.make("Regular QR")

   # Micro QR code
   qr2 = segno.make("Micro", micro=True)

   # QR code with specific version
   qr3 = segno.make("Version 10", version=10)

   # All work with the plugin
   for i, qr in enumerate([qr1, qr2, qr3]):
       with open(f'qr_{i}.svg', 'w') as f:
           write(qr, f, shape='connected')

Phase 4: Professional QR Codes
-------------------------------

Create professional QR codes with custom frames and logo areas:

.. code-block:: python

   # Circle frame with logo area
   qr = segno.make("https://example.com", error='h')

   with open('professional.svg', 'w') as f:
       write(qr, f,
             scale=20,
             border=6,

             # Circular frame
             frame_shape='circle',

             # Logo area in center
             centerpiece_enabled=True,
             centerpiece_shape='circle',
             centerpiece_size=0.15,

             # Gradient background
             quiet_zone_style='gradient',
             quiet_zone_gradient={
                 'type': 'radial',
                 'colors': ['#ffffff', '#f0f0f0']
             },

             # Smooth module shapes
             shape='squircle',
             merge='soft')

Frame Shapes
~~~~~~~~~~~~

Available frame shapes:

* ``'square'`` - Standard rectangular QR code (default)
* ``'circle'`` - Circular boundary
* ``'rounded-rect'`` - Rectangle with rounded corners
* ``'squircle'`` - Modern superellipse shape
* ``'custom'`` - Define your own SVG path

Centerpiece Logo Areas
~~~~~~~~~~~~~~~~~~~~~~

Reserve space for logos with automatic error correction validation:

.. code-block:: python

   # Reserve 15% of center for logo
   write(qr, f,
         centerpiece_enabled=True,
         centerpiece_size=0.15,        # Size as fraction
         centerpiece_shape='circle',   # 'rect', 'circle', or 'squircle'
         centerpiece_margin=2)         # Safety margin in modules

Error Handling and Production Use
----------------------------------

Intent-Based Error Handling (Recommended)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The intent-based API provides comprehensive error handling with specific exception types:

.. code-block:: python

   from segnomms.intents import render_with_intents
   from segnomms.intents.models import PayloadConfig, IntentsConfig, StyleIntents
   from segnomms.exceptions import IntentValidationError, UnsupportedIntentError

   try:
       # This might have validation issues
       intents = IntentsConfig(
           style=StyleIntents(
               module_shape="pyramid",  # Might not be supported
               corner_radius=2.5        # Out of valid range
           )
       )
       result = render_with_intents(PayloadConfig(text="Hello!"), intents)

       # Check for degradation warnings
       if result.has_warnings:
           for warning in result.warnings:
               if warning.code == "FEATURE_DEGRADED":
                   print(f"Feature '{warning.detail}' was degraded for compatibility")

   except IntentValidationError as e:
       print(f"Invalid configuration: {e.message}")
       print(f"Field: {e.intent_path}")
       print(f"Suggestion: {e.suggestion}")

   except UnsupportedIntentError as e:
       print(f"Feature not supported: {e.feature}")
       print(f"Try these alternatives: {e.alternatives}")

For complete error handling patterns, see :doc:`api/exceptions`.

Development Best Practices
---------------------------

For testing and development, use test constants to avoid magic strings:

.. code-block:: python

   from segnomms.constants import (
       ModuleShape, TEST_COLORS, create_config,
       QR_PAYLOADS, DEFAULT_SCALE, DEFAULT_BORDER
   )

   # Type-safe and maintainable
   qr = segno.make(QR_PAYLOADS["url"])
   config = create_config(
       shape=ModuleShape.SQUIRCLE.value,
       dark=TEST_COLORS["brand_primary"],
       light=TEST_COLORS["white"],
       scale=DEFAULT_SCALE,
       border=DEFAULT_BORDER
   )

   with open('professional.svg', 'w') as f:
       write(qr, f, **config)

Benefits of using constants:

* **Type safety** - Prevent typos in shape names
* **IDE support** - Autocomplete for all valid values
* **Consistency** - Same colors/shapes across your project
* **Maintainability** - Change values in one place

See :doc:`testing/index` for comprehensive testing documentation.

Next Steps
----------

* **Intent-Based API**: See :doc:`api/intents` for comprehensive intent configuration options
* **Error Handling**: Review :doc:`api/exceptions` for production error handling patterns
* **Degradation System**: Learn about :doc:`api/degradation` for graceful feature fallbacks
* **Shape Options**: See :doc:`shapes` for a complete list of available shapes
* **Examples**: Explore :doc:`examples` for usage patterns, including Intent-Based API examples
* **Testing**: Read :doc:`testing/index` for testing best practices and development guidelines
* **Full API Reference**: Check :doc:`api/index` for complete API documentation
