"""
Custom assertions for SVG and QR validation.

This module provides specialized assertion functions for testing QR code generation,
SVG structure validation, and accessibility compliance. These assertions provide
more meaningful error messages and encapsulate common validation patterns.
"""

import re
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Tuple, Union, Any
from pathlib import Path


class SVGValidationError(AssertionError):
    """Raised when SVG validation fails."""
    pass


class QRValidationError(AssertionError):
    """Raised when QR code validation fails."""
    pass


class AccessibilityValidationError(AssertionError):
    """Raised when accessibility validation fails."""
    pass


def assert_svg_structure(svg_content: str, 
                        expected_width: Optional[int] = None,
                        expected_height: Optional[int] = None,
                        expected_viewbox: Optional[str] = None,
                        require_namespace: bool = True) -> ET.Element:
    """
    Assert that SVG has valid basic structure.
    
    Args:
        svg_content: SVG content as string
        expected_width: Expected width attribute value
        expected_height: Expected height attribute value
        expected_viewbox: Expected viewBox attribute value
        require_namespace: Whether to require SVG namespace
        
    Returns:
        Parsed SVG root element
        
    Raises:
        SVGValidationError: If SVG structure is invalid
    """
    if not svg_content.strip():
        raise SVGValidationError("SVG content is empty")
        
    if not svg_content.strip().startswith('<svg'):
        raise SVGValidationError("SVG content does not start with <svg> element")
        
    try:
        root = ET.fromstring(svg_content)
    except ET.ParseError as e:
        raise SVGValidationError(f"SVG content is not valid XML: {e}")
        
    # Check root element
    if not root.tag.endswith('svg'):
        raise SVGValidationError(f"Root element is {root.tag}, expected 'svg'")
        
    # Check namespace if required
    if require_namespace:
        if root.tag not in ['{http://www.w3.org/2000/svg}svg', 'svg']:
            raise SVGValidationError(f"SVG namespace missing or incorrect. Tag: {root.tag}")
            
    # Check required attributes
    if root.get('width') is None:
        raise SVGValidationError("SVG missing required 'width' attribute")
        
    if root.get('height') is None:
        raise SVGValidationError("SVG missing required 'height' attribute")
        
    if root.get('viewBox') is None:
        raise SVGValidationError("SVG missing required 'viewBox' attribute")
        
    # Check expected values
    if expected_width is not None:
        actual_width = root.get('width')
        if actual_width != str(expected_width):
            raise SVGValidationError(f"Expected width {expected_width}, got {actual_width}")
            
    if expected_height is not None:
        actual_height = root.get('height')
        if actual_height != str(expected_height):
            raise SVGValidationError(f"Expected height {expected_height}, got {actual_height}")
            
    if expected_viewbox is not None:
        actual_viewbox = root.get('viewBox')
        if actual_viewbox != expected_viewbox:
            raise SVGValidationError(f"Expected viewBox '{expected_viewbox}', got '{actual_viewbox}'")
            
    return root


def assert_svg_elements_present(root: ET.Element, 
                               required_elements: List[str],
                               forbidden_elements: Optional[List[str]] = None) -> None:
    """
    Assert that required SVG elements are present and forbidden ones are absent.
    
    Args:
        root: SVG root element
        required_elements: List of element names that must be present
        forbidden_elements: List of element names that must not be present
        
    Raises:
        SVGValidationError: If element requirements are not met
    """
    # Find all elements in the SVG
    all_elements = {elem.tag.split('}')[-1] for elem in root.iter()}
    
    # Check required elements
    for element in required_elements:
        if element not in all_elements:
            raise SVGValidationError(f"Required SVG element '{element}' not found. "
                                   f"Available elements: {sorted(all_elements)}")
                                   
    # Check forbidden elements
    if forbidden_elements:
        for element in forbidden_elements:
            if element in all_elements:
                raise SVGValidationError(f"Forbidden SVG element '{element}' found")


