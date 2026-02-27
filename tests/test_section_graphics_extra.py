from apps.sections.section_graphics import SectionGraphicsController
from src.core_calculus.core.geometry_model import (
    CoreData,
    EllipseData,
    SectionGeometry,
    SectionProperties,
)
from src.core_calculus.section_calculations import compute_section_properties_from_geometry


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


def test_draw_inertia_ellipse_and_core_rendered_on_canvas():
    canvas = FakeCanvas(600, 400)
    geom = SectionGeometry.from_rectangle(10.0, 20.0, name="rect")
    props = SectionProperties(
        x_c=0.0,
        y_c=0.0,
        theta_p_deg=0.0,
        ellipse=EllipseData(a=3.0, b=1.5, theta_deg=30.0),
        core=CoreData(polygon=[(-3.0, -1.0), (3.0, -1.0), (3.0, 1.0), (-3.0, 1.0)]),
        r1=0.0,
        r2=0.0,
    )
    controller = SectionGraphicsController(canvas)

    controller.draw_all(geom, props, show_core=True, show_ellipse=True)

    # Expect an inertia ellipse drawn as a 'line' with purple fill and smooth=True
    found_ellipse = any(
        kind == "line" and call_kwargs.get("fill") == "purple" and call_kwargs.get("smooth")
        for kind, _args, call_kwargs in canvas.calls
    )
    assert found_ellipse

    # Expect a core polygon drawn with orange outline
    found_core = any(
        kind == "polygon" and call_kwargs.get("outline") == "orange" for kind, _args, call_kwargs in canvas.calls
    )
    assert found_core


def test_dimensioning_text_includes_units():
    canvas = FakeCanvas(500, 300)
    geom = SectionGeometry.from_rectangle(12.0, 6.0, name="rect")
    geom.units = "mm"
    props = compute_section_properties_from_geometry(geom)
    controller = SectionGraphicsController(canvas)

    controller.draw_all(geom, props)

    texts = [kw.get("text") for kind, _args, kw in canvas.calls if kind == "text"]
    # Expect b= and h= dimensioning strings with units
    assert any(isinstance(t, str) and "b =" in t and "mm" in t for t in texts)
    assert any(isinstance(t, str) and "h =" in t and "mm" in t for t in texts)


def test_principal_axes_and_labels_and_radii_drawn():
    canvas = FakeCanvas(400, 300)
    geom = SectionGeometry.from_rectangle(8.0, 6.0)
    props = SectionProperties(x_c=0.0, y_c=0.0, theta_p_deg=30.0, r1=1.2, r2=0.8)
    controller = SectionGraphicsController(canvas)

    controller.draw_all(geom, props)

    # principal axes lines: look for lines with blue and green fills
    has_blue = any(kind == "line" and kw.get("fill") == "blue" for kind, _args, kw in canvas.calls)
    has_green = any(kind == "line" and kw.get("fill") == "green" for kind, _args, kw in canvas.calls)
    assert has_blue and has_green

    # axis labels 'x' and 'y' should appear as create_text calls
    text_values = [kw.get("text") for kind, _args, kw in canvas.calls if kind == "text"]
    assert any(t == "x" for t in text_values)
    assert any(t == "y" for t in text_values)

    # radii of gyration drawn as a line + a small oval marker
    assert any(kind == "oval" for kind, _args, kw in canvas.calls)
    assert any(kind == "line" for kind, _args, kw in canvas.calls)
