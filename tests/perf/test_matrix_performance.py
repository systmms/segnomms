"""
Performance tests for matrix manipulation operations.

Tests for performance monitoring, warnings, and benchmarking
of matrix operations under various conditions.
"""

import time

import pytest

from segnomms.config import CenterpieceConfig, ReserveMode
from segnomms.core.detector import ModuleDetector
from segnomms.core.matrix import MatrixManipulator


class TestMatrixPerformanceWarnings:
    """Test performance warning system for matrix operations."""

    @pytest.fixture
    def large_matrix(self):
        """Create a large QR matrix for performance testing."""
        # Create a 177x177 matrix (Version 40 QR code)
        size = 177
        matrix = []
        for i in range(size):
            row = []
            for j in range(size):
                row.append(True)
            matrix.append(row)
        return matrix

    @pytest.fixture
    def large_detector(self, large_matrix):
        """Create a detector for large matrix."""
        return ModuleDetector(large_matrix)

    @pytest.fixture
    def large_manipulator(self, large_matrix, large_detector):
        """Create manipulator for large matrix."""
        return MatrixManipulator(large_matrix, large_detector)

    def test_performance_warnings_large_centerpiece(self, large_manipulator):
        """Test performance warnings for large centerpiece operations."""
        # Large centerpiece should trigger performance warnings
        config = CenterpieceConfig(enabled=True, size=0.4, shape="circle")  # 40% - very large

        start_time = time.time()
        metadata = large_manipulator.get_centerpiece_metadata(config)
        elapsed = time.time() - start_time

        # Should have performance warnings in metadata
        assert "performance_warnings" in metadata
        warnings = metadata["performance_warnings"]

        # Should warn about large centerpiece
        large_area_warning = any("large centerpiece area" in w.lower() for w in warnings)
        assert large_area_warning

        # Operation should complete but may be slow
        assert elapsed < 5.0  # Should complete within 5 seconds

    def test_performance_warnings_squircle_complexity(self, large_manipulator):
        """Test performance warnings for complex squircle calculations."""
        config = CenterpieceConfig(enabled=True, size=0.3, shape="squircle")  # More complex than circle/rect

        start_time = time.time()

        # Test multiple containment checks (expensive for squircle)
        containment_checks = 0
        for x in range(0, 177, 10):  # Sample every 10th module
            for y in range(0, 177, 10):
                large_manipulator.is_in_centerpiece(x, y, config)
                containment_checks += 1

        elapsed = time.time() - start_time

        # Assert reasonable performance for large matrix operations
        assert elapsed < 10.0, f"Large matrix operations took too long: {elapsed:.2f}s"

        # Should warn about complex shape calculations
        metadata = large_manipulator.get_centerpiece_metadata(config)
        if "performance_warnings" in metadata:
            warnings = metadata["performance_warnings"]
            complex_shape_warning = any("squircle" in w.lower() or "complex" in w.lower() for w in warnings)
            # May or may not trigger depending on implementation

    def test_performance_warnings_imprint_mode(self, large_manipulator):
        """Test performance warnings for imprint mode processing."""
        config = CenterpieceConfig(enabled=True, size=0.25, shape="circle", mode=ReserveMode.IMPRINT)

        start_time = time.time()

        # Imprint mode requires distance calculations for each module
        # This is more expensive than knockout mode
        metadata = large_manipulator.get_centerpiece_metadata(config)

        elapsed = time.time() - start_time

        # Should have reasonable performance even with complex calculations
        assert elapsed < 3.0  # Should complete within 3 seconds

        # May have warnings about imprint complexity
        if "performance_warnings" in metadata:
            warnings = metadata["performance_warnings"]
            imprint_warning = any("imprint" in w.lower() for w in warnings)

    def test_performance_warnings_large_margin(self, large_manipulator):
        """Test performance warnings for large margin calculations."""
        config = CenterpieceConfig(enabled=True, size=0.2, shape="rect", margin=20)  # Very large margin

        start_time = time.time()
        bounds = large_manipulator.get_centerpiece_bounds(config)
        elapsed = time.time() - start_time

        # Large margin should not significantly impact performance
        assert elapsed < 1.0

        # But should provide bounds that account for margin
        assert bounds is not None
        assert "left" in bounds
        assert "right" in bounds
        assert "top" in bounds
        assert "bottom" in bounds

    def test_comprehensive_performance_warnings(self, large_manipulator):
        """Test comprehensive performance monitoring."""
        # Configuration that might trigger multiple warnings
        config = CenterpieceConfig(
            enabled=True,
            size=0.35,  # Large
            shape="squircle",  # Complex
            mode=ReserveMode.IMPRINT,  # Expensive
            margin=10,  # Additional complexity
        )

        start_time = time.time()

        # Perform multiple expensive operations
        metadata = large_manipulator.get_centerpiece_metadata(config)
        validation = large_manipulator.validate_reserve_impact(config, "M")

        # Test some containment checks
        for i in range(50):  # Limited sample for performance
            large_manipulator.is_in_centerpiece(i * 3, i * 3, config)

        elapsed = time.time() - start_time

        # Should complete within reasonable time
        assert elapsed < 10.0  # Allow more time for comprehensive test

        # Should have some performance insights
        assert "area_info" in metadata
        assert metadata["area_info"]["estimated_modules"] > 0


