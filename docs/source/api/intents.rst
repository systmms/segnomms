Intent-Based API
================

The SegnoMMS Intent-Based API provides a high-level, declarative interface for QR code generation. Instead of
specifying exact technical parameters, you describe your intentions and the system translates them into
appropriate configurations with graceful degradation and comprehensive feedback.

Overview
--------

The Intent-Based API:

* Accepts high-level intents instead of technical parameters
* Provides graceful degradation when features aren't available
* Returns detailed transformation reports
* Includes performance metrics and scanability predictions
* Tracks all intent processing for transparency

Quick Example
~~~~~~~~~~~~~

.. code-block:: python

   from segnomms.intents import render_with_intents
   from segnomms.intents.models import PayloadConfig, IntentsConfig, StyleIntents

   # Describe what you want
   intents = IntentsConfig(
       style=StyleIntents(
           module_shape="squircle",
           palette={"fg": "#1a1a2e", "bg": "#ffffff"}
       )
   )

   # Get comprehensive result
   payload = PayloadConfig(text="Hello World")
   result = render_with_intents(payload, intents)
   print(f"Scanability: {result.scanability_prediction}")

Intent Categories
-----------------

PayloadConfig
~~~~~~~~~~~~~

Specifies the content to encode in the QR code, with support for various data types and common payload formats.

.. autoclass:: segnomms.intents.models.PayloadConfig
   :members:
   :undoc-members:
   :show-inheritance:

**Supported Content Types:**

* ``text``: Plain text content ✅
* ``url``: Website URLs with automatic validation ✅
* ``data``: Binary data for custom encoding ✅
* ``email``: Email addresses with mailto: generation ✅
* ``phone``: Phone numbers with tel: generation ✅
* ``sms``: SMS content with automatic SMS URL formatting ✅
* ``wifi_ssid`` / ``wifi_password``: WiFi network configuration ✅
* ``eci``: Extended Channel Interpretation for international characters ✅
* ``error_correction``: Override default error correction level ✅

StyleIntents
~~~~~~~~~~~~

Visual styling and shape configuration.

.. autoclass:: segnomms.intents.models.StyleIntents
   :members:
   :undoc-members:
   :show-inheritance:

**Supported Features:**

* ``module_shape``: Basic shape for QR modules (square, circle, rounded, etc.) ✅
* ``merge``: Module merging strategy ✅
* ``connectivity``: Neighbor detection mode ✅
* ``corner_radius``: Corner radius for applicable shapes ✅
* ``patterns``: Pattern-specific shapes ✅
* ``palette``: Color configuration ✅

FrameIntents
~~~~~~~~~~~~

Frame and edge treatment configuration.

.. autoclass:: segnomms.intents.models.FrameIntents
   :members:
   :undoc-members:
   :show-inheritance:

**Supported Features:**

* ``shape``: Frame shape (square, circle, rounded-rect, etc.) ✅
* ``clip_mode``: Edge treatment (clip, fade, scale) ✅
* ``corner_radius``: Frame corner radius ✅
* ``fade_distance``: Fade effect distance ✅
* ``scale_distance``: Scale effect distance ✅

ReserveIntents
~~~~~~~~~~~~~~

Reserve area (centerpiece) configuration.

.. autoclass:: segnomms.intents.models.ReserveIntents
   :members:
   :undoc-members:
   :show-inheritance:

**Supported Features:**

* ``area_pct``: Reserve area size as percentage ✅
* ``shape``: Reserve area shape ✅
* ``placement``: Placement mode (center/arbitrary) ✅
* ``mode``: Knockout or imprint mode ✅
* ``offset_x``, ``offset_y``: Position offsets ✅

AccessibilityIntents
~~~~~~~~~~~~~~~~~~~~

Accessibility and ARIA support configuration.

.. autoclass:: segnomms.intents.models.AccessibilityIntents
   :members:
   :undoc-members:
   :show-inheritance:

**Supported Features:**

* ``ids``: Stable ID generation ✅
* ``id_prefix``: Custom ID prefix ✅
* ``title``: SVG title element ✅
* ``desc``: SVG description element ✅
* ``aria``: ARIA attribute support ✅

ValidationIntents
~~~~~~~~~~~~~~~~~

Validation and quality control configuration.

.. autoclass:: segnomms.intents.models.ValidationIntents
   :members:
   :undoc-members:
   :show-inheritance:

