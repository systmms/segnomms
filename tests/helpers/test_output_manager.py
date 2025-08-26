"""
Test output manager for consistent file naming and organization.

This module provides a centralized way to manage all test outputs (SVG, PNG, config)
with consistent naming conventions and directory organization.
"""

import io
import json
import re
from pathlib import Path
from typing import Any, Dict, Optional, Union

import segno

from segnomms import write
from segnomms.config import RenderingConfig


class OutputManager:
    """Manages all test output with consistent naming and organization."""

    def __init__(self, base_dir: Optional[Path] = None):
        """
        Initialize the test output manager.

        Args:
            base_dir: Base directory for tests. Defaults to tests/ directory.
        """
        if base_dir is None:
            base_dir = Path(__file__).parent.parent

        self.base_dir = base_dir
        self.visual_dir = base_dir / "visual"
        self.review_dir = base_dir / "review"
        self.structural_dir = base_dir / "structural"

        # Visual subdirectories
        self.baseline_dir = self.visual_dir / "baseline"
        self.output_dir = self.visual_dir / "output"
        self.diff_dir = self.visual_dir / "diff"

        # Review subdirectories
        self.review_output_dir = self.review_dir / "output"

        # Ensure directories exist
        self._ensure_directories()

    def _ensure_directories(self):
        """Ensure all required directories exist."""
        dirs = [
            self.visual_dir,
            self.baseline_dir,
            self.output_dir,
            self.diff_dir,
            self.review_dir,
            self.review_output_dir,
            self.structural_dir,
        ]

        for directory in dirs:
            directory.mkdir(parents=True, exist_ok=True)

    def generate_test_output(
        self,
        test_case_id: str,
        qr_code: segno.QRCode,
        config: Union[RenderingConfig, Dict[str, Any]],
        output_type: str = "output",
    ) -> Dict[str, Path]:
        """
        Generate all outputs for a test case with consistent naming.

        Args:
            test_case_id: Unique identifier for the test case
            qr_code: Segno QR code object
            config: Rendering configuration (RenderingConfig or dict)
            output_type: Type of output - "output", "baseline", or "review"

        Returns:
            Dictionary with paths to generated files:
                - svg: Path to SVG file
                - png: Path to PNG file
                - config: Path to config JSON file
                - test_id: Sanitized test ID
        """
        # Determine output directory based on type
        if output_type == "baseline":
            output_dir = self.baseline_dir
        elif output_type == "review":
            output_dir = self.review_output_dir
        else:
            output_dir = self.output_dir

        # Consistent file naming
        base_name = self._sanitize_test_id(test_case_id)

        # File paths
        svg_path = output_dir / f"{base_name}.svg"
        png_path = output_dir / f"{base_name}.png"
        config_path = output_dir / f"{base_name}.config.json"

        # Generate SVG
        svg_buffer = io.StringIO()
        if isinstance(config, dict):
            write(qr_code, svg_buffer, **config)
        else:
            # Convert RenderingConfig to kwargs
            write(qr_code, svg_buffer, **self._config_to_kwargs(config))

        svg_content = svg_buffer.getvalue()
        svg_path.write_text(svg_content)

        # Generate PNG by converting SVG
        try:
            # Try cairosvg first (most reliable when it works)
            try:
                import cairosvg

                png_bytes = cairosvg.svg2png(
                    bytestring=svg_content.encode("utf-8"),
                    output_width=800,  # Default reasonable size
                    output_height=800,
                    dpi=96,
                )
                png_path.write_bytes(png_bytes)

            except (ImportError, OSError):
                # Fallback to rsvg-convert (available via Nix)
                import subprocess
                import tempfile

                # Create temporary SVG file since rsvg-convert doesn't support --stdin
                with tempfile.NamedTemporaryFile(mode="w", suffix=".svg", delete=False) as temp_svg:
                    temp_svg.write(svg_content)
                    temp_svg_path = temp_svg.name

                try:
                    result = subprocess.run(
                        ["rsvg-convert", "--format=png", "--output", str(png_path), temp_svg_path],
                        capture_output=True,
                        text=True,
                    )

                    if result.returncode != 0:
                        raise RuntimeError(f"rsvg-convert failed: {result.stderr}")
                finally:
                    # Clean up temporary file
                    Path(temp_svg_path).unlink(missing_ok=True)

        except (FileNotFoundError, RuntimeError, subprocess.SubprocessError) as e:
            print(f"Warning: Could not generate PNG for {test_case_id}: {e}")
            print("PNG conversion requires cairosvg or rsvg-convert")
            png_path = None

        except Exception as e:
            print(f"Warning: PNG conversion failed for {test_case_id}: {e}")
            png_path = None

        # Save config
        if isinstance(config, dict):
            config_data = config
        else:
            config_data = config.model_dump() if hasattr(config, "model_dump") else config.dict()

        config_path.write_text(json.dumps(config_data, indent=2, sort_keys=True))

        return {"svg": svg_path, "png": png_path, "config": config_path, "test_id": base_name}

    def get_baseline_path(self, test_case_id: str, file_type: str = "png") -> Path:
        """
        Get the baseline file path for a test case.

        Args:
            test_case_id: Test case identifier
            file_type: Type of file - "png", "svg", or "config"

        Returns:
            Path to baseline file
        """
        base_name = self._sanitize_test_id(test_case_id)
        return self.baseline_dir / f"{base_name}.{file_type}"

    def get_output_path(self, test_case_id: str, file_type: str = "png") -> Path:
        """
        Get the output file path for a test case.

        Args:
            test_case_id: Test case identifier
            file_type: Type of file - "png", "svg", or "config"

        Returns:
            Path to output file
        """
        base_name = self._sanitize_test_id(test_case_id)
        return self.output_dir / f"{base_name}.{file_type}"

    def get_diff_path(self, test_case_id: str) -> Path:
        """
        Get the diff file path for a test case.

        Args:
            test_case_id: Test case identifier

        Returns:
            Path to diff file
        """
        base_name = self._sanitize_test_id(test_case_id)
        return self.diff_dir / f"{base_name}_diff.png"

    def _sanitize_test_id(self, test_id: str) -> str:
        """
        Convert test ID to safe filename.

        Examples:
            "circle shape (safe mode on)" -> "circle_shape_safe_mode_on"
            "Error Level: H" -> "error_level_h"
            "Frame: circle/fade" -> "frame_circle_fade"

        Args:
            test_id: Test identifier string

        Returns:
            Sanitized filename-safe string
        """
        # Convert to lowercase
        safe_id = test_id.lower()

        # Replace common separators with underscores
        safe_id = re.sub(r"[:\s\-/]+", "_", safe_id)

        # Remove parentheses and other special characters
        safe_id = re.sub(r'[()[\]{}<>,.!?@#$%^&*+=|\\`~"\']', "", safe_id)

        # Replace multiple underscores with single
        safe_id = re.sub(r"_+", "_", safe_id)

        # Strip leading/trailing underscores
        safe_id = safe_id.strip("_")

        return safe_id

    def _config_to_kwargs(self, config: RenderingConfig) -> Dict[str, Any]:
        """
        Convert RenderingConfig to kwargs for write function.

        Args:
            config: RenderingConfig object

        Returns:
            Dictionary of kwargs for write function
        """
        kwargs = {}

        # Basic parameters
        if hasattr(config, "scale"):
            kwargs["scale"] = config.scale
        if hasattr(config, "border"):
            kwargs["border"] = config.border
        if hasattr(config, "dark"):
            kwargs["dark"] = config.dark
        if hasattr(config, "light"):
            kwargs["light"] = config.light

        # Geometry parameters
        if hasattr(config, "geometry"):
            geo = config.geometry
            if hasattr(geo, "shape"):
                kwargs["shape"] = geo.shape.value if hasattr(geo.shape, "value") else geo.shape
            if hasattr(geo, "corner_radius"):
                kwargs["corner_radius"] = geo.corner_radius
            if hasattr(geo, "connectivity"):
                kwargs["connectivity"] = (
                    geo.connectivity.value if hasattr(geo.connectivity, "value") else geo.connectivity
                )
            if hasattr(geo, "merge"):
                kwargs["merge"] = geo.merge.value if hasattr(geo.merge, "value") else geo.merge
            if hasattr(geo, "min_island_modules"):
                kwargs["min_island_modules"] = geo.min_island_modules

        # Finder parameters
        if hasattr(config, "finder"):
            finder = config.finder
            if hasattr(finder, "shape"):
                kwargs["finder_shape"] = (
                    finder.shape.value if hasattr(finder.shape, "value") else finder.shape
                )
            if hasattr(finder, "inner_scale"):
                kwargs["finder_inner_scale"] = finder.inner_scale
            if hasattr(finder, "stroke"):
                kwargs["finder_stroke"] = finder.stroke

        # Style parameters
        if hasattr(config, "style"):
            style = config.style
            if hasattr(style, "interactive"):
                kwargs["interactive"] = style.interactive
            if hasattr(style, "safe_mode"):
                kwargs["safe_mode"] = style.safe_mode

        # Phase control
        for phase_num in range(1, 5):
            phase_attr = f"phase{phase_num}"
            if hasattr(config, phase_attr):
                phase = getattr(config, phase_attr)
                if hasattr(phase, "enabled"):
                    kwargs[f"enable_phase{phase_num}"] = phase.enabled

        # Frame parameters
        if hasattr(config, "frame"):
            frame = config.frame
            if hasattr(frame, "shape"):
                kwargs["frame_shape"] = frame.shape
            if hasattr(frame, "clip_mode"):
                kwargs["frame_clip_mode"] = frame.clip_mode
            if hasattr(frame, "corner_radius"):
                kwargs["frame_corner_radius"] = frame.corner_radius

        # Centerpiece parameters
        if hasattr(config, "centerpiece"):
            cp = config.centerpiece
            if hasattr(cp, "enabled"):
                kwargs["centerpiece_enabled"] = cp.enabled
            if hasattr(cp, "size"):
                kwargs["centerpiece_size"] = cp.size
            if hasattr(cp, "shape"):
                kwargs["centerpiece_shape"] = cp.shape

        return kwargs

    def cleanup_outputs(self, directory: str = "output"):
        """
        Clean up output directory.

        Args:
            directory: Which directory to clean - "output", "diff", or "all"
        """
        if directory == "all":
            dirs_to_clean = [self.output_dir, self.diff_dir, self.review_output_dir]
        elif directory == "diff":
            dirs_to_clean = [self.diff_dir]
        elif directory == "review":
            dirs_to_clean = [self.review_output_dir]
        else:
            dirs_to_clean = [self.output_dir]

        for dir_path in dirs_to_clean:
            if dir_path.exists():
                for file in dir_path.iterdir():
                    if file.is_file():
                        file.unlink()

    def list_test_cases(self, directory: str = "output") -> list[str]:
        """
        List all test cases in a directory.

        Args:
            directory: Which directory to list - "output", "baseline", or "review"

        Returns:
            List of test case IDs
        """
        if directory == "baseline":
            target_dir = self.baseline_dir
        elif directory == "review":
            target_dir = self.review_output_dir
        else:
            target_dir = self.output_dir

        # Get unique test cases by looking at .svg files
        test_cases = []
        for svg_file in target_dir.glob("*.svg"):
            test_case_id = svg_file.stem
            test_cases.append(test_case_id)

        return sorted(test_cases)
