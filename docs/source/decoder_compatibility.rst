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

Error Correction Level Reference
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

QR codes use Reed-Solomon error correction to recover from damage or scanning issues.
Higher error correction levels allow more data recovery but reduce available data capacity:

.. list-table:: Error Correction Levels
   :header-rows: 1
   :widths: 20 30 50

   * - Level
     - Recovery Capacity
     - Recommended Use
   * - **L** (Low)
     - ~7% damage recovery
     - Clean environments, maximum data capacity needed
   * - **M** (Medium)
     - ~15% damage recovery
     - Standard usage, good balance (default)
   * - **Q** (Quartile)
     - ~25% damage recovery
     - Stylized QR codes, moderate visual effects
   * - **H** (High)
     - ~30% damage recovery
     - Heavy styling, logos, outdoor use, critical applications

**For stylized QR codes**, use at least Level M. For connected shapes, merged modules,
or centerpiece overlays, Level Q or H is strongly recommended to compensate for the
visual modifications that may affect scanning.

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
~~~~~~~~~~~~~~~~~~~~

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
~~~~~~~~~~~~~~~~~~~~

**Rounded Modules at Various Scales**
- **Issue**: Rounded modules may lose definition at certain scales during SVG→bitmap conversion
- **Affected Scales**: All tested scales (5, 10, 20 pixels/module) with rounded shape
- **Affected Decoders**: zxingcpp, opencv
- **Root Cause**: SVG rendering precision during PNG conversion
- **Recommendation**: Test specific scale + decoder combinations for critical applications

Error Correction Level Issues
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Low Error Correction (Level L)**
- **Issue**: Connected shapes with ECC Level L may have insufficient error correction
- **Affected Configuration**: ``error="L"`` with ``shape="connected"``
- **Affected Decoders**: zxingcpp, opencv
- **Recommendation**: Use ECC Level M or higher for connected/merged shapes
- **Explanation**: Visual styling reduces available error correction capacity

