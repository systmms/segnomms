"""
Comprehensive unit tests for advanced configuration models.

Tests AdvancedQRConfig, PerformanceConfig, and DebugConfig validation,
parameters, constraints, and complex integration scenarios.
"""

import pytest
from pydantic import ValidationError
from unittest.mock import patch
import logging

from segnomms.config import AdvancedQRConfig, PerformanceConfig, DebugConfig


class TestAdvancedQRConfig:
    """Test AdvancedQRConfig validation and functionality."""
    
    def test_default_advanced_qr_config(self):
        """Test default advanced QR configuration values."""
        config = AdvancedQRConfig()
        
        assert config.eci_enabled is False
        assert config.encoding is None
        assert config.mask_pattern is None
        assert config.auto_mask is True
        assert config.structured_append is False
        assert config.symbol_count is None
        assert config.boost_error is True

    def test_eci_configuration(self):
        """Test ECI mode configuration."""
        # ECI enabled with encoding
        config = AdvancedQRConfig(eci_enabled=True, encoding="UTF-8")
        assert config.eci_enabled is True
        assert config.encoding == "UTF-8"
        
        # ECI enabled without encoding (should default to UTF-8)
        config = AdvancedQRConfig(eci_enabled=True)
        assert config.eci_enabled is True
        assert config.encoding == "UTF-8"
        
        # Encoding without ECI (should log info)
        config = AdvancedQRConfig(encoding="ISO-8859-1")
        assert config.eci_enabled is False
        assert config.encoding == "ISO-8859-1"

    def test_comprehensive_encoding_support(self):
        """Test comprehensive encoding support validation."""
        # UTF encodings
        utf_encodings = ["UTF-8", "UTF-16", "UTF-32"]
        for encoding in utf_encodings:
            config = AdvancedQRConfig(encoding=encoding)
            assert config.encoding == encoding
        
        # ISO-8859 series
        iso_encodings = [
            "ISO-8859-1", "ISO-8859-2", "ISO-8859-3", "ISO-8859-4",
            "ISO-8859-5", "ISO-8859-6", "ISO-8859-7", "ISO-8859-8",
            "ISO-8859-9", "ISO-8859-10", "ISO-8859-11", "ISO-8859-13",
            "ISO-8859-14", "ISO-8859-15", "ISO-8859-16"
        ]
        for encoding in iso_encodings:
            config = AdvancedQRConfig(encoding=encoding)
            assert config.encoding == encoding
        
        # Asian encodings
        asian_encodings = ["Shift_JIS", "CP932", "EUC-JP", "GB2312", "GBK", "GB18030", "BIG5"]
        for encoding in asian_encodings:
            config = AdvancedQRConfig(encoding=encoding)
            assert config.encoding == encoding
        
        # Other common encodings
        other_encodings = ["CP1252", "ASCII"]
        for encoding in other_encodings:
            config = AdvancedQRConfig(encoding=encoding)
            assert config.encoding == encoding

    def test_encoding_normalization(self):
        """Test encoding name normalization."""
        # Case variations should work
        config = AdvancedQRConfig(encoding="utf-8")
        assert config.encoding == "utf-8"
        
        config = AdvancedQRConfig(encoding="iso-8859-1")
        assert config.encoding == "iso-8859-1"
        
        # With spaces and hyphens
        config = AdvancedQRConfig(encoding="Shift JIS")
        assert config.encoding == "Shift JIS"

    def test_encoding_warning_for_unsupported(self):
        """Test warning for potentially unsupported encodings."""
        with patch('segnomms.config.models.advanced.logger') as mock_logger:
            config = AdvancedQRConfig(encoding="UNKNOWN-ENCODING")
            assert config.encoding == "UNKNOWN-ENCODING"
            
            # Should have logged a warning
            mock_logger.warning.assert_called_once()
            warning_message = mock_logger.warning.call_args[0][0]
            assert "UNKNOWN-ENCODING" in warning_message
            assert "may not be supported" in warning_message

    def test_mask_pattern_validation(self):
        """Test mask pattern validation and constraints."""
        # Valid mask patterns (0-7 for QR codes)
        valid_patterns = [0, 1, 2, 3, 4, 5, 6, 7]
        for pattern in valid_patterns:
            config = AdvancedQRConfig(mask_pattern=pattern)
            assert config.mask_pattern == pattern
            assert config.auto_mask is False  # Should be disabled automatically
        
        # Invalid mask patterns
        invalid_patterns = [-1, 8, 10, 100]
        for pattern in invalid_patterns:
            with pytest.raises(ValidationError) as exc_info:
                AdvancedQRConfig(mask_pattern=pattern)
            assert "mask_pattern" in str(exc_info.value).lower()
        
        # Auto mask by default
        config = AdvancedQRConfig()
        assert config.auto_mask is True
        assert config.mask_pattern is None

    def test_mask_pattern_auto_mask_consistency(self):
        """Test mask pattern and auto_mask consistency validation."""
        # Manual mask pattern disables auto_mask
        config = AdvancedQRConfig(mask_pattern=3, auto_mask=True)
        assert config.mask_pattern == 3
        assert config.auto_mask is False  # Should be overridden
        
        # No mask pattern keeps auto_mask enabled
        config = AdvancedQRConfig(auto_mask=True)
        assert config.mask_pattern is None
        assert config.auto_mask is True

    def test_structured_append_configuration(self):
        """Test structured append configuration."""
        # Structured append enabled (should default symbol_count to 2)
        config = AdvancedQRConfig(structured_append=True)
        assert config.structured_append is True
        assert config.symbol_count == 2
        
        # Structured append with explicit symbol count
        config = AdvancedQRConfig(structured_append=True, symbol_count=4)
        assert config.structured_append is True
        assert config.symbol_count == 4
        
        # Symbol count without structured append (should warn)
        with patch('segnomms.config.models.advanced.logger') as mock_logger:
            config = AdvancedQRConfig(symbol_count=3)
            assert config.structured_append is False
            assert config.symbol_count == 3
            
            # Should have logged a warning
            mock_logger.warning.assert_called_once()

    def test_symbol_count_validation(self):
        """Test symbol count validation constraints."""
        # Valid symbol counts (2-16)
        valid_counts = [2, 3, 5, 8, 12, 16]
        for count in valid_counts:
            config = AdvancedQRConfig(structured_append=True, symbol_count=count)
            assert config.symbol_count == count
        
        # Invalid symbol counts
        invalid_counts = [0, 1, 17, 20, 100]
        for count in invalid_counts:
            with pytest.raises(ValidationError) as exc_info:
                AdvancedQRConfig(symbol_count=count)
            assert "symbol_count" in str(exc_info.value).lower()

    def test_eci_encoding_consistency_validation(self):
        """Test ECI and encoding consistency validation."""
        # ECI enabled without encoding (should default to UTF-8)
        config = AdvancedQRConfig(eci_enabled=True)
        assert config.eci_enabled is True
        assert config.encoding == "UTF-8"
        
        # Encoding specified without ECI (should log info)
        with patch('segnomms.config.models.advanced.logger') as mock_logger:
            config = AdvancedQRConfig(encoding="ISO-8859-1")
            assert config.eci_enabled is False
            assert config.encoding == "ISO-8859-1"
            
            # Should have logged an info message
            mock_logger.info.assert_called_once()
            info_message = mock_logger.info.call_args[0][0]
            assert "ISO-8859-1" in info_message
            assert "without ECI" in info_message

    def test_complex_advanced_qr_configuration(self):
        """Test complex advanced QR configuration."""
        config = AdvancedQRConfig(
            eci_enabled=True,
            encoding="UTF-8",
            mask_pattern=5,
            structured_append=True,
            symbol_count=8,
            boost_error=False
        )
        
        assert config.eci_enabled is True
        assert config.encoding == "UTF-8"
        assert config.mask_pattern == 5
        assert config.auto_mask is False  # Should be disabled
        assert config.structured_append is True
        assert config.symbol_count == 8
        assert config.boost_error is False

    def test_international_encoding_scenarios(self):
        """Test international encoding scenarios."""
        # Japanese with Shift_JIS
        config = AdvancedQRConfig(eci_enabled=True, encoding="Shift_JIS")
        assert config.encoding == "Shift_JIS"
        
        # Chinese with GB18030
        config = AdvancedQRConfig(eci_enabled=True, encoding="GB18030")
        assert config.encoding == "GB18030"
        
        # European with ISO-8859-15
        config = AdvancedQRConfig(eci_enabled=True, encoding="ISO-8859-15")
        assert config.encoding == "ISO-8859-15"

    def test_boundary_values_advanced_qr(self):
        """Test boundary values for advanced QR configuration."""
        # Minimum mask pattern
        config = AdvancedQRConfig(mask_pattern=0)
        assert config.mask_pattern == 0
        
        # Maximum mask pattern
        config = AdvancedQRConfig(mask_pattern=7)
        assert config.mask_pattern == 7
        
        # Minimum symbol count
        config = AdvancedQRConfig(structured_append=True, symbol_count=2)
        assert config.symbol_count == 2
        
        # Maximum symbol count
        config = AdvancedQRConfig(structured_append=True, symbol_count=16)
        assert config.symbol_count == 16

    def test_extra_fields_forbidden_advanced_qr(self):
        """Test that extra fields are forbidden in AdvancedQRConfig."""
        with pytest.raises(ValidationError) as exc_info:
            AdvancedQRConfig(invalid_field="value")
        assert "Extra inputs are not permitted" in str(exc_info.value)


