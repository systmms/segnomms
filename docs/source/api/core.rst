Core Components
===============

This section documents the core components and interfaces of the plugin.

Interfaces
----------

.. automodule:: segnomms.core.interfaces
   :members:
   :undoc-members:
   :show-inheritance:

Module Detector
---------------

.. automodule:: segnomms.core.detector
   :members:
   :undoc-members:
   :show-inheritance:

The ``ModuleDetector`` class is responsible for identifying different types of QR code modules
(finder patterns, timing patterns, data modules, etc.) and providing context information
for shape renderers.

Example Usage
~~~~~~~~~~~~~

.. code-block:: python

   from segnomms.core.detector import ModuleDetector

   # Create detector with QR matrix
   detector = ModuleDetector(matrix, version=1)

   # Check module type
   module_type = detector.get_module_type(5, 5)

   # Get neighbor information
   def get_neighbor(dx, dy):
       return detector.is_module_active(x + dx, y + dy)

Matrix Manipulation
-------------------

.. automodule:: segnomms.core.matrix.manipulator
   :members:
   :undoc-members:
   :show-inheritance:

The ``MatrixManipulator`` provides utilities for QR matrix operations
including centerpiece area clearing and module manipulation.

Algorithms
----------

Connected Component Analyzer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: segnomms.algorithms.clustering
   :members:
   :undoc-members:
   :show-inheritance:

The clustering algorithm groups connected modules together for more efficient
rendering and better visual effects with connected shapes.

Phase 4 Core Components
-----------------------

Advanced QR Generation
~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: segnomms.core.advanced_qr
   :members:
   :undoc-members:
   :show-inheritance:

The advanced QR generation system provides enhanced features including
ECI character encoding, manual mask patterns, and structured append sequences.

Extending the Plugin
--------------------

Creating a Custom Shape Renderer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from segnomms.core.interfaces import ShapeRenderer
   import xml.etree.ElementTree as ET

   class CustomRenderer(ShapeRenderer):
       """My custom shape renderer."""

       def render(self, x: float, y: float, size: float, **kwargs) -> ET.Element:
           """Render the shape."""
           # Create your custom SVG element
           element = ET.Element('polygon', {
               'points': self._calculate_points(x, y, size),
               'class': kwargs.get('css_class', 'qr-module')
           })
           return element

       def supports_type(self, shape_type: str) -> bool:
           """Check if this renderer handles the shape type."""
           return shape_type == 'custom'

       def _calculate_points(self, x, y, size):
           # Custom logic here
           pass

Creating a Custom Algorithm
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from segnomms.core.interfaces import AlgorithmProcessor

   class CustomProcessor(AlgorithmProcessor):
       """Custom algorithm processor."""

       def process(self, matrix, config):
           """Process the QR matrix."""
           # Your algorithm logic
           results = self._analyze(matrix)
           return results

       def get_config_schema(self):
           """Return configuration schema."""
           return {
               'type': 'object',
               'properties': {
                   'threshold': {'type': 'number'}
               }
           }

Module Types
------------

The plugin recognizes these QR code module types:

* ``ModuleType.FINDER`` - Finder pattern modules
* ``ModuleType.SEPARATOR`` - Separator modules around finders
* ``ModuleType.TIMING`` - Timing pattern modules
* ``ModuleType.ALIGNMENT`` - Alignment pattern modules
* ``ModuleType.FORMAT`` - Format information modules
* ``ModuleType.VERSION`` - Version information modules
* ``ModuleType.DATA`` - Data and error correction modules
* ``ModuleType.DARK`` - Fixed dark module

Architecture Overview
---------------------

The plugin follows a modular architecture:

1. **Configuration Layer** - Validates and manages all settings
2. **Detection Layer** - Identifies module types and relationships
3. **Algorithm Layer** - Processes modules (clustering, optimization)
4. **Rendering Layer** - Generates SVG elements for each module
5. **Assembly Layer** - Combines elements into final SVG

This separation allows for easy extension and modification of individual components
without affecting the rest of the system.
