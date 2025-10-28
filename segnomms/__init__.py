"""SegnoMMS - Advanced QR Code Generation with Intent-Based API.

A modular plugin for generating interactive SVG QR codes with custom shapes,
advanced clustering, and dynamic styling capabilities.

This plugin provides two APIs:

**Intent-Based API (Recommended)**: High-level declarative QR generation with
structured configuration, comprehensive error handling, and graceful degradation.

**Legacy Write API**: Direct function-based generation for simple use cases and
backward compatibility.

Features:

* **Intent-Based Configuration**: Structured, type-safe configuration with
  automatic validation
* **Multiple Shape Renderers**: 14+ shapes including squares, circles, stars,
  and connected shapes
* **Context-Aware Shapes**: Adaptive shapes based on neighboring modules
* **Safe Mode**: Preserves QR code scannability using simple shapes for
  critical patterns
* **CSS Classes & Interactivity**: Full styling and animation support
* **Graceful Degradation**: Automatic fallbacks with detailed warning system
* **Performance Optimization**: Multi-phase processing pipeline with
  clustering algorithms
* **Phase 4 Features**: Custom frames, centerpiece areas, and gradient
  backgrounds
* **Comprehensive Error Handling**: Structured exceptions with suggestions
  and alternatives

Example:
    Modern Intent-Based API (Recommended)::

        from segnomms.intents import render_with_intents, PayloadConfig, IntentsConfig
        from segnomms.intents.models import StyleIntents

        # Define payload and styling intentions
        payload = PayloadConfig(text="Hello, World!")
        intents = IntentsConfig(
            style=StyleIntents(
                module_shape="squircle",
                palette={"fg": "#1a1a2e", "bg": "#ffffff"}
            )
        )

        # Generate with comprehensive error handling
        result = render_with_intents(payload, intents)

        # Check for warnings and degradations
        if result.has_warnings:
            for warning in result.warnings:
                print(f"Notice: {warning.detail}")

        with open('modern-qr.svg', 'w') as f:
            f.write(result.svg_content)

    Legacy Write API (Simple Cases)::

        import segno
        from segnomms import write

        qr = segno.make("Hello, World!")
        with open('basic.svg', 'w') as f:
            write(qr, f, shape='connected', scale=10)

    Configuration Presets::

        from segnomms.config import ConfigPresets

        qr = segno.make("Hello, World!")
        config = ConfigPresets.artistic()
        with open('preset.svg', 'w') as f:
            write(qr, f, **config.to_kwargs())

Note:
    This plugin requires Segno 1.5.0 or higher and Pydantic 2.0 or higher.
    The Intent-Based API provides superior error handling and is recommended
    for production applications.

"""

# Import constants module for convenient access (but don't pollute main namespace)
from . import constants
from .algorithms.clustering import ConnectedComponentAnalyzer
from .config import (
    AdvancedQRConfig,
    Phase1Config,
    Phase2Config,
    Phase3Config,
    RenderingConfig,
)
from .config.presets import ConfigPresets
from .core.detector import ModuleDetector
from .core.interfaces import AlgorithmProcessor, RendererFactory, ShapeRenderer

# Import exceptions
from .exceptions import (
    CapabilityError,
    CapabilityManifestError,
    ColorError,
    ConfigurationError,
    ContrastRatioError,
    DependencyError,
    FeatureNotSupportedError,
    IncompatibleConfigError,
    IntentDegradationError,
    IntentProcessingError,
    IntentTransformationError,
    IntentValidationError,
    InvalidColorFormatError,
    MatrixBoundsError,
    MatrixError,
    MatrixSizeError,
    MissingDependencyError,
    OptionalFeatureUnavailableError,
    PaletteValidationError,
    PerformanceError,
    PresetNotFoundError,
    RenderingError,
    SegnoMMSError,
    ShapeRenderingError,
    SVGGenerationError,
    UnsupportedIntentError,
    ValidationError,
)

# Import the main write functions
from .plugin import generate_interactive_svg, write, write_advanced
from .shapes.factory import (
    create_shape_renderer,
    get_shape_factory,
    register_custom_renderer,
)
from .svg import InteractiveSVGBuilder

# Import capability discovery (with graceful degradation)
try:
    from .capabilities import (  # noqa: F401
        CapabilityManifest,
        get_capability_manifest,
        get_supported_features,
    )

    _capabilities_available = True
except ImportError:
    _capabilities_available = False

# Import intent-based API (with graceful degradation)
try:
    from .intents import (  # noqa: F401
        IntentsConfig,
        PayloadConfig,
        RenderingResult,
        process_intents,
        render_with_intents,
    )

    _intents_available = True
except ImportError:
    _intents_available = False

# Version information
__version__ = "0.1.0b4"
__author__ = "QRCodeMMS"

# Export main functionality
__all__ = [
    # Main functions
    "write",
    "write_advanced",
    "generate_interactive_svg",
    # Constants module
    "constants",
    # Core classes
    "ModuleDetector",
    "RenderingConfig",
    "InteractiveSVGBuilder",
    # Configuration classes
    "Phase1Config",
    "Phase2Config",
    "Phase3Config",
    "AdvancedQRConfig",
    "ConfigPresets",
    # Factory functions
    "get_shape_factory",
    "create_shape_renderer",
    "register_custom_renderer",
    # Algorithm classes
    "ConnectedComponentAnalyzer",
    # Interfaces for extension
    "ShapeRenderer",
    "AlgorithmProcessor",
    "RendererFactory",
    # Exceptions
    "SegnoMMSError",
    "ConfigurationError",
    "ValidationError",
    "IntentValidationError",
    "PresetNotFoundError",
    "IncompatibleConfigError",
    "RenderingError",
    "MatrixError",
    "MatrixSizeError",
    "MatrixBoundsError",
    "ShapeRenderingError",
    "SVGGenerationError",
    "PerformanceError",
    "IntentProcessingError",
    "UnsupportedIntentError",
    "IntentDegradationError",
    "IntentTransformationError",
    "ColorError",
    "InvalidColorFormatError",
    "ContrastRatioError",
    "PaletteValidationError",
    "CapabilityError",
    "FeatureNotSupportedError",
    "CapabilityManifestError",
    "DependencyError",
    "MissingDependencyError",
    "OptionalFeatureUnavailableError",
]

# Add capability discovery exports if available
if _capabilities_available:
    __all__.extend(
        [
            "CapabilityManifest",
            "get_capability_manifest",
            "get_supported_features",
        ]
    )

# Add intent-based API exports if available
if _intents_available:
    __all__.extend(
        [
            "PayloadConfig",
            "IntentsConfig",
            "RenderingResult",
            "render_with_intents",
            "process_intents",
        ]
    )

# Plugin metadata for segno registration
PLUGIN_NAME = "interactive_svg"
PLUGIN_VERSION = __version__
