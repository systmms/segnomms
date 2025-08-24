"""
Pytest configuration and fixtures for segno-plugin tests.
"""

import os
import shutil
from pathlib import Path
from typing import Callable, Generator, Optional
from io import BytesIO

import coverage
import pytest
from PIL import Image

# Start coverage collection for visual tests
cov = coverage.Coverage(source=["segnomms"])
cov.start()


# Standard rendering parameters for visual regression testing
RENDER_PARAMS = {
    "width": 400,
    "height": 400,
    "dpi": 96,
    "background_color": "white",
}


def svg_to_png(svg_content: str, output_path: Optional[Path] = None, return_bytes: bool = False):
    """Convert SVG content to PNG file or bytes.
    
    Args:
        svg_content: SVG content as string
        output_path: Path to save PNG file (optional if return_bytes=True)
        return_bytes: If True, return PNG as bytes instead of saving to file
        
    Returns:
        bytes if return_bytes=True, otherwise None
    """
    try:
        # Try cairosvg first (most reliable)
        import cairosvg
        
        if return_bytes:
            png_bytes = cairosvg.svg2png(
                bytestring=svg_content.encode("utf-8"),
                output_width=RENDER_PARAMS["width"],
                output_height=RENDER_PARAMS["height"],
                dpi=RENDER_PARAMS["dpi"]
            )
            return png_bytes
        else:
            cairosvg.svg2png(
                bytestring=svg_content.encode("utf-8"), 
                write_to=str(output_path),
                output_width=RENDER_PARAMS["width"],
                output_height=RENDER_PARAMS["height"],
                dpi=RENDER_PARAMS["dpi"]
            )
            return
    except ImportError:
        pass

    try:
        # Try using system rsvg-convert command (from librsvg in flake.nix)
        import subprocess
        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".svg", delete=False) as f:
            f.write(svg_content)
            temp_svg = f.name

        try:
            # Use rsvg-convert to convert SVG to PNG
            if return_bytes:
                # Generate to temporary file then read bytes
                import tempfile as tmpfile
                with tmpfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_png:
                    tmp_png_path = tmp_png.name
                
                subprocess.run(
                    [
                        "rsvg-convert",
                        "-w",
                        str(RENDER_PARAMS["width"]),
                        "-h",
                        str(RENDER_PARAMS["height"]),
                        temp_svg,
                        "-o",
                        tmp_png_path,
                    ],
                    check=True,
                    capture_output=True,
                )
                
                with open(tmp_png_path, 'rb') as f:
                    png_bytes = f.read()
                os.unlink(tmp_png_path)
                return png_bytes
            else:
                subprocess.run(
                    [
                        "rsvg-convert",
                        "-w",
                        str(RENDER_PARAMS["width"]),
                        "-h",
                        str(RENDER_PARAMS["height"]),
                        temp_svg,
                        "-o",
                        str(output_path),
                    ],
                    check=True,
                    capture_output=True,
                )
                return
        finally:
            os.unlink(temp_svg)
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    try:
        # Try svglib + reportlab as fallback
        import io

        from reportlab.graphics import renderPM
        from svglib.svglib import svg2rlg

        drawing = svg2rlg(io.StringIO(svg_content))
        if drawing:
            renderPM.drawToFile(drawing, str(output_path))
            return
    except ImportError:
        pass

    try:
        # Try wand (ImageMagick) as another fallback
        from wand.api import library
        from wand.image import Image

        with Image(blob=svg_content.encode("utf-8"), format="svg") as img:
            img.format = "png"
            img.save(filename=str(output_path))
        return
    except ImportError:
        pass

    try:
        # Try using system ImageMagick convert command
        import subprocess
        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".svg", delete=False) as f:
            f.write(svg_content)
            temp_svg = f.name

        try:
            subprocess.run(
                ["convert", temp_svg, "-resize", "400x400", str(output_path)],
                check=True,
                capture_output=True,
            )
            return
        finally:
            os.unlink(temp_svg)
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    # If no converter is available, at least warn the user
    if output_path:
        print(
            f"Warning: No SVG to PNG converter available. PNG output skipped for {output_path.name}"
        )
    else:
        print("Warning: No SVG to PNG converter available.")
    print(
        "Install one of: cairosvg (pip), or ensure rsvg-convert/imagemagick is in PATH"
    )
    
    if return_bytes:
        # Return empty image bytes as fallback
        img = Image.new('RGB', (RENDER_PARAMS["width"], RENDER_PARAMS["height"]), 'white')
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        return buffer.getvalue()


