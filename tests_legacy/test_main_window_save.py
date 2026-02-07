import json
import tkinter as tk

import pytest

from sections_app.models.sections import RectangularSection
from sections_app.services.repository import CsvSectionSerializer, SectionRepository
from sections_app.ui.main_window import MainWindow


@pytest.mark.ui
@pytest.mark.slow
def test_main_window_save_creates_section_with_principals(tmp_path, monkeypatch):
    # Skip if no tkinter available
    try:
        root = tk.Tk()
        root.withdraw()
    except tk.TclError:
        pytest.skip("Tkinter not available (headless)")

    # Monkeypatch notification functions to avoid dialogs
    monkeypatch.setattr("sections_app.ui.main_window.notify_info", lambda *a, **k: None)
    monkeypatch.setattr("sections_app.ui.main_window.notify_error", lambda *a, **k: None)

    path = tmp_path / "repo.jsons"
    repo = SectionRepository(json_file=str(path))
    serializer = CsvSectionSerializer()

    mw = MainWindow(root, repo, serializer, material_repository=None)

    # Select rectangular type
    mw.section_var.set("Rettangolare")
    # Set name and inputs
    mw.name_entry.delete(0, tk.END)
    mw.name_entry.insert(0, "rect")
    mw.inputs["width"].delete(0, tk.END)
    mw.inputs["width"].insert(0, "4.0")
    mw.inputs["height"].delete(0, tk.END)
    mw.inputs["height"].insert(0, "2.0")

    # Call save - should compute properties and persist
    mw.save_section()

    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    assert len(data) == 1
    item = data[0]
    for key in ("I1", "I2", "principal_angle_deg", "principal_rx", "principal_ry"):
        assert key in item
        assert item[key] is not None
        assert isinstance(item[key], (int, float))

    # Cleanup
    mw.destroy()
    root.destroy()
