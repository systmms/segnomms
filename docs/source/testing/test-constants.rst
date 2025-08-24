Using Test Constants
====================

This guide shows how to use the centralized test constants in SegnoMMS to write more maintainable and reliable tests.

Why Use Constants?
------------------

Using string literals in tests creates several problems:

1. **Brittleness**: Typos in strings cause runtime failures
2. **Inconsistency**: Same value written differently in different places
3. **No autocomplete**: IDEs can't help with string values
4. **No validation**: Invalid values only discovered at runtime
5. **Refactoring difficulty**: Changing values requires finding all occurrences

The Constants Module
--------------------

The ``tests/constants.py`` module provides:

* Enum re-exports for type safety
* Predefined test data sets
* Common configurations
* Utility functions

Migration Examples
------------------

Before: Using String Literals
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # ❌ Brittle string literals
   def test_circle_shape():
       write(qr, output, shape="circle", scale=10)
       
   # ❌ Typo causes runtime error
   def test_squircle_shape():
       write(qr, output, shape="squirle")  # Oops! Typo!
       
   # ❌ Inconsistent test data
   def test_colors():
       test_cases = [
           {"dark": "#000000", "light": "#FFFFFF"},
           {"dark": "#000", "light": "#FFF"},  # Same color, different format
       ]

After: Using Constants
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from tests.constants import ModuleShape, create_test_config, TEST_COLORS
   
   # ✅ Type-safe enum values
   def test_circle_shape():
       config = create_test_config(shape=ModuleShape.CIRCLE.value)
       write(qr, output, **config)
       
   # ✅ IDE autocomplete prevents typos
   def test_squircle_shape():
       config = create_test_config(shape=ModuleShape.SQUIRCLE.value)
       write(qr, output, **config)
       
   # ✅ Consistent test data
   def test_colors():
       config = create_test_config(
           dark=TEST_COLORS["black"],
           light=TEST_COLORS["white"]
       )
       write(qr, output, **config)

Common Patterns
---------------

Testing All Shapes
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from tests.constants import VALID_SHAPES
   
   @pytest.mark.parametrize("shape", VALID_SHAPES)
   def test_all_shapes(shape):
       config = create_test_config(shape=shape)
       write(qr, output, **config)
       # Test assertions...

Testing Shape Categories
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from tests.constants import BASIC_SHAPES, CONNECTED_SHAPES
   
   def test_basic_shapes_only():
       for shape in BASIC_SHAPES:
           # Basic shapes should work with safe mode
           config = create_test_config(shape=shape, safe_mode=True)
           write(qr, output, **config)
   
   def test_connected_shapes():
       for shape in CONNECTED_SHAPES:
           # Connected shapes need special handling
           config = create_test_config(
               shape=shape,
               merge=MergeStrategy.SOFT.value,
               connectivity=ConnectivityMode.EIGHT_WAY.value
           )
           write(qr, output, **config)

Using Predefined Test Cases
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from tests.constants import SHAPE_TEST_CASES
   
   @pytest.mark.parametrize("test_case", SHAPE_TEST_CASES)
   def test_shape_configurations(test_case):
       config = create_test_config(
           shape=test_case["shape"],
           corner_radius=test_case["corner_radius"]
       )
       write(qr, output, **config)
       
       # Use test case metadata for assertions
       if test_case["supports_merging"]:
           assert "merge" in result

Testing with Common Payloads
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from tests.constants import QR_PAYLOADS
   
   def test_url_encoding():
       qr = segno.make(QR_PAYLOADS["url"])
       # Test URL-specific behavior
       
   def test_unicode_support():
       qr = segno.make(QR_PAYLOADS["unicode"])
       # Test Unicode handling

Best Practices
--------------

1. Import What You Need
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Import specific constants
   from tests.constants import ModuleShape, DEFAULT_SCALE
   
   # Or import categories
   from tests.constants import VALID_SHAPES, COLOR_TEST_CASES

2. Use Enum Values
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # ✅ Good: Use enum value
   shape = ModuleShape.CIRCLE.value
   
   # ❌ Avoid: Direct string
   shape = "circle"

3. Extend Constants Module
~~~~~~~~~~~~~~~~~~~~~~~~~~

When adding new test cases, add them to the constants module:

.. code-block:: python

   # In tests/constants.py
   NEW_FEATURE_TEST_CASES = [
       {"config": {...}, "expected": ...},
       {"config": {...}, "expected": ...},
   ]
   
   # In your test
   from tests.constants import NEW_FEATURE_TEST_CASES

4. Type Hints
~~~~~~~~~~~~~

Use type hints with enums for better IDE support:

.. code-block:: python

   from tests.constants import ModuleShape
   
   def create_qr_with_shape(shape: str) -> str:
       # shape should be ModuleShape.XXX.value
       config = create_test_config(shape=shape)
       # ...

Available Constants
-------------------

