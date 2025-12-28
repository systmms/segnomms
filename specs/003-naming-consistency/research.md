# Research: Project Naming Consistency Review

**Feature**: 003-naming-consistency
**Date**: 2025-12-28
**Status**: Complete

## Research Tasks Completed

### 1. Phase4Validator Investigation

**Question**: What is Phase4Validator and how should it be renamed?

**Decision**: Rename to `CompositionValidator`

**Rationale**:
- Phase4Validator validates frame shapes, centerpiece reserves, and feature interactions
- It is fundamentally different from Phases 1-3 which are processing steps
- The name "CompositionValidator" accurately describes its purpose: validating the composition of QR code visual elements
- Maintains validation-focused naming consistent with its methods: `validate_frame_safety()`, `validate_centerpiece_safety()`, etc.

**Alternatives Considered**:
- `FrameValidator` - Too narrow, also validates centerpieces
- `AdvancedFeatureValidator` - Too vague
- `OutputValidator` - Doesn't convey the composition aspect
- Documentation-only fix - Rejected per clarification; rename provides clearer API

**Location**: `segnomms/validation/phase4.py:31-46`

**Implementation Notes**:
- Create `Phase4Validator` as deprecated alias pointing to `CompositionValidator`
- Update all internal imports
- Class methods remain unchanged

---

### 2. Boolean Naming Convention Audit

**Question**: What naming convention should be adopted for boolean options?

**Decision**: Hybrid approach matching ecosystem conventions

**Rationale**:
Based on `.specify/ideas/project-naming.md` ecosystem research:
- Python QR/image ecosystem (Segno, qrcode, Pillow) prefers bare boolean names
- `enable_*` is an action verb, not a state descriptor
- SegnoMMS is more verbose than ecosystem norms

**Convention Adopted**:

| Pattern | When to Use | Example |
|---------|-------------|---------|
| Bare name | Segno-inherited concepts | `eci`, `boost_error` |
| `*_enabled` suffix | State booleans | `centerpiece_enabled`, `phase1_enabled` |
| `use_*` prefix | Strategy/algorithm selection | `use_marching_squares` |
| Bare name | UI behaviors | `interactive`, `tooltips` |

**Deprecated Pattern**: `enable_*` prefix (action verb, not state)

**Alternatives Considered**:
- All bare names - Would break Segno compatibility
- All `enable_*` - Contradicts ecosystem conventions
- All `is_*` prefix - Too verbose for kwargs API

**No code changes for existing options** - This defines the convention for future development and documentation. Existing options remain with deprecation policy.

---

### 3. Deprecated Option Aliases Audit

**Question**: What options need deprecation warnings?

**Decision**: Add warnings for all legacy aliases

**Findings from `segnomms/config/models/core.py`**:

**`reserve_*` → `centerpiece_*` (Lines 309-324)**:
| Deprecated | Current |
|------------|---------|
| `reserve_center` | `centerpiece_enabled` |
| `reserve_shape` | `centerpiece_shape` |
| `reserve_size` | `centerpiece_size` |
| `reserve_offset_x` | `centerpiece_offset_x` |
| `reserve_offset_y` | `centerpiece_offset_y` |
| `reserve_margin` | `centerpiece_margin` |

**`qr_*` → Direct Names (Lines 333-346)**:
| Deprecated | Current |
|------------|---------|
| `qr_eci` | `eci` |
| `qr_encoding` | `encoding` |
| `qr_mask` | `mask_pattern` |
| `qr_symbol_count` | `symbol_count` |
| `qr_boost_error` | `boost_error` |
| `multi_symbol` | `structured_append` |

**Note**: `qr_eci` maps to bare `eci` (not `eci_enabled`) following the convention that Segno-inherited concepts use bare names.

**Implementation Approach**:
1. Use `warnings.warn()` with `DeprecationWarning` category
2. Emit warning when deprecated option is used
3. Error if both deprecated and current provided with different values
4. Warn only if both provided with same value

**Rationale**: Standard Python deprecation pattern; allows gradual migration while catching conflicts early.

---

### 4. Underscore-Prefixed Exports Investigation

**Question**: Which private functions are incorrectly exported?