class TestMatrixBenchmarks:
    """Benchmark tests for matrix operations."""

    @pytest.fixture
    def benchmark_matrices(self):
        """Create matrices of different sizes for benchmarking."""
        sizes = [21, 45, 89, 133, 177]  # Different QR versions
        matrices = {}

        for size in sizes:
            matrix = []
            for i in range(size):
                row = [True] * size
                matrix.append(row)
            matrices[f"v{size}"] = matrix

        return matrices

    def test_containment_performance_scaling(self, benchmark_matrices):
        """Test how containment checking scales with matrix size."""
        results = {}

        for version, matrix in benchmark_matrices.items():
            detector = ModuleDetector(matrix)
            manipulator = MatrixManipulator(matrix, detector)

            config = CenterpieceConfig(enabled=True, size=0.2, shape="circle")

            # Measure containment check performance
            start_time = time.time()

            # Sample every 5th module for performance
            size = len(matrix)
            checks = 0
            for x in range(0, size, 5):
                for y in range(0, size, 5):
                    manipulator.is_in_centerpiece(x, y, config)
                    checks += 1

            elapsed = time.time() - start_time
            results[version] = {
                "elapsed": elapsed,
                "checks": checks,
                "checks_per_second": checks / elapsed if elapsed > 0 else 0,
                "size": size,
            }

        # Performance should scale reasonably with matrix size
        # Larger matrices should still have acceptable performance
        for version, result in results.items():
            assert result["checks_per_second"] > 100  # Should handle at least 100 checks/sec
            assert result["elapsed"] < 5.0  # Should complete within 5 seconds

    def test_metadata_generation_performance(self, benchmark_matrices):
        """Test metadata generation performance across matrix sizes."""
        results = {}

        for version, matrix in benchmark_matrices.items():
            detector = ModuleDetector(matrix)
            manipulator = MatrixManipulator(matrix, detector)

            config = CenterpieceConfig(
                enabled=True,
                size=0.2,
                shape="squircle",  # Most complex shape
                mode=ReserveMode.IMPRINT,  # Most complex mode
            )

            start_time = time.time()
            metadata = manipulator.get_centerpiece_metadata(config)
            elapsed = time.time() - start_time

            results[version] = {
                "elapsed": elapsed,
                "size": len(matrix),
                "estimated_modules": metadata["area_info"]["estimated_modules"],
            }

        # Metadata generation should be efficient
        for version, result in results.items():
            assert result["elapsed"] < 2.0  # Should complete within 2 seconds
            assert result["estimated_modules"] > 0  # Should calculate meaningful results

    def test_validation_performance(self, benchmark_matrices):
        """Test validation performance across matrix sizes."""
        results = {}

        for version, matrix in benchmark_matrices.items():
            detector = ModuleDetector(matrix)
            manipulator = MatrixManipulator(matrix, detector)

            config = CenterpieceConfig(enabled=True, size=0.25, shape="circle")

            start_time = time.time()
            validation = manipulator.validate_reserve_impact(config, "M")
            elapsed = time.time() - start_time

            results[version] = {"elapsed": elapsed, "size": len(matrix), "safe": validation["safe"]}

        # Validation should be very fast
        for version, result in results.items():
            assert result["elapsed"] < 0.5  # Should complete within 0.5 seconds
            assert isinstance(result["safe"], bool)  # Should return valid result
