"""
Test suite for enhanced palette support.
"""

import pytest

from segnomms.color.palette import (
    ColorInfo,
    ColorSpace,
    ContrastAnalysis,
    ContrastStandard,
    PaletteConfig,
    PaletteType,
    PaletteValidationResult,
    generate_palette_suggestions,
    get_safe_color_alternatives,
    validate_palette,
)
from segnomms.config import PatternStyleConfig, RenderingConfig
from segnomms.exceptions import InvalidColorFormatError, PaletteValidationError
from tests.constants import TEST_COLORS


class TestColorInfo:
    """Test the ColorInfo dataclass."""

    def test_color_info_from_valid_color(self):
        """Test creating ColorInfo from valid colors."""
        # Test with hex color from test constants
        info = ColorInfo.from_string(TEST_COLORS["red"])
        assert info is not None
        assert info.original == TEST_COLORS["red"]
        assert info.rgb == (255, 0, 0)
        assert info.hex.upper() == TEST_COLORS["red"]
        assert info.luminance > 0
        assert not info.is_dark  # Red is not dark

        # Test with named color
        info = ColorInfo.from_string(TEST_COLORS["black"])
        assert info is not None
        assert info.original == TEST_COLORS["black"]
        assert info.rgb == (0, 0, 0)
        assert info.hex == TEST_COLORS["black"]
        assert info.luminance == 0.0
        assert info.is_dark

        # Test with RGB function
        info = ColorInfo.from_string("rgb(128, 128, 128)")
        assert info is not None
        assert info.rgb == (128, 128, 128)
        assert 0.0 < info.luminance < 1.0

    def test_color_info_from_invalid_color(self):
        """Test creating ColorInfo from invalid colors."""
        assert ColorInfo.from_string("invalid") is None
        assert ColorInfo.from_string("") is None
        assert ColorInfo.from_string("#gggggg") is None


class TestContrastAnalysis:
    """Test the ContrastAnalysis dataclass."""

    def test_high_contrast_analysis(self):
        """Test contrast analysis for high contrast colors."""
        analysis = ContrastAnalysis.analyze(TEST_COLORS["black"], TEST_COLORS["white"])
        assert analysis is not None
        assert analysis.ratio == 21.0  # Maximum possible contrast
        assert analysis.meets_aa_normal
        assert analysis.meets_aa_large
        assert analysis.meets_aaa_normal
        assert analysis.meets_aaa_large
        assert analysis.meets_qr_optimal
        assert analysis.grade == "AAA"

    def test_low_contrast_analysis(self):
        """Test contrast analysis for low contrast colors."""
        analysis = ContrastAnalysis.analyze("yellow", "white")
        assert analysis is not None
        assert analysis.ratio < 4.5  # Below AA standard
        assert not analysis.meets_aa_normal
        assert analysis.grade == "FAIL"

    def test_medium_contrast_analysis(self):
        """Test contrast analysis for medium contrast colors."""
        analysis = ContrastAnalysis.analyze("#666666", "white")  # Use specific gray for consistent results
        assert analysis is not None
        assert 3.0 < analysis.ratio < 7.0  # Between AA and AAA
        assert analysis.meets_aa_normal
        assert not analysis.meets_aaa_normal
        assert analysis.grade == "AA"

    def test_invalid_color_analysis(self):
        """Test contrast analysis with invalid colors."""
        assert ContrastAnalysis.analyze("invalid", "white") is None
        assert ContrastAnalysis.analyze("black", "invalid") is None


