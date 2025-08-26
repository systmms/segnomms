"""
Integration tests for matrix manipulation workflows.

Tests for full matrix manipulation workflows including function pattern
preservation, mode switching, and end-to-end centerpiece operations.
"""

import pytest

from segnomms.config import CenterpieceConfig, ReserveMode
from segnomms.core.detector import ModuleDetector
from segnomms.core.matrix import MatrixManipulator


class TestMatrixManipulatorIntegration:
    """Integration tests for full matrix manipulation workflows."""

    @pytest.fixture
    def sample_matrix(self):
        """Create a sample 21x21 QR matrix for testing."""
        # Simple test matrix with all modules set to True
        matrix = []
        for i in range(21):
            row = []
            for j in range(21):
                row.append(True)
            matrix.append(row)
        return matrix

    @pytest.fixture
    def detector(self, sample_matrix):
        """Create a ModuleDetector for testing."""
        return ModuleDetector(sample_matrix)

    @pytest.fixture
    def manipulator(self, sample_matrix, detector):
        """Create a MatrixManipulator for testing."""
        return MatrixManipulator(sample_matrix, detector)

    def test_clear_centerpiece_area(self, manipulator, sample_matrix):
        """Test clearing modules in centerpiece area."""
        config = CenterpieceConfig(enabled=True, shape="rect", size=0.2, offset_x=0.0, offset_y=0.0, margin=0)

        # Clear centerpiece area
        modified = manipulator.clear_centerpiece_area(config)

        # Verify center is cleared
        assert modified[10][10] is False

        # Verify corners are not cleared
        assert modified[0][0] == sample_matrix[0][0]
        assert modified[20][20] == sample_matrix[20][20]

        # Verify it's a deep copy
        assert modified is not sample_matrix
        assert modified[0] is not sample_matrix[0]

    def test_clear_centerpiece_preserves_function_patterns(self, manipulator, detector):
        """Test that function patterns are preserved when clearing centerpiece."""
        # Create a config that would overlap with finder pattern
        config = CenterpieceConfig(
            enabled=True,
            shape="rect",
            size=0.5,  # Very large to ensure overlap
            offset_x=-0.3,
            offset_y=-0.3,
            margin=0,
        )

        # Get original state of finder pattern modules
        finder_modules = []
        for row in range(7):
            for col in range(7):
                module_type = detector.get_module_type(row, col)
                if module_type in ["finder", "finder_inner"]:
                    finder_modules.append((row, col, manipulator.matrix[row][col]))

        # Clear centerpiece
        modified = manipulator.clear_centerpiece_area(config)

        # Verify finder pattern modules retain their original state
        for row, col, original_value in finder_modules:
            assert (
                modified[row][col] == original_value
            ), f"Finder pattern module at ({row}, {col}) was modified"


class TestReserveModeIntegration:
    """Integration tests for different reserve area modes."""

    @pytest.fixture
    def sample_matrix(self):
        """Create a sample 21x21 QR matrix for testing."""
        matrix = []
        for i in range(21):
            row = []
            for j in range(21):
                row.append(True)
            matrix.append(row)
        return matrix

    @pytest.fixture
    def detector(self, sample_matrix):
        """Create a ModuleDetector for testing."""
        return ModuleDetector(sample_matrix)

    @pytest.fixture
    def manipulator(self, sample_matrix, detector):
        """Create a MatrixManipulator for testing."""
        return MatrixManipulator(sample_matrix, detector)

    def test_knockout_mode_basic(self, manipulator):
        """Test basic knockout mode functionality."""
        config = CenterpieceConfig(enabled=True, shape="circle", size=0.15, mode=ReserveMode.KNOCKOUT)

        # Test knockout mode
        modified = manipulator.clear_centerpiece_area(config)

        # In knockout mode, modules should be completely removed (set to False)
        center_cleared = not modified[10][10]  # Center should be cleared
        assert center_cleared

        # Edge modules outside centerpiece should be unchanged
        assert modified[0][0] == manipulator.matrix[0][0]

    def test_imprint_mode_preserves_matrix(self, manipulator):
        """Test that imprint mode preserves original matrix."""
        config = CenterpieceConfig(enabled=True, shape="circle", size=0.15, mode=ReserveMode.IMPRINT)

        # Test imprint mode
        modified = manipulator.clear_centerpiece_area(config)

        # In imprint mode, matrix should be unchanged (visual treatment handled elsewhere)
        assert modified == manipulator.matrix

        # But should generate metadata about the treatment
        metadata = manipulator.get_centerpiece_metadata(config)
        assert metadata["mode"] == ReserveMode.IMPRINT

    def test_imprint_mode_generates_metadata(self, manipulator):
        """Test that imprint mode generates appropriate metadata."""
        config = CenterpieceConfig(enabled=True, shape="circle", size=0.2, mode=ReserveMode.IMPRINT)

        # Clear centerpiece (should not modify in imprint mode)
        modified = manipulator.clear_centerpiece_area(config)
        assert modified is False or modified is None  # Imprint mode should not modify matrix

        # Get metadata
        metadata = manipulator.get_centerpiece_metadata(config)

        # Should have imprint-specific metadata
        assert "mode" in metadata
        assert metadata["mode"] == ReserveMode.IMPRINT
        assert "imprint_treatments" in metadata

        # Should have treatment information for affected modules
        treatments = metadata["imprint_treatments"]
        assert len(treatments) > 0

        # Each treatment should have opacity and size_ratio
        for treatment in treatments:
            assert "x" in treatment
            assert "y" in treatment
            assert "opacity" in treatment
            assert "size_ratio" in treatment
            assert 0 <= treatment["opacity"] <= 1.0
            assert 0 < treatment["size_ratio"] <= 1.0

    def test_knockout_mode_edge_refinement(self, manipulator):
        """Test edge refinement in knockout mode."""
        config = CenterpieceConfig(
            enabled=True,
            shape="circle",
            size=0.2,
            mode=ReserveMode.KNOCKOUT,
            margin=2,  # Add margin for edge refinement
        )

        # Get bounds before clearing
        bounds = manipulator.get_centerpiece_bounds(config)

        # Clear centerpiece
        modified = manipulator.clear_centerpiece_area(config)

        # Check that margin is respected
        # Modules near but outside the centerpiece bounds should be preserved
        edge_x = int(bounds["right"]) + 1
        edge_y = int(bounds["bottom"]) + 1

        if edge_x < 21 and edge_y < 21:
            # Edge module should be preserved due to margin
            assert modified[edge_y][edge_x] == manipulator.matrix[edge_y][edge_x]

    def test_centerpiece_metadata_with_modes(self, manipulator):
        """Test metadata generation with different modes."""
        # Test knockout mode metadata
        knockout_config = CenterpieceConfig(enabled=True, shape="rect", size=0.2, mode=ReserveMode.KNOCKOUT)

        knockout_metadata = manipulator.get_centerpiece_metadata(knockout_config)
        assert knockout_metadata["mode"] == ReserveMode.KNOCKOUT
        assert "cleared_modules" in knockout_metadata

        # Test imprint mode metadata
        imprint_config = CenterpieceConfig(enabled=True, shape="rect", size=0.2, mode=ReserveMode.IMPRINT)

        imprint_metadata = manipulator.get_centerpiece_metadata(imprint_config)
        assert imprint_metadata["mode"] == ReserveMode.IMPRINT
        assert "imprint_treatments" in imprint_metadata

        # Both should have common metadata
        for metadata in [knockout_metadata, imprint_metadata]:
            assert "shape" in metadata
            assert "size" in metadata
            assert "bounds" in metadata
            assert "area_info" in metadata


