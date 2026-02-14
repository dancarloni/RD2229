# Section calculations (pipeline & APIs)

Canonical calculation module: `src/core_calculus/section_calculations.py`.

Contents
- Centroid and polygon area helpers
- Inertia computations (Ix, Iy, Ixy) about centroid
- Principal axes and radii of gyration
- Core-of-inertia heuristic and shapely-backed improvements
- Section → SectionGeometry adapter for existing `Section` models

Public API (high level)
- `compute_section_properties_from_geometry(geom: SectionGeometry, shear_factor=None) -> SectionProperties`
  - High-level pipeline returning `SectionProperties` (area, inertia, centroid, core, ellipse).
- `section_to_geometry(section: Section) -> SectionGeometry`
  - Adapter from `apps.sections.models.sections.Section` to polygonal geometry.

Example

```py
from src.core_calculus.core.geometry_model import SectionGeometry
from src.core_calculus.section_calculations import compute_section_properties_from_geometry

geom = SectionGeometry.from_rectangle(10.0, 20.0)
props = compute_section_properties_from_geometry(geom)
print(props.area, props.x_c, props.Ix)
```

Testing and regression
- Add regression tests for rotated geometries and shapes with holes.
- See `tests/test_section_calculations.py` and `tests/test_section_calculations_extra.py`.

Implementation notes
- When `shapely` is installed the module uses robust polygon/offset operations — behaviour falls back to pure-python algorithms when shapely is not available.
- The core-of-inertia algorithm is intentionally conservative to return an inner polygon contained in the material domain.

To extend
- Add more unit tests that assert invariance to rigid-body transforms (translations/rotations).
- Document formulas used (e.g., polygon moment integrals) in comments for auditability.