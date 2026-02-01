from __future__ import annotations

from dataclasses import dataclass
from math import pi
from typing import Iterable, List, Tuple


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


@dataclass(frozen=True)
class CompositeSection(SectionGeometry):
    rectangles: Iterable[_SignedRectangle]

    def _rects(self) -> List[_SignedRectangle]:
        return list(self.rectangles)

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


@dataclass(frozen=True)
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
        object.__setattr__(self, "rectangles", rectangles)


@dataclass(frozen=True)
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
        object.__setattr__(self, "rectangles", rectangles)


@dataclass(frozen=True)
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
        object.__setattr__(self, "rectangles", rectangles)
