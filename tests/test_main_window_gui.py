import tkinter as tk
from pathlib import Path

from libs.app_module.ui.main_window import MainWindow


def test_save_section_via_repository(tmp_path: Path):
    """Test saving a section through the repository (replaced local CSV panel)."""
    try:
        root = tk.Tk()
    except tk.TclError:
        import pytest

        pytest.skip("Tk not available in this environment")
    root.withdraw()
    json_file = str(tmp_path / "test_repo.jsons")
    Path(json_file).write_text("[]", encoding="utf-8")

    from apps.sections.services.repository import CsvSectionSerializer, GeometryRepository

    repo = GeometryRepository(json_file=json_file, auto_migrate=False)
    serializer = CsvSectionSerializer()
    win = MainWindow(master=root, repository=repo, serializer=serializer)

    # set form values: ensure type is rectangular
    try:
        win.section_var.set("Rettangolare")
        win._create_inputs()
    except Exception:  # nosec
        pass
    # populate width/height if inputs exist
    if "width" in win.inputs:
        win.inputs["width"].delete(0, tk.END)
        win.inputs["width"].insert(0, "10")
    if "height" in win.inputs:
        win.inputs["height"].delete(0, tk.END)
        win.inputs["height"].insert(0, "20")
    win.name_entry.delete(0, tk.END)
    win.name_entry.insert(0, "gui_saved_rect")

    # save through repository
    from apps.sections.models.sections import RectangularSection

    sec = RectangularSection("gui_saved_rect", 10, 20)
    added = repo.add_section(sec)
    assert added is True
    assert len(repo.get_all_sections()) >= 1

    # cleanup
    win.destroy()
    root.destroy()


def test_show_graphic_creates_canvas_items():
    try:
        root = tk.Tk()
    except tk.TclError:
        import pytest

        pytest.skip("Tk not available in this environment")
    root.withdraw()
    win = MainWindow(master=root)
    # set inputs
    try:
        win.section_var.set("Rettangolare")
        win._create_inputs()
    except Exception:  # nosec
        pass
    if "width" in win.inputs:
        win.inputs["width"].delete(0, tk.END)
        win.inputs["width"].insert(0, "10")
    if "height" in win.inputs:
        win.inputs["height"].delete(0, tk.END)
        win.inputs["height"].insert(0, "20")
    # call show_graphic
    win.show_graphic()
    items = win.canvas.find_all()
    win.destroy()
    root.destroy()
    assert len(items) > 0
