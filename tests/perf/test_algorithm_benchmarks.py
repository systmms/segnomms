"""
Comprehensive algorithm benchmarking for critical SegnoMMS algorithms.

This module provides performance benchmarks for the most critical algorithms
in the SegnoMMS system to detect performance regressions and guide optimization efforts.
"""

import os
import statistics
import time
from dataclasses import dataclass
from typing import Callable, List, Tuple
from unittest.mock import Mock

import psutil
import pytest

from segnomms.algorithms.clustering import ConnectedComponentAnalyzer
from segnomms.config import RenderingConfig
from segnomms.core.detector import ModuleDetector
from segnomms.core.matrix.manipulator import MatrixManipulator
from segnomms.intents.processor import IntentProcessor
from segnomms.svg.path_clipper import PathClipper


@dataclass
class BenchmarkResult:
    """Benchmark result with timing and memory statistics."""

    name: str
    mean_time: float
    median_time: float
    std_dev: float
    min_time: float
    max_time: float
    memory_usage_mb: float
    iterations: int
    success_rate: float


class PerformanceBenchmarker:
    """Professional benchmarking framework for algorithms."""

    def __init__(self, iterations: int = 10, warmup_iterations: int = 3):
        """
        Initialize benchmarker.

        Args:
            iterations: Number of benchmark iterations
            warmup_iterations: Number of warmup runs to exclude from results
        """
        self.iterations = iterations
        self.warmup_iterations = warmup_iterations
        self.process = psutil.Process(os.getpid())

    def benchmark_function(self, func: Callable, *args, name: str = None, **kwargs) -> BenchmarkResult:
        """
        Benchmark a function with comprehensive timing and memory tracking.

        Args:
            func: Function to benchmark
            *args: Positional arguments for function
            name: Name for the benchmark
            **kwargs: Keyword arguments for function

        Returns:
            BenchmarkResult with comprehensive statistics
        """
        name = name or func.__name__
        times = []
        memory_before = self.process.memory_info().rss / 1024 / 1024  # MB
        success_count = 0

        # Warmup runs
        for _ in range(self.warmup_iterations):
            try:
                func(*args, **kwargs)
            except Exception:
                pass  # Ignore warmup failures

        # Benchmark runs
        for _ in range(self.iterations):
            try:
                start_time = time.perf_counter()
                result = func(*args, **kwargs)
                end_time = time.perf_counter()

                times.append(end_time - start_time)
                success_count += 1
            except Exception:
                # Record failed iterations but continue
                times.append(float("inf"))

        memory_after = self.process.memory_info().rss / 1024 / 1024  # MB
        memory_usage = memory_after - memory_before

        # Calculate statistics for successful runs only
        valid_times = [t for t in times if t != float("inf")]

        if not valid_times:
            # All runs failed
            return BenchmarkResult(
                name=name,
                mean_time=float("inf"),
                median_time=float("inf"),
                std_dev=float("inf"),
                min_time=float("inf"),
                max_time=float("inf"),
                memory_usage_mb=memory_usage,
                iterations=self.iterations,
                success_rate=0.0,
            )

        return BenchmarkResult(
            name=name,
            mean_time=statistics.mean(valid_times),
            median_time=statistics.median(valid_times),
            std_dev=statistics.stdev(valid_times) if len(valid_times) > 1 else 0.0,
            min_time=min(valid_times),
            max_time=max(valid_times),
            memory_usage_mb=memory_usage,
            iterations=self.iterations,
            success_rate=success_count / self.iterations,
        )


