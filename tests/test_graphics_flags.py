import tkinter as tk

import pytest

from apps.sections.geometry_model import SectionGeometry
from apps.sections.section_calculations import compute_section_properties_from_geometry
from apps.sections.section_graphics import SectionGraphicsController


def test_draw_all_flags_affect_items():
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("Tk not available in this environment")
    root.withdraw()
    canvas = tk.Canvas(root, width=400, height=300)
    canvas.pack()
    geom = SectionGeometry.from_rectangle(10.0, 20.0, name="rect")
    props = compute_section_properties_from_geometry(geom)
    controller = SectionGraphicsController(canvas)
    canvas.update_idletasks()
    controller.draw_all(geom, props, show_core=False, show_ellipse=False)
    items_no_core = canvas.find_all()
    canvas.delete("all")
    controller.draw_all(geom, props, show_core=True, show_ellipse=True)
    items_with_core = canvas.find_all()
    root.destroy()
    assert len(items_with_core) >= len(items_no_core)
    # Expect at least one extra item when enabling core/ellipse (conservative)
    assert len(items_with_core) - len(items_no_core) >= 1
