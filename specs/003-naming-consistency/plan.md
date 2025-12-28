# Implementation Plan: Project Naming Consistency Review

**Branch**: `003-naming-consistency` | **Date**: 2025-12-28 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-naming-consistency/spec.md`

## Summary

Standardize naming patterns across SegnoMMS configuration options to improve developer experience and API learnability. Key changes include:
1. Rename Phase4Validator to CompositionValidator with deprecation alias
2. Add deprecation warnings for `reserve_*` and `qr_*` option aliases
3. Fix underscore-prefixed exports in `segnomms.plugin.__init__`
4. Correct phase descriptions in documentation to match implementation
5. Document boolean naming conventions for future development

## Technical Context

**Language/Version**: Python 3.9+ (see pyproject.toml for compatibility matrix)
**Primary Dependencies**: Segno >=1.5.2, Pydantic >=2.7,<3, typing-extensions >=4.8
**Configuration System**: Pydantic v2 with discriminated unions and strict MyPy compliance
**Plugin Architecture**: Segno plugin via entry-points, maintains backward compatibility
**Testing Framework**: pytest with comprehensive test categories (unit/integration/visual/structural/performance)
**Target Platform**: Cross-platform Python package (Linux/macOS/Windows)
**Project Type**: Segno QR generation plugin with multi-phase processing pipeline
**Performance Goals**: Sub-second QR generation, scalable algorithms, <100MB memory usage
**Constraints**: Backward compatibility with existing API, commercial SVG quality standards
**Scale/Scope**: Professional QR generation service, 14 shape renderers, comprehensive configuration system

### Feature-Specific Context

**Current State (from codebase exploration):**

1. **Phase4Validator** (`segnomms/validation/phase4.py:31-46`):
   - Currently named `Phase4Validator`
   - Actually performs validation of frame shapes, centerpiece reserves, and feature interactions
   - Not a processing phase like Phases 1-3; it's a validation system

2. **Boolean Naming Patterns** (127 config fields, 5 different patterns):
   - `enabled` suffix: `Phase1Config.enabled`, `CenterpieceConfig.enabled` (6 instances)
   - `use_*` prefix: `use_enhanced_shapes`, `use_cluster_rendering` (5 instances)
   - `enable_*` prefix: `enable_palette_validation`, `enable_caching` (3 instances)
   - Bare names: `interactive`, `tooltips` (2 instances)
   - Inconsistent: `eci_enabled` vs `boost_error` in same class

3. **Underscore-Prefixed Exports** (`segnomms/plugin/__init__.py:35-49`):
   - 7 private functions in `__all__`: `_export_configuration`, `_generate_config_hash`, `_get_pattern_specific_style`, `_get_pattern_specific_render_kwargs`, `_render_cluster`, `_get_enhanced_render_kwargs`, `_format_svg_string`, `_detect_and_remove_islands`

4. **Deprecated Aliases** (`segnomms/config/models/core.py:307-352`):
   - `reserve_*` → `centerpiece_*` (5 options): Lines 309-324
   - `qr_*` → direct names (6 options): Lines 333-346
   - Currently no deprecation warnings emitted

5. **Phase Documentation Mismatch** (`docs/source/api/config.rst`):
   - Phase 1 labeled "Clustering" → Actually "Enhanced 8-neighbor detection"
   - Phase 2 labeled "Shape Rendering" → Actually "Connected component clustering"
   - Phase 3 labeled "SVG Assembly" → Actually "Marching squares with Bezier curves"

### SegnoMMS Architecture Context

**Multi-Phase Pipeline**: This feature touches documentation and naming but respects the Phase 1-4 architecture
- Phase 1: Configuration & Validation (Pydantic v2 models)
- Phase 2: Matrix Processing & Analysis (QR matrix manipulation)
- Phase 3: Shape Rendering & Geometry (factory pattern with TypedDict **kwargs)
- Phase 4: SVG Assembly & Output (to be renamed CompositionValidator)

**Configuration Management**: Uses established Pydantic v2 patterns
- Deprecation warnings will use Python's standard `warnings` module (not logger)
- Backward compatibility via aliases in `from_kwargs()` method

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**SegnoMMS Constitutional Compliance Verification:**

### Core Principles Compliance
- [x] **Type Safety**: Feature uses Pydantic v2 with strict MyPy compliance, enum objects at runtime
- [x] **Documentation**: User-facing docs planned for Sphinx/RST format only
- [x] **Testing**: Comprehensive coverage planned across unit/integration/documentation test categories
- [x] **Quality Gates**: Implementation will pass pre-commit hooks without `--no-verify`
- [x] **Plugin Architecture**: Maintains backward compatibility with existing Segno plugin API

### Commercial Quality Standards
- [x] **Performance**: No performance impact (naming/documentation changes only)
- [x] **Security**: No security changes; input validation unchanged
- [x] **SVG Output**: No SVG output changes

### Development Workflow Standards
- [x] **Makefile Integration**: Naming audit script will be added to Makefile targets
- [x] **Version Control**: Follows conventional commit format and release practices
- [x] **Spec-Driven**: Aligns with constitutional principles and architecture patterns

**Constitution Version Referenced**: 1.2.0

## Project Structure

### Documentation (this feature)

```text
specs/003-naming-consistency/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
└── tasks.md             # Phase 2 output (from /speckit.tasks)
```

### Source Code Changes

```text
segnomms/
├── validation/
│   └── phase4.py                    # RENAME: Phase4Validator → CompositionValidator
├── config/
│   └── models/
│       └── core.py                  # ADD: deprecation warnings in from_kwargs()
├── plugin/
│   └── __init__.py                  # MODIFY: remove underscore-prefixed from __all__

