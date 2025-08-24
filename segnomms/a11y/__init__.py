"""Accessibility enhancement subsystem.

This package provides comprehensive accessibility features for QR code
generation, ensuring compliance with accessibility standards and best
practices for assistive technologies.

Key Components:

    ARIA Support:
        - Role definitions and management
        - Label and description generation
        - Live region support

    ID Management:
        - Stable, predictable ID generation
        - Configurable prefixes and schemes
        - Conflict resolution

    Screen Reader Optimization:
        - Semantic SVG structure
        - Alternative text generation
        - Content description

    Keyboard Navigation:
        - Focus management
        - Tab order optimization
        - Keyboard shortcuts

The accessibility subsystem handles:

* ARIA attribute management
* Screen reader compatibility
* Keyboard navigation support
* ID generation and management
* Accessibility validation
* WCAG compliance checking
* Alternative content generation

Example:
    Basic accessibility enhancement::

        from segnomms.a11y import AccessibilityEnhancer, ARIARole

        enhancer = AccessibilityEnhancer(
            id_prefix="qr",
            default_role=ARIARole.IMG
        )

        # Generate stable IDs
        module_id = enhancer.generate_id("module", 5, 3)

        # Add ARIA attributes
        aria_attrs = enhancer.get_aria_attributes(
            role=ARIARole.GRAPHICS_OBJECT,
            label="QR code module at position 5,3"
        )

See Also:
    :mod:`segnomms.a11y.accessibility`: Core accessibility features
"""

from .accessibility import (
    AccessibilityConfig,
    AccessibilityEnhancer,
    ARIARole,
)

__all__ = [
    "AccessibilityEnhancer",
    "ARIARole",
    "AccessibilityConfig",
]
