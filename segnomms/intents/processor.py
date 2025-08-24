"""Intent processing system for SegnoMMS.

This module provides the main intent processing logic, converting client
intents into SegnoMMS configuration with graceful degradation and
comprehensive result tracking.
"""

import time
from typing import Any, Dict, List, Literal, Optional, Tuple

import segno

from ..capabilities import get_capability_manifest
from ..color.color_analysis import validate_qr_contrast
from ..config import RenderingConfig, AdvancedQRConfig
from ..core.advanced_qr import AdvancedQRGenerator
from ..exceptions import (
    ConfigurationError,
    IntentDegradationError,
    IntentTransformationError,
    IntentValidationError,
    SegnoMMSError,
    UnsupportedIntentError,
)
from ..plugin import generate_interactive_svg
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
    PerformanceMetrics,
    RenderingResult,
    ReserveIntents,
    StyleIntents,
    TransformationStep,
    ValidationIntents,
    WarningInfo,
)


class IntentProcessor:
    """Main intent processing system with integrated degradation handling."""

    def __init__(self) -> None:
        """Initialize the intent processor."""
        self.manifest = get_capability_manifest()
        self.warnings: List[WarningInfo] = []
        self.transformation_steps: List[TransformationStep] = []
        self.degradation_details: List[DegradationDetail] = []
        self.compatibility_info: List[CompatibilityInfo] = []
        self.original_intents: Optional[Dict[str, Any]] = None

    def process_intents(
        self, payload: PayloadConfig, intents: Optional[IntentsConfig] = None
    ) -> RenderingResult:
        """Process payload and intents into rendering result.

        Args:
            payload: Payload configuration with content to encode
            intents: Optional intent configuration

        Returns:
            RenderingResult with SVG, warnings, metrics, and used options
        """
        start_time = time.time()

        # Clear any previous state
        self.clear_state()

        # Track original intents for comparison
        if intents:
            self.original_intents = intents.model_dump(exclude_none=True)

        # Step 1: Process intents with degradation
        config_kwargs = {}
        unsupported_intents = []

        if intents:
            processed_config, unsupported = self._process_all_intents(intents)
            config_kwargs.update(processed_config)
            unsupported_intents.extend(unsupported)
            
            # Apply performance optimizations if any were requested
            self._apply_performance_suggestions(config_kwargs)

        # Step 2: Check if advanced features are needed
        needs_advanced = self._needs_advanced_features(config_kwargs, payload)
        
        # Step 3: Create QR code(s) based on requirements
        if needs_advanced:
            qr_codes, generation_metadata = self._create_advanced_qr(payload, config_kwargs)
            # For now, use the first QR code for rendering
            # TODO: Handle multiple QR codes for structured append
            qr_code = qr_codes[0] if qr_codes else self._create_qr_code(payload)
        else:
            qr_code = self._create_qr_code(payload)

        # Step 4: Build RenderingConfig
        validation_start = time.time()
        try:
            # Extract min contrast ratio if specified
            min_contrast_ratio = config_kwargs.pop("_min_contrast_ratio", None)
            
            config = RenderingConfig.from_kwargs(**config_kwargs)
            validation_time = (time.time() - validation_start) * 1000
            
            # Step 4a: Validate contrast if requested
            if min_contrast_ratio is not None:
                self._validate_contrast(config, min_contrast_ratio)
                
        except ConfigurationError as e:
            # Add configuration error as warning and use defaults
            self._add_warning(
                e.code,
                "config",
                e.message,
                e.suggestion or "Using default configuration",
            )
            config = RenderingConfig()
            validation_time = (time.time() - validation_start) * 1000
        except Exception as e:
            # Handle unexpected errors
            self._add_warning(
                "CONFIGURATION_ERROR",
                "config",
                f"Configuration validation failed: {str(e)}",
                "Using default configuration",
            )
            config = RenderingConfig()
            validation_time = (time.time() - validation_start) * 1000

        # Step 4a: Apply degradation and capture warnings
        from ..degradation import DegradationManager
        degradation_manager = DegradationManager()
        config, degradation_result = degradation_manager.apply_degradation(config)
        
        # Convert degradation warnings to intent processor warnings
        for warning in degradation_result.warnings:
            self._add_warning(
                "DEGRADATION_APPLIED",
                warning.feature,
                warning.message,
                warning.suggestion or "Configuration adjusted for optimal rendering"
            )
        
        # Step 4b: Generate SVG
        svg_start = time.time()
        svg_content = generate_interactive_svg(qr_code, config)
        svg_time = (time.time() - svg_start) * 1000

        # Step 5: Calculate metrics
        total_time = (time.time() - start_time) * 1000
        metrics = self._calculate_metrics(config, total_time, validation_time, svg_time)

        # Step 6: Build translation report
        translation_report = self._build_translation_report()

        # Step 7: Calculate feature impact
        feature_impact = self._calculate_feature_impact(config)

        # Step 8: Predict scanability
        scanability_prediction = self._predict_scanability(config)

        # Step 9: Build result
        result = RenderingResult(
            svg_content=svg_content,
            warnings=self.get_warnings(),
            metrics=metrics,
            used_options=config.to_kwargs(),
            degradation_applied=len(unsupported_intents) > 0 or degradation_result.warning_count > 0,
            unsupported_intents=unsupported_intents,
            translation_report=translation_report,
            requested_options=self.original_intents,
            feature_impact=feature_impact,
            scanability_prediction=scanability_prediction,
        )

        return result

    def _process_all_intents(
        self, intents: IntentsConfig
    ) -> tuple[Dict[str, Any], list[str]]:
        """Process all intent categories."""
        config_kwargs = {}
        all_unsupported = []

        # Process style intents
        if intents.style:
            style_config, style_unsupported = self.process_style_intents(intents.style)
            config_kwargs.update(style_config)
            all_unsupported.extend(style_unsupported)

        # Process frame intents
        if intents.frame:
            frame_config, frame_unsupported = self.process_frame_intents(intents.frame)
            # Map frame config to nested structure
            if frame_config:
                frame_dict = {}
                for key, value in frame_config.items():
                    if key.startswith("frame_"):
                        frame_key = key.replace("frame_", "")
                        frame_dict[frame_key] = value
                    else:
                        frame_dict[key] = value
                config_kwargs["frame"] = frame_dict
            all_unsupported.extend(frame_unsupported)

        # Process reserve intents
        if intents.reserve:
            reserve_config, reserve_unsupported = self.process_reserve_intents(
                intents.reserve
            )
            # Map reserve config to nested structure
            if reserve_config:
                centerpiece_dict = {}
                for key, value in reserve_config.items():
                    if key.startswith("centerpiece_"):
                        centerpiece_key = key.replace("centerpiece_", "")
                        centerpiece_dict[centerpiece_key] = value
                    else:
                        centerpiece_dict[key] = value
                config_kwargs["centerpiece"] = centerpiece_dict
            all_unsupported.extend(reserve_unsupported)

        # Process accessibility intents
        if intents.accessibility:
            accessibility_config = self._process_accessibility_intents(
                intents.accessibility
            )
            config_kwargs.update(accessibility_config)

        # Process validation intents
        if intents.validation:
            validation_config = self._process_validation_intents(intents.validation)
            config_kwargs.update(validation_config)

        # Process interactivity intents
        if intents.interactivity:
            interactivity_config, interactivity_unsupported = (
                self._process_interactivity_intents(intents.interactivity)
            )
            config_kwargs.update(interactivity_config)
            all_unsupported.extend(interactivity_unsupported)

        # Process animation intents
        if intents.animation:
            animation_config, animation_unsupported = self._process_animation_intents(
                intents.animation
            )
            config_kwargs.update(animation_config)
            all_unsupported.extend(animation_unsupported)

        # Process performance intents
        if intents.performance:
            performance_config, performance_unsupported = (
                self._process_performance_intents(intents.performance)
            )
            config_kwargs.update(performance_config)
            all_unsupported.extend(performance_unsupported)

        # Process branding intents
        if intents.branding:
            branding_config, branding_unsupported = self._process_branding_intents(
                intents.branding
            )
            config_kwargs.update(branding_config)
            all_unsupported.extend(branding_unsupported)

        # Process advanced intents (mostly unsupported for now)
        if intents.advanced:
            advanced_config, advanced_unsupported = self._process_advanced_intents(
                intents.advanced
            )
            config_kwargs.update(advanced_config)
            all_unsupported.extend(advanced_unsupported)

        return config_kwargs, all_unsupported

    def _process_accessibility_intents(self, accessibility: Optional[AccessibilityIntents]) -> Dict[str, Any]:
        """Process accessibility intents."""
        config: Dict[str, Any] = {}

        if accessibility is None:
            return config

        # Enable accessibility with ID generation
        if accessibility.ids is not None:
            config["enable_accessibility"] = accessibility.ids
            self._track_transformation(
                "accessibility.ids",
                accessibility.ids,
                accessibility.ids,
                "accepted",
                reason="Stable ID generation available",
                confidence=1.0,
            )

        # ID prefix configuration
        if accessibility.id_prefix:
            config["accessibility_id_prefix"] = accessibility.id_prefix
            self._track_transformation(
                "accessibility.id_prefix",
                accessibility.id_prefix,
                accessibility.id_prefix,
                "accepted",
                confidence=1.0,
            )

        # Title and description
        if accessibility.title:
            config["svg_title"] = accessibility.title
            self._track_transformation(
                "accessibility.title",
                accessibility.title,
                accessibility.title,
                "accepted",
                confidence=1.0,
            )

        if accessibility.desc:
            config["svg_description"] = accessibility.desc
            self._track_transformation(
                "accessibility.desc",
                accessibility.desc,
                accessibility.desc,
                "accepted",
                confidence=1.0,
            )

        # ARIA support
        if accessibility.aria is not None:
            config["enable_aria"] = accessibility.aria
            self._track_transformation(
                "accessibility.aria",
                accessibility.aria,
                accessibility.aria,
                "accepted",
                reason="ARIA attributes supported via accessibility system",
                confidence=1.0,
            )

            # Add compatibility info
            self._add_compatibility_info(
                "accessibility.aria",
                "full",
                available_since="0.1.0",
                workarounds=[],
            )

        return config

    def _process_validation_intents(self, validation: Optional[ValidationIntents]) -> Dict[str, Any]:
        """Process validation intents."""
        config: Dict[str, Any] = {}

        if validation is None:
            return config

        if validation.enforce_scanability is not None:
            # Scanability validation is always on in SegnoMMS
            config["safe_mode"] = validation.enforce_scanability

        if validation.min_contrast is not None:
            # Store minimum contrast requirement for later validation
            config["_min_contrast_ratio"] = validation.min_contrast
            self._track_transformation(
                "validation.min_contrast",
                validation.min_contrast,
                validation.min_contrast,
                "accepted",
                reason="Contrast validation will be performed",
                confidence=1.0,
            )
            self._add_compatibility_info(
                "validation.min_contrast",
                "full",
                available_since="0.1.0",
                workarounds=[],
            )

        if validation.quiet_zone is not None:
            config["border"] = validation.quiet_zone

        return config

    def _process_advanced_intents(self, advanced: Optional[AdvancedIntents]) -> tuple[Dict[str, Any], list[str]]:
        """Process advanced intents."""
        config: Dict[str, Any] = {}
        unsupported: list[str] = []

        if advanced is None:
            return config, unsupported

        # Support mask pattern selection
        if advanced.mask_pattern is not None:
            # Validate mask pattern is in valid range (0-7)
            if 0 <= advanced.mask_pattern <= 7:
                config["mask"] = advanced.mask_pattern
                self._track_transformation(
                    "advanced.mask_pattern",
                    advanced.mask_pattern,
                    advanced.mask_pattern,
                    "accepted",
                    reason="Manual mask pattern selection supported",
                    confidence=1.0,
                )
                self._add_compatibility_info(
                    "advanced.mask_pattern",
                    "full",
                    available_since="0.1.0",
                    workarounds=[],
                )
            else:
                self._add_warning(
                    "INTENT_OUT_OF_RANGE",
                    "advanced.mask_pattern",
                    f"Mask pattern {advanced.mask_pattern} out of valid range (0-7)",
                    "Using automatic mask selection",
                )
                self._track_transformation(
                    "advanced.mask_pattern",
                    advanced.mask_pattern,
                    None,
                    "rejected",
                    reason="Invalid mask pattern value",
                    confidence=1.0,
                )
                unsupported.append("advanced.mask_pattern")

        # Support structured append
        if advanced.structured_append:
            # Process structured append configuration
            if isinstance(advanced.structured_append, dict):
                if advanced.structured_append.get("enabled", False):
                    config["structured_append"] = True
                    sa_config = {"enabled": True}
                    
                    # Symbol count configuration
                    symbol_count = advanced.structured_append.get("symbol_count")
                    if symbol_count is not None:
                        if 2 <= symbol_count <= 16:
                            config["symbol_count"] = symbol_count
                            sa_config["symbol_count"] = symbol_count
                        else:
                            self._add_warning(
                                "INTENT_OUT_OF_RANGE",
                                "advanced.structured_append.symbol_count",
                                f"Symbol count {symbol_count} out of valid range (2-16)",
                                "Using automatic symbol count",
                            )
                    
                    self._track_transformation(
                        "advanced.structured_append",
                        advanced.structured_append,
                        sa_config,
                        "accepted",
                        reason="Structured append supported via write_advanced",
                        confidence=1.0,
                    )
                    self._add_compatibility_info(
                        "advanced.structured_append",
                        "full",
                        available_since="0.1.0",
                        workarounds=[],
                    )

        return config, unsupported

    def _apply_performance_suggestions(self, config_kwargs: Dict[str, Any]) -> None:
        """Apply performance optimization suggestions to config."""
        # Extract and remove performance hints
        optimization_mode = config_kwargs.pop("_optimization_mode", None)
        max_svg_size = config_kwargs.pop("_max_svg_size_kb", None)
        simplify_paths = config_kwargs.pop("_simplify_paths", None)
        inline_styles = config_kwargs.pop("_inline_styles", None)
        coordinate_precision = config_kwargs.pop("_coordinate_precision", None)
        lazy_rendering = config_kwargs.pop("_lazy_rendering", None)
        
        # Apply suggested values if user hasn't explicitly set them
        if optimization_mode:
            # Apply scale suggestion if not explicitly set
            if "scale" not in config_kwargs and "_suggested_scale" in config_kwargs:
                config_kwargs["scale"] = config_kwargs.pop("_suggested_scale")
                
            # Apply shape suggestion if not explicitly set
            if "shape" not in config_kwargs and "_suggested_shape" in config_kwargs:
                config_kwargs["shape"] = config_kwargs.pop("_suggested_shape")
                
            # Apply merge suggestion if not explicitly set
            if "merge" not in config_kwargs and "_suggested_merge" in config_kwargs:
                config_kwargs["merge"] = config_kwargs.pop("_suggested_merge")
        
        # Apply path simplification suggestions
        if simplify_paths and "_suggested_corner_radius" in config_kwargs:
            if "corner_radius" not in config_kwargs:
                config_kwargs["corner_radius"] = config_kwargs.pop("_suggested_corner_radius")
            if "connectivity" not in config_kwargs and "_suggested_connectivity" in config_kwargs:
                config_kwargs["connectivity"] = config_kwargs.pop("_suggested_connectivity")
        
        # Clean up any remaining suggestion keys
        keys_to_remove = [k for k in config_kwargs if k.startswith("_suggested_")]
        for key in keys_to_remove:
            config_kwargs.pop(key)
        
        # Store performance metadata for later use
        if any([max_svg_size, inline_styles, coordinate_precision, lazy_rendering]):
            self._performance_metadata = {
                "max_svg_size_kb": max_svg_size,
                "inline_styles": inline_styles,
                "coordinate_precision": coordinate_precision,
                "lazy_rendering": lazy_rendering,
            }

    def _needs_advanced_features(self, config_kwargs: Dict[str, Any], payload: PayloadConfig) -> bool:
        """Check if advanced QR generation is needed."""
        # Check for advanced features in config
        if config_kwargs.get("structured_append", False):
            return True
        if config_kwargs.get("mask") is not None:
            return True
        if payload.eci:
            return True
        return False
    
    def _create_advanced_qr(self, payload: PayloadConfig, config_kwargs: Dict[str, Any]) -> tuple[List, Dict[str, Any]]:
        """Create QR code(s) using advanced generator."""
        try:
            content = payload.get_content()
        except ValueError as e:
            raise IntentValidationError(
                intent_path="payload",
                message=str(e),
                original_value=payload.model_dump(exclude_none=True),
                suggestion="Provide at least one of: text, url, or data",
            ) from e
        
        # Build advanced config
        advanced_config = AdvancedQRConfig(
            eci_enabled=bool(payload.eci) if payload.eci is not None else False,
            mask_pattern=config_kwargs.get("mask"),
            structured_append=config_kwargs.get("structured_append", False),
            symbol_count=config_kwargs.get("symbol_count"),
        )
        
        # Create generator and generate QR codes
        generator = AdvancedQRGenerator()
        result = generator.generate_qr(
            content,
            advanced_config,
            error=payload.error_correction or "M"
        )
        
        # Track metadata
        if result.warnings:
            for warning in result.warnings:
                self._add_warning(
                    "ADVANCED_QR_WARNING",
                    "advanced",
                    warning,
                    None,
                    "info"
                )
        
        return result.qr_codes, result.metadata

    def _create_qr_code(self, payload: PayloadConfig) -> 'segno.QRCode':
        """Create QR code from payload.

        Raises:
            IntentValidationError: If payload content is invalid
        """
        try:
            content = payload.get_content()
        except ValueError as e:
            raise IntentValidationError(
                intent_path="payload",
                message=str(e),
                original_value=payload.model_dump(exclude_none=True),
                suggestion="Provide at least one of: text, url, or data",
            ) from e

        # Basic QR code creation
        qr_kwargs = {}
        if payload.error_correction:
            # Pass through segno error correction (segno expects L, M, Q, H)
            qr_kwargs["error"] = payload.error_correction

        # Pass the error correction level directly as the correct type
        if 'error' in qr_kwargs:
            # Convert string error level to segno's expected format
            error_level = qr_kwargs['error']
            return segno.make(content, error=error_level)
        else:
            return segno.make(content)

    def _validate_contrast(self, config: RenderingConfig, min_ratio: float) -> None:
        """Validate color contrast meets minimum requirements."""
        # Get colors from config
        dark_color = config.dark
        light_color = config.light
        
        # Validate contrast
        is_valid, actual_ratio, message = validate_qr_contrast(
            dark_color, light_color, min_ratio
        )
        
        if not is_valid:
            # Add warning about poor contrast
            self._add_warning(
                "CONTRAST_BELOW_MINIMUM",
                "validation.min_contrast",
                message,
                f"Consider using colors with contrast ratio >= {min_ratio}:1",
                severity="error" if actual_ratio < 3.0 else "warning"
            )
            self._add_degradation_detail(
                "validation.min_contrast",
                f"Minimum contrast ratio {min_ratio}:1",
                f"Actual contrast ratio {actual_ratio:.1f}:1",
                message,
                ["Increase contrast between dark and light colors", 
                 "Use black (#000000) and white (#FFFFFF) for maximum contrast"],
                "major" if actual_ratio < 3.0 else "moderate"
            )
        else:
            # Track successful validation
            self._track_transformation(
                "validation.min_contrast",
                min_ratio,
                actual_ratio,
                "accepted",
                reason=message,
                confidence=1.0
            )
            
        # Store actual contrast ratio in metrics
        self._actual_contrast_ratio = actual_ratio

    def _calculate_metrics(
        self,
        config: RenderingConfig,
        total_time: float,
        validation_time: float,
        svg_time: float,
    ) -> PerformanceMetrics:
        """Calculate performance and quality metrics."""

        # Basic performance metrics
        metrics = PerformanceMetrics(
            rendering_time_ms=total_time,
            validation_time_ms=validation_time,
            svg_generation_time_ms=svg_time,
            estimated_scanability="pass",  # Basic assumption for now
            min_module_px=config.scale,
            actual_quiet_zone=config.border,
        )

        # Add actual contrast ratio if calculated
        if hasattr(self, "_actual_contrast_ratio"):
            metrics = metrics.model_copy(
                update={"contrast_ratio": self._actual_contrast_ratio}
            )
        elif hasattr(config, "dark") and hasattr(config, "light"):
            # Calculate contrast ratio if not already done
            _, ratio, _ = validate_qr_contrast(config.dark, config.light)
            if ratio:
                metrics = metrics.model_copy(
                    update={"contrast_ratio": ratio}
                )

        return metrics

    def process_style_intents(
        self, style: Optional[StyleIntents]
    ) -> tuple[Dict[str, Any], list[str]]:
        """Process style intents with degradation.

        Returns:
            Tuple of (processed_config, unsupported_paths)
        """
        if not style:
            return {}, []

        processed: Dict[str, Any] = {}
        unsupported: list[str] = []

        # Module shape validation
        if style.module_shape:
            supported_shapes = self.manifest.features.shapes.module_shapes
            if style.module_shape in supported_shapes:
                processed["shape"] = style.module_shape
                self._track_transformation(
                    "style.module_shape",
                    style.module_shape,
                    style.module_shape,
                    "accepted",
                    confidence=1.0,
                )
            else:
                # Create UnsupportedIntentError but continue with degradation
                error = UnsupportedIntentError(
                    intent_path="style.module_shape",
                    feature=f"Shape '{style.module_shape}'",
                    alternatives=supported_shapes[:5],
                )
                self._add_warning(
                    error.code,
                    error.intent_path,
                    error.message,
                    error.suggestion,
                )
                processed["shape"] = "square"
                self._track_transformation(
                    "style.module_shape",
                    style.module_shape,
                    "square",
                    "rejected",
                    reason=f"Shape '{style.module_shape}' not supported, using default",
                    confidence=0.0,
                )
                self._add_degradation_detail(
                    "style.module_shape",
                    f"Shape '{style.module_shape}'",
                    "square",
                    f"Shape '{style.module_shape}' not supported",
                    error.alternatives,
                    "minor",
                )
                unsupported.append("style.module_shape")

        # Merge strategy validation
        if style.merge:
            supported_strategies = self.manifest.features.shapes.merge_strategies
            if style.merge in supported_strategies:
                processed["merge"] = style.merge
                self._track_transformation(
                    "style.merge",
                    style.merge,
                    style.merge,
                    "accepted",
                    confidence=1.0,
                )
            else:
                error = UnsupportedIntentError(
                    intent_path="style.merge",
                    feature=f"Merge strategy '{style.merge}'",
                    alternatives=supported_strategies,
                )
                self._add_warning(
                    error.code,
                    error.intent_path,
                    error.message,
                    error.suggestion,
                )
                processed["merge"] = "none"
                self._track_transformation(
                    "style.merge",
                    style.merge,
                    "none",
                    "rejected",
                    reason=f"Merge strategy '{style.merge}' not supported, using default",
                    confidence=0.0,
                )
                unsupported.append("style.merge")

        # Connectivity validation
        if style.connectivity:
            supported_modes = self.manifest.features.shapes.connectivity_modes
            if style.connectivity in supported_modes:
                processed["connectivity"] = style.connectivity
                self._track_transformation(
                    "style.connectivity",
                    style.connectivity,
                    style.connectivity,
                    "accepted",
                    confidence=1.0,
                )
            else:
                self._add_warning(
                    "INTENT_UNSUPPORTED_VALUE",
                    "style.connectivity",
                    f"Connectivity mode '{style.connectivity}' not supported",
                    f"Using '4-way' instead. Supported: {supported_modes}",
                )
                processed["connectivity"] = "4-way"
                self._track_transformation(
                    "style.connectivity",
                    style.connectivity,
                    "4-way",
                    "rejected",
                    reason=f"Connectivity mode '{style.connectivity}' not supported, using default",
                    confidence=0.0,
                )
                unsupported.append("style.connectivity")

        # Corner radius validation
        if style.corner_radius is not None:
            bounds = self.manifest.bounds.get("corner_radius", {})
            min_val, max_val = bounds.get("min", 0.0), bounds.get("max", 1.0)
            if min_val <= style.corner_radius <= max_val:
                processed["corner_radius"] = style.corner_radius
            else:
                validation_error = IntentValidationError(
                    intent_path="style.corner_radius",
                    message=f"Corner radius {style.corner_radius} outside valid range [{min_val}, {max_val}]",
                    original_value=style.corner_radius,
                    suggestion=f"Use a value between {min_val} and {max_val}",
                )
                self._add_warning(
                    validation_error.code,
                    validation_error.intent_path,
                    validation_error.message,
                    validation_error.suggestion,
                )
                processed["corner_radius"] = max(
                    min_val, min(max_val, style.corner_radius)
                )

        # Pattern-specific styling
        if style.patterns:
            pattern_config = self._process_pattern_styles(style.patterns)
            if pattern_config:
                processed.update(pattern_config)
                self._track_transformation(
                    "style.patterns",
                    style.patterns,
                    pattern_config,
                    "accepted",
                    reason="Pattern-specific styling applied",
                    confidence=0.9,
                )
            else:
                unsupported.append("style.patterns")

        # Color palette processing
        if style.palette:
            processed_palette = self._process_palette(style.palette)
            processed.update(processed_palette)

        return processed, unsupported

    def process_frame_intents(
        self, frame: Optional[FrameIntents]
    ) -> tuple[Dict[str, Any], list[str]]:
        """Process frame intents with degradation."""
        if not frame:
            return {}, []

        processed: Dict[str, Any] = {}
        unsupported: list[str] = []

        # Frame shape validation
        if frame.shape:
            supported_shapes = self.manifest.features.frames.frame_shapes
            if frame.shape in supported_shapes:
                processed["frame_shape"] = frame.shape
            else:
                self._add_warning(
                    "INTENT_UNSUPPORTED_VALUE",
                    "frame.shape",
                    f"Frame shape '{frame.shape}' not supported",
                    f"Using 'square' instead. Supported: {supported_shapes}",
                )
                processed["frame_shape"] = "square"
                unsupported.append("frame.shape")

        # Clip mode validation
        if frame.clip_mode:
            supported_modes = self.manifest.features.frames.clip_modes
            if frame.clip_mode in supported_modes:
                processed["clip_mode"] = frame.clip_mode
            else:
                self._add_warning(
                    "INTENT_UNSUPPORTED_VALUE",
                    "frame.clip_mode",
                    f"Clip mode '{frame.clip_mode}' not supported",
                    f"Using 'clip' instead. Supported: {supported_modes}",
                )
                processed["clip_mode"] = "clip"
                unsupported.append("frame.clip_mode")

        # Corner radius validation
        if frame.corner_radius is not None:
            min_val, max_val = self.manifest.features.frames.corner_radius_range
            if min_val <= frame.corner_radius <= max_val:
                processed["frame_corner_radius"] = frame.corner_radius
            else:
                self._add_warning(
                    "INTENT_OUT_OF_RANGE",
                    "frame.corner_radius",
                    f"Frame corner radius {frame.corner_radius} outside valid range [{min_val}, {max_val}]",
                    "Clamping to valid range",
                )
                processed["frame_corner_radius"] = max(
                    min_val, min(max_val, frame.corner_radius)
                )

        # Fade distance for fade mode
        if frame.fade_distance is not None:
            # Validate fade distance is within reasonable bounds
            if 0 <= frame.fade_distance <= 50:
                processed["frame_fade_distance"] = float(frame.fade_distance)
                self._track_transformation(
                    "frame.fade_distance",
                    frame.fade_distance,
                    float(frame.fade_distance),
                    "accepted",
                    reason="Fade distance parameter supported",
                    confidence=1.0,
                )
            else:
                self._add_warning(
                    "INTENT_OUT_OF_RANGE",
                    "frame.fade_distance",
                    f"Fade distance {frame.fade_distance} outside valid range [0, 50]",
                    "Clamping to valid range",
                )
                processed["frame_fade_distance"] = max(0.0, min(50.0, float(frame.fade_distance)))
                self._track_transformation(
                    "frame.fade_distance",
                    frame.fade_distance,
                    processed["frame_fade_distance"],
                    "modified",
                    reason="Clamped to valid range",
                    confidence=0.9,
                )

        # Scale distance for scale mode
        if frame.scale_distance is not None:
            # Validate scale distance is within reasonable bounds
            if 0 <= frame.scale_distance <= 25:
                processed["frame_scale_distance"] = float(frame.scale_distance)
                self._track_transformation(
                    "frame.scale_distance",
                    frame.scale_distance,
                    float(frame.scale_distance),
                    "accepted",
                    reason="Scale distance parameter supported",
                    confidence=1.0,
                )
            else:
                self._add_warning(
                    "INTENT_OUT_OF_RANGE",
                    "frame.scale_distance",
                    f"Scale distance {frame.scale_distance} outside valid range [0, 25]",
                    "Clamping to valid range",
                )
                processed["frame_scale_distance"] = max(0.0, min(25.0, float(frame.scale_distance)))
                self._track_transformation(
                    "frame.scale_distance",
                    frame.scale_distance,
                    processed["frame_scale_distance"],
                    "modified",
                    reason="Clamped to valid range",
                    confidence=0.9,
                )

        return processed, unsupported

    def process_reserve_intents(
        self, reserve: Optional[ReserveIntents]
    ) -> tuple[Dict[str, Any], list[str]]:
        """Process reserve area intents with degradation."""
        if not reserve:
            return {}, []

        processed: Dict[str, Any] = {}
        unsupported: list[str] = []

        # Area percentage validation
        if reserve.area_pct is not None:
            max_safe = self.manifest.features.reserve.max_area_pct
            if reserve.area_pct <= max_safe:
                # Convert percentage to size (0.0-0.5 range)
                processed["centerpiece_size"] = reserve.area_pct / 100.0
            else:
                self._add_warning(
                    "SCANABILITY_AT_RISK",
                    "reserve.area_pct",
                    f"Reserve area {reserve.area_pct}% exceeds safe limit of {max_safe}%",
                    f"Reducing to {max_safe}% for scanability",
                )
                processed["centerpiece_size"] = max_safe / 100.0

        # Reserve shape validation
        if reserve.shape:
            supported_shapes = self.manifest.features.reserve.shapes
            if reserve.shape in supported_shapes:
                processed["centerpiece_shape"] = reserve.shape
            else:
                self._add_warning(
                    "INTENT_UNSUPPORTED_VALUE",
                    "reserve.shape",
                    f"Reserve shape '{reserve.shape}' not supported",
                    f"Using 'rect' instead. Supported: {supported_shapes}",
                )
                processed["centerpiece_shape"] = "rect"
                unsupported.append("reserve.shape")

        # Positioning
        if reserve.offset_x is not None:
            processed["centerpiece_offset_x"] = reserve.offset_x
        if reserve.offset_y is not None:
            processed["centerpiece_offset_y"] = reserve.offset_y

        # Reserve mode processing
        if reserve.mode:
            # Validate reserve mode
            valid_modes = ["knockout", "imprint"]
            if reserve.mode.lower() in valid_modes:
                processed["centerpiece_mode"] = reserve.mode.lower()
                self._track_transformation(
                    "reserve.mode",
                    reserve.mode,
                    reserve.mode.lower(),
                    "accepted",
                    reason=f"Reserve mode '{reserve.mode}' supported",
                    confidence=1.0,
                )
                self._add_compatibility_info(
                    "reserve.mode",
                    "full",
                    available_since="0.1.0",
                    workarounds=[],
                )
            else:
                self._add_warning(
                    "INTENT_UNSUPPORTED_VALUE",
                    "reserve.mode",
                    f"Reserve mode '{reserve.mode}' not recognized",
                    f"Using 'knockout' mode. Valid modes: {', '.join(valid_modes)}",
                )
                processed["centerpiece_mode"] = "knockout"
                self._track_transformation(
                    "reserve.mode",
                    reserve.mode,
                    "knockout",
                    "rejected",
                    reason=f"Invalid mode, falling back to default",
                    confidence=0.0,
                )
                unsupported.append("reserve.mode")

        # Enable centerpiece if any reserve settings specified
        if processed:
            processed["centerpiece_enabled"] = True

        return processed, unsupported

    def _process_palette(self, palette: Dict[str, str]) -> Dict[str, Any]:
        """Process color palette with basic validation."""
        processed = {}

        # Map common palette keys to config keys
        palette_map = {
            "fg": "dark",
            "foreground": "dark",
            "dark": "dark",
            "bg": "light",
            "background": "light",
            "light": "light",
        }

        for key, value in palette.items():
            if key in palette_map:
                config_key = palette_map[key]
                # Basic color validation (accept any string for now)
                if isinstance(value, str) and value.strip():
                    processed[config_key] = value.strip()
                else:
                    self._add_warning(
                        "INTENT_INVALID_VALUE",
                        f"style.palette.{key}",
                        f"Invalid color value: {value}",
                        "Using default color",
                    )
            else:
                self._add_warning(
                    "INTENT_UNSUPPORTED_KEY",
                    f"style.palette.{key}",
                    f"Palette key '{key}' not supported",
                    "Use 'fg'/'bg' or 'dark'/'light' instead",
                )

        return processed

    def _process_pattern_styles(self, patterns: Dict[str, str]) -> Dict[str, Any]:
        """Process pattern-specific styling."""
        processed = {}

        # Map pattern types to config keys
        pattern_map = {
            "finder": "finder_pattern_shape",
            "timing": "timing_pattern_shape",
            "alignment": "alignment_pattern_shape",
            "data": "data_module_shape",
        }

        for pattern_type, shape in patterns.items():
            if pattern_type in pattern_map:
                config_key = pattern_map[pattern_type]

                # Validate shape is supported
                supported_shapes = self.manifest.features.shapes.module_shapes
                if shape in supported_shapes:
                    processed[config_key] = shape
                    self._track_transformation(
                        f"style.patterns.{pattern_type}",
                        shape,
                        shape,
                        "accepted",
                        confidence=1.0,
                    )
                else:
                    self._add_warning(
                        "INTENT_UNSUPPORTED_VALUE",
                        f"style.patterns.{pattern_type}",
                        f"Shape '{shape}' not supported for {pattern_type} patterns",
                        f"Using default shape. Supported: {supported_shapes[:5]}...",
                    )
                    self._track_transformation(
                        f"style.patterns.{pattern_type}",
                        shape,
                        None,
                        "rejected",
                        reason="Unsupported shape",
                        confidence=1.0,
                    )
            else:
                self._add_warning(
                    "INTENT_UNSUPPORTED_KEY",
                    f"style.patterns.{pattern_type}",
                    f"Pattern type '{pattern_type}' not recognized",
                    "Use 'finder', 'timing', 'alignment', or 'data'",
                )

        return processed

    def _process_interactivity_intents(
        self, interactivity: Optional[InteractivityIntents]
    ) -> tuple[Dict[str, Any], list[str]]:
        """Process interactivity intents with tracking."""
        if not interactivity:
            return {}, []

        processed: Dict[str, Any] = {}
        unsupported: list[str] = []

        # Basic interactivity support
        if interactivity.hover_effects is not None:
            processed["interactive"] = interactivity.hover_effects
            self._track_transformation(
                "interactivity.hover_effects",
                interactivity.hover_effects,
                interactivity.hover_effects,
                "accepted",
                confidence=1.0,
            )

        if interactivity.tooltips is not None:
            processed["tooltips"] = interactivity.tooltips
            self._track_transformation(
                "interactivity.tooltips",
                interactivity.tooltips,
                interactivity.tooltips,
                "accepted",
                confidence=1.0,
            )

        # Enhanced hover effects
        if interactivity.hover_scale is not None:
            # Validate hover scale is within reasonable bounds (1.0-2.0)
            if 1.0 <= interactivity.hover_scale <= 2.0:
                processed["hover_scale"] = interactivity.hover_scale
                self._track_transformation(
                    "interactivity.hover_scale",
                    interactivity.hover_scale,
                    interactivity.hover_scale,
                    "accepted",
                    reason="Hover scale customization supported",
                    confidence=1.0,
                )
            else:
                self._add_warning(
                    "INTENT_OUT_OF_RANGE",
                    "interactivity.hover_scale",
                    f"Hover scale {interactivity.hover_scale} outside valid range [1.0, 2.0]",
                    "Clamping to valid range",
                )
                processed["hover_scale"] = max(1.0, min(2.0, interactivity.hover_scale))
                self._track_transformation(
                    "interactivity.hover_scale",
                    interactivity.hover_scale,
                    processed["hover_scale"],
                    "modified",
                    reason="Clamped to valid range",
                    confidence=0.9,
                )

        if interactivity.hover_brightness is not None:
            # Validate hover brightness is within reasonable bounds (0.5-2.0)
            if 0.5 <= interactivity.hover_brightness <= 2.0:
                processed["hover_brightness"] = interactivity.hover_brightness
                self._track_transformation(
                    "interactivity.hover_brightness",
                    interactivity.hover_brightness,
                    interactivity.hover_brightness,
                    "accepted",
                    reason="Hover brightness customization supported",
                    confidence=1.0,
                )
            else:
                self._add_warning(
                    "INTENT_OUT_OF_RANGE",
                    "interactivity.hover_brightness",
                    f"Hover brightness {interactivity.hover_brightness} outside valid range [0.5, 2.0]",
                    "Clamping to valid range",
                )
                processed["hover_brightness"] = max(0.5, min(2.0, interactivity.hover_brightness))
                self._track_transformation(
                    "interactivity.hover_brightness",
                    interactivity.hover_brightness,
                    processed["hover_brightness"],
                    "modified",
                    reason="Clamped to valid range",
                    confidence=0.9,
                )

        if interactivity.click_handlers is not None:
            processed["click_handlers"] = interactivity.click_handlers
            self._track_transformation(
                "interactivity.click_handlers",
                interactivity.click_handlers,
                interactivity.click_handlers,
                "accepted",
                reason="Click handlers supported via JavaScript events",
                confidence=1.0,
            )

        # Tooltip template support
        if interactivity.tooltip_template is not None:
            processed["tooltip_template"] = interactivity.tooltip_template
            self._track_transformation(
                "interactivity.tooltip_template",
                interactivity.tooltip_template,
                interactivity.tooltip_template,
                "accepted",
                reason="Custom tooltip templates supported",
                confidence=1.0,
            )

        # Cursor style support
        if interactivity.cursor_style is not None:
            # Validate cursor style is a valid CSS cursor value
            valid_cursors = [
                "auto", "default", "none", "context-menu", "help", "pointer",
                "progress", "wait", "cell", "crosshair", "text", "vertical-text",
                "alias", "copy", "move", "no-drop", "not-allowed", "grab", "grabbing",
                "e-resize", "n-resize", "ne-resize", "nw-resize", "s-resize",
                "se-resize", "sw-resize", "w-resize", "ew-resize", "ns-resize",
                "nesw-resize", "nwse-resize", "col-resize", "row-resize",
                "all-scroll", "zoom-in", "zoom-out"
            ]
            
            if interactivity.cursor_style in valid_cursors or interactivity.cursor_style.startswith("url("):
                processed["cursor_style"] = interactivity.cursor_style
                self._track_transformation(
                    "interactivity.cursor_style",
                    interactivity.cursor_style,
                    interactivity.cursor_style,
                    "accepted",
                    reason="Custom cursor styles supported",
                    confidence=1.0,
                )
            else:
                self._add_warning(
                    "INTENT_INVALID_VALUE",
                    "interactivity.cursor_style",
                    f"Invalid cursor style '{interactivity.cursor_style}'",
                    "Falling back to 'pointer' cursor",
                )
                processed["cursor_style"] = "pointer"
                self._track_transformation(
                    "interactivity.cursor_style",
                    interactivity.cursor_style,
                    "pointer",
                    "degraded",
                    reason="Invalid cursor style, using default pointer",
                    confidence=0.7,
                )

        return processed, unsupported

    def _process_animation_intents(
        self, animation: Optional[AnimationIntents]
    ) -> tuple[Dict[str, Any], list[str]]:
        """Process animation intents."""
        if not animation:
            return {}, []

        processed: Dict[str, Any] = {}
        unsupported: list[str] = []

        # Enable animations flag
        animation_enabled = False

        # Fade-in animation support
        if animation.fade_in is not None:
            if animation.fade_in:
                animation_enabled = True
                processed["animation_fade_in"] = True
                
                # Use default or specified fade duration
                fade_duration = animation.fade_duration or 0.5
                processed["animation_fade_duration"] = fade_duration
                
                self._track_transformation(
                    "animation.fade_in",
                    animation.fade_in,
                    animation.fade_in,
                    "accepted",
                    reason="Fade-in animation supported via CSS keyframes",
                    confidence=1.0,
                )

        # Fade duration configuration
        if animation.fade_duration is not None:
            # Validate duration is within bounds
            if 0.1 <= animation.fade_duration <= 5.0:
                processed["animation_fade_duration"] = animation.fade_duration
                self._track_transformation(
                    "animation.fade_duration",
                    animation.fade_duration,
                    animation.fade_duration,
                    "accepted",
                    reason="Fade duration within valid range",
                    confidence=1.0,
                )
            else:
                self._add_warning(
                    "INTENT_OUT_OF_RANGE",
                    "animation.fade_duration",
                    f"Fade duration {animation.fade_duration} outside valid range [0.1, 5.0]",
                    "Clamping to valid range",
                )
                processed["animation_fade_duration"] = max(0.1, min(5.0, animation.fade_duration))
                self._track_transformation(
                    "animation.fade_duration",
                    animation.fade_duration,
                    processed["animation_fade_duration"],
                    "modified",
                    reason="Clamped to valid range",
                    confidence=0.9,
                )

        # Stagger animation support
        if animation.stagger_animation is not None:
            if animation.stagger_animation:
                animation_enabled = True
                processed["animation_stagger"] = True
                
                # Use default or specified stagger delay
                stagger_delay = animation.stagger_delay or 0.02
                
                # Cap total reveal time to 800ms for scanability
                # Estimate module count (typical QR codes have 21x21 to 177x177 modules)
                # We'll use a conservative estimate
                max_total_reveal_ms = 800
                estimated_modules = 400  # Reasonable estimate for typical QR codes
                max_stagger_delay = max_total_reveal_ms / estimated_modules / 1000  # Convert to seconds
                
                if stagger_delay > max_stagger_delay:
                    self._add_warning(
                        "ANIMATION_REVEAL_TIME",
                        "animation.stagger_delay",
                        f"Stagger delay {stagger_delay}s would exceed max reveal time",
                        f"Capping to {max_stagger_delay:.4f}s for scanability",
                    )
                    stagger_delay = max_stagger_delay
                
                processed["animation_stagger_delay"] = stagger_delay
                
                self._track_transformation(
                    "animation.stagger_animation",
                    animation.stagger_animation,
                    animation.stagger_animation,
                    "accepted",
                    reason="Stagger animation supported via CSS delays",
                    confidence=1.0,
                )

        # Stagger delay configuration
        if animation.stagger_delay is not None:
            # Validate delay is within bounds
            if 0.01 <= animation.stagger_delay <= 0.5:
                processed["animation_stagger_delay"] = animation.stagger_delay
                self._track_transformation(
                    "animation.stagger_delay",
                    animation.stagger_delay,
                    animation.stagger_delay,
                    "accepted",
                    reason="Stagger delay within valid range",
                    confidence=1.0,
                )
            else:
                self._add_warning(
                    "INTENT_OUT_OF_RANGE",
                    "animation.stagger_delay",
                    f"Stagger delay {animation.stagger_delay} outside valid range [0.01, 0.5]",
                    "Clamping to valid range",
                )
                processed["animation_stagger_delay"] = max(0.01, min(0.5, animation.stagger_delay))
                self._track_transformation(
                    "animation.stagger_delay",
                    animation.stagger_delay,
                    processed["animation_stagger_delay"],
                    "modified",
                    reason="Clamped to valid range",
                    confidence=0.9,
                )

        # Pulse effect support
        if animation.pulse_effect is not None:
            if animation.pulse_effect:
                animation_enabled = True
                processed["animation_pulse"] = True
                
                self._track_transformation(
                    "animation.pulse_effect",
                    animation.pulse_effect,
                    animation.pulse_effect,
                    "accepted",
                    reason="Pulse effect supported for finder patterns",
                    confidence=1.0,
                )

        # Transition timing function
        if animation.transition_timing is not None:
            # Validate timing function
            valid_timings = [
                "linear", "ease", "ease-in", "ease-out", "ease-in-out",
                "step-start", "step-end"
            ]
            
            # Also allow cubic-bezier() and steps() functions
            if (animation.transition_timing in valid_timings or
                animation.transition_timing.startswith("cubic-bezier(") or
                animation.transition_timing.startswith("steps(")):
                
                processed["animation_timing"] = animation.transition_timing
                self._track_transformation(
                    "animation.transition_timing",
                    animation.transition_timing,
                    animation.transition_timing,
                    "accepted",
                    reason="Valid CSS timing function",
                    confidence=1.0,
                )
            else:
                self._add_warning(
                    "INTENT_INVALID_VALUE",
                    "animation.transition_timing",
                    f"Invalid timing function '{animation.transition_timing}'",
                    "Using default 'ease' timing",
                )
                processed["animation_timing"] = "ease"
                self._track_transformation(
                    "animation.transition_timing",
                    animation.transition_timing,
                    "ease",
                    "degraded",
                    reason="Invalid timing function, using default",
                    confidence=0.7,
                )

        # Enable animation system if any animation is requested
        if animation_enabled:
            processed["animations_enabled"] = True

        return processed, unsupported

    def _process_performance_intents(
        self, performance: Optional[PerformanceIntents]
    ) -> tuple[Dict[str, Any], list[str]]:
        """Process performance optimization intents."""
        if not performance:
            return {}, []

        processed: Dict[str, Any] = {}
        unsupported: list[str] = []

        # Optimization mode handling
        if performance.optimize_for:
            processed["_optimization_mode"] = performance.optimize_for
            
            if performance.optimize_for == "size":
                # Apply size optimizations
                processed["_suggested_scale"] = 8  # Smaller modules
                processed["_suggested_shape"] = "square"  # Simplest shape
                processed["_suggested_merge"] = "none"  # No complex merging
                self._add_warning(
                    "PERFORMANCE_OPTIMIZATION",
                    "performance.optimize_for",
                    "Size optimization applied",
                    "Using smaller scale (8px), square shapes, and no merging",
                    severity="info",
                )
            elif performance.optimize_for == "quality":
                # Apply quality optimizations
                processed["_suggested_scale"] = 12  # Larger modules
                processed["_suggested_merge"] = "soft"  # Better visual quality
                self._add_warning(
                    "PERFORMANCE_OPTIMIZATION",
                    "performance.optimize_for",
                    "Quality optimization applied",
                    "Using larger scale (12px) and soft merging for better visuals",
                    severity="info",
                )
            else:  # balanced
                # Balanced settings
                processed["_suggested_scale"] = 10  # Default scale
                self._add_warning(
                    "PERFORMANCE_OPTIMIZATION",
                    "performance.optimize_for",
                    "Balanced optimization applied",
                    "Using default settings for balanced size/quality",
                    severity="info",
                )
                
            self._track_transformation(
                "performance.optimize_for",
                performance.optimize_for,
                performance.optimize_for,
                "accepted",
                reason=f"Optimization mode '{performance.optimize_for}' applied",
                confidence=0.9,
            )

        # SVG size constraints
        if performance.max_svg_size_kb is not None:
            processed["_max_svg_size_kb"] = performance.max_svg_size_kb
            self._track_transformation(
                "performance.max_svg_size_kb",
                performance.max_svg_size_kb,
                performance.max_svg_size_kb,
                "accepted",
                reason="SVG size constraint recorded for post-processing",
                confidence=0.8,
            )
            self._add_warning(
                "PERFORMANCE_CONSTRAINT",
                "performance.max_svg_size_kb",
                f"SVG size target: {performance.max_svg_size_kb}KB",
                "Consider using simpler shapes if size exceeds target",
                severity="info",
            )

        # Path simplification
        if performance.simplify_paths is not None:
            processed["_simplify_paths"] = performance.simplify_paths
            if performance.simplify_paths:
                # Suggest settings that generate simpler paths
                processed["_suggested_corner_radius"] = 0.0  # No rounded corners
                processed["_suggested_connectivity"] = "4-way"  # Simpler connections
            self._track_transformation(
                "performance.simplify_paths",
                performance.simplify_paths,
                performance.simplify_paths,
                "accepted",
                reason="Path simplification preference recorded",
                confidence=0.8,
            )

        # Style inlining preference
        if performance.inline_styles is not None:
            processed["_inline_styles"] = performance.inline_styles
            self._track_transformation(
                "performance.inline_styles",
                performance.inline_styles,
                performance.inline_styles,
                "accepted",
                reason="CSS inlining preference recorded",
                confidence=1.0,
            )

        # Coordinate precision
        if performance.precision is not None:
            processed["_coordinate_precision"] = performance.precision
            self._track_transformation(
                "performance.precision",
                performance.precision,
                performance.precision,
                "accepted",
                reason=f"Coordinate precision set to {performance.precision} decimal places",
                confidence=1.0,
            )

        # Lazy rendering hints
        if performance.lazy_rendering is not None:
            processed["_lazy_rendering"] = performance.lazy_rendering
            self._track_transformation(
                "performance.lazy_rendering",
                performance.lazy_rendering,
                performance.lazy_rendering,
                "accepted",
                reason="Progressive rendering hint recorded",
                confidence=0.7,
            )

        return processed, unsupported

    def _process_branding_intents(
        self, branding: Optional[BrandingIntents]
    ) -> tuple[Dict[str, Any], list[str]]:
        """Process branding and customization intents."""
        if not branding:
            return {}, []

        processed = {}
        unsupported = []

        # Brand colors can be mapped to palette
        if branding.brand_colors:
            palette_config = self._process_palette(branding.brand_colors)
            processed.update(palette_config)
            self._track_transformation(
                "branding.brand_colors",
                branding.brand_colors,
                palette_config,
                "accepted" if palette_config else "rejected",
                confidence=0.9,
            )

        # Logo integration via centerpiece + metadata
        if branding.logo_url:
            # Enable centerpiece for logo space
            processed["centerpiece_enabled"] = True
            processed["centerpiece_size"] = branding.logo_padding or 0.15
            
            # Store logo metadata for overlay layer
            processed["logo_metadata"] = {
                "url": branding.logo_url,
                "padding": branding.logo_padding or 0.1
            }
            
            self._track_transformation(
                "branding.logo_url",
                branding.logo_url,
                processed["logo_metadata"],
                "accepted",
                reason="Logo embedding supported via overlay metadata",
                confidence=0.95,
            )

        # Logo padding configuration
        if branding.logo_padding is not None:
            # Already handled above with logo_url
            if not branding.logo_url:
                self._add_warning(
                    "INTENT_MISSING_DEPENDENCY",
                    "branding.logo_padding",
                    "Logo padding specified without logo URL",
                    "Specify logo_url to apply padding",
                )

        # Watermark support
        if branding.watermark:
            processed["watermark_text"] = branding.watermark
            processed["watermark_enabled"] = True
            
            self._track_transformation(
                "branding.watermark",
                branding.watermark,
                branding.watermark,
                "accepted",
                reason="Watermark text overlay supported",
                confidence=1.0,
            )

        # Custom patterns
        if branding.custom_patterns:
            self._add_warning(
                "INTENT_PARTIALLY_SUPPORTED",
                "branding.custom_patterns",
                "Custom pattern definitions partially supported",
                "Use pattern-specific shapes in style intents instead",
            )
            # Pass through for potential future use
            processed["custom_patterns"] = branding.custom_patterns
            self._track_transformation(
                "branding.custom_patterns",
                branding.custom_patterns,
                branding.custom_patterns,
                "degraded",
                reason="Limited custom pattern support",
                confidence=0.5,
            )

        # Theme presets
        if branding.theme_preset:
            # Define available theme presets
            theme_presets: Dict[str, Dict[str, Any]] = {
                "minimal": {
                    "dark": "#000000",
                    "light": "#FFFFFF",
                    "shape": "square",
                    "merge": "none",
                },
                "rounded": {
                    "dark": "#1a1a1a",
                    "light": "#FFFFFF",
                    "shape": "squircle",
                    "corner_radius": 0.3,
                    "merge": "soft",
                },
                "dots": {
                    "dark": "#2c3e50",
                    "light": "#ecf0f1",
                    "shape": "circle",
                    "merge": "none",
                },
                "corporate": {
                    "dark": "#003366",
                    "light": "#FFFFFF",
                    "shape": "rounded_square",
                    "corner_radius": 0.2,
                    "merge": "contiguous",
                },
                "playful": {
                    "dark": "#ff6b6b",
                    "light": "#ffe66d",
                    "shape": "leaf",
                    "merge": "soft",
                },
                "tech": {
                    "dark": "#00d4ff",
                    "light": "#001a33",
                    "shape": "hexagon",
                    "merge": "contiguous",
                },
            }
            
            if branding.theme_preset in theme_presets:
                theme_config = theme_presets[branding.theme_preset]
                processed.update(theme_config)
                
                self._track_transformation(
                    "branding.theme_preset",
                    branding.theme_preset,
                    theme_config,
                    "accepted",
                    reason=f"Applied {branding.theme_preset} theme preset",
                    confidence=1.0,
                )
            else:
                self._add_warning(
                    "INTENT_INVALID_VALUE",
                    "branding.theme_preset",
                    f"Unknown theme preset '{branding.theme_preset}'",
                    f"Available presets: {', '.join(theme_presets.keys())}",
                )
                unsupported.append("branding.theme_preset")

        return processed, unsupported

    def _track_transformation(
        self,
        path: str,
        original: Any,
        transformed: Any,
        transform_type: Literal["accepted", "degraded", "rejected", "modified"],
        reason: Optional[str] = None,
        confidence: Optional[float] = None,
    ) -> None:
        """Track a transformation step."""
        step = TransformationStep(
            intent_path=path,
            original_value=original,
            transformed_value=transformed,
            transformation_type=transform_type,
            reason=reason,
            confidence=confidence,
        )
        self.transformation_steps.append(step)

    def _add_degradation_detail(
        self,
        path: str,
        requested: str,
        applied: Optional[str],
        reason: str,
        alternatives: List[str],
        impact: Literal["minor", "moderate", "major"],
    ) -> None:
        """Add detailed degradation information."""
        detail = DegradationDetail(
            intent_path=path,
            requested_feature=requested,
            applied_feature=applied,
            degradation_reason=reason,
            alternatives=alternatives,
            impact_level=impact,
        )
        self.degradation_details.append(detail)

    def _add_compatibility_info(
        self,
        path: str,
        support_level: Literal["full", "partial", "unsupported", "experimental"],
        available_since: Optional[str] = None,
        planned_support: Optional[str] = None,
        workarounds: Optional[List[str]] = None,
    ) -> None:
        """Add compatibility information."""
        info = CompatibilityInfo(
            intent_path=path,
            support_level=support_level,
            available_since=available_since,
            planned_support=planned_support,
            workarounds=workarounds or [],
        )
        self.compatibility_info.append(info)

    def _build_translation_report(self) -> IntentTranslationReport:
        """Build comprehensive translation report."""
        # Create intent summary
        summary = {}

        # Count transformations by type
        transform_counts: Dict[str, int] = {}
        for step in self.transformation_steps:
            transform_counts[step.transformation_type] = (
                transform_counts.get(step.transformation_type, 0) + 1
            )

        summary["total_intents_processed"] = str(len(self.transformation_steps))
        summary["transformations"] = str(transform_counts)
        summary["degradations_applied"] = str(len(self.degradation_details))
        summary["compatibility_issues"] = str(len(self.compatibility_info))

        return IntentTranslationReport(
            transformation_steps=self.transformation_steps.copy(),
            degradation_details=self.degradation_details.copy(),
            compatibility_info=self.compatibility_info.copy(),
            intent_summary=summary,
        )

    def _calculate_feature_impact(self, config: RenderingConfig) -> Dict[str, str]:
        """Calculate performance/quality impact of features."""
        impact = {}

        # Module complexity impact
        if hasattr(config.geometry, "shape"):
            shape = config.geometry.shape
            # Handle both enum and string values
            shape_value = shape.value if hasattr(shape, "value") else shape
            if shape_value in ["connected", "connected-smooth", "connected-full"]:
                impact["module_shape"] = "High complexity, larger file size"
            elif shape_value in ["circle", "dot", "star"]:
                impact["module_shape"] = "Medium complexity, moderate file size"
            else:
                impact["module_shape"] = "Low complexity, smaller file size"

        # Interactivity impact
        if hasattr(config.style, "interactive") and config.style.interactive:
            impact["interactivity"] = "Adds CSS and classes, increases file size"

        # Frame impact
        if hasattr(config, "frame") and config.frame:
            impact["frame"] = "Adds clipping paths, slight size increase"

        # Centerpiece impact
        if (
            hasattr(config, "centerpiece")
            and config.centerpiece
            and hasattr(config.centerpiece, "enabled")
            and config.centerpiece.enabled
        ):
            impact["centerpiece"] = "May affect scanability if too large"

        return impact

    def _predict_scanability(self, config: RenderingConfig) -> str:
        """Predict scanability based on configuration."""
        risk_factors = []

        # Check quiet zone
        if config.border < 2:
            risk_factors.append("small_quiet_zone")

        # Check centerpiece size
        if hasattr(config, "centerpiece") and config.centerpiece:
            if hasattr(config.centerpiece, "size") and config.centerpiece.size > 0.2:
                risk_factors.append("large_centerpiece")

        # Check scale
        if config.scale < 5:
            risk_factors.append("small_module_size")

        # Make prediction
        if not risk_factors:
            return "excellent"
        elif len(risk_factors) == 1:
            return "good"
        elif len(risk_factors) == 2:
            return "moderate"
        else:
            return "poor"

    def clear_state(self) -> None:
        """Clear all state (warnings and tracking)."""
        self.warnings.clear()
        self.transformation_steps.clear()
        self.degradation_details.clear()
        self.compatibility_info.clear()
        self.original_intents = None

    def _add_warning(
        self,
        code: str,
        path: str,
        detail: str,
        suggestion: Optional[str] = None,
        severity: Literal["info", "warning", "error"] = "warning",
    ) -> None:
        """Add a warning to the collection."""
        warning = WarningInfo(
            code=code,
            path=path,
            detail=detail,
            suggestion=suggestion,
            severity=severity,
        )
        self.warnings.append(warning)

    def get_warnings(self) -> List[WarningInfo]:
        """Get all collected warnings."""
        return self.warnings.copy()


