"""Pure calculation module: compute centroid, inertia, principal axes, radii, core, ellipse.

No tkinter or GUI imports here.
"""

from __future__ import annotations
from math import atan2, degrees, sqrt, cos, sin, radians
from typing import Tuple

from sections_app.geometry_model import (
    SectionGeometry,
    SectionProperties,
    EllipseData,
    CoreData,
)

# Optional shapely support for robust geometry operations
try:
    from shapely.geometry import Polygon

    _HAS_SHAPELY = True
except Exception:  # pragma: no cover - shapely optional
    _HAS_SHAPELY = False


def _polygon_area_and_centroid(pts: list[tuple[float, float]]) -> tuple[float, float, float]:
    """Return (area, cx, cy) where area is positive polygon area and centroid cx,cy."""
    area2 = 0.0
    cx = 0.0
    cy = 0.0
    n = len(pts)
    for i in range(n):
        x0, y0 = pts[i]
        x1, y1 = pts[(i + 1) % n]
        cross = x0 * y1 - x1 * y0
        area2 += cross
        cx += (x0 + x1) * cross
        cy += (y0 + y1) * cross
    A = area2 / 2.0
    if abs(A) < 1e-12:
        return 0.0, 0.0, 0.0
    cx /= 6.0 * A
    cy /= 6.0 * A
    return abs(A), cx, cy


def compute_centroid(geom: SectionGeometry) -> tuple[float, float]:
    """Compute centroid (x_c, y_c) of polygon (accounts for holes as negative area)."""
    A_ext, cx_ext, cy_ext = _polygon_area_and_centroid(geom.exterior)
    total_area = A_ext
    weighted_x = A_ext * cx_ext
    weighted_y = A_ext * cy_ext
    for hole in geom.holes:
        Ah, cxh, cyh = _polygon_area_and_centroid(hole)
        total_area -= Ah
        weighted_x -= Ah * cxh
        weighted_y -= Ah * cyh
    if abs(total_area) < 1e-12:
        return 0.0, 0.0
    return weighted_x / total_area, weighted_y / total_area


def compute_inertia(
    geom: SectionGeometry, centroid: tuple[float, float]
) -> tuple[float, float, float]:
    """Compute Ix, Iy, Ixy about centroid, accounting for holes by subtraction."""
    cx, cy = centroid

    def poly_inertia_about_centroid(
        pts: list[tuple[float, float]], cx0: float, cy0: float
    ) -> tuple[float, float, float]:
        Ix = 0.0
        Iy = 0.0
        Ixy = 0.0
        n = len(pts)
        for i in range(n):
            x0, y0 = pts[i][0] - cx0, pts[i][1] - cy0
            x1, y1 = pts[(i + 1) % n][0] - cx0, pts[(i + 1) % n][1] - cy0
            cross = x0 * y1 - x1 * y0
            Ix += (y0**2 + y0 * y1 + y1**2) * cross
            Iy += (x0**2 + x0 * x1 + x1**2) * cross
            Ixy += (x0 * y1 + 2 * x0 * y0 + 2 * x1 * y1 + x1 * y0) * cross
        Ix = abs(Ix) / 12.0
        Iy = abs(Iy) / 12.0
        Ixy = abs(Ixy) / 24.0
        return Ix, Iy, Ixy

    # exterior contribution
    Ix_ext, Iy_ext, Ixy_ext = poly_inertia_about_centroid(geom.exterior, cx, cy)
    # subtract holes
    Ix_h = 0.0
    Iy_h = 0.0
    Ixy_h = 0.0
    for hole in geom.holes:
        ixh, iyh, ixyh = poly_inertia_about_centroid(hole, cx, cy)
        Ix_h += ixh
        Iy_h += iyh
        Ixy_h += ixyh
    return Ix_ext - Ix_h, Iy_ext - Iy_h, Ixy_ext - Ixy_h


def compute_principal_axes(Ix: float, Iy: float, Ixy: float) -> tuple[float, float, float]:
    """Compute principal moments I1, I2 and orientation theta_p in degrees."""
    avg = 0.5 * (Ix + Iy)
    diff = 0.5 * (Ix - Iy)
    R = sqrt(diff**2 + Ixy**2)
    I1 = avg + R
    I2 = avg - R
    theta = 0.5 * atan2(-2.0 * Ixy, (Iy - Ix))  # radians
    return I1, I2, degrees(theta)


def compute_radii_of_gyration(area: float, I1: float, I2: float) -> tuple[float, float]:
    if area <= 0:
        return 0.0, 0.0
    return (sqrt(I1 / area), sqrt(I2 / area))