def assert_svg_attributes(root: ET.Element,
                         required_attributes: Dict[str, Any],
                         xpath: str = ".") -> None:
    """
    Assert that elements have required attributes with correct values.
    
    Args:
        root: SVG root element
        required_attributes: Dict of attribute_name -> expected_value
        xpath: XPath to select elements to check (default: root element)
        
    Raises:
        SVGValidationError: If attribute requirements are not met
    """
    elements = root.findall(xpath)
    if not elements:
        raise SVGValidationError(f"No elements found matching XPath: {xpath}")
        
    for element in elements:
        for attr_name, expected_value in required_attributes.items():
            actual_value = element.get(attr_name)
            
            if actual_value is None:
                raise SVGValidationError(f"Element {element.tag} missing required "
                                       f"attribute '{attr_name}'")
                                       
            if expected_value is not None and actual_value != str(expected_value):
                raise SVGValidationError(f"Element {element.tag} attribute '{attr_name}' "
                                       f"expected '{expected_value}', got '{actual_value}'")


def assert_svg_css_classes(root: ET.Element,
                          required_classes: List[str],
                          element_xpath: str = ".") -> None:
    """
    Assert that elements have required CSS classes.
    
    Args:
        root: SVG root element
        required_classes: List of CSS class names that must be present
        element_xpath: XPath to select elements to check
        
    Raises:
        SVGValidationError: If CSS class requirements are not met
    """
    elements = root.findall(element_xpath)
    if not elements:
        raise SVGValidationError(f"No elements found matching XPath: {element_xpath}")
        
    for element in elements:
        class_attr = element.get('class', '')
        actual_classes = set(class_attr.split())
        
        for required_class in required_classes:
            if required_class not in actual_classes:
                raise SVGValidationError(f"Element {element.tag} missing required "
                                       f"CSS class '{required_class}'. "
                                       f"Current classes: {actual_classes}")


def assert_svg_color_format(color: str) -> None:
    """
    Assert that a color value is in valid format.
    
    Args:
        color: Color value to validate
        
    Raises:
        SVGValidationError: If color format is invalid
    """
    if not color:
        raise SVGValidationError("Color value is empty")
        
    # Check hex format
    hex_pattern = r'^#[0-9A-Fa-f]{6}$'
    if re.match(hex_pattern, color):
        return
        
    # Check RGB format
    rgb_pattern = r'^rgb\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*\)$'
    if re.match(rgb_pattern, color):
        return
        
    # Check named colors (basic list)
    named_colors = {
        'red', 'green', 'blue', 'black', 'white', 'yellow', 'orange', 
        'purple', 'pink', 'brown', 'gray', 'grey', 'cyan', 'magenta'
    }
    if color.lower() in named_colors:
        return
        
    raise SVGValidationError(f"Invalid color format: '{color}'. "
                           f"Expected hex (#RRGGBB), rgb(r,g,b), or named color")


def assert_qr_scannable(qr_matrix: List[List[bool]], 
                       min_version: int = 1,
                       max_version: int = 40) -> None:
    """
    Assert that QR code matrix has valid scannable structure.
    
    Args:
        qr_matrix: 2D boolean matrix representing QR code
        min_version: Minimum acceptable QR version
        max_version: Maximum acceptable QR version
        
    Raises:
        QRValidationError: If QR structure is invalid
    """
    if not qr_matrix or not qr_matrix[0]:
        raise QRValidationError("QR matrix is empty")
        
    size = len(qr_matrix)
    
    # Check that matrix is square
    if not all(len(row) == size for row in qr_matrix):
        raise QRValidationError("QR matrix is not square")
        
    # Check size corresponds to valid QR version
    # QR version formula: size = 4*version + 17
    if (size - 17) % 4 != 0:
        raise QRValidationError(f"Invalid QR matrix size {size}x{size}. "
                              f"Size must be 4*version + 17")
                              
    version = (size - 17) // 4
    if version < min_version or version > max_version:
        raise QRValidationError(f"QR version {version} outside acceptable range "
                              f"[{min_version}, {max_version}]")
                              
    # Check finder patterns (3 corners)
    finder_positions = [(0, 0), (0, size-7), (size-7, 0)]
    
    for row, col in finder_positions:
        # Check 7x7 finder pattern structure
        if not _check_finder_pattern(qr_matrix, row, col):
            raise QRValidationError(f"Invalid finder pattern at position ({row}, {col})")


