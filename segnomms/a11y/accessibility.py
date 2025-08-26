"""
Accessibility enhancement utilities for SegnoMMS.

This module provides comprehensive accessibility features including:
- Stable ID generation with configurable prefixes
- ARIA attribute management
- Screen reader optimization
- Keyboard navigation support
- Accessibility validation
"""

import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Set

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ARIARole(str, Enum):
    """Standard ARIA roles for QR code elements."""

    IMG = "img"
    GRAPHICS_DOCUMENT = "graphics-document"
    GRAPHICS_OBJECT = "graphics-object"
    APPLICATION = "application"
    GROUP = "group"
    PRESENTATION = "presentation"


class AccessibilityLevel(str, Enum):
    """WCAG accessibility compliance levels."""

    A = "A"
    AA = "AA"
    AAA = "AAA"


@dataclass
class ElementAccessibility:
    """Accessibility information for a single SVG element."""

    element_id: str
    aria_role: Optional[str] = None
    aria_label: Optional[str] = None
    aria_describedby: Optional[str] = None
    aria_labelledby: Optional[str] = None
    title: Optional[str] = None
    tabindex: Optional[int] = None

    def to_attributes(self) -> Dict[str, str]:
        """Convert to SVG element attributes."""
        attrs = {"id": self.element_id}

        if self.aria_role:
            attrs["role"] = self.aria_role
        if self.aria_label:
            attrs["aria-label"] = self.aria_label
        if self.aria_describedby:
            attrs["aria-describedby"] = self.aria_describedby
        if self.aria_labelledby:
            attrs["aria-labelledby"] = self.aria_labelledby
        if self.title:
            attrs["title"] = self.title
        if self.tabindex is not None:
            attrs["tabindex"] = str(self.tabindex)

        return attrs


class AccessibilityConfig(BaseModel):
    """Comprehensive accessibility configuration."""

    model_config = ConfigDict(validate_default=True, extra="forbid")

    # Enable/disable accessibility features
    enabled: bool = Field(default=True, description="Enable accessibility features")

    # ID generation
    id_prefix: str = Field(default="qr", description="Prefix for generated IDs")
    use_stable_ids: bool = Field(
        default=True, description="Generate stable, predictable IDs"
    )
    include_coordinates: bool = Field(
        default=False, description="Include row/col coordinates in IDs"
    )

    # ARIA support
    enable_aria: bool = Field(default=True, description="Enable ARIA attributes")
    root_role: ARIARole = Field(
        default=ARIARole.IMG, description="ARIA role for root SVG element"
    )
    module_role: Optional[ARIARole] = Field(
        default=None, description="ARIA role for individual modules"
    )

    # Labels and descriptions
    root_label: str = Field(
        default="QR Code", description="ARIA label for root element"
    )
    root_description: Optional[str] = Field(
        default=None, description="Description of QR code content"
    )
    include_module_labels: bool = Field(
        default=False, description="Add labels to individual modules"
    )
    include_pattern_labels: bool = Field(
        default=True, description="Add labels to QR patterns (finder, timing, etc.)"
    )

    # Screen reader optimization
    optimize_for_screen_readers: bool = Field(
        default=True, description="Optimize structure for screen readers"
    )
    group_similar_elements: bool = Field(
        default=True, description="Group similar elements for better navigation"
    )
    add_structural_markup: bool = Field(
        default=True, description="Add structural markup for complex layouts"
    )

    # Interactive features
    enable_keyboard_navigation: bool = Field(
        default=False, description="Enable keyboard navigation"
    )
    focus_visible_elements: List[str] = Field(
        default_factory=lambda: ["root"],
        description="Elements that should be focusable",
    )

    # Compliance level
    target_compliance: AccessibilityLevel = Field(
        default=AccessibilityLevel.AA, description="Target WCAG compliance level"
    )

    # Custom attributes
    custom_attributes: Dict[str, str] = Field(
        default_factory=dict, description="Custom accessibility attributes"
    )

    @field_validator("id_prefix")
    @classmethod
    def validate_id_prefix(cls, v: str) -> str:
        """Validate ID prefix follows HTML standards."""
        if not re.match(r"^[a-zA-Z][a-zA-Z0-9_-]*$", v):
            raise ValueError(
                "ID prefix must start with a letter and contain only "
                "letters, numbers, underscores, and hyphens"
            )
        return v

    @field_validator("focus_visible_elements")
    @classmethod
    def validate_focus_elements(cls, v: List[str]) -> List[str]:
        """Validate focus element names."""
        valid_elements = {
            "root",
            "frame",
            "centerpiece",
            "modules",
            "finder",
            "timing",
            "alignment",
            "data",
        }
        for element in v:
            if element not in valid_elements:
                raise ValueError(
                    f"Invalid focus element: {element}. Must be one of {valid_elements}"
                )
        return v


