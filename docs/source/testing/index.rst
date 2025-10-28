Testing Documentation
=====================

This section provides comprehensive documentation for testing SegnoMMS, including test organization, best practices, and available utilities.

.. toctree::
   :maxdepth: 2

   test-suite
   test-constants
   visual-regression
   best-practices

Overview
--------

The SegnoMMS test suite is organized into multiple categories for systematic validation of all functionality:

* **Unit tests** - Test individual components in isolation
* **Integration tests** - Test component interaction and end-to-end workflows
* **Structural tests** - SVG structure and format validation
* **Visual regression tests** - Visual output validation and QR functionality
* **Performance tests** - Benchmarks and profiling

Quick Start
-----------

Run All Tests
~~~~~~~~~~~~~

.. code-block:: bash

   # Comprehensive test suite (recommended for CI/CD)
   make test

   # All tests including strict type checking
   make test-all

   # Quick development testing (unit tests only)
   make test-quick

Run Specific Test Categories
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Individual test categories
   make test-unit           # Unit tests
   make test-integration    # Integration tests
   make test-structural     # SVG structure validation
   make test-visual        # Visual regression tests
   make test-performance   # Performance benchmarks

   # All test categories (no linting/docs)
   make test-all-categories

Performance Benchmarking
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Comprehensive performance testing
   make benchmark           # Full benchmark suite
   make benchmark-quick     # Quick benchmarks
   make benchmark-memory    # Memory profiling
   make benchmark-report    # Generate performance report

Test Directory Structure
-------------------------

.. code-block:: text

   tests/
   ├── unit/                        # Unit tests for individual components
   ├── integration/                 # Integration tests for component interaction
   ├── structural/                  # SVG structure and format validation
   ├── visual/                      # Visual regression and QR functionality tests
   ├── perf/                        # Performance benchmarks and profiling
   ├── helpers/                     # Test utilities and custom assertions
   ├── fixtures/                    # Test data and configuration fixtures
   └── conftest.py                  # Pytest configuration and shared fixtures

Development Testing Best Practices
-----------------------------------

1. **Use Constants**: Import from ``segnomms.constants`` instead of string literals for better maintainability
2. **Follow Naming Conventions**: Use descriptive test names that explain the expected behavior
3. **Test Edge Cases**: Include boundary conditions and error scenarios
4. **Mock External Dependencies**: Isolate unit tests from external systems
5. **Validate Visual Output**: Use visual regression tests for shape and rendering changes
6. **Performance Regression**: Run benchmarks for performance-sensitive changes

For detailed information, see the individual testing documentation sections.
