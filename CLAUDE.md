# Claude Development Context

This file contains important development context and reminders for Claude when working on the SegnoMMS project.

## 📋 Active Client Requirements Tracking

**⚠️ IMPORTANT:** Keep `CLIENT_REQUIREMENTS_IMPLEMENTATION.md` updated during all development work.

### Current Status (as of 2025-01-18)
- **Implementation Coverage:** 68% (35/52 features implemented or partial)
- **Remaining Effort:** ~7-10 weeks development time
- **Status Breakdown:**
  - ✅ **32 features (62%) IMPLEMENTED** - No work needed
  - 🟡 **3 features (6%) PARTIAL** - Enhancement needed
  - 🔴 **17 features (33%) MISSING** - New development required

### Update Requirements

**When making ANY code changes, you MUST:**

1. **Check Relevance:** Does this change relate to any client requirement?
2. **Update Status:** If implementing/fixing a client requirement, update the Implementation State Table
3. **Update Effort:** Adjust effort estimates if work is easier/harder than expected
4. **Document Location:** Add implementation file paths for newly implemented features
5. **Update Summary Stats:** Recalculate percentages and coverage when status changes

### Key Client Requirements to Track

**Core (MUST) - High Priority:**
- 🔴 Capability Discovery (0.5 weeks) - `segnomms/capabilities/` module needed
- 🔴 Scanability Harness (1 week) - Automated testing system
- 🔴 Reserve Area Modes (1 week) - Knockout vs. imprint enum
- 🔴 Intent-Based API (0.5 weeks) - Layer over existing RenderingConfig

**Enhanced (SHOULD) - Medium Priority:**
- 🔴 Pattern-Specific Styling (1.5 weeks) - finder/timing/alignment shapes
- 🔴 Frame Fade/Scale Modes (2 weeks) - Opacity and size transitions
- 🔴 Enhanced Accessibility (1 week) - ID generation and ARIA support

**Advanced (MAY) - Lower Priority:**
- 🔴 Imprint Mode Algorithm (1.5 weeks) - Complex reserve area interaction
- 🔴 Performance Monitoring (1 week) - Timing and metrics collection

### File Locations to Monitor

**When modifying these files, check for client requirement impacts:**

- `segnomms/config/schema.py` - Configuration models (affects multiple requirements)
- `segnomms/validation/phase4.py` - Scanability validation (Core requirement)
- `segnomms/utils/svg_builder.py` - SVG generation (affects accessibility, frames)
- `segnomms/shapes/` - Shape system (affects styling intents)
- `segnomms/plugin.py` - Main API (affects input/output models)

### Status Change Examples

**When you implement a missing feature:**
```markdown
# Before
| Reserve Area | Knockout vs. imprint modes | MUST | 🔴 | None | 1 week | New mode enum needed |

# After
| Reserve Area | Knockout vs. imprint modes | MUST | ✅ | `config/schema.py` | 0 weeks | ReserveMode enum implemented |
```

**When you enhance a partial feature:**
```markdown
# Before
| Reserve Area | Arbitrary placement | MUST | 🟡 | `config/schema.py` | 0.5 weeks | Extend offset system |

# After
| Reserve Area | Arbitrary placement | MUST | ✅ | `config/schema.py` | 0 weeks | Full arbitrary placement implemented |
```

### Update Process

1. **During Development:** Note which client requirements your changes address
2. **After Implementation:** Update the Implementation State Table immediately
3. **Recalculate Stats:** Update Summary Statistics and Coverage by Category
4. **Commit Together:** Include both code changes AND documentation updates in commits

### Completion Trigger

**🎯 When ALL requirements show ✅ IMPLEMENTED:**
- Update the document status to "COMPLETED"
- Ask the user if this tracking section can be removed from CLAUDE.md
- Archive or move the CLIENT_REQUIREMENTS_IMPLEMENTATION.md as appropriate

---

## ✅ Pydantic v2 + MyPy Modernization Achievement

**🎉 COMPLETED:** SegnoMMS configuration system successfully modernized to Pydantic v2 + MyPy strict typing patterns.

### Achievement Summary (as of 2025-01-25)

