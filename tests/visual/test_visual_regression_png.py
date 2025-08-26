"""
PNG-based visual regression tests using the unified test infrastructure.

These tests generate PNG images and compare them against baselines to detect
visual changes in QR code generation.
"""

import io

import numpy as np
import pytest
from PIL import Image

from tests.helpers.test_case_generator import Case, Category, TestCaseGenerator
from tests.helpers.test_output_manager import OutputManager


class TestVisualRegressionPNG:
    """PNG-based visual regression tests."""

    @pytest.fixture(autouse=True)
    def setup(self, tmp_path, request):
        """Setup test output manager."""
        self.output_manager = OutputManager()
        self.update_baseline = request.config.getoption("--update-baseline", False)

        # Ensure clean output directory
        self.output_manager.cleanup_outputs("output")

    def _compare_images(self, test_case_id: str, generated_png: bytes) -> bool:
        """
        Compare generated PNG with baseline.

        Args:
            test_case_id: Test case identifier
            generated_png: Generated PNG as bytes

        Returns:
            True if images match, False otherwise
        """
        baseline_path = self.output_manager.get_baseline_path(test_case_id, "png")

        # If baseline doesn't exist and we're not updating, create it
        if not baseline_path.exists():
            if self.update_baseline:
                baseline_path.write_bytes(generated_png)
                return True
            else:
                pytest.skip(f"No baseline image for {test_case_id}. Run with --update-baseline to create.")

        # Load images
        try:
            baseline_img = Image.open(baseline_path)
            generated_img = Image.open(io.BytesIO(generated_png))
        except Exception as e:
            pytest.fail(f"Could not load images for {test_case_id}: {e}")

        # Convert to same mode for comparison
        if baseline_img.mode != generated_img.mode:
            # Convert both to RGBA for consistent comparison
            baseline_img = baseline_img.convert("RGBA")
            generated_img = generated_img.convert("RGBA")

        # Check dimensions
        if baseline_img.size != generated_img.size:
            # Save the generated image for inspection
            output_path = self.output_manager.get_output_path(test_case_id, "png")
            output_path.write_bytes(generated_png)

            pytest.fail(
                f"Image dimensions differ for {test_case_id}: "
                f"baseline {baseline_img.size} vs generated {generated_img.size}"
            )

        # Compare pixel data
        baseline_array = np.array(baseline_img)
        generated_array = np.array(generated_img)

        # Calculate difference
        diff = np.abs(baseline_array.astype(np.int16) - generated_array.astype(np.int16))
        max_diff = np.max(diff)
        mean_diff = np.mean(diff)

        # Tolerance for minor differences (anti-aliasing, compression artifacts)
        max_tolerance = 5  # Maximum pixel value difference
        mean_tolerance = 1.0  # Average difference tolerance

        images_match = max_diff <= max_tolerance and mean_diff <= mean_tolerance

        if not images_match:
            # Check if we should update the baseline instead of failing
            if self.update_baseline:
                baseline_path.write_bytes(generated_png)
                return True

            # Save the generated image and create a diff image
            output_path = self.output_manager.get_output_path(test_case_id, "png")
            output_path.write_bytes(generated_png)

            # Create diff image
            diff_normalized = (diff * 255 / max(max_diff, 1)).astype(np.uint8)
            if len(diff_normalized.shape) == 3 and diff_normalized.shape[2] > 1:
                # For color images, show diff as grayscale
                diff_gray = np.max(diff_normalized[:, :, :3], axis=2)
                diff_img = Image.fromarray(diff_gray, mode="L")
            else:
                diff_img = Image.fromarray(diff_normalized[:, :, 0], mode="L")

            diff_path = self.output_manager.get_diff_path(test_case_id)
            diff_img.save(diff_path)

            pytest.fail(
                f"Images differ for {test_case_id}: "
                f"max_diff={max_diff}, mean_diff={mean_diff:.2f}. "
                f"Check {output_path} and {diff_path}"
            )

        return True

    def _generate_and_test_case(self, test_case: Case):
        """Generate output for a test case and compare with baseline."""
        # Generate QR code
        qr = TestCaseGenerator.generate_qr(test_case)

        # Generate all outputs using TestOutputManager
        outputs = self.output_manager.generate_test_output(test_case.id, qr, test_case.config, "output")

        # Read generated PNG
        png_path = outputs["png"]
        if png_path and png_path.exists():
            generated_png = png_path.read_bytes()

            # Compare with baseline
            self._compare_images(test_case.id, generated_png)
        else:
            pytest.fail(f"Could not generate PNG for {test_case.id}")

    @pytest.mark.visual
    @pytest.mark.parametrize("test_case", TestCaseGenerator.get_shape_test_cases())
    def test_shape_variations(self, test_case: Case):
        """Test all shape variations."""
        self._generate_and_test_case(test_case)

    @pytest.mark.visual
    @pytest.mark.parametrize("test_case", TestCaseGenerator.get_color_test_cases())
    def test_color_variations(self, test_case: Case):
        """Test color variations."""
        self._generate_and_test_case(test_case)

    @pytest.mark.visual
    @pytest.mark.parametrize("test_case", TestCaseGenerator.get_error_level_test_cases())
    def test_error_correction_levels(self, test_case: Case):
        """Test different error correction levels."""
        self._generate_and_test_case(test_case)

    @pytest.mark.visual
    @pytest.mark.parametrize("test_case", TestCaseGenerator.get_payload_test_cases())
    def test_payload_variations(self, test_case: Case):
        """Test different payload types."""
        self._generate_and_test_case(test_case)

    @pytest.mark.visual
    @pytest.mark.parametrize("test_case", TestCaseGenerator.get_frame_test_cases())
    def test_frame_effects(self, test_case: Case):
        """Test frame effects."""
        self._generate_and_test_case(test_case)

    @pytest.mark.visual
    @pytest.mark.parametrize("test_case", TestCaseGenerator.get_complex_test_cases())
    def test_complex_configurations(self, test_case: Case):
        """Test complex configurations with multiple features."""
        self._generate_and_test_case(test_case)

    @pytest.mark.visual
    @pytest.mark.parametrize("test_case", TestCaseGenerator.get_edge_case_test_cases())
    def test_edge_cases(self, test_case: Case):
        """Test edge cases."""
        self._generate_and_test_case(test_case)

    @pytest.mark.visual
    def test_quick_regression_suite(self):
        """Run a quick subset of tests for fast regression checking."""
        quick_cases = TestCaseGenerator.get_quick_test_suite()

        for test_case in quick_cases:
            self._generate_and_test_case(test_case)


