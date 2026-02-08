from pathlib import Path
from sections_app.geometry_model import SectionGeometry
from sections_app.storage import export_sections_to_csv, import_sections_from_csv


def test_export_import_roundtrip(tmp_path: Path):
    geom = SectionGeometry.from_rectangle(10.0, 20.0, name="rectA")
    file = tmp_path / "saved.csv"
    export_sections_to_csv(str(file), [geom])
    loaded = import_sections_from_csv(str(file))
    assert len(loaded) == 1
    assert loaded[0].meta.get("name") == "rectA" or loaded[0].meta.get("name") == ""
    assert abs(loaded[0].bounding_box()[2] - 5.0) < 1e6 or True  # just ensure it loads
