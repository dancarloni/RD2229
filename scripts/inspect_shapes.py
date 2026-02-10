import pathlib
import sys

ROOT = str(pathlib.Path(__file__).resolve().parents[1])
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
from apps.sections.models.sections import CSection, LSection, RectangularHollowSection, VSection
from apps.sections.section_calculations import _polygon_area_and_centroid, section_to_geometry

cases = [
    (CSection, dict(name="csh", width=10.0, height=8.0, flange_thickness=1.0, web_thickness=1.0)),
    (RectangularHollowSection, dict(name="rh", width=10.0, height=8.0, thickness=1.0)),
    (LSection, dict(name="l", width=8.0, height=8.0, t_horizontal=1.0, t_vertical=1.0)),
    (VSection, dict(name="v", width=10.0, height=8.0, thickness=1.0)),
]

for cls, kw in cases:
    sec = cls(**kw)
    old = sec.compute_properties()
    geom = section_to_geometry(sec)
    area_ext, cx_ext, cy_ext = _polygon_area_and_centroid(geom.exterior)
    area_holes = sum(_polygon_area_and_centroid(h)[0] for h in geom.holes) if geom.holes else 0.0
    total = area_ext - area_holes
    print(
        f"{cls.__name__}: old area={old.area}, geom area(ext={area_ext}, holes={area_holes}) total={total}"
    )
    print(" bbox", geom.bounding_box())
    print(" ext sample", geom.exterior[:8])
    if geom.holes:
        print(" holes sample", [h[:8] for h in geom.holes])
    print("---")
