"""Tests for deprecation warnings on legacy option names.

This module tests:
- Each reserve_* option emits DeprecationWarning
- Each qr_* option emits DeprecationWarning
- Conflict detection raises ValueError for different values
- Same-value duplicates only emit warning (no error)
"""

from __future__ import annotations

import warnings

import pytest

from segnomms.config import RenderingConfig


class TestCenterpieceDeprecationWarnings:
    """Test deprecation warnings for reserve_* options."""

    def test_reserve_center_emits_warning(self) -> None:
        """Test that reserve_center emits deprecation warning."""
        with pytest.warns(DeprecationWarning, match="reserve_center"):
            RenderingConfig.from_kwargs(reserve_center=True)

    def test_reserve_shape_emits_warning(self) -> None:
        """Test that reserve_shape emits deprecation warning."""
        with pytest.warns(DeprecationWarning, match="reserve_shape"):
            RenderingConfig.from_kwargs(reserve_shape="circle")

    def test_reserve_size_emits_warning(self) -> None:
        """Test that reserve_size emits deprecation warning."""
        with pytest.warns(DeprecationWarning, match="reserve_size"):
            RenderingConfig.from_kwargs(reserve_size=0.15)

    def test_reserve_offset_x_emits_warning(self) -> None:
        """Test that reserve_offset_x emits deprecation warning."""
        with pytest.warns(DeprecationWarning, match="reserve_offset_x"):
            RenderingConfig.from_kwargs(reserve_offset_x=0.1)

    def test_reserve_offset_y_emits_warning(self) -> None:
        """Test that reserve_offset_y emits deprecation warning."""
        with pytest.warns(DeprecationWarning, match="reserve_offset_y"):
            RenderingConfig.from_kwargs(reserve_offset_y=-0.1)

    def test_reserve_margin_emits_warning(self) -> None:
        """Test that reserve_margin emits deprecation warning."""
        with pytest.warns(DeprecationWarning, match="reserve_margin"):
            RenderingConfig.from_kwargs(reserve_margin=3)


class TestQRAdvancedDeprecationWarnings:
    """Test deprecation warnings for qr_* options."""

    def test_qr_eci_emits_warning(self) -> None:
        """Test that qr_eci emits deprecation warning."""
        with pytest.warns(DeprecationWarning, match="qr_eci"):
            RenderingConfig.from_kwargs(qr_eci=True)

    def test_qr_encoding_emits_warning(self) -> None:
        """Test that qr_encoding emits deprecation warning."""
        with pytest.warns(DeprecationWarning, match="qr_encoding"):
            RenderingConfig.from_kwargs(qr_encoding="utf-8")

    def test_qr_mask_emits_warning(self) -> None:
        """Test that qr_mask emits deprecation warning."""
        with pytest.warns(DeprecationWarning, match="qr_mask"):
            RenderingConfig.from_kwargs(qr_mask=3)

    def test_qr_symbol_count_emits_warning(self) -> None:
        """Test that qr_symbol_count emits deprecation warning."""
        with pytest.warns(DeprecationWarning, match="qr_symbol_count"):
            RenderingConfig.from_kwargs(qr_symbol_count=1)

    def test_qr_boost_error_emits_warning(self) -> None:
        """Test that qr_boost_error emits deprecation warning."""
        with pytest.warns(DeprecationWarning, match="qr_boost_error"):
            RenderingConfig.from_kwargs(qr_boost_error=True)

    def test_multi_symbol_emits_warning(self) -> None:
        """Test that multi_symbol emits deprecation warning."""
        with pytest.warns(DeprecationWarning, match="multi_symbol"):
            RenderingConfig.from_kwargs(multi_symbol=False)


class TestDeprecationConflictHandling:
    """Test conflict handling when both deprecated and current names are used."""

    def test_conflicting_values_raises_error(self) -> None:
        """Test that conflicting values raise ValueError."""
        with pytest.raises(ValueError, match="[Cc]onflict"):
            RenderingConfig.from_kwargs(
                reserve_size=0.3,
                centerpiece_size=0.4,
            )

    def test_same_values_only_warns(self) -> None:
        """Test that same values only emit warning, no error."""
        # Should not raise, but should warn
        with pytest.warns(DeprecationWarning, match="reserve_size"):
            config = RenderingConfig.from_kwargs(
                reserve_size=0.3,
                centerpiece_size=0.3,
            )
            # Verify the config was created successfully
            assert config.centerpiece.size == 0.3

    def test_deprecated_value_maps_to_current(self) -> None:
        """Test that deprecated option value is correctly mapped to current."""
        with pytest.warns(DeprecationWarning):
            # Note: centerpiece_enabled=True requires a size, so we test with size
            config = RenderingConfig.from_kwargs(reserve_size=0.15)
            assert config.centerpiece.size == 0.15

    def test_qr_option_conflict_raises_error(self) -> None:
        """Test that conflicting qr_* options raise ValueError."""
        with pytest.raises(ValueError, match="[Cc]onflict"):
            RenderingConfig.from_kwargs(
                qr_mask=3,
                mask_pattern=5,
            )


class TestDeprecationWarningMessage:
    """Test that deprecation warning messages are informative."""

    def test_warning_includes_old_name(self) -> None:
        """Test warning message includes the deprecated option name."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            RenderingConfig.from_kwargs(reserve_center=True)

            deprecation_warnings = [
                warning for warning in w if issubclass(warning.category, DeprecationWarning)
            ]
            assert len(deprecation_warnings) >= 1
            assert "reserve_center" in str(deprecation_warnings[0].message)

    def test_warning_includes_new_name(self) -> None:
        """Test warning message includes the recommended new option name."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            RenderingConfig.from_kwargs(reserve_center=True)

            deprecation_warnings = [
                warning for warning in w if issubclass(warning.category, DeprecationWarning)
            ]
            assert len(deprecation_warnings) >= 1
            assert "centerpiece_enabled" in str(deprecation_warnings[0].message)
