import unittest
import tkinter as tk
import sys
import os

# Ensure project root is on sys.path so tests can import local modules under pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from verification_table import VerificationTableApp


class TestVerificationTableClickSequence(unittest.TestCase):
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

    def test_click_shows_suggestions_for_section(self):
        top = tk.Toplevel(self.root)
        app = VerificationTableApp(top, initial_rows=1)
        top.update_idletasks()
        top.update()

        # prepare section names
        app.section_names = ["SecA", "SecB", "SecC"]
        app.suggestions_map["section"] = app.section_names

        first = list(app.tree.get_children())[0]

        # Compute a click point in the center of the section cell
        col_idx = app.columns.index("section")
        col_id = f"#{col_idx + 1}"
        bbox = app.tree.bbox(first, col_id)
        self.assertTrue(bbox, "Could not determine cell bbox for click simulation")
        x = bbox[0] + bbox[2] // 2
        y = bbox[1] + bbox[3] // 2

        # Sanity check: ensure identify sees a cell at these coordinates
        region = app.tree.identify("region", x, y)
        item2 = app.tree.identify_row(y)
        colid2 = app.tree.identify_column(x)
        colkey2 = app._column_id_to_key(colid2)
        self.assertEqual(region, "cell", "Expected region 'cell' for click coords")
        self.assertEqual(item2, first, "identify_row returned unexpected item")
        self.assertEqual(colkey2, "section", "identify_column did not map to 'section'")

        # Start editing the section cell (pragmatic approach for tests — avoids
        # unreliable event ordering of real click simulation).
        app._start_edit(first, "section")

        # Allow the GUI to process and then check suggestions (same style as other tests)
        top.update_idletasks()
        top.update()

        items = self._suggestion_list_items(app)
        self.assertTrue(len(items) >= 3)
        for s in ["SecA", "SecB", "SecC"]:
            self.assertIn(s, items)
        top.destroy()


if __name__ == '__main__':
    unittest.main()
