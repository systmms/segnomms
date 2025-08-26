"""Matrix validation for centerpiece modifications and QR functionality.

This module validates matrix modifications to ensure they don't compromise
QR code functionality while providing detailed feedback about validation results.
"""

import logging
from typing import Any, Dict, List, Tuple, TypedDict

from ..detector import ModuleDetector
from ..geometry import CenterpieceGeometry


class PatternStats(TypedDict):
    """Statistics for pattern preservation analysis."""

    preserved: int
    affected: int


class PatternAnalysis(TypedDict):
    """Analysis of QR pattern preservation."""

    finder_patterns: PatternStats
    timing_patterns: PatternStats
    alignment_patterns: PatternStats
    format_info: PatternStats
    version_info: PatternStats
    critical_violations: List[str]
    preservation_score: float


class IntegrityReport(TypedDict):
    """Matrix integrity validation report."""

    finder_patterns_intact: bool
    timing_patterns_intact: bool
    data_regions_accessible: bool
    structural_issues: List[str]
    recommendations: List[str]


class ScanabilityAssessment(TypedDict):
    """Comprehensive scanability assessment."""

    overall_score: float
    pattern_integrity: float
    data_preservation: float
    visual_clarity: float
    error_tolerance: float
    recommendations: List[str]
    risk_factors: List[str]


logger = logging.getLogger(__name__)


