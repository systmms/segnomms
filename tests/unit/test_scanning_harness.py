"""Test suite for QR code scanning harness validation.

This module provides comprehensive testing for the automated QR code scanning
validation system, including test case generation, scanning simulation, and
result analysis.
"""

import time
from unittest.mock import Mock, patch

import pytest

from tests.helpers.scanning_harness import (
    OPENCV_AVAILABLE,
    PIL_AVAILABLE,
    PYZBAR_AVAILABLE,
    QRScanabilityHarness,
    ScanResult,
    ScanTestCase,
    ScanTestResult,
)


class TestScanTestCase:
    """Test cases for ScanTestCase dataclass."""

    def test_scan_test_case_creation_basic(self):
        """Test creating basic scan test case."""
        test_case = ScanTestCase(name="basic_test", description="Basic scanning test", dpi=150)

        assert test_case.name == "basic_test"
        assert test_case.description == "Basic scanning test"
        assert test_case.dpi == 150
        assert test_case.scale_factor == 1.0  # Default value
        assert test_case.rotation_degrees == 0  # Default value
        assert test_case.blur_radius == 0.0  # Default value
        assert test_case.noise_level == 0.0  # Default value
        assert test_case.brightness_adjustment == 0.0  # Default value
        assert test_case.contrast_adjustment == 1.0  # Default value

    def test_scan_test_case_creation_full(self):
        """Test creating scan test case with all parameters."""
        test_case = ScanTestCase(
            name="complex_test",
            description="Complex scanning test with all parameters",
            dpi=300,
            scale_factor=0.8,
            rotation_degrees=15,
            blur_radius=1.5,
            noise_level=0.1,
            brightness_adjustment=-0.2,
            contrast_adjustment=1.3,
        )

        assert test_case.name == "complex_test"
        assert test_case.dpi == 300
        assert test_case.scale_factor == 0.8
        assert test_case.rotation_degrees == 15
        assert test_case.blur_radius == 1.5
        assert test_case.noise_level == 0.1
        assert test_case.brightness_adjustment == -0.2
        assert test_case.contrast_adjustment == 1.3


class TestScanTestResult:
    """Test cases for ScanTestResult dataclass."""

    def test_scan_test_result_success(self):
        """Test creating successful scan test result."""
        test_case = ScanTestCase("test", "Test case", 150)

        result = ScanTestResult(
            test_case=test_case,
            result=ScanResult.SUCCESS,
            decoded_data="Hello, World!",
            scan_time_ms=45.2,
            confidence=0.98,
        )

        assert result.test_case == test_case
        assert result.result == ScanResult.SUCCESS
        assert result.decoded_data == "Hello, World!"
        assert result.scan_time_ms == 45.2
        assert result.error_message is None  # Default value
        assert result.confidence == 0.98

    def test_scan_test_result_failure(self):
        """Test creating failed scan test result."""
        test_case = ScanTestCase("test", "Test case", 150)

        result = ScanTestResult(
            test_case=test_case,
            result=ScanResult.FAILURE,
            scan_time_ms=100.0,
            error_message="Could not decode QR code",
        )

        assert result.result == ScanResult.FAILURE
        assert result.decoded_data is None  # Default value
        assert result.scan_time_ms == 100.0
        assert result.error_message == "Could not decode QR code"
        assert result.confidence is None  # Default value

    def test_scan_test_result_error(self):
        """Test creating error scan test result."""
        test_case = ScanTestCase("test", "Test case", 150)

        result = ScanTestResult(
            test_case=test_case, result=ScanResult.ERROR, error_message="Scanner library not available"
        )

        assert result.result == ScanResult.ERROR
        assert result.error_message == "Scanner library not available"
        assert result.decoded_data is None
        assert result.scan_time_ms is None
        assert result.confidence is None


