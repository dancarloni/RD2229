import os
import sys
import tempfile
import tkinter as tk
import unittest

# Ensure project root is on sys.path so tests can import local modules under pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from verification_table import VerificationTableApp


class TestVerificationTableCSVRoundtrip(unittest.TestCase):
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

    def test_export_import_roundtrip_preserves_values(self):
        top = tk.Toplevel(self.root)
        app = VerificationTableApp(top, initial_rows=1)
        items = list(app.tree.get_children())
        self.assertEqual(len(items), 1)
        first = items[0]
        # populate row with a mix of numerical and textual values
        app.tree.set(first, "section", "Rect-20x30")
        app.tree.set(first, "mat_concrete", "C120")
        app.tree.set(first, "N", "123,45")  # decimal with comma
        app.tree.set(first, "M", "1.23")  # dot will be exported as comma
        app.tree.set(first, "notes", "Test note")

        # export to temp file
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
        tmp_path = tmp.name
        tmp.close()
        try:
            app.export_csv(tmp_path)
            # create a second app and import
            top2 = tk.Toplevel(self.root)
            app2 = VerificationTableApp(top2, initial_rows=0)
            imported, skipped, errors = app2.import_csv(tmp_path, clear=True)
            self.assertEqual(imported, 1)
            self.assertEqual(skipped, 0)
            self.assertEqual(errors, [])
            # compare values cell by cell (strings normalized)
            items2 = list(app2.tree.get_children())
            self.assertEqual(len(items2), 1)
            row_vals = list(app2.tree.item(items2[0], "values"))
            # locate columns and check
            keys = app2.columns

            def get_val(row, key):
                return str(row[keys.index(key)])

            self.assertEqual(get_val(row_vals, "section"), "Rect-20x30")
            self.assertEqual(get_val(row_vals, "mat_concrete"), "C120")
            # numeric fields should be normalized to use comma in CSV then parsed back to float
            # and written as string with dot replaced to comma in export;
            # import produces floats stored as numeric; we check approximate numeric equivalence
            self.assertAlmostEqual(float(get_val(row_vals, "N").replace(",", ".")), 123.45, places=2)
            self.assertAlmostEqual(float(get_val(row_vals, "M").replace(",", ".")), 1.23, places=2)
            self.assertEqual(get_val(row_vals, "notes"), "Test note")
        finally:
            try:
                os.unlink(tmp_path)
            except Exception:
                pass
        top.destroy()


if __name__ == "__main__":
    unittest.main()
