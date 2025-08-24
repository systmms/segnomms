"""Core interfaces for the segno interactive SVG plugin.

This module defines the abstract base classes and interfaces that all
components must implement to ensure consistency and extensibility.

The interfaces provide contracts for:

* Shape rendering (ShapeRenderer)
* Module analysis (ModuleAnalyzer)
* Algorithm processing (AlgorithmProcessor)
* Configuration management (ConfigurationProvider)
* Factory patterns (RendererFactory)
* SVG building (SVGBuilder)
* QR code analysis (QRCodeAnalyzer)

All custom implementations should inherit from these base classes.
"""

import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple


class ModuleAnalyzer(ABC):
    """Interface for module analysis algorithms.

    Implementations analyze QR code matrices to extract information
    about module patterns, relationships, and properties.
    """

    @abstractmethod
    def analyze(self, matrix: List[List[bool]], detector: Any) -> Any:
        """
        Analyze the QR code matrix and return analysis results.

        Args:
            matrix: 2D boolean matrix representing QR code modules
            detector: Module detector for determining module types

        Returns:
            Analysis results specific to the analyzer implementation
        """


class ShapeRenderer(ABC):
    """Interface for shape rendering implementations.

    All shape renderers must implement this interface to ensure
    compatibility with the rendering pipeline.

    Implementations should:

    1. Create SVG elements for individual modules
    2. Support configuration through kwargs
    3. Declare which shape types they handle
    """

    @abstractmethod
    def render(self, x: float, y: float, size: float, **kwargs) -> ET.Element:
        """
        Render a shape at the specified position.

        Args:
            x: X coordinate
            y: Y coordinate
            size: Size of the shape
            **kwargs: Additional rendering parameters

        Returns:
            SVG element representing the rendered shape
        """

    @abstractmethod
    def supports_type(self, shape_type: str) -> bool:
        """
        Check if this renderer supports the given shape type.

        Args:
            shape_type: Name of the shape type

        Returns:
            True if this renderer can handle the shape type
        """


class AlgorithmProcessor(ABC):
    """Interface for algorithm-based processors.

    Processors implement algorithms like clustering, contour detection,
    or other matrix transformations.
    """

    @abstractmethod
    def process(
        self, matrix: List[List[bool]], detector: Any, **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Process the QR matrix using the specific algorithm.

        Args:
            matrix: 2D boolean matrix representing QR code modules
            detector: Module detector for determining module types
            **kwargs: Algorithm-specific parameters

        Returns:
            List of processing results (clusters, contours, etc.)
        """


class ConfigurationProvider(ABC):
    """Interface for configuration providers.

    Components that require configuration should implement this
    interface to provide default values and validation.
    """

    @abstractmethod
    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration for this component.

        Returns:
            Dict[str, Any]: Default configuration values
        """

    @abstractmethod
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate a configuration dictionary.

        Args:
            config: Configuration to validate

        Returns:
            bool: True if configuration is valid

        Raises:
            ValueError: If configuration is invalid with details
        """


class RendererFactory(ABC):
    """Interface for renderer factories.

    Factories manage the creation and registration of shape renderers.
    """

    @abstractmethod
    def create_renderer(self, shape_type: str, config: Dict[str, Any]) -> ShapeRenderer:
        """
        Create a renderer for the specified shape type.

        Args:
            shape_type: Type of shape to render
            config: Configuration parameters

        Returns:
            Appropriate shape renderer
        """

    @abstractmethod
    def list_supported_types(self) -> List[str]:
        """List all shape types supported by this factory.

        Returns:
            List[str]: Supported shape type names
        """


class SVGBuilder(ABC):
    """Interface for SVG document builders.

    Builders handle the construction of complete SVG documents
    with proper structure, styles, and metadata.
    """

    @abstractmethod
    def create_svg_root(self, width: int, height: int, **kwargs) -> ET.Element:
        """Create the root SVG element.

        Args:
            width: SVG width in pixels
            height: SVG height in pixels
            **kwargs: Additional SVG attributes

        Returns:
            ET.Element: Root SVG element
        """

    @abstractmethod
    def add_styles(self, svg: ET.Element, interactive: bool = False) -> None:
        """Add CSS styles to the SVG.

        Args:
            svg: SVG root element
            interactive: Whether to include interactive styles
        """

    @abstractmethod
    def add_background(
        self, svg: ET.Element, width: int, height: int, color: str
    ) -> None:
        """Add background to the SVG.

        Args:
            svg: SVG root element
            width: Background width
            height: Background height
            color: Background color (CSS color string)
        """


class QRCodeAnalyzer(ABC):
    """Interface for QR code analyzers.

    Analyzers determine module types (finder, timing, data, etc.)
    and extract QR code properties.
    """

    @abstractmethod
    def get_module_type(self, row: int, col: int) -> str:
        """Get the type of module at the specified position.

        Args:
            row: Row index
            col: Column index

        Returns:
            str: Module type identifier
        """

    @abstractmethod
    def get_version(self) -> int:
        """Get the QR code version.

        Returns:
            int: QR code version (1-40)
        """

    @abstractmethod
    def get_size(self) -> int:
        """Get the size of the QR code matrix.

        Returns:
            int: Number of modules per side
        """


#: Type alias for QR code matrix (2D list of booleans)
Matrix = List[List[bool]]

#: Type alias for module position (row, col)
Position = Tuple[int, int]

#: Type alias for bounding box (min_row, min_col, max_row, max_col)
BoundingBox = Tuple[int, int, int, int]

#: Type alias for RGB color (red, green, blue)
RGBColor = Tuple[int, int, int]

#: Type alias for 2D point (x, y)
Point2D = Tuple[float, float]
