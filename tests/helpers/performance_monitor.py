"""
Performance monitoring framework for SegnoMMS testing.

This module provides comprehensive performance tracking, regression detection,
and reporting capabilities for the test suite.
"""

import json
import os
import statistics
import time
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import psutil
import pytest


@dataclass
class PerformanceMetric:
    """Individual performance measurement."""

    name: str
    execution_time: float
    memory_usage_mb: float
    cpu_percent: float
    timestamp: str
    metadata: Dict[str, Any] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


@dataclass
class PerformanceBaseline:
    """Performance baseline for regression detection."""

    name: str
    mean_time: float
    std_dev: float
    memory_baseline: float
    sample_count: int
    last_updated: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PerformanceBaseline":
        """Create from dictionary."""
        return cls(**data)


class PerformanceMonitor:
    """Comprehensive performance monitoring system."""

    def __init__(
        self,
        baseline_file: Optional[Path] = None,
        metrics_file: Optional[Path] = None,
        enable_cpu_monitoring: bool = True,
    ):
        """
        Initialize performance monitor.

        Args:
            baseline_file: File to store performance baselines
            metrics_file: File to store raw metrics
            enable_cpu_monitoring: Whether to monitor CPU usage
        """
        self.baseline_file = baseline_file or Path("performance_baselines.json")
        self.metrics_file = metrics_file or Path("performance_metrics.json")
        self.enable_cpu_monitoring = enable_cpu_monitoring

        self.process = psutil.Process(os.getpid())
        self.baselines: Dict[str, PerformanceBaseline] = {}
        self.metrics: List[PerformanceMetric] = []

        self._load_baselines()
        self._load_metrics()

    def _load_baselines(self):
        """Load performance baselines from file."""
        if self.baseline_file.exists():
            try:
                with open(self.baseline_file, "r") as f:
                    data = json.load(f)
                    self.baselines = {
                        name: PerformanceBaseline.from_dict(baseline_data)
                        for name, baseline_data in data.items()
                    }
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Warning: Could not load baselines from {self.baseline_file}: {e}")

    def _load_metrics(self):
        """Load historical metrics from file."""
        if self.metrics_file.exists():
            try:
                with open(self.metrics_file, "r") as f:
                    data = json.load(f)
                    self.metrics = [PerformanceMetric(**metric_data) for metric_data in data]
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Warning: Could not load metrics from {self.metrics_file}: {e}")

    def save_baselines(self):
        """Save current baselines to file."""
        with open(self.baseline_file, "w") as f:
            data = {name: baseline.to_dict() for name, baseline in self.baselines.items()}
            json.dump(data, f, indent=2)

    def save_metrics(self):
        """Save current metrics to file."""
        with open(self.metrics_file, "w") as f:
            data = [metric.to_dict() for metric in self.metrics]
            json.dump(data, f, indent=2)

    @contextmanager
    def measure(self, name: str, metadata: Optional[Dict[str, Any]] = None, update_baseline: bool = False):
        """
        Context manager for measuring performance.

        Args:
            name: Name of the operation being measured
            metadata: Additional metadata to store
            update_baseline: Whether to update baseline with this measurement

        Example:
            with monitor.measure("matrix_manipulation") as measurement:
                # Perform operation
                result = expensive_operation()

            # measurement contains the performance data
        """
        # Get initial measurements
        memory_before = self.process.memory_info().rss / 1024 / 1024  # MB
        cpu_before = self.process.cpu_percent()
        start_time = time.perf_counter()

        try:
            yield
        finally:
            # Get final measurements
            end_time = time.perf_counter()
            execution_time = end_time - start_time
            memory_after = self.process.memory_info().rss / 1024 / 1024  # MB
            memory_usage = memory_after - memory_before

            if self.enable_cpu_monitoring:
                cpu_after = self.process.cpu_percent()
                cpu_percent = cpu_after - cpu_before if cpu_before else cpu_after
            else:
                cpu_percent = 0.0

            # Create metric
            metric = PerformanceMetric(
                name=name,
                execution_time=execution_time,
                memory_usage_mb=memory_usage,
                cpu_percent=cpu_percent,
                timestamp=datetime.now().isoformat(),
                metadata=metadata or {},
            )

            self.metrics.append(metric)

            # Update baseline if requested
            if update_baseline:
                self._update_baseline(name, metric)

    def _update_baseline(self, name: str, metric: PerformanceMetric):
        """Update baseline with new measurement."""
        if name in self.baselines:
            baseline = self.baselines[name]
            # Update baseline using exponential moving average
            alpha = 0.1  # Learning rate
            baseline.mean_time = (1 - alpha) * baseline.mean_time + alpha * metric.execution_time
            baseline.memory_baseline = (1 - alpha) * baseline.memory_baseline + alpha * metric.memory_usage_mb
            baseline.sample_count += 1
            baseline.last_updated = metric.timestamp
        else:
            # Create new baseline
            self.baselines[name] = PerformanceBaseline(
                name=name,
                mean_time=metric.execution_time,
                std_dev=0.0,  # Will be calculated from historical data
                memory_baseline=metric.memory_usage_mb,
                sample_count=1,
                last_updated=metric.timestamp,
            )

    def check_regression(
        self, name: str, current_time: float, current_memory: float = 0.0, threshold_factor: float = 2.0
    ) -> Dict[str, Any]:
        """
        Check if current performance represents a regression.

        Args:
            name: Name of the operation
            current_time: Current execution time
            current_memory: Current memory usage (MB)
            threshold_factor: Factor by which performance can degrade

        Returns:
            Dictionary with regression analysis results
        """
        result = {
            "name": name,
            "has_regression": False,
            "time_regression": False,
            "memory_regression": False,
            "details": {},
        }

        if name not in self.baselines:
            result["details"]["message"] = "No baseline available"
            return result

        baseline = self.baselines[name]

        # Check time regression
        time_threshold = baseline.mean_time * threshold_factor
        if current_time > time_threshold:
            result["has_regression"] = True
            result["time_regression"] = True
            result["details"]["time_ratio"] = current_time / baseline.mean_time
            result["details"]["time_threshold"] = time_threshold

        # Check memory regression
        memory_threshold = baseline.memory_baseline * threshold_factor
        if current_memory > memory_threshold:
            result["has_regression"] = True
            result["memory_regression"] = True
            result["details"]["memory_ratio"] = current_memory / baseline.memory_baseline
            result["details"]["memory_threshold"] = memory_threshold

        # Add baseline information
        result["details"]["baseline_time"] = baseline.mean_time
        result["details"]["baseline_memory"] = baseline.memory_baseline
        result["details"]["current_time"] = current_time
        result["details"]["current_memory"] = current_memory

        return result

    def get_metrics_summary(self, name: str = None) -> Dict[str, Any]:
        """
        Get summary statistics for metrics.

        Args:
            name: Optional filter by operation name

        Returns:
            Summary statistics
        """
        if name:
            filtered_metrics = [m for m in self.metrics if m.name == name]
        else:
            filtered_metrics = self.metrics

        if not filtered_metrics:
            return {"error": "No metrics found"}

        times = [m.execution_time for m in filtered_metrics]
        memories = [m.memory_usage_mb for m in filtered_metrics]

        return {
            "name": name,
            "count": len(filtered_metrics),
            "time_stats": {
                "mean": statistics.mean(times),
                "median": statistics.median(times),
                "std_dev": statistics.stdev(times) if len(times) > 1 else 0.0,
                "min": min(times),
                "max": max(times),
            },
            "memory_stats": {
                "mean": statistics.mean(memories),
                "median": statistics.median(memories),
                "std_dev": statistics.stdev(memories) if len(memories) > 1 else 0.0,
                "min": min(memories),
                "max": max(memories),
            },
            "recent_metrics": [m.to_dict() for m in filtered_metrics[-5:]],  # Last 5 measurements
        }

    def generate_performance_report(self, output_file: Optional[Path] = None) -> str:
        """
        Generate comprehensive performance report.

        Args:
            output_file: Optional file to write report to

        Returns:
            Report as string
        """
        report_lines = []
        report_lines.append("SEGNOMMS PERFORMANCE REPORT")
        report_lines.append("=" * 50)
        report_lines.append(f"Generated: {datetime.now().isoformat()}")
        report_lines.append(f"Total metrics: {len(self.metrics)}")
        report_lines.append(f"Baselines: {len(self.baselines)}")
        report_lines.append("")

        # Get unique operation names
        operation_names = list(set(m.name for m in self.metrics))
        operation_names.sort()

        for name in operation_names:
            summary = self.get_metrics_summary(name)
            if "error" in summary:
                continue

            report_lines.append(f"Operation: {name}")
            report_lines.append("-" * 40)

            time_stats = summary["time_stats"]
            memory_stats = summary["memory_stats"]

            report_lines.append(f"  Samples: {summary['count']}")
            report_lines.append("  Execution Time:")
            report_lines.append(f"    Mean: {time_stats['mean'] * 1000:.2f} ms")
            report_lines.append(f"    Median: {time_stats['median'] * 1000:.2f} ms")
            report_lines.append(f"    Std Dev: {time_stats['std_dev'] * 1000:.2f} ms")
            report_lines.append(
                f"    Range: {time_stats['min'] * 1000:.2f} - {time_stats['max'] * 1000:.2f} ms"
            )

            report_lines.append("  Memory Usage:")
            report_lines.append(f"    Mean: {memory_stats['mean']:.2f} MB")
            report_lines.append(f"    Median: {memory_stats['median']:.2f} MB")
            report_lines.append(f"    Range: {memory_stats['min']:.2f} - {memory_stats['max']:.2f} MB")

            # Check for potential issues
            if time_stats["mean"] > 1.0:
                report_lines.append("    ⚠️  WARNING: High execution time")
            if memory_stats["mean"] > 50:
                report_lines.append("    ⚠️  WARNING: High memory usage")
            if time_stats["std_dev"] / time_stats["mean"] > 0.5:
                report_lines.append("    ⚠️  WARNING: High variability in execution time")

            report_lines.append("")

        # Baseline information
        if self.baselines:
            report_lines.append("PERFORMANCE BASELINES")
            report_lines.append("=" * 50)

            for name, baseline in self.baselines.items():
                report_lines.append(f"{name}:")
                report_lines.append(f"  Baseline Time: {baseline.mean_time * 1000:.2f} ms")
                report_lines.append(f"  Memory Baseline: {baseline.memory_baseline:.2f} MB")
                report_lines.append(f"  Samples: {baseline.sample_count}")
                report_lines.append(f"  Last Updated: {baseline.last_updated}")
                report_lines.append("")

        report = "\n".join(report_lines)

        if output_file:
            with open(output_file, "w") as f:
                f.write(report)

        return report

    def alert_regressions(self, threshold_factor: float = 2.0) -> List[Dict[str, Any]]:
        """
        Check all recent metrics for performance regressions.

        Args:
            threshold_factor: Factor by which performance can degrade

        Returns:
            List of regression alerts
        """
        alerts = []

        # Check recent metrics against baselines
        recent_metrics = self.metrics[-20:]  # Last 20 measurements

        for metric in recent_metrics:
            regression = self.check_regression(
                metric.name, metric.execution_time, metric.memory_usage_mb, threshold_factor
            )

            if regression["has_regression"]:
                alerts.append(regression)

        return alerts


