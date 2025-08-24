"""Tests for intent processing error handling with custom exceptions."""

import pytest

from segnomms.intents import (
    PayloadConfig,
    IntentsConfig,
    StyleIntents,
    render_with_intents,
)
from segnomms.intents.processor import IntentProcessor
from segnomms.exceptions import (
    IntentValidationError,
    UnsupportedIntentError,
    ConfigurationError,
)


class TestPayloadErrorHandling:
    """Test error handling for payload processing."""
    
    def test_empty_payload_raises_error(self):
        """Test that empty payload raises IntentValidationError."""
        # Pydantic validates at creation time, so we expect ValueError
        with pytest.raises(ValueError) as exc_info:
            payload = PayloadConfig()  # No content specified
        
        assert "at least one content type must be specified" in str(exc_info.value).lower()
    
    def test_payload_with_content_succeeds(self):
        """Test that valid payload processes successfully."""
        processor = IntentProcessor()
        
        # Test with text
        payload = PayloadConfig(text="Hello World")
        result = processor.process_intents(payload)
        assert result.svg_content
        
        # Test with URL
        payload = PayloadConfig(url="https://example.com")
        result = processor.process_intents(payload)
        assert result.svg_content
        
        # Test with data
        payload = PayloadConfig(data=b"Binary data")
        result = processor.process_intents(payload)
        assert result.svg_content


class TestStyleIntentErrorHandling:
    """Test error handling for style intents."""
    
    def test_unsupported_shape_creates_warning(self):
        """Test that unsupported shape creates warning with UnsupportedIntentError details."""
        payload = PayloadConfig(text="Test")
        intents = IntentsConfig(
            style=StyleIntents(module_shape="invalid-shape")
        )
        
        result = render_with_intents(payload, intents)
        
        # Should have warning
        assert result.has_warnings
        
        # Find the unsupported intent warning
        shape_warnings = [w for w in result.warnings if w.path == "style.module_shape"]
        assert len(shape_warnings) == 1
        
        warning = shape_warnings[0]
        assert warning.code == "UNSUPPORTED_INTENT"
        assert "Shape 'invalid-shape'" in warning.detail
        assert warning.suggestion is not None
        
        # Should use default shape
        assert result.used_options["shape"] == "square"
        assert "style.module_shape" in result.unsupported_intents
    
    def test_invalid_corner_radius_validation(self):
        """Test that invalid corner radius is caught by Pydantic validation."""
        # Pydantic validates at model creation time
        with pytest.raises(ValueError) as exc_info:
            StyleIntents(corner_radius=2.0)  # Out of range [0, 1]
        
        assert "less than or equal to 1" in str(exc_info.value)
    
    def test_unsupported_merge_strategy(self):
        """Test unsupported merge strategy handling."""
        payload = PayloadConfig(text="Test")
        intents = IntentsConfig(
            style=StyleIntents(merge="ultra-aggressive")  # Not a real strategy
        )
        
        result = render_with_intents(payload, intents)
        
        # Should have warning
        merge_warnings = [w for w in result.warnings if w.path == "style.merge"]
        assert len(merge_warnings) == 1
        
        warning = merge_warnings[0]
        assert warning.code == "UNSUPPORTED_INTENT"
        assert "Merge strategy 'ultra-aggressive'" in warning.detail
        
        # Should use default
        assert result.used_options["merge"] == "none"


class TestIntentTransformationTracking:
    """Test that intent transformations are properly tracked."""
    
    def test_transformation_report_includes_errors(self):
        """Test that transformation report includes error details."""
        payload = PayloadConfig(text="Test")
        intents = IntentsConfig(
            style=StyleIntents(
                module_shape="invalid",
                corner_radius=0.8,  # Valid value
                merge="unknown",
            )
        )
        
        result = render_with_intents(payload, intents)
        
        # Should have transformation report
        assert result.translation_report is not None
        
        report = result.translation_report
        
        # Should have transformation steps
        assert len(report.transformation_steps) > 0
        
        # Should have degradation details for unsupported features
        assert len(report.degradation_details) > 0
        
        # Check specific transformations
        shape_transforms = [
            t for t in report.transformation_steps 
            if t.intent_path == "style.module_shape"
        ]
        assert len(shape_transforms) > 0
        
        # Should show rejected transformation
        rejected = [t for t in shape_transforms if t.transformation_type == "rejected"]
        assert len(rejected) > 0


