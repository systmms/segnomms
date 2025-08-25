"""Performance monitoring and warning system for SegnoMMS operations.

This module provides performance tracking, threshold monitoring, and warning
generation for computationally intensive operations like reserve area processing.
"""

import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class PerformanceLevel(Enum):
    """Performance impact levels for operations."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class WarningLevel(Enum):
    """Warning severity levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class PerformanceThreshold:
    """Performance threshold configuration."""

    operation: str
    max_time_ms: float
    max_memory_mb: Optional[float] = None
    max_complexity: Optional[int] = None
    warning_level: WarningLevel = WarningLevel.WARNING

    def check_time(self, elapsed_ms: float) -> bool:
        """Check if elapsed time exceeds threshold."""
        return elapsed_ms > self.max_time_ms

    def check_complexity(self, complexity: int) -> bool:
        """Check if complexity exceeds threshold."""
        return self.max_complexity is not None and complexity > self.max_complexity


@dataclass
class PerformanceMetric:
    """Performance measurement result."""

    operation: str
    start_time: float
    end_time: float
    elapsed_ms: float
    memory_peak_mb: Optional[float] = None
    complexity_score: Optional[int] = None
    warning_level: Optional[WarningLevel] = None
    warning_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def exceeded_threshold(self) -> bool:
        """Check if any thresholds were exceeded."""
        return self.warning_level is not None


