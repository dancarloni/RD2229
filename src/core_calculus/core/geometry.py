from __future__ import annotations

from dataclasses import dataclass
from math import pi
from typing import Iterable, List, Optional, Tuple


@dataclass(frozen=True)
class SectionPropertiesBase:
    area: float
    centroid_x: float
    centroid_y: float
    ix: float
    iy: float
    qx: float
    qy: float


class SectionGeometry:
    def area(self) -> float:
        raise NotImplementedError

    def centroid(self) -> Tuple[float, float]:
        raise NotImplementedError

    def inertia(self) -> Tuple[float, float]:
        """Momenti d'inerzia baricentrici (Ix, Iy)."""
        raise NotImplementedError

    def static_moment(self) -> Tuple[float, float]:
        """Momenti statici rispetto agli assi x=0 e y=0."""
        a = self.area()
        cx, cy = self.centroid()
        return a * cy, a * cx


@dataclass(frozen=True)
class RectangularSection(SectionGeometry):
    width: float
    height: float
    x0: float = 0.0
    y0: float = 0.0

    def area(self) -> float:
        return self.width * self.height

    def centroid(self) -> Tuple[float, float]:
        return (self.x0 + self.width / 2.0, self.y0 + self.height / 2.0)

    def inertia(self) -> Tuple[float, float]:
        ix = self.width * self.height**3 / 12.0
        iy = self.height * self.width**3 / 12.0
        return ix, iy


@dataclass(frozen=True)
class CircularSection(SectionGeometry):
    diameter: float
    x0: float = 0.0
    y0: float = 0.0

    def area(self) -> float:
        r = self.diameter / 2.0
        return pi * r * r

    def centroid(self) -> Tuple[float, float]:
        r = self.diameter / 2.0
        return (self.x0 + r, self.y0 + r)

    def inertia(self) -> Tuple[float, float]:
        r = self.diameter / 2.0
        i = pi * r**4 / 4.0
        return i, i


@dataclass(frozen=True)
class _SignedRectangle:
    x: float
    y: float
    width: float
    height: float
    sign: int = 1

    def area(self) -> float:
        return self.sign * self.width * self.height

    def centroid(self) -> Tuple[float, float]:
        return (self.x + self.width / 2.0, self.y + self.height / 2.0)

    def inertia(self) -> Tuple[float, float]:
        ix = self.width * self.height**3 / 12.0
        iy = self.height * self.width**3 / 12.0
        return ix, iy


class CompositeSection(SectionGeometry):
    def __init__(self, rectangles: Optional[Iterable[_SignedRectangle]] = None):
        self._rectangles = list(rectangles) if rectangles else []

    def _rects(self) -> List[_SignedRectangle]:
        return self._rectangles

    def area(self) -> float:
        return sum(r.area() for r in self._rects())

    def centroid(self) -> Tuple[float, float]:
        rects = self._rects()
        a = self.area()
        if a == 0:
            raise ValueError("Area nulla nella sezione composita")
        sx = 0.0
        sy = 0.0
        for r in rects:
            cx, cy = r.centroid()
            sx += r.area() * cx
            sy += r.area() * cy
        return sx / a, sy / a

    def inertia(self) -> Tuple[float, float]:
        rects = self._rects()
        cx, cy = self.centroid()
        ix = 0.0
        iy = 0.0
        for r in rects:
            rx, ry = r.centroid()
            i_rx, i_ry = r.inertia()
            dx = rx - cx
            dy = ry - cy
            ix += r.area() * dy**2 + r.sign * i_rx
            iy += r.area() * dx**2 + r.sign * i_ry
        return ix, iy


@dataclass
class TSection(CompositeSection):
    flange_width: float
    flange_thickness: float
    web_thickness: float
    web_height: float

    def __post_init__(self):
        bf = self.flange_width
        tf = self.flange_thickness
        tw = self.web_thickness
        hw = self.web_height
        xw = (bf - tw) / 2.0
        rectangles = [
            _SignedRectangle(x=0.0, y=hw, width=bf, height=tf, sign=1),
            _SignedRectangle(x=xw, y=0.0, width=tw, height=hw, sign=1),
        ]
        super().__init__(rectangles)


