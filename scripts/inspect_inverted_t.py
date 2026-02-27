import pathlib
import sys

ROOT = str(pathlib.Path(__file__).resolve().parents[1])
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
from sections_app.models.sections import InvertedTSection
from sections_app.section_calculations import section_to_geometry

sec = InvertedTSection(name="it", flange_width=10.0, flange_thickness=2.0, web_thickness=1.0, web_height=8.0)
old = sec.compute_properties()
print("old area", old.area)
geom = section_to_geometry(sec)
print("bbox", geom.bounding_box())
print("exterior len", len(geom.exterior))
print("exterior sample", geom.exterior[:8])
from sections_app.section_calculations import _polygon_area_and_centroid

area, cx, cy = _polygon_area_and_centroid(geom.exterior)
print("shoelace area", area, "centroid", cx, cy)
try:
    from shapely.geometry import Polygon

    print("poly area", Polygon(geom.exterior).area)
except Exception as e:
    print("shapely not available", e)
