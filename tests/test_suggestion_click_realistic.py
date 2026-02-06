import unittest
import tkinter as tk
import sys
import os
import time

# Ensure project root is on sys.path so tests can import local modules under pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from verification_table import VerificationTableApp


class TestSuggestionClickRealistic(unittest.TestCase):
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

    def test_clicking_suggestion_applies_and_commits(self):
        top = tk.Toplevel(self.root)
        app = VerificationTableApp(top, initial_rows=1)
        top.update_idletasks()
        top.update()

        # prepare section names
        app.section_names = ["RealA", "RealB", "RealC"]
        app.suggestions_map["section"] = app.section_names

        first = list(app.tree.get_children())[0]

        # Start editing the empty section cell
        app._start_edit(first, "section")
        # Allow event loop to create suggestion box
        for _ in range(20):
            top.update_idletasks()
            top.update()
            time.sleep(0.01)

        # Ensure suggestions are present
        self.assertIsNotNone(app._suggest_box, "Suggestion box not created")
        self.assertIsNotNone(app._suggest_list, "Suggestion list not created")
        self.assertGreater(app._suggest_list.size(), 0, "Suggestion list empty")

        # Click (press+release) on the first suggestion in the listbox
        (lx, ly, lw, lh) = app._suggest_list.bbox(0)
        click_x = lx + lw // 2
        click_y = ly + lh // 2
        app._suggest_list.event_generate("<ButtonPress-1>", x=click_x, y=click_y)
        app._suggest_list.event_generate("<ButtonRelease-1>", x=click_x, y=click_y)

        # Process events so handler runs
        for _ in range(10):
            top.update_idletasks()
            top.update()
            time.sleep(0.01)

        # After clicking the suggestion the suggestion popup should be hidden
        self.assertIsNone(app._suggest_box, "Suggestion box still present after click")
        self.assertIsNone(app._suggest_list, "Suggestion list still present after click")

        # The selection may have been applied and committed immediately (focus out),
        # or may have left the editor open with the suggestion applied. Accept both.
        selected = "RealA"
        if app.edit_entry is None:
            # Editor already committed by focus-out; check tree cell
            self.assertEqual(app.tree.set(first, "section"), selected)
        else:
            # Editor still present: check entry content then commit immediately
            self.assertEqual(app.edit_entry.get(), selected)
            # Commit synchronously to avoid platform-specific event semantics
            app._commit_edit()
            top.update_idletasks()
            top.update()
            self.assertEqual(app.tree.set(first, "section"), selected)

        top.destroy()


if __name__ == '__main__':
    unittest.main()
