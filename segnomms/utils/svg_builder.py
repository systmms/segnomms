"""SVG document building utilities.

This module provides the InteractiveSVGBuilder class for creating
well-structured SVG documents with support for CSS styling, backgrounds,
definitions, and interactive features.

The builder handles:

* SVG root element creation with proper namespaces
* CSS style injection with hover effects
* Background and foreground layering
* Reusable definitions (gradients, patterns, filters)
* Accessibility features (title and description)
* Interactive tooltip support
"""

import xml.etree.ElementTree as ET
from typing import Any, Dict, Optional

from ..core.interfaces import SVGBuilder


class InteractiveSVGBuilder(SVGBuilder):
    """Builder for creating interactive SVG documents with proper structure.

    This class implements the SVGBuilder interface to create well-formed
    SVG documents with support for CSS styling, backgrounds, definitions,
    and interactive features like hover effects and tooltips.

    Example:
        >>> builder = InteractiveSVGBuilder()
        >>> svg = builder.create_svg_root(200, 200, id='my-qr')
        >>> builder.add_styles(svg, interactive=True)
        >>> builder.add_background(svg, 200, 200, '#ffffff')
        >>> builder.add_title_and_description(svg, 'QR Code', 'Scan me!')
    """

    def create_svg_root(self, width: int, height: int, **kwargs) -> ET.Element:
        """Create the root SVG element with proper viewport and namespace.

        Args:
            width: SVG width in pixels
            height: SVG height in pixels
            **kwargs: Additional attributes including:
                id: SVG element ID
                class: CSS class names

        Returns:
            ET.Element: Root SVG element with proper setup
        """
        svg = ET.Element(
            "svg",
            {
                "width": str(width),
                "height": str(height),
                "viewBox": f"0 0 {width} {height}",
                "xmlns": "http://www.w3.org/2000/svg",
                "xmlns:xlink": "http://www.w3.org/1999/xlink",
            },
        )

        # Add optional attributes
        if "id" in kwargs:
            svg.set("id", kwargs["id"])

        if "class" in kwargs:
            svg.set("class", kwargs["class"])

        return svg

    def add_styles(self, svg: ET.Element, interactive: bool = False) -> None:
        """Add CSS styles to the SVG for styling and interactions.

        Args:
            svg: SVG root element to add styles to
            interactive: Enable interactive hover effects
        """
        style_content = self._generate_css_styles(interactive)

        if style_content:
            style = ET.SubElement(svg, "style")
            style.set("type", "text/css")
            style.text = f"\n<![CDATA[\n{style_content}\n]]>\n"

    def add_background(
        self, svg: ET.Element, width: int, height: int, color: str
    ) -> None:
        """Add background rectangle to the SVG.

        Creates a full-size rectangle behind all other elements to provide
        a solid background color.

        Args:
            svg: SVG element to add background to
            width: Background width in pixels
            height: Background height in pixels
            color: CSS color string (e.g., 'white', '#FFFFFF', 'rgb(255,255,255)')
        """
        ET.SubElement(
            svg,
            "rect",
            {
                "x": "0",
                "y": "0",
                "width": str(width),
                "height": str(height),
                "fill": color,
                "class": "qr-background",
            },
        )

    def add_definitions(
        self, svg: ET.Element, definitions: Dict[str, Any]
    ) -> ET.Element:
        """Add a definitions section for reusable SVG elements.

        Creates a <defs> section containing gradients, patterns, and filters
        that can be referenced by other elements in the SVG.

        Args:
            svg: SVG element to add definitions to
            definitions: Dictionary containing:
                gradients: Dict of gradient definitions
                patterns: Dict of pattern definitions
                filters: Dict of filter definitions

        Returns:
            ET.Element: The created defs element
        """
        defs = ET.SubElement(svg, "defs")

        # Add gradients
        if "gradients" in definitions:
            for gradient_id, gradient_data in definitions["gradients"].items():
                self._add_gradient(defs, gradient_id, gradient_data)

        # Add patterns
        if "patterns" in definitions:
            for pattern_id, pattern_data in definitions["patterns"].items():
                self._add_pattern(defs, pattern_id, pattern_data)

        # Add filters
        if "filters" in definitions:
            for filter_id, filter_data in definitions["filters"].items():
                self._add_filter(defs, filter_id, filter_data)

        return defs

    def add_title_and_description(
        self,
        svg: ET.Element,
        title: Optional[str] = None,
        description: Optional[str] = None,
    ) -> None:
        """Add accessibility information to the SVG.

        Adds <title> and <desc> elements for screen readers and
        accessibility tools to properly identify the SVG content.

        Args:
            svg: SVG element to add metadata to
            title: Title text for the SVG (appears in tooltips)
            description: Longer description of the SVG content
        """
        if title:
            title_elem = ET.SubElement(svg, "title")
            title_elem.text = title

        if description:
            desc_elem = ET.SubElement(svg, "desc")
            desc_elem.text = description

    def _generate_css_styles(self, interactive: bool) -> str:
        """Generate CSS styles for the SVG elements.

        Creates comprehensive CSS rules for styling QR code modules,
        including base styles and optional interactive hover effects.

        Args:
            interactive: Whether to include hover effects and transitions

        Returns:
            str: Complete CSS stylesheet content
        """
        styles = []

        # Base styles
        styles.append(
            """
        .qr-background {
            pointer-events: none;
        }

        .qr-module {
            transition: all 0.2s ease;
        }

        .qr-finder {
            fill: currentColor;
        }

        .qr-finder-inner {
            fill: var(--qr-bg-color, white);
        }

        .qr-timing {
            fill: currentColor;
        }

        .qr-data {
            fill: currentColor;
        }

        .qr-alignment {
            fill: currentColor;
        }

        .qr-format {
            fill: currentColor;
        }

        .qr-cluster {
            fill: currentColor;
            stroke: none;
        }

        .qr-contour {
            fill: currentColor;
            stroke: none;
        }
        """
        )

        # Interactive styles
        if interactive:
            styles.append(
                """
            .qr-module:hover {
                filter: brightness(1.2);
            }

            .qr-module.clickable {
                cursor: pointer;
            }

            .qr-module.clickable:hover {
                filter: brightness(1.3) drop-shadow(0 0 3px rgba(0,0,0,0.3));
            }

            .qr-module.selected {
                filter: brightness(1.5) drop-shadow(0 0 5px rgba(255,255,0,0.8));
            }

            .qr-finder:hover {
                fill: #333;
            }

            .qr-data:hover {
                fill: #666;
            }

            .qr-timing:hover {
                fill: #999;
            }

            .qr-cluster:hover {
                fill: #444;
                stroke: #666;
                stroke-width: 1;
            }

            .qr-contour:hover {
                fill: #555;
                stroke: #777;
                stroke-width: 1;
            }

            @media (prefers-reduced-motion: reduce) {
                .qr-module {
                    transition: none;
                }

                .qr-module:hover {
                    transform: none;
                }
            }
            """
            )

        return "\n".join(styles)

    def _add_gradient(
        self, defs: ET.Element, gradient_id: str, gradient_data: Dict[str, Any]
    ) -> None:
        """Add a gradient definition to the defs section.

        Creates either a linear or radial gradient that can be referenced
        by fill or stroke attributes.

        Args:
            defs: Definitions element to add gradient to
            gradient_id: Unique ID for the gradient
            gradient_data: Gradient specification including:
                type: 'linear' or 'radial'
                x1, y1, x2, y2: Linear gradient coordinates
                cx, cy, r: Radial gradient center and radius
                stops: List of color stops
        """
        gradient_type = gradient_data.get("type", "linear")

        if gradient_type == "linear":
            gradient = ET.SubElement(defs, "linearGradient", {"id": gradient_id})
            gradient.set("x1", str(gradient_data.get("x1", "0%")))
            gradient.set("y1", str(gradient_data.get("y1", "0%")))
            gradient.set("x2", str(gradient_data.get("x2", "100%")))
            gradient.set("y2", str(gradient_data.get("y2", "0%")))
        else:  # radial
            gradient = ET.SubElement(defs, "radialGradient", {"id": gradient_id})
            gradient.set("cx", str(gradient_data.get("cx", "50%")))
            gradient.set("cy", str(gradient_data.get("cy", "50%")))
            gradient.set("r", str(gradient_data.get("r", "50%")))

        # Add stops
        for stop_data in gradient_data.get("stops", []):
            stop = ET.SubElement(gradient, "stop")
            stop.set("offset", str(stop_data.get("offset", "0%")))
            stop.set("stop-color", stop_data.get("color", "black"))
            if "opacity" in stop_data:
                stop.set("stop-opacity", str(stop_data["opacity"]))

    def _add_pattern(
        self, defs: ET.Element, pattern_id: str, pattern_data: Dict[str, Any]
    ) -> None:
        """Add a pattern definition to the defs section.

        Creates a repeating pattern that can be used as a fill.

        Args:
            defs: Definitions element to add pattern to
            pattern_id: Unique ID for the pattern
            pattern_data: Pattern specification including:
                width: Pattern width
                height: Pattern height
                patternUnits: Coordinate system for pattern
                elements: Child elements of the pattern
        """
        pattern = ET.SubElement(defs, "pattern", {"id": pattern_id})
        pattern.set("x", str(pattern_data.get("x", "0")))
        pattern.set("y", str(pattern_data.get("y", "0")))
        pattern.set("width", str(pattern_data.get("width", "10")))
        pattern.set("height", str(pattern_data.get("height", "10")))
        pattern.set("patternUnits", pattern_data.get("units", "userSpaceOnUse"))

        # Add pattern content (would need to be implemented based on specific patterns needed)

    def _add_filter(
        self, defs: ET.Element, filter_id: str, filter_data: Dict[str, Any]
    ) -> None:
        """Add a filter definition to the defs section.

        Creates SVG filters for visual effects like drop shadows and blurs.

        Args:
            defs: Definitions element to add filter to
            filter_id: Unique ID for the filter
            filter_data: Filter specification including:
                type: Filter type (e.g., 'dropShadow')
                blur: Blur amount for shadows
                dx, dy: Shadow offset
        """
        filter_elem = ET.SubElement(defs, "filter", {"id": filter_id})

        # Add common filters like drop shadow, blur, etc.
        filter_type = filter_data.get("type", "dropShadow")

        if filter_type == "dropShadow":
            # Create drop shadow filter
            blur = ET.SubElement(filter_elem, "feGaussianBlur")
            blur.set("in", "SourceAlpha")
            blur.set("stdDeviation", str(filter_data.get("blur", "2")))
            blur.set("result", "blur")

            offset = ET.SubElement(filter_elem, "feOffset")
            offset.set("in", "blur")
            offset.set("dx", str(filter_data.get("dx", "2")))
            offset.set("dy", str(filter_data.get("dy", "2")))
            offset.set("result", "offsetBlur")

            merge = ET.SubElement(filter_elem, "feMerge")
            ET.SubElement(merge, "feMergeNode", {"in": "offsetBlur"})
            ET.SubElement(merge, "feMergeNode", {"in": "SourceGraphic"})

    def add_javascript(self, svg: ET.Element, script_content: str) -> None:
        """Add JavaScript to the SVG for interactive behavior.

        Embeds JavaScript code within the SVG document for client-side
        interactivity.

        Args:
            svg: SVG element to add script to
            script_content: JavaScript code to embed

        Warning:
            Be careful with user-provided scripts to avoid XSS vulnerabilities.
        """
        script = ET.SubElement(svg, "script")
        script.set("type", "text/javascript")
        script.text = f"\n<![CDATA[\n{script_content}\n]]>\n"

    def add_interaction_handlers(self, svg: ET.Element) -> None:
        """Add basic interaction handlers for QR module interactions.

        Injects JavaScript event handlers for click events, hover effects,
        and custom events on QR code modules. Modules with the 'clickable'
        class become interactive.

        Args:
            svg: SVG element to add handlers to

        Events:
            qr-module-click: Fired when a clickable module is clicked
        """
        script_content = """
        // QR Code Interactive Handlers
        document.addEventListener('DOMContentLoaded', function() {
            const modules = document.querySelectorAll('.qr-module');

            modules.forEach(function(module) {
                // Add click handler for clickable modules
                if (module.classList.contains('clickable')) {
                    module.addEventListener('click', function(e) {
                        module.classList.toggle('selected');

                        // Dispatch custom event
                        const event = new CustomEvent('qr-module-click', {
                            detail: {
                                element: module,
                                moduleType: module.classList.contains('qr-data') ? 'data' : 'other',
                                position: {
                                    x: parseFloat(module.getAttribute('x') || module.getAttribute('cx')),
                                    y: parseFloat(module.getAttribute('y') || module.getAttribute('cy'))
                                }
                            }
                        });
                        document.dispatchEvent(event);
                    });
                }

                // Add tooltip functionality
                if (module.hasAttribute('title')) {
                    module.addEventListener('mouseenter', function(e) {
                        // Tooltip logic could be implemented here
                    });
                }
            });
        });
        """

        self.add_javascript(svg, script_content)
