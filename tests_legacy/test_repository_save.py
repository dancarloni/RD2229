import json

from sections_app.models.sections import RectangularSection
from sections_app.services.repository import SectionRepository


def test_repository_save_includes_principal_fields(tmp_path):
    path = tmp_path / "repo.jsons"
    repo = SectionRepository(json_file=str(path))

    rect = RectangularSection(name="rect", width=4.0, height=2.0)
    added = repo.add_section(rect)
    assert added

    # Read file and assert keys exist
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    assert isinstance(data, list)
    assert len(data) == 1
    item = data[0]

    for key in ("I1", "I2", "principal_angle_deg", "principal_rx", "principal_ry"):
        assert key in item
        assert item[key] is not None
        assert isinstance(item[key], (int, float))
