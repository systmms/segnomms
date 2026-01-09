Installation
============

.. warning::
   **Beta Software Notice**: SegnoMMS is currently in beta (v0.1.x). While the core
   functionality is stable and extensively tested, APIs may change between minor versions.
   We recommend pinning to specific versions (e.g., ``segnomms==0.1.0``) for production
   use and reviewing the changelog before upgrading.

Requirements
------------

* Python >= 3.10
* Segno >= 1.5.2
* Pydantic >= 2.7

Install from PyPI
-----------------

The easiest way to install SegnoMMS is via pip:

.. code-block:: bash

   pip install segnomms

Install from Source
-------------------

To install from source:

.. code-block:: bash

   git clone https://github.com/systmms/segnomms.git
   cd segnomms
   pip install -e .

Development Installation
------------------------

For development, install with extra dependencies.

**Prerequisites**: Install `uv <https://github.com/astral-sh/uv>`_ for ultra-fast dependency management:

.. code-block:: bash

   # Install uv (if not already installed)
   pip install uv

Then clone and setup:

.. code-block:: bash

   git clone https://github.com/systmms/segnomms.git
   cd segnomms
   make setup

This installs the package with all development dependencies using uv, including:

* pytest and pytest-cov for testing
* black, isort, flake8, mypy for code quality
* pillow, lxml, beautifulsoup4 for testing utilities
* sphinx and sphinx-rtd-theme for documentation

Alternatively, if you prefer to use uv directly:

.. code-block:: bash

   uv sync
   uv pip install -e .

Verify Installation
-------------------

You can verify the installation by running:

.. code-block:: python

   import segno
   from segnomms import write

   # Create a simple QR code
   qr = segno.make("Test")

   # Test basic functionality
   with open('test.svg', 'w') as f:
       write(qr, f)

   # Test composition features
   with open('test_composition.svg', 'w') as f:
       write(qr, f, frame_shape='circle', centerpiece_enabled=True)

   print("Installation successful!")
