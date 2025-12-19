# Feature Idea: Documentation Improvements

**Status**: Backlog
**Priority**: Medium (do before refactors)
**Category**: Documentation

---

## Problem Statement

Current documentation gaps:

1. **Phase Pipeline Interactions**: How do phases depend on each other?
2. **Magic Numbers**: Why `size_ratio = 0.9`? Why `min_cluster_size = 3`?
3. **Architecture Overview**: No high-level diagram for new contributors
4. **Developer Onboarding**: How to add new shapes/intents?

## Proposed Documentation

### 1. Architecture Diagram

Add to Sphinx docs (`docs/source/internals/pipeline.rst`):

```
                    SegnoMMS Pipeline

User Input → IntentProcessor ┬→ RenderingConfig (used by all phases)
                             └→ QR Matrix
                                   ↓
                            Phase 1 (Enhanced Shapes)
                                   ↓
                            Phase 2 (Clustering)
                                   ↓
                            Phase 3 (Contours)
                                   ↓
                            Phase 4 (Visual Enhancement)
                                   ↓
                              SVG Output
```

Include:
- When each phase runs
- What triggers auto-enable
- Phase dependencies
- Data flow between phases

### 2. Phase Interaction Documentation

Document in code and Sphinx:
- Phase 1 (Enhanced Shapes): When `shape != "square"` or `corner_radius > 0`
- Phase 2 (Clustering): When `merge != "none"`
- Phase 3 (Contours): When `merge == "aggressive"`
- Phase 4 (Visual): Always runs for frames/centerpieces

Questions to answer:
- Can Phase 3 run without Phase 2?
- Does Phase 2 output replace Phase 1 output?
- What happens if all phases are disabled?

### 3. Magic Number Documentation

Create `docs/source/internals/constants.rst`:

| Constant | Value | Rationale |
|----------|-------|-----------|
| `size_ratio` | 0.9 | Visual testing: 90% fill prevents bleeding |
| `min_cluster_size` | 3 | Clusters < 3 modules don't benefit from merging |
| `corner_radius` | 0.3 | Default matches common design expectations |
| `kappa` (squircle) | 0.37 | Mathematical: approximates superellipse n=4 |

### 4. Developer Onboarding Guides

Create the following tutorial files in `docs/source/development/`:
- `architecture.rst` - High-level module overview
- `adding-shapes.rst` - Shape renderer tutorial (content below)
- `adding-intents.rst` - Intent type tutorial (content below)

#### How to Add a New Shape Renderer
*(Content for `adding-shapes.rst`)*

```python
# 1. Create renderer class in segnomms/shapes/basic.py
class OctagonRenderer(BaseShapeRenderer):
    shape_names = ["octagon"]

    def render(self, x: float, y: float, size: float, **kwargs: Any) -> ET.Element:
        center_x, center_y = get_module_center(x, y, size)
        radius = apply_size_ratio(size / 2, kwargs, 0.9)
        points = generate_regular_polygon(center_x, center_y, radius, 8, start_angle=math.pi/8)
        return create_svg_element("polygon", {"points": " ".join(points)}, kwargs)

# 2. Register in factory (segnomms/shapes/factory.py)
def _register_default_renderers(self):
    ...
    self.register_renderer("octagon", OctagonRenderer)

# 3. Add to enum (segnomms/config/enums.py)
class ModuleShape(str, Enum):
    ...
    OCTAGON = "octagon"

# 4. Add tests (tests/unit/test_shapes_basic.py)
```

#### How to Add a New Intent Type
*(Content for `adding-intents.rst`)*

1. Add model in `segnomms/intents/models.py`
2. Add processor method in `segnomms/intents/processor.py`
3. Add to `IntentsConfig` in models.py
4. Update `_process_all_intents()` router
5. Add tests

## Files to Create/Modify

| File | Action | Content |
|------|--------|---------|
| `docs/source/internals/pipeline.rst` | Create | Architecture diagram, phase docs |
| `docs/source/internals/constants.rst` | Create | Magic number rationale |
| `docs/source/development/architecture.rst` | Create | Developer guides |
| `docs/source/development/adding-shapes.rst` | Create | Shape tutorial |
| `docs/source/development/adding-intents.rst` | Create | Intent tutorial |
| `segnomms/config/models/core.py` | Update | Add "why" comments |

## Success Criteria

- Architecture diagram exists in Sphinx docs
- All magic numbers have documented rationale
- Developer can add new shape following guide
- Developer can add new intent following guide
- Phase interactions explicitly documented

## Integration with Sphinx

Ensure new docs are added to `docs/source/index.rst` toctree:

```rst
.. toctree::
   :maxdepth: 2

   internals/pipeline
   internals/constants
   development/architecture
   development/adding-shapes
   development/adding-intents
```

---

## Notes

*Add documentation drafts, decisions, and learnings here as work progresses*
