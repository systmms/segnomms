"""Knockout mode processor for centerpiece clearing operations.

This module handles knockout mode centerpiece clearing with enhanced edge
refinement and statistical tracking for optimal scanability preservation.
"""

import logging
from typing import Any, Dict, List, Tuple

from ..detector import ModuleDetector
from ..geometry import CenterpieceGeometry
from ..performance import measure_centerpiece_operation

logger = logging.getLogger(__name__)


class KnockoutProcessor:
    """Handles knockout mode centerpiece clearing operations.

    This processor completely clears modules from the centerpiece area
    while preserving critical QR code patterns and providing smart edge
    refinement for smoother boundaries.
    """

    def __init__(
        self,
        matrix: List[List[bool]],
        detector: ModuleDetector,
        geometry: CenterpieceGeometry,
    ):
        """Initialize the knockout processor.

        Args:
            matrix: QR code matrix as 2D boolean list
            detector: Module detector instance for pattern identification
            geometry: Geometry calculator for centerpiece calculations
        """
        self.matrix = matrix
        self.detector = detector
        self.geometry = geometry
        self.size = len(matrix)

        # Protected patterns that should never be cleared
        self._protected_patterns = {
            "finder",
            "finder_inner",
            "timing",
            "alignment",
            "format",
            "version",
            "dark",
            "separator",
        }

    @measure_centerpiece_operation
    def apply_knockout_mode(self, config) -> List[List[bool]]:
        """Apply knockout mode - clear modules completely from reserve area.

        This implementation provides enhanced edge handling and statistical tracking
        for better centerpiece clearing with optimal scanability preservation.

        Args:
            config: CenterpieceConfig instance

        Returns:
            Modified matrix with centerpiece area cleared
        """
        # Create a deep copy of the matrix
        modified = [row[:] for row in self.matrix]

        # Track clearing statistics
        stats = {
            "total_checked": 0,
            "in_centerpiece": 0,
            "function_patterns_preserved": 0,
            "data_modules_cleared": 0,
            "edge_modules_refined": 0,
        }

        # First pass: identify all modules in centerpiece area
        centerpiece_modules, edge_modules = self._collect_centerpiece_modules(
            config, stats
        )

        # Second pass: clear modules with edge refinement
        modified = self._clear_modules_with_refinement(
            modified, centerpiece_modules, edge_modules, config, stats
        )

        # Log statistics and performance warnings
        self._log_clearing_results(stats)

        return modified

    def _collect_centerpiece_modules(
        self, config, stats: Dict[str, Any]
    ) -> Tuple[List, List]:
        """Collect centerpiece and edge modules for processing.

        Args:
            config: CenterpieceConfig instance
            stats: Statistics tracking dictionary

        Returns:
            Tuple of (centerpiece_modules, edge_modules) lists
        """
        centerpiece_modules = []
        edge_modules = []

        for row in range(self.size):
            for col in range(self.size):
                stats["total_checked"] += 1

                if self.geometry.is_in_centerpiece(row, col, config):
                    stats["in_centerpiece"] += 1
                    module_type = self.detector.get_module_type(row, col)

                    # Check if this is a protected pattern
                    if module_type in self._protected_patterns:
                        stats["function_patterns_preserved"] += 1
                        continue

                    # Check if this is an edge module (for refinement)
                    is_edge = self.geometry.is_edge_module(row, col, config)

                    if is_edge:
                        edge_modules.append((row, col, module_type))
                    else:
                        centerpiece_modules.append((row, col, module_type))

        return centerpiece_modules, edge_modules

    def _clear_modules_with_refinement(
        self,
        modified: List[List[bool]],
        centerpiece_modules: List,
        edge_modules: List,
        config,
        stats: Dict[str, Any],
    ) -> List[List[bool]]:
        """Clear centerpiece modules with edge refinement.

        Args:
            modified: Matrix to modify
            centerpiece_modules: List of centerpiece modules to clear
            edge_modules: List of edge modules to process
            config: CenterpieceConfig instance
            stats: Statistics tracking dictionary

        Returns:
            Modified matrix with cleared modules
        """
        # Clear all centerpiece modules (non-edge)
        for row, col, module_type in centerpiece_modules:
            if modified[row][col]:  # Only count if it was dark
                stats["data_modules_cleared"] += 1
            modified[row][col] = False

        # Edge refinement: apply smart edge handling for smoother boundaries
        for row, col, module_type in edge_modules:
            should_clear = self.geometry.should_clear_edge_module(
                row, col, config, modified
            )

            if should_clear:
                if modified[row][col]:  # Only count if it was dark
                    stats["data_modules_cleared"] += 1
                    stats["edge_modules_refined"] += 1
                modified[row][col] = False

        return modified

    def _log_clearing_results(self, stats: Dict[str, Any]) -> None:
        """Log clearing statistics and performance warnings.

        Args:
            stats: Statistics tracking dictionary
        """
        logger.debug(f"Knockout mode statistics: {stats}")

        # Performance warning for large centerpieces
        if stats["data_modules_cleared"] > 100:
            logger.warning(
                f"Large centerpiece cleared {stats['data_modules_cleared']} modules. "
                f"Consider reducing size for optimal scanability."
            )

    def get_clearing_statistics(self, config) -> Dict[str, Any]:
        """Get statistics about what would be cleared without modifying the matrix.

        Args:
            config: CenterpieceConfig instance

        Returns:
            Dictionary with clearing statistics
        """
        stats = {
            "total_checked": 0,
            "in_centerpiece": 0,
            "function_patterns_preserved": 0,
            "data_modules_would_clear": 0,
            "edge_modules_would_refine": 0,
        }

        centerpiece_modules, edge_modules = self._collect_centerpiece_modules(
            config, stats
        )

        # Count what would be cleared
        for row, col, module_type in centerpiece_modules:
            if self.matrix[row][col]:  # Only count if it's currently dark
                stats["data_modules_would_clear"] += 1

        for row, col, module_type in edge_modules:
            if self.geometry.should_clear_edge_module(row, col, config, self.matrix):
                if self.matrix[row][col]:  # Only count if it's currently dark
                    stats["data_modules_would_refine"] += 1

        return stats
