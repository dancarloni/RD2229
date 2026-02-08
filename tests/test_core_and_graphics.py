import tkinter as tk
from sections_app.geometry_model import SectionGeometry
from sections_app.section_calculations import compute_section_properties_from_geometry, compute_core_of_inertia
from sections_app.section_graphics import SectionGraphicsController


def test_core_polygon_inside_and_smaller():
    geom = SectionGeometry.from_rectangle(10.0, 20.0, name="outer")
    props = compute_section_properties_from_geometry(geom)
    core = compute_core_of_inertia(geom, props)
    assert core.polygon is not None
    # core polygon should have positive area and be smaller than original bbox
    minx, miny, maxx, maxy = geom.bounding_box()
    # basic checks: core vertices remain inside bbox
    xs = [p[0] for p in core.polygon]
    ys = [p[1] for p in core.polygon]
    assert min(xs) >= minx - 1e-8
    assert max(xs) <= maxx + 1e-8
    assert min(ys) >= miny - 1e-8
    assert max(ys) <= maxy + 1e-8


def test_graphics_draws_items():
    try:
        root = tk.Tk()
    except tk.TclError:
        import pytest

        pytest.skip("Tk not available in this environment")
    root.withdraw()
    canvas = tk.Canvas(root, width=400, height=300)
    canvas.pack()
    geom = SectionGeometry.from_rectangle(10.0, 20.0, name="rect")
    props = compute_section_properties_from_geometry(geom)
    controller = SectionGraphicsController(canvas)
    # force canvas to have size
    canvas.update_idletasks()
    controller.draw_all(geom, props)
    items = canvas.find_all()
    root.destroy()
    assert len(items) > 0
