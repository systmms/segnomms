Validation
==========

This module provides validation for QR code composition features to ensure scannability and safety.

Composition Validator
---------------------

.. automodule:: segnomms.validation.composition
   :members:
   :undoc-members:
   :show-inheritance:

The ``CompositionValidator`` class validates frame shapes and centerpiece configurations
to prevent settings that might make QR codes unscannable.

.. note::

   The ``CompositionValidator`` class was previously named ``Phase4Validator``.
   The old name is retained as a deprecated alias for backward compatibility.

Validation Classes
------------------

.. autoclass:: segnomms.validation.composition.CompositionValidator
   :members:
   :undoc-members:
   :show-inheritance:

Validation checks include:

* **Frame Safety**: Ensures adequate borders for non-square frames
* **Centerpiece Size**: Validates logo area size against error correction capacity
* **Configuration Conflicts**: Detects incompatible feature combinations
* **QR Code Limits**: Prevents configurations that exceed QR code capabilities

Error Correction Guidelines
---------------------------

The validator enforces safe centerpiece size limits based on error correction levels:

.. list-table:: Centerpiece Size Limits
   :header-rows: 1
   :widths: 20 20 60

   * - Error Level
     - Recovery
     - Max Centerpiece Size
   * - L (Low)
     - ~7%
     - 5% - Very conservative
   * - M (Medium)
     - ~15%
     - 8% - Good for small logos
   * - Q (Quartile)
     - ~25%
     - 15% - Medium logos
   * - H (High)
     - ~30%
     - 20% - Large logos

Frame Validation
----------------

Frame shape validation includes:

* **Border Requirements**: Minimum quiet zone sizes for different frame shapes
* **Clipping Safety**: Ensures critical patterns aren't clipped by frame shapes
* **Custom Path Validation**: Basic validation of custom SVG paths

Examples
--------

Manual Validation::

    from segnomms.validation import CompositionValidator
    from segnomms.config import RenderingConfig
    import segno

    # Create QR code and config
    qr = segno.make("Test data", error='m')
    config = RenderingConfig.from_kwargs(
        frame_shape='circle',
        border=3,  # May be too small
        centerpiece_enabled=True,
        centerpiece_size=0.2  # May be too large for M level
    )

    # Validate configuration
    validator = CompositionValidator(
        qr_version=qr.version, error_level='M', matrix_size=qr.symbol_size()[0]
    )
    result = validator.validate_all(config)

    for warning in result.warnings:
        print(f"Warning: {warning}")

Automatic Validation::

    # Validation happens automatically during rendering
    from segnomms import write

    qr = segno.make("Test", error='l')

    # This will log warnings for unsafe configuration
    with open('output.svg', 'w') as f:
        write(qr, f,
              frame_shape='circle',
              centerpiece_enabled=True,
              centerpiece_size=0.15,  # Too large for L level
              border=2)  # Too small for circle frame

Validation Results
------------------

Validation methods return lists of warning strings:

* **Empty list**: Configuration is safe
* **Warning messages**: Potential issues that may affect scannability
* **Recommendations**: Suggested parameter adjustments

Common Warnings
---------------

**Frame Shape Warnings:**

* "Circle/custom frames should use 5+ module quiet zone"
* "Frame shape may clip important QR patterns"

**Centerpiece Warnings:**

* "Centerpiece size exceeds safe limit for error level"
* "Large centerpiece with aggressive merging may cause issues"

**Configuration Conflicts:**

* "Custom frame path appears invalid"
* "Centerpiece offset places logo outside QR bounds"

Best Practices
--------------

To avoid validation warnings:

1. **Use adequate borders**: 5-6 modules for circle/custom frames
2. **Match error correction to centerpiece size**: Use H level for large logos
3. **Test scannability**: Always test with target scanning devices
4. **Conservative sizing**: Start with smaller centerpieces and increase if needed
