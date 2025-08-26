"""
Unit tests for accessibility core components.

Tests for configuration validation, ID generation, and element accessibility
without external dependencies.
"""

import pytest

from segnomms.a11y.accessibility import (
    AccessibilityConfig,
    AccessibilityLevel,
    ARIARole,
    ElementAccessibility,
    IDGenerator,
    create_basic_accessibility,
    create_enhanced_accessibility,
    create_minimal_accessibility,
)


class TestAccessibilityConfig:
    """Test the AccessibilityConfig model."""

    def test_default_config(self):
        """Test default accessibility configuration."""
        config = AccessibilityConfig()
        assert config.enabled is True
        assert config.id_prefix == "qr"
        assert config.use_stable_ids is True
        assert config.enable_aria is True
        assert config.root_role == ARIARole.IMG
        assert config.root_label == "QR Code"
        assert config.target_compliance == AccessibilityLevel.AA

    def test_valid_id_prefix(self):
        """Test valid ID prefix validation."""
        # Valid prefixes
        valid_prefixes = ["qr", "qr-code", "my_qr", "QR123", "a"]
        for prefix in valid_prefixes:
            config = AccessibilityConfig(id_prefix=prefix)
            assert config.id_prefix == prefix

    def test_invalid_id_prefix(self):
        """Test invalid ID prefix validation."""
        # Invalid prefixes (start with number, contain spaces, special chars)
        invalid_prefixes = ["123qr", "qr code", "qr@code", "", "!invalid"]
        for prefix in invalid_prefixes:
            with pytest.raises(ValueError, match="ID prefix must start with a letter"):
                AccessibilityConfig(id_prefix=prefix)

    def test_valid_focus_elements(self):
        """Test valid focus element validation."""
        valid_elements = ["root", "frame", "centerpiece", "modules", "finder", "timing"]
        config = AccessibilityConfig(focus_visible_elements=valid_elements)
        assert config.focus_visible_elements == valid_elements

    def test_invalid_focus_elements(self):
        """Test invalid focus element validation."""
        with pytest.raises(ValueError, match="Invalid focus element"):
            AccessibilityConfig(focus_visible_elements=["root", "invalid_element"])


class TestIDGenerator:
    """Test the IDGenerator class."""

    @pytest.fixture
    def generator(self):
        """Create an IDGenerator for testing."""
        config = AccessibilityConfig(id_prefix="test", include_coordinates=True)
        return IDGenerator(config)

    def test_basic_id_generation(self, generator):
        """Test basic ID generation."""
        # Test basic module ID
        module_id = generator.generate_module_id(5, 10)
        assert module_id == "test-module-5-10"

        # Test pattern IDs
        finder_id = generator.generate_pattern_id("finder", 0)
        assert finder_id == "test-finder-0"

        timing_id = generator.generate_pattern_id("timing", None)
        assert timing_id == "test-timing"

    def test_coordinate_based_ids(self, generator):
        """Test coordinate-based ID generation."""
        # Test various coordinates
        coords = [(0, 0), (1, 5), (20, 20), (100, 999)]
        for x, y in coords:
            module_id = generator.generate_module_id(x, y)
            expected = f"test-module-{x}-{y}"
            assert module_id == expected

    def test_pattern_ids(self, generator):
        """Test pattern-specific ID generation."""
        # Test finder patterns (0-2)
        for i in range(3):
            finder_id = generator.generate_pattern_id("finder", i)
            assert finder_id == f"test-finder-{i}"

        # Test alignment patterns
        alignment_id = generator.generate_pattern_id("alignment", 5)
        assert alignment_id == "test-alignment-5"

        # Test timing patterns (no index)
        timing_id = generator.generate_pattern_id("timing", None)
        assert timing_id == "test-timing"

        # Test frame elements
        frame_id = generator.generate_pattern_id("frame", None)
        assert frame_id == "test-frame"

        # Test centerpiece
        centerpiece_id = generator.generate_pattern_id("centerpiece", None)
        assert centerpiece_id == "test-centerpiece"

    def test_unique_id_generation(self, generator):
        """Test that IDs are unique for different coordinates."""
        ids = set()

        # Generate IDs for a grid
        for x in range(10):
            for y in range(10):
                module_id = generator.generate_module_id(x, y)
                assert module_id not in ids, f"Duplicate ID generated: {module_id}"
                ids.add(module_id)

        # Test pattern uniqueness
        pattern_ids = set()
        pattern_types = ["finder", "alignment", "timing", "frame", "centerpiece"]
        for pattern_type in pattern_types:
            if pattern_type in ["finder", "alignment"]:
                for i in range(5):
                    pattern_id = generator.generate_pattern_id(pattern_type, i)
                    assert pattern_id not in pattern_ids
                    pattern_ids.add(pattern_id)
            else:
                pattern_id = generator.generate_pattern_id(pattern_type, None)
                assert pattern_id not in pattern_ids
                pattern_ids.add(pattern_id)

    def test_other_id_types(self, generator):
        """Test other ID generation methods."""
        # Test group IDs
        group_id = generator.generate_group_id("data-modules")
        assert group_id == "test-data-modules-group"

        # Test layer IDs
        layer_id = generator.generate_layer_id("background")
        assert layer_id == "test-layer-background"

        # Test title/desc IDs
        title_id = generator.generate_title_id()
        assert title_id == "test-title"

        desc_id = generator.generate_desc_id()
        assert desc_id == "test-desc"