Compatibility Recommendations
-----------------------------

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
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    import segno
    from segnomms import write
    import io
    from pathlib import Path
    from typing import Dict, List, Optional

    def test_decoder_compatibility(
        config: Dict,
        test_data: str = "Test Message",
        output_dir: Optional[Path] = None
    ) -> Dict[str, any]:
        """
        Test decoder compatibility for a configuration.

        Args:
            config: Dictionary of configuration options for write()
            test_data: Data to encode in the QR code
            output_dir: Optional directory for saving test files

        Returns:
            Dictionary with test results from all available decoders
        """
        import tempfile
        import shutil

        # Create QR code with specified error level
        qr = segno.make(test_data, error=config.get('error', 'M'))

        # Generate SVG
        output = io.StringIO()
        write(qr, output, **config)
        svg_content = output.getvalue()

        # Prepare output directory
        if output_dir is None:
            output_dir = Path(tempfile.mkdtemp(prefix='qr_test_'))
        else:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)

        # Save SVG
        svg_path = output_dir / "test.svg"
        with open(svg_path, 'w') as f:
            f.write(svg_content)

        # Convert SVG to PNG for testing
        # Using cairosvg for reliable conversion
        try:
            import cairosvg
            png_path = output_dir / "test.png"
            cairosvg.svg2png(
                bytestring=svg_content.encode('utf-8'),
                write_to=str(png_path),
                dpi=200,
                output_width=400,
                output_height=400
            )
        except ImportError:
            return {
                'error': 'cairosvg not installed',
                'suggestion': 'pip install cairosvg',
                'config': config
            }

        # Test with available decoders
        test_results = {
            'config': config,
            'test_data': test_data,
            'svg_path': str(svg_path),
            'png_path': str(png_path),
            'decoders': {}
        }

        # Test with zxingcpp
        try:
            import zxingcpp
            from PIL import Image

            img = Image.open(png_path)
            result = zxingcpp.read_barcode(img)

            test_results['decoders']['zxingcpp'] = {
                'available': True,
                'detected': result is not None,
                'decoded': result.text if result else None,
                'matches': result.text == test_data if result else False,
                'error': None
            }
        except ImportError:
            test_results['decoders']['zxingcpp'] = {
                'available': False,
                'error': 'zxingcpp not installed'
            }
        except Exception as e:
            test_results['decoders']['zxingcpp'] = {
                'available': True,
                'detected': False,
                'error': str(e)
            }

        # Test with OpenCV
        try:
            import cv2

            img = cv2.imread(str(png_path))
            detector = cv2.QRCodeDetector()
            data, bbox, _ = detector.detectAndDecode(img)

            test_results['decoders']['opencv'] = {
                'available': True,
                'detected': bbox is not None,
                'decoded': data if data else None,
                'matches': data == test_data if data else False,
                'error': None
            }
        except ImportError:
            test_results['decoders']['opencv'] = {
                'available': False,
                'error': 'opencv-python not installed'
            }
        except Exception as e:
            test_results['decoders']['opencv'] = {
                'available': True,
                'detected': False,
                'error': str(e)
            }

        # Test with pyzbar
        try:
            from pyzbar import pyzbar
            from PIL import Image

            img = Image.open(png_path)
            results = pyzbar.decode(img)

            if results:
                decoded_data = results[0].data.decode('utf-8')
                test_results['decoders']['pyzbar'] = {
                    'available': True,
                    'detected': True,
                    'decoded': decoded_data,
                    'matches': decoded_data == test_data,
                    'error': None
                }
            else:
                test_results['decoders']['pyzbar'] = {
                    'available': True,
                    'detected': False,
                    'decoded': None,
                    'matches': False,
                    'error': 'No QR code detected'
                }
        except ImportError:
            test_results['decoders']['pyzbar'] = {
                'available': False,
                'error': 'pyzbar not installed (requires system libzbar)'
            }
        except Exception as e:
            test_results['decoders']['pyzbar'] = {
                'available': True,
                'detected': False,
                'error': str(e)
            }

        # Calculate summary
        available_decoders = [name for name, result in test_results['decoders'].items()
                            if result.get('available', False)]
        successful_decoders = [name for name, result in test_results['decoders'].items()
                              if result.get('matches', False)]

        test_results['summary'] = {
            'total_decoders': len(available_decoders),
            'successful_decoders': len(successful_decoders),
            'success_rate': len(successful_decoders) / len(available_decoders)
                           if available_decoders else 0.0,
            'all_passed': len(successful_decoders) == len(available_decoders)
                         and len(available_decoders) > 0
        }

        return test_results


    def print_test_results(results: Dict) -> None:
        """Pretty print decoder test results."""
        print(f"\n{'='*60}")
        print("QR Decoder Compatibility Test Results")
        print(f"{'='*60}")
        print(f"Configuration: {results['config']}")
        print(f"Test Data: {results['test_data']}")
        print(f"\nDecoder Results:")
        print(f"{'-'*60}")

        for decoder_name, decoder_result in results['decoders'].items():
            if not decoder_result.get('available', False):
                print(f"  {decoder_name}: ❌ Not available - {decoder_result.get('error', 'Unknown')}")
            elif decoder_result.get('matches', False):
                print(f"  {decoder_name}: ✅ SUCCESS - Decoded correctly")
            elif decoder_result.get('detected', False):
                print(f"  {decoder_name}: ⚠️  MISMATCH - Decoded as '{decoder_result.get('decoded')}'")
            else:
                error = decoder_result.get('error', 'Detection failed')
                print(f"  {decoder_name}: ❌ FAILED - {error}")

        print(f"\n{'-'*60}")
        summary = results['summary']
        print(f"Summary: {summary['successful_decoders']}/{summary['total_decoders']} decoders succeeded")
        print(f"Success Rate: {summary['success_rate']*100:.1f}%")
        print(f"Overall: {'✅ PASS' if summary['all_passed'] else '❌ FAIL'}")
        print(f"{'='*60}\n")


    def batch_test_configurations(configs: List[Dict], test_data: str = "https://example.com") -> None:
        """Test multiple configurations and report results."""
        all_results = []

        for i, config in enumerate(configs, 1):
            print(f"\n[{i}/{len(configs)}] Testing configuration...")
            results = test_decoder_compatibility(config, test_data)
            print_test_results(results)
            all_results.append(results)

        # Print aggregate summary
        print(f"\n{'='*60}")
        print("AGGREGATE TEST RESULTS")
        print(f"{'='*60}")

        total_configs = len(all_results)
        passed_configs = sum(1 for r in all_results if r['summary']['all_passed'])

        print(f"Total Configurations Tested: {total_configs}")
        print(f"Fully Compatible: {passed_configs}")
        print(f"Partial Compatibility: {total_configs - passed_configs}")
        print(f"Overall Compatibility Rate: {passed_configs/total_configs*100:.1f}%")
        print(f"{'='*60}\n")


    # Example Usage
    if __name__ == "__main__":
        # Test individual configuration
        config = {
            'shape': 'circle',
            'safe_mode': True,
            'scale': 10,
            'error': 'M'
        }

        results = test_decoder_compatibility(config, "https://example.com")
        print_test_results(results)

        # Test multiple configurations
        test_configs = [
            {'shape': 'square', 'scale': 10, 'error': 'M'},
            {'shape': 'circle', 'safe_mode': True, 'scale': 10, 'error': 'M'},
            {'shape': 'rounded', 'safe_mode': True, 'scale': 15, 'error': 'M'},
            {'shape': 'connected', 'safe_mode': True, 'scale': 12, 'error': 'H'},
        ]

        batch_test_configurations(test_configs)

Performance Considerations
--------------------------

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
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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
~~~~~~~~~~~~~~~~~~~~~~~~~~~

