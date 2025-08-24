"""Automated QR code scanning harness for validation.

This module provides comprehensive testing of QR code scanability across
various conditions, DPIs, and scanning scenarios.
"""

import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

# Try to import scanning libraries (with graceful degradation)
try:
    from PIL import Image, ImageDraw

    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    # Create placeholder for type hints
    if TYPE_CHECKING:
        from PIL import Image

try:
    import cv2
    import numpy as np

    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False

try:
    from pyzbar import pyzbar

    PYZBAR_AVAILABLE = True
except ImportError:
    PYZBAR_AVAILABLE = False

import segno

from segnomms.config import RenderingConfig

logger = logging.getLogger(__name__)


class ScanResult(Enum):
    """Scanning test result status."""

    SUCCESS = "success"
    FAILURE = "failure"
    ERROR = "error"
    SKIPPED = "skipped"


@dataclass
class ScanTestCase:
    """Individual scanning test case configuration."""

    name: str
    description: str
    dpi: int
    scale_factor: float = 1.0
    rotation_degrees: int = 0
    blur_radius: float = 0.0
    noise_level: float = 0.0
    brightness_adjustment: float = 0.0
    contrast_adjustment: float = 1.0


@dataclass
class ScanTestResult:
    """Result from a single scanning test."""

    test_case: ScanTestCase
    result: ScanResult
    decoded_data: Optional[str] = None
    scan_time_ms: Optional[float] = None
    error_message: Optional[str] = None
    confidence: Optional[float] = None


