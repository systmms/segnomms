"""Tests for configuration export functionality."""

import json
from pathlib import Path

import segno

from segnomms import write, write_advanced
from segnomms.config import RenderingConfig


class TestConfigurationExport:
    """Test configuration export features."""

    def test_basic_config_export(self, tmp_path):
        """Test basic configuration export alongside SVG."""
        qr = segno.make("Test")
        output_file = tmp_path / "test.svg"

        # Generate with config export
        result = write(qr, str(output_file), scale=12, shape="circle", export_config=True)

        # Check result structure
        assert result is not None
        assert "svg_file" in result
        assert "config_file" in result
        assert "files_created" in result

        # Check files exist
        assert Path(result["svg_file"]).exists()
        assert Path(result["config_file"]).exists()

        # Check config file name
        config_path = Path(result["config_file"])
        assert config_path.stem == "test_config"
        assert config_path.suffix == ".json"

    def test_config_export_disabled(self, tmp_path):
        """Test disabling configuration export."""
        qr = segno.make("Test")
        output_file = tmp_path / "test.svg"

        # Generate without config export
        result = write(qr, str(output_file), scale=10, shape="square", export_config=False)

        # Should return None (backward compatibility)
        assert result is None

        # Only SVG should exist
        assert output_file.exists()
        config_file = output_file.parent / "test_config.json"
        assert not config_file.exists()

    def test_hash_based_naming(self, tmp_path):
        """Test hash-based file naming."""
        qr = segno.make("Test")
        output_file = tmp_path / "original.svg"

        # Generate with hash naming
        result = write(
            qr, str(output_file), scale=15, shape="squircle", corner_radius=0.3, use_hash_naming=True
        )

        assert result is not None
        assert "config_hash" in result
        assert len(result["config_hash"]) == 8  # Short hash

        # Check generated filename
        svg_path = Path(result["svg_file"])
        assert svg_path.name.startswith("qr_")
        assert result["config_hash"] in svg_path.name
        assert svg_path.suffix == ".svg"

    def test_configuration_content(self, tmp_path):
        """Test exported configuration file content."""
        qr = segno.make("Test", error="M")  # Specify error level
        output_file = tmp_path / "test.svg"

        # Generate with specific configuration
        result = write(
            qr,
            str(output_file),
            scale=20,
            shape="connected-extra-rounded",
            corner_radius=0.25,
            dark="#123456",
            light="#ffffff",
            frame_shape="circle",
            centerpiece_enabled=True,
            centerpiece_size=0.2,
            interactive=True,
            export_config=True,
        )

        # Load configuration file
        with open(result["config_file"], "r") as f:
            config_data = json.load(f)

        # Check structure
        assert "segnomms_version" in config_data
        assert "schema_version" in config_data
        assert "$schema" in config_data
        assert "configuration" in config_data

        # Check configuration values
        config = config_data["configuration"]
        assert config["scale"] == 20
        assert config["geometry"]["shape"] == "connected-extra-rounded"
        assert config["geometry"]["corner_radius"] == 0.25
        assert config["dark"] == "#123456"
        assert config["frame"]["shape"] == "circle"
        assert config["centerpiece"]["enabled"] is True
        assert config["centerpiece"]["size"] == 0.2
        assert config["style"]["interactive"] is True

    def test_advanced_qr_config_export(self, tmp_path):
        """Test configuration export with advanced QR features."""
        output_file = tmp_path / "advanced.svg"

        # Generate with advanced features
        result = write_advanced(
            "Hello 世界",
            str(output_file),
            eci_enabled=True,
            encoding="UTF-8",
            mask_pattern=3,
            scale=10,
            shape="circle",
            export_config=True,
        )

        assert result["export_config"] is True
        assert len(result["config_files_created"]) == 1

        # Load configuration
        config_file = result["config_files_created"][0]
        with open(config_file, "r") as f:
            config_data = json.load(f)

        # Check metadata
        assert "metadata" in config_data
        metadata = config_data["metadata"]
        assert metadata["content"] == "Hello 世界"
        assert metadata["advanced_config"]["eci_enabled"] is True
        assert metadata["advanced_config"]["encoding"] == "UTF-8"
        assert metadata["advanced_config"]["mask_pattern"] == 3

    def test_structured_append_config_export(self, tmp_path):
        """Test configuration export for structured append sequences."""
        output_file = tmp_path / "sequence.svg"

        # Generate structured append
        long_content = "Test content " * 50
        result = write_advanced(
            long_content,
            str(output_file),
            structured_append=True,
            symbol_count=3,
            scale=8,
            export_config=True,
        )

        assert result["qr_count"] == 3
        assert len(result["config_files_created"]) == 3

        # Check each config file
        for i, config_file in enumerate(result["config_files_created"]):
            with open(config_file, "r") as f:
                config_data = json.load(f)

            # Check sequence metadata
            metadata = config_data["metadata"]
            assert metadata["sequence_index"] == i + 1
            assert metadata["sequence_total"] == 3
            assert metadata["content"] == long_content

    def test_hash_naming_consistency(self, tmp_path):
        """Test that same configuration produces same hash."""
        qr = segno.make("Test")

        # Generate twice with same config
        config = {
            "scale": 10,
            "shape": "squircle",
            "corner_radius": 0.3,
            "dark": "#000000",
            "use_hash_naming": True,
        }

        result1 = write(qr, str(tmp_path / "test1.svg"), **config)
        result2 = write(qr, str(tmp_path / "test2.svg"), **config)

        # Should produce same hash
        assert result1["config_hash"] == result2["config_hash"]

        # Different config should produce different hash
        config["scale"] = 15
        result3 = write(qr, str(tmp_path / "test3.svg"), **config)
        assert result3["config_hash"] != result1["config_hash"]

    def test_yaml_format_fallback(self, tmp_path):
        """Test YAML format fallback to JSON."""
        qr = segno.make("Test", error="M")
        output_file = tmp_path / "test.svg"

        # Request YAML format (will fall back to JSON if PyYAML not installed)
        result = write(qr, str(output_file), scale=10, config_format="yaml", export_config=True)

        # Config file should exist
        config_file_path = Path(result["config_file"])
        assert config_file_path.exists()

        # Check that file has content
        assert config_file_path.stat().st_size > 0

        # Read content and check format
        with open(result["config_file"], "r") as f:
            content = f.read().strip()

        # Should have some content
        assert len(content) > 0

        # Try to parse as JSON first (fallback case)
        try:
            config_data = json.loads(content)
            assert "configuration" in config_data
            # JSON fallback worked
        except json.JSONDecodeError:
            # Might be actual YAML, try to parse basic structure
            assert "configuration:" in content or "segnomms_version:" in content
            # YAML format used (if PyYAML is available)

    def test_stream_output_no_config(self, tmp_path):
        """Test that stream output doesn't export config."""
        qr = segno.make("Test")
        output_file = tmp_path / "test.svg"

        # Write to stream
        with open(output_file, "w") as f:
            result = write(qr, f, scale=10, export_config=True)

        # Should return None for stream output
        assert result is None

        # SVG should exist but no config
        assert output_file.exists()
        config_file = output_file.parent / "test_config.json"
        assert not config_file.exists()

    def test_config_export_with_metadata(self, tmp_path):
        """Test configuration export with custom metadata."""
        qr = segno.make("Test")
        output_file = tmp_path / "test.svg"

        # Create config with metadata
        from segnomms.config import RenderingConfig

        # Note: This tests the internal structure
        # In practice, metadata would be set internally
        config = RenderingConfig(scale=10, metadata={"custom_field": "custom_value"})

        # The metadata field should be preserved
        assert config.metadata == {"custom_field": "custom_value"}

        # Export to JSON
        config_json = config.model_dump(exclude_none=True)
        assert "metadata" in config_json
        assert config_json["metadata"]["custom_field"] == "custom_value"


