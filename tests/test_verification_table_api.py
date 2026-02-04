import unittest
import tkinter as tk
import sys
import os

# Ensure project root is on sys.path so tests can import local modules under pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from verification_table import VerificationTableApp
from tkinter import ttk


class TestVerificationTableAPI(unittest.TestCase):
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

    def test_create_editor_for_cell_public_api_returns_widget(self):
        top = tk.Toplevel(self.root)
        app = VerificationTableApp(top, initial_rows=1)
        items = list(app.tree.get_children())
        first = items[0]
        top.update_idletasks()
        top.update()
        # create editor for a non-material column (Entry expected)
        editor = app.create_editor_for_cell(first, 'section')
        self.assertIsNotNone(editor)
        self.assertTrue(isinstance(editor, (ttk.Entry, ttk.Combobox)))
        editor.destroy()
        top.destroy()

    def test_compute_target_cell_public_api_creates_row_when_needed(self):
        top = tk.Toplevel(self.root)
        app = VerificationTableApp(top, initial_rows=1)
        items = list(app.tree.get_children())
        first = items[0]
        # compute target for Tab from last column -> should create new row
        last_col = app.columns[-1]
        target_item, target_col, created = app.compute_target_cell(first, last_col, delta_col=1, delta_row=0)
        self.assertTrue(created)
        self.assertEqual(target_col, app.columns[0])
        # new item should exist in tree
        self.assertIn(target_item, list(app.tree.get_children()))
        top.destroy()


if __name__ == '__main__':
    unittest.main()
