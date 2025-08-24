"""Connected shape renderers that create fluid, context-aware QR code modules.

These renderers analyze neighboring modules to create shapes that connect
smoothly, inspired by qr-code-styling's advanced rendering techniques.

The connected renderers use neighbor analysis to determine the appropriate
shape for each module, creating smooth transitions and organic patterns.

Available connected renderers:

* ConnectedRoundedRenderer: Basic connected style with rounded corners
* ConnectedExtraRoundedRenderer: Extra smooth curves using quadratic beziers
* AdvancedClassyRenderer: Boundary-focused styling with strategic rounding
* AdvancedClassyRoundedRenderer: Classy style with extra-rounded corners

"""

import xml.etree.ElementTree as ET
from enum import Enum, auto
from typing import Callable, Optional

from ..core.interfaces import ShapeRenderer
from .basic import apply_element_attributes


class Corner(Enum):
    """Enumeration for corner positions.

    Used to specify which corner of a module should be rounded.
    """

    TOP_LEFT = auto()
    TOP_RIGHT = auto()
    BOTTOM_LEFT = auto()
    BOTTOM_RIGHT = auto()


class Side(Enum):
    """Enumeration for side positions.

    Used to specify which side of a module should be rounded.
    """

    TOP = auto()
    BOTTOM = auto()
    LEFT = auto()
    RIGHT = auto()