**Supported Features:**

* ``enforce_scanability``: Scanability validation ✅
* ``min_contrast``: Minimum contrast ratio ✅
* ``quiet_zone``: Quiet zone size validation ✅

InteractivityIntents
~~~~~~~~~~~~~~~~~~~~

Interactive features configuration.

.. autoclass:: segnomms.intents.models.InteractivityIntents
   :members:
   :undoc-members:
   :show-inheritance:

**Supported Features:**

* ``hover_effects``: Basic hover effects ✅
* ``tooltips``: Module tooltips ✅
* ``hover_scale``: Scale on hover 🚧 (planned)
* ``hover_brightness``: Brightness adjustment 🚧 (planned)
* ``click_handlers``: Click event handlers 🚧 (planned)
* ``tooltip_template``: Custom tooltip content 🚧 (planned)
* ``cursor_style``: Cursor styling 🚧 (planned)

AnimationIntents
~~~~~~~~~~~~~~~~

CSS animation configuration.

.. autoclass:: segnomms.intents.models.AnimationIntents
   :members:
   :undoc-members:
   :show-inheritance:

**Supported Features:**

* ``fade_in``: Fade-in animation ✅
* ``fade_duration``: Animation duration ✅
* ``stagger_animation``: Staggered module reveal ✅
* ``stagger_delay``: Delay between modules ✅
* ``pulse_effect``: Finder pattern pulse ✅
* ``transition_timing``: CSS timing function ✅

.. note::
   Animation features were recently implemented. See :doc:`animation` for details.

PerformanceIntents
~~~~~~~~~~~~~~~~~~

Performance optimization hints.

.. autoclass:: segnomms.intents.models.PerformanceIntents
   :members:
   :undoc-members:
   :show-inheritance:

**Supported Features:**

* ``optimize_for``: Optimization priority hint 🚧 (advisory only)
* Other features planned for future releases

BrandingIntents
~~~~~~~~~~~~~~~

Branding and customization configuration.

.. autoclass:: segnomms.intents.models.BrandingIntents
   :members:
   :undoc-members:
   :show-inheritance:

**Supported Features:**

* ``brand_colors``: Brand color palette mapping ✅
* ``logo_url``: Enables centerpiece for logo space ✅
* ``logo_padding``: Logo padding configuration 🚧 (planned)
* ``watermark``: Watermark support 🚧 (planned)
* ``custom_patterns``: Custom patterns 🚧 (planned)
* ``theme_preset``: Theme presets 🚧 (experimental)

AdvancedIntents
~~~~~~~~~~~~~~~

Advanced QR code features.

.. autoclass:: segnomms.intents.models.AdvancedIntents
   :members:
   :undoc-members:
   :show-inheritance:

**Supported Features:**

* ``mask_pattern``: Manual mask pattern selection ✅
* ``structured_append``: Multi-symbol sequences ✅
* ``micro_qr``: Micro QR format 🚧 (planned)
* ``force_version``: Force specific version ✅
* ``boost_ecc``: Enhanced error correction ✅

Result Models
-------------

RenderingResult
~~~~~~~~~~~~~~~

The comprehensive result returned by intent-based rendering.

.. autoclass:: segnomms.intents.models.RenderingResult
   :members:
   :undoc-members:
   :show-inheritance:

**Key Properties:**

* ``svg_content``: Generated SVG as string
* ``warnings``: List of warnings generated during processing
* ``metrics``: Performance and quality metrics
* ``used_options``: Actually applied configuration
* ``translation_report``: Detailed intent transformation report
* ``scanability_prediction``: Predicted scanability level

IntentTranslationReport
~~~~~~~~~~~~~~~~~~~~~~~

Detailed report of how intents were processed.

.. autoclass:: segnomms.intents.models.IntentTranslationReport
   :members:
   :undoc-members:
   :show-inheritance:

TransformationStep
~~~~~~~~~~~~~~~~~~

Individual transformation applied to an intent.

.. autoclass:: segnomms.intents.models.TransformationStep
   :members:
   :undoc-members:
   :show-inheritance:

DegradationDetail
~~~~~~~~~~~~~~~~~

Information about degraded features.

.. autoclass:: segnomms.intents.models.DegradationDetail
   :members:
   :undoc-members:
   :show-inheritance:

WarningInfo
~~~~~~~~~~~

Structured warning information.

