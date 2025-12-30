"""Refactored SVG rendering orchestration for the SegnoMMS plugin.

This module contains the core SVG generation logic, including the main
generate_interactive_svg function and related rendering utilities.
The code has been refactored to improve maintainability and readability.
"""

import logging
import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Optional, Set, Tuple

from ..algorithms.clustering import ConnectedComponentAnalyzer
from ..config import ConnectivityMode, FinderShape, MergeStrategy, RenderingConfig
from ..core.detector import ModuleDetector
from ..core.matrix import MatrixManipulator
from ..degradation import DegradationManager
from ..shapes.factory import get_shape_factory
from ..svg import InteractiveSVGBuilder, PathClipper
from ..validation.composition import CompositionValidator
from .patterns import _get_pattern_specific_render_kwargs, _get_pattern_specific_style

# Maximum QR code size to prevent DoS attacks
MAX_QR_SIZE = 1000  # ~1000x1000 modules is very large but still reasonable

# Non-styled module types that should always use square shape in safe mode
# Refined scope: only protect the most critical functional patterns
NON_STYLED_MODULES = [
    "finder",  # Critical for QR detection - must remain square
    "finder_inner",  # Critical for QR detection - must remain square
    "timing",  # Important for scanning alignment - should remain square
]


class QRCodeRenderer:
    """Encapsulates the QR code rendering logic with better organization."""

    def __init__(self, qr_code: Any, config: RenderingConfig) -> None:
        """Initialize the renderer with QR code and configuration.

        Args:
            qr_code: Segno QR code object
            config: Rendering configuration
        """
        self.qr_code = qr_code
        self.config = self._apply_degradation(config)
        self.matrix = self._extract_matrix()
        self._validate_size()

        # Initialize components
        self.detector = ModuleDetector(self.matrix, qr_code.version)
        self.svg_builder = InteractiveSVGBuilder(accessibility_config=self.config.accessibility)
        self.shape_factory = get_shape_factory()
        self.logger = logging.getLogger(__name__)

        # Initialize optional components
        self.composition_validator = self._init_composition_validator()
        self.path_clipper: Optional[Any] = None
        self.centerpiece_metadata: Optional[Dict[str, Any]] = None

    def _apply_degradation(self, config: RenderingConfig) -> RenderingConfig:
        """Apply graceful degradation to the configuration."""
        degradation_manager = DegradationManager()
        degraded_config, degradation_result = degradation_manager.apply_degradation(config)

        # Log degradation warnings
        if degradation_result.warning_count > 0:
            logger = logging.getLogger(__name__)
            logger.info(f"Graceful degradation applied " f"{degradation_result.warning_count} warnings")

            for warning in degradation_result.warnings:
                logger.warning(f"Degradation: {warning}")

        return degraded_config

    def _extract_matrix(self) -> List[List[bool]]:
        """Extract boolean matrix from QR code."""
        matrix = []
        for row in self.qr_code.matrix:
            matrix.append([bool(module) for module in row])
        return matrix

    def _validate_size(self) -> None:
        """Check size limits to prevent DoS attacks."""
        size = len(self.matrix)
        if size > MAX_QR_SIZE:
            raise ValueError(
                f"QR code size {size}x{size} exceeds maximum allowed size of "
                f"{MAX_QR_SIZE}x{MAX_QR_SIZE}. This limit exists to prevent "
                f"denial-of-service attacks. If you need to generate larger "
                f"QR codes, please contact support."
            )

    def _init_composition_validator(self) -> Optional[CompositionValidator]:
        """Initialize composition validator if needed."""
        if self.config.frame.shape == "square" and not self.config.centerpiece.enabled:
            return None

        # Extract numeric version from version string (e.g., "M3" -> 3)
        try:
            numeric_version = int("".join(filter(str.isdigit, str(self.qr_code.version))))
        except (ValueError, TypeError):
            # Fallback if version parsing fails
            numeric_version = 3

        validator = CompositionValidator(numeric_version, self.qr_code.error, len(self.matrix))

        # Validate Phase 4 features
        validation_result = validator.validate_all(self.config)
        if not validation_result.valid:
            # Log errors but continue (fail gracefully)
            for error in validation_result.errors:
                self.logger.error(f"Phase 4 validation error: {error}")

        # Log warnings
        for warning in validation_result.warnings:
            self.logger.warning(f"Phase 4 warning: {warning}")

        return validator

    def render(self) -> str:
        """Render the QR code as an interactive SVG string.

        Returns:
            SVG content as string
        """
        # Apply centerpiece clearing if enabled
        self._apply_centerpiece()

        # Setup SVG structure
        svg = self._create_svg_structure()

        # Get modules group for rendering
        layers = self.svg_builder.create_layered_structure(svg)
        modules_group = layers["modules"]

        # Apply frame clipping if needed
        self._apply_frame_clipping(svg, modules_group)

        # Set default fill color
        if not self.config.patterns.enabled:
            modules_group.set("fill", self.config.dark)

        # Process different rendering phases
        processed_positions = set()

        # Phase 1: Island detection and removal
        if self.config.geometry.min_island_modules > 1:
            island_positions = self._detect_islands()
            processed_positions.update(island_positions)

        # Phase 2: Connected component clustering
        if self._should_use_clustering():
            cluster_positions = self._render_clusters(modules_group)
            processed_positions.update(cluster_positions)

        # Phase 3: Regular module rendering
        self._render_individual_modules(layers, processed_positions)

        # Phase 3.5: Add finder halos if pulse animation is enabled
        if getattr(self.config, "animation_pulse", False):
            self._add_finder_halos(svg, layers)

        # Phase 4: Apply pattern group accessibility
        self._enhance_pattern_groups(layers)

        # Convert to string and format
        rough_string = ET.tostring(svg, encoding="unicode")
        return _format_svg_string(rough_string)

    def _apply_centerpiece(self) -> None:
        """Apply centerpiece clearing if enabled."""
        if not self.config.centerpiece.enabled:
            return

        manipulator = MatrixManipulator(self.matrix, self.detector)
        self.matrix = manipulator.clear_centerpiece_area(self.config.centerpiece)
        self.centerpiece_metadata = manipulator.get_centerpiece_metadata(self.config.centerpiece)

    def _create_svg_structure(self) -> ET.Element:
        """Create the base SVG structure with accessibility features."""
        # Calculate dimensions
        module_count = len(self.matrix)
        svg_size = (module_count + 2 * self.config.border) * self.config.scale

        # Prepare accessibility info
        svg_title = "Interactive QR Code"
        svg_description = f"QR Code with {module_count}x{module_count} modules"
        if self.config.accessibility and self.config.accessibility.enabled:
            if self.config.accessibility.root_label:
                svg_title = self.config.accessibility.root_label
            if self.config.accessibility.root_description:
                svg_description = self.config.accessibility.root_description

        # Generate root ID using accessibility configuration if available
        if self.config.accessibility and self.config.accessibility.enabled:
            from ..a11y.accessibility import IDGenerator

            id_generator = IDGenerator(self.config.accessibility)
            root_id = id_generator.generate_root_id()
        else:
            root_id = "qr-code"

        # Create SVG root with accessibility
        svg = self.svg_builder.create_svg_root(
            svg_size,
            svg_size,
            id=root_id,
            title=svg_title,
            description=svg_description,
            **{"class": "interactive-qr"},
        )

        # Add title and description for accessibility (backward compatibility)
        self.svg_builder.add_title_and_description(
            svg,
            title=svg_title,
            description=svg_description,
        )

        # Add enhanced quiet zone background
        self.svg_builder.add_quiet_zone_with_style(svg, self.config.quiet_zone, svg_size, svg_size)

        # Add styles
        self.svg_builder.add_styles(svg, self.config.style.interactive)

        # Add interactive handlers if enabled
        if self.config.style.interactive:
            self.svg_builder.add_interaction_handlers(svg)

        # Add centerpiece metadata if applicable
        if self.centerpiece_metadata:
            bounds = self.centerpiece_metadata.get("bounds", {})
            self.svg_builder.add_centerpiece_metadata(
                svg,
                self.config.centerpiece,
                bounds,
                self.config.scale,
                self.config.border,
            )

        return svg

    def _apply_frame_clipping(self, svg: ET.Element, modules_group: ET.Element) -> Optional[str]:
        """Add frame definitions and apply clipping to modules group."""
        if self.config.frame.shape == "square":
            return None

        # Calculate dimensions
        module_count = len(self.matrix)
        svg_size = (module_count + 2 * self.config.border) * self.config.scale

        # Add frame definitions
        frame_clip_url = self.svg_builder.add_frame_definitions(
            svg,
            self.config.frame,
            svg_size,
            svg_size,
            self.config.border * self.config.scale,
        )

        # Create path clipper
        self.path_clipper = PathClipper(
            self.config.frame.shape,
            svg_size,
            svg_size,
            self.config.border * self.config.scale,
            self.config.frame.corner_radius,
        )

        # Apply frame clipping based on mode (only if frame_clip_url was created)
        if frame_clip_url:
            if self.config.frame.clip_mode == "fade":
                modules_group.set("mask", frame_clip_url)
            else:
                modules_group.set("clip-path", frame_clip_url)

        return frame_clip_url

    def _detect_islands(self) -> Set[Tuple[int, int]]:
        """Detect and mark small island groups for removal."""
        return _detect_and_remove_islands(
            self.matrix,
            self.detector,
            self.config.geometry.min_island_modules,
            self.config.geometry.connectivity.value,
        )

    def _should_use_clustering(self) -> bool:
        """Check if clustering should be used based on configuration."""
        return (
            self.config.phase2.enabled
            and self.config.phase2.use_cluster_rendering
            and self.config.geometry.merge != MergeStrategy.NONE
        )

    def _render_clusters(self, modules_group: ET.Element) -> Set[Tuple[int, int]]:
        """Render connected component clusters and return processed positions."""
        # Configure min cluster size based on merge strategy
        if self.config.geometry.merge == MergeStrategy.AGGRESSIVE:
            min_cluster_size = max(1, self.config.geometry.min_island_modules)
        else:
            min_cluster_size = max(
                self.config.phase2.min_cluster_size,
                self.config.geometry.min_island_modules,
            )

        cluster_analyzer = ConnectedComponentAnalyzer(
            min_cluster_size,
            self.config.phase2.density_threshold,
            self.config.geometry.connectivity.value,
        )

        clusters = cluster_analyzer.process(
            self.matrix,
            self.detector,
            cluster_module_types=self.config.phase2.cluster_module_types,
        )

        processed_positions = set()

        # Render clusters based on merge strategy
        for cluster in clusters:
            # For aggressive merge, render all clusters as single shapes
            # For soft merge, only render clusters that are suitable
            if self.config.geometry.merge == MergeStrategy.AGGRESSIVE or (
                self.config.geometry.merge == MergeStrategy.SOFT
                and cluster["rendering_hints"]["render_as_single_shape"]
            ):
                _render_cluster(
                    modules_group,
                    cluster,
                    self.config,
                    self.detector,
                    self.path_clipper,
                    self.svg_builder,
                )
                processed_positions.update(cluster["positions"])

        return processed_positions

    def _render_individual_modules(
        self, layers: Dict[str, ET.Element], processed_positions: Set[Tuple[int, int]]
    ) -> None:
        """Render individual modules that aren't part of clusters."""
        module_count = len(self.matrix)
        module_index = 0

        for row in range(module_count):
            for col in range(module_count):
                if (row, col) in processed_positions:
                    continue

                if not self.matrix[row][col]:
                    continue

                # Get module type to determine which pattern group to use
                module_type = self.detector.get_module_type(row, col)

                # Determine target group based on module type
                if module_type in ["finder", "finder_inner"]:
                    target_group = layers.get("pattern_finder", layers["modules"])
                elif module_type in ["timing", "timing_horizontal", "timing_vertical"]:
                    target_group = layers.get("pattern_timing", layers["modules"])
                elif module_type in ["alignment"]:
                    target_group = layers.get("pattern_alignment", layers["modules"])
                elif module_type in ["format"]:
                    target_group = layers.get("pattern_format", layers["modules"])
                elif module_type in ["version"]:
                    target_group = layers.get("pattern_version", layers["modules"])
                else:
                    target_group = layers.get("pattern_data", layers["modules"])

                # Render the module
                module_renderer = ModuleRenderer(
                    self.config,
                    self.detector,
                    self.shape_factory,
                    self.path_clipper,
                    self.svg_builder,
                )
                element = module_renderer.render_module(row, col, module_index)

                if element is not None:
                    target_group.append(element)
                    module_index += 1

    def _add_finder_halos(self, svg: ET.Element, layers: Dict[str, ET.Element]) -> None:
        """Add decorative halo elements behind finder patterns for pulse animation."""
        # Find finder pattern positions
        finder_positions = []
        module_count = len(self.matrix)

        # Top-left finder
        finder_positions.append((0, 0))
        # Top-right finder
        finder_positions.append((0, module_count - 7))
        # Bottom-left finder
        finder_positions.append((module_count - 7, 0))

        # Create halos group
        halos_group = ET.Element("g", attrib={"class": "finder-halos", "aria-hidden": "true"})

        # Insert halos group before the modules group
        parent = svg.find(".//g[@class='qr-layer-modules']/..")
        if parent is not None:
            modules_index = list(parent).index(layers["modules"])
            parent.insert(modules_index, halos_group)

        # Add halo for each finder pattern
        for idx, (row, col) in enumerate(finder_positions):
            x = (col + self.config.border) * self.config.scale
            y = (row + self.config.border) * self.config.scale
            size = 7 * self.config.scale  # Finder patterns are 7x7

            # Create halo element (slightly larger than finder)
            ET.SubElement(
                halos_group,
                "rect",
                attrib={
                    "class": "finder-halo",
                    "x": str(x - self.config.scale * 0.5),  # Expand by half a module
                    "y": str(y - self.config.scale * 0.5),
                    "width": str(size + self.config.scale),
                    "height": str(size + self.config.scale),
                    "rx": str(self.config.scale),  # Rounded corners
                    "ry": str(self.config.scale),
                    "fill": self.config.dark,
                    "opacity": "0.3",
                },
            )

    def _enhance_pattern_groups(self, layers: Dict[str, ET.Element]) -> None:
        """Apply accessibility enhancements to pattern groups."""
        pattern_types = [
            ("pattern_finder", "finder"),
            ("pattern_timing", "timing"),
            ("pattern_alignment", "alignment"),
            ("pattern_format", "format"),
            ("pattern_version", "version"),
            ("pattern_data", "data"),
        ]

        for layer_key, pattern_type in pattern_types:
            if layer_key in layers:
                group = layers[layer_key]
                # Count modules in this pattern group
                module_count = len(list(group))
                if module_count > 0:
                    # Apply pattern group accessibility enhancement
                    self.svg_builder.enhance_pattern_group_accessibility(group, pattern_type, module_count)


