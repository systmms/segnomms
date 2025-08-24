"""Shape rendering components for QR code modules.

This package provides a comprehensive shape rendering system for
creating visually appealing QR codes with various module shapes.

The package includes:

* **Basic shapes**: Square, circle, dot, diamond, star, triangle, hexagon, cross
* **Connected shapes**: Context-aware renderers that create fluid connections
* **Factory system**: Dynamic shape creation and registration
* **Shape management**: Functions for listing and checking available shapes

Key Components:

    Factory Functions:
        - :func:`get_shape_factory`: Get the singleton factory instance
        - :func:`create_shape_renderer`: Create a renderer for a shape type
        - :func:`register_custom_renderer`: Register custom shape renderers
        - :func:`list_available_shapes`: List all available shape types
        - :func:`is_shape_supported`: Check if a shape type is available

    Basic Renderers:
        - :class:`SquareRenderer`: Traditional square modules
        - :class:`CircleRenderer`: Circular modules
        - :class:`DotRenderer`: Small dot modules
        - :class:`DiamondRenderer`: 45-degree rotated squares
        - :class:`StarRenderer`: Multi-pointed star shapes
        - :class:`TriangleRenderer`: Triangular modules
        - :class:`HexagonRenderer`: Six-sided modules
        - :class:`CrossRenderer`: Cross-shaped modules

    Connected Renderers:
        - :class:`ConnectedRoundedRenderer`: Basic connected style
        - :class:`ConnectedExtraRoundedRenderer`: Extra smooth curves
        - :class:`AdvancedClassyRenderer`: Boundary-focused styling
        - :class:`AdvancedClassyRoundedRenderer`: Ultra-smooth boundaries

Example:
    Basic usage of the shape system::

        from segnomms import create_shape_renderer

        # Create a star renderer
        renderer = create_shape_renderer('star')

        # Render a module
        element = renderer.render(x=0, y=0, size=10)

        # List available shapes
        shapes = list_available_shapes()
        print(shapes)  # ['square', 'circle', 'star', ...]

See Also:
    - :mod:`segnomms.shapes.basic`: Basic shape implementations
    - :mod:`segnomms.shapes.connected`: Connected shape renderers
    - :mod:`segnomms.shapes.factory`: Factory system details
"""

from .basic import (
    CircleRenderer,
    CrossRenderer,
    DiamondRenderer,
    DotRenderer,
    HexagonRenderer,
    RoundedRenderer,
    SquareRenderer,
    StarRenderer,
    TriangleRenderer,
)
from .connected import (  # ConnectedClassyRenderer removed
    AdvancedClassyRenderer,
    AdvancedClassyRoundedRenderer,
    ConnectedExtraRoundedRenderer,
    ConnectedRoundedRenderer,
)
from .factory import (
    ShapeRendererFactory,
    create_shape_renderer,
    get_shape_factory,
    is_shape_supported,
    list_available_shapes,
    register_custom_renderer,
)

__all__ = [
    # Factory functions
    "ShapeRendererFactory",
    "get_shape_factory",
    "register_custom_renderer",
    "create_shape_renderer",
    "list_available_shapes",
    "is_shape_supported",
    # Basic renderers
    "SquareRenderer",
    "CircleRenderer",
    "RoundedRenderer",
    "DotRenderer",
    "DiamondRenderer",
    "StarRenderer",
    "TriangleRenderer",
    "HexagonRenderer",
    "CrossRenderer",
    # Connected renderers
    "ConnectedRoundedRenderer",
    "ConnectedExtraRoundedRenderer",
    # 'ConnectedClassyRenderer', removed
    "AdvancedClassyRenderer",
    "AdvancedClassyRoundedRenderer",
]
