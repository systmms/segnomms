"""Test suite for Performance monitoring system."""

import pytest
import time
from segnomms.core.performance import (
    PerformanceMonitor, PerformanceThreshold, PerformanceMetric,
    WarningLevel, measure_matrix_operation, measure_centerpiece_operation,
    measure_imprint_rendering, get_performance_monitor, set_performance_monitor
)


class TestPerformanceMonitor:
    """Test cases for the PerformanceMonitor class."""
    
    @pytest.fixture
    def monitor(self):
        """Create a fresh PerformanceMonitor instance."""
        return PerformanceMonitor(enabled=True)
    
    def test_monitor_initialization(self, monitor):
        """Test monitor initialization with default thresholds."""
        assert monitor.enabled is True
        assert len(monitor.thresholds) > 0
        assert "matrix_manipulation" in monitor.thresholds
        assert "imprint_rendering" in monitor.thresholds
        assert "centerpiece_clearing" in monitor.thresholds
        assert len(monitor.metrics) == 0
    
    def test_operation_timing(self, monitor):
        """Test basic operation timing functionality."""
        operation_id = monitor.start_operation("test_operation")
        
        # Simulate some work
        time.sleep(0.01)  # 10ms
        
        metric = monitor.end_operation(operation_id)
        
        assert metric is not None
        assert metric.operation == "test_operation"
        assert metric.elapsed_ms >= 10  # Should be at least 10ms
        assert metric.start_time < metric.end_time
    
    def test_threshold_checking(self, monitor):
        """Test threshold checking and warning generation."""
        # Set a very low threshold for testing
        threshold = PerformanceThreshold(
            operation="test_op",
            max_time_ms=1.0,  # 1ms threshold
            warning_level=WarningLevel.WARNING
        )
        monitor.set_threshold(threshold)
        
        operation_id = monitor.start_operation("test_op")
        time.sleep(0.01)  # 10ms - should exceed threshold
        metric = monitor.end_operation(operation_id)
        
        assert metric.exceeded_threshold is True
        assert metric.warning_level == WarningLevel.WARNING
        assert "threshold" in metric.warning_message.lower()
    
    def test_complexity_scoring(self, monitor):
        """Test complexity scoring and threshold checking."""
        threshold = PerformanceThreshold(
            operation="complex_op",
            max_time_ms=1000.0,  # High time threshold
            max_complexity=100,   # Low complexity threshold
            warning_level=WarningLevel.INFO
        )
        monitor.set_threshold(threshold)
        
        operation_id = monitor.start_operation("complex_op")
        metric = monitor.end_operation(operation_id, complexity_score=500)  # High complexity
        
        assert metric.exceeded_threshold is True
        assert metric.warning_level == WarningLevel.INFO
        assert "complexity" in metric.warning_message.lower()
    
    def test_measure_operation_method(self, monitor):
        """Test the measure_operation convenience method."""
        def test_function(x, y):
            time.sleep(0.005)  # 5ms
            return x + y
        
        def complexity_calc(result, x, y):
            return x * y
        
        result = monitor.measure_operation(
            "test_function", test_function, 5, 10,
            complexity_func=complexity_calc
        )
        
        assert result == 15  # 5 + 10
        assert len(monitor.metrics) == 1
        
        metric = monitor.metrics[0]
        assert metric.operation == "test_function"
        assert metric.complexity_score == 50  # 5 * 10
        assert metric.elapsed_ms >= 5
    
    def test_performance_summary(self, monitor):
        """Test performance summary generation."""
        # Generate some test metrics
        for i in range(3):
            operation_id = monitor.start_operation("test_op")
            time.sleep(0.001)
            monitor.end_operation(operation_id, complexity_score=i * 10)
        
        summary = monitor.get_performance_summary()
        
        assert summary["enabled"] is True
        assert summary["total_operations"] == 3
        assert "operations" in summary
        assert "test_op" in summary["operations"]
        
        op_stats = summary["operations"]["test_op"]
        assert op_stats["count"] == 3
        assert op_stats["avg_time_ms"] > 0
        assert op_stats["max_time_ms"] >= op_stats["avg_time_ms"]
    
    def test_recent_warnings(self, monitor):
        """Test recent warnings retrieval."""
        # Set low threshold to generate warnings
        threshold = PerformanceThreshold(
            operation="warn_test",
            max_time_ms=1.0,
            warning_level=WarningLevel.ERROR
        )
        monitor.set_threshold(threshold)
        
        # Generate warnings
        for i in range(5):
            operation_id = monitor.start_operation("warn_test")
            time.sleep(0.002)  # Should exceed 1ms threshold
            monitor.end_operation(operation_id)
        
        warnings = monitor.get_recent_warnings(3)
        assert len(warnings) == 3  # Limited to 3
        
        all_warnings = monitor.get_recent_warnings()
        assert len(all_warnings) == 5  # All warnings
        
        for warning in warnings:
            assert warning.exceeded_threshold is True
    
    def test_operation_specific_warnings(self, monitor):
        """Test operation-specific warning retrieval."""
        # Set thresholds for different operations
        monitor.set_threshold(PerformanceThreshold("op1", 1.0, warning_level=WarningLevel.WARNING))
        monitor.set_threshold(PerformanceThreshold("op2", 1.0, warning_level=WarningLevel.ERROR))
        
        # Generate warnings for op1
        for i in range(2):
            operation_id = monitor.start_operation("op1")
            time.sleep(0.002)
            monitor.end_operation(operation_id)
        
        # Generate warnings for op2
        operation_id = monitor.start_operation("op2")
        time.sleep(0.002)
        monitor.end_operation(operation_id)
        
        op1_warnings = monitor.get_operation_warnings("op1")
        op2_warnings = monitor.get_operation_warnings("op2")
        
        assert len(op1_warnings) == 2
        assert len(op2_warnings) == 1
        assert all(w.operation == "op1" for w in op1_warnings)
        assert all(w.operation == "op2" for w in op2_warnings)
    
    def test_performance_recommendations(self, monitor):
        """Test performance recommendation generation."""
        # Generate metrics that should trigger recommendations
        # Imprint preprocessing with high warning rate
        monitor.set_threshold(PerformanceThreshold("imprint_preprocessing", 1.0))
        
        for i in range(5):
            operation_id = monitor.start_operation("imprint_preprocessing")
            time.sleep(0.002)  # Exceed threshold
            monitor.end_operation(operation_id)
        
        recommendations = monitor.generate_performance_recommendations()
        
        assert len(recommendations) > 0
        imprint_rec = any("imprint" in rec.lower() for rec in recommendations)
        assert imprint_rec, "Should generate imprint-specific recommendations"