**Decision**: Remove all underscore-prefixed functions from `__all__`

**Findings from `segnomms/plugin/__init__.py:35-49`**:

**To Remove from `__all__`**:
1. `_export_configuration`
2. `_generate_config_hash`
3. `_get_pattern_specific_style`
4. `_get_pattern_specific_render_kwargs`
5. `_render_cluster`
6. `_get_enhanced_render_kwargs`
7. `_format_svg_string`
8. `_detect_and_remove_islands`

**To Keep in `__all__`**:
- `write` - Public API
- `write_advanced` - Public API
- `register_with_segno` - Public API
- `generate_interactive_svg` - Public API
- `MAX_QR_SIZE` - Public constant

**Rationale**:
- Underscore prefix indicates internal implementation details
- Exporting them contradicts Python's encapsulation conventions
- Removing from `__all__` doesn't break internal usage
- Users relying on these should be using the documented public API

**Alternatives Considered**:
- Rename without underscore - Would suggest API stability guarantee we don't want
- Keep in `__all__` with documentation - Perpetuates the anti-pattern

---

### 5. Phase Documentation Accuracy

**Question**: What do the phases actually do vs what documentation says?

**Decision**: Update documentation to match implementation

**Findings from `segnomms/config/models/phases.py` docstrings**:

| Phase | Documentation Says | Actually Does |
|-------|-------------------|---------------|
| Phase 1 | "Clustering" | Enhanced 8-neighbor context detection |
| Phase 2 | "Shape Rendering" | Connected component clustering |
| Phase 3 | "SVG Assembly" | Marching squares with Bezier curve smoothing |
| Phase 4 | (Not documented in config) | Frame/centerpiece validation (CompositionValidator) |

**Correct Descriptions**:
- **Phase 1**: Enhanced neighbor detection that analyzes 8-directional module connectivity for context-aware shape selection
- **Phase 2**: Connected component clustering that groups adjacent modules for unified rendering
- **Phase 3**: Marching squares algorithm with Bezier curve smoothing for organic contour generation
- **CompositionValidator**: Validation system for frames, centerpieces, and feature interactions (not a processing phase)

**Location to Update**: `docs/source/api/config.rst` lines 121-145

---

### 6. Deprecation Warning Implementation Pattern

**Question**: How should deprecation warnings be implemented?

**Decision**: Use Python's standard `warnings` module

**Pattern**:
```python
import warnings

def from_kwargs(cls, **kwargs):
    # Check for deprecated options
    deprecated_mappings = {
        "reserve_center": "centerpiece_enabled",
        "reserve_shape": "centerpiece_shape",
        # ... etc
    }

    for old_name, new_name in deprecated_mappings.items():
        if old_name in kwargs:
            warnings.warn(
                f"Option '{old_name}' is deprecated, use '{new_name}' instead. "
                f"This option will be removed in a future version.",
                DeprecationWarning,
                stacklevel=2
            )

            # Handle conflict: both old and new provided
            if new_name in kwargs:
                if kwargs[old_name] != kwargs[new_name]:
                    raise ValueError(
                        f"Conflicting values for '{old_name}' and '{new_name}': "
                        f"received {kwargs[old_name]!r} and {kwargs[new_name]!r}"
                    )
                # Same value: just warn, use new name's value
```

**Rationale**:
- `warnings.warn()` is Python standard
- `DeprecationWarning` is the correct category
- `stacklevel=2` points to the caller's code, not our internal code
- Explicit conflict handling prevents silent data loss

**Alternatives Considered**:
- Using `logger.warning()` - Doesn't integrate with Python's warning system
- Silent replacement - Loses opportunity to guide migration

---

## Summary

All research tasks complete. No outstanding questions. Ready to proceed to Phase 1 design and task generation.

**Key Decisions**:
1. Rename Phase4Validator → CompositionValidator with deprecated alias
2. Adopt hybrid boolean naming convention (bare for Segno, `*_enabled` for state)
3. Add deprecation warnings for 12 legacy option aliases
4. Remove 8 underscore-prefixed functions from `__all__`
5. Correct phase descriptions in documentation
6. Use standard Python `warnings` module for deprecations
