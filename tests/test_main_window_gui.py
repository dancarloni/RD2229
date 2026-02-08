import tkinter as tk
from pathlib import Path
from sections_app.ui.main_window import MainWindow


def test_save_and_load_section_via_gui(tmp_path: Path):
    try:
        root = tk.Tk()
    except tk.TclError:
        import pytest

        pytest.skip("Tk not available in this environment")
    root.withdraw()
    win = MainWindow(master=root)
    # ensure saved path is in tmp
    win._saved_path = tmp_path / "saved_sections.csv"
    # set form values: ensure type is rectangular
    try:
        win.section_var.set("Rettangolare")
        win._create_inputs()
    except Exception:
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
    # save
    win._save_current_section()
    # repopulate list and check
    win._populate_saved_list()
    assert win.saved_listbox.size() >= 1
    # cleanup
    win.destroy()
    root.destroy()


def test_show_graphic_creates_canvas_items():
    root = tk.Tk()
    root.withdraw()
    win = MainWindow(master=root)
    # set inputs
    try:
        win.section_var.set("Rettangolare")
        win._create_inputs()
    except Exception:
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
