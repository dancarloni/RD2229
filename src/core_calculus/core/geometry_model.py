"""Polygon-based section geometry models (canonical location).

This module centralizes the polygon-style SectionGeometry / SectionProperties
used across UI, section adapters and shapely-based calculations.

Replaces previous copies under `apps.sections.geometry_model` and
`libs.app_module.geometry_model`.
"""

from __future__ import annotations

from dataclasses import dataclass, field

Point = tuple[float, float]  # (x, y) in model units (e.g. cm)


@dataclass
class SectionGeometry:
    """Describe contours and holes in real-world units (cm/mm).

    Attributes:
        exterior: list[Point]  -- outer ring in CCW order
        holes: list[list[Point]] -- optional holes (each ring CCW)
        units: str -- units string (default: "cm")
        meta: dict -- extra metadata
    """

    exterior: list[Point]
    holes: list[list[Point]] = field(default_factory=list)
    units: str = "cm"
    meta: dict = field(default_factory=dict)

    @classmethod
    def from_rectangle(
        cls, b: float, h: float, rotation_deg: float = 0.0, name: str = ""
    ) -> SectionGeometry:
        """Convenience constructor for axis-aligned rectangle centered at origin.

        Points are returned in CCW order.
        """
        hw = b / 2.0
        hh = h / 2.0
        pts = [(-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh)]
        return cls(
            exterior=pts, meta={"name": name, "rotation_deg": rotation_deg, "type": "rectangular"}
        )

    def bounding_box(self) -> tuple[float, float, float, float]:
        """Return bbox (minx, miny, maxx, maxy) over exterior and holes."""
        xs = [p[0] for p in self.exterior]
        ys = [p[1] for p in self.exterior]
        for hole in self.holes:
            xs.extend(p[0] for p in hole)
            ys.extend(p[1] for p in hole)
        return min(xs), min(ys), max(xs), max(ys)


@dataclass
class CoreData:
    """Representation of the core (nocciolo) as needed."""

    polygon: list[Point] | None = None


@dataclass
class EllipseData:
    a: float = 0.0  # semi-major (in model units)
    b: float = 0.0  # semi-minor
    theta_deg: float = 0.0  # rotation of ellipse


@dataclass
class SectionProperties:
    """Computed geometric properties (polygon-based representation)."""

    area: float = 0.0
    Ix: float = 0.0
    Iy: float = 0.0
    Ixy: float = 0.0
    x_c: float = 0.0
    y_c: float = 0.0
    I1: float = 0.0
    I2: float = 0.0
    theta_p_deg: float = 0.0
    r1: float = 0.0
    r2: float = 0.0
    core: CoreData | None = None
    ellipse: EllipseData | None = None
    meta: dict = field(default_factory=dict)
