"""Frame and visual effects builder for SVG documents.

This module handles frame shapes, quiet zones, centerpiece metadata,
and other visual effects for QR codes.
"""

import logging
import xml.etree.ElementTree as ET
from typing import Any, Dict, Optional, Tuple, Union

from ..config import RenderingConfig
from ..config.models.visual import CenterpieceConfig, FrameConfig, QuietZoneConfig
from ..shapes.frames import FrameShapeGenerator

logger = logging.getLogger(__name__)


class FrameVisualBuilder:
    """Builder for frame shapes and visual effects.

    Manages frame definitions, quiet zone styling, centerpiece metadata,
    and other visual enhancements for QR codes.
    """

    def add_frame_definitions(
        self,
        svg: ET.Element,
        frame_config: FrameConfig,
        qr_size: int,
        module_count: int,
    ) -> Optional[str]:
        """Add frame shape definitions to the SVG.

        Args:
            svg: SVG element to add frame definitions to
            frame_config: Frame configuration object
            qr_size: Size of the QR code in pixels
            module_count: Number of modules in the QR code

        Returns:
            ID of the frame clip path if created
        """
        if not frame_config or not getattr(frame_config, "shape", None):
            return None

        # Find or create defs element
        defs = svg.find(".//defs")
        if defs is None:
            defs = ET.SubElement(svg, "defs")

        try:
            # Generate frame shape
            generator = FrameShapeGenerator()

            # Generate appropriate frame shape based on configuration
            if frame_config.shape == "circle":
                frame_element = generator.generate_circle_clip(qr_size, qr_size)
            elif frame_config.shape == "rounded-rect":
                corner_radius = getattr(frame_config, "corner_radius", 0.0)
                frame_element = generator.generate_rounded_rect_clip(qr_size, qr_size, 0, corner_radius)
            elif frame_config.shape == "squircle":
                frame_element = generator.generate_squircle_clip(qr_size, qr_size)
            elif frame_config.shape == "custom":
                custom_path = getattr(frame_config, "custom_path", "")
                if custom_path:
                    frame_element = f'<path d="{custom_path}"/>'
                else:
                    # Fallback to square if no custom path provided
                    frame_element = f'<rect x="0" y="0" width="{qr_size}" height="{qr_size}"/>'
            else:
                frame_element = None

            if frame_element is not None:
                # Create clip path
                # Generate consistent clip ID based on frame shape
                shape_name = getattr(frame_config, "shape", "unknown")
                clip_id = f"frame-clip-{shape_name}-clip"
                clipPath = ET.SubElement(defs, "clipPath", attrib={"id": clip_id})
                # Parse the string into an Element and append
                shape_elem = ET.fromstring(frame_element)
                clipPath.append(shape_elem)

                # Add fade mask if needed and return appropriate URL
                if hasattr(frame_config, "clip_mode") and frame_config.clip_mode == "fade":
                    mask_id = self._add_fade_mask(defs, clip_id, frame_config, qr_size)
                    return f"url(#{mask_id})"
                else:
                    return f"url(#{clip_id})"

        except Exception as e:
            logger.warning(f"Failed to generate frame shape: {e}")

        return None

    def add_quiet_zone_with_style(
        self,
        svg: ET.Element,
        config: QuietZoneConfig,
        qr_bounds: Tuple[int, int, int, int],
    ) -> None:
        """Add styled quiet zone to the SVG.

        Args:
            svg: SVG element to add quiet zone to
            config: Rendering configuration with quiet_zone settings
            qr_bounds: Tuple of (x, y, width, height) for QR code bounds
        """
        # config is the quiet zone config directly
        style = getattr(config, "style", "none")

        if style == "none":
            return

        x, y, width, height = qr_bounds

        # Create quiet zone rectangle
        qz_rect = ET.SubElement(
            svg,
            "rect",
            attrib={
                "x": str(x),
                "y": str(y),
                "width": str(width),
                "height": str(height),
                "class": "segnomms-quiet-zone",
            },
        )

        if style == "solid":
            # Simple solid color
            qz_rect.set("fill", getattr(config, "color", "#ffffff"))

        elif style == "gradient" and hasattr(config, "gradient"):
            # Gradient quiet zone
            gradient = config.gradient
            grad_id = "quiet-zone-gradient"

            # Find or create defs
            defs = svg.find(".//defs")
            if defs is None:
                defs = ET.SubElement(svg, "defs")

            # Add gradient definition
            self._create_quiet_zone_gradient(defs, grad_id, gradient)
            qz_rect.set("fill", f"url(#{grad_id})")

    def add_centerpiece_metadata(
        self,
        svg: ET.Element,
        config: Union[RenderingConfig, CenterpieceConfig],
        qr_bounds: Tuple[int, int, int, int],
        scale: int,
    ) -> None:
        """Add metadata for centerpiece/reserve area.

        Args:
            svg: SVG element to add metadata to
            config: Rendering configuration with centerpiece settings
            qr_bounds: Tuple of (x, y, width, height) for QR code bounds
            scale: Scale factor for module size calculations
        """
        # Handle both full config with centerpiece attribute and direct config
        if hasattr(config, "centerpiece"):
            cp = config.centerpiece
        else:
            # config is the centerpiece config itself
            cp = config

        if not cp.enabled:
            return

        # Register custom namespace for metadata
        ET.register_namespace("qr", "https://segnomms.io/ns/qr")

        # Calculate centerpiece bounds
        x, y, width, height = qr_bounds
        cp_size = cp.size * min(width, height)

        # Calculate position based on placement mode
        if cp.placement == "center":
            cp_x = x + (width - cp_size) / 2
            cp_y = y + (height - cp_size) / 2
        else:  # custom placement
            cp_x = x + (width / 2) + (cp.offset_x * width) - (cp_size / 2)
            cp_y = y + (height / 2) + (cp.offset_y * height) - (cp_size / 2)

        # Find or create metadata container
        metadata_container = svg.find("metadata")
        if metadata_container is None:
            metadata_container = ET.SubElement(svg, "metadata")

        # Add centerpiece metadata element
        centerpiece_metadata = ET.SubElement(
            metadata_container,
            "{https://segnomms.io/ns/qr}centerpiece",
            attrib={
                "shape": cp.shape,
                "margin": str(cp.margin),
                "mode": cp.mode.value if hasattr(cp.mode, "value") else str(cp.mode),
            },
        )

        # Add bounds child element
        bounds_element = ET.SubElement(
            centerpiece_metadata,
            "{https://segnomms.io/ns/qr}bounds",
            attrib={
                "x": str(int(cp_x)),
                "y": str(int(cp_y)),
                "width": str(int(cp_size)),
                "height": str(int(cp_size)),
            },
        )

        # Convert to module coordinates and add as attributes
        bounds_element.set("module-x", str(int(cp_x / scale)))
        bounds_element.set("module-y", str(int(cp_y / scale)))
        bounds_element.set("module-width", str(int(cp_size / scale)))
        bounds_element.set("module-height", str(int(cp_size / scale)))

        # Add configuration details including offset information
        config_element = ET.SubElement(
            centerpiece_metadata,
            "{https://segnomms.io/ns/qr}config",
        )

        # Add offset information if available
        if hasattr(cp, "offset_x") and hasattr(cp, "offset_y"):
            offset_x_element = ET.SubElement(config_element, "{https://segnomms.io/ns/qr}offset-x")
            offset_x_element.text = str(cp.offset_x)

            offset_y_element = ET.SubElement(config_element, "{https://segnomms.io/ns/qr}offset-y")
            offset_y_element.text = str(cp.offset_y)

    def _add_fade_mask(self, defs: ET.Element, clip_id: str, frame_config: FrameConfig, qr_size: int) -> str:
        """Add fade mask for frame clipping.

        Args:
            defs: Defs element to add mask to
            clip_id: ID of the clip path
            frame_config: Frame configuration
            qr_size: Size of the QR code

        Returns:
            The mask ID that was created
        """
        # Use consistent mask ID pattern matching shapes/frames.py
        shape_name = getattr(frame_config, "shape", "unknown")
        mask_id = f"fade-mask-{shape_name}"
        mask = ET.SubElement(defs, "mask", attrib={"id": mask_id})

        # White background (fully visible)
        ET.SubElement(
            mask,
            "rect",
            attrib={"width": str(qr_size), "height": str(qr_size), "fill": "white"},
        )

        # Gradient for fade effect
        fade_distance = getattr(frame_config, "fade_distance", 10)
        grad_id = f"{mask_id}-gradient"

        if frame_config.shape == "circle":
            # Radial gradient for circular fade
            gradient = ET.SubElement(
                defs,
                "radialGradient",
                attrib={"id": grad_id, "cx": "50%", "cy": "50%", "r": "50%"},
            )

            fade_start = (qr_size / 2 - fade_distance) / (qr_size / 2)
            ET.SubElement(
                gradient,
                "stop",
                attrib={"offset": str(max(0, fade_start)), "stop-color": "white"},
            )
            ET.SubElement(gradient, "stop", attrib={"offset": "100%", "stop-color": "black"})

        else:
            # Linear gradient for rectangular fade (simplified to single gradient)
            # For complex multi-edge fades, would need composite mask approach
            gradient = ET.SubElement(
                defs,
                "linearGradient",
                attrib={
                    "id": grad_id,
                    "x1": "0%",
                    "y1": "0%",
                    "x2": "100%",
                    "y2": "100%",
                },
            )

            # Create fade from edges to center
            fade_pct = (fade_distance / (qr_size / 2)) * 100
            ET.SubElement(
                gradient,
                "stop",
                attrib={"offset": "0%", "stop-color": "black"},
            )
            ET.SubElement(
                gradient,
                "stop",
                attrib={"offset": f"{fade_pct}%", "stop-color": "white"},
            )
            ET.SubElement(
                gradient,
                "stop",
                attrib={"offset": f"{100 - fade_pct}%", "stop-color": "white"},
            )
            ET.SubElement(gradient, "stop", attrib={"offset": "100%", "stop-color": "black"})

        # Apply gradient to mask
        ET.SubElement(
            mask,
            "rect",
            attrib={
                "width": str(qr_size),
                "height": str(qr_size),
                "fill": f"url(#{grad_id})",
            },
        )

        return mask_id

    def _create_quiet_zone_gradient(
        self, defs: ET.Element, grad_id: str, gradient_config: Optional[Dict[str, Any]]
    ) -> None:
        """Create gradient definition for quiet zone.

        Args:
            defs: Defs element to add gradient to
            grad_id: ID for the gradient
            gradient_config: Gradient configuration
        """
        if gradient_config is None:
            return

        grad_type = gradient_config.get("type", "linear")

        if grad_type == "linear":
            gradient = ET.SubElement(
                defs,
                "linearGradient",
                attrib={
                    "id": grad_id,
                    "x1": str(gradient_config.get("x1", "0%")),
                    "y1": str(gradient_config.get("y1", "0%")),
                    "x2": str(gradient_config.get("x2", "100%")),
                    "y2": str(gradient_config.get("y2", "100%")),
                },
            )
        else:  # radial
            gradient = ET.SubElement(
                defs,
                "radialGradient",
                attrib={
                    "id": grad_id,
                    "cx": str(gradient_config.get("cx", "50%")),
                    "cy": str(gradient_config.get("cy", "50%")),
                    "r": str(gradient_config.get("r", "50%")),
                },
            )

        # Add gradient stops - handle both 'stops' and 'colors' formats
        if "stops" in gradient_config:
            stops = gradient_config["stops"]
        elif "colors" in gradient_config:
            # Convert colors format to stops format
            colors = gradient_config["colors"]
            stops = []
            for i, color in enumerate(colors):
                offset = f"{int(i * 100 / max(1, len(colors) - 1))}%" if len(colors) > 1 else "0%"
                if isinstance(color, dict):
                    # Color with opacity: {"color": "#ffffff", "opacity": 1.0}
                    stops.append(
                        {
                            "offset": offset,
                            "color": color["color"],
                            "opacity": color.get("opacity", 1),
                        }
                    )
                else:
                    # Simple color string
                    stops.append({"offset": offset, "color": color, "opacity": 1})
        else:
            # Default stops
            stops = [
                {"offset": "0%", "color": "#ffffff", "opacity": 0},
                {"offset": "100%", "color": "#ffffff", "opacity": 1},
            ]

        for stop in stops:
            ET.SubElement(
                gradient,
                "stop",
                attrib={
                    "offset": stop["offset"],
                    "stop-color": stop["color"],
                    "stop-opacity": str(stop.get("opacity", 1)),
                },
            )