class ConnectedRoundedRenderer(ShapeRenderer):
    """Renders modules that connect to their neighbors with rounded corners.

    Creates fluid, organic-looking QR codes by analyzing module context.
    The renderer determines the appropriate shape based on the number and
    position of neighboring dark modules.

    Shape selection logic:

    * 0 neighbors: Isolated dot
    * 1 neighbor: Rounded end cap
    * 2 neighbors (line): Straight module
    * 2 neighbors (corner): Rounded corner
    * 3+ neighbors: Straight module

    """

    def render(self, x: float, y: float, size: float, **kwargs) -> ET.Element:
        """Render a connected module based on its neighbors.

        Args:
            x: X coordinate of module
            y: Y coordinate of module
            size: Module size in pixels
            **kwargs: Additional parameters including:
                get_neighbor: Function to check neighbor existence
                css_class: CSS class for the element
                id: Optional element ID

        Returns:
            ET.Element: SVG element representing the module

        Note:
            Requires a 'get_neighbor' function in kwargs that returns whether
            a neighbor exists at the given offset (dx, dy).
        """
        get_neighbor: Optional[Callable[[int, int], bool]] = kwargs.get("get_neighbor")

        if not get_neighbor:
            return self._basic_square(x, y, size, **kwargs)

        # Store neighbor information for use in drawing methods
        self._left_neighbor = get_neighbor(-1, 0)
        self._right_neighbor = get_neighbor(1, 0)
        self._top_neighbor = get_neighbor(0, -1)
        self._bottom_neighbor = get_neighbor(0, 1)

        neighbors_count = sum(
            [
                self._left_neighbor,
                self._right_neighbor,
                self._top_neighbor,
                self._bottom_neighbor,
            ]
        )

        if neighbors_count == 0:
            return self._draw_isolated(x, y, size, **kwargs)
        elif neighbors_count == 1:
            return self._draw_terminal(x, y, size, **kwargs)
        elif neighbors_count == 2:
            # Check for straight line case
            if (self._left_neighbor and self._right_neighbor) or (
                self._top_neighbor and self._bottom_neighbor
            ):
                return self._draw_straight(x, y, size, **kwargs)
            return self._draw_corner(x, y, size, **kwargs)
        else:  # > 2 neighbors
            return self._draw_straight(x, y, size, **kwargs)

    def _draw_isolated(self, x: float, y: float, size: float, **kwargs) -> ET.Element:
        """Draw an isolated module with no neighbors.

        Args:
            x: X coordinate
            y: Y coordinate
            size: Module size
            **kwargs: Additional parameters

        Returns:
            ET.Element: Circular dot element
        """
        return self._basic_dot(x, y, size, **kwargs)

    def _draw_straight(self, x: float, y: float, size: float, **kwargs) -> ET.Element:
        """Draw a module that's part of a straight line or has many neighbors."""
        return self._basic_square(x, y, size, **kwargs)

    def _draw_terminal(self, x: float, y: float, size: float, **kwargs) -> ET.Element:
        """Draw a terminal module with exactly one neighbor."""
        if self._top_neighbor:
            return self._side_rounded(x, y, size, Side.BOTTOM, **kwargs)
        elif self._right_neighbor:
            return self._side_rounded(x, y, size, Side.LEFT, **kwargs)
        elif self._bottom_neighbor:
            return self._side_rounded(x, y, size, Side.TOP, **kwargs)
        elif self._left_neighbor:
            return self._side_rounded(x, y, size, Side.RIGHT, **kwargs)

        # Fallback (shouldn't happen)
        return self._basic_square(x, y, size, **kwargs)

    def _draw_corner(self, x: float, y: float, size: float, **kwargs) -> ET.Element:
        """Draw a corner module with exactly two perpendicular neighbors."""
        if self._left_neighbor and self._top_neighbor:
            return self._corner_rounded(x, y, size, Corner.BOTTOM_RIGHT, **kwargs)
        elif self._top_neighbor and self._right_neighbor:
            return self._corner_rounded(x, y, size, Corner.BOTTOM_LEFT, **kwargs)
        elif self._right_neighbor and self._bottom_neighbor:
            return self._corner_rounded(x, y, size, Corner.TOP_LEFT, **kwargs)
        elif self._bottom_neighbor and self._left_neighbor:
            return self._corner_rounded(x, y, size, Corner.TOP_RIGHT, **kwargs)

        # Fallback (shouldn't happen)
        return self._basic_square(x, y, size, **kwargs)

    def _basic_dot(self, x: float, y: float, size: float, **kwargs) -> ET.Element:
        """Create a circular dot for isolated modules."""
        circle = ET.Element(
            "circle",
            {
                "cx": str(x + size / 2),
                "cy": str(y + size / 2),
                "r": str(size / 2),
                "class": kwargs.get("css_class", "qr-module"),
            },
        )
        apply_element_attributes(circle, kwargs)
        return circle

    def _basic_square(self, x: float, y: float, size: float, **kwargs) -> ET.Element:
        """Create a square for highly connected modules."""
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
        apply_element_attributes(rect, kwargs)
        return rect

    def _side_rounded(
        self, x: float, y: float, size: float, side: Side, **kwargs
    ) -> ET.Element:
        """Create a module with one rounded side."""
        half_size = size / 2

        if side == Side.RIGHT:
            path_data = (
                f"M {x} {y} "
                f"v {size} "
                f"h {half_size} "
                f"a {half_size} {half_size} 0 0 0 0 {-size} "
                f"Z"
            )
        elif side == Side.LEFT:
            path_data = (
                f"M {x + size} {y} "
                f"v {size} "
                f"h {-half_size} "
                f"a {half_size} {half_size} 0 0 1 0 {-size} "
                f"Z"
            )
        elif side == Side.BOTTOM:
            path_data = (
                f"M {x} {y} "
                f"h {size} "
                f"v {half_size} "
                f"a {half_size} {half_size} 0 0 1 {-size} 0 "
                f"Z"
            )
        else:  # Side.TOP
            path_data = (
                f"M {x} {y + size} "
                f"h {size} "
                f"v {-half_size} "
                f"a {half_size} {half_size} 0 0 0 {-size} 0 "
                f"Z"
            )

        return self._create_path(path_data, **kwargs)

    def _corner_rounded(
        self, x: float, y: float, size: float, corner: Corner, **kwargs
    ) -> ET.Element:
        """Create a module with one rounded corner.

        The rounded corner is on the opposite side of the neighbors.
        E.g., if neighbors are RIGHT and BOTTOM, the TOP-LEFT corner is rounded.
        """
        half_size = size / 2

        if corner == Corner.TOP_LEFT:
            # Start at bottom-left, move clockwise with rounded top-left
            path_data = (
                f"M {x} {y + size} "  # Start at bottom-left
                f"V {y + half_size} "  # Move up to middle-left
                f"A {half_size} {half_size} 0 0 1 {x + half_size} {y} "  # Arc to top-middle
                f"H {x + size} "  # Line to top-right
                f"V {y + size} "  # Line to bottom-right
                f"Z"  # Close path back to bottom-left
            )
        elif corner == Corner.TOP_RIGHT:
            # Start at bottom-right, move clockwise with rounded top-right
            path_data = (
                f"M {x + size} {y + size} "  # Start at bottom-right
                f"H {x} "  # Line to bottom-left
                f"V {y} "  # Line to top-left
                f"H {x + half_size} "  # Line to top-middle
                f"A {half_size} {half_size} 0 0 1 {x + size} {y + half_size} "  # Arc to right-middle
                f"Z"  # Close path back to bottom-right
            )
        elif corner == Corner.BOTTOM_RIGHT:
            # Start at top-right, move clockwise with rounded bottom-right
            path_data = (
                f"M {x + size} {y} "  # Start at top-right
                f"V {y + half_size} "  # Line to right-middle
                f"A {half_size} {half_size} 0 0 1 {x + half_size} {y + size} "  # Arc to bottom-middle
                f"H {x} "  # Line to bottom-left
                f"V {y} "  # Line to top-left
                f"Z"  # Close path back to top-right
            )
        else:  # Corner.BOTTOM_LEFT
            # Start at top-left, move clockwise with rounded bottom-left
            path_data = (
                f"M {x} {y} "  # Start at top-left
                f"H {x + size} "  # Line to top-right
                f"V {y + size} "  # Line to bottom-right
                f"H {x + half_size} "  # Line to bottom-middle
                f"A {half_size} {half_size} 0 0 1 {x} {y + half_size} "  # Arc to left-middle
                f"Z"  # Close path back to top-left
            )

        return self._create_path(path_data, **kwargs)

    def _create_path(self, path_data: str, **kwargs) -> ET.Element:
        """Create a path element with the given data."""
        path = ET.Element(
            "path",
            {"d": path_data, "class": kwargs.get("css_class", "qr-module")},
        )
        apply_element_attributes(path, kwargs)
        return path

    def supports_type(self, shape_type: str) -> bool:
        """Check if this renderer supports the given shape type."""
        return shape_type.lower() in ["connected"]


