"""Main plugin module for Segno Interactive SVG Plugin.

This module provides the primary interface for generating interactive SVG QR codes
with custom shapes and advanced rendering features.

"""

import xml.etree.ElementTree as ET
from typing import Any, BinaryIO, Dict, TextIO, Union

from .algorithms.clustering import ConnectedComponentAnalyzer
from .config.schema import RenderingConfig
from .core.detector import ModuleDetector
from .shapes.factory import get_shape_factory
from .utils.svg_builder import InteractiveSVGBuilder


def write(qr_code, out: Union[TextIO, BinaryIO, str], **kwargs) -> None:
    """Write an interactive SVG representation of the QR code.

    This is the main entry point for the segno plugin system. It generates
    an SVG with custom shapes and interactive features.

    Args:
        qr_code: Segno QR code object to render
        out: Output destination - can be a file path (str), text stream, or binary stream
        **kwargs: Rendering options including:

            * shape (str): Shape type for modules (default: 'square')
            * scale (int): Size of each module in pixels (default: 10)
            * border (int): Number of modules for quiet zone (default: 4)
            * dark (str): Color for dark modules (default: 'black')
            * light (str): Color for light modules (default: 'white')
            * safe_mode (bool): Use simple shapes for special patterns (default: True)
            * xmldecl (bool): Include XML declaration (default: True)
            * svgclass (str): CSS class for SVG element (default: 'interactive-qr')
            * lineclass (str): CSS class for path elements (default: None)
            * title (str): SVG title element (default: 'Interactive QR Code')
            * desc (str): SVG description element (default: auto-generated)

    Raises:
        ValueError: If an invalid shape type is specified
        TypeError: If the output type is not supported

    Example:
        >>> import segno
        >>> from segnomms import write
        >>> qr = segno.make("Hello, World!")
        >>> with open('output.svg', 'w') as f:
        ...     write(qr, f, shape='connected', scale=15)
    """
    # Create configuration from kwargs
    config = RenderingConfig.from_kwargs(**kwargs)

    # Generate the SVG content
    svg_content = generate_interactive_svg(qr_code, config)

    # Handle output
    if isinstance(out, str):
        # File path provided
        with open(out, "w", encoding="utf-8") as f:
            f.write(svg_content)
    elif hasattr(out, "write"):
        # Stream provided
        if hasattr(out, "mode") and "b" in out.mode:
            # Binary mode - write as UTF-8 bytes
            out.write(svg_content.encode("utf-8"))
        else:
            # Text mode
            out.write(svg_content)
    else:
        # Fallback
        try:
            out.write(svg_content)
        except TypeError:
            # Binary stream - write as UTF-8 bytes
            out.write(svg_content.encode("utf-8"))


