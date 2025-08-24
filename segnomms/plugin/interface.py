"""Main API interface for the SegnoMMS plugin.

This module contains the primary public functions that users interact with:
- write(): Generate interactive SVG from existing QR code
- write_advanced(): Generate QR code with advanced features
- register_with_segno(): Register plugin with Segno
"""

import logging
from pathlib import Path
from typing import Any, BinaryIO, Dict, Optional, TextIO, Union

from ..config import RenderingConfig
from .config import AdvancedQRConfig, create_advanced_qr_generator
from .export import _export_configuration, _generate_config_hash
from .rendering import generate_interactive_svg

# Maximum QR code size to prevent DoS attacks
MAX_QR_SIZE = 1000  # ~1000x1000 modules is very large but still reasonable


def write(
    qr_code: Any, out: Union[TextIO, BinaryIO, str], **kwargs: Any
) -> Optional[Dict[str, Any]]:
    """Write an interactive SVG representation of the QR code.

    This is the main entry point for the segno plugin system. It generates
    an SVG with custom shapes and interactive features.

    Args:
        qr_code: Segno QR code object to render
        out: Output destination - can be a file path (str), text stream, or binary stream
        **kwargs: Rendering options including:

            Basic parameters:
            * scale (int): Size of each module in pixels (default: 10)
            * border (int): Number of modules for quiet zone (default: 4)
            * dark (str): Color for dark modules (default: 'black')
            * light (str): Color for light modules (default: 'white')
            * safe_mode (bool): Force square shapes for critical QR patterns (finder, timing) to ensure scannability (default: False)

            Geometry parameters:
            * connectivity (str): '4-way' or '8-way' neighbor connectivity
            * merge (str): 'none', 'soft', or 'aggressive' merging strategy
            * corner_radius (float): Corner radius 0.0-1.0 (0=square, 1=circle)
            * shape (str): 'square', 'circle', 'squircle', or 'diamond' base shape
            * min_island_modules (int): Minimum modules for island groups (1-10)

            Finder pattern parameters:
            * finder_shape (str): 'square', 'rounded', or 'circle'
            * finder_inner_scale (float): Inner square scale 0.1-1.0
            * finder_stroke (float): Stroke width in modules 0-5

            Phase control (auto-detected if None):
            * enable_phase1 (bool): Enable enhanced shapes
            * enable_phase2 (bool): Enable clustering
            * enable_phase3 (bool): Enable smoothing
            * enable_phase4 (bool): Enable frame and centerpiece features

            Phase 4 - Frame shape parameters:
            * frame_shape (str): 'square', 'circle', 'rounded-rect', 'squircle', 'custom'
            * frame_corner_radius (float): Corner radius for rounded-rect (0.0-1.0)
            * frame_clip_mode (str): 'clip' or 'fade' for edge treatment
            * frame_custom_path (str): Custom SVG path for 'custom' frame shape

            Phase 4 - Centerpiece reserve parameters:
            * centerpiece_enabled (bool): Enable centerpiece area clearing
            * centerpiece_shape (str): 'rect', 'circle', or 'squircle'
            * centerpiece_size (float): Size as fraction of QR code (0.0-0.5)
            * centerpiece_offset_x (float): X offset from center (-0.5 to 0.5)
            * centerpiece_offset_y (float): Y offset from center (-0.5 to 0.5)
            * centerpiece_margin (int): Module margin around centerpiece (0-10)

            Phase 4 - Quiet zone enhancement:
            * quiet_zone_style (str): 'none', 'solid', or 'gradient'
            * quiet_zone_color (str): Color for solid quiet zone
            * quiet_zone_gradient (dict): Gradient config with type, colors, etc.

            Legacy parameters:
            * xmldecl (bool): Include XML declaration (default: True)
            * svgclass (str): CSS class for SVG element (default: 'interactive-qr')
            * lineclass (str): CSS class for path elements (default: None)
            * title (str): SVG title element (default: 'Interactive QR Code')
            * desc (str): SVG description element (default: auto-generated)

    Raises:
        ValueError: If an invalid shape type is specified
        TypeError: If the output type is not supported

    Example:
        >>> import segno
        >>> from segnomms import write
        >>> qr = segno.make("Hello, World!")
        >>> # Basic usage
        >>> with open('output.svg', 'w') as f:
        ...     write(qr, f, shape='connected', scale=15)
        >>> # With circle frame and centerpiece
        >>> with open('framed.svg', 'w') as f:
        ...     write(qr, f, frame_shape='circle', centerpiece_enabled=True,
        ...           centerpiece_size=0.2, centerpiece_shape='circle')
    """
    # Create configuration from kwargs
    config = RenderingConfig.from_kwargs(**kwargs)

    # Extract export configuration options
    export_config = kwargs.get("export_config", True)
    use_hash_naming = kwargs.get("use_hash_naming", False)
    config_format = kwargs.get("config_format", "json")  # json or yaml

    # Generate the SVG content
    svg_content = generate_interactive_svg(qr_code, config)

    # Track files created
    files_created = []
    config_path = None
    config_hash = None

    # Handle output
    if isinstance(out, str):
        # File path provided - handle new naming and config export
        output_path = Path(out)

        # Generate config hash if needed for naming or export
        if use_hash_naming or export_config:
            config_hash = _generate_config_hash(config)

        # Generate improved filename if requested
        if use_hash_naming and config_hash:
            new_filename = f"qr_{config_hash[:8]}.svg"
            output_path = output_path.parent / new_filename

        # Write SVG file
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(svg_content)
        files_created.append(str(output_path))

        # Export configuration if requested
        if export_config:
            config_path = _export_configuration(config, output_path, config_format)
            if config_path:
                files_created.append(str(config_path))

        # Return result information if hash naming or config export was used
        if use_hash_naming or export_config:
            result = {
                "files": files_created,
                "svg_file": str(output_path),
                "config_files": [str(config_path)] if config_path else [],
                "files_created": files_created,  # Backward compatibility
            }
            if use_hash_naming and config_hash:
                result["config_hash"] = config_hash[:8]
            if export_config and config_path:
                result["config_file"] = str(config_path)  # Backward compatibility
            return result

        # No special result needed for basic file output
        return None

    elif hasattr(out, "write"):
        # Stream provided - use type: ignore for complex Union handling
        if hasattr(out, "mode") and "b" in getattr(out, "mode", ""):
            # Binary mode - write as UTF-8 bytes
            out.write(svg_content.encode("utf-8"))  # type: ignore[arg-type]
        else:
            # Text mode or unknown - try text first
            try:
                out.write(svg_content)  # type: ignore[call-overload]
            except (TypeError, AttributeError):
                # Fallback to binary
                out.write(svg_content.encode("utf-8"))  # type: ignore[arg-type]
        return None

    else:
        # Unsupported output type
        raise TypeError(f"Unsupported output type: {type(out)}")