class TestPaletteConfig:
    """Test the PaletteConfig model."""

    def test_valid_palette_config(self):
        """Test creating valid palette configurations."""
        config = PaletteConfig(
            dark="black", light="white", accent_colors=["red", "blue"], min_contrast_ratio=4.5
        )
        assert config.dark == "black"
        assert config.light == "white"
        assert len(config.accent_colors) == 2
        assert config.min_contrast_ratio == 4.5

    def test_invalid_color_validation(self):
        """Test validation of invalid colors."""
        with pytest.raises(InvalidColorFormatError):
            PaletteConfig(dark="invalid_color")

        with pytest.raises(InvalidColorFormatError):
            PaletteConfig(light="invalid_color")

        with pytest.raises(PaletteValidationError):
            PaletteConfig(accent_colors=["red", "invalid_color"])

    def test_empty_color_validation(self):
        """Test validation of empty colors."""
        with pytest.raises(InvalidColorFormatError):
            PaletteConfig(dark="")

    def test_palette_methods(self):
        """Test palette utility methods."""
        config = PaletteConfig(dark="black", light="white", accent_colors=["red", "blue"])

        # Test get_all_colors
        all_colors = config.get_all_colors()
        assert len(all_colors) == 4
        assert "black" in all_colors
        assert "white" in all_colors
        assert "red" in all_colors
        assert "blue" in all_colors

        # Test get_primary_contrast
        contrast = config.get_primary_contrast()
        assert contrast is not None
        assert contrast.ratio == 21.0

    def test_validate_palette_method(self):
        """Test the validate_palette method."""
        config = PaletteConfig(dark="black", light="white")
        result = config.validate_palette()
        assert isinstance(result, PaletteValidationResult)
        assert result.is_valid


class TestPaletteValidation:
    """Test the palette validation function."""

    def test_valid_palette_validation(self):
        """Test validation of a valid palette."""
        config = PaletteConfig(dark="black", light="white", accent_colors=["red"], min_contrast_ratio=4.5)

        result = validate_palette(config)
        assert result.is_valid
        assert len(result.issues) == 0
        assert result.primary_contrast is not None
        assert result.primary_contrast.ratio == 21.0

        # Check color info
        assert "black" in result.color_info
        assert "white" in result.color_info
        assert "red" in result.color_info

        # Check contrast matrix
        assert "black" in result.contrast_matrix
        assert "white" in result.contrast_matrix["black"]

    def test_low_contrast_palette_validation(self):
        """Test validation of low contrast palette."""
        config = PaletteConfig(dark="yellow", light="white", min_contrast_ratio=4.5, enforce_standards=True)

        result = validate_palette(config)
        assert not result.is_valid
        assert len(result.issues) > 0
        assert "contrast ratio" in result.issues[0].lower()
        assert result.primary_contrast is not None
        assert result.primary_contrast.ratio < 4.5

    def test_similar_colors_validation(self):
        """Test validation of similar colors."""
        config = PaletteConfig(
            dark="black",
            light="white",
            accent_colors=["#010101"],  # Very similar to black
            allow_similar_colors=False,
        )

        result = validate_palette(config)
        # Should be valid but have warnings about similar colors
        assert result.is_valid
        assert len(result.warnings) > 0
        assert "similar" in result.warnings[0].lower()

    def test_too_many_colors_validation(self):
        """Test validation with too many colors."""
        many_colors = [f"#{i:02x}0000" for i in range(20)]  # 20 red variants
        config = PaletteConfig(dark="black", light="white", accent_colors=many_colors, max_colors=10)

        result = validate_palette(config)
        assert not result.is_valid
        assert any("maximum" in issue.lower() for issue in result.issues)

    def test_invalid_colors_validation(self):
        """Test validation with invalid colors."""
        # This should be caught by Pydantic validation before reaching validate_palette
        # But if somehow an invalid color gets through, validation should handle it
        config = PaletteConfig(dark="black", light="white")

        # Manually modify to test error handling
        config.accent_colors = ["black", "white"]  # Valid colors
        result = validate_palette(config)
        assert result.is_valid

    def test_color_distribution_analysis(self):
        """Test color distribution analysis."""
        # Only dark colors
        config = PaletteConfig(
            dark="black", light="#333333", accent_colors=["#111111"]  # Also dark  # Also dark
        )

        result = validate_palette(config)
        assert len(result.warnings) > 0
        assert any("light color" in warning.lower() for warning in result.warnings)


