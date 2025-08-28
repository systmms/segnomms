#!/usr/bin/env python3
"""Generate comprehensive performance report from benchmark data.

This script generates a performance report based on collected benchmark metrics,
checking for regressions and providing a summary of performance characteristics.

Usage:
    python repo/generate_performance_report.py

The script looks for performance metrics in tests/perf/performance_metrics.json
and generates a report at tests/perf/performance_report.txt.
"""

import sys
from pathlib import Path


def main():
    """Generate performance report from benchmark data."""
    # Check if performance metrics exist
    metrics_file = Path("tests/perf/performance_metrics.json")
    if not metrics_file.exists():
        print("⚠️  No performance metrics found. Generating placeholder report...")
        # Create a placeholder performance report
        report_path = Path("tests/perf/performance_report.txt")
        report_path.parent.mkdir(exist_ok=True)

        with open(report_path, "w") as f:
            f.write("Performance Benchmark Report\n")
            f.write("=" * 30 + "\n")
            f.write("Status: No performance metrics found\n")
            f.write("Action: Run benchmarks first with: make benchmark\n")
            f.write("\nPlaceholder report generated for CI workflow continuity.\n")

        print(f"📊 Placeholder report created at: {report_path}")
        return 0

    try:
        # Import performance monitor
        from tests.helpers.performance_monitor import PerformanceMonitor

        # Initialize monitor and generate report
        monitor = PerformanceMonitor()
        report_path = Path("tests/perf/performance_report.txt")
        report = monitor.generate_performance_report(report_path)
        assert report is not None  # Validate performance report generated

        print("📊 Performance report generated at: tests/perf/performance_report.txt")

        # Display summary
        if monitor.metrics:
            print(f"📈 Total metrics collected: {len(monitor.metrics)}")
            print(f"📊 Baselines established: {len(monitor.baselines)}")

            # Check for recent regressions
            alerts = monitor.alert_regressions()
            if alerts:
                print(f"⚠️  {len(alerts)} potential performance regressions detected!")
                for alert in alerts[:3]:  # Show first 3
                    time_ratio = alert.get("details", {}).get("time_ratio", "N/A")
                    print(f'   - {alert["name"]}: {time_ratio}x slower')
            else:
                print("✅ No performance regressions detected")
        else:
            print("⚠️  No performance metrics found. Run benchmarks first with: make benchmark")

        return 0

    except ImportError as e:
        print(f"❌ Error importing performance monitor: {e}")
        print("   Make sure performance testing dependencies are installed")
        return 1
    except Exception as e:
        print(f"❌ Error generating performance report: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
