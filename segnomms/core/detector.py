"""Core module detection functionality for QR codes.

This module contains the ModuleDetector class which identifies different
types of modules in a QR code (finder patterns, timing patterns, etc.).

The detector analyzes QR code matrices to classify each module as:

* Finder patterns (including inner regions)
* Separator modules
* Timing patterns
* Alignment patterns
* Format information
* Version information
* Data modules

"""

from typing import List, Optional, Tuple, Union

from .interfaces import QRCodeAnalyzer
from .models import ModuleDetectorConfig, NeighborAnalysis

#: Positions of finder patterns (top-left, top-right, bottom-left)
FINDER_PATTERN_POSITIONS = [(0, 0), (0, -7), (-7, 0)]

#: Size of finder patterns in modules
FINDER_SIZE = 7

#: Size of alignment patterns in modules
ALIGNMENT_PATTERN_SIZE = 5


class ModuleDetector(QRCodeAnalyzer):
    """Detects QR code module types and properties.

    This class analyzes a QR code matrix to identify different module types
    such as finder patterns, timing patterns, alignment patterns, and data modules.

    Attributes:
        matrix: The QR code matrix as a 2D boolean list
        size: Size of the QR code (modules per side)
        version: QR code version (1-40)
        alignment_positions: Calculated alignment pattern positions

    Example:
        >>> # Create a minimal valid matrix (21x21 for version 1)
        >>> matrix = [[True] * 21 for _ in range(21)]
        >>> detector = ModuleDetector(matrix, version=1)
        >>> module_type = detector.get_module_type(10, 10)
        >>> print(module_type)  # 'data'
    """

    def __init__(self, matrix: List[List[bool]], version: Optional[Union[int, str]] = None):
        """Initialize the detector with QR code matrix and optional version.

        Args:
            matrix: The QR code matrix as a 2D boolean list
            version: QR code version (1-40, 'M1'-'M4', or None for auto-detection)

        Example:
            >>> # Create a valid matrix for version 1 QR code (21x21)
            >>> matrix = [[True] * 21 for _ in range(21)]
            >>> detector = ModuleDetector(matrix, version=1)
            >>> # Or using Pydantic model
            >>> config = ModuleDetectorConfig(matrix=matrix, version=1)
            >>> detector = ModuleDetector(**config.model_dump())
        """
        # Validate inputs using Pydantic
        config = ModuleDetectorConfig(matrix=matrix, version=version)

        # Use validated values
        self.matrix = config.matrix
        self.size = len(config.matrix)

        # Parse version from validated format
        if config.version is not None:
            self.version = self._parse_version(config.version)
        else:
            self.version = self._estimate_version()
        self.alignment_positions = self._get_alignment_positions()

    def _parse_version(self, version: Union[int, str, None]) -> int:
        """Parse version from various formats.

        Args:
            version: Version in various formats (int, str, or None)

        Returns:
            int: Parsed version number

        Note:
            Handles formats like 'M3' (Micro QR), '4', or plain integers.
        """
        if isinstance(version, int):
            return version
        elif isinstance(version, str):
            # Handle formats like 'M3', 'M4' (Micro QR) or plain numbers
            if version.startswith("M"):
                # Micro QR version - extract number
                return int(version[1:])
            else:
                # Regular version string
                return int(version)
        else:
            # Fallback to estimation
            return self._estimate_version()

    def _estimate_version(self) -> int:
        """Estimate QR version from matrix size.

        Returns:
            int: Estimated version (1-40)

        Note:
            Uses the formula: version = (size - 21) / 4 + 1
        """
        return (self.size - 21) // 4 + 1 if self.size >= 21 else 1

    def _get_alignment_positions(self) -> List[Tuple[int, int]]:
        """Calculate alignment pattern positions based on version.

        Returns:
            List[Tuple[int, int]]: List of (row, col) positions

        Note:
            Version 1 has no alignment patterns.
            Higher versions have complex alignment pattern arrangements.
        """
        # Simplified alignment position calculation
        if self.version == 1:
            return []
        elif self.version <= 6:
            return [(self.size - 7, self.size - 7)]
        else:
            # More complex calculation for higher versions
            positions: List[Tuple[int, int]] = []
            # Add positions based on version...
            return positions

    def get_module_type(self, row: int, col: int) -> str:
        """Determine the type of module at given position.

        Args:
            row: Row index (0-based)
            col: Column index (0-based)

        Returns:
            str: Module type identifier:
                - 'finder': Finder pattern module
                - 'finder_inner': Inner finder pattern module
                - 'separator': Separator module
                - 'timing': Timing pattern module
                - 'alignment': Alignment pattern module
                - 'format': Format information module
                - 'version': Version information module
                - 'data': Data or error correction module

        Raises:
            IndexError: If row or col is out of bounds
        """
        # Validate bounds
        if not (0 <= row < self.size and 0 <= col < self.size):
            raise IndexError(
                f"Position ({row}, {col}) out of bounds for {self.size}x{self.size} matrix"
            )

        size = self.size

        # Finder patterns
        for base_row, base_col in FINDER_PATTERN_POSITIONS:
            abs_row = base_row if base_row >= 0 else size + base_row
            abs_col = base_col if base_col >= 0 else size + base_col

            if (
                abs_row <= row < abs_row + FINDER_SIZE
                and abs_col <= col < abs_col + FINDER_SIZE
            ):
                # Check if it's the inner part
                if (
                    abs_row + 2 <= row < abs_row + 5
                    and abs_col + 2 <= col < abs_col + 5
                ):
                    return "finder_inner"
                return "finder"

        # Separators (white border around finder patterns)
        for base_row, base_col in FINDER_PATTERN_POSITIONS:
            abs_row = base_row if base_row >= 0 else size + base_row
            abs_col = base_col if base_col >= 0 else size + base_col

            # Horizontal separator
            if (
                row == abs_row + FINDER_SIZE
                and abs_col <= col < abs_col + FINDER_SIZE + 1
            ):
                return "separator"
            # Vertical separator
            if (
                col == abs_col + FINDER_SIZE
                and abs_row <= row < abs_row + FINDER_SIZE + 1
            ):
                return "separator"

        # Timing patterns
        if row == 6 or col == 6:
            return "timing"

        # Alignment patterns
        for align_row, align_col in self.alignment_positions:
            if abs(row - align_row) <= 2 and abs(col - align_col) <= 2:
                if row == align_row and col == align_col:
                    return "alignment_center"
                return "alignment"

        # Dark module (always dark module near bottom-left finder)
        if row == 4 * self.version + 9 and col == 8:
            return "dark"

        # Format information
        if (row == 8 and (col < 9 or col >= size - 8)) or (
            col == 8 and (row < 9 or row >= size - 7)
        ):
            return "format"

        # Version information (for version 7+)
        if self.version >= 7:
            if (row < 6 and col >= size - 11) or (col < 6 and row >= size - 11):
                return "version"

        return "data"

    def get_version(self) -> int:
        """Get the QR code version.

        Returns:
            int: QR code version (1-40)
        """
        return self.version

    def get_size(self) -> int:
        """Get the size of the QR code matrix.

        Returns:
            int: Number of modules per side
        """
        return self.size

    def is_module_active(self, row: int, col: int) -> bool:
        """Check if the module at given position is active (dark).

        Args:
            row: Row index
            col: Column index

        Returns:
            bool: True if module is dark, False otherwise
        """
        if 0 <= row < self.size and 0 <= col < self.size:
            return self.matrix[row][col]
        return False

    def get_neighbors(
        self, row: int, col: int, neighborhood: str = "von_neumann"
    ) -> List[Tuple[int, int]]:
        """
        Get neighboring positions for a module.

        Args:
            row: Row position
            col: Column position
            neighborhood: 'von_neumann' (4-connected) or 'moore' (8-connected)

        Returns:
            List of valid neighbor positions
        """
        neighbors = []

        if neighborhood == "von_neumann":
            # 4-connected neighbors (cardinal directions)
            deltas = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        else:  # moore
            # 8-connected neighbors (cardinal + diagonal)
            deltas = [
                (-1, -1),
                (-1, 0),
                (-1, 1),
                (0, -1),
                (0, 1),
                (1, -1),
                (1, 0),
                (1, 1),
            ]

        for dr, dc in deltas:
            nr, nc = row + dr, col + dc
            if 0 <= nr < self.size and 0 <= nc < self.size:
                neighbors.append((nr, nc))

        return neighbors

    def get_weighted_neighbor_analysis(
        self, row: int, col: int, module_type: str = "data"
    ) -> NeighborAnalysis:
        """
        Enhanced neighbor analysis using Moore neighborhood (8-connected) with weighted connectivity.

        Returns comprehensive neighbor analysis including connectivity strength,
        flow direction, and shape hints for advanced rendering.

        Args:
            row: Row position
            col: Column position
            module_type: Type of module for weighting

        Returns:
            NeighborAnalysis model with comprehensive neighbor data

        Raises:
            IndexError: If row or col is out of bounds
        """
        # Validate bounds
        if not (0 <= row < self.size and 0 <= col < self.size):
            raise IndexError(
                f"Position ({row}, {col}) out of bounds for {self.size}x{self.size} matrix"
            )

        neighbors = self.get_neighbors(row, col, "moore")

        # Separate cardinal and diagonal neighbors
        cardinal_neighbors = []
        diagonal_neighbors = []

        cardinal_deltas = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for nr, nc in neighbors:
            dr, dc = nr - row, nc - col
            if (dr, dc) in cardinal_deltas:
                cardinal_neighbors.append(self.is_module_active(nr, nc))
            else:
                diagonal_neighbors.append(self.is_module_active(nr, nc))

        # Count active neighbors
        cardinal_count = sum(cardinal_neighbors)
        diagonal_count = sum(diagonal_neighbors)

        # Calculate weighted connectivity strength
        # Cardinal neighbors have full weight, diagonals have reduced weight
        connectivity_strength = cardinal_count + (diagonal_count * 0.7)

        # Flow weights based on module type
        flow_weights = {
            "finder": 0.5,
            "finder_inner": 0.3,
            "timing": 0.8,
            "data": 1.0,
            "alignment": 0.6,
            "format": 0.7,
        }

        weighted_strength = connectivity_strength * flow_weights.get(module_type, 1.0)

        # Determine flow direction (for pill shapes, etc.)
        horizontal_flow = 0.0
        vertical_flow = 0.0

        if len(cardinal_neighbors) >= 4:
            horizontal_flow = (
                cardinal_neighbors[2] + cardinal_neighbors[3]
            ) / 2  # left + right
            vertical_flow = (
                cardinal_neighbors[0] + cardinal_neighbors[1]
            ) / 2  # up + down

        # Get active neighbor positions
        active_neighbors = [
            (nr, nc) for nr, nc in neighbors if self.is_module_active(nr, nc)
        ]

        return NeighborAnalysis(
            cardinal_count=cardinal_count,
            diagonal_count=diagonal_count,
            connectivity_strength=connectivity_strength,
            weighted_strength=weighted_strength,
            horizontal_flow=horizontal_flow,
            vertical_flow=vertical_flow,
            flow_direction=(
                "horizontal" if horizontal_flow > vertical_flow else "vertical"
            ),
            isolation_level=4 - cardinal_count,
            corner_connections=diagonal_count,
            active_neighbors=active_neighbors,
        )
