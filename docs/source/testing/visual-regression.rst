Visual Regression Testing
========================

SegnoMMS uses visual regression testing to ensure that QR code generation remains visually consistent across code changes. This guide explains our visual regression testing approach and best practices.

Philosophy
----------

Visual regression tests compare **rendered PNG images** rather than SVG structure. This approach ensures we catch actual visual changes while ignoring inconsequential SVG markup differences.

Key principles:

* Compare rendered output (PNG), not source code (SVG)
* Use deterministic rendering parameters
* Store baseline images in version control
* Provide clear update workflows

Research Findings
~~~~~~~~~~~~~~~~~

Research into visual regression testing best practices for Python projects confirms that comparing rendered images 
rather than source code is critical for reliable testing:

**Rendered Images Over XML Comparison**: Comparing SVG XML structure leads to false failures when visual appearance 
hasn't changed. XML attributes can reorder, metadata can change, and library updates can alter structure without 
visual impact.

**False Positive Prevention**: For high-contrast geometric content like QR codes, visual regression testing is 
particularly effective as changes are usually stark and meaningful. Tolerance settings should start with exact 
comparison and add minimal tolerance only when needed.

**Industry Tools**: Mature pytest plugins like pytest-image-snapshot provide automated baseline management, 
diff visualization, and tolerance support with minimal configuration.

Directory Structure
------------------

Visual regression test files are organized as follows::

    tests/
    ├── visual/
    │   ├── baseline/     # Reference images
    │   │   ├── test_name.baseline.svg
    │   │   └── test_name.baseline.png
    │   ├── output/       # Generated during test runs
    │   │   ├── test_name.actual.svg
    │   │   └── test_name.actual.png
    │   └── diff/         # Difference visualizations
    │       └── test_name.diff.html

PNG files are stored alongside SVG files for easy comparison and debugging.

Rendering Parameters
-------------------

To ensure consistent rendering across environments, we use standardized parameters:

.. code-block:: python

    RENDER_PARAMS = {
        "width": 400,        # Fixed width in pixels
        "height": 400,       # Fixed height in pixels
        "dpi": 96,          # Standard screen DPI
        "background_color": "white",  # Consistent background
    }

These parameters are defined in ``tests/conftest.py`` and used by all visual tests.

Writing Visual Tests
-------------------

Basic Example
~~~~~~~~~~~~~

.. code-block:: python

    def test_basic_qr_visual(image_snapshot):
        """Test basic QR code visual output."""
        # Generate QR code
        buffer = io.StringIO()
        write_segno_mms(
            "Hello Visual Testing",
            buffer,
            scale=10,
            dark="#000000",
            light="#FFFFFF"
        )
        svg_content = buffer.getvalue()
        
        # Convert to PNG
        png_bytes = svg_to_png(svg_content, return_bytes=True)
        
        # Compare with baseline
        assert image_snapshot(png_bytes, "basic_qr_visual")

Parametrized Tests
~~~~~~~~~~~~~~~~~~

.. code-block:: python

    @pytest.mark.parametrize("shape,corner_radius", [
        ("square", 0),
        ("squircle", 0.2),
        ("circle", 0),
    ])
    def test_shape_variations(image_snapshot, shape, corner_radius):
        """Test various shape configurations."""
        buffer = io.StringIO()
        kwargs = {
            "scale": 10,
            "shape": shape,
        }
        if corner_radius > 0:
            kwargs["corner_radius"] = corner_radius
            
        write_segno_mms("Shape Test", buffer, **kwargs)
        svg_content = buffer.getvalue()
        
        # Convert to PNG
        png_bytes = svg_to_png(svg_content, return_bytes=True)
        
        # Compare with baseline
        test_name = f"shape_{shape}_radius_{corner_radius}"
        assert image_snapshot(png_bytes, test_name)

Running Visual Tests
-------------------

First Run (Create Baselines)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

On the first run, baseline images are automatically created::

    pytest tests/test_visual_regression_enhanced.py

This will create baseline PNG and SVG files in ``tests/visual/baseline/``.

Subsequent Runs
~~~~~~~~~~~~~~~

Future test runs compare generated images against baselines::

    pytest tests/test_visual_regression_enhanced.py

If images differ, tests will fail and difference files will be created in ``tests/visual/diff/``.

Updating Baselines
~~~~~~~~~~~~~~~~~~

When visual changes are intentional, update baselines using::

    pytest tests/test_visual_regression_enhanced.py --update-baseline

Review the changes carefully before committing updated baselines.

Debugging Failures
-----------------

When a visual test fails:

1. **Check output directory**: Compare ``output/*.png`` with ``baseline/*.png``
2. **Review diff files**: Open ``diff/*.html`` to see side-by-side comparison
3. **Verify changes**: Ensure the visual change is intentional
4. **Update if needed**: Run with ``--update-baseline`` if change is correct

Dependencies
-----------

Visual regression testing requires:

* **Pillow**: For image manipulation (``pip install pillow``)
* **CairoSVG**: Recommended SVG to PNG converter (``pip install cairosvg``)

Alternative converters (fallback order):

1. rsvg-convert (command line tool)
2. svglib + reportlab
3. ImageMagick (wand library or convert command)

Best Practices
-------------

1. **Use descriptive test names**: Makes it easy to identify which visual aspect failed
2. **Test one aspect per test**: Isolate visual features for clearer debugging
3. **Include edge cases**: Test minimum/maximum sizes, complex content
4. **Document visual changes**: Include rationale when updating baselines
5. **Review baseline updates**: Treat baseline changes like code changes in reviews

CI/CD Integration
----------------

For consistent results in CI:

1. Use the same rendering library (recommend CairoSVG)
2. Pin dependency versions
3. Consider using Docker for environment consistency
4. Store baseline images in git (they're typically small for QR codes)

Example GitHub Actions setup:

.. code-block:: yaml

    - name: Install visual test dependencies
      run: |
        pip install pillow cairosvg
        
    - name: Run visual regression tests
      run: |
        pytest tests/test_visual_regression_enhanced.py

Advanced Usage
-------------

Custom Tolerance
~~~~~~~~~~~~~~~

For tests that may have minor variations:

.. code-block:: python

    def snapshot_with_tolerance(image_data, name, threshold=0.1):
        """Compare with tolerance for minor differences."""
        # Custom comparison logic with threshold
        pass

Platform-Specific Baselines
~~~~~~~~~~~~~~~~~~~~~~~~~~

If rendering differs across platforms:

.. code-block:: python

    import platform
    
    def test_platform_specific(image_snapshot):
        system = platform.system().lower()
        test_name = f"test_{system}"
        assert image_snapshot(png_bytes, test_name)

Migration from SVG Comparison
----------------------------

To migrate existing SVG-based visual tests:

1. Keep existing SVG comparison for structure validation
2. Add PNG comparison for visual validation
3. Gradually phase out SVG comparison as confidence grows
4. Maintain both during transition period

The enhanced visual regression approach provides more reliable testing by focusing on actual visual output rather than implementation details.