def assert_qr_timing_patterns(qr_matrix: List[List[bool]]) -> None:
    """
    Assert that QR code has valid timing patterns.
    
    Args:
        qr_matrix: 2D boolean matrix representing QR code
        
    Raises:
        QRValidationError: If timing patterns are invalid
    """
    size = len(qr_matrix)
    
    # Check horizontal timing pattern (row 6)
    timing_row = 6
    expected_pattern = True
    for col in range(8, size - 8):
        if qr_matrix[timing_row][col] != expected_pattern:
            raise QRValidationError(f"Invalid horizontal timing pattern at ({timing_row}, {col}). "
                                  f"Expected {expected_pattern}, got {qr_matrix[timing_row][col]}")
        expected_pattern = not expected_pattern
        
    # Check vertical timing pattern (col 6)
    timing_col = 6
    expected_pattern = True
    for row in range(8, size - 8):
        if qr_matrix[row][timing_col] != expected_pattern:
            raise QRValidationError(f"Invalid vertical timing pattern at ({row}, {timing_col}). "
                                  f"Expected {expected_pattern}, got {qr_matrix[row][timing_col]}")
        expected_pattern = not expected_pattern


def assert_accessibility_compliance(root: ET.Element,
                                   level: str = "A",
                                   require_aria: bool = True,
                                   require_ids: bool = True) -> None:
    """
    Assert that SVG meets accessibility compliance requirements.
    
    Args:
        root: SVG root element
        level: WCAG compliance level ("A", "AA", or "AAA")
        require_aria: Whether to require ARIA attributes
        require_ids: Whether to require element IDs
        
    Raises:
        AccessibilityValidationError: If accessibility requirements are not met
    """
    issues = []
    
    # Check for title element
    title_elem = root.find('.//title')
    if title_elem is None:
        issues.append("Missing <title> element for basic accessibility")
        
    # Check root element accessibility
    if require_aria:
        if root.get('role') is None:
            issues.append("Root element missing 'role' attribute")
            
        if root.get('aria-label') is None and title_elem is None:
            issues.append("Root element missing 'aria-label' or <title> element")
            
    # Check for meaningful IDs if required
    if require_ids:
        elements_with_ids = root.findall('.//*[@id]')
        total_elements = len(list(root.iter()))
        
        if len(elements_with_ids) / total_elements < 0.5:
            issues.append(f"Only {len(elements_with_ids)}/{total_elements} elements have IDs. "
                         f"Consider adding more IDs for better accessibility")
                         
    # Level-specific checks
    if level in ["AA", "AAA"]:
        # Check for description element for AA/AAA compliance
        desc_elem = root.find('.//desc')
        if desc_elem is None:
            issues.append("Missing <desc> element required for AA/AAA compliance")
            
    if level == "AAA":
        # Stricter requirements for AAA
        if root.get('aria-describedby') is None and root.find('.//desc') is None:
            issues.append("AAA compliance requires aria-describedby or description element")
            
    if issues:
        raise AccessibilityValidationError(f"Accessibility compliance issues for level {level}:\n" + 
                                         "\n".join(f"  - {issue}" for issue in issues))


