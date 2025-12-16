# Feature Idea: Split IntentProcessor Monolith

**Status**: Backlog
**Priority**: High Impact, Moderate Effort
**Category**: Refactoring

---

## Problem Statement

`segnomms/intents/processor.py` is 2,007 lines - a monolithic file handling 10+ intent types, QR generation, degradation, validation, and metrics. This violates single-responsibility and makes the codebase harder to navigate and test.

## Current Structure

```
IntentProcessor class (lines 46-2007):
├── process_intents()           # Main orchestrator (lines 58-184)
├── _process_all_intents()      # Intent router (lines 186-271)
├── _process_accessibility_intents()  (lines 273-344)
├── _process_validation_intents()
├── _process_interactivity_intents()
├── _process_animation_intents()
├── _process_performance_intents()
├── _process_branding_intents()
├── _process_advanced_intents()
├── process_style_intents()           # Public (style)
├── process_frame_intents()           # Public (frame)
├── process_reserve_intents()         # Public (reserve)
├── _track_transformation()           # Tracking helpers
├── _add_warning()
├── _add_compatibility_info()
├── _calculate_metrics()
├── _build_translation_report()
└── ... (20+ more helper methods)
```

## Proposed Solution

Split into 5-7 focused modules:

| New File | Content | Est. LOC |
|----------|---------|----------|
| `intents/processor.py` | `IntentProcessor` orchestrator only | ~300 |
| `intents/style_processor.py` | `process_style_intents()` + helpers | ~350 |
| `intents/frame_processor.py` | `process_frame_intents()`, `process_reserve_intents()` | ~250 |
| `intents/advanced_processor.py` | Advanced, animation, performance, branding | ~400 |
| `intents/accessibility_processor.py` | Accessibility, validation intents | ~250 |
| `intents/tracking.py` | `_track_transformation`, `_add_warning`, etc. | ~200 |
| `intents/metrics.py` | `_calculate_metrics`, `_build_translation_report` | ~200 |

## Implementation Steps

1. Create `intents/tracking.py` with mixin class for transformation tracking
2. Create `intents/metrics.py` with metrics calculation logic
3. Extract each intent type processor to dedicated file
4. Update `IntentProcessor` to compose from sub-processors
5. Update imports in dependent modules
6. Add tests for sub-processor interfaces

## Files to Modify

- `segnomms/intents/processor.py` (refactor)
- `segnomms/intents/__init__.py` (update exports)
- `tests/unit/test_intents_processor_logic.py` (update)

## Success Criteria

- No file > 500 LOC
- Each module has single responsibility
- All existing tests pass
- No change to public API

## Dependencies

- Should complete BACKLOG 3 (Test Quality Audit) first to establish baseline

---

## Notes

*Add implementation notes, decisions, and learnings here as work progresses*
