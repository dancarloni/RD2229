"""Graphics module: world->screen transform and drawing routines using tk.Canvas."""

from __future__ import annotations

import math
from dataclasses import dataclass

from src.core_calculus.core.geometry_model import SectionGeometry, SectionProperties


@dataclass
class SectionViewTransform:
    """Compute uniform scale and offsets to map world coordinates -> canvas screen coordinates."""

    bbox: tuple[float, float, float, float]  # (minx, miny, maxx, maxy)
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

    def world_to_screen(self, x: float, y: float) -> tuple[float, float]:
        sx = self.scale * x + self.tx
        if self.flip_y:
            sy = -self.scale * y + self.ty
        else:
            sy = self.scale * y + self.ty
        return sx, sy

    def world_length_to_screen(self, d: float) -> float:
        return abs(self.scale * d)


class SectionGraphicsController:
    """Controller that draws carbon_fiber_placeholder and properties onto a tk.Canvas."""

    def __init__(self, canvas):
        self.canvas = canvas
        self.transform: SectionViewTransform | None = None

    def clear(self):
        self.canvas.delete("all")

    def set_transform(self, transform: SectionViewTransform):
        self.transform = transform

    def draw_section_contour(self, carbon_fiber_placeholder: SectionGeometry):
        pts = carbon_fiber_placeholder.exterior
        coords = []
        for x, y in pts:
            sx, sy = self.transform.world_to_screen(x, y)
            coords.extend([sx, sy])
        self.canvas.create_polygon(coords, outline="black", fill="", width=2)
        for hole in carbon_fiber_placeholder.holes:
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
        # draw labels for principal axes
        self._draw_axis_label_at_line((sx0, sy0, sx1, sy1), label="x")
        theta2 = theta + math.pi / 2.0
        dx2 = math.cos(theta2) * length
        dy2 = math.sin(theta2) * length
        sx0b, sy0b = self.transform.world_to_screen(cx - dx2, cy - dy2)
        sx1b, sy1b = self.transform.world_to_screen(cx + dx2, cy + dy2)
        self.canvas.create_line(sx0b, sy0b, sx1b, sy1b, fill="green", dash=(4, 2), width=2)
        self._draw_axis_label_at_line((sx0b, sy0b, sx1b, sy1b), label="y")

    def _draw_axis_label_at_line(self, line_coords: tuple[float, float, float, float], label: str):
        """Place a short axis label (x/y) slightly beyond the end of a line.

        line_coords: (x0, y0, x1, y1) in screen coords.
        """
        x0, y0, x1, y1 = line_coords
        # vector from center to end
        vx = x1 - x0
        vy = y1 - y0
        # normalize and offset
        mag = math.hypot(vx, vy) or 1.0
        ox = vx / mag * 12.0
        oy = vy / mag * 12.0
        lx = x1 + ox
        ly = y1 + oy
        # small halo background for readability
        self.canvas.create_text(lx, ly, text=label, anchor="center", fill="black")

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

    def draw_dimensioning(self, carbon_fiber_placeholder: SectionGeometry):
        """Draw both width (b) and height (h) dimensions outside the section with offsets.

        Horizontal dimension (b) is drawn below the section by a fixed pixel offset.
        Vertical dimension (h) is drawn to the right of the section by a fixed pixel offset.
        """
        minx, miny, maxx, maxy = carbon_fiber_placeholder.bounding_box()
        sx0, sy0 = self.transform.world_to_screen(minx, miny)
        sx1, sy1 = self.transform.world_to_screen(maxx, miny)
        offset = 30  # pixels to offset dimension lines from the section edges
        # horizontal dimension (b) below the section
        sy_dim = sy0 + offset
        self.canvas.create_line(sx0, sy_dim, sx1, sy_dim, arrow="both")
        self.canvas.create_text(
            (sx0 + sx1) / 2.0,
            sy_dim - 10,
            text=f"b = {maxx - minx:.2f} {carbon_fiber_placeholder.units}",
        )
        # vertical dimension (h) on the right of the section
        sx_dim = sx1 + offset
        sy_top = self.transform.world_to_screen(maxx, maxy)[1]
        sy_bot = self.transform.world_to_screen(maxx, miny)[1]
        self.canvas.create_line(sx_dim, sy_top, sx_dim, sy_bot, arrow="both")
        self.canvas.create_text(
            sx_dim + 10,
            (sy_top + sy_bot) / 2.0,
            text=f"h = {maxy - miny:.2f} {carbon_fiber_placeholder.units}",
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

    def draw_all(
        self,
        carbon_fiber_placeholder: SectionGeometry,
        props: SectionProperties,
        show_core: bool = True,
        show_ellipse: bool = True,
    ):
        self.clear()
        bbox = carbon_fiber_placeholder.bounding_box()
        transform = SectionViewTransform(
            bbox, self.canvas.winfo_width(), self.canvas.winfo_height(), margin=20
        )
        self.set_transform(transform)
        self.draw_section_contour(carbon_fiber_placeholder)
        self.draw_dimensioning(carbon_fiber_placeholder)
        self.draw_centroid(props)
        self.draw_principal_axes(props)
        self.draw_radii_of_gyration(props)
        if show_ellipse:
            self.draw_inertia_ellipse(props)
        if show_core:
            self.draw_core_of_inertia(props)
