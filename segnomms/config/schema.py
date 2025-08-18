"""Configuration schema using dataclasses for type safety and validation.

This module defines all configuration classes used by the plugin, including:

* Phase configurations for the multi-phase rendering pipeline
* Style configurations for CSS and interactivity
* Main rendering configuration that combines all settings
* Plugin-specific configuration for Segno integration

"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class ContourMode(Enum):
    """Contour rendering modes for Phase 3.

    Attributes:
        BEZIER: Use Bezier curves for smooth contours
        COMBINED: Combine multiple contour strategies
        OVERLAY: Overlay contours on existing shapes
    """

    BEZIER = "bezier"
    COMBINED = "combined"
    OVERLAY = "overlay"


class OptimizationLevel(Enum):
    """Optimization levels for Bezier curve generation.

    Attributes:
        LOW: Minimal optimization, fastest rendering
        MEDIUM: Balanced optimization (default)
        HIGH: Maximum optimization, smallest file size
    """

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class Phase1Config:
    """Configuration for Phase 1: Enhanced 8-neighbor detection.

    This phase handles context-aware shape rendering based on neighboring modules.

    Attributes:
        enabled: Whether Phase 1 processing is enabled
        use_enhanced_shapes: Use enhanced shape variants
        roundness: Corner roundness factor (0.0-1.0)
        size_ratio: Module size relative to grid size (0.1-1.0)
        flow_weights: Weight factors for different module types
    """

    enabled: bool = False
    use_enhanced_shapes: bool = False
    roundness: float = 0.3
    size_ratio: float = 0.9
    flow_weights: Optional[Dict[str, float]] = None

    def __post_init__(self):
        if self.flow_weights is None:
            self.flow_weights = {
                "finder": 0.5,
                "finder_inner": 0.3,
                "timing": 0.8,
                "data": 1.0,
                "alignment": 0.6,
                "format": 0.7,
            }


@dataclass
class Phase2Config:
    """Configuration for Phase 2: Connected component clustering.

    This phase groups connected modules for optimized rendering.

    Attributes:
        enabled: Whether Phase 2 processing is enabled
        use_cluster_rendering: Render clusters as single shapes
        cluster_module_types: Module types to include in clustering
        min_cluster_size: Minimum modules required to form a cluster
        density_threshold: Minimum density for valid clusters (0.0-1.0)
        aspect_ratio_tolerance: Maximum deviation from square clusters (0.0-1.0)
    """

    enabled: bool = False
    use_cluster_rendering: bool = False
    cluster_module_types: List[str] = field(default_factory=lambda: ["data"])
    min_cluster_size: int = 3
    density_threshold: float = 0.5
    aspect_ratio_tolerance: float = 0.3


@dataclass
class Phase3Config:
    """Configuration for Phase 3: Marching squares with Bezier curves.

    This phase creates smooth contours around module groups.

    Attributes:
        enabled: Whether Phase 3 processing is enabled
        use_marching_squares: Apply marching squares algorithm
        contour_module_types: Module types to generate contours for
        contour_mode: Contour rendering strategy
        contour_smoothing: Smoothing factor for contours (0.0-1.0)
        bezier_optimization: Optimization level for curve generation
        tension: Bezier curve tension (0.0-1.0)
        point_reduction: Factor for reducing control points (0.0-1.0)
    """

    enabled: bool = False
    use_marching_squares: bool = False
    contour_module_types: List[str] = field(default_factory=lambda: ["data"])
    contour_mode: ContourMode = ContourMode.BEZIER
    contour_smoothing: float = 0.3
    bezier_optimization: OptimizationLevel = OptimizationLevel.MEDIUM
    tension: float = 0.3
    point_reduction: float = 0.7


@dataclass
class StyleConfig:
    """CSS and styling configuration.

    Controls visual styling and interactivity features.

    Attributes:
        css_classes: Mapping of module types to CSS classes
        custom_styles: Additional CSS styles to inject
        interactive: Enable interactive features
        tooltips: Enable tooltip display on hover
    """

    css_classes: Optional[Dict[str, str]] = None
    custom_styles: Optional[str] = None
    interactive: bool = False
    tooltips: bool = False

    def __post_init__(self):
        if self.css_classes is None:
            self.css_classes = {
                "finder": "qr-module qr-finder",
                "finder_inner": "qr-module qr-finder-inner",
                "timing": "qr-module qr-timing",
                "data": "qr-module qr-data",
                "alignment": "qr-module qr-alignment",
                "format": "qr-module qr-format",
                "cluster": "qr-cluster",
                "contour": "qr-contour",
            }


@dataclass
class RenderingConfig:
    """Main rendering configuration that combines all phases.

    This is the primary configuration class that controls all aspects
    of QR code rendering.

    Attributes:
        scale: Size of each module in pixels
        border: Quiet zone size in modules
        dark: Color for dark modules (CSS color string)
        light: Color for light modules (CSS color string)
        phase1: Phase 1 configuration
        phase2: Phase 2 configuration
        phase3: Phase 3 configuration
        style: Style configuration
        xmldecl: Include XML declaration
        title: SVG title element content
        desc: SVG description element content
        svgclass: CSS class for SVG element
        lineclass: CSS class for path elements
        svgid: ID attribute for SVG element
        svgversion: SVG version number
        encoding: Character encoding for XML
        indent: Number of spaces for indentation
        newline: Newline character
        nl: Add newlines to output
        omitsize: Omit width/height attributes
    """

    scale: int = 8
    border: int = 2
    dark: str = "black"
    light: str = "white"

    # Phase configurations
    phase1: Phase1Config = field(default_factory=Phase1Config)
    phase2: Phase2Config = field(default_factory=Phase2Config)
    phase3: Phase3Config = field(default_factory=Phase3Config)

    # Styling
    style: StyleConfig = field(default_factory=StyleConfig)

    # Legacy support for direct kwargs
    shape: str = "square"
    shape_options: Optional[Dict[str, Any]] = None

    # Safe mode - forces functional patterns to render as simple squares
    safe_mode: bool = True

    @classmethod
    def from_kwargs(cls, **kwargs) -> "RenderingConfig":
        """Create configuration from legacy kwargs format.

        This method converts keyword arguments into a proper RenderingConfig
        instance, maintaining backward compatibility with the original API.

        Args:
            **kwargs: Keyword arguments including:
                scale (int): Module size in pixels
                border (int): Quiet zone size
                dark (str): Dark module color
                light (str): Light module color
                shape (str): Shape type name
                safe_mode (bool): Use safe rendering mode
                shape_options (dict): Additional shape parameters

        Returns:
            RenderingConfig: Configured instance

        Example:
            >>> config = RenderingConfig.from_kwargs(
            ...     shape='star',
            ...     scale=20,
            ...     star_points=8,
            ...     inner_ratio=0.3
            ... )
        """
        config = cls()

        # Basic rendering parameters
        config.scale = kwargs.get("scale", 8)
        config.border = kwargs.get("border", 2)
        config.dark = kwargs.get("dark", "black")
        config.light = kwargs.get("light", "white")
        config.shape = kwargs.get("shape", "square")
        config.safe_mode = kwargs.get("safe_mode", True)

        # Shape options (legacy)
        shape_options = kwargs.get("shape_options", {})
        config.shape_options = shape_options

        # Pass through other kwargs as shape options
        for key, value in kwargs.items():
            if key not in [
                "scale",
                "border",
                "dark",
                "light",
                "shape",
                "safe_mode",
                "shape_options",
            ]:
                if config.shape_options is None:
                    config.shape_options = {}
                config.shape_options[key] = value

        # Phase 1 configuration
        if shape_options.get("use_enhanced_shapes", False):
            config.phase1.enabled = True
            config.phase1.use_enhanced_shapes = True
            config.phase1.roundness = shape_options.get("roundness", 0.3)
            config.phase1.size_ratio = shape_options.get("size_ratio", 0.9)

        # Phase 2 configuration
        if shape_options.get("use_cluster_rendering", False):
            config.phase2.enabled = True
            config.phase2.use_cluster_rendering = True
            config.phase2.cluster_module_types = shape_options.get(
                "cluster_module_types", ["data"]
            )
            config.phase2.min_cluster_size = shape_options.get("min_cluster_size", 3)

        # Phase 3 configuration
        if shape_options.get("use_marching_squares", False):
            config.phase3.enabled = True
            config.phase3.use_marching_squares = True
            config.phase3.contour_module_types = shape_options.get(
                "contour_module_types", ["data"]
            )

            contour_mode_str = shape_options.get("contour_mode", "bezier")
            try:
                config.phase3.contour_mode = ContourMode(contour_mode_str)
            except ValueError:
                config.phase3.contour_mode = ContourMode.BEZIER

            config.phase3.contour_smoothing = shape_options.get(
                "contour_smoothing", 0.3
            )

            optimization_str = shape_options.get("bezier_optimization", "medium")
            try:
                config.phase3.bezier_optimization = OptimizationLevel(optimization_str)
            except ValueError:
                config.phase3.bezier_optimization = OptimizationLevel.MEDIUM

        # Style configuration
        config.style.css_classes = kwargs.get("css_classes")
        config.style.interactive = kwargs.get("interactive", False)
        config.style.tooltips = kwargs.get("tooltips", False)

        return config

    def to_kwargs(self) -> Dict[str, Any]:
        """Convert configuration back to kwargs format for compatibility."""
        kwargs = {
            "scale": self.scale,
            "border": self.border,
            "dark": self.dark,
            "light": self.light,
            "shape": self.shape,
            "safe_mode": self.safe_mode,
            "interactive": self.style.interactive,
            "tooltips": self.style.tooltips,
        }

        if self.style.css_classes:
            kwargs["css_classes"] = self.style.css_classes

        # Build shape_options
        shape_options = {}

        if self.phase1.enabled:
            shape_options.update(
                {
                    "use_enhanced_shapes": self.phase1.use_enhanced_shapes,
                    "roundness": self.phase1.roundness,
                    "size_ratio": self.phase1.size_ratio,
                }
            )

        if self.phase2.enabled:
            shape_options.update(
                {
                    "use_cluster_rendering": self.phase2.use_cluster_rendering,
                    "cluster_module_types": self.phase2.cluster_module_types,
                    "min_cluster_size": self.phase2.min_cluster_size,
                }
            )

        if self.phase3.enabled:
            shape_options.update(
                {
                    "use_marching_squares": self.phase3.use_marching_squares,
                    "contour_module_types": self.phase3.contour_module_types,
                    "contour_mode": self.phase3.contour_mode.value,
                    "contour_smoothing": self.phase3.contour_smoothing,
                    "bezier_optimization": self.phase3.bezier_optimization.value,
                }
            )

        if shape_options:
            kwargs["shape_options"] = shape_options

        return kwargs

    def validate(self) -> List[str]:
        """Validate the configuration and return any error messages."""
        errors = []

        if self.scale <= 0:
            errors.append("Scale must be positive")

        if self.border < 0:
            errors.append("Border must be non-negative")

        if not (0.0 <= self.phase1.roundness <= 1.0):
            errors.append("Phase1 roundness must be between 0.0 and 1.0")

        if not (0.0 <= self.phase1.size_ratio <= 1.0):
            errors.append("Phase1 size_ratio must be between 0.0 and 1.0")

        if self.phase2.min_cluster_size < 2:
            errors.append("Phase2 min_cluster_size must be at least 2")

        if not (0.0 <= self.phase3.contour_smoothing <= 1.0):
            errors.append("Phase3 contour_smoothing must be between 0.0 and 1.0")

        if not (0.0 <= self.phase3.tension <= 1.0):
            errors.append("Phase3 tension must be between 0.0 and 1.0")

        return errors


@dataclass
class PerformanceConfig:
    """Performance and optimization settings."""

    enable_caching: bool = True
    max_cache_size: int = 100
    enable_parallel_processing: bool = False
    memory_limit_mb: Optional[int] = None
    debug_timing: bool = False


@dataclass
class DebugConfig:
    """Debug and development settings."""

    debug_mode: bool = False
    debug_stroke: bool = False
    debug_colors: Dict[str, str] = field(
        default_factory=lambda: {
            "contour": "red",
            "cluster": "blue",
            "enhanced": "green",
        }
    )
    save_intermediate_results: bool = False
    verbose_logging: bool = False