def _point_in_polygon(x: float, y: float, poly: list[tuple[float, float]]) -> bool:
    """Ray casting point-in-polygon. Returns True if point is inside polygon or on edge."""
    inside = False
    n = len(poly)
    if n == 0:
        return False
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        intersect = ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi + 1e-24) + xi)
        if intersect:
            inside = not inside
        j = i
    return inside


def compute_core_of_inertia(geom: SectionGeometry, props: SectionProperties) -> CoreData:
    """Compute a robust approximate core polygon by scaling the exterior polygon

    Algorithm:
    - compute centroid (cx, cy)
    - try scaling vertices toward centroid by factor s in decreasing sequence (0.95 .. 0.1)
      and accept the first s where *all* scaled vertices are inside the exterior and not in holes.
    - fallback to inward fraction 0.2 if none found.
    """
    pts = geom.exterior
    if not pts:
        return CoreData(polygon=None)
    cx, cy = compute_centroid(geom)

    def vertices_scaled(s: float) -> list[tuple[float, float]]:
        return [(x + (cx - x) * s, y + (cy - y) * s) for x, y in pts]

    def all_inside(poly_pts: list[tuple[float, float]]) -> bool:
        # point must be inside exterior and not inside any hole
        for x, y in poly_pts:
            if not _point_in_polygon(x, y, geom.exterior):
                return False
            for hole in geom.holes:
                if _point_in_polygon(x, y, hole):
                    return False
        return True

    # try a sequence of scaling factors for robustness
    for s in [0.95, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2]:
        scaled = vertices_scaled(s)
        if all_inside(scaled):
            return CoreData(polygon=scaled)

    # fallback: small inward offset (previous behavior)
    alpha = 0.2
    core_poly = [(x + (cx - x) * alpha, y + (cy - y) * alpha) for x, y in pts]
    return CoreData(polygon=core_poly)


def compute_inertia_ellipse(props: SectionProperties) -> EllipseData:
    """Return ellipse semi-axes equivalent from I1, I2 (placeholder mapping)."""
    if props.area <= 0:
        return EllipseData(0.0, 0.0, props.theta_p_deg)
    a = sqrt(props.I1 / props.area) if props.I1 else 0.0
    b = sqrt(props.I2 / props.area) if props.I2 else 0.0
    return EllipseData(a=a, b=b, theta_deg=props.theta_p_deg)


# Convenience: convert Section (existing code model) to SectionGeometry
# to reuse this calculations module with existing Section objects.
from sections_app.models.sections import Section, RectangularSection, CircularSection


def section_to_geometry(section: Section) -> SectionGeometry:
    """Convert a Section instance (from sections_app.models.sections) into SectionGeometry.

    This is a pragmatic adapter; extend to other section types as needed.
    """
    st = section.section_type.upper()
    name = section.name
    if st == "RECTANGULAR" and hasattr(section, "width") and hasattr(section, "height"):
        b = float(getattr(section, "width"))
        h = float(getattr(section, "height"))
        geom = SectionGeometry.from_rectangle(
            b=b, h=h, rotation_deg=section.rotation_angle_deg, name=name
        )
        # apply rotation to points if necessary
        if abs(section.rotation_angle_deg) > 1e-9:
            theta = radians(section.rotation_angle_deg)
            pts = []
            for x, y in geom.exterior:
                xr = x * cos(theta) - y * sin(theta)
                yr = x * sin(theta) + y * cos(theta)
                pts.append((xr, yr))
            geom.exterior = pts
        return geom
    if st == "CIRCULAR" and hasattr(section, "diameter"):
        d = float(getattr(section, "diameter"))
        # approximate circle as polygon
        r = d / 2.0
        steps = 64
        pts = []
        for i in range(steps):
            ang = 2.0 * 3.141592653589793 * i / steps
            pts.append((r * cos(ang), r * sin(ang)))
        geom = SectionGeometry(exterior=pts, meta={"name": name, "type": "circular"})
        return geom
    # Fallback: try to use dimensions dict if present
    dims = getattr(section, "dimensions", None) or {}
    if dims.get("width") and dims.get("height"):
        b = float(dims.get("width"))
        h = float(dims.get("height"))
        return SectionGeometry.from_rectangle(
            b=b, h=h, rotation_deg=section.rotation_angle_deg, name=name
        )
    # last resort: tiny degenerate square
    return SectionGeometry.from_rectangle(1.0, 1.0, name=name)


