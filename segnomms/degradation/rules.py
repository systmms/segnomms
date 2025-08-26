"""
Degradation rules defining incompatible feature combinations.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Optional

from ..config import RenderingConfig
from .models import DegradationWarning, WarningLevel


class IncompatibilityType(str, Enum):
    """Types of feature incompatibilities."""

    SHAPE_COMPLEXITY = "shape_complexity"
    COLOR_CONTRAST = "color_contrast"
    SIZE_CONSTRAINT = "size_constraint"
    PATTERN_CONFLICT = "pattern_conflict"
    PERFORMANCE = "performance"
    SCANABILITY = "scanability"


class DegradationRule(ABC):
    """Base class for degradation rules."""

    def __init__(self) -> None:
        self.incompatibility_type = IncompatibilityType.SCANABILITY
        self.name = self.__class__.__name__

    @abstractmethod
    def check(self, config: RenderingConfig) -> Optional[DegradationWarning]:
        """Check if this rule is violated and return a warning if so."""

    @abstractmethod
    def apply_fallback(self, config: RenderingConfig) -> RenderingConfig:
        """Apply the fallback to make the configuration safe."""


class ComplexShapeWithHighErrorRule(DegradationRule):
    """Complex shapes with high error correction can impact scanability."""

    def __init__(self) -> None:
        super().__init__()
        self.incompatibility_type = IncompatibilityType.SHAPE_COMPLEXITY

    def check(self, config: RenderingConfig) -> Optional[DegradationWarning]:
        # Complex connected shapes with small modules
        complex_shapes = [
            "connected-classy",
            "connected-classy-rounded",
            "star",
            "hexagon",
        ]

        if config.geometry.shape in complex_shapes and config.scale < 8 and not config.safe_mode:

            return DegradationWarning(
                level=WarningLevel.WARNING,
                feature="shape",
                message=f"Complex shape '{config.geometry.shape}' with small scale "
                f"({config.scale}px) may impact scanability",
                original_value=config.geometry.shape,
                degraded_value="square",
                reason="Complex shapes need larger module sizes for reliable scanning",
                suggestion="Increase scale to at least 8px or use a simpler shape",
            )
        return None

    def apply_fallback(self, config: RenderingConfig) -> RenderingConfig:
        """Fallback to square shape."""
        config_dict = config.model_dump()
        config_dict["geometry"]["shape"] = "square"
        return RenderingConfig(**config_dict)


class LowContrastRule(DegradationRule):
    """Detect low contrast between dark and light colors using enhanced palette validation."""

    def __init__(self) -> None:
        super().__init__()
        self.incompatibility_type = IncompatibilityType.COLOR_CONTRAST

    def check(self, config: RenderingConfig) -> Optional[DegradationWarning]:
        # Use enhanced palette validation if enabled
        if config.enable_palette_validation:
            ratio = config.get_contrast_ratio()
            if ratio is not None and ratio < config.min_contrast_ratio:
                return DegradationWarning(
                    level=WarningLevel.CRITICAL,
                    feature="colors",
                    message=f"Low contrast ratio {ratio:.2f} between dark ('{config.dark}') "
                    f"and light ('{config.light}') colors, "
                    f"minimum required: {config.min_contrast_ratio:.2f}",
                    original_value={"dark": config.dark, "light": config.light},
                    degraded_value={"dark": "black", "light": "white"},
                    reason="QR codes require high contrast for reliable scanning",
                    suggestion=f"Use colors with contrast ratio of at least "
                    f"{config.min_contrast_ratio:.1f}:1",
                )
        else:
            # Fallback to simple contrast check
            if self._is_low_contrast(config.dark, config.light):
                return DegradationWarning(
                    level=WarningLevel.CRITICAL,
                    feature="colors",
                    message=f"Low contrast between dark ('{config.dark}') "
                    f"and light ('{config.light}') colors",
                    original_value={"dark": config.dark, "light": config.light},
                    degraded_value={"dark": "black", "light": "white"},
                    reason="QR codes require high contrast for reliable scanning",
                    suggestion="Use colors with higher contrast ratio (WCAG AA minimum)",
                )
        return None

    def apply_fallback(self, config: RenderingConfig) -> RenderingConfig:
        """Fallback to black and white."""
        config_dict = config.model_dump()
        config_dict["dark"] = "black"
        config_dict["light"] = "white"
        return RenderingConfig(**config_dict)

    def _is_low_contrast(self, dark: str, light: str) -> bool:
        """Simple contrast check fallback."""
        # For now, just check some known problematic combinations
        problematic = [
            ("yellow", "white"),
            ("lightgray", "white"),
            ("gray", "lightgray"),
            ("#FFFF00", "#FFFFFF"),
            ("#DDDDDD", "#FFFFFF"),
        ]

        dark_lower = dark.lower()
        light_lower = light.lower()

        return any(
            (dark_lower == d and light_lower == l) or (dark_lower == l and light_lower == d)
            for d, l in problematic
        )


class TinyModulesWithComplexityRule(DegradationRule):
    """Very small modules with complex features."""

    def __init__(self) -> None:
        super().__init__()
        self.incompatibility_type = IncompatibilityType.SIZE_CONSTRAINT

    def check(self, config: RenderingConfig) -> Optional[DegradationWarning]:
        if config.scale < 5:
            # Check for features that don't work well with tiny modules
            issues = []

            if config.geometry.corner_radius > 0.3:
                issues.append("high corner radius")

            if config.geometry.shape in ["star", "hexagon", "connected-classy"]:
                issues.append(f"complex shape '{config.geometry.shape}'")

            if config.patterns.enabled:
                issues.append("pattern-specific styling")

            if issues:
                return DegradationWarning(
                    level=WarningLevel.WARNING,
                    feature="scale",
                    message=f"Small module size ({config.scale}px) with {', '.join(issues)}",
                    original_value=config.scale,
                    degraded_value=config.scale,  # We'll simplify features instead
                    reason="Complex features need larger modules to render properly",
                    suggestion="Increase scale to at least 8px or simplify visual features",
                )
        return None

    def apply_fallback(self, config: RenderingConfig) -> RenderingConfig:
        """Simplify features for tiny modules."""
        config_dict = config.model_dump()

        # Reduce corner radius
        if config_dict["geometry"]["corner_radius"] > 0.3:
            config_dict["geometry"]["corner_radius"] = 0.0

        # Simplify shape
        if config_dict["geometry"]["shape"] in ["star", "hexagon", "connected-classy"]:
            config_dict["geometry"]["shape"] = "square"

        # Disable pattern styling
        if config_dict["patterns"]["enabled"]:
            config_dict["patterns"]["enabled"] = False

        return RenderingConfig(**config_dict)


class FadeFrameWithPatternStylingRule(DegradationRule):
    """Fade frame mode can conflict with pattern-specific colors."""

    def __init__(self) -> None:
        super().__init__()
        self.incompatibility_type = IncompatibilityType.PATTERN_CONFLICT

    def check(self, config: RenderingConfig) -> Optional[DegradationWarning]:
        if (
            config.frame.clip_mode == "fade"
            and config.patterns.enabled
            and any([config.patterns.finder_color, config.patterns.timing_color])
        ):

            return DegradationWarning(
                level=WarningLevel.WARNING,
                feature="frame",
                message="Fade frame effect may not work well with pattern-specific colors",
                original_value=config.frame.clip_mode,
                degraded_value="clip",
                reason="Fade masks can interfere with custom pattern colors",
                suggestion="Use 'clip' mode or disable pattern-specific colors near frame edges",
            )
        return None

    def apply_fallback(self, config: RenderingConfig) -> RenderingConfig:
        """Change to clip mode."""
        config_dict = config.model_dump()
        config_dict["frame"]["clip_mode"] = "clip"
        return RenderingConfig(**config_dict)


class ExcessiveMergingRule(DegradationRule):
    """Aggressive merging with certain patterns can break scanning."""

    def __init__(self) -> None:
        super().__init__()
        self.incompatibility_type = IncompatibilityType.SCANABILITY

    def check(self, config: RenderingConfig) -> Optional[DegradationWarning]:
        if config.geometry.merge == "aggressive" and config.geometry.min_island_modules < 3:
            return DegradationWarning(
                level=WarningLevel.WARNING,
                feature="merge",
                message="Aggressive merging with small island threshold may merge critical patterns",
                original_value={
                    "merge": "aggressive",
                    "min_island": config.geometry.min_island_modules,
                },
                degraded_value={"merge": "soft", "min_island": 3},
                reason="Aggressive merging can accidentally merge functional patterns",
                suggestion="Use 'soft' merge or increase min_island_modules to at least 3",
            )
        return None

    def apply_fallback(self, config: RenderingConfig) -> RenderingConfig:
        """Use soft merging and increase island threshold."""
        config_dict = config.model_dump()
        config_dict["geometry"]["merge"] = "soft"
        config_dict["geometry"]["min_island_modules"] = 3
        return RenderingConfig(**config_dict)


class CenterpieceTooLargeRule(DegradationRule):
    """Centerpiece reserve area that's too large for QR version."""

    def __init__(self) -> None:
        super().__init__()
        self.incompatibility_type = IncompatibilityType.SIZE_CONSTRAINT

    def check(self, config: RenderingConfig) -> Optional[DegradationWarning]:
        if config.centerpiece.enabled and config.centerpiece.size > 0.3:
            return DegradationWarning(
                level=WarningLevel.CRITICAL,
                feature="centerpiece",
                message=f"Centerpiece size ({config.centerpiece.size:.0%}) may be too large",
                original_value=config.centerpiece.size,
                degraded_value=0.2,
                reason="Large centerpiece areas can remove too many data modules",
                suggestion="Keep centerpiece size under 20% of QR code area",
            )
        return None

    def apply_fallback(self, config: RenderingConfig) -> RenderingConfig:
        """Reduce centerpiece size."""
        config_dict = config.model_dump()
        config_dict["centerpiece"]["size"] = 0.2
        return RenderingConfig(**config_dict)


