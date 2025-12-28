# Tasks: Project Naming Consistency Review

**Input**: Design documents from `/specs/003-naming-consistency/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: Included per spec requirement for comprehensive test coverage

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Source code**: `segnomms/` at repository root
- **Tests**: `tests/` at repository root
- **Documentation**: `docs/source/` (Sphinx RST format)

---

## Phase 1: Setup

**Purpose**: Verify prerequisites and prepare for implementation

- [ ] T001 Verify current branch is `003-naming-consistency` and working tree is clean
- [ ] T002 [P] Review existing imports of `Phase4Validator` across codebase with `grep -r "Phase4Validator" segnomms/`
- [ ] T003 [P] Review existing `__all__` contents in segnomms/plugin/__init__.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Import statement for warnings module needed by multiple user stories

**⚠️ CRITICAL**: This phase provides shared infrastructure for deprecation warnings

- [ ] T004 Add `import warnings` to segnomms/config/models/core.py (if not already present)
- [ ] T005 Verify existing test infrastructure supports `pytest.warns()` pattern

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Learning Boolean Configuration Options (Priority: P1) 🎯 MVP

**Goal**: Document boolean naming conventions so developers can predict option names

**Independent Test**: Verify naming convention guide exists and is complete by reviewing docs/source/developer/naming-conventions.rst

### Implementation for User Story 1

- [ ] T006 [US1] Create docs/source/developer/ directory if it doesn't exist
- [ ] T007 [US1] Create naming convention guide in docs/source/developer/naming-conventions.rst with:
  - Bare name pattern (Segno-inherited: `eci`, `boost_error`)
  - `*_enabled` suffix pattern (state booleans: `centerpiece_enabled`)
  - `use_*` prefix pattern (strategy selection: `use_marching_squares`)
  - Bare name pattern for UI behaviors (`interactive`, `tooltips`)
  - Deprecated `enable_*` pattern note
- [ ] T008 [US1] Add naming-conventions to docs/source/index.rst toctree
- [ ] T009 [US1] Build docs with `make docs` to verify RST syntax is valid
- [ ] T009a [US1] Create naming audit script in repo/audit_boolean_naming.py that:
  - Scans all Pydantic config models for boolean fields
  - Checks each field name against documented convention patterns
  - Reports violations with file:line references
  - Returns non-zero exit code if violations found
- [ ] T009b [US1] Add `audit-naming` target to Makefile for discoverability
- [ ] T009c [US1] Run audit script to verify current codebase (document known exceptions)

**Checkpoint**: User Story 1 complete - developers can now reference naming conventions

---

## Phase 4: User Story 2 - Understanding Phase Terminology (Priority: P1)

**Goal**: Rename Phase4Validator to CompositionValidator and fix documentation to distinguish validation from processing phases

**Independent Test**: Verify `from segnomms.validation.phase4 import CompositionValidator` works and Phase4Validator still works with deprecation warning

### Tests for User Story 2

- [ ] T010 [P] [US2] Create test for Phase4Validator deprecation alias in tests/unit/test_composition_validator.py:
  - Test `CompositionValidator` can be imported and instantiated
  - Test `Phase4Validator` still works as alias
  - Test deprecation warning emitted when using `Phase4Validator`

### Implementation for User Story 2

- [ ] T011 [US2] Rename class `Phase4Validator` to `CompositionValidator` in segnomms/validation/phase4.py:31-46
- [ ] T012 [US2] Add backward-compatible alias in segnomms/validation/phase4.py:
  - After class definition: `Phase4Validator = CompositionValidator`
  - This allows existing `from segnomms.validation.phase4 import Phase4Validator` to work
  - Note: Direct alias does NOT emit warning; warning handled by `__getattr__` in `__init__.py`
- [ ] T013 [US2] Add deprecation warning in segnomms/validation/__init__.py using `__getattr__`:
  ```python
  def __getattr__(name: str):
      if name == "Phase4Validator":
          import warnings
          warnings.warn(
              "Phase4Validator is deprecated, use CompositionValidator instead. "
              "Phase4Validator will be removed in a future version.",
              DeprecationWarning,
              stacklevel=2
          )
          from segnomms.validation.phase4 import CompositionValidator
          return CompositionValidator
      raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
  ```
  - This emits warning when importing via `from segnomms.validation import Phase4Validator`
- [ ] T014 [P] [US2] Update all internal imports from `Phase4Validator` to `CompositionValidator` across segnomms/
- [ ] T015 [US2] Update docstring in segnomms/validation/phase4.py to reflect new class name and purpose
- [ ] T016 [US2] Fix Phase 1 description in docs/source/api/config.rst from "Clustering" to "Enhanced 8-neighbor context detection for context-aware shape selection"
- [ ] T017 [US2] Fix Phase 2 description in docs/source/api/config.rst from "Shape Rendering" to "Connected component clustering for unified module group rendering"
- [ ] T018 [US2] Fix Phase 3 description in docs/source/api/config.rst from "SVG Assembly" to "Marching squares algorithm with Bezier curve smoothing for organic contours"
- [ ] T019 [US2] Add CompositionValidator section to docs/source/api/config.rst clearly stating it's a validation system, not a processing phase
- [ ] T020 [US2] Run `make docs` to verify documentation builds without errors
- [ ] T021 [US2] Run tests with `pytest tests/unit/test_composition_validator.py -v` to verify rename works

**Checkpoint**: User Story 2 complete - Phase terminology is now clear and consistent

---

## Phase 5: User Story 3 - Migrating from Deprecated Options (Priority: P2)

**Goal**: Add deprecation warnings for `reserve_*` and `qr_*` option aliases so developers receive clear migration guidance

**Independent Test**: Verify using deprecated options emits warnings and conflict detection works

### Tests for User Story 3

- [ ] T022 [P] [US3] Create test file tests/unit/test_deprecation_warnings.py with:
  - Test each `reserve_*` option emits DeprecationWarning
  - Test each `qr_*` option emits DeprecationWarning
  - Test conflict detection raises ValueError for different values
  - Test same-value duplicates only emit warning (no error)
- [ ] T023 [P] [US3] Create integration test tests/integration/test_backward_compatibility.py:
  - Test deprecated options still produce correct QR output
  - Test mixed deprecated/current options work when values match

### Implementation for User Story 3

- [ ] T024 [US3] Define `DEPRECATED_CENTERPIECE_OPTIONS` mapping dict in segnomms/config/models/core.py:
  ```python
  DEPRECATED_CENTERPIECE_OPTIONS = {
      "reserve_center": "centerpiece_enabled",
      "reserve_shape": "centerpiece_shape",
      "reserve_size": "centerpiece_size",
      "reserve_offset_x": "centerpiece_offset_x",
      "reserve_offset_y": "centerpiece_offset_y",
      "reserve_margin": "centerpiece_margin",
  }
  ```
- [ ] T025 [US3] Define `DEPRECATED_QR_OPTIONS` mapping dict in segnomms/config/models/core.py:
  ```python
  DEPRECATED_QR_OPTIONS = {
      "qr_eci": "eci",  # Bare name for Segno-inherited concept
      "qr_encoding": "encoding",
      "qr_mask": "mask_pattern",
      "qr_symbol_count": "symbol_count",
      "qr_boost_error": "boost_error",
      "multi_symbol": "structured_append",
  }
  ```
- [ ] T026 [US3] Create helper function `_handle_deprecated_options(kwargs, mappings)` in segnomms/config/models/core.py that:
  - Iterates through deprecated mappings
  - Emits `warnings.warn()` with `DeprecationWarning` and `stacklevel=2`
  - Raises `ValueError` if both deprecated and current provided with different values
  - Warns if both provided with same value
  - Maps deprecated to current name in kwargs
- [ ] T027 [US3] Call `_handle_deprecated_options()` at start of `from_kwargs()` in segnomms/config/models/core.py for both mapping dicts
- [ ] T028 [US3] Create migration guide docs/source/migration/ directory
- [ ] T029 [US3] Create docs/source/migration/deprecated-options.rst with:
  - Full table of deprecated → current mappings
  - Code examples showing migration
  - Conflict handling explanation
  - Deprecation policy reference (pre-1.0.0 vs post-1.0.0)
- [ ] T030 [US3] Add migration guide to docs/source/index.rst toctree
- [ ] T031 [US3] Run `pytest tests/unit/test_deprecation_warnings.py -v` to verify warnings work
- [ ] T032 [US3] Run `pytest tests/integration/test_backward_compatibility.py -v` to verify backward compat

**Checkpoint**: User Story 3 complete - deprecated options now emit clear warnings

---

## Phase 6: User Story 4 - Understanding Public API Boundaries (Priority: P3)

**Goal**: Remove underscore-prefixed functions from `__all__` so public API is clearly defined

**Independent Test**: Verify `from segnomms.plugin import *` only imports public functions (no underscore-prefixed)

### Tests for User Story 4

- [ ] T033 [P] [US4] Create test in tests/unit/test_plugin_exports.py:
  - Test `__all__` contains only public names (no underscore prefix)
  - Test star import works and only exposes public API
  - Test internal functions still accessible via direct import

### Implementation for User Story 4

- [ ] T034 [US4] Remove `_export_configuration` from `__all__` in segnomms/plugin/__init__.py
- [ ] T035 [US4] Remove `_generate_config_hash` from `__all__` in segnomms/plugin/__init__.py
- [ ] T036 [US4] Remove `_get_pattern_specific_style` from `__all__` in segnomms/plugin/__init__.py
- [ ] T037 [US4] Remove `_get_pattern_specific_render_kwargs` from `__all__` in segnomms/plugin/__init__.py
- [ ] T038 [US4] Remove `_render_cluster` from `__all__` in segnomms/plugin/__init__.py
- [ ] T039 [US4] Remove `_get_enhanced_render_kwargs` from `__all__` in segnomms/plugin/__init__.py
- [ ] T040 [US4] Remove `_format_svg_string` from `__all__` in segnomms/plugin/__init__.py
- [ ] T041 [US4] Remove `_detect_and_remove_islands` from `__all__` in segnomms/plugin/__init__.py
- [ ] T042 [US4] Verify `__all__` now contains only: `write`, `write_advanced`, `register_with_segno`, `generate_interactive_svg`, `MAX_QR_SIZE`
- [ ] T043 [US4] Run `pytest tests/unit/test_plugin_exports.py -v` to verify exports are correct

**Checkpoint**: User Story 4 complete - public API boundaries are now clear

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and cleanup

- [ ] T044 Run full test suite with `pytest tests/ -v` to ensure no regressions
- [ ] T045 Run MyPy type checking with `mypy segnomms/` to verify type safety
- [ ] T046 Run pre-commit hooks with `pre-commit run --all-files` to verify formatting
- [ ] T047 Build documentation with `make docs` and verify all new pages render correctly
- [ ] T048 Review all changes with `git diff` before committing
- [ ] T049 Create commit with conventional commit format: `refactor(naming): standardize naming conventions and add deprecation warnings`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User stories can proceed in priority order (P1 → P1 → P2 → P3)
  - US1 and US2 are both P1 and can run in parallel if desired
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Documentation only - no code dependencies
- **User Story 2 (P1)**: Class rename - independent of other stories
- **User Story 3 (P2)**: Deprecation warnings - independent of US1/US2
- **User Story 4 (P3)**: API cleanup - independent of other stories

### Within Each User Story

- Tests written first (where applicable)
- Implementation follows tests
- Documentation updates after implementation
- Verification step at end of each story

### Parallel Opportunities

**Within Phase 1 (Setup)**:
```
T002 and T003 can run in parallel
```

**Within Phase 4 (User Story 2)**:
```
T010 (test) and T014 (import updates) can run in parallel
```

**Within Phase 5 (User Story 3)**:
```
T022 (unit test) and T023 (integration test) can run in parallel
```

**Across User Stories** (if team capacity allows):
```
US1 (documentation) and US2 (class rename) can run in parallel
US3 (deprecation) and US4 (API cleanup) can run in parallel after US1/US2
```

---

## Implementation Strategy

### MVP First (User Stories 1 & 2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1 (naming convention docs)
4. Complete Phase 4: User Story 2 (Phase4Validator rename)
5. **STOP and VALIDATE**: Test that naming is now consistent and documented
6. Deploy/demo if ready

### Full Implementation

1. Complete Setup + Foundational
2. User Story 1 → Naming conventions documented
3. User Story 2 → Phase terminology fixed
4. User Story 3 → Deprecation warnings active
5. User Story 4 → API boundaries clean
6. Polish → All tests pass, docs build, ready to merge

### Incremental Delivery

Each user story adds value independently:
- **After US1**: Developers have naming guide
- **After US2**: Phase confusion eliminated
- **After US3**: Migration path clear with warnings
- **After US4**: Public API clearly defined

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story is independently completable and testable
- Verify tests fail before implementing (TDD approach for test tasks)
- Commit after each phase or logical group
- Stop at any checkpoint to validate story independently
- All documentation is Sphinx/RST format per constitution
- All code changes must pass pre-commit hooks