class TestAlgorithmBenchmarks:
    """Comprehensive benchmarks for critical SegnoMMS algorithms."""

    @pytest.fixture(scope="class")
    def benchmarker(self):
        """Create a benchmarker for the test class."""
        return PerformanceBenchmarker(iterations=10, warmup_iterations=3)

    @pytest.fixture(scope="class")
    def qr_matrices(self):
        """Create QR matrices of various sizes for benchmarking."""
        matrices = {}

        # Small QR (Version 1: 21x21)
        size_small = 21
        matrices["small"] = [[i % 2 == 0 for i in range(size_small)] for _ in range(size_small)]

        # Medium QR (Version 10: 57x57)
        size_medium = 57
        matrices["medium"] = [[i % 2 == 0 for i in range(size_medium)] for _ in range(size_medium)]

        # Large QR (Version 40: 177x177)
        size_large = 177
        matrices["large"] = [[i % 3 == 0 for i in range(size_large)] for _ in range(size_large)]

        return matrices

    @pytest.fixture(scope="class")
    def mock_detectors(self, qr_matrices):
        """Create mock detectors for each matrix size."""
        detectors = {}
        for size_name, matrix in qr_matrices.items():
            detector = Mock(spec=ModuleDetector)
            detector.get_module_type.return_value = "data"
            detectors[size_name] = detector
        return detectors

    @pytest.mark.slow
    @pytest.mark.benchmark
    def test_matrix_manipulator_benchmarks(self, benchmarker, qr_matrices, mock_detectors):
        """Benchmark MatrixManipulator operations across different QR sizes."""
        results = []

        for size_name, matrix in qr_matrices.items():
            detector = mock_detectors[size_name]

            # Benchmark MatrixManipulator creation
            result = benchmarker.benchmark_function(
                MatrixManipulator, matrix, detector, name=f"MatrixManipulator_create_{size_name}"
            )
            results.append(result)

            # Benchmark get_module_bounds operation
            manipulator = MatrixManipulator(matrix, detector)
            result = benchmarker.benchmark_function(
                manipulator.get_module_bounds, name=f"get_module_bounds_{size_name}"
            )
            results.append(result)

            # Benchmark centerpiece bounds calculation
            result = benchmarker.benchmark_function(
                manipulator.get_centerpiece_bounds, name=f"get_centerpiece_bounds_{size_name}"
            )
            results.append(result)

        self._report_benchmark_results("MatrixManipulator", results)
        self._assert_performance_thresholds(results)

    @pytest.mark.slow
    @pytest.mark.benchmark
    def test_clustering_algorithm_benchmarks(self, benchmarker, qr_matrices, mock_detectors):
        """Benchmark ConnectedComponentAnalyzer performance."""
        results = []

        # Test different connectivity modes
        connectivity_modes = ["4-way", "8-way"]

        for mode in connectivity_modes:
            analyzer = ConnectedComponentAnalyzer(
                min_cluster_size=3, density_threshold=0.5, connectivity_mode=mode
            )

            for size_name, matrix in qr_matrices.items():
                detector = mock_detectors[size_name]

                result = benchmarker.benchmark_function(
                    analyzer.process, matrix, detector, name=f"clustering_{mode}_{size_name}"
                )
                results.append(result)

        self._report_benchmark_results("ConnectedComponentAnalyzer", results)
        self._assert_performance_thresholds(results)

    @pytest.mark.slow
    @pytest.mark.benchmark
    def test_path_clipper_benchmarks(self, benchmarker):
        """Benchmark PathClipper operations."""
        results = []
        clipper = PathClipper()

        # Test different coordinate scenarios
        coordinate_sets = [
            ("center", [(50, 50)]),
            ("corners", [(0, 0), (100, 0), (0, 100), (100, 100)]),
            ("grid", [(x, y) for x in range(0, 100, 10) for y in range(0, 100, 10)]),
            ("large_grid", [(x, y) for x in range(0, 500, 25) for y in range(0, 500, 25)]),
        ]

        for scenario_name, coordinates in coordinate_sets:
            # Benchmark scale factor calculation
            def benchmark_scale_factors():
                return [clipper.get_scale_factor(x, y, distance=25) for x, y in coordinates]

            result = benchmarker.benchmark_function(
                benchmark_scale_factors, name=f"path_clipper_scale_{scenario_name}"
            )
            results.append(result)

        # Benchmark path clipping with complex paths
        complex_paths = {
            "simple": "M 10 10 L 50 50 Z",
            "medium": "M 0 0 L 50 0 Q 75 25 50 50 L 0 50 Z",
            "complex": " ".join(
                [
                    f"M {i} {i} L {i + 10} {i + 10} Q {i + 20} {i + 20} {i + 30} {i + 30}"
                    for i in range(0, 200, 40)
                ]
            )
            + " Z",
        }

        for path_name, path_data in complex_paths.items():
            result = benchmarker.benchmark_function(
                clipper.clip_path, path_data, name=f"path_clipping_{path_name}"
            )
            results.append(result)

        self._report_benchmark_results("PathClipper", results)
        self._assert_performance_thresholds(results)

    @pytest.mark.slow
    @pytest.mark.benchmark
    def test_intent_processor_benchmarks(self, benchmarker):
        """Benchmark IntentProcessor operations."""
        results = []
        config = RenderingConfig()
        processor = IntentProcessor(config)

        # Test different intent complexity levels
        intent_scenarios = [
            ("simple", {"shape": "circle", "scale": "large"}),
            (
                "medium",
                {
                    "shape": "rounded",
                    "scale": "medium",
                    "colors": "brand",
                    "interactive": True,
                    "centerpiece": True,
                },
            ),
            (
                "complex",
                {
                    "shape": "connected",
                    "scale": "large",
                    "colors": "gradient",
                    "interactive": True,
                    "centerpiece": True,
                    "frame": True,
                    "advanced": True,
                    "accessibility": True,
                },
            ),
            (
                "conflicting",
                {
                    "shape": "circle",
                    "geometry": {"shape": "square"},
                    "scale": "large",
                    "size": {"scale": 1},
                    "colors": "red",
                    "style": {"colors": "blue"},
                },
            ),
        ]

        for scenario_name, intents in intent_scenarios:
            result = benchmarker.benchmark_function(
                processor.process_intents, intents, name=f"intent_processing_{scenario_name}"
            )
            results.append(result)

        self._report_benchmark_results("IntentProcessor", results)
        self._assert_performance_thresholds(results)

    @pytest.mark.slow
    @pytest.mark.benchmark
    def test_configuration_creation_benchmarks(self, benchmarker):
        """Benchmark RenderingConfig creation and validation."""
        results = []

        # Test different configuration complexity levels
        config_scenarios = [
            ("minimal", {}),
            ("basic", {"scale": 10, "border": 4, "dark": "#000000"}),
            (
                "comprehensive",
                {
                    "scale": 15,
                    "border": 6,
                    "dark": "#1a1a2e",
                    "light": "#ffffff",
                    "shape": "rounded",
                    "corner_radius": 0.3,
                    "merge": "soft",
                    "connectivity": "8-way",
                    "interactive": True,
                    "tooltips": True,
                    "centerpiece_enabled": True,
                    "centerpiece_size": 0.15,
                    "frame_shape": "circle",
                    "frame_clip_mode": "fade",
                },
            ),
            (
                "kwargs_heavy",
                {
                    "scale": 20,
                    "shape": "connected",
                    "merge": "aggressive",
                    "enable_phase1": True,
                    "enable_phase2": True,
                    "enable_phase3": True,
                    "accessibility_enabled": True,
                    "patterns_enabled": True,
                    "frame_enabled": True,
                    "interactive": True,
                },
            ),
        ]

        for scenario_name, kwargs in config_scenarios:
            # Benchmark from_kwargs creation
            result = benchmarker.benchmark_function(
                RenderingConfig.from_kwargs, **kwargs, name=f"config_from_kwargs_{scenario_name}"
            )
            results.append(result)

            # Benchmark model_validate creation
            config_data = {"scale": kwargs.get("scale", 10)}
            result = benchmarker.benchmark_function(
                RenderingConfig.model_validate, config_data, name=f"config_model_validate_{scenario_name}"
            )
            results.append(result)

        self._report_benchmark_results("RenderingConfig", results)
        self._assert_performance_thresholds(results)

    def _report_benchmark_results(self, algorithm_name: str, results: List[BenchmarkResult]):
        """Report benchmark results in a formatted way."""
        print(f"\n{'=' * 60}")
        print(f"BENCHMARK RESULTS: {algorithm_name}")
        print(f"{'=' * 60}")

        for result in results:
            print(f"\n{result.name}:")
            print(f"  Mean time: {result.mean_time * 1000:.2f} ms")
            print(f"  Median time: {result.median_time * 1000:.2f} ms")
            print(f"  Std dev: {result.std_dev * 1000:.2f} ms")
            print(f"  Min / Max: {result.min_time * 1000:.2f} / {result.max_time * 1000:.2f} ms")
            print(f"  Memory usage: {result.memory_usage_mb:.2f} MB")
            print(f"  Success rate: {result.success_rate * 100:.1f}%")

            # Performance warnings
            if result.mean_time > 1.0:  # > 1 second
                print("  ⚠️  WARNING: High execution time")
            if result.memory_usage_mb > 50:  # > 50 MB
                print("  ⚠️  WARNING: High memory usage")
            if result.success_rate < 1.0:
                print("  ❌ WARNING: Failures detected")

    def _assert_performance_thresholds(self, results: List[BenchmarkResult]):
        """Assert that performance meets minimum thresholds."""
        for result in results:
            # All operations should complete successfully
            assert (
                result.success_rate >= 0.9
            ), f"{result.name} has low success rate: {result.success_rate * 100:.1f}%"

            # Performance thresholds (adjust based on requirements)
            if "small" in result.name:
                # Small QR operations should be very fast
                assert result.mean_time < 0.1, f"{result.name} too slow for small QR: {result.mean_time:.3f}s"
            elif "medium" in result.name:
                # Medium QR operations should be reasonably fast
                assert (
                    result.mean_time < 0.5
                ), f"{result.name} too slow for medium QR: {result.mean_time:.3f}s"
            elif "large" in result.name:
                # Large QR operations can be slower but should complete in reasonable time
                assert result.mean_time < 2.0, f"{result.name} too slow for large QR: {result.mean_time:.3f}s"
            else:
                # General operations should be fast
                assert result.mean_time < 1.0, f"{result.name} too slow: {result.mean_time:.3f}s"

            # Memory usage should be reasonable
            assert (
                result.memory_usage_mb < 100
            ), f"{result.name} uses too much memory: {result.memory_usage_mb:.1f}MB"


