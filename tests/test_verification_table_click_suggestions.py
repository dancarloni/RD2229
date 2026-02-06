import unittest
import tkinter as tk
import sys
import os

# Ensure project root is on sys.path so tests can import local modules under pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from verification_table import VerificationTableApp


class TestVerificationTableClickSuggestions(unittest.TestCase):
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

    def test_focusin_shows_suggestions_for_section(self):
        top = tk.Toplevel(self.root)
        app = VerificationTableApp(top, initial_rows=1)
        top.update_idletasks()
        top.update()

        # prepare section names
        app.section_names = ["SecA", "SecB"]
        app.suggestions_map["section"] = app.section_names

        first = list(app.tree.get_children())[0]

        # Start editing the section cell (as would happen on click) and then
        # simulate the Entry receiving focus which should trigger suggestions.
        app._start_edit(first, "section")
        top.update_idletasks()
        top.update()

        # Simulate the focus in event that occurs when the user clicks the cell
        app.edit_entry.event_generate("<FocusIn>")
        top.update_idletasks()
        top.update()

        items = self._suggestion_list_items(app)
        self.assertTrue(len(items) >= 2)
        self.assertIn("SecA", items)
        self.assertIn("SecB", items)
        top.destroy()


if __name__ == '__main__':
    unittest.main()