@dataclass
class LSection(CompositeSection):
    leg_x: float
    leg_y: float
    thickness: float

    def __post_init__(self):
        b = self.leg_x
        h = self.leg_y
        t = self.thickness
        rectangles = [
            _SignedRectangle(x=0.0, y=0.0, width=b, height=t, sign=1),
            _SignedRectangle(x=0.0, y=0.0, width=t, height=h, sign=1),
            _SignedRectangle(x=0.0, y=0.0, width=t, height=t, sign=-1),
        ]
        super().__init__(rectangles)


@dataclass
class ISection(CompositeSection):
    flange_width: float
    flange_thickness: float
    web_thickness: float
    web_height: float

    def __post_init__(self):
        bf = self.flange_width
        tf = self.flange_thickness
        tw = self.web_thickness
        hw = self.web_height
        xw = (bf - tw) / 2.0
        rectangles = [
            _SignedRectangle(x=0.0, y=0.0, width=bf, height=tf, sign=1),
            _SignedRectangle(x=xw, y=tf, width=tw, height=hw, sign=1),
            _SignedRectangle(x=0.0, y=tf + hw, width=bf, height=tf, sign=1),
        ]
        super().__init__(rectangles)


@dataclass
class InvertedTSection(CompositeSection):
    flange_width: float
    flange_thickness: float
    web_thickness: float
    web_height: float

    def __post_init__(self):
        bf = self.flange_width
        tf = self.flange_thickness
        tw = self.web_thickness
        hw = self.web_height
        xw = (bf - tw) / 2.0
        rectangles = [
            _SignedRectangle(x=0.0, y=0.0, width=bf, height=tf, sign=1),
            _SignedRectangle(x=xw, y=tf, width=tw, height=hw, sign=1),
        ]
        super().__init__(rectangles)


@dataclass
class PiSection(CompositeSection):
    """Sezione a pigreco (simile al simbolo Π): flange superiore con due montanti verticali."""

    width: float
    top_thickness: float
    leg_thickness: float
    leg_height: float

    def __post_init__(self):
        bf = self.width
        tf = self.top_thickness
        tw = self.leg_thickness
        hw = self.leg_height
        rectangles = [
            _SignedRectangle(x=0.0, y=hw, width=bf, height=tf, sign=1),
            _SignedRectangle(x=0.0, y=0.0, width=tw, height=hw, sign=1),
            _SignedRectangle(x=bf - tw, y=0.0, width=tw, height=hw, sign=1),
        ]
        super().__init__(rectangles)


@dataclass(frozen=True)
class RectangularHollowSection(SectionGeometry):
    outer_width: float
    outer_height: float
    inner_width: float
    inner_height: float
    x0: float = 0.0
    y0: float = 0.0

    def area(self) -> float:
        return self.outer_width * self.outer_height - self.inner_width * self.inner_height

    def centroid(self) -> Tuple[float, float]:
        return (self.x0 + self.outer_width / 2.0, self.y0 + self.outer_height / 2.0)

    def inertia(self) -> Tuple[float, float]:
        ix_outer = self.outer_width * self.outer_height**3 / 12.0
        iy_outer = self.outer_height * self.outer_width**3 / 12.0
        ix_inner = self.inner_width * self.inner_height**3 / 12.0
        iy_inner = self.inner_height * self.inner_width**3 / 12.0
        return ix_outer - ix_inner, iy_outer - iy_inner


@dataclass(frozen=True)
class CircularHollowSection(SectionGeometry):
    outer_diameter: float
    inner_diameter: float
    x0: float = 0.0
    y0: float = 0.0

    def area(self) -> float:
        r = self.outer_diameter / 2.0
        ri = self.inner_diameter / 2.0
        return pi * (r * r - ri * ri)

    def centroid(self) -> Tuple[float, float]:
        r = self.outer_diameter / 2.0
        return (self.x0 + r, self.y0 + r)

    def inertia(self) -> Tuple[float, float]:
        r = self.outer_diameter / 2.0
        ri = self.inner_diameter / 2.0
        i_outer = pi * r**4 / 4.0
        i_inner = pi * ri**4 / 4.0
        return i_outer - i_inner, i_outer - i_inner
