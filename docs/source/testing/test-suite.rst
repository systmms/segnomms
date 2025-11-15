Test Suite Organization
=======================

The SegnoMMS test suite contains 733+ tests organized into multiple categories for comprehensive validation of all functionality.

Unit Tests (tests/unit/)
-------------------------

**Purpose:** Test individual components in isolation with comprehensive coverage.

**Coverage:** 733+ tests across core functionality:

* Configuration models and validation
* Matrix manipulation algorithms
* Shape rendering systems
* Color and accessibility utilities
* Intent processing logic
* Export and serialization

**Key Features:**

* Mock-based isolation testing
* Comprehensive edge case coverage
* Pydantic model validation testing
* Error handling and boundary condition tests

**Run Command:**

.. code-block:: bash

   make test-unit
   # With coverage: pytest tests/unit/ --cov=segnomms

**Test Categories:**

* **Configuration Tests** - Pydantic model validation, schema generation, serialization
* **Core Algorithm Tests** - Matrix detection, neighbor analysis, clustering algorithms
* **Shape Rendering Tests** - All 14+ shape renderers with parameter validation
* **Color System Tests** - Palette validation, contrast checking, accessibility compliance
* **Plugin Interface Tests** - Segno integration, parameter passing, output validation

Integration Tests (tests/integration/)
---------------------------------------

**Purpose:** Test component interaction and end-to-end workflows.

**Focus Areas:**

* Plugin integration with Segno
* Configuration processing pipelines
* Shape rendering with different backends
* Frame effects and clipping operations
* Export format generation and validation

**Key Features:**

* Real QR code generation testing
* Cross-component interaction validation
* Configuration compatibility testing
* Plugin interface compliance

**Run Command:**

.. code-block:: bash

   make test-integration

**Test Scenarios:**

* **End-to-End Rendering** - Complete QR generation workflows with different configurations
* **Configuration Processing** - Complex configuration validation and transformation
* **Shape Interactions** - How different shapes work together in the same QR code
* **Frame and Centerpiece** - Advanced Phase 4 features integration testing
* **Export Compatibility** - Different output formats and options

Structural Tests (tests/structural/)
------------------------------------

**Purpose:** Validate SVG structure, accessibility compliance, and format correctness.

**Validation Areas:**

* SVG XML structure and syntax
* CSS class application and naming
* Accessibility attributes and ARIA compliance
* Interactive element structure
* Frame and clipping path definitions

**Key Features:**

* XML schema validation
* CSS selector testing
* WCAG compliance checking
* Cross-browser compatibility validation

**Run Command:**

.. code-block:: bash

   make test-structural

**Validation Types:**

* **SVG Schema Validation** - Proper XML structure and SVG specification compliance
* **CSS Class Verification** - Correct CSS class application for interactive features
* **Accessibility Compliance** - ARIA attributes, labels, and accessibility standards
* **Interactive Elements** - Hover effects, click handlers, and tooltip data
* **Frame Structure** - Custom frame shapes, clipping paths, and gradients

Visual Regression Tests (tests/visual/)
----------------------------------------

**Purpose:** Detect visual changes and ensure QR code functionality through image comparison.

**Testing Strategy:**

* Render QR codes to PNG for pixel-perfect comparison
* Automated baseline management with tolerance settings
* Cross-platform consistency verification
* Scanability validation with multiple readers

**Key Features:**

* Automated baseline generation and updates
* Configurable tolerance for minor rendering differences
* Integration with CI/CD for automatic regression detection
* Visual diff reporting for debugging

**Run Command:**

.. code-block:: bash

   make test-visual

**Test Coverage:**

* **Shape Rendering** - All 14+ shapes with various parameters
* **Color Variations** - Different color combinations and accessibility compliance
* **Frame Effects** - Custom frames, clipping modes, and gradient backgrounds
* **Interactive Features** - Hover states, animations, and CSS effects
* **Scanability Testing** - QR code functionality validation

**Tools and Dependencies:**

* ``pytest-image-snapshot`` for baseline management
* ``cairosvg`` or ``rsvg-convert`` for PNG rendering
* ``qr`` or ``zxing`` for scanability testing
* Platform-specific rendering consistency checks

Performance Tests (tests/perf/)
-------------------------------

**Purpose:** Monitor performance characteristics and prevent regressions.

**Benchmarking Areas:**

* QR generation speed across different sizes
* Memory usage with various configurations
* Complex shape rendering performance
* Batch processing efficiency
* Configuration validation overhead

**Key Metrics:**

* Processing time per QR code
* Memory consumption patterns
* CPU usage during complex rendering
* Scaling behavior with QR code size
* Cache effectiveness

**Run Commands:**

.. code-block:: bash

   make benchmark           # Full benchmark suite
   make benchmark-quick     # Quick benchmarks
   make benchmark-memory    # Memory profiling
   make benchmark-report    # Generate performance report

**Performance Targets:**

* **Small QR codes** (21x21): < 10ms generation time
* **Large QR codes** (177x177): < 100ms generation time
* **Memory usage**: < 50MB peak for typical workloads
* **Batch processing**: Linear scaling with batch size

**Profiling Tools:**

* ``cProfile`` for CPU profiling
* ``memory_profiler`` for memory analysis
* ``pytest-benchmark`` for automated benchmarking
* Custom timing decorators for specific operations

Test Helpers and Utilities (tests/helpers/)
--------------------------------------------

**Purpose:** Provide reusable testing utilities and custom assertions.

**Available Utilities:**

