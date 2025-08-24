"""Validation for Phase 4 frame and centerpiece features.

This module provides validation logic for the new Phase 4 features including
frame shapes, centerpiece reserves, and quiet zone enhancements.
"""

import logging
from typing import List, Literal

from ..color.color_analysis import suggest_color_improvements, validate_qr_contrast
from ..config import CenterpieceConfig, FrameConfig, MergeStrategy, RenderingConfig
from ..core.geometry import CenterpieceGeometry
from .models import Phase4ValidatorConfig, ValidationResult

try:
    # Import from test helpers - graceful degradation if not available in testing environment
    from ...tests.helpers.scanning_harness import get_scanability_harness
except ImportError:
    # Fallback if tests module is not available
    def get_scanability_harness() -> None:
        return None


logger = logging.getLogger(__name__)


class Phase4Validator:
    """Validation for Phase 4 frame and centerpiece features.

    This class provides comprehensive validation for frame shapes, centerpiece
    reserves, and their interaction with existing QR code features.

    Example:
        >>> validator = Phase4Validator(qr_version=7, error_level='M', matrix_size=45)
        >>> # Or using Pydantic model
        >>> config = Phase4ValidatorConfig(qr_version=7, error_level='m', matrix_size=45)
        >>> validator = Phase4Validator(**config.model_dump())
    """

    def __init__(self, qr_version: int, error_level: Literal['L', 'M', 'Q', 'H'], matrix_size: int):
        """Initialize the validator.

        Args:
            qr_version: QR code version (1-40)
            error_level: Error correction level ('L', 'M', 'Q', 'H')
            matrix_size: Size of the QR matrix in modules
        """
        # Validate inputs using Pydantic
        config = Phase4ValidatorConfig(
            qr_version=qr_version, error_level=error_level, matrix_size=matrix_size
        )

        # Use validated values
        self.qr_version = config.qr_version
        self.error_level = config.error_level
        self.matrix_size = config.matrix_size

    def validate_frame_safety(
        self, frame_config: FrameConfig, border_modules: int
    ) -> List[str]:
        """Validate frame configuration for QR code safety.

        Args:
            frame_config: Frame configuration to validate
            border_modules: Number of border modules (quiet zone)

        Returns:
            List of warning messages (empty if all valid)
        """
        warnings = []

        # Non-square frames need adequate quiet zone
        if frame_config.shape != "square" and border_modules < 4:
            warnings.append(
                f"Non-square frame shape '{frame_config.shape}' requires minimum "
                f"4-module quiet zone for reliable scanning (current: {border_modules})"
            )

        # Fade mode with custom shapes warning
        if frame_config.clip_mode == "fade" and frame_config.shape == "custom":
            warnings.append(
                "Fade mode with custom frame shapes may produce unexpected results. "
                "Consider using 'clip' mode for custom shapes."
            )

        # Circle frames with small QR codes
        if frame_config.shape == "circle" and self.matrix_size < 25:
            warnings.append(
                f"Circle frame with small QR code (size {self.matrix_size}) may "
                "clip important corner areas. Consider increasing QR size or using "
                "rounded-rect frame."
            )

        # Validate corner radius for rounded rectangles
        if frame_config.shape == "rounded-rect":
            if frame_config.corner_radius > 0.5:
                warnings.append(
                    f"Large corner radius ({frame_config.corner_radius}) may impact "
                    "scannability. Consider using values <= 0.3 for better compatibility."
                )

        return warnings

    def validate_centerpiece_safety(
        self, centerpiece_config: CenterpieceConfig
    ) -> List[str]:
        """Validate centerpiece size against error correction capacity.

        Args:
            centerpiece_config: Centerpiece configuration to validate

        Returns:
            List of error messages (empty if valid)
        """
        if not centerpiece_config.enabled:
            return []

        errors = []

        # Calculate safe size
        geometry = CenterpieceGeometry(self.matrix_size)
        safe_size = geometry.calculate_safe_reserve_size(
            self.qr_version, self.error_level
        )

        # Check if size exceeds safe limit
        if centerpiece_config.size > safe_size:
            errors.append(
                f"Centerpiece size {centerpiece_config.size:.1%} exceeds safe limit "
                f"{safe_size:.1%} for error level {self.error_level}. "
                f"Reduce size or use higher error correction level."
            )

        # Warn about large centerpieces even if within limits
        elif centerpiece_config.size > safe_size * 0.9:
            logger.warning(
                f"Centerpiece size {centerpiece_config.size:.1%} is close to limit "
                f"{safe_size:.1%}. Consider reducing for better reliability."
            )

        # Check offset bounds
        max_offset = 0.5 - centerpiece_config.size
        if abs(centerpiece_config.offset_x) > max_offset:
            errors.append(
                f"Centerpiece X offset {centerpiece_config.offset_x} with size "
                f"{centerpiece_config.size} would extend beyond QR bounds"
            )
        if abs(centerpiece_config.offset_y) > max_offset:
            errors.append(
                f"Centerpiece Y offset {centerpiece_config.offset_y} with size "
                f"{centerpiece_config.size} would extend beyond QR bounds"
            )

        # Version-specific warnings
        if self.qr_version <= 2 and centerpiece_config.size > 0.1:
            errors.append(
                f"QR version {self.qr_version} is too small for centerpiece. "
                "Minimum version 3 recommended for centerpiece reserves."
            )

        # Margin validation
        if centerpiece_config.margin > 5:
            logger.warning(
                f"Large centerpiece margin ({centerpiece_config.margin} modules) "
                "may unnecessarily reduce QR capacity"
            )

        return errors

    def validate_contrast_ratio(
        self, config: RenderingConfig, min_ratio: float = 3.0
    ) -> List[str]:
        """Validate color contrast ratio for scanability.

        Args:
            config: Rendering configuration containing colors
            min_ratio: Minimum acceptable contrast ratio (default: 3.0)

        Returns:
            List of error messages (empty if valid)
        """
        errors = []

        # Get colors from config
        dark_color = getattr(config, "dark", "black")
        light_color = getattr(config, "light", "white")

        # Validate contrast
        is_valid, actual_ratio, message = validate_qr_contrast(
            dark_color, light_color, min_ratio
        )

        if not is_valid:
            errors.append(message)

            # Add specific suggestions
            suggestions = suggest_color_improvements(dark_color, light_color)
            for suggestion in suggestions:
                errors.append(f"Suggestion: {suggestion}")

        return errors

    def validate_module_size_scanability(self, config: RenderingConfig) -> List[str]:
        """Validate module size against scanability requirements.

        Args:
            config: Rendering configuration

        Returns:
            List of warning messages
        """
        warnings = []

        # Module size (scale) validation
        scale = getattr(config, "scale", 10)

        # Very small modules
        if scale < 3:
            warnings.append(
                f"Module size {scale}px is very small and may not scan reliably "
                "on some devices. Consider using at least 5px for better compatibility."
            )
        elif scale < 5:
            warnings.append(
                f"Module size {scale}px is small. Consider using at least 8px "
                "for optimal scanning across devices."
            )

        # Very large modules (memory/performance warning)
        elif scale > 50:
            warnings.append(
                f"Module size {scale}px is very large and may impact performance. "
                "Consider using smaller scale values for better efficiency."
            )

        # Module size vs QR version compatibility
        total_pixels = self.matrix_size * scale
        
        # Density validation based on total pixel count
        if total_pixels < 441:  # 21x21 minimum for readability 
            warnings.append(
                f"Very small QR code ({total_pixels} total pixels). "
                "May be difficult to scan reliably."
            )
        elif total_pixels > 1000000:  # 1000x1000 maximum practical size
            warnings.append(
                f"Very large QR code ({total_pixels} total pixels). "
                "May cause performance issues or memory constraints."
            )

        # Warn about pixel density issues
        if scale >= 1 and scale <= 2:
            warnings.append(
                "Small module sizes may cause aliasing issues on high-DPI displays. "
                "Test on various screen densities."
            )

        # Large QR codes with small modules
        if self.matrix_size > 50 and scale < 5:
            warnings.append(
                f"Large QR code ({self.matrix_size}x{self.matrix_size}) with small "
                f"modules ({scale}px) may be difficult to scan. Consider larger modules."
            )

        # Frame shape interaction with module size
        frame_shape = getattr(config.frame, "shape", "square")
        if frame_shape != "square" and scale < 8:
            warnings.append(
                f"Non-square frame with small modules ({scale}px) may impact "
                "edge scanning reliability. Consider larger modules or square frame."
            )

        return warnings

    def run_automated_scanability_test(
        self,
        config: RenderingConfig,
        minimum_success_rate: float = 0.8,
        test_data: str = "SegnoMMS Test",
    ) -> List[str]:
        """Run automated scanability testing harness.

        Args:
            config: Rendering configuration to test
            minimum_success_rate: Minimum required success rate
            test_data: Data to encode for testing

        Returns:
            List of error messages (empty if passes)
        """
        errors = []

        # Get scanning harness
        harness = get_scanability_harness()
        if not harness:
            # No scanning libraries available - skip test
            logger.warning(
                "Automated scanability testing skipped - no scanning libraries available"
            )
            errors.append(
                "Automated scanability testing unavailable. "
                "Install PIL, opencv-python, and pyzbar for comprehensive validation."
            )
            return errors

        try:
            # Import SVG generator dynamically to avoid circular imports
            from ..plugin import generate_interactive_svg

            # Run comprehensive scanability test
            meets_threshold, results = harness.validate_scanability_threshold(
                config,
                minimum_success_rate,
                test_data,
                svg_generator=generate_interactive_svg,
            )

            if not meets_threshold:
                success_rate = results.get("success_rate", 0)
                errors.append(
                    f"Automated scanability test failed: {success_rate:.1%} success rate "
                    f"(minimum {minimum_success_rate:.1%} required). "
                    f"Configuration may not scan reliably across devices and conditions."
                )

                # Add specific failure information
                failure_count = results.get("failure_count", 0)
                error_count = results.get("error_count", 0)
                if failure_count > 0:
                    errors.append(
                        f"Failed {failure_count} scanning tests. "
                        "Consider adjusting contrast, module size, or frame settings."
                    )

                if error_count > 0:
                    errors.append(
                        f"Encountered {error_count} test errors. "
                        "Configuration may be too complex for reliable scanning."
                    )
            else:
                # Test passed - log success
                success_rate = results.get("success_rate", 0)
                logger.info(
                    f"Automated scanability test passed: {success_rate:.1%} success rate "
                    f"across {results.get('total_tests', 0)} test conditions"
                )

        except Exception as e:
            errors.append(f"Automated scanability test failed with error: {str(e)}")
            logger.error(f"Scanability test error: {e}")

        return errors

    def validate_combined_features(self, config: RenderingConfig) -> List[str]:
        """Check for problematic feature combinations.

        Args:
            config: Complete rendering configuration

        Returns:
            List of warning messages
        """
        warnings = []

        # Circle frame with large centerpiece
        if (
            config.frame.shape == "circle"
            and config.centerpiece.enabled
            and config.centerpiece.size > 0.3
        ):
            warnings.append(
                "Large centerpiece with circle frame may significantly impact "
                "scannability, especially at frame edges. Consider using a "
                "smaller centerpiece or different frame shape."
            )

        # Aggressive merging with centerpiece
        if (
            config.geometry.merge == MergeStrategy.AGGRESSIVE
            and config.centerpiece.enabled
        ):
            warnings.append(
                "Aggressive module merging with centerpiece reserve may create "
                "scanning issues. Consider using 'soft' or 'none' merge strategy."
            )

        # Small quiet zone with non-square frame
        if config.frame.shape != "square" and config.border < 4:
            warnings.append(
                f"Frame shape '{config.frame.shape}' with {config.border}-module "
                "border may not scan reliably. Increase border to at least 4."
            )

        # Fade mode with interactive features
        if config.frame.clip_mode == "fade" and config.style.interactive:
            warnings.append(
                "Fade frame mode may interfere with interactive hover effects "
                "at frame edges."
            )

        # Low error correction with multiple advanced features
        feature_count = sum(
            [
                config.frame.shape != "square",
                config.centerpiece.enabled,
                config.geometry.merge != MergeStrategy.NONE,
                config.phase3.enabled,
            ]
        )

        if self.error_level == "L" and feature_count >= 2:
            warnings.append(
                f"Low error correction with {feature_count} advanced features "
                "may impact reliability. Consider using error level 'M' or higher."
            )

        # Centerpiece with certain shapes
        if config.centerpiece.enabled and config.geometry.shape in [
            "star",
            "triangle",
            "hexagon",
        ]:
            warnings.append(
                f"Module shape '{config.geometry.shape}' with centerpiece "
                "may create visual conflicts. Test thoroughly."
            )

        return warnings

    def get_recommendations(self, config: RenderingConfig) -> List[str]:
        """Get recommendations for optimal configuration.

        Args:
            config: Rendering configuration to analyze

        Returns:
            List of recommendation messages
        """
        recommendations = []

        # Frame recommendations
        if config.frame.shape == "circle" and self.matrix_size > 45:
            recommendations.append(
                "For large QR codes, consider 'rounded-rect' or 'squircle' "
                "frames to preserve more corner area."
            )

        # Centerpiece recommendations
        if config.centerpiece.enabled:
            if self.error_level in ["L", "M"] and config.centerpiece.size > 0.15:
                recommendations.append(
                    f"For {config.centerpiece.size:.0%} centerpiece, consider "
                    f"using error level 'Q' or 'H' instead of '{self.error_level}'."
                )

            if config.centerpiece.shape == "rect" and config.frame.shape == "circle":
                recommendations.append(
                    "Consider using circular centerpiece to match circle frame "
                    "for better visual harmony."
                )

        # Performance recommendations
        if config.frame.clip_mode == "fade" and config.phase3.enabled:
            recommendations.append(
                "Fade frame with Phase 3 bezier curves may impact performance. "
                "Consider using 'clip' mode for faster rendering."
            )

        return recommendations

    def validate_all(
        self,
        config: RenderingConfig,
        min_contrast_ratio: float = 3.0,
        run_scanability_tests: bool = False,
        min_scanability_success_rate: float = 0.8,
    ) -> ValidationResult:
        """Perform complete validation of Phase 4 features.

        Args:
            config: Complete rendering configuration
            min_contrast_ratio: Minimum contrast ratio for scanability (default: 3.0)
            run_scanability_tests: Whether to run automated scanning tests (default: False)
            min_scanability_success_rate: Minimum success rate for scanning tests (default: 0.8)

        Returns:
            ValidationResult with errors, warnings, and recommendations
        """
        errors = []
        warnings = []

        # Configuration object validation is now handled by Pydantic automatically
        # during model creation, so no additional validation needed here

        # Enhanced scanability validation (new features)
        errors.extend(self.validate_contrast_ratio(config, min_contrast_ratio))
        warnings.extend(self.validate_module_size_scanability(config))

        # Automated scanability testing (optional, expensive)
        if run_scanability_tests:
            errors.extend(
                self.run_automated_scanability_test(
                    config, min_scanability_success_rate
                )
            )

        # Existing safety validation
        warnings.extend(self.validate_frame_safety(config.frame, config.border))
        errors.extend(self.validate_centerpiece_safety(config.centerpiece))

        # Combined feature validation
        warnings.extend(self.validate_combined_features(config))

        # Get recommendations
        recommendations = self.get_recommendations(config)

        return ValidationResult(
            errors=errors,
            warnings=warnings,
            recommendations=recommendations,
            valid=len(errors) == 0,
        )
