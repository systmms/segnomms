"""
Memory profiling and leak detection tests for SegnoMMS.

This module provides comprehensive memory usage analysis and leak detection
for critical operations to ensure optimal memory management.
"""

import gc
import os
from dataclasses import dataclass
from typing import Any, Dict, List
from unittest.mock import Mock

import psutil
import pytest

from segnomms.algorithms.clustering import ConnectedComponentAnalyzer
from segnomms.config import RenderingConfig
from segnomms.core.detector import ModuleDetector
from segnomms.core.matrix.manipulator import MatrixManipulator


@dataclass
class MemorySnapshot:
    """Memory usage snapshot."""

    rss_mb: float  # Resident Set Size
    vms_mb: float  # Virtual Memory Size
    percent: float  # Memory percentage
    timestamp: str
    operation: str


class MemoryProfiler:
    """Memory profiling and leak detection utility."""

    def __init__(self) -> None:
        self.process = psutil.Process(os.getpid())
        self.snapshots: List[MemorySnapshot] = []

    def take_snapshot(self, operation: str = "unknown") -> MemorySnapshot:
        """Take a memory usage snapshot."""
        memory_info = self.process.memory_info()
        memory_percent = self.process.memory_percent()

        snapshot = MemorySnapshot(
            rss_mb=memory_info.rss / 1024 / 1024,
            vms_mb=memory_info.vms / 1024 / 1024,
            percent=memory_percent,
            timestamp=str(len(self.snapshots)),
            operation=operation,
        )

        self.snapshots.append(snapshot)
        return snapshot

    def detect_memory_leak(
        self, baseline_snapshot: MemorySnapshot, threshold_mb: float = 10.0
    ) -> Dict[str, Any]:
        """
        Detect potential memory leaks by comparing against baseline.

        Args:
            baseline_snapshot: Initial memory snapshot
            threshold_mb: Memory increase threshold to consider a leak

        Returns:
            Dictionary with leak detection results
        """
        if not self.snapshots:
            return {"leak_detected": False, "reason": "No snapshots available"}

        current_snapshot = self.snapshots[-1]
        memory_increase = current_snapshot.rss_mb - baseline_snapshot.rss_mb

        return {
            "leak_detected": memory_increase > threshold_mb,
            "memory_increase_mb": memory_increase,
            "threshold_mb": threshold_mb,
            "baseline_mb": baseline_snapshot.rss_mb,
            "current_mb": current_snapshot.rss_mb,
            "operations_since_baseline": len(self.snapshots) - int(baseline_snapshot.timestamp) - 1,
        }

    def analyze_memory_growth(self) -> Dict[str, Any]:
        """Analyze memory growth pattern across all snapshots."""
        if len(self.snapshots) < 2:
            return {"error": "Need at least 2 snapshots for growth analysis"}

        memory_values = [s.rss_mb for s in self.snapshots]

        # Calculate growth statistics
        total_growth = memory_values[-1] - memory_values[0]
        max_memory = max(memory_values)
        min_memory = min(memory_values)
        avg_memory = sum(memory_values) / len(memory_values)

        # Detect significant growth periods
        growth_periods = []
        for i in range(1, len(memory_values)):
            growth = memory_values[i] - memory_values[i - 1]
            if growth > 5.0:  # >5MB growth
                growth_periods.append(
                    {
                        "from_operation": self.snapshots[i - 1].operation,
                        "to_operation": self.snapshots[i].operation,
                        "growth_mb": growth,
                    }
                )

        return {
            "total_growth_mb": total_growth,
            "max_memory_mb": max_memory,
            "min_memory_mb": min_memory,
            "avg_memory_mb": avg_memory,
            "memory_range_mb": max_memory - min_memory,
            "growth_periods": growth_periods,
            "snapshots_count": len(self.snapshots),
        }


