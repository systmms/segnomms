Testing Best Practices
======================

This section outlines best practices for testing SegnoMMS applications and contributing to the SegnoMMS test suite.

Development Testing Principles
-------------------------------

1. **Use Test Constants**
   Always import from ``tests.constants`` instead of using string literals for better maintainability and IDE support.

2. **Follow Testing Pyramid**
   Write many unit tests, some integration tests, and few end-to-end tests for optimal coverage and speed.

3. **Test Edge Cases**
   Include boundary conditions, error scenarios, and invalid input handling in your tests.

4. **Mock External Dependencies**
   Isolate unit tests from external systems and dependencies to ensure reliability and speed.

5. **Validate Visual Output**
   Use visual regression tests for shape and rendering changes that could affect QR appearance.

Type-Safe Testing with Constants
---------------------------------

Always use the centralized test constants for consistent, validated test data:

.. code-block:: python

   # ✅ Good - Type-safe with validation
   from tests.constants import ModuleShape, TEST_COLORS, QR_PAYLOADS

   def test_shape_rendering():
       qr = segno.make(QR_PAYLOADS["url"])
       config = create_test_config(
           shape=ModuleShape.CIRCLE.value,
           dark=TEST_COLORS["black"],
           light=TEST_COLORS["white"]
       )

   # ❌ Avoid - String literals without validation
   def test_shape_rendering_bad():
       qr = segno.make("https://example.com")  # Magic string
       write(qr, output, shape="cirle")        # cspell:disable-line - intentional typo example

Error Handling Testing
----------------------

Test both success and error paths with the intent-based API:

.. code-block:: python

   def test_intent_error_handling():
       """Test comprehensive error handling patterns."""
       from segnomms.exceptions import IntentValidationError, UnsupportedIntentError

       renderer = SegnoMMS()

       # Test validation errors
       with pytest.raises(IntentValidationError) as exc_info:
           invalid_intents = IntentsConfig(
               style=StyleIntents(corner_radius=5.0)  # Out of range
           )
           renderer.render_with_intents("test", invalid_intents)

       assert "corner_radius" in str(exc_info.value)

       # Test unsupported features
       with pytest.raises(UnsupportedIntentError) as exc_info:
           unsupported_intents = IntentsConfig(
               style=StyleIntents(module_shape="pyramid")  # Unsupported
           )
           renderer.render_with_intents("test", unsupported_intents)

       assert exc_info.value.alternatives  # Should suggest alternatives

Visual Regression Testing Guidelines
------------------------------------

When testing visual changes:

1. **Use Appropriate Baselines**
   Generate baselines on the same platform where tests will run (CI/CD environment).

2. **Set Reasonable Tolerance**
   Configure tolerance levels that catch real regressions without triggering on minor rendering differences.

3. **Test Key Scenarios**
   Focus on shapes, colors, frame effects, and accessibility features that users will notice.

4. **Update Baselines Carefully**
   Only update baselines after verifying that visual changes are intentional and correct.

Example visual regression test:

.. code-block:: python

   def test_shape_visual_regression(tmp_path):
       """Test that shape rendering matches expected output."""
       qr = segno.make(QR_PAYLOADS["text"])
       output_path = tmp_path / "shape_test.svg"

       config = create_test_config(
           shape=ModuleShape.SQUIRCLE.value,
           scale=DEFAULT_SCALE
       )

       write(qr, output_path, **config)

       # Convert to PNG for pixel comparison
       png_path = convert_svg_to_png(output_path)

       # Compare with baseline (pytest-image-snapshot)
       assert_image_matches_baseline(png_path, "squircle_shape.png")

Performance Testing Practices
-----------------------------

Include performance considerations in your tests:

.. code-block:: python

   import time
   from tests.helpers.benchmarks import performance_test

   @performance_test(max_duration_ms=100)
   def test_qr_generation_performance():
       """Test that QR generation completes within performance targets."""
       qr = segno.make(QR_PAYLOADS["long_text"])

       start_time = time.time()
       config = create_test_config(shape=ModuleShape.CONNECTED.value)
       write(qr, output, **config)
       duration_ms = (time.time() - start_time) * 1000

       assert duration_ms < 100, f"Generation took {duration_ms}ms, expected < 100ms"

Test Organization Best Practices
---------------------------------

Structure tests for maintainability:

1. **Group Related Tests**
   Use classes to group related functionality tests together.

2. **Use Descriptive Names**
   Test names should clearly describe what behavior is being verified.

