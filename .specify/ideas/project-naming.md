# Feature Idea: Project Naming Consistency Review

**Status**: Backlog
**Priority**: Medium Impact, Low-Medium Effort
**Category**: Developer Experience / API Design

---

## Problem Statement

Several naming patterns in SegnoMMS may confuse users of this open source library. Terminology is overloaded (e.g., "phase" means different things in different contexts), documentation doesn't match implementation, and naming conventions may not be intuitive for new users.

## Known Issues

### 1. Phase Terminology Overload

The term "phase" is used for three distinct concepts:

| Concept | What It Is | User-Facing? |
|---------|-----------|--------------|
| **Processing Phases 1-3** | Optional rendering optimization features (neighbor analysis, clustering, marching squares) | Yes - config kwargs |
| **Phase 4** | Validation system for frames/centerpieces | Yes - validator class |
| **Architecture Phases** | Conceptual pipeline stages in dev docs | No - internal only |

**Specific Problems:**

1. **Phase 4 is conceptually different** - Phases 1-3 are processing features you enable/disable. Phase 4 is a validation system, not a processing step.

2. **Documentation mismatch** - `docs/source/api/config.rst` (lines 121-145) describes phases incorrectly:
   - Phase 1 labeled "Clustering" -> Actually "Enhanced 8-neighbor detection"
   - Phase 2 labeled "Shape Rendering" -> Actually "Connected component clustering"
   - Phase 3 labeled "SVG Assembly" -> Actually "Marching squares with Bezier curves"

3. **Hidden auto-enablement** - Phases auto-enable based on config settings, which may surprise users.

**Key Files:**
- `segnomms/config/models/phases.py` - Phase 1-3 config definitions
- `segnomms/validation/phase4.py` - Phase 4 validator
- `segnomms/config/models/core.py` - Phase integration, kwargs parsing (lines 271-289, 498-530)
- `docs/source/api/config.rst` - User-facing docs with incorrect descriptions

### 2. Config Option Naming - AUDIT COMPLETE

**Total: ~127 user-facing configuration fields**

#### Boolean Prefix Inconsistency (Critical Issue)

| Pattern | Count | Examples |
|---------|-------|----------|
| `enable_*` | 17 | `enable_phase1`, `enable_aria`, `enable_palette_validation` |
| `use_*` | 4 | `use_enhanced_shapes`, `use_cluster_rendering`, `use_marching_squares` |
| `*_enabled` suffix | 7 | `eci_enabled`, `centerpiece_enabled`, `patterns_enabled` |
| Bare boolean (no prefix) | 5 | `interactive`, `tooltips`, `boost_error`, `auto_mask` |
| Other (`add_*`, `include_*`) | 5 | `add_structural_markup`, `include_module_labels` |

**Problem:** Five different patterns for boolean options makes API hard to learn.

#### Duplicate/Alias Options (Maintenance Burden)

| Old Name | New Name | Issue |
|----------|----------|-------|
| `reserve_*` (5 options) | `centerpiece_*` | Both work, creates confusion |
| `qr_*` (6 options) | Direct names | `qr_eci`/`eci_enabled`, `qr_mask`/`mask_pattern` |
| `enable_phase1` | `phase1.enabled` | Two ways to enable same feature |

#### Confusing Names

| Name | Problem | Better Alternative |
|------|---------|-------------------|
| `safe_mode` | Only affects critical patterns | `force_functional_patterns_square` |
| `min_island_modules` | Jargon | `min_isolated_module_group_size` |
| `auto_mask` | Looks like type selector | `enable_auto_mask` |

### 3. Module/Class Naming - AUDIT COMPLETE

#### Class Naming: EXCELLENT Consistency

| Pattern | Count | Assessment |
|---------|-------|------------|
| `*Config` | 14+ | All config classes follow pattern |
| `*Renderer` | 13 | All shape renderers follow pattern |
| `*Error` | 22 | All exceptions follow pattern |
| `*Builder` | 6 | SVG builders follow pattern |
| Enums (CamelCase) | 12 | No suffix, follows Python convention |

#### Public/Private Distinction: ONE ISSUE

**Problem:** `segnomms/plugin/__init__.py` exports 8 private (`_` prefixed) functions in `__all__`:
- `_export_configuration`, `_generate_config_hash`, `_render_cluster`, etc.

This violates public/private convention - underscore prefix contradicts public export.

#### Package Structure: EXCELLENT

- Clear separation of concerns (config, shapes, core, svg, intents)
- Intuitive naming reflects purpose
- Max 3 levels of nesting

## Proposed Approach

