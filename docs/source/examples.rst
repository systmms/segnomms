Examples
========

This section provides comprehensive examples of using the Segno Interactive SVG Plugin.

.. note::
   For testing and development, consider using the test constants module for more maintainable code.
   See :doc:`testing/test-constants` for best practices.

Basic Examples
--------------

Simple QR Code
~~~~~~~~~~~~~~

The simplest usage with default settings:

.. code-block:: python

   import segno
   from segnomms import write

   qr = segno.make("Hello, World!")
   with open('simple.svg', 'w') as f:
       write(qr, f)

Custom Colors
~~~~~~~~~~~~~

Changing the module colors:

.. code-block:: python

   # Blue on white
   with open('blue.svg', 'w') as f:
       write(qr, f, dark='#0066cc', light='white')

   # Dark theme
   with open('dark.svg', 'w') as f:
       write(qr, f, dark='#ffffff', light='#1a1a1a')

   # Transparent background
   with open('transparent.svg', 'w') as f:
       write(qr, f, dark='#000000', light='transparent')

Using Test Constants (Recommended)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For more maintainable code, especially in testing or development:

.. code-block:: python

   from tests.constants import (
       ModuleShape, TEST_COLORS, create_test_config,
       DEFAULT_SCALE, DEFAULT_BORDER
   )

   # Type-safe shape selection
   config = create_test_config(
       shape=ModuleShape.CIRCLE.value,
       dark=TEST_COLORS["blue"],
       light=TEST_COLORS["white"],
       scale=DEFAULT_SCALE,
       border=DEFAULT_BORDER
   )

   with open('circles_safe.svg', 'w') as f:
       write(qr, f, **config)

This approach provides:

* **Type safety** through enum values
* **Consistency** across your codebase
* **IDE support** with autocomplete
* **Easier refactoring** when values change

Shape Examples
--------------

Basic Shapes
~~~~~~~~~~~~

.. code-block:: python

   # Circle modules
   with open('circles.svg', 'w') as f:
       write(qr, f, shape='circle', size_ratio=0.85)

   # Small dots
   with open('dots.svg', 'w') as f:
       write(qr, f, shape='dot', size_ratio=0.5)

   # Diamond pattern
   with open('diamonds.svg', 'w') as f:
       write(qr, f, shape='diamond')

   # Star pattern with 6 points
   with open('stars.svg', 'w') as f:
       write(qr, f, shape='star', star_points=6, inner_ratio=0.4)

Connected Shapes
~~~~~~~~~~~~~~~~

.. code-block:: python

   # Basic connected style
   with open('connected.svg', 'w') as f:
       write(qr, f, shape='connected')

   # Extra rounded connections
   with open('smooth.svg', 'w') as f:
       write(qr, f, shape='connected-extra-rounded')

   # Classy boundary styling
   with open('classy.svg', 'w') as f:
       write(qr, f, shape='connected-classy')

Advanced Examples
-----------------

URL QR Code with Branding
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import segno
   from segnomms import write

   # Create URL QR code with high error correction
   qr = segno.make("https://example.com", error='h')

   # Save with branding colors and sophisticated shape
   with open('branded.svg', 'w') as f:
       write(qr, f,
             shape='connected-classy',
             scale=25,
             border=2,
             dark='#e11d48',      # Brand red
             light='#fef2f2',     # Light red background
             safe_mode=False)     # Apply shape to all modules

vCard QR Code
~~~~~~~~~~~~~

.. code-block:: python

   # Create vCard
   vcard = '''BEGIN:VCARD
   VERSION:3.0
   FN:John Doe
   ORG:Example Corp
   TEL:+1234567890
   EMAIL:john@example.com
   END:VCARD'''

   qr = segno.make(vcard, error='l')

   # Professional look with hexagons
   with open('vcard.svg', 'w') as f:
       write(qr, f,
             shape='hexagon',
             size_ratio=0.9,
             scale=15,
             dark='#1f2937',
             light='#f9fafb')

WiFi QR Code
~~~~~~~~~~~~

.. code-block:: python

   # Create WiFi QR code
   wifi = segno.make_wifi(
       ssid='GuestNetwork',
       password='Welcome123',
       security='WPA'
   )

   # Tech-themed with crosses
   with open('wifi.svg', 'w') as f:
       write(wifi, f,
             shape='cross',
             thickness=0.15,
             sharp=True,
             scale=20,
             dark='#10b981')

Batch Processing
----------------

Processing Multiple QR Codes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import segno
   from segnomms import write
   from pathlib import Path

   # Data to encode
   items = [
       ('Product A', 'SKU001'),
       ('Product B', 'SKU002'),
       ('Product C', 'SKU003'),
   ]

   # Output directory
   output_dir = Path('qr_codes')
   output_dir.mkdir(exist_ok=True)

   # Generate QR codes
   for name, sku in items:
       qr = segno.make(f"https://example.com/product/{sku}")

       output_file = output_dir / f"{sku}.svg"
       with open(output_file, 'w') as f:
           write(qr, f,
                 shape='connected',
                 scale=10,
                 title=f"QR Code for {name}")