def compute_section_properties_from_geometry(geom: SectionGeometry) -> SectionProperties:
    """High-level pipeline returning SectionProperties from SectionGeometry.

    If shapely is available, use it for robust area and centroid calculations and for
    improved core (offset) estimation.
    """
    # use shapely for area and centroid if available
    if _HAS_SHAPELY:
        try:
            ext = Polygon(geom.exterior, holes=geom.holes)
            area = float(ext.area)
            centroid = ext.centroid
            x_c, y_c = float(centroid.x), float(centroid.y)
        except Exception:  # pragma: no cover - fallback
            x_c, y_c = compute_centroid(geom)
            # compute area considering holes
            def poly_area(pts: list[tuple[float, float]]) -> float:
                area2 = 0.0
                for i in range(len(pts)):
                    x0, y0 = pts[i]
                    x1, y1 = pts[(i + 1) % len(pts)]
                    area2 += x0 * y1 - x1 * y0
                return abs(area2) / 2.0

            area_ext = poly_area(geom.exterior)
            area_holes = sum(poly_area(h) for h in geom.holes)
            area = area_ext - area_holes
    else:
        x_c, y_c = compute_centroid(geom)
        # compute area considering holes
        def poly_area(pts: list[tuple[float, float]]) -> float:
            area2 = 0.0
            for i in range(len(pts)):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % len(pts)]
                area2 += x0 * y1 - x1 * y0
            return abs(area2) / 2.0

        area_ext = poly_area(geom.exterior)
        area_holes = sum(poly_area(h) for h in geom.holes)
        area = area_ext - area_holes

    # inertia and principal axes
    Ix, Iy, Ixy = compute_inertia(geom, (x_c, y_c))
    I1, I2, theta_p = compute_principal_axes(Ix, Iy, Ixy)

    r1, r2 = compute_radii_of_gyration(area, I1, I2)
    props = SectionProperties(
        area=area,
        Ix=Ix,
        Iy=Iy,
        Ixy=Ixy,
        x_c=x_c,
        y_c=y_c,
        I1=I1,
        I2=I2,
        theta_p_deg=theta_p,
        r1=r1,
        r2=r2,
    )

    # improved core: if shapely available, try inner offset (buffer negative)
    if _HAS_SHAPELY:
        try:
            # choose offset distances as fractions of bbox diagonal
            minx, miny, maxx, maxy = geom.bounding_box()
            diag = ((maxx - minx) ** 2 + (maxy - miny) ** 2) ** 0.5
            from shapely.geometry import Polygon

            poly = Polygon(geom.exterior, holes=geom.holes)
            core_poly = None
            candidates = []
            # try a few inward offsets and collect valid candidate polygons
            for frac in [0.01, 0.02, 0.03, 0.05, 0.07, 0.1, 0.15, 0.2]:
                d = -frac * diag
                buf = poly.buffer(d)
                if buf.is_empty:
                    continue
                polys = []
                if buf.geom_type == "Polygon":
                    polys = [buf]
                else:
                    try:
                        polys = [p for p in buf.geoms if getattr(p, "area", 0.0) > 0]
                    except Exception:
                        continue
                # score candidates by area * solidity (area / convex hull area)
                for cand in polys:
                    try:
                        cand_area = float(cand.area)
                        hull = cand.convex_hull
                        hull_area = float(hull.area) if hull is not None else cand_area
                        if hull_area <= 0:
                            continue
                        solidity = cand_area / (hull_area + 1e-12)
                        # compactness (isoperimetric ratio): 4*pi*A / P^2
                        perim = float(cand.length)
                        compactness = (4.0 * 3.141592653589793 * cand_area) / (perim * perim + 1e-12)
                        # aspect ratio estimate from hull bbox
                        hx0, hy0, hx1, hy1 = hull.bounds
                        dx = hx1 - hx0
                        dy = hy1 - hy0
                        min_dim = min(dx, dy)
                        max_dim = max(dx, dy)
                        if min_dim <= 1e-12:
                            aspect = float('inf')
                        else:
                            aspect = max_dim / (min_dim + 1e-12)
                        aspect_factor = 1.0 / aspect if aspect > 0 and aspect != float('inf') else 0.0
                        # require a minimum area fraction of the original polygon
                        if cand_area < 0.005 * float(poly.area):
                            continue
                        # combined score: favor large, compact, and low-aspect candidates
                        score = cand_area * solidity * max(0.0, compactness) * max(1e-6, aspect_factor)
                        candidates.append((score, cand))
                    except Exception:
                        continue
            if candidates:
                # choose best scored candidate
                candidates.sort(key=lambda t: t[0], reverse=True)
                best = candidates[0][1]
                coords = list(best.exterior.coords)
                props.core = CoreData(polygon=[(float(x), float(y)) for x, y in coords])
            else:
                # fallback to previous heuristic
                props.core = compute_core_of_inertia(geom, props)
        except Exception:
            props.core = compute_core_of_inertia(geom, props)
    else:
        props.core = compute_core_of_inertia(geom, props)

    props.ellipse = compute_inertia_ellipse(props)
    return props


def compute_section_properties_from_section(section: Section) -> SectionProperties:
    geom = section_to_geometry(section)
    return compute_section_properties_from_geometry(geom)
