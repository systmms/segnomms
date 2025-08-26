"""Shape renderer factory for managing and creating shape renderers.

This module provides a centralized factory for creating shape renderers
and managing the registry of available shapes.

The factory pattern allows:

* Dynamic registration of new shape renderers
* Centralized management of shape types
* Easy extension with custom shapes
* Consistent renderer instantiation

Example:
    Using the factory to create renderers::

        factory = get_shape_factory()
        renderer = factory.create_renderer('star', {})
        element = renderer.render(0, 0, 10)

    Registering a custom renderer::

        register_custom_renderer('my-shape', MyShapeRenderer)

"""

from typing import Any, Dict, List, Optional, Type

from ..core.interfaces import RendererFactory, ShapeRenderer
from .basic import (
    CircleRenderer,
    CrossRenderer,
    DiamondRenderer,
    DotRenderer,
    HexagonRenderer,
    RoundedRenderer,
    SquareRenderer,
    SquircleRenderer,
    StarRenderer,
    TriangleRenderer,
)
from .connected import (  # ConnectedClassyRenderer removed
    AdvancedClassyRenderer,
    AdvancedClassyRoundedRenderer,
    ConnectedExtraRoundedRenderer,
    ConnectedRoundedRenderer,
)


class ShapeRendererFactory(RendererFactory):
    """Factory for creating and managing shape renderers.

    This factory maintains a registry of available shape renderers
    and provides methods to create appropriate renderers based on
    shape type names.

    Attributes:
        _renderers: Internal registry mapping shape names to renderer classes
    """

    def __init__(self) -> None:
        self._renderers: Dict[str, Type[ShapeRenderer]] = {}
        self._register_default_renderers()

    def _normalize_shape_type(self, shape_type: Any) -> str:
        """Normalize shape type to lowercase string, handling both enums and strings.

        Args:
            shape_type: Shape type as string or enum

        Returns:
            str: Normalized lowercase shape type string
        """
        if hasattr(shape_type, "value"):
            # It's an enum, get the string value
            return str(shape_type.value).lower()
        else:
            # It's already a string
            return str(shape_type).lower()

    def _register_default_renderers(self) -> None:
        """Register all default shape renderers.

        This method is called during initialization to register
        all built-in shape renderers with the factory.
        """
        renderers: List[Type[ShapeRenderer]] = [
            SquareRenderer,
            CircleRenderer,
            RoundedRenderer,
            DotRenderer,
            DiamondRenderer,
            SquircleRenderer,
            StarRenderer,
            TriangleRenderer,
            HexagonRenderer,
            CrossRenderer,
            ConnectedRoundedRenderer,
            ConnectedExtraRoundedRenderer,
            # ConnectedClassyRenderer removed
            AdvancedClassyRenderer,
            AdvancedClassyRoundedRenderer,
        ]

        for renderer_class in renderers:
            # Create instance only for introspection
            try:
                renderer_instance = renderer_class()
                for shape_type in self._get_supported_types(renderer_instance):
                    self._renderers[shape_type] = renderer_class
            except TypeError:
                # Skip if cannot instantiate
                pass

    def _get_supported_types(self, renderer: ShapeRenderer) -> List[str]:
        """Get all shape types supported by a renderer.

        Args:
            renderer: Shape renderer instance to query

        Returns:
            List[str]: List of supported shape type names

        Note:
            This method tests common shape names against the renderer's
            supports_type() method to build a list of supported types.
        """
        # Test common shape names to find supported types
        common_shapes = [
            "square",
            "circle",
            "rounded",
            "dot",
            "diamond",
            "star",
            "triangle",
            "hexagon",
            "cross",
            "squircle",
            "connected",
            "connected-extra-rounded",
            "connected-classy",
            "connected-classy-rounded",
        ]

        supported = []
        for shape_type in common_shapes:
            if renderer.supports_type(shape_type):
                supported.append(shape_type)

        return supported

    def register_renderer(self, shape_type: str, renderer_class: Type[ShapeRenderer]) -> None:
        """Register a custom shape renderer.

        Args:
            shape_type: Name of the shape type
            renderer_class: Renderer class to register

        Example:
            >>> factory.register_renderer('my-shape', MyShapeRenderer)
        """
        self._renderers[self._normalize_shape_type(shape_type)] = renderer_class

    def create_renderer(self, shape_type: str, config: Dict[str, Any]) -> ShapeRenderer:
        """Create a renderer for the specified shape type.

        Args:
            shape_type: Type of shape to render
            config: Configuration parameters (currently unused)

        Returns:
            ShapeRenderer: Instance of appropriate renderer

        Note:
            Falls back to 'square' renderer if shape type is not found,
            but logs a warning with available options.
        """
        import logging

        logger = logging.getLogger(__name__)

        shape_type_lower = self._normalize_shape_type(shape_type)

        if shape_type_lower not in self._renderers:
            available_shapes = sorted(self._renderers.keys())
            logger.warning(
                f"Unknown shape type '{shape_type}'. Available shapes are: "
                f"{', '.join(available_shapes)}. Using 'square' as fallback."
            )
            # Default to square renderer if shape type not found
            shape_type_lower = "square"

        renderer_class = self._renderers[shape_type_lower]
        return renderer_class()

    def list_supported_types(self) -> List[str]:
        """List all shape types supported by this factory.

        Returns:
            List[str]: List of all registered shape type names
        """
        return list(self._renderers.keys())

    def is_supported(self, shape_type: str) -> bool:
        """Check if a shape type is supported.

        Args:
            shape_type: Shape type name to check

        Returns:
            bool: True if shape type is registered
        """
        return self._normalize_shape_type(shape_type) in self._renderers

    def get_renderer_info(self, shape_type: str) -> Dict[str, Any]:
        """Get information about a specific renderer.

        Args:
            shape_type: Shape type to query

        Returns:
            Dict[str, Any]: Information including class name, supported types, and module  # noqa: E501
        """
        shape_type_lower = self._normalize_shape_type(shape_type)
        if shape_type_lower not in self._renderers:
            return {}

        renderer_class = self._renderers[shape_type_lower]
        renderer_instance = renderer_class()

        return {
            "class_name": renderer_class.__name__,
            "supported_types": self._get_supported_types(renderer_instance),
            "module": renderer_class.__module__,  # noqa: E501
        }

    def get_all_renderer_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all registered renderers.

        Returns:
            Dict[str, Dict[str, Any]]: Mapping of renderer class names to their info
        """
        info = {}
        seen_classes = set()

        for shape_type, renderer_class in self._renderers.items():
            if renderer_class not in seen_classes:
                info[renderer_class.__name__] = self.get_renderer_info(shape_type)
                seen_classes.add(renderer_class)

        return info


#: Global factory instance (singleton)
_shape_factory = None


def get_shape_factory() -> ShapeRendererFactory:
    """Get the global shape factory instance.

    Returns:
        ShapeRendererFactory: Singleton factory instance

    Note:
        This function ensures only one factory instance exists globally.
    """
    global _shape_factory
    if _shape_factory is None:
        _shape_factory = ShapeRendererFactory()
    return _shape_factory


def register_custom_renderer(shape_type: str, renderer_class: Type[ShapeRenderer]) -> None:
    """Register a custom shape renderer with the global factory.

    Args:
        shape_type: Name of the shape type
        renderer_class: Renderer class to register

    Example:
        >>> from segnomms import register_custom_renderer
        >>> register_custom_renderer('my-shape', MyShapeRenderer)
    """
    factory = get_shape_factory()
    factory.register_renderer(shape_type, renderer_class)


def create_shape_renderer(shape_type: str, config: Optional[Dict[str, Any]] = None) -> ShapeRenderer:
    """Create a shape renderer using the global factory.

    Args:
        shape_type: Type of shape to render
        config: Optional configuration parameters

    Returns:
        ShapeRenderer: Instance of appropriate renderer

    Example:
        >>> renderer = create_shape_renderer('star')
        >>> element = renderer.render(0, 0, 10)
    """
    if config is None:
        config = {}

    factory = get_shape_factory()
    return factory.create_renderer(shape_type, config)


def list_available_shapes() -> List[str]:
    """List all available shape types.

    Returns:
        List[str]: List of all registered shape type names

    Example:
        >>> shapes = list_available_shapes()
        >>> print(shapes)
        ['square', 'circle', 'dot', 'diamond', ...]
    """
    factory = get_shape_factory()
    return factory.list_supported_types()


def is_shape_supported(shape_type: str) -> bool:
    """Check if a shape type is supported.

    Args:
        shape_type: Shape type name to check

    Returns:
        bool: True if shape type is available

    Example:
        >>> is_shape_supported('star')
        True
        >>> is_shape_supported('invalid')
        False
    """
    factory = get_shape_factory()
    return factory.is_supported(shape_type)
