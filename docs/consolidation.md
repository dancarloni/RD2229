# Consolidation of geometry and graphics modules

Summary

- Canonical geometry model: `src/core_calculus/core/geometry_model.py` (polygon-based `SectionGeometry`, `SectionProperties`, `CoreData`, `EllipseData`).
- Canonical graphics controller: `apps/sections/section_graphics.py` (`SectionViewTransform`, `SectionGraphicsController`).
- All legacy copies and shims of `geometry_model` / `section_graphics` have been removed; imports were redirected repository-wide.

Why

- Remove duplicated implementations that diverged over time.
- Provide a single, well-tested API for geometry and UI drawing.
- Simplify maintenance and prevent subtle behavioral differences across packages.

Developer migration notes

1. Replace old imports with the canonical path:
   - `from apps.sections.geometry_model import SectionGeometry`  -->
     `from src.core_calculus.core.geometry_model import SectionGeometry`
   - `from libs.app_module.section_graphics import SectionGraphicsController`  -->
     `from apps.sections.section_graphics import SectionGraphicsController`

2. Use the convenience constructors and helpers:
   - `SectionGeometry.from_rectangle(b, h, rotation_deg=0.0, name="")`
   - `SectionGeometry.bounding_box()` returns (minx, miny, maxx, maxy)

3. For UI code, prefer `SectionViewTransform` to compute a `scale` and translations
   and then call the `SectionGraphicsController` drawing helpers.

Rollback / safety

- All changes are on branch `consolidate/geometry-graphics-and-docs`.
- Several removed legacy files were backed up as `.bak` in-place before deletion.
- If you need to restore a legacy file, use git on the branch or find the `.bak` copy.

Notes for reviewers

- Focus on import-site updates and on any behavioral differences in drawing or
  geometry (centroid, bbox, core-of-inertia). Numeric algorithms were not
  intentionally changed; the goal was consolidation only.
- Suggested review items:
  - Verify there are no remaining local copies of `geometry_model` or `section_graphics`.
  - Confirm unit tests cover both geometry helpers and drawing flows.

Files added/updated by this consolidation

- Added: `src/core_calculus/core/geometry_model.py`
- Kept canonical: `apps/sections/section_graphics.py`
- Updated: multiple import sites across `src/`, `apps/`, `tests/`, `scripts/`.

Example usages

```py
from src.core_calculus.core.geometry_model import SectionGeometry
from apps.sections.section_graphics import SectionGraphicsController

geom = SectionGeometry.from_rectangle(10.0, 20.0, name="rect")
props = compute_section_properties_from_geometry(geom)
# draw on tkinter canvas
controller = SectionGraphicsController(canvas)
controller.draw_all(geom, props)
```