class QRScanabilityHarness:
    """Automated QR code scanning validation harness.

    Provides comprehensive testing of QR codes across multiple conditions
    to validate scanability and reliability.
    """

    def __init__(self, require_all_libraries: bool = False):
        """Initialize the scanning harness.

        Args:
            require_all_libraries: If True, raise error if scanning libraries unavailable
        """
        self.available_scanners = []

        if PIL_AVAILABLE:
            self.available_scanners.append("PIL")
        if OPENCV_AVAILABLE:
            self.available_scanners.append("OpenCV")
        if PYZBAR_AVAILABLE:
            self.available_scanners.append("pyzbar")

        if require_all_libraries and len(self.available_scanners) < 3:
            missing = []
            if not PIL_AVAILABLE:
                missing.append("PIL/Pillow")
            if not OPENCV_AVAILABLE:
                missing.append("opencv-python")
            if not PYZBAR_AVAILABLE:
                missing.append("pyzbar")
            raise ImportError(f"Missing required libraries: {missing}")

        if not self.available_scanners:
            logger.warning(
                "No QR scanning libraries available. Install PIL, opencv-python, and pyzbar for full functionality."
            )

    def get_standard_test_cases(self) -> List[ScanTestCase]:
        """Get standard set of scanning test cases.

        Returns:
            List of comprehensive test cases for validation
        """
        return [
            # Basic DPI tests
            ScanTestCase("low_dpi", "Low DPI scanning (72 DPI)", 72),
            ScanTestCase("standard_dpi", "Standard DPI scanning (150 DPI)", 150),
            ScanTestCase("high_dpi", "High DPI scanning (300 DPI)", 300),
            ScanTestCase("print_dpi", "Print quality DPI (600 DPI)", 600),
            # Scale factor tests
            ScanTestCase("small_scale", "Small scale factor", 150, scale_factor=0.5),
            ScanTestCase("large_scale", "Large scale factor", 150, scale_factor=2.0),
            # Rotation tests
            ScanTestCase("rotate_90", "90 degree rotation", 150, rotation_degrees=90),
            ScanTestCase(
                "rotate_180", "180 degree rotation", 150, rotation_degrees=180
            ),
            ScanTestCase(
                "rotate_270", "270 degree rotation", 150, rotation_degrees=270
            ),
            ScanTestCase("rotate_45", "45 degree rotation", 150, rotation_degrees=45),
            # Quality degradation tests
            ScanTestCase("slight_blur", "Slight blur", 150, blur_radius=0.5),
            ScanTestCase("moderate_blur", "Moderate blur", 150, blur_radius=1.0),
            ScanTestCase(
                "low_brightness", "Low brightness", 150, brightness_adjustment=-0.3
            ),
            ScanTestCase(
                "high_brightness", "High brightness", 150, brightness_adjustment=0.3
            ),
            ScanTestCase("low_contrast", "Low contrast", 150, contrast_adjustment=0.7),
            ScanTestCase(
                "high_contrast", "High contrast", 150, contrast_adjustment=1.3
            ),
            ScanTestCase("noise", "Added noise", 150, noise_level=0.1),
            # Combined stress tests
            ScanTestCase(
                "stress_combo",
                "Combined stress test",
                72,
                scale_factor=0.7,
                rotation_degrees=15,
                blur_radius=0.3,
                brightness_adjustment=-0.2,
                contrast_adjustment=0.8,
            ),
        ]

    def svg_to_image(
        self, svg_content: str, dpi: int = 150, scale_factor: float = 1.0
    ) -> Optional["Image.Image"]:
        """Convert SVG content to PIL Image.

        Args:
            svg_content: SVG content string
            dpi: Dots per inch for rasterization
            scale_factor: Additional scaling factor

        Returns:
            PIL Image object, or None if conversion fails
        """
        if not PIL_AVAILABLE:
            return None

        try:
            # For now, we'll create a simple bitmap version
            # In production, you'd want to use proper SVG rendering like cairosvg

            # Extract basic SVG dimensions (simplified parsing)
            import re

            width_match = re.search(r'width="(\d+)"', svg_content)
            height_match = re.search(r'height="(\d+)"', svg_content)

            if not (width_match and height_match):
                # Try viewBox
                viewbox_match = re.search(r'viewBox="0 0 (\d+) (\d+)"', svg_content)
                if viewbox_match:
                    width = int(viewbox_match.group(1))
                    height = int(viewbox_match.group(2))
                else:
                    # Default size
                    width, height = 200, 200
            else:
                width = int(width_match.group(1))
                height = int(height_match.group(2))

            # Scale dimensions
            width = int(width * scale_factor * dpi / 150)
            height = int(height * scale_factor * dpi / 150)

            # Create a basic bitmap representation
            # This is a simplified implementation - production would use proper SVG rendering
            image = Image.new("RGB", (width, height), "white")
            draw = ImageDraw.Draw(image)

            # For testing purposes, create a simple pattern
            # Real implementation would properly render the SVG
            module_size = max(1, width // 25)  # Approximate module size

            # Create basic QR pattern for testing
            for y in range(0, height, module_size):
                for x in range(0, width, module_size):
                    # Simplified pattern - just for testing the harness
                    if (x // module_size + y // module_size) % 2 == 0:
                        draw.rectangle(
                            [x, y, x + module_size, y + module_size], fill="black"
                        )

            return image

        except Exception as e:
            logger.error(f"Failed to convert SVG to image: {e}")
            return None

    def apply_image_effects(
        self, image: "Image.Image", test_case: ScanTestCase
    ) -> Optional["Image.Image"]:
        """Apply test case effects to image.

        Args:
            image: PIL Image to modify
            test_case: Test case with effect parameters

        Returns:
            Modified PIL Image, or None if effects fail
        """
        if not PIL_AVAILABLE:
            return None

        try:
            # Apply rotation
            if test_case.rotation_degrees != 0:
                image = image.rotate(
                    test_case.rotation_degrees, expand=True, fillcolor="white"
                )

            # Apply blur
            if test_case.blur_radius > 0:
                from PIL import ImageFilter

                image = image.filter(ImageFilter.GaussianBlur(test_case.blur_radius))

            # Apply brightness adjustment
            if test_case.brightness_adjustment != 0:
                from PIL import ImageEnhance

                enhancer = ImageEnhance.Brightness(image)
                image = enhancer.enhance(1.0 + test_case.brightness_adjustment)

            # Apply contrast adjustment
            if test_case.contrast_adjustment != 1.0:
                from PIL import ImageEnhance

                enhancer = ImageEnhance.Contrast(image)
                image = enhancer.enhance(test_case.contrast_adjustment)

            # Apply noise
            if test_case.noise_level > 0:
                if OPENCV_AVAILABLE:
                    # Convert to numpy array for noise
                    img_array = np.array(image)
                    noise = np.random.normal(
                        0, test_case.noise_level * 255, img_array.shape
                    )
                    noisy_array = np.clip(img_array + noise, 0, 255).astype(np.uint8)
                    image = Image.fromarray(noisy_array)

            return image

        except Exception as e:
            logger.error(f"Failed to apply image effects: {e}")
            return image  # Return original if effects fail

    def scan_with_pyzbar(
        self, image: "Image.Image"
    ) -> Tuple[bool, Optional[str], Optional[float]]:
        """Scan QR code using pyzbar.

        Args:
            image: PIL Image containing QR code

        Returns:
            Tuple of (success, decoded_data, confidence)
        """
        if not PYZBAR_AVAILABLE:
            return False, None, None

        try:
            start_time = time.time()
            barcodes = pyzbar.decode(image)
            scan_time = (time.time() - start_time) * 1000

            if barcodes:
                # Get first QR code found
                barcode = barcodes[0]
                if barcode.type == "QRCODE":
                    decoded_data = barcode.data.decode("utf-8")
                    # pyzbar doesn't provide confidence, estimate from quality
                    confidence = 0.9  # Assume good if successfully decoded
                    return True, decoded_data, confidence

            return False, None, None

        except Exception as e:
            logger.error(f"pyzbar scanning failed: {e}")
            return False, None, None

    def scan_with_opencv(
        self, image: "Image.Image"
    ) -> Tuple[bool, Optional[str], Optional[float]]:
        """Scan QR code using OpenCV.

        Args:
            image: PIL Image containing QR code

        Returns:
            Tuple of (success, decoded_data, confidence)
        """
        if not OPENCV_AVAILABLE:
            return False, None, None

        try:
            # Convert PIL to OpenCV format
            img_array = np.array(image)
            if len(img_array.shape) == 3:
                img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)

            # Use OpenCV QR detector
            detector = cv2.QRCodeDetector()
            start_time = time.time()
            data, vertices, _ = detector.detectAndDecode(img_array)
            scan_time = (time.time() - start_time) * 1000

            if data:
                # Estimate confidence from detection quality
                confidence = 0.8 if vertices is not None else 0.6
                return True, data, confidence

            return False, None, None

        except Exception as e:
            logger.error(f"OpenCV scanning failed: {e}")
            return False, None, None

    def run_single_test(
        self, svg_content: str, test_case: ScanTestCase, expected_data: str
    ) -> ScanTestResult:
        """Run a single scanning test case.

        Args:
            svg_content: SVG content to test
            test_case: Test case configuration
            expected_data: Expected decoded data

        Returns:
            ScanTestResult with test outcome
        """
        try:
            # Convert SVG to image
            image = self.svg_to_image(
                svg_content, test_case.dpi, test_case.scale_factor
            )
            if not image:
                return ScanTestResult(
                    test_case=test_case,
                    result=ScanResult.SKIPPED,
                    error_message="Could not convert SVG to image",
                )

            # Apply test effects
            image = self.apply_image_effects(image, test_case)
            if not image:
                return ScanTestResult(
                    test_case=test_case,
                    result=ScanResult.ERROR,
                    error_message="Could not apply image effects",
                )

            # Try different scanners
            scan_results = []

            if PYZBAR_AVAILABLE:
                success, data, confidence = self.scan_with_pyzbar(image)
                scan_results.append(("pyzbar", success, data, confidence))

            if OPENCV_AVAILABLE:
                success, data, confidence = self.scan_with_opencv(image)
                scan_results.append(("opencv", success, data, confidence))

            # Evaluate results
            successful_scans = [r for r in scan_results if r[1]]

            if successful_scans:
                # Use best result (highest confidence)
                best_scan = max(successful_scans, key=lambda x: x[3] or 0)
                scanner, success, data, confidence = best_scan

                # Check if data matches expected
                if data == expected_data:
                    return ScanTestResult(
                        test_case=test_case,
                        result=ScanResult.SUCCESS,
                        decoded_data=data,
                        confidence=confidence,
                    )
                else:
                    return ScanTestResult(
                        test_case=test_case,
                        result=ScanResult.FAILURE,
                        decoded_data=data,
                        confidence=confidence,
                        error_message=f"Data mismatch: got '{data}', expected '{expected_data}'",
                    )
            else:
                return ScanTestResult(
                    test_case=test_case,
                    result=ScanResult.FAILURE,
                    error_message="No scanner could decode the QR code",
                )

        except Exception as e:
            return ScanTestResult(
                test_case=test_case, result=ScanResult.ERROR, error_message=str(e)
            )

    def run_comprehensive_test(
        self,
        config: RenderingConfig,
        test_data: str = "Hello, Scanning Test!",
        test_cases: Optional[List[ScanTestCase]] = None,
        svg_generator=None,
    ) -> Dict[str, Any]:
        """Run comprehensive scanning test suite.

        Args:
            config: Rendering configuration to test
            test_data: Data to encode in QR code
            test_cases: Custom test cases (uses standard if None)
            svg_generator: Function to generate SVG (to avoid circular imports)

        Returns:
            Comprehensive test results dictionary
        """
        if test_cases is None:
            test_cases = self.get_standard_test_cases()

        # Generate QR code with config
        qr_code = segno.make(test_data)

        # Use provided SVG generator or import dynamically
        if svg_generator:
            svg_content = svg_generator(qr_code, config)
        else:
            try:
                from ..plugin import generate_interactive_svg

                svg_content = generate_interactive_svg(qr_code, config)
            except ImportError:
                logger.error("Cannot import SVG generator - circular import issue")
                return {
                    "error": "SVG generation unavailable due to import issues",
                    "success_rate": 0.0,
                }

        results = []
        start_time = time.time()

        for test_case in test_cases:
            result = self.run_single_test(svg_content, test_case, test_data)
            results.append(result)
            logger.info(f"Test '{test_case.name}': {result.result.value}")

        total_time = time.time() - start_time

        # Analyze results
        success_count = sum(1 for r in results if r.result == ScanResult.SUCCESS)
        failure_count = sum(1 for r in results if r.result == ScanResult.FAILURE)
        error_count = sum(1 for r in results if r.result == ScanResult.ERROR)
        skipped_count = sum(1 for r in results if r.result == ScanResult.SKIPPED)

        success_rate = success_count / len(results) if results else 0

        return {
            "config": config.to_kwargs(),
            "test_data": test_data,
            "total_tests": len(results),
            "success_count": success_count,
            "failure_count": failure_count,
            "error_count": error_count,
            "skipped_count": skipped_count,
            "success_rate": success_rate,
            "total_time_seconds": total_time,
            "available_scanners": self.available_scanners,
            "individual_results": [
                {
                    "test_name": r.test_case.name,
                    "description": r.test_case.description,
                    "result": r.result.value,
                    "decoded_data": r.decoded_data,
                    "confidence": r.confidence,
                    "error_message": r.error_message,
                }
                for r in results
            ],
        }

    def validate_scanability_threshold(
        self,
        config: RenderingConfig,
        minimum_success_rate: float = 0.8,
        test_data: str = "Scanability Test",
        svg_generator=None,
    ) -> Tuple[bool, Dict[str, Any]]:
        """Validate that configuration meets scanability threshold.

        Args:
            config: Configuration to validate
            minimum_success_rate: Minimum required success rate (0.0-1.0)
            test_data: Test data to encode
            svg_generator: Function to generate SVG (to avoid circular imports)

        Returns:
            Tuple of (meets_threshold, detailed_results)
        """
        results = self.run_comprehensive_test(
            config, test_data, svg_generator=svg_generator
        )
        success_rate = results.get("success_rate", 0.0)
        meets_threshold = success_rate >= minimum_success_rate

        return meets_threshold, results

    def generate_standard_test_cases(self) -> List[ScanTestCase]:
        """Generate standard test cases (alias for get_standard_test_cases).

        Returns:
            List of comprehensive test cases for validation
        """
        return self.get_standard_test_cases()

    def generate_stress_test_cases(self) -> List[ScanTestCase]:
        """Generate stress test cases for challenging conditions.

        Returns:
            List of stress test cases for validation
        """
        return [
            # Extreme scale tests
            ScanTestCase("tiny_scale", "Tiny scale factor", 72, scale_factor=0.3),
            ScanTestCase("huge_scale", "Huge scale factor", 300, scale_factor=3.0),
            # Extreme rotation tests
            ScanTestCase("slight_rotation", "Slight rotation", 150, rotation_degrees=5),
            ScanTestCase(
                "extreme_rotation", "Extreme rotation", 150, rotation_degrees=359
            ),
            # Heavy degradation tests
            ScanTestCase("heavy_blur", "Heavy blur", 150, blur_radius=2.0),
            ScanTestCase(
                "very_low_brightness",
                "Very low brightness",
                150,
                brightness_adjustment=-0.5,
            ),
            ScanTestCase(
                "very_high_brightness",
                "Very high brightness",
                150,
                brightness_adjustment=0.7,
            ),
            ScanTestCase(
                "very_low_contrast", "Very low contrast", 150, contrast_adjustment=0.5
            ),
            ScanTestCase("heavy_noise", "Heavy noise", 150, noise_level=0.3),
            # Extreme combination tests
            ScanTestCase(
                "nightmare_combo",
                "Nightmare combination",
                72,
                scale_factor=0.4,
                rotation_degrees=37,
                blur_radius=1.5,
                brightness_adjustment=-0.4,
                contrast_adjustment=0.6,
                noise_level=0.2,
            ),
            ScanTestCase(
                "print_stress",
                "Print stress test",
                600,
                scale_factor=0.5,
                rotation_degrees=10,
                blur_radius=0.8,
                brightness_adjustment=0.3,
                contrast_adjustment=1.2,
            ),
        ]

    def analyze_results(self, results: List[ScanTestResult]) -> Dict[str, Any]:
        """Analyze scanning test results.

        Args:
            results: List of scan test results

        Returns:
            Analysis dictionary with statistics
        """
        total_tests = len(results)

        if total_tests == 0:
            return {
                "total_tests": 0,
                "successful_tests": 0,
                "failed_tests": 0,
                "error_tests": 0,
                "skipped_tests": 0,
                "success_rate": 0.0,
                "average_scan_time": 0.0,
                "scanability_verdict": "no_data",
                "test_details": [],
            }

        # Count results by status
        successful_tests = sum(1 for r in results if r.result == ScanResult.SUCCESS)
        failed_tests = sum(1 for r in results if r.result == ScanResult.FAILURE)
        error_tests = sum(1 for r in results if r.result == ScanResult.ERROR)
        skipped_tests = sum(1 for r in results if r.result == ScanResult.SKIPPED)

        # Calculate metrics
        success_rate = successful_tests / total_tests if total_tests > 0 else 0.0

        # Calculate average scan time (only for completed tests)
        completed_results = [r for r in results if r.scan_time_ms is not None]
        average_scan_time = (
            sum(r.scan_time_ms for r in completed_results) / len(completed_results)
            if completed_results
            else 0.0
        )

        # Group results by test case type
        test_details = {}
        for result in results:
            test_name = result.test_case.name
            if test_name not in test_details:
                test_details[test_name] = {
                    "description": result.test_case.description,
                    "attempts": 0,
                    "successes": 0,
                    "failures": 0,
                    "errors": 0,
                    "skipped": 0,
                }

            test_details[test_name]["attempts"] += 1
            if result.result == ScanResult.SUCCESS:
                test_details[test_name]["successes"] += 1
            elif result.result == ScanResult.FAILURE:
                test_details[test_name]["failures"] += 1
            elif result.result == ScanResult.ERROR:
                test_details[test_name]["errors"] += 1
            elif result.result == ScanResult.SKIPPED:
                test_details[test_name]["skipped"] += 1

        # Determine scanability verdict
        if total_tests == 0:
            scanability_verdict = "no_data"
        elif success_rate >= 0.9:
            scanability_verdict = "excellent"
        elif success_rate >= 0.8:
            scanability_verdict = "good"
        elif success_rate >= 0.6:
            scanability_verdict = "acceptable"
        elif success_rate >= 0.3:
            scanability_verdict = "poor"
        else:
            scanability_verdict = "failed"

        return {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "failed_tests": failed_tests,
            "error_tests": error_tests,
            "skipped_tests": skipped_tests,
            "success_rate": success_rate,
            "average_scan_time": average_scan_time,
            "scanability_verdict": scanability_verdict,
            "test_details": test_details,
            "by_test_type": test_details,
        }

    def validate_qr_with_test_case(
        self, svg_content: str, expected_data: str, test_case: ScanTestCase
    ) -> ScanTestResult:
        """Validate QR code with a specific test case.

        Args:
            svg_content: SVG content to test
            expected_data: Expected decoded content
            test_case: Test case parameters

        Returns:
            ScanTestResult with validation results
        """
        if not self.available_scanners:
            return ScanTestResult(
                test_case=test_case,
                result=ScanResult.SKIPPED,
                error_message="No scanning libraries available",
            )

        return self.run_single_test(svg_content, test_case, expected_data)


def get_scanability_harness() -> Optional[QRScanabilityHarness]:
    """Get scanability harness with graceful degradation.

    Returns:
        QRScanabilityHarness instance, or None if no scanning libraries available
    """
    try:
        harness = QRScanabilityHarness(require_all_libraries=False)
        if harness.available_scanners:
            return harness
        else:
            logger.warning("No QR scanning libraries available for validation")
            return None
    except Exception as e:
        logger.error(f"Could not initialize scanning harness: {e}")
        return None