class TestElementAccessibility:
    """Test the ElementAccessibility class."""

    def test_basic_accessibility_element(self):
        """Test basic accessibility element creation."""
        element = ElementAccessibility(
            element_id="test-element",
            aria_role=ARIARole.GROUP.value,  # Use available role
            aria_label="Test Button",
            aria_describedby="description-element",
        )

        assert element.element_id == "test-element"
        assert element.aria_role == ARIARole.GROUP.value
        assert element.aria_label == "Test Button"
        assert element.aria_describedby == "description-element"
        assert element.tabindex is None

    def test_optional_attributes(self):
        """Test accessibility element with optional attributes."""
        element = ElementAccessibility(
            element_id="focusable-element",
            aria_role=ARIARole.IMG.value,
            aria_label="Interactive QR Code",
            tabindex=0,
            title="QR Code Title",
        )

        assert element.element_id == "focusable-element"
        assert element.aria_role == ARIARole.IMG.value
        assert element.tabindex == 0
        assert element.title == "QR Code Title"

    def test_tabindex_handling(self):
        """Test tabindex handling logic."""
        # Test tabindex preservation in current implementation
        element_with_tabindex = ElementAccessibility(
            element_id="focusable-element",
            aria_role=ARIARole.IMG.value,
            aria_label="Static QR Code",
            tabindex=0,
        )
        assert element_with_tabindex.tabindex == 0

        # Test element without tabindex
        element_no_tabindex = ElementAccessibility(
            element_id="no-tabindex",
            aria_role=ARIARole.APPLICATION.value,
            aria_label="Interactive QR Code",
            tabindex=-1,
        )
        assert element_no_tabindex.tabindex == -1


class TestAccessibilityPresets:
    """Test accessibility preset functions."""

    def test_basic_accessibility_preset(self):
        """Test basic accessibility preset."""
        config = create_basic_accessibility()

        assert config.enabled is True
        assert config.enable_aria is True
        assert config.use_stable_ids is True
        assert config.target_compliance == AccessibilityLevel.AA
        assert config.root_role == ARIARole.IMG

    def test_enhanced_accessibility_preset(self):
        """Test enhanced accessibility preset."""
        config = create_enhanced_accessibility()

        assert config.enabled is True
        assert config.enable_aria is True
        assert config.use_stable_ids is True
        assert config.target_compliance == AccessibilityLevel.AAA
        assert config.root_role == ARIARole.IMG
        assert "finder" in config.focus_visible_elements
        assert "frame" in config.focus_visible_elements
        assert "centerpiece" in config.focus_visible_elements

    def test_minimal_accessibility_preset(self):
        """Test minimal accessibility preset."""
        config = create_minimal_accessibility()

        assert config.enabled is True
        assert config.enable_aria is False  # Minimal ARIA
        assert config.use_stable_ids is False  # Allow dynamic IDs
        assert config.target_compliance == AccessibilityLevel.A
        assert config.focus_visible_elements == ["root"]  # Only root focusable