class TestMemoryProfiling:
    """Comprehensive memory profiling tests."""

    @pytest.fixture
    def profiler(self) -> MemoryProfiler:
        """Create a memory profiler for testing."""
        return MemoryProfiler()

    @pytest.fixture
    def qr_matrices(self) -> Dict[str, List[List[bool]]]:
        """Create QR matrices for memory testing."""
        matrices = {}

        # Small matrix (21x21)
        matrices["small"] = [[i % 2 == 0 for i in range(21)] for _ in range(21)]

        # Medium matrix
        matrices["medium"] = [[i % 2 == 0 for i in range(57)] for _ in range(57)]

        # Large matrix
        matrices["large"] = [[i % 3 == 0 for i in range(177)] for _ in range(177)]

        return matrices

    @pytest.mark.slow
    def test_matrix_manipulator_memory_usage(
        self, profiler: MemoryProfiler, qr_matrices: Dict[str, List[List[bool]]]
    ) -> None:
        """Test memory usage patterns of MatrixManipulator."""
        baseline = profiler.take_snapshot("baseline")

        manipulators = []

        for size_name, matrix in qr_matrices.items():
            detector = Mock(spec=ModuleDetector)
            detector.get_module_type.return_value = "data"
            # Mock get_neighbors to return empty list (no neighbors to process)
            detector.get_neighbors.return_value = []

            # Create manipulator and take snapshot
            manipulator = MatrixManipulator(matrix, detector)
            manipulators.append(manipulator)  # Keep reference to prevent GC

            profiler.take_snapshot(f"create_{size_name}_manipulator")

            # Perform operations
            manipulator.get_module_bounds()  # Perform operation for memory testing
            profiler.take_snapshot(f"{size_name}_get_bounds")

        # Analyze memory usage
        analysis = profiler.analyze_memory_growth()

        # Memory should not grow excessively
        assert (
            analysis["total_growth_mb"] < 50
        ), f"Excessive memory growth: {analysis['total_growth_mb']:.1f}MB"

        # Check for potential leaks
        leak_result = profiler.detect_memory_leak(baseline, threshold_mb=30)
        assert not leak_result["leak_detected"], f"Potential memory leak detected: {leak_result}"

        # Report memory usage
        self._report_memory_analysis("MatrixManipulator", analysis)

    @pytest.mark.slow
    def test_clustering_memory_usage(
        self, profiler: MemoryProfiler, qr_matrices: Dict[str, List[List[bool]]]
    ) -> None:
        """Test memory usage of clustering algorithms."""
        baseline = profiler.take_snapshot("clustering_baseline")

        for size_name, matrix in qr_matrices.items():
            # Create fresh analyzer instance for each matrix to prevent memory accumulation
            analyzer = ConnectedComponentAnalyzer()

            detector = Mock(spec=ModuleDetector)
            detector.get_module_type.return_value = "data"
            # Mock get_neighbors to return empty list (no neighbors to process)
            detector.get_neighbors.return_value = []

            # Perform clustering and monitor memory
            clusters = analyzer.process(matrix, detector)
            profiler.take_snapshot(f"clustering_{size_name}")

            # Force cleanup
            del clusters
            del analyzer  # Explicitly delete analyzer instance
            del detector  # Explicitly delete mock detector
            gc.collect()
            profiler.take_snapshot(f"clustering_{size_name}_cleanup")

        analysis = profiler.analyze_memory_growth()

        # Check for memory leaks in clustering
        leak_result = profiler.detect_memory_leak(baseline, threshold_mb=25)
        assert not leak_result["leak_detected"], f"Clustering memory leak: {leak_result}"

        self._report_memory_analysis("Clustering", analysis)

    @pytest.mark.slow
    def test_config_creation_memory_usage(self, profiler: MemoryProfiler) -> None:
        """Test memory usage of configuration creation."""
        baseline = profiler.take_snapshot("config_baseline")

        configs = []

        # Create many configurations to test for leaks
        for i in range(100):
            config = RenderingConfig.from_kwargs(
                scale=10 + i % 10,
                border=4,
                dark=f"#{'%06x' % (i * 1000 % 0xFFFFFF)}",
                shape="circle" if i % 2 else "square",
                interactive=True,
                centerpiece_enabled=True,
            )
            configs.append(config)

            if i % 20 == 19:  # Take snapshot every 20 iterations
                profiler.take_snapshot(f"config_batch_{i // 20}")

        # Cleanup and check for leaks
        del configs
        gc.collect()
        profiler.take_snapshot("config_cleanup")

        analysis = profiler.analyze_memory_growth()
        leak_result = profiler.detect_memory_leak(baseline, threshold_mb=15)

        assert not leak_result["leak_detected"], f"Config creation memory leak: {leak_result}"

        self._report_memory_analysis("ConfigCreation", analysis)

    def test_memory_intensive_operations(self, profiler: MemoryProfiler) -> None:
        """Test memory usage during intensive operations."""
        baseline = profiler.take_snapshot("intensive_baseline")

        # Simulate intensive matrix operations
        large_matrices = []

        try:
            for i in range(10):
                # Create progressively larger matrices
                size = 50 + i * 20
                matrix = [[j % 2 == 0 for j in range(size)] for _ in range(size)]
                large_matrices.append(matrix)

                detector = Mock(spec=ModuleDetector)
                detector.get_module_type.return_value = "data"

                manipulator = MatrixManipulator(matrix, detector)
                bounds = manipulator.get_module_bounds()

                profiler.take_snapshot(f"intensive_op_{i}")

                # Cleanup manipulator
                del manipulator
                del bounds

        finally:
            # Ensure cleanup
            del large_matrices
            gc.collect()
            profiler.take_snapshot("intensive_cleanup")

        analysis = profiler.analyze_memory_growth()

        # Memory should return to reasonable levels after cleanup
        final_snapshot = profiler.snapshots[-1]
        memory_increase = final_snapshot.rss_mb - baseline.rss_mb

        assert memory_increase < 20, f"Memory not properly released: {memory_increase:.1f}MB still allocated"

        self._report_memory_analysis("IntensiveOperations", analysis)

    def test_repeated_operations_memory_stability(self, profiler: MemoryProfiler) -> None:
        """Test memory stability during repeated operations."""
        baseline = profiler.take_snapshot("stability_baseline")

        # Repeated operations should not accumulate memory
        matrix = [[i % 2 == 0 for i in range(21)] for _ in range(21)]
        detector = Mock(spec=ModuleDetector)
        detector.get_module_type.return_value = "data"

        for i in range(50):
            # Create, use, and dispose of manipulator
            manipulator = MatrixManipulator(matrix, detector)
            manipulator.get_module_bounds()  # Perform operation for memory testing

            # Cleanup
            del manipulator

            if i % 10 == 9:
                gc.collect()
                profiler.take_snapshot(f"stability_iter_{i}")

        analysis = profiler.analyze_memory_growth()

        # Memory should remain stable across iterations
        assert (
            analysis["total_growth_mb"] < 10
        ), f"Memory instability detected: {analysis['total_growth_mb']:.1f}MB growth"

        # Check that cleanup is working
        leak_result = profiler.detect_memory_leak(baseline, threshold_mb=8)
        assert not leak_result["leak_detected"], f"Memory not being released properly: {leak_result}"

        self._report_memory_analysis("RepeatedOperations", analysis)

    def _report_memory_analysis(self, test_name: str, analysis: Dict[str, Any]) -> None:
        """Report memory analysis results."""
        print(f"\n{'=' * 50}")
        print(f"MEMORY ANALYSIS: {test_name}")
        print(f"{'=' * 50}")
        print(f"Total growth: {analysis.get('total_growth_mb', 0):.1f} MB")
        print(f"Peak memory: {analysis.get('max_memory_mb', 0):.1f} MB")
        print(f"Average memory: {analysis.get('avg_memory_mb', 0):.1f} MB")
        print(f"Memory range: {analysis.get('memory_range_mb', 0):.1f} MB")
        print(f"Snapshots taken: {analysis.get('snapshots_count', 0)}")

        growth_periods = analysis.get("growth_periods", [])
        if growth_periods:
            print("\nSignificant growth periods:")
            for period in growth_periods:
                print(
                    f"  {period['from_operation']} -> {period['to_operation']}: "
                    f"{period['growth_mb']:.1f} MB"
                )
        else:
            print("\n✅ No significant memory growth periods detected")


