import unittest
import tkinter as tk

from sections_app.ui.module_selector import ModuleSelectorWindow
from verification_table import VerificationTableWindow, VerificationTableApp


class TestVerificationTableIntegration(unittest.TestCase):
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

    def test_select_suggestion_with_keyboard(self):
        # Create a small material repository via ModuleSelector wiring
        try:
            from core_models.materials import MaterialRepository, Material
        except Exception:
            self.skipTest("MaterialRepository not available")

        import tempfile
        from pathlib import Path
        tmpdir = tempfile.TemporaryDirectory()
        repo_path = Path(tmpdir.name) / "materials.json"
        repo = MaterialRepository(json_file=str(repo_path))
        # avoid writing files in quick succession on Windows by writing
        # directly to the in-memory storage
        repo.clear()
        m1 = Material(name="C120", type="concrete")
        m2 = Material(name="C123", type="concrete")
        m3 = Material(name="A500", type="steel")
        repo._materials[m1.id] = m1
        repo._materials[m2.id] = m2
        repo._materials[m3.id] = m3

        win = VerificationTableWindow(self.root, section_repository=None, material_repository=repo)
        app = win.app
        # Ensure UI is rendered
        self.root.update_idletasks()
        self.root.update()

        item = list(app.tree.get_children())[0]
        app._start_edit(item, "mat_concrete")
        # type "C12"
        app.edit_entry.delete(0, tk.END)
        app.edit_entry.insert(0, "C12")
        app._update_suggestions()
        self.root.update_idletasks()
        self.root.update()

        self.assertIsNotNone(app._suggest_list)
        # Simulate keyboard navigation: move down then press Enter
        app._on_entry_move_down(None)
        app._on_suggestion_enter(None)

        # The edited cell should now contain a selected material name
        val = app.tree.set(item, "mat_concrete")
        self.assertIn(val, ("C120", "C123"))

        # Confirm Enter moves focus/commits (commit_and_move behaviour preserved)
        # Start editing next cell and press Enter to commit and move down
        app._start_edit(item, "mat_steel")
        app.edit_entry.delete(0, tk.END)
        app.edit_entry.insert(0, "A500")
        app._update_suggestions()
        self.root.update_idletasks()
        self.root.update()
        # Press Enter to apply suggestion if available
        if app._suggest_list is not None:
            app._on_suggestion_enter(None)
        val2 = app.tree.set(item, "mat_steel")
        self.assertEqual(val2, "A500")

        win.destroy()

    def test_limits_parameterizable(self):
        # create many materials and set low limits
        try:
            from core_models.materials import MaterialRepository, Material
        except Exception:
            self.skipTest("MaterialRepository not available")

        import tempfile
        from pathlib import Path
        tmpdir = tempfile.TemporaryDirectory()
        repo_path = Path(tmpdir.name) / "materials.json"
        repo = MaterialRepository(json_file=str(repo_path))
        repo.clear()
        # Avoid file I/O during mass insertion by populating the in-memory map
        for i in range(100):
            m = Material(name=f"C{i:03}", type="concrete")
            repo._materials[m.id] = m

        # Use small display limit and small search limit
        win = VerificationTableWindow(self.root, section_repository=None, material_repository=repo)
        # set small limits on underlying app
        win.app.search_limit = 10
        win.app.display_limit = 5

        app = win.app
        # ensure UI layout is up-to-date before starting to edit
        self.root.update_idletasks()
        self.root.update()
        item = list(app.tree.get_children())[0]
        app._start_edit(item, "mat_concrete")
        app.edit_entry.delete(0, tk.END)
        app.edit_entry.insert(0, "C")
        app._update_suggestions()
        self.root.update_idletasks()
        self.root.update()

        # The suggestions list should be present and have at most display_limit items
        self.assertIsNotNone(app._suggest_list)
        self.assertLessEqual(app._suggest_list.size(), 5)

        win.destroy()


if __name__ == "__main__":
    unittest.main()
