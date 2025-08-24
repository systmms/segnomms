"""Path clipping utilities for frame boundaries.

This module provides utilities to clip SVG paths to frame boundaries,
ensuring that cluster paths and other generated shapes respect the
configured frame shape.
"""

from typing import List, Optional, Tuple


class PathClipper:
    """Clips SVG paths to frame boundaries.

    This class provides methods to ensure that generated paths (from clustering
    or other phases) don't extend beyond the configured frame shape boundaries.
    """

    def __init__(
        self,
        frame_shape: str,
        width: int,
        height: int,
        border: int,
        corner_radius: float = 0.0,
    ):
        """Initialize the path clipper.

        Args:
            frame_shape: Frame shape type ('square', 'circle', 'rounded-rect', 'squircle')
            width: Total SVG width in pixels
            height: Total SVG height in pixels
            border: Border size in pixels
            corner_radius: Corner radius for rounded-rect (0.0-1.0)
        """
        self.frame_shape = frame_shape
        self.width = width
        self.height = height
        self.border = border
        self.corner_radius = corner_radius

        # Calculate frame boundaries
        self.frame_left = border
        self.frame_top = border
        self.frame_right = width - border
        self.frame_bottom = height - border
        self.frame_width = width - 2 * border
        self.frame_height = height - 2 * border

    def is_point_in_frame(self, x: float, y: float) -> bool:
        """Check if a point is within the frame boundaries.

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            True if point is within frame boundaries
        """
        if self.frame_shape == "square":
            return (
                self.frame_left <= x <= self.frame_right
                and self.frame_top <= y <= self.frame_bottom
            )

        elif self.frame_shape == "circle":
            cx = self.width / 2
            cy = self.height / 2
            r = min(self.width, self.height) / 2
            dist = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
            return dist <= r

        elif self.frame_shape == "rounded-rect":
            # Check if in main rectangle area
            if (
                self.frame_left + self.corner_radius * self.frame_width
                <= x
                <= self.frame_right - self.corner_radius * self.frame_width
                and self.frame_top <= y <= self.frame_bottom
            ):
                return True
            if (
                self.frame_left <= x <= self.frame_right
                and self.frame_top + self.corner_radius * self.frame_height
                <= y
                <= self.frame_bottom - self.corner_radius * self.frame_height
            ):
                return True

            # Check corners
            corner_r = self.corner_radius * min(self.frame_width, self.frame_height) / 2

            # Top-left corner
            if x < self.frame_left + corner_r and y < self.frame_top + corner_r:
                cx = self.frame_left + corner_r
                cy = self.frame_top + corner_r
                return ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5 <= corner_r

            # Similar checks for other corners...
            return True  # Simplified for now

        elif self.frame_shape == "squircle":
            # Superellipse formula
            cx = self.width / 2
            cy = self.height / 2
            rx = self.frame_width / 2
            ry = self.frame_height / 2
            n = 4  # Squircle parameter

            if rx <= 0 or ry <= 0:
                return False

            return (abs(x - cx) / rx) ** n + (abs(y - cy) / ry) ** n <= 1

        return True  # Default to allowing the point

    def get_distance_from_edge(self, x: float, y: float) -> float:
        """Calculate distance from point to frame edge.

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            Distance in pixels from the nearest frame edge (0 = on edge, positive = inside)
        """
        if self.frame_shape == "square":
            # Distance to nearest edge
            dist_left = x - self.frame_left
            dist_right = self.frame_right - x
            dist_top = y - self.frame_top
            dist_bottom = self.frame_bottom - y
            return min(dist_left, dist_right, dist_top, dist_bottom)

        elif self.frame_shape == "circle":
            cx = self.width / 2
            cy = self.height / 2
            r = min(self.width, self.height) / 2
            dist_from_center = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
            return r - dist_from_center

        elif self.frame_shape in ["rounded-rect", "squircle"]:
            # Simplified: use rectangular distance for now
            # TODO: Implement proper distance calculation for rounded shapes
            dist_left = x - self.frame_left
            dist_right = self.frame_right - x
            dist_top = y - self.frame_top
            dist_bottom = self.frame_bottom - y
            return min(dist_left, dist_right, dist_top, dist_bottom)

        return 0.0  # Default

    def get_scale_factor(self, x: float, y: float, scale_distance: float) -> float:
        """Calculate scale factor for a point based on distance from frame edge.

        Args:
            x: X coordinate
            y: Y coordinate
            scale_distance: Distance in pixels where scaling begins

        Returns:
            Scale factor (1.0 = full size, 0.0 = invisible)
        """
        distance = self.get_distance_from_edge(x, y)

        if distance >= scale_distance:
            return 1.0  # Full size
        elif distance <= 0:
            return 0.0  # At or outside edge
        else:
            # Linear interpolation
            return distance / scale_distance

    def clip_rectangle_to_frame(
        self, x: float, y: float, width: float, height: float
    ) -> Optional[str]:
        """Clip a rectangle to frame boundaries.

        Args:
            x: Rectangle X position
            y: Rectangle Y position
            width: Rectangle width
            height: Rectangle height

        Returns:
            SVG path string for clipped shape, or None if entirely outside
        """
        # For non-square frames, check if rectangle corners are in frame
        if self.frame_shape == "square":
            # Simple clipping for square frames
            clipped_x = max(x, self.frame_left)
            clipped_y = max(y, self.frame_top)
            clipped_right = min(x + width, self.frame_right)
            clipped_bottom = min(y + height, self.frame_bottom)

            if clipped_right <= clipped_x or clipped_bottom <= clipped_y:
                return None

            return (
                f"M {clipped_x} {clipped_y} "
                f"L {clipped_right} {clipped_y} "
                f"L {clipped_right} {clipped_bottom} "
                f"L {clipped_x} {clipped_bottom} Z"
            )

        # For other frame shapes, check if any part is visible
        # This is a simplified check - just see if center is in frame
        center_x = x + width / 2
        center_y = y + height / 2

        if not self.is_point_in_frame(center_x, center_y):
            # Check corners
            corners = [(x, y), (x + width, y), (x + width, y + height), (x, y + height)]

            if not any(self.is_point_in_frame(cx, cy) for cx, cy in corners):
                return None

        # Return the original rectangle path
        # In a full implementation, this would actually clip to the frame shape
        return (
            f"M {x} {y} "
            f"L {x + width} {y} "
            f"L {x + width} {y + height} "
            f"L {x} {y + height} Z"
        )

    def adjust_cluster_path(self, path: str, scale: int) -> str:
        """Adjust a cluster path to respect frame boundaries.

        Args:
            path: SVG path string
            scale: Module scale in pixels

        Returns:
            Adjusted SVG path string
        """
        # For now, just return the original path
        # In a full implementation, this would parse the path and clip it
        return path

    def get_frame_aware_bounds(
        self, positions: List[Tuple[int, int]], scale: int
    ) -> Tuple[int, int, int, int]:
        """Get bounding box for positions, constrained by frame.

        Args:
            positions: List of (row, col) positions
            scale: Module scale in pixels

        Returns:
            Tuple of (x, y, width, height) in pixels
        """
        if not positions:
            return (0, 0, 0, 0)

        # Get module bounds
        rows = [p[0] for p in positions]
        cols = [p[1] for p in positions]
        min_row, max_row = min(rows), max(rows)
        min_col, max_col = min(cols), max(cols)

        # Convert to pixel coordinates
        x = min_col * scale + self.border
        y = min_row * scale + self.border
        width = (max_col - min_col + 1) * scale
        height = (max_row - min_row + 1) * scale

        # For square frames, simple clipping
        if self.frame_shape == "square":
            x = max(x, self.frame_left)
            y = max(y, self.frame_top)
            right = min(x + width, self.frame_right)
            bottom = min(y + height, self.frame_bottom)

            if right > x and bottom > y:
                return (x, y, right - x, bottom - y)
            else:
                return (0, 0, 0, 0)

        # For other shapes, return original bounds
        # The path generation will handle the clipping
        return (x, y, width, height)
