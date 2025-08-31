Exception Handling
==================

SegnoMMS provides a comprehensive exception hierarchy for better error handling, debugging, and user experience.
All exceptions inherit from :class:`~segnomms.exceptions.SegnoMMSError` and provide structured error information.

Exception Hierarchy
-------------------

.. code-block:: text

   SegnoMMSError (base)
   ├── ConfigurationError
   │   ├── ValidationError
   │   ├── IntentValidationError
   │   ├── PresetNotFoundError
   │   └── IncompatibleConfigError
   ├── RenderingError
   │   ├── MatrixError
   │   │   ├── MatrixSizeError
   │   │   └── MatrixBoundsError
   │   ├── ShapeRenderingError
   │   ├── SVGGenerationError
   │   └── PerformanceError
   ├── IntentProcessingError
   │   ├── UnsupportedIntentError
   │   ├── IntentDegradationError
   │   └── IntentTransformationError
   ├── ColorError
   │   ├── InvalidColorFormatError
   │   ├── ContrastRatioError
   │   └── PaletteValidationError
   ├── CapabilityError
   │   ├── FeatureNotSupportedError
   │   └── CapabilityManifestError
   └── DependencyError
       ├── MissingDependencyError
       └── OptionalFeatureUnavailableError

Base Exception
--------------

.. autoexception:: segnomms.exceptions.SegnoMMSError
   :members:
   :undoc-members:
   :show-inheritance:

All SegnoMMS exceptions inherit from this base class and provide structured error information:

* ``message``: Human-readable error message
* ``code``: Stable error code for programmatic handling
* ``details``: Dictionary with additional error context
* ``suggestion``: Suggestion for resolving the error

Example Usage
~~~~~~~~~~~~~

.. code-block:: python

   from segnomms.intents import render_with_intents
   from segnomms.exceptions import SegnoMMSError

   try:
       # Some SegnoMMS operation
       result = render_with_intents(payload, intents)
   except SegnoMMSError as e:
       print(f"Error [{e.code}]: {e.message}")
       if e.suggestion:
           print(f"Suggestion: {e.suggestion}")
       if e.details:
           print(f"Details: {e.details}")

       # Convert to dictionary for API responses
       error_dict = e.to_dict()

Configuration Errors
--------------------

ValidationError
~~~~~~~~~~~~~~~

.. autoexception:: segnomms.exceptions.ValidationError
   :members:
   :undoc-members:
   :show-inheritance:

Raised when configuration values fail validation rules.

.. code-block:: python

   from segnomms.exceptions import ValidationError
   from segnomms.config import RenderingConfig

   try:
       config = RenderingConfig(scale=-1)  # Invalid scale
   except ValidationError as e:
       print(f"Invalid {e.field}: {e.value}")
       print(f"Fix: {e.suggestion}")

IntentValidationError
~~~~~~~~~~~~~~~~~~~~~

.. autoexception:: segnomms.exceptions.IntentValidationError
   :members:
   :undoc-members:
   :show-inheritance:

Raised for invalid intent configurations in the intent-based API.

.. code-block:: python

   from segnomms.exceptions import IntentValidationError
   from segnomms.intents.models import IntentsConfig, StyleIntents

   try:
       intents = IntentsConfig(
           style=StyleIntents(corner_radius=5.0)  # Out of valid range
       )
   except IntentValidationError as e:
       print(f"Invalid intent at {e.intent_path}")
       print(f"Original value: {e.original_value}")

PresetNotFoundError
~~~~~~~~~~~~~~~~~~~

.. autoexception:: segnomms.exceptions.PresetNotFoundError
   :members:
   :undoc-members:
   :show-inheritance:

Raised when a requested configuration preset doesn't exist.

IncompatibleConfigError
~~~~~~~~~~~~~~~~~~~~~~~

.. autoexception:: segnomms.exceptions.IncompatibleConfigError
   :members:
   :undoc-members:
   :show-inheritance:

Raised when configuration options are incompatible with each other.

Rendering Errors
----------------

RenderingError
~~~~~~~~~~~~~~

.. autoexception:: segnomms.exceptions.RenderingError
   :members:
   :undoc-members:
   :show-inheritance:

Base class for all rendering-related errors.

MatrixError
~~~~~~~~~~~

.. autoexception:: segnomms.exceptions.MatrixError
   :members:
   :undoc-members:
   :show-inheritance:

Base class for QR matrix-related errors.

MatrixSizeError
~~~~~~~~~~~~~~~

.. autoexception:: segnomms.exceptions.MatrixSizeError
   :members:
   :undoc-members:
   :show-inheritance:

Raised when QR matrix has invalid dimensions.

MatrixBoundsError
~~~~~~~~~~~~~~~~~

.. autoexception:: segnomms.exceptions.MatrixBoundsError
   :members:
   :undoc-members:
   :show-inheritance:

Raised when attempting to access matrix positions out of bounds.

ShapeRenderingError
~~~~~~~~~~~~~~~~~~~

.. autoexception:: segnomms.exceptions.ShapeRenderingError
   :members:
   :undoc-members:
   :show-inheritance:

Raised when shape rendering fails.

SVGGenerationError
~~~~~~~~~~~~~~~~~~

.. autoexception:: segnomms.exceptions.SVGGenerationError
   :members:
   :undoc-members:
   :show-inheritance:

Raised when SVG generation fails.

PerformanceError
~~~~~~~~~~~~~~~~

.. autoexception:: segnomms.exceptions.PerformanceError
   :members:
   :undoc-members:
   :show-inheritance:

Raised when performance limits are exceeded.

Intent Processing Errors
------------------------

IntentProcessingError
~~~~~~~~~~~~~~~~~~~~~

.. autoexception:: segnomms.exceptions.IntentProcessingError
   :members:
   :undoc-members:
   :show-inheritance:

Base class for intent processing errors.

UnsupportedIntentError
~~~~~~~~~~~~~~~~~~~~~~

.. autoexception:: segnomms.exceptions.UnsupportedIntentError
   :members:
   :undoc-members:
   :show-inheritance:

Raised when an intent feature is not supported.

.. code-block:: python

   from segnomms.exceptions import UnsupportedIntentError

   try:
       # Request unsupported feature
       intents = IntentsConfig(style=StyleIntents(module_shape="pyramid"))
   except UnsupportedIntentError as e:
       print(f"Unsupported: {e.feature}")
       print(f"Alternatives: {e.alternatives}")
       print(f"Planned for: {e.planned_version}")

IntentDegradationError
~~~~~~~~~~~~~~~~~~~~~~

.. autoexception:: segnomms.exceptions.IntentDegradationError
   :members:
   :undoc-members:
   :show-inheritance:

Raised when intent degradation fails.

IntentTransformationError
~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoexception:: segnomms.exceptions.IntentTransformationError
   :members:
   :undoc-members:
   :show-inheritance:

Raised when intent transformation fails.

Color Errors
------------

ColorError
~~~~~~~~~~

.. autoexception:: segnomms.exceptions.ColorError
   :members:
   :undoc-members:
   :show-inheritance:

Base class for color-related errors.

InvalidColorFormatError
~~~~~~~~~~~~~~~~~~~~~~~

.. autoexception:: segnomms.exceptions.InvalidColorFormatError
   :members:
   :undoc-members:
   :show-inheritance:

Raised when color format is invalid.

.. code-block:: python

   from segnomms.exceptions import InvalidColorFormatError

   try:
       config = RenderingConfig(dark="not-a-color")
   except InvalidColorFormatError as e:
       print(f"Invalid color: {e.color}")
       print(f"Accepted formats: {e.accepted_formats}")

ContrastRatioError
~~~~~~~~~~~~~~~~~~

.. autoexception:: segnomms.exceptions.ContrastRatioError
   :members:
   :undoc-members:
   :show-inheritance:

Raised when color contrast is insufficient for accessibility or scanability.

.. code-block:: python

   from segnomms.exceptions import ContrastRatioError

   try:
       # Colors with poor contrast
       config = RenderingConfig(dark="#888888", light="#999999")
   except ContrastRatioError as e:
       print(f"Contrast too low: {e.ratio:.2f} < {e.required_ratio}")
       print(f"Standard: {e.standard}")

PaletteValidationError
~~~~~~~~~~~~~~~~~~~~~~

.. autoexception:: segnomms.exceptions.PaletteValidationError
   :members:
   :undoc-members:
   :show-inheritance:

Raised when color palette validation fails.

Capability Errors
-----------------

CapabilityError
~~~~~~~~~~~~~~~

.. autoexception:: segnomms.exceptions.CapabilityError
   :members:
   :undoc-members:
   :show-inheritance:

Base class for capability-related errors.

FeatureNotSupportedError
~~~~~~~~~~~~~~~~~~~~~~~~

.. autoexception:: segnomms.exceptions.FeatureNotSupportedError
   :members:
   :undoc-members:
   :show-inheritance:

Raised when a feature is not supported in the current version.

CapabilityManifestError
~~~~~~~~~~~~~~~~~~~~~~~

.. autoexception:: segnomms.exceptions.CapabilityManifestError
   :members:
   :undoc-members:
   :show-inheritance:

Raised when the capability manifest has issues.

Dependency Errors
-----------------

DependencyError
~~~~~~~~~~~~~~~

.. autoexception:: segnomms.exceptions.DependencyError
   :members:
   :undoc-members:
   :show-inheritance:

Base class for dependency-related errors.

MissingDependencyError
~~~~~~~~~~~~~~~~~~~~~~

.. autoexception:: segnomms.exceptions.MissingDependencyError
   :members:
   :undoc-members:
   :show-inheritance:

Raised when a required dependency is missing.

.. code-block:: python

   from segnomms.exceptions import MissingDependencyError

   try:
       # Feature requiring optional dependency
       result = some_feature_requiring_opencv()
   except MissingDependencyError as e:
       print(f"Missing: {e.dependency}")
       print(f"Required for: {e.feature}")
       print(f"Install: {e.install_command}")

OptionalFeatureUnavailableError
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoexception:: segnomms.exceptions.OptionalFeatureUnavailableError
   :members:
   :undoc-members:
   :show-inheritance:

Raised when an optional feature is unavailable.

Error Handling Best Practices
-----------------------------

Intent-Specific Error Patterns
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When working with the intent-based API, use structured error handling for different scenarios:

.. code-block:: python

   from segnomms.intents import render_with_intents
   from segnomms.exceptions import (
       IntentValidationError,
       UnsupportedIntentError,
       IntentDegradationError,
       IntentTransformationError,
       ContrastRatioError,
       SegnoMMSError
   )

   def robust_intent_processing(payload: str, intents: IntentsConfig):
       """Robust intent processing with comprehensive error handling."""
       try:
           result = render_with_intents(payload, intents)

           # Success path - check for warnings
           if result.has_warnings:
               handle_intent_warnings(result.warnings)

           return result

       except IntentValidationError as e:
           # Invalid intent structure or values
           print(f"Intent validation failed at {e.intent_path}")
           print(f"Invalid value: {e.original_value}")
           print(f"Expected: {e.details.get('expected_type', 'Valid value')}")
           if e.suggestion:
               print(f"Suggestion: {e.suggestion}")

           # Try with corrected intent
           return retry_with_fixed_intent(payload, intents, e)

       except UnsupportedIntentError as e:
           # Feature not available - graceful degradation
           print(f"Feature '{e.feature}' not supported")
           print(f"Available alternatives: {e.alternatives}")

           # Apply automatic fallback
           fallback_intents = apply_feature_fallback(intents, e.feature, e.alternatives)
           return render_with_intents(payload, fallback_intents)

       except IntentDegradationError as e:
           # Degradation system failed
           print(f"Degradation failed for: {e.details.get('failed_feature')}")
           print(f"Reason: {e.message}")

           # Use simplified configuration
           safe_intents = create_safe_fallback_intents(intents)
           return render_with_intents(payload, safe_intents)

       except ContrastRatioError as e:
           # Accessibility issue - adjust colors
           print(f"Contrast ratio {e.ratio:.2f} below required {e.required_ratio}")

           # Auto-adjust colors for accessibility
           adjusted_intents = improve_intent_contrast(intents, e.required_ratio)
           return render_with_intents(payload, adjusted_intents)

       except IntentTransformationError as e:
           # Internal transformation failed
           print(f"Intent transformation failed: {e.message}")
           print(f"Failed step: {e.details.get('transformation_step', 'Unknown')}")

           # Log for debugging and use minimal intents
           log_transformation_error(e, payload, intents)
           minimal_intents = create_minimal_intents()
           return render_with_intents(payload, minimal_intents)

       except SegnoMMSError as e:
           # Any other SegnoMMS error
           print(f"SegnoMMS error [{e.code}]: {e.message}")
           if e.suggestion:
               print(f"Suggestion: {e.suggestion}")

           # Log error details for analysis
           log_error_with_context(e, payload, intents)
           raise  # Re-raise for higher-level handling

Catching Specific Exceptions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Always catch the most specific exception type for better error recovery:

.. code-block:: python

   from segnomms.intents import render_with_intents
   from segnomms.exceptions import (
       ValidationError,
       UnsupportedIntentError,
       ContrastRatioError,
       SegnoMMSError
   )

   try:
       result = render_with_intents(payload, intents)
   except ValidationError as e:
       # Handle validation errors specifically
       fix_validation_error(e.field, e.value, e.suggestion)
   except UnsupportedIntentError as e:
       # Gracefully degrade unsupported features
       fallback_to_alternative(e.alternatives)
   except ContrastRatioError as e:
       # Adjust colors for better contrast
       improve_contrast(e.foreground, e.background, e.required_ratio)
   except SegnoMMSError as e:
       # Handle any other SegnoMMS error
       log_error(e.code, e.message, e.details)

Production Error Recovery Strategies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Implement robust error recovery for production systems:

.. code-block:: python

   from typing import Optional, Dict, Any
   import logging

   class ProductionIntentHandler:
       """Production-ready intent handler with comprehensive error recovery."""

       def __init__(self, renderer):
           self.renderer = renderer
           self.logger = logging.getLogger(__name__)
           self.fallback_configs = self._load_fallback_configs()

       def process_with_recovery(
           self,
           payload: str,
           intents: IntentsConfig,
           max_retries: int = 3
       ) -> Dict[str, Any]:
           """Process intents with automatic error recovery."""

           for attempt in range(max_retries):
               try:
                   result = self.renderer.render_with_intents(payload, intents)

                   # Check for warnings that might indicate issues
                   warnings = self._analyze_warnings(result.warnings)

                   return {
                       "success": True,
                       "svg_content": result.svg_content,
                       "warnings": warnings,
                       "metrics": result.metrics.model_dump(),
                       "attempt": attempt + 1
                   }

               except IntentValidationError as e:
                   self.logger.warning(f"Intent validation error on attempt {attempt + 1}: {e}")
                   intents = self._fix_validation_issues(intents, e)

               except UnsupportedIntentError as e:
                   self.logger.warning(f"Unsupported feature on attempt {attempt + 1}: {e.feature}")
                   intents = self._apply_feature_fallbacks(intents, e.feature, e.alternatives)

               except IntentDegradationError as e:
                   self.logger.error(f"Degradation failed on attempt {attempt + 1}: {e}")
                   intents = self._use_safe_fallback(attempt)

               except SegnoMMSError as e:
                   self.logger.error(f"SegnoMMS error on attempt {attempt + 1}: {e.code}")
                   if attempt == max_retries - 1:
                       # Last attempt - return error response
                       return {
                           "success": False,
                           "error": e.to_dict(),
                           "fallback_used": True,
                           "svg_content": self._generate_error_qr(payload)
                       }
                   intents = self._use_safe_fallback(attempt)

           # All retries exhausted
           return {
               "success": False,
               "error": "MAX_RETRIES_EXCEEDED",
               "attempts": max_retries,
               "fallback_used": True,
               "svg_content": self._generate_minimal_qr(payload)
           }

       def _analyze_warnings(self, warnings: List[WarningInfo]) -> List[Dict[str, Any]]:
           """Analyze warnings for production monitoring."""
           analyzed = []
           for warning in warnings:
               analyzed.append({
                   "code": warning.code,
                   "severity": self._classify_warning_severity(warning),
                   "detail": warning.detail,
                   "actionable": warning.context.get("suggestion") is not None,
                   "feature_impact": warning.context.get("feature_impact", "unknown")
               })
           return analyzed

       def _fix_validation_issues(
           self,
           intents: IntentsConfig,
           error: IntentValidationError
       ) -> IntentsConfig:
           """Automatically fix common validation issues."""
           # Clone intents for modification
           fixed_intents = intents.model_copy(deep=True)

           # Common fixes based on error path
           if "corner_radius" in error.intent_path:
               # Clamp corner radius to valid range
               setattr(fixed_intents, error.intent_path.split(".")[0], 0.3)
           elif "contrast" in error.intent_path:
               # Use high contrast colors
               if hasattr(fixed_intents, 'style'):
                   fixed_intents.style.palette = {"fg": "#000000", "bg": "#FFFFFF"}

           return fixed_intents

       def _apply_feature_fallbacks(
           self,
           intents: IntentsConfig,
           unsupported_feature: str,
           alternatives: List[str]
       ) -> IntentsConfig:
           """Apply automatic feature fallbacks."""
           fallback_intents = intents.model_copy(deep=True)

           # Apply first available alternative
           if alternatives:
               # Logic to apply alternatives based on feature type
               if "shape" in unsupported_feature:
                   fallback_intents.style.module_shape = alternatives[0]
               elif "frame" in unsupported_feature:
                   fallback_intents.frame.shape = alternatives[0]

           return fallback_intents

       def _use_safe_fallback(self, attempt: int) -> IntentsConfig:
           """Use progressively simpler fallback configurations."""
           if attempt < len(self.fallback_configs):
               return self.fallback_configs[attempt]
           else:
               # Ultimate fallback - minimal configuration
               return IntentsConfig()

       def _generate_error_qr(self, payload: str) -> str:
           """Generate a basic QR code when all else fails."""
           try:
               return self.renderer.render_with_intents(
                   payload,
                   IntentsConfig()  # Minimal config
               ).svg_content
           except Exception:
               return self._generate_minimal_qr(payload)

       def _generate_minimal_qr(self, payload: str) -> str:
           """Generate the most basic QR code possible."""
           import segno
           qr = segno.make(payload)
           return qr.svg_inline()

Error Codes for API Integration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use error codes for programmatic handling:

.. code-block:: python

   from segnomms.intents import render_with_intents

   try:
       result = render_with_intents(payload, intents)
   except SegnoMMSError as e:
       if e.code == "CONTRAST_RATIO_ERROR":
           # Adjust colors automatically
           payload.dark = "#000000"
           payload.light = "#FFFFFF"
           result = render_with_intents(payload, intents)
       elif e.code == "UNSUPPORTED_INTENT":
           # Remove unsupported features
           simplified_intents = simplify_intents(intents)
           result = render_with_intents(payload, simplified_intents)
       else:
           # Re-raise unknown errors
           raise

API Integration Examples
~~~~~~~~~~~~~~~~~~~~~~~~

