"""
Unit tests for segnomms.types module.

Tests type definitions, protocols, and type aliases to ensure
they work correctly with the type system and runtime usage.
"""

import pytest
from typing import Any, Dict, List, Optional, get_type_hints
from unittest.mock import Mock

from segnomms.types import (
    ConfigType,
    CenterpieceConfigType,
    MatrixType,
    CoordinateType,
    BoundingBoxType,
    SVGPathType,
    SVGAttributesType,
    PerformanceMetricsType,
    ValidationResultType,
    ConfigProtocol,
    CenterpieceConfigProtocol,
    OptionalConfigType,
    OptionalCenterpieceConfigType,
)

from tests.constants import (
    TEST_COLORS, ModuleShape, DEFAULT_SCALE
)


class TestTypeAliases:
    """Test type aliases are properly defined."""
    
    def test_matrix_type_structure(self):
        """Test MatrixType represents correct matrix structure."""
        # Valid matrix structures
        valid_matrices: List[MatrixType] = [
            [[1, 0, 1], [0, 1, 0], [1, 0, 1]],  # Simple matrix
            [[1, 1], [1, 1]],  # 2x2 matrix
            [[None, 1, None], [1, None, 1]],  # Matrix with None values
            [],  # Empty matrix
            [[]],  # Matrix with empty row
        ]
        
        # All should be valid MatrixType instances
        for matrix in valid_matrices:
            assert isinstance(matrix, list)
            for row in matrix:
                assert isinstance(row, list)
                for cell in row:
                    assert cell is None or isinstance(cell, int)
    
    def test_coordinate_type_structure(self):
        """Test CoordinateType represents correct coordinate structure."""
        # Valid coordinates
        valid_coords: List[CoordinateType] = [
            (0, 0),
            (10, 20),
            (-5, 15),
            (100, 100),
        ]
        
        for coord in valid_coords:
            assert isinstance(coord, tuple)
            assert len(coord) == 2
            assert all(isinstance(c, int) for c in coord)
    
    def test_bounding_box_type_structure(self):
        """Test BoundingBoxType represents correct bounding box structure."""
        # Valid bounding boxes (min_x, min_y, max_x, max_y)
        valid_boxes: List[BoundingBoxType] = [
            (0, 0, 10, 10),
            (5, 5, 15, 20),
            (-10, -10, 10, 10),
            (0, 0, 0, 0),  # Zero-size box
        ]
        
        for bbox in valid_boxes:
            assert isinstance(bbox, tuple)
            assert len(bbox) == 4
            assert all(isinstance(c, int) for c in bbox)
            # min_x <= max_x and min_y <= max_y should be true for valid boxes
            min_x, min_y, max_x, max_y = bbox
            assert min_x <= max_x
            assert min_y <= max_y
    
    def test_svg_attributes_type_structure(self):
        """Test SVGAttributesType represents correct attribute structure."""
        # Valid attribute dictionaries
        valid_attrs: List[SVGAttributesType] = [
            {"x": "10", "y": "20", "width": "100", "height": "100"},
            {"fill": TEST_COLORS["red"], "stroke": TEST_COLORS["black"], "stroke-width": 2},
            {"id": "test-element", "class": "qr-module"},
            {"viewBox": "0 0 100 100", "xmlns": "http://www.w3.org/2000/svg"},
            {},  # Empty attributes
        ]
        
        for attrs in valid_attrs:
            assert isinstance(attrs, dict)
            for key, value in attrs.items():
                assert isinstance(key, str)
                assert isinstance(value, (str, int, float))
    
    def test_performance_metrics_type_structure(self):
        """Test PerformanceMetricsType represents correct metrics structure."""
        # Valid performance metrics
        valid_metrics: List[PerformanceMetricsType] = [
            {
                "operation": "qr_generation",
                "duration": 0.123,
                "memory_usage": 1024,
                "warnings": ["Minor performance issue"]
            },
            {
                "total_time": 1.5,
                "render_time": 0.8,
                "validation_time": 0.2,
                "errors": []
            },
            {},  # Empty metrics
        ]
        
        for metrics in valid_metrics:
            assert isinstance(metrics, dict)
            for key, value in metrics.items():
                assert isinstance(key, str)
                assert isinstance(value, (str, float, int, list))
    
    def test_validation_result_type_structure(self):
        """Test ValidationResultType represents correct validation structure."""
        # Valid validation results
        valid_results: List[ValidationResultType] = [
            {
                "is_valid": True,
                "message": "Validation passed",
                "errors": []
            },
            {
                "scannable": False,
                "reason": "Insufficient contrast",
                "suggestions": ["Increase color contrast", "Simplify design"]
            },
            {
                "structure_valid": True,
                "accessibility_valid": False,
                "warnings": ["Missing alt text"]
            },
            {},  # Empty result
        ]
        
        for result in valid_results:
            assert isinstance(result, dict)
            for key, value in result.items():
                assert isinstance(key, str)
                assert isinstance(value, (bool, str, list))


