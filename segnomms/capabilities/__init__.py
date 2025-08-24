"""Capability discovery and manifest generation for SegnoMMS.

This module provides runtime capability discovery, feature enumeration,
and manifest generation for the SegnoMMS plugin. It enables clients to
discover available features, supported configurations, and implementation
bounds at runtime.

Key Components:

    :class:`CapabilityManifest`: Complete capability information model
    :func:`get_capability_manifest`: Generate runtime capability manifest
    :func:`get_supported_features`: List specific feature categories

The capability system leverages existing Pydantic models and factory patterns
to provide accurate, up-to-date feature information without duplication.

Example:
    Basic capability discovery:

        from segnomms.capabilities import get_capability_manifest

        manifest = get_capability_manifest()
        print(f"Available shapes: {manifest.features.module_shapes}")
        print(f"Max reserve area: {manifest.features.reserve.max_area_pct}")

    Feature checking:

        from segnomms.capabilities import get_supported_features

        shapes = get_supported_features("shapes")
        if "squircle" in shapes:
            print("Squircle shape is supported")

See Also:
    :mod:`segnomms.capabilities.manifest`: Capability manifest implementation
    :mod:`segnomms.config.schema`: Configuration models used for discovery
"""

# Import with graceful degradation
try:
    from .manifest import (
        CapabilityManifest,
        get_capability_manifest,
        get_supported_features,
    )

    __all__ = [
        "CapabilityManifest",
        "get_capability_manifest",
        "get_supported_features",
    ]

except ImportError as e:
    # Graceful degradation if capabilities can't load
    import warnings

    warnings.warn(f"Capability discovery unavailable: {e}", ImportWarning)
    __all__ = []