def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption(
        "--update-baseline",
        action="store_true",
        default=False,
        help="Update visual regression baselines",
    )


@pytest.fixture(scope="session")
def test_output_dir() -> Path:
    """Create and return test output directory."""
    output_dir = Path(__file__).parent.parent / "test-output"
    output_dir.mkdir(exist_ok=True)
    return output_dir


@pytest.fixture(scope="session")
def visual_baseline_dir() -> Path:
    """Return visual test baseline directory."""
    baseline_dir = Path(__file__).parent / "visual" / "baseline"
    baseline_dir.mkdir(parents=True, exist_ok=True)
    return baseline_dir


@pytest.fixture(scope="session")
def visual_output_dir() -> Path:
    """Return visual test output directory."""
    output_dir = Path(__file__).parent / "visual" / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


@pytest.fixture(scope="session")
def visual_diff_dir() -> Path:
    """Return visual test diff directory."""
    diff_dir = Path(__file__).parent / "visual" / "diff"
    diff_dir.mkdir(parents=True, exist_ok=True)
    return diff_dir


@pytest.fixture(scope="session")
def examples_generated_dir() -> Path:
    """Return generated examples directory."""
    examples_dir = Path(__file__).parent.parent / "examples-generated"
    examples_dir.mkdir(exist_ok=True)
    return examples_dir


@pytest.fixture
def visual_regression_tester(
    visual_baseline_dir, visual_output_dir, visual_diff_dir
):
    """Fixture for visual regression testing."""

    def compare_svgs(name: str, actual_svg: str, update_baseline: bool = False) -> bool:
        """
        Compare generated SVG with baseline.

        Args:
            name: Test name (used for filenames)
            actual_svg: Generated SVG content
            update_baseline: If True, update the baseline instead of comparing

        Returns:
            True if SVGs match (or baseline was updated)
        """
        baseline_path = visual_baseline_dir / f"{name}.baseline.svg"
        baseline_png_path = visual_baseline_dir / f"{name}.baseline.png"
        output_path = visual_output_dir / f"{name}.actual.svg"
        output_png_path = visual_output_dir / f"{name}.actual.png"

        # Save actual output
        output_path.write_text(actual_svg)

        # Generate PNG version of actual output
        try:
            svg_to_png(actual_svg, output_png_path)
        except Exception as e:
            print(f"Warning: Failed to generate PNG for {name}: {e}")

        if update_baseline or not baseline_path.exists():
            # Create/update baseline SVG
            baseline_path.write_text(actual_svg)
            
            # Create/update baseline PNG
            try:
                svg_to_png(actual_svg, baseline_png_path)
            except Exception as e:
                print(f"Warning: Failed to generate baseline PNG for {name}: {e}")
            
            return True

        # Compare with baseline
        baseline_svg = baseline_path.read_text()

        # Normalize SVGs for comparison (remove timestamps, random IDs, etc.)
        actual_normalized = normalize_svg(actual_svg)
        baseline_normalized = normalize_svg(baseline_svg)

        if actual_normalized == baseline_normalized:
            return True

        # Generate diff visualization
        diff_path = visual_diff_dir / f"{name}.diff.html"
        generate_diff_html(diff_path, baseline_svg, actual_svg)

        return False

    return compare_svgs


def normalize_svg(svg_content: str) -> str:
    """Normalize SVG content for comparison."""
    import re
    from xml.etree import ElementTree as ET
    
    try:
        # Parse SVG properly with XML parser
        root = ET.fromstring(svg_content)
        
        # Recursively process all elements
        for elem in root.iter():
            # Sort attributes deterministically
            if elem.attrib:
                elem.attrib = dict(sorted(elem.attrib.items()))
            
            # Remove dynamic IDs and ID references
            elem.attrib.pop("id", None)
            elem.attrib.pop("aria-labelledby", None)
            elem.attrib.pop("aria-describedby", None)
            
            # Round floating point values to 3 decimal places
            for key, value in list(elem.attrib.items()):
                if re.match(r'^-?\d+\.\d+$', value):
                    elem.attrib[key] = f"{float(value):.3f}"
        
        # Convert back to string with sorted attributes
        normalized = ET.tostring(root, encoding="unicode", method="xml")
        
        # Additional normalization
        # Remove XML declaration if present
        normalized = re.sub(r'^<\?xml[^>]+\?>\s*', '', normalized)
        
        # Normalize numeric precision (catch any we missed)
        normalized = re.sub(r'(\d+\.\d{3})\d+', r'\1', normalized)
        
        # Normalize whitespace between tags
        normalized = re.sub(r'>\s+<', '><', normalized)
        
        return normalized.strip()
        
    except ET.ParseError:
        # Fallback to regex-based normalization if XML parsing fails
        # Remove comments
        svg_content = re.sub(r"<!--.*?-->", "", svg_content, flags=re.DOTALL)
        
        # Normalize whitespace
        svg_content = " ".join(svg_content.split())
        
        # Remove timestamps or generated IDs
        svg_content = re.sub(r'id="[^"]*"', '', svg_content)
        
        # Round floats
        svg_content = re.sub(r'(\d+\.\d{3})\d+', r'\1', svg_content)
        
        return svg_content


