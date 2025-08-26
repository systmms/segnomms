"""
Performance tests for example generation.

Tests the performance of generating QR codes with various configurations.
"""

import json
import time
from pathlib import Path
from typing import Any, Dict, List

import pytest
import segno

from segnomms import write


class TestExampleGenerationPerformance:
    """Test performance of generating examples with different configurations."""

    @pytest.fixture(autouse=True)
    def setup(self, examples_generated_dir: Path) -> None:
        """Setup for performance testing."""
        self.output_dir = examples_generated_dir
        self.performance_dir = self.output_dir / "performance"
        self.performance_dir.mkdir(exist_ok=True)

    @pytest.mark.visual
    @pytest.mark.slow
    def test_generate_performance_samples(self) -> None:
        """Generate samples for performance testing."""
        sizes = [
            ("small", "Hello", "L"),
            ("medium", "https://example.com/medium-complexity-url", "M"),
            ("large", "A" * 500, "H"),  # Large data
            ("complex", "https://github.com/" + "x" * 100, "H"),  # High version QR
        ]

        performance_data = []

        for size_name, data, error in sizes:
            qr = segno.make(data, error=error)

            # Test each shape
            for shape in ["square", "circle", "connected"]:
                start_time = time.time()

                output_path = self.performance_dir / f"{size_name}_{shape}.svg"
                write(
                    qr,
                    str(output_path),
                    shape=shape,
                    scale=10,
                    border=2,
                    style_interactive=True,
                )

                generation_time = time.time() - start_time

                performance_data.append(
                    {
                        "size": size_name,
                        "shape": shape,
                        "version": qr.version,
                        "modules": len(qr.matrix) ** 2,
                        "time_ms": generation_time * 1000,
                    }
                )

        # Save performance data
        perf_file = self.performance_dir / "performance_data.json"
        perf_file.write_text(json.dumps(performance_data, indent=2))

    @pytest.mark.slow
    def test_shape_rendering_performance(self) -> None:
        """Test performance of different shape renderers."""
        shapes = [
            "square",
            "circle",
            "rounded",
            "diamond",
            "star",
            "hexagon",
            "triangle",
            "cross",
            "connected",
            "connected-extra-rounded",
        ]

        qr = segno.make("Performance test data", error="M")
        performance_results = []

        for shape in shapes:
            # Warm up
            write(qr, "/dev/null", shape=shape, scale=10)

            # Measure
            times = []
            for _ in range(5):
                start_time = time.time()
                write(
                    qr,
                    "/dev/null",
                    shape=shape,
                    scale=10,
                    border=2,
                    style_interactive=False,
                )
                times.append((time.time() - start_time) * 1000)

            avg_time = sum(times) / len(times)
            performance_results.append(
                {
                    "shape": shape,
                    "avg_time_ms": avg_time,
                    "min_time_ms": min(times),
                    "max_time_ms": max(times),
                }
            )

        # Save performance comparison
        perf_file = self.performance_dir / "shape_performance_comparison.json"
        perf_file.write_text(json.dumps(performance_results, indent=2))

    @pytest.mark.slow
    def test_scale_performance(self) -> None:
        """Test performance impact of different scale values."""
        scales = [5, 10, 20, 50, 100]
        qr = segno.make("Scale performance test", error="M")

        performance_results = []

        for scale in scales:
            start_time = time.time()

            write(
                qr,
                "/dev/null",
                shape="rounded",
                scale=scale,
                border=2,
                style_interactive=True,
            )

            generation_time = (time.time() - start_time) * 1000

            size_width, size_height = qr.symbol_size(border=2)
            performance_results.append(
                {
                    "scale": scale,
                    "time_ms": generation_time,
                    "pixels_per_module": scale,
                    "total_pixels": (size_width * scale) * (size_height * scale),
                }
            )

        # Save scale performance data
        perf_file = self.performance_dir / "scale_performance.json"
        perf_file.write_text(json.dumps(performance_results, indent=2))

    @pytest.mark.slow
    def test_interactive_features_overhead(self) -> None:
        """Test performance overhead of interactive features."""
        qr = segno.make("Interactive overhead test", error="M")

        configs: List[Dict[str, Any]] = [
            {"name": "baseline", "config": {}},
            {"name": "interactive", "config": {"style_interactive": True}},
            {
                "name": "tooltips",
                "config": {"style_interactive": True, "style_tooltips": True},
            },
            {
                "name": "custom_css",
                "config": {
                    "style_interactive": True,
                    "style_custom_css": ".qr-module:hover { fill: red; }",
                },
            },
            {
                "name": "full_features",
                "config": {
                    "style_interactive": True,
                    "style_tooltips": True,
                    "style_css_classes": {
                        "data": "custom-data",
                        "finder": "custom-finder",
                    },
                    "style_custom_css": ".qr-module:hover { transform: scale(1.1); }",
                },
            },
        ]

        performance_results = []

        for test_config in configs:
            times = []
            for _ in range(10):
                start_time = time.time()

                write(
                    qr,
                    "/dev/null",
                    shape="rounded",
                    scale=10,
                    border=2,
                    **test_config["config"],
                )

                times.append((time.time() - start_time) * 1000)

            avg_time = sum(times) / len(times)
            performance_results.append(
                {
                    "config": test_config["name"],
                    "avg_time_ms": avg_time,
                    "overhead_pct": 0,  # Will calculate after baseline
                }
            )

        # Calculate overhead percentages
        baseline_time: float = performance_results[0]["avg_time_ms"]
        for result in performance_results:
            result["overhead_pct"] = ((float(result["avg_time_ms"]) - baseline_time) / baseline_time) * 100

        # Save interactive overhead data
        perf_file = self.performance_dir / "interactive_overhead.json"
        perf_file.write_text(json.dumps(performance_results, indent=2))
