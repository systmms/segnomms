"""
Unified test case generator for consistent test data across all test types.

This module provides a single source of truth for all test cases used in
visual regression, structural tests, and review generation.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List

import segno


class Category(Enum):
    """Categories of test cases."""

    SHAPES = "shapes"
    COLORS = "colors"
    PHASES = "phases"
    FRAMES = "frames"
    CENTERPIECE = "centerpiece"
    ERROR_LEVELS = "error_levels"
    PAYLOADS = "payloads"
    EDGE_CASES = "edge_cases"
    INTEGRATION = "integration"


@dataclass
class Case:
    """Represents a single test case."""

    id: str
    category: Category
    description: str
    qr_data: str
    config: Dict[str, Any]
    tags: List[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []


class TestCaseGenerator:
    """Single source of truth for all test cases."""

    # QR payloads for different test scenarios
    QR_PAYLOADS = {
        "simple": "Hello World",
        "url": "https://example.com",
        "email": "test@example.com",
        "phone": "+1234567890",
        "complex_url": "https://github.com/example/project/issues/123?query=test&filter=open#section",
        "vcard": "BEGIN:VCARD\nVERSION:3.0\nFN:John Doe\nORG:Example Corp\nEND:VCARD",
        "wifi": "WIFI:T:WPA;S:MyNetwork;P:MyPassword;;",
        "small": "X",
        "medium": "A" * 100,
        "large": "B" * 500,
    }

    # Color combinations to test
    COLOR_COMBINATIONS = [
        ("Classic B&W", {"dark": "#000000", "light": "#FFFFFF"}),
        ("Brand Colors", {"dark": "#2c3e50", "light": "#ecf0f1"}),
        ("High Contrast", {"dark": "#FF0000", "light": "#FFFF00"}),
        ("Gray Scale", {"dark": "#333333", "light": "#EEEEEE"}),
        ("Dark Theme", {"dark": "#FFFFFF", "light": "#1a1a1a"}),
        ("Blue Theme", {"dark": "#0066CC", "light": "#E6F2FF"}),
    ]

    # Shape configurations
    SHAPE_CONFIGS = {
        "square": {"shape": "square", "corner_radius": 0.0},
        "circle": {"shape": "circle", "corner_radius": 1.0},
        "rounded": {"shape": "rounded", "corner_radius": 0.3},
        "diamond": {"shape": "diamond", "corner_radius": 0.0},
        "star": {"shape": "star"},
        "triangle": {"shape": "triangle"},
        "hexagon": {"shape": "hexagon"},
        "cross": {"shape": "cross"},
        "squircle": {"shape": "squircle", "corner_radius": 0.3},
        "dot": {"shape": "dot"},
        "connected": {"shape": "connected", "connectivity": "8-way", "merge": "soft"},
        "connected-classy": {"shape": "connected-classy"},
        "connected-classy-rounded": {"shape": "connected-classy-rounded"},
        "connected-extra-rounded": {"shape": "connected-extra-rounded"},
    }

    @classmethod
    def get_shape_test_cases(cls, include_safe_mode: bool = True) -> List[Case]:
        """
        Get all shape test cases.

        Args:
            include_safe_mode: Whether to include safe mode variations

        Returns:
            List of shape test cases
        """
        test_cases = []

        for shape_name, shape_config in cls.SHAPE_CONFIGS.items():
            # Determine if this shape supports safe mode
            supports_safe_mode = not shape_name.startswith("connected")

            if include_safe_mode and supports_safe_mode:
                # Test with safe mode on and off
                for safe_mode in [True, False]:
                    config = shape_config.copy()
                    config["safe_mode"] = safe_mode
                    config["scale"] = 10
                    config["border"] = 4

                    safe_str = "on" if safe_mode else "off"
                    test_case = Case(
                        id=f"{shape_name}_safe_{safe_str}",
                        category=Category.SHAPES,
                        description=f"{shape_name} shape with safe mode {safe_str}",
                        qr_data=cls.QR_PAYLOADS["simple"],
                        config=config,
                        tags=["shape", shape_name, f"safe_mode_{safe_str}"],
                    )
                    test_cases.append(test_case)
            else:
                # Single test without safe mode
                config = shape_config.copy()
                config["safe_mode"] = False
                config["scale"] = 10
                config["border"] = 4

                test_case = Case(
                    id=f"{shape_name}_safe_off",
                    category=Category.SHAPES,
                    description=f"{shape_name} shape",
                    qr_data=cls.QR_PAYLOADS["simple"],
                    config=config,
                    tags=["shape", shape_name],
                )
                test_cases.append(test_case)

        return test_cases

    @classmethod
    def get_color_test_cases(cls) -> List[Case]:
        """Get all color variation test cases."""
        test_cases = []

        for color_name, color_config in cls.COLOR_COMBINATIONS:
            config = {"shape": "rounded", "scale": 10, "border": 4, **color_config}

            test_case = Case(
                id=f"colors_{color_name.replace(' ', '_').replace('&', 'and')}",
                category=Category.COLORS,
                description=f"Color test: {color_name}",
                qr_data=cls.QR_PAYLOADS["simple"],
                config=config,
                tags=["color", color_name.lower().replace(" ", "_")],
            )
            test_cases.append(test_case)

        return test_cases

    @classmethod
    def get_error_level_test_cases(cls) -> List[Case]:
        """Get error correction level test cases."""
        test_cases = []

        for error_level in ["L", "M", "Q", "H"]:
            config = {
                "shape": "square",
                "scale": 10,
                "border": 4,
            }

            test_case = Case(
                id=f"error_level_{error_level}",
                category=Category.ERROR_LEVELS,
                description=f"Error correction level {error_level}",
                qr_data=cls.QR_PAYLOADS["simple"],
                config=config,
                tags=["error_level", error_level],
            )
            test_cases.append(test_case)

        return test_cases

    @classmethod
    def get_payload_test_cases(cls) -> List[Case]:
        """Get different payload type test cases."""
        test_cases = []

        payload_configs = {
            "simple": "Simple text",
            "url": "URL",
            "email": "Email address",
            "phone": "Phone number",
            "complex_url": "Complex URL with parameters",
        }

        for payload_key, description in payload_configs.items():
            config = {
                "shape": "rounded",
                "scale": 10,
                "border": 4,
            }

            test_case = Case(
                id=f"payload_{payload_key}",
                category=Category.PAYLOADS,
                description=f"Payload type: {description}",
                qr_data=cls.QR_PAYLOADS[payload_key],
                config=config,
                tags=["payload", payload_key],
            )
            test_cases.append(test_case)

        return test_cases

    @classmethod
    def get_frame_test_cases(cls) -> List[Case]:
        """Get frame effect test cases."""
        test_cases = []

        frame_configs = [
            ("square_clip", {"frame_shape": "square", "frame_clip_mode": "clip"}),
            ("circle_fade", {"frame_shape": "circle", "frame_clip_mode": "fade"}),
            ("rounded_scale", {"frame_shape": "rounded-rect", "frame_clip_mode": "scale"}),
        ]

        for frame_name, frame_config in frame_configs:
            config = {"shape": "square", "scale": 10, "border": 4, **frame_config}

            test_case = Case(
                id=f"frame_{frame_name}",
                category=Category.FRAMES,
                description=f"Frame effect: {frame_name}",
                qr_data=cls.QR_PAYLOADS["simple"],
                config=config,
                tags=["frame", frame_name],
            )
            test_cases.append(test_case)

        return test_cases

    @classmethod
    def get_complex_test_cases(cls) -> List[Case]:
        """Get complex integration test cases."""
        test_cases = []

        # Complex configuration with multiple features
        complex_config = {
            "scale": 15,
            "border": 3,
            "shape": "squircle",
            "corner_radius": 0.3,
            "dark": "#1a1a2e",
            "light": "#f5f5f5",
            "connectivity": "8-way",
            "merge": "soft",
            "safe_mode": False,
            "finder_shape": "rounded",
            "finder_inner_scale": 0.4,
            "frame_shape": "circle",
            "frame_clip_mode": "fade",
            "centerpiece_enabled": True,
            "centerpiece_size": 0.15,
            "centerpiece_shape": "circle",
            "interactive": True,
        }

        test_case = Case(
            id="complex_full_config",
            category=Category.INTEGRATION,
            description="Complex configuration with all features",
            qr_data=cls.QR_PAYLOADS["complex_url"],
            config=complex_config,
            tags=["complex", "integration", "all_features"],
        )
        test_cases.append(test_case)

        return test_cases

    @classmethod
    def get_edge_case_test_cases(cls) -> List[Case]:
        """Get edge case test cases."""
        test_cases = []

        # Very small QR code
        test_cases.append(
            Case(
                id="edge_case_small",
                category=Category.EDGE_CASES,
                description="Very small QR code",
                qr_data=cls.QR_PAYLOADS["small"],
                config={"shape": "square", "scale": 10, "border": 4},
                tags=["edge_case", "small"],
            )
        )

        # Large data
        test_cases.append(
            Case(
                id="edge_case_large_data",
                category=Category.EDGE_CASES,
                description="QR code with large data",
                qr_data=cls.QR_PAYLOADS["large"],
                config={"shape": "rounded", "scale": 5, "border": 2},
                tags=["edge_case", "large_data"],
            )
        )

        # Complex content (vCard)
        test_cases.append(
            Case(
                id="edge_case_vcard",
                category=Category.EDGE_CASES,
                description="vCard data",
                qr_data=cls.QR_PAYLOADS["vcard"],
                config={"shape": "square", "scale": 10, "border": 4},
                tags=["edge_case", "vcard"],
            )
        )

        return test_cases

    @classmethod
    def get_all_test_cases(cls) -> List[Case]:
        """Get all test cases across all categories."""
        all_cases = []

        all_cases.extend(cls.get_shape_test_cases())
        all_cases.extend(cls.get_color_test_cases())
        all_cases.extend(cls.get_error_level_test_cases())
        all_cases.extend(cls.get_payload_test_cases())
        all_cases.extend(cls.get_frame_test_cases())
        all_cases.extend(cls.get_complex_test_cases())
        all_cases.extend(cls.get_edge_case_test_cases())

        return all_cases

    @classmethod
    def get_test_cases_by_category(cls, category: Category) -> List[Case]:
        """Get test cases for a specific category."""
        category_methods = {
            Category.SHAPES: cls.get_shape_test_cases,
            Category.COLORS: cls.get_color_test_cases,
            Category.ERROR_LEVELS: cls.get_error_level_test_cases,
            Category.PAYLOADS: cls.get_payload_test_cases,
            Category.FRAMES: cls.get_frame_test_cases,
            Category.INTEGRATION: cls.get_complex_test_cases,
            Category.EDGE_CASES: cls.get_edge_case_test_cases,
        }

        method = category_methods.get(category)
        if method:
            return method()

        return []

    @classmethod
    def get_test_cases_by_tags(cls, tags: List[str]) -> List[Case]:
        """Get test cases matching any of the specified tags."""
        all_cases = cls.get_all_test_cases()

        matching_cases = []
        for test_case in all_cases:
            if any(tag in test_case.tags for tag in tags):
                matching_cases.append(test_case)

        return matching_cases

    @classmethod
    def generate_qr(cls, test_case: Case, error_level: str = "M") -> segno.QRCode:
        """
        Generate QR code for a test case.

        Args:
            test_case: Test case to generate QR for
            error_level: Error correction level (L, M, Q, H)

        Returns:
            Segno QR code object
        """
        # Check if test case specifies error level
        if test_case.id.startswith("error_level_"):
            error_level = test_case.id.split("_")[-1]

        return segno.make(test_case.qr_data, error=error_level)

    @classmethod
    def get_quick_test_suite(cls) -> List[Case]:
        """Get a quick subset of test cases for rapid testing."""
        quick_cases = []

        # One shape from each major category
        quick_shapes = ["square", "circle", "rounded", "connected", "squircle"]
        for shape in quick_shapes:
            config = cls.SHAPE_CONFIGS.get(shape, {}).copy()
            config.update({"scale": 10, "border": 4})

            quick_cases.append(
                Case(
                    id=f"quick_{shape}",
                    category=Category.SHAPES,
                    description=f"Quick test: {shape}",
                    qr_data=cls.QR_PAYLOADS["simple"],
                    config=config,
                    tags=["quick", shape],
                )
            )

        # One color test
        quick_cases.append(
            Case(
                id="quick_colors",
                category=Category.COLORS,
                description="Quick color test",
                qr_data=cls.QR_PAYLOADS["simple"],
                config={"shape": "square", "scale": 10, "dark": "#2c3e50", "light": "#ecf0f1"},
                tags=["quick", "color"],
            )
        )

        return quick_cases
