from apps.sections.section_graphics import SectionGraphicsController
from src.core_calculus.core.geometry_model import SectionGeometry, SectionProperties


class FakeCanvas:
    def __init__(self, width=400, height=300):
        self._width = width
        self._height = height
        self.calls = []

    def create_polygon(self, coords, **kwargs):
        self.calls.append(("polygon", tuple(coords), kwargs))
        return 1

    def create_oval(self, *args, **kwargs):
        self.calls.append(("oval", args, kwargs))
        return 2

    def create_text(self, *args, **kwargs):
        self.calls.append(("text", args, kwargs))
        return 3

    def create_line(self, *args, **kwargs):
        self.calls.append(("line", args, kwargs))
        return 4

    def delete(self, _):
        self.calls.append(("delete", (), {}))

    def winfo_width(self):
        return self._width

    def winfo_height(self):
        return self._height


def test_draw_all_uses_expected_canvas_methods():
    canvas = FakeCanvas(500, 400)
    geom = SectionGeometry.from_rectangle(10.0, 20.0, name="rect")
    props = SectionProperties(x_c=0.0, y_c=0.0, theta_p_deg=0.0, ellipse=None, core=None, r1=0.0, r2=0.0)
    controller = SectionGraphicsController(canvas)

    controller.draw_all(geom, props)

    kinds = {c[0] for c in canvas.calls}
    # Expect at least these primitives to be used by draw_all
    assert "polygon" in kinds
    assert "line" in kinds
    assert "text" in kinds
    # centroid drawn as an oval
    assert "oval" in kinds
