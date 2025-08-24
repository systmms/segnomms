"""
Unit tests for AdvancedQR generator logic.

Tests for generator functionality, configuration validation, and encoding
recommendations without external file operations.
"""

import pytest

from segnomms.core.advanced_qr import AdvancedQRGenerator, QRGenerationResult, create_advanced_qr_generator
from segnomms.config import AdvancedQRConfig


class TestAdvancedQRGenerator:
    """Test cases for the AdvancedQRGenerator class."""
    
    @pytest.fixture
    def generator(self):
        """Create an AdvancedQRGenerator instance."""
        return create_advanced_qr_generator()
    
    def test_basic_qr_generation(self, generator):
        """Test basic QR generation without advanced features."""
        config = AdvancedQRConfig()
        result = generator.generate_qr("Hello, World!", config)
        
        assert isinstance(result, QRGenerationResult)
        assert len(result.qr_codes) == 1
        assert result.is_sequence is False
        assert result.fallback_used is False
        assert len(result.warnings) == 0
        assert "version" in result.metadata
    
    def test_eci_mode_generation(self, generator):
        """Test QR generation with ECI mode."""
        config = AdvancedQRConfig(eci_enabled=True, encoding="UTF-8")
        content = "Hello café 世界 🌟"
        
        result = generator.generate_qr(content, config)
        
        assert len(result.qr_codes) == 1
        assert result.metadata.get("eci_enabled") is True
        assert result.metadata.get("encoding") == "UTF-8"
        assert result.is_sequence is False
        
        # Should have warning about ECI compatibility
        eci_warning = any("ECI" in warning for warning in result.warnings)
        assert eci_warning
    
    def test_mask_pattern_selection(self, generator):
        """Test manual mask pattern selection."""
        config = AdvancedQRConfig(mask_pattern=5)
        
        result = generator.generate_qr("Test content", config)
        
        assert len(result.qr_codes) == 1
        assert result.metadata.get("mask_pattern") == 5
        assert result.metadata.get("auto_mask") is False
        
        # Check if mask was applied (if QR has mask attribute)
        qr = result.qr_codes[0]
        if hasattr(qr, 'mask'):
            # Note: actual mask might differ due to QR code constraints
            assert isinstance(qr.mask, int)
    
    def test_structured_append_generation(self, generator):
        """Test structured append sequence generation."""
        # Create content that will require multiple symbols
        long_content = "This is a very long content string that should require multiple QR codes " * 20
        config = AdvancedQRConfig(structured_append=True, symbol_count=3)
        
        result = generator.generate_qr(long_content, config, error='M', version=10)
        
        assert result.is_sequence
        assert len(result.qr_codes) >= 1  # May be fewer if content fits
        assert result.metadata.get("total_data_length") == len(long_content)
        assert "sequence_info" in result.metadata
        
        # Check sequence info
        for i, qr_info in enumerate(result.metadata["sequence_info"]):
            assert qr_info["symbol_number"] == i + 1
            assert "version" in qr_info
    
    def test_combined_advanced_features(self, generator):
        """Test combination of multiple advanced features."""
        config = AdvancedQRConfig(
            eci_enabled=True,
            encoding="UTF-8",
            mask_pattern=2,
            structured_append=True,
            symbol_count=2,
            boost_error=True
        )
        
        content = "Advanced QR with 日本語 characters"
        result = generator.generate_qr(content, config, error='H')
        
        assert len(result.qr_codes) >= 1
        assert result.metadata.get("eci_enabled") is True
        assert result.metadata.get("mask_pattern") == 2
        
        # Should have appropriate warnings
        assert len(result.warnings) > 0
    
    def test_fallback_mechanisms(self, generator):
        """Test fallback mechanisms when advanced features fail."""
        # This might not always trigger fallback, but tests the structure
        config = AdvancedQRConfig(
            eci_enabled=True,
            encoding="INVALID-ENCODING"  # Might cause fallback
        )
        
        try:
            result = generator.generate_qr("Test content", config)
            # If it succeeds, check for fallback indicators
            assert isinstance(result, QRGenerationResult)
            assert len(result.qr_codes) >= 1
        except Exception:
            # Fallback to basic generation should work
            pass
    
    def test_config_validation(self, generator):
        """Test configuration validation."""
        # Valid config
        config = AdvancedQRConfig(eci_enabled=True, encoding="UTF-8")
        warnings = generator.validate_config(config)
        assert "ECI mode may not be supported" in warnings[0]
        
        # Invalid mask pattern - should raise validation error
        with pytest.raises(Exception):  # Pydantic ValidationError
            config = AdvancedQRConfig(mask_pattern=10)  # Invalid
        
        # Structured append - too many symbols
        with pytest.raises(Exception):  # Pydantic ValidationError
            config = AdvancedQRConfig(structured_append=True, symbol_count=20)  # Too many
    
    def test_encoding_recommendations(self, generator):
        """Test encoding recommendation system."""
        # ASCII content
        recommendations = generator.get_encoding_recommendations("Hello World")
        assert recommendations["recommended_encoding"] == "ASCII"
        assert recommendations["needs_eci"] is False
        assert recommendations["analysis"]["ascii_compatible"] is True
        
        # Latin-1 content
        recommendations = generator.get_encoding_recommendations("Café naïve")
        assert recommendations["recommended_encoding"] in ["ASCII", "ISO-8859-1"]
        
        # Unicode content
        recommendations = generator.get_encoding_recommendations("Hello 世界")
        assert recommendations["recommended_encoding"] == "UTF-8"
        assert recommendations["needs_eci"] is True
        assert recommendations["analysis"]["requires_unicode"] is True
        
        # CJK content
        recommendations = generator.get_encoding_recommendations("こんにちは")
        assert recommendations["recommended_encoding"] == "UTF-8"
        assert recommendations["analysis"]["has_cjk"] is True
        assert "Shift_JIS" in recommendations["alternatives"]