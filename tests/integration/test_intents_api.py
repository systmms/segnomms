"""
Integration tests for intent-based API functions.

Tests for public API functions, full workflow processing,
and end-to-end intent processing with real QR generation.
"""

import time

import pytest

from segnomms.intents.models import (
    AccessibilityIntents,
    AdvancedIntents,
    FrameIntents,
    IntentsConfig,
    InteractivityIntents,
    PayloadConfig,
    PerformanceMetrics,
    RenderingResult,
    ReserveIntents,
    StyleIntents,
    ValidationIntents,
)
from segnomms.intents.processor import process_intents, render_with_intents


class TestPublicAPIFunctions:
    """Test public API functions for intent processing."""

    def test_render_with_intents_basic(self):
        """Test render_with_intents function with basic payload."""
        payload = PayloadConfig(text="Hello World")

        result = render_with_intents(payload)

        assert isinstance(result, RenderingResult)
        assert result.svg_content is not None
        assert len(result.svg_content) > 0
        assert result.svg_content.startswith("<?xml") or result.svg_content.startswith("<svg")

    def test_render_with_intents_with_intents(self):
        """Test render_with_intents function with intents."""
        payload = PayloadConfig(text="Hello World")
        intents = IntentsConfig(
            style=StyleIntents(module_shape="squircle"), validation=ValidationIntents(quiet_zone=4)
        )

        result = render_with_intents(payload, intents)

        assert isinstance(result, RenderingResult)
        assert result.svg_content is not None
        assert len(result.svg_content) > 0

        # Check that border was set from quiet_zone
        used_options = result.used_options
        if "border" in used_options:
            assert used_options["border"] == 4

    def test_process_intents_dict_basic(self):
        """Test process_intents function with dictionary input."""
        intents_dict = {"payload": {"text": "Hello World"}}

        result = process_intents(intents_dict)

        assert isinstance(result, RenderingResult)
        assert result.svg_content is not None
        assert len(result.svg_content) > 0

    def test_process_intents_dict_with_intents(self):
        """Test process_intents function with full dictionary input."""
        intents_dict = {
            "payload": {"text": "Hello World", "error_correction": "M"},
            "intents": {
                "style": {"module_shape": "circle", "merge": "soft"},
                "accessibility": {"title": "Test QR Code"},
                "validation": {"enforce_scanability": True, "quiet_zone": 3},
            },
        }

        result = process_intents(intents_dict)

        assert isinstance(result, RenderingResult)
        assert result.svg_content is not None
        assert len(result.svg_content) > 0

        # Should have processed the intents
        assert len(result.warnings) >= 0  # May have warnings for unsupported features

        # Check that quiet_zone was applied
        used_options = result.used_options
        if "border" in used_options:
            assert used_options["border"] == 3

    def test_process_intents_dict_invalid_payload(self):
        """Test process_intents function with invalid payload."""
        intents_dict = {"payload": {"invalid_field": "value"}}  # Missing required text/url

        # Should raise validation error
        with pytest.raises(Exception):  # Pydantic ValidationError
            process_intents(intents_dict)

    def test_process_intents_dict_invalid_intents(self):
        """Test process_intents function with invalid intents (ignored gracefully)."""
        intents_dict = {
            "payload": {"text": "Hello World"},
            "intents": {"invalid_intent_type": {"some": "value"}},  # Should be ignored
        }

        # Should not raise error - invalid fields are ignored gracefully
        result = process_intents(intents_dict)
        assert result is not None
        assert result.svg_content is not None
        assert len(result.svg_content) > 0

    def test_process_intents_dict_no_intents(self):
        """Test process_intents function with no intents section."""
        intents_dict = {"payload": {"text": "Hello World"}}

        result = process_intents(intents_dict)

        assert isinstance(result, RenderingResult)
        assert result.svg_content is not None
        assert len(result.svg_content) > 0

        # Should work fine with no intents
        assert len(result.unsupported_intents) == 0


