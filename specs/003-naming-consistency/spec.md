# Feature Specification: Project Naming Consistency Review

**Feature Branch**: `003-naming-consistency`
**Created**: 2025-12-27
**Status**: Draft
**Input**: Standardize naming patterns across SegnoMMS configuration options to improve developer experience and API learnability.

## Clarifications

### Session 2025-12-28

- Q: Phase 4 disambiguation approach? → A: Rename Phase 4 to "CompositionValidator" (or similar) with deprecation alias for backward compatibility
- Q: Conflict resolution for duplicate options? → A: Error on conflict - raise configuration error if both deprecated and current names provided with different values; warn if same value
- Q: Deprecation timeline? → A: Version N+2 OR 12 months (whichever later) for post-1.0.0; pre-1.0.0 has no backward compatibility guarantee and deprecated items may be removed without notice

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Learning Boolean Configuration Options (Priority: P1)

A developer new to SegnoMMS wants to configure boolean options for their QR code generation. Currently, they encounter five different naming patterns (`enable_*`, `use_*`, `*_enabled`, bare booleans, `add_*/include_*`) and cannot predict which pattern any given option uses.

**Why this priority**: Boolean options are the most frequently used configuration surface. Inconsistent naming directly impacts every user's first experience with the library.

**Independent Test**: Can be fully tested by auditing all boolean options and verifying they follow the standardized naming convention. Delivers immediate improvement to API discoverability.

**Acceptance Scenarios**:

1. **Given** a developer reading the configuration documentation, **When** they look for a boolean option to enable a feature, **Then** they can predict the option name based on a consistent pattern
2. **Given** a developer familiar with Segno upstream, **When** they use SegnoMMS, **Then** inherited concepts use naming patterns consistent with Segno (bare names)
3. **Given** a developer using IDE autocompletion, **When** they type a feature name, **Then** related boolean options appear with consistent prefixes/suffixes

---

### User Story 2 - Understanding Phase Terminology (Priority: P1)

A developer reads about "phases" in SegnoMMS documentation and becomes confused because Phase 1-3 are optional processing features they can enable/disable, while Phase 4 is actually a validation system with a completely different purpose.

**Why this priority**: Phase terminology appears throughout documentation and code. The conceptual mismatch between "processing phases" and "validation phase" causes fundamental confusion about how the library works.

**Independent Test**: Can be fully tested by reviewing documentation and verifying Phase 4 is clearly distinguished from Phases 1-3, either through renaming or explicit documentation that Phase 4 serves a different purpose.

**Acceptance Scenarios**:

1. **Given** a developer reading phase documentation, **When** they encounter Phase 4, **Then** they immediately understand it is a validation system, not a processing step
2. **Given** a developer configuring phases, **When** they enable Phase 1-3, **Then** they understand these are optional rendering optimizations
3. **Given** the documentation for `docs/source/api/config.rst`, **When** a developer reads the phase descriptions, **Then** each description accurately matches what the phase actually does

---

### User Story 3 - Migrating from Deprecated Options (Priority: P2)

A developer using older SegnoMMS code with `reserve_*` options wants to update to current best practices. They discover both `reserve_*` and `centerpiece_*` options work, but documentation doesn't clearly indicate which to use.

**Why this priority**: Deprecated aliases create maintenance burden and confusion. Clear migration guidance prevents new users from adopting deprecated patterns.

**Independent Test**: Can be fully tested by verifying deprecated options emit warnings and documentation clearly indicates preferred option names.

**Acceptance Scenarios**:

1. **Given** a developer using `reserve_*` options, **When** they run their code, **Then** they receive a deprecation warning pointing to the `centerpiece_*` equivalent
2. **Given** a developer reading configuration documentation, **When** they look for centerpiece/logo options, **Then** only the current `centerpiece_*` names are prominently documented
3. **Given** code using deprecated option names, **When** the developer searches documentation, **Then** they find clear migration instructions

---

### User Story 4 - Understanding Public API Boundaries (Priority: P3)

A developer importing from `segnomms.plugin` sees functions with underscore prefixes (e.g., `_export_configuration`) in `__all__`, which contradicts Python convention that underscore-prefixed names are private.

**Why this priority**: While this affects fewer users than configuration naming, it creates confusion about API stability guarantees and what is safe to use.

**Independent Test**: Can be fully tested by auditing `__all__` exports and verifying no underscore-prefixed functions are publicly exported.

**Acceptance Scenarios**:

1. **Given** a developer importing from `segnomms.plugin`, **When** they use IDE autocompletion, **Then** only properly public functions (without underscore prefix) appear
2. **Given** a developer checking `__all__` in plugin module, **When** they review the exports, **Then** all exported names follow public naming conventions

---

### Edge Cases

