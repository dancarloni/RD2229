from sections_app.ui.verification_comparator import VerificationComparatorWindow


def polygon_area(poly):
    # shoelace formula
    if not poly:
        return 0.0
    area = 0.0
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i+1) % n]
        area += x1 * y2 - x2 * y1
    return abs(area) / 2.0


def test_compute_na_endpoints_horizontal():
    b, h = 30.0, 50.0
    p = (15.0, 10.0)
    e1, e2 = VerificationComparatorWindow._compute_na_endpoints(b, h, p, 0.0)
    # endpoints should lie on y == 10 and x in [0,b]
    assert abs(e1[1] - 10.0) < 1e-6
    assert 0.0 - 1e-6 <= e1[0] <= b + 1e-6
    assert abs(e2[1] - 10.0) < 1e-6
    assert 0.0 - 1e-6 <= e2[0] <= b + 1e-6


def test_compute_shaded_polygon_has_area():
    b, h = 30.0, 50.0
    p = (15.0, 10.0)
    poly = VerificationComparatorWindow._compute_shaded_polygon(b, h, p, 0.0)
    area = polygon_area(poly)
    assert area > 0.0


def test_shaded_polygon_prefers_top_or_bottom_based_on_stresses():
    class FakeRes:
        pass
    b, h = 30.0, 50.0
    # Top compression (sigma_c_max larger)
    r_top = FakeRes()
    r_top.sigma_c_max = 5.0
    r_top.sigma_c_min = -1.0
    r_top.asse_neutro = 10.0
    r_top.inclinazione_asse_neutro = 0.0
    poly_top = VerificationComparatorWindow._compute_shaded_polygon(b, h, (b/2.0, r_top.asse_neutro), r_top.inclinazione_asse_neutro, pick_side_point=(b/2.0,0.0))
    # top center should be inside the polygon
    def point_in_poly(x,y,poly):
        inside = False
        n = len(poly)
        for i in range(n):
            xi, yi = poly[i]
            xj, yj = poly[(i+1)%n]
            intersect = ((yi>y) != (yj>y)) and (x < (xj-xi) * (y-yi) / (yj-yi+1e-12) + xi)
            if intersect:
                inside = not inside
        return inside
    assert point_in_poly(b/2.0, 0.0, poly_top)
    # Bottom compression (sigma_c_min larger magnitude)
    r_bot = FakeRes()
    r_bot.sigma_c_max = 1.0
    r_bot.sigma_c_min = -8.0
    r_bot.asse_neutro = 10.0
    r_bot.inclinazione_asse_neutro = 0.0
    poly_bot = VerificationComparatorWindow._compute_shaded_polygon(b, h, (b/2.0, r_bot.asse_neutro), r_bot.inclinazione_asse_neutro, pick_side_point=(b/2.0,h))
    assert point_in_poly(b/2.0, h, poly_bot)


def test_compute_na_endpoints_diagonal():
    b, h = 30.0, 50.0
    p = (10.0, 20.0)
    e1, e2 = VerificationComparatorWindow._compute_na_endpoints(b, h, p, 30.0)
    # endpoints should be on rectangle boundary
    def on_edge(pt):
        x, y = pt
        return abs(x - 0.0) < 1e-6 or abs(x - b) < 1e-6 or abs(y - 0.0) < 1e-6 or abs(y - h) < 1e-6
    assert on_edge(e1)
    assert on_edge(e2)