import math

from sections_app.services.calculations import compute_transform


def test_compute_transform_scaling_and_offsets():
    width = 100.0
    height = 50.0
    canvas_w = 200
    canvas_h = 200

    t = compute_transform(width, height, canvas_w, canvas_h, padding=20)
    assert math.isclose(t.scale, 1.6, rel_tol=1e-9)
    assert math.isclose(t.offset_x, 20.0, rel_tol=1e-9)
    assert math.isclose(t.offset_y, 60.0, rel_tol=1e-9)


def _ellipse_points(a, b, angle_rad, n=360):
    pts = []
    ca = math.cos(angle_rad)
    sa = math.sin(angle_rad)
    for i in range(n):
        t = 2 * math.pi * i / n
        x = a * math.cos(t)
        y = b * math.sin(t)
        # rotate
        xr = x * ca - y * sa
        yr = x * sa + y * ca
        pts.append((xr, yr))
    return pts


def test_recover_rotation_from_ellipse_covariance():
    a = 5.0
    b = 2.0
    angle_deg = 33.0
    angle_rad = math.radians(angle_deg)

    pts = _ellipse_points(a, b, angle_rad, n=720)
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    n = len(pts)
    mx = sum(xs) / n
    my = sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs) / n
    syy = sum((y - my) ** 2 for y in ys) / n
    sxy = sum((x - mx) * (y - my) for x, y in pts) / n

    angle_est = 0.5 * math.atan2(2 * sxy, sxx - syy)
    angle_est_deg = math.degrees(angle_est) % 180.0

    assert abs(angle_est_deg - angle_deg) < 0.5  # within 0.5 degrees
