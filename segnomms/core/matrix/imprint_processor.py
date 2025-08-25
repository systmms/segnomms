"""Imprint mode processor for centerpiece visual treatment operations.

This module handles imprint mode processing where QR modules are preserved
for scanability but receive special visual treatment for rendering underneath
centerpiece overlays.
"""

import logging
from typing import Any, Dict, List

from ...config import CenterpieceConfig
from ..detector import ModuleDetector
from ..geometry import CenterpieceGeometry
from ..performance import measure_imprint_rendering

logger = logging.getLogger(__name__)


class ImprintProcessor:
    """Handles imprint mode processing and visual treatment calculations.

    In imprint mode, QR modules remain scannable but are visually modified
    for special rendering to indicate they are underneath the centerpiece overlay.
    This processor preserves the matrix structure while collecting metadata about
    modules that should receive special visual treatment.
    """

    def __init__(
        self,
        matrix: List[List[bool]],
        detector: ModuleDetector,
        geometry: CenterpieceGeometry,
    ):
        """Initialize the imprint processor.

        Args:
            matrix: QR code matrix as 2D boolean list
            detector: Module detector instance for pattern identification
            geometry: Geometry calculator for centerpiece calculations
        """
        self.matrix = matrix
        self.detector = detector
        self.geometry = geometry
        self.size = len(matrix)
        self._imprint_metadata: Dict[str, Any] = {}

        # Protected patterns that should never be visually modified even in imprint mode
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

    @measure_imprint_rendering
    def apply_imprint_mode(self, config: CenterpieceConfig) -> List[List[bool]]:
        """Apply imprint mode - preserve modules underneath centerpiece for scanability.

        In imprint mode, the QR modules remain scannable but are visually modified
        for special rendering to indicate they are underneath the centerpiece overlay.
        This method preserves the matrix structure while collecting metadata about
        modules that should receive special visual treatment.

        Args:
            config: CenterpieceConfig instance

        Returns:
            Original matrix (modules preserved for scanability)
        """
        # Create a deep copy of the matrix (preserving scanability)
        preserved_matrix = [row[:] for row in self.matrix]

        # Track imprint statistics
        stats = {
            "total_checked": 0,
            "in_centerpiece": 0,
            "function_patterns_preserved": 0,
            "data_modules_imprinted": 0,
            "protected_modules": 0,
        }

        # Collect modules for visual imprinting without modifying the matrix
        imprinted_modules = self._collect_imprinted_modules(config, stats)

        # Store comprehensive imprint metadata for rendering system
        self._store_imprint_metadata(imprinted_modules, stats, config)

        # Log results and warnings
        self._log_imprint_results(stats)

        # Return original matrix unchanged for full scanability
        return preserved_matrix

    def _collect_imprinted_modules(
        self, config: CenterpieceConfig, stats: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Collect modules that need visual imprinting treatment.

        Args:
            config: CenterpieceConfig instance
            stats: Statistics tracking dictionary

        Returns:
            List of imprinted module information dictionaries
        """
        imprinted_modules = []

        for row in range(self.size):
            for col in range(self.size):
                stats["total_checked"] += 1

                if self.geometry.is_in_centerpiece(row, col, config):
                    stats["in_centerpiece"] += 1
                    module_type = self.detector.get_module_type(row, col)

                    # Check if this is a protected pattern
                    if module_type in self._protected_patterns:
                        stats["function_patterns_preserved"] += 1
                        stats["protected_modules"] += 1
                        continue

                    # Only track dark modules for imprinting
                    # (preserve light modules as-is)
                    if self.matrix[row][col]:  # Dark module
                        stats["data_modules_imprinted"] += 1

                        # Store module information for rendering system
                        imprinted_modules.append(
                            {
                                "row": row,
                                "col": col,
                                "type": module_type,
                                "original_state": True,  # Was dark
                                "visual_treatment": self._get_imprint_visual_treatment(
                                    row, col, config, module_type
                                ),
                            }
                        )

        return imprinted_modules

    def _store_imprint_metadata(
        self,
        imprinted_modules: List[Dict[str, Any]],
        stats: Dict[str, Any],
        config: CenterpieceConfig,
    ) -> None:
        """Store imprint metadata for later use by rendering system.

        Args:
            imprinted_modules: List of modules needing visual treatment
            stats: Processing statistics
            config: CenterpieceConfig instance
        """
        self._imprint_metadata = {
            "imprinted_modules": imprinted_modules,
            "statistics": stats,
            "centerpiece_bounds": self.geometry.get_centerpiece_bounds(config),
            "preserve_scanability": True,
            "visual_effects": {
                "opacity_reduction": self._calculate_imprint_opacity(config),
                "color_adjustment": self._calculate_imprint_color_shift(config),
                "size_adjustment": self._calculate_imprint_size_ratio(config),
            },
        }

    def _log_imprint_results(self, stats: Dict[str, Any]) -> None:
        """Log imprint processing results and warnings.

        Args:
            stats: Processing statistics
        """
        logger.debug(f"Imprint mode statistics: {stats}")

        # Performance warning for complex imprint areas
        if stats["data_modules_imprinted"] > 150:
            logger.warning(
                f"Large imprint area covers {stats['data_modules_imprinted']} modules. "
                f"Consider reducing centerpiece size for optimal visual clarity."
            )

    def _get_imprint_visual_treatment(
        self, row: int, col: int, config: CenterpieceConfig, module_type: str
    ) -> Dict[str, Any]:
        """Calculate visual treatment parameters for an imprinted module.

        Args:
            row: Module row position
            col: Module column position
            config: CenterpieceConfig instance
            module_type: Type of module

        Returns:
            Dictionary with visual treatment parameters
        """
        # Calculate effective offsets for consistent positioning
        offset_x, offset_y = self.geometry.calculate_placement_offsets(config)

        # Calculate distance from centerpiece center for gradient effects
        center_x = self.size / 2 + (offset_x * self.size)
        center_y = self.size / 2 + (offset_y * self.size)

        # Distance from center (normalized)
        dist_from_center = ((col - center_x) ** 2 + (row - center_y) ** 2) ** 0.5
        max_radius = config.size * self.size / 2

        # Normalize distance (0.0 = center, 1.0 = edge of centerpiece)
        normalized_distance = (
            min(dist_from_center / max_radius, 1.0) if max_radius > 0 else 0.0
        )

        # Calculate visual effects based on distance and module type
        base_opacity = 0.3  # Base opacity for imprinted modules
        distance_opacity_boost = normalized_distance * 0.4  # Fade towards edges

        # Module type adjustments
        type_adjustments = {
            "data": {"opacity_boost": 0.0, "size_factor": 1.0},
            "format": {
                "opacity_boost": 0.2,
                "size_factor": 0.9,
            },  # Slightly more visible
            "version": {"opacity_boost": 0.2, "size_factor": 0.9},
            "alignment": {"opacity_boost": 0.1, "size_factor": 0.95},
        }

        adjustment = type_adjustments.get(
            module_type, {"opacity_boost": 0.0, "size_factor": 1.0}
        )

        return {
            "opacity": min(
                base_opacity + distance_opacity_boost + adjustment["opacity_boost"], 1.0
            ),
            "size_ratio": adjustment["size_factor"],
            "color_shift": self._calculate_color_shift_for_distance(
                normalized_distance
            ),
            "blur_radius": max(
                0, (1.0 - normalized_distance) * 0.5
            ),  # More blur at center
            "distance_from_center": normalized_distance,
        }

    def _calculate_imprint_opacity(self, config: CenterpieceConfig) -> float:
        """Calculate base opacity for imprinted modules.

        Args:
            config: CenterpieceConfig instance

        Returns:
            Base opacity value (0.0-1.0)
        """
        # Base opacity varies by centerpiece size
        # Larger centerpieces need more transparency to maintain visual balance
        size_factor = config.size

        if size_factor <= 0.1:
            return 0.6  # Small centerpiece, modules more visible
        elif size_factor <= 0.2:
            return 0.4  # Medium centerpiece
        elif size_factor <= 0.3:
            return 0.3  # Large centerpiece
        else:
            return 0.2  # Very large centerpiece, very subtle modules

    def _calculate_imprint_color_shift(
        self, config: CenterpieceConfig
    ) -> Dict[str, float]:
        """Calculate color shift parameters for imprinted modules.

        Args:
            config: CenterpieceConfig instance

        Returns:
            Color adjustment parameters
        """
        # Color adjustments to make modules blend with potential centerpiece overlay
        return {
            "brightness_reduction": 0.3,  # Make modules lighter
            "saturation_reduction": 0.2,  # Reduce color intensity
            "hue_shift": 0.0,  # No hue change by default
            "contrast_reduction": 0.4,  # Reduce contrast with background
        }

    def _calculate_imprint_size_ratio(self, config: CenterpieceConfig) -> float:
        """Calculate size adjustment ratio for imprinted modules.

        Args:
            config: CenterpieceConfig instance

        Returns:
            Size ratio multiplier (0.0-1.0)
        """
        # Slightly reduce module size for imprint mode to create space for overlay
        # Size reduction varies by centerpiece size
        size_factor = config.size

        if size_factor <= 0.1:
            return 0.95  # Minimal reduction for small centerpieces
        elif size_factor <= 0.2:
            return 0.9  # Moderate reduction
        elif size_factor <= 0.3:
            return 0.85  # More reduction for large centerpieces
        else:
            return 0.8  # Maximum reduction for very large centerpieces

    def _calculate_color_shift_for_distance(
        self, normalized_distance: float
    ) -> Dict[str, float]:
        """Calculate color shift based on distance from centerpiece center.

        Args:
            normalized_distance: Distance from center (0.0-1.0)

        Returns:
            Distance-based color adjustment parameters
        """
        # Modules closer to center get more adjustment
        center_intensity = 1.0 - normalized_distance

        return {
            "brightness_boost": center_intensity * 0.2,  # Brighten center modules
            "alpha_reduction": center_intensity * 0.3,  # More transparency at center
            "edge_sharpness": normalized_distance
            * 0.5,  # Sharper edges away from center
        }

    def get_imprint_metadata(self) -> Dict[str, Any]:
        """Get stored imprint metadata from the last imprint operation.

        Returns:
            Imprint metadata dictionary, or empty dict if no imprint operation performed
        """
        return self._imprint_metadata.copy()

    def clear_imprint_metadata(self) -> None:
        """Clear stored imprint metadata."""
        self._imprint_metadata = {}

    def has_imprint_data(self) -> bool:
        """Check if imprint metadata is available.

        Returns:
            True if imprint metadata is stored
        """
        return bool(self._imprint_metadata)