class TestPerformanceDecorators:
    """Test cases for performance measurement decorators."""
    
    def test_matrix_operation_decorator(self):
        """Test matrix operation performance decorator."""
        # Mock matrix manipulator with size attribute
        class MockManipulator:
            def __init__(self):
                self.size = 25
        
        @measure_matrix_operation
        def mock_matrix_op(manipulator, config):
            time.sleep(0.005)
            return "result"
        
        manipulator = MockManipulator()
        result = mock_matrix_op(manipulator, {"test": "config"})
        
        assert result == "result"
        
        # Check that metrics were recorded
        monitor = get_performance_monitor()
        assert len(monitor.metrics) > 0
        
        metric = monitor.metrics[-1]  # Most recent
        assert metric.operation == "matrix_manipulation"
        assert metric.complexity_score == 625  # 25 * 25
    
    def test_centerpiece_operation_decorator(self):
        """Test centerpiece operation performance decorator."""
        from segnomms.config import ReserveMode, CenterpieceConfig
        
        class MockManipulator:
            def __init__(self):
                self.size = 21
        
        @measure_centerpiece_operation
        def mock_centerpiece_op(manipulator, config):
            time.sleep(0.003)
            return "centerpiece_result"
        
        manipulator = MockManipulator()
        config = CenterpieceConfig(
            size=0.2,
            mode=ReserveMode.IMPRINT
        )
        
        result = mock_centerpiece_op(manipulator, config)
        
        assert result == "centerpiece_result"
        
        # Check metrics
        monitor = get_performance_monitor()
        metric = monitor.metrics[-1]
        
        # Should detect imprint mode and use imprint_preprocessing
        assert metric.operation in ["centerpiece_clearing", "imprint_preprocessing"]
        # Complexity should be increased for imprint mode
        assert metric.complexity_score is not None
    
    def test_imprint_rendering_decorator(self):
        """Test imprint rendering performance decorator."""
        class MockRenderer:
            def get_imprint_metadata(self):
                return {
                    "imprinted_modules": [{"row": i, "col": i} for i in range(10)]
                }
        
        @measure_imprint_rendering
        def mock_render_op(renderer, config):
            time.sleep(0.002)
            return "render_result"
        
        renderer = MockRenderer()
        result = mock_render_op(renderer, {"test": "config"})
        
        assert result == "render_result"
        
        # Check metrics
        monitor = get_performance_monitor()
        metric = monitor.metrics[-1]
        
        assert metric.operation == "imprint_rendering"
        assert metric.complexity_score == 100  # 10 modules * 10