class ModuleRenderer:
    """Handles rendering of individual QR code modules."""

    def __init__(
        self,
        config: RenderingConfig,
        detector: ModuleDetector,
        shape_factory: Any,
        path_clipper: Optional[PathClipper] = None,
        svg_builder: Any = None,
    ) -> None:
        """Initialize the module renderer.

        Args:
            config: Rendering configuration
            detector: Module detector instance
            shape_factory: Shape factory for creating renderers
            path_clipper: Optional path clipper for frame clipping
            svg_builder: SVG builder for accessibility enhancements
        """
        self.config = config
        self.detector = detector
        self.shape_factory = shape_factory
        self.path_clipper = path_clipper
        self.svg_builder = svg_builder

    def render_module(self, row: int, col: int, module_index: Optional[int] = None) -> Optional[ET.Element]:
        """Render a single module at the given position.

        Args:
            row: Row position
            col: Column position
            module_index: Optional module index for CSS animations

        Returns:
            XML element for the module, or None if skipped
        """
        # Calculate position
        x = (col + self.config.border) * self.config.scale
        y = (row + self.config.border) * self.config.scale

        # Check if module is within frame
        if not self._is_module_in_frame(x, y):
            return None

        # Get module type and determine shape/color
        module_type = self.detector.get_module_type(row, col)
        current_shape, current_color = self._determine_module_style(module_type)

        # Create shape renderer
        shape_renderer = self.shape_factory.create_renderer(current_shape, {})

        # Build render kwargs
        render_kwargs = self._build_render_kwargs(row, col, module_type, current_shape)

        # Apply scale mode if needed
        if not self._apply_scale_mode(x, y, render_kwargs):
            return None  # Module too close to edge

        # Render the module
        element = shape_renderer.render(x, y, int(self.config.scale), **render_kwargs)

        # Apply color
        self._apply_module_color(element, current_color)

        # Add CSS variable for animation index if provided
        if module_index is not None:
            style = element.get("style", "")
            if style and not style.endswith(";"):
                style += ";"
            style += f"--i:{module_index}"
            element.set("style", style)

        # Add tooltip if enabled
        if self.config.style.tooltips:
            self._add_tooltip(element, module_type, row, col)

        # Apply accessibility enhancements if svg_builder is available
        if self.svg_builder:
            self.svg_builder.enhance_module_accessibility(element, row, col, module_type)

        return element  # type: ignore[no-any-return]

    def _is_module_in_frame(self, x: float, y: float) -> bool:
        """Check if module is within the frame boundaries."""
        if not self.path_clipper:
            return True

        # Check module center point
        center_x = x + self.config.scale / 2
        center_y = y + self.config.scale / 2
        return self.path_clipper.is_point_in_frame(center_x, center_y)

    def _determine_module_style(self, module_type: str) -> Tuple[str, str]:
        """Determine the shape and color for a module based on its type."""
        # Apply safe mode - force functional patterns to use square shape
        if self.config.safe_mode and module_type in NON_STYLED_MODULES:
            return "square", self.config.dark

        # Determine current shape with pattern-specific styling support
        current_shape, current_color = _get_pattern_specific_style(
            self.config, module_type, self.config.geometry.shape.value, self.config.dark
        )

        # Legacy finder shape override (for backward compatibility)
        if module_type in ["finder", "finder_inner"] and self.config.finder.shape != FinderShape.SQUARE:
            if self.config.finder.shape == FinderShape.ROUNDED:
                current_shape = "rounded"
            elif self.config.finder.shape == FinderShape.CIRCLE:
                current_shape = "circle"

        return current_shape, current_color

    def _build_render_kwargs(
        self, row: int, col: int, module_type: str, current_shape: str
    ) -> Dict[str, Any]:
        """Build the rendering kwargs for a module."""
        # Get CSS classes safely
        css_classes = self.config.style.css_classes or {}

        # Create get_neighbor function based on connectivity mode
        get_neighbor = self._create_neighbor_function(row, col)

        # Enhanced rendering for Phase 1
        if self.config.phase1.enabled and self.config.phase1.use_enhanced_shapes:
            # Get neighbor analysis
            analysis = self.detector.get_weighted_neighbor_analysis(row, col, module_type)
            # Adjust rendering based on analysis
            analysis_dict = analysis.model_dump() if hasattr(analysis, "model_dump") else analysis.__dict__
            render_kwargs = _get_enhanced_render_kwargs(self.config, analysis_dict, module_type)
        else:
            # Standard rendering
            render_kwargs = {
                "css_class": css_classes.get(module_type, "qr-module"),
            }

        # Apply pattern-specific styling enhancements
        render_kwargs = _get_pattern_specific_render_kwargs(self.config, module_type, render_kwargs)

        # Add common parameters
        render_kwargs["get_neighbor"] = get_neighbor
        render_kwargs["corner_radius"] = self.config.geometry.corner_radius

        # Add shape-specific parameters
        self._add_shape_specific_params(render_kwargs, current_shape, module_type)

        # Add interactive attributes
        if self.config.style.interactive:
            render_kwargs.update(
                {
                    "id": f"module-{row}-{col}",
                    "data-row": str(row),
                    "data-col": str(col),
                    "data-type": module_type,
                }
            )

        return render_kwargs

    def _create_neighbor_function(self, row: int, col: int) -> Any:
        """Create get_neighbor function based on connectivity mode."""
        if self.config.geometry.connectivity == ConnectivityMode.EIGHT_WAY:
            # 8-way connectivity includes diagonals
            def get_neighbor(x_offset: int, y_offset: int, r: int = row, c: int = col) -> bool:
                return self.detector.is_module_active(r + y_offset, c + x_offset)

        else:
            # 4-way connectivity only includes orthogonal neighbors
            def get_neighbor(x_offset: int, y_offset: int, r: int = row, c: int = col) -> bool:
                # Only allow orthogonal neighbors
                if abs(x_offset) + abs(y_offset) == 1:
                    return self.detector.is_module_active(r + y_offset, c + x_offset)
                return False

        return get_neighbor

    def _add_shape_specific_params(self, render_kwargs: Dict[str, Any], shape: str, module_type: str) -> None:
        """Add shape-specific parameters to render kwargs."""
        # Add roundness for RoundedRenderer
        if shape == "rounded":
            # Use corner_radius for roundness, defaulting to 0.3 if not set
            roundness = self.config.geometry.corner_radius if self.config.geometry.corner_radius > 0 else 0.3
            render_kwargs["roundness"] = roundness

        # Add finder-specific parameters
        if module_type == "finder_inner" and self.config.finder.inner_scale != 0.6:
            render_kwargs["scale_factor"] = self.config.finder.inner_scale
        if module_type in ["finder", "finder_inner"] and self.config.finder.stroke > 0:
            render_kwargs["stroke_width"] = self.config.finder.stroke

        # Add shape-specific options
        if self.config.shape_options:
            render_kwargs.update(self.config.shape_options)

    def _apply_scale_mode(self, x: float, y: float, render_kwargs: Dict[str, Any]) -> bool:
        """Apply scale mode adjustments if enabled.

        Returns:
            False if module should be skipped, True otherwise
        """
        if self.config.frame.clip_mode != "scale" or not self.path_clipper:
            return True

        center_x = x + self.config.scale / 2
        center_y = y + self.config.scale / 2
        scale_factor = self.path_clipper.get_scale_factor(
            center_x, center_y, self.config.frame.scale_distance * self.config.scale
        )

        if scale_factor <= 0.1:
            # Module too close to edge, skip rendering
            return False
        elif scale_factor < 1.0:
            # Apply scaling by modifying render_kwargs
            render_kwargs["size_ratio"] = render_kwargs.get("size_ratio", 1.0) * scale_factor

        return True

    def _apply_module_color(self, element: ET.Element, color: str) -> None:
        """Apply color to the module element."""
        if self.config.patterns.enabled:
            # When pattern styling is enabled, always set individual element colors
            element.set("fill", color)
        elif color != self.config.dark:
            # Legacy: only set if different from default
            element.set("fill", color)

    def _add_tooltip(self, element: ET.Element, module_type: str, row: int, col: int) -> None:
        """Add tooltip to the module element."""
        title = ET.SubElement(element, "title")
        title.text = f"{module_type} module at ({row}, {col})"