class IDGenerator:
    """Generates stable, predictable IDs for QR code elements."""

    def __init__(self, config: AccessibilityConfig):
        self.config = config
        self.used_ids: Set[str] = set()
        self.element_counter = 0

    def generate_root_id(self) -> str:
        """Generate ID for the root SVG element."""
        base_id = f"{self.config.id_prefix}-root"
        return self._ensure_unique(base_id)

    def generate_module_id(
        self, row: int, col: int, module_type: str = "module"
    ) -> str:
        """Generate ID for a QR module."""
        if self.config.include_coordinates:
            base_id = f"{self.config.id_prefix}-{module_type}-{row}-{col}"
        else:
            self.element_counter += 1
            base_id = f"{self.config.id_prefix}-{module_type}-{self.element_counter}"

        return self._ensure_unique(base_id)

    def generate_pattern_id(
        self, pattern_type: str, index: Optional[int] = None
    ) -> str:
        """Generate ID for a QR pattern (finder, timing, etc.)."""
        if index is not None:
            base_id = f"{self.config.id_prefix}-{pattern_type}-{index}"
        else:
            base_id = f"{self.config.id_prefix}-{pattern_type}"

        return self._ensure_unique(base_id)

    def generate_group_id(self, group_type: str) -> str:
        """Generate ID for a group element."""
        base_id = f"{self.config.id_prefix}-{group_type}-group"
        return self._ensure_unique(base_id)

    def generate_frame_id(self) -> str:
        """Generate ID for frame element."""
        base_id = f"{self.config.id_prefix}-frame"
        return self._ensure_unique(base_id)

    def generate_centerpiece_id(self) -> str:
        """Generate ID for centerpiece element."""
        base_id = f"{self.config.id_prefix}-centerpiece"
        return self._ensure_unique(base_id)

    def generate_layer_id(self, layer_type: str) -> str:
        """Generate ID for a layer element."""
        base_id = f"{self.config.id_prefix}-layer-{layer_type}"
        return self._ensure_unique(base_id)

    def generate_title_id(self) -> str:
        """Generate ID for title element."""
        base_id = f"{self.config.id_prefix}-title"
        return self._ensure_unique(base_id)

    def generate_desc_id(self) -> str:
        """Generate ID for description element."""
        base_id = f"{self.config.id_prefix}-desc"
        return self._ensure_unique(base_id)

    def _ensure_unique(self, base_id: str) -> str:
        """Ensure ID is unique by adding suffix if needed."""
        if base_id not in self.used_ids:
            self.used_ids.add(base_id)
            return base_id

        counter = 1
        while f"{base_id}-{counter}" in self.used_ids:
            counter += 1

        unique_id = f"{base_id}-{counter}"
        self.used_ids.add(unique_id)
        return unique_id