1. **Fix known Phase documentation** - Update `docs/source/api/config.rst` to match implementation
2. **Consider renaming Phase 4** - Maybe "AdvancedFeatureValidator" or similar
3. **Audit config naming** - Create inventory of all user-facing config options
4. **Audit module/class naming** - Map public API surface and evaluate clarity
5. **Document naming conventions** - Add guidelines for future development

## Files to Modify (Estimated)

- `docs/source/api/config.rst` - Fix phase descriptions
- `docs/source/api/validation.rst` - Clarify Phase 4 purpose
- Possibly rename `phase4.py` and `Phase4Validator` class
- Various docstrings throughout config modules

## Success Criteria

- New users can understand what "phases" are without reading implementation
- Config option names are self-explanatory
- Documentation matches implementation
- Consistent naming conventions throughout public API
- Internal vs user-facing code is clearly distinguished

## Dependencies

- None - can be done independently

---

## Terminology Reference

This section documents the origin, purpose, and relationships of key terms used in SegnoMMS.

### Terminology Layers

```
QR Code Standard (ISO/IEC 18004)
├── Finder Patterns ──────── 3 corner 7x7 position markers
├── Alignment Patterns ───── 5x5 scaling/position aids (v2+)
├── Timing Patterns ──────── Alternating module sequences
├── Format Information ───── Error correction + mask encoding
├── Version Information ──── QR version encoding (v7+)
├── Error Correction ─────── L/M/Q/H recovery levels
├── Modules ──────────────── Individual QR squares
├── Data Modules ─────────── Encoded content area
└── Quiet Zone ───────────── 4-module white border

    ↓ wrapped by

Segno Library (Python QR generation)
├── QRCode Object ────────── Generated by segno.make()
├── Plugin Interface ─────── Entry point: segnomms.plugin:write
├── ECI Mode ─────────────── International character encoding
├── Mask Patterns ────────── Visual optimization (0-7)
└── Structured Append ────── Multi-code sequences

    ↓ extended by

SegnoMMS Enhancement System
├── Intent System ────────── Content detection → auto-config
├── Multi-Phase Pipeline
│   ├── Phase 1 ──────────── 8-neighbor context analysis
│   ├── Phase 2 ──────────── Connected component clustering
│   ├── Phase 3 ──────────── Bezier curve smoothing
│   └── Phase 4 ──────────── SVG assembly + validation
├── Shape Customization
│   ├── Connectivity Mode ── 4-way vs 8-way neighbors
│   ├── Merge Strategy ───── none / soft / aggressive
│   └── 14 Shape Types ───── basic + connected variants
├── Centerpiece System
│   ├── Reserve Mode ─────── knockout vs imprint
│   └── Placement Mode ───── 9 position options
└── Advanced Rendering
    ├── Contour Mode ─────── bezier / combined / overlay
    └── Optimization Level ─ file size vs precision
```

### Glossary by Origin

#### QR Code Specification (ISO/IEC 18004)

| Term | Definition | Purpose | Source File |
|------|-----------|---------|-------------|
| Finder Pattern | 7x7 markers at 3 corners | QR code location/orientation | `core/detector.py:23-27` |
| Alignment Pattern | 5x5 markers (version 2+) | Position correction for larger codes | `core/detector.py:29-30` |
| Timing Pattern | Alternating dark/light sequences | Module position reference | `core/detector.py:148` |
| Module | Single square in QR matrix | Basic unit of QR data | Throughout codebase |
| Quiet Zone | White border (4 modules) | Scanner isolation | `validation/phase4.py:76-87` |
| Error Correction | L/M/Q/H levels | Data recovery capability | `intents/models.py:34-36` |

#### Segno Library (Upstream Dependency)

| Term | Definition | Purpose | Source File |
|------|-----------|---------|-------------|
| QRCode | Segno's generated QR object | Base generation | `core/advanced_qr.py:16-17` |
| Plugin Interface | `segnomms.plugin:write` entry point | Segno integration | `README.md:14` |
| ECI Mode | Extended Channel Interpretation | International characters | `core/advanced_qr.py:28` |
| Mask Pattern | Visual optimization pattern (0-7) | Improve scannability | `core/advanced_qr.py:29` |

#### SegnoMMS Innovations

