"""Intent-based API for SegnoMMS.

This module provides a client-friendly intent-based API that accepts
structured payload and intents objects, processes them with graceful
degradation, and returns comprehensive results with warnings and metrics.

The intent-based API is designed to meet client requirements for:
- Structured payload + intents input model
- Graceful degradation with warnings
- Comprehensive output with SVG + warnings + metrics + used options
- Backward compatibility with existing kwargs API

Key Components:

    :class:`PayloadConfig`: Payload specification and validation
    :class:`IntentsConfig`: Intent specification with graceful degradation
    :class:`RenderingResult`: Comprehensive output model
    :func:`render_with_intents`: Main intent-based rendering function

Example:
    Basic intent-based rendering:

        from segnomms.intents import render_with_intents, PayloadConfig, IntentsConfig

        payload = PayloadConfig(text="https://example.com")
        intents = IntentsConfig(
            style={
                "module_shape": "squircle",
                "merge": "soft"
            },
            accessibility={
                "title": "Example QR Code"
            }
        )

        result = render_with_intents(payload, intents)
        print(f"Generated SVG: {len(result.svg_content)} characters")
        print(f"Warnings: {len(result.warnings)}")

See Also:
    :mod:`segnomms.intents.models`: Intent and payload models
    :mod:`segnomms.intents.processor`: Intent processing logic
    :mod:`segnomms.intents.degradation`: Graceful degradation system
"""

# Import with graceful degradation
try:
    from .models import (
        AccessibilityIntents,
        AdvancedIntents,
        AnimationIntents,
        BrandingIntents,
        CompatibilityInfo,
        DegradationDetail,
        FrameIntents,
        IntentsConfig,
        IntentTranslationReport,
        InteractivityIntents,
        PayloadConfig,
        PerformanceIntents,
        RenderingResult,
        ReserveIntents,
        StyleIntents,
        TransformationStep,
        ValidationIntents,
        WarningInfo,
    )
    from .processor import process_intents, render_with_intents

    __all__ = [
        "PayloadConfig",
        "IntentsConfig",
        "RenderingResult",
        "WarningInfo",
        "TransformationStep",
        "DegradationDetail",
        "CompatibilityInfo",
        "IntentTranslationReport",
        "render_with_intents",
        "process_intents",
        # Intent categories
        "StyleIntents",
        "FrameIntents",
        "ReserveIntents",
        "AccessibilityIntents",
        "ValidationIntents",
        "InteractivityIntents",
        "AnimationIntents",
        "PerformanceIntents",
        "BrandingIntents",
        "AdvancedIntents",
    ]

except ImportError as e:
    # Graceful degradation if intents can't load
    import warnings

    warnings.warn(f"Intent-based API unavailable: {e}", ImportWarning)
    __all__ = []