QR decoder algorithms continue to evolve, potentially improving compatibility
with stylized codes:

- **Machine learning approaches** may better handle non-standard shapes
- **Improved edge detection** could handle merged modules more reliably
- **Multi-scale analysis** might improve small QR code recognition

However, compatibility with older devices and legacy decoders remains important
for broad accessibility.

SegnoMMS Development
~~~~~~~~~~~~~~~~~~~~

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
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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

Phase 4 Advanced Features Compatibility
----------------------------------------

Phase 4 features (frames, centerpieces, gradients) introduce additional compatibility
considerations beyond basic shape styling. These features can significantly impact
scannability and require careful testing.

Frame Shape Compatibility
~~~~~~~~~~~~~~~~~~~~~~~~~

Frame shapes affect decoder recognition by altering the QR code's boundary detection:

.. list-table:: Frame Shape Decoder Compatibility
   :header-rows: 1

   * - Frame Shape
     - ZXing C++
     - OpenCV
     - PyZBar
     - Mobile Apps
     - Recommended Settings
   * - square (none)
     - ✅ Excellent
     - ✅ Excellent
     - ✅ Excellent
     - ✅ Excellent
     - Standard settings
   * - rounded-rect
     - ✅ Very Good
     - ✅ Very Good
     - ✅ Good
     - ⚠️ Variable
     - corner_radius ≤ 0.2, border ≥ 4
   * - circle
     - ⚠️ Good
     - ⚠️ Good
     - ⚠️ Fair
     - ❌ Poor
     - border ≥ 5, clip_mode='clip'
   * - squircle
     - ⚠️ Good
     - ⚠️ Fair
     - ❌ Poor
     - ❌ Poor
     - border ≥ 5, simple shapes only
   * - custom
     - ❌ Variable
     - ❌ Variable
     - ❌ Poor
     - ❌ Poor
     - Extensive testing required

**Production Recommendations:**

* **High Compatibility**: Use no frame or ``rounded-rect`` with small corner radius
* **Testing Required**: Circle and squircle frames need thorough validation
* **Avoid in Production**: Custom frames without comprehensive decoder testing

Centerpiece (Logo Area) Compatibility
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Centerpiece areas impact error correction capability and pattern recognition:

.. list-table:: Centerpiece Size Compatibility by Error Level
   :header-rows: 1

   * - Error Level
     - Max Safe Size
     - Recommended Size
     - Notes
   * - L (7%)
     - 0.05
     - 0.03
     - Very limited logo space
   * - M (15%)
     - 0.12
     - 0.08
     - Suitable for small logos
   * - Q (25%)
     - 0.18
     - 0.12
     - Good logo visibility
   * - H (30%)
     - 0.25
     - 0.15
     - Maximum logo area

**Centerpiece Shape Compatibility:**

* **Rectangle**: Best compatibility, most predictable
* **Circle**: Good with most decoders, test mobile apps
* **Squircle**: Variable compatibility, requires testing

**Critical Guidelines:**

* Always use ``centerpiece_margin ≥ 2`` for safety buffer
* Test centerpiece + frame combinations thoroughly
* Consider fallback QR codes for critical applications
* Use highest error correction level (H) for large centerpieces

Combined Features Compatibility Risk
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When combining multiple Phase 4 features, compatibility risks multiply:

.. warning::
   **High Risk Combinations (Extensive Testing Required):**

   * Circle frame + large centerpiece + gradient background
   * Custom frame + squircle centerpiece
   * Fade clip mode + connected shapes + centerpiece

   **Lower Risk Combinations:**

   * Rounded-rect frame + small rect centerpiece + solid background
   * No frame + small circle centerpiece + simple shapes

PNG Conversion for Phase 4 Features
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Phase 4 features require special attention during PNG conversion:

.. code-block:: python

   # Recommended settings for Phase 4 features
   conversion_settings = {
       'dpi': 300,          # Higher DPI for frame clarity
       'width': 600,        # Larger size for centerpiece detail
       'height': 600,
       'background': 'white',
       'antialias': False,  # Sharp edges for frame detection
       'format': 'PNG'
   }

**Testing Protocol for Phase 4:**

1. **Generate test QR codes** with your exact Phase 4 configuration
2. **Convert to PNG** using recommended settings
3. **Test with multiple libraries** (zxingcpp, OpenCV, pyzbar)
4. **Validate on mobile devices** your users will actually use
5. **Test edge cases** (low light, angled scanning, small sizes)
6. **Implement fallbacks** if any decoder fails

Related Documentation
---------------------

- :doc:`api/index` - Complete API reference
- :doc:`shapes` - Shape options and visual styling examples
- :doc:`quickstart` - Getting started guide
- :doc:`examples` - Usage examples and patterns

.. note::
    This compatibility reference is based on testing with specific decoder versions.
    Results may vary with different implementations or versions. Always test with
    your specific deployment environment.