class AccessibilityEnhancer:
    """Enhances SVG elements with comprehensive accessibility features."""

    def __init__(self, config: AccessibilityConfig):
        self.config = config
        self.id_generator = IDGenerator(config)
        self.element_registry: Dict[str, ElementAccessibility] = {}

    def enhance_root_element(
        self,
        svg_element: ET.Element,
        title: Optional[str] = None,
        description: Optional[str] = None,
    ) -> ElementAccessibility:
        """Enhance the root SVG element with accessibility features."""
        if not self.config.enabled:
            # Even when disabled, add basic title for minimal accessibility
            if title:
                import xml.etree.ElementTree as ET

                title_element = ET.SubElement(svg_element, "title")
                title_element.text = title
            # Use proper ID generation even when disabled
            element_id = self.id_generator.generate_root_id()
            return ElementAccessibility(element_id=element_id)

        # Generate stable ID
        element_id = self.id_generator.generate_root_id()

        # Create accessibility info
        accessibility = ElementAccessibility(
            element_id=element_id,
            aria_role=self.config.root_role.value if self.config.enable_aria else None,
            aria_label=title or self.config.root_label,
            title=title or self.config.root_label,
        )

        # Add description if provided
        if description or self.config.root_description:
            desc_id = f"{element_id}-desc"
            accessibility.aria_describedby = desc_id

        # Add keyboard navigation if enabled
        if (
            self.config.enable_keyboard_navigation
            and "root" in self.config.focus_visible_elements
        ):
            accessibility.tabindex = 0

        # Apply attributes
        self._apply_accessibility_attributes(svg_element, accessibility)

        # Create child elements for title and description (SVG best practice)
        import xml.etree.ElementTree as ET

        if title or self.config.root_label:
            title_text = title or self.config.root_label
            title_id = f"{self.config.id_prefix}-title"
            title_element = ET.SubElement(svg_element, "title", id=title_id)
            title_element.text = title_text
            accessibility.aria_labelledby = title_id

        if description or self.config.root_description:
            desc_text = description or self.config.root_description
            desc_id = f"{self.config.id_prefix}-desc"
            desc_element = ET.SubElement(svg_element, "desc", id=desc_id)
            desc_element.text = desc_text
            accessibility.aria_describedby = desc_id

        # Register element
        self.element_registry[element_id] = accessibility

        return accessibility

    def enhance_module_element(
        self, element: Any, row: int, col: int, module_type: str = "data"
    ) -> ElementAccessibility:
        """Enhance a QR module element with accessibility features."""
        if not self.config.enabled:
            return ElementAccessibility(element_id=f"module-{row}-{col}")

        # Generate ID
        element_id = self.id_generator.generate_module_id(row, col, module_type)

        # Create accessibility info
        accessibility = ElementAccessibility(
            element_id=element_id,
            aria_role=(
                self.config.module_role.value if self.config.module_role else None
            ),
        )

        # Add label if enabled
        if self.config.include_module_labels:
            accessibility.aria_label = (
                f"{module_type} module at row {row}, column {col}"
            )

        # Add title for hover information
        if module_type != "data":  # Add titles for special patterns
            accessibility.title = f"{module_type.title()} pattern module"

        # Apply attributes
        self._apply_accessibility_attributes(element, accessibility)

        # Add data attributes for debugging and testing
        element.set("data-module-type", module_type)
        element.set("data-x", str(row))
        element.set("data-y", str(col))

        # Register element
        self.element_registry[element_id] = accessibility

        return accessibility

    def enhance_pattern_group(
        self, group_element: Any, pattern_type: str, index: int = 0
    ) -> ElementAccessibility:
        """Enhance a pattern group (finder, timing, etc.) with accessibility."""
        if not self.config.enabled:
            return ElementAccessibility(element_id=f"{pattern_type}-{index}")

        # Generate ID
        element_id = self.id_generator.generate_pattern_id(pattern_type, index)

        # Create accessibility info
        accessibility = ElementAccessibility(
            element_id=element_id,
            aria_role=ARIARole.GROUP.value if self.config.enable_aria else None,
        )

        # Add pattern-specific labels
        if self.config.include_pattern_labels:
            labels = {
                "finder": (
                    f"Finder pattern {index + 1}"
                    if index is not None
                    else "Finder pattern"
                ),
                "timing": "Timing pattern",
                "alignment": (
                    f"Alignment pattern {index + 1}"
                    if index is not None
                    else "Alignment pattern"
                ),
                "format": "Format information",
                "version": "Version information",
                "data": "Data modules",
                "quiet": "Quiet zone",
            }
            accessibility.aria_label = labels.get(
                pattern_type, f"{pattern_type} pattern"
            )

        # Apply attributes
        self._apply_accessibility_attributes(group_element, accessibility)

        # Register element
        self.element_registry[element_id] = accessibility

        return accessibility

    def create_description_element(
        self, parent_element: Any, description: str, ref_id: str
    ) -> str:
        """Create a description element and return its ID."""
        import xml.etree.ElementTree as ET

        desc_id = f"{ref_id}-desc"
        desc_element = ET.SubElement(parent_element, "desc", id=desc_id)
        desc_element.text = description

        return desc_id

    def generate_accessibility_report(self) -> Dict[str, Any]:
        """Generate a report of accessibility features applied."""
        report = {
            "enabled": self.config.enabled,
            "compliance_target": self.config.target_compliance.value,
            "total_elements": len(self.element_registry),
            "elements_with_aria": sum(
                1 for elem in self.element_registry.values() if elem.aria_role
            ),
            "elements_with_labels": sum(
                1 for elem in self.element_registry.values() if elem.aria_label
            ),
            "focusable_elements": sum(
                1
                for elem in self.element_registry.values()
                if elem.tabindex is not None
            ),
            "features": {
                "stable_ids": self.config.use_stable_ids,
                "aria_support": self.config.enable_aria,
                "keyboard_navigation": self.config.enable_keyboard_navigation,
                "screen_reader_optimization": self.config.optimize_for_screen_readers,
                "pattern_labels": self.config.include_pattern_labels,
                "module_labels": self.config.include_module_labels,
            },
            "id_statistics": {
                "prefix": self.config.id_prefix,
                "total_generated": len(self.id_generator.used_ids),
                "include_coordinates": self.config.include_coordinates,
            },
        }

        return report

    def validate_accessibility(self, svg_root: Optional[Any] = None) -> List[str]:
        """Validate accessibility implementation and return issues."""
        issues = []

        if not self.config.enabled:
            return ["Accessibility features are disabled"]

        # If svg_root is provided, validate directly from the element
        if svg_root is not None:
            return self._validate_svg_element(svg_root)

        # Check for root element
        root_elements = [
            elem for elem in self.element_registry.values() if "root" in elem.element_id
        ]
        if not root_elements:
            issues.append("No root element found with accessibility attributes")

        # Check ARIA compliance
        if self.config.enable_aria:
            elements_without_role = [
                elem
                for elem in self.element_registry.values()
                if not elem.aria_role and "root" in elem.element_id
            ]
            if elements_without_role:
                issues.append("Root element missing ARIA role")

        # Check keyboard navigation
        if self.config.enable_keyboard_navigation:
            focusable = [
                elem
                for elem in self.element_registry.values()
                if elem.tabindex is not None
            ]
            if not focusable:
                issues.append(
                    "Keyboard navigation enabled but no focusable elements found"
                )

        # Check for proper labeling
        if self.config.target_compliance in [
            AccessibilityLevel.AA,
            AccessibilityLevel.AAA,
        ]:
            unlabeled_interactive = [
                elem
                for elem in self.element_registry.values()
                if elem.tabindex is not None and not elem.aria_label
            ]
            if unlabeled_interactive:
                issues.append("Interactive elements missing ARIA labels")

        return issues

    def _validate_svg_element(self, svg_root: Any) -> List[str]:
        """Validate accessibility of an SVG element directly."""
        issues = []

        # Check for title element
        title_elem = svg_root.find("title")
        if title_elem is None:
            issues.append("Missing title element for accessibility")

        # Check for description element (optional but good for comprehensive
        # accessibility)
        # desc_elem = svg_root.find("desc")  # Not currently used

        # Check for ARIA attributes if enabled
        if self.config.enable_aria:
            if not svg_root.get("role"):
                issues.append("Missing ARIA role attribute")
            if not svg_root.get("aria-label") and title_elem is None:
                issues.append("Missing ARIA label or title element")

        # Check for proper ID structure
        if self.config.use_stable_ids and not svg_root.get("id"):
            issues.append("Missing ID attribute for stable identification")

        return issues

    def _apply_accessibility_attributes(
        self, element: Any, accessibility: ElementAccessibility
    ) -> None:
        """Apply accessibility attributes to an SVG element."""
        attributes = accessibility.to_attributes()

        # Add custom attributes
        attributes.update(self.config.custom_attributes)

        # Apply all attributes
        for key, value in attributes.items():
            if value is not None:
                element.set(key, str(value))