Multiple Formats
~~~~~~~~~~~~~~~~

.. code-block:: python

   shapes = ['square', 'circle', 'connected', 'star']

   qr = segno.make("Multi-format example")

   for shape in shapes:
       with open(f'example_{shape}.svg', 'w') as f:
           write(qr, f, shape=shape, scale=15)

Integration Examples
--------------------

Flask Web Application
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from flask import Flask, Response
   import segno
   from segnomms import write
   import io

   app = Flask(__name__)

   @app.route('/qr/<data>')
   def generate_qr(data):
       # Create QR code
       qr = segno.make(data)

       # Generate SVG to string buffer
       buffer = io.StringIO()
       write(qr, buffer, shape='connected', scale=10)

       # Return as SVG response
       svg_content = buffer.getvalue()
       return Response(svg_content, mimetype='image/svg+xml')

Django View
~~~~~~~~~~~

.. code-block:: python

   from django.http import HttpResponse
   import segno
   from segnomms import write
   import io

   def qr_code_view(request, data):
       # Get parameters from request
       shape = request.GET.get('shape', 'square')
       color = request.GET.get('color', '#000000')

       # Generate QR code
       qr = segno.make(data)

       # Create SVG
       buffer = io.StringIO()
       write(qr, buffer, shape=shape, dark=color)

       # Return SVG response
       return HttpResponse(
           buffer.getvalue(),
           content_type='image/svg+xml'
       )

Custom Styling
--------------

CSS Integration
~~~~~~~~~~~~~~~

.. code-block:: python

   # Generate QR code with custom CSS class
   with open('styled.svg', 'w') as f:
       write(qr, f,
             shape='circle',
             svgclass='my-qr-code',
             lineclass='qr-path')

Then style with CSS:

.. code-block:: css

   .my-qr-code {
       filter: drop-shadow(0 4px 6px rgba(0, 0, 0, 0.1));
   }

   .my-qr-code .qr-module {
       transition: all 0.3s ease;
   }

   .my-qr-code .qr-module:hover {
       opacity: 0.7;
   }

Animation
~~~~~~~~~

.. code-block:: python

   # Generate QR code for animation
   with open('animated.svg', 'w') as f:
       write(qr, f, shape='dot', size_ratio=0.6)

Add CSS animations:

.. code-block:: html

   <style>
   @keyframes pulse {
       0% { transform: scale(1); opacity: 1; }
       50% { transform: scale(1.1); opacity: 0.8; }
       100% { transform: scale(1); opacity: 1; }
   }

   .qr-module {
       animation: pulse 2s ease-in-out infinite;
       animation-delay: calc(var(--delay) * 0.01s);
   }
   </style>

Phase 4: Advanced Frame and Centerpiece Features
=================================================

Phase 4 introduces powerful new features for creating professional QR codes with custom frame shapes, centerpiece logo areas, and enhanced styling options.

Frame Shapes
------------

Circle Frame
~~~~~~~~~~~~

Create QR codes with circular boundaries:

.. code-block:: python

   import segno
   from segnomms import write

   qr = segno.make("https://example.com", error='h')

   # Simple circle frame
   with open('circle_frame.svg', 'w') as f:
       write(qr, f,
             scale=15,
             border=5,  # Larger border recommended for circular frames
             frame_shape='circle')

Rounded Rectangle Frame
~~~~~~~~~~~~~~~~~~~~~~~

Soften your QR code edges with rounded corners:

.. code-block:: python

   # Subtle rounded corners
   with open('rounded_subtle.svg', 'w') as f:
       write(qr, f,
             scale=15,
             border=4,
             frame_shape='rounded-rect',
             frame_corner_radius=0.1)  # 10% corner radius

   # More pronounced rounding
   with open('rounded_strong.svg', 'w') as f:
       write(qr, f,
             scale=15,
             border=4,
             frame_shape='rounded-rect',
             frame_corner_radius=0.3)  # 30% corner radius

Squircle Frame
~~~~~~~~~~~~~~

Use the modern squircle shape (superellipse) for a contemporary look:

.. code-block:: python

   with open('squircle_frame.svg', 'w') as f:
       write(qr, f,
             scale=18,
             border=5,
             frame_shape='squircle',
             shape='circle',  # Circular modules complement squircle frame
             merge='soft')    # Enable soft merging for smoother appearance

Custom Frame Shapes
~~~~~~~~~~~~~~~~~~~

Define your own frame shape with SVG paths:

.. code-block:: python

   # Diamond-shaped frame
   custom_diamond = "M 100 0 L 200 100 L 100 200 L 0 100 Z"

   with open('diamond_frame.svg', 'w') as f:
       write(qr, f,
             scale=10,
             border=6,
             frame_shape='custom',
             frame_custom_path=custom_diamond)

Frame Effects
~~~~~~~~~~~~~

Control how the frame interacts with QR modules:

.. code-block:: python

   # Sharp clipping (default)
   with open('circle_clip.svg', 'w') as f:
       write(qr, f,
             frame_shape='circle',
             frame_clip_mode='clip')

   # Soft fade at edges
   with open('circle_fade.svg', 'w') as f:
       write(qr, f,
             frame_shape='circle',
             frame_clip_mode='fade')

Centerpiece Logo Areas
----------------------

Basic Centerpiece
~~~~~~~~~~~~~~~~~

Reserve space in the center for logo placement:

.. code-block:: python

   # Rectangular logo area
   with open('logo_rect.svg', 'w') as f:
       write(qr, f,
             scale=15,
             border=4,
             centerpiece_enabled=True,
             centerpiece_shape='rect',
             centerpiece_size=0.15,  # 15% of QR code size
             centerpiece_margin=2)   # 2-module safety margin

Circular Logo Area
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   with open('logo_circle.svg', 'w') as f:
       write(qr, f,
             scale=15,
             border=4,
             centerpiece_enabled=True,
             centerpiece_shape='circle',
             centerpiece_size=0.12)  # Smaller for circular shape

Off-Center Logo Placement
~~~~~~~~~~~~~~~~~~~~~~~~~~

Position logos away from the center:

.. code-block:: python

   # Top-left logo placement
   with open('logo_offset.svg', 'w') as f:
       write(qr, f,
             scale=20,
             border=5,
             centerpiece_enabled=True,
             centerpiece_shape='rect',
             centerpiece_size=0.1,
             centerpiece_offset_x=-0.2,  # Move left
             centerpiece_offset_y=-0.2,  # Move up
             centerpiece_margin=3)

Error Correction Considerations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Choose appropriate error correction levels for logo areas:

.. code-block:: python

   # Small logo with medium error correction
   qr_medium = segno.make("https://example.com", error='m')
   with open('logo_medium.svg', 'w') as f:
       write(qr_medium, f,
             centerpiece_enabled=True,
             centerpiece_size=0.08)  # 8% is safe for M level

   # Larger logo requires high error correction
   qr_high = segno.make("https://example.com", error='h')
   with open('logo_large.svg', 'w') as f:
       write(qr_high, f,
             centerpiece_enabled=True,
             centerpiece_size=0.20)  # 20% requires H level

Enhanced Quiet Zones
---------------------

Gradient Backgrounds
~~~~~~~~~~~~~~~~~~~~

Create visually appealing backgrounds with gradients:

.. code-block:: python

   # Radial gradient
   with open('gradient_radial.svg', 'w') as f:
       write(qr, f,
             scale=15,
             border=6,
             quiet_zone_style='gradient',
             quiet_zone_gradient={
                 'type': 'radial',
                 'colors': ['#ffffff', '#f0f0f0', '#e0e0e0']
             })

   # Linear gradient
   with open('gradient_linear.svg', 'w') as f:
       write(qr, f,
             scale=15,
             border=6,
             quiet_zone_style='gradient',
             quiet_zone_gradient={
                 'type': 'linear',
                 'x1': '0%', 'y1': '0%',
                 'x2': '100%', 'y2': '100%',
                 'colors': ['#fef3c7', '#fbbf24', '#f59e0b']
             })

Brand Color Backgrounds
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Solid brand color
   with open('brand_background.svg', 'w') as f:
       write(qr, f,
             scale=15,
             border=5,
             quiet_zone_style='solid',
             quiet_zone_color='#1e40af',  # Brand blue
             dark='#ffffff',              # White modules on blue
             light='transparent')         # Transparent QR background

Combined Features
-----------------

Professional Business Card QR
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Combine frame, centerpiece, and gradient for professional results:

.. code-block:: python

   # Business card QR with vCard data
   vcard_data = '''BEGIN:VCARD
   VERSION:3.0
   FN:Jane Smith
   ORG:Design Studio
   EMAIL:jane@designstudio.com
   URL:https://designstudio.com
   END:VCARD'''

   qr = segno.make(vcard_data, error='h')

   with open('business_card.svg', 'w') as f:
       write(qr, f,
             scale=20,
             border=6,

             # Frame styling
             frame_shape='rounded-rect',
             frame_corner_radius=0.2,

             # Logo area
             centerpiece_enabled=True,
             centerpiece_shape='circle',
             centerpiece_size=0.15,
             centerpiece_margin=3,

             # Background gradient
             quiet_zone_style='gradient',
             quiet_zone_gradient={
                 'type': 'radial',
                 'colors': ['#f8fafc', '#e2e8f0']
             },

             # Module styling
             shape='squircle',
             merge='soft',
             dark='#1e293b')

Event Poster QR
~~~~~~~~~~~~~~~

Create eye-catching QR codes for events:

.. code-block:: python

   event_url = "https://eventsite.com/concert-2024"
   qr = segno.make(event_url, error='h')

   with open('concert_qr.svg', 'w') as f:
       write(qr, f,
             scale=25,
             border=8,

             # Circular frame for dynamic look
             frame_shape='circle',
             frame_clip_mode='fade',

             # Off-center logo space
             centerpiece_enabled=True,
             centerpiece_shape='squircle',
             centerpiece_size=0.12,
             centerpiece_offset_x=0.1,
             centerpiece_offset_y=-0.1,

             # Vibrant gradient
             quiet_zone_style='gradient',
             quiet_zone_gradient={
                 'type': 'linear',
                 'x1': '0%', 'y1': '0%',
                 'x2': '100%', 'y2': '100%',
                 'colors': ['#7c3aed', '#c084fc', '#ddd6fe']
             },

             # Connected modules for flow
             shape='connected-classy',
             merge='aggressive',
             dark='#ffffff')

Product Packaging QR
~~~~~~~~~~~~~~~~~~~~

Subtle QR codes that integrate well with packaging design:

.. code-block:: python

   product_info = "https://product.com/verify/ABC123"
   qr = segno.make(product_info, error='m')

   with open('package_qr.svg', 'w') as f:
       write(qr, f,
             scale=12,
             border=4,

             # Soft rounded frame
             frame_shape='squircle',

             # Small centered logo area
             centerpiece_enabled=True,
             centerpiece_shape='circle',
             centerpiece_size=0.08,

             # Minimal styling
             shape='dot',
             dark='#374151',
             light='#f9fafb')

Best Practices
--------------

Error Correction Guidelines
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Guidelines for centerpiece sizes by error level:
   centerpiece_limits = {
       'L': 0.05,  # 5% max - very conservative
       'M': 0.08,  # 8% max - good for small logos
       'Q': 0.15,  # 15% max - medium logos
       'H': 0.20,  # 20% max - large logos
   }

Frame Safety Tips
~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Minimum border sizes for non-square frames
   frame_borders = {
       'square': 4,       # Standard quiet zone
       'circle': 5,       # Extra space for corner clipping
       'rounded-rect': 4, # Standard is usually sufficient
       'squircle': 4,     # Standard is usually sufficient
       'custom': 6,       # Conservative for unknown shapes
   }

Testing and Validation
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Always test scannability
   test_data = "https://your-test-url.com"

   for error_level in ['L', 'M', 'Q', 'H']:
       qr = segno.make(test_data, error=error_level)

       with open(f'test_{error_level}.svg', 'w') as f:
           write(qr, f,
                 frame_shape='circle',
                 centerpiece_enabled=True,
                 centerpiece_size=0.15,
                 # Test with your target settings
                 )

       # Test scanning with your target devices/apps

Troubleshooting
---------------

Common Issues
~~~~~~~~~~~~~

**QR Code won't scan:**

- Increase ``border`` parameter (especially for circular frames)
- Reduce ``centerpiece_size``
- Use higher error correction level (``error='h'``)
- Test ``frame_clip_mode='clip'`` instead of ``'fade'``

**Logo area too small:**

- Increase ``centerpiece_size`` (up to limits above)
- Use higher error correction level
- Reduce ``centerpiece_margin`` carefully

**Frame cuts off important areas:**

- Increase ``border`` parameter
- Use ``frame_shape='rounded-rect'`` with small ``corner_radius``
- Test with different ``frame_clip_mode`` settings

Performance Considerations
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # For large batch processing, simpler settings perform better
   with open('performance_optimized.svg', 'w') as f:
       write(qr, f,
             frame_shape='rounded-rect',    # Faster than 'circle'
             frame_clip_mode='clip',        # Faster than 'fade'
             quiet_zone_style='solid',      # Faster than 'gradient'
             merge='none')                  # Faster than clustering

Intent-Based API Examples
=========================

The Intent-Based API provides high-level, declarative QR code generation with comprehensive error handling and graceful degradation.

Basic Intent Usage
------------------

Simple Style Intents
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from segnomms.intents import render_with_intents
   from segnomms.intents.models import PayloadConfig, IntentsConfig, StyleIntents

   # Basic styling intents
   intents = IntentsConfig(
       style=StyleIntents(
           module_shape="squircle",
           palette={"fg": "#1a1a2e", "bg": "#ffffff"},
           corner_radius=0.3
       )
   )

   payload = PayloadConfig(text="Hello World")
   result = render_with_intents(payload, intents)

   # Check for any warnings or degradations
   if result.has_warnings:
       print(f"Generated with {len(result.warnings)} warnings:")
       for warning in result.warnings:
           print(f"  - {warning.detail}")

   print(f"Scanability prediction: {result.scanability_prediction}")

Multi-Category Intents
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from segnomms.intents.models import (
       IntentsConfig, StyleIntents, FrameIntents,
       ReserveIntents, AccessibilityIntents
   )

   # Comprehensive intent configuration
   intents = IntentsConfig(
       style=StyleIntents(
           module_shape="circle",
           patterns={
               "finder": "rounded",
               "timing": "square",
               "data": "circle"
           },
           palette={"fg": "#2563eb", "bg": "#f8fafc"}
       ),
       frame=FrameIntents(
           shape="rounded-rect",
           corner_radius=0.2,
           clip_mode="fade"
       ),
       reserve=ReserveIntents(
           area_pct=12.0,
           shape="circle",
           mode="knockout"
       ),
       accessibility=AccessibilityIntents(
           ids=True,
           title="Company Website QR Code",
           desc="Scan to visit our website"
       )
   )

   from segnomms.intents import render_with_intents
   from segnomms.intents.models import PayloadConfig
   result = render_with_intents(PayloadConfig(text="https://example.com"), intents)

Error Handling Examples
-----------------------

Comprehensive Error Recovery
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from segnomms.exceptions import (
       IntentValidationError,
       UnsupportedIntentError,
       IntentDegradationError,
       ContrastRatioError,
       SegnoMMSError
   )

   def robust_qr_generation(payload: str, intents: IntentsConfig):
       """Generate QR with comprehensive error handling."""
       try:
           result = render_with_intents(payload, intents)

           # Success - check for degradation warnings
           degradations = []
           for warning in result.warnings:
               if warning.code == "FEATURE_DEGRADED":
                   degradations.append({
                       "feature": warning.context.get("original_feature"),
                       "fallback": warning.context.get("fallback_feature"),
                       "reason": warning.context.get("reason")
                   })

           return {
               "success": True,
               "svg_content": result.svg_content,
               "degradations": degradations,
               "scanability": result.scanability_prediction,
               "metrics": result.metrics.model_dump()
           }

       except IntentValidationError as e:
           return {
               "success": False,
               "error_type": "validation_error",
               "message": f"Invalid intent at {e.intent_path}: {e.original_value}",
               "suggestion": e.suggestion,
               "intent_path": e.intent_path
           }

       except UnsupportedIntentError as e:
           return {
               "success": False,
               "error_type": "unsupported_feature",
               "message": f"Feature '{e.feature}' is not supported",
               "alternatives": e.alternatives,
               "planned_version": e.planned_version
           }

       except ContrastRatioError as e:
           return {
               "success": False,
               "error_type": "accessibility_error",
               "message": f"Contrast ratio {e.ratio:.2f} is below required {e.required_ratio}",
               "standard": e.standard,
               "colors": {"foreground": e.foreground, "background": e.background}
           }

       except SegnoMMSError as e:
           return {
               "success": False,
               "error_type": "general_error",
               "code": e.code,
               "message": e.message,
               "details": e.details,
               "suggestion": e.suggestion
           }

Production Error Recovery with Retries
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   def generate_qr_with_fallback(payload: str, intents: IntentsConfig, max_retries: int = 3):
       """Production-ready QR generation with automatic fallback."""

       original_intents = intents.model_copy(deep=True)
       current_intents = intents

       for attempt in range(max_retries):
           try:
               result = render_with_intents(payload, current_intents)

               return {
                   "success": True,
                   "svg_content": result.svg_content,
                   "warnings": [w.model_dump() for w in result.warnings],
                   "attempt": attempt + 1,
                   "degradation_applied": len(result.warnings) > 0,
                   "scanability": result.scanability_prediction
               }

           except IntentValidationError as e:
               # Fix common validation issues
               if "corner_radius" in e.intent_path:
                   current_intents.style.corner_radius = 0.3  # Safe default
               elif "area_pct" in e.intent_path:
                   current_intents.reserve.area_pct = 10.0  # Safe default

           except UnsupportedIntentError as e:
               # Apply feature fallbacks
               if "module_shape" in e.feature and e.alternatives:
                   current_intents.style.module_shape = e.alternatives[0]
               elif "frame.shape" in e.feature and e.alternatives:
                   current_intents.frame.shape = e.alternatives[0]

           except ContrastRatioError:
               # Use high contrast colors
               current_intents.style.palette = {"fg": "#000000", "bg": "#FFFFFF"}

           except Exception as e:
               if attempt == max_retries - 1:
                   # Final fallback - minimal configuration
                   try:
                       minimal_intents = IntentsConfig()
                       result = render_with_intents(payload, minimal_intents)
                       return {
                           "success": True,
                           "svg_content": result.svg_content,
                           "fallback_used": True,
                           "original_error": str(e)
                       }
                   except Exception:
                       return {
                           "success": False,
                           "error": "All fallback attempts failed",
                           "final_error": str(e)
                       }

       return {"success": False, "error": "Max retries exceeded"}

Batch Processing with Error Tracking
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   def process_batch_qr_codes(requests: List[Dict[str, Any]]) -> Dict[str, Any]:
       """Process multiple QR requests with comprehensive error tracking."""

       results = []
       error_summary = {
           "validation_errors": 0,
           "unsupported_features": 0,
           "contrast_errors": 0,
           "general_errors": 0,
           "successful_with_degradation": 0,
           "fully_successful": 0
       }

       for i, request in enumerate(requests):
           try:
               payload = request["payload"]
               intents = IntentsConfig.model_validate(request["intents"])

               result = render_with_intents(payload, intents)

               if result.warnings:
                   error_summary["successful_with_degradation"] += 1
                   warning_details = []
                   for warning in result.warnings:
                       if warning.code == "FEATURE_DEGRADED":
                           warning_details.append({
                               "feature": warning.context.get("original_feature"),
                               "fallback": warning.context.get("fallback_feature")
                           })

                   results.append({
                       "index": i,
                       "success": True,
                       "svg_content": result.svg_content,
                       "degradations": warning_details
                   })
               else:
                   error_summary["fully_successful"] += 1
                   results.append({
                       "index": i,
                       "success": True,
                       "svg_content": result.svg_content
                   })

           except IntentValidationError as e:
               error_summary["validation_errors"] += 1
               results.append({
                   "index": i,
                   "success": False,
                   "error_type": "validation",
                   "error": e.message,
                   "path": e.intent_path
               })

           except UnsupportedIntentError as e:
               error_summary["unsupported_features"] += 1
               results.append({
                   "index": i,
                   "success": False,
                   "error_type": "unsupported",
                   "feature": e.feature,
                   "alternatives": e.alternatives
               })

           except ContrastRatioError as e:
               error_summary["contrast_errors"] += 1
               results.append({
                   "index": i,
                   "success": False,
                   "error_type": "contrast",
                   "ratio": e.ratio,
                   "required": e.required_ratio
               })

           except Exception as e:
               error_summary["general_errors"] += 1
               results.append({
                   "index": i,
                   "success": False,
                   "error_type": "general",
                   "error": str(e)
               })

       return {
           "results": results,
           "summary": error_summary,
           "total_processed": len(requests),
           "success_rate": (error_summary["fully_successful"] + error_summary["successful_with_degradation"]) / len(requests)
       }

Web Framework Integration
-------------------------

FastAPI with Intent-Based Error Handling
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from fastapi import FastAPI, HTTPException
   from fastapi.responses import JSONResponse, Response
   from pydantic import BaseModel
   from typing import Dict, Any, Optional, List

   app = FastAPI()

   class QRRequest(BaseModel):
       payload: str
       intents: Dict[str, Any]
       options: Optional[Dict[str, Any]] = {}

   class QRResponse(BaseModel):
       success: bool
       svg_content: Optional[str] = None
       warnings: Optional[List[Dict[str, Any]]] = None
       error: Optional[Dict[str, Any]] = None
       metrics: Optional[Dict[str, Any]] = None

   @app.post("/api/qr/generate", response_model=QRResponse)
   async def generate_qr_code(request: QRRequest):
       """Generate QR code with comprehensive error handling."""
       try:
           # Parse intents with validation
           intents_config = IntentsConfig.model_validate(request.intents)

           # Generate QR code
           result = render_with_intents(request.payload, intents_config)

           return QRResponse(
               success=True,
               svg_content=result.svg_content,
               warnings=[w.model_dump() for w in result.warnings],
               metrics=result.metrics.model_dump()
           )

       except IntentValidationError as e:
           return JSONResponse(
               status_code=400,
               content=QRResponse(
                   success=False,
                   error={
                       "type": "intent_validation_error",
                       "message": e.message,
                       "intent_path": e.intent_path,
                       "invalid_value": e.original_value,
                       "suggestion": e.suggestion
                   }
               ).model_dump()
           )

       except UnsupportedIntentError as e:
           return JSONResponse(
               status_code=422,
               content=QRResponse(
                   success=False,
                   error={
                       "type": "unsupported_intent_error",
                       "message": e.message,
                       "feature": e.feature,
                       "alternatives": e.alternatives,
                       "planned_version": e.planned_version
                   }
               ).model_dump()
           )

       except ContrastRatioError as e:
           return JSONResponse(
               status_code=400,
               content=QRResponse(
                   success=False,
                   error={
                       "type": "contrast_ratio_error",
                       "message": e.message,
                       "actual_ratio": e.ratio,
                       "required_ratio": e.required_ratio,
                       "standard": e.standard
                   }
               ).model_dump()
           )

   @app.get("/api/qr/generate/{payload}")
   async def generate_qr_simple(payload: str, shape: str = "square", color: str = "#000000"):
       """Simple QR generation endpoint with automatic error recovery."""
       try:
           intents = IntentsConfig(
               style=StyleIntents(
                   module_shape=shape,
                   palette={"fg": color, "bg": "#ffffff"}
               )
           )

           result = render_with_intents(payload, intents)

           return Response(
               content=result.svg_content,
               media_type="image/svg+xml",
               headers={
                   "X-QR-Warnings": str(len(result.warnings)),
                   "X-QR-Scanability": str(result.scanability_prediction)
               }
           )

       except Exception as e:
           # Fallback to minimal QR
           minimal_intents = IntentsConfig()
           result = render_with_intents(payload, minimal_intents)

           return Response(
               content=result.svg_content,
               media_type="image/svg+xml",
               headers={
                   "X-QR-Fallback-Used": "true",
                   "X-QR-Original-Error": str(e)
               }
           )

Flask with Error Monitoring
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from flask import Flask, request, jsonify, Response
   import logging
   from datetime import datetime
   from collections import defaultdict

   app = Flask(__name__)

   # Configure error monitoring
   error_logger = logging.getLogger('segnomms.errors')
   error_metrics = {
       "total_requests": 0,
       "error_counts": defaultdict(int),
       "degradation_counts": defaultdict(int)
   }

   @app.route('/api/qr/generate', methods=['POST'])
   def generate_qr():
       """Generate QR with comprehensive error tracking."""
       start_time = datetime.utcnow()
       error_metrics["total_requests"] += 1

       try:
           data = request.get_json()
           payload = data.get('payload', '')
           intents_data = data.get('intents', {})

           # Parse and validate intents
           intents = IntentsConfig.model_validate(intents_data)
           result = render_with_intents(payload, intents)

           # Track degradations for monitoring
           degradations = []
           for warning in result.warnings:
               if warning.code == "FEATURE_DEGRADED":
                   feature = warning.context.get('original_feature', 'unknown')
                   fallback = warning.context.get('fallback_feature', 'unknown')
                   degradations.append({"feature": feature, "fallback": fallback})
                   error_metrics["degradation_counts"][f"{feature}->{fallback}"] += 1

           processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000

           return jsonify({
               "success": True,
               "svg": result.svg_content,
               "warnings": [w.model_dump() for w in result.warnings],
               "degradations": degradations,
               "metrics": {
                   **result.metrics.model_dump(),
                   "processing_time_ms": processing_time
               }
           })

       except IntentValidationError as e:
           error_metrics["error_counts"]["validation_error"] += 1
           error_logger.warning(f"Intent validation error: {e.intent_path} = {e.original_value}")

           return jsonify({
               "success": False,
               "error": {
                   "type": "validation_error",
                   "message": e.message,
                   "field": e.intent_path,
                   "invalid_value": e.original_value,
                   "suggestion": e.suggestion
               }
           }), 400

       except UnsupportedIntentError as e:
           error_metrics["error_counts"]["unsupported_feature"] += 1
           error_logger.info(f"Unsupported feature requested: {e.feature}")

           return jsonify({
               "success": False,
               "error": {
                   "type": "unsupported_feature",
                   "message": e.message,
                   "feature": e.feature,
                   "alternatives": e.alternatives
               }
           }), 422

       except Exception as e:
           error_metrics["error_counts"]["unexpected_error"] += 1
           error_logger.error(f"Unexpected error: {e}", exc_info=True)

           return jsonify({
               "success": False,
               "error": {
                   "type": "internal_error",
                   "message": "An unexpected error occurred"
               }
           }), 500

   @app.route('/api/metrics/errors', methods=['GET'])
   def get_error_metrics():
       """Endpoint for monitoring error metrics."""
       return jsonify({
           "total_requests": error_metrics["total_requests"],
           "error_counts": dict(error_metrics["error_counts"]),
           "degradation_counts": dict(error_metrics["degradation_counts"]),
           "error_rate": sum(error_metrics["error_counts"].values()) / max(error_metrics["total_requests"], 1)
       })

Advanced Degradation Examples
-----------------------------

Custom Degradation Rules
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from segnomms.degradation.rules import DegradationRule
   from segnomms.degradation.models import DegradationWarning, WarningLevel
   from segnomms.degradation.manager import DegradationManager

   class OrganizationPolicyRule(DegradationRule):
       """Custom rule enforcing organization design policies."""

       def __init__(self):
           self.allowed_colors = ["#000000", "#ffffff", "#1a73e8", "#ea4335"]
           self.allowed_shapes = ["square", "circle", "rounded"]

       def check(self, config):
           warnings = []

           # Check color policy
           if config.dark not in self.allowed_colors:
               config.dark = "#000000"  # Fallback to black
               warnings.append(DegradationWarning(
                   feature="dark_color",
                   level=WarningLevel.WARNING,
                   reason="Color not in approved brand palette",
                   original_value=config.dark,
                   fallback_value="#000000",
                   suggestion="Use approved brand colors"
               ))

           # Check shape policy
           current_shape = str(config.geometry.shape)
           if current_shape not in self.allowed_shapes:
               config.geometry.shape = "square"
               warnings.append(DegradationWarning(
                   feature="module_shape",
                   level=WarningLevel.WARNING,
                   reason="Shape not approved for production use",
                   original_value=current_shape,
                   fallback_value="square",
                   suggestion=f"Use approved shapes: {', '.join(self.allowed_shapes)}"
               ))

           return warnings

   # Use custom rule
   custom_manager = DegradationManager(rules=[OrganizationPolicyRule()])
   intents = IntentsConfig(
       style=StyleIntents(
           module_shape="pyramid",  # Will be degraded
           palette={"fg": "#ff00ff", "bg": "#ffffff"}  # Will be degraded
       )
   )

   from segnomms.config import RenderingConfig
   # Apply custom degradation manager to a configuration
   config = RenderingConfig.from_kwargs(shape="pyramid", dark="#ff00ff", light="#ffffff")
   degraded_config, result = custom_manager.apply_degradation(config)