Shapes
~~~~~~

.. code-block:: python

   from tests.constants import (
       VALID_SHAPES,        # All valid shape names
       BASIC_SHAPES,        # Simple geometric shapes
       CONNECTED_SHAPES,    # Shapes that support merging
       SHAPE_TEST_CASES     # Predefined shape configurations
   )

Colors
~~~~~~

.. code-block:: python

   from tests.constants import (
       TEST_COLORS,         # Named color constants
       COLOR_TEST_CASES,    # Common color combinations
       DEFAULT_DARK,        # Standard dark color
       DEFAULT_LIGHT        # Standard light color
   )

Payloads
~~~~~~~~

.. code-block:: python

   from tests.constants import (
       QR_PAYLOADS,         # Common test content (url, simple, unicode, etc.)
       ERROR_LEVELS         # QR error correction levels
   )

Configuration Helpers
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from tests.constants import (
       create_test_config,  # Build consistent configs
       DEFAULT_SCALE,       # Standard scale value (10)
       DEFAULT_BORDER,      # Standard border size (4)
       DEFAULT_TEST_CONFIG, # Minimal default configuration
       FULL_TEST_CONFIG     # Complete configuration example
   )

Test Helpers
~~~~~~~~~~~~

SegnoMMS also provides test helper classes for advanced testing scenarios:

.. code-block:: python

   from tests.helpers import (
       QRScanabilityHarness,     # QR code scanning validation
       TestCaseGenerator,        # Generate standardized test cases
       TestOutputManager         # Organized file output management
   )

**QRScanabilityHarness** - Validates that generated QR codes are actually scannable:

.. code-block:: python

   from tests.helpers import get_scanability_harness
   
   def test_qr_scanability():
       qr = segno.make("Test content")
       config = create_test_config(shape=ModuleShape.CIRCLE.value)
       
       # Generate SVG
       output = StringIO()
       write(qr, output, **config)
       svg_content = output.getvalue()
       
       # Validate scanability
       harness = get_scanability_harness()
       result = harness.validate_svg(svg_content, "Test content")
       assert result.is_scannable

**TestCaseGenerator** - Creates standardized test case configurations:

.. code-block:: python

   from tests.helpers import TestCaseGenerator, TestCategory
   
   def test_shape_gallery():
       # Get all shape test cases
       test_cases = TestCaseGenerator.get_shape_test_cases()
       
       for test_case in test_cases:
           qr = TestCaseGenerator.generate_qr(test_case)
           # Test each shape configuration...

**TestOutputManager** - Organizes test output files systematically:

.. code-block:: python

   from tests.helpers import TestOutputManager
   
   def test_visual_regression():
       output_manager = TestOutputManager(Path("test_output"))
       
       # Generate organized output with SVG, PNG, and config JSON
       outputs = output_manager.generate_test_output(
           test_case_id="shape_circle_safe_mode",
           qr_code=qr,
           config=config,
           output_type="regression"
       )

Benefits
--------

1. **Maintainability**: Change values in one place
2. **Reliability**: Catch errors at import time
3. **Discoverability**: See all valid values easily
4. **Documentation**: Constants serve as living documentation
5. **Consistency**: Same values used everywhere
6. **IDE Support**: Autocomplete and type checking

Migration Checklist
-------------------

When updating existing tests:

* Replace string literals with enum values
* Use predefined test data sets
* Replace magic numbers with named constants
* Use ``create_test_config()`` for consistency
* Add new test cases to constants module
* Remove duplicate test data definitions
* Add type hints where helpful

Example Migration
-----------------

Before
~~~~~~

.. code-block:: python

   def test_various_shapes():
       # ❌ String literals, inconsistent configs
       for shape in ["square", "circle", "rounded"]:
           write(qr, output, shape=shape, scale=10, border=4)
           
       # ❌ Magic numbers
       write(qr, output, shape="squircle", corner_radius=0.3, scale=8)
       
       # ❌ Duplicate color definitions
       write(qr, output, dark="#000000", light="#FFFFFF")

After
~~~~~

.. code-block:: python

   from tests.constants import (
       BASIC_SHAPES, 
       create_test_config,
       ModuleShape,
       TEST_COLORS
   )
   
   def test_various_shapes():
       # ✅ Type-safe shapes, consistent config
       for shape in BASIC_SHAPES:
           config = create_test_config(shape=shape)
           write(qr, output, **config)
           
       # ✅ Named constants
       squircle_config = create_test_config(
           shape=ModuleShape.SQUIRCLE.value,
           corner_radius=0.3
       )
       write(qr, output, **squircle_config)
       
       # ✅ Predefined test data
       color_config = create_test_config(
           dark=TEST_COLORS["brand_primary"],
           light=TEST_COLORS["brand_secondary"]
       )
       write(qr, output, **color_config)

This approach makes tests more maintainable, reduces errors, and provides better developer experience through IDE support and type safety.