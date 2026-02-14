import pathlib
import sys

ROOT = str(pathlib.Path(__file__).resolve().parents[1])
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
from apps.sections.models.sections import LSection  # noqa: E402
from src.core_calculus.section_calculations import (  # noqa: E402
    compute_section_properties_from_section,
    section_to_geometry,
)

sec = LSection(name="l", width=8.0, height=8.0, t_horizontal=1.0, t_vertical=1.0)
old = sec.compute_properties()
geom = section_to_geometry(sec)
print("geom exterior", geom.exterior)
print("old centroid", old.centroid_x, old.centroid_y)
new = compute_section_properties_from_section(sec)
minx, miny, _, _ = geom.bounding_box()
print("new centroid corner coords", new.x_c - minx, new.y_c - miny)