class TestPerformanceConfig:
    """Test PerformanceConfig validation and functionality."""

    def test_default_performance_config(self):
        """Test default performance configuration."""
        config = PerformanceConfig()
        
        assert config.enable_caching is True
        assert config.max_cache_size == 100
        assert config.enable_parallel_processing is False
        assert config.memory_limit_mb is None
        assert config.debug_timing is False

    def test_caching_configuration(self):
        """Test caching configuration options."""
        # Caching enabled with custom cache size
        config = PerformanceConfig(enable_caching=True, max_cache_size=500)
        assert config.enable_caching is True
        assert config.max_cache_size == 500
        
        # Caching disabled
        config = PerformanceConfig(enable_caching=False)
        assert config.enable_caching is False
        assert config.max_cache_size == 100  # Default value preserved

    def test_max_cache_size_validation(self):
        """Test max_cache_size validation constraints."""
        # Valid cache sizes
        valid_sizes = [1, 10, 100, 1000, 10000]
        for size in valid_sizes:
            config = PerformanceConfig(max_cache_size=size)
            assert config.max_cache_size == size
        
        # Invalid cache sizes
        invalid_sizes = [0, -1, -100]
        for size in invalid_sizes:
            with pytest.raises(ValidationError) as exc_info:
                PerformanceConfig(max_cache_size=size)
            assert "max_cache_size" in str(exc_info.value).lower()

    def test_parallel_processing_configuration(self):
        """Test parallel processing configuration."""
        # Parallel processing enabled
        config = PerformanceConfig(enable_parallel_processing=True)
        assert config.enable_parallel_processing is True
        
        # Parallel processing disabled (default)
        config = PerformanceConfig()
        assert config.enable_parallel_processing is False

    def test_memory_limit_validation(self):
        """Test memory_limit_mb validation."""
        # Valid memory limits
        valid_limits = [1, 256, 1024, 4096, 16384]
        for limit in valid_limits:
            config = PerformanceConfig(memory_limit_mb=limit)
            assert config.memory_limit_mb == limit
        
        # Invalid memory limits
        invalid_limits = [0, -1, -512]
        for limit in invalid_limits:
            with pytest.raises(ValidationError) as exc_info:
                PerformanceConfig(memory_limit_mb=limit)
            assert "memory_limit_mb" in str(exc_info.value).lower()
        
        # None is valid (no limit)
        config = PerformanceConfig(memory_limit_mb=None)
        assert config.memory_limit_mb is None

    def test_debug_timing_configuration(self):
        """Test debug timing configuration."""
        # Debug timing enabled
        config = PerformanceConfig(debug_timing=True)
        assert config.debug_timing is True
        
        # Debug timing disabled (default)
        config = PerformanceConfig()
        assert config.debug_timing is False

    def test_comprehensive_performance_configuration(self):
        """Test comprehensive performance configuration."""
        config = PerformanceConfig(
            enable_caching=True,
            max_cache_size=2000,
            enable_parallel_processing=True,
            memory_limit_mb=8192,
            debug_timing=True
        )
        
        assert config.enable_caching is True
        assert config.max_cache_size == 2000
        assert config.enable_parallel_processing is True
        assert config.memory_limit_mb == 8192
        assert config.debug_timing is True

    def test_performance_optimization_scenarios(self):
        """Test different performance optimization scenarios."""
        # High-performance scenario
        high_perf = PerformanceConfig(
            enable_caching=True,
            max_cache_size=10000,
            enable_parallel_processing=True,
            memory_limit_mb=16384,
            debug_timing=False
        )
        assert high_perf.enable_caching is True
        assert high_perf.max_cache_size == 10000
        assert high_perf.enable_parallel_processing is True
        
        # Memory-constrained scenario
        low_mem = PerformanceConfig(
            enable_caching=True,
            max_cache_size=50,
            memory_limit_mb=512,
            enable_parallel_processing=False
        )
        assert low_mem.max_cache_size == 50
        assert low_mem.memory_limit_mb == 512
        assert low_mem.enable_parallel_processing is False
        
        # Debug scenario
        debug = PerformanceConfig(
            debug_timing=True,
            enable_caching=False
        )
        assert debug.debug_timing is True
        assert debug.enable_caching is False

    def test_boundary_values_performance(self):
        """Test boundary values for performance configuration."""
        # Minimum cache size
        config = PerformanceConfig(max_cache_size=1)
        assert config.max_cache_size == 1
        
        # Minimum memory limit
        config = PerformanceConfig(memory_limit_mb=1)
        assert config.memory_limit_mb == 1

    def test_extra_fields_forbidden_performance(self):
        """Test that extra fields are forbidden in PerformanceConfig."""
        with pytest.raises(ValidationError) as exc_info:
            PerformanceConfig(invalid_field="value")
        assert "Extra inputs are not permitted" in str(exc_info.value)


