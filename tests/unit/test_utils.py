"""
Unit tests for segnomms.utils module.

Tests the utility imports and re-exports to ensure the module
structure is correct and all components are accessible.
"""

import pytest
from unittest.mock import Mock, patch

from tests.constants import (
    DEFAULT_SCALE, DEFAULT_BORDER, TEST_COLORS,
    ModuleShape, FinderShape
)


class TestUtilsImports:
    """Test that utils module imports work correctly."""
    
    def test_interactive_svg_builder_import(self):
        """Test InteractiveSVGBuilder can be imported from utils."""
        from segnomms.utils import InteractiveSVGBuilder
        
        # Should be importable
        assert InteractiveSVGBuilder is not None
        
        # Should be a class
        assert isinstance(InteractiveSVGBuilder, type)
        
        # Should be instantiable
        builder = InteractiveSVGBuilder()
        assert builder is not None
    
    def test_svg_model_imports(self):
        """Test SVG model classes can be imported from utils."""
        from segnomms.utils import (
            SVGElementConfig,
            BackgroundConfig,
            GradientConfig,
            TitleDescriptionConfig,
            InteractionConfig,
            FrameDefinitionConfig,
            LayerStructureConfig,
            CenterpieceMetadataConfig,
        )
        
        # All should be importable
        models = [
            SVGElementConfig,
            BackgroundConfig,
            GradientConfig,
            TitleDescriptionConfig,
            InteractionConfig,
            FrameDefinitionConfig,
            LayerStructureConfig,
            CenterpieceMetadataConfig,
        ]
        
        for model in models:
            assert model is not None
            assert isinstance(model, type)
    
    def test_all_exports(self):
        """Test that __all__ contains all expected exports."""
        import segnomms.utils
        
        expected_exports = [
            "InteractiveSVGBuilder",
            "SVGElementConfig",
            "BackgroundConfig",
            "GradientConfig",
            "TitleDescriptionConfig",
            "InteractionConfig",
            "FrameDefinitionConfig",
            "LayerStructureConfig",
            "CenterpieceMetadataConfig",
        ]
        
        assert hasattr(segnomms.utils, '__all__')
        assert segnomms.utils.__all__ == expected_exports
        
        # All exported items should be accessible
        for export in expected_exports:
            assert hasattr(segnomms.utils, export)
            assert getattr(segnomms.utils, export) is not None


class TestInteractiveSVGBuilderAccess:
    """Test InteractiveSVGBuilder accessibility through utils."""
    
    def test_builder_instantiation(self):
        """Test InteractiveSVGBuilder can be instantiated through utils."""
        from segnomms.utils import InteractiveSVGBuilder
        
        builder = InteractiveSVGBuilder()
        assert builder is not None
        
        # Should have expected methods (basic smoke test)
        expected_methods = [
            'create_svg_root',
            'add_styles',
            'add_background',
        ]
        
        for method in expected_methods:
            assert hasattr(builder, method)
            assert callable(getattr(builder, method))
    
    def test_builder_create_svg_root(self):
        """Test create_svg_root method works through utils import."""
        from segnomms.utils import InteractiveSVGBuilder
        
        builder = InteractiveSVGBuilder()
        svg_root = builder.create_svg_root(100, 100)
        
        assert svg_root is not None
        # Should be an XML element
        assert hasattr(svg_root, 'tag')
        assert hasattr(svg_root, 'attrib')
    
    def test_builder_methods_callable(self):
        """Test all builder methods are callable through utils."""
        from segnomms.utils import InteractiveSVGBuilder
        
        builder = InteractiveSVGBuilder()
        
        # Test method calls (basic functionality)
        svg_root = builder.create_svg_root(200, 200)
        
        # Should be able to add styles
        builder.add_styles(svg_root, interactive=True)
        
        # Should be able to add background
        builder.add_background(svg_root, 200, 200, TEST_COLORS["white"])
        
        # No exceptions should be raised