class PerformanceMonitor:
    """Monitor and track performance of SegnoMMS operations."""

    # Default performance thresholds
    DEFAULT_THRESHOLDS = {
        "matrix_manipulation": PerformanceThreshold(
            operation="matrix_manipulation",
            max_time_ms=500.0,  # 500ms threshold
            max_complexity=10000,  # Matrix operations
            warning_level=WarningLevel.WARNING,
        ),
        "imprint_rendering": PerformanceThreshold(
            operation="imprint_rendering",
            max_time_ms=800.0,  # 800ms threshold for complex visual processing
            max_complexity=30000,  # Visual effect complexity
            warning_level=WarningLevel.WARNING,
        ),
        "imprint_preprocessing": PerformanceThreshold(
            operation="imprint_preprocessing",
            max_time_ms=300.0,  # 300ms threshold for imprint calculation
            max_complexity=15000,  # Module analysis complexity
            warning_level=WarningLevel.INFO,
        ),
        "centerpiece_clearing": PerformanceThreshold(
            operation="centerpiece_clearing",
            max_time_ms=200.0,  # 200ms threshold
            max_complexity=5000,  # Module clearing complexity
            warning_level=WarningLevel.INFO,
        ),
        "svg_generation": PerformanceThreshold(
            operation="svg_generation",
            max_time_ms=2000.0,  # 2s threshold
            max_complexity=100000,  # SVG element count
            warning_level=WarningLevel.WARNING,
        ),
    }

    def __init__(self, enabled: bool = True):
        """Initialize performance monitor.

        Args:
            enabled: Whether performance monitoring is active
        """
        self.enabled = enabled
        self.thresholds: Dict[str, PerformanceThreshold] = (
            self.DEFAULT_THRESHOLDS.copy()
        )
        self.metrics: List[PerformanceMetric] = []
        self._active_operations: Dict[str, Tuple[float, str]] = {}

    def set_threshold(self, threshold: PerformanceThreshold) -> None:
        """Set or update a performance threshold.

        Args:
            threshold: Performance threshold configuration
        """
        self.thresholds[threshold.operation] = threshold

    def start_operation(self, operation: str, **metadata: Any) -> str:
        """Start timing an operation.

        Args:
            operation: Operation name/identifier
            **metadata: Additional metadata to track

        Returns:
            Operation ID for stopping the timer
        """
        if not self.enabled:
            return operation

        start_time = time.perf_counter()
        operation_id = f"{operation}#{start_time}"
        self._active_operations[operation_id] = (start_time, operation)

        logger.debug(f"Started performance monitoring for {operation}")
        return operation_id

    def end_operation(
        self, operation_id: str, complexity_score: Optional[int] = None, **metadata: Any
    ) -> Optional[PerformanceMetric]:
        """End timing an operation and check thresholds.

        Args:
            operation_id: Operation ID from start_operation
            complexity_score: Optional complexity metric
            **metadata: Additional metadata

        Returns:
            PerformanceMetric if monitoring enabled, None otherwise
        """
        if not self.enabled or operation_id not in self._active_operations:
            return None

        end_time = time.perf_counter()
        start_time, operation = self._active_operations.pop(operation_id)
        elapsed_ms = (end_time - start_time) * 1000

        # Create metric
        metric = PerformanceMetric(
            operation=operation,
            start_time=start_time,
            end_time=end_time,
            elapsed_ms=elapsed_ms,
            complexity_score=complexity_score,
            metadata=metadata,
        )

        # Check thresholds
        threshold = self.thresholds.get(operation)
        if threshold:
            if threshold.check_time(elapsed_ms):
                metric.warning_level = threshold.warning_level
                metric.warning_message = (
                    f"{operation} took {elapsed_ms:.1f}ms "
                    f"(threshold: {threshold.max_time_ms:.1f}ms)"
                )

            elif complexity_score and threshold.check_complexity(complexity_score):
                metric.warning_level = threshold.warning_level
                metric.warning_message = (
                    f"{operation} complexity {complexity_score} "
                    f"(threshold: {threshold.max_complexity})"
                )

        # Log warning if threshold exceeded
        if metric.warning_level:
            log_method = getattr(logger, metric.warning_level.value, logger.info)
            log_method(f"Performance warning: {metric.warning_message}")

        self.metrics.append(metric)
        return metric

    def measure_operation(
        self,
        operation: str,
        func: Callable[..., Any],
        *args: Any,
        complexity_func: Optional[Callable[..., int]] = None,
        **kwargs: Any,
    ) -> Any:
        """Measure the performance of a function call.

        Args:
            operation: Operation name for tracking
            func: Function to measure
            *args: Function arguments
            complexity_func: Optional function to calculate complexity
            **kwargs: Function keyword arguments

        Returns:
            Function result
        """
        operation_id = self.start_operation(operation)

        try:
            result = func(*args, **kwargs)

            # Calculate complexity if function provided
            complexity = None
            if complexity_func:
                try:
                    complexity = complexity_func(result, *args, **kwargs)
                except Exception as e:
                    logger.debug(f"Failed to calculate complexity for {operation}: {e}")

            self.end_operation(operation_id, complexity_score=complexity)
            return result

        except Exception as e:
            # Still record the operation even if it failed
            self.end_operation(operation_id, metadata={"error": str(e)})
            raise

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get summary of performance metrics.

        Returns:
            Summary dictionary with performance statistics
        """
        if not self.metrics:
            return {"enabled": self.enabled, "total_operations": 0}

        # Group by operation
        by_operation = {}
        total_warnings = 0

        for metric in self.metrics:
            if metric.operation not in by_operation:
                by_operation[metric.operation] = {
                    "count": 0,
                    "total_time_ms": 0.0,
                    "avg_time_ms": 0.0,
                    "max_time_ms": 0.0,
                    "warnings": 0,
                }

            op_stats = by_operation[metric.operation]
            op_stats["count"] += 1
            op_stats["total_time_ms"] += metric.elapsed_ms
            op_stats["max_time_ms"] = max(op_stats["max_time_ms"], metric.elapsed_ms)

            if metric.exceeded_threshold:
                op_stats["warnings"] += 1
                total_warnings += 1

        # Calculate averages
        for stats in by_operation.values():
            if stats["count"] > 0:
                stats["avg_time_ms"] = stats["total_time_ms"] / stats["count"]

        return {
            "enabled": self.enabled,
            "total_operations": len(self.metrics),
            "total_warnings": total_warnings,
            "operations": by_operation,
            "thresholds": {
                name: {
                    "max_time_ms": t.max_time_ms,
                    "max_complexity": t.max_complexity,
                    "warning_level": t.warning_level.value,
                }
                for name, t in self.thresholds.items()
            },
        }

    def get_recent_warnings(self, limit: int = 10) -> List[PerformanceMetric]:
        """Get recent performance warnings.

        Args:
            limit: Maximum number of warnings to return

        Returns:
            List of recent metrics that exceeded thresholds
        """
        warnings = [m for m in self.metrics if m.exceeded_threshold]
        return warnings[-limit:] if warnings else []

    def get_operation_warnings(self, operation: str) -> List[PerformanceMetric]:
        """Get all warnings for a specific operation type.

        Args:
            operation: Operation name to filter by

        Returns:
            List of metrics with warnings for the specified operation
        """
        return [
            m for m in self.metrics if m.operation == operation and m.exceeded_threshold
        ]

    def generate_performance_recommendations(self) -> List[str]:
        """Generate performance improvement recommendations based on metrics.

        Returns:
            List of recommendation messages
        """
        recommendations: List[str] = []

        if not self.metrics:
            return recommendations

        # Analyze by operation type
        by_operation: Dict[str, Any] = {}
        for metric in self.metrics:
            if metric.operation not in by_operation:
                by_operation[metric.operation] = []
            by_operation[metric.operation].append(metric)

        # Generate operation-specific recommendations
        for operation, metrics in by_operation.items():
            warnings = [m for m in metrics if m.exceeded_threshold]

            if not warnings:
                continue

            avg_time = sum(m.elapsed_ms for m in metrics) / len(metrics)
            max_time = max(m.elapsed_ms for m in metrics)
            warning_rate = len(warnings) / len(metrics)

            if operation == "imprint_preprocessing" and warning_rate > 0.3:
                recommendations.append(
                    f"Imprint preprocessing shows {warning_rate:.0%} warning rate. "
                    f"Consider reducing centerpiece size or using simpler shapes."
                )

            elif operation == "imprint_rendering" and avg_time > 500:
                recommendations.append(
                    f"Imprint rendering averaging {avg_time:.0f}ms. "
                    f"Consider reducing visual effects complexity or module count."
                )

            elif operation == "centerpiece_clearing" and max_time > 300:
                recommendations.append(
                    f"Centerpiece clearing peaked at {max_time:.0f}ms. "
                    f"Consider using more efficient edge refinement algorithms."
                )

            elif operation == "matrix_manipulation" and warning_rate > 0.5:
                recommendations.append(
                    f"Matrix manipulation shows high warning rate "
                    f"({warning_rate:.0%}). Consider optimizing matrix "
                    f"processing algorithms."
                )

        return recommendations

    def record_centerpiece_metric(self, metric: Any) -> None:
        """Record a centerpiece performance metric.

        Args:
            metric: CenterpiecePerformanceMetric instance
        """
        # Convert centerpiece metric to standard performance metric
        perf_metric = PerformanceMetric(
            operation=metric.operation,
            start_time=metric.timestamp - metric.execution_time,
            end_time=metric.timestamp,
            elapsed_ms=metric.execution_time * 1000,  # Convert to milliseconds
            complexity_score=metric.centerpiece_area,
            warning_message="; ".join(metric.warnings) if metric.warnings else None,
            warning_level=WarningLevel.WARNING if metric.warnings else None,
            metadata={
                "centerpiece_area": metric.centerpiece_area,
                "matrix_size": metric.matrix_size,
                "memory_usage": metric.memory_usage,
            },
        )

        # Add to metrics collection
        self.metrics.append(perf_metric)

        # Check thresholds and log warnings
        for threshold in self.thresholds.values():
            if threshold.operation == metric.operation:
                if threshold.check_time(metric.execution_time * 1000):  # Convert to ms
                    logger.warning(
                        f"Centerpiece operation {metric.operation} exceeded "
                        f"time threshold: {metric.execution_time:.3f}s"
                    )

                if threshold.check_complexity(metric.centerpiece_area):
                    logger.warning(
                        f"Centerpiece operation {metric.operation} exceeded "
                        f"complexity threshold: {metric.centerpiece_area} modules"
                    )

    def clear_metrics(self) -> None:
        """Clear collected performance metrics."""
        self.metrics.clear()
        self._active_operations.clear()


# Global performance monitor instance
_global_monitor: Optional[PerformanceMonitor] = None


def get_performance_monitor() -> PerformanceMonitor:
    """Get the global performance monitor instance."""
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = PerformanceMonitor()
    return _global_monitor


def set_performance_monitor(monitor: PerformanceMonitor) -> None:
    """Set the global performance monitor instance."""
    global _global_monitor
    _global_monitor = monitor


def measure_matrix_operation(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to measure matrix operation performance.

    Args:
        func: Function to measure

    Returns:
        Decorated function with performance monitoring
    """

    def wrapper(*args: Any, **kwargs: Any) -> Any:
        monitor = get_performance_monitor()

        # Create simpler complexity calculator
        def complexity_calc() -> int:
            if args and hasattr(args[0], "size"):
                return int(getattr(args[0], "size", 1)) ** 2
            return 1

        return monitor.measure_operation(
            "matrix_manipulation",
            func,
            *args,
            complexity_func=complexity_calc,
            **kwargs,
        )

    return wrapper