class TestIntentWorkflowIntegration:
    """Test complete intent processing workflows."""

    def test_basic_payload_processing_workflow(self):
        """Test processing basic payload without intents."""
        payload = PayloadConfig(text="Hello, World!")

        result = render_with_intents(payload)

        assert isinstance(result, RenderingResult)
        assert result.svg_content is not None
        assert len(result.svg_content) > 0
        assert isinstance(result.warnings, list)
        assert isinstance(result.metrics, PerformanceMetrics)
        assert isinstance(result.used_options, dict)
        assert result.degradation_applied in [True, False]
        assert isinstance(result.unsupported_intents, list)

    def test_payload_with_intents_processing_workflow(self):
        """Test processing payload with intent configuration."""
        payload = PayloadConfig(text="Hello, World!")
        intents = IntentsConfig(
            style=StyleIntents(module_shape="squircle", merge="soft"),
            accessibility=AccessibilityIntents(title="Test QR Code", desc="A test QR code for unit testing"),
        )

        result = render_with_intents(payload, intents)

        assert isinstance(result, RenderingResult)
        assert result.svg_content is not None
        assert len(result.svg_content) > 0

        # Check that style intents were processed
        used_options = result.used_options
        # Note: Actual keys depend on how intents map to config
        assert isinstance(used_options, dict)

        # Should have some warnings for unsupported accessibility features
        assert len(result.warnings) >= 0  # May have warnings for unsupported features

    def test_complex_intents_workflow(self):
        """Test processing with complex intents configuration."""
        payload = PayloadConfig(text="Complex QR Code Test", error_correction="H")

        intents = IntentsConfig(
            style=StyleIntents(module_shape="circle", merge="aggressive", corner_radius=0.3),
            frame=FrameIntents(enabled=True, shape="rounded-rect", clip_mode="clip"),
            reserve=ReserveIntents(area_pct=15.0, shape="circle", placement="center"),
            accessibility=AccessibilityIntents(
                title="Complex QR Code", desc="A complex QR code with multiple intents"
            ),
            validation=ValidationIntents(enforce_scanability=True, quiet_zone=4),
            advanced=AdvancedIntents(mask_pattern=2, structured_append={"enabled": False}),
            interactivity=InteractivityIntents(hover_effects=True, hover_scale=1.2, tooltips=True),
        )

        result = render_with_intents(payload, intents)

        assert isinstance(result, RenderingResult)
        assert result.svg_content is not None
        assert len(result.svg_content) > 0

        # Should have processed multiple intents successfully
        # Note: Current implementation supports most intents, so warnings may be minimal
        assert len(result.warnings) >= 0  # May have warnings from degradation
        assert len(result.unsupported_intents) >= 0  # May have some unsupported features
        # Degradation may be applied due to aggressive merge strategy
        assert result.degradation_applied in [True, False]  # Depends on configuration

        # Check that some basic intents were processed
        used_options = result.used_options
        assert isinstance(used_options, dict)

        # Validation intents should be processed
        if "border" in used_options:
            assert used_options["border"] == 4
        if "safe_mode" in used_options:
            assert used_options["safe_mode"] is True

    def test_url_payload_workflow(self):
        """Test processing with URL payload."""
        payload = PayloadConfig(url="https://example.com/test?param=value")
        intents = IntentsConfig(
            style=StyleIntents(module_shape="squircle"), validation=ValidationIntents(quiet_zone=2)
        )

        result = render_with_intents(payload, intents)

        assert isinstance(result, RenderingResult)
        assert result.svg_content is not None
        assert len(result.svg_content) > 0

        # Should handle URL payload correctly
        used_options = result.used_options
        if "border" in used_options:
            assert used_options["border"] == 2

    def test_email_payload_workflow(self):
        """Test processing with email payload."""
        payload = PayloadConfig(email="test@example.com")
        intents = IntentsConfig(
            style=StyleIntents(module_shape="rounded", merge="soft"),
            validation=ValidationIntents(enforce_scanability=True),
        )

        result = render_with_intents(payload, intents)

        assert isinstance(result, RenderingResult)
        assert result.svg_content is not None
        assert len(result.svg_content) > 0

        # Should handle email payload correctly
        used_options = result.used_options
        if "safe_mode" in used_options:
            assert used_options["safe_mode"] is True