def generate_interactive_svg(qr_code, config: RenderingConfig) -> str:
    """
    Generate interactive SVG content for a QR code.

    Args:
        qr_code: Segno QR code object
        config: Rendering configuration

    Returns:
        SVG content as string
    """
    # Extract matrix from QR code
    matrix = []
    for row in qr_code.matrix:
        matrix.append([bool(module) for module in row])

    # Initialize components
    detector = ModuleDetector(matrix, qr_code.version)
    svg_builder = InteractiveSVGBuilder()
    shape_factory = get_shape_factory()

    # Calculate dimensions
    module_count = len(matrix)
    svg_size = (module_count + 2 * config.border) * config.scale

    # Create SVG root
    svg = svg_builder.create_svg_root(
        svg_size, svg_size, id="qr-code", **{"class": "interactive-qr"}
    )

    # Add title and description for accessibility
    svg_builder.add_title_and_description(
        svg,
        title="Interactive QR Code",
        description=f"QR Code with {module_count}x{module_count} modules",
    )

    # Add background
    svg_builder.add_background(svg, svg_size, svg_size, config.light)

    # Add styles
    svg_builder.add_styles(svg, config.style.interactive)

    # Add interactive handlers if enabled
    if config.style.interactive:
        svg_builder.add_interaction_handlers(svg)

    # Create main group for modules
    modules_group = ET.SubElement(
        svg, "g", {"class": "qr-modules", "fill": config.dark}
    )

    # Process different phases
    processed_positions = set()

    # Phase 2: Connected component clustering
    if config.phase2.enabled and config.phase2.use_cluster_rendering:
        cluster_analyzer = ConnectedComponentAnalyzer(
            config.phase2.min_cluster_size, config.phase2.density_threshold
        )

        clusters = cluster_analyzer.process(
            matrix,
            detector,
            cluster_module_types=config.phase2.cluster_module_types,
        )

        # Render clusters
        for cluster in clusters:
            if cluster["rendering_hints"]["render_as_single_shape"]:
                _render_cluster(modules_group, cluster, config, detector)
                processed_positions.update(cluster["positions"])

    # Phase 1 & Regular module rendering
    for row in range(module_count):
        for col in range(module_count):
            if (row, col) in processed_positions:
                continue

            if not matrix[row][col]:
                continue

            # Calculate position
            x = (col + config.border) * config.scale
            y = (row + config.border) * config.scale

            # Get module type and shape
            module_type = detector.get_module_type(row, col)

            # Apply safe mode - force functional patterns to use square shape
            NON_STYLED_MODULES = [
                "finder",
                "finder_inner",
                "timing",
                "alignment",
                "format",
                "version",
                "dark",
            ]
            current_shape = config.shape
            if config.safe_mode and module_type in NON_STYLED_MODULES:
                current_shape = (
                    "square"  # Always render functional patterns as simple squares
                )

            # Create shape renderer
            shape_renderer = shape_factory.create_renderer(current_shape, {})

            # Get CSS classes safely
            css_classes = config.style.css_classes or {}

            # Create get_neighbor function for this module
            def get_neighbor(x_offset, y_offset, r=row, c=col):
                return detector.is_module_active(r + y_offset, c + x_offset)

            # Enhanced rendering for Phase 1
            if config.phase1.enabled and config.phase1.use_enhanced_shapes:
                # Get neighbor analysis
                analysis = detector.get_weighted_neighbor_analysis(
                    row, col, module_type
                )

                # Adjust rendering based on analysis
                render_kwargs = _get_enhanced_render_kwargs(
                    config, analysis, module_type
                )
            else:
                # Standard rendering
                render_kwargs = {
                    "css_class": css_classes.get(module_type, "qr-module"),
                }

            # Add get_neighbor function for connected shapes
            render_kwargs["get_neighbor"] = get_neighbor

            # Add shape options to render kwargs
            if config.shape_options:
                render_kwargs.update(config.shape_options)

            # Add interactive attributes
            if config.style.interactive:
                render_kwargs.update(
                    {
                        "id": f"module-{row}-{col}",
                        "data-row": str(row),
                        "data-col": str(col),
                        "data-type": module_type,
                    }
                )

            # Render the module
            element = shape_renderer.render(x, y, config.scale, **render_kwargs)

            # Add tooltip if enabled
            if config.style.tooltips:
                title = ET.SubElement(element, "title")
                title.text = f"{module_type} module at ({row}, {col})"

            modules_group.append(element)

    # Convert to string
    rough_string = ET.tostring(svg, encoding="unicode")

    # Pretty print (basic indentation)
    return _format_svg_string(rough_string)


def _render_cluster(
    group: ET.Element,
    cluster: Dict[str, Any],
    config: RenderingConfig,
    detector: ModuleDetector,
) -> None:
    """Render a cluster as a single shape"""
    cluster_analyzer = ConnectedComponentAnalyzer()
    path_data = cluster_analyzer.get_cluster_svg_path(cluster, config.scale)

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
            path.set("class", path.get("class") + " clickable")
            path.set("data-cluster-size", str(cluster["size"]))
            path.set("data-cluster-type", cluster["shape_type"])

        if config.style.tooltips:
            title = ET.SubElement(path, "title")
            title.text = (
                f"Cluster of {cluster['size']} modules ({cluster['shape_type']})"
            )


def _get_enhanced_render_kwargs(
    config: RenderingConfig, analysis: Dict[str, Any], module_type: str
) -> Dict[str, Any]:
    """Get enhanced rendering parameters based on neighbor analysis"""
    css_classes = config.style.css_classes or {}
    kwargs = {
        "css_class": css_classes.get(module_type, "qr-module"),
    }

    # Adjust size based on connectivity
    if analysis["connectivity_strength"] > 6:
        kwargs["size_ratio"] = config.phase1.size_ratio * 1.1
    elif analysis["connectivity_strength"] < 2:
        kwargs["size_ratio"] = config.phase1.size_ratio * 0.9
    else:
        kwargs["size_ratio"] = config.phase1.size_ratio

    # Adjust roundness based on flow
    if analysis["flow_direction"] == "horizontal":
        kwargs["roundness"] = config.phase1.roundness * 0.7
    elif analysis["flow_direction"] == "vertical":
        kwargs["roundness"] = config.phase1.roundness * 0.7
    else:
        kwargs["roundness"] = config.phase1.roundness

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
    svg_string = re.sub(
        r"(<style[^>]*>.*?</style>)", r"\1\n", svg_string, flags=re.DOTALL
    )

    return svg_string


# Plugin registration helper
def register_with_segno():
    """Register this plugin with segno's plugin system"""
    try:
        import segno.writers

        segno.writers._WRITERS["interactive_svg"] = write
        return True
    except (ImportError, AttributeError):
        return False
