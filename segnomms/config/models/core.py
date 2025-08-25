"""Core configuration models.

This module contains the main RenderingConfig class that combines all
other configuration models into a comprehensive configuration system.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

# mypy: disable-error-code=unreachable


if TYPE_CHECKING:
    from ...color.palette import PaletteValidationResult

from ...exceptions import (
    InvalidColorFormatError,
)
from ..enums import ContourMode, OptimizationLevel
from .advanced import AdvancedQRConfig

# Import all component models
from .geometry import FinderConfig, GeometryConfig
from .phases import Phase1Config, Phase2Config, Phase3Config
from .visual import (
    CenterpieceConfig,
    FrameConfig,
    PatternStyleConfig,
    QuietZoneConfig,
    StyleConfig,
)

# Set up logger for configuration warnings
logger = logging.getLogger(__name__)


class RenderingConfig(BaseModel):
    """Main QR code rendering configuration.

    This is the central configuration class that combines all aspects of QR code
    generation including geometry, visual styling, advanced features, and processing
    phases.

    The configuration supports both Pydantic model initialization and a convenient
    kwargs-based factory method for backward compatibility.

    Attributes:
        scale: Size of each module in pixels
        border: Quiet zone border thickness in modules
        dark: Primary foreground color (hex, rgb, or named)
        light: Primary background color (hex, rgb, or named)
        safe_mode: Enable safe fallback modes for production
        geometry: Module geometry and shape configuration
        finder: Finder pattern styling configuration
        patterns: Pattern-specific styling configuration
        frame: Frame shape and clipping configuration
        centerpiece: Central reserve area configuration
        quiet_zone: Quiet zone styling configuration
        style: General styling and CSS configuration
        phase1: Phase 1 processing configuration (enhanced shapes)
        phase2: Phase 2 processing configuration (clustering)
        phase3: Phase 3 processing configuration (contours)
        advanced_qr: Advanced QR features configuration
        accessibility: Accessibility features configuration
        shape_options: Additional shape-specific parameters
        min_contrast_ratio: Minimum WCAG contrast ratio requirement
        enable_palette_validation: Validate color accessibility
        enforce_wcag_standards: Enforce WCAG AA/AAA compliance

    Example:
        Creating configuration with model syntax::

            config = RenderingConfig(
                scale=10,
                dark="#1a1a2e",
                light="#ffffff",
                geometry=GeometryConfig(
                    shape="rounded",
                    corner_radius=0.3
                ),
                style=StyleConfig(interactive=True)
            )

        Creating configuration from kwargs (backward compatible)::

            config = RenderingConfig.from_kwargs(
                scale=10,
                dark="#1a1a2e",
                light="#ffffff",
                shape="rounded",
                corner_radius=0.3,
                interactive=True
            )
    """

    model_config = ConfigDict(validate_default=True, extra="forbid")

    # Basic QR code parameters
    scale: int = Field(
        default=1, ge=1, le=100, description="Size of each module in pixels"
    )
    border: int = Field(
        default=4, ge=0, le=20, description="Quiet zone border thickness in modules"
    )
    dark: str = Field(
        default="#000000", description="Primary foreground color (hex, rgb, or named)"
    )
    light: str = Field(
        default="#ffffff", description="Primary background color (hex, rgb, or named)"
    )
    safe_mode: bool = Field(
        default=False,
        description="Force square shapes for critical QR patterns (finder, timing) "
        "to ensure scannability",
    )

    # Configuration subsections
    geometry: GeometryConfig = Field(
        default_factory=GeometryConfig,
        description="Module geometry and shape configuration",
    )
    finder: FinderConfig = Field(
        default_factory=FinderConfig, description="Finder pattern styling configuration"
    )
    patterns: PatternStyleConfig = Field(
        default_factory=PatternStyleConfig,
        description="Pattern-specific styling configuration",
    )
    frame: FrameConfig = Field(
        default_factory=FrameConfig,
        description="Frame shape and clipping configuration",
    )
    centerpiece: CenterpieceConfig = Field(
        default_factory=CenterpieceConfig,
        description="Central reserve area configuration",
    )
    quiet_zone: QuietZoneConfig = Field(
        default_factory=QuietZoneConfig, description="Quiet zone styling configuration"
    )
    style: StyleConfig = Field(
        default_factory=StyleConfig, description="General styling and CSS configuration"
    )

    # Processing phases
    phase1: Phase1Config = Field(
        default_factory=Phase1Config,
        description="Phase 1 processing configuration (enhanced shapes)",
    )
    phase2: Phase2Config = Field(
        default_factory=Phase2Config,
        description="Phase 2 processing configuration (clustering)",
    )
    phase3: Phase3Config = Field(
        default_factory=Phase3Config,
        description="Phase 3 processing configuration (contours)",
    )

    # Advanced features
    advanced_qr: AdvancedQRConfig = Field(
        default_factory=AdvancedQRConfig,
        description="Advanced QR features configuration",
    )

    # Accessibility features (optional, imported dynamically)
    accessibility: "AccessibilityConfig" = Field(
        default_factory=lambda: AccessibilityConfig(enabled=False),
        description="Accessibility features configuration",
    )

    # Additional shape parameters
    shape_options: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional shape-specific parameters"
    )

    # Color validation parameters
    min_contrast_ratio: float = Field(
        default=4.5,
        ge=1.0,
        le=21.0,
        description="Minimum WCAG contrast ratio requirement",
    )
    enable_palette_validation: bool = Field(
        default=False, description="Validate color accessibility"
    )
    enforce_wcag_standards: bool = Field(
        default=False, description="Enforce WCAG AA/AAA compliance"
    )

    # Optional metadata for tracking purposes
    metadata: Optional[Dict[str, Any]] = Field(
        default=None, description="Optional metadata for configuration tracking"
    )

    @field_validator("dark", "light")
    @classmethod
    def validate_colors(cls, v: str) -> str:
        """Validate color format."""
        # Basic validation - more comprehensive validation happens in palette validation
        if isinstance(v, str) and len(v.strip()) > 0:
            return v.strip()
        raise InvalidColorFormatError(
            color=str(v),
            accepted_formats=["hex (#RRGGBB)", "rgb(r,g,b)", "named colors"],
        )

    @classmethod
    def from_kwargs(cls, **kwargs: Any) -> "RenderingConfig":
        """Create RenderingConfig from flat kwargs for backward compatibility.

        This factory method allows creating configuration using the traditional
        flat parameter approach while internally organizing into the structured
        configuration model.

        Args:
            **kwargs: Flat configuration parameters

        Returns:
            RenderingConfig instance with organized configuration

        Example:
            config = RenderingConfig.from_kwargs(
                scale=10,
                border=4,
                dark="#1a1a2e",
                light="#ffffff",
                shape="rounded",
                corner_radius=0.3,
                merge="soft",
                connectivity="8-way",
                interactive=True,
                centerpiece_enabled=True,
                centerpiece_size=0.15
            )
        """
        # Start with basic parameters
        config_data = {
            key: kwargs.get(key, cls.model_fields[key].default)
            for key in [
                "scale",
                "border",
                "dark",
                "light",
                "safe_mode",
                "shape_options",
                "min_contrast_ratio",
                "enable_palette_validation",
                "enforce_wcag_standards",
            ]
            if key in kwargs or key in cls.model_fields
        }

        # Geometry configuration
        geometry_data = {}
        geometry_mappings = {
            "connectivity": "connectivity",
            "merge": "merge",
            "corner_radius": "corner_radius",
            "shape": "shape",
            "min_island_modules": "min_island_modules",
        }
        for kwarg_key, config_key in geometry_mappings.items():
            if kwarg_key in kwargs:
                geometry_data[config_key] = kwargs[kwarg_key]
        if geometry_data:
            config_data["geometry"] = geometry_data

        # Finder configuration
        finder_data = {}
        finder_mappings = {
            "finder_shape": "shape",
            "finder_inner_scale": "inner_scale",
            "finder_stroke": "stroke",
        }
        for kwarg_key, config_key in finder_mappings.items():
            if kwarg_key in kwargs:
                finder_data[config_key] = kwargs[kwarg_key]
        if finder_data:
            config_data["finder"] = finder_data

        # Phase configurations
        for phase_num in [1, 2, 3]:
            phase_key = f"phase{phase_num}"
            phase_data = {}

            # Check for explicit enable/disable
            enable_key = f"enable_phase{phase_num}"
            if enable_key in kwargs:
                phase_data["enabled"] = kwargs[enable_key]

            # Phase-specific parameters
            phase_prefix = f"phase{phase_num}_"
            for key, value in kwargs.items():
                if key.startswith(phase_prefix):
                    param_name = key[len(phase_prefix) :]
                    phase_data[param_name] = value

            if phase_data:
                config_data[phase_key] = phase_data

        # Frame configuration
        frame_data = {}
        frame_mappings = {
            "frame_shape": "shape",
            "frame_corner_radius": "corner_radius",
            "frame_clip_mode": "clip_mode",
            "frame_custom_path": "custom_path",
            "frame_fade_distance": "fade_distance",
            "frame_scale_distance": "scale_distance",
        }
        for kwarg_key, config_key in frame_mappings.items():
            if kwarg_key in kwargs:
                frame_data[config_key] = kwargs[kwarg_key]
        if frame_data:
            config_data["frame"] = frame_data

        # Centerpiece configuration (with backward compatibility)
        centerpiece_data = {}
        centerpiece_mappings = {
            "centerpiece_enabled": "enabled",
            "reserve_center": "enabled",  # backward compat
            "centerpiece_shape": "shape",
            "reserve_shape": "shape",  # backward compat
            "centerpiece_size": "size",
            "reserve_size": "size",  # backward compat
            "centerpiece_offset_x": "offset_x",
            "reserve_offset_x": "offset_x",  # backward compat
            "centerpiece_offset_y": "offset_y",
            "reserve_offset_y": "offset_y",  # backward compat
            "centerpiece_margin": "margin",
            "centerpiece_mode": "mode",
            "centerpiece_placement": "placement",
            "reserve_margin": "margin",  # backward compat
        }
        for kwarg_key, config_key in centerpiece_mappings.items():
            if kwarg_key in kwargs:
                centerpiece_data[config_key] = kwargs[kwarg_key]
        if centerpiece_data:
            config_data["centerpiece"] = centerpiece_data

        # Advanced QR features configuration
        advanced_qr_data = {}
        advanced_qr_mappings = {
            "eci_enabled": "eci_enabled",
            "qr_eci": "eci_enabled",  # Alternative naming
            "encoding": "encoding",
            "qr_encoding": "encoding",  # Alternative naming
            "mask_pattern": "mask_pattern",
            "qr_mask": "mask_pattern",  # Alternative naming
            "auto_mask": "auto_mask",
            "structured_append": "structured_append",
            "multi_symbol": "structured_append",  # Alternative naming
            "symbol_count": "symbol_count",
            "qr_symbol_count": "symbol_count",  # Alternative naming
            "boost_error": "boost_error",
            "qr_boost_error": "boost_error",  # Alternative naming
        }
        for kwarg_key, config_key in advanced_qr_mappings.items():
            if kwarg_key in kwargs:
                advanced_qr_data[config_key] = kwargs[kwarg_key]
        if advanced_qr_data:
            config_data["advanced_qr"] = advanced_qr_data

        # Pattern styling configuration
        pattern_data = {}
        pattern_mappings = {
            "patterns_enabled": "enabled",
            "pattern_finder": "finder",
            "pattern_finder_inner": "finder_inner",
            "pattern_timing": "timing",
            "pattern_alignment": "alignment",
            "pattern_format": "format",
            "pattern_version": "version",
            "pattern_data": "data",
            "pattern_finder_color": "finder_color",
            "pattern_finder_inner_color": "finder_inner_color",
            "pattern_timing_color": "timing_color",
            "pattern_alignment_color": "alignment_color",
            "pattern_format_color": "format_color",
            "pattern_version_color": "version_color",
            "pattern_data_color": "data_color",
            "pattern_finder_scale": "finder_scale",
            "pattern_timing_scale": "timing_scale",
            "pattern_alignment_scale": "alignment_scale",
            "pattern_finder_effects": "finder_effects",
            "pattern_timing_effects": "timing_effects",
            "pattern_alignment_effects": "alignment_effects",
        }
        for kwarg_key, config_key in pattern_mappings.items():
            if kwarg_key in kwargs:
                pattern_data[config_key] = kwargs[kwarg_key]
        if pattern_data:
            config_data["patterns"] = pattern_data

        # Quiet zone configuration
        quiet_zone_data = {}
        quiet_zone_mappings = {
            "quiet_zone_style": "style",
            "quiet_zone_color": "color",
            "quiet_zone_gradient": "gradient",
        }
        for kwarg_key, config_key in quiet_zone_mappings.items():
            if kwarg_key in kwargs:
                quiet_zone_data[config_key] = kwargs[kwarg_key]
        if quiet_zone_data:
            config_data["quiet_zone"] = quiet_zone_data

        # Style configuration
        style_data = {}
        style_mappings = {
            "interactive": "interactive",
            "tooltips": "tooltips",
            "custom_styles": "custom_styles",
            "css_classes": "css_classes",
            "style_css_classes": "css_classes",  # Alternative parameter name
        }
        for kwarg_key, config_key in style_mappings.items():
            if kwarg_key in kwargs:
                style_data[config_key] = kwargs[kwarg_key]
        if style_data:
            config_data["style"] = style_data

        # Accessibility configuration
        accessibility_data = {}

        # Handle direct accessibility config object
        if "accessibility" in kwargs:
            direct_accessibility = kwargs["accessibility"]
            if hasattr(direct_accessibility, "model_dump"):
                # Pydantic model - use model_dump()
                accessibility_data = direct_accessibility.model_dump()
            elif hasattr(direct_accessibility, "__dict__"):
                # Object with attributes - convert to dict
                accessibility_data = direct_accessibility.__dict__.copy()
            elif isinstance(direct_accessibility, dict):
                # Already a dictionary
                accessibility_data = direct_accessibility.copy()
            else:
                # Unknown type - skip
                pass

        # Handle prefixed accessibility parameters (flat kwargs format)
        accessibility_mappings = {
            "accessibility_enabled": "enabled",
            "accessibility_id_prefix": "id_prefix",
            "accessibility_use_stable_ids": "use_stable_ids",
            "accessibility_include_coordinates": "include_coordinates",
            "accessibility_enable_aria": "enable_aria",
            "accessibility_root_role": "root_role",
            "accessibility_module_role": "module_role",
            "accessibility_root_label": "root_label",
            "accessibility_root_description": "root_description",
            "accessibility_include_module_labels": "include_module_labels",
            "accessibility_include_pattern_labels": "include_pattern_labels",
            "accessibility_optimize_for_screen_readers": "optimize_for_screen_readers",
            "accessibility_group_similar_elements": "group_similar_elements",
            "accessibility_add_structural_markup": "add_structural_markup",
            "accessibility_enable_keyboard_navigation": "enable_keyboard_navigation",
            "accessibility_focus_visible_elements": "focus_visible_elements",
            "accessibility_target_compliance": "target_compliance",
            "accessibility_custom_attributes": "custom_attributes",
        }
        for kwarg_key, config_key in accessibility_mappings.items():
            if kwarg_key in kwargs:
                accessibility_data[config_key] = kwargs[kwarg_key]

        # Auto-enable accessibility for basic features if any accessibility
        # params are provided
        if accessibility_data and "enabled" not in accessibility_data:
            accessibility_data["enabled"] = True

        if accessibility_data:
            config_data["accessibility"] = accessibility_data

        # Use Pydantic's model_validate for automatic validation and type conversion
        try:
            config = cls.model_validate(config_data)
        except ValueError as e:
            # Handle validation errors gracefully by falling back to defaults
            import logging

            logger = logging.getLogger(__name__)
            logger.warning(f"Configuration validation error, using defaults: {e}")

            # Try to identify and fix common validation errors
            if "geometry.shape" in str(e) and "shape" in kwargs:
                logger.warning(
                    f"Invalid shape '{kwargs['shape']}', falling back to 'square'"
                )
                config_data["geometry"]["shape"] = "square"

            if "frame.shape" in str(e) and "frame_shape" in kwargs:
                logger.warning(
                    f"Invalid frame shape '{kwargs['frame_shape']}', "
                    f"falling back to 'square'"
                )
                config_data["frame"]["shape"] = "square"

            # Retry validation with corrected values
            try:
                config = cls.model_validate(config_data)
            except ValueError:
                # If still failing, create a basic default config
                logger.warning(
                    "Using minimal default configuration due to validation errors"
                )
                config = cls()

        # Auto-enable phases based on configuration
        cls._auto_enable_phases(config, kwargs)

        return config

    @classmethod
    def _auto_enable_phases(cls, config: "RenderingConfig", kwargs: dict) -> None:
        """Auto-enable phases based on configuration settings."""
        # Only auto-enable if not explicitly set in kwargs
        enable_phase1 = kwargs.get("enable_phase1")
        enable_phase2 = kwargs.get("enable_phase2")
        enable_phase3 = kwargs.get("enable_phase3")

        # Phase 1: Auto-enable when shape != "square" or corner_radius > 0
        if enable_phase1 is None and not config.phase1.enabled:
            needs_phase1 = (
                config.geometry.shape.value != "square"
                or config.geometry.corner_radius > 0
            )
            if needs_phase1:
                config.phase1.enabled = True
                config.phase1.use_enhanced_shapes = True
                config.phase1.roundness = config.geometry.corner_radius
                config.phase1.size_ratio = 0.9

        # Phase 2: Auto-enable when merge != "none"
        if enable_phase2 is None and not config.phase2.enabled:
            if config.geometry.merge.value != "none":
                config.phase2.enabled = True
                config.phase2.use_cluster_rendering = True
                config.phase2.cluster_module_types = ["data"]
                config.phase2.min_cluster_size = 3

        # Phase 3: Auto-enable when merge == "aggressive"
        if enable_phase3 is None and not config.phase3.enabled:
            if config.geometry.merge.value == "aggressive":
                config.phase3.enabled = True
                config.phase3.use_marching_squares = True
                config.phase3.contour_module_types = ["data"]
                config.phase3.contour_mode = ContourMode.BEZIER
                config.phase3.contour_smoothing = 0.3
                config.phase3.bezier_optimization = OptimizationLevel.MEDIUM

    def validate_palette(self) -> "PaletteValidationResult":
        """Validate the color palette using enhanced validation."""
        from ...color.palette import PaletteConfig, validate_palette

        # Create palette config from current colors
        palette_config = PaletteConfig(
            dark=self.dark,
            light=self.light,
            accent_colors=self._get_accent_colors(),
            min_contrast_ratio=self.min_contrast_ratio,
            enforce_standards=self.enforce_wcag_standards,
            validate_accessibility=self.enable_palette_validation,
        )

        return validate_palette(palette_config)

    def _get_accent_colors(self) -> List[str]:
        """Extract accent colors from pattern styling."""
        accent_colors = []

        if self.patterns.enabled:
            # Collect pattern-specific colors
            pattern_colors = [
                self.patterns.finder_color,
                self.patterns.finder_inner_color,
                self.patterns.timing_color,
                self.patterns.alignment_color,
                self.patterns.format_color,
                self.patterns.version_color,
                self.patterns.data_color,
            ]

            for color in pattern_colors:
                if (
                    color
                    and color not in accent_colors
                    and color not in [self.dark, self.light]
                ):
                    accent_colors.append(color)

        return accent_colors

    def get_contrast_ratio(self) -> Optional[float]:
        """Get contrast ratio between primary dark and light colors."""
        from ...color.color_analysis import calculate_contrast_ratio

        return calculate_contrast_ratio(self.dark, self.light)

    def meets_contrast_requirements(self) -> bool:
        """Check if primary colors meet minimum contrast requirements."""
        ratio = self.get_contrast_ratio()
        return ratio is not None and ratio >= self.min_contrast_ratio

    def to_kwargs(self) -> Dict[str, Any]:
        """Convert configuration back to kwargs format.

        Returns flat kwargs dictionary suitable for passing to from_kwargs.
        """
        kwargs = {
            "scale": self.scale,
            "border": self.border,
            "dark": self.dark,
            "light": self.light,
            "safe_mode": self.safe_mode,
            # Geometry parameters
            "connectivity": self.geometry.connectivity,
            "merge": self.geometry.merge,
            "corner_radius": self.geometry.corner_radius,
            "shape": self.geometry.shape,
            "min_island_modules": self.geometry.min_island_modules,
            # Finder parameters
            "finder_shape": self.finder.shape,
            "finder_inner_scale": self.finder.inner_scale,
            "finder_stroke": self.finder.stroke,
            # Frame parameters
            "frame_shape": self.frame.shape,
            "frame_corner_radius": self.frame.corner_radius,
            "frame_clip_mode": self.frame.clip_mode,
            "frame_fade_distance": self.frame.fade_distance,
            "frame_scale_distance": self.frame.scale_distance,
            # Centerpiece parameters
            "centerpiece_enabled": self.centerpiece.enabled,
            "centerpiece_shape": self.centerpiece.shape,
            "centerpiece_size": self.centerpiece.size,
            "centerpiece_offset_x": self.centerpiece.offset_x,
            "centerpiece_offset_y": self.centerpiece.offset_y,
            "centerpiece_margin": self.centerpiece.margin,
            "centerpiece_mode": self.centerpiece.mode.value,
            "centerpiece_placement": self.centerpiece.placement.value,
            # Advanced QR features parameters
            "eci_enabled": self.advanced_qr.eci_enabled,
            "encoding": self.advanced_qr.encoding,
            "mask_pattern": self.advanced_qr.mask_pattern,
            "auto_mask": self.advanced_qr.auto_mask,
            "structured_append": self.advanced_qr.structured_append,
            "symbol_count": self.advanced_qr.symbol_count,
            "boost_error": self.advanced_qr.boost_error,
            # Pattern styling parameters
            "patterns_enabled": self.patterns.enabled,
            "pattern_finder": self.patterns.finder,
            "pattern_finder_inner": self.patterns.finder_inner,
            "pattern_timing": self.patterns.timing,
            "pattern_alignment": self.patterns.alignment,
            "pattern_format": self.patterns.format,
            "pattern_version": self.patterns.version,
            "pattern_data": self.patterns.data,
            "pattern_finder_color": self.patterns.finder_color,
            "pattern_finder_inner_color": self.patterns.finder_inner_color,
            "pattern_timing_color": self.patterns.timing_color,
            "pattern_alignment_color": self.patterns.alignment_color,
            "pattern_format_color": self.patterns.format_color,
            "pattern_version_color": self.patterns.version_color,
            "pattern_data_color": self.patterns.data_color,
            "pattern_finder_scale": self.patterns.finder_scale,
            "pattern_timing_scale": self.patterns.timing_scale,
            "pattern_alignment_scale": self.patterns.alignment_scale,
            # Quiet zone parameters
            "quiet_zone_style": self.quiet_zone.style,
            "quiet_zone_color": self.quiet_zone.color,
            # Style parameters
            "interactive": self.style.interactive,
            "tooltips": self.style.tooltips,
        }

        # Optional values
        if self.shape_options:
            kwargs["shape_options"] = self.shape_options
        if self.frame.custom_path:
            kwargs["frame_custom_path"] = self.frame.custom_path
        if self.quiet_zone.gradient:
            kwargs["quiet_zone_gradient"] = self.quiet_zone.gradient
        # Compare with default StyleConfig
        default_style = StyleConfig()
        if self.style.css_classes != default_style.css_classes:
            kwargs["css_classes"] = self.style.css_classes
        # Note: custom_styles doesn't exist in StyleConfig

        # Phase enables
        kwargs["enable_phase1"] = self.phase1.enabled
        kwargs["enable_phase2"] = self.phase2.enabled
        kwargs["enable_phase3"] = self.phase3.enabled

        # Accessibility parameters
        if self.accessibility:
            kwargs.update(
                {
                    "accessibility_enabled": self.accessibility.enabled,
                    "accessibility_id_prefix": self.accessibility.id_prefix,
                    "accessibility_use_stable_ids": self.accessibility.use_stable_ids,
                    "accessibility_include_coordinates": self.accessibility.include_coordinates,  # noqa: E501
                    "accessibility_enable_aria": self.accessibility.enable_aria,
                    "accessibility_root_role": self.accessibility.root_role,
                    "accessibility_module_role": self.accessibility.module_role,
                    "accessibility_root_label": self.accessibility.root_label,  # noqa: E501
                    "accessibility_root_description": self.accessibility.root_description,  # noqa: E501
                    "accessibility_include_module_labels": self.accessibility.include_module_labels,  # noqa: E501
                    "accessibility_include_pattern_labels": self.accessibility.include_pattern_labels,  # noqa: E501
                    "accessibility_optimize_for_screen_readers": self.accessibility.optimize_for_screen_readers,  # noqa: E501
                    "accessibility_group_similar_elements": self.accessibility.group_similar_elements,  # noqa: E501
                    "accessibility_add_structural_markup": self.accessibility.add_structural_markup,  # noqa: E501
                    "accessibility_enable_keyboard_navigation": self.accessibility.enable_keyboard_navigation,  # noqa: E501
                    "accessibility_focus_visible_elements": self.accessibility.focus_visible_elements,  # noqa: E501
                    "accessibility_target_compliance": self.accessibility.target_compliance,  # noqa: E501
                    "accessibility_custom_attributes": self.accessibility.custom_attributes,  # noqa: E501
                }
            )

        return kwargs

    @classmethod
    def json_schema(cls) -> Dict[str, Any]:
        """Generate JSON Schema for the configuration.

        Returns:
            JSON Schema dictionary for external tools and documentation
        """
        return cls.model_json_schema()

    def to_json(self) -> str:
        """Serialize configuration to JSON string.

        Returns:
            JSON string representation of the configuration
        """
        return self.model_dump_json(indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> "RenderingConfig":
        """Create configuration from JSON string.

        Args:
            json_str: JSON string representation

        Returns:
            RenderingConfig instance
        """
        return cls.model_validate_json(json_str)


class PerformanceConfig(BaseModel):
    """Performance and optimization settings."""

    model_config = ConfigDict(validate_default=True, extra="forbid")

    enable_caching: bool = True
    max_cache_size: int = Field(default=100, ge=1, description="Maximum cache size")
    enable_parallel_processing: bool = False
    memory_limit_mb: Optional[int] = Field(
        default=None, ge=1, description="Memory limit in MB"
    )
    debug_timing: bool = False


class DebugConfig(BaseModel):
    """Debug and development settings."""

    model_config = ConfigDict(validate_default=True, extra="forbid")

    debug_mode: bool = False
    debug_stroke: bool = False
    debug_colors: Dict[str, str] = Field(
        default_factory=lambda: {
            "contour": "red",
            "cluster": "blue",
            "enhanced": "green",
        },
        description="Debug colors for different components",
    )
    save_intermediate_results: bool = False
    verbose_logging: bool = False


# Import at end to handle forward references
try:
    from ...a11y.accessibility import AccessibilityConfig

    # Rebuild model to handle forward reference
    RenderingConfig.model_rebuild()
except ImportError:
    # Graceful fallback if accessibility module is not available
    pass