# Pytest integration
class PerformanceTestPlugin:
    """Pytest plugin for performance monitoring integration."""

    def __init__(self):
        self.monitor = PerformanceMonitor(
            baseline_file=Path("tests/perf/performance_baselines.json"),
            metrics_file=Path("tests/perf/performance_metrics.json"),
        )

    @pytest.hookimpl
    def pytest_runtest_setup(self, item):
        """Hook called before each test."""
        # Add performance monitoring to test items marked with @pytest.mark.benchmark
        if item.get_closest_marker("benchmark"):
            # Store monitor in test item for access in test
            item.performance_monitor = self.monitor

    @pytest.hookimpl
    def pytest_runtest_teardown(self, item):
        """Hook called after each test."""
        if hasattr(item, "performance_monitor"):
            # Save metrics after benchmark tests
            self.monitor.save_metrics()

    @pytest.hookimpl
    def pytest_sessionfinish(self, session):
        """Hook called at end of test session."""
        # Generate performance report
        if self.monitor.metrics:
            report_file = Path("tests/perf/performance_report.txt")
            self.monitor.generate_performance_report(report_file)
            print(f"\nPerformance report saved to: {report_file}")

            # Check for regressions
            alerts = self.monitor.alert_regressions()
            if alerts:
                print(f"\n⚠️  {len(alerts)} performance regression(s) detected!")
                for alert in alerts:
                    print(f"  - {alert['name']}: {alert['details']}")

            # Save baselines and metrics
            self.monitor.save_baselines()
            self.monitor.save_metrics()


# Global performance monitor instance for easy access
_global_monitor = None


def get_performance_monitor() -> PerformanceMonitor:
    """Get the global performance monitor instance."""
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = PerformanceMonitor()
    return _global_monitor


# Convenience decorator for performance monitoring
def monitor_performance(name: str = None, update_baseline: bool = False):
    """
    Decorator for automatic performance monitoring of functions.

    Args:
        name: Optional name for the measurement (defaults to function name)
        update_baseline: Whether to update baseline with this measurement

    Example:
        @monitor_performance("matrix_operation", update_baseline=True)
        def expensive_function():
            # function code
            pass
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            monitor = get_performance_monitor()
            operation_name = name or f"{func.__module__}.{func.__name__}"

            with monitor.measure(operation_name, update_baseline=update_baseline):
                return func(*args, **kwargs)

        return wrapper

    return decorator