FastAPI Integration with Intent-Specific Error Handling
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from fastapi import FastAPI, HTTPException
   from fastapi.responses import JSONResponse
   from pydantic import BaseModel
   from typing import Dict, Any, Optional
   from segnomms.intents import render_with_intents

   app = FastAPI()

   class QRGenerationRequest(BaseModel):
       payload: str
       intents: Dict[str, Any]

   class QRGenerationResponse(BaseModel):
       success: bool
       svg_content: Optional[str] = None
       warnings: Optional[List[Dict[str, Any]]] = None
       error: Optional[Dict[str, Any]] = None
       metrics: Optional[Dict[str, Any]] = None
       degradation_used: bool = False

   @app.post("/api/qr/generate", response_model=QRGenerationResponse)
   async def generate_qr(request: QRGenerationRequest):
       """Generate QR code with comprehensive error handling."""
       try:
           intents_config = IntentsConfig.model_validate(request.intents)
           result = render_with_intents(request.payload, intents_config)

           # Success response with warnings
           return QRGenerationResponse(
               success=True,
               svg_content=result.svg_content,
               warnings=[warning.model_dump() for warning in result.warnings],
               metrics=result.metrics.model_dump(),
               degradation_used=len(result.warnings) > 0
           )

       except IntentValidationError as e:
           return JSONResponse(
               status_code=400,
               content=QRGenerationResponse(
                   success=False,
                   error={
                       "type": "intent_validation_error",
                       "code": e.code,
                       "message": e.message,
                       "intent_path": e.intent_path,
                       "invalid_value": e.original_value,
                       "suggestion": e.suggestion
                   }
               ).model_dump()
           )

       except UnsupportedIntentError as e:
           # Try with fallback configuration
           try:
               fallback_intents = create_fallback_from_alternatives(
                   intents_config, e.feature, e.alternatives
               )
               result = render_with_intents(request.payload, fallback_intents)

               return QRGenerationResponse(
                   success=True,
                   svg_content=result.svg_content,
                   warnings=[{
                       "code": "FEATURE_FALLBACK_APPLIED",
                       "message": f"Feature '{e.feature}' not supported, used '{e.alternatives[0]}'",
                       "original_feature": e.feature,
                       "fallback_used": e.alternatives[0]
                   }],
                   degradation_used=True
               )

           except Exception:
               return JSONResponse(
                   status_code=422,
                   content=QRGenerationResponse(
                       success=False,
                       error={
                           "type": "unsupported_intent_error",
                           "code": e.code,
                           "message": e.message,
                           "unsupported_feature": e.feature,
                           "alternatives": e.alternatives,
                           "planned_version": e.planned_version
                       }
                   ).model_dump()
               )

       except ContrastRatioError as e:
           return JSONResponse(
               status_code=400,
               content=QRGenerationResponse(
                   success=False,
                   error={
                       "type": "contrast_ratio_error",
                       "code": e.code,
                       "message": e.message,
                       "actual_ratio": e.ratio,
                       "required_ratio": e.required_ratio,
                       "accessibility_standard": e.standard,
                       "suggestion": "Use higher contrast colors or adjust the color palette"
                   }
               ).model_dump()
           )

       except SegnoMMSError as e:
           return JSONResponse(
               status_code=500,
               content=QRGenerationResponse(
                   success=False,
                   error=e.to_dict()
               ).model_dump()
           )

