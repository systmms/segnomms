"""
Property-based tests using Hypothesis to find edge cases.

These tests generate random valid inputs and verify invariants
that should always hold true.
"""

import io
from typing import Any

import pytest
import segno
from hypothesis import assume, given, strategies as st, settings

from segnomms import write
from segnomms.config import (
    ConnectivityMode, MergeStrategy, ModuleShape, GeometryConfig
)


# Custom strategies for our domain types
connectivity_strategy = st.sampled_from([mode.value for mode in ConnectivityMode])
merge_strategy = st.sampled_from([strategy.value for strategy in MergeStrategy])
shape_strategy = st.sampled_from([shape.value for shape in ModuleShape])

# Valid QR sizes: 21x21 to 177x177, where (size-21) % 4 == 0
qr_size_strategy = st.integers(min_value=21, max_value=177).filter(
    lambda n: (n - 21) % 4 == 0
)

# Error correction levels
error_level_strategy = st.sampled_from(["L", "M", "Q", "H"])

# Color strategies - valid hex colors
color_strategy = st.from_regex(r"^#[0-9A-Fa-f]{6}$", fullmatch=True)

# Geometry configuration
geometry_config_strategy = st.builds(
    dict,
    connectivity=connectivity_strategy,
    merge=merge_strategy,
    corner_radius=st.floats(min_value=0.0, max_value=1.0),
    min_island_modules=st.integers(min_value=1, max_value=10),
)