* **Custom Assertions** - Domain-specific test assertions for QR validation
* **Mock Generators** - Generate test data for various scenarios
* **Test Fixtures** - Reusable test configurations and data
* **Validation Helpers** - SVG structure and content validation functions

**Key Components:**

.. code-block:: python

   # Custom assertions for QR testing
   from tests.helpers.assertions import (
       assert_valid_qr_structure,
       assert_scannable_qr,
       assert_css_classes_present,
       assert_accessibility_compliant
   )

   # Mock data generators
   from tests.helpers.generators import (
       generate_test_qr_codes,
       create_mock_configuration,
       generate_color_test_cases
   )

   # Validation utilities
   from tests.helpers.validators import (
       validate_svg_structure,
       validate_qr_scanability,
       check_visual_regression
   )

Test Fixtures (tests/fixtures/)
-------------------------------

**Purpose:** Provide consistent test data and configuration objects.

**Available Fixtures:**

* **QR Code Fixtures** - Pre-generated QR codes for various content types
* **Configuration Fixtures** - Standard configurations for different test scenarios
* **Color Palettes** - Test color combinations including accessibility edge cases
* **Shape Parameters** - Parameter sets for comprehensive shape testing

**Usage Example:**

.. code-block:: python

   import pytest
   from tests.fixtures import qr_fixtures, config_fixtures

   def test_shape_rendering(qr_fixtures, config_fixtures):
       qr = qr_fixtures['medium_url']
       config = config_fixtures['artistic_preset']
       result = render_qr(qr, config)
       assert_valid_qr_structure(result)

Test Configuration (conftest.py)
---------------------------------

**Purpose:** Central pytest configuration and shared fixture definitions.

**Configuration Features:**

* **Test Discovery** - Automatic test collection patterns
* **Fixture Scoping** - Session, module, and function-level fixtures
* **Plugin Configuration** - pytest plugin settings and customizations
* **Marker Definitions** - Custom test markers for categorization

**Available Markers:**

* ``@pytest.mark.slow`` - For long-running tests
* ``@pytest.mark.visual`` - For visual regression tests
* ``@pytest.mark.integration`` - For integration tests
* ``@pytest.mark.performance`` - For performance benchmarks

**Shared Fixtures:**

.. code-block:: python

   @pytest.fixture(scope="session")
   def test_qr_codes():
       """Generate standard test QR codes once per test session."""
       return generate_standard_test_qrs()

   @pytest.fixture
   def temp_output_dir(tmp_path):
       """Provide temporary directory for test output files."""
       return tmp_path / "test_output"

Continuous Integration
----------------------

**GitHub Actions Integration:**

The test suite is fully integrated with GitHub Actions for automated testing:

* **Pull Request Validation** - All tests run on PR creation/updates
* **Cross-Platform Testing** - Tests run on Ubuntu, macOS, and Windows
* **Python Version Matrix** - Tests across supported Python versions (3.8-3.12)
* **Performance Regression Detection** - Benchmark comparisons between commits

**CI Configuration:**

.. code-block:: yaml

   # Example GitHub Actions workflow
   name: Test Suite
   on: [push, pull_request]

   jobs:
     test:
       runs-on: ubuntu-latest
       strategy:
         matrix:
           python-version: [3.8, 3.9, 3.10, 3.11, 3.12]

       steps:
         - uses: actions/checkout@v4
         - name: Set up Python
           uses: actions/setup-python@v4
           with:
             python-version: ${{ matrix.python-version }}
         - name: Install dependencies
           run: make setup
         - name: Run test suite
           run: make test-all

**Quality Gates:**

* **Test Coverage** - Minimum 90% code coverage required
* **Performance Regression** - No more than 10% performance degradation
* **Visual Regression** - Zero unexpected visual changes
* **Documentation** - All public APIs must have docstrings

Local Development Testing
-------------------------

**Development Workflow:**

1. **Quick Iteration Testing:**

   .. code-block:: bash

      # Fast unit tests during development
      make test-quick

      # Test specific module
      pytest tests/unit/test_shapes.py -v

      # Test with coverage
      pytest tests/unit/ --cov=segnomms --cov-report=html

2. **Pre-Commit Validation:**

   .. code-block:: bash

      # Full test suite before committing
      make test-all

      # Include performance benchmarks
      make benchmark-quick

3. **Visual Regression Testing:**

   .. code-block:: bash

      # Update visual baselines after intentional changes
      make test-visual --update-baselines

      # Review visual diffs
      make test-visual --show-diffs

**IDE Integration:**

* **pytest integration** in VSCode, PyCharm, and other IDEs
* **Test discovery** automatically finds all test files
* **Debugging support** with breakpoints in test code
* **Coverage visualization** highlights untested code paths

Troubleshooting Common Issues
-----------------------------

**Test Failures:**

1. **Visual Regression Failures:**
   - Check if changes are intentional
   - Update baselines with ``--update-baselines`` flag
   - Verify rendering environment consistency

2. **Performance Regression:**
   - Profile with ``make benchmark-memory``
   - Check for memory leaks or inefficient algorithms
   - Compare with baseline performance metrics

3. **Integration Test Failures:**
   - Verify external dependencies are available
   - Check for environment-specific issues
   - Validate test data and fixtures

**Environment Issues:**

1. **Missing Dependencies:**

   .. code-block:: bash

      # Install all development dependencies (including tests)
      make setup

2. **Platform-Specific Issues:**
   - Use Docker for consistent environment
   - Check platform-specific test markers
   - Verify tool availability (rsvg-convert, etc.)

**Getting Help:**

* Check test logs for detailed error messages
* Use ``pytest -v`` for verbose output
* Enable debug logging for complex failures
* Consult the development team for persistent issues
