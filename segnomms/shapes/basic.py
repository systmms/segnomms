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

import xml.etree.ElementTree as ET

from ..core.interfaces import ShapeRenderer


class SquareRenderer(ShapeRenderer):
    """Renders traditional square QR code modules.

    The most basic shape renderer, creating perfect squares for each module.
    This is the default shape for QR codes and provides maximum reliability
    for scanning while maintaining the classic QR code appearance.

    Example:
        >>> renderer = SquareRenderer()
        >>> square = renderer.render(0, 0, 10)
        >>> # Creates a 10x10 square at position (0,0)
    """

    def render(self, x: float, y: float, size: float, **kwargs) -> ET.Element:
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
        rect = ET.Element(
            "rect",
            {
                "x": str(x),
                "y": str(y),
                "width": str(size),
                "height": str(size),
                "class": kwargs.get("css_class", "qr-module"),
            },
        )
        if "id" in kwargs:
            rect.set("id", kwargs["id"])
        return rect

    def supports_type(self, shape_type: str) -> bool:
        """Check if this renderer supports the given shape type.

        Args:
            shape_type: Name of the shape type to check

        Returns:
            bool: True if shape_type is 'square'
        """
        return shape_type.lower() in ["square"]


class CircleRenderer(ShapeRenderer):
    """Renders circular QR code modules.

    Creates perfect circles that fit within the module grid. This shape
    provides a softer, more organic appearance while maintaining good
    scannability due to the consistent module centers.

    Example:
        >>> renderer = CircleRenderer()
        >>> circle = renderer.render(5, 5, 10)
        >>> # Creates a circle with radius 5 centered at (10,10)
    """

    def render(self, x: float, y: float, size: float, **kwargs) -> ET.Element:
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
        circle = ET.Element(
            "circle",
            {
                "cx": str(x + size / 2),
                "cy": str(y + size / 2),
                "r": str(size / 2 * kwargs.get("size_ratio", 0.9)),
                "class": kwargs.get("css_class", "qr-module"),
            },
        )
        if "id" in kwargs:
            circle.set("id", kwargs["id"])
        return circle

    def supports_type(self, shape_type: str) -> bool:
        """Check if this renderer supports the given shape type.

        Args:
            shape_type: Name of the shape type to check

        Returns:
            bool: True if shape_type is 'circle'
        """
        return shape_type.lower() in ["circle"]


# RoundedRenderer removed - shapes 'rounded', 'rounded_square', 'rounded_rect' no longer supported


class RoundedRenderer(ShapeRenderer):
    """Renders square modules with rounded corners.

    Creates modules with softly rounded corners for a more friendly,
    modern appearance. The corner radius can be controlled via the
    roundness parameter.

    Example:
        >>> renderer = RoundedRenderer()
        >>> rounded_rect = renderer.render(0, 0, 10, roundness=0.3)
        >>> # Creates a square with 30% corner radius
    """

    def render(self, x: float, y: float, size: float, **kwargs) -> ET.Element:
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
        roundness = kwargs.get("roundness", 0.3)
        radius = size * roundness

        rect = ET.Element(
            "rect",
            {
                "x": str(x),
                "y": str(y),
                "width": str(size),
                "height": str(size),
                "rx": str(radius),
                "ry": str(radius),
                "class": kwargs.get("css_class", "qr-module"),
            },
        )
        if "id" in kwargs:
            rect.set("id", kwargs["id"])
        return rect

    def supports_type(self, shape_type: str) -> bool:
        """Check if this renderer supports the given shape type.

        Args:
            shape_type: Name of the shape type to check

        Returns:
            bool: True if shape_type is 'rounded'
        """
        return shape_type.lower() in ["rounded"]


