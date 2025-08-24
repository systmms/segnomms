"""HTML generation utilities for the visual review suite."""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import re


class HTMLGenerator:
    """Generates HTML pages for the visual review suite."""
    
    def __init__(self, template_dir: Optional[Path] = None):
        """Initialize the HTML generator.
        
        Args:
            template_dir: Path to template directory (defaults to ./templates)
        """
        self.template_dir = template_dir or Path(__file__).parent / "templates"
        self._template_cache = {}
    
    def _load_template(self, template_name: str) -> str:
        """Load a template file with caching."""
        if template_name not in self._template_cache:
            template_path = self.template_dir / template_name
            if not template_path.exists():
                raise FileNotFoundError(f"Template not found: {template_path}")
            self._template_cache[template_name] = template_path.read_text()
        return self._template_cache[template_name]
    
    def _render_template(self, template_content: str, context: Dict[str, Any]) -> str:
        """Simple template rendering with variable substitution.
        
        Supports:
        - Variable substitution: {{ variable }}
        - Default values: {{ variable | default('value') }}
        - Safe HTML: {{ variable | safe }}
        - JSON formatting: {{ variable | tojson(indent=2) }}
        - Conditionals: {% if condition %} ... {% endif %}
        - For loops: {% for item in items %} ... {% endfor %}
        - Template inheritance: {% extends "base.html" %}, {% block content %}
        """
        # Handle template inheritance
        extends_match = re.search(r'{%\s*extends\s*"([^"]+)"\s*%}', template_content)
        if extends_match:
            base_template = self._load_template(extends_match.group(1))
            template_content = self._process_inheritance(base_template, template_content)
        
        # Process conditionals
        template_content = self._process_conditionals(template_content, context)
        
        # Process loops
        template_content = self._process_loops(template_content, context)
        
        # Process variables
        template_content = self._process_variables(template_content, context)
        
        return template_content
    
    def _process_inheritance(self, base_content: str, child_content: str) -> str:
        """Process template inheritance."""
        # Extract blocks from child
        blocks = {}
        block_pattern = r'{%\s*block\s+(\w+)\s*%}(.*?){%\s*endblock\s*%}'
        for match in re.finditer(block_pattern, child_content, re.DOTALL):
            blocks[match.group(1)] = match.group(2).strip()
        
        # Replace blocks in base
        result = base_content
        for block_name, block_content in blocks.items():
            pattern = r'{%\s*block\s+' + block_name + r'\s*%}.*?{%\s*endblock\s*%}'
            replacement = f'{{% block {block_name} %}}{block_content}{{% endblock %}}'
            result = re.sub(pattern, replacement, result, flags=re.DOTALL)
        
        return result
    
    def _process_conditionals(self, content: str, context: Dict[str, Any]) -> str:
        """Process if/endif conditionals."""
        def evaluate_condition(match):
            condition = match.group(1).strip()
            body = match.group(2)
            
            # Simple evaluation (only supports variable existence and comparisons)
            if condition in context and context[condition]:
                return body
            elif ' > ' in condition:
                parts = condition.split(' > ')
                if len(parts) == 2:
                    left = context.get(parts[0].strip(), 0)
                    right = int(parts[1].strip()) if parts[1].strip().isdigit() else parts[1].strip()
                    if left > right:
                        return body
            return ''
        
        pattern = r'{%\s*if\s+([^%]+)\s*%}(.*?){%\s*endif\s*%}'
        return re.sub(pattern, evaluate_condition, content, flags=re.DOTALL)
    
    def _process_loops(self, content: str, context: Dict[str, Any]) -> str:
        """Process for loops."""
        def process_loop(match):
            var_name = match.group(1).strip()
            items_name = match.group(2).strip()
            loop_body = match.group(3)
            
            items = context.get(items_name, [])
            result = []
            
            for item in items:
                # Create new context with loop variable
                loop_context = context.copy()
                loop_context[var_name] = item
                
                # Process the loop body with the loop context
                processed_body = self._process_variables(loop_body, loop_context)
                result.append(processed_body)
            
            return '\n'.join(result)
        
        pattern = r'{%\s*for\s+(\w+)\s+in\s+(\w+)\s*%}(.*?){%\s*endfor\s*%}'
        return re.sub(pattern, process_loop, content, flags=re.DOTALL)
    
    def _process_variables(self, content: str, context: Dict[str, Any]) -> str:
        """Process variable substitutions."""
        def replace_var(match):
            var_expr = match.group(1).strip()
            
            # Handle filters
            if '|' in var_expr:
                parts = var_expr.split('|')
                var_name = parts[0].strip()
                filter_expr = parts[1].strip()
                
                # Get variable value
                if '.' in var_name:
                    # Handle nested attributes
                    value = context
                    for part in var_name.split('.'):
                        value = value.get(part, '') if isinstance(value, dict) else getattr(value, part, '')
                else:
                    value = context.get(var_name, '')
                
                # Apply filter
                if filter_expr.startswith('default('):
                    default_match = re.search(r"default\(['\"]([^'\"]*)['\"](?:\s*,\s*(\w+))?\)", filter_expr)
                    if default_match:
                        default_value = default_match.group(1)
                        return str(value) if value else default_value
                elif filter_expr == 'safe':
                    return str(value)
                elif filter_expr.startswith('tojson'):
                    indent_match = re.search(r'indent=(\d+)', filter_expr)
                    indent = int(indent_match.group(1)) if indent_match else None
                    return json.dumps(value, indent=indent)
            else:
                # Simple variable
                var_name = var_expr
                if '.' in var_name:
                    # Handle nested attributes
                    value = context
                    for part in var_name.split('.'):
                        value = value.get(part, '') if isinstance(value, dict) else getattr(value, part, '')
                else:
                    value = context.get(var_name, '')
                return str(value)
            
            return match.group(0)  # Return original if not processed
        
        return re.sub(r'{{(.*?)}}', replace_var, content)
    
    def generate_dashboard(self, 
                         test_results: Dict[str, Any],
                         visual_stats: Dict[str, int],
                         recent_activity: Optional[List[Dict]] = None) -> str:
        """Generate the main dashboard HTML.
        
        Args:
            test_results: Test execution results (passed, failed, total, coverage)
            visual_stats: Visual test statistics (pending, approved, rejected)
            recent_activity: List of recent test activities
            
        Returns:
            Generated HTML string
        """
        template = self._load_template("dashboard.html")
        
        # Calculate pass rate
        total = test_results.get('total', 0)
        passed = test_results.get('passed', 0)
        pass_rate = (passed / total * 100) if total > 0 else 0
        
        context = {
            'title': 'SegnoMMS Review Dashboard',
            'passed': test_results.get('passed', 0),
            'failed': test_results.get('failed', 0),
            'total': total,
            'coverage': f"{test_results.get('coverage', 0):.1f}%" if test_results.get('coverage') else 'N/A',
            'pass_rate': f"{pass_rate:.1f}",
            'visual_pending': visual_stats.get('pending', 0),
            'visual_approved': visual_stats.get('approved', 0),
            'visual_rejected': visual_stats.get('rejected', 0),
            'recent_activity': recent_activity or []
        }
        
        return self._render_template(template, context)
    
    def generate_diff_page(self,
                          test_name: str,
                          baseline_content: str,
                          actual_content: str,
                          current_index: int = 1,
                          total_tests: int = 1,
                          test_info: Optional[str] = None,
                          config: Optional[Dict] = None) -> str:
        """Generate a visual diff comparison page.
        
        Args:
            test_name: Name of the test
            baseline_content: Baseline SVG content or image path
            actual_content: Actual SVG content or image path
            current_index: Current test index (for navigation)
            total_tests: Total number of tests
            test_info: Additional test information
            config: Test configuration
            
        Returns:
            Generated HTML string
        """
        template = self._load_template("diff.html")
        
        # Determine if content is SVG or image path
        is_baseline_svg = baseline_content.strip().startswith('<svg') if baseline_content else False
        is_actual_svg = actual_content.strip().startswith('<svg') if actual_content else False
        
        context = {
            'test_name': test_name,
            'baseline_svg': baseline_content if is_baseline_svg else None,
            'baseline_path': baseline_content if not is_baseline_svg else None,
            'actual_svg': actual_content if is_actual_svg else None,
            'actual_path': actual_content if not is_actual_svg else None,
            'current_index': current_index,
            'total_tests': total_tests,
            'test_info': test_info,
            'baseline_config': config,
            'show_nav': False  # Don't show main nav on diff pages
        }
        
        return self._render_template(template, context)
    
    def generate_gallery_page(self,
                            gallery_items: List[Dict[str, Any]],
                            title: str = "Shape Gallery",
                            description: Optional[str] = None,
                            show_search: bool = True) -> str:
        """Generate a gallery page for shapes or features.
        
        Args:
            gallery_items: List of gallery items with structure:
                {
                    'title': str,
                    'shape': str,  # shape identifier
                    'comparison': bool,  # if True, show safe mode on/off
                    'safe_on_path': str,  # path or SVG content
                    'safe_off_path': str,  # path or SVG content
                    'path': str,  # single image path (if not comparison)
                    'description': str,  # optional description
                    'config': dict  # optional configuration
                }
            title: Gallery title
            description: Gallery description
            show_search: Whether to show search box
            
        Returns:
            Generated HTML string
        """
        template = self._load_template("gallery.html")
        
        context = {
            'gallery_title': title,
            'gallery_description': description,
            'gallery_items': gallery_items,
            'show_search': show_search,
            'show_nav': False  # Don't show main nav on gallery pages
        }
        
        return self._render_template(template, context)
    
    def generate_full_review_suite(self,
                                 test_results: Dict[str, Any],
                                 visual_tests: List[Dict[str, Any]],
                                 shape_gallery: List[Dict[str, Any]],
                                 output_dir: Path) -> None:
        """Generate the complete review suite with all pages.
        
        Args:
            test_results: Test execution results
            visual_tests: List of visual test results
            shape_gallery: List of shape examples
            output_dir: Directory to write output files
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy assets
        assets_dir = output_dir / "assets"
        assets_dir.mkdir(exist_ok=True)
        
        # Copy CSS and JS
        css_source = Path(__file__).parent / "assets" / "review.css"
        js_source = Path(__file__).parent / "assets" / "review.js"
        
        if css_source.exists():
            (assets_dir / "review.css").write_text(css_source.read_text())
        if js_source.exists():
            (assets_dir / "review.js").write_text(js_source.read_text())
        
        # Calculate visual stats
        visual_stats = {
            'pending': len([t for t in visual_tests if t.get('status') == 'pending']),
            'approved': len([t for t in visual_tests if t.get('status') == 'approved']),
            'rejected': len([t for t in visual_tests if t.get('status') == 'rejected'])
        }
        
        # Generate main dashboard
        dashboard_html = self.generate_dashboard(test_results, visual_stats)
        (output_dir / "index.html").write_text(dashboard_html)
        
        # Generate visual diffs
        diffs_dir = output_dir / "diffs"
        diffs_dir.mkdir(exist_ok=True)
        
        for i, test in enumerate(visual_tests):
            diff_html = self.generate_diff_page(
                test_name=test['name'],
                baseline_content=test['baseline'],
                actual_content=test['actual'],
                current_index=i + 1,
                total_tests=len(visual_tests),
                test_info=test.get('info'),
                config=test.get('config')
            )
            (diffs_dir / f"{test['name']}.html").write_text(diff_html)
        
        # Generate shape gallery
        gallery_html = self.generate_gallery_page(
            gallery_items=shape_gallery,
            title="Shape Gallery - Safe Mode Comparison",
            description="Visual comparison of all shape types with safe mode ON vs OFF"
        )
        (output_dir / "gallery.html").write_text(gallery_html)
        
        # Generate data for JavaScript
        data_dir = output_dir / "data"
        data_dir.mkdir(exist_ok=True)
        
        review_data = {
            'generated': datetime.now().isoformat(),
            'test_results': test_results,
            'visual_tests': visual_tests,
            'visual_stats': visual_stats
        }
        
        (data_dir / "test_results.json").write_text(json.dumps(review_data, indent=2))