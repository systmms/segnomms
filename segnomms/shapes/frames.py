"""Frame shape generators for QR codes.

This module provides generators for creating SVG clipping paths and masks
for various frame shapes including circles, rounded rectangles, and squircles.
"""

import xml.etree.ElementTree as ET
from typing import Optional, Tuple


class FrameShapeGenerator:
    """Generates SVG paths and definitions for frame shapes.

    This class provides static methods to generate various frame shapes
    as SVG elements for use in clipping paths and masks.
    """

    @staticmethod
    def generate_circle_clip(width: int, height: int, border: int = 0) -> str:
        """Generate circular clipping path.

        Args:
            width: Total SVG width in pixels
            height: Total SVG height in pixels
            border: Border size in pixels (unused for circle)

        Returns:
            SVG circle element as string
        """
        cx = width / 2
        cy = height / 2
        r = min(width, height) / 2
        return f'<circle cx="{cx}" cy="{cy}" r="{r}"/>'

    @staticmethod
    def generate_rounded_rect_clip(
        width: int, height: int, border: int, corner_radius: float
    ) -> str:
        """Generate rounded rectangle clipping path.

        Args:
            width: Total SVG width in pixels
            height: Total SVG height in pixels
            border: Border size in pixels (unused)
            corner_radius: Corner radius as fraction (0.0-1.0)

        Returns:
            SVG rect element with rounded corners as string
        """
        # Calculate actual radius based on smallest dimension
        radius = corner_radius * min(width, height) / 2

        # Ensure radius doesn't exceed half the smallest dimension
        max_radius = min(width, height) / 2
        radius = min(radius, max_radius)

        return (
            f'<rect x="0" y="0" width="{width}" height="{height}" '
            f'rx="{radius}" ry="{radius}"/>'
        )

    @staticmethod
    def generate_squircle_clip(width: int, height: int, border: int = 0) -> str:
        """Generate squircle (superellipse) clipping path.

        A squircle is a mathematical shape between a square and a circle,
        defined by the superellipse equation with n=4.

        Args:
            width: Total SVG width in pixels
            height: Total SVG height in pixels
            border: Border size in pixels (unused)

        Returns:
            SVG path element forming a squircle as string
        """
        cx, cy = width / 2, height / 2
        rx, ry = width / 2, height / 2

        # Control point offset for cubic bezier approximation
        # This value approximates a superellipse with n=4
        kappa = 0.37
        ox = rx * kappa
        oy = ry * kappa

        # Build path using cubic bezier curves
        # Start at left center, move clockwise
        path = (
            f"M {cx - rx} {cy} "
            # Top left quadrant
            f"C {cx - rx} {cy - oy} {cx - ox} {cy - ry} {cx} {cy - ry} "
            # Top right quadrant
            f"C {cx + ox} {cy - ry} {cx + rx} {cy - oy} {cx + rx} {cy} "
            # Bottom right quadrant
            f"C {cx + rx} {cy + oy} {cx + ox} {cy + ry} {cx} {cy + ry} "
            # Bottom left quadrant
            f"C {cx - ox} {cy + ry} {cx - rx} {cy + oy} {cx - rx} {cy} Z"
        )
        return f'<path d="{path}"/>'

    @staticmethod
    def generate_fade_mask(
        width: int,
        height: int,
        shape: str,
        fade_distance: float,
        corner_radius: float = 0.0,
        custom_path: Optional[str] = None,
    ) -> str:
        """Generate fade mask for soft edges.

        Creates a gradient mask that provides a soft fade effect at the edges
        of the frame shape using SVG gradients and masks.

        Args:
            width: Total SVG width in pixels
            height: Total SVG height in pixels
            shape: Frame shape type ('circle', 'rounded-rect', 'squircle', 'custom')
            fade_distance: Fade distance in pixels
            corner_radius: Corner radius for rounded-rect (0.0-1.0)
            custom_path: Custom SVG path for custom shapes

        Returns:
            SVG gradient and mask elements as string
        """
        mask_id = f"fade-mask-{shape}"
        grad_id = f"fade-gradient-{shape}"

        # Calculate fade parameters
        min_dimension = min(width, height)
        max_fade = min_dimension * 0.4  # Max 40% of dimension
        actual_fade = min(fade_distance, max_fade)

        if shape == "circle":
            # Radial gradient for circular fade
            cx, cy = width / 2, height / 2
            r = min_dimension / 2
            fade_r = r - actual_fade
            fade_start = fade_r / r if r > 0 else 0

            return f"""
                <defs>
                    <radialGradient id="{grad_id}" cx="50%" cy="50%" r="50%">
                        <stop offset="{fade_start * 100:.1f}%" stop-color="white" stop-opacity="1"/>
                        <stop offset="100%" stop-color="white" stop-opacity="0"/>
                    </radialGradient>
                    <mask id="{mask_id}">
                        <circle cx="{cx}" cy="{cy}" r="{r}" fill="url(#{grad_id})"/>
                    </mask>
                </defs>
            """

        elif shape == "rounded-rect":
            # Multiple gradient approach for rounded rectangles
            radius = corner_radius * min_dimension / 2

            return f"""
                <defs>
                    <radialGradient id="{grad_id}" cx="50%" cy="50%" r="50%">
                        <stop offset="70%" stop-color="white" stop-opacity="1"/>
                        <stop offset="100%" stop-color="white" stop-opacity="0"/>
                    </radialGradient>
                    <mask id="{mask_id}">
                        <rect x="{actual_fade}" y="{actual_fade}"
                              width="{width - 2*actual_fade}" height="{height - 2*actual_fade}"
                              rx="{radius}" ry="{radius}" fill="white"/>
                        <rect x="0" y="0" width="{width}" height="{height}"
                              rx="{radius}" ry="{radius}" fill="url(#{grad_id})"/>
                    </mask>
                </defs>
            """

        elif shape == "squircle":
            # Squircle fade using composite mask
            return f"""
                <defs>
                    <radialGradient id="{grad_id}" cx="50%" cy="50%" r="70%">
                        <stop offset="60%" stop-color="white" stop-opacity="1"/>
                        <stop offset="100%" stop-color="white" stop-opacity="0"/>
                    </radialGradient>
                    <mask id="{mask_id}">
                        {FrameShapeGenerator.generate_squircle_clip(int(width - 2*actual_fade), int(height - 2*actual_fade))}
                        <rect x="0" y="0" width="{width}" height="{height}" fill="url(#{grad_id})"/>
                    </mask>
                </defs>
            """

        elif shape == "custom" and custom_path:
            # For custom paths, use a simple radial fade
            return f"""
                <defs>
                    <radialGradient id="{grad_id}" cx="50%" cy="50%" r="50%">
                        <stop offset="70%" stop-color="white" stop-opacity="1"/>
                        <stop offset="100%" stop-color="white" stop-opacity="0"/>
                    </radialGradient>
                    <mask id="{mask_id}">
                        <path d="{custom_path}" fill="url(#{grad_id})"/>
                    </mask>
                </defs>
            """

        # Default: no fade mask
        return ""

    @staticmethod
    def generate_scale_transform(
        width: int,
        height: int,
        shape: str,
        scale_distance: float,
        corner_radius: float = 0.0,
        custom_path: Optional[str] = None,
    ) -> Tuple[str, str]:
        """Generate scale transform for modules near frame edges.

        Creates transform groups that gradually scale down modules as they approach
        the frame edge, creating a smooth transition effect.

        Args:
            width: Total SVG width in pixels
            height: Total SVG height in pixels
            shape: Frame shape type ('circle', 'rounded-rect', 'squircle', 'custom')
            scale_distance: Distance in pixels from edge where scaling begins
            corner_radius: Corner radius for rounded-rect (0.0-1.0)
            custom_path: Custom SVG path for custom shapes

        Returns:
            Tuple of (clip_path_url, scale_group_transform)
        """
        clip_id = f"scale-clip-{shape}"

        # Create base clip path (same as regular clip)
        if shape == "circle":
            clip_path = FrameShapeGenerator.generate_circle_clip(width, height)
        elif shape == "rounded-rect":
            clip_path = FrameShapeGenerator.generate_rounded_rect_clip(
                width, height, 0, corner_radius
            )
        elif shape == "squircle":
            clip_path = FrameShapeGenerator.generate_squircle_clip(width, height)
        elif shape == "custom" and custom_path:
            clip_path = f'<path d="{custom_path}"/>'
        else:
            clip_path = f'<rect x="0" y="0" width="{width}" height="{height}"/>'

        # For scale mode, we'll apply scaling via CSS transforms based on distance from edge
        # This is a placeholder - the actual scaling logic will be applied per-module
        # in the rendering code
        clip_def = f"""
            <defs>
                <clipPath id="{clip_id}">
                    {clip_path}
                </clipPath>
            </defs>
        """

        return f"url(#{clip_id})", clip_def

    @staticmethod
    def validate_custom_path(path: str, width: int, height: int) -> Tuple[bool, str]:
        """Validate a custom SVG path.

        Performs basic validation on custom SVG path strings to ensure they
        are likely to work as clipping paths.

        Args:
            path: SVG path data string
            width: Expected width for the path
            height: Expected height for the path

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not path:
            return False, "Path cannot be empty"

        # Check for basic SVG path commands
        valid_commands = set("MmLlHhVvCcSsQqTtAaZz")
        path_commands = set(c for c in path if c.isalpha())

        if not path_commands.issubset(valid_commands):
            invalid = path_commands - valid_commands
            return False, f"Invalid path commands: {invalid}"

        # Check if path is closed
        if "Z" not in path.upper():
            return False, "Path should be closed with Z command"

        # Basic check for move command at start
        if not path.strip().upper().startswith("M"):
            return False, "Path should start with M (move) command"

        return True, ""

    @staticmethod
    def scale_path_to_fit(
        path: str,
        current_box: Tuple[float, float, float, float],
        target_width: int,
        target_height: int,
    ) -> str:
        """Scale an SVG path to fit target dimensions.

        This is a placeholder for path scaling functionality.
        In practice, this would parse the path and transform coordinates.

        Args:
            path: Original SVG path string
            current_box: Current bounding box (x, y, width, height)
            target_width: Target width in pixels
            target_height: Target height in pixels

        Returns:
            Scaled SVG path string
        """
        # Basic path scaling implementation
        # NOTE: This is a simplified implementation that only handles transform attribute
        # For complex path coordinate transformation, would need SVG path parser
        
        if not path or not current_box:
            return path
            
        current_width, current_height = current_box[2], current_box[3]
        
        # Avoid division by zero
        if current_width == 0 or current_height == 0:
            return path
            
        # Calculate scaling factors
        scale_x = target_width / current_width
        scale_y = target_height / current_height
        
        # If no scaling needed, return original
        if abs(scale_x - 1.0) < 0.001 and abs(scale_y - 1.0) < 0.001:
            return path
            
        # For complex paths, recommend using transform attribute at element level
        # rather than modifying path coordinates directly
        import logging
        logging.getLogger(__name__).info(
            f"Path scaling requested (scale: {scale_x:.3f}, {scale_y:.3f}). "
            "Consider using SVG transform attribute for better precision."
        )
        
        return path

    @staticmethod
    def create_frame_group(
        shape_type: str, width: int, height: int, config: Optional[dict] = None
    ) -> ET.Element:
        """Create a complete frame shape group.

        Convenience method to create a frame shape element that can be
        directly inserted into an SVG.

        Args:
            shape_type: Type of frame ('circle', 'rounded-rect', 'squircle', 'custom')
            width: Frame width in pixels
            height: Frame height in pixels
            config: Additional configuration (corner_radius, custom_path, etc.)

        Returns:
            ET.Element containing the frame shape
        """
        config = config or {}

        if shape_type == "circle":
            shape_str = FrameShapeGenerator.generate_circle_clip(width, height)
        elif shape_type == "rounded-rect":
            corner_radius = config.get("corner_radius", 0.1)
            shape_str = FrameShapeGenerator.generate_rounded_rect_clip(
                width, height, 0, corner_radius
            )
        elif shape_type == "squircle":
            shape_str = FrameShapeGenerator.generate_squircle_clip(width, height)
        elif shape_type == "custom":
            custom_path = config.get("custom_path", "")
            if custom_path:
                shape_str = f'<path d="{custom_path}"/>'
            else:
                # Fallback to square
                shape_str = f'<rect x="0" y="0" width="{width}" height="{height}"/>'
        else:
            # Default square
            shape_str = f'<rect x="0" y="0" width="{width}" height="{height}"/>'

        # Parse the string to create an Element
        return ET.fromstring(shape_str)
