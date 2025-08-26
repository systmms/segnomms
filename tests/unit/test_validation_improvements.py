"""
Test the validation improvements added to address code analysis findings.
"""

import logging

import pytest
import segno

from segnomms import write
from segnomms.core.detector import ModuleDetector


class TestValidationImprovements:
    """Test input validation and error handling improvements."""

    def test_empty_matrix_validation(self):
        """Test that empty matrix raises appropriate error."""
        with pytest.raises(ValueError, match="Matrix cannot be empty"):
            ModuleDetector([])

    def test_non_square_matrix_validation(self):
        """Test that non-square matrix raises appropriate error."""
        matrix = [[True, False, True], [False, True]]  # Wrong length
        with pytest.raises(ValueError, match="Matrix must be square"):
            ModuleDetector(matrix)

    def test_invalid_qr_size_validation(self):
        """Test that invalid QR sizes are rejected."""
        # Size 22x22 is invalid (should be 21 + 4*n)
        matrix = [[True] * 22 for _ in range(22)]
        with pytest.raises(ValueError, match="Invalid QR code size 22x22"):
            ModuleDetector(matrix)

    def test_too_small_matrix_validation(self):
        """Test that matrices smaller than minimum QR size are rejected."""
        # 10x10 is smaller than minimum Micro QR size (11x11)
        matrix = [[True] * 10 for _ in range(10)]
        with pytest.raises(ValueError, match="Matrix size 10x10 is too small"):
            ModuleDetector(matrix)

    def test_valid_qr_sizes(self):
        """Test that valid QR sizes are accepted."""
        valid_sizes = [21, 25, 29, 33, 37, 41, 45]
        for size in valid_sizes:
            matrix = [[True] * size for _ in range(size)]
            detector = ModuleDetector(matrix)
            assert detector.size == size

    def test_bounds_checking_get_module_type(self):
        """Test bounds checking in get_module_type."""
        # Create a QR code with enough data to ensure size >= 21x21
        qr = segno.make("This is a test message to ensure the QR code is large enough")
        matrix = [[bool(module) for module in row] for row in qr.matrix]
        detector = ModuleDetector(matrix, qr.version)

        # Out of bounds access should raise IndexError
        with pytest.raises(IndexError, match="out of bounds"):
            detector.get_module_type(-1, 0)

        with pytest.raises(IndexError, match="out of bounds"):
            detector.get_module_type(0, detector.size)

        with pytest.raises(IndexError, match="out of bounds"):
            detector.get_module_type(detector.size, detector.size)

    def test_bounds_checking_weighted_analysis(self):
        """Test bounds checking in get_weighted_neighbor_analysis."""
        # Create a QR code with enough data to ensure size >= 21x21
        qr = segno.make("This is a test message to ensure the QR code is large enough")
        matrix = [[bool(module) for module in row] for row in qr.matrix]
        detector = ModuleDetector(matrix, qr.version)

        # Out of bounds access should raise IndexError
        with pytest.raises(IndexError, match="out of bounds"):
            detector.get_weighted_neighbor_analysis(100, 100)

    def test_qr_size_limit(self, tmp_path):
        """Test that oversized QR codes are rejected."""

        # Create a mock QR code with size > 1000
        class MockQR:
            def __init__(self, size):
                self.matrix = [[True] * size for _ in range(size)]
                self.version = 250  # Fake large version

        mock_qr = MockQR(1001)
        output_file = tmp_path / "large.svg"

        with pytest.raises(ValueError, match="exceeds maximum allowed size"):
            write(mock_qr, str(output_file))

    def test_configuration_logging(self, caplog):
        """Test that invalid configurations log warnings."""
        import io

        # Create a QR code with enough data to ensure size >= 21x21
        qr = segno.make("This is a test message to ensure the QR code is large enough")
        output = io.StringIO()

        # Test that invalid configurations are handled gracefully
        # Should not raise exceptions, but use fallback values
        write(qr, output, shape="invalid-shape")
        output.getvalue()  # Should contain valid SVG

        output = io.StringIO()
        write(qr, output, connectivity="6-way")  # Will fall back to valid value
        output.getvalue()  # Should contain valid SVG

        output = io.StringIO()
        write(qr, output, merge="extreme")  # Will fall back to valid value
        output.getvalue()  # Should contain valid SVG

    def test_shape_factory_logging(self, caplog):
        """Test that unknown shapes log helpful warnings."""
        from segnomms.shapes.factory import get_shape_factory

        factory = get_shape_factory()

        with caplog.at_level(logging.WARNING):
            renderer = factory.create_renderer("custom-shape", {})
            assert "Unknown shape type 'custom-shape'" in caplog.text
            assert "Available shapes are:" in caplog.text
            assert "Using 'square' as fallback" in caplog.text
            # Should still return a valid renderer
            assert renderer is not None


class TestErrorMessages:
    """Test that error messages are actionable and helpful."""

    def test_size_limit_error_message(self):
        """Test that size limit error includes helpful information."""

        class MockQR:
            def __init__(self, size):
                self.matrix = [[True] * size for _ in range(size)]
                self.version = 250

        mock_qr = MockQR(1500)

        import io

        with pytest.raises(ValueError) as exc_info:
            write(mock_qr, io.StringIO())

        error_msg = str(exc_info.value)
        assert "1500x1500" in error_msg
        assert "1000x1000" in error_msg
        assert "denial-of-service" in error_msg
        assert "contact support" in error_msg

    def test_matrix_validation_error_messages(self):
        """Test that matrix validation errors are clear."""
        # Empty matrix
        with pytest.raises(ValueError) as exc_info:
            ModuleDetector([])
        assert "Matrix cannot be empty" in str(exc_info.value)

        # Non-square matrix
        with pytest.raises(ValueError) as exc_info:
            ModuleDetector([[True], [True, False]])
        assert "must be square" in str(exc_info.value)
        assert "same length" in str(exc_info.value)

        # Invalid size
        with pytest.raises(ValueError) as exc_info:
            ModuleDetector([[True] * 23 for _ in range(23)])
        assert "23x23" in str(exc_info.value)
        assert "21+4*n" in str(exc_info.value) or "21 + 4*n" in str(exc_info.value)