def render_with_intents(
    payload: PayloadConfig, intents: Optional[IntentsConfig] = None
) -> RenderingResult:
    """Main function for intent-based rendering.

    This is the primary entry point for the client's intent-based API.

    Args:
        payload: Payload configuration specifying content to encode
        intents: Optional intent configuration for styling and behavior

    Returns:
        RenderingResult with comprehensive output including SVG, warnings, and metrics

    Example:
        >>> payload = PayloadConfig(text="Hello World")
        >>> intents = IntentsConfig(
        ...     style=StyleIntents(module_shape="squircle", merge="soft"),
        ...     accessibility=AccessibilityIntents(title="Test QR")
        ... )
        >>> result = render_with_intents(payload, intents)
        >>> print(f"Generated {len(result.svg_content)} character SVG")
        >>> print(f"Warnings: {result.warning_count}")
    """
    processor = IntentProcessor()
    return processor.process_intents(payload, intents)


def process_intents(intents_dict: Dict[str, Any]) -> RenderingResult:
    """Process intents from dictionary format (for JSON API).

    Args:
        intents_dict: Dictionary containing 'payload' and optional 'intents'

    Returns:
        RenderingResult with comprehensive output

    Example:
        >>> intents_dict = {
        ...     "payload": {"text": "Hello World"},
        ...     "intents": {
        ...         "style": {"module_shape": "squircle"},
        ...         "accessibility": {"title": "Test QR"}
        ...     }
        ... }
        >>> result = process_intents(intents_dict)
    """
    # Extract payload
    payload_data = intents_dict.get("payload", {})
    payload = PayloadConfig.model_validate(payload_data)

    # Extract intents
    intents_data = intents_dict.get("intents")
    intents = IntentsConfig.model_validate(intents_data) if intents_data else None

    return render_with_intents(payload, intents)