class PaletteValidationRule(DegradationRule):
    """Comprehensive palette validation using enhanced palette system."""

    def __init__(self) -> None:
        super().__init__()
        self.incompatibility_type = IncompatibilityType.COLOR_CONTRAST

    def check(self, config: RenderingConfig) -> Optional[DegradationWarning]:
        if not config.enable_palette_validation:
            return None

        # Run comprehensive palette validation
        try:
            validation_result = config.validate_palette()

            # Check for palette issues beyond basic contrast
            if not validation_result.is_valid:
                # Find the most serious issue
                if validation_result.issues:
                    most_serious = validation_result.issues[0]
                    return DegradationWarning(
                        level=WarningLevel.WARNING,
                        feature="palette",
                        message=f"Palette validation failed: {most_serious}",
                        original_value={"palette": config._get_accent_colors()},
                        degraded_value={"palette": []},  # Will disable accent colors
                        reason="Enhanced palette validation detected issues",
                        suggestion="Simplify color palette or adjust colors for better compatibility",
                    )

            # Check for warnings that might affect QR scanning
            elif validation_result.warnings:
                warning_count = len(validation_result.warnings)
                if warning_count >= 3:  # Multiple warnings indicate problematic palette
                    return DegradationWarning(
                        level=WarningLevel.INFO,
                        feature="palette",
                        message=f"Palette has {warning_count} validation warnings",
                        original_value={"accent_colors": config._get_accent_colors()},
                        degraded_value={"accent_colors": []},
                        reason="Multiple palette issues may affect visual clarity",
                        suggestion="Consider using fewer or more distinct colors",
                    )
        except Exception:
            # If palette validation fails, don't crash - just skip
            pass

        return None

    def apply_fallback(self, config: RenderingConfig) -> RenderingConfig:
        """Simplify palette by disabling pattern-specific colors."""
        config_dict = config.model_dump()

        # Disable pattern styling to simplify palette
        if config_dict["patterns"]["enabled"]:
            config_dict["patterns"]["enabled"] = False

        return RenderingConfig(**config_dict)


# Registry of all rules
DEGRADATION_RULES: List[DegradationRule] = [
    ComplexShapeWithHighErrorRule(),
    LowContrastRule(),
    TinyModulesWithComplexityRule(),
    FadeFrameWithPatternStylingRule(),
    ExcessiveMergingRule(),
    CenterpieceTooLargeRule(),
    PaletteValidationRule(),
]