@pytest.mark.slow
@pytest.mark.benchmark
class TestScalabilityBenchmarks:
    """Test how algorithms scale with input size."""

    def test_matrix_manipulator_scaling(self):
        """Test how MatrixManipulator scales with QR code size."""
        benchmarker = PerformanceBenchmarker(iterations=5)

        # Test QR sizes from version 1 to 40
        qr_versions = [1, 5, 10, 20, 30, 40]
        qr_sizes = [4 * version + 17 for version in qr_versions]  # QR size formula

        results = []
        for version, size in zip(qr_versions, qr_sizes):
            # Create matrix of appropriate size
            matrix = [[i % 2 == 0 for i in range(size)] for _ in range(size)]
            detector = Mock(spec=ModuleDetector)
            detector.get_module_type.return_value = "data"

            # Benchmark creation and operations
            result = benchmarker.benchmark_function(
                self._matrix_operations_combined, matrix, detector, name=f"matrix_ops_v{version}_size{size}"
            )
            results.append((version, size, result))

        # Analyze scaling behavior
        self._analyze_scaling_behavior("MatrixManipulator", results)

    def test_clustering_scaling(self):
        """Test how clustering scales with QR code size."""
        benchmarker = PerformanceBenchmarker(iterations=5)
        analyzer = ConnectedComponentAnalyzer()

        qr_versions = [1, 5, 10, 15, 20]
        qr_sizes = [4 * version + 17 for version in qr_versions]

        results = []
        for version, size in zip(qr_versions, qr_sizes):
            # Create dense matrix (worst case for clustering)
            matrix = [[True] * size for _ in range(size)]
            detector = Mock(spec=ModuleDetector)
            detector.get_module_type.return_value = "data"

            result = benchmarker.benchmark_function(
                analyzer.process, matrix, detector, name=f"clustering_v{version}_size{size}"
            )
            results.append((version, size, result))

        self._analyze_scaling_behavior("ConnectedComponentAnalyzer", results)

    def _matrix_operations_combined(self, matrix, detector):
        """Combine multiple matrix operations for realistic benchmark."""
        manipulator = MatrixManipulator(matrix, detector)
        bounds = manipulator.get_module_bounds()
        centerpiece_bounds = manipulator.get_centerpiece_bounds()
        return bounds, centerpiece_bounds

    def _analyze_scaling_behavior(self, algorithm_name: str, results: List[Tuple]):
        """Analyze and report scaling behavior."""
        print(f"\n{'=' * 60}")
        print(f"SCALING ANALYSIS: {algorithm_name}")
        print(f"{'=' * 60}")

        for version, size, result in results:
            print(
                f"Version {version:2d} (Size {size:3d}x{size:3d}): "
                f"{result.mean_time * 1000:6.1f} ms "
                f"({result.memory_usage_mb:4.1f} MB)"
            )

        # Check for reasonable scaling (should be roughly O(n²) or better for matrix ops)
        times = [result.mean_time for _, _, result in results]
        sizes = [size * size for _, size, _ in results]  # Total modules

        if len(times) >= 3:
            # Simple scaling analysis: ratio between largest and smallest
            time_ratio = times[-1] / times[0]
            size_ratio = sizes[-1] / sizes[0]

            print(f"\nScaling factor: {time_ratio:.1f}x time for {size_ratio:.1f}x size")

            # Alert if scaling is worse than O(n²)
            if time_ratio > size_ratio * 2:
                print("⚠️  WARNING: Potentially poor scaling behavior")
            else:
                print("✅ Scaling behavior appears reasonable")