3. **Separate Happy Path and Error Cases**
   Keep success scenarios and error handling tests organized separately.

4. **Use Fixtures Appropriately**
   Share common setup using pytest fixtures with appropriate scoping.

Example test organization:

.. code-block:: python

   class TestShapeRendering:
       """Tests for shape rendering functionality."""

       def test_basic_shapes_render_successfully(self):
           """All basic shapes should render without errors."""
           # Test happy path

       def test_invalid_shape_raises_validation_error(self):
           """Invalid shape names should raise clear errors."""
           # Test error handling

       def test_shape_parameters_are_validated(self):
           """Shape-specific parameters should be validated."""
           # Test parameter validation

   class TestColorConfiguration:
       """Tests for color configuration and validation."""

       @pytest.fixture
       def color_test_cases(self):
           return TEST_COLORS["accessibility_compliant"]

       def test_valid_colors_accepted(self, color_test_cases):
           """Valid color formats should be accepted."""
           # Use fixture data

Contributing Test Guidelines
----------------------------

When contributing tests to SegnoMMS:

1. **Follow Existing Patterns**
   Look at existing tests for similar functionality and follow the same patterns.

2. **Add Comprehensive Coverage**
   New features should include unit tests, integration tests, and visual tests as appropriate.

3. **Update Test Documentation**
   Document any new test utilities, fixtures, or patterns in this documentation.

4. **Run Full Test Suite**
   Always run ``make test-all`` before submitting pull requests.

5. **Include Performance Tests**
   Performance-sensitive changes should include benchmarking tests.

Test Naming Conventions
------------------------

Use consistent naming patterns:

.. code-block:: python

   # Unit tests - test specific behavior
   def test_circle_shape_generates_circular_modules():
       pass

   # Integration tests - test component interaction
   def test_shape_renderer_integrates_with_svg_builder():
       pass

   # Error handling - test specific error conditions
   def test_invalid_corner_radius_raises_validation_error():
       pass

   # Performance tests - test speed/memory constraints
   def test_large_qr_generation_completes_within_time_limit():
       pass

   # Visual regression - test visual output
   def test_squircle_shape_visual_regression():
       pass

Debugging Failed Tests
----------------------

When tests fail:

1. **Check Test Output**
   Read pytest output carefully - it often contains helpful debugging information.

2. **Use Verbose Mode**
   Run ``pytest -v`` for more detailed output about what's happening.

3. **Isolate the Problem**
   Run just the failing test with ``pytest path/to/test.py::test_name``.

4. **Check Dependencies**
   Ensure all required dependencies are installed and up to date.

5. **Verify Environment**
   Platform-specific issues may require checking the test environment.

Common debugging commands:

.. code-block:: bash

   # Run specific test with verbose output
   pytest tests/unit/test_shapes.py::test_circle_shape -v

   # Run with debugging breakpoints
   pytest tests/unit/test_shapes.py --pdb

   # Show test coverage
   pytest tests/unit/ --cov=segnomms --cov-report=html

   # Run tests with specific markers
   pytest -m "not slow" tests/

Testing Environment Setup
--------------------------

For consistent testing environments:

1. **Use Virtual Environments**
   Always test in isolated Python environments to avoid dependency conflicts.

2. **Pin Test Dependencies**
   Use specific versions of testing tools to ensure reproducible results.

3. **Platform Consistency**
   Use Docker or similar tools for cross-platform consistency when needed.

4. **CI/CD Integration**
   Ensure tests pass in the same environment where they'll run in CI/CD.

Local development setup:

.. code-block:: bash

   # Set up development environment
   make setup

   # Run quick development tests
   make test-quick

   # Run full test suite before committing
   make test-all

   # Update visual baselines after intentional changes
   make test-visual --update-baselines

Quality Metrics and Goals
-------------------------

SegnoMMS maintains high quality standards:

**Coverage Targets:**
- Unit test coverage: >90%
- Integration test coverage: >80%
- End-to-end scenario coverage: >70%

**Performance Targets:**
- Small QR codes (21x21): <10ms generation
- Large QR codes (177x177): <100ms generation
- Memory usage: <50MB peak for typical workloads

**Quality Gates:**
- All tests must pass before merging
- No decrease in test coverage allowed
- Performance regressions >10% require investigation
- Visual regressions must be explicitly approved

**Monitoring:**
- Automated test runs on all pull requests
- Performance benchmarking on releases
- Visual regression testing with baseline management
- Test execution time monitoring

These practices ensure SegnoMMS maintains high quality while enabling rapid development and deployment.