class ConnectedExtraRoundedRenderer(ConnectedRoundedRenderer):
    """Renders modules with extra rounded corners for a softer appearance.

    Similar to ConnectedRoundedRenderer but with more pronounced curves
    using quadratic Bezier curves instead of circular arcs.

    Key differences from ConnectedRoundedRenderer:

    * Smaller isolated dots (0.375 vs 0.5 radius)
    * Quadratic Bezier curves for ultra-smooth corners
    * Full-size radius for side rounding
    * More organic, flowing appearance

    Example:
        >>> renderer = ConnectedExtraRoundedRenderer()
        >>> # Requires get_neighbor function
        >>> element = renderer.render(0, 0, 10, get_neighbor=neighbor_func)
    """

    def _basic_dot(self, x: float, y: float, size: float, **kwargs) -> ET.Element:
        """Create a smaller circular dot for isolated modules."""
        circle = ET.Element(
            "circle",
            {
                "cx": str(x + size / 2),
                "cy": str(y + size / 2),
                "r": str(size * 0.375),  # Smaller than standard
                "class": kwargs.get("css_class", "qr-module"),
            },
        )
        apply_element_attributes(circle, kwargs)
        return circle

    def _basic_square(self, x: float, y: float, size: float, **kwargs) -> ET.Element:
        """Create a square for highly connected modules.

        Note: This uses sharp corners (no rounding) because these modules
        need to connect seamlessly with their neighbors.
        """
        rect = ET.Element(
            "rect",
            {
                "x": str(x),
                "y": str(y),
                "width": str(size),
                "height": str(size),
                # No rounding - sharp corners for proper connections
                "class": kwargs.get("css_class", "qr-module"),
            },
        )
        apply_element_attributes(rect, kwargs)
        return rect

    def _side_rounded(
        self, x: float, y: float, size: float, side: Side, **kwargs
    ) -> ET.Element:
        """Creates a module with one pill-shaped, extra-rounded side."""
        half = size / 2
        if side == Side.RIGHT:
            # Connects left. Right side is a semicircle.
            path_data = f"M {x} {y} v {size} h {half} a {half} {half} 0 0 0 0 {-size} Z"
        elif side == Side.LEFT:
            path_data = (
                f"M {x + size} {y} v {size} h {-half} a {half} {half} 0 0 1 0 {-size} Z"
            )
        elif side == Side.BOTTOM:
            path_data = f"M {x} {y} h {size} v {half} a {half} {half} 0 0 1 {-size} 0 Z"
        else:  # Side.TOP
            path_data = (
                f"M {x} {y + size} h {size} v {-half} a {half} {half} 0 0 0 {-size} 0 Z"
            )
        return self._create_path(path_data, **kwargs)

    def _corner_rounded(
        self, x: float, y: float, size: float, corner: Corner, **kwargs
    ) -> ET.Element:
        """
        Creates a module with one extra-rounded, convex corner using a Quadratic Bezier curve.
        """
        if corner == Corner.TOP_LEFT:
            # Neighbors are RIGHT and BOTTOM. Soft corner is TOP-LEFT.
            path_data = (
                f"M {x + size} {y} "  # Start at top-right
                f"L {x + size} {y + size} "  # Line to bottom-right (connects to bottom neighbor)
                f"L {x} {y + size} "  # Line to bottom-left
                f"Q {x} {y} {x + size} {y} "  # Curve to top-right with top-left as control point
                f"Z"
            )
        elif corner == Corner.TOP_RIGHT:
            # Neighbors are LEFT and BOTTOM. Soft corner is TOP-RIGHT.
            path_data = (
                f"M {x + size} {y + size} "  # Start at bottom-right
                f"L {x} {y + size} "  # Line to bottom-left (connects to bottom neighbor)
                f"L {x} {y} "  # Line to top-left (connects to left neighbor)
                f"Q {x + size} {y} {x + size} {y + size} "  # Curve to bottom-right with top-right as control
                f"Z"
            )
        elif corner == Corner.BOTTOM_RIGHT:
            # Neighbors are LEFT and TOP. Soft corner is BOTTOM-RIGHT.
            path_data = (
                f"M {x} {y + size} "  # Start at bottom-left
                f"L {x} {y} "  # Line to top-left (connects to top neighbor)
                f"L {x + size} {y} "  # Line to top-right
                f"Q {x + size} {y + size} {x} {y + size} "  # Curve to bottom-left with bottom-right as control
                f"Z"
            )
        else:  # corner == Corner.BOTTOM_LEFT
            # Neighbors are RIGHT and TOP. Soft corner is BOTTOM-LEFT.
            path_data = (
                f"M {x} {y} "  # Start at top-left
                f"L {x + size} {y} "  # Line to top-right (connects to top neighbor)
                f"L {x + size} {y + size} "  # Line to bottom-right (connects to right neighbor)
                f"Q {x} {y + size} {x} {y} "  # Curve to top-left with bottom-left as control
                f"Z"
            )
        return self._create_path(path_data, **kwargs)

    def supports_type(self, shape_type: str) -> bool:
        """Check if this renderer supports the given shape type."""
        return shape_type.lower() in ["connected-extra-rounded"]