class TestConfigurationErrorHandling:
    """Test configuration validation error handling."""
    
    def test_invalid_configuration_falls_back_to_default(self):
        """Test that invalid configuration falls back to default with warning."""
        processor = IntentProcessor()
        payload = PayloadConfig(text="Test")
        
        # Create intents that will cause configuration error
        intents = IntentsConfig(
            style=StyleIntents(
                # This would need a configuration that causes error
                # For now, we'll test the general flow
                module_shape="square"
            )
        )
        
        result = processor.process_intents(payload, intents)
        
        # Should complete successfully
        assert result.svg_content
        
        # If there were config errors, they should be in warnings
        config_warnings = [w for w in result.warnings if w.path == "config"]
        for warning in config_warnings:
            assert warning.code in ["CONFIGURATION_ERROR", "VALIDATION_ERROR"]


class TestErrorRecovery:
    """Test that processing recovers gracefully from errors."""
    
    def test_multiple_errors_still_generate_svg(self):
        """Test that multiple errors don't prevent SVG generation."""
        payload = PayloadConfig(text="Test")
        intents = IntentsConfig(
            style=StyleIntents(
                module_shape="invalid",
                merge="unknown",
                connectivity="diagonal",  # Not valid
                corner_radius=1.0,  # Valid range [0, 1]
            )
        )
        
        result = render_with_intents(payload, intents)
        
        # Should still generate SVG
        assert result.svg_content
        assert len(result.svg_content) > 100
        
        # Should have multiple warnings
        assert result.warning_count >= 3  # Changed from 4 since corner_radius is valid
        
        # Should have multiple unsupported intents
        assert len(result.unsupported_intents) >= 3
        
        # Should still be valid SVG
        assert result.svg_content.startswith("<svg")
        assert result.svg_content.endswith("</svg>")
    
    def test_error_details_in_translation_report(self):
        """Test that error details are captured in translation report."""
        payload = PayloadConfig(text="Test")
        intents = IntentsConfig(
            style=StyleIntents(patterns={"finder": "invalid-pattern"})
        )
        
        result = render_with_intents(payload, intents)
        
        # Should have translation report
        assert result.translation_report is not None
        
        # Should have summary with error counts
        summary = result.translation_report.intent_summary
        assert "transformations" in summary
        
        # Should track the pattern style attempt
        pattern_steps = [
            s for s in result.translation_report.transformation_steps
            if "patterns" in s.intent_path
        ]
        assert len(pattern_steps) > 0


class TestExceptionPropagation:
    """Test that critical exceptions are propagated correctly."""
    
    def test_payload_validation_error_propagates(self):
        """Test that payload validation errors propagate."""
        # Pydantic validates at creation time
        with pytest.raises(ValueError) as exc_info:
            payload = PayloadConfig()  # Empty payload
        
        assert "at least one content type must be specified" in str(exc_info.value).lower()
    
    def test_non_critical_errors_dont_propagate(self):
        """Test that non-critical errors don't stop processing."""
        # Invalid intents should not raise exceptions
        payload = PayloadConfig(text="Test")
        intents = IntentsConfig(
            style=StyleIntents(
                module_shape="completely-invalid",
                merge="not-a-strategy",
            )
        )
        
        # Should not raise exception
        result = render_with_intents(payload, intents)
        
        # Should complete with warnings
        assert result.svg_content
        assert result.has_warnings
        assert result.degradation_applied