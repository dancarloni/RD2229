import os
import sys
import tkinter as tk
import unittest

# Ensure project root is on sys.path so tests can import local modules under pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tkinter import ttk

from verification_table import VerificationTableApp


class TestVerificationTableCombobox(unittest.TestCase):
    def setUp(self) -> None:
        try:
            self.root = tk.Tk()
            self.root.withdraw()
        except tk.TclError:
            self.skipTest("Tkinter not available in this environment")

    def tearDown(self) -> None:
        try:
            self.root.destroy()
        except Exception:
            pass

    def test_combobox_used_for_material_columns(self):
        top = tk.Toplevel(self.root)
        app = VerificationTableApp(top, initial_rows=1)
        # Provide material names so combobox is chosen
        app.material_names = ["C120", "C200"]
        # start edit on mat_concrete
        items = list(app.tree.get_children())
        first = items[0]
        top.update_idletasks()
        top.update()
        app._start_edit(first, "mat_concrete")
        self.assertIsNotNone(app.edit_entry)
        self.assertIsInstance(app.edit_entry, ttk.Combobox)
        # Combobox should show current value (empty by default)
        self.assertEqual(app.edit_entry.get(), "")
        top.destroy()

    def test_combobox_commit_and_move_down_creates_row_and_keeps_column(self):
        top = tk.Toplevel(self.root)
        app = VerificationTableApp(top, initial_rows=1)
        app.material_names = ["C120", "C200"]
        items = list(app.tree.get_children())
        first = items[0]
        top.update_idletasks()
        top.update()

        # Start edit on mat_concrete and set value to C200
        app._start_edit(first, "mat_concrete")
        cb = app.edit_entry
        cb.set("C200")
        # Press Enter to move down (commit + same column next row)
        app._on_entry_commit_down(None)

        items = list(app.tree.get_children())
        self.assertEqual(len(items), 2)
        new_item = items[1]
        # New row should have C200 in the same column
        self.assertEqual(app.tree.set(new_item, "mat_concrete"), "C200")
        # Editor should be open on new item's same column
        self.assertEqual(app.edit_item, new_item)
        self.assertEqual(app.edit_column, "mat_concrete")
        top.destroy()

    def test_combobox_tab_moves_to_next_column(self):
        top = tk.Toplevel(self.root)
        app = VerificationTableApp(top, initial_rows=1)
        app.material_names = ["C120", "C200"]
        items = list(app.tree.get_children())
        first = items[0]
        top.update_idletasks()
        top.update()

        app._start_edit(first, "mat_concrete")
        cb = app.edit_entry
        cb.set("C120")
        # Tab to next column
        app._on_entry_commit_next(None)
        self.assertEqual(app.edit_column, app.columns[app.columns.index("mat_concrete") + 1])
        top.destroy()


if __name__ == "__main__":
    unittest.main()