@pytest.mark.slow
class TestMemoryLeakDetection:
    """Specific tests for memory leak detection."""

    def test_no_memory_leaks_in_basic_operations(self) -> None:
        """Ensure basic operations don't leak memory."""
        profiler = MemoryProfiler()
        baseline = profiler.take_snapshot("leak_test_baseline")

        # Perform many basic operations
        for i in range(100):
            config = RenderingConfig(scale=10, border=4)

            # Create and immediately discard objects
            matrix = [[True, False] * 10 for _ in range(20)]
            detector = Mock(spec=ModuleDetector)
            detector.get_module_type.return_value = "data"
            # Mock get_neighbors to return empty list (no neighbors to process)
            detector.get_neighbors.return_value = []

            manipulator = MatrixManipulator(matrix, detector)
            bounds = manipulator.get_module_bounds()

            # Explicit cleanup
            del config, matrix, detector, manipulator, bounds

            # Periodic garbage collection and memory check
            if i % 25 == 24:
                gc.collect()
                profiler.take_snapshot(f"leak_check_{i // 25}")

        # Final cleanup and check
        gc.collect()
        profiler.take_snapshot("leak_test_final")

        leak_result = profiler.detect_memory_leak(baseline, threshold_mb=5)

        assert not leak_result["leak_detected"], f"Memory leak in basic operations: {leak_result}"

    def test_clustering_memory_release(self) -> None:
        """Test that clustering properly releases memory."""
        profiler = MemoryProfiler()
        baseline = profiler.take_snapshot("clustering_leak_baseline")

        # Process many matrices and ensure memory is released
        for i in range(20):
            # Create fresh analyzer instance for each iteration
            analyzer = ConnectedComponentAnalyzer()

            size = 30 + i
            matrix = [[True] * size for _ in range(size)]  # Dense matrix
            detector = Mock(spec=ModuleDetector)
            detector.get_module_type.return_value = "data"
            # Mock get_neighbors to return empty list (no neighbors to process)
            detector.get_neighbors.return_value = []

            clusters = analyzer.process(matrix, detector)

            # Explicit cleanup
            del matrix, detector, clusters, analyzer

            if i % 5 == 4:
                gc.collect()
                profiler.take_snapshot(f"clustering_leak_check_{i // 5}")

        gc.collect()
        profiler.take_snapshot("clustering_leak_final")

        leak_result = profiler.detect_memory_leak(baseline, threshold_mb=8)
        assert not leak_result["leak_detected"], f"Memory leak in clustering: {leak_result}"
