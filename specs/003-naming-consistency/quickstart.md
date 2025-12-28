# Quickstart: Project Naming Consistency Review

**Feature**: 003-naming-consistency
**Date**: 2025-12-28

## Overview

This feature improves naming consistency across SegnoMMS. After implementation:
- Phase4Validator becomes CompositionValidator
- Deprecated option names emit warnings
- Private functions are no longer publicly exported
- Documentation accurately describes phases

## For Users

### Deprecation Warnings

If you see deprecation warnings, update your code:

**Centerpiece Options**:
```python
# Old (deprecated)
qr.save("output.svg", kind="svg",
        reserve_center=True,
        reserve_size=0.3)

# New (recommended)
qr.save("output.svg", kind="svg",
        centerpiece_enabled=True,
        centerpiece_size=0.3)
```

**QR Advanced Options**:
```python
# Old (deprecated)
qr.save("output.svg", kind="svg",
        qr_eci=True,
        qr_mask=3)

# New (recommended)
qr.save("output.svg", kind="svg",
        eci=True,
        mask_pattern=3)
```

### Full Migration Table

| Deprecated | Use Instead |
|------------|-------------|
| `reserve_center` | `centerpiece_enabled` |
| `reserve_shape` | `centerpiece_shape` |
| `reserve_size` | `centerpiece_size` |
| `reserve_offset_x` | `centerpiece_offset_x` |
| `reserve_offset_y` | `centerpiece_offset_y` |
| `reserve_margin` | `centerpiece_margin` |
| `qr_eci` | `eci_enabled` |
| `qr_encoding` | `encoding` |
| `qr_mask` | `mask_pattern` |
| `qr_symbol_count` | `symbol_count` |
| `qr_boost_error` | `boost_error` |
| `multi_symbol` | `structured_append` |

### Conflict Handling

If you accidentally provide both old and new names with different values, you'll get an error:

```python
# This raises ValueError
qr.save("output.svg", kind="svg",
        reserve_size=0.3,
        centerpiece_size=0.4)  # Conflicting values!

# This only warns (same value)
qr.save("output.svg", kind="svg",
        reserve_size=0.3,
        centerpiece_size=0.3)  # Redundant but allowed
```

---

## For Developers

### Using CompositionValidator

```python
# New import (recommended)
from segnomms.validation.phase4 import CompositionValidator

# Old import (still works, emits warning)
from segnomms.validation.phase4 import Phase4Validator

# Usage unchanged
validator = CompositionValidator(config)
result = validator.validate_all()
```

### Boolean Naming Convention

When adding new boolean options, follow this convention:

| Pattern | When to Use | Example |
|---------|-------------|---------|
| Bare name | Segno-inherited concepts | `eci`, `boost_error` |
| `*_enabled` | State booleans | `centerpiece_enabled` |
| `use_*` | Algorithm selection | `use_marching_squares` |
| Bare name | UI behaviors | `interactive`, `tooltips` |

**Avoid**: `enable_*` prefix (deprecated pattern)

### Adding Deprecation Warnings

If you need to deprecate an option:

```python
import warnings

def from_kwargs(cls, **kwargs):
    if "old_option" in kwargs:
        warnings.warn(
            "Option 'old_option' is deprecated, use 'new_option' instead. "
            "This option will be removed in a future version.",
            DeprecationWarning,
            stacklevel=2
        )
        # Handle value mapping
        if "new_option" not in kwargs:
            kwargs["new_option"] = kwargs.pop("old_option")
        else:
            # Conflict detection
            if kwargs["old_option"] != kwargs["new_option"]:
                raise ValueError(
                    f"Conflicting values for 'old_option' and 'new_option'"
                )
            kwargs.pop("old_option")
```

### Testing Deprecation Warnings

```python
import pytest
import warnings

def test_deprecated_option_warns():
    with pytest.warns(DeprecationWarning, match="reserve_center"):
        config = PluginConfig.from_kwargs(reserve_center=True)

def test_conflicting_options_error():
    with pytest.raises(ValueError, match="Conflicting"):
        PluginConfig.from_kwargs(
            reserve_size=0.3,
            centerpiece_size=0.4
        )
```

---

## Quick Reference

### Key Files

| File | Purpose |
|------|---------|
| `segnomms/validation/phase4.py` | CompositionValidator (formerly Phase4Validator) |
| `segnomms/config/models/core.py` | Deprecation warning logic |
| `segnomms/plugin/__init__.py` | Public API exports |
| `docs/source/api/config.rst` | Phase documentation |

### Deprecation Policy

- **Pre-1.0.0**: Deprecated items may be removed without notice
- **Post-1.0.0**: Deprecated items preserved for N+2 versions OR 12 months (whichever is later)

### Phase Descriptions (Corrected)

| Phase | What It Does |
|-------|--------------|
| Phase 1 | Enhanced 8-neighbor context detection for shape selection |
| Phase 2 | Connected component clustering for unified rendering |
| Phase 3 | Marching squares with Bezier curves for smooth contours |
| CompositionValidator | Validates frames, centerpieces, and feature interactions |
