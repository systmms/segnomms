Installation
============

Requirements
------------

* Python 3.8 or higher
* Segno 1.5.2 or higher
* Pydantic 2.0 or higher

Install from PyPI
-----------------

The easiest way to install the Segno Interactive SVG Plugin is via pip:

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

For development, install with extra dependencies:

.. code-block:: bash

   git clone https://github.com/systmms/segnomms.git
   cd segnomms
   pip install -e ".[dev]"

This installs additional packages for testing and documentation:

* pytest and pytest-cov for testing
* black, isort, flake8, mypy for code quality
* pillow, lxml, beautifulsoup4 for testing utilities
* sphinx and sphinx-rtd-theme for documentation

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
   
   # Test Phase 4 features
   with open('test_phase4.svg', 'w') as f:
       write(qr, f, frame_shape='circle', centerpiece_enabled=True)

   print("Installation successful!")