| Term | Definition | Purpose | Source File |
|------|-----------|---------|-------------|
| Intent | Content type + auto-config | Smart defaults | `intents/processor.py:3-4` |
| Phase 1 | Enhanced 8-neighbor detection | Context-aware shapes | `config/models/phases.py:16-45` |
| Phase 2 | Connected component clustering | Group adjacent modules | `config/models/phases.py:48-79` |
| Phase 3 | Marching squares + Bezier | Smooth contours | `config/models/phases.py:82-96` |
| Phase 4 | SVG assembly + validation | Output generation | `validation/phase4.py` |
| Merge Strategy | Module blending behavior | Visual fluidity | `config/enums.py:51-93` |
| Connectivity | 4-way vs 8-way neighbors | Neighbor detection | `config/enums.py:11-48` |
| Shape Factory | Dynamic renderer creation | Extensible shapes | `shapes/factory.py:49-114` |
| Reserve Mode | Centerpiece interaction | Logo integration | `config/enums.py:96-130` |
| Contour Mode | Smoothing strategy | Edge rendering | `config/enums.py:314-354` |

### Naming Issues by Origin

| Issue | Origin Layer | Problem |
|-------|-------------|---------|
| "Phase" overload | SegnoMMS | 3 different meanings |
| Phase 4 mismatch | SegnoMMS | Validation ≠ processing |
| `enable_*` vs `use_*` | SegnoMMS | Inconsistent boolean prefixes |
| Doc descriptions | SegnoMMS | Don't match implementation |

---

## Ecosystem Naming Conventions

Research into related Python libraries and broader software engineering best practices to inform SegnoMMS naming decisions.

### Python QR/Image Ecosystem

#### Segno (Upstream - Most Important)

**Boolean naming:** Bare descriptive names, NO prefixes
- `micro`, `eci`, `boost_error`, `compact`, `plain`, `hidden`
- `xmldecl`, `svgns`, `omitsize`, `draw_transparent`

**Structure:** Keyword arguments to methods, not config classes

**Pipeline terms:** "serialization" for output, no numbered stages