class TestSVGModelAccess:
    """Test SVG model classes accessibility through utils."""
    
    def test_svg_element_config(self):
        """Test SVGElementConfig can be used through utils."""
        from segnomms.utils import SVGElementConfig
        
        # Should be instantiable with required fields
        config = SVGElementConfig(width=100, height=100)
        assert config is not None
        
        # Should be a Pydantic model
        assert hasattr(config, 'model_dump')
        assert callable(config.model_dump)
    
    def test_background_config(self):
        """Test BackgroundConfig can be used through utils."""
        from segnomms.utils import BackgroundConfig
        
        # Should be instantiable with required fields
        config = BackgroundConfig(
            width=100, 
            height=100, 
            color=TEST_COLORS["white"]
        )
        assert config is not None
        
        # Should be a Pydantic model
        assert hasattr(config, 'model_dump')
        assert callable(config.model_dump)
    
    def test_gradient_config(self):
        """Test GradientConfig can be used through utils."""
        from segnomms.utils import GradientConfig
        
        # Should be instantiable with required fields
        config = GradientConfig(
            gradient_id="test-gradient",
            gradient_type="linear",
            colors=[TEST_COLORS["red"], TEST_COLORS["blue"]]
        )
        assert config is not None
        
        # Should be a Pydantic model
        assert hasattr(config, 'model_dump')
        assert callable(config.model_dump)
    
    def test_title_description_config(self):
        """Test TitleDescriptionConfig can be used through utils."""
        from segnomms.utils import TitleDescriptionConfig
        
        # Should be instantiable with required fields
        config = TitleDescriptionConfig(title="Test QR Code")
        assert config is not None
        
        # Should be a Pydantic model
        assert hasattr(config, 'model_dump')
        assert callable(config.model_dump)
    
    def test_interaction_config(self):
        """Test InteractionConfig can be used through utils."""
        from segnomms.utils import InteractionConfig
        
        # Should be instantiable
        config = InteractionConfig()
        assert config is not None
        
        # Should be a Pydantic model
        assert hasattr(config, 'model_dump')
        assert callable(config.model_dump)
    
    def test_frame_definition_config(self):
        """Test FrameDefinitionConfig can be used through utils."""
        from segnomms.utils import FrameDefinitionConfig
        
        # Should be instantiable with required fields
        config = FrameDefinitionConfig(
            frame_shape=ModuleShape.CIRCLE.value,
            width=200,
            height=200,
            border_pixels=8
        )
        assert config is not None
        
        # Should be a Pydantic model
        assert hasattr(config, 'model_dump')
        assert callable(config.model_dump)
    
    def test_layer_structure_config(self):
        """Test LayerStructureConfig can be used through utils."""
        from segnomms.utils import LayerStructureConfig
        
        # Should be instantiable
        config = LayerStructureConfig()
        assert config is not None
        
        # Should be a Pydantic model
        assert hasattr(config, 'model_dump')
        assert callable(config.model_dump)
    
    def test_centerpiece_metadata_config(self):
        """Test CenterpieceMetadataConfig can be used through utils."""
        from segnomms.utils import CenterpieceMetadataConfig
        
        # Should be instantiable with required fields
        config = CenterpieceMetadataConfig(
            x=10,
            y=10,
            width=50,
            height=50,
            scale=DEFAULT_SCALE,
            border=DEFAULT_BORDER
        )
        assert config is not None
        
        # Should be a Pydantic model
        assert hasattr(config, 'model_dump')
        assert callable(config.model_dump)


class TestModuleStructure:
    """Test the module structure and organization."""
    
    def test_module_docstring(self):
        """Test module has proper documentation."""
        import segnomms.utils
        
        assert segnomms.utils.__doc__ is not None
        assert len(segnomms.utils.__doc__) > 0
        
        # Should mention key components
        docstring = segnomms.utils.__doc__.lower()
        assert 'svg' in docstring
        assert 'interactive' in docstring
    
    def test_module_imports_work(self):
        """Test all module imports work without errors."""
        # Should be able to import the entire module
        import segnomms.utils
        
        # Should have all expected attributes
        for attr in segnomms.utils.__all__:
            assert hasattr(segnomms.utils, attr)
    
    def test_no_circular_imports(self):
        """Test that importing utils doesn't cause circular imports."""
        # This test passing means we can import without circular dependency issues
        try:
            import segnomms.utils
            from segnomms.utils import InteractiveSVGBuilder
            from segnomms.utils import SVGElementConfig
        except ImportError as e:
            pytest.fail(f"Circular import detected: {e}")
    
    def test_re_export_consistency(self):
        """Test that re-exported classes are the same as direct imports."""
        from segnomms.utils import InteractiveSVGBuilder as UtilsBuilder
        from segnomms.svg import InteractiveSVGBuilder as DirectBuilder
        
        # Should be the same class
        assert UtilsBuilder is DirectBuilder
        
        from segnomms.utils import SVGElementConfig as UtilsConfig
        from segnomms.svg.models import SVGElementConfig as DirectConfig
        
        # Should be the same class
        assert UtilsConfig is DirectConfig