class TestDebugConfig:
    """Test DebugConfig validation and functionality."""

    def test_default_debug_config(self):
        """Test default debug configuration."""
        config = DebugConfig()
        
        assert config.debug_mode is False
        assert config.debug_stroke is False
        assert config.save_intermediate_results is False
        assert config.verbose_logging is False
        
        # Check default debug colors
        expected_colors = {
            "contour": "red",
            "cluster": "blue",
            "enhanced": "green",
        }
        assert config.debug_colors == expected_colors

    def test_debug_mode_configuration(self):
        """Test debug mode configuration."""
        # Debug mode enabled
        config = DebugConfig(debug_mode=True)
        assert config.debug_mode is True
        
        # Debug mode disabled (default)
        config = DebugConfig()
        assert config.debug_mode is False

    def test_debug_stroke_configuration(self):
        """Test debug stroke configuration."""
        # Debug stroke enabled
        config = DebugConfig(debug_stroke=True)
        assert config.debug_stroke is True
        
        # Debug stroke disabled (default)
        config = DebugConfig()
        assert config.debug_stroke is False

    def test_debug_colors_customization(self):
        """Test debug colors customization."""
        custom_colors = {
            "contour": "#e74c3c",
            "cluster": "#3498db",
            "enhanced": "#2ecc71",
            "custom_element": "#9b59b6",
        }
        
        config = DebugConfig(debug_colors=custom_colors)
        assert config.debug_colors == custom_colors

    def test_debug_colors_partial_override(self):
        """Test partial debug colors override."""
        partial_colors = {
            "contour": "orange",
            "custom": "purple",
        }
        
        config = DebugConfig(debug_colors=partial_colors)
        assert config.debug_colors == partial_colors

    def test_debug_colors_with_hex_values(self):
        """Test debug colors with hex color values."""
        hex_colors = {
            "contour": "#ff0000",
            "cluster": "#0000ff",
            "enhanced": "#00ff00",
            "timing": "#ffff00",
            "finder": "#ff00ff",
        }
        
        config = DebugConfig(debug_colors=hex_colors)
        assert config.debug_colors == hex_colors

    def test_save_intermediate_results_configuration(self):
        """Test save intermediate results configuration."""
        # Save intermediate results enabled
        config = DebugConfig(save_intermediate_results=True)
        assert config.save_intermediate_results is True
        
        # Save intermediate results disabled (default)
        config = DebugConfig()
        assert config.save_intermediate_results is False

    def test_verbose_logging_configuration(self):
        """Test verbose logging configuration."""
        # Verbose logging enabled
        config = DebugConfig(verbose_logging=True)
        assert config.verbose_logging is True
        
        # Verbose logging disabled (default)
        config = DebugConfig()
        assert config.verbose_logging is False

    def test_comprehensive_debug_configuration(self):
        """Test comprehensive debug configuration."""
        custom_colors = {
            "contour": "#e74c3c",
            "cluster": "#3498db",
            "enhanced": "#2ecc71",
            "timing": "#f39c12",
            "finder": "#9b59b6",
            "alignment": "#e67e22",
        }
        
        config = DebugConfig(
            debug_mode=True,
            debug_stroke=True,
            debug_colors=custom_colors,
            save_intermediate_results=True,
            verbose_logging=True
        )
        
        assert config.debug_mode is True
        assert config.debug_stroke is True
        assert config.debug_colors == custom_colors
        assert config.save_intermediate_results is True
        assert config.verbose_logging is True

    def test_debug_development_scenarios(self):
        """Test different debug and development scenarios."""
        # Development scenario
        dev_config = DebugConfig(
            debug_mode=True,
            verbose_logging=True,
            save_intermediate_results=True
        )
        assert dev_config.debug_mode is True
        assert dev_config.verbose_logging is True
        assert dev_config.save_intermediate_results is True
        
        # Visual debugging scenario
        visual_config = DebugConfig(
            debug_mode=True,
            debug_stroke=True,
            debug_colors={
                "contour": "red",
                "cluster": "blue",
                "enhanced": "green",
                "highlight": "yellow",
            }
        )
        assert visual_config.debug_mode is True
        assert visual_config.debug_stroke is True
        assert "highlight" in visual_config.debug_colors
        
        # Production debugging scenario (minimal)
        prod_config = DebugConfig(
            debug_mode=False,
            verbose_logging=False,
            save_intermediate_results=False
        )
        assert prod_config.debug_mode is False
        assert prod_config.verbose_logging is False
        assert prod_config.save_intermediate_results is False

    def test_debug_colors_named_colors(self):
        """Test debug colors with named color values."""
        named_colors = {
            "contour": "red",
            "cluster": "blue",
            "enhanced": "green",
            "timing": "yellow",
            "finder": "magenta",
            "alignment": "cyan",
            "data": "orange",
        }
        
        config = DebugConfig(debug_colors=named_colors)
        assert config.debug_colors == named_colors

    def test_debug_colors_rgb_values(self):
        """Test debug colors with RGB color values."""
        rgb_colors = {
            "contour": "rgb(255, 0, 0)",
            "cluster": "rgb(0, 0, 255)",
            "enhanced": "rgb(0, 255, 0)",
        }
        
        config = DebugConfig(debug_colors=rgb_colors)
        assert config.debug_colors == rgb_colors

    def test_empty_debug_colors(self):
        """Test empty debug colors configuration."""
        config = DebugConfig(debug_colors={})
        assert config.debug_colors == {}

    def test_extra_fields_forbidden_debug(self):
        """Test that extra fields are forbidden in DebugConfig."""
        with pytest.raises(ValidationError) as exc_info:
            DebugConfig(invalid_field="value")
        assert "Extra inputs are not permitted" in str(exc_info.value)