*Source: [Segno API Documentation](https://segno.readthedocs.io/en/stable/api.html)*

#### qrcode (Popular Alternative)

**Boolean naming:** Bare names + constants
- `fit` parameter
- `ERROR_CORRECT_L/M/Q/H` constants (not booleans)

**Class naming:** `*Drawer`, `*Mask`, `*Image` suffixes
- `RoundedModuleDrawer`, `RadialGradiantColorMask`, `StyledPilImage`

*Source: [python-qrcode GitHub](https://github.com/lincolnloop/python-qrcode)*

#### python-barcode

**Boolean naming:** `add_*` prefix for optional additions
- `add_checksum=False`

*Source: [python-barcode Documentation](https://python-barcode.readthedocs.io/)*

#### Pillow

**Boolean naming:** Descriptive suffixes, keyword-only
- `alpha_only`, `expand`
- Avoids unclear boolean flags

*Source: [Pillow Image Reference](https://pillow.readthedocs.io/en/stable/reference/Image.html)*

#### svgwrite

**Parameter naming:** Underscore conventions
- Trailing underscore for Python keywords: `class_`
- Replace hyphens with underscores: `stroke_width`

*Source: [svgwrite Documentation](https://svgwrite.readthedocs.io/)*

### Key Ecosystem Insight

**The Python QR/image ecosystem prefers BARE boolean names** - not prefixed.

| Library | Example | SegnoMMS Equivalent |
|---------|---------|---------------------|
| Segno | `eci=True` | `eci_enabled=True` |
| Segno | `boost_error=True` | (matches) |
| qrcode | `fit=True` | N/A |

**SegnoMMS is MORE VERBOSE than ecosystem norms** with its `enable_*` prefixes.

### Broader Software Engineering Best Practices

#### Boolean Naming Guidance (Microsoft, etc.)

**Recommended prefixes by meaning:**

| Prefix | Usage | Example |
|--------|-------|---------|
| `is` | Current state | `is_enabled`, `is_active` |
| `has` | Possession | `has_children`, `has_access` |
| `can` | Capability | `can_seek`, `can_write` |
| `should` | Recommendation | `should_validate` |

**`enable` is an ACTION verb**, not a state descriptor:
- `enable_feature` suggests "turn this on" (imperative)
- `is_enabled` describes "is this currently on?" (state)
- Microsoft: Use affirmative phrases like `CanSeek` not `CantSeek`

*Sources: [Microsoft Framework Design Guidelines](https://learn.microsoft.com/en-us/dotnet/standard/design-guidelines/names-of-type-members), [Boolean Naming Guidelines](https://serendipidata.com/posts/naming-guidelines-for-boolean-variables)*

#### Key Principles

1. **Avoid negatives**: `is_invalid` not `is_not_valid`
2. **Default to False**: Optional params should default to `False`
3. **Clarity > brevity**: `is_file_open` clearer than `file_open`
4. **Consistency**: Pick one pattern and use it everywhere

### The SegnoMMS Problem

SegnoMMS uses `enable_*` (action/imperative) when `*_enabled` or bare names would be more standard:
- `enable_phase1=True` → suggests "turn on phase1"
- Better: `phase1_enabled=True` or just `phase1=True`

### Recommendations Based on Research

| Current SegnoMMS | Standard Convention | Rationale |
|------------------|---------------------|-----------|
| `enable_phase1` | `phase1` or `phase1_enabled` | Matches Segno + state description |
| `use_enhanced_shapes` | `enhanced_shapes` | `use_` acceptable but verbose |
| `centerpiece_enabled` | `centerpiece_enabled` | Already correct |
| `interactive` (bare) | `is_interactive` | State needs prefix for clarity |

### Recommended Approach

**Hybrid strategy (pragmatic):**
1. **Segno-inherited concepts**: Use bare names (matching upstream)
2. **State booleans**: Use `*_enabled` suffix (state description)
3. **Strategy selection**: `use_*` prefix acceptable
4. **Deprecate `enable_*`**: It's an action verb, not state

---

## Notes

*Add investigation findings, decisions, and learnings here as research progresses*

### Initial Research (2025-01-XX)

Phase terminology research completed. Key finding: "Phase 4" is fundamentally different from Phases 1-3 and should probably be renamed to avoid confusion.

**Alternative names for Phase 4 to consider:**
- `AdvancedFeatureValidator`
- `FrameValidator` / `CenterpieceValidator`
- `CompositionValidator`
- Remove "Phase" entirely from the name

### Terminology Origin Research (2025-01-XX)

Documented three-layer terminology hierarchy:
1. **QR Spec layer** - Standard terms (finder, timing, alignment, modules, etc.)
2. **Segno layer** - Upstream library terms (QRCode, plugin, ECI, mask)
3. **SegnoMMS layer** - Project innovations (phases, intents, merge strategy, shapes)

Key insight: Most naming confusion exists in SegnoMMS-specific terms, not inherited terminology.

### Config & Module Naming Audit (2025-12-27)

Completed comprehensive audits:
- **Config options**: 127 fields, 5 different boolean prefix patterns
- **Class naming**: Excellent consistency (`*Config`, `*Renderer`, `*Error`)
- **Package structure**: Intuitive, well-organized

Key issues to fix:
1. Boolean option prefix chaos (standardize based on ecosystem research)
2. Deprecated aliases still active (`reserve_*` → `centerpiece_*`)
3. Private functions exported publicly in plugin module

### Ecosystem Naming Research (2025-12-27)

Researched naming conventions from:
- **Python QR/Image libraries**: Segno, qrcode, python-barcode, Pillow, svgwrite
- **Broader best practices**: Microsoft Framework Design Guidelines, various dev community resources

**Key findings:**
- Python QR/image ecosystem prefers **bare boolean names** (no prefix)
- `enable_*` is an **action verb**, not a state descriptor
- `*_enabled` suffix or bare names are more standard
- SegnoMMS is more verbose than ecosystem norms

**Recommended approach:**
1. Match Segno's bare naming for inherited concepts
2. Use `*_enabled` suffix for state booleans
3. Deprecate `enable_*` prefix pattern

---

## Spec-Kit Input

**Feature description for `/speckit.specify`:**

```
As a developer using SegnoMMS, I want clear and consistent naming throughout
the library so I can understand features from their names alone, find related
options easily, and trust that documentation matches actual behavior.

Current problems:
- "Phase" terminology is confusing: Phase 1-3 are processing features you
  enable/disable, but Phase 4 is actually a validation system
- Boolean options use 5 different naming patterns (enable_*, use_*, *_enabled,
  bare booleans, add_*/include_*), making the API hard to learn
- The `enable_*` prefix is non-standard - the Python QR ecosystem uses bare
  names, and software best practices recommend `*_enabled` for state
- Documentation describes phases incorrectly (doesn't match implementation)
- Deprecated option names (reserve_*) still work alongside new names
  (centerpiece_*), creating confusion about which to use

Desired outcomes:
- New users can configure the library correctly on first try
- Option names follow ecosystem conventions (bare names or *_enabled)
- Documentation accurately describes what each feature does
- Related options share consistent naming patterns
- Clear guidance on which option names to use (deprecate old aliases)
```

**Success criteria (user-focused):**
- A developer familiar with Segno can use SegnoMMS without relearning naming
- Boolean options follow ecosystem-standard naming conventions
- Documentation phase descriptions match actual feature behavior
- No confusion about deprecated vs current option names