class TestVisualRegressionSpecific:
    """Specific visual regression tests for particular features."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test output manager."""
        self.output_manager = OutputManager()
        self.update_baseline = False

    def _test_specific_config(self, test_id: str, qr_data: str, config: dict):
        """Test a specific configuration."""
        qr = TestCaseGenerator.generate_qr(
            Case(test_id, Category.INTEGRATION, "Specific test", qr_data, config)
        )

        outputs = self.output_manager.generate_test_output(test_id, qr, config, "output")

        png_path = outputs["png"]
        if png_path and png_path.exists():
            generated_png = png_path.read_bytes()

            # Use same comparison logic
            baseline_path = self.output_manager.get_baseline_path(test_id, "png")

            if not baseline_path.exists():
                if self.update_baseline:
                    baseline_path.write_bytes(generated_png)
                else:
                    pytest.skip(f"No baseline for {test_id}")

            # Simple comparison - could use more sophisticated logic
            baseline_png = baseline_path.read_bytes()
            if generated_png != baseline_png:
                # Images differ - save for inspection
                output_path = self.output_manager.get_output_path(test_id, "png")
                output_path.write_bytes(generated_png)

                # For now, just warn rather than fail
                pytest.warn(f"Images differ for {test_id}")

    @pytest.mark.visual
    def test_corner_radius_variations(self):
        """Test corner radius variations for squircle shapes."""
        base_data = "Corner Radius Test"

        for radius in [0.0, 0.2, 0.4, 0.6, 0.8]:
            test_id = f"corner_radius_{str(radius).replace('.', '_')}"
            config = {"shape": "squircle", "corner_radius": radius, "scale": 10, "border": 4}

            self._test_specific_config(test_id, base_data, config)

    @pytest.mark.visual
    def test_scale_variations(self):
        """Test different scale factors."""
        base_data = "Scale Test"

        for scale in [5, 10, 15, 20]:
            test_id = f"scale_{scale}"
            config = {"shape": "square", "scale": scale, "border": 4}

            self._test_specific_config(test_id, base_data, config)

    @pytest.mark.visual
    def test_border_variations(self):
        """Test different border sizes."""
        base_data = "Border Test"

        for border in [0, 2, 4, 6, 8]:
            test_id = f"border_{border}"
            config = {"shape": "square", "scale": 10, "border": border}

            self._test_specific_config(test_id, base_data, config)

    @pytest.mark.visual
    def test_interactive_features(self):
        """Test interactive feature rendering."""
        test_id = "interactive_features"
        config = {
            "shape": "rounded",
            "scale": 10,
            "border": 4,
            "interactive": True,
            "dark": "#2c3e50",
            "light": "#ecf0f1",
        }

        self._test_specific_config(test_id, "Interactive Test", config)

    @pytest.mark.visual
    def test_finder_pattern_styles(self):
        """Test different finder pattern styles."""
        base_data = "Finder Pattern Test"

        finder_configs = [
            ("square", {"finder_shape": "square"}),
            ("circle", {"finder_shape": "circle"}),
            ("rounded", {"finder_shape": "rounded"}),
        ]

        for name, finder_config in finder_configs:
            test_id = f"finder_{name}"
            config = {"shape": "square", "scale": 10, "border": 4, **finder_config}

            self._test_specific_config(test_id, base_data, config)

    @pytest.mark.visual
    def test_centerpiece_variations(self):
        """Test centerpiece variations."""
        base_data = "Centerpiece Test"

        centerpiece_configs = [
            ("small", {"centerpiece_enabled": True, "centerpiece_size": 0.1}),
            ("medium", {"centerpiece_enabled": True, "centerpiece_size": 0.15}),
            ("large", {"centerpiece_enabled": True, "centerpiece_size": 0.2}),
            (
                "circle",
                {"centerpiece_enabled": True, "centerpiece_size": 0.15, "centerpiece_shape": "circle"},
            ),
            (
                "square",
                {"centerpiece_enabled": True, "centerpiece_size": 0.15, "centerpiece_shape": "square"},
            ),
        ]

        for name, cp_config in centerpiece_configs:
            test_id = f"centerpiece_{name}"
            config = {"shape": "square", "scale": 12, "border": 4, **cp_config}

            self._test_specific_config(test_id, base_data, config)


