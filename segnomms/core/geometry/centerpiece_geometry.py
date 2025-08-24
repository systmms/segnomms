"""Geometric calculations for centerpiece positioning and containment.

This module provides pure mathematical functions for calculating centerpiece
bounds, placement offsets, containment checks, and safe reserve sizes.
"""

from typing import Tuple


class CenterpieceGeometry:
    """Handles geometric calculations for centerpiece positioning.

    This class provides pure mathematical calculations for centerpiece
    positioning and containment. All methods are stateless and free of
    side effects.

    Attributes:
        ERROR_CORRECTION_CAPACITY: Maximum data loss capacity by error level
    """

    # Error correction capacities by level
    ERROR_CORRECTION_CAPACITY = {
        "L": 0.07,  # 7% recovery capability
        "M": 0.15,  # 15% recovery capability
        "Q": 0.25,  # 25% recovery capability
        "H": 0.30,  # 30% recovery capability
    }

    def __init__(self, matrix_size: int):
        """Initialize the geometry calculator.

        Args:
            matrix_size: Size of the QR code matrix (width/height)
        """
        self.size = matrix_size

    def calculate_safe_reserve_size(self, version: int, error_level: str) -> float:
        """Calculate maximum safe reserve size based on error correction.

        Args:
            version: QR code version (1-40)
            error_level: Error correction level ('L', 'M', 'Q', 'H')

        Returns:
            Maximum safe reserve size as a fraction of QR code area
        """
        capacity = self.ERROR_CORRECTION_CAPACITY.get(error_level.upper(), 0.15)
        # Use 80% of capacity for safety margin
        return capacity * 0.8

    def calculate_placement_offsets(self, config) -> Tuple[float, float]:
        """Calculate offset_x and offset_y based on placement mode.

        Args:
            config: CenterpieceConfig instance

        Returns:
            Tuple of (offset_x, offset_y) values
        """
        # Import locally to avoid circular imports
        from ...config import PlacementMode

        if not hasattr(config, "placement") or config.placement == PlacementMode.CUSTOM:
            # Use explicit offset values
            return config.offset_x, config.offset_y

        # Calculate based on placement mode
        placement_offsets = {
            PlacementMode.CENTER: (0.0, 0.0),
            PlacementMode.TOP_LEFT: (-0.3, -0.3),
            PlacementMode.TOP_RIGHT: (0.3, -0.3),
            PlacementMode.BOTTOM_LEFT: (-0.3, 0.3),
            PlacementMode.BOTTOM_RIGHT: (0.3, 0.3),
            PlacementMode.TOP_CENTER: (0.0, -0.3),
            PlacementMode.BOTTOM_CENTER: (0.0, 0.3),
            PlacementMode.LEFT_CENTER: (-0.3, 0.0),
            PlacementMode.RIGHT_CENTER: (0.3, 0.0),
        }

        return placement_offsets.get(config.placement, (0.0, 0.0))

    def get_centerpiece_bounds(self, config) -> Tuple[int, int, int, int]:
        """Calculate centerpiece bounds in module coordinates.

        Args:
            config: CenterpieceConfig instance

        Returns:
            Tuple of (x1, y1, x2, y2) representing the bounding box
        """
        # Calculate effective offsets based on placement mode
        offset_x, offset_y = self.calculate_placement_offsets(config)

        center_x = self.size / 2 + (offset_x * self.size)
        center_y = self.size / 2 + (offset_y * self.size)
        half_size = config.size * self.size / 2

        x1 = int(center_x - half_size - config.margin)
        y1 = int(center_y - half_size - config.margin)
        x2 = int(center_x + half_size + config.margin)
        y2 = int(center_y + half_size + config.margin)

        # Clamp to matrix bounds
        return max(0, x1), max(0, y1), min(self.size, x2), min(self.size, y2)

    def is_in_centerpiece(self, row: int, col: int, config) -> bool:
        """Check if a module is within the centerpiece area.

        Args:
            row: Module row position
            col: Module column position
            config: CenterpieceConfig instance

        Returns:
            True if module is within centerpiece area
        """
        # Calculate effective offsets for consistent positioning
        offset_x, offset_y = self.calculate_placement_offsets(config)

        if config.shape == "rect":
            x1, y1, x2, y2 = self.get_centerpiece_bounds(config)
            return x1 <= col < x2 and y1 <= row < y2

        elif config.shape == "circle":
            center_x = self.size / 2 + (offset_x * self.size)
            center_y = self.size / 2 + (offset_y * self.size)
            radius = config.size * self.size / 2 + config.margin
            dist = ((col - center_x) ** 2 + (row - center_y) ** 2) ** 0.5
            return dist <= radius

        elif config.shape == "squircle":
            # Superellipse formula for squircle
            center_x = self.size / 2 + (offset_x * self.size)
            center_y = self.size / 2 + (offset_y * self.size)
            radius = config.size * self.size / 2 + config.margin
            n = 4  # Squircle parameter

            # Avoid division by zero
            if radius <= 0:
                return False

            return (abs(col - center_x) / radius) ** n + (
                abs(row - center_y) / radius
            ) ** n <= 1

        return False

    def is_edge_module(self, row: int, col: int, config) -> bool:
        """Check if a module is on the edge of the centerpiece area.

        Args:
            row: Module row position
            col: Module column position
            config: CenterpieceConfig instance

        Returns:
            True if module is on the edge of the centerpiece area
        """
        # Check if module is in centerpiece
        if not self.is_in_centerpiece(row, col, config):
            return False

        # Check if any adjacent module is outside the centerpiece
        adjacent_positions = [
            (row - 1, col),
            (row + 1, col),  # vertical neighbors
            (row, col - 1),
            (row, col + 1),  # horizontal neighbors
        ]

        for adj_row, adj_col in adjacent_positions:
            # Skip out-of-bounds positions
            if 0 <= adj_row < self.size and 0 <= adj_col < self.size:
                if not self.is_in_centerpiece(adj_row, adj_col, config):
                    return True

        return False

    def should_clear_edge_module(self, row: int, col: int, config, matrix) -> bool:
        """Determine if an edge module should be cleared based on refinement settings.

        Args:
            row: Module row position
            col: Module column position
            config: CenterpieceConfig instance
            matrix: QR code matrix for context

        Returns:
            True if edge module should be cleared
        """
        if not hasattr(config, "edge_refinement") or not config.edge_refinement:
            return True  # Clear all edge modules if no refinement

        refinement = config.edge_refinement

        # Always preserve critical patterns regardless of refinement settings
        if self._is_critical_pattern_module(row, col, matrix):
            return False

        if refinement == "preserve_data":
            # Only clear if module is currently False (non-data module)
            return not matrix[row][col]
        elif refinement == "smooth_edges":
            # Use neighbor analysis to create smoother edges
            return self._should_clear_for_smooth_edge(row, col, config, matrix)
        else:  # "minimal" or any other setting
            # Clear all edge modules for clean appearance
            return True

    def _is_critical_pattern_module(self, row: int, col: int, matrix) -> bool:
        """Check if a module is part of a critical QR pattern.

        This is a simplified check - in practice, this would use
        the ModuleDetector for more accurate pattern detection.
        """
        # Check for finder patterns (approximate positions)
        finder_positions = [
            (0, 0),
            (0, self.size - 7),
            (self.size - 7, 0),  # Top-left, top-right, bottom-left
        ]

        for finder_row, finder_col in finder_positions:
            if (
                finder_row <= row < finder_row + 7
                and finder_col <= col < finder_col + 7
            ):
                return True

        # Check for timing patterns
        if row == 6 or col == 6:
            return True

        return False

    def _should_clear_for_smooth_edge(self, row: int, col: int, config, matrix) -> bool:
        """Determine if a module should be cleared for smooth edge refinement.

        This analyzes neighboring modules to create visually pleasing edges.
        """
        # Count how many neighboring modules are also in the centerpiece
        neighbors_in_centerpiece = 0
        total_valid_neighbors = 0

        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = row + dr, col + dc
            if 0 <= nr < self.size and 0 <= nc < self.size:
                total_valid_neighbors += 1
                if self.is_in_centerpiece(nr, nc, config):
                    neighbors_in_centerpiece += 1

        # Clear module if it has fewer than half its neighbors in the centerpiece
        # This creates more natural, rounded edges
        return neighbors_in_centerpiece < (total_valid_neighbors / 2)