**Core Modernization Completed:**
- ✅ **Removed `use_enum_values=True`** - Config models now return enum objects at runtime
- ✅ **100% Config Module MyPy Compliance** - All 9 config modules pass strict MyPy validation
- ✅ **Discriminated Unions** - Shape configurations use proper type narrowing with `Field(discriminator="shape")`
- ✅ **TypedDict Patterns** - Type-safe **kwargs for shape renderers using `Unpack[TypedDict]`
- ✅ **Modern Typing Practices** - `from __future__ import annotations`, strict MyPy settings
- ✅ **Enum Objects at Runtime** - Proper enum object behavior instead of string conversion

### Technical Implementation

**Build System Updates:**
- Updated `pyproject.toml` with Pydantic `>=2.7,<3` constraint
- Added `plugins = ["pydantic.mypy"]` integration
- Enabled strict MyPy configuration with `disallow_any_generics=true`
- Added `py.typed` file for PEP 561 compliance

**Configuration Model Improvements:**
- Removed `use_enum_values=True` from all ConfigDict instances
- Added discriminated unions for shape-specific configurations:
  ```python
  ShapeSpecificConfig = Annotated[
      Union[BasicShapeConfig, RoundedShapeConfig, ConnectedShapeConfig],
      Field(discriminator="shape"),
  ]
  ```
- Updated enum comparisons to use `.value` only when string comparison needed
- Modern factory methods with proper type safety

**Type Safety Enhancements:**
- Created comprehensive TypedDict definitions in `segnomms/types.py`
- Updated shape renderers with type-safe patterns:
  ```python
  def render(
      self, x: float, y: float, size: float, **kwargs: Unpack[SquareRenderKwargs]
  ) -> ET.Element:
  ```
- Added proper type annotations throughout config modules

### Validation Status

