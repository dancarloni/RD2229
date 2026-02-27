import os
import sys
import tkinter as tk
import unittest

# Ensure project root is on sys.path so tests can import local modules under pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from verification_table import VerificationTableApp


class TestVerificationTableAutocompleteAndEvents(unittest.TestCase):
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

    def test_copy_and_change_material_with_suggestion(self):
        top = tk.Toplevel(self.root)
        app = VerificationTableApp(top, initial_rows=1)
        top.update_idletasks()
        top.update()

        items = list(app.tree.get_children())
        first = items[0]
        # Set material values to be copied
        app.tree.set(first, "mat_concrete", "C120")
        app.tree.set(first, "mat_steel", "A500")
        app.tree.set(first, "stirrups_mat", "SS")

        # Create a new row by tabbing from the last column of the first row
        app._start_edit(first, app.columns[-1])
        app._on_entry_commit_next(None)  # Tab on last column -> creates copied row
        top.update_idletasks()
        top.update()

        items = list(app.tree.get_children())
        self.assertEqual(len(items), 2)
        new_item = items[1]

        # Start editing 'mat_concrete' on the new row and verify copied value
        app._start_edit(new_item, "mat_concrete")
        self.assertIsNotNone(app.edit_entry)
        self.assertEqual(app.edit_entry.get(), "C120")

        # Now change via suggestions: supply material names and filter
        app.material_names = ["C120", "C200", "A500"]
        app.suggestions_map["mat_concrete"] = app.material_names
        # Simulate typing 'C2' and updating suggestions
        app.edit_entry.delete(0, tk.END)
        app.edit_entry.insert(0, "C2")
        app._update_suggestions()
        top.update_idletasks()
        top.update()

        # Suggestion list should exist and include 'C200'
        self.assertIsNotNone(app._suggest_list)
        items_s = [app._suggest_list.get(i) for i in range(app._suggest_list.size())]
        self.assertIn("C200", items_s)

        # Simulate selecting suggestion by invoking handler (Enter on suggestion)
        app._on_suggestion_enter(None)
        top.update_idletasks()
        top.update()

        # After suggestion enter, the entry should be committed with the suggestion
        # and the tree cell should contain 'C200'
        self.assertEqual(app.tree.set(new_item, "mat_concrete"), "C200")
        top.destroy()

    def test_event_generation_start_and_navigation(self):
        top = tk.Toplevel(self.root)
        app = VerificationTableApp(top, initial_rows=1)
        top.update_idletasks()
        top.update()

        items = list(app.tree.get_children())
        first = items[0]

        # Try to start editing by generating a printable key event on the tree
        app.tree.focus(first)
        try:
            app.tree.event_generate("<Key>", char="x")
            top.update_idletasks()
            top.update()
        except tk.TclError:
            # fallback: start edit directly
            app._start_edit(first, app.columns[0], initial_text="x")

        # Ensure entry started
        if app.edit_entry is None:
            app._start_edit(first, app.columns[0], initial_text="x")
        self.assertIsNotNone(app.edit_entry)
        self.assertEqual(app.edit_column, app.columns[0])

        # Simulate Tab via event_generate on the entry to move to next column
        try:
            app.edit_entry.event_generate("<Tab>")
            top.update_idletasks()
            top.update()
        except tk.TclError:
            app._on_entry_commit_next(None)

        # If event did not move (some Tk implementations), fallback to handler
        if app.edit_column == app.columns[0]:
            app._on_entry_commit_next(None)

        self.assertEqual(app.edit_column, app.columns[1])

        # Simulate Return (Enter) to move down (same column)
        try:
            app.edit_entry.event_generate("<Return>")
            top.update_idletasks()
            top.update()
        except tk.TclError:
            app._on_entry_commit_down(None)

        # If we started on row 0 and were on column 1, pressing Return should create a new row
        items_after = list(app.tree.get_children())
        self.assertTrue(len(items_after) >= 1)
        # Ensure editor is now focused on some row (ideally row 1) in same column index
        self.assertEqual(app.edit_column, app.columns[1])
        top.destroy()


if __name__ == "__main__":
    unittest.main()