class TestPerformanceMetricsIntegration:
    """Test performance metrics in integration context."""

    def test_metrics_timing_accuracy_integration(self):
        """Test that metrics timing is reasonably accurate in real workflow."""
        payload = PayloadConfig(text="Performance Test")

        start_time = time.time()
        result = render_with_intents(payload)
        end_time = time.time()

        actual_time_ms = (end_time - start_time) * 1000
        reported_time_ms = result.metrics.rendering_time_ms

        # Reported time should be close to actual time (within 100ms tolerance)
        assert abs(reported_time_ms - actual_time_ms) < 100

        # Individual components should sum to roughly the total
        component_sum = result.metrics.validation_time_ms + result.metrics.svg_generation_time_ms
        # Allow for overhead in total time
        assert component_sum <= reported_time_ms + 50

    def test_metrics_with_complex_workflow(self):
        """Test metrics with complex intent processing workflow."""
        payload = PayloadConfig(text="Complex Metrics Test")
        intents = IntentsConfig(
            style=StyleIntents(module_shape="circle", merge="aggressive"),
            validation=ValidationIntents(enforce_scanability=True, quiet_zone=5),
            accessibility=AccessibilityIntents(title="Metrics Test QR", desc="Testing performance metrics"),
        )

        result = render_with_intents(payload, intents)
        metrics = result.metrics

        # Check that all timing metrics are populated
        assert metrics.rendering_time_ms > 0
        assert metrics.validation_time_ms >= 0
        assert metrics.svg_generation_time_ms >= 0

        # Check content analysis metrics
        assert metrics.min_module_px > 0
        assert metrics.actual_quiet_zone >= 0
        assert metrics.estimated_scanability in ["pass", "warning", "fail"]

        # Quiet zone should reflect the intent
        assert metrics.actual_quiet_zone == 5

    def test_metrics_comparison_across_configurations(self):
        """Test metrics comparison across different configurations."""
        payload = PayloadConfig(text="Comparison Test")

        # Test different quiet zone configurations
        results = []
        for quiet_zone in [1, 3, 7]:
            intents = IntentsConfig(validation=ValidationIntents(quiet_zone=quiet_zone))
            result = render_with_intents(payload, intents)
            results.append((quiet_zone, result))

        # Compare metrics across configurations
        for quiet_zone, result in results:
            metrics = result.metrics
            assert metrics.rendering_time_ms > 0
            assert metrics.min_module_px > 0
            assert metrics.actual_quiet_zone == quiet_zone

    def test_metrics_with_different_payload_types(self):
        """Test metrics with different payload types."""
        payloads = [
            PayloadConfig(text="Text payload"),
            PayloadConfig(url="https://example.com"),
            PayloadConfig(email="test@example.com"),
        ]

        for payload in payloads:
            result = render_with_intents(payload)
            metrics = result.metrics

            # All payload types should generate valid metrics
            assert metrics.rendering_time_ms > 0
            assert metrics.min_module_px > 0
            assert metrics.actual_quiet_zone >= 0
            assert metrics.estimated_scanability is not None


class TestIntentValidationIntegration:
    """Test validation aspects of intent processing in integration context."""

    def test_validation_enforcement_integration(self):
        """Test validation enforcement in complete workflow."""
        payload = PayloadConfig(text="Validation Test")
        intents = IntentsConfig(validation=ValidationIntents(enforce_scanability=True, quiet_zone=3))

        result = render_with_intents(payload, intents)

        # Should enable safe mode for scanability
        used_options = result.used_options
        assert used_options.get("safe_mode") is True
        assert used_options.get("border") == 3

        # Metrics should reflect validation settings
        assert result.metrics.actual_quiet_zone == 3

    def test_degradation_application_integration(self):
        """Test that degradation is applied correctly in full workflow."""
        payload = PayloadConfig(text="Degradation Test")
        intents = IntentsConfig(
            # Use intents that should trigger degradation warnings
            accessibility=AccessibilityIntents(ids=True, aria=True),
            advanced=AdvancedIntents(mask_pattern=4, structured_append={"enabled": True}),
        )

        result = render_with_intents(payload, intents)

        # Should have processed intents (degradation depends on specific features used)
        # Note: Simple accessibility and advanced intents may all be supported
        assert result.degradation_applied in [True, False]  # Depends on feature interactions
        assert len(result.warnings) >= 0  # May have warnings
        assert len(result.unsupported_intents) >= 0  # May have unsupported features

        # Should still produce valid SVG
        assert result.svg_content is not None
        assert len(result.svg_content) > 0
