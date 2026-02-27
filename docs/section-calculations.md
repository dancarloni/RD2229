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

Formulas (summary)
- Polygon area (signed):
  A = 1/2 * sum_{i=0..n-1} (x_i * y_{i+1} - x_{i+1} * y_i)
- Centroid (for polygon with vertices (x_i,y_i)):
  C_x = (1/(6A)) * sum_{i} (x_i + x_{i+1}) * (x_i*y_{i+1} - x_{i+1}*y_i)
  C_y = (1/(6A)) * sum_{i} (y_i + y_{i+1}) * (x_i*y_{i+1} - x_{i+1}*y_i)
- Second moments (about origin) and inertia about centroid are computed via standard polygon integral formulas (see implementation comments in `src/core_calculus/section_calculations.py`).

Testing (what we added)
- Regression tests for analytic comparisons and invariants:
  - `tests/test_section_calculations_regression.py` (area/centroid/invariant checks)
  - `tests/test_section_calculations_rotation.py` (rotation invariants for principal moments and radii)
  - `tests/test_section_to_geometry_types.py` (adapter `Section` → `SectionGeometry` checks)
  - `tests/test_shapely_integration_optional.py` (shapely-specific core/offset behaviour — skipped if shapely missing)

How to add tests
- Use `SectionGeometry.from_rectangle(...)` for deterministic polygonal shapes.
- For shapely-specific behaviours use `pytest.importorskip("shapely")`.

To extend
- Add unit tests that reproduce known reference values (hand-calculated or from literature) and add them under `tests/` with clear names and tolerances.