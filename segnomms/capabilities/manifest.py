"""Capability manifest generation and models.

This module implements the core capability discovery system, providing
runtime manifest generation that reflects the actual features and bounds
of the SegnoMMS plugin.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

# Import existing models to discover capabilities
from ..config import (
    ConnectivityMode,
    MergeStrategy,
    ModuleShape,
)


class FeatureSupport(BaseModel):
    """Support level for a feature category."""

    supported: bool = Field(description="Whether feature category is supported")
    version_added: Optional[str] = Field(default=None, description="Version when feature was added")
    experimental: bool = Field(default=False, description="Whether feature is experimental")


class ShapeCapabilities(BaseModel):
    """Capabilities related to module shapes."""

    module_shapes: List[str] = Field(description="Available module shape types")
    connected_shapes: List[str] = Field(description="Advanced connected shape variants")
    merge_strategies: List[str] = Field(description="Module merging strategies")
    connectivity_modes: List[str] = Field(description="Neighbor connectivity modes")
    custom_shapes: FeatureSupport = Field(description="Custom shape registration support")


class FrameCapabilities(BaseModel):
    """Capabilities related to frame shapes and clipping."""

    frame_shapes: List[str] = Field(description="Available frame shape types")
    clip_modes: List[str] = Field(description="Frame clipping modes")
    custom_paths: FeatureSupport = Field(description="Custom SVG path support")
    corner_radius_range: tuple[float, float] = Field(description="Corner radius min/max values")


class ReserveCapabilities(BaseModel):
    """Capabilities related to reserve areas."""

    supported: bool = Field(description="Whether reserve areas are supported")
    max_area_pct: float = Field(description="Maximum safe reserve area percentage")
    shapes: List[str] = Field(description="Available reserve area shapes")
    placement_modes: List[str] = Field(description="Reserve placement modes")
    arbitrary_placement: FeatureSupport = Field(description="Arbitrary placement support")


class ValidationCapabilities(BaseModel):
    """Capabilities related to validation and safety."""

    scanability_validation: FeatureSupport = Field(description="QR scanability validation")
    contrast_validation: FeatureSupport = Field(description="Color contrast validation")
    frame_safety: FeatureSupport = Field(description="Frame safety validation")
    centerpiece_safety: FeatureSupport = Field(description="Centerpiece safety validation")
    performance_warnings: FeatureSupport = Field(description="Performance warning system")


class AccessibilityCapabilities(BaseModel):
    """Capabilities related to accessibility features."""

    css_classes: FeatureSupport = Field(description="CSS class generation")
    stable_ids: FeatureSupport = Field(description="Stable ID generation")
    title_description: FeatureSupport = Field(description="SVG title/description support")
    aria_attributes: FeatureSupport = Field(description="ARIA attribute support")
    interactive_features: FeatureSupport = Field(description="Interactive hover/click support")


class APICapabilities(BaseModel):
    """Capabilities related to API features."""

    pydantic_validation: FeatureSupport = Field(description="Pydantic-based validation")
    json_schema: FeatureSupport = Field(description="JSON Schema generation")
    configuration_presets: FeatureSupport = Field(description="Built-in configuration presets")
    serialization: FeatureSupport = Field(description="JSON serialization/deserialization")
    kwargs_compatibility: FeatureSupport = Field(description="Backward compatible kwargs API")


class AdvancedFeatures(BaseModel):
    """Advanced and experimental features."""

    multi_phase_pipeline: FeatureSupport = Field(description="Multi-phase processing pipeline")
    clustering: FeatureSupport = Field(description="Connected component clustering")
    neighbor_analysis: FeatureSupport = Field(description="8-connected neighbor analysis")
    performance_monitoring: FeatureSupport = Field(description="Performance timing and metrics")
    intent_based_api: FeatureSupport = Field(description="Intent-based configuration API")


class CapabilityFeatures(BaseModel):
    """Complete feature capability information."""

    shapes: ShapeCapabilities = Field(description="Shape rendering capabilities")
    frames: FrameCapabilities = Field(description="Frame and clipping capabilities")
    reserve: ReserveCapabilities = Field(description="Reserve area capabilities")
    validation: ValidationCapabilities = Field(description="Validation and safety capabilities")
    accessibility: AccessibilityCapabilities = Field(description="Accessibility capabilities")
    api: APICapabilities = Field(description="API and configuration capabilities")
    advanced: AdvancedFeatures = Field(description="Advanced and experimental features")


class CapabilityManifest(BaseModel):
    """Complete capability manifest for SegnoMMS plugin.

    Provides comprehensive information about supported features, bounds,
    and capabilities for runtime discovery and client integration.
    """

    name: str = Field(description="Plugin name")
    version: str = Field(description="Plugin version")
    segno_compatibility: List[str] = Field(description="Compatible Segno versions")
    python_compatibility: List[str] = Field(description="Compatible Python versions")

    features: CapabilityFeatures = Field(description="Feature capabilities")

    bounds: Dict[str, Any] = Field(description="Feature bounds and limits")
    examples: Dict[str, Any] = Field(description="Example configurations")

    model_config = {"extra": "forbid", "frozen": True}


def _get_shape_capabilities() -> ShapeCapabilities:
    """Discover shape capabilities from existing implementation."""

    # Get available shapes from enum and factory
    module_shapes = [shape.value for shape in ModuleShape]

    # Identify connected shapes (those with "connected" in name)
    connected_shapes = [shape for shape in module_shapes if "connected" in shape.lower()]

    # Get merge strategies and connectivity modes
    merge_strategies = [strategy.value for strategy in MergeStrategy]
    connectivity_modes = [mode.value for mode in ConnectivityMode]

    return ShapeCapabilities(
        module_shapes=module_shapes,
        connected_shapes=connected_shapes,
        merge_strategies=merge_strategies,
        connectivity_modes=connectivity_modes,
        custom_shapes=FeatureSupport(supported=True, version_added="0.0.0b3", experimental=False),
    )


def _get_frame_capabilities() -> FrameCapabilities:
    """Discover frame capabilities from existing configuration."""

    # Get frame shapes from FrameConfig literal type
    frame_shapes = ["square", "circle", "rounded-rect", "squircle", "custom"]
    clip_modes = ["clip", "fade"]  # From FrameConfig

    return FrameCapabilities(
        frame_shapes=frame_shapes,
        clip_modes=clip_modes,
        custom_paths=FeatureSupport(supported=True, experimental=False),
        corner_radius_range=(0.0, 1.0),
    )


def _get_reserve_capabilities() -> ReserveCapabilities:
    """Discover reserve area capabilities from existing configuration."""

    # Get shapes from CenterpieceConfig
    reserve_shapes = ["rect", "circle", "squircle"]
    placement_modes = ["center", "offset"]  # Current implementation

    return ReserveCapabilities(
        supported=True,
        max_area_pct=25.0,  # Conservative safe limit
        shapes=reserve_shapes,
        placement_modes=placement_modes,
        arbitrary_placement=FeatureSupport(
            supported=False, experimental=True  # Partial - only offset support
        ),
    )


def _get_validation_capabilities() -> ValidationCapabilities:
    """Discover validation capabilities from existing implementation."""

    return ValidationCapabilities(
        scanability_validation=FeatureSupport(supported=True, version_added="0.0.0b3"),
        contrast_validation=FeatureSupport(supported=False),
        frame_safety=FeatureSupport(supported=True),
        centerpiece_safety=FeatureSupport(supported=True),
        performance_warnings=FeatureSupport(supported=False),
    )


def _get_accessibility_capabilities() -> AccessibilityCapabilities:
    """Discover accessibility capabilities from existing implementation."""

    return AccessibilityCapabilities(
        css_classes=FeatureSupport(supported=True),
        stable_ids=FeatureSupport(supported=False),
        title_description=FeatureSupport(supported=True),
        aria_attributes=FeatureSupport(supported=False),
        interactive_features=FeatureSupport(supported=True),
    )


def _get_api_capabilities() -> APICapabilities:
    """Discover API capabilities from existing implementation."""

    return APICapabilities(
        pydantic_validation=FeatureSupport(supported=True, version_added="0.0.0b3"),
        json_schema=FeatureSupport(supported=True),
        configuration_presets=FeatureSupport(supported=True),
        serialization=FeatureSupport(supported=True),
        kwargs_compatibility=FeatureSupport(supported=True),
    )


def _get_advanced_features() -> AdvancedFeatures:
    """Discover advanced features from existing implementation."""

    return AdvancedFeatures(
        multi_phase_pipeline=FeatureSupport(supported=True),
        clustering=FeatureSupport(supported=True, experimental=True),
        neighbor_analysis=FeatureSupport(supported=True),
        performance_monitoring=FeatureSupport(supported=False),
        intent_based_api=FeatureSupport(supported=True, version_added="0.1.0", experimental=False),
    )


def _get_feature_bounds() -> Dict[str, Any]:
    """Get feature bounds and limits."""

    return {
        "scale": {"min": 1, "max": 100, "default": 8},
        "border": {"min": 0, "max": 20, "default": 2},
        "corner_radius": {"min": 0.0, "max": 1.0, "default": 0.0},
        "centerpiece_size": {"min": 0.0, "max": 0.5, "default": 0.0},
        "centerpiece_offset": {"min": -0.5, "max": 0.5, "default": 0.0},
        "max_qr_version": 40,
        "min_qr_version": 1,
        "supported_error_levels": ["L", "M", "Q", "H"],
    }


def _get_example_configurations() -> Dict[str, Any]:
    """Get example configurations demonstrating capabilities."""

    return {
        "minimal": {"shape": "square", "scale": 8, "border": 2},
        "modern": {
            "shape": "squircle",
            "corner_radius": 0.3,
            "merge": "soft",
            "connectivity": "8-way",
        },
        "interactive": {
            "shape": "rounded",
            "interactive": True,
            "tooltips": True,
            "css_classes": {"data": "qr-data-module", "finder": "qr-finder-pattern"},
        },
        "branded": {
            "shape": "connected-classy-rounded",
            "centerpiece": {"enabled": True, "size": 0.15, "shape": "circle"},
            "frame": {"shape": "rounded-rect", "corner_radius": 0.2},
        },
    }


def get_capability_manifest() -> CapabilityManifest:
    """Generate complete capability manifest for SegnoMMS plugin.

    This function discovers capabilities from the actual implementation,
    ensuring the manifest accurately reflects current functionality.

    Returns:
        CapabilityManifest: Complete capability information

    Example:
        >>> manifest = get_capability_manifest()
        >>> print(f"Plugin: {manifest.name} v{manifest.version}")
        >>> print(f"Shapes: {len(manifest.features.shapes.module_shapes)}")
    """

    # Import version here to avoid circular imports
    try:
        from .. import __version__
    except ImportError:
        __version__ = "unknown"

    features = CapabilityFeatures(
        shapes=_get_shape_capabilities(),
        frames=_get_frame_capabilities(),
        reserve=_get_reserve_capabilities(),
        validation=_get_validation_capabilities(),
        accessibility=_get_accessibility_capabilities(),
        api=_get_api_capabilities(),
        advanced=_get_advanced_features(),
    )

    return CapabilityManifest(
        name="SegnoMMS",
        version=__version__,
        segno_compatibility=[">=1.5.2"],
        python_compatibility=[">=3.8"],
        features=features,
        bounds=_get_feature_bounds(),
        examples=_get_example_configurations(),
    )


def get_supported_features(category: str) -> List[str]:
    """Get list of supported features for a specific category.

    Args:
        category: Feature category ('shapes', 'frames', 'merge_strategies', etc.)

    Returns:
        List of supported feature names in that category

    Example:
        >>> shapes = get_supported_features('shapes')
        >>> print(f"Available shapes: {shapes}")
    """

    manifest = get_capability_manifest()

    category_map = {
        "shapes": manifest.features.shapes.module_shapes,
        "connected_shapes": manifest.features.shapes.connected_shapes,
        "merge_strategies": manifest.features.shapes.merge_strategies,
        "connectivity_modes": manifest.features.shapes.connectivity_modes,
        "frame_shapes": manifest.features.frames.frame_shapes,
        "clip_modes": manifest.features.frames.clip_modes,
        "reserve_shapes": manifest.features.reserve.shapes,
        "placement_modes": manifest.features.reserve.placement_modes,
    }

    return category_map.get(category, [])
