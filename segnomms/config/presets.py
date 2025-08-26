"""Pre-defined configuration presets for common use cases.

This module provides ready-to-use configuration presets that can be used
directly or as starting points for custom configurations.

Example:
    Using configuration presets::

        from segnomms.config.presets import ConfigPresets

        # Get a preset
        config = ConfigPresets.artistic()

        # Modify a preset
        config = ConfigPresets.minimal()
        config.scale = 12  # Override default scale

        # List available presets
        presets = ConfigPresets.list_presets()
        for name, description in presets.items():
            print(f"{name}: {description}")
"""

from typing import Any, Dict

from .models import RenderingConfig


class ConfigPresets:
    """Pre-defined configuration presets for common use cases."""

    @staticmethod
    def minimal() -> RenderingConfig:
        """Minimal configuration for simple, fast rendering.

        Features:
        - Square modules
        - No special effects
        - Safe mode enabled
        - Optimized for performance

        Returns:
            RenderingConfig: Minimal configuration

        Example:
            >>> config = ConfigPresets.minimal()
            >>> qr.save("output.svg", kind="interactive_svg", **config.to_kwargs())
        """
        return RenderingConfig.from_kwargs(scale=8, shape="square", safe_mode=True, border=4)

    @staticmethod
    def artistic() -> RenderingConfig:
        """Artistic configuration with smooth, flowing shapes.

        Features:
        - Connected classy modules
        - Soft merging strategy
        - 8-way connectivity
        - Rounded corners

        Returns:
            RenderingConfig: Artistic configuration

        Example:
            >>> config = ConfigPresets.artistic()
            >>> # Optionally customize
            >>> config.dark = '#e74c3c'
        """
        return RenderingConfig.from_kwargs(
            shape="connected-classy",
            corner_radius=0.3,
            connectivity="8-way",
            merge="soft",
            scale=10,
            border=3,
        )

    @staticmethod
    def interactive() -> RenderingConfig:
        """Interactive configuration with hover effects and tooltips.

        Features:
        - Squircle modules for modern look
        - Interactive hover effects
        - Tooltips on modules
        - Medium corner radius

        Returns:
            RenderingConfig: Interactive configuration
        """
        return RenderingConfig.from_kwargs(
            shape="squircle",
            corner_radius=0.4,
            interactive=True,
            tooltips=True,
            scale=12,
            border=3,
        )

    @staticmethod
    def branded() -> RenderingConfig:
        """Configuration optimized for branded QR codes with logos.

        Features:
        - Centerpiece area for logo
        - Rounded modules
        - Professional appearance
        - Frame shape options

        Returns:
            RenderingConfig: Branded configuration

        Example:
            >>> config = ConfigPresets.branded()
            >>> # Customize brand colors
            >>> config.dark = '#1a1a2e'
            >>> config.light = '#ffffff'
        """
        return RenderingConfig.from_kwargs(
            shape="rounded",
            corner_radius=0.2,
            centerpiece_enabled=True,
            centerpiece_shape="circle",
            centerpiece_size=0.2,
            frame_shape="rounded-rect",
            frame_corner_radius=0.15,
            scale=10,
            border=4,
            safe_mode=True,
        )

    @staticmethod
    def modern() -> RenderingConfig:
        """Modern configuration with contemporary design elements.

        Features:
        - Circle frame
        - Gradient quiet zone
        - Connected modules
        - Enhanced visual appeal

        Returns:
            RenderingConfig: Modern configuration
        """
        return RenderingConfig.from_kwargs(
            shape="connected",
            connectivity="8-way",
            merge="soft",
            frame_shape="circle",
            quiet_zone_style="gradient",
            quiet_zone_gradient={
                "type": "radial",
                "colors": ["#ffffff", "#f8f9fa", "#e9ecef"],
            },
            scale=10,
            border=5,
        )

    @staticmethod
    def compact() -> RenderingConfig:
        """Compact configuration for small display sizes.

        Features:
        - Small scale
        - Minimal border
        - Simple shapes
        - High contrast

        Returns:
            RenderingConfig: Compact configuration
        """
        return RenderingConfig.from_kwargs(
            scale=5,
            border=2,
            shape="square",
            safe_mode=True,
            dark="#000000",
            light="#ffffff",
        )

    @staticmethod
    def high_capacity() -> RenderingConfig:
        """Configuration optimized for high-capacity QR codes.

        Features:
        - Small modules
        - Island removal
        - Performance optimized
        - Clear module separation

        Returns:
            RenderingConfig: High capacity configuration
        """
        return RenderingConfig.from_kwargs(
            scale=6,
            border=4,
            shape="dot",
            min_island_modules=2,
            connectivity="4-way",
            safe_mode=True,
        )

    @staticmethod
    def decorative() -> RenderingConfig:
        """Decorative configuration with visual flair.

        Features:
        - Star-shaped modules
        - Circular finder patterns
        - Enhanced visual interest
        - Suitable for artistic uses

        Returns:
            RenderingConfig: Decorative configuration
        """
        return RenderingConfig.from_kwargs(
            shape="star",
            finder_shape="circle",
            finder_inner_scale=0.5,
            scale=15,
            border=4,
            interactive=True,
        )

    @staticmethod
    def professional() -> RenderingConfig:
        """Professional configuration for business use.

        Features:
        - Clean, professional appearance
        - Subtle rounding
        - Reliable scanning
        - Balanced aesthetics

        Returns:
            RenderingConfig: Professional configuration
        """
        return RenderingConfig.from_kwargs(
            shape="rounded",
            corner_radius=0.15,
            finder_shape="rounded",
            finder_inner_scale=0.6,
            scale=10,
            border=4,
            dark="#2c3e50",
            light="#ffffff",
            safe_mode=True,
        )

    @staticmethod
    def social_media() -> RenderingConfig:
        """Configuration optimized for social media sharing.

        Features:
        - Eye-catching design
        - Medium scale for visibility
        - Interactive elements
        - Modern shapes

        Returns:
            RenderingConfig: Social media configuration
        """
        return RenderingConfig.from_kwargs(
            shape="squircle",
            corner_radius=0.35,
            scale=12,
            border=3,
            frame_shape="squircle",
            interactive=True,
            tooltips=True,
            dark="#e74c3c",
            light="#ffffff",
        )

    @staticmethod
    def print_friendly() -> RenderingConfig:
        """Configuration optimized for printing.

        Features:
        - High contrast colors
        - Simple shapes
        - No gradients
        - Clear module boundaries

        Returns:
            RenderingConfig: Print-friendly configuration
        """
        return RenderingConfig.from_kwargs(
            shape="square",
            scale=10,
            border=5,
            dark="#000000",
            light="#ffffff",
            safe_mode=True,
            quiet_zone_style="solid",
            quiet_zone_color="#ffffff",
        )

    @staticmethod
    def custom(base_preset: str = "minimal", **overrides: Any) -> RenderingConfig:
        """Create a custom configuration based on a preset.

        Args:
            base_preset: Name of the base preset to use
            **overrides: Parameters to override from the base preset

        Returns:
            RenderingConfig: Customized configuration

        Raises:
            ValueError: If base_preset is not found

        Example:
            >>> config = ConfigPresets.custom(
            ...     'artistic',
            ...     scale=15,
            ...     dark='#3498db'
            ... )
        """
        preset_map = {
            "minimal": ConfigPresets.minimal,
            "artistic": ConfigPresets.artistic,
            "interactive": ConfigPresets.interactive,
            "branded": ConfigPresets.branded,
            "modern": ConfigPresets.modern,
            "compact": ConfigPresets.compact,
            "high_capacity": ConfigPresets.high_capacity,
            "decorative": ConfigPresets.decorative,
            "professional": ConfigPresets.professional,
            "social_media": ConfigPresets.social_media,
            "print_friendly": ConfigPresets.print_friendly,
        }

        if base_preset not in preset_map:
            raise ValueError(
                f"Unknown preset '{base_preset}'. " f"Available presets: {', '.join(preset_map.keys())}"
            )

        # Get base configuration
        config = preset_map[base_preset]()

        # Apply overrides using to_kwargs and from_kwargs
        config_kwargs = config.to_kwargs()
        config_kwargs.update(overrides)

        return RenderingConfig.from_kwargs(**config_kwargs)

    @staticmethod
    def list_presets() -> Dict[str, str]:
        """List all available presets with descriptions.

        Returns:
            Dict[str, str]: Mapping of preset names to descriptions

        Example:
            >>> presets = ConfigPresets.list_presets()
            >>> for name, desc in presets.items():
            ...     print(f"{name}: {desc}")
        """
        return {
            "minimal": "Simple, fast rendering with square modules",
            "artistic": "Smooth, flowing shapes with soft merging",
            "interactive": "Modern look with hover effects and tooltips",
            "branded": "Optimized for logos with centerpiece area",
            "modern": "Contemporary design with gradients and frames",
            "compact": "Small display sizes with minimal borders",
            "high_capacity": "Optimized for large data QR codes",
            "decorative": "Visual flair with star shapes",
            "professional": "Clean business appearance",
            "social_media": "Eye-catching design for sharing",
            "print_friendly": "High contrast for printing",
        }

    @staticmethod
    def for_qr_version(qr_version: int) -> RenderingConfig:
        """Get recommended configuration for a specific QR version.

        Args:
            qr_version: QR code version (1-40)

        Returns:
            RenderingConfig: Optimized configuration for the version

        Example:
            >>> import segno
            >>> qr = segno.make("Hello World")
            >>> config = ConfigPresets.for_qr_version(qr.version)
        """
        if qr_version <= 3:
            # Small QR codes - keep it simple
            return ConfigPresets.minimal()
        elif qr_version <= 10:
            # Medium QR codes - can use some enhancements
            return RenderingConfig.from_kwargs(
                shape="rounded", corner_radius=0.2, scale=10, border=4, safe_mode=True
            )
        elif qr_version <= 20:
            # Larger QR codes - more features available
            return ConfigPresets.artistic()
        else:
            # Very large QR codes - optimize for capacity
            return ConfigPresets.high_capacity()

    @staticmethod
    def for_use_case(use_case: str) -> RenderingConfig:
        """Get recommended configuration for a specific use case.

        Args:
            use_case: Use case identifier (e.g., 'business-card', 'poster', 'website')

        Returns:
            RenderingConfig: Optimized configuration for the use case

        Raises:
            ValueError: If use_case is not recognized

        Example:
            >>> config = ConfigPresets.for_use_case('business-card')
        """
        use_case_map = {
            "business-card": ConfigPresets.professional,
            "poster": ConfigPresets.modern,
            "website": ConfigPresets.interactive,
            "social-media": ConfigPresets.social_media,
            "print": ConfigPresets.print_friendly,
            "logo": ConfigPresets.branded,
            "art": ConfigPresets.decorative,
            "mobile": ConfigPresets.compact,
            "document": ConfigPresets.minimal,
        }

        if use_case not in use_case_map:
            raise ValueError(
                f"Unknown use case '{use_case}'. " f"Available use cases: {', '.join(use_case_map.keys())}"
            )

        return use_case_map[use_case]()
