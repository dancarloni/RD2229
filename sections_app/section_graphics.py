2"""Graphics module: world->screen transform and drawing routines using tk.Canvas."""

from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple, List
import math

from sections_app.geometry_model import SectionGeometry, SectionProperties


@dataclass
class SectionViewTransform:
    """Compute uniform scale and offsets to map world coordinates -> canvas screen coordinates."""

    bbox: Tuple[float, float, float, float]  # (minx, miny, maxx, maxy)
    canvas_width: int
    canvas_height: int
    margin: int = 20  # pixels margin around drawing

    scale: float = 1.0
    tx: float = 0.0  # translation in pixels
    ty: float = 0.0
    flip_y: bool = True

    def __post_init__(self):
        minx, miny, maxx, maxy = self.bbox
        w = maxx - minx if maxx > minx else 1.0
        h = maxy - miny if maxy > miny else 1.0
        avail_w = max(self.canvas_width - 2 * self.margin, 1)
        avail_h = max(self.canvas_height - 2 * self.margin, 1)
        self.scale = min(avail_w / w, avail_h / h)
        world_cx = (minx + maxx) / 2.0
        world_cy = (miny + maxy) / 2.0
        screen_cx = self.canvas_width / 2.0
        screen_cy = self.canvas_height / 2.0
        self.tx = screen_cx - self.scale * world_cx
        if self.flip_y:
            self.ty = screen_cy + self.scale * world_cy
        else:
            self.ty = screen_cy - self.scale * world_cy

    def world_to_screen(self, x: float, y: float) -> Tuple[float, float]:
        sx = self.scale * x + self.tx
        if self.flip_y:
            sy = -self.scale * y + self.ty
        else:
            sy = self.scale * y + self.ty
        return sx, sy

    def world_length_to_screen(self, d: float) -> float:
        return abs(self.scale * d)


class SectionGraphicsController:
    """Controller that draws geometry and properties onto a tk.Canvas."""

    def __init__(self, canvas):
        self.canvas = canvas
        self.transform: SectionViewTransform | None = None

    def clear(self):
        self.canvas.delete("all")

    def set_transform(self, transform: SectionViewTransform):
        self.transform = transform

    def draw_section_contour(self, geometry: SectionGeometry):
        pts = geometry.exterior
        coords = []
        for x, y in pts:
            sx, sy = self.transform.world_to_screen(x, y)
            coords.extend([sx, sy])
        self.canvas.create_polygon(coords, outline="black", fill="", width=2)
        for hole in geometry.holes:
            coords = []
            for x, y in hole:
                sx, sy = self.transform.world_to_screen(x, y)
                coords.extend([sx, sy])
            self.canvas.create_polygon(coords, outline="black", fill="white", width=1)

    def draw_centroid(self, props: SectionProperties):
        sx, sy = self.transform.world_to_screen(props.x_c, props.y_c)
        r = 4
        self.canvas.create_oval(sx - r, sy - r, sx + r, sy + r, fill="red")
        self.canvas.create_text(sx + 10, sy, text="G", anchor="w", fill="red")

    def draw_principal_axes(self, props: SectionProperties):
        length = (
            max(self.canvas.winfo_width(), self.canvas.winfo_height())
            * 0.4
            / (self.transform.scale or 1)
        )
        theta = math.radians(props.theta_p_deg)
        cx, cy = props.x_c, props.y_c
        dx = math.cos(theta) * length
        dy = math.sin(theta) * length
        sx0, sy0 = self.transform.world_to_screen(cx - dx, cy - dy)
        sx1, sy1 = self.transform.world_to_screen(cx + dx, cy + dy)
        self.canvas.create_line(sx0, sy0, sx1, sy1, fill="blue", dash=(4, 2), width=2)
        theta2 = theta + math.pi / 2.0
        dx2 = math.cos(theta2) * length
        dy2 = math.sin(theta2) * length
        sx0, sy0 = self.transform.world_to_screen(cx - dx2, cy - dy2)
        sx1, sy1 = self.transform.world_to_screen(cx + dx2, cy + dy2)
        self.canvas.create_line(sx0, sy0, sx1, sy1, fill="green", dash=(4, 2), width=2)

    def draw_inertia_ellipse(self, props: SectionProperties):
        if not props.ellipse:
            return
        a = props.ellipse.a
        b = props.ellipse.b
        theta = math.radians(props.ellipse.theta_deg)
        cx, cy = props.x_c, props.y_c
        points = []
        steps = 64
        for i in range(steps):
            t = 2 * math.pi * i / steps
            x = a * math.cos(t)
            y = b * math.sin(t)
            xr = x * math.cos(theta) - y * math.sin(theta) + cx
            yr = x * math.sin(theta) + y * math.cos(theta) + cy
            sx, sy = self.transform.world_to_screen(xr, yr)
            points.extend([sx, sy])
        self.canvas.create_line(points, fill="purple", smooth=True, width=1)

    def draw_core_of_inertia(self, props: SectionProperties):
        if not props.core or not props.core.polygon:
            return
        coords = []
        for x, y in props.core.polygon:
            sx, sy = self.transform.world_to_screen(x, y)
            coords.extend([sx, sy])
        self.canvas.create_polygon(coords, outline="orange", fill="", width=1, dash=(3, 3))

    def draw_dimensioning(self, geometry: SectionGeometry):
        minx, miny, maxx, maxy = geometry.bounding_box()
        sx0, sy0 = self.transform.world_to_screen(minx, miny)
        sx1, sy1 = self.transform.world_to_screen(maxx, miny)
        midy = (sy0 + sy1) / 2.0
        self.canvas.create_line(sx0, midy, sx1, midy, arrow="both")
        self.canvas.create_text(
            (sx0 + sx1) / 2.0, midy - 10, text=f"b = {maxx - minx:.2f} {geometry.units}"
        )

    def draw_radii_of_gyration(self, props: SectionProperties):
        if props.r1 and props.r2:
            theta = math.radians(props.theta_p_deg)
            cx, cy = props.x_c, props.y_c
            sx0, sy0 = self.transform.world_to_screen(cx, cy)
            sx1, sy1 = self.transform.world_to_screen(
                cx + props.r1 * math.cos(theta), cy + props.r1 * math.sin(theta)
            )
            self.canvas.create_line(sx0, sy0, sx1, sy1, fill="brown", width=2)
            self.canvas.create_oval(sx1 - 3, sy1 - 3, sx1 + 3, sy1 + 3, fill="brown")

    def draw_all(self, geometry: SectionGeometry, props: SectionProperties):
        self.clear()
        bbox = geometry.bounding_box()
        transform = SectionViewTransform(
            bbox, self.canvas.winfo_width(), self.canvas.winfo_height(), margin=20
        )
        self.set_transform(transform)
        self.draw_section_contour(geometry)
        self.draw_dimensioning(geometry)
        self.draw_centroid(props)
        self.draw_principal_axes(props)
        self.draw_radii_of_gyration(props)
        self.draw_inertia_ellipse(props)
        self.draw_core_of_inertia(props)