class TestQRScanabilityHarness:
    """Test cases for QRScanabilityHarness class."""

    def test_harness_initialization_basic(self):
        """Test basic harness initialization."""
        harness = QRScanabilityHarness()

        assert harness is not None
        assert isinstance(harness.available_scanners, list)

        # Check that available scanners match actual library availability
        expected_scanners = []
        if PIL_AVAILABLE:
            expected_scanners.append("PIL")
        if OPENCV_AVAILABLE:
            expected_scanners.append("OpenCV")
        if PYZBAR_AVAILABLE:
            expected_scanners.append("pyzbar")

        assert set(harness.available_scanners) == set(expected_scanners)

    def test_harness_initialization_require_all_libraries_success(self):
        """Test harness initialization requiring all libraries when available."""
        # Only test if all libraries are actually available
        if PIL_AVAILABLE and OPENCV_AVAILABLE and PYZBAR_AVAILABLE:
            harness = QRScanabilityHarness(require_all_libraries=True)
            assert harness is not None
            assert len(harness.available_scanners) == 3
        else:
            # Skip test if libraries not available
            pytest.skip("Not all scanning libraries available")

    def test_harness_initialization_require_all_libraries_failure(self):
        """Test harness initialization requiring all libraries when not available."""
        # Mock library availability to simulate missing libraries
        with patch.multiple(
            "tests.helpers.scanning_harness",
            PIL_AVAILABLE=False,
            OPENCV_AVAILABLE=False,
            PYZBAR_AVAILABLE=False,
        ):
            # Should raise error when requiring all libraries but none available
            with pytest.raises(ImportError, match="Missing required libraries"):
                QRScanabilityHarness(require_all_libraries=True)

    def test_generate_standard_test_cases(self):
        """Test generating standard test cases."""
        harness = QRScanabilityHarness()

        test_cases = harness.generate_standard_test_cases()

        assert isinstance(test_cases, list)
        assert len(test_cases) > 0

        # Check that all test cases are valid
        for test_case in test_cases:
            assert isinstance(test_case, ScanTestCase)
            assert test_case.name is not None
            assert test_case.description is not None
            assert test_case.dpi > 0
            assert test_case.scale_factor > 0
            assert test_case.contrast_adjustment > 0

    def test_generate_stress_test_cases(self):
        """Test generating stress test cases."""
        harness = QRScanabilityHarness()

        test_cases = harness.generate_stress_test_cases()

        assert isinstance(test_cases, list)
        assert len(test_cases) > 0

        # Stress test cases should have more challenging parameters
        challenging_cases = 0
        for test_case in test_cases:
            assert isinstance(test_case, ScanTestCase)

            # Count cases with challenging parameters
            if (
                test_case.scale_factor < 1.0
                or test_case.rotation_degrees != 0
                or test_case.blur_radius > 0
                or test_case.noise_level > 0
                or test_case.brightness_adjustment != 0.0
                or test_case.contrast_adjustment != 1.0
            ):
                challenging_cases += 1

        # Should have at least some challenging test cases
        assert challenging_cases > 0

    def test_validate_qr_with_svg_content_mock(self):
        """Test QR validation with mocked SVG content."""
        harness = QRScanabilityHarness()

        # Create mock SVG content
        svg_content = """<svg width="100" height="100" xmlns="http://www.w3.org/2000/svg">
            <rect x="0" y="0" width="10" height="10" fill="black"/>
            <rect x="20" y="0" width="10" height="10" fill="black"/>
        </svg>"""

        # Mock that we have scanning libraries available
        with patch.object(harness, "available_scanners", ["PIL"]):
            # Mock the scanning process using the actual method name
            with patch.object(harness, "svg_to_image") as mock_convert:
                with patch.object(harness, "run_single_test") as mock_run_single:
                    # Mock successful scanning
                    mock_convert.return_value = Mock()  # Mock PIL Image
                    mock_run_single.return_value = ScanTestResult(
                        test_case=ScanTestCase("test", "Test", 150),
                        result=ScanResult.SUCCESS,
                        decoded_data="Hello World",
                        scan_time_ms=50.0,
                        confidence=0.95,
                    )

                    test_case = ScanTestCase("test", "Test case", 150)
                    result = harness.validate_qr_with_test_case(svg_content, "Hello World", test_case)

                    assert isinstance(result, ScanTestResult)
                    assert result.result == ScanResult.SUCCESS
                    assert result.decoded_data == "Hello World"

                    # Verify mock calls - validate_qr_with_test_case calls run_single_test
                    mock_run_single.assert_called_once_with(svg_content, test_case, "Hello World")

    def test_validate_qr_comprehensive_mock(self):
        """Test comprehensive QR validation with mocked components."""
        harness = QRScanabilityHarness()

        svg_content = "<svg>mock content</svg>"
        expected_data = "Test Data"

        # Mock that we have scanning libraries available
        with patch.object(harness, "available_scanners", ["PIL"]):
            # Mock all the scanning components - use existing methods
            with patch.object(harness, "generate_standard_test_cases") as mock_generate:
                with patch.object(harness, "validate_qr_with_test_case") as mock_validate:
                    # Mock test case generation
                    mock_test_cases = [
                        ScanTestCase("standard_1", "Standard test 1", 150),
                        ScanTestCase("standard_2", "Standard test 2", 300),
                    ]
                    mock_generate.return_value = mock_test_cases

                    # Mock validation results
                    mock_results = [
                        ScanTestResult(
                            test_case=mock_test_cases[0],
                            result=ScanResult.SUCCESS,
                            decoded_data=expected_data,
                            scan_time_ms=45.0,
                        ),
                        ScanTestResult(
                            test_case=mock_test_cases[1],
                            result=ScanResult.SUCCESS,
                            decoded_data=expected_data,
                            scan_time_ms=52.0,
                        ),
                    ]
                    mock_validate.side_effect = mock_results

                    # Create our own comprehensive validation method
                    test_cases = harness.generate_standard_test_cases()
                    results = []
                    for test_case in test_cases:
                        result = harness.validate_qr_with_test_case(svg_content, expected_data, test_case)
                        results.append(result)

                    assert isinstance(results, list)
                    assert len(results) == 2
                    assert all(isinstance(r, ScanTestResult) for r in results)
                    assert all(r.result == ScanResult.SUCCESS for r in results)

                    # Verify method calls
                    mock_generate.assert_called()
                    assert mock_validate.call_count == 2

    def test_analyze_results_all_success(self):
        """Test result analysis with all successful tests."""
        harness = QRScanabilityHarness()

        # Create successful results
        test_cases = [ScanTestCase(f"test_{i}", f"Test {i}", 150) for i in range(3)]
        results = [
            ScanTestResult(
                test_case=tc, result=ScanResult.SUCCESS, decoded_data="Test Data", scan_time_ms=50.0 + i * 10
            )
            for i, tc in enumerate(test_cases)
        ]

        analysis = harness.analyze_results(results)

        assert isinstance(analysis, dict)
        assert analysis["total_tests"] == 3
        assert analysis["successful_tests"] == 3
        assert analysis["failed_tests"] == 0
        assert analysis["error_tests"] == 0
        assert analysis["success_rate"] == 1.0
        assert analysis["average_scan_time"] == 60.0  # (50 + 60 + 70) / 3
        assert analysis["scanability_verdict"] == "excellent"

    def test_analyze_results_mixed(self):
        """Test result analysis with mixed success/failure."""
        harness = QRScanabilityHarness()

        test_cases = [ScanTestCase(f"test_{i}", f"Test {i}", 150) for i in range(4)]
        results = [
            ScanTestResult(test_cases[0], ScanResult.SUCCESS, "Data", scan_time_ms=45.0),
            ScanTestResult(test_cases[1], ScanResult.SUCCESS, "Data", scan_time_ms=55.0),
            ScanTestResult(test_cases[2], ScanResult.FAILURE, error_message="Failed"),
            ScanTestResult(test_cases[3], ScanResult.ERROR, error_message="Error"),
        ]

        analysis = harness.analyze_results(results)

        assert analysis["total_tests"] == 4
        assert analysis["successful_tests"] == 2
        assert analysis["failed_tests"] == 1
        assert analysis["error_tests"] == 1
        assert analysis["success_rate"] == 0.5
        assert analysis["average_scan_time"] == 50.0  # Only successful tests
        assert analysis["scanability_verdict"] in ["poor", "warning"]

    def test_analyze_results_empty(self):
        """Test result analysis with no results."""
        harness = QRScanabilityHarness()

        analysis = harness.analyze_results([])

        assert analysis["total_tests"] == 0
        assert analysis["successful_tests"] == 0
        assert analysis["failed_tests"] == 0
        assert analysis["error_tests"] == 0
        assert analysis["success_rate"] == 0.0
        assert analysis["average_scan_time"] == 0.0
        assert analysis["scanability_verdict"] == "no_data"