class TestAdvancedConfigIntegration:
    """Test integration between advanced configuration models."""

    def test_coordinated_advanced_configuration(self):
        """Test coordinated advanced configuration across models."""
        # High-performance configuration with debugging
        advanced_qr = AdvancedQRConfig(
            eci_enabled=True,
            encoding="UTF-8",
            mask_pattern=None,  # Auto-optimized
            auto_mask=True
        )
        
        performance = PerformanceConfig(
            enable_caching=True,
            max_cache_size=5000,
            enable_parallel_processing=True,
            memory_limit_mb=8192,
            debug_timing=True
        )
        
        debug = DebugConfig(
            debug_mode=False,  # Production mode
            verbose_logging=False,
            save_intermediate_results=False
        )
        
        assert advanced_qr.eci_enabled is True
        assert advanced_qr.auto_mask is True
        assert performance.enable_parallel_processing is True
        assert performance.debug_timing is True
        assert debug.debug_mode is False

    def test_development_configuration_scenario(self):
        """Test development-focused configuration scenario."""
        # Development with extensive debugging
        advanced_qr = AdvancedQRConfig(
            eci_enabled=True,
            encoding="UTF-8",
            structured_append=False,
            mask_pattern=None  # Let auto-mask optimize
        )
        
        performance = PerformanceConfig(
            enable_caching=False,  # Disable for consistent results
            debug_timing=True,
            memory_limit_mb=1024  # Conservative limit
        )
        
        debug = DebugConfig(
            debug_mode=True,
            debug_stroke=True,
            verbose_logging=True,
            save_intermediate_results=True,
            debug_colors={
                "contour": "#e74c3c",
                "cluster": "#3498db",
                "enhanced": "#2ecc71",
                "timing": "#f39c12",
            }
        )
        
        assert advanced_qr.encoding == "UTF-8"
        assert performance.enable_caching is False
        assert performance.debug_timing is True
        assert debug.debug_mode is True
        assert debug.verbose_logging is True

    def test_production_configuration_scenario(self):
        """Test production-optimized configuration scenario."""
        # Production with maximum performance
        advanced_qr = AdvancedQRConfig(
            eci_enabled=False,  # Broader compatibility
            auto_mask=True,  # Optimize automatically
            structured_append=False,
            boost_error=True
        )
        
        performance = PerformanceConfig(
            enable_caching=True,
            max_cache_size=10000,
            enable_parallel_processing=True,
            memory_limit_mb=16384,
            debug_timing=False
        )
        
        debug = DebugConfig(
            debug_mode=False,
            debug_stroke=False,
            verbose_logging=False,
            save_intermediate_results=False
        )
        
        assert advanced_qr.eci_enabled is False
        assert performance.enable_caching is True
        assert performance.max_cache_size == 10000
        assert debug.debug_mode is False

    def test_memory_constrained_scenario(self):
        """Test memory-constrained configuration scenario."""
        performance = PerformanceConfig(
            enable_caching=True,
            max_cache_size=25,  # Small cache
            enable_parallel_processing=False,  # Single-threaded
            memory_limit_mb=256,  # Limited memory
            debug_timing=False
        )
        
        debug = DebugConfig(
            debug_mode=False,
            save_intermediate_results=False,  # Save memory
            verbose_logging=False
        )
        
        assert performance.max_cache_size == 25
        assert performance.enable_parallel_processing is False
        assert performance.memory_limit_mb == 256
        assert debug.save_intermediate_results is False

    def test_international_qr_scenario(self):
        """Test international QR code generation scenario."""
        # Multi-symbol international QR codes
        advanced_qr = AdvancedQRConfig(
            eci_enabled=True,
            encoding="UTF-8",
            structured_append=True,
            symbol_count=4,
            boost_error=True,  # Better error correction for international use
            auto_mask=True
        )
        
        performance = PerformanceConfig(
            enable_caching=True,
            max_cache_size=1000,  # Moderate cache
            enable_parallel_processing=True,  # Speed up multi-symbol generation
            debug_timing=False
        )
        
        assert advanced_qr.eci_enabled is True
        assert advanced_qr.encoding == "UTF-8"
        assert advanced_qr.structured_append is True
        assert advanced_qr.symbol_count == 4
        assert performance.enable_parallel_processing is True