# ConnectedClassyRenderer removed - shapes 'classy', 'connected_classy', 'elegant' no longer supported


class AdvancedClassyRenderer(ConnectedRoundedRenderer):
    """Renders modules with advanced classy style focusing on shape boundaries.

    This renderer implements a sophisticated boundary detection algorithm
    that only rounds specific corners of QR code shapes, creating a
    distinctive "classy" appearance.

    The renderer follows these rules:

    1. **Isolated modules**: Get jewel-like appearance with opposite corners rounded
    2. **Top-left outer corners**: Modules with no neighbors above or left
    3. **Bottom-right outer corners**: Modules with no neighbors below or right
    4. **All other modules**: Rendered as solid squares

    This creates an elegant look where only the outer boundaries of shapes
    have rounded corners, while internal modules remain square for stability.

    Example:
        >>> renderer = AdvancedClassyRenderer()
        >>> # Requires get_neighbor function
        >>> element = renderer.render(0, 0, 10, get_neighbor=neighbor_func)

    Note:
        Based on the TypeScript QRDot.ts _drawClassy logic from qr-code-styling.
    """

    def render(self, x: float, y: float, size: float, **kwargs) -> ET.Element:
        get_neighbor: Optional[Callable[[int, int], bool]] = kwargs.get("get_neighbor")
        if not get_neighbor:
            return self._basic_square(x, y, size, **kwargs)

        # Get neighbor states
        left = get_neighbor(-1, 0)
        right = get_neighbor(1, 0)
        top = get_neighbor(0, -1)
        bottom = get_neighbor(0, 1)

        neighbors_count = sum([left, right, top, bottom])

        # Rule 1: Isolated module gets jewel-like shape with opposite corners rounded
        if neighbors_count == 0:
            return self._basic_corners_rounded(x, y, size, **kwargs)

        # Rule 2: Top-left outer corner of a shape (no neighbors above or left)
        if not top and not left:
            return self._corner_rounded(x, y, size, Corner.TOP_LEFT, **kwargs)

        # Rule 3: Bottom-right outer corner of a shape (no neighbors below or right)
        if not bottom and not right:
            return self._corner_rounded(x, y, size, Corner.BOTTOM_RIGHT, **kwargs)

        # Rule 4: Everything else is a solid square (middle of lines, T-junctions, crosses)
        return self._basic_square(x, y, size, **kwargs)

    def _basic_corners_rounded(
        self, x: float, y: float, size: float, **kwargs
    ) -> ET.Element:
        """Create a jewel-like shape with opposite corners rounded.

        This method creates a distinctive shape used for isolated modules,
        with top-left and bottom-right corners rounded using circular arcs.

        Args:
            x: X coordinate
            y: Y coordinate
            size: Module size
            **kwargs: Additional parameters

        Returns:
            ET.Element: Path element with opposite rounded corners
        """
        half_size = size / 2
        path_data = (
            f"M {x} {y + half_size} "  # Start at middle-left
            f"A {half_size} {half_size} 0 0 1 {x + half_size} {y} "  # Arc for top-left corner
            f"H {x + size} "  # Line to top-right
            f"V {y + half_size} "  # Line to middle-right
            f"A {half_size} {half_size} 0 0 1 {x + half_size} {y + size} "  # Arc for bottom-right
            f"H {x} "  # Line to bottom-left
            f"Z"
        )
        return self._create_path(path_data, **kwargs)

    def supports_type(self, shape_type: str) -> bool:
        """Check if this renderer supports the given shape type."""
        return shape_type.lower() in ["connected-classy"]


