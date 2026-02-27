# Geometry model (canonical)

This page documents the canonical polygon-based geometry model used across the
project.

Files
- `src/core_calculus/core/geometry_model.py` — canonical dataclasses: `SectionGeometry`, `SectionProperties`, `CoreData`, `EllipseData`.

Overview
- `SectionGeometry` represents an exterior ring and optional holes (lists of (x,y) points).
- Coordinates use model units (default `cm`); use `meta` for type/rotation info.

Quick examples

```py
from src.core_calculus.core.geometry_model import SectionGeometry

# simple rectangle
geom = SectionGeometry.from_rectangle(10.0, 20.0, name="rect")

# polygon with hole
outer = [(0,0),(10,0),(10,10),(0,10)]
inner = [(4,4),(6,4),(6,6),(4,6)]
geom2 = SectionGeometry(exterior=outer, holes=[inner])
```

Testing
- See `tests/test_geometry_model_extra.py` for unit-tests and edge cases.

Notes
- Prefer `SectionGeometry` from this module anywhere a polygonal representation is needed.
- Add new convenience constructors here when needed (keep behaviour deterministic).