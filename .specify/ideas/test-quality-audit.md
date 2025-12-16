# Feature Idea: Test Quality Audit

**Status**: Backlog
**Priority**: Foundation (do first)
**Category**: Quality Assurance

---

## Problem Statement

The test suite has 25,700 LOC (healthy 1.2:1 test-to-code ratio), but we need to verify:

1. Are edge cases covered, not just happy paths?
2. Are all 14 shape renderers tested?
3. Are all 10 intent types tested?
4. Do phase combinations have integration tests?
5. Are failure/degradation paths tested?

## Current State

Key test files:
- `test_svg_builder.py`: 1,181 lines
- `test_scanning_harness.py`: 629 lines
- `test_matrix_manipulator.py`: 505 lines
- `test_intents_processor_logic.py`: 482 lines

## Audit Checklist

| Area | Test File | Status | Notes |
|------|-----------|--------|-------|
| Shape Renderers | `test_shapes_*.py` | TBD | All 14 renderers? |
| Config Validation | `test_config_*.py` | TBD | Edge cases? |
| Intent Processing | `test_intents_processor_logic.py` | 482 LOC | All 10 types? |
| Phase Pipeline | `test_phase*.py` | TBD | Combinations? |
| Degradation | `test_degradation_*.py` | TBD | Fallback paths? |
| Accessibility | `test_accessibility_core.py` | TBD | WCAG compliance? |
| Connected Shapes | TBD | TBD | Neighbor-state tests? |
| Factory Pattern | TBD | TBD | Unknown shape fallback? |

## Specific Investigations

### 1. Coverage Numbers
```bash
pytest --cov=segnomms --cov-report=html tests/
```
Get actual line coverage, branch coverage, and identify untested paths.

### 2. Shape Renderer Testing
Check if `connected` shape renderers have tests for:
- 0 neighbors (isolated)
- 1 neighbor (terminal)
- 2 neighbors - corner case
- 2 neighbors - straight line case
- 3+ neighbors (junction)

### 3. Phase Auto-Enable Logic
Verify tests exist for magic thresholds in `RenderingConfig.from_kwargs()`:
- `size_ratio = 0.9`
- `min_cluster_size = 3`
- `corner_radius > 0` triggers Phase 1

### 4. Degradation Manager
Check tests for each incompatibility type and fallback behavior.

### 5. Intent Processor
Verify all 10 intent types have dedicated tests:
1. Style intents
2. Frame intents
3. Reserve intents
4. Accessibility intents
5. Validation intents
6. Interactivity intents
7. Animation intents
8. Performance intents
9. Branding intents
10. Advanced intents

## Files to Review

- `tests/unit/test_intents_processor_logic.py`
- `tests/unit/test_edge_cases_critical_algorithms.py`
- `tests/unit/test_property_based.py`
- `tests/visual/test_visual_regression_png.py`

## Success Criteria

- >90% line coverage documented
- All 14 shape renderers have tests
- All 10 intent types have tests
- Edge cases identified and documented (even if not all implemented)
- Gap analysis document produced

## Deliverables

1. Coverage report (HTML)
2. Gap analysis document listing missing test cases
3. Prioritized list of tests to add
4. Issues/tickets for critical gaps

---

## Notes

*Add audit findings, coverage numbers, and gap analysis here as work progresses*

### Coverage Results
*Run `pytest --cov` and record results here*

### Identified Gaps
*List specific untested scenarios*

### Priority Additions
*List tests to add in priority order*