.. autoclass:: segnomms.intents.models.WarningInfo
   :members:
   :undoc-members:
   :show-inheritance:

PerformanceMetrics
~~~~~~~~~~~~~~~~~~

Performance and quality metrics.

.. autoclass:: segnomms.intents.models.PerformanceMetrics
   :members:
   :undoc-members:
   :show-inheritance:

Usage Examples
--------------

Basic Intent Usage
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from segnomms.intents import render_with_intents
   from segnomms.intents.models import PayloadConfig, IntentsConfig, StyleIntents

   # Simple style intent
   intents = IntentsConfig(
       style=StyleIntents(
           module_shape="circle",
           palette={"fg": "#000000", "bg": "#ffffff"}
       )
   )

   payload = PayloadConfig(text="https://example.com")
   result = render_with_intents(payload, intents)

   # Check if any warnings were generated
   if result.has_warnings:
       for warning in result.warnings:
           print(f"[{warning.code}] {warning.detail}")

Pattern-Specific Styling
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   intents = IntentsConfig(
       style=StyleIntents(
           module_shape="squircle",
           patterns={
               "finder": "rounded",    # Rounded finder patterns
               "timing": "square",     # Square timing patterns
               "alignment": "circle",  # Circular alignment patterns
               "data": "squircle"      # Squircle data modules
           }
       )
   )

   payload = PayloadConfig(text="Hello World")
   result = render_with_intents(payload, intents)

Branding and Reserve Area
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   intents = IntentsConfig(
       branding=BrandingIntents(
           brand_colors={
               "primary": "#1a73e8",
               "secondary": "#ea4335"
           },
           logo_url="https://example.com/logo.png"  # Enables centerpiece
       ),
       reserve=ReserveIntents(
           area_pct=15.0,  # 15% of QR code area
           shape="circle",
           mode="knockout"  # Remove modules in logo area
       )
   )

Accessibility Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   intents = IntentsConfig(
       accessibility=AccessibilityIntents(
           ids=True,  # Generate stable IDs
           id_prefix="myqr",
           title="Company Website QR Code",
           desc="Scan to visit our website",
           aria=True  # Enable ARIA attributes
       )
   )

Animation Setup
~~~~~~~~~~~~~~~

.. code-block:: python

   intents = IntentsConfig(
       animation=AnimationIntents(
           fade_in=True,
           fade_duration=0.6,
           stagger_animation=True,
           stagger_delay=0.02,
           pulse_effect=True,
           transition_timing="ease-out"
       )
   )

Analyzing Results
~~~~~~~~~~~~~~~~~

.. code-block:: python

   from segnomms.intents import render_with_intents
   result = render_with_intents(payload, intents)

   # Check transformation report
   report = result.translation_report
   print(f"Transformations: {len(report.transformation_steps)}")
   print(f"Degradations: {len(report.degradation_details)}")

   # Compare requested vs applied
   for step in report.transformation_steps:
       if step.transformation_type == "degraded":
           print(f"{step.intent_path}: {step.original_value} → {step.transformed_value}")
           print(f"Reason: {step.reason}")

   # Check scanability
   print(f"Scanability prediction: {result.scanability_prediction}")
   print(f"Minimum module size: {result.metrics.min_module_px}px")
   print(f"Contrast ratio: {result.metrics.contrast_ratio}")

Error Handling and Degradation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from segnomms.intents import render_with_intents
   from segnomms.exceptions import (
       IntentValidationError,
       UnsupportedIntentError,
       IntentDegradationError
   )

   try:
       result = render_with_intents(payload, intents)

       # Check for degradation warnings (non-blocking)
       if result.has_warnings:
           for warning in result.warnings:
               if warning.code == "FEATURE_DEGRADED":
                   print(f"Feature degraded: {warning.detail}")
                   print(f"Reason: {warning.context.get('reason', 'Unknown')}")
                   print(f"Suggestion: {warning.context.get('suggestion', 'None')}")

   except IntentValidationError as e:
       print(f"Invalid intent at {e.intent_path}: {e.original_value}")
       if e.suggestion:
           print(f"Suggestion: {e.suggestion}")
   except UnsupportedIntentError as e:
       print(f"Unsupported feature: {e.feature}")
       print(f"Alternatives: {e.alternatives}")
       print(f"Planned for: {e.planned_version}")
   except IntentDegradationError as e:
       print(f"Degradation error: {e.message}")
       print(f"Failed degradation: {e.details.get('failed_feature', 'Unknown')}")