class DotRenderer(ShapeRenderer):
    """Renders small dot modules for a minimalist QR code style.

    Creates smaller circles that leave more whitespace between modules,
    resulting in a lighter, more delicate appearance. The dot size can
    be controlled via the size_ratio parameter.

    Example:
        >>> renderer = DotRenderer()
        >>> dot = renderer.render(0, 0, 10, size_ratio=0.5)
        >>> # Creates a 5-pixel diameter dot in a 10x10 module
    """

    def render(self, x: float, y: float, size: float, **kwargs) -> ET.Element:
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
        dot_size = size * kwargs.get("size_ratio", 0.6)
        circle = ET.Element(
            "circle",
            {
                "cx": str(x + size / 2),
                "cy": str(y + size / 2),
                "r": str(dot_size / 2),
                "class": kwargs.get("css_class", "qr-module"),
            },
        )
        if "id" in kwargs:
            circle.set("id", kwargs["id"])
        return circle

    def supports_type(self, shape_type: str) -> bool:
        """Check if this renderer supports the given shape type.

        Args:
            shape_type: Name of the shape type to check

        Returns:
            bool: True if shape_type is 'dot'
        """
        return shape_type.lower() in ["dot"]


class DiamondRenderer(ShapeRenderer):
    """Renders diamond (rhombus) shaped modules.

    Creates 45-degree rotated squares that form diamond patterns.
    This shape adds a geometric, crystalline quality to QR codes
    while maintaining good contrast for scanning.

    Example:
        >>> renderer = DiamondRenderer()
        >>> diamond = renderer.render(0, 0, 10)
        >>> # Creates a diamond touching all edges of the 10x10 module
    """

    def render(self, x: float, y: float, size: float, **kwargs) -> ET.Element:
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
        half = size / 2
        points = [
            f"{x + half},{y}",
            f"{x + size},{y + half}",
            f"{x + half},{y + size}",
            f"{x},{y + half}",
        ]
        polygon = ET.Element(
            "polygon",
            {
                "points": " ".join(points),
                "class": kwargs.get("css_class", "qr-module"),
            },
        )
        if "id" in kwargs:
            polygon.set("id", kwargs["id"])
        return polygon

    def supports_type(self, shape_type: str) -> bool:
        """Check if this renderer supports the given shape type.

        Args:
            shape_type: Name of the shape type to check

        Returns:
            bool: True if shape_type is 'diamond'
        """
        return shape_type.lower() in ["diamond"]


class StarRenderer(ShapeRenderer):
    """Renders star-shaped modules with configurable points.

    Creates multi-pointed star shapes that add a decorative flair to QR codes.
    The number of points and the inner/outer radius ratio can be customized
    to create different star styles from sharp to more rounded.

    Example:
        >>> renderer = StarRenderer()
        >>> star = renderer.render(0, 0, 10, star_points=6, inner_ratio=0.4)
        >>> # Creates a 6-pointed star with sharp points
    """

    def render(self, x: float, y: float, size: float, **kwargs) -> ET.Element:
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
        import math

        points = kwargs.get("star_points", 5)
        inner_ratio = kwargs.get("inner_ratio", 0.5)
        center_x = x + size / 2
        center_y = y + size / 2
        outer_radius = size / 2
        inner_radius = outer_radius * inner_ratio

        star_points = []
        for i in range(points * 2):
            angle = i * math.pi / points
            if i % 2 == 0:
                # Outer point
                px = center_x + outer_radius * math.cos(angle - math.pi / 2)
                py = center_y + outer_radius * math.sin(angle - math.pi / 2)
            else:
                # Inner point
                px = center_x + inner_radius * math.cos(angle - math.pi / 2)
                py = center_y + inner_radius * math.sin(angle - math.pi / 2)
            star_points.append(f"{px:.2f},{py:.2f}")

        polygon = ET.Element(
            "polygon",
            {
                "points": " ".join(star_points),
                "class": kwargs.get("css_class", "qr-module"),
            },
        )
        if "id" in kwargs:
            polygon.set("id", kwargs["id"])
        return polygon

    def supports_type(self, shape_type: str) -> bool:
        """Check if this renderer supports the given shape type.

        Args:
            shape_type: Name of the shape type to check

        Returns:
            bool: True if shape_type is 'star'
        """
        return shape_type.lower() in ["star"]


