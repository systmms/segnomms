QR Decoder Compatibility Reference
====================================

This document provides comprehensive information about QR code decoder compatibility
with SegnoMMS stylized QR codes, including known limitations and recommendations
for different use cases.

Overview
--------

SegnoMMS generates visually stylized QR codes that prioritize aesthetic appeal while
maintaining functional scanability. However, some combinations of visual styling and
decoder implementations may result in reduced compatibility compared to standard
square-module QR codes.

This reference documents tested decoder compatibility across different configurations
to help developers make informed decisions about styling choices for their specific
use cases.

Decoder Library Compatibility Matrix
------------------------------------

The following decoders have been tested with SegnoMMS output:

**Recommended Decoders (High Compatibility):**
- **zxingcpp** - ZXing C++ implementation with Python bindings
- **OpenCV QRCodeDetector** - Part of opencv-python package
- **pyzbar** - Python wrapper for ZBar library (requires system dependencies)

**Mobile and Web Decoders:**
- Most smartphone camera apps use ZXing or similar algorithms
- Web-based QR scanners vary widely in capability

Installation
~~~~~~~~~~~~

.. code-block:: bash

    # Recommended: ZXing C++ (no system dependencies)
    pip install zxingcpp

    # Alternative: OpenCV
    pip install opencv-python

    # Alternative: PyZBar (requires libzbar)
    # On macOS: brew install zbar
    # On Ubuntu: sudo apt-get install libzbar0
    pip install pyzbar

Known Compatibility Issues
--------------------------

Based on systematic testing, the following configurations have known decoder
compatibility limitations:

Shape-Related Issues
~~~~~~~~~~~~~~~~~~~

**Circle Modules (safe_mode=False)**
- **Issue**: Circle modules without safe mode may not be recognized by some decoders
- **Affected Decoders**: zxingcpp, opencv
- **Recommendation**: Use ``safe_mode=True`` for circle shapes in critical applications
- **Alternative**: Use ``squircle`` shape for rounded appearance with better compatibility

**Diamond Modules (safe_mode=False)**
- **Issue**: Diamond-shaped modules can confuse edge detection algorithms
- **Affected Decoders**: zxingcpp, opencv
- **Recommendation**: Use ``safe_mode=True`` or consider ``rounded`` shape instead
- **Note**: Diamond with safe_mode=True works reliably

Scale-Related Issues
~~~~~~~~~~~~~~~~~~~

**Rounded Modules at Various Scales**
- **Issue**: Rounded modules may lose definition at certain scales during SVG→bitmap conversion
- **Affected Scales**: All tested scales (5, 10, 20 pixels/module) with rounded shape
- **Affected Decoders**: zxingcpp, opencv
- **Root Cause**: SVG rendering precision during PNG conversion
- **Recommendation**: Test specific scale + decoder combinations for critical applications

Error Correction Level Issues
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Low Error Correction (Level L)**
- **Issue**: Connected shapes with ECC Level L may have insufficient error correction
- **Affected Configuration**: ``error="L"`` with ``shape="connected"``
- **Affected Decoders**: zxingcpp, opencv
- **Recommendation**: Use ECC Level M or higher for connected/merged shapes
- **Explanation**: Visual styling reduces available error correction capacity

Compatibility Recommendations
----------------------------

High Compatibility Configurations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For maximum decoder compatibility, use these "safe" configurations:

.. code-block:: python

    # Safest configuration - works with all tested decoders
    safe_config = {
        'shape': 'square',
        'scale': 10,
        'dark': '#000000',
        'light': '#FFFFFF',
        'error': 'M'  # Medium error correction
    }

    # Safe rounded appearance
    safe_rounded = {
        'shape': 'squircle',
        'safe_mode': True,
        'scale': 10,
        'error': 'M'
    }

    # Safe connected modules
    safe_connected = {
        'shape': 'connected',
        'safe_mode': True,
        'error': 'Q',  # Higher ECC for merging
        'scale': 12
    }

Balanced Styling Configurations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

These configurations provide good visual appeal with reasonable compatibility:

.. code-block:: python

    # Stylized but compatible
    balanced_config = {
        'shape': 'rounded',
        'safe_mode': True,
        'scale': 15,  # Larger scale for better definition
        'error': 'M',
        'dark': '#1a1a2e',
        'light': '#f5f5f5'
    }

    # Connected modules with safety
    balanced_connected = {
        'shape': 'connected',
        'connectivity': '8-way',
        'merge': 'soft',
        'safe_mode': True,
        'error': 'H',  # Highest ECC for complex styling
        'scale': 12
    }

Testing and Validation
----------------------

Decoder Testing Methodology
~~~~~~~~~~~~~~~~~~~~~~~~~~~

When deploying SegnoMMS QR codes, follow this testing approach:

1. **Generate test codes** with your exact configuration
2. **Convert to PNG** using the same process as production
3. **Test with multiple decoders** (zxingcpp, opencv, mobile apps)
4. **Verify across different scales** and viewing conditions
5. **Document compatibility** for your specific use case

Example Testing Code
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    import segno
    from segnomms import write
    import io

    def test_decoder_compatibility(config, test_data="Test Message"):
        """Test decoder compatibility for a configuration."""
        qr = segno.make(test_data, error=config.get('error', 'M'))

        # Generate SVG
        output = io.StringIO()
        write(qr, output, **config)
        svg_content = output.getvalue()

        # Convert to PNG and test with available decoders
        # (Implementation depends on your conversion setup)

        return test_results