class TestScanningHarnessIntegration:
    """Integration tests for scanning harness with actual QR generation."""

    @pytest.fixture
    def simple_svg_content(self):
        """Create simple SVG content for testing."""
        return """<svg width="210" height="210" xmlns="http://www.w3.org/2000/svg">
            <rect x="0" y="0" width="210" height="210" fill="white"/>
            <rect x="10" y="10" width="10" height="10" fill="black"/>
            <rect x="30" y="10" width="10" height="10" fill="black"/>
            <rect x="10" y="30" width="10" height="10" fill="black"/>
        </svg>"""

    def test_harness_with_real_svg_no_scanners(self, simple_svg_content):
        """Test harness with real SVG when no scanners available."""
        # Mock no scanners available
        with patch.multiple(
            "tests.helpers.scanning_harness",
            PIL_AVAILABLE=False,
            OPENCV_AVAILABLE=False,
            PYZBAR_AVAILABLE=False,
        ):
            harness = QRScanabilityHarness()

            # Should handle gracefully when no scanners available
            test_case = ScanTestCase("test", "Test", 150)
            result = harness.validate_qr_with_test_case(simple_svg_content, "Test Data", test_case)

            assert isinstance(result, ScanTestResult)
            assert result.result == ScanResult.SKIPPED
            assert "No scanning libraries available" in result.error_message

    @pytest.mark.skipif(not PIL_AVAILABLE, reason="PIL not available")
    def test_svg_to_image_conversion_basic(self, simple_svg_content):
        """Test SVG to image conversion when PIL is available."""
        harness = QRScanabilityHarness()

        # Test the SVG conversion method if it exists
        if hasattr(harness, "_convert_svg_to_image"):
            try:
                image = harness._convert_svg_to_image(simple_svg_content, 150)
                # Basic validation that we got an image-like object
                assert image is not None
                # PIL Image should have certain attributes
                if hasattr(image, "size"):
                    assert image.size[0] > 0
                    assert image.size[1] > 0
            except Exception as e:
                # SVG conversion might require additional libraries (cairosvg, etc.)
                pytest.skip(f"SVG conversion failed: {e}")
        else:
            pytest.skip("SVG conversion method not implemented")

    def test_custom_test_case_generation(self):
        """Test generating custom test cases."""
        # Test custom test case creation
        custom_cases = []

        # Low DPI test
        custom_cases.append(ScanTestCase("low_dpi", "Low DPI scanning", 72, scale_factor=0.5))

        # High DPI test
        custom_cases.append(ScanTestCase("high_dpi", "High DPI scanning", 600, scale_factor=1.5))

        # Rotated test
        custom_cases.append(ScanTestCase("rotated", "Rotated QR code", 150, rotation_degrees=45))

        # Validate all custom cases
        assert len(custom_cases) == 3
        for case in custom_cases:
            assert isinstance(case, ScanTestCase)
            assert case.dpi > 0
            assert case.scale_factor > 0


