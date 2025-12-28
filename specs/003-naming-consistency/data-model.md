# Data Model: Project Naming Consistency Review

**Feature**: 003-naming-consistency
**Date**: 2025-12-28

## Overview

This feature primarily affects naming conventions and documentation rather than data structures. However, there are key entities representing the naming patterns and deprecation system.

## Entities

### 1. DeprecatedOptionMapping

Represents the mapping between deprecated option names and their current equivalents.

**Attributes**:
| Field | Type | Description |
|-------|------|-------------|
| `deprecated_name` | `str` | The old option name (e.g., `reserve_center`) |
| `current_name` | `str` | The new option name (e.g., `centerpiece_enabled`) |
| `category` | `str` | Grouping category (`centerpiece`, `qr_advanced`) |
| `deprecated_since` | `str` | Version when deprecation started |
| `removal_version` | `str | None` | Version when removal planned (None for pre-1.0.0) |

**Instances**:

#### Centerpiece Aliases
| Deprecated | Current | Category |
|------------|---------|----------|
| `reserve_center` | `centerpiece_enabled` | centerpiece |
| `reserve_shape` | `centerpiece_shape` | centerpiece |
| `reserve_size` | `centerpiece_size` | centerpiece |
| `reserve_offset_x` | `centerpiece_offset_x` | centerpiece |
| `reserve_offset_y` | `centerpiece_offset_y` | centerpiece |
| `reserve_margin` | `centerpiece_margin` | centerpiece |

#### QR Advanced Aliases
| Deprecated | Current | Category |
|------------|---------|----------|
| `qr_eci` | `eci` | qr_advanced |
| `qr_encoding` | `encoding` | qr_advanced |
| `qr_mask` | `mask_pattern` | qr_advanced |
| `qr_symbol_count` | `symbol_count` | qr_advanced |
| `qr_boost_error` | `boost_error` | qr_advanced |
| `multi_symbol` | `structured_append` | qr_advanced |

**Note**: `qr_eci` maps to bare `eci` following the convention that Segno-inherited concepts use bare names.

---

### 2. BooleanNamingConvention

Represents the naming convention rules for boolean configuration options.

**Rules**:
| Pattern | Use Case | Examples |
|---------|----------|----------|
| Bare name | Segno-inherited concepts | `eci`, `boost_error`, `micro` |
| `*_enabled` suffix | State booleans | `centerpiece_enabled`, `phase1.enabled` |
| `use_*` prefix | Algorithm/strategy selection | `use_marching_squares`, `use_cluster_rendering` |
| Bare name | UI interaction behaviors | `interactive`, `tooltips` |

**Deprecated Pattern**: `enable_*` prefix (action verb, should be avoided)

---

### 3. ClassRename

Represents the Phase4Validator → CompositionValidator rename.

**Attributes**:
| Field | Value |
|-------|-------|
| `old_name` | `Phase4Validator` |
| `new_name` | `CompositionValidator` |
| `file_path` | `segnomms/validation/phase4.py` |
| `alias_strategy` | Class alias with `__getattr__` or direct assignment |

**Deprecation Alias Pattern**:
```python
# In segnomms/validation/phase4.py
class CompositionValidator:
    """Validates composition of QR code visual elements."""
    ...

# Deprecated alias for backward compatibility
Phase4Validator = CompositionValidator
```

---

### 4. PublicAPIExport

Represents items in the `__all__` list.

**Current State** (`segnomms/plugin/__init__.py`):

| Export | Type | Status |
|--------|------|--------|
| `write` | function | Keep |
| `write_advanced` | function | Keep |
| `register_with_segno` | function | Keep |
| `generate_interactive_svg` | function | Keep |
| `MAX_QR_SIZE` | constant | Keep |
| `_export_configuration` | function | **Remove** |
| `_generate_config_hash` | function | **Remove** |
| `_get_pattern_specific_style` | function | **Remove** |
| `_get_pattern_specific_render_kwargs` | function | **Remove** |
| `_render_cluster` | function | **Remove** |
| `_get_enhanced_render_kwargs` | function | **Remove** |
| `_format_svg_string` | function | **Remove** |
| `_detect_and_remove_islands` | function | **Remove** |

**Target State**:
```python
__all__ = [
    "write",
    "write_advanced",
    "register_with_segno",
    "generate_interactive_svg",
    "MAX_QR_SIZE",
]
```

---

### 5. PhaseDocumentation

Represents the correct documentation for each processing phase.

| Phase | Current Doc Label | Correct Description |
|-------|-------------------|---------------------|
| Phase 1 | "Clustering" | Enhanced 8-neighbor context detection for context-aware shape selection |
| Phase 2 | "Shape Rendering" | Connected component clustering for unified module group rendering |
| Phase 3 | "SVG Assembly" | Marching squares algorithm with Bezier curve smoothing for organic contours |
| Phase 4 / CompositionValidator | (undocumented in config) | Validation system for frames, centerpieces, and feature interactions |

---

## State Transitions

### Deprecation Warning States

```
Option Used
    │
    ├─► [Deprecated Name Only]
    │       └─► Emit DeprecationWarning → Process with mapped current name
    │
    ├─► [Current Name Only]
    │       └─► No warning → Process normally
    │
    ├─► [Both Names, Same Value]
    │       └─► Emit DeprecationWarning (duplicate) → Use current name's value
    │
    └─► [Both Names, Different Values]
            └─► Raise ValueError (conflict)
```

---

## Validation Rules

### Option Conflict Detection

1. **Conflict**: Both deprecated and current names provided with different values
   - Result: `ValueError` with message explaining the conflict

2. **Duplicate**: Both deprecated and current names provided with same value
   - Result: `DeprecationWarning` mentioning redundant usage

3. **Deprecated Only**: Only deprecated name provided
   - Result: `DeprecationWarning` with migration guidance

### Naming Convention Compliance

For future development, boolean options MUST follow:
1. Use bare names for Segno-inherited concepts
2. Use `*_enabled` suffix for state booleans (not `enable_*` prefix)
3. Use `use_*` prefix for algorithm/strategy selection
4. Use bare names for UI behaviors

---

## No Database/API Changes

This feature does not introduce:
- New database tables or fields
- New API endpoints
- New data persistence requirements

All changes are to:
- Class/function naming
- Configuration option aliasing
- Documentation content
- Warning emission
