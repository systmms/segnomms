Accessibility
=============

This module provides accessibility enhancements for QR code generation.

Accessibility System
---------------------

.. automodule:: segnomms.a11y
   :members:
   :undoc-members:
   :show-inheritance:

Accessibility Enhancer
-----------------------

.. autoclass:: segnomms.a11y.AccessibilityEnhancer
   :no-index:
   :members:
   :undoc-members:
   :show-inheritance:

ARIA Roles
----------

.. autoclass:: segnomms.a11y.ARIARole
   :no-index:
   :members:
   :undoc-members:
   :show-inheritance:

Configuration
-------------

.. autoclass:: segnomms.a11y.AccessibilityConfig
   :no-index:
   :members:
   :undoc-members:
   :show-inheritance:

Example Usage
-------------

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

Configuration setup::

    from segnomms.a11y import AccessibilityConfig

    config = AccessibilityConfig(
        enable_aria=True,
        enable_screen_reader=True,
        enable_keyboard_nav=True,
        default_title="Interactive QR Code",
        default_description="Scannable QR code with custom styling"
    )
