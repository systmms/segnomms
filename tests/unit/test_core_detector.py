"""
Unit tests for segnomms.core.detector module.

Tests the ModuleDetector class which identifies different types of modules
in QR codes (finder patterns, timing patterns, data modules, etc.).
"""

import pytest

from segnomms.core.detector import (
    ALIGNMENT_PATTERN_SIZE,
    FINDER_PATTERN_POSITIONS,
    FINDER_SIZE,
    ModuleDetector,
)


class TestModuleDetector:
    """Test ModuleDetector class functionality."""

    def test_detector_initialization_with_version(self):
        """Test detector initialization with explicit version."""
        # Create a simple 21x21 matrix (version 1)
        matrix = [[True] * 21 for _ in range(21)]

        detector = ModuleDetector(matrix, version=1)
        assert detector.get_version() == 1
        assert detector.get_size() == 21
        assert detector.matrix == matrix

    def test_detector_initialization_without_version(self):
        """Test detector initialization with version estimation."""
        # Create a 25x25 matrix (version 2)
        matrix = [[True] * 25 for _ in range(25)]

        detector = ModuleDetector(matrix)
        assert detector.get_version() == 2
        assert detector.get_size() == 25

    def test_version_parsing_valid_inputs(self):
        """Test version parsing with various valid inputs."""
        matrix = [[True] * 21 for _ in range(21)]
        detector = ModuleDetector(matrix, version=1)

        # Test integer input
        assert detector._parse_version(1) == 1
        assert detector._parse_version(10) == 10

        # Test string input
        assert detector._parse_version("1") == 1
        assert detector._parse_version("15") == 15

        # Test None input (should estimate)
        assert detector._parse_version(None) == 1  # 21x21 matrix

    def test_version_parsing_invalid_inputs(self):
        """Test version parsing with invalid inputs."""
        matrix = [[True] * 21 for _ in range(21)]
        detector = ModuleDetector(matrix, version=1)

        # The actual implementation doesn't validate version ranges in _parse_version
        # It accepts any integer or tries to parse strings
        assert detector._parse_version(0) == 0
        assert detector._parse_version(41) == 41

        # Test invalid string format
        with pytest.raises(ValueError):
            detector._parse_version("invalid")

    def test_version_estimation(self):
        """Test automatic version estimation from matrix size."""
        # Test various QR code sizes
        test_cases = [
            (21, 1),  # Version 1
            (25, 2),  # Version 2
            (29, 3),  # Version 3
            (33, 4),  # Version 4
            (37, 5),  # Version 5
        ]

        for size, expected_version in test_cases:
            matrix = [[True] * size for _ in range(size)]
            detector = ModuleDetector(matrix)
            assert detector._estimate_version() == expected_version

    def test_version_estimation_invalid_size(self):
        """Test version estimation with invalid matrix size."""
        # Invalid size that doesn't match any QR version
        matrix = [[True] * 20 for _ in range(20)]

        with pytest.raises(ValueError, match="Invalid QR code size"):
            ModuleDetector(matrix)

    def test_alignment_positions_version_1(self):
        """Test alignment pattern positions for version 1 (no alignment patterns)."""
        matrix = [[True] * 21 for _ in range(21)]
        detector = ModuleDetector(matrix, version=1)

        positions = detector._get_alignment_positions()
        assert positions == []

    def test_alignment_positions_version_2(self):
        """Test alignment pattern positions for version 2."""
        matrix = [[True] * 25 for _ in range(25)]
        detector = ModuleDetector(matrix, version=2)

        positions = detector._get_alignment_positions()
        # Version 2 has one alignment pattern at (size-7, size-7)
        assert len(positions) == 1
        assert (18, 18) in positions  # 25-7 = 18

    def test_module_type_finder_patterns(self):
        """Test detection of finder pattern modules."""
        matrix = [[True] * 21 for _ in range(21)]
        detector = ModuleDetector(matrix, version=1)

        # Test corner finder patterns
        # Top-left finder
        assert detector.get_module_type(0, 0) == "finder"
        assert detector.get_module_type(3, 3) == "finder_inner"
        assert detector.get_module_type(6, 6) == "finder"

        # Top-right finder
        assert detector.get_module_type(0, 14) == "finder"
        assert detector.get_module_type(3, 17) == "finder_inner"

        # Bottom-left finder
        assert detector.get_module_type(14, 0) == "finder"
        assert detector.get_module_type(17, 3) == "finder_inner"

    def test_module_type_separators(self):
        """Test detection of separator modules around finder patterns."""
        matrix = [[True] * 21 for _ in range(21)]
        detector = ModuleDetector(matrix, version=1)

        # Separators are around finder patterns
        # Top-left separator
        assert detector.get_module_type(7, 0) == "separator"
        assert detector.get_module_type(0, 7) == "separator"
        assert detector.get_module_type(7, 7) == "separator"

    def test_module_type_timing_patterns(self):
        """Test detection of timing pattern modules."""
        matrix = [[True] * 21 for _ in range(21)]
        detector = ModuleDetector(matrix, version=1)

        # Timing patterns are at row 6 and column 6
        # Skip the finder pattern intersections
        assert detector.get_module_type(6, 8) == "timing"
        assert detector.get_module_type(6, 12) == "timing"
        assert detector.get_module_type(8, 6) == "timing"
        assert detector.get_module_type(12, 6) == "timing"

    def test_module_type_format_information(self):
        """Test detection of format information modules."""
        matrix = [[True] * 21 for _ in range(21)]
        detector = ModuleDetector(matrix, version=1)

        # Format information is around timing patterns
        # Horizontal format strip
        assert detector.get_module_type(8, 0) == "format"
        assert detector.get_module_type(8, 1) == "format"
        assert detector.get_module_type(8, 7) == "format"

        # Vertical format strip
        assert detector.get_module_type(0, 8) == "format"
        assert detector.get_module_type(1, 8) == "format"
        assert detector.get_module_type(7, 8) == "format"

    def test_module_type_data_modules(self):
        """Test detection of data modules."""
        matrix = [[True] * 21 for _ in range(21)]
        detector = ModuleDetector(matrix, version=1)

        # Data modules are everything else
        # Pick some positions that should be data
        assert detector.get_module_type(9, 9) == "data"
        assert detector.get_module_type(10, 15) == "data"
        assert detector.get_module_type(15, 10) == "data"

    def test_module_type_alignment_patterns(self):
        """Test detection of alignment pattern modules."""
        matrix = [[True] * 25 for _ in range(25)]
        detector = ModuleDetector(matrix, version=2)

        # Version 2 has alignment pattern at (18, 18)
        center_row, center_col = 18, 18

        # Center of alignment pattern
        assert detector.get_module_type(center_row, center_col) == "alignment_center"

        # Edges of alignment pattern (5x5 size)
        assert detector.get_module_type(center_row - 2, center_col - 2) == "alignment"
        assert detector.get_module_type(center_row + 2, center_col + 2) == "alignment"

    def test_module_type_bounds_checking(self):
        """Test module type detection with out-of-bounds coordinates."""
        matrix = [[True] * 21 for _ in range(21)]
        detector = ModuleDetector(matrix, version=1)

        # Out of bounds should raise IndexError
        with pytest.raises(IndexError, match="out of bounds"):
            detector.get_module_type(-1, 0)

        with pytest.raises(IndexError, match="out of bounds"):
            detector.get_module_type(0, -1)

        with pytest.raises(IndexError, match="out of bounds"):
            detector.get_module_type(21, 0)

        with pytest.raises(IndexError, match="out of bounds"):
            detector.get_module_type(0, 21)

    def test_is_module_active(self):
        """Test checking if modules are active (dark)."""
        # Create matrix with minimum size (21x21) and alternating pattern
        matrix = [[False] * 21 for _ in range(21)]
        # Set some modules as active
        matrix[0][0] = True
        matrix[0][1] = False
        matrix[1][0] = False
        matrix[1][1] = True

        detector = ModuleDetector(matrix, version=1)

        assert detector.is_module_active(0, 0) is True
        assert detector.is_module_active(0, 1) is False
        assert detector.is_module_active(1, 0) is False
        assert detector.is_module_active(1, 1) is True

    def test_is_module_active_bounds(self):
        """Test is_module_active with out-of-bounds coordinates."""
        matrix = [[True] * 21 for _ in range(21)]
        detector = ModuleDetector(matrix, version=1)

        # Out of bounds should return False
        assert detector.is_module_active(-1, 0) is False
        assert detector.is_module_active(0, -1) is False
        assert detector.is_module_active(21, 0) is False
        assert detector.is_module_active(0, 21) is False