class TestScanningHarnessErrorHandling:
    """Test error handling in scanning harness."""

    def test_invalid_svg_content(self):
        """Test handling of invalid SVG content."""
        harness = QRScanabilityHarness()

        invalid_svg = "not valid svg content"
        test_case = ScanTestCase("test", "Test", 150)

        # Mock that we have scanning libraries available and mock the conversion to raise an error
        with patch.object(harness, "available_scanners", ["PIL"]):
            with patch.object(harness, "svg_to_image") as mock_convert:
                mock_convert.side_effect = Exception("Invalid SVG")

                result = harness.validate_qr_with_test_case(invalid_svg, "Test Data", test_case)

                assert isinstance(result, ScanTestResult)
                # When svg_to_image fails, it should return ERROR not SKIPPED
                assert result.result == ScanResult.ERROR
                assert "Invalid SVG" in result.error_message

    def test_scanner_library_error(self):
        """Test handling of scanner library errors."""
        harness = QRScanabilityHarness()

        # Mock that we have scanning libraries available
        with patch.object(harness, "available_scanners", ["pyzbar"]):
            # Mock successful conversion and image effects, but scanner error
            with patch.object(harness, "svg_to_image") as mock_convert:
                with patch.object(harness, "apply_image_effects") as mock_effects:
                    with patch.object(harness, "scan_with_pyzbar") as mock_scan:
                        mock_convert.return_value = Mock()  # Mock PIL Image
                        mock_effects.return_value = Mock()  # Mock PIL Image after effects
                        mock_scan.side_effect = Exception("Scanner error")

                        test_case = ScanTestCase("test", "Test", 150)
                        result = harness.validate_qr_with_test_case("<svg></svg>", "Test Data", test_case)

                        assert isinstance(result, ScanTestResult)
                        # Scanner errors are handled gracefully and return FAILURE, not ERROR
                        assert result.result == ScanResult.FAILURE
                        assert "No scanner could decode" in result.error_message

    def test_timeout_handling(self):
        """Test handling of scanning timeouts."""
        harness = QRScanabilityHarness()

        # Mock slow scanning operation using actual method name
        def slow_scan(*args, **kwargs):
            time.sleep(0.1)  # Simulate slow operation
            raise TimeoutError("Scanning timeout")

        # Mock that we have scanning libraries available
        with patch.object(harness, "available_scanners", ["pyzbar"]):
            with patch.object(harness, "svg_to_image") as mock_convert:
                with patch.object(harness, "apply_image_effects") as mock_effects:
                    with patch.object(harness, "scan_with_pyzbar") as mock_scan:
                        mock_convert.return_value = Mock()
                        mock_effects.return_value = Mock()  # Mock PIL Image after effects
                        mock_scan.side_effect = slow_scan

                        test_case = ScanTestCase("test", "Test", 150)
                        result = harness.validate_qr_with_test_case("<svg></svg>", "Test Data", test_case)

                        assert isinstance(result, ScanTestResult)
                        # Timeout errors are handled gracefully and return FAILURE, not ERROR
                        assert result.result == ScanResult.FAILURE
                        assert "No scanner could decode" in result.error_message


