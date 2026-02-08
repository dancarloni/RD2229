import tkinter as tk
from pathlib import Path
from sections_app.ui.main_window import MainWindow


def test_save_multiple_edit_and_delete(tmp_path: Path):
    try:
        root = tk.Tk()
    except tk.TclError:
        import pytest

        pytest.skip("Tk not available in this environment")
    root.withdraw()
    win = MainWindow(master=root)
    win._saved_path = tmp_path / "saved_sections.csv"

    # Save first section
    win.section_var.set("Rettangolare")
    win._create_inputs()
    if "width" in win.inputs:
        win.inputs["width"].delete(0, tk.END)
        win.inputs["width"].insert(0, "10")
    if "height" in win.inputs:
        win.inputs["height"].delete(0, tk.END)
        win.inputs["height"].insert(0, "20")
    win.name_entry.delete(0, tk.END)
    win.name_entry.insert(0, "rect1")
    win._save_current_section()

    # Save second section
    win.inputs["width"].delete(0, tk.END)
    win.inputs["width"].insert(0, "5")
    win.inputs["height"].delete(0, tk.END)
    win.inputs["height"].insert(0, "8")
    win.name_entry.delete(0, tk.END)
    win.name_entry.insert(0, "rect2")
    win._save_current_section()

    # refresh and check two items
    win._populate_saved_list()
    assert win.saved_listbox.size() == 2

    # select second, load and edit
    win.saved_listbox.selection_clear(0, tk.END)
    win.saved_listbox.selection_set(1)
    win._load_selected_section()
    assert win.name_entry.get() == "rect2"
    # edit fields
    if "width" in win.inputs:
        win.inputs["width"].delete(0, tk.END)
        win.inputs["width"].insert(0, "6")
    win._update_selected_saved()

    # reload and ensure updated
    win._populate_saved_list()
    win.saved_listbox.selection_clear(0, tk.END)
    win.saved_listbox.selection_set(1)
    win._load_selected_section()
    if "width" in win.inputs:
        # numeric comparison to be robust to '6' vs '6.0' string formatting
        assert abs(float(win.inputs["width"].get()) - 6.0) < 1e-9

    # delete first
    win.saved_listbox.selection_clear(0, tk.END)
    win.saved_listbox.selection_set(0)
    win._delete_selected_saved()
    win._populate_saved_list()
    assert win.saved_listbox.size() == 1

    win.destroy()
    root.destroy()