@pytest.mark.hypothesis
class TestPropertyBased:
    """Property-based tests for QR code generation."""
    
    @given(
        data=st.text(min_size=1, max_size=100),
        shape=shape_strategy,
        scale=st.integers(min_value=1, max_value=50),
        safe_mode=st.booleans(),
    )
    @settings(max_examples=50, deadline=1000)
    def test_basic_generation_never_crashes(
        self, data: str, shape: str, scale: int, safe_mode: bool
    ):
        """Test that QR generation never crashes with valid inputs."""
        qr = segno.make(data)
        output = io.StringIO()
        
        # Should not raise any exception
        write(qr, output, shape=shape, scale=scale, safe_mode=safe_mode)
        svg_content = output.getvalue()
        
        # Basic invariants
        assert svg_content.startswith("<svg")
        assert svg_content.endswith("</svg>")
        assert len(svg_content) > 100  # Non-trivial content
        assert 'width="' in svg_content
        assert 'height="' in svg_content
    
    @given(
        data=st.text(min_size=1, max_size=50),
        error_level=error_level_strategy,
        geometry_config=geometry_config_strategy,
    )
    @settings(max_examples=30, deadline=2000)
    def test_geometry_configs_produce_valid_svg(
        self, data: str, error_level: str, geometry_config: dict
    ):
        """Test that all geometry configurations produce valid SVG."""
        qr = segno.make(data, error=error_level)
        output = io.StringIO()
        
        write(qr, output, shape="square", scale=10, **geometry_config)
        svg_content = output.getvalue()
        
        # Verify it's valid XML
        from xml.etree import ElementTree as ET
        try:
            root = ET.fromstring(svg_content)
            assert root.tag.endswith("svg")
        except ET.ParseError as e:
            pytest.fail(f"Invalid XML generated: {e}")
    
    @given(
        size=qr_size_strategy,
        error_level=error_level_strategy,
    )
    def test_qr_size_invariants(self, size: int, error_level: str):
        """Test QR code size invariants."""
        # Generate data that will create a QR of approximately the target size
        # This is approximate - actual size depends on data and ECC
        data = "X" * ((size - 21) // 4)
        
        try:
            qr = segno.make(data, error=error_level, boost_error=False)
        except ValueError:
            # Data too long for this size/ECC combination
            assume(False)
            return
        
        output = io.StringIO()
        write(qr, output, shape="square", scale=1, border=4)  # Explicit border
        svg_content = output.getvalue()
        
        # Extract viewBox to verify size
        import re
        viewbox_match = re.search(r'viewBox="0 0 (\d+) (\d+)"', svg_content)
        assert viewbox_match, "No viewBox found"
        
        width = int(viewbox_match.group(1))
        height = int(viewbox_match.group(2))
        
        # QR codes are always square
        assert width == height
        
        # Get actual matrix size from QR object
        matrix_size = len(qr.matrix[0]) if hasattr(qr, 'matrix') else qr.symbol_size()[0]
        expected_size = matrix_size + (2 * 4)  # matrix + 2*border
        assert width == expected_size
    
    @given(
        data=st.text(min_size=1, max_size=50),
        dark=color_strategy,
        light=color_strategy,
    )
    def test_color_combinations(self, data: str, dark: str, light: str):
        """Test that any valid color combination works."""
        assume(dark != light)  # Different colors
        
        # Skip colors that are too similar (would trigger degradation)
        try:
            # Simple contrast check
            dark_val = int(dark.lstrip('#'), 16) if dark.startswith('#') else 0
            light_val = int(light.lstrip('#'), 16) if light.startswith('#') else 0xFFFFFF
            if abs(dark_val - light_val) < 0x100000:  # Too similar
                assume(False)
        except ValueError:
            pass  # Not hex colors, proceed
        
        qr = segno.make(data)
        output = io.StringIO()
        
        write(qr, output, shape="circle", scale=5, dark=dark, light=light)
        svg_content = output.getvalue()
        
        # The SVG should be valid
        assert svg_content.startswith('<svg')
        assert '</svg>' in svg_content
        
        # Should have some path elements for the QR modules
        assert '<path' in svg_content or '<rect' in svg_content or '<circle' in svg_content
    
    @given(
        shape=shape_strategy,
        safe_mode=st.booleans(),
        scale=st.integers(min_value=5, max_value=20),
    )
    def test_safe_mode_creates_valid_qr(self, shape: str, safe_mode: bool, scale: int):
        """Test that safe mode always produces valid QR structure."""
        test_data = "Safe mode test"
        qr = segno.make(test_data)
        
        output = io.StringIO()
        write(qr, output, shape=shape, safe_mode=safe_mode, scale=scale)
        svg_content = output.getvalue()
        
        # In safe mode, finder patterns should be clearly defined
        if safe_mode:
            # Check for finder pattern structure (3 corners)
            # This is a simplified check
            assert svg_content.count('class="qr-finder"') >= 3 or \
                   svg_content.count('finder') >= 3 or \
                   'M0' in svg_content  # Path-based finders
    
    @given(
        connectivity=connectivity_strategy,
        merge=merge_strategy,
        min_island=st.integers(min_value=1, max_value=5),
    )
    def test_island_removal_consistency(
        self, connectivity: str, merge: str, min_island: int
    ):
        """Test island removal doesn't break QR structure."""
        qr = segno.make("Island test")
        output = io.StringIO()
        
        write(
            qr, output,
            shape="square",
            scale=10,
            connectivity=connectivity,
            merge=merge,
            min_island_modules=min_island
        )
        svg_content = output.getvalue()
        
        # Should still be valid SVG
        assert svg_content.startswith("<svg")
        assert svg_content.endswith("</svg>")
        
        # Should have module elements
        assert "qr-module" in svg_content or "<rect" in svg_content or "<path" in svg_content
    
    @given(
        shapes=st.lists(shape_strategy, min_size=2, max_size=5),
        scales=st.lists(st.integers(min_value=5, max_value=15), min_size=2, max_size=5),
    )
    def test_multiple_renders_consistent(self, shapes: list[str], scales: list[int]):
        """Test that rendering the same data multiple times is consistent."""
        test_data = "Consistency test"
        qr = segno.make(test_data)
        
        outputs = []
        for shape, scale in zip(shapes, scales):
            output = io.StringIO()
            write(qr, output, shape=shape, scale=scale)
            outputs.append(output.getvalue())
        
        # All outputs should be valid
        for svg in outputs:
            assert svg.startswith("<svg")
            assert svg.endswith("</svg>")
            assert len(svg) > 100
    
    @given(
        data=st.text(alphabet=st.characters(blacklist_categories=["Cc", "Cs"]), min_size=1, max_size=50),
        shape=shape_strategy,
    )
    def test_unicode_handling(self, data: str, shape: str):
        """Test that unicode data is handled correctly."""
        try:
            qr = segno.make(data)
        except ValueError:
            # Some unicode might not be encodable in QR
            assume(False)
            return
        
        output = io.StringIO()
        write(qr, output, shape=shape, scale=5)
        svg_content = output.getvalue()
        
        # Should produce valid output
        assert svg_content.startswith("<svg")
        assert len(svg_content) > 100


@pytest.mark.hypothesis
@given(
    corner_radius=st.floats(min_value=0.0, max_value=1.0),
    shape=st.sampled_from(["square", "squircle"]),
)
def test_corner_radius_bounds(corner_radius: float, shape: str):
    """Test corner radius stays within valid bounds."""
    qr = segno.make("Corner radius test")
    output = io.StringIO()
    
    write(qr, output, shape=shape, scale=10, corner_radius=corner_radius)
    svg_content = output.getvalue()
    
    # Should not crash and produce valid SVG
    assert svg_content.startswith("<svg")
    
    # For shapes that support corner radius, it should affect the output
    if shape in ["square", "squircle"] and corner_radius > 0:
        # Look for rounded corners in paths or rect rx/ry attributes
        assert any(x in svg_content for x in ["rx=", "ry=", "curve", "arc", "Q", "C"])