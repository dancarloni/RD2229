import unittest
import tkinter as tk
import sys
import os

# Ensure project root is on sys.path so tests can import local modules under pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from verification_table import VerificationTableApp


class TestVerificationTableNavigation(unittest.TestCase):
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

    def _values_for_item(self, app, item):
        return list(app.tree.item(item, "values"))

    def test_tab_on_last_column_creates_row_and_moves_to_first_column(self):
        top = tk.Toplevel(self.root)
        app = VerificationTableApp(top, initial_rows=1)
        top.update_idletasks()
        top.update()

        items = list(app.tree.get_children())
        self.assertEqual(len(items), 1)
        first = items[0]
        # set distinct values on the first row to check copying
        for col_idx, col in enumerate(app.columns):
            app.tree.set(first, col, f"val{col_idx}")

        # start editing the last column
        last_col = app.columns[-1]
        app._start_edit(first, last_col)
        # simulate Tab press (commit next)
        app._on_entry_commit_next(None)

        items = list(app.tree.get_children())
        # new row created
        self.assertEqual(len(items), 2)
        new_item = items[1]
        # editor opened on first column of new item
        self.assertEqual(app.edit_item, new_item)
        self.assertEqual(app.edit_column, app.columns[0])
        # values copied
        copied = self._values_for_item(app, new_item)
        original = [f"val{i}" for i in range(len(app.columns))]
        self.assertEqual(copied, original)
        top.destroy()

    def test_tab_on_last_column_moves_to_existing_next_row_if_present(self):
        top = tk.Toplevel(self.root)
        app = VerificationTableApp(top, initial_rows=2)
        top.update_idletasks()
        top.update()

        items = list(app.tree.get_children())
        self.assertEqual(len(items), 2)
        first, second = items[0], items[1]
        # set a marker on second row to ensure we moved to it
        app.tree.set(second, app.columns[0], "SECOND_START")

        # start editing the last column of the first row
        last_col = app.columns[-1]
        app._start_edit(first, last_col)
        # Tab should move to first cell of the next existing row (second)
        app._on_entry_commit_next(None)

        # ensure we did not create a new row
        items2 = list(app.tree.get_children())
        self.assertEqual(len(items2), 2)
        # editor opened on first column of second row
        self.assertEqual(app.edit_item, second)
        self.assertEqual(app.edit_column, app.columns[0])
        self.assertEqual(app.tree.set(second, app.columns[0]), "SECOND_START")
        top.destroy()

    def test_enter_advances_same_column_creates_row_if_needed(self):
        top = tk.Toplevel(self.root)
        app = VerificationTableApp(top, initial_rows=1)
        top.update_idletasks()
        top.update()

        items = list(app.tree.get_children())
        first = items[0]
        col = app.columns[4]  # choose a middle column (e.g., 'N')
        app.tree.set(first, col, "100")

        # start editing that column
        app._start_edit(first, col)
        # Press Enter (commit down) -> should create new row and focus same column
        app._on_entry_commit_down(None)

        items = list(app.tree.get_children())
        self.assertEqual(len(items), 2)
        new_item = items[1]
        self.assertEqual(app.edit_item, new_item)
        self.assertEqual(app.edit_column, col)
        # copied value must be equal
        self.assertEqual(app.tree.set(new_item, col), "100")
        top.destroy()

    def test_down_arrow_creates_row_and_keeps_column(self):
        top = tk.Toplevel(self.root)
        app = VerificationTableApp(top, initial_rows=1)
        top.update_idletasks()
        top.update()

        items = list(app.tree.get_children())
        first = items[0]
        col = app.columns[2]
        app.tree.set(first, col, "XMARK")

        app._start_edit(first, col)
        # Simulate pressing Down while editing
        app._on_entry_move_down(None)

        items = list(app.tree.get_children())
        self.assertEqual(len(items), 2)
        new_item = items[1]
        self.assertEqual(app.edit_item, new_item)
        self.assertEqual(app.edit_column, col)
        self.assertEqual(app.tree.set(new_item, col), "XMARK")
        top.destroy()

    def test_tab_on_last_column_copies_to_existing_empty_next_row(self):
        top = tk.Toplevel(self.root)
        app = VerificationTableApp(top, initial_rows=2)
        top.update_idletasks()
        top.update()

        items = list(app.tree.get_children())
        self.assertEqual(len(items), 2)
        first, second = items[0], items[1]
        # ensure second row is empty
        for c in app.columns:
            app.tree.set(second, c, "")
        # set distinct values on the first row to check copying
        for idx, col in enumerate(app.columns):
            app.tree.set(first, col, f"val{idx}")

        # start editing the last column
        last_col = app.columns[-1]
        app._start_edit(first, last_col)
        # simulate Tab press (commit next)
        app._on_entry_commit_next(None)

        # ensure we did not create a new row
        items2 = list(app.tree.get_children())
        self.assertEqual(len(items2), 2)
        # editor opened on first column of second row
        self.assertEqual(app.edit_item, second)
        self.assertEqual(app.edit_column, app.columns[0])
        # values copied
        copied = self._values_for_item(app, second)
        original = [f"val{i}" for i in range(len(app.columns))]
        self.assertEqual(copied, original)
        top.destroy()

    def test_enter_down_copies_to_existing_empty_next_row(self):
        top = tk.Toplevel(self.root)
        app = VerificationTableApp(top, initial_rows=2)
        top.update_idletasks()
        top.update()

        items = list(app.tree.get_children())
        first, second = items[0], items[1]
        # choose a middle column
        col = app.columns[4]
        # ensure second row is empty
        for c in app.columns:
            app.tree.set(second, c, "")
        app.tree.set(first, col, "200")

        app._start_edit(first, col)
        # Press Enter (commit down) -> should move to same column on existing second row and copy
        app._on_entry_commit_down(None)

        # ensure we did not create a new row
        items2 = list(app.tree.get_children())
        self.assertEqual(len(items2), 2)
        # editor opened on same column of second row
        self.assertEqual(app.edit_item, second)
        self.assertEqual(app.edit_column, col)
        # copied value must be equal
        self.assertEqual(app.tree.set(second, col), "200")
        top.destroy()

    def test_down_arrow_copies_to_existing_empty_next_row(self):
        top = tk.Toplevel(self.root)
        app = VerificationTableApp(top, initial_rows=2)
        top.update_idletasks()
        top.update()

        items = list(app.tree.get_children())
        first, second = items[0], items[1]
        col = app.columns[2]
        # ensure second row is empty
        for c in app.columns:
            app.tree.set(second, c, "")
        app.tree.set(first, col, "DOWNX")

        app._start_edit(first, col)
        # Simulate pressing Down while editing
        app._on_entry_move_down(None)

        items = list(app.tree.get_children())
        self.assertEqual(len(items), 2)
        new_item = items[1]
        self.assertEqual(app.edit_item, new_item)
        self.assertEqual(app.edit_column, col)
        self.assertEqual(app.tree.set(new_item, col), "DOWNX")
        top.destroy()


if __name__ == '__main__':
    unittest.main()