class TestConfigurationReproducibility:
    """Test using exported configurations for reproducibility."""

    def test_load_and_recreate(self, tmp_path):
        """Test loading configuration and recreating QR code."""
        qr = segno.make("Reproducible")

        # Generate original
        result = write(
            qr,
            str(tmp_path / "original.svg"),
            scale=15,
            shape="squircle",
            corner_radius=0.35,
            dark="#e74c3c",
            export_config=True,
        )

        # Load configuration
        with open(result["config_file"], "r") as f:
            saved_data = json.load(f)

        # Extract configuration
        config_dict = saved_data["configuration"]

        # Verify we can create RenderingConfig from loaded data
        config = RenderingConfig(**config_dict)

        # Check values match
        assert config.scale == 15
        assert config.geometry.shape == "squircle"
        assert config.geometry.corner_radius == 0.35
        assert config.dark == "#e74c3c"

    def test_batch_consistency(self, tmp_path):
        """Test batch generation with consistent naming."""
        configs = [
            {"shape": "square", "scale": 10},
            {"shape": "circle", "scale": 12},
            {"shape": "squircle", "scale": 15},
        ]

        hashes = []
        for i, cfg in enumerate(configs):
            qr = segno.make(f"Batch {i}")
            result = write(
                qr, str(tmp_path / f"batch_{i}.svg"), use_hash_naming=True, export_config=True, **cfg
            )
            hashes.append(result["config_hash"])

        # All hashes should be different
        assert len(set(hashes)) == len(hashes)

        # Regenerating with same config should produce same hash
        qr = segno.make("Batch 0")
        result = write(qr, str(tmp_path / "batch_0_copy.svg"), use_hash_naming=True, **configs[0])
        assert result["config_hash"] == hashes[0]
