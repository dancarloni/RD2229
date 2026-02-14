# Graphics (Section view transform & drawing)

Canonical UI drawing helpers: `apps/sections/section_graphics.py`.

Key classes
- `SectionViewTransform(bbox, canvas_w, canvas_h, margin=20)` — compute uniform scale and pixel translation from world coordinates to canvas screen coordinates.
- `SectionGraphicsController(canvas)` — drawing controller exposing `draw_all` plus helpers: `draw_section_contour`, `draw_centroid`, `draw_principal_axes`, `draw_inertia_ellipse`, `draw_core_of_inertia`, `draw_dimensioning`, `draw_radii_of_gyration`.

Examples

```py
from src.core_calculus.core.geometry_model import SectionGeometry
from src.core_calculus.section_calculations import compute_section_properties_from_geometry
from apps.sections.section_graphics import SectionGraphicsController

geom = SectionGeometry.from_rectangle(10.0,20.0)
props = compute_section_properties_from_geometry(geom)
# on a tkinter Canvas named `canvas`
controller = SectionGraphicsController(canvas)
controller.draw_all(geom, props)
```

Testing
- Use `FakeCanvas` in `tests/test_section_graphics_fake_canvas.py` for headless unit tests.
- GUI integration tests can run conditionally (skip when Tk is unavailable).

Notes for contributors
- Keep drawing logic independent from app state — controller expects `SectionGeometry` + `SectionProperties`.
- When adding new draw helpers, add corresponding fake-canvas tests to validate canvas API calls.
