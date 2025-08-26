"""Matrix manipulation orchestrator using composition pattern.

This module provides the new MatrixManipulator class that orchestrates
specialized components for centerpiece reserve functionality while
maintaining backward compatibility with the existing API.
"""

import logging
from typing import Any, Dict, List, Tuple

from ...config.models.visual import CenterpieceConfig
from ..detector import ModuleDetector
from ..geometry import CenterpieceGeometry
from .imprint_processor import ImprintProcessor
from .knockout_processor import KnockoutProcessor
from .matrix_validator import MatrixValidator, PatternAnalysis, ScanabilityAssessment
from .performance_monitor import CenterpiecePerformanceMonitor

logger = logging.getLogger(__name__)


class MatrixManipulator:
    """Handles matrix modifications for centerpiece reserve using composition.

    This class orchestrates specialized components to provide comprehensive
    centerpiece functionality while maintaining the original API for backward
    compatibility.

    Components:
        - CenterpieceGeometry: Pure geometric calculations
        - KnockoutProcessor: Handles knockout mode clearing
        - ImprintProcessor: Handles imprint mode processing
        - MatrixValidator: Validates matrix modifications
        - CenterpiecePerformanceMonitor: Performance tracking

    Attributes:
        ERROR_CORRECTION_CAPACITY: Maximum data loss capacity by error level
    """

    # Error correction capacities by level (maintained for compatibility)
    ERROR_CORRECTION_CAPACITY = {
        "L": 0.07,  # 7% recovery capability
        "M": 0.15,  # 15% recovery capability
        "Q": 0.25,  # 25% recovery capability
        "H": 0.30,  # 30% recovery capability
    }

    def __init__(self, matrix: List[List[bool]], detector: ModuleDetector):
        """Initialize the matrix manipulator with specialized components.

        Args:
            matrix: QR code matrix as 2D boolean list
            detector: Module detector instance for pattern identification

        Raises:
            ValueError: If matrix is invalid (empty, non-square, or malformed)
        """
        # Validate matrix
        if not matrix:
            raise ValueError("Matrix cannot be empty")

        if not all(isinstance(row, list) for row in matrix):
            raise ValueError("Matrix must be a list of lists")

        # Check if matrix is square
        expected_size = len(matrix)
        for i, row in enumerate(matrix):
            if len(row) != expected_size:
                raise ValueError(
                    f"Matrix must be square. Row {i} has length {len(row)}, expected {expected_size}"
                )

        self.matrix = matrix
        self.detector = detector
        self.size = len(matrix)

        # Initialize specialized components
        self.geometry = CenterpieceGeometry(self.size)
        self.knockout_processor = KnockoutProcessor(matrix, detector, self.geometry)
        self.imprint_processor = ImprintProcessor(matrix, detector, self.geometry)
        self.validator = MatrixValidator(matrix, detector, self.geometry)
        self.performance_monitor = CenterpiecePerformanceMonitor(matrix_size=self.size)

    # Geometry delegation methods (maintain original API)

    def calculate_safe_reserve_size(self, version: int, error_level: str) -> float:
        """Calculate maximum safe reserve size based on error correction.

        Args:
            version: QR code version (1-40)
            error_level: Error correction level ('L', 'M', 'Q', 'H')

        Returns:
            Maximum safe reserve size as a fraction of QR code area
        """
        return self.geometry.calculate_safe_reserve_size(version, error_level)

    def calculate_placement_offsets(self, config: CenterpieceConfig) -> Tuple[float, float]:
        """Calculate offset_x and offset_y based on placement mode.

        Args:
            config: CenterpieceConfig instance

        Returns:
            Tuple of (offset_x, offset_y) values
        """
        return self.geometry.calculate_placement_offsets(config)

    def get_module_bounds(self) -> Dict[str, int]:
        """Get bounds of all active modules in the matrix.

        Returns:
            Dict with 'left', 'top', 'right', 'bottom' keys representing
            the bounding box of all active (True) modules in the matrix
        """
        # Find bounds of all active modules
        left, right, top, bottom = None, None, None, None

        for row in range(len(self.matrix)):
            for col in range(len(self.matrix[row])):
                if self.matrix[row][col]:  # Active module
                    if left is None or col < left:
                        left = col
                    if right is None or col > right:
                        right = col
                    if top is None or row < top:
                        top = row
                    if bottom is None or row > bottom:
                        bottom = row

        # Handle empty matrix case
        if left is None:
            return {"left": 0, "top": 0, "right": 0, "bottom": 0}

        # At this point, all bounds must be non-None since left is not None
        assert left is not None and top is not None and right is not None and bottom is not None
        return {"left": left, "top": top, "right": right, "bottom": bottom}

    def get_centerpiece_bounds(self, config: CenterpieceConfig) -> Dict[str, int]:
        """Calculate centerpiece bounds in module coordinates.

        Args:
            config: CenterpieceConfig instance

        Returns:
            Dict with 'left', 'top', 'right', 'bottom' keys
        """
        x1, y1, x2, y2 = self.geometry.get_centerpiece_bounds(config)
        return {"left": x1, "top": y1, "right": x2, "bottom": y2}

    def is_in_centerpiece(self, row: int, col: int, config: CenterpieceConfig) -> bool:
        """Check if a module is within the centerpiece area.

        Args:
            row: Module row position
            col: Module column position
            config: CenterpieceConfig instance

        Returns:
            True if module is within centerpiece area
        """
        return self.geometry.is_in_centerpiece(row, col, config)

    # Matrix modification methods (main functionality)

    def clear_centerpiece_area(self, config: CenterpieceConfig) -> List[List[bool]]:
        """Clear modules in centerpiece area, preserving function patterns.

        This method orchestrates the appropriate processor based on the
        reserve mode configuration.

        Args:
            config: CenterpieceConfig instance

        Returns:
            Modified matrix with centerpiece area processed
        """
        # Import ReserveMode locally to avoid circular imports
        from ...config import ReserveMode

        # Start performance monitoring
        perf_context = self.performance_monitor.start_operation("centerpiece_clearing", config)

        try:
            logger.debug(
                f"Applying reserve mode: {config.mode.value if hasattr(config, 'mode') else 'knockout'}"
            )

            # Route to appropriate processor based on mode
            if hasattr(config, "mode") and config.mode == ReserveMode.IMPRINT:
                result: List[List[bool]] = self.imprint_processor.apply_imprint_mode(config)
                operation_type = "imprint_processing"
            else:
                result = self.knockout_processor.apply_knockout_mode(config)
                operation_type = "knockout_processing"

            # End performance monitoring
            warnings = self.performance_monitor.get_performance_warnings(config)
            self.performance_monitor.end_operation(perf_context, warnings)

            logger.debug(f"Successfully applied {operation_type}")
            return result

        except Exception as e:
            # End performance monitoring with error
            self.performance_monitor.end_operation(perf_context, [f"Error during processing: {str(e)}"])
            logger.error(f"Error during centerpiece processing: {e}")
            raise

    def apply_knockout_mode(self, config: CenterpieceConfig) -> List[List[bool]]:
        """Apply knockout mode - clear modules completely from reserve area.

        Args:
            config: CenterpieceConfig instance

        Returns:
            Modified matrix with centerpiece area cleared
        """
        # Start performance monitoring
        perf_context = self.performance_monitor.start_operation("knockout_processing", config)

        try:
            result: List[List[bool]] = self.knockout_processor.apply_knockout_mode(config)

            # End performance monitoring
            warnings = self.performance_monitor.get_performance_warnings(config)
            self.performance_monitor.end_operation(perf_context, warnings)

            return result

        except Exception as e:
            self.performance_monitor.end_operation(
                perf_context, [f"Error during knockout processing: {str(e)}"]
            )
            logger.error(f"Error during knockout processing: {e}")
            raise

    def apply_imprint_mode(self, config: CenterpieceConfig) -> List[List[bool]]:
        """Apply imprint mode - preserve modules underneath centerpiece for scanability.

        Args:
            config: CenterpieceConfig instance

        Returns:
            Original matrix (modules preserved for scanability)
        """
        # Start performance monitoring
        perf_context = self.performance_monitor.start_operation("imprint_processing", config)

        try:
            result: List[List[bool]] = self.imprint_processor.apply_imprint_mode(config)

            # End performance monitoring
            warnings = self.performance_monitor.get_performance_warnings(config)
            self.performance_monitor.end_operation(perf_context, warnings)

            return result

        except Exception as e:
            self.performance_monitor.end_operation(
                perf_context, [f"Error during imprint processing: {str(e)}"]
            )
            logger.error(f"Error during imprint processing: {e}")
            raise

    # Validation methods

    def validate_reserve_impact(self, config: CenterpieceConfig, error_level: str) -> Dict[str, Any]:
        """Validate the impact of a centerpiece configuration.

        Args:
            config: CenterpieceConfig instance
            error_level: QR error correction level ("L", "M", "Q", "H")

        Returns:
            Dictionary with validation results including 'safe', 'estimated_modules', 'warnings'
        """
        # Calculate estimated modules that would be affected
        x1, y1, x2, y2 = self.geometry.get_centerpiece_bounds(config)
        area_width = x2 - x1
        area_height = y2 - y1
        estimated_modules = area_width * area_height

        # Get configuration validation
        is_valid, warnings = self.validator.validate_centerpiece_configuration(config)

        # Calculate safety based on error correction capacity
        total_modules = len(self.matrix) * len(self.matrix[0]) if self.matrix else 0
        affected_ratio = estimated_modules / total_modules if total_modules > 0 else 0

        # Simple safety heuristics based on error correction level
        safety_thresholds = {"L": 0.07, "M": 0.15, "Q": 0.25, "H": 0.30}
        threshold = safety_thresholds.get(error_level, 0.15)
        safe = affected_ratio <= threshold and is_valid

        return {
            "safe": safe,
            "estimated_modules": estimated_modules,
            "affected_ratio": affected_ratio,
            "warnings": warnings,
            "error_correction_level": error_level,
            "threshold_used": threshold,
        }

    def _validate_reserve_impact_matrices(
        self,
        original_matrix: List[List[bool]],
        modified_matrix: List[List[bool]],
        error_level: str,
    ) -> Tuple[bool, str]:
        """Validate that reserve doesn't compromise QR functionality.

        Args:
            original_matrix: Original unmodified matrix
            modified_matrix: Matrix with centerpiece cleared
            error_level: Error correction level

        Returns:
            Tuple of (is_valid, message) indicating validation result
        """
        # Start performance monitoring
        perf_context = self.performance_monitor.start_operation("matrix_validation", None)

        try:
            result = self.validator.validate_reserve_impact(original_matrix, modified_matrix, error_level)

            # End performance monitoring
            self.performance_monitor.end_operation(perf_context)

            return result

        except Exception as e:
            self.performance_monitor.end_operation(perf_context, [f"Error during validation: {str(e)}"])
            logger.error(f"Error during validation: {e}")
            raise

    def validate_centerpiece_configuration(self, config: CenterpieceConfig) -> Tuple[bool, List[str]]:
        """Validate centerpiece configuration for potential issues.

        Args:
            config: CenterpieceConfig instance

        Returns:
            Tuple of (is_valid, warnings_list)
        """
        return self.validator.validate_centerpiece_configuration(config)

    def analyze_pattern_preservation(self, config: CenterpieceConfig) -> PatternAnalysis:
        """Analyze how well critical QR patterns are preserved.

        Args:
            config: CenterpieceConfig instance

        Returns:
            Dictionary with pattern preservation analysis
        """
        return self.validator.analyze_pattern_preservation(config)

    def get_scanability_assessment(
        self, config: CenterpieceConfig, modified_matrix: List[List[bool]]
    ) -> ScanabilityAssessment:
        """Provide comprehensive scanability assessment for the modified matrix.

        Args:
            config: CenterpieceConfig instance
            modified_matrix: Matrix with centerpiece modifications

        Returns:
            Dictionary with scanability assessment
        """
        return self.validator.get_scanability_assessment(config, modified_matrix)

    # Metadata and information methods

    def get_centerpiece_metadata(self, config: CenterpieceConfig) -> Dict[str, Any]:
        """Get metadata about the centerpiece area for SVG generation.

        Args:
            config: CenterpieceConfig instance

        Returns:
            Dictionary with centerpiece bounds and properties
        """
        # Import ReserveMode locally to avoid circular imports
        from ...config import ReserveMode

        x1, y1, x2, y2 = self.geometry.get_centerpiece_bounds(config)

        # Convert to pixel coordinates based on standard scale
        # This will be adjusted by the actual scale during SVG generation

        # Calculate area info
        area_width = x2 - x1
        area_height = y2 - y1
        estimated_modules = area_width * area_height

        # Calculate center coordinates using the same logic as geometry
        offset_x, offset_y = self.geometry.calculate_placement_offsets(config)
        center_x = self.size / 2 + (offset_x * self.size)
        center_y = self.size / 2 + (offset_y * self.size)

        metadata = {
            "bounds": {"x": x1, "y": y1, "width": area_width, "height": area_height},
            "center": {"x": center_x, "y": center_y},
            "shape": config.shape,
            "mode": config.mode if hasattr(config, "mode") else ReserveMode.KNOCKOUT,
            "area_info": {
                "estimated_modules": estimated_modules,
                "width": area_width,
                "height": area_height,
                "area_ratio": (
                    estimated_modules / (len(self.matrix) * len(self.matrix[0])) if self.matrix else 0
                ),
            },
        }

        # Add mode-specific metadata
        if hasattr(config, "mode") and config.mode == ReserveMode.IMPRINT:
            # Get stored imprint metadata if available (from apply_imprint_mode call)
            imprint_metadata = self.get_imprint_metadata()

            if imprint_metadata:
                # Use comprehensive metadata from imprint operation
                metadata.update(
                    {
                        "imprinted_modules": imprint_metadata.get("imprinted_modules", []),
                        "preserve_scanability": True,
                        "visual_effects": imprint_metadata.get("visual_effects", {}),
                        "imprint_treatments": [
                            {
                                "x": module["col"],
                                "y": module["row"],
                                "opacity": module.get("visual_treatment", {}).get("opacity", 0.7),
                                "size_ratio": module.get("visual_treatment", {}).get("size_ratio", 1.0),
                                "type": module.get("type", "data"),
                            }
                            for module in imprint_metadata.get("imprinted_modules", [])
                        ],
                    }
                )
            else:
                # Fallback: collect basic imprint modules (backward compatibility)
                imprinted_modules = []
                protected_patterns = {
                    "finder",
                    "finder_inner",
                    "timing",
                    "alignment",
                    "format",
                    "version",
                    "dark",
                    "separator",
                }

                for row in range(self.size):
                    for col in range(self.size):
                        if self.geometry.is_in_centerpiece(row, col, config):
                            if self.matrix[row][col]:  # Only dark modules
                                module_type = self.detector.get_module_type(row, col)
                                if module_type not in protected_patterns:
                                    imprinted_modules.append({"row": row, "col": col, "type": module_type})

                # Generate basic imprint treatments for fallback
                imprint_treatments = [
                    {
                        "x": module["col"],
                        "y": module["row"],
                        "opacity": 0.7,  # Default opacity
                        "size_ratio": 1.0,  # Default size ratio
                        "type": module["type"],
                    }
                    for module in imprinted_modules
                ]

                metadata.update(
                    {
                        "imprinted_modules": imprinted_modules,
                        "preserve_scanability": True,
                        "imprint_treatments": imprint_treatments,
                    }
                )
        else:
            # Knockout mode - add cleared modules information
            cleared_modules = []
            for row in range(self.size):
                for col in range(self.size):
                    if self.geometry.is_in_centerpiece(row, col, config):
                        if self.matrix[row][col]:  # Only dark modules that would be cleared
                            module_type = (
                                self.detector.get_module_type(row, col) if self.detector else "unknown"
                            )
                            # Skip function patterns (they are preserved)
                            protected_patterns = {
                                "finder",
                                "finder_inner",
                                "timing",
                                "alignment",
                                "format",
                                "version",
                                "dark",
                                "separator",
                            }
                            if module_type not in protected_patterns:
                                cleared_modules.append({"row": row, "col": col, "type": module_type})

            metadata.update({"cleared_modules": cleared_modules, "preserve_scanability": False})

        return {
            **metadata,
            "module_coords": True,  # Indicates these are in module coordinates
            "offset": {"x": config.offset_x, "y": config.offset_y},
            "size": config.size,
            "margin": config.margin,
        }

    def get_imprint_metadata(self) -> Dict[str, Any]:
        """Get stored imprint metadata from the last imprint operation.

        Returns:
            Imprint metadata dictionary, or empty dict if no imprint operation performed
        """
        return self.imprint_processor.get_imprint_metadata()

    # Performance methods

    def get_performance_warnings(self, config: CenterpieceConfig) -> List[str]:
        """Get performance warnings for centerpiece configuration.

        Args:
            config: CenterpieceConfig instance

        Returns:
            List of performance warning messages
        """
        return self.performance_monitor.get_performance_warnings(config)

    def get_comprehensive_performance_warnings(self, config: CenterpieceConfig) -> List[str]:
        """Get comprehensive performance warnings including configuration and runtime metrics.

        Args:
            config: CenterpieceConfig instance

        Returns:
            List of all performance warning messages
        """
        return self.performance_monitor.get_comprehensive_performance_warnings(config)

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary.

        Returns:
            Dictionary with performance summary
        """
        return self.performance_monitor.get_performance_summary()

    # Utility methods for backward compatibility

    def _is_edge_module(self, row: int, col: int, config: CenterpieceConfig) -> bool:
        """Check if a module is on the edge of the centerpiece area.

        Args:
            row: Module row position
            col: Module column position
            config: CenterpieceConfig instance

        Returns:
            True if module is on the edge of the centerpiece
        """
        return self.geometry.is_edge_module(row, col, config)

    def _should_clear_edge_module(
        self,
        row: int,
        col: int,
        config: CenterpieceConfig,
        modified_matrix: List[List[bool]],
    ) -> bool:
        """Determine if an edge module should be cleared for smoother boundaries.

        Args:
            row: Module row position
            col: Module column position
            config: CenterpieceConfig instance
            modified_matrix: Current state of the matrix

        Returns:
            True if edge module should be cleared
        """
        return self.geometry.should_clear_edge_module(row, col, config, modified_matrix)

    # Methods delegated to components for backward compatibility

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
        return self.imprint_processor._get_imprint_visual_treatment(row, col, config, module_type)

    def _calculate_imprint_opacity(self, config: CenterpieceConfig) -> float:
        """Calculate base opacity for imprinted modules.

        Args:
            config: CenterpieceConfig instance

        Returns:
            Base opacity value (0.0-1.0)
        """
        return self.imprint_processor._calculate_imprint_opacity(config)

    def _calculate_imprint_color_shift(self, config: CenterpieceConfig) -> Dict[str, float]:
        """Calculate color shift parameters for imprinted modules.

        Args:
            config: CenterpieceConfig instance

        Returns:
            Color adjustment parameters
        """
        return self.imprint_processor._calculate_imprint_color_shift(config)

    def _calculate_imprint_size_ratio(self, config: CenterpieceConfig) -> float:
        """Calculate size adjustment ratio for imprinted modules.

        Args:
            config: CenterpieceConfig instance

        Returns:
            Size ratio multiplier (0.0-1.0)
        """
        return self.imprint_processor._calculate_imprint_size_ratio(config)

    def _calculate_color_shift_for_distance(self, normalized_distance: float) -> Dict[str, float]:
        """Calculate color shift based on distance from centerpiece center.

        Args:
            normalized_distance: Distance from center (0.0-1.0)

        Returns:
            Distance-based color adjustment parameters
        """
        return self.imprint_processor._calculate_color_shift_for_distance(normalized_distance)

    # Component access methods (for advanced usage)

    def get_geometry_component(self) -> CenterpieceGeometry:
        """Get the geometry calculation component."""
        return self.geometry

    def get_knockout_processor(self) -> KnockoutProcessor:
        """Get the knockout processor component."""
        return self.knockout_processor

    def get_imprint_processor(self) -> ImprintProcessor:
        """Get the imprint processor component."""
        return self.imprint_processor

    def get_validator(self) -> MatrixValidator:
        """Get the matrix validator component."""
        return self.validator

    def get_performance_monitor(self) -> CenterpiecePerformanceMonitor:
        """Get the performance monitor component."""
        return self.performance_monitor
