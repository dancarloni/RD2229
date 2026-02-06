import unittest
import tkinter as tk
import sys
import os
import time

# Ensure project root is on sys.path so tests can import local modules under pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from verification_table import VerificationTableApp


class TestSuggestionPersistence(unittest.TestCase):
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

    def test_suggestions_stay_open_until_selection(self):
        top = tk.Toplevel(self.root)
        app = VerificationTableApp(top, initial_rows=1)
        top.update_idletasks()
        top.update()

        app.section_names = ["S1", "S2", "S3"]
        app.suggestions_map["section"] = app.section_names

        first = list(app.tree.get_children())[0]

        # Start editing the empty section cell (as when moving to it)
        app._start_edit(first, "section")
        # Allow event loop to process suggestion creation
        for _ in range(10):
            top.update_idletasks()
            top.update()
            time.sleep(0.01)

        # The suggestion list should be present and non-empty
        self.assertIsNotNone(app._suggest_box, "Suggestion box not created")
        self.assertIsNotNone(app._suggest_list, "Suggestion list not created")
        self.assertGreater(app._suggest_list.size(), 0, "Suggestion list empty")

        # Wait a bit longer and re-check: the popup should still be present
        for _ in range(20):
            top.update_idletasks()
            top.update()
            time.sleep(0.01)
        self.assertIsNotNone(app._suggest_box, "Suggestion box disappeared prematurely")
        self.assertIsNotNone(app._suggest_list, "Suggestion list disappeared prematurely")
        self.assertGreater(app._suggest_list.size(), 0, "Suggestion list empty after delay")

        # Now simulate selecting a suggestion via click
        app._on_suggestion_click(None)
        top.update_idletasks()
        top.update()

        # After selection the suggestions should be hidden
        self.assertIsNone(app._suggest_box, "Suggestion box still present after selection")
        self.assertIsNone(app._suggest_list, "Suggestion list still present after selection")

        top.destroy()


if __name__ == '__main__':
    unittest.main()