def generate_interactive_svg(qr_code: Any, config: RenderingConfig) -> str:
    """
    Generate interactive SVG content for a QR code.

    This is the main entry point that maintains backward compatibility.

    Args:
        qr_code: Segno QR code object
        config: Rendering configuration

    Returns:
        SVG content as string

    Raises:
        ValueError: If QR code size exceeds maximum allowed size
    """
    renderer = QRCodeRenderer(qr_code, config)
    return renderer.render()


# Keep the existing helper functions unchanged for compatibility


def _render_cluster(
    group: ET.Element,
    cluster: Dict[str, Any],
    config: RenderingConfig,
    detector: ModuleDetector,
    path_clipper: Any = None,
    svg_builder: Any = None,
) -> None:
    """Render a cluster as a single shape"""
    cluster_analyzer = ConnectedComponentAnalyzer()
    path_data = cluster_analyzer.get_cluster_svg_path(cluster, config.scale, config.border, path_clipper)

    if path_data:
        # Get CSS classes safely
        css_classes = config.style.css_classes or {}

        # Create path element for cluster
        path = ET.SubElement(
            group,
            "path",
            {
                "d": path_data,
                "class": css_classes.get("cluster", "qr-cluster"),
                "fill": config.dark,
            },
        )

        if config.style.interactive:
            current_class = path.get("class") or ""
            path.set("class", current_class + " clickable")
            path.set("data-cluster-size", str(cluster["size"]))
            path.set("data-cluster-type", cluster["shape_type"])

        if config.style.tooltips:
            title = ET.SubElement(path, "title")
            title.text = f"Cluster of {cluster['size']} modules ({cluster['shape_type']})"

        # Apply accessibility enhancements if svg_builder is available
        if svg_builder and cluster["positions"]:
            # Use first position in cluster for accessibility info
            first_position = next(iter(cluster["positions"]))
            row, col = first_position
            # Enhance as a data cluster
            svg_builder.enhance_module_accessibility(path, row, col, "cluster")