def generate_diff_html(diff_path: Path, baseline: str, actual: str):
    """Generate an HTML file showing the visual diff using the new review suite."""
    try:
        from tests.review.html_generator import HTMLGenerator
        
        # Use the new HTML generator for consistent styling
        generator = HTMLGenerator()
        test_name = diff_path.stem.replace('.diff', '')
        
        html_content = generator.generate_diff_page(
            test_name=test_name,
            baseline_content=baseline,
            actual_content=actual,
            test_info=f"Visual regression test for {test_name}"
        )
        
        diff_path.write_text(html_content)
    except ImportError:
        # Fallback to simple diff if review suite not available
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Visual Regression Diff</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .container {{ display: flex; gap: 20px; }}
                .panel {{ flex: 1; border: 1px solid #ccc; padding: 10px; }}
                h2 {{ margin-top: 0; }}
                .svg-container {{ background: #f5f5f5; padding: 10px; overflow: auto; }}
            </style>
        </head>
        <body>
            <h1>Visual Regression Test Failed</h1>
            <div class="container">
                <div class="panel">
                    <h2>Baseline</h2>
                    <div class="svg-container">{baseline}</div>
                </div>
                <div class="panel">
                    <h2>Actual</h2>
                    <div class="svg-container">{actual}</div>
                </div>
            </div>
        </body>
        </html>
        """
        diff_path.write_text(html_content)


@pytest.fixture(scope="session", autouse=True)
def coverage_report():
    """Generate coverage report at the end of test session."""
    yield
    cov.stop()
    cov.save()


# Playwright fixtures for browser testing
@pytest.fixture(scope="session")
def browser_context_args():
    """Browser context arguments for Playwright."""
    return {
        "viewport": {"width": 1280, "height": 720},
        "ignore_https_errors": True,
    }


@pytest.fixture(scope="session")
def base_url():
    """Base URL for serving examples."""
    return "http://localhost:8000"


@pytest.fixture
def image_snapshot(request, visual_baseline_dir, visual_output_dir):
    """Enhanced image snapshot fixture for visual regression testing.
    
    This provides compatibility with pytest-image-snapshot style testing
    while using our existing infrastructure.
    """
    def snapshot(image_data, name=None, threshold=0.1):
        """
        Compare image against baseline snapshot.
        
        Args:
            image_data: Can be PIL Image, bytes, or file path
            name: Name for the snapshot (defaults to test name)
            threshold: Allowed difference threshold (0.0-1.0)
            
        Returns:
            True if images match within threshold
        """
        if name is None:
            name = request.node.name
            
        # Ensure name is filesystem safe
        name = name.replace("::", "_").replace("[", "_").replace("]", "_")
        
        baseline_path = visual_baseline_dir / f"{name}.png"
        output_path = visual_output_dir / f"{name}.png"
        
        # Convert input to PIL Image
        if isinstance(image_data, bytes):
            current_img = Image.open(BytesIO(image_data))
        elif isinstance(image_data, str) or isinstance(image_data, Path):
            current_img = Image.open(image_data)
        elif isinstance(image_data, Image.Image):
            current_img = image_data
        else:
            raise ValueError(f"Unsupported image data type: {type(image_data)}")
            
        # Save current image
        current_img.save(output_path)
        
        # Check if we should update baseline
        update_baseline = request.config.getoption("--update-baseline", False)
        
        if update_baseline or not baseline_path.exists():
            # Create/update baseline
            current_img.save(baseline_path)
            return True
            
        # Compare with baseline
        baseline_img = Image.open(baseline_path)
        
        # Simple pixel comparison (can be enhanced with tolerance)
        if list(current_img.getdata()) == list(baseline_img.getdata()):
            return True
            
        # Images differ - could implement threshold comparison here
        return False
        
    return snapshot