class TestModuleDetectorEdgeCases:
    """Test edge cases and error conditions."""

    def test_empty_matrix(self):
        """Test detector with empty matrix."""
        with pytest.raises(ValueError):
            ModuleDetector([])

    def test_non_square_matrix(self):
        """Test detector with non-square matrix."""
        matrix = [[True] * 20 for _ in range(21)]  # 21x20 matrix

        with pytest.raises(ValueError):
            ModuleDetector(matrix)

    def test_matrix_too_small(self):
        """Test detector with matrix smaller than minimum QR size."""
        matrix = [[True] * 10 for _ in range(10)]  # Too small

        with pytest.raises(ValueError):
            ModuleDetector(matrix)

    def test_version_mismatch_warning(self):
        """Test when provided version doesn't match matrix size."""
        # 25x25 matrix (version 2) but claim it's version 1
        matrix = [[True] * 25 for _ in range(25)]

        # Should use provided version but may cause issues
        detector = ModuleDetector(matrix, version=1)
        assert detector.get_version() == 1  # Uses provided version
        assert detector.get_size() == 25  # But matrix is still 25x25


class TestModuleDetectorIntegration:
    """Integration tests with real QR code patterns."""

    def test_complete_qr_analysis(self):
        """Test analyzing a complete QR code pattern."""
        # Create a realistic 21x21 QR matrix with proper finder patterns
        matrix = [[False] * 21 for _ in range(21)]

        # Add finder patterns (simplified)
        for row in range(7):
            for col in range(7):
                # Top-left finder
                matrix[row][col] = (
                    row in [0, 6]
                    or col in [0, 6]
                    or (1 <= row <= 5 and 1 <= col <= 5 and (row in [2, 4] or col in [2, 4]))
                )

                # Top-right finder
                if col < 7:
                    matrix[row][14 + col] = matrix[row][col]

                # Bottom-left finder
                if row < 7:
                    matrix[14 + row][col] = matrix[row][col]

        detector = ModuleDetector(matrix, version=1)

        # Verify different module types are detected
        module_types = set()
        for row in range(21):
            for col in range(21):
                module_types.add(detector.get_module_type(row, col))

        # Should have detected multiple types
        expected_types = {"finder", "finder_inner", "separator", "timing", "format", "data"}
        assert expected_types.issubset(module_types)

    def test_detector_config_integration(self):
        """Test detector with configuration object."""
        matrix = [[True] * 21 for _ in range(21)]
        detector = ModuleDetector(matrix, version=1)

        # Should work with different detection scenarios
        assert detector.get_module_type(0, 0) == "finder"
        assert detector.get_module_type(10, 10) == "data"

        # Verify all public methods work
        assert isinstance(detector.get_version(), int)
        assert isinstance(detector.get_size(), int)
        assert isinstance(detector.is_module_active(0, 0), bool)


class TestFinderPatternConstants:
    """Test module constants and helper values."""

    def test_finder_pattern_positions(self):
        """Test finder pattern position constants."""
        assert len(FINDER_PATTERN_POSITIONS) == 3
        assert (0, 0) in FINDER_PATTERN_POSITIONS  # Top-left
        assert (0, -7) in FINDER_PATTERN_POSITIONS  # Top-right
        assert (-7, 0) in FINDER_PATTERN_POSITIONS  # Bottom-left

    def test_pattern_sizes(self):
        """Test pattern size constants."""
        assert FINDER_SIZE == 7
        assert ALIGNMENT_PATTERN_SIZE == 5

        # Verify these are positive integers
        assert isinstance(FINDER_SIZE, int)
        assert isinstance(ALIGNMENT_PATTERN_SIZE, int)
        assert FINDER_SIZE > 0
        assert ALIGNMENT_PATTERN_SIZE > 0