Advanced PayLoad Examples
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Email with subject and body
   email_payload = PayloadConfig(
       email="contact@example.com",
       text="subject=Hello&body=Thank you for scanning!"
   )

   # WiFi network configuration
   wifi_payload = PayloadConfig(
       wifi_ssid="MyNetwork",
       wifi_password="SecurePassword123",
       text="WIFI:T:WPA;S:MyNetwork;P:SecurePassword123;;"
   )

   # International content with ECI
   international_payload = PayloadConfig(
       text="Hello 世界! こんにちは",
       eci=26  # UTF-8 encoding
   )

   # Phone with SMS fallback
   phone_payload = PayloadConfig(
       phone="+1-555-123-4567",
       sms="Hello! Thanks for scanning our QR code."
   )

Degradation System Integration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The intent processing system integrates with SegnoMMS's degradation manager to provide graceful handling of unsupported features:

.. code-block:: python

   from segnomms.intents import render_with_intents
   from segnomms.intents.models import PayloadConfig, IntentsConfig, StyleIntents, FrameIntents

   # Request advanced features that may not be available
   intents = IntentsConfig(
       style=StyleIntents(
           module_shape="pyramid",  # Unsupported shape
           patterns={"finder": "hexagon"}  # Unsupported pattern
       ),
       frame=FrameIntents(
           shape="star",  # Unsupported frame
           clip_mode="gradient"  # Unsupported clip mode
       )
   )

   payload = PayloadConfig(text="Hello World")
   result = render_with_intents(payload, intents)

   # Analyze degradation results
   report = result.translation_report
   for step in report.transformation_steps:
       if step.transformation_type == "degraded":
           print(f"Feature degraded: {step.intent_path}")
           print(f"Original: {step.original_value}")
           print(f"Applied: {step.transformed_value}")
           print(f"Reason: {step.reason}")

   # Check final configuration
   print(f"Actual shape used: {result.used_options.geometry.shape}")
   print(f"Scanability maintained: {result.scanability_prediction}")

Real-time Intent Validation
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from segnomms.intents.processor import IntentProcessor
   from segnomms.intents.models import IntentsConfig, ValidationIntents

   processor = IntentProcessor()

   # Enable strict validation
   intents = IntentsConfig(
       validation=ValidationIntents(
           enforce_scanability=True,
           min_contrast=7.0,  # AAA compliance
           quiet_zone=True
       )
   )

   try:
       # Pre-validate intents before processing
       validation_result = processor.validate_intents(intents)
       if not validation_result.is_valid:
           print("Validation errors:")
           for error in validation_result.errors:
               print(f"  - {error.path}: {error.message}")

       # Process with validated intents
       result = processor.process_intents("Hello World", intents)

   except IntentValidationError as e:
       # Handle validation failures
       print(f"Intent validation failed: {e.message}")
       print(f"Path: {e.intent_path}")
       print(f"Invalid value: {e.original_value}")

Performance Metrics Integration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   result = render_with_intents(payload, intents)

   # Access detailed performance metrics
   metrics = result.metrics
   print(f"Rendering time: {metrics.rendering_time_ms}ms")
   print(f"SVG generation: {metrics.svg_generation_time_ms}ms")
   print(f"Quiet zone: {metrics.actual_quiet_zone}")
   print(f"Contrast ratio: {metrics.contrast_ratio:.2f}")
   print(f"Minimum module size: {metrics.min_module_px}px")

   # Performance warnings
   if metrics.processing_time_ms > 1000:
       print("⚠️ Slow processing detected - consider simplifying intents")

   if metrics.contrast_ratio < 4.5:
       print("⚠️ Contrast ratio below WCAG AA standards")

   # Memory usage tracking
   if hasattr(metrics, 'memory_usage_mb'):
       print(f"Memory used: {metrics.memory_usage_mb:.1f}MB")

