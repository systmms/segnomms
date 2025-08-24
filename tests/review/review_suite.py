"""Visual review suite orchestrator for SegnoMMS testing."""

import json
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .html_generator import HTMLGenerator


class ReviewSuite:
    """Orchestrates the generation of the visual review suite."""
    
    def __init__(self, project_root: Optional[Path] = None):
        """Initialize the review suite.
        
        Args:
            project_root: Root directory of the project
        """
        self.project_root = project_root or Path.cwd()
        self.tests_dir = self.project_root / "tests"
        self.review_dir = self.tests_dir / "review"
        self.output_dir = self.review_dir / "output"
        self.generator = HTMLGenerator()
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def collect_test_results(self) -> Dict[str, Any]:
        """Collect test results from various sources.
        
        Returns:
            Dictionary with test results (passed, failed, total, coverage)
        """
        results = {
            'passed': 0,
            'failed': 0,
            'total': 0,
            'coverage': None,
            'duration': None,
            'timestamp': datetime.now().isoformat()
        }
        
        # Try to load pytest JSON report
        test_report = self.project_root / "test-report.json"
        if test_report.exists():
            try:
                with open(test_report) as f:
                    report_data = json.load(f)
                    summary = report_data.get('summary', {})
                    results['passed'] = summary.get('passed', 0)
                    results['failed'] = summary.get('failed', 0)
                    results['total'] = summary.get('total', 0)
                    results['duration'] = report_data.get('duration', 0)
            except (json.JSONDecodeError, KeyError):
                pass
        
        # Try to load coverage data
        coverage_file = self.project_root / "coverage.json"
        if coverage_file.exists():
            try:
                with open(coverage_file) as f:
                    coverage_data = json.load(f)
                    results['coverage'] = coverage_data['totals']['percent_covered']
            except (json.JSONDecodeError, KeyError):
                pass
        
        return results
    
    def collect_visual_tests(self) -> List[Dict[str, Any]]:
        """Collect visual test results.
        
        Returns:
            List of visual test results with baseline/actual comparisons
        """
        visual_tests = []
        
        baseline_dir = self.tests_dir / "visual" / "baseline"
        output_dir = self.tests_dir / "visual" / "output"
        
        if not baseline_dir.exists() or not output_dir.exists():
            return visual_tests
        
        # Find all baseline SVGs
        for baseline_file in sorted(baseline_dir.glob("*.baseline.svg")):
            test_name = baseline_file.stem.replace(".baseline", "")
            actual_file = output_dir / f"{test_name}.actual.svg"
            
            if actual_file.exists():
                # Load SVG contents
                baseline_content = baseline_file.read_text()
                actual_content = actual_file.read_text()
                
                # Check for config file
                config_file = baseline_dir / f"{test_name}.baseline_config.json"
                config = None
                if config_file.exists():
                    try:
                        config = json.loads(config_file.read_text())
                    except json.JSONDecodeError:
                        pass
                
                visual_tests.append({
                    'name': test_name,
                    'baseline': baseline_content,
                    'actual': actual_content,
                    'status': 'pending',  # Will be updated by user review
                    'config': config,
                    'baseline_path': str(baseline_file.relative_to(self.project_root)),
                    'actual_path': str(actual_file.relative_to(self.project_root))
                })
        
        return visual_tests
    
    def collect_shape_gallery(self) -> List[Dict[str, Any]]:
        """Collect shape gallery items from test outputs.
        
        Returns:
            List of gallery items for shape comparison
        """
        gallery_items = []
        
        # Look for generated shape examples
        shapes_dir = self.tests_dir / "visual" / "output"
        if not shapes_dir.exists():
            return gallery_items
        
        # Define shape types we're looking for
        shape_types = [
            'square', 'circle', 'rounded', 'diamond', 'star',
            'hexagon', 'triangle', 'cross', 'connected',
            'connected-extra-rounded', 'squircle', 'dot'
        ]
        
        for shape in shape_types:
            safe_on_file = shapes_dir / f"{shape}_safe_on.actual.svg"
            safe_off_file = shapes_dir / f"{shape}_safe_off.actual.svg"
            
            if safe_on_file.exists() and safe_off_file.exists():
                gallery_items.append({
                    'title': shape.replace('-', ' ').title(),
                    'shape': shape,
                    'comparison': True,
                    'safe_on_svg': safe_on_file.read_text(),
                    'safe_off_svg': safe_off_file.read_text(),
                    'description': f'Shape type: {shape}'
                })
        
        return gallery_items
    
    def copy_assets(self) -> None:
        """Copy CSS and JS assets to output directory."""
        assets_src = self.review_dir / "assets"
        assets_dst = self.output_dir / "assets"
        
        if assets_src.exists():
            shutil.copytree(assets_src, assets_dst, dirs_exist_ok=True)
    
    def generate_review_pages(self) -> None:
        """Generate all review pages."""
        print("🎨 Generating Visual Review Suite...")
        
        # Collect data
        print("  📊 Collecting test results...")
        test_results = self.collect_test_results()
        
        print("  🖼️ Collecting visual tests...")
        visual_tests = self.collect_visual_tests()
        
        print("  🎨 Collecting shape gallery...")
        shape_gallery = self.collect_shape_gallery()
        
        # Copy assets
        print("  📁 Copying assets...")
        self.copy_assets()
        
        # Calculate visual stats
        visual_stats = {
            'pending': len(visual_tests),
            'approved': 0,
            'rejected': 0
        }
        
        # Generate dashboard
        print("  📄 Generating dashboard...")
        dashboard_html = self.generator.generate_dashboard(
            test_results=test_results,
            visual_stats=visual_stats,
            recent_activity=self._get_recent_activity()
        )
        (self.output_dir / "index.html").write_text(dashboard_html)
        
        # Generate shape gallery
        if shape_gallery:
            print("  🎨 Generating shape gallery...")
            gallery_html = self.generator.generate_gallery_page(
                gallery_items=shape_gallery,
                title="Shape Gallery - Safe Mode Comparison",
                description=(
                    "<strong>Safe Mode:</strong> When enabled (default), functional QR patterns "
                    "(finder, timing, alignment) are always rendered as squares to ensure scannability. "
                    "When disabled, all patterns use the selected shape."
                )
            )
            (self.output_dir / "gallery.html").write_text(gallery_html)
        
        # Generate individual diff pages
        if visual_tests:
            print(f"  🔍 Generating {len(visual_tests)} visual diff pages...")
            diffs_dir = self.output_dir / "diffs"
            diffs_dir.mkdir(exist_ok=True)
            
            for i, test in enumerate(visual_tests):
                diff_html = self.generator.generate_diff_page(
                    test_name=test['name'],
                    baseline_content=test['baseline'],
                    actual_content=test['actual'],
                    current_index=i + 1,
                    total_tests=len(visual_tests),
                    config=test.get('config')
                )
                (diffs_dir / f"{test['name']}.html").write_text(diff_html)
        
        # Save review data for JavaScript
        print("  💾 Saving review data...")
        data_dir = self.output_dir / "data"
        data_dir.mkdir(exist_ok=True)
        
        review_data = {
            'generated': datetime.now().isoformat(),
            'test_results': test_results,
            'visual_tests': [
                {
                    'name': t['name'],
                    'status': t['status'],
                    'baseline': f"../visual/baseline/{t['name']}.baseline.svg",
                    'actual': f"../visual/output/{t['name']}.actual.svg"
                }
                for t in visual_tests
            ]
        }
        (data_dir / "test_results.json").write_text(json.dumps(review_data, indent=2))
        
        print(f"\n✅ Review suite generated at: {self.output_dir}")
        print(f"   Open {self.output_dir / 'index.html'} to view the dashboard")
    
    def _get_recent_activity(self) -> List[Dict[str, Any]]:
        """Get recent test activity (placeholder for now)."""
        # This could be enhanced to read from test logs or git history
        return []
    
    def serve(self, port: int = 8080) -> None:
        """Serve the review suite locally.
        
        Args:
            port: Port to serve on
        """
        print(f"\n🌐 Starting review server on http://localhost:{port}")
        print("   Press Ctrl+C to stop\n")
        
        try:
            subprocess.run(
                ["python", "-m", "http.server", str(port)],
                cwd=str(self.output_dir),
                check=True
            )
        except KeyboardInterrupt:
            print("\n✋ Server stopped")


def main():
    """CLI entry point for the review suite."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate SegnoMMS Visual Review Suite")
    parser.add_argument(
        "--serve",
        action="store_true",
        help="Serve the review suite after generation"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Port to serve on (default: 8080)"
    )
    parser.add_argument(
        "--no-generate",
        action="store_true",
        help="Skip generation and only serve existing files"
    )
    
    args = parser.parse_args()
    
    suite = ReviewSuite()
    
    if not args.no_generate:
        suite.generate_review_pages()
    
    if args.serve:
        suite.serve(args.port)


if __name__ == "__main__":
    main()