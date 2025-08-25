"""SVG definitions builder for gradients, patterns, and filters.

This module handles creating and managing SVG definition elements like
gradients, patterns, and filters that can be reused throughout the document.
"""

import xml.etree.ElementTree as ET
from typing import Any, Dict, Optional, Sequence, Union

from .models import GradientConfig


class DefinitionsBuilder:
    """Builder for SVG definition elements.

    Manages gradients, patterns, filters, and other reusable SVG elements
    that belong in the <defs> section.
    """

    def add_definitions(
        self,
        svg: ET.Element,
        gradients: Optional[Sequence[Union[GradientConfig, Dict[str, Any]]]] = None,
        patterns: Optional[Sequence[Dict[str, Any]]] = None,
        filters: Optional[Sequence[Dict[str, Any]]] = None,
    ) -> ET.Element:
        """Add definitions section to SVG with gradients, patterns, and filters.

        Args:
            svg: SVG element to add definitions to
            gradients: List of gradient configurations
            patterns: List of pattern configurations
            filters: List of filter configurations

        Returns:
            The defs element
        """
        # Find or create defs element
        defs = svg.find(".//defs")
        if defs is None:
            defs = ET.SubElement(svg, "defs")

        # Add gradients
        if gradients:
            for gradient in gradients:
                self._add_gradient(defs, gradient)

        # Add patterns
        if patterns:
            for pattern in patterns:
                self._add_pattern(defs, pattern)

        # Add filters
        if filters:
            for filter_config in filters:
                self._add_filter(defs, filter_config)

        return defs

    def _add_gradient(
        self, defs: ET.Element, gradient: Union[GradientConfig, Dict[str, Any]]
    ) -> None:
        """Add a gradient definition to the defs element.

        Args:
            defs: Defs element to add gradient to
            gradient: Gradient configuration
        """
        # Handle dictionary format (test format or raw dict)
        if isinstance(gradient, dict):
            self._add_gradient_from_dict(defs, gradient)
            return

        # Handle GradientConfig object
        if gradient.gradient_type == "linear":
            grad_elem = ET.SubElement(
                defs,
                "linearGradient",
                attrib={
                    "id": gradient.gradient_id,
                    "x1": str(gradient.x1),
                    "y1": str(gradient.y1),
                    "x2": str(gradient.x2),
                    "y2": str(gradient.y2),
                },
            )
        else:  # radial
            grad_elem = ET.SubElement(
                defs,
                "radialGradient",
                attrib={
                    "id": gradient.gradient_id,
                    "cx": str(gradient.cx),
                    "cy": str(gradient.cy),
                    "r": str(gradient.r),
                },
            )

            # Note: fx and fy not supported in current GradientConfig model

        # Add gradient stops
        if gradient.stops is not None:
            for i, stop_position in enumerate(gradient.stops):
                # Use color from colors list
                color = (
                    gradient.colors[i]
                    if i < len(gradient.colors)
                    else gradient.colors[-1]
                )
                ET.SubElement(
                    grad_elem,
                    "stop",
                    attrib={
                        "offset": str(stop_position),
                        "stop-color": color,
                        "stop-opacity": "1",
                    },
                )
        else:
            # Auto-generate stops based on colors
            for i, color in enumerate(gradient.colors):
                offset = (
                    i / (len(gradient.colors) - 1) if len(gradient.colors) > 1 else 0
                )
                ET.SubElement(
                    grad_elem,
                    "stop",
                    attrib={
                        "offset": str(offset),
                        "stop-color": color,
                        "stop-opacity": "1",
                    },
                )

    def _add_gradient_from_dict(
        self, defs: ET.Element, gradient: Dict[str, Any]
    ) -> None:
        """Add a gradient definition from dictionary format.

        This method handles the test format which may not match GradientConfig model.

        Args:
            defs: Defs element to add gradient to
            gradient: Gradient configuration dictionary
        """
        gradient_type = gradient.get("gradient_type", gradient.get("type", "linear"))
        gradient_id = gradient.get("gradient_id", gradient.get("id"))

        if gradient_type == "linear":
            # Build attributes, preserving original format
            attrib = {"id": gradient_id}

            # Add coordinates, preserving original format (percentages, etc.)
            for coord in ["x1", "y1", "x2", "y2"]:
                if coord in gradient:
                    attrib[coord] = str(gradient[coord])

            grad_elem = ET.SubElement(defs, "linearGradient", attrib=attrib)
        else:  # radial
            # Build attributes for radial gradient
            attrib = {"id": gradient_id}

            # Add coordinates for radial gradients
            for coord in ["cx", "cy", "r", "fx", "fy"]:
                if coord in gradient:
                    attrib[coord] = str(gradient[coord])

            grad_elem = ET.SubElement(defs, "radialGradient", attrib=attrib)

        # Add gradient stops from test format
        stops = gradient.get("stops", [])
        if stops:
            for stop in stops:
                if isinstance(stop, dict):
                    stop_attrib = {}
                    if "offset" in stop:
                        stop_attrib["offset"] = str(stop["offset"])
                    if "color" in stop:
                        stop_attrib["stop-color"] = stop["color"]
                    if "opacity" in stop:
                        stop_attrib["stop-opacity"] = str(stop["opacity"])
                    else:
                        stop_attrib["stop-opacity"] = "1"

                    ET.SubElement(grad_elem, "stop", attrib=stop_attrib)

    def _add_pattern(self, defs: ET.Element, pattern: Dict[str, Any]) -> None:
        """Add a pattern definition to the defs element.

        Args:
            defs: Defs element to add pattern to
            pattern: Pattern configuration dictionary
        """
        pattern_elem = ET.SubElement(
            defs,
            "pattern",
            attrib={
                "id": pattern["id"],
                "x": str(pattern.get("x", 0)),
                "y": str(pattern.get("y", 0)),
                "width": str(pattern["width"]),
                "height": str(pattern["height"]),
                "patternUnits": pattern.get("patternUnits", "userSpaceOnUse"),
            },
        )

        # Add pattern content
        if "content" in pattern:
            # Pattern content should be a list of element configurations
            for element in pattern["content"]:
                self._create_pattern_element(pattern_elem, element)

    def _add_filter(self, defs: ET.Element, filter_config: Dict[str, Any]) -> None:
        """Add a filter definition to the defs element.

        Args:
            defs: Defs element to add filter to
            filter_config: Filter configuration dictionary
        """
        filter_elem = ET.SubElement(defs, "filter", attrib={"id": filter_config["id"]})

        # Add filter primitives based on type
        filter_type = filter_config.get("type", "custom")

        if filter_type == "blur":
            ET.SubElement(
                filter_elem,
                "feGaussianBlur",
                attrib={"stdDeviation": str(filter_config.get("stdDeviation", 2))},
            )
        elif filter_type in ("shadow", "dropShadow"):
            # Drop shadow filter
            _ = ET.SubElement(
                filter_elem,
                "feGaussianBlur",
                attrib={
                    "in": "SourceAlpha",
                    "stdDeviation": str(filter_config.get("blur", 3)),
                },
            )
            _ = ET.SubElement(
                filter_elem,
                "feOffset",
                attrib={
                    "dx": str(filter_config.get("dx", 2)),
                    "dy": str(filter_config.get("dy", 2)),
                    "result": "offsetblur",
                },
            )
            _ = ET.SubElement(
                filter_elem,
                "feFlood",
                attrib={
                    "flood-color": filter_config.get("color", "#000000"),
                    "flood-opacity": str(filter_config.get("opacity", 0.5)),
                },
            )
            _ = ET.SubElement(
                filter_elem,
                "feComposite",
                attrib={"in2": "offsetblur", "operator": "in"},
            )
            merge = ET.SubElement(filter_elem, "feMerge")
            ET.SubElement(merge, "feMergeNode")
            ET.SubElement(merge, "feMergeNode", attrib={"in": "SourceGraphic"})
        elif filter_type == "custom" and "primitives" in filter_config:
            # Custom filter with explicit primitives
            for primitive in filter_config["primitives"]:
                self._create_filter_primitive(filter_elem, primitive)

    def _create_pattern_element(
        self, pattern_elem: ET.Element, element_config: Dict[str, Any]
    ) -> None:
        """Create an element within a pattern.

        Args:
            pattern_elem: Pattern element to add content to
            element_config: Element configuration
        """
        elem_type = element_config.get("type", "rect")
        attribs = {k: str(v) for k, v in element_config.items() if k != "type"}
        ET.SubElement(pattern_elem, elem_type, attrib=attribs)

    def _create_filter_primitive(
        self, filter_elem: ET.Element, primitive_config: Dict[str, Any]
    ) -> None:
        """Create a filter primitive element.

        Args:
            filter_elem: Filter element to add primitive to
            primitive_config: Primitive configuration
        """
        prim_type = primitive_config.get("type")
        if prim_type:
            attribs = {k: str(v) for k, v in primitive_config.items() if k != "type"}
            ET.SubElement(filter_elem, prim_type, attrib=attribs)