def assert_svg_performance(svg_content: str,
                          max_elements: Optional[int] = None,
                          max_size_kb: Optional[float] = None,
                          warn_complex_paths: bool = True) -> Dict[str, Any]:
    """
    Assert that SVG meets performance requirements and return metrics.
    
    Args:
        svg_content: SVG content as string
        max_elements: Maximum allowed number of elements
        max_size_kb: Maximum allowed size in kilobytes
        warn_complex_paths: Whether to warn about complex path elements
        
    Returns:
        Dict with performance metrics
        
    Raises:
        SVGValidationError: If performance requirements are not met
    """
    root = ET.fromstring(svg_content)
    
    # Count elements
    element_count = len(list(root.iter()))
    
    # Calculate size
    size_bytes = len(svg_content.encode('utf-8'))
    size_kb = size_bytes / 1024
    
    # Count complex elements
    complex_elements = {
        'path': len(root.findall('.//path')),
        'circle': len(root.findall('.//circle')),
        'rect': len(root.findall('.//rect')),
        'polygon': len(root.findall('.//polygon')),
        'style': len(root.findall('.//style')),
        'defs': len(root.findall('.//defs'))
    }
    
    metrics = {
        'element_count': element_count,
        'size_bytes': size_bytes,
        'size_kb': size_kb,
        'complex_elements': complex_elements
    }
    
    # Check limits
    issues = []
    
    if max_elements is not None and element_count > max_elements:
        issues.append(f"Too many elements: {element_count} > {max_elements}")
        
    if max_size_kb is not None and size_kb > max_size_kb:
        issues.append(f"SVG too large: {size_kb:.1f}KB > {max_size_kb}KB")
        
    if warn_complex_paths and complex_elements['path'] > element_count * 0.7:
        issues.append(f"High path element ratio: {complex_elements['path']}/{element_count} "
                     f"may impact performance")
                     
    if issues:
        raise SVGValidationError(f"Performance issues:\n" + 
                               "\n".join(f"  - {issue}" for issue in issues))
                               
    return metrics


def _check_finder_pattern(matrix: List[List[bool]], start_row: int, start_col: int) -> bool:
    """
    Check if a 7x7 finder pattern is valid at the given position.
    
    Args:
        matrix: QR code matrix
        start_row: Starting row of finder pattern
        start_col: Starting column of finder pattern
        
    Returns:
        True if finder pattern is valid
    """
    # Expected 7x7 finder pattern (True = dark, False = light)
    expected = [
        [True,  True,  True,  True,  True,  True,  True ],
        [True,  False, False, False, False, False, True ],
        [True,  False, True,  True,  True,  False, True ],
        [True,  False, True,  True,  True,  False, True ],
        [True,  False, True,  True,  True,  False, True ],
        [True,  False, False, False, False, False, True ],
        [True,  True,  True,  True,  True,  True,  True ]
    ]
    
    size = len(matrix)
    
    for row in range(7):
        for col in range(7):
            matrix_row = start_row + row
            matrix_col = start_col + col
            
            if (matrix_row >= size or matrix_col >= size or
                matrix[matrix_row][matrix_col] != expected[row][col]):
                return False
                
    return True


# Convenience function combinations
def assert_complete_svg_validation(svg_content: str,
                                 expected_width: int,
                                 expected_height: int,
                                 required_elements: List[str],
                                 required_classes: List[str],
                                 accessibility_level: str = "A") -> ET.Element:
    """
    Perform complete SVG validation including structure, elements, and accessibility.
    
    Args:
        svg_content: SVG content to validate
        expected_width: Expected width value
        expected_height: Expected height value  
        required_elements: List of required element names
        required_classes: List of required CSS classes
        accessibility_level: WCAG compliance level
        
    Returns:
        Parsed SVG root element
        
    Raises:
        SVGValidationError: If any validation fails
        AccessibilityValidationError: If accessibility validation fails
    """
    # Basic structure validation
    root = assert_svg_structure(svg_content, expected_width, expected_height)
    
    # Element validation
    assert_svg_elements_present(root, required_elements)
    
    # CSS class validation
    if required_classes:
        assert_svg_css_classes(root, required_classes)
        
    # Accessibility validation
    assert_accessibility_compliance(root, accessibility_level)
    
    return root


def assert_qr_code_complete(qr_matrix: List[List[bool]],
                           min_version: int = 1,
                           max_version: int = 40,
                           check_timing: bool = True) -> None:
    """
    Perform complete QR code validation including structure and patterns.
    
    Args:
        qr_matrix: QR code matrix to validate
        min_version: Minimum acceptable QR version
        max_version: Maximum acceptable QR version
        check_timing: Whether to validate timing patterns
        
    Raises:
        QRValidationError: If any QR validation fails
    """
    # Basic structure validation
    assert_qr_scannable(qr_matrix, min_version, max_version)
    
    # Timing pattern validation
    if check_timing:
        assert_qr_timing_patterns(qr_matrix)