class TestComplexCenterpieceWorkflows:
    """Test complex centerpiece manipulation workflows."""

    @pytest.fixture
    def sample_matrix(self):
        """Create a sample 21x21 QR matrix for testing."""
        matrix = []
        for i in range(21):
            row = []
            for j in range(21):
                row.append(True)
            matrix.append(row)
        return matrix

    @pytest.fixture
    def detector(self, sample_matrix):
        """Create a ModuleDetector for testing."""
        return ModuleDetector(sample_matrix)

    @pytest.fixture
    def manipulator(self, sample_matrix, detector):
        """Create a MatrixManipulator for testing."""
        return MatrixManipulator(sample_matrix, detector)

    def test_multiple_centerpiece_operations(self, manipulator):
        """Test multiple centerpiece operations in sequence."""
        # First operation: small knockout
        config1 = CenterpieceConfig(
            enabled=True, shape="circle", size=0.1, mode=ReserveMode.KNOCKOUT, offset_x=-0.1
        )

        modified1 = manipulator.clear_centerpiece_area(config1)
        metadata1 = manipulator.get_centerpiece_metadata(config1)

        # Second operation: different position, imprint mode
        config2 = CenterpieceConfig(
            enabled=True, shape="rect", size=0.15, mode=ReserveMode.IMPRINT, offset_x=0.1, offset_y=0.1
        )

        # Use modified matrix from first operation
        manipulator2 = MatrixManipulator(modified1, manipulator.detector)
        modified2 = manipulator2.clear_centerpiece_area(config2)
        metadata2 = manipulator2.get_centerpiece_metadata(config2)

        # Verify both operations had effect
        assert metadata1["area_info"]["estimated_modules"] > 0
        assert metadata2["area_info"]["estimated_modules"] > 0

        # Final matrix should reflect first operation's knockout
        center1_x = 10 + int(-0.1 * 21)  # First centerpiece center
        assert modified2[10][center1_x] is False  # Should still be cleared

    def test_validation_with_complex_config(self, manipulator):
        """Test validation with complex centerpiece configuration."""
        config = CenterpieceConfig(
            enabled=True,
            shape="squircle",
            size=0.25,
            mode=ReserveMode.IMPRINT,
            offset_x=0.05,
            offset_y=-0.05,
            margin=3,
        )

        # Validate the configuration
        validation = manipulator.validate_reserve_impact(config, "M")
        metadata = manipulator.get_centerpiece_metadata(config)

        # Should provide comprehensive validation results
        assert "safe" in validation
        assert "estimated_modules" in validation
        assert "warnings" in validation
        assert isinstance(validation["safe"], bool)

        # Metadata should be complete
        assert metadata["shape"] == "squircle"
        assert metadata["mode"] == ReserveMode.IMPRINT
        assert "center" in metadata
        assert "bounds" in metadata

        # Center should be offset
        center = metadata["center"]
        assert center["x"] != 10  # Should be offset from default center
        assert center["y"] != 10

    def test_edge_case_configurations(self, manipulator):
        """Test edge case centerpiece configurations."""
        # Very small centerpiece
        tiny_config = CenterpieceConfig(
            enabled=True, shape="circle", size=0.05, mode=ReserveMode.KNOCKOUT  # 5% - very small
        )

        metadata_tiny = manipulator.get_centerpiece_metadata(tiny_config)
        assert metadata_tiny["area_info"]["estimated_modules"] >= 0

        # Very large centerpiece (should trigger warnings)
        large_config = CenterpieceConfig(
            enabled=True, shape="rect", size=0.4, mode=ReserveMode.KNOCKOUT  # 40% - very large
        )

        validation_large = manipulator.validate_reserve_impact(large_config, "L")  # Low error correction
        # Should likely be unsafe for low error correction
        assert "warnings" in validation_large

        # Edge position (near corner)
        edge_config = CenterpieceConfig(
            enabled=True,
            shape="rect",
            size=0.15,
            offset_x=0.3,  # Near edge
            offset_y=0.3,
            mode=ReserveMode.IMPRINT,
        )

        bounds_edge = manipulator.get_centerpiece_bounds(edge_config)
        # Should handle edge positioning gracefully
        assert bounds_edge["left"] >= 0
        assert bounds_edge["top"] >= 0
        assert bounds_edge["right"] <= 21
        assert bounds_edge["bottom"] <= 21
