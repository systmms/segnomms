Deprecated Options Migration Guide
==================================

This guide helps you migrate from deprecated configuration option names to their
current equivalents. All deprecated options continue to work but emit
``DeprecationWarning`` messages to help you update your code.

Centerpiece Options (formerly "reserve")
----------------------------------------

The ``reserve_*`` options have been renamed to ``centerpiece_*`` for clarity.
The new names better describe the feature's purpose: reserving space for a logo
or centerpiece in the QR code center.

.. list-table::
   :header-rows: 1
   :widths: 35 35 30

   * - Deprecated Option
     - Current Option
     - Description
   * - ``reserve_center``
     - ``centerpiece_enabled``
     - Enable centerpiece reservation
   * - ``reserve_shape``
     - ``centerpiece_shape``
     - Shape of the reserved area
   * - ``reserve_size``
     - ``centerpiece_size``
     - Size as fraction of QR code
   * - ``reserve_offset_x``
     - ``centerpiece_offset_x``
     - Horizontal offset from center
   * - ``reserve_offset_y``
     - ``centerpiece_offset_y``
     - Vertical offset from center
   * - ``reserve_margin``
     - ``centerpiece_margin``
     - Margin around centerpiece

Migration Example
~~~~~~~~~~~~~~~~~

**Before (deprecated):**

.. code-block:: python

   from segnomms import write

   write(
       qr,
       output,
       reserve_center=True,
       reserve_size=0.15,
       reserve_shape="circle",
       reserve_margin=2,
   )

**After (current):**

.. code-block:: python

   from segnomms import write

   write(
       qr,
       output,
       centerpiece_enabled=True,
       centerpiece_size=0.15,
       centerpiece_shape="circle",
       centerpiece_margin=2,
   )

QR Advanced Options
-------------------

The ``qr_*`` prefixed options have been renamed to use more intuitive names
that align with Segno's terminology.

.. list-table::
   :header-rows: 1
   :widths: 35 35 30

   * - Deprecated Option
     - Current Option
     - Description
   * - ``qr_eci``
     - ``eci_enabled``
     - Enable Extended Channel Interpretation
   * - ``qr_encoding``
     - ``encoding``
     - Character encoding
   * - ``qr_mask``
     - ``mask_pattern``
     - QR code mask pattern (0-7)
   * - ``qr_symbol_count``
     - ``symbol_count``
     - Number of symbols in sequence
   * - ``qr_boost_error``
     - ``boost_error``
     - Boost error correction if possible
   * - ``multi_symbol``
     - ``structured_append``
     - Enable structured append mode

Migration Example
~~~~~~~~~~~~~~~~~

**Before (deprecated):**

.. code-block:: python

   from segnomms.config import RenderingConfig

   config = RenderingConfig.from_kwargs(
       qr_boost_error=True,
       qr_mask=3,
       qr_eci=True,
   )

**After (current):**

.. code-block:: python

   from segnomms.config import RenderingConfig

   config = RenderingConfig.from_kwargs(
       boost_error=True,
       mask_pattern=3,
       eci_enabled=True,
   )

Conflict Handling
-----------------

If you accidentally use both the deprecated and current option names in the same
call, SegnoMMS handles this gracefully:

**Same values**: Only emits a deprecation warning (no error)

.. code-block:: python

   # This works but emits a warning
   config = RenderingConfig.from_kwargs(
       reserve_size=0.15,
       centerpiece_size=0.15,  # Same value - just warns
   )

**Different values**: Raises ``ValueError``

.. code-block:: python

   # This raises ValueError due to conflict
   config = RenderingConfig.from_kwargs(
       reserve_size=0.15,
       centerpiece_size=0.20,  # Different value - error!
   )
   # ValueError: Conflicting values for 'reserve_size' and 'centerpiece_size':
   #             received 0.15 and 0.20.

Deprecation Policy
------------------

SegnoMMS follows semantic versioning with the following deprecation policy:

**Pre-1.0.0 (current)**:
  Deprecated options may be removed in any minor version bump (e.g., 0.5.0 to 0.6.0).
  We recommend migrating promptly when deprecation warnings appear.

**Post-1.0.0 (future)**:
  Deprecated options will be retained for at least one major version cycle.
  For example, options deprecated in 1.x will continue to work until 3.0.0.

Filtering Deprecation Warnings
------------------------------

If you need to suppress deprecation warnings temporarily (not recommended for
production code), you can use Python's warnings module:

.. code-block:: python

   import warnings
   from segnomms.config import RenderingConfig

   # Suppress only SegnoMMS deprecation warnings
   with warnings.catch_warnings():
       warnings.filterwarnings(
           "ignore",
           category=DeprecationWarning,
           module=r"segnomms\..*"
       )
       config = RenderingConfig.from_kwargs(reserve_center=True)

Phase4Validator Rename
----------------------

The ``Phase4Validator`` class has been renamed to ``CompositionValidator`` to
better reflect its purpose as a validation system for visual composition, rather
than a processing phase.

**Before (deprecated):**

.. code-block:: python

   from segnomms.validation import Phase4Validator

   validator = Phase4Validator(config)
   result = validator.validate_all()

**After (current):**

.. code-block:: python

   from segnomms.validation import CompositionValidator

   validator = CompositionValidator(config)
   result = validator.validate_all()

The old import continues to work but emits a ``DeprecationWarning``.

phase4 Module Rename
--------------------

The ``segnomms.validation.phase4`` module has been renamed to
``segnomms.validation.composition``. This module-level rename reflects the
transition from internal development phase naming to descriptive functionality.

**Before (deprecated):**

.. code-block:: python

   from segnomms.validation.phase4 import Phase4Validator

   validator = Phase4Validator(
       qr_version=5, error_level='M', matrix_size=37
   )

**After (current):**

.. code-block:: python

   from segnomms.validation.composition import CompositionValidator

   # Or use the package-level import (recommended):
   from segnomms.validation import CompositionValidator

   validator = CompositionValidator(
       qr_version=5, error_level='M', matrix_size=37
   )

Importing from the old module path emits a ``DeprecationWarning`` at import time.

Phase4ValidatorConfig Rename
----------------------------

The configuration class ``Phase4ValidatorConfig`` has been renamed to
``CompositionValidatorConfig`` for consistency with the validator class.

**Before (deprecated):**

.. code-block:: python

   from segnomms.validation.models import Phase4ValidatorConfig

   config = Phase4ValidatorConfig(
       qr_version=5,
       error_level='M',
       matrix_size=37
   )

**After (current):**

.. code-block:: python

   from segnomms.validation.models import CompositionValidatorConfig

   config = CompositionValidatorConfig(
       qr_version=5,
       error_level='M',
       matrix_size=37
   )

The old class name continues to work but emits a ``DeprecationWarning``.
