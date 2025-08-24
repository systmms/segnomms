"""Accessibility builder for SVG documents.

This module handles accessibility enhancements including ARIA attributes,
semantic structure, and screen reader support.
"""

import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Optional

from ..a11y.accessibility import (
    AccessibilityConfig,
    AccessibilityEnhancer,
    create_basic_accessibility,
)
from .models import LayerStructureConfig, TitleDescriptionConfig


class AccessibilityBuilder:
    """Builder for SVG accessibility features.

    Manages ARIA attributes, semantic structure, titles, descriptions,
    and other accessibility enhancements.
    """

    def __init__(self, accessibility_config: Optional[AccessibilityConfig] = None):
        """Initialize the accessibility builder.

        Args:
            accessibility_config: Configuration for accessibility features
        """
        if accessibility_config and accessibility_config.enabled:
            self.enhancer = AccessibilityEnhancer(accessibility_config)
        else:
            # Create basic accessibility config and enhancer
            basic_config = create_basic_accessibility()
            self.enhancer = AccessibilityEnhancer(basic_config)

    def add_title_and_description(
        self,
        svg: ET.Element,
        title: Optional[str] = None,
        description: Optional[str] = None,
    ) -> None:
        """Add title and description elements for accessibility.

        Args:
            svg: SVG element to add title and description to
            title: Title text for the SVG
            description: Description text for the SVG
        """
        if title is None or title == "":
            return  # Nothing to add
        config = TitleDescriptionConfig(title=title, description=description)

        # Add title element
        if config.title:
            # Remove any existing title
            existing_title = svg.find(".//title")
            if existing_title is not None:
                svg.remove(existing_title)

            title_elem = ET.Element("title")
            title_elem.text = config.title
            svg.insert(0, title_elem)

        # Add description element
        if config.description:
            # Remove any existing description
            existing_desc = svg.find(".//desc")
            if existing_desc is not None:
                svg.remove(existing_desc)

            desc_elem = ET.Element("desc")
            desc_elem.text = config.description
            # Insert after title if it exists, otherwise at beginning
            insert_pos = 1 if config.title else 0
            svg.insert(insert_pos, desc_elem)

        # Set ARIA attributes
        if config.title or config.description:
            # Ensure proper ARIA labeling
            label_id = svg.get("aria-labelledby", "")
            desc_id = svg.get("aria-describedby", "")

            if config.title and not label_id:
                title_elem_found = svg.find(".//title")
                if title_elem_found is not None:
                    title_id = "qr-title"  # Use deterministic ID
                    title_elem_found.set("id", title_id)
                    svg.set("aria-labelledby", title_id)

            if config.description and not desc_id:
                desc_elem_found = svg.find(".//desc")
                if desc_elem_found is not None:
                    desc_id = "qr-desc"  # Use deterministic ID
                    desc_elem_found.set("id", desc_id)
                    svg.set("aria-describedby", desc_id)

    def create_layered_structure(self, svg: ET.Element) -> Dict[str, ET.Element]:
        """Create a semantic layered structure for the SVG.

        Creates groups for different layers (background, modules, overlays)
        with proper semantic markup.

        Args:
            svg: SVG element to structure

        Returns:
            Dictionary mapping layer names to group elements
        """
        # TODO: LayerStructureConfig will be used for configurable layer structure
        # config = LayerStructureConfig()
        layers = {}

        # Background layer (direct child of SVG)
        bg_group = ET.SubElement(
            svg,
            "g",
            attrib={
                "id": "segnomms-background",
                "class": "qr-layer-background", 
                "aria-hidden": "true"
            },
        )
        layers["background"] = bg_group

        # Quiet zone layer (direct child of SVG)
        qz_group = ET.SubElement(
            svg,
            "g",
            attrib={
                "id": "segnomms-quiet-zone",
                "class": "qr-layer-quiet-zone", 
                "aria-hidden": "true"
            },
        )
        layers["quiet_zone"] = qz_group

        # Modules layer (direct child of SVG - main content)
        modules_group = ET.SubElement(
            svg,
            "g",
            attrib={
                "id": "segnomms-modules",
                "class": "qr-modules", 
                "role": "presentation"
            },
        )
        layers["modules"] = modules_group

        # Pattern groups within modules (also returned as accessible layers)
        for pattern_type in [
            "finder",
            "timing", 
            "alignment",
            "format",
            "version",
            "data",
        ]:
            pattern_group = ET.SubElement(
                modules_group,
                "g",
                attrib={
                    "class": f"qr-pattern-{pattern_type}",
                    "data-pattern-type": pattern_type,
                },
            )
            # Add to layers for accessibility enhancement
            layers[f"pattern_{pattern_type}"] = pattern_group

        # Effects layer (direct child of SVG - for frame effects, overlays, etc.)
        effects_group = ET.SubElement(
            svg,
            "g", 
            attrib={
                "id": "segnomms-frame-effects",
                "class": "frame-effects", 
                "pointer-events": "none"
            }
        )
        layers["effects"] = effects_group

        # Frame layer (for backward compatibility)
        layers["frame"] = effects_group

        # Interactive overlay layer (for backward compatibility)  
        layers["overlay"] = effects_group

        return layers

    def enhance_module_accessibility(
        self, element: ET.Element, row: int, col: int, module_type: str = "data"
    ) -> None:
        """Enhance accessibility for individual QR modules.

        Args:
            element: Module element to enhance
            row: Row position of the module
            col: Column position of the module
            module_type: Type of QR module
        """
        # Use the accessibility enhancer
        self.enhancer.enhance_module_element(element, row, col, module_type)

    def enhance_pattern_group_accessibility(
        self, group_element: ET.Element, pattern_type: str, module_count: int
    ) -> None:
        """Enhance accessibility for pattern groups.

        Args:
            group_element: Group element containing pattern modules
            pattern_type: Type of pattern (finder, timing, etc.)
            module_count: Number of modules in the pattern
        """
        # Use the accessibility enhancer
        # Note: AccessibilityEnhancer expects 'index' parameter, but we receive module_count
        # In the test context, module_count is actually used as the pattern index
        self.enhancer.enhance_pattern_group(group_element, pattern_type, module_count)

    def get_accessibility_report(self) -> Dict[str, Any]:
        """Get a report of accessibility features applied.

        Returns:
            Dictionary containing accessibility metrics and features
        """
        return self.enhancer.generate_accessibility_report()

    def validate_accessibility(self) -> List[str]:
        """Validate accessibility compliance.

        Returns:
            List of validation warnings or errors
        """
        return self.enhancer.validate_accessibility()

    def apply_final_enhancements(self, svg: ET.Element) -> None:
        """Apply final accessibility enhancements to the complete SVG.

        Args:
            svg: Complete SVG element
        """
        # Ensure SVG has proper role
        if not svg.get("role"):
            svg.set("role", "img")

        # Check for title and add generic one if missing
        if not svg.find(".//title"):
            self.add_title_and_description(svg, title="QR Code")

        # Ensure proper focus management
        focusable_elements = svg.findall(".//*[@tabindex]")
        if focusable_elements:
            # Set up focus order
            for i, elem in enumerate(focusable_elements):
                if i == 0:
                    elem.set("tabindex", "0")
                else:
                    elem.set("tabindex", "-1")

        # Add skip link for keyboard navigation
        if self.enhancer.config.enable_keyboard_navigation:
            skip_link = ET.Element(
                "a",
                attrib={
                    "href": "#qr-content",
                    "class": "qr-skip-link",
                    "style": "position: absolute; left: -9999px;",
                },
            )
            skip_link.text = "Skip to QR content"
            svg.insert(0, skip_link)
