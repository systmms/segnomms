# Feature Idea: Refactor PatternStyleConfig

**Status**: Backlog
**Priority**: High Impact, Moderate Effort
**Category**: Refactoring

---

## Problem Statement

`PatternStyleConfig` in `segnomms/config/models/visual.py:15-153` has 28 fields following a repetitive `{pattern}_{attribute}` pattern. This creates:

- Maintenance burden (7 patterns × 4 attributes = 28 fields)
- Validator complexity (must enumerate all 28 fields)
- No extensibility (adding a new attribute requires touching 7+ places)

## Current State

```python
class PatternStyleConfig(BaseModel):
    finder: Optional[str]           # 7 pattern types
    finder_color: Optional[str]     # × 4 attribute types
    finder_scale: Optional[float]   # = 28 fields
    finder_effects: Optional[Dict]
    timing: Optional[str]           # Same pattern repeated
    timing_color: Optional[str]
    timing_scale: Optional[float]
    timing_effects: Optional[Dict]
    alignment: Optional[str]
    alignment_color: Optional[str]
    # ... 18 more fields
```

Validators at lines 77-152 manually enumerate all 28 fields twice.

## Proposed Solution

```python
class PatternOverride(BaseModel):
    """Configuration for a single pattern type."""
    shape: Optional[str] = None
    color: Optional[str] = None
    scale: Optional[float] = Field(default=None, ge=0.1, le=2.0)
    effects: Optional[Dict[str, Any]] = None

class PatternStyleConfig(BaseModel):
    """Pattern-specific styling configuration."""
    enabled: bool = False
    overrides: Dict[str, PatternOverride] = Field(
        default_factory=dict,
        description="Pattern overrides keyed by pattern type"
    )

    @field_validator("overrides")
    def validate_pattern_types(cls, v):
        valid_patterns = {"finder", "finder_inner", "timing", "alignment", "format", "version", "data"}
        invalid = set(v.keys()) - valid_patterns
        if invalid:
            raise ValueError(f"Invalid pattern types: {invalid}")
        return v
```

## Benefits

- **Extensible**: Add new attributes without touching field list
- **DRY**: Single validator, not 28-field enumeration
- **API clarity**: `config.patterns.overrides["finder"].color` is explicit
- **Future-proof**: Easy to add new pattern types or attributes

## Migration Path

1. Add new `PatternOverride` model alongside existing fields
2. Add `from_legacy()` classmethod for backward compatibility
3. Update `from_kwargs()` to handle both formats
4. Deprecate old field names with warnings
5. Update tests to use new format
6. Remove deprecated fields in future version

## Files to Modify

- `segnomms/config/models/visual.py` (primary)
- `segnomms/config/models/core.py` (from_kwargs mappings)
- `tests/unit/test_config_visual.py` (update tests)

## Success Criteria

- < 50 total config fields (down from 28 for patterns alone)
- Single validator for pattern types
- Backward compatibility maintained during transition
- All existing tests pass

## API Comparison

**Before (flat fields):**
```python
config = RenderingConfig(
    patterns=PatternStyleConfig(
        enabled=True,
        finder="circle",
        finder_color="#ff0000",
        timing="dot",
        timing_scale=0.8,
    )
)
```

**After (dict-based):**
```python
config = RenderingConfig(
    patterns=PatternStyleConfig(
        enabled=True,
        overrides={
            "finder": PatternOverride(shape="circle", color="#ff0000"),
            "timing": PatternOverride(shape="dot", scale=0.8),
        }
    )
)
```

---

## Notes

*Add implementation notes, decisions, and learnings here as work progresses*
