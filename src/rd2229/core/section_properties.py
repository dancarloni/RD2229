from __future__ import annotations

from dataclasses import dataclass

from .geometry import SectionGeometry


@dataclass(frozen=True)
class SectionProperties:
    area: float
    centroid_x: float
    centroid_y: float
    ix: float
    iy: float
    qx: float
    qy: float


def compute_section_properties(section: SectionGeometry) -> SectionProperties:
    area = section.area()
    cx, cy = section.centroid()
    ix, iy = section.inertia()
    qx, qy = section.static_moment()
    return SectionProperties(
        area=area,
        centroid_x=cx,
        centroid_y=cy,
        ix=ix,
        iy=iy,
        qx=qx,
        qy=qy,
    )