docs/source/
├── api/
│   └── config.rst                   # FIX: phase descriptions
├── developer/
│   └── naming-conventions.rst       # NEW: naming convention guide
└── migration/
    └── deprecated-options.rst       # NEW: migration guide

tests/
├── unit/
│   └── test_deprecation_warnings.py # NEW: deprecation warning tests
└── integration/
    └── test_backward_compatibility.py # NEW: backward compat tests
```

## Complexity Tracking

No constitution violations requiring justification.

## Implementation Phases

### Phase A: Core Renaming (P1 - User Stories 1 & 2)

1. **Rename Phase4Validator to CompositionValidator**
   - File: `segnomms/validation/phase4.py`
   - Create `Phase4Validator` as deprecated alias
   - Update all internal references
   - Update imports across codebase

2. **Fix Documentation Phase Descriptions**
   - File: `docs/source/api/config.rst`
   - Correct Phase 1-3 descriptions to match implementation
   - Add clear distinction for validation system (formerly Phase 4)

### Phase B: Deprecation Warnings (P2 - User Story 3)

1. **Add Deprecation Warnings for Aliases**
   - File: `segnomms/config/models/core.py`
   - Emit `DeprecationWarning` for `reserve_*` options
   - Emit `DeprecationWarning` for `qr_*` options
   - Handle duplicate option conflict (error if different values)

2. **Create Migration Documentation**
   - File: `docs/source/migration/deprecated-options.rst`
   - List all deprecated options with replacements
   - Include code migration examples

### Phase C: API Cleanup (P3 - User Story 4)

1. **Remove Underscore-Prefixed Exports**
   - File: `segnomms/plugin/__init__.py`
   - Remove 7 private functions from `__all__`
   - Keep internal access unchanged

2. **Document Naming Conventions**
   - File: `docs/source/developer/naming-conventions.rst`
   - Boolean naming guide (bare names for Segno concepts, `*_enabled` for state)
   - Future development guidance

### Phase D: Testing & Validation

1. **Unit Tests for Deprecation Warnings**
   - Test each deprecated option emits warning
   - Test duplicate option conflict raises error
   - Test same-value duplicates only warn

2. **Integration Tests for Backward Compatibility**
   - Test deprecated options still work
   - Test across Segno versions 1.5.2 to 1.6.6

3. **Documentation Validation**
   - Verify phase descriptions match implementation
   - Verify naming convention guide completeness

## Key Files to Modify

| File | Change Type | Priority |
|------|-------------|----------|
| `segnomms/validation/phase4.py` | Rename class | P1 |
| `docs/source/api/config.rst` | Fix descriptions | P1 |
| `segnomms/config/models/core.py` | Add deprecation warnings | P2 |
| `segnomms/plugin/__init__.py` | Remove private exports | P3 |
| `docs/source/developer/naming-conventions.rst` | New file | P3 |
| `docs/source/migration/deprecated-options.rst` | New file | P2 |
| `tests/unit/test_deprecation_warnings.py` | New file | P2 |
| `tests/integration/test_backward_compatibility.py` | New file | P2 |

## Risk Mitigation

1. **Backward Compatibility**: All deprecated names remain functional with warnings
2. **Deprecation Policy**: Pre-1.0.0 allows removal without notice; post-1.0.0 requires N+2 versions or 12 months
3. **Conflict Handling**: Error on conflicting values prevents silent data loss
