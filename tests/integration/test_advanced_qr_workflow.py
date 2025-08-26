"""
Integration tests for AdvancedQR workflow and file operations.

Tests for write_advanced function, file creation, and complete end-to-end
workflows with external dependencies.
"""

import os
import tempfile
from io import StringIO

import pytest

from segnomms.plugin import write_advanced


class TestWriteAdvanced:
    """Test cases for the write_advanced function."""

    def test_basic_advanced_write(self):
        """Test basic write_advanced functionality."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".svg", delete=False) as f:
            result = write_advanced("Hello, World!", f.name, scale=8, eci_enabled=False)

        try:
            assert result["success"] is True
            assert result["qr_count"] == 1
            assert result["is_sequence"] is False
            assert len(result["files_created"]) == 1
            assert os.path.exists(result["files_created"][0])

            # Check file content
            with open(result["files_created"][0], "r") as f:
                content = f.read()
                assert content.startswith("<?xml") or content.startswith("<svg")
                assert "svg" in content
        finally:
            # Cleanup
            for file_path in result["files_created"]:
                if os.path.exists(file_path):
                    os.unlink(file_path)

    def test_eci_mode_write(self):
        """Test write_advanced with ECI mode."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".svg", delete=False) as f:
            result = write_advanced(
                "International: café 日本語 🌟", f.name, scale=10, eci_enabled=True, encoding="UTF-8"
            )

        try:
            assert result["success"] is True
            assert result["advanced_config"]["eci_enabled"] is True
            assert result["advanced_config"]["encoding"] == "UTF-8"
            assert len(result["warnings"]) > 0  # Should warn about ECI compatibility

            # Check ECI was used in metadata
            assert result["metadata"].get("eci_enabled") is True
        finally:
            for file_path in result["files_created"]:
                if os.path.exists(file_path):
                    os.unlink(file_path)

    def test_mask_pattern_write(self):
        """Test write_advanced with manual mask pattern."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".svg", delete=False) as f:
            result = write_advanced("Mask pattern test", f.name, scale=8, mask_pattern=3)

        try:
            assert result["success"] is True
            assert result["advanced_config"]["mask_pattern"] == 3
            assert result["advanced_config"]["auto_mask"] is False
            assert result["metadata"].get("mask_pattern") == 3
        finally:
            for file_path in result["files_created"]:
                if os.path.exists(file_path):
                    os.unlink(file_path)

    def test_structured_append_write(self):
        """Test write_advanced with structured append."""
        # Create content that will fit in multiple QR codes but not too large
        long_content = (
            "This is a test content string that should work with "
            "structured append mode for multiple QR codes. " * 10
        )

        base_path = tempfile.mktemp(suffix=".svg")

        result = write_advanced(
            long_content,
            base_path,
            scale=6,
            structured_append=True,
            symbol_count=3,
            error="L",  # Use lower error correction for more capacity
            version=20,  # Use specific version to ensure capacity
        )

        try:
            assert result["success"] is True
            assert result["is_sequence"] is True
            assert result["qr_count"] >= 1

            # Should create multiple files for sequence
            if result["qr_count"] > 1:
                assert len(result["files_created"]) == result["qr_count"]

                # Check filename pattern for sequences
                for file_path in result["files_created"]:
                    assert os.path.exists(file_path)
                    # Should have format like "base-03-01.svg", "base-03-02.svg", etc.
                    filename = os.path.basename(file_path)
                    assert "-" in filename

            # Check metadata
            assert "sequence_info" in result["metadata"]
            assert result["metadata"]["total_data_length"] == len(long_content)

        finally:
            for file_path in result["files_created"]:
                if os.path.exists(file_path):
                    os.unlink(file_path)

    def test_stringio_output(self):
        """Test write_advanced with StringIO output."""
        output = StringIO()

        result = write_advanced("StringIO test", output, scale=8, mask_pattern=1)

        assert result["success"] is True
        assert result["qr_count"] == 1
        assert result["is_sequence"] is False

        # Check StringIO content
        content = output.getvalue()
        assert len(content) > 0
        assert "svg" in content

    def test_invalid_config_handling(self):
        """Test error handling for invalid configurations."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".svg", delete=False) as f:
            # Invalid mask pattern
            with pytest.raises(ValueError):
                write_advanced("Test", f.name, mask_pattern=10)  # Invalid

        # File should not be created on error
        if os.path.exists(f.name):
            os.unlink(f.name)

    def test_alternative_parameter_names(self):
        """Test alternative parameter naming."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".svg", delete=False) as f:
            result = write_advanced(
                "Alternative naming test",
                f.name,
                scale=8,
                qr_eci=True,  # Alternative to eci_enabled
                qr_encoding="UTF-8",  # Alternative to encoding
                qr_mask=2,  # Alternative to mask_pattern
                multi_symbol=True,  # Alternative to structured_append
                qr_symbol_count=2,  # Alternative to symbol_count
            )

        try:
            assert result["success"] is True
            assert result["advanced_config"]["eci_enabled"] is True
            assert result["advanced_config"]["encoding"] == "UTF-8"
            assert result["advanced_config"]["mask_pattern"] == 2
            assert result["advanced_config"]["structured_append"] is True
            assert result["advanced_config"]["symbol_count"] == 2
        finally:
            for file_path in result["files_created"]:
                if os.path.exists(file_path):
                    os.unlink(file_path)

    def test_combined_rendering_options(self):
        """Test advanced QR features combined with standard rendering options."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".svg", delete=False) as f:
            result = write_advanced(
                "Combined options test",
                f.name,
                # Advanced QR options
                eci_enabled=True,
                encoding="UTF-8",
                mask_pattern=4,
                # Standard rendering options
                scale=12,
                shape="squircle",
                corner_radius=0.3,
                dark="darkblue",
                light="lightgray",
                # Centerpiece options
                centerpiece_enabled=True,
                centerpiece_shape="circle",
                centerpiece_size=0.15,
            )

        try:
            assert result["success"] is True
            assert result["advanced_config"]["eci_enabled"] is True
            assert result["advanced_config"]["mask_pattern"] == 4

            # Check that file was created with rendering options
            with open(result["files_created"][0], "r") as file:
                content = file.read()
                assert "svg" in content
                # Advanced rendering should still work

        finally:
            for file_path in result["files_created"]:
                if os.path.exists(file_path):
                    os.unlink(file_path)