class TriangleRenderer(ShapeRenderer):
    """Renders triangular modules with directional orientation.

    Creates equilateral triangles that can point in different directions.
    This shape adds a dynamic, directional quality to QR codes and can
    create interesting patterns when modules align.

    Example:
        >>> renderer = TriangleRenderer()
        >>> triangle = renderer.render(0, 0, 10, direction='up')
        >>> # Creates an upward-pointing triangle
    """

    def render(self, x: float, y: float, size: float, **kwargs) -> ET.Element:
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
        direction = kwargs.get("direction", "up")  # up, down, left, right

        if direction == "up":
            points = [
                f"{x + size / 2},{y}",
                f"{x + size},{y + size}",
                f"{x},{y + size}",
            ]
        elif direction == "down":
            points = [
                f"{x},{y}",
                f"{x + size},{y}",
                f"{x + size / 2},{y + size}",
            ]
        elif direction == "left":
            points = [
                f"{x},{y + size / 2}",
                f"{x + size},{y}",
                f"{x + size},{y + size}",
            ]
        else:  # right
            points = [
                f"{x},{y}",
                f"{x},{y + size}",
                f"{x + size},{y + size / 2}",
            ]

        polygon = ET.Element(
            "polygon",
            {
                "points": " ".join(points),
                "class": kwargs.get("css_class", "qr-module"),
            },
        )
        if "id" in kwargs:
            polygon.set("id", kwargs["id"])
        return polygon

    def supports_type(self, shape_type: str) -> bool:
        """Check if this renderer supports the given shape type.

        Args:
            shape_type: Name of the shape type to check

        Returns:
            bool: True if shape_type is 'triangle'
        """
        return shape_type.lower() in ["triangle"]


class HexagonRenderer(ShapeRenderer):
    """Renders hexagonal modules for a honeycomb-like appearance.

    Creates regular hexagons that can tessellate beautifully when
    adjacent modules are also hexagons. This shape provides an
    organic, nature-inspired look to QR codes.

    Example:
        >>> renderer = HexagonRenderer()
        >>> hexagon = renderer.render(0, 0, 10, size_ratio=0.95)
        >>> # Creates a hexagon slightly smaller than the module
    """

    def render(self, x: float, y: float, size: float, **kwargs) -> ET.Element:
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
        import math

        center_x = x + size / 2
        center_y = y + size / 2
        radius = size / 2 * kwargs.get("size_ratio", 0.9)

        hex_points = []
        for i in range(6):
            angle = i * math.pi / 3
            px = center_x + radius * math.cos(angle)
            py = center_y + radius * math.sin(angle)
            hex_points.append(f"{px:.2f},{py:.2f}")

        polygon = ET.Element(
            "polygon",
            {
                "points": " ".join(hex_points),
                "class": kwargs.get("css_class", "qr-module"),
            },
        )
        if "id" in kwargs:
            polygon.set("id", kwargs["id"])
        return polygon

    def supports_type(self, shape_type: str) -> bool:
        """Check if this renderer supports the given shape type.

        Args:
            shape_type: Name of the shape type to check

        Returns:
            bool: True if shape_type is 'hexagon'
        """
        return shape_type.lower() in ["hexagon"]


class CrossRenderer(ShapeRenderer):
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

    def render(self, x: float, y: float, size: float, **kwargs) -> ET.Element:
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

        # Create cross using path
        center_x = x + size / 2
        center_y = y + size / 2
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

        path = ET.Element(
            "path",
            {"d": path_data, "class": kwargs.get("css_class", "qr-module")},
        )
        if "id" in kwargs:
            path.set("id", kwargs["id"])
        return path

    def supports_type(self, shape_type: str) -> bool:
        """Check if this renderer supports the given shape type.

        Args:
            shape_type: Name of the shape type to check

        Returns:
            bool: True if shape_type is 'cross'
        """
        return shape_type.lower() in ["cross"]
