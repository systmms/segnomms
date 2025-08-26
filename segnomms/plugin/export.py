"""Export utilities for the SegnoMMS plugin.

This module handles configuration export, hash generation, and file naming
functionality for the plugin system.
"""

import hashlib
import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

from ..config import RenderingConfig


def _generate_config_hash(config: RenderingConfig) -> str:
    """Generate a stable hash from rendering configuration.

    This creates a short, deterministic hash based on the configuration
    parameters that affect visual output.

    Args:
        config: Rendering configuration

    Returns:
        Hexadecimal hash string
    """
    # Get full config dump in JSON-serializable format
    config_dict = config.model_dump(exclude_none=True, mode="json")

    # Extract key parameters that affect visual output
    key_params = {
        "scale": config_dict.get("scale"),
        "border": config_dict.get("border"),
        "shape": config_dict.get("geometry", {}).get("shape"),
        "corner_radius": config_dict.get("geometry", {}).get("corner_radius"),
        "dark": config_dict.get("dark"),
        "light": config_dict.get("light"),
        "merge": config_dict.get("geometry", {}).get("merge"),
        "connectivity": config_dict.get("geometry", {}).get("connectivity"),
        "frame_shape": config_dict.get("frame", {}).get("shape"),
        "centerpiece_enabled": config_dict.get("centerpiece", {}).get("enabled"),
        "centerpiece_shape": (
            config_dict.get("centerpiece", {}).get("shape")
            if config_dict.get("centerpiece", {}).get("enabled")
            else None
        ),
        "centerpiece_size": (
            config_dict.get("centerpiece", {}).get("size")
            if config_dict.get("centerpiece", {}).get("enabled")
            else None
        ),
        "centerpiece_mode": config_dict.get("centerpiece", {}).get("mode"),
        "interactive": config_dict.get("style", {}).get("interactive"),
        "patterns_enabled": config_dict.get("patterns", {}).get("enabled"),
    }

    # Convert to stable JSON string
    config_str = json.dumps(key_params, sort_keys=True)

    # Generate hash
    return hashlib.sha256(config_str.encode()).hexdigest()


def _export_configuration(
    config: RenderingConfig,
    svg_path: Path,
    format: str = "json",
    additional_metadata: Optional[Dict[str, Any]] = None,
) -> Optional[Path]:
    """Export rendering configuration alongside SVG file.

    Saves the complete configuration that was used to generate the SVG,
    allowing for reproducible generation and configuration tracking.

    Args:
        config: Rendering configuration to export
        svg_path: Path to the SVG file
        format: Export format ('json' or 'yaml')
        additional_metadata: Extra metadata to include

    Returns:
        Path to the configuration file if created, None otherwise
    """
    try:
        # Determine config filename
        if format in ["json", "yaml"]:
            config_filename = svg_path.stem + "_config." + format
        else:
            # Invalid format - return None
            return None

        config_path = svg_path.parent / config_filename

        # Prepare configuration data
        try:
            from .. import __version__

            segnomms_version = __version__
        except ImportError:
            segnomms_version = "unknown"

        config_data = {
            "segnomms_version": segnomms_version,
            "schema_version": "1.0",
            "generation_timestamp": None,  # Could add timestamp if needed
            "configuration": config.model_dump(exclude_none=True, mode="json"),
        }

        # Add additional metadata if provided
        if additional_metadata:
            config_data["metadata"] = additional_metadata

        # Add JSON schema reference
        config_data["$schema"] = "https://segnomms.io/schemas/v1/rendering-config.json"

        # Export based on format
        if format == "json":
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
        elif format == "yaml":
            # Optional YAML support
            try:
                import yaml

                with open(config_path, "w", encoding="utf-8") as f:
                    yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True)
            except ImportError:
                # Fall back to JSON if yaml not available
                config_path = svg_path.parent / (svg_path.stem + "_config.json")
                with open(config_path, "w", encoding="utf-8") as f:
                    json.dump(config_data, f, indent=2, ensure_ascii=False)

        return config_path

    except Exception as e:
        # Log error but don't fail the main operation
        logger = logging.getLogger(__name__)
        logger.warning(f"Failed to export configuration: {e}")
        return None