Performance Considerations
-------------------------

SVG to Bitmap Conversion
~~~~~~~~~~~~~~~~~~~~~~~~

The quality of SVG→PNG/JPEG conversion significantly affects decoder compatibility:

**Rendering Settings Impact:**
- **DPI**: Higher DPI (≥150) improves fine detail preservation
- **Antialiasing**: May blur edges; consider disabling for small QR codes
- **Scale**: Larger output dimensions generally improve compatibility
- **Format**: PNG preserves sharp edges better than JPEG

**Recommended Conversion Settings:**

.. code-block:: python

    conversion_settings = {
        'dpi': 200,
        'width': 400,   # Minimum 400px for reliable decoding
        'height': 400,
        'background': 'white',
        'format': 'PNG'
    }

Mobile Camera Considerations
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Mobile QR code scanning has additional constraints:

- **Minimum size**: QR codes should be at least 2cm (0.8") for reliable mobile scanning
- **Contrast**: Maintain high contrast ratios (≥7:1) for accessibility
- **Lighting**: Test under various lighting conditions
- **Distance**: QR codes are typically scanned from 10-50cm distance

Troubleshooting Decoder Issues
------------------------------

Common Problems and Solutions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**"QR code not detected"**
- Increase scale parameter (try 12-20)
- Enable safe_mode if using non-square shapes
- Increase error correction level
- Check contrast ratio between dark/light colors

**"Detected but can't decode content"**
- Increase error correction level (try 'H')
- Reduce visual complexity (disable merging, use simpler shapes)
- Test with different decoders

**"Works on some devices but not others"**
- Test with multiple decoder implementations
- Consider using "high compatibility" configuration
- Document known limitations for users

**"Intermittent scanning failures"**
- Increase quiet zone (border parameter)
- Use larger scale for small QR codes
- Test SVG→bitmap conversion quality

Decoder-Specific Notes
~~~~~~~~~~~~~~~~~~~~~~

**ZXing C++**
- Generally most permissive with styling
- Good performance with connected modules
- May struggle with very small scales

**OpenCV QRCodeDetector**
- Sensitive to edge definition
- Works well with high-contrast configurations
- May have issues with complex merged shapes

**PyZBar**
- Requires system library installation
- Good compatibility with standard configurations
- May be sensitive to image preprocessing

Future Compatibility
--------------------

Decoder Algorithm Evolution
~~~~~~~~~~~~~~~~~~~~~~~~~~

QR decoder algorithms continue to evolve, potentially improving compatibility
with stylized codes:

- **Machine learning approaches** may better handle non-standard shapes
- **Improved edge detection** could handle merged modules more reliably
- **Multi-scale analysis** might improve small QR code recognition

However, compatibility with older devices and legacy decoders remains important
for broad accessibility.

SegnoMMS Development
~~~~~~~~~~~~~~~~~~~

Future SegnoMMS versions may include:

- **Compatibility scoring** during configuration validation
- **Decoder-specific optimization** modes
- **Automatic safe mode recommendations**
- **Enhanced SVG rendering** for better bitmap conversion

Recommendations for Library Users
---------------------------------

Production Deployment Checklist
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Before deploying stylized QR codes in production:

1. **Test with target decoders** (mobile apps, web scanners, etc.)
2. **Validate across different devices** and operating systems
3. **Document known limitations** for end users
4. **Provide fallback options** (URL shorteners, manual entry)
5. **Monitor scanning success rates** if possible

Configuration Selection Guidelines
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Critical Applications** (payment, authentication)
- Use high compatibility configurations
- Test extensively with target decoders
- Consider multiple QR code sizes/formats

**Marketing Materials** (posters, business cards)
- Balanced styling acceptable
- Include fallback information
- Test under expected viewing conditions

**Decorative Applications** (art, design elements)
- Full styling freedom
- Clearly communicate any scanning limitations
- Consider QR codes as supplementary, not primary interface

Documentation and Support
-------------------------

When documenting QR codes for end users:

**Include Scanning Instructions:**
- Recommended scanning apps if compatibility is limited
- Optimal scanning distance and lighting
- Alternative access methods (typed URLs, etc.)

**Set Appropriate Expectations:**
- Acknowledge that stylized QR codes may require specific scanners
- Provide clear fallback options
- Consider user accessibility needs

Conclusion
----------

SegnoMMS enables creation of visually appealing QR codes while maintaining good
decoder compatibility for most configurations. Understanding the documented limitations
allows developers to make informed decisions about styling trade-offs.

For maximum compatibility, use the recommended "safe" configurations. For applications
requiring specific styling, thorough testing with target decoders is essential.

The QR code ecosystem continues to evolve, and future decoder improvements may resolve
some current limitations. Until then, this compatibility reference provides guidance
for reliable deployment of stylized QR codes.

Related Documentation
--------------------

- :doc:`api/index` - Complete API reference
- :doc:`shapes` - Shape options and visual styling examples
- :doc:`quickstart` - Getting started guide
- :doc:`examples` - Usage examples and patterns

.. note::
    This compatibility reference is based on testing with specific decoder versions.
    Results may vary with different implementations or versions. Always test with
    your specific deployment environment.