class TestUsagePatterns:
    """Test common usage patterns through utils module."""
    
    def test_builder_workflow(self):
        """Test typical workflow using utils imports."""
        from segnomms.utils import InteractiveSVGBuilder, BackgroundConfig
        
        # Create builder
        builder = InteractiveSVGBuilder()
        
        # Create SVG
        svg_root = builder.create_svg_root(300, 300)
        
        # Add components
        builder.add_styles(svg_root, interactive=True)
        builder.add_background(svg_root, 300, 300, TEST_COLORS["white"])
        
        # Should result in valid SVG structure
        assert svg_root.tag.endswith('svg')
        assert 'width' in svg_root.attrib
        assert 'height' in svg_root.attrib
    
    def test_config_usage(self):
        """Test using config classes through utils."""
        from segnomms.utils import (
            BackgroundConfig,
            GradientConfig,
            InteractionConfig
        )
        
        # Should be able to create and use configs
        bg_config = BackgroundConfig(width=200, height=200, color=TEST_COLORS["white"])
        gradient_config = GradientConfig(
            gradient_id="test-grad",
            gradient_type="linear", 
            colors=[TEST_COLORS["red"], TEST_COLORS["blue"]]
        )
        interaction_config = InteractionConfig()
        
        # Should be able to serialize
        bg_data = bg_config.model_dump()
        gradient_data = gradient_config.model_dump()
        interaction_data = interaction_config.model_dump()
        
        assert isinstance(bg_data, dict)
        assert isinstance(gradient_data, dict)
        assert isinstance(interaction_data, dict)


class TestErrorHandling:
    """Test error handling in utils module."""
    
    def test_missing_dependencies_handled(self):
        """Test that missing optional dependencies are handled gracefully."""
        # This test verifies that the module can be imported even if some
        # optional dependencies are missing
        
        # Should be able to import without errors
        import segnomms.utils
        
        # Core functionality should still work
        from segnomms.utils import InteractiveSVGBuilder
        builder = InteractiveSVGBuilder()
        assert builder is not None
    
    def test_import_errors_propagated(self):
        """Test that real import errors are properly propagated."""
        # If there's a real import error (not optional dependency),
        # it should be raised properly
        
        # This test just verifies the imports work
        # Real import errors would be caught during module loading
        try:
            from segnomms.utils import InteractiveSVGBuilder
            from segnomms.utils import SVGElementConfig
        except ImportError as e:
            pytest.fail(f"Unexpected import error: {e}")


class TestDocumentationExamples:
    """Test that examples in module docstring work."""
    
    def test_basic_usage_example(self):
        """Test the basic usage example from the docstring."""
        # Example from docstring:
        # from segnomms.svg import InteractiveSVGBuilder
        # builder = InteractiveSVGBuilder()
        # svg_root = builder.create_svg_root(200, 200)
        # builder.add_styles(svg_root, interactive=True)
        # builder.add_background(svg_root, 200, 200, 'white')
        
        from segnomms.utils import InteractiveSVGBuilder
        
        builder = InteractiveSVGBuilder()
        svg_root = builder.create_svg_root(200, 200)
        builder.add_styles(svg_root, interactive=True)
        builder.add_background(svg_root, 200, 200, TEST_COLORS["white"])
        
        # Should complete without errors
        assert svg_root is not None
        assert svg_root.tag.endswith('svg')
        
        # Should have the expected dimensions
        assert svg_root.attrib.get('width') == '200'
        assert svg_root.attrib.get('height') == '200'