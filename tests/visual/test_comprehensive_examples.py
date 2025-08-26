"""
Generate comprehensive visual examples showcasing all plugin capabilities.

These examples are saved to examples-generated/ directory which is
excluded from git. They serve as visual tests and documentation.
"""

import json
from datetime import datetime
from pathlib import Path

import pytest
import segno

from segnomms import write
from tests.constants import (
    DEFAULT_BORDER,
    DEFAULT_SCALE,
    VALID_SHAPES,
    create_test_config,
)


class TestComprehensiveExamples:
    """Generate comprehensive examples of plugin capabilities."""

    @pytest.fixture(autouse=True)
    def setup(self, examples_generated_dir):
        """Setup for example generation."""
        self.output_dir = examples_generated_dir
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Create subdirectories
        self.shapes_dir = self.output_dir / "shapes"
        self.interactive_dir = self.output_dir / "interactive"
        self.advanced_dir = self.output_dir / "advanced"

        for dir in [
            self.shapes_dir,
            self.interactive_dir,
            self.advanced_dir,
        ]:
            dir.mkdir(exist_ok=True)

    @pytest.mark.visual
    def test_generate_shape_gallery(self):
        """Generate a comprehensive shape gallery with safe mode variations."""
        # Use all valid shapes from constants - no more hardcoded lists!
        shapes = VALID_SHAPES

        # Generate individual shape examples with safe mode ON and OFF
        for shape in shapes:
            qr = segno.make(f"Shape: {shape}", error="M")

            # Safe mode ON (default) using test constants
            output_path_safe = self.shapes_dir / f"{shape}_safe_on.svg"
            config_safe = create_test_config(
                shape=shape,
                scale=DEFAULT_SCALE,
                border=DEFAULT_BORDER,
                safe_mode=True,
                style_interactive=True,
                style_tooltips=True,
            )
            write(qr, str(output_path_safe), **config_safe)

            # Safe mode OFF using test constants
            output_path_unsafe = self.shapes_dir / f"{shape}_safe_off.svg"
            config_unsafe = create_test_config(
                shape=shape,
                scale=DEFAULT_SCALE,
                border=DEFAULT_BORDER,
                safe_mode=False,
                style_interactive=True,
                style_tooltips=True,
            )
            write(qr, str(output_path_unsafe), **config_unsafe)

        # Generate comparison sheet
        self._generate_shape_comparison_sheet(shapes)

        # Generate shape configuration matrix
        self._generate_shape_config_matrix()

    @pytest.mark.visual
    def test_generate_interactive_demos(self):
        """Generate interactive feature demonstrations."""
        demos = [
            {
                "name": "click_handlers",
                "data": "Click any module to see its coordinates",
                "config": {
                    "shape": "rounded",
                    "style_interactive": True,
                    "style_tooltips": True,
                    "style_css_classes": {
                        "finder": "qr-module qr-finder clickable",
                        "data": "qr-module qr-data clickable",
                    },
                },
            },
            {
                "name": "hover_effects",
                "data": "Hover over modules for effects",
                "config": {
                    "shape": "circle",
                    "style_interactive": True,
                    "style_custom_css": """
                        .qr-module.clickable:hover {
                            fill: #e74c3c !important;
                            transform: scale(1.2);
                            transition: all 0.3s ease;
                        }
                    """,
                },
            },
            {
                "name": "module_types_highlighted",
                "data": "Different module types with distinct colors",
                "config": {
                    "shape": "diamond",
                    "style_interactive": True,
                    "style_custom_css": """
                        .qr-finder { fill: #3498db; }
                        .qr-finder-inner { fill: #2980b9; }
                        .qr-timing { fill: #e74c3c; }
                        .qr-data { fill: #2c3e50; }
                        .qr-alignment { fill: #27ae60; }
                    """,
                },
            },
        ]

        for demo in demos:
            qr = segno.make(demo["data"], error="H")
            output_path = self.interactive_dir / f"{demo['name']}.svg"

            write(qr, str(output_path), scale=12, border=3, **demo["config"])

        # Generate interactive showcase HTML
        self._generate_interactive_showcase(demos)

    @pytest.mark.visual
    def test_generate_advanced_features(self):
        """Generate examples of advanced features."""
        # Phase 1: Enhanced shapes with neighbor detection
        test_cases = [
            {
                "name": "phase1_connected_flow",
                "data": "https://github.com/advanced/phase1",
                "shape": "connected",
                "phase1_enabled": True,
                "phase1_use_enhanced_shapes": True,
                "phase1_flow_weights": {"finder": 0.3, "data": 1.0, "timing": 0.7},
            },
            {
                "name": "phase1_extra_rounded",
                "data": "Phase 1 Extra Rounded Demo",
                "shape": "connected-extra-rounded",
                "phase1_enabled": True,
                "phase1_use_enhanced_shapes": True,
                "phase1_roundness": 0.7,
                "phase1_size_ratio": 0.95,
            },
            {
                "name": "phase1_classy_elegant",
                "data": "Elegant QR Design",
                "shape": "connected",
                "phase1_enabled": True,
                "phase1_use_enhanced_shapes": True,
            },
        ]

        for test in test_cases:
            qr = segno.make(test["data"], error="H")
            output_path = self.advanced_dir / f"{test['name']}.svg"

            config = {k: v for k, v in test.items() if k not in ["name", "data"]}
            write(qr, str(output_path), scale=15, border=3, **config)

        # Generate phase comparison
        self._generate_phase_comparison()

    @pytest.mark.visual
    def test_generate_content_type_examples(self):
        """Generate examples for different QR content types."""
        content_types = [
            ("URL", "https://example.com"),
            ("Email", "mailto:test@example.com"),
            ("Phone", "tel:+1234567890"),
            ("SMS", "sms:+1234567890?body=Hello"),
            ("WiFi", "WIFI:T:WPA;S:NetworkName;P:Password;;"),
            ("vCard", "BEGIN:VCARD\nVERSION:3.0\nFN:John Doe\nEND:VCARD"),
            ("Text", "Simple text message with unicode: 🚀✨🎨"),
            ("JSON", json.dumps({"type": "example", "data": [1, 2, 3]})),
        ]

        for content_type, data in content_types:
            qr = segno.make(data, error="M")
            output_path = self.advanced_dir / f"content_{content_type.lower()}.svg"

            write(
                qr,
                str(output_path),
                shape="rounded",
                scale=10,
                border=2,
                style_interactive=True,
                style_tooltips=True,
            )

    def _generate_shape_comparison_sheet(self, shapes):
        """Generate an HTML sheet comparing all shapes with safe mode on/off."""
        # Try to use the new review suite HTML generator
        try:
            from ..review.html_generator import HTMLGenerator

            generator = HTMLGenerator()

            # Prepare gallery items for the new format
            gallery_items = []
            for shape in shapes:
                safe_on_path = self.shapes_dir / f"{shape}_safe_on.svg"
                safe_off_path = self.shapes_dir / f"{shape}_safe_off.svg"

                if safe_on_path.exists() and safe_off_path.exists():
                    gallery_items.append(
                        {
                            "title": shape.replace("-", " ").title(),
                            "shape": shape,
                            "comparison": True,
                            "safe_on_svg": safe_on_path.read_text(),
                            "safe_off_svg": safe_off_path.read_text(),
                            "description": f"Shape type: {shape}",
                        }
                    )

            # Generate gallery using new system
            html = generator.generate_gallery_page(
                gallery_items=gallery_items,
                title="Shape Gallery - Safe Mode Comparison",
                description=(
                    "<strong>Safe Mode:</strong> When enabled (default), functional QR patterns "
                    "(finder, timing, alignment) are always rendered as squares to ensure scannability. "
                    "When disabled, all patterns use the selected shape."
                ),
                show_search=True,
            )

            # Save to both locations
            (self.output_dir / "shape_gallery.html").write_text(html)

            # Also save to review output directory if it exists
            review_output = Path(__file__).parent.parent / "review" / "output"
            if review_output.exists():
                (review_output / "shape_gallery.html").write_text(html)

        except ImportError:
            # Fallback to original implementation
            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Shape Comparison Sheet - Safe Mode ON vs OFF</title>
                <style>
                    body { font-family: Arial, sans-serif; padding: 20px; }
                    h1 { text-align: center; }
                    .shape-section { margin-bottom: 40px; border: 1px solid #ddd; padding: 20px; }
                    .shape-title { font-size: 24px; margin-bottom: 15px; }
                    .comparison { display: flex; gap: 20px; justify-content: center; }
                    .variant { text-align: center; }
                    .variant h4 { margin: 10px 0; }
                    .safe-on { border: 2px solid #059669; padding: 5px; }
                    .safe-off { border: 2px solid #dc2626; padding: 5px; }
                    .info { background: #e0f2fe; padding: 15px; margin-bottom: 20px; border-radius: 5px; }
                </style>
            </head>
            <body>
                <h1>Segno Interactive SVG - Shape Gallery with Safe Mode</h1>
                <div class="info">
                    <strong>Safe Mode:</strong> When enabled (default), functional QR patterns
                    (finder, timing, alignment) are always rendered as squares to ensure scannability.
                    When disabled, all patterns use the selected shape.
                </div>
            """

            for shape in shapes:
                html += f"""
                <div class="shape-section">
                    <h2 class="shape-title">{shape.title().replace('_', ' ')}</h2>
                    <div class="comparison">
                        <div class="variant">
                            <h4 style="color: #059669;">Safe Mode ON ✓</h4>
                            <img src="shapes/{shape}_safe_on.svg" width="200" height="200" class="safe-on">
                            <p>Functional patterns protected</p>
                        </div>
                        <div class="variant">
                            <h4 style="color: #dc2626;">Safe Mode OFF</h4>
                            <img src="shapes/{shape}_safe_off.svg" width="200" height="200" class="safe-off">
                            <p>All patterns styled</p>
                        </div>
                    </div>
                </div>
                """

            html += """
            </body>
            </html>
            """

            (self.output_dir / "shape_gallery.html").write_text(html)

    def _generate_shape_config_matrix(self):
        """Generate a matrix showing shape + configuration combinations."""
        shapes = ["square", "rounded", "connected"]
        configs = [
            {"scale": 5, "border": 1},
            {"scale": 10, "border": 2},
            {"scale": 20, "border": 4},
        ]

        for shape in shapes:
            for i, config in enumerate(configs):
                qr = segno.make("Config Test", error="M")
                output_path = self.shapes_dir / f"matrix_{shape}_config{i}.svg"

                write(qr, str(output_path), shape=shape, **config)

    def _generate_interactive_showcase(self, demos):
        """Generate HTML showcase for interactive features."""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Interactive Features Showcase</title>
            <script>
                function setupInteractivity() {
                    document.querySelectorAll('.qr-module.clickable').forEach(module => {
                        module.addEventListener('click', (e) => {
                            let row, col, type;

                            // Extract row/col from id attribute (e.g., "module-10-15")
                            const idMatch = module.id?.match(/module-(\\d+)-(\\d+)/);
                            if (idMatch) {
                                row = idMatch[1];
                                col = idMatch[2];
                            }

                            // Get type from title element
                            const title = module.querySelector('title')?.textContent || '';
                            if (title.includes('data module')) {
                                type = 'data';
                            } else if (title.includes('finder')) {
                                type = 'finder';
                            } else if (title.includes('timing')) {
                                type = 'timing';
                            } else {
                                type = 'unknown';
                            }

                            console.log(`Clicked: [${row},${col}] type=${type}`);
                            document.getElementById('click-log').innerHTML +=
                                `<div>Clicked: [${row},${col}] type=${type}</div>`;
                        });
                    });
                }
            </script>
            <style>
                body { font-family: Arial, sans-serif; padding: 20px; }
                .demo { margin: 30px 0; padding: 20px; border: 1px solid #ddd; }
                #click-log { height: 100px; overflow-y: auto; border: 1px solid #ccc;
                            padding: 10px; margin-top: 10px; font-family: monospace; }
            </style>
        </head>
        <body onload="setupInteractivity()">
            <h1>Interactive Features Showcase</h1>
        """

        for demo in demos:
            html += f"""
            <div class="demo">
                <h2>{demo['name'].replace('_', ' ').title()}</h2>
                <p>{demo['data']}</p>
                <div class="svg-container">
                    <!-- SVG content would be embedded here -->
                    <object data="interactive/{demo['name']}.svg" type="image/svg+xml"></object>
                </div>
            </div>
            """

        html += """
            <div class="demo">
                <h2>Click Log</h2>
                <div id="click-log"></div>
            </div>
        </body>
        </html>
        """

        (self.output_dir / "interactive_showcase.html").write_text(html)

    def _generate_phase_comparison(self):
        """Generate comparison of rendering phases with safe mode variations."""
        data = "Phase Comparison Test"
        qr = segno.make(data, error="H")

        # Standard rendering with safe mode ON
        output_path = self.advanced_dir / "phase_standard_safe_on.svg"
        write(qr, str(output_path), shape="connected", scale=15, border=3, safe_mode=True)

        # Standard rendering with safe mode OFF
        output_path = self.advanced_dir / "phase_standard_safe_off.svg"
        write(qr, str(output_path), shape="connected", scale=15, border=3, safe_mode=False)

        # Phase 1 enabled with safe mode ON
        output_path = self.advanced_dir / "phase_phase1_safe_on.svg"
        write(
            qr,
            str(output_path),
            shape="connected",
            scale=15,
            border=3,
            safe_mode=True,
            phase1_enabled=True,
            phase1_use_enhanced_shapes=True,
        )

        # Phase 1 enabled with safe mode OFF
        output_path = self.advanced_dir / "phase_phase1_safe_off.svg"
        write(
            qr,
            str(output_path),
            shape="connected",
            scale=15,
            border=3,
            safe_mode=False,
            phase1_enabled=True,
            phase1_use_enhanced_shapes=True,
        )

    @pytest.fixture(scope="class", autouse=True)
    def generate_index(self, examples_generated_dir):
        """Generate index.html for browsing all examples."""
        yield  # Run tests first

        # After all tests, generate index
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Segno Plugin - Generated Examples</title>
            <style>
                body {{ font-family: Arial, sans-serif; padding: 20px; }}
                .timestamp {{ color: #666; font-size: 0.9em; }}
                ul {{ line-height: 1.8; }}
                a {{ color: #3498db; text-decoration: none; }}
                a:hover {{ text-decoration: underline; }}
            </style>
        </head>
        <body>
            <h1>Segno Interactive SVG Plugin - Generated Examples</h1>
            <p class="timestamp">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

            <h2>Browse Examples:</h2>
            <ul>
                <li><a href="shape_gallery.html">Shape Gallery</a></li>
                <li><a href="interactive_showcase.html">Interactive Features</a></li>
                <li><a href="shapes/">Individual Shapes</a></li>
                <li><a href="interactive/">Interactive Demos</a></li>
                <li><a href="advanced/">Advanced Features</a></li>
            </ul>

            <p><em>Note: These examples are generated during testing and excluded from git.</em></p>
        </body>
        </html>
        """

        (examples_generated_dir / "index.html").write_text(html)
