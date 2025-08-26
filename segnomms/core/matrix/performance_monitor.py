"""Performance monitoring for centerpiece operations.

This module provides comprehensive performance tracking and analysis for
centerpiece processing operations, including timing metrics and recommendations.
"""

import logging
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Any, DefaultDict, Dict, List, Optional, Tuple, Union

from ..performance import get_performance_monitor

logger = logging.getLogger(__name__)


@dataclass
class CenterpiecePerformanceMetric:
    """Performance metric for centerpiece operations."""

    operation: str
    execution_time: float
    centerpiece_area: int
    matrix_size: int
    timestamp: float
    memory_usage: int = 0
    warnings: List[str] = field(default_factory=list)


class CenterpiecePerformanceMonitor:
    """Monitors and analyzes performance of centerpiece operations.

    This monitor tracks timing, memory usage, and generates performance
    recommendations for centerpiece processing operations.
    """

    def __init__(self, max_history: int = 100, matrix_size: Optional[int] = None):
        """Initialize the performance monitor.

        Args:
            max_history: Maximum number of metrics to keep in history
            matrix_size: Size of the QR matrix for area calculations
        """
        self.max_history = max_history
        self.matrix_size = matrix_size
        self.metrics_history: deque[CenterpiecePerformanceMetric] = deque(
            maxlen=max_history
        )
        self.operation_stats: DefaultDict[str, List[CenterpiecePerformanceMetric]] = (
            defaultdict(list)
        )

        # Performance thresholds (in seconds)
        self.performance_thresholds = {
            "knockout_processing": 0.1,
            "imprint_processing": 0.05,
            "matrix_validation": 0.02,
            "geometry_calculation": 0.01,
            "centerpiece_clearing": 0.05,
        }

        # Area-based performance expectations
        self.area_performance_factors = {
            "small": (0, 100),  # 0-100 modules
            "medium": (101, 300),  # 101-300 modules
            "large": (301, 600),  # 301-600 modules
            "xlarge": (601, float("inf")),  # 600+ modules
        }

    def start_operation(self, operation: str, config: Any) -> Dict[str, Any]:
        """Start monitoring a centerpiece operation.

        Args:
            operation: Name of the operation being monitored
            config: CenterpieceConfig instance or None for validation operations

        Returns:
            Context dictionary for the operation
        """
        # Handle validation operations that don't have a centerpiece config
        if config is None:
            centerpiece_area = 0
            matrix_size = self.matrix_size or 21
        else:
            centerpiece_area = self._estimate_centerpiece_area(config)
            matrix_size = getattr(config, "matrix_size", self.matrix_size or 21)

        context = {
            "operation": operation,
            "start_time": time.time(),
            "config": config,
            "centerpiece_area": centerpiece_area,
            "matrix_size": matrix_size,
        }

        logger.debug(
            f"Started monitoring {operation} (area: {context['centerpiece_area']} modules)"
        )
        return context

    def end_operation(
        self, context: Dict[str, Any], warnings: Optional[List[str]] = None
    ) -> CenterpiecePerformanceMetric:
        """End monitoring a centerpiece operation and record metrics.

        Args:
            context: Context dictionary from start_operation
            warnings: Optional list of warnings generated during operation

        Returns:
            Performance metric for the completed operation
        """
        end_time = time.time()
        execution_time = end_time - context["start_time"]

        metric = CenterpiecePerformanceMetric(
            operation=context["operation"],
            execution_time=execution_time,
            centerpiece_area=context["centerpiece_area"],
            matrix_size=context["matrix_size"],
            timestamp=end_time,
            warnings=warnings or [],
        )

        # Check performance against thresholds
        self._check_performance_thresholds(metric)

        # Store metrics
        self.metrics_history.append(metric)
        self.operation_stats[context["operation"]].append(metric)

        # Trim operation stats to prevent unbounded growth
        if len(self.operation_stats[context["operation"]]) > self.max_history:
            self.operation_stats[context["operation"]] = self.operation_stats[
                context["operation"]
            ][-self.max_history :]

        logger.debug(f"Completed {context['operation']} in {execution_time:.4f}s")

        # Forward to global performance monitor
        global_monitor = get_performance_monitor()
        global_monitor.record_centerpiece_metric(metric)

        return metric

    def get_operation_statistics(self, operation: str) -> Dict[str, Any]:
        """Get comprehensive statistics for a specific operation.

        Args:
            operation: Name of the operation

        Returns:
            Dictionary with operation statistics
        """
        metrics = self.operation_stats.get(operation, [])

        if not metrics:
            return {"operation": operation, "total_executions": 0}

        execution_times = [m.execution_time for m in metrics]
        areas = [m.centerpiece_area for m in metrics]

        return {
            "operation": operation,
            "total_executions": len(metrics),
            "avg_execution_time": sum(execution_times) / len(execution_times),
            "min_execution_time": min(execution_times),
            "max_execution_time": max(execution_times),
            "avg_centerpiece_area": sum(areas) / len(areas) if areas else 0,
            "recent_warnings": [m.warnings for m in metrics[-5:] if m.warnings],
            "performance_trend": self._calculate_performance_trend(metrics),
        }

    def get_performance_warnings(self, config: Any) -> List[str]:
        """Get performance warnings for a centerpiece configuration.

        Args:
            config: CenterpieceConfig instance

        Returns:
            List of performance warning messages
        """
        warnings = []

        # Calculate estimated complexity
        area = self._estimate_centerpiece_area(config)

        # Area-based warnings (scale threshold based on matrix size)
        matrix_area = (self.matrix_size or 21) ** 2
        large_threshold = max(100, int(matrix_area * 0.15))  # 15% of total matrix

        if area > large_threshold:
            warnings.append(
                f"Large centerpiece area ({area} modules) may impact rendering performance. "
                f"Consider reducing size or using imprint mode."
            )

        if (
            config
            and hasattr(config, "shape")
            and config.shape == "squircle"
            and area > 15
        ):  # Lower threshold for squircles
            warnings.append(
                "Squircle shapes with large areas require complex calculations. "
                "Consider using circle or rect for better performance."
            )

        # Mode-specific warnings
        if hasattr(config, "mode"):
            from ...config import ReserveMode

            if config.mode == ReserveMode.IMPRINT:
                if area > 200:
                    warnings.append(
                        "Large imprint areas may affect visual clarity. "
                        "Consider using knockout mode for large centerpieces."
                    )
                if area > 100 and config.shape == "squircle":
                    warnings.append(
                        "Squircle imprint shapes with large areas require complex visual processing. "
                        "Consider using circle or rect shapes for better performance."
                    )
                if config.size > 0.3:
                    warnings.append(
                        f"Large imprint centerpiece ({config.size:.1%} of QR code) may create "
                        f"visual conflicts with background elements. Consider reducing size."
                    )

        # Margin warnings
        if config.margin > 5:
            warnings.append(
                f"Large margin ({config.margin} modules) increases centerpiece impact. "
                f"Consider reducing margin for better scanability."
            )

        # Historical performance warnings
        historical_warnings = self._get_historical_performance_warnings(config)
        warnings.extend(historical_warnings)

        return warnings

    def get_comprehensive_performance_warnings(self, config: Any) -> List[str]:
        """Get comprehensive performance warnings including configuration and runtime metrics.

        Args:
            config: CenterpieceConfig instance

        Returns:
            List of all performance warning messages
        """
        warnings = []

        # Get configuration-based warnings
        config_warnings = self.get_performance_warnings(config)
        warnings.extend(config_warnings)

        # Get runtime performance warnings from global monitor
        global_monitor = get_performance_monitor()

        # Get recent warnings for centerpiece-related operations
        centerpiece_operations = [
            "centerpiece_clearing",
            "imprint_preprocessing",
            "imprint_rendering",
            "matrix_manipulation",
        ]

        for operation in centerpiece_operations:
            operation_warnings = global_monitor.get_operation_warnings(operation)
            for metric in operation_warnings[-3:]:  # Last 3 warnings per operation
                warnings.append(
                    f"Performance warning in {operation}: {metric.warning_message}"
                )

        # Get performance recommendations from global monitor
        recommendations = global_monitor.generate_performance_recommendations()
        for rec in recommendations:
            warnings.append(f"Recommendation: {rec}")

        # Remove duplicates while preserving order
        seen = set()
        unique_warnings = []
        for warning in warnings:
            if warning not in seen:
                seen.add(warning)
                unique_warnings.append(warning)

        return unique_warnings

    def generate_performance_recommendations(self, config: Any = None) -> List[str]:
        """Generate performance improvement recommendations.

        Args:
            config: Optional CenterpieceConfig to generate specific recommendations

        Returns:
            List of performance improvement recommendations
        """
        recommendations = []

        # Configuration-specific recommendations
        if config:
            area = self._estimate_centerpiece_area(config)
            area_category = self._categorize_area(area)

            if area_category == "large" or area_category == "xlarge":
                recommendations.append(
                    "Consider using knockout mode instead of imprint for large centerpieces"
                )
                recommendations.append(
                    "Reduce centerpiece size to improve processing performance"
                )

            if config.shape == "squircle" and area > 50:
                recommendations.append(
                    "Use circle or rectangle shapes for better performance with large centerpieces"
                )

            if config.margin > 3:
                recommendations.append(
                    "Reduce margin to minimize processing area and improve performance"
                )

        # Historical performance recommendations
        if self.metrics_history:
            slow_operations = self._identify_slow_operations()
            for operation, avg_time in slow_operations:
                recommendations.append(
                    f"Optimize {operation} operations (average: {avg_time:.3f}s)"
                )

        # Memory usage recommendations
        memory_recommendations = self._get_memory_recommendations()
        recommendations.extend(memory_recommendations)

        return recommendations

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get a comprehensive performance summary.

        Returns:
            Dictionary with performance summary
        """
        if not self.metrics_history:
            return {"total_operations": 0, "message": "No performance data available"}

        recent_metrics = list(self.metrics_history)[-20:]  # Last 20 operations

        # Calculate summary statistics
        total_time = sum(m.execution_time for m in recent_metrics)
        avg_time = total_time / len(recent_metrics)

        operation_counts: DefaultDict[str, int] = defaultdict(int)
        for metric in recent_metrics:
            operation_counts[metric.operation] += 1

        return {
            "total_operations": len(self.metrics_history),
            "recent_operations": len(recent_metrics),
            "avg_execution_time": avg_time,
            "total_recent_time": total_time,
            "operation_breakdown": dict(operation_counts),
            "performance_trend": self._calculate_overall_performance_trend(),
            "slowest_operations": self._get_slowest_operations(recent_metrics),
            "recommendations": self.generate_performance_recommendations()[:3],  # Top 3
        }

    def _estimate_centerpiece_area(self, config: Any) -> int:
        """Estimate the area covered by the centerpiece."""
        # Use actual matrix size if available, otherwise try common approaches
        if hasattr(config, "matrix_size"):
            matrix_size = config.matrix_size
        elif hasattr(self, "matrix_size"):
            matrix_size = self.matrix_size
        else:
            matrix_size = 21  # Fallback default

        area_fraction = config.size * config.size
        estimated_area = int(area_fraction * matrix_size * matrix_size)

        # Add margin impact
        margin_impact = (
            config.margin * 4 * int(config.size * matrix_size)
        )  # Perimeter effect

        return int(estimated_area + margin_impact)

    def _check_performance_thresholds(
        self, metric: CenterpiecePerformanceMetric
    ) -> None:
        """Check metric against performance thresholds and add warnings."""
        threshold = self.performance_thresholds.get(metric.operation)

        if threshold and metric.execution_time > threshold:
            # Adjust threshold based on area
            area_factor = self._get_area_performance_factor(metric.centerpiece_area)
            adjusted_threshold = threshold * area_factor

            if metric.execution_time > adjusted_threshold:
                warning = (
                    f"Execution time {metric.execution_time:.3f}s exceeds "
                    f"expected threshold {adjusted_threshold:.3f}s for area {metric.centerpiece_area}"
                )
                metric.warnings.append(warning)

    def _get_area_performance_factor(self, area: int) -> float:
        """Get performance factor adjustment based on centerpiece area."""
        if area <= 100:
            return 1.0  # Small areas - no adjustment
        elif area <= 300:
            return 1.5  # Medium areas - 50% more time allowed
        elif area <= 600:
            return 2.0  # Large areas - 100% more time allowed
        else:
            return 3.0  # Extra large areas - 200% more time allowed

    def _categorize_area(self, area: int) -> str:
        """Categorize area size."""
        for category, (min_area, max_area) in self.area_performance_factors.items():
            if min_area <= area <= max_area:
                return category
        return "unknown"

    def _calculate_performance_trend(
        self, metrics: List[CenterpiecePerformanceMetric]
    ) -> str:
        """Calculate performance trend for metrics."""
        if len(metrics) < 2:
            return "insufficient_data"

        recent_avg = sum(m.execution_time for m in metrics[-5:]) / min(5, len(metrics))
        older_avg = sum(m.execution_time for m in metrics[:-5]) / max(
            1, len(metrics) - 5
        )

        if recent_avg < older_avg * 0.9:
            return "improving"
        elif recent_avg > older_avg * 1.1:
            return "degrading"
        else:
            return "stable"

    def _get_historical_performance_warnings(self, config: Any) -> List[str]:
        """Get warnings based on historical performance for similar configurations."""
        warnings = []

        area = self._estimate_centerpiece_area(config)

        # Find similar operations in history
        similar_metrics = [
            m
            for m in self.metrics_history
            if abs(m.centerpiece_area - area) <= area * 0.2  # Within 20% of area
        ]

        if similar_metrics:
            avg_time = sum(m.execution_time for m in similar_metrics) / len(
                similar_metrics
            )
            max_time = max(m.execution_time for m in similar_metrics)

            if avg_time > 0.1:  # Average time over 100ms
                warnings.append(
                    f"Similar configurations averaged {avg_time:.3f}s processing time. "
                    f"Consider optimizing for better performance."
                )

            if max_time > 0.5:  # Maximum time over 500ms
                warnings.append(
                    f"Similar configurations have taken up to {max_time:.3f}s. "
                    f"Performance may vary significantly."
                )

        return warnings

    def _identify_slow_operations(self) -> List[Tuple[str, float]]:
        """Identify operations that consistently perform slowly."""
        slow_operations = []

        for operation, metrics in self.operation_stats.items():
            if len(metrics) >= 3:  # Need sufficient data
                avg_time = sum(m.execution_time for m in metrics) / len(metrics)
                threshold = self.performance_thresholds.get(operation, 0.1)

                if avg_time > threshold * 1.5:  # 50% slower than threshold
                    slow_operations.append((operation, avg_time))

        return sorted(slow_operations, key=lambda x: x[1], reverse=True)

    def _get_memory_recommendations(self) -> List[str]:
        """Get recommendations related to memory usage."""
        recommendations = []

        # Check for metrics with high memory usage (placeholder for now)
        high_memory_metrics = [
            m for m in self.metrics_history if m.memory_usage > 50 * 1024 * 1024
        ]  # 50MB

        if high_memory_metrics:
            recommendations.append(
                "Consider processing smaller areas to reduce memory usage"
            )

        return recommendations

    def _calculate_overall_performance_trend(self) -> str:
        """Calculate overall performance trend across all operations."""
        if len(self.metrics_history) < 10:
            return "insufficient_data"

        recent_metrics = list(self.metrics_history)[-10:]
        older_metrics = (
            list(self.metrics_history)[-20:-10]
            if len(self.metrics_history) >= 20
            else []
        )

        if not older_metrics:
            return "insufficient_data"

        recent_avg = sum(m.execution_time for m in recent_metrics) / len(recent_metrics)
        older_avg = sum(m.execution_time for m in older_metrics) / len(older_metrics)

        if recent_avg < older_avg * 0.85:
            return "significantly_improving"
        elif recent_avg < older_avg * 0.95:
            return "improving"
        elif recent_avg > older_avg * 1.15:
            return "significantly_degrading"
        elif recent_avg > older_avg * 1.05:
            return "degrading"
        else:
            return "stable"

    def _get_slowest_operations(
        self, metrics: List[CenterpiecePerformanceMetric]
    ) -> List[Dict[str, Any]]:
        """Get the slowest operations from a list of metrics."""
        sorted_metrics = sorted(metrics, key=lambda m: m.execution_time, reverse=True)

        return [
            {
                "operation": m.operation,
                "execution_time": m.execution_time,
                "centerpiece_area": m.centerpiece_area,
                "timestamp": m.timestamp,
            }
            for m in sorted_metrics[:5]
        ]  # Top 5 slowest

    def clear_history(self) -> None:
        """Clear all performance history."""
        self.metrics_history.clear()
        self.operation_stats.clear()
        logger.info("Performance history cleared")

    def export_metrics(self) -> List[Dict[str, Any]]:
        """Export all metrics for analysis.

        Returns:
            List of metric dictionaries
        """
        return [
            {
                "operation": m.operation,
                "execution_time": m.execution_time,
                "centerpiece_area": m.centerpiece_area,
                "matrix_size": m.matrix_size,
                "timestamp": m.timestamp,
                "memory_usage": m.memory_usage,
                "warnings": m.warnings,
            }
            for m in self.metrics_history
        ]
