"""Basic shape renderers for QR code modules.

This module provides simple geometric shape renderers that don't depend on
neighboring modules. Each renderer creates a single SVG element for each
QR code module.

Available shapes:
    * SquareRenderer: Traditional square modules
    * CircleRenderer: Circular modules
    * DotRenderer: Small circular dots
    * DiamondRenderer: Diamond/rhombus shapes
    * StarRenderer: Configurable star shapes
    * TriangleRenderer: Directional triangles
    * HexagonRenderer: Six-sided polygons
    * CrossRenderer: Plus/cross shapes

"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Tuple, Union

from ..core.interfaces import ShapeRenderer


class BaseShapeRenderer(ShapeRenderer):
    """Abstract base class for basic shape renderers with common functionality.

    Provides standardized implementations of common methods like supports_type()
    and shared constants. Subclasses should define shape_names to specify
    which shape types they support.
    """

    # Subclasses should override this with their supported shape names
    shape_names: List[str] = []

    def supports_type(self, shape_type: str) -> bool:
        """Check if this renderer supports the given shape type.

        Args:
            shape_type: Name of the shape type to check

        Returns:
            bool: True if shape_type is in the renderer's shape_names list
        """
        return shape_type.lower() in self.shape_names


def apply_element_attributes(element: ET.Element, kwargs: Union[Dict[str, Any], Any]) -> None:
    """Apply common attributes to an SVG element.

    This helper function applies standard attributes like id, data-* attributes,
    and other interactive properties to SVG elements.

    Args:
        element: SVG element to modify
        kwargs: Dictionary of attributes, may include:
            - id: Element ID
            - data-row: Row position data attribute
            - data-col: Column position data attribute
            - data-type: Module type data attribute
            - Any other attribute to be applied
    """
    # Apply common attributes
    if "id" in kwargs:
        element.set("id", kwargs["id"])

    # Apply data attributes for interactivity
    for key, value in kwargs.items():
        if key.startswith("data-"):
            element.set(key, str(value))


def create_svg_element(
    tag: str, attributes: Dict[str, Any], kwargs: Union[Dict[str, Any], Any]
) -> ET.Element:
    """Create an SVG element with common attributes applied.

    This helper function combines element creation with common attribute
    application, reducing boilerplate code across all renderers.

    Args:
        tag: SVG element tag name (e.g., 'rect', 'circle', 'polygon')
        attributes: Dictionary of SVG-specific attributes
        kwargs: Additional parameters including css_class, id, data-* attributes

    Returns:
        ET.Element: SVG element with all attributes applied
    """
    # Ensure css_class is always set to default if not provided
    attributes.setdefault("class", kwargs.get("css_class", "qr-module"))

    # Convert all attribute values to strings for XML
    str_attributes = {k: str(v) for k, v in attributes.items()}

    # Create element and apply additional attributes
    element = ET.Element(tag, str_attributes)
    apply_element_attributes(element, kwargs)

    return element


# Geometry utility functions
def get_module_center(x: float, y: float, size: float) -> Tuple[float, float]:
    """Calculate the center point of a module.

    Args:
        x: Module's top-left x coordinate
        y: Module's top-left y coordinate
        size: Module size

    Returns:
        tuple[float, float]: Center coordinates (cx, cy)
    """
    return x + size / 2, y + size / 2


def apply_size_ratio(size: float, kwargs: Union[Dict[str, Any], Any], default: float = 1.0) -> float:
    """Apply size ratio from kwargs to a base size.

    Args:
        size: Base size value
        kwargs: Parameters dictionary that may contain 'size_ratio'
        default: Default ratio if not specified in kwargs

    Returns:
        float: Size multiplied by the ratio
    """
    ratio = kwargs.get("size_ratio", default)
    return size * float(ratio)


def get_corner_radius(
    size: float,
    kwargs: Union[Dict[str, Any], Any],
    param_name: str = "roundness",
    default: float = 0.3,
) -> float:
    """Calculate corner radius from size and roundness parameter.

    Args:
        size: Base size value
        kwargs: Parameters dictionary
        param_name: Name of the parameter to look for (default: 'roundness')
        default: Default roundness ratio if not specified

    Returns:
        float: Corner radius value
    """
    ratio = kwargs.get(param_name, default)
    return size * float(ratio)


# Polygon generation utilities
def generate_regular_polygon(
    center_x: float,
    center_y: float,
    radius: float,
    sides: int,
    start_angle: float = 0.0,
) -> list[str]:
    """Generate points for a regular polygon.

    Args:
        center_x: X coordinate of polygon center
        center_y: Y coordinate of polygon center
        radius: Distance from center to vertices
        sides: Number of polygon sides (must be >= 3)
        start_angle: Starting angle in radians (default: 0.0)

    Returns:
        list[str]: List of point strings in "x,y" format for SVG polygon

    Raises:
        ValueError: If sides < 3
    """
    if sides < 3:
        raise ValueError("Polygon must have at least 3 sides")

    import math

    points = []
    angle_step = 2 * math.pi / sides

    for i in range(sides):
        angle = start_angle + i * angle_step
        px = center_x + radius * math.cos(angle)
        py = center_y + radius * math.sin(angle)
        points.append(f"{px:.2f},{py:.2f}")

    return points


def generate_star_polygon(
    center_x: float,
    center_y: float,
    outer_radius: float,
    inner_radius: float,
    points: int,
    start_angle: float = -3.141592653589793 / 2,
) -> list[str]:
    """Generate points for a star polygon.

    Args:
        center_x: X coordinate of star center
        center_y: Y coordinate of star center
        outer_radius: Distance from center to outer points
        inner_radius: Distance from center to inner points
        points: Number of star points (must be >= 3)
        start_angle: Starting angle in radians (default: -π/2 for upward point)

    Returns:
        list[str]: List of point strings in "x,y" format for SVG polygon

    Raises:
        ValueError: If points < 3
    """
    if points < 3:
        raise ValueError("Star must have at least 3 points")

    import math

    star_points = []
    angle_step = math.pi / points  # Half the angle between outer points

    for i in range(points * 2):
        angle = start_angle + i * angle_step
        if i % 2 == 0:
            # Outer point
            px = center_x + outer_radius * math.cos(angle)
            py = center_y + outer_radius * math.sin(angle)
        else:
            # Inner point
            px = center_x + inner_radius * math.cos(angle)
            py = center_y + inner_radius * math.sin(angle)
        star_points.append(f"{px:.2f},{py:.2f}")

    return star_points


def generate_diamond_points(x: float, y: float, size: float) -> list[str]:
    """Generate points for a diamond (rotated square) shape.

    Args:
        x: Top-left x coordinate of bounding box
        y: Top-left y coordinate of bounding box
        size: Size of the bounding box

    Returns:
        list[str]: List of point strings for diamond polygon
    """
    half = size / 2
    return [
        f"{x + half},{y}",  # Top
        f"{x + size},{y + half}",  # Right
        f"{x + half},{y + size}",  # Bottom
        f"{x},{y + half}",  # Left
    ]


def generate_triangle_points(x: float, y: float, size: float, direction: str = "up") -> list[str]:
    """Generate points for a triangle in the specified direction.

    Args:
        x: Top-left x coordinate of bounding box
        y: Top-left y coordinate of bounding box
        size: Size of the bounding box
        direction: Triangle direction ('up', 'down', 'left', 'right')

    Returns:
        list[str]: List of point strings for triangle polygon

    Raises:
        ValueError: If direction is not valid
    """
    direction = direction.lower()

    if direction == "up":
        return [
            f"{x + size / 2},{y}",
            f"{x + size},{y + size}",
            f"{x},{y + size}",
        ]
    elif direction == "down":
        return [
            f"{x},{y}",
            f"{x + size},{y}",
            f"{x + size / 2},{y + size}",
        ]
    elif direction == "left":
        return [
            f"{x},{y + size / 2}",
            f"{x + size},{y}",
            f"{x + size},{y + size}",
        ]
    elif direction == "right":
        return [
            f"{x},{y}",
            f"{x},{y + size}",
            f"{x + size},{y + size / 2}",
        ]
    else:
        raise ValueError(f"Invalid direction '{direction}'. Must be 'up', 'down', 'left', or 'right'")


class SquareRenderer(BaseShapeRenderer):
    """Renders traditional square QR code modules.

    The most basic shape renderer, creating perfect squares for each module.
    This is the default shape for QR codes and provides maximum reliability
    for scanning while maintaining the classic QR code appearance.

    Example:
        >>> renderer = SquareRenderer()
        >>> square = renderer.render(0, 0, 10)
        >>> # Creates a 10x10 square at position (0,0)
    """

    shape_names = ["square"]

    def render(self, x: float, y: float, size: float, **kwargs: Any) -> ET.Element:
        """Render a square module.

        Args:
            x: X coordinate of the top-left corner
            y: Y coordinate of the top-left corner
            size: Width and height of the square
            **kwargs: Additional parameters including:
                css_class: CSS class for styling (default: 'qr-module')
                id: Optional element ID

        Returns:
            ET.Element: SVG rect element
        """
        return create_svg_element(
            "rect",
            {
                "x": x,
                "y": y,
                "width": size,
                "height": size,
            },
            kwargs,
        )


class CircleRenderer(BaseShapeRenderer):
    """Renders circular QR code modules.

    Creates perfect circles that fit within the module grid. This shape
    provides a softer, more organic appearance while maintaining good
    scannability due to the consistent module centers.

    Example:
        >>> renderer = CircleRenderer()
        >>> circle = renderer.render(5, 5, 10)
        >>> # Creates a circle with radius 5 centered at (10,10)
    """

    shape_names = ["circle"]

    def render(self, x: float, y: float, size: float, **kwargs: Any) -> ET.Element:
        """Render a circular module.

        Args:
            x: X coordinate of the module's top-left corner
            y: Y coordinate of the module's top-left corner
            size: Module size (circle diameter)
            **kwargs: Additional parameters including:
                css_class: CSS class for styling (default: 'qr-module')
                id: Optional element ID

        Returns:
            ET.Element: SVG circle element centered in the module
        """
        cx, cy = get_module_center(x, y, size)
        radius = apply_size_ratio(size / 2, kwargs, 0.9)

        return create_svg_element("circle", {"cx": cx, "cy": cy, "r": radius}, kwargs)


class RoundedRenderer(BaseShapeRenderer):
    """Renders square modules with rounded corners.

    Creates modules with softly rounded corners for a more friendly,
    modern appearance. The corner radius can be controlled via the
    roundness parameter.

    Example:
        >>> renderer = RoundedRenderer()
        >>> rounded_rect = renderer.render(0, 0, 10, roundness=0.3)
        >>> # Creates a square with 30% corner radius
    """

    shape_names = ["rounded"]

    def render(self, x: float, y: float, size: float, **kwargs: Any) -> ET.Element:
        """Render a rounded square module.

        Args:
            x: X coordinate of the module's top-left corner
            y: Y coordinate of the module's top-left corner
            size: Module size
            **kwargs: Additional parameters including:
                roundness: Corner radius as fraction of size (default: 0.3)
                css_class: CSS class for styling (default: 'qr-module')
                id: Optional element ID

        Returns:
            ET.Element: SVG rect element with rounded corners
        """
        radius = get_corner_radius(size, kwargs)

        return create_svg_element(
            "rect",
            {
                "x": x,
                "y": y,
                "width": size,
                "height": size,
                "rx": radius,
                "ry": radius,
            },
            kwargs,
        )


class DotRenderer(BaseShapeRenderer):
    """Renders small dot modules for a minimalist QR code style.

    Creates smaller circles that leave more whitespace between modules,
    resulting in a lighter, more delicate appearance. The dot size can
    be controlled via the size_ratio parameter.

    Example:
        >>> renderer = DotRenderer()
        >>> dot = renderer.render(0, 0, 10, size_ratio=0.5)
        >>> # Creates a 5-pixel diameter dot in a 10x10 module
    """

    shape_names = ["dot"]

    def render(self, x: float, y: float, size: float, **kwargs: Any) -> ET.Element:
        """Render a small dot module.

        Args:
            x: X coordinate of the module's top-left corner
            y: Y coordinate of the module's top-left corner
            size: Module size
            **kwargs: Additional parameters including:
                size_ratio: Dot size relative to module (default: 0.6)
                css_class: CSS class for styling (default: 'qr-module')
                id: Optional element ID

        Returns:
            ET.Element: SVG circle element smaller than the module size
        """
        cx, cy = get_module_center(x, y, size)
        dot_size = apply_size_ratio(size, kwargs, 0.6)

        return create_svg_element("circle", {"cx": cx, "cy": cy, "r": dot_size / 2}, kwargs)


class DiamondRenderer(BaseShapeRenderer):
    """Renders diamond (rhombus) shaped modules.

    Creates 45-degree rotated squares that form diamond patterns.
    This shape adds a geometric, crystalline quality to QR codes
    while maintaining good contrast for scanning.

    Example:
        >>> renderer = DiamondRenderer()
        >>> diamond = renderer.render(0, 0, 10)
        >>> # Creates a diamond touching all edges of the 10x10 module
    """

    shape_names = ["diamond"]

    def render(self, x: float, y: float, size: float, **kwargs: Any) -> ET.Element:
        """Render a diamond shape module.

        Args:
            x: X coordinate of the module's top-left corner
            y: Y coordinate of the module's top-left corner
            size: Module size
            **kwargs: Additional parameters including:
                css_class: CSS class for styling (default: 'qr-module')
                id: Optional element ID

        Returns:
            ET.Element: SVG polygon element forming a diamond
        """
        points = generate_diamond_points(x, y, size)
        return create_svg_element("polygon", {"points": " ".join(points)}, kwargs)


class StarRenderer(BaseShapeRenderer):
    """Renders star-shaped modules with configurable points.

    Creates multi-pointed star shapes that add a decorative flair to QR codes.
    The number of points and the inner/outer radius ratio can be customized
    to create different star styles from sharp to more rounded.

    Example:
        >>> renderer = StarRenderer()
        >>> star = renderer.render(0, 0, 10, star_points=6, inner_ratio=0.4)
        >>> # Creates a 6-pointed star with sharp points
    """

    shape_names = ["star"]

    def render(self, x: float, y: float, size: float, **kwargs: Any) -> ET.Element:
        """Render a star shape module.

        Args:
            x: X coordinate of the module's top-left corner
            y: Y coordinate of the module's top-left corner
            size: Module size
            **kwargs: Additional parameters including:
                star_points: Number of star points (default: 5)
                inner_ratio: Inner radius ratio 0-1 (default: 0.5)
                css_class: CSS class for styling (default: 'qr-module')
                id: Optional element ID

        Returns:
            ET.Element: SVG polygon element forming a star
        """
        points = kwargs.get("star_points", 5)
        inner_ratio = kwargs.get("inner_ratio", 0.5)
        center_x, center_y = get_module_center(x, y, size)
        outer_radius = size / 2
        inner_radius = outer_radius * inner_ratio

        star_points = generate_star_polygon(center_x, center_y, outer_radius, inner_radius, points)

        return create_svg_element("polygon", {"points": " ".join(star_points)}, kwargs)


class TriangleRenderer(BaseShapeRenderer):
    """Renders triangular modules with directional orientation.

    Creates equilateral triangles that can point in different directions.
    This shape adds a dynamic, directional quality to QR codes and can
    create interesting patterns when modules align.

    Example:
        >>> renderer = TriangleRenderer()
        >>> triangle = renderer.render(0, 0, 10, direction='up')
        >>> # Creates an upward-pointing triangle
    """

    shape_names = ["triangle"]

    def render(self, x: float, y: float, size: float, **kwargs: Any) -> ET.Element:
        """Render a triangle shape module.

        Args:
            x: X coordinate of the module's top-left corner
            y: Y coordinate of the module's top-left corner
            size: Module size
            **kwargs: Additional parameters including:
                direction: Triangle direction ('up', 'down', 'left', 'right')
                css_class: CSS class for styling (default: 'qr-module')
                id: Optional element ID

        Returns:
            ET.Element: SVG polygon element forming a triangle
        """
        direction = kwargs.get("direction", "up")
        points = generate_triangle_points(x, y, size, direction)

        return create_svg_element("polygon", {"points": " ".join(points)}, kwargs)


class HexagonRenderer(BaseShapeRenderer):
    """Renders hexagonal modules for a honeycomb-like appearance.

    Creates regular hexagons that can tessellate beautifully when
    adjacent modules are also hexagons. This shape provides an
    organic, nature-inspired look to QR codes.

    Example:
        >>> renderer = HexagonRenderer()
        >>> hexagon = renderer.render(0, 0, 10, size_ratio=0.95)
        >>> # Creates a hexagon slightly smaller than the module
    """

    shape_names = ["hexagon"]

    def render(self, x: float, y: float, size: float, **kwargs: Any) -> ET.Element:
        """Render a hexagon shape module.

        Args:
            x: X coordinate of the module's top-left corner
            y: Y coordinate of the module's top-left corner
            size: Module size
            **kwargs: Additional parameters including:
                size_ratio: Hexagon size relative to module (default: 0.9)
                css_class: CSS class for styling (default: 'qr-module')
                id: Optional element ID

        Returns:
            ET.Element: SVG polygon element forming a regular hexagon
        """
        center_x, center_y = get_module_center(x, y, size)
        radius = apply_size_ratio(size / 2, kwargs, 0.9)

        hex_points = generate_regular_polygon(center_x, center_y, radius, 6)

        return create_svg_element("polygon", {"points": " ".join(hex_points)}, kwargs)


class CrossRenderer(BaseShapeRenderer):
    """Renders cross (plus sign) shaped modules.

    Creates cross or plus sign shapes that can vary in thickness
    and style. Supports both uniform width crosses and tapered
    crosses for a sharper appearance. This shape adds a technical,
    precise feel to QR codes.

    Example:
        >>> renderer = CrossRenderer()
        >>> cross = renderer.render(0, 0, 10, thickness=0.25, sharp=True)
        >>> # Creates a sharp cross with tapered arms
    """

    shape_names = ["cross"]

    def render(self, x: float, y: float, size: float, **kwargs: Any) -> ET.Element:
        """Render a cross shape module.

        Args:
            x: X coordinate of the module's top-left corner
            y: Y coordinate of the module's top-left corner
            size: Module size
            **kwargs: Additional parameters including:
                thickness: Cross arm thickness ratio (default: 0.2)
                sharp: Use tapered arms for sharper look (default: False)
                css_class: CSS class for styling (default: 'qr-module')
                id: Optional element ID

        Returns:
            ET.Element: SVG path element forming a cross
        """
        # Default to thinner cross for sharper appearance
        thickness = kwargs.get("thickness", 0.2)  # Reduced from 0.3 to 0.2
        arm_width = size * thickness

        # Debug: Add thickness info as data attribute
        debug_thickness = thickness

        # Create cross using path
        center_x, center_y = get_module_center(x, y, size)
        half_arm = arm_width / 2

        # For extra sharp crosses, we can make the arms taper
        sharp_mode = kwargs.get("sharp", False)

        if sharp_mode:
            # Create a cross with tapered arms for a sharper look
            taper = 0.7  # Arms are 70% width at the tips
            tip_half = half_arm * taper

            path_data = (
                # Top arm with taper
                f"M {center_x - tip_half} {y} "
                f"L {center_x + tip_half} {y} "
                f"L {center_x + half_arm} {center_y - half_arm} "
                # Right arm with taper
                f"L {x + size} {center_y - tip_half} "
                f"L {x + size} {center_y + tip_half} "
                f"L {center_x + half_arm} {center_y + half_arm} "
                # Bottom arm with taper
                f"L {center_x + tip_half} {y + size} "
                f"L {center_x - tip_half} {y + size} "
                f"L {center_x - half_arm} {center_y + half_arm} "
                # Left arm with taper
                f"L {x} {center_y + tip_half} "
                f"L {x} {center_y - tip_half} "
                f"L {center_x - half_arm} {center_y - half_arm} "
                f"Z"
            )
        else:
            # Standard cross with uniform width
            path_data = (
                f"M {center_x - half_arm} {y} "
                f"L {center_x + half_arm} {y} "
                f"L {center_x + half_arm} {center_y - half_arm} "
                f"L {x + size} {center_y - half_arm} "
                f"L {x + size} {center_y + half_arm} "
                f"L {center_x + half_arm} {center_y + half_arm} "
                f"L {center_x + half_arm} {y + size} "
                f"L {center_x - half_arm} {y + size} "
                f"L {center_x - half_arm} {center_y + half_arm} "
                f"L {x} {center_y + half_arm} "
                f"L {x} {center_y - half_arm} "
                f"L {center_x - half_arm} {center_y - half_arm} "
                f"Z"
            )

        return create_svg_element(
            "path",
            {
                "d": path_data,
                "data-thickness": debug_thickness,
                "data-arm-width": arm_width,
            },
            kwargs,
        )


class SquircleRenderer(BaseShapeRenderer):
    """Renders superellipse (squircle) shaped QR code modules.

    A squircle is a mathematical shape that's between a square and a circle,
    providing a modern, smooth appearance while maintaining good scannability.
    The shape is defined by the superellipse equation with n=4.

    Example:
        >>> renderer = SquircleRenderer()
        >>> squircle = renderer.render(0, 0, 10)
        >>> # Creates a 10x10 squircle at position (0,0)
    """

    shape_names = ["squircle"]

    def render(self, x: float, y: float, size: float, **kwargs: Any) -> ET.Element:
        """Render a squircle module.

        Args:
            x: X coordinate of the top-left corner
            y: Y coordinate of the top-left corner
            size: Width and height of the module
            **kwargs: Additional parameters including:
                css_class: CSS class for styling (default: 'qr-module')
                id: Optional element ID
                corner_radius: Override corner radius (0.0-1.0)

        Returns:
            ET.Element: SVG path element forming a squircle
        """
        # Get corner radius from kwargs or use default
        corner_radius = get_corner_radius(1.0, kwargs, "corner_radius", 0.35)

        # Calculate control point offset for cubic bezier curves
        # This approximates a superellipse with n=4
        cp_offset = size * corner_radius * 0.447  # Magic number for squircle

        # Create path data for squircle using cubic bezier curves
        path_data = (
            f"M {x + size * corner_radius} {y} "
            f"L {x + size - size * corner_radius} {y} "
            f"C {x + size - size * corner_radius + cp_offset} {y} "
            f"{x + size} {y + size * corner_radius - cp_offset} "
            f"{x + size} {y + size * corner_radius} "
            f"L {x + size} {y + size - size * corner_radius} "
            f"C {x + size} {y + size - size * corner_radius + cp_offset} "
            f"{x + size - size * corner_radius + cp_offset} {y + size} "
            f"{x + size - size * corner_radius} {y + size} "
            f"L {x + size * corner_radius} {y + size} "
            f"C {x + size * corner_radius - cp_offset} {y + size} "
            f"{x} {y + size - size * corner_radius + cp_offset} "
            f"{x} {y + size - size * corner_radius} "
            f"L {x} {y + size * corner_radius} "
            f"C {x} {y + size * corner_radius - cp_offset} "
            f"{x + size * corner_radius - cp_offset} {y} "
            f"{x + size * corner_radius} {y} "
            f"Z"
        )

        return create_svg_element("path", {"d": path_data}, kwargs)
