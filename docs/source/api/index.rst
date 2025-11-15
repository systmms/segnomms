API Reference
=============

This section contains the complete API reference for SegnoMMS.

.. toctree::
   :maxdepth: 2

   main
   config
   constants
   intents
   shapes
   animation
   svg
   color
   accessibility
   core
   frames
   validation
   exceptions
   degradation

Main Module
-----------

The top-level package re-exports key classes and functions for convenience
(`segnomms.write`, configuration models, exceptions, and factories). See the
section pages in this API reference for authoritative docs on each area.

Quick Reference
---------------

Basic Usage
~~~~~~~~~~~

The main entry point is the :func:`~segnomms.write` function:

.. code-block:: python

   from segnomms import write

   write(qr, output, shape='connected', scale=10)

Intent-Based API with Error Handling
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For advanced features with graceful degradation:

.. code-block:: python

   from segnomms.intents import render_with_intents
   from segnomms.intents.models import PayloadConfig, IntentsConfig, StyleIntents
   from segnomms.exceptions import IntentValidationError, UnsupportedIntentError

   try:
       intents = IntentsConfig(
           style=StyleIntents(
               module_shape="squircle",
               patterns={"finder": "rounded"}
           )
       )
       payload = PayloadConfig(text="Hello World")
       result = render_with_intents(payload, intents)

       # Check for degradation warnings
       if result.has_warnings:
           for warning in result.warnings:
               if warning.code == "FEATURE_DEGRADED":
                   print(f"Feature degraded: {warning.detail}")

   except IntentValidationError as e:
       print(f"Invalid intent at {e.intent_path}: {e.original_value}")
   except UnsupportedIntentError as e:
       print(f"Feature '{e.feature}' not supported, alternatives: {e.alternatives}")

Production Error Recovery
~~~~~~~~~~~~~~~~~~~~~~~~~

Robust error handling for production systems:

.. code-block:: python

   def generate_qr_with_fallback(payload, intents, max_retries=3):
       """Generate QR with comprehensive error recovery."""
       for attempt in range(max_retries):
           try:
               result = render_with_intents(payload, intents)
               return {"success": True, "svg": result.svg_content, "warnings": result.warnings}

           except IntentValidationError as e:
               # Fix validation issues and retry
               intents = fix_validation_issues(intents, e)

           except UnsupportedIntentError as e:
               # Apply feature fallbacks
               intents = apply_feature_fallbacks(intents, e.feature, e.alternatives)

           except Exception as e:
               if attempt == max_retries - 1:
                   # Last attempt - return minimal QR
                   return {"success": False, "error": str(e), "svg": generate_minimal_qr(payload)}

       return {"success": False, "error": "Max retries exceeded"}