class TestGlobalMonitor:
    """Test cases for global monitor management."""
    
    def test_global_monitor_singleton(self):
        """Test global monitor singleton behavior."""
        monitor1 = get_performance_monitor()
        monitor2 = get_performance_monitor()
        
        assert monitor1 is monitor2  # Should be same instance
    
    def test_set_global_monitor(self):
        """Test setting custom global monitor."""
        original_monitor = get_performance_monitor()
        custom_monitor = PerformanceMonitor(enabled=False)
        
        set_performance_monitor(custom_monitor)
        
        current_monitor = get_performance_monitor()
        assert current_monitor is custom_monitor
        assert current_monitor.enabled is False
        
        # Restore original for other tests
        set_performance_monitor(original_monitor)
    
    def test_disabled_monitor(self):
        """Test behavior when monitor is disabled."""
        disabled_monitor = PerformanceMonitor(enabled=False)
        
        operation_id = disabled_monitor.start_operation("test")
        metric = disabled_monitor.end_operation(operation_id)
        
        assert metric is None
        assert len(disabled_monitor.metrics) == 0


class TestPerformanceThreshold:
    """Test cases for PerformanceThreshold class."""
    
    def test_threshold_time_check(self):
        """Test time threshold checking."""
        threshold = PerformanceThreshold(
            operation="test",
            max_time_ms=100.0,
            warning_level=WarningLevel.WARNING
        )
        
        assert threshold.check_time(50.0) is False  # Under threshold
        assert threshold.check_time(150.0) is True   # Over threshold
        assert threshold.check_time(100.0) is False  # At threshold
    
    def test_threshold_complexity_check(self):
        """Test complexity threshold checking."""
        threshold = PerformanceThreshold(
            operation="test",
            max_time_ms=1000.0,
            max_complexity=500,
            warning_level=WarningLevel.INFO
        )
        
        assert threshold.check_complexity(300) is False  # Under threshold
        assert threshold.check_complexity(600) is True   # Over threshold
        assert threshold.check_complexity(500) is False  # At threshold
        
        # Test with no complexity threshold set
        threshold_no_complexity = PerformanceThreshold(
            operation="test",
            max_time_ms=1000.0,
            warning_level=WarningLevel.WARNING
        )
        
        assert threshold_no_complexity.check_complexity(1000) is False


class TestPerformanceMetric:
    """Test cases for PerformanceMetric class."""
    
    def test_metric_exceeded_threshold_property(self):
        """Test exceeded_threshold property."""
        # Metric without warning
        metric1 = PerformanceMetric(
            operation="test",
            start_time=0.0,
            end_time=0.1,
            elapsed_ms=100.0
        )
        
        assert metric1.exceeded_threshold is False
        
        # Metric with warning
        metric2 = PerformanceMetric(
            operation="test",
            start_time=0.0,
            end_time=0.2,
            elapsed_ms=200.0,
            warning_level=WarningLevel.WARNING,
            warning_message="Test warning"
        )
        
        assert metric2.exceeded_threshold is True