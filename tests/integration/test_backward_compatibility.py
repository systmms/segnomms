"""Integration tests for backward compatibility with deprecated options.

This module tests:
- Deprecated options still produce correct QR output
- Mixed deprecated/current options work when values match
"""

from __future__ import annotations

import io
import warnings

import segno


class TestDeprecatedOptionsProduceCorrectOutput:
    """Test that deprecated options still produce correct QR output."""

    def test_reserve_options_produce_valid_svg(self) -> None:
        """Test that reserve_* options still produce valid SVG."""
        from segnomms import write

        qr = segno.make("Test QR Code")
        buffer = io.StringIO()

        # Use deprecated options - should still work
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            write(
                qr,
                buffer,
                reserve_center=True,
                reserve_size=0.15,
                reserve_shape="circle",
                scale=10,
            )

        svg_content = buffer.getvalue()
        assert svg_content.startswith("<?xml") or svg_content.startswith("<svg")
        assert "</svg>" in svg_content

    def test_qr_advanced_options_produce_valid_svg(self) -> None:
        """Test that qr_* options still produce valid SVG."""
        from segnomms import write

        qr = segno.make("Test QR Code")
        buffer = io.StringIO()

        # Use deprecated options - should still work
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            write(
                qr,
                buffer,
                qr_boost_error=False,
                scale=10,
            )

        svg_content = buffer.getvalue()
        assert svg_content.startswith("<?xml") or svg_content.startswith("<svg")
        assert "</svg>" in svg_content


class TestMixedOptionsCompatibility:
    """Test that mixing deprecated and current options works correctly."""

    def test_mixed_options_with_matching_values(self) -> None:
        """Test that mixed options with matching values work."""
        from segnomms.config import RenderingConfig

        # When values match, should work with just a warning
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            config = RenderingConfig.from_kwargs(
                reserve_size=0.15,
                centerpiece_size=0.15,  # Same value
                scale=10,
            )

        assert config.centerpiece.size == 0.15

    def test_deprecated_options_apply_correctly(self) -> None:
        """Test that deprecated option values are correctly applied."""
        from segnomms.config import RenderingConfig

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            config = RenderingConfig.from_kwargs(
                reserve_size=0.2,
                reserve_shape="rect",
                reserve_margin=5,
            )

        assert config.centerpiece.size == 0.2
        assert config.centerpiece.shape == "rect"
        assert config.centerpiece.margin == 5

    def test_current_options_still_work(self) -> None:
        """Test that current options work without deprecation warnings."""
        from segnomms.config import RenderingConfig

        # Should not emit any deprecation warnings
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            config = RenderingConfig.from_kwargs(
                centerpiece_enabled=True,
                centerpiece_size=0.15,
                centerpiece_shape="circle",
                scale=10,
            )

            deprecation_warnings = [
                warning
                for warning in w
                if issubclass(warning.category, DeprecationWarning)
                and "deprecated" in str(warning.message).lower()
            ]
            # Filter out Phase4Validator warning which may appear from imports
            option_warnings = [w for w in deprecation_warnings if "Phase4Validator" not in str(w.message)]
            assert len(option_warnings) == 0, f"Unexpected warnings: {option_warnings}"

        assert config.centerpiece.enabled is True
        assert config.centerpiece.size == 0.15


class TestFullRenderingWithDeprecatedOptions:
    """Test complete rendering workflows with deprecated options."""

    def test_full_render_with_deprecated_centerpiece_options(self) -> None:
        """Test full QR rendering using deprecated centerpiece options."""
        from segnomms import write

        qr = segno.make("https://example.com")
        buffer = io.StringIO()

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            write(
                qr,
                buffer,
                reserve_center=True,
                reserve_size=0.12,
                reserve_shape="circle",
                reserve_margin=2,
                shape="squircle",
                scale=15,
                border=4,
            )

        svg_content = buffer.getvalue()

        # Verify SVG structure
        assert "<svg" in svg_content
        assert "</svg>" in svg_content
        # Verify it's a reasonable size
        assert len(svg_content) > 1000  # Should have substantial content

    def test_deprecated_and_modern_features_together(self) -> None:
        """Test that deprecated options work with modern features."""
        from segnomms import write

        qr = segno.make("Mixed features test")
        buffer = io.StringIO()

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            write(
                qr,
                buffer,
                # Deprecated options
                reserve_center=True,
                reserve_size=0.1,
                # Modern options
                frame_shape="rounded-rect",
                frame_corner_radius=0.15,
                shape="connected",
                scale=12,
            )

        svg_content = buffer.getvalue()
        assert "<svg" in svg_content
        assert "</svg>" in svg_content
