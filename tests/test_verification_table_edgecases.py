import unittest
import tkinter as tk
import sys
import os

# Ensure project root is on sys.path so tests can import local modules under pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from verification_table import VerificationTableApp


class TestVerificationTableEdgeCases(unittest.TestCase):
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

    def test_shift_tab_wraps_to_previous_row_last_column(self):
        top = tk.Toplevel(self.root)
        app = VerificationTableApp(top, initial_rows=2)
        top.update_idletasks()
        top.update()

        items = list(app.tree.get_children())
        first, second = items[0], items[1]
        # Start editing second row, first column
        app._start_edit(second, app.columns[0])
        self.assertIsNotNone(app.edit_entry)
        # Simulate Shift-Tab -> should move to previous row last column
        app._on_entry_commit_prev(None)

        self.assertEqual(app.edit_item, first)
        self.assertEqual(app.edit_column, app.columns[-1])
        top.destroy()

    def test_home_end_open_first_and_last_column(self):
        top = tk.Toplevel(self.root)
        app = VerificationTableApp(top, initial_rows=1)
        top.update_idletasks()
        top.update()

        items = list(app.tree.get_children())
        first = items[0]
        # Focus first item and call home
        app.tree.focus(first)
        app._on_tree_home(None)
        self.assertIsNotNone(app.edit_entry)
        self.assertEqual(app.edit_column, app.columns[0])
        # Now call end
        app._on_tree_end(None)
        self.assertIsNotNone(app.edit_entry)
        self.assertEqual(app.edit_column, app.columns[-1])
        top.destroy()

    def test_shift_tab_applies_suggestion_and_moves_prev(self):
        top = tk.Toplevel(self.root)
        app = VerificationTableApp(top, initial_rows=1)
        top.update_idletasks()
        top.update()

        items = list(app.tree.get_children())
        first = items[0]
        # Start editing "mat_concrete" (column index 1)
        app._start_edit(first, 'mat_concrete')
        self.assertIsNotNone(app.edit_entry)
        # Provide suggestion source and type a query that filters
        app.material_names = ['C120', 'C200', 'A500']
        app.suggestions_map['mat_concrete'] = app.material_names
        app.edit_entry.delete(0, tk.END)
        app.edit_entry.insert(0, 'C2')
        app._update_suggestions()
        top.update_idletasks()
        top.update()

        self.assertIsNotNone(app._suggest_list)
        # Trigger Shift-Tab (apply suggestion then move to previous column)
        app._on_entry_commit_prev(None)
        # The suggestion should have been applied to the cell
        self.assertIn(app.tree.set(first, 'mat_concrete'), ['C120', 'C200'])
        # The editor should now be on the previous column (index 0)
        self.assertEqual(app.edit_column, app.columns[0])
        top.destroy()


if __name__ == '__main__':
    unittest.main()
