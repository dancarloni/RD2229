import os
import sys
import tkinter as tk
import unittest

# Ensure project root is on sys.path so tests can import local modules under pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from verification_table import VerificationTableApp


class TestVerificationTableSuggestionsOnEmpty(unittest.TestCase):
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

    def _suggestion_list_items(self, app):
        if app._suggest_list is None:
            return []
        return [app._suggest_list.get(i) for i in range(app._suggest_list.size())]

    def test_empty_section_shows_all_sections(self):
        top = tk.Toplevel(self.root)
        app = VerificationTableApp(top, initial_rows=1)
        top.update_idletasks()
        top.update()

        # prepare section names
        app.section_names = ["SecA", "SecB", "SecC"]
        app.suggestions_map["section"] = app.section_names

        items = list(app.tree.get_children())
        first = items[0]

        # Start editing an empty section cell
        app._start_edit(first, "section")
        top.update_idletasks()
        top.update()

        items_s = self._suggestion_list_items(app)
        self.assertTrue(len(items_s) >= 3)
        for s in ["SecA", "SecB", "SecC"]:
            self.assertIn(s, items_s)
        top.destroy()

    def test_empty_mat_concrete_shows_all_concrete_materials(self):
        top = tk.Toplevel(self.root)
        app = VerificationTableApp(top, initial_rows=1)
        top.update_idletasks()
        top.update()

        # prepare material names containing concrete only
        app.material_names = ["C120", "C200"]
        # Use a static suggestion source for concrete materials to avoid
        # dependency on repository-backed helpers in test environment
        app.suggestions_map["mat_concrete"] = app.material_names
        items = list(app.tree.get_children())
        first = items[0]

        # Start editing mat_concrete cell
        app._start_edit(first, "mat_concrete")
        top.update_idletasks()
        top.update()

        items_s = self._suggestion_list_items(app)
        self.assertTrue(len(items_s) >= 2)
        self.assertIn("C120", items_s)
        self.assertIn("C200", items_s)
        top.destroy()

    def test_empty_mat_steel_shows_all_steel_materials(self):
        top = tk.Toplevel(self.root)
        app = VerificationTableApp(top, initial_rows=1)
        top.update_idletasks()
        top.update()

        # prepare material names containing steel only
        app.material_names = ["A500", "A600"]
        # Use static suggestion source for steel
        app.suggestions_map["mat_steel"] = app.material_names
        items = list(app.tree.get_children())
        first = items[0]

        # Start editing mat_steel cell
        app._start_edit(first, "mat_steel")
        top.update_idletasks()
        top.update()

        items_s = self._suggestion_list_items(app)
        self.assertTrue(len(items_s) >= 2)
        self.assertIn("A500", items_s)
        self.assertIn("A600", items_s)
        top.destroy()

    def test_empty_stirrups_mat_shows_all_steel_materials(self):
        top = tk.Toplevel(self.root)
        app = VerificationTableApp(top, initial_rows=1)
        top.update_idletasks()
        top.update()

        # prepare material names containing steel only
        app.material_names = ["A500", "A600"]
        # Use static suggestion source for stirrups materials (steel)
        app.suggestions_map["stirrups_mat"] = app.material_names
        items = list(app.tree.get_children())
        first = items[0]

        # Start editing stirrups_mat cell
        app._start_edit(first, "stirrups_mat")
        top.update_idletasks()
        top.update()

        items_s = self._suggestion_list_items(app)
        self.assertTrue(len(items_s) >= 2)
        self.assertIn("A500", items_s)
        self.assertIn("A600", items_s)
        top.destroy()


if __name__ == "__main__":
    unittest.main()