class MatrixValidator:
    """Validates matrix modifications for QR code functionality preservation.

    This validator ensures that centerpiece modifications don't exceed safe
    thresholds and provides detailed analysis of the impact on QR functionality.
    """

    # Error correction capacities by level
    ERROR_CORRECTION_CAPACITY = {
        "L": 0.07,  # 7% recovery capability
        "M": 0.15,  # 15% recovery capability
        "Q": 0.25,  # 25% recovery capability
        "H": 0.30,  # 30% recovery capability
    }

    def __init__(
        self,
        matrix: List[List[bool]],
        detector: ModuleDetector,
        geometry: CenterpieceGeometry,
    ):
        """Initialize the matrix validator.

        Args:
            matrix: QR code matrix as 2D boolean list
            detector: Module detector instance for pattern identification
            geometry: Geometry calculator for centerpiece calculations
        """
        self.matrix = matrix
        self.detector = detector
        self.geometry = geometry
        self.size = len(matrix)

    def validate_reserve_impact(
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
        # Count total data modules and cleared modules
        total_modules = sum(sum(row) for row in original_matrix)
        cleared_modules = 0

        for row in range(self.size):
            for col in range(self.size):
                if original_matrix[row][col] and not modified_matrix[row][col]:
                    cleared_modules += 1

        # Calculate percentage cleared
        if total_modules > 0:
            cleared_percentage = cleared_modules / total_modules
        else:
            cleared_percentage = 0

        # Get safe threshold
        safe_threshold = (
            self.ERROR_CORRECTION_CAPACITY.get(error_level.upper(), 0.15) * 0.8
        )

        if cleared_percentage > safe_threshold:
            return False, (
                f"Cleared {cleared_percentage:.1%} of modules exceeds "
                f"safe threshold of {safe_threshold:.1%} for error level {error_level}"
            )

        return (
            True,
            f"Cleared {cleared_percentage:.1%} of modules is within safe limits",
        )

    def validate_centerpiece_configuration(self, config: Any) -> Tuple[bool, List[str]]:
        """Validate centerpiece configuration for potential issues.

        Args:
            config: CenterpieceConfig instance

        Returns:
            Tuple of (is_valid, warnings_list)
        """
        warnings = []
        is_valid = True

        # Check size limits
        if config.size > 0.4:
            warnings.append(
                f"Large centerpiece size ({config.size:.1%}) may severely impact scanability"
            )
            is_valid = False
        elif config.size > 0.3:
            warnings.append(
                f"Centerpiece size ({config.size:.1%}) approaches safe limits"
            )

        # Check margin constraints
        if config.margin > 10:
            warnings.append(
                f"Large margin ({config.margin} modules) significantly increases impact area"
            )
        elif config.margin < 0:
            warnings.append("Negative margin may cause visual artifacts")
            is_valid = False

        # Check offset bounds
        if abs(config.offset_x) > 0.5 or abs(config.offset_y) > 0.5:
            warnings.append(
                f"Large offsets ({config.offset_x}, {config.offset_y}) may place centerpiece near critical patterns"
            )

        # Validate shape-specific constraints
        if config.shape == "squircle":
            area = self._estimate_centerpiece_area(config)
            if area > 200:  # Arbitrary threshold for complex calculations
                warnings.append(
                    "Complex squircle shapes with large areas may impact performance"
                )

        # Check for potential finder pattern conflicts
        if self._conflicts_with_finder_patterns(config):
            warnings.append("Centerpiece may overlap with critical finder patterns")
            is_valid = False

        return is_valid, warnings

    def analyze_pattern_preservation(self, config: Any) -> PatternAnalysis:
        """Analyze how well critical QR patterns are preserved with the given configuration.

        Args:
            config: CenterpieceConfig instance

        Returns:
            Dictionary with pattern preservation analysis
        """
        analysis: PatternAnalysis = {
            "finder_patterns": {"preserved": 0, "affected": 0},
            "timing_patterns": {"preserved": 0, "affected": 0},
            "alignment_patterns": {"preserved": 0, "affected": 0},
            "format_info": {"preserved": 0, "affected": 0},
            "version_info": {"preserved": 0, "affected": 0},
            "critical_violations": [],
            "preservation_score": 0.0,
        }

        # Check each critical pattern type
        self._analyze_finder_patterns(config, analysis)
        self._analyze_timing_patterns(config, analysis)
        self._analyze_alignment_patterns(config, analysis)
        self._analyze_format_info(config, analysis)
        self._analyze_version_info(config, analysis)

        # Calculate overall preservation score
        total_critical = (
            analysis["finder_patterns"]["preserved"]
            + analysis["finder_patterns"]["affected"]
            + analysis["timing_patterns"]["preserved"]
            + analysis["timing_patterns"]["affected"]
        )

        if total_critical > 0:
            preservation_score = (
                analysis["finder_patterns"]["preserved"]
                + analysis["timing_patterns"]["preserved"]
            ) / total_critical
            analysis["preservation_score"] = preservation_score
        else:
            analysis["preservation_score"] = 1.0

        return analysis

    def validate_matrix_integrity(
        self, modified_matrix: List[List[bool]]
    ) -> Tuple[bool, IntegrityReport]:
        """Validate the structural integrity of a modified matrix.

        Args:
            modified_matrix: Matrix with centerpiece modifications

        Returns:
            Tuple of (is_valid, integrity_report)
        """
        integrity_report: IntegrityReport = {
            "finder_patterns_intact": True,
            "timing_patterns_intact": True,
            "data_regions_accessible": True,
            "structural_issues": [],
            "recommendations": [],
        }

        # Check finder pattern integrity
        if not self._verify_finder_patterns(modified_matrix):
            integrity_report["finder_patterns_intact"] = False
            integrity_report["structural_issues"].append("Finder patterns compromised")

        # Check timing pattern integrity
        if not self._verify_timing_patterns(modified_matrix):
            integrity_report["timing_patterns_intact"] = False
            integrity_report["structural_issues"].append("Timing patterns compromised")

        # Check data region accessibility
        if not self._verify_data_accessibility(modified_matrix):
            integrity_report["data_regions_accessible"] = False
            integrity_report["structural_issues"].append(
                "Critical data regions inaccessible"
            )

        # Generate recommendations
        if integrity_report["structural_issues"]:
            integrity_report["recommendations"].extend(
                self._generate_integrity_recommendations(integrity_report)
            )

        is_valid = (
            integrity_report["finder_patterns_intact"]
            and integrity_report["timing_patterns_intact"]
            and integrity_report["data_regions_accessible"]
        )

        return is_valid, integrity_report

    def get_scanability_assessment(
        self, config: Any, modified_matrix: List[List[bool]]
    ) -> ScanabilityAssessment:
        """Provide comprehensive scanability assessment for the modified matrix.

        Args:
            config: CenterpieceConfig instance
            modified_matrix: Matrix with centerpiece modifications

        Returns:
            Dictionary with scanability assessment
        """
        assessment: ScanabilityAssessment = {
            "overall_score": 0.0,
            "pattern_integrity": 0.0,
            "data_preservation": 0.0,
            "visual_clarity": 0.0,
            "error_tolerance": 0.0,
            "recommendations": [],
            "risk_factors": [],
        }

        # Assess pattern integrity (40% of overall score)
        pattern_analysis = self.analyze_pattern_preservation(config)
        assessment["pattern_integrity"] = pattern_analysis["preservation_score"]

        # Assess data preservation (30% of overall score)
        data_score = self._calculate_data_preservation_score(modified_matrix)
        assessment["data_preservation"] = data_score

        # Assess visual clarity (20% of overall score)
        clarity_score = self._calculate_visual_clarity_score(config, modified_matrix)
        assessment["visual_clarity"] = clarity_score

        # Assess error tolerance (10% of overall score)
        tolerance_score = self._calculate_error_tolerance_score(config)
        assessment["error_tolerance"] = tolerance_score

        # Calculate weighted overall score
        assessment["overall_score"] = (
            assessment["pattern_integrity"] * 0.4
            + assessment["data_preservation"] * 0.3
            + assessment["visual_clarity"] * 0.2
            + assessment["error_tolerance"] * 0.1
        )

        # Generate recommendations based on scores
        assessment["recommendations"] = self._generate_scanability_recommendations(
            assessment
        )

        # Identify risk factors
        assessment["risk_factors"] = self._identify_risk_factors(config, assessment)

        return assessment

    def _estimate_centerpiece_area(self, config: Any) -> int:
        """Estimate the area covered by the centerpiece."""
        x1, y1, x2, y2 = self.geometry.get_centerpiece_bounds(config)
        return (x2 - x1) * (y2 - y1)

    def _conflicts_with_finder_patterns(self, config: Any) -> bool:
        """Check if centerpiece conflicts with finder patterns."""
        # Finder pattern positions (approximate)
        finder_positions = [
            (0, 0, 7, 7),  # Top-left
            (0, self.size - 7, 7, self.size),  # Top-right
            (self.size - 7, 0, self.size, 7),  # Bottom-left
        ]

        centerpiece_bounds = self.geometry.get_centerpiece_bounds(config)
        cp_x1, cp_y1, cp_x2, cp_y2 = centerpiece_bounds

        for fx1, fy1, fx2, fy2 in finder_positions:
            # Check for overlap
            if not (cp_x2 <= fx1 or cp_x1 >= fx2 or cp_y2 <= fy1 or cp_y1 >= fy2):
                return True

        return False

    def _analyze_finder_patterns(self, config: Any, analysis: PatternAnalysis) -> None:
        """Analyze finder pattern preservation."""
        finder_positions = [(0, 0), (0, self.size - 7), (self.size - 7, 0)]

        for finder_row, finder_col in finder_positions:
            affected = False
            for row in range(finder_row, min(finder_row + 7, self.size)):
                for col in range(finder_col, min(finder_col + 7, self.size)):
                    if self.geometry.is_in_centerpiece(row, col, config):
                        affected = True
                        break
                if affected:
                    break

            if affected:
                analysis["finder_patterns"]["affected"] += 1
                analysis["critical_violations"].append(
                    f"Finder pattern at ({finder_row}, {finder_col}) affected"
                )
            else:
                analysis["finder_patterns"]["preserved"] += 1

    def _analyze_timing_patterns(self, config: Any, analysis: PatternAnalysis) -> None:
        """Analyze timing pattern preservation."""
        # Check row 6 (horizontal timing)
        row_affected = any(
            self.geometry.is_in_centerpiece(6, col, config) for col in range(self.size)
        )

        # Check column 6 (vertical timing)
        col_affected = any(
            self.geometry.is_in_centerpiece(row, 6, config) for row in range(self.size)
        )

        if row_affected:
            analysis["timing_patterns"]["affected"] += 1
            analysis["critical_violations"].append(
                "Horizontal timing pattern (row 6) affected"
            )
        else:
            analysis["timing_patterns"]["preserved"] += 1

        if col_affected:
            analysis["timing_patterns"]["affected"] += 1
            analysis["critical_violations"].append(
                "Vertical timing pattern (column 6) affected"
            )
        else:
            analysis["timing_patterns"]["preserved"] += 1

    def _analyze_alignment_patterns(
        self, config: Any, analysis: PatternAnalysis
    ) -> None:
        """Analyze alignment pattern preservation (for larger QR codes)."""
        # Simplified - would need actual QR version to determine alignment positions
        # For now, assume no alignment patterns in smaller codes
        analysis["alignment_patterns"]["preserved"] = 1

    def _analyze_format_info(self, config: Any, analysis: PatternAnalysis) -> None:
        """Analyze format information preservation."""
        # Format info is around finder patterns - if finders are OK, format should be too
        if analysis["finder_patterns"]["affected"] == 0:
            analysis["format_info"]["preserved"] = 1
        else:
            analysis["format_info"]["affected"] = 1

    def _analyze_version_info(self, config: Any, analysis: PatternAnalysis) -> None:
        """Analyze version information preservation."""
        # Version info only exists in QR codes version 7 and above
        # For simplicity, assume preserved unless centerpiece is very large
        if self._estimate_centerpiece_area(config) > 300:
            analysis["version_info"]["affected"] = 1
        else:
            analysis["version_info"]["preserved"] = 1

    def _verify_finder_patterns(self, modified_matrix: List[List[bool]]) -> bool:
        """Verify finder patterns are structurally intact."""
        finder_positions = [(0, 0), (0, self.size - 7), (self.size - 7, 0)]

        for finder_row, finder_col in finder_positions:
            # Simple check - ensure the center dark square exists
            center_row, center_col = finder_row + 3, finder_col + 3
            if 0 <= center_row < self.size and 0 <= center_col < self.size:
                if not modified_matrix[center_row][center_col]:
                    return False

        return True

    def _verify_timing_patterns(self, modified_matrix: List[List[bool]]) -> bool:
        """Verify timing patterns have sufficient alternation."""
        # Check that row 6 and column 6 still have some alternating pattern
        row_6_changes = 0
        for col in range(1, self.size):
            if modified_matrix[6][col] != modified_matrix[6][col - 1]:
                row_6_changes += 1

        col_6_changes = 0
        for row in range(1, self.size):
            if modified_matrix[row][6] != modified_matrix[row - 1][6]:
                col_6_changes += 1

        # Need at least some alternation to be functional
        return row_6_changes >= 3 and col_6_changes >= 3

    def _verify_data_accessibility(self, modified_matrix: List[List[bool]]) -> bool:
        """Verify sufficient data regions remain accessible."""
        total_modules = self.size * self.size
        remaining_modules = sum(sum(row) for row in modified_matrix)

        # Need at least 50% of modules to remain for basic functionality
        return remaining_modules >= (total_modules * 0.5)

    def _generate_integrity_recommendations(
        self, integrity_report: IntegrityReport
    ) -> List[str]:
        """Generate recommendations for integrity issues."""
        recommendations = []

        if not integrity_report["finder_patterns_intact"]:
            recommendations.append(
                "Reduce centerpiece size to avoid finder pattern conflicts"
            )

        if not integrity_report["timing_patterns_intact"]:
            recommendations.append(
                "Adjust centerpiece position to preserve timing patterns"
            )

        if not integrity_report["data_regions_accessible"]:
            recommendations.append(
                "Significantly reduce centerpiece size to preserve data capacity"
            )

        return recommendations

    def _calculate_data_preservation_score(
        self, modified_matrix: List[List[bool]]
    ) -> float:
        """Calculate score based on how much data capacity is preserved."""
        original_data_modules = sum(sum(row) for row in self.matrix)
        remaining_data_modules = sum(sum(row) for row in modified_matrix)

        if original_data_modules == 0:
            return 1.0

        preservation_ratio = remaining_data_modules / original_data_modules

        # Score based on preservation ratio (non-linear to penalize excessive clearing)
        if preservation_ratio >= 0.9:
            return 1.0
        elif preservation_ratio >= 0.7:
            return 0.8
        elif preservation_ratio >= 0.5:
            return 0.6
        elif preservation_ratio >= 0.3:
            return 0.4
        else:
            return 0.2

    def _calculate_visual_clarity_score(
        self, config: Any, modified_matrix: List[List[bool]]
    ) -> float:
        """Calculate score based on visual clarity of the result."""
        # Higher scores for configurations that create clear, well-defined centerpieces
        score = 1.0

        # Penalty for very small centerpieces (hard to see)
        if config.size < 0.1:
            score -= 0.3

        # Penalty for overly complex shapes
        if config.shape == "squircle" and self._estimate_centerpiece_area(config) > 100:
            score -= 0.2

        # Bonus for moderate sizes that balance visibility and functionality
        if 0.15 <= config.size <= 0.25:
            score += 0.1

        return max(0.0, min(1.0, score))

    def _calculate_error_tolerance_score(self, config: Any) -> float:
        """Calculate score based on error correction tolerance."""
        centerpiece_area = self._estimate_centerpiece_area(config)
        total_area = self.size * self.size

        if total_area == 0:
            return 1.0

        area_ratio = centerpiece_area / total_area

        # Score based on staying within error correction capacity
        if area_ratio <= 0.1:
            return 1.0
        elif area_ratio <= 0.2:
            return 0.8
        elif area_ratio <= 0.3:
            return 0.6
        elif area_ratio <= 0.4:
            return 0.3
        else:
            return 0.1

    def _generate_scanability_recommendations(
        self, assessment: ScanabilityAssessment
    ) -> List[str]:
        """Generate recommendations to improve scanability."""
        recommendations = []

        if assessment["overall_score"] < 0.7:
            recommendations.append(
                "Consider reducing centerpiece size for better scanability"
            )

        if assessment["pattern_integrity"] < 0.8:
            recommendations.append(
                "Adjust centerpiece position to avoid critical QR patterns"
            )

        if assessment["data_preservation"] < 0.6:
            recommendations.append(
                "Centerpiece clears too much data - reduce size significantly"
            )

        if assessment["visual_clarity"] < 0.7:
            recommendations.append(
                "Consider using simpler centerpiece shape for better clarity"
            )

        if assessment["error_tolerance"] < 0.5:
            recommendations.append("Centerpiece exceeds safe error correction limits")

        return recommendations

    def _identify_risk_factors(
        self, config: Any, assessment: ScanabilityAssessment
    ) -> List[str]:
        """Identify risk factors that might affect scanning reliability."""
        risk_factors = []

        if config.size > 0.25:
            risk_factors.append(
                "Large centerpiece size increases scanning failure risk"
            )

        if assessment["pattern_integrity"] < 0.9:
            risk_factors.append("Critical pattern interference detected")

        if config.shape == "squircle" and self._estimate_centerpiece_area(config) > 150:
            risk_factors.append("Complex shape with large area may confuse scanners")

        if abs(config.offset_x) > 0.3 or abs(config.offset_y) > 0.3:
            risk_factors.append("Large offsets may place centerpiece in critical areas")

        return risk_factors