class TestConfigProtocol:
    """Test ConfigProtocol protocol definition."""
    
    def test_config_protocol_compliance(self):
        """Test that objects can comply with ConfigProtocol."""
        # Create a mock object that implements the protocol
        mock_config = Mock(spec=ConfigProtocol)
        mock_config.model_dump.return_value = {"shape": "circle", "scale": 10}
        
        # Should be able to call protocol methods
        result = mock_config.model_dump()
        assert isinstance(result, dict)
        assert "shape" in result
        assert "scale" in result
    
    def test_config_protocol_with_real_objects(self):
        """Test ConfigProtocol with real configuration objects."""
        from segnomms.config import RenderingConfig
        
        config = RenderingConfig()
        
        # Should implement the protocol
        assert hasattr(config, 'model_dump')
        assert callable(getattr(config, 'model_dump'))
        
        # Should return a dictionary
        result = config.model_dump()
        assert isinstance(result, dict)


class TestCenterpieceConfigProtocol:
    """Test CenterpieceConfigProtocol protocol definition."""
    
    def test_centerpiece_protocol_compliance(self):
        """Test that objects can comply with CenterpieceConfigProtocol."""
        # Create a mock object that implements the protocol
        mock_centerpiece = Mock(spec=CenterpieceConfigProtocol)
        mock_centerpiece.enabled = True
        mock_centerpiece.size = 0.15
        mock_centerpiece.shape = "circle"
        mock_centerpiece.model_dump.return_value = {
            "enabled": True,
            "size": 0.15,
            "shape": "circle"
        }
        
        # Should have required attributes
        assert mock_centerpiece.enabled is True
        assert mock_centerpiece.size == 0.15
        assert mock_centerpiece.shape == "circle"
        
        # Should be able to call protocol methods
        result = mock_centerpiece.model_dump()
        assert isinstance(result, dict)
        assert result["enabled"] is True
    
    def test_centerpiece_protocol_with_real_objects(self):
        """Test CenterpieceConfigProtocol with real configuration objects."""
        from segnomms.config.models.visual import CenterpieceConfig
        
        centerpiece = CenterpieceConfig(enabled=True, size=0.2, shape="rect")
        
        # Should implement the protocol
        assert hasattr(centerpiece, 'enabled')
        assert hasattr(centerpiece, 'size')
        assert hasattr(centerpiece, 'shape')
        assert hasattr(centerpiece, 'model_dump')
        assert callable(getattr(centerpiece, 'model_dump'))
        
        # Should have correct values
        assert centerpiece.enabled is True
        assert centerpiece.size == 0.2
        assert centerpiece.shape == "rect"
        
        # Should return a dictionary
        result = centerpiece.model_dump()
        assert isinstance(result, dict)


class TestUnionTypes:
    """Test union type definitions."""
    
    def test_config_type_accepts_various_inputs(self):
        """Test ConfigType accepts different configuration formats."""
        from segnomms.config import RenderingConfig
        
        # Should accept RenderingConfig instance
        config_obj = RenderingConfig()
        config_type_value: ConfigType = config_obj
        assert config_type_value is not None
        
        # Should accept dictionary
        config_dict: ConfigType = {"shape": ModuleShape.CIRCLE.value, "scale": DEFAULT_SCALE}
        assert config_dict is not None
        
        # Should accept None
        config_none: ConfigType = None
        assert config_none is None
    
    def test_centerpiece_config_type_accepts_various_inputs(self):
        """Test CenterpieceConfigType accepts different configuration formats."""
        from segnomms.config.models.visual import CenterpieceConfig
        
        # Should accept CenterpieceConfig instance
        centerpiece_obj = CenterpieceConfig()
        centerpiece_type_value: CenterpieceConfigType = centerpiece_obj
        assert centerpiece_type_value is not None
        
        # Should accept dictionary
        centerpiece_dict: CenterpieceConfigType = {
            "enabled": True,
            "size": 0.15,
            "shape": "circle"
        }
        assert centerpiece_dict is not None
        
        # Should accept None
        centerpiece_none: CenterpieceConfigType = None
        assert centerpiece_none is None
    
    def test_optional_config_types(self):
        """Test optional configuration types."""
        from segnomms.config import RenderingConfig
        
        # OptionalConfigType should accept config, dict, or None
        optional_config: OptionalConfigType = RenderingConfig()
        assert optional_config is not None
        
        optional_config = {"shape": ModuleShape.SQUARE.value}
        assert optional_config is not None
        
        optional_config = None
        assert optional_config is None
        
        # OptionalCenterpieceConfigType should accept config, dict, or None
        from segnomms.config.models.visual import CenterpieceConfig
        
        optional_centerpiece: OptionalCenterpieceConfigType = CenterpieceConfig()
        assert optional_centerpiece is not None
        
        optional_centerpiece = {"enabled": False}
        assert optional_centerpiece is not None
        
        optional_centerpiece = None
        assert optional_centerpiece is None