- **Duplicate option conflict**: When a user provides both deprecated and current option names for the same setting with different values, system MUST raise a configuration error. If values match, emit deprecation warning only.
- **Deprecation period handling**: Existing code using deprecated names (including `enable_*` if deprecated) continues to work with warnings; post-1.0.0 aliases preserved for N+2 versions or 12 months; pre-1.0.0 may remove without notice.
- **Documentation mismatch**: Phase descriptions that don't match implementation MUST be corrected as part of this feature (FR-001).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Documentation MUST accurately describe what each processing phase (1-3) does, matching actual implementation
- **FR-002**: Phase 4 MUST be renamed (e.g., `CompositionValidator`) and clearly distinguished from Phases 1-3 in all documentation, indicating it is a validation system rather than a processing step; the old "Phase4Validator" name MUST remain as a deprecated alias
- **FR-003**: Boolean configuration options MUST follow a consistent naming convention documented in a style guide
- **FR-004**: Deprecated option names (`reserve_*`, `qr_*`) MUST emit deprecation warnings when used
- **FR-005**: The `segnomms.plugin` module MUST NOT export underscore-prefixed functions in `__all__`
- **FR-006**: Configuration documentation MUST include a naming convention reference for developers extending the library
- **FR-007**: All boolean options MUST be auditable against the naming convention via automated tooling
- **FR-008**: When both deprecated and current option names are provided for the same setting, system MUST raise a configuration error if values differ; if values match, emit deprecation warning only

### Key Entities

- **Configuration Option**: A user-facing setting with a name, type, default value, and description. Boolean options are the primary focus.
- **Processing Phase (1-3)**: Optional rendering optimization features that can be enabled/disabled
- **Validation System (Phase 4)**: SVG assembly and validation functionality, conceptually distinct from processing phases
- **Deprecated Alias**: An old option name that still works but should be migrated to a newer name

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of boolean configuration options follow the documented naming convention
- **SC-002**: Developers can correctly identify whether an option uses `*_enabled`, bare name, or other pattern based on the naming guide 90% of the time (validated through user testing or documentation review)
- **SC-003**: Phase documentation descriptions match actual implementation behavior for all 4 phases
- **SC-004**: Zero underscore-prefixed functions appear in public `__all__` exports
- **SC-005**: All deprecated option names emit warnings when used, with 100% coverage
- **SC-006**: New users can configure basic options correctly on first attempt (qualitative feedback from documentation review)

## SegnoMMS Integration Requirements *(mandatory for SegnoMMS features)*

### Plugin Architecture Compliance
- Feature MUST maintain backward compatibility with existing Segno plugin API
- Configuration changes MUST preserve existing kwargs API patterns (deprecated options continue to work with warnings)
- Naming convention changes MUST NOT break existing user code during deprecation period

### Type Safety Requirements
- All configuration models MUST use Pydantic v2 with strict MyPy compliance
- Deprecation warnings MUST be properly typed
- Enum objects at runtime (no `use_enum_values=True`)

### Testing Requirements
- MUST include comprehensive test coverage across all categories:
  - Unit tests for deprecation warning emission
  - Integration tests for backward compatibility with deprecated names
  - Documentation tests validating phase descriptions match implementation
- Backward compatibility testing across Segno versions 1.5.2 to 1.6.6

### Documentation Requirements
- User-facing documentation MUST be written in Sphinx/RST format
- Naming convention guide MUST be added to developer documentation
- Phase descriptions in `docs/source/api/config.rst` MUST be corrected
- Migration guide for deprecated options MUST be provided

### Quality Gates
- MUST pass all pre-commit hooks without `--no-verify`
- MyPy type checking with zero errors for new code
- All phase descriptions validated against implementation

### Commercial Standards
- Professional documentation with clear, accurate descriptions
- Backward compatibility maintained for commercial users
- Clear deprecation timeline communicated

## Assumptions *(document reasonable defaults)*

### Technology Assumptions
- Uses established SegnoMMS technology stack
- Follows existing Pydantic v2 + MyPy patterns
- Integrates with current testing framework and CI/CD pipeline
- Respects existing documentation policy (Sphinx-first)

### Architecture Assumptions
- Boolean naming convention follows hybrid approach: bare names for Segno-inherited concepts, `*_enabled` suffix for state booleans
- Deprecation warnings use Python's standard `warnings` module
- Phase 4 WILL be renamed to `CompositionValidator` (or similar validation-focused name) with a deprecation alias preserving backward compatibility

### Quality Assumptions
- Maintains >90% test coverage standard
- All documentation changes validated for accuracy
- **Deprecation policy**: Post-1.0.0 releases preserve deprecated aliases for N+2 versions OR 12 months (whichever is later); pre-1.0.0 releases have no backward compatibility guarantee and may remove deprecated items without notice

### Scope Assumptions
- This specification covers naming consistency improvements only
- Actual removal of deprecated options is out of scope (deprecation warnings only)
- Internal-only naming (non-user-facing) is out of scope unless it leaks into public API