Flask Integration with Error Monitoring
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from flask import Flask, request, jsonify
   import logging
   from datetime import datetime

   app = Flask(__name__)

   # Configure error monitoring
   error_logger = logging.getLogger('segnomms.errors')
   handler = logging.StreamHandler()
   handler.setFormatter(logging.Formatter(
       '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
   ))
   error_logger.addHandler(handler)
   error_logger.setLevel(logging.WARNING)

   class ErrorMetrics:
       """Track error metrics for monitoring."""
       def __init__(self):
           self.error_counts = {}
           self.degradation_counts = {}

       def record_error(self, error_type: str, error_code: str):
           key = f"{error_type}:{error_code}"
           self.error_counts[key] = self.error_counts.get(key, 0) + 1

       def record_degradation(self, feature: str, fallback: str):
           key = f"{feature}->{fallback}"
           self.degradation_counts[key] = self.degradation_counts.get(key, 0) + 1

   from segnomms.intents import render_with_intents
   metrics = ErrorMetrics()

   @app.route('/api/qr/generate', methods=['POST'])
   def generate_qr():
       """Generate QR with comprehensive error tracking."""
       start_time = datetime.utcnow()
       data = request.get_json()

       try:
           payload = data.get('payload', '')
           intents_data = data.get('intents', {})

           intents = IntentsConfig.model_validate(intents_data)
           result = render_with_intents(payload, intents)

           # Track successful degradations for monitoring
           for warning in result.warnings:
               if warning.code == "FEATURE_DEGRADED":
                   feature = warning.context.get('original_feature', 'unknown')
                   fallback = warning.context.get('fallback_feature', 'unknown')
                   metrics.record_degradation(feature, fallback)

           processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000

           return jsonify({
               "success": True,
               "svg": result.svg_content,
               "warnings": [w.model_dump() for w in result.warnings],
               "metrics": {
                   **result.metrics.model_dump(),
                   "processing_time_ms": processing_time
               },
               "degradation_applied": len(result.warnings) > 0
           })

       except IntentValidationError as e:
           metrics.record_error("IntentValidationError", e.code)
           error_logger.warning(f"Intent validation error: {e.intent_path} = {e.original_value}")

           return jsonify({
               "success": False,
               "error": {
                   "type": "validation_error",
                   "code": e.code,
                   "message": e.message,
                   "field": e.intent_path,
                   "invalid_value": e.original_value,
                   "suggestion": e.suggestion
               }
           }), 400

       except UnsupportedIntentError as e:
           metrics.record_error("UnsupportedIntentError", e.code)
           error_logger.info(f"Unsupported feature requested: {e.feature}")

           return jsonify({
               "success": False,
               "error": {
                   "type": "unsupported_feature",
                   "code": e.code,
                   "message": e.message,
                   "feature": e.feature,
                   "alternatives": e.alternatives,
                   "will_be_supported": e.planned_version
               }
           }), 422

       except Exception as e:
           metrics.record_error("UnexpectedError", type(e).__name__)
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
           "error_counts": metrics.error_counts,
           "degradation_counts": metrics.degradation_counts,
           "total_errors": sum(metrics.error_counts.values()),
           "total_degradations": sum(metrics.degradation_counts.values())
       })

Converting to API Responses
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use the ``to_dict()`` method for API responses:

.. code-block:: python

   from flask import jsonify
   from segnomms.intents import render_with_intents

   try:
       result = render_with_intents(payload, intents)
       return jsonify({"success": True, "svg": result.svg_content})
   except SegnoMMSError as e:
       return jsonify({
           "success": False,
           "error": e.to_dict()
       }), 400

Custom Error Handling
~~~~~~~~~~~~~~~~~~~~~

Create custom handlers for different error types:

.. code-block:: python

   def handle_segnomms_error(error: SegnoMMSError) -> dict:
       """Convert SegnoMMS errors to consistent API responses."""
       response = {
           "success": False,
           "error_code": error.code,
           "message": error.message,
           "details": error.details
       }

       if error.suggestion:
           response["suggestion"] = error.suggestion

       # Add specific handling for different error types
       if isinstance(error, UnsupportedIntentError):
           response["alternatives"] = error.alternatives
           response["planned_version"] = error.planned_version
       elif isinstance(error, ContrastRatioError):
           response["contrast_info"] = {
               "actual_ratio": error.ratio,
               "required_ratio": error.required_ratio,
               "standard": error.standard
           }

       return response