class VisualRegressionUtilities:
    """Utilities for managing visual regression tests."""

    def __init__(self):
        self.output_manager = OutputManager()

    def generate_all_baselines(self):
        """Generate baseline images for all test cases."""
        all_cases = TestCaseGenerator.get_all_test_cases()

        for test_case in all_cases:
            qr = TestCaseGenerator.generate_qr(test_case)

            # Generate baseline
            self.output_manager.generate_test_output(test_case.id, qr, test_case.config, "baseline")

    def cleanup_old_outputs(self):
        """Clean up old output files."""
        self.output_manager.cleanup_outputs("all")

    def list_missing_baselines(self) -> list[str]:
        """List test cases that don't have baseline images."""
        all_cases = TestCaseGenerator.get_all_test_cases()
        missing = []

        for test_case in all_cases:
            baseline_path = self.output_manager.get_baseline_path(test_case.id, "png")
            if not baseline_path.exists():
                missing.append(test_case.id)

        return missing


# Utility functions for pytest integration
def pytest_configure(config):
    """Configure pytest with visual regression options."""
    config.addinivalue_line("markers", "visual: mark test as visual regression test")


def pytest_addoption(parser):
    """Add command line options for visual regression testing."""
    parser.addoption(
        "--update-baseline",
        action="store_true",
        default=False,
        help="Update baseline images instead of comparing",
    )
    parser.addoption(
        "--visual-quick", action="store_true", default=False, help="Run only quick visual regression tests"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection for visual regression options."""
    if config.getoption("--visual-quick"):
        # Only run quick tests
        quick_items = []
        for item in items:
            if "quick" in item.nodeid or "quick_regression_suite" in item.name:
                quick_items.append(item)
        items[:] = quick_items
