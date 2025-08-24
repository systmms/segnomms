Shape Renderers
===============

This section documents all available shape renderers and the factory system.

Shape Factory
-------------

.. automodule:: segnomms.shapes.factory
   :members:
   :undoc-members:
   :show-inheritance:

Basic Shapes
------------

.. automodule:: segnomms.shapes.basic
   :members:
   :undoc-members:
   :show-inheritance:

Connected Shapes
----------------

.. automodule:: segnomms.shapes.connected
   :members:
   :undoc-members:
   :show-inheritance:

Shape Interface
---------------

All shape renderers implement the following interface:

.. autoclass:: segnomms.core.interfaces.ShapeRenderer
   :members:
   :undoc-members:
   :show-inheritance:

Creating Custom Shapes
----------------------

To create a custom shape, inherit from ``ShapeRenderer``::

    from segnomms.core.interfaces import ShapeRenderer
    import xml.etree.ElementTree as ET
    
    class MyCustomShape(ShapeRenderer):
        def render(self, x, y, size, **kwargs):
            # Create and return an SVG element
            return ET.Element('rect', {
                'x': str(x),
                'y': str(y),
                'width': str(size),
                'height': str(size),
                'rx': str(size * 0.3)
            })
        
        def supports_type(self, shape_type):
            return shape_type == 'my-custom'
    
    # Register the shape
    from segnomms import register_custom_renderer
    register_custom_renderer('my-custom', MyCustomShape)