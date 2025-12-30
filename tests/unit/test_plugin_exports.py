"""Tests for plugin module exports and public API boundaries.

This module tests:
- __all__ contains only public names (no underscore prefix)
- Star import works and only exposes public API
- Internal functions still accessible via direct import
"""

from __future__ import annotations

import importlib


class TestPluginExports:
    """Test the plugin module __all__ exports."""

    def test_all_contains_only_public_names(self) -> None:
        """Test that __all__ contains only public names (no underscore prefix)."""
        from segnomms import plugin

        for name in plugin.__all__:
            assert not name.startswith("_"), (
                f"Internal name '{name}' should not be in __all__. "
                f"Only public API names should be exported."
            )

    def test_expected_public_exports(self) -> None:
        """Test that __all__ contains the expected public functions."""
        from segnomms import plugin

        expected = {
            "write",
            "write_advanced",
            "register_with_segno",
            "generate_interactive_svg",
            "MAX_QR_SIZE",
        }
        actual = set(plugin.__all__)
        assert actual == expected, (
            f"Expected public exports: {expected}\n"
            f"Actual exports: {actual}\n"
            f"Missing: {expected - actual}\n"
            f"Unexpected: {actual - expected}"
        )

    def test_star_import_only_exposes_public_api(self) -> None:
        """Test that star import works and only exposes public API."""
        # Import the module and check what __all__ would expose
        plugin = importlib.import_module("segnomms.plugin")

        # Verify all names in __all__ are accessible and public
        for name in plugin.__all__:
            assert hasattr(plugin, name), f"Name '{name}' in __all__ is not accessible"
            assert not name.startswith("_"), f"Internal name '{name}' was exposed via __all__"

        # Should contain expected public API
        expected = {
            "write",
            "write_advanced",
            "register_with_segno",
            "generate_interactive_svg",
            "MAX_QR_SIZE",
        }
        assert (
            set(plugin.__all__) == expected
        ), f"__all__ exposed unexpected names: {set(plugin.__all__) - expected}"


class TestInternalFunctionsStillAccessible:
    """Test that internal functions remain accessible via direct import."""

    def test_export_configuration_accessible(self) -> None:
        """Test that _export_configuration is accessible via direct import."""
        from segnomms.plugin.export import _export_configuration

        assert callable(_export_configuration)

    def test_generate_config_hash_accessible(self) -> None:
        """Test that _generate_config_hash is accessible via direct import."""
        from segnomms.plugin.export import _generate_config_hash

        assert callable(_generate_config_hash)

    def test_get_pattern_specific_style_accessible(self) -> None:
        """Test that _get_pattern_specific_style is accessible via direct import."""
        from segnomms.plugin.patterns import _get_pattern_specific_style

        assert callable(_get_pattern_specific_style)

    def test_get_pattern_specific_render_kwargs_accessible(self) -> None:
        """Test that _get_pattern_specific_render_kwargs is accessible via direct import."""
        from segnomms.plugin.patterns import _get_pattern_specific_render_kwargs

        assert callable(_get_pattern_specific_render_kwargs)

    def test_render_cluster_accessible(self) -> None:
        """Test that _render_cluster is accessible via direct import."""
        from segnomms.plugin.rendering import _render_cluster

        assert callable(_render_cluster)

    def test_get_enhanced_render_kwargs_accessible(self) -> None:
        """Test that _get_enhanced_render_kwargs is accessible via direct import."""
        from segnomms.plugin.rendering import _get_enhanced_render_kwargs

        assert callable(_get_enhanced_render_kwargs)

    def test_format_svg_string_accessible(self) -> None:
        """Test that _format_svg_string is accessible via direct import."""
        from segnomms.plugin.rendering import _format_svg_string

        assert callable(_format_svg_string)

    def test_detect_and_remove_islands_accessible(self) -> None:
        """Test that _detect_and_remove_islands is accessible via direct import."""
        from segnomms.plugin.rendering import _detect_and_remove_islands

        assert callable(_detect_and_remove_islands)