def write_advanced(
    content: str, out: Union[TextIO, BinaryIO, str], **kwargs: Any
) -> Dict[str, Any]:
    """Write advanced QR code(s) with ECI, mask patterns, or structured append.

    This function provides enhanced QR code generation with advanced features
    including international character encoding, manual mask pattern selection,
    and multi-symbol structured append sequences.

    Args:
        content: Text content to encode
        out: Output path or stream for the generated QR code(s)
        **kwargs: Advanced configuration options:

            Basic Parameters:
            * scale (int): Module size in pixels (default: 10)
            * border (int): Quiet zone modules (default: 4)
            * dark (str): Dark module color (default: 'black')
            * light (str): Light module color (default: 'white')

            Advanced QR Generation:
            * eci_enabled (bool): Enable Extended Channel Interpretation
            * mask_pattern (int): Manual mask pattern selection (0-7)
            * structured_append (bool): Enable structured append for long content
            * auto_mask (bool): Use automatic mask pattern selection (default: True)
            * boost_error (bool): Use higher error correction when possible

            Export Options:
            * export_config (bool): Export configuration file (default: True)
            * use_hash_naming (bool): Use content-based filenames (default: False)
            * config_format (str): Configuration format - 'json' or 'yaml' (default: 'json')

            Rendering Options:
            All standard rendering options from write() are supported

    Returns:
        dict: Generation result containing:
            - files (list): List of all generated files
            - config_files (list): Configuration files created
            - warnings (list): Any generation warnings
            - advanced_config (dict): Advanced QR configuration used
            - fallback_used (bool): Whether fallback generation was used

    Example:
        >>> result = write_advanced(
        ...     "Hello, 世界! This is a long message with international characters.",
        ...     "output.svg",
        ...     eci_enabled=True,
        ...     structured_append=True,
        ...     export_config=True
        ... )
        >>> print(f"Generated {len(result['files'])} files")
    """
    # Parse and validate advanced configuration
    advanced_keys = {
        "eci_enabled",
        "mask_pattern",
        "structured_append",
        "symbol_count",
        "auto_mask",
        "boost_error",
        "encoding",
        "multi_symbol",
    }

    qr_keys = {"error", "version", "mode"}

    # Alternative parameter names for backward compatibility
    alternative_names = {
        "multi_symbol": "structured_append",
        "qr_eci": "eci_enabled",
        "qr_encoding": "encoding",
        "qr_mask": "mask_pattern",
        "qr_symbol_count": "symbol_count",
    }

    advanced_params = {}
    qr_params = {}

    # Separate parameters by target
    for key, value in kwargs.items():
        # Check if it's an alternative name first
        if key in alternative_names:
            mapped_key = alternative_names[key]
            advanced_params[mapped_key] = value
        elif key in advanced_keys:
            advanced_params[key] = value
        elif key in qr_keys:
            qr_params[key] = value

    # Handle special parameter formats for backward compatibility
    if "structured_append" in advanced_params:
        value = advanced_params["structured_append"]
        if isinstance(value, dict):
            # Convert dictionary format to boolean (enabled flag)
            advanced_params["structured_append"] = value.get("enabled", False)
            # Extract symbol_count if provided
            if "total" in value:
                advanced_params["symbol_count"] = value["total"]

    # Create advanced QR configuration
    try:
        advanced_config = AdvancedQRConfig(**advanced_params)
    except Exception as e:
        raise ValueError(f"Invalid advanced QR configuration: {e}") from e

    # Set defaults for QR generation
    error_level = qr_params.get("error", "M")
    version = qr_params.get("version", None)

    # Generate QR code(s) with advanced features
    generator = create_advanced_qr_generator()

    try:
        result = generator.generate_qr(content, advanced_config, error_level, version)
    except Exception as e:
        raise RuntimeError(f"Advanced QR generation failed: {e}") from e

    # Extract export configuration options
    export_config = kwargs.get("export_config", True)
    use_hash_naming = kwargs.get("use_hash_naming", False)
    config_format = kwargs.get("config_format", "json")

    # Handle output for single QR or sequence
    files_created = []
    config_files_created = []

    # Filter out advanced-only parameters from rendering config
    rendering_kwargs = {k: v for k, v in kwargs.items() if k not in advanced_keys}
    rendering_config = RenderingConfig.from_kwargs(**rendering_kwargs)

    if result.is_sequence and len(result.qr_codes) > 1:
        # Handle structured append sequence
        # Sequences require file path output, not streams
        if hasattr(out, "write"):
            raise ValueError(
                "Structured append sequences cannot be written to streams. "
                "Please provide a file path for multi-QR output."
            )

        # Validate that out is a valid string path
        if not isinstance(out, (str, Path)):
            raise TypeError(
                f"Output must be a file path (str/Path) for sequences, "
                f"got {type(out).__name__}"
            )

        base_path = str(out)

        # Generate sequence filenames
        if base_path.endswith(".svg"):
            base_name = base_path[:-4]
            extension = ".svg"
        else:
            base_name = base_path
            extension = ""

        # Generate each QR in sequence
        for i, qr in enumerate(result.qr_codes):
            if use_hash_naming:
                # Generate config with sequence metadata
                seq_config = rendering_config.model_copy()
                seq_config.metadata = seq_config.metadata or {}
                seq_config.metadata["sequence_index"] = i + 1
                seq_config.metadata["sequence_total"] = len(result.qr_codes)

                config_hash = _generate_config_hash(seq_config)
                sequence_filename = f"qr_{config_hash[:8]}_seq{i+1:02d}{extension}"
                sequence_path = Path(base_path).parent / sequence_filename
            else:
                # Standard sequence naming: base-03-01.svg, base-03-02.svg, etc.
                total = len(result.qr_codes)
                sequence_filename = (
                    f"{Path(base_name).name}-{total:02d}-{i+1:02d}{extension}"
                )
                sequence_path = Path(base_path).parent / sequence_filename

            # Generate SVG for this QR
            svg_content = generate_interactive_svg(qr, rendering_config)

            with open(sequence_path, "w", encoding="utf-8") as f:
                f.write(svg_content)
            files_created.append(str(sequence_path))

            # Export config for each sequence item if requested
            if export_config:
                if use_hash_naming:
                    # Add metadata to hash-named config
                    hash_metadata = {
                        "sequence_index": i + 1,
                        "sequence_total": len(result.qr_codes),
                        "content": content,
                        "advanced_config": advanced_config.model_dump(),
                    }
                    config_path = _export_configuration(
                        seq_config, sequence_path, config_format, hash_metadata
                    )
                else:
                    # Add sequence metadata including content and advanced config
                    sequence_metadata = {
                        "sequence_index": i + 1,
                        "sequence_total": len(result.qr_codes),
                        "content": content,
                        "advanced_config": advanced_config.model_dump(),
                    }
                    config_path = _export_configuration(
                        rendering_config,
                        sequence_path,
                        config_format,
                        sequence_metadata,
                    )

                if config_path:
                    config_files_created.append(str(config_path))

    else:
        # Single QR code output
        qr = result.qr_codes[0]

        # Generate SVG
        svg_content = generate_interactive_svg(qr, rendering_config)

        # Check if output is a stream or file path
        if hasattr(out, "write"):
            # Stream output (StringIO, file object, etc.)
            if hasattr(out, "mode") and "b" in getattr(out, "mode", ""):
                # Binary mode - write as UTF-8 bytes
                out.write(svg_content.encode("utf-8"))  # type: ignore[arg-type]
            else:
                # Text mode
                out.write(svg_content)  # type: ignore[call-overload]
            # For streams, we don't track file creation
        else:
            # File path output
            # Validate that out is a valid string path
            if not isinstance(out, (str, Path)):
                raise TypeError(
                    f"Output must be a file path (str/Path) or file-like object, "
                    f"got {type(out).__name__}"
                )
            output_path = Path(str(out))
            if use_hash_naming:
                config_hash = _generate_config_hash(rendering_config)
                new_filename = f"qr_{config_hash[:8]}.svg"
                output_path = output_path.parent / new_filename

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(svg_content)
            files_created.append(str(output_path))

            # Export configuration if requested
            if export_config:
                # Create metadata with content and advanced config
                metadata = {
                    "content": content,
                    "advanced_config": advanced_config.model_dump(),
                }
                config_path = _export_configuration(
                    rendering_config, output_path, config_format, metadata
                )
                if config_path:
                    config_files_created.append(str(config_path))

    # Return comprehensive result
    return {
        "success": True,
        "files_created": files_created,
        "config_files_created": config_files_created,
        "files": files_created,  # Backward compatibility alias
        "config_files": config_files_created,  # Backward compatibility alias
        "warnings": result.warnings,
        "qr_count": len(result.qr_codes),
        "is_sequence": result.is_sequence,
        "metadata": result.metadata,
        "advanced_config": advanced_config.model_dump(),
        "fallback_used": getattr(result, "fallback_used", False),
        "export_config": export_config,
    }


def register_with_segno() -> bool:
    """Register the SegnoMMS plugin with Segno.

    This function registers the write function as a plugin for the Segno
    library, allowing it to be used via segno.plugins.

    Returns:
        bool: True if registration successful, False otherwise
    """
    try:
        import segno.plugins

        segno.plugins.register(write, "segnomms")
        logging.info("SegnoMMS plugin registered successfully with Segno")
        return True
    except ImportError:
        logging.warning("Segno not available - plugin registration skipped")
        return False
    except Exception as e:
        logging.error(f"Failed to register SegnoMMS plugin with Segno: {e}")
        return False