**MyPy Compliance:**
- ✅ **segnomms/config/**: 9/9 files pass strict MyPy validation (100% clean)
- 🔄 **Overall codebase**: 215 MyPy errors remain (primarily in other modules, mostly annotation issues)

**Testing Status:**
- ✅ **Core functionality**: Configuration models work correctly with enum objects
- 🔄 **Test expectations**: Some tests still expect string values, need updating to expect enum objects
- ✅ **Backward compatibility**: Factory methods maintain compatibility with string inputs

### Best Practices Established

**For Future Development:**
1. **Always use enum objects** - Compare against `MergeStrategy.SOFT`, not `"soft"`
2. **Use discriminated unions** - For shape-specific configuration variants
3. **Apply TypedDict patterns** - For type-safe **kwargs usage
4. **Maintain strict MyPy** - All config modules must pass strict validation
5. **Test enum expectations** - Update test assertions to expect enum objects

### Achievement Impact

This modernization provides:
- **Enhanced Type Safety** - Catch more errors at development time
- **Better IDE Support** - Improved autocompletion and error detection
- **Runtime Enum Objects** - More robust enum handling without string conversion
- **Modern Pydantic Patterns** - Following current best practices
- **Discriminated Union Benefits** - Proper type narrowing for shape configurations

**The configuration system is now a model implementation of Pydantic v2 + MyPy best practices.**

---

## 📚 Documentation Strategy and Policy

**⚠️ IMPORTANT:** This project uses a **Sphinx-first documentation strategy** to prevent documentation sprawl.

### Primary Documentation: Sphinx/RST (docs/source/)

**All user-facing documentation MUST go in Sphinx:**
- API reference (auto-generated from docstrings)
- Configuration guides
- Usage examples
- Installation instructions
- Feature documentation

**Update Sphinx docs when:**
- Adding new features or configuration options
- Changing existing APIs
- Adding examples or tutorials
- Updating installation/setup procedures

### Allowed Markdown Files (Repository Only)

**ONLY these Markdown files are permitted:**
1. `README.md` - GitHub landing page and quick start
2. `CHANGELOG.md` - Version history and release notes
3. `CLAUDE.md` - Development context and instructions (this file)

### Forbidden: Analysis and Temporary Documentation

**❌ DO NOT CREATE:**
- Analysis documents (`*_ANALYSIS.md`, `*_REPORT.md`)
- Implementation plans (`*_IMPLEMENTATION.md`, `*_PLAN.md`)
- Requirements documents (`REQUIREMENTS_*.md`)
- Testing guides outside of Sphinx
- API documentation in Markdown
- Configuration guides in Markdown
- Temporary development notes as permanent files

### Documentation Workflow

1. **New Feature Development:**
   - Write comprehensive docstrings in code
   - Add configuration examples to Sphinx
   - Update API documentation if needed
   - Add to CHANGELOG.md when released

2. **Research/Analysis:**
   - Use temporary files locally (not committed)
   - Document final decisions in code comments or Sphinx
   - Update CLAUDE.md if it affects development workflow

3. **Before Committing:**
   - Check that no new `.md` files are being added (except the 3 allowed)
   - Ensure Sphinx docs are updated if APIs changed
   - Run `make docs` to verify documentation builds

### Building Documentation

```bash
# Build Sphinx documentation
make docs

# Serve documentation locally
make docs-serve
```

### Rationale

This project serves a **commercial QR generation service** where:
- Comprehensive API documentation is essential for development
- Searchable, cross-referenced docs improve productivity
- Auto-generated docs from docstrings stay current
- Professional documentation supports commercial use

**Documentation sprawl previously reached 48 MD + 23 RST files. This policy prevents recurrence.**

---

## 🎯 Test Script Discoverability Policy

**⚠️ IMPORTANT:** All permanent test scripts must be represented in the Makefile for discoverability and consistency.

### Test Script Categories

**✅ MUST be in Makefile:**
- **Regression test scripts** - Cross-platform, visual, compatibility testing
- **Integration test suites** - End-to-end testing, external dependencies
- **Compatibility test scripts** - Multi-version, multi-environment testing
- **Performance benchmarks** - Repeatable performance measurement
- **Build validation scripts** - Distribution verification, deployment checks

**🔄 SHOULD be in Makefile:**
- **Development test utilities** - Frequently used during development
- **Platform-specific tests** - OS-specific or environment-specific testing
- **Documentation tests** - Example validation, documentation consistency

**⚪ MAY be standalone:**
- **One-off test scripts** - Temporary debugging, investigation scripts
- **Experimental scripts** - Proof-of-concept, research testing
- **Personal development tools** - Individual developer utilities

### Implementation Requirements

**Makefile Target Naming:**
- Use descriptive targets: `test-segno-compatibility` not `test-compat`
- Group related tests: `test-cross-platform`, `test-environments`
- Include help text in the `help` target

**Documentation in Makefile:**
```makefile
# Test compatibility across multiple Segno versions
test-segno-compatibility:
	@echo "Testing compatibility with Segno versions 1.3.1 to 1.6.6..."
	$(PYTHON) scripts/test_segno_compatibility.py

# Test distribution build process
test-build:
	@echo "Testing distribution build process..."
	$(PYTHON) -m build --wheel
```

### Benefits of This Policy

1. **Discoverability** - `make help` shows all available tests
2. **Consistency** - Standardized execution patterns
3. **CI/CD Integration** - Easy to include in automated pipelines
4. **Documentation** - Makefile becomes living test documentation
5. **Dependency Management** - Handle prerequisites and setup
6. **Maintenance** - Single place to update test commands

### Enforcement

**During development:**
- When creating new test scripts, add Makefile target immediately
- When reviewing PRs, verify test scripts have corresponding targets
- Use `make help` to audit available vs. actual test scripts

**File naming convention:**
- Permanent tests: `test_*.py` or `*_test.py`
- Temporary tests: `debug_*.py`, `explore_*.py`, `tmp_*.py`

---

## 🧪 QR Generation Testing Framework

**⚠️ IMPORTANT:** Use this systematic testing approach when evaluating/testing QR code generation.

### Testing Methodology

**When testing any QR generation, you MUST systematically evaluate:**

1. **Configuration Analysis** - Review all options used
2. **Format Validation** - Verify SVG structure and values
3. **Visual Inspection** - Confirm all visual settings are respected
4. **Scanability Check** - Ensure QR codes remain functional

### 1. Configuration Analysis Phase

**For EVERY QR generation test, document:**

```python
# Example systematic review:
config_analysis = {
    "payload": "Hello World",  # What content is encoded
    "scale": 10,              # Module size in pixels
    "border": 4,              # Quiet zone size
    "shape": "squircle",      # Module shape type
    "corner_radius": 0.3,     # Shape-specific parameter
    "dark": "#1a1a2e",        # Foreground color
    "light": "#ffffff",       # Background color
    "merge": "soft",          # Module merging strategy
    "connectivity": "8-way",  # Neighbor detection mode
    "interactive": True,      # Enable hover effects
    "frame": {                # Frame configuration
        "shape": "circle",
        "clip_mode": "fade"
    },
    "centerpiece": {          # Reserve area
        "enabled": True,
        "size": 0.15,
        "shape": "circle"
    }
}
```

**Document Expected Behavior:**
- Which shapes should be used where
- What colors should appear
- How modules should connect/merge
- Frame effects and clipping
- Interactive features expected

### 2. Format Validation Phase

**SVG Structure Verification:**

```python
# Required SVG validation checks:
format_validation = {
    "svg_attributes": {
        "width": "expected_width",
        "height": "expected_height",
        "viewBox": "0 0 width height",
        "xmlns": "http://www.w3.org/2000/svg"
    },
    "layer_structure": [
        "background",      # Background layer present
        "quiet-zone",      # Quiet zone if enabled
        "frame",           # Frame layer if configured
        "modules",         # QR module elements
        "centerpiece",     # Centerpiece if enabled
        "styles"           # CSS styles if interactive
    ],
    "css_classes": [
        "qr-module",       # Base module class
        "qr-finder",       # Finder pattern class
        "qr-data",         # Data module class
        "qr-timing"        # Timing pattern class
    ],
    "accessibility": {
        "title": "present_if_specified",
        "desc": "present_if_specified"
    }
}
```

**Validate Specific Elements:**
- Module count matches QR version
- Finder patterns in correct positions
- Timing patterns present and positioned correctly
- Alignment patterns (for larger QR codes)
- Frame clipping paths if configured
- CSS classes applied correctly

### 3. Visual Inspection Phase

**Systematic Visual Checks:**

#### 3.1 Module Shape Verification
```python
visual_checks = {
    "module_shapes": {
        "data_modules": "verify_shape_matches_config",
        "finder_patterns": "check_finder_shape_config",
        "timing_patterns": "verify_timing_appearance",
        "alignment_patterns": "check_alignment_rendering"
    },
    "shape_parameters": {
        "corner_radius": "measure_actual_vs_expected",
        "size_ratio": "verify_module_size_consistency",
        "spacing": "check_gaps_between_modules"
    }
}
```

#### 3.2 Color and Style Verification
```python
color_style_checks = {
    "colors": {
        "foreground": "verify_dark_color_applied",
        "background": "verify_light_color_applied",
        "gradients": "check_gradient_application"
    },
    "merging": {
        "merge_strategy": "verify_adjacent_module_merging",
        "connectivity": "check_neighbor_connections",
        "flow": "observe_visual_flow_patterns"
    }
}
```

#### 3.3 Frame and Effects Verification
```python
frame_effects_checks = {
    "frame": {
        "shape": "verify_frame_shape_matches_config",
        "clipping": "check_module_clipping_at_edges",
        "fade_effects": "verify_opacity_transitions"
    },
    "centerpiece": {
        "area_cleared": "verify_modules_removed_correctly",
        "shape_match": "check_centerpiece_shape",
        "positioning": "verify_center_or_offset_placement"
    }
}
```

#### 3.4 Interactive Features Verification
```python
interactive_checks = {
    "css_classes": "verify_all_modules_have_classes",
    "hover_styles": "check_css_hover_definitions",
    "tooltips": "verify_tooltip_data_attributes",
    "click_handlers": "check_javascript_event_handlers"
}
```

### 4. Scanability Verification

**QR Code Functional Testing:**

```python
scanability_checks = {
    "pattern_integrity": {
        "finder_patterns": "three_corners_clearly_defined",
        "timing_patterns": "alternating_pattern_visible",
        "alignment_patterns": "positioned_correctly"
    },
    "quiet_zone": {
        "size": "verify_border_meets_minimum",
        "clarity": "ensure_no_visual_interference"
    },
    "contrast": {
        "ratio": "verify_sufficient_contrast",
        "consistency": "check_uniform_module_appearance"
    },
    "frame_interference": {
        "clipping": "ensure_no_critical_pattern_clipping",
        "fade_effects": "verify_patterns_remain_scannable"
    }
}
```

### 5. Testing Workflow

**Step-by-Step Process:**

#### Phase 1: Pre-Generation Analysis
```python
def analyze_configuration(config):
    """Analyze configuration before generation."""
    print("🔍 Configuration Analysis")
    print(f"Shape: {config.geometry.shape}")
    print(f"Scale: {config.scale}px per module")
    print(f"Colors: {config.dark} on {config.light}")
    print(f"Merge strategy: {config.geometry.merge}")
    print(f"Interactive: {config.style.interactive}")
    # ... document all relevant settings
```

#### Phase 2: Post-Generation Validation
```python
def validate_svg_format(svg_content):
    """Validate SVG structure and content."""
    # Parse SVG and verify structure
    # Check required elements present
    # Validate attributes and values
    # Verify CSS classes applied
```

#### Phase 3: Visual Inspection Protocol
```python
def visual_inspection_checklist(config, svg_path):
    """Systematic visual inspection."""
    checklist = {
        "module_shape_correct": False,
        "colors_applied": False,
        "merging_visible": False,
        "frame_effects_working": False,
        "centerpiece_cleared": False,
        "interactive_features_present": False
    }

    # Manual inspection with screenshots if needed
    # Document any discrepancies
    return checklist
```

#### Phase 4: Scanability Testing
```python
def test_scanability(svg_path):
    """Test QR code scannability."""
    # Convert SVG to raster if needed
    # Test with multiple QR scanners
    # Verify content matches original payload
    # Test at different sizes/DPI
```

### 6. Documentation Requirements

**For each test, document:**

```markdown
## QR Generation Test: [Test Name]

### Configuration Used
```python
# Complete configuration object
```

### Expected Behavior
- Shape: [expected module shapes]
- Colors: [expected color application]
- Effects: [expected visual effects]
- Interactive: [expected interactive features]

### Format Validation Results
- ✅/❌ SVG structure correct
- ✅/❌ Required elements present
- ✅/❌ CSS classes applied
- ✅/❌ Accessibility features included

### Visual Inspection Results
- ✅/❌ Module shapes match configuration
- ✅/❌ Colors applied correctly
- ✅/❌ Merging/connectivity working
- ✅/❌ Frame effects functioning
- ✅/❌ Centerpiece area cleared

### Scanability Test Results
- ✅/❌ QR code scans successfully
- ✅/❌ Content matches original
- ✅/❌ Patterns clearly defined
- ✅/❌ Sufficient contrast maintained

### Issues Found
[Document any problems or discrepancies]

### Screenshots
[Include visual evidence if needed]
```

### 7. Common Issues to Watch For

**Frequent Problem Areas:**

#### Shape Rendering Issues
- Corner radius not applied consistently
- Connected shapes not merging properly
- Shape variants not matching configuration
- Size ratios incorrect

#### Color Application Problems
- Colors not applied to all module types
- Gradient effects not working
- Contrast insufficient for scanning
- CSS color overrides not functioning

#### Frame and Clipping Issues
- Frame shape not matching configuration
- Clipping cutting off critical QR patterns
- Fade effects too aggressive
- Custom SVG paths malformed

#### Interactive Feature Problems
- CSS classes missing from modules
- Hover effects not defined
- JavaScript handlers not attached
- Tooltip data attributes missing

#### Centerpiece/Reserve Area Issues
- Wrong modules cleared from reserve area
- Shape not matching configuration
- Positioning offset incorrect
- Size calculation wrong

### 8. Automated Testing Hooks

**Integration with Testing:**

```python
# Add to test functions:
def test_qr_generation_systematic(config_name, expected_behavior):
    """Systematic QR generation test."""

    # Phase 1: Configuration analysis
    config = get_test_config(config_name)
    analyze_configuration(config)

    # Phase 2: Generate QR
    svg_content = generate_qr_with_config(config)

    # Phase 3: Format validation
    format_results = validate_svg_format(svg_content)

    # Phase 4: Visual inspection (manual step)
    print("🔍 Manual visual inspection required")
    print("Check generated SVG against expected behavior")

    # Phase 5: Scanability test
    scanability_results = test_scanability(svg_content)

    # Document results
    document_test_results(config, expected_behavior,
                         format_results, scanability_results)
```

### 9. Quality Gates

**Before declaring a QR generation test successful:**

- [ ] Configuration analysis completed and documented
- [ ] SVG format validation passes all checks
- [ ] Visual inspection confirms all settings respected
- [ ] Scanability test passes with multiple scanners
- [ ] No critical issues identified
- [ ] Results documented with evidence

**If any quality gate fails:**
1. Document the failure in detail
2. Identify root cause in code
3. Fix the issue
4. Re-run complete testing cycle
5. Update test documentation

---

## 🛠️ Development Environment Updates

**⚠️ IMPORTANT:** When adding new dependencies or system requirements, always update:

1. **Python Dependencies** (`pyproject.toml` [tool.uv.dev-dependencies] or `docs/requirements.txt` for documentation)
2. **Lock File** (`uv lock` to update uv.lock)
3. **Nix Environment** (`flake.nix` and reload with `direnv reload` if using Nix)

### Development Environment Management

SegnoMMS uses `uv` for ultra-fast Python package management and `Hatchling` as the build backend (modern replacement for setuptools).

**Quick start:**
```bash
# Install uv (one-time setup)
pip install uv

# Setup development environment
make setup

# Or manually:
uv sync
uv pip install -e .

# Run tests
uv run pytest tests/
```

### Documentation Dependencies with uv

Documentation dependencies are managed separately for flexibility:

- **Development deps**: `pyproject.toml` [tool.uv.dev-dependencies] (installed via `uv sync`)
- **Documentation deps**: `docs/requirements.txt` (includes MyST-Parser for markdown integration)

**Building documentation:**
```bash
# Install docs dependencies
uv pip install -r docs/requirements.txt

# Build documentation
cd docs && make html

# Or use the make target
make docs
```

### MyST-Parser Integration

**GitHub-First Markdown Files:**
- `CONTRIBUTING.md` is the single source of truth (included in Sphinx via MyST-Parser)
- `README.md` remains GitHub-focused (different purpose than `index.rst`)
- Sphinx includes contributing content: `.. include:: ../../CONTRIBUTING.md`

**MyST-Parser Configuration:**
- Extension enabled in `docs/source/conf.py`
- Supports GitHub-flavored markdown features
- Automatic heading anchors and cross-references

### Common Environment Updates

**When adding Python packages:**
```bash
# 1. Add to appropriate location:
# - Development: pyproject.toml [tool.uv.dev-dependencies]
# - Documentation: docs/requirements.txt

# 2. Update lock file (for pyproject.toml changes)
uv lock

# 3. Sync environment
uv sync
# OR for docs dependencies:
uv pip install -r docs/requirements.txt

# 4. Add to flake.nix pythonEnv section if needed by Nix
# Edit flake.nix and add the package

# 5. Reload Nix environment (if using)
direnv reload
```

**When adding system dependencies:**
```bash
# 1. Add to flake.nix buildInputs section
# Edit flake.nix

# 2. Reload Nix environment
direnv reload
```

### Visual Regression Testing Setup

For visual regression testing to work properly:
- **rsvg-convert** is provided by Nix (librsvg in flake.nix)
- **cairosvg** may have issues with cffi in mixed Python environments
- The system will automatically fallback to rsvg-convert when cairosvg fails

---

## 🔧 Development Context

### Project Architecture
- **Plugin Type:** Segno QR code generation plugin
- **Build System:** Hatchling (modern PEP 517/518 build backend)
- **Configuration:** Comprehensive Pydantic-based system with 14+ models
- **Shape System:** 14 different renderers with factory pattern
- **Processing:** Multi-phase pipeline (Phase 1-4)
- **Output:** Professional SVG with accessibility and interactivity

### Code Conventions
- Use existing Pydantic patterns for new configuration models
- Follow factory pattern for extending shape renderers
- Maintain backward compatibility with existing kwargs API
- Add comprehensive type hints and validation
- Include docstrings and field descriptions

### Testing Requirements
- Run existing test suite: `pytest tests/`
- Add tests for new functionality
- Maintain >90% test coverage
- Test backward compatibility
- Include visual regression tests for shape changes

---

*This file should be updated regularly during development. Remove this client tracking section once all requirements are implemented and confirmed with the user.*