Batch Intent Processing
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from typing import List, Dict
   from segnomms.intents.models import IntentsConfig, RenderingResult

   def process_batch_intents(
       payloads: List[str],
       intents_list: List[IntentsConfig]
   ) -> Dict[str, RenderingResult]:
       """Process multiple intents with aggregated error handling."""

       results = {}
       errors = []

       for i, (payload, intents) in enumerate(zip(payloads, intents_list)):
           try:
               result = render_with_intents(payload, intents)
               results[f"qr_{i}"] = result

               # Collect warnings for batch analysis
               if result.has_warnings:
                   for warning in result.warnings:
                       errors.append({
                           "qr_index": i,
                           "warning": warning.code,
                           "detail": warning.detail
                       })

           except IntentValidationError as e:
               errors.append({
                   "qr_index": i,
                   "error": "validation_failed",
                   "detail": e.message,
                   "path": e.intent_path
               })

       # Generate batch report
       print(f"Processed {len(results)}/{len(payloads)} QR codes successfully")
       if errors:
           print(f"Encountered {len(errors)} warnings/errors:")
           for error in errors[:5]:  # Show first 5
               print(f"  QR {error['qr_index']}: {error.get('warning', error.get('error'))}")

       return results

Best Practices
--------------

1. **Start Simple**: Begin with basic intents and add complexity as needed
2. **Handle Degradation Gracefully**: Always check warnings and handle degraded features appropriately
3. **Validate Early**: Use intent validation before processing to catch issues early
4. **Monitor Performance**: Check processing time and memory usage for large QR codes
5. **Check Scanability**: Verify scanability prediction and contrast ratios before production
6. **Use Structured Error Handling**: Catch specific exception types for better error recovery
7. **Test Edge Cases**: Test with unsupported features to verify degradation behavior
8. **Batch Processing**: Use batch processing for multiple QR codes to improve efficiency
9. **Production Monitoring**: Track degradation warnings in production for feature usage insights
10. **Fallback Strategies**: Implement fallback configurations for critical features

Intent Processing Flow
----------------------

The intent processing system follows a comprehensive pipeline with integrated degradation handling:

1. **Intent Validation**:
   - Validate intent structure and field types
   - Check for required fields and value ranges
   - Raise IntentValidationError for invalid intents

2. **Capability Discovery**:
   - Query capability manifest for available features
   - Compare requested intents against system capabilities
   - Identify features requiring degradation

3. **Intent Transformation**:
   - Convert high-level intents to technical parameters
   - Apply feature mappings and value transformations
   - Generate intermediate configuration objects

4. **Degradation Processing**:
   - Apply degradation rules from rendering system
   - Capture degradation warnings and alternatives
   - Maintain scanability during feature fallbacks

5. **Configuration Building**:
   - Create final RenderingConfig object
   - Merge degraded and non-degraded settings
   - Validate final configuration consistency

6. **QR Code Generation**:
   - Generate QR code using validated configuration
   - Apply advanced features (ECI, structured append, etc.)
   - Handle generation errors gracefully

7. **Result Assembly**:
   - Build comprehensive RenderingResult
   - Include performance metrics and warnings
   - Generate transformation report for transparency

8. **Post-processing Validation**:
   - Verify scanability predictions
   - Check contrast ratios and accessibility
   - Add final warnings for production considerations

Transformation Types
--------------------

* **accepted**: Intent applied exactly as requested without modification
* **degraded**: Intent modified to use available fallback feature with warning
* **rejected**: Intent cannot be applied and was removed (with error or warning)
* **modified**: Intent value adjusted for compatibility (e.g., clamped to valid range)
* **enhanced**: Intent upgraded to use better available feature
* **conditional**: Intent applied only when certain conditions are met

Degradation Integration Details
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The intent processor integrates seamlessly with the degradation system:

.. code-block:: python

   # Example of degradation flow
   original_intent = StyleIntents(module_shape="pyramid")  # Unsupported

   # Step 1: Intent processor detects unsupported feature
   # Step 2: Queries degradation manager for alternatives
   # Step 3: Applies fallback (e.g., "squircle") with warning
   # Step 4: Captures transformation details in report

   from segnomms.intents import render_with_intents
   from segnomms.intents.models import PayloadConfig
   result = render_with_intents(PayloadConfig(text="Hello"), intents)

   # Degradation captured in transformation report
   transformation = result.translation_report.transformation_steps[0]
   assert transformation.transformation_type == "degraded"
   assert transformation.original_value == "pyramid"
   assert transformation.transformed_value == "squircle"
   assert "pyramid not supported" in transformation.reason

Future Enhancements
-------------------

* Machine learning for intent optimization
* Auto-optimization based on content type
* Intent templates for common use cases
* Visual preview generation
* Real-time intent validation
