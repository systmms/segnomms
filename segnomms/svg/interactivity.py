"""SVG interactivity builder for JavaScript and event handlers.

This module handles adding interactive features to SVG documents including
JavaScript code, event handlers, and interactive behaviors.
"""

import xml.etree.ElementTree as ET
from typing import Dict, List

from .models import InteractionConfig


class InteractivityBuilder:
    """Builder for SVG interactive features.

    Manages JavaScript injection, event handlers, and interactive
    behaviors for SVG elements.
    """

    def add_javascript(self, svg: ET.Element, script_content: str) -> None:
        """Add JavaScript code to the SVG document.

        Args:
            svg: SVG element to add JavaScript to
            script_content: JavaScript code to embed
        """
        # Check if script already exists
        existing_script = svg.find(".//script")
        if existing_script is not None:
            # Append to existing script
            existing_script.text = (existing_script.text or "") + "\n" + script_content
        else:
            # Create new script element
            script = ET.SubElement(svg, "script", attrib={"type": "text/javascript"})
            # Use CDATA to prevent XML parsing of JavaScript
            script.text = f"//<![CDATA[\n{script_content}\n//]]>"

    def add_interaction_handlers(self, svg: ET.Element) -> None:
        """Add default interaction handlers to the SVG.

        Adds standard interaction handlers for tooltips, click events,
        and hover effects.

        Args:
            svg: SVG element to add handlers to
        """
        default_handlers = """
        // Default interaction handlers
        document.addEventListener('DOMContentLoaded', function() {
            // Tooltip handling
            const modules = document.querySelectorAll('.qr-module');

            modules.forEach(module => {
                // Show tooltip on hover
                module.addEventListener('mouseenter', function(e) {
                    const tooltip = this.querySelector('.qr-tooltip');
                    if (tooltip) {
                        tooltip.style.display = 'block';
                    }
                });

                // Hide tooltip on leave
                module.addEventListener('mouseleave', function(e) {
                    const tooltip = this.querySelector('.qr-tooltip');
                    if (tooltip) {
                        tooltip.style.display = 'none';
                    }
                });

                // Click handler
                module.addEventListener('click', function(e) {
                    const moduleType = this.getAttribute('data-module-type');
                    const row = this.getAttribute('data-row');
                    const col = this.getAttribute('data-col');

                    // Dispatch custom event
                    const event = new CustomEvent('qrModuleClick', {
                        detail: { type: moduleType, row: row, col: col }
                    });
                    document.dispatchEvent(event);
                });
            });

            // Focus management for keyboard navigation
            const firstModule = document.querySelector('.qr-module');
            if (firstModule) {
                firstModule.setAttribute('tabindex', '0');
            }

            // Keyboard navigation
            document.addEventListener('keydown', function(e) {
                const focused = document.activeElement;
                if (!focused || !focused.classList.contains('qr-module')) return;

                const modules = Array.from(document.querySelectorAll('.qr-module'));
                const currentIndex = modules.indexOf(focused);
                let nextIndex = currentIndex;

                switch(e.key) {
                    case 'ArrowRight':
                        nextIndex = Math.min(currentIndex + 1, modules.length - 1);
                        break;
                    case 'ArrowLeft':
                        nextIndex = Math.max(currentIndex - 1, 0);
                        break;
                    case 'ArrowDown':
                        // Calculate based on grid
                        const cols = Math.sqrt(modules.length);
                        nextIndex = Math.min(currentIndex + cols, modules.length - 1);
                        break;
                    case 'ArrowUp':
                        const colsUp = Math.sqrt(modules.length);
                        nextIndex = Math.max(currentIndex - colsUp, 0);
                        break;
                }

                if (nextIndex !== currentIndex) {
                    e.preventDefault();
                    modules[currentIndex].setAttribute('tabindex', '-1');
                    modules[nextIndex].setAttribute('tabindex', '0');
                    modules[nextIndex].focus();
                }
            });
        });
        """

        self.add_javascript(svg, default_handlers)

    def add_custom_interaction(
        self, svg: ET.Element, element_selector: str, event_type: str, handler_code: str
    ) -> None:
        """Add a custom interaction handler to specific elements.

        Args:
            svg: SVG element to add handler to
            element_selector: CSS selector for target elements
            event_type: Event type (e.g., 'click', 'hover', 'focus')
            handler_code: JavaScript handler code
        """
        custom_handler = f"""
        // Custom interaction handler for {element_selector}
        document.addEventListener('DOMContentLoaded', function() {{
            const elements = document.querySelectorAll('{element_selector}');
            elements.forEach(element => {{
                element.addEventListener('{event_type}', function(e) {{
                    {handler_code}
                }});
            }});
        }});
        """

        self.add_javascript(svg, custom_handler)

    def add_animation_controls(
        self, svg: ET.Element, animations: List[Dict[str, str]]
    ) -> None:
        """Add animation control handlers.

        Args:
            svg: SVG element to add animation controls to
            animations: List of animation configurations
        """
        if not animations:
            return

        animation_code = """
        // Animation control handlers
        const animations = {
        """

        for anim in animations:
            anim_id = anim.get("id", "default")
            animation_code += f"""
            '{anim_id}': {{
                play: function() {{
                    const elem = document.getElementById('{anim_id}');
                    if (elem) elem.beginElement();
                }},
                pause: function() {{
                    const elem = document.getElementById('{anim_id}');
                    if (elem) elem.endElement();
                }},
                restart: function() {{
                    const elem = document.getElementById('{anim_id}');
                    if (elem) {{
                        elem.endElement();
                        elem.beginElement();
                    }}
                }}
            }},
            """

        animation_code += """
        };

        // Expose animation controls globally
        window.qrAnimations = animations;
        """

        self.add_javascript(svg, animation_code)

    def configure_interaction(
        self, element: ET.Element, config: InteractionConfig
    ) -> None:
        """Configure interaction settings for a specific element.

        Args:
            element: Element to configure
            config: Interaction configuration
        """
        # Set data attributes for interaction
        if config.click_handlers:
            element.set("data-clickable", "true")
            element.set("style", element.get("style", "") + "; cursor: pointer;")

        if config.hover_effects:
            element.set("data-hoverable", "true")

        if config.interactive:
            element.set("tabindex", "0")
            element.set("role", "button")

        if config.tooltips:
            # Add tooltip as title for basic support
            element.set("title", "QR Module")

            # Add custom tooltip element for styled tooltips
            if config.hover_effects:
                tooltip = ET.SubElement(
                    element,
                    "text",
                    attrib={
                        "class": "qr-tooltip",
                        "style": "display: none; font-size: 12px;",
                    },
                )
                tooltip.text = "QR Module"