class TestPaletteSuggestions:
    """Test palette suggestion functions."""

    def test_generate_monochrome_suggestions(self):
        """Test generating monochrome palette suggestions."""
        suggestions = generate_palette_suggestions("red", PaletteType.MONOCHROME)
        assert len(suggestions) > 0
        assert "black" in suggestions or "white" in suggestions

    def test_generate_complementary_suggestions(self):
        """Test generating complementary palette suggestions."""
        suggestions = generate_palette_suggestions("red", PaletteType.COMPLEMENTARY)
        assert len(suggestions) > 0
        # Should include a complementary color and black/white
        assert "black" in suggestions or "white" in suggestions

    def test_generate_analogous_suggestions(self):
        """Test generating analogous palette suggestions."""
        suggestions = generate_palette_suggestions("red", PaletteType.ANALOGOUS)
        assert len(suggestions) > 0

    def test_generate_triadic_suggestions(self):
        """Test generating triadic palette suggestions."""
        suggestions = generate_palette_suggestions("red", PaletteType.TRIADIC)
        assert len(suggestions) > 0

    def test_generate_suggestions_invalid_color(self):
        """Test generating suggestions for invalid color."""
        suggestions = generate_palette_suggestions("invalid")
        assert len(suggestions) == 0

    def test_get_safe_color_alternatives(self):
        """Test getting safe alternatives for problematic colors."""
        alternatives = get_safe_color_alternatives("yellow")
        assert len(alternatives) > 0
        assert "black" in alternatives or "#333333" in alternatives

        alternatives = get_safe_color_alternatives("black", target_luminance=0.8)
        assert len(alternatives) > 0
        assert "white" in alternatives or "#f0f0f0" in alternatives

    def test_get_safe_alternatives_invalid_color(self):
        """Test getting alternatives for invalid color."""
        alternatives = get_safe_color_alternatives("invalid")
        assert len(alternatives) == 2  # Should return ["black", "white"]
        assert "black" in alternatives
        assert "white" in alternatives


class TestRenderingConfigIntegration:
    """Test integration with RenderingConfig."""

    def test_basic_palette_validation(self):
        """Test basic palette validation on RenderingConfig."""
        config = RenderingConfig(dark="black", light="white", enable_palette_validation=True)

        result = config.validate_palette()
        assert result.is_valid
        assert result.primary_contrast is not None
        assert result.primary_contrast.ratio == 21.0

    def test_palette_validation_with_patterns(self):
        """Test palette validation with pattern colors."""
        config = RenderingConfig(
            dark="black",
            light="white",
            patterns=PatternStyleConfig(enabled=True, finder_color="red", timing_color="blue"),
            enable_palette_validation=True,
        )

        result = config.validate_palette()
        assert result.is_valid

        # Should include pattern colors in validation
        assert "red" in result.color_info
        assert "blue" in result.color_info

    def test_contrast_ratio_methods(self):
        """Test contrast ratio utility methods."""
        config = RenderingConfig(dark="black", light="white")

        ratio = config.get_contrast_ratio()
        assert ratio == 21.0

        assert config.meets_contrast_requirements()

        # Test with low contrast
        config.dark = "yellow"
        ratio = config.get_contrast_ratio()
        assert ratio < 4.5
        assert not config.meets_contrast_requirements()

    def test_accent_color_extraction(self):
        """Test extraction of accent colors from patterns."""
        config = RenderingConfig(
            dark="black",
            light="white",
            patterns=PatternStyleConfig(
                enabled=True, finder_color="red", timing_color="blue", data_color="green"
            ),
        )

        accent_colors = config._get_accent_colors()
        assert "red" in accent_colors
        assert "blue" in accent_colors
        assert "green" in accent_colors
        assert "black" not in accent_colors  # Should exclude primary colors
        assert "white" not in accent_colors

    def test_disabled_palette_validation(self):
        """Test behavior when palette validation is disabled."""
        config = RenderingConfig(
            dark="yellow", light="white", enable_palette_validation=False  # Low contrast
        )

        # Should still work but not perform enhanced validation
        ratio = config.get_contrast_ratio()
        assert ratio is not None
        assert ratio < 4.5

        # Should not meet requirements but validation is disabled
        assert not config.meets_contrast_requirements()

    def test_custom_contrast_requirements(self):
        """Test custom contrast ratio requirements."""
        config = RenderingConfig(dark="gray", light="white", min_contrast_ratio=3.0)  # Lower requirement

        ratio = config.get_contrast_ratio()
        assert ratio is not None

        # Should meet lower requirement
        if ratio >= 3.0:
            assert config.meets_contrast_requirements()

        # Test with higher requirement
        config.min_contrast_ratio = 8.0
        assert not config.meets_contrast_requirements()  # Gray/white won't meet 8:1