class TestScanningHarnessConfiguration:
    """Test scanning harness configuration and customization."""

    def test_harness_with_custom_timeout(self):
        """Test harness with custom scanning timeout."""
        harness = QRScanabilityHarness()

        # Test custom timeout setting (if supported)
        if hasattr(harness, "set_scanning_timeout"):
            harness.set_scanning_timeout(5.0)  # 5 second timeout
            assert harness.scanning_timeout == 5.0
        else:
            # Skip if timeout configuration not implemented
            pytest.skip("Custom timeout configuration not implemented")

    def test_harness_with_custom_scanner_order(self):
        """Test harness with custom scanner priority order."""
        harness = QRScanabilityHarness()

        # Test custom scanner ordering (if supported)
        if hasattr(harness, "set_scanner_priority"):
            custom_order = ["pyzbar", "OpenCV", "PIL"]
            harness.set_scanner_priority(custom_order)
            # Verify the order was set (implementation dependent)
        else:
            pytest.skip("Custom scanner priority not implemented")

    def test_generate_test_cases_with_parameters(self):
        """Test generating test cases with custom parameters."""
        harness = QRScanabilityHarness()

        # Generate test cases with custom DPI range
        if hasattr(harness, "generate_test_cases_with_dpi_range"):
            test_cases = harness.generate_test_cases_with_dpi_range(min_dpi=100, max_dpi=400, step=100)

            assert isinstance(test_cases, list)
            assert len(test_cases) > 0

            # Verify DPI values are in range
            dpi_values = [tc.dpi for tc in test_cases]
            assert min(dpi_values) >= 100
            assert max(dpi_values) <= 400
        else:
            pytest.skip("Custom DPI range generation not implemented")


class TestScanningHarnessReporting:
    """Test scanning harness reporting functionality."""

    def test_generate_summary_report(self):
        """Test generating summary report from results."""
        harness = QRScanabilityHarness()

        # Create sample results
        test_cases = [ScanTestCase(f"test_{i}", f"Test {i}", 150) for i in range(3)]
        results = [
            ScanTestResult(test_cases[0], ScanResult.SUCCESS, "Data", scan_time_ms=45.0),
            ScanTestResult(test_cases[1], ScanResult.SUCCESS, "Data", scan_time_ms=55.0),
            ScanTestResult(test_cases[2], ScanResult.FAILURE, error_message="Failed"),
        ]

        # Generate summary report
        if hasattr(harness, "generate_summary_report"):
            report = harness.generate_summary_report(results)

            assert isinstance(report, str)
            assert "SUCCESS" in report
            assert "FAILURE" in report
            assert "45.0" in report  # Scan time
        else:
            # Use analyze_results as fallback
            analysis = harness.analyze_results(results)
            assert isinstance(analysis, dict)
            assert "success_rate" in analysis

    def test_export_results_json(self):
        """Test exporting results to JSON format."""
        harness = QRScanabilityHarness()

        test_case = ScanTestCase("test", "Test", 150)
        result = ScanTestResult(test_case, ScanResult.SUCCESS, "Data")

        # Test JSON export if available
        if hasattr(harness, "export_results_json"):
            json_output = harness.export_results_json([result])

            assert isinstance(json_output, str)
            assert "test" in json_output
            assert "SUCCESS" in json_output
        else:
            pytest.skip("JSON export not implemented")

    def test_generate_detailed_report(self):
        """Test generating detailed test report."""
        harness = QRScanabilityHarness()

        # Create detailed test scenario
        test_case = ScanTestCase(
            "detailed_test",
            "Detailed test with all parameters",
            dpi=300,
            scale_factor=0.8,
            rotation_degrees=15,
            blur_radius=1.0,
            noise_level=0.05,
        )

        result = ScanTestResult(
            test_case=test_case,
            result=ScanResult.SUCCESS,
            decoded_data="Detailed Test Data",
            scan_time_ms=75.5,
            confidence=0.89,
        )

        # Generate detailed report
        if hasattr(harness, "generate_detailed_report"):
            report = harness.generate_detailed_report([result])

            assert isinstance(report, str)
            assert "detailed_test" in report
            assert "300" in report  # DPI
            assert "75.5" in report  # Scan time
            assert "0.89" in report  # Confidence
        else:
            pytest.skip("Detailed report generation not implemented")
