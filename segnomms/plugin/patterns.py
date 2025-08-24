"""Pattern-specific processing utilities for the SegnoMMS plugin.

This module handles pattern-specific shape and color mapping, as well as
specialized rendering parameters for different QR code pattern types.
"""

from typing import Tuple

from ..config import RenderingConfig


def _get_pattern_specific_style(
    config: RenderingConfig, module_type: str, default_shape: str, default_color: str
) -> Tuple[str, str]:
    """Get pattern-specific shape and color overrides.

    Args:
        config: Rendering configuration
        module_type: Type of module ('finder', 'timing', 'alignment', etc.)
        default_shape: Default shape to use
        default_color: Default color to use

    Returns:
        Tuple of (shape, color) with pattern-specific overrides applied
    """
    if not config.patterns.enabled:
        return default_shape, default_color

    # Pattern-specific shape mappings
    pattern_shape_map = {
        "finder": config.patterns.finder,
        "finder_inner": config.patterns.finder_inner,
        "timing": config.patterns.timing,
        "alignment": config.patterns.alignment,
        "format": config.patterns.format,
        "version": config.patterns.version,
        "data": config.patterns.data,
    }

    # Pattern-specific color mappings
    pattern_color_map = {
        "finder": config.patterns.finder_color,
        "finder_inner": config.patterns.finder_inner_color,
        "timing": config.patterns.timing_color,
        "alignment": config.patterns.alignment_color,
        "format": config.patterns.format_color,
        "version": config.patterns.version_color,
        "data": config.patterns.data_color,
    }

    # Get pattern-specific overrides
    pattern_shape = pattern_shape_map.get(module_type)
    pattern_color = pattern_color_map.get(module_type)

    # Use pattern-specific values if available, otherwise use defaults
    final_shape = pattern_shape if pattern_shape is not None else default_shape
    final_color = pattern_color if pattern_color is not None else default_color

    return final_shape, final_color


def _get_pattern_specific_render_kwargs(
    config: RenderingConfig, module_type: str, base_kwargs: dict
) -> dict:
    """Get pattern-specific rendering parameters.

    Args:
        config: Rendering configuration
        module_type: Type of module
        base_kwargs: Base rendering kwargs

    Returns:
        Updated kwargs with pattern-specific parameters
    """
    if not config.patterns.enabled:
        return base_kwargs

    kwargs = base_kwargs.copy()

    # Pattern-specific scale factors
    if module_type == "finder" and config.patterns.finder_scale is not None:
        kwargs["size_ratio"] = config.patterns.finder_scale
    elif module_type == "timing" and config.patterns.timing_scale is not None:
        kwargs["size_ratio"] = config.patterns.timing_scale
    elif module_type == "alignment" and config.patterns.alignment_scale is not None:
        kwargs["size_ratio"] = config.patterns.alignment_scale

    # Pattern-specific effects
    if module_type == "finder" and config.patterns.finder_effects:
        kwargs.update(config.patterns.finder_effects)
    elif module_type == "timing" and config.patterns.timing_effects:
        kwargs.update(config.patterns.timing_effects)
    elif module_type == "alignment" and config.patterns.alignment_effects:
        kwargs.update(config.patterns.alignment_effects)

    return kwargs
