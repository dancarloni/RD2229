import tkinter as tk
from pathlib import Path

from sections_app.models.sections import RectangularSection
from sections_app.services.repository import CsvSectionSerializer, GeometryRepository
from sections_app.ui.main_window import MainWindow


def test_save_multiple_edit_and_delete(tmp_path: Path):
    """Test CRUD operations through the repository (replaced local CSV panel)."""
    try:
        root = tk.Tk()
    except tk.TclError:
        import pytest

        pytest.skip("Tk not available in this environment")
    root.withdraw()
    json_file = str(tmp_path / "test_repo.jsons")
    Path(json_file).write_text("[]", encoding="utf-8")

    repo = GeometryRepository(json_file=json_file, auto_migrate=False)
    serializer = CsvSectionSerializer()
    win = MainWindow(master=root, repository=repo, serializer=serializer)

    # Save first section via repository
    sec1 = RectangularSection("rect1", 10, 20)
    assert repo.add_section(sec1) is True

    # Save second section via repository
    sec2 = RectangularSection("rect2", 5, 8)
    assert repo.add_section(sec2) is True

    # Check two sections exist
    assert len(repo.get_all_sections()) >= 2

    # Update second section
    updated = RectangularSection("rect2_updated", 6, 8)
    repo.update_section(sec2.id, updated)
    found = repo.find_by_id(sec2.id)
    assert found is not None
    assert found.name == "rect2_updated"

    # Delete first section
    deleted = repo.delete_section(sec1.id)
    assert deleted is True
    assert repo.find_by_id(sec1.id) is None

    # Verify load_section_into_form works with remaining section
    remaining = repo.find_by_id(sec2.id)
    if remaining:
        win.load_section_into_form(remaining)
        assert win.editing_section_id == sec2.id

    win.destroy()
    root.destroy()