def create_accessibility_config(**kwargs: Any) -> AccessibilityConfig:
    """Factory function to create accessibility configuration with common presets."""
    return AccessibilityConfig(**kwargs)


def create_basic_accessibility() -> AccessibilityConfig:
    """Create basic accessibility configuration (WCAG AA compliance)."""
    return AccessibilityConfig(
        enabled=True,
        target_compliance=AccessibilityLevel.AA,
        enable_aria=True,
        include_pattern_labels=True,
        optimize_for_screen_readers=True,
    )


def create_enhanced_accessibility() -> AccessibilityConfig:
    """Create enhanced accessibility configuration (WCAG AAA compliance)."""
    return AccessibilityConfig(
        enabled=True,
        target_compliance=AccessibilityLevel.AAA,
        enable_aria=True,
        include_pattern_labels=True,
        include_module_labels=True,
        optimize_for_screen_readers=True,
        enable_keyboard_navigation=True,
        focus_visible_elements=["root", "finder", "frame", "centerpiece", "timing"],
        add_structural_markup=True,
    )


def create_minimal_accessibility() -> AccessibilityConfig:
    """Create minimal accessibility configuration."""
    return AccessibilityConfig(
        enabled=True,
        target_compliance=AccessibilityLevel.A,
        enable_aria=False,
        include_pattern_labels=False,
        optimize_for_screen_readers=False,
        use_stable_ids=False,
    )