def _get_enhanced_render_kwargs(
    config: RenderingConfig, analysis: Dict[str, Any], module_type: str
) -> Dict[str, Any]:
    """Get enhanced rendering parameters based on neighbor analysis"""
    css_classes = config.style.css_classes or {}
    kwargs = {
        "css_class": css_classes.get(module_type, "qr-module"),
    }

    # Adjust size based on connectivity (handle both dict and Pydantic model)
    if hasattr(analysis, "connectivity_strength"):
        connectivity_strength = analysis.connectivity_strength
    else:
        connectivity_strength = analysis.get("connectivity_strength", 0)

    if connectivity_strength > 6:
        kwargs["size_ratio"] = str(config.phase1.size_ratio * 1.1)
    elif connectivity_strength < 2:
        kwargs["size_ratio"] = str(config.phase1.size_ratio * 0.9)
    else:
        kwargs["size_ratio"] = str(config.phase1.size_ratio)

    # Adjust roundness based on flow (handle both dict and Pydantic model)
    if hasattr(analysis, "flow_direction"):
        flow_direction = analysis.flow_direction
    else:
        flow_direction = analysis.get("flow_direction", "none")
    if flow_direction == "horizontal":
        kwargs["roundness"] = str(config.phase1.roundness * 0.7)
    elif flow_direction == "vertical":
        kwargs["roundness"] = str(config.phase1.roundness * 0.7)
    else:
        kwargs["roundness"] = str(config.phase1.roundness)

    return kwargs


def _format_svg_string(svg_string: str) -> str:
    """Basic SVG string formatting for readability"""
    # Simple indentation - more sophisticated formatting could be added
    import re

    # Add newlines after major elements
    svg_string = re.sub(r"(<svg[^>]*>)", r"\1\n", svg_string)
    svg_string = re.sub(r"(<g[^>]*>)", r"\1\n  ", svg_string)
    svg_string = re.sub(r"(</g>)", r"\n\1", svg_string)
    svg_string = re.sub(r"(<rect[^>]*/>)", r"  \1\n", svg_string)
    svg_string = re.sub(r"(<circle[^>]*/>)", r"  \1\n", svg_string)
    svg_string = re.sub(r"(<path[^>]*/>)", r"  \1\n", svg_string)
    svg_string = re.sub(r"(<style[^>]*>.*?</style>)", r"\1\n", svg_string, flags=re.DOTALL)

    return svg_string


def _detect_and_remove_islands(
    matrix: List[List[bool]],
    detector: ModuleDetector,
    min_size: int,
    connectivity_mode: str,
) -> Set[Tuple[int, int]]:
    """Detect and mark small island groups for removal.

    Args:
        matrix: QR code matrix
        detector: Module detector instance
        min_size: Minimum size for valid islands
        connectivity_mode: '4-way' or '8-way' connectivity

    Returns:
        Set of positions belonging to islands smaller than min_size
    """
    visited = set()
    small_islands = set()

    # Use ConnectedComponentAnalyzer to find all islands
    # Convert connectivity_mode to string value for analyzer
    if hasattr(connectivity_mode, "value"):
        conn_value = connectivity_mode.value
    else:
        conn_value = str(connectivity_mode)
    analyzer = ConnectedComponentAnalyzer(1, 0.0, conn_value)

    # Process all module types as islands
    for row in range(len(matrix)):
        for col in range(len(matrix[0])):
            if (row, col) not in visited and matrix[row][col]:
                # Find connected component starting from this position
                component = analyzer._find_connected_component(
                    matrix,
                    detector,
                    row,
                    col,
                    [
                        "data",
                        "finder",
                        "finder_inner",
                        "timing",
                        "alignment",
                        "format",
                        "version",
                        "dark",
                    ],
                )

                # Mark all positions as visited
                positions = component["positions"]
                visited.update(positions)

                # If component is too small, mark for removal
                if len(positions) < min_size:
                    small_islands.update(positions)

    return small_islands