class TestAdvancedConfigEdgeCases:
    """Test edge cases and boundary conditions for advanced configurations."""

    def test_extreme_performance_values(self):
        """Test extreme performance configuration values."""
        # Very large cache
        config = PerformanceConfig(max_cache_size=1000000)
        assert config.max_cache_size == 1000000
        
        # Very large memory limit
        config = PerformanceConfig(memory_limit_mb=65536)  # 64 GB
        assert config.memory_limit_mb == 65536

    def test_debug_colors_edge_cases(self):
        """Test debug colors edge cases."""
        # Very long color names/values
        long_colors = {
            "very_long_component_name_with_underscores": "#123456",
            "contour": "rgba(255, 0, 0, 0.8)",
        }
        
        config = DebugConfig(debug_colors=long_colors)
        assert config.debug_colors == long_colors
        
        # Single color
        config = DebugConfig(debug_colors={"single": "red"})
        assert config.debug_colors == {"single": "red"}

    def test_structured_append_edge_cases(self):
        """Test structured append edge cases."""
        # Maximum symbol count
        config = AdvancedQRConfig(structured_append=True, symbol_count=16)
        assert config.symbol_count == 16
        
        # Minimum symbol count
        config = AdvancedQRConfig(structured_append=True, symbol_count=2)
        assert config.symbol_count == 2

    def test_type_coercion_advanced_configs(self):
        """Test type coercion for advanced configurations."""
        # Integer to boolean coercion works in Pydantic
        config = AdvancedQRConfig(eci_enabled=1)
        assert config.eci_enabled is True
        
        config = AdvancedQRConfig(eci_enabled=0)
        assert config.eci_enabled is False
        
        # String to int coercion for numeric fields
        config = PerformanceConfig(max_cache_size="500")
        assert config.max_cache_size == 500
        assert isinstance(config.max_cache_size, int)

    def test_none_value_handling_advanced(self):
        """Test handling of None values in advanced configurations."""
        # None allowed for optional fields
        config = AdvancedQRConfig(encoding=None, mask_pattern=None, symbol_count=None)
        assert config.encoding is None
        assert config.mask_pattern is None
        assert config.symbol_count is None
        
        # None allowed for optional performance fields
        config = PerformanceConfig(memory_limit_mb=None)
        assert config.memory_limit_mb is None
        
        # None not allowed for required fields
        with pytest.raises(ValidationError):
            PerformanceConfig(enable_caching=None)