def measure_centerpiece_operation(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to measure centerpiece operation performance.

    Args:
        func: Function to measure

    Returns:
        Decorated function with performance monitoring
    """

    def wrapper(*args: Any, **kwargs: Any) -> Any:
        monitor = get_performance_monitor()

        # Simplified complexity calculation
        def complexity_calc() -> int:
            return 100  # Fixed complexity for centerpiece operations

        # Determine operation type based on function name and config
        operation_type = "centerpiece_clearing"
        if len(args) >= 2 and hasattr(args[1], "mode"):
            config = args[1]
            if hasattr(config, "mode"):
                from ..config import ReserveMode

                if (
                    config.mode == ReserveMode.IMPRINT
                    and func.__name__ == "apply_imprint_mode"
                ):
                    operation_type = "imprint_preprocessing"

        return monitor.measure_operation(
            operation_type, func, *args, complexity_func=complexity_calc, **kwargs
        )

    return wrapper


def measure_imprint_rendering(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to measure imprint rendering performance.

    Args:
        func: Function to measure

    Returns:
        Decorated function with performance monitoring
    """

    def wrapper(*args: Any, **kwargs: Any) -> Any:
        monitor = get_performance_monitor()

        # Simplified complexity calculation
        def complexity_calc() -> int:
            return 50  # Fixed complexity for imprint rendering

        return monitor.measure_operation(
            "imprint_rendering", func, *args, complexity_func=complexity_calc, **kwargs
        )

    return wrapper
