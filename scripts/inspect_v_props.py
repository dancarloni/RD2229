import pathlib
import sys

ROOT = str(pathlib.Path(__file__).resolve().parents[1])
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
from sections_app.models.sections import VSection
from sections_app.section_calculations import compute_section_properties_from_section

sec = VSection(name="v", width=10.0, height=8.0, thickness=1.0)
old = sec.compute_properties()
new = compute_section_properties_from_section(sec)
print("old area", getattr(old, "area", None), "new area", new.area)
print(
    "old centroid",
    (getattr(old, "x_c", None), getattr(old, "y_c", None)),
    "new centroid",
    (new.x_c, new.y_c),
)
print("old Ix,Iy,Ixy", getattr(old, "Ix", None), getattr(old, "Iy", None), getattr(old, "Ixy", None))
print("new Ix,Iy,Ixy", new.Ix, new.Iy, new.Ixy)