class TestAdvancedConfigValidationMessages:
    """Test quality of validation error messages for advanced configurations."""

    def test_advanced_qr_validation_error_messages(self):
        """Test AdvancedQRConfig validation error message quality."""
        # Test mask_pattern validation error
        with pytest.raises(ValidationError) as exc_info:
            AdvancedQRConfig(mask_pattern=10)
        
        error_message = str(exc_info.value)
        assert "mask_pattern" in error_message.lower()
        assert "7" in error_message  # Maximum value mentioned
        
        # Test symbol_count validation error
        with pytest.raises(ValidationError) as exc_info:
            AdvancedQRConfig(symbol_count=20)
        
        error_message = str(exc_info.value)
        assert "symbol_count" in error_message.lower()

    def test_performance_validation_error_messages(self):
        """Test PerformanceConfig validation error message quality."""
        # Test max_cache_size validation error
        with pytest.raises(ValidationError) as exc_info:
            PerformanceConfig(max_cache_size=0)
        
        error_message = str(exc_info.value)
        assert "max_cache_size" in error_message.lower()
        assert "greater" in error_message.lower()

    def test_multiple_validation_errors_advanced(self):
        """Test handling of multiple validation errors in advanced configs."""
        with pytest.raises(ValidationError) as exc_info:
            AdvancedQRConfig(
                mask_pattern=10,  # Invalid: > 7
                symbol_count=20  # Invalid: > 16
            )
        
        error_message = str(exc_info.value)
        # Should contain information about multiple fields
        assert "mask_pattern" in error_message.lower()
        assert "symbol_count" in error_message.lower()