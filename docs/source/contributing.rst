Contributing to SegnoMMS
========================

Thank you for your interest in contributing to SegnoMMS! This document provides guidelines for contributing to the project.

Development Setup
-----------------

1. **Clone the repository:**

   .. code-block:: bash

      git clone https://github.com/systmms/segnomms.git
      cd segnomms

2. **Set up development environment:**

   .. code-block:: bash

      make setup

3. **Install git hooks (Lefthook):**

   .. code-block:: bash

      lefthook install

   Lefthook manages git hooks for code quality checks including:

   - **actionlint**: GitHub Actions workflow validation
   - **black**: Python code formatting
   - **isort**: Import sorting
   - **flake8**: Python linting
   - **mypy**: Type checking
   - **bandit**: Security analysis

   Hooks run automatically on commit. To run manually:

   .. code-block:: bash

      lefthook run pre-commit

Development Workflow
--------------------

Code Quality Standards
~~~~~~~~~~~~~~~~~~~~~~~

- **MyPy:** All code must pass strict type checking with zero errors
- **Black:** All Python code must be formatted with Black
- **isort:** All imports must be properly sorted and organized
- **flake8:** All code must pass linting checks
- **Tests:** All existing tests must pass before committing

Discovering Available Commands
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use ``make help`` to discover all available Makefile targets:

.. code-block:: bash

   make help

This displays all commands organized by category (setup, testing, documentation, etc.)

Running Tests
~~~~~~~~~~~~~

.. code-block:: bash

   # Run all tests
   make test

   # Run specific test categories
   make test-unit
   make test-integration
   make test-visual
   make test-structural
   make test-performance

   # Run quick tests during development
   make test-quick

**Test Script Discoverability Policy:**

All permanent test scripts must have corresponding Makefile targets to ensure
discoverability. When creating new test scripts:

- **Permanent scripts** (regression tests, compatibility tests, benchmarks): Add a Makefile target
- **Temporary scripts** (one-off debugging): No Makefile target needed
- Use ``make help`` to verify your script is discoverable

Documentation
~~~~~~~~~~~~~

- Update documentation when adding new features
- All public APIs must have comprehensive docstrings
- Run ``make docs`` to build documentation locally
- Documentation uses Sphinx with RST format

Git Commit Standards
~~~~~~~~~~~~~~~~~~~~

**NEVER use ``--no-verify`` flag with git commits.**

- Lefthook git hooks exist to maintain code quality and consistency
- All formatting, linting, and type checking issues must be resolved before committing
- If git hooks fail, fix the underlying issues rather than bypassing them
- Commits must follow `Conventional Commits <https://www.conventionalcommits.org/>`_ format

Submitting Changes
------------------

1. **Create a feature branch:**

   .. code-block:: bash

      git checkout -b feature/your-feature-name

2. **Make your changes:**

   - Write code following the established patterns
   - Add tests for new functionality
   - Update documentation as needed

3. **Test your changes:**

   .. code-block:: bash

      make test
      make docs

4. **Commit your changes:**

   .. code-block:: bash

      git add .
      git commit -m "feat: add your feature description"

5. **Push and create a pull request:**

   .. code-block:: bash

      git push origin feature/your-feature-name

Code Review Process
-------------------

1. All changes must be reviewed via pull request
2. Ensure all CI checks pass
3. Address any review feedback
4. Maintain clean commit history

Getting Help
------------

- Check existing issues and discussions
- Create an issue for bug reports or feature requests
- Join our community discussions for general questions

License
-------

By contributing to SegnoMMS, you agree that your contributions will be licensed under the project's license.
