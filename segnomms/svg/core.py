"""Core SVG building functionality.

This module provides the base SVG building operations including creating
root elements, adding styles, and managing backgrounds.
"""

import xml.etree.ElementTree as ET
from typing import Any, Dict, Optional

from ..core.interfaces import SVGBuilder
from .models import BackgroundConfig, SVGElementConfig


class CoreSVGBuilder(SVGBuilder):
    """Core SVG document builder for basic operations.

    Handles fundamental SVG operations like creating root elements,
    adding CSS styles, and managing background elements.
    """

    def create_svg_root(self, width: int, height: int, **kwargs: Any) -> ET.Element:
        """Create the root SVG element with proper attributes and namespaces.

        Args:
            width: Width of the SVG in pixels
            height: Height of the SVG in pixels
            **kwargs: Additional attributes for the SVG element

        Returns:
            Root SVG Element with configured attributes
        """
        config = SVGElementConfig(width=width, height=height, **kwargs)

        # Create SVG element with namespace
        ET.register_namespace("", "http://www.w3.org/2000/svg")
        ET.register_namespace("xlink", "http://www.w3.org/1999/xlink")

        svg = ET.Element(
            "svg",
            attrib={
                "width": str(config.width),
                "height": str(config.height),
                "viewBox": f"0 0 {config.width} {config.height}",
                "xmlns": "http://www.w3.org/2000/svg",
                "xmlns:xlink": "http://www.w3.org/1999/xlink",
            },
        )

        # Add ID if provided
        if config.id:
            svg.set("id", config.id)

        # Add CSS classes if provided
        if config.css_class:
            svg.set("class", config.css_class)

        return svg

    def add_styles(
        self,
        svg: ET.Element,
        interactive: bool = False,
        animation_config: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Add CSS styles to the SVG.

        Args:
            svg: SVG element to add styles to
            interactive: Whether to include interactive hover styles
            animation_config: Optional animation configuration dict
        """
        # Check if styles already exist
        existing_style = svg.find(".//style")
        if existing_style is not None:
            return

        style_content = self._generate_css_styles(interactive, animation_config)

        if style_content:
            style = ET.SubElement(svg, "style", attrib={"type": "text/css"})
            style.text = f"\n<![CDATA[\n{style_content}\n]]>\n"

    def add_background(
        self, svg: ET.Element, width: int, height: int, color: str, **kwargs: Any
    ) -> None:
        """Add a background rectangle to the SVG.

        Args:
            svg: SVG element to add background to
            width: Width of the background
            height: Height of the background
            color: Background color
            **kwargs: Additional background configuration options
        """
        config = BackgroundConfig(width=width, height=height, color=color, **kwargs)

        # Create background rectangle
        ET.SubElement(
            svg,
            "rect",
            attrib={
                "x": "0",
                "y": "0",
                "width": str(config.width),
                "height": str(config.height),
                "fill": config.color,
                "class": "qr-background",
            },
        )

    def _generate_css_styles(
        self, interactive: bool, animation_config: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate CSS styles for the SVG.

        Args:
            interactive: Whether to include interactive styles
            animation_config: Optional animation configuration dict

        Returns:
            CSS style string
        """
        styles = []

        # Base styles (matching original)
        styles.append(
            """
        .qr-background {
            pointer-events: none;
        }
        /* Transform geometry fixes to prevent wiggle during animations */
        .qr-root, .qr-module, .qr-finder, .qr-timing, .qr-data,
        .qr-alignment, .qr-format, .qr-cluster, .qr-contour {
            transform-box: fill-box;
            transform-origin: center;
            animation-fill-mode: both;
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

        # Interactive styles (matching original)
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

        # Animation styles
        if animation_config:
            animation_styles = self._generate_animation_styles(animation_config)
            if animation_styles:
                styles.append(animation_styles)

        return "\n".join(styles)

    def _generate_animation_styles(self, config: Dict[str, Any]) -> str:
        """Generate CSS animation styles based on configuration.

        Args:
            config: Animation configuration dictionary

        Returns:
            CSS animation styles string
        """
        animation_styles = []

        # Extract animation settings
        fade_in = config.get("animation_fade_in", False)
        fade_duration = config.get("animation_fade_duration", 0.5)
        stagger = config.get("animation_stagger", False)
        stagger_delay = config.get("animation_stagger_delay", 0.02)
        pulse = config.get("animation_pulse", False)
        timing = config.get("animation_timing", "ease")

        # Fade-in animation
        if fade_in:
            animation_styles.append(
                f"""
            @keyframes qrFadeIn {{
                from {{
                    opacity: 0;
                    transform: scale(0.8);
                }}
                to {{
                    opacity: 1;
                    transform: scale(1);
                }}
            }}

            .qr-module {{
                animation: qrFadeIn {fade_duration}s {timing} both;
            }}
            """
            )

            # Stagger support using CSS variables
            if stagger:
                animation_styles.append(
                    f"""
            /* Staggered animation delays using CSS variables */
            .qr-root {{
                --stagger-step: {stagger_delay}s;
            }}

            .qr-module {{
                animation-delay: calc(var(--i, 0) * var(--stagger-step));
            }}
            """
                )

        # Pulse effect for finder patterns (using halos)
        if pulse:
            animation_styles.append(
                f"""
            @keyframes qrPulse {{
                0%, 100% {{
                    transform: scale(1);
                    opacity: 0.3;
                }}
                50% {{
                    transform: scale(1.1);
                    opacity: 0.1;
                }}
            }}

            /* Pulse effect on finder halos only, not the actual patterns */
            .finder-halo {{
                animation: qrPulse 2s {timing} infinite;
                transform-origin: center;
                pointer-events: none;
            }}

            .finder-halo:nth-child(1) {{ animation-delay: 0s; }}
            .finder-halo:nth-child(2) {{ animation-delay: 0.66s; }}
            .finder-halo:nth-child(3) {{ animation-delay: 1.33s; }}

            /* Ensure actual finder patterns are not animated */
            .qr-finder {{
                animation: none !important;
            }}
            """
            )

        # Respect reduced motion preferences
        animation_styles.append(
            """
        @media (prefers-reduced-motion: reduce) {
            .qr-root * {
                animation: none !important;
                transition: none !important;
                animation-delay: 0s !important;
            }
        }
        @media print {
            .qr-root * {
                animation: none !important;
                transition: none !important;
            }
        }
        """
        )

        return "\n".join(animation_styles)