class AdvancedClassyRoundedRenderer(ConnectedExtraRoundedRenderer):
    """Renders modules with classy rounded style using ultra-smooth curves.

    Combines the boundary detection logic of AdvancedClassyRenderer with
    the extra-rounded drawing methods of ConnectedExtraRoundedRenderer.

    Key features:

    * Same boundary detection rules as AdvancedClassyRenderer
    * Uses quadratic Bezier curves instead of circular arcs
    * Creates softer, more organic appearance
    * Isolated modules get jewel-like shapes with Bezier curves

    The result is a highly polished look with smooth boundaries and
    flowing curves that enhance the QR code's visual appeal.

    Example:
        >>> renderer = AdvancedClassyRoundedRenderer()
        >>> # Creates ultra-smooth classy style
        >>> element = renderer.render(0, 0, 10, get_neighbor=neighbor_func)
    """

    def render(self, x: float, y: float, size: float, **kwargs) -> ET.Element:
        get_neighbor: Optional[Callable[[int, int], bool]] = kwargs.get("get_neighbor")
        if not get_neighbor:
            return self._basic_square(x, y, size, **kwargs)

        # Get neighbor states
        left = get_neighbor(-1, 0)
        right = get_neighbor(1, 0)
        top = get_neighbor(0, -1)
        bottom = get_neighbor(0, 1)

        neighbors_count = sum([left, right, top, bottom])

        # Rule 1: Isolated module gets jewel-like shape with opposite corners rounded
        if neighbors_count == 0:
            return self._basic_corners_rounded(x, y, size, **kwargs)

        # Rule 2: Top-left outer corner of a shape (no neighbors above or left)
        if not top and not left:
            return self._corner_rounded(x, y, size, Corner.TOP_LEFT, **kwargs)

        # Rule 3: Bottom-right outer corner of a shape (no neighbors below or right)
        if not bottom and not right:
            return self._corner_rounded(x, y, size, Corner.BOTTOM_RIGHT, **kwargs)

        # Rule 4: Everything else is a solid square (middle of lines, T-junctions, crosses)
        return self._basic_square(x, y, size, **kwargs)

    def _basic_corners_rounded(
        self, x: float, y: float, size: float, **kwargs
    ) -> ET.Element:
        """Create a jewel-like shape with ultra-smooth opposite corners.

        Uses quadratic Bezier curves to create an extra-rounded version
        of the isolated module shape with smoother transitions.

        Args:
            x: X coordinate
            y: Y coordinate
            size: Module size
            **kwargs: Additional parameters

        Returns:
            ET.Element: Path element with Bezier-curved corners
        """
        # Use larger radius for extra-rounded appearance
        radius = size * 0.5  # Full radius for extra-rounded effect
        path_data = (
            f"M {x} {y + radius} "  # Start at middle-left
            f"Q {x} {y} {x + radius} {y} "  # Quadratic curve for top-left corner
            f"H {x + size} "  # Line to top-right
            f"V {y + radius} "  # Line to middle-right
            f"Q {x + size} {y + size} {x + radius} {y + size} "  # Quadratic curve for bottom-right
            f"H {x} "  # Line to bottom-left
            f"Z"
        )
        return self._create_path(path_data, **kwargs)

    def supports_type(self, shape_type: str) -> bool:
        """Check if this renderer supports the given shape type."""
        return shape_type.lower() in ["connected-classy-rounded"]