Monitoring Degradation Patterns
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from collections import defaultdict
   import json
   from typing import Dict, List

   class DegradationAnalyzer:
       """Analyze degradation patterns for system optimization."""

       def __init__(self):
           self.feature_degradations = defaultdict(int)
           self.fallback_usage = defaultdict(int)
           self.user_patterns = defaultdict(list)
           self.time_patterns = defaultdict(list)

       def record_result(self, result, user_id: str = None):
           """Record degradation event for analysis."""
           timestamp = datetime.utcnow().isoformat()

           for warning in result.warnings:
               if warning.code == "FEATURE_DEGRADED":
                   feature = warning.context.get('original_feature', 'unknown')
                   fallback = warning.context.get('fallback_feature', 'unknown')

                   self.feature_degradations[feature] += 1
                   self.fallback_usage[f"{feature}->{fallback}"] += 1
                   self.time_patterns[feature].append(timestamp)

                   if user_id:
                       self.user_patterns[user_id].append({
                           "feature": feature,
                           "fallback": fallback,
                           "timestamp": timestamp
                       })

       def generate_insights(self) -> Dict:
           """Generate actionable insights from degradation data."""
           total_degradations = sum(self.feature_degradations.values())

           if total_degradations == 0:
               return {"message": "No degradations recorded"}

           # Find most problematic features
           top_degraded = sorted(
               self.feature_degradations.items(),
               key=lambda x: x[1],
               reverse=True
           )[:5]

           # Find most common fallback patterns
           top_fallbacks = sorted(
               self.fallback_usage.items(),
               key=lambda x: x[1],
               reverse=True
           )[:5]

           # Generate recommendations
           recommendations = []
           for feature, count in top_degraded:
               if count > 50:  # High degradation threshold
                   recommendations.append(
                       f"Consider implementing native support for '{feature}' "
                       f"(degraded {count} times, {count/total_degradations*100:.1f}% of all degradations)"
                   )

           return {
               "total_degradations": total_degradations,
               "most_degraded_features": top_degraded,
               "most_common_fallbacks": top_fallbacks,
               "recommendations": recommendations,
               "degradation_trends": self._analyze_trends()
           }

       def _analyze_trends(self) -> Dict:
           """Analyze temporal patterns in degradations."""
           # Implementation would analyze time_patterns for trends
           return {
               "peak_degradation_hours": "Analysis not implemented",
               "trending_features": "Analysis not implemented"
           }

   # Usage in production monitoring
   analyzer = DegradationAnalyzer()

   # Record results over time
   for request in daily_requests:
       result = render_with_intents(request.payload, request.intents)
       analyzer.record_result(result, request.user_id)

   # Generate daily insights
   insights = analyzer.generate_insights()
   print(json.dumps(insights, indent=2))

Best Practices for Intent-Based API
-----------------------------------

1. **Error Handling Strategy**

.. code-block:: python

   # Always use specific exception handling
   try:
       result = render_with_intents(payload, intents)
   except IntentValidationError as e:
       # Handle validation issues specifically
       pass
   except UnsupportedIntentError as e:
       # Handle unsupported features specifically
       pass
   except SegnoMMSError as e:
       # Handle other SegnoMMS errors
       pass

2. **Graceful Degradation**

.. code-block:: python

   # Always check for degradation warnings
   if result.has_warnings:
       for warning in result.warnings:
           if warning.code == "FEATURE_DEGRADED":
               log_degradation(warning)

3. **Production Monitoring**

.. code-block:: python

   # Track degradation patterns for feature usage insights
   degradation_metrics = track_degradations(result.warnings)

   # Monitor scanability predictions
   if result.scanability_prediction < 0.8:
       alert_low_scanability(result)

4. **Fallback Strategies**

.. code-block:: python

   # Implement progressive fallback strategies
   fallback_intents = [
       intents,                    # Original
       simplified_intents,         # Simplified version
       IntentsConfig()            # Minimal fallback
   ]

   for intent_config in fallback_intents:
       try:
           return render_with_intents(payload, intent_config)
       except Exception:
           continue