class TestTypeHints:
    """Test that type hints work correctly."""
    
    def test_type_hints_importable(self):
        """Test that all type definitions can be imported and used."""
        # All these should be importable without errors
        from segnomms.types import (
            ConfigType,
            CenterpieceConfigType,
            MatrixType,
            CoordinateType,
            BoundingBoxType,
            SVGPathType,
            SVGAttributesType,
            PerformanceMetricsType,
            ValidationResultType,
        )
        
        # Should be usable in type annotations
        def test_function(
            config: ConfigType,
            matrix: MatrixType,
            coord: CoordinateType,
            bbox: BoundingBoxType,
            path: SVGPathType,
            attrs: SVGAttributesType,
            metrics: PerformanceMetricsType,
            result: ValidationResultType,
        ) -> bool:
            return True
        
        # Function should be callable
        assert callable(test_function)
    
    def test_type_checking_imports(self):
        """Test TYPE_CHECKING imports work correctly."""
        # These imports should work without circular import issues
        import segnomms.types
        
        # Module should load successfully
        assert hasattr(segnomms.types, 'ConfigType')
        assert hasattr(segnomms.types, 'CenterpieceConfigType')


class TestTypeValidation:
    """Test type validation and runtime behavior."""
    
    def test_coordinate_validation(self):
        """Test coordinate type validation."""
        # Valid coordinates
        valid_coords = [(0, 0), (10, 20), (-5, 15)]
        
        for coord in valid_coords:
            assert len(coord) == 2
            assert all(isinstance(c, int) for c in coord)
    
    def test_bounding_box_validation(self):
        """Test bounding box type validation."""
        # Valid bounding boxes
        valid_boxes = [(0, 0, 10, 10), (5, 5, 15, 20)]
        
        for bbox in valid_boxes:
            assert len(bbox) == 4
            assert all(isinstance(c, int) for c in bbox)
            min_x, min_y, max_x, max_y = bbox
            assert min_x <= max_x
            assert min_y <= max_y
    
    def test_matrix_validation(self):
        """Test matrix type validation."""
        # Valid matrices
        valid_matrices = [
            [[1, 0, 1], [0, 1, 0]],
            [[None, 1], [1, None]],
            []
        ]
        
        for matrix in valid_matrices:
            assert isinstance(matrix, list)
            for row in matrix:
                assert isinstance(row, list)
                for cell in row:
                    assert cell is None or isinstance(cell, int)


class TestProtocolUsage:
    """Test protocol usage in real scenarios."""
    
    def test_config_protocol_usage(self):
        """Test ConfigProtocol can be used for type checking."""
        def process_config(config: ConfigProtocol) -> Dict[str, Any]:
            """Function that expects a ConfigProtocol."""
            return config.model_dump()
        
        from segnomms.config import RenderingConfig
        config = RenderingConfig()
        
        # Should work with real config objects
        result = process_config(config)
        assert isinstance(result, dict)
    
    def test_centerpiece_protocol_usage(self):
        """Test CenterpieceConfigProtocol can be used for type checking."""
        def process_centerpiece(centerpiece: CenterpieceConfigProtocol) -> bool:
            """Function that expects a CenterpieceConfigProtocol."""
            return centerpiece.enabled
        
        from segnomms.config.models.visual import CenterpieceConfig
        centerpiece = CenterpieceConfig(enabled=True, size=0.15)
        
        # Should work with real centerpiece objects
        result = process_centerpiece(centerpiece)
        assert result is True