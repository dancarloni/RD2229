import unittest
import tkinter as tk
import tempfile
import os

from verification_table import VerificationTableApp, VerificationInput


class TestVerificationTableCSV(unittest.TestCase):
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

    def make_sample_rows(self):
        return [
            VerificationInput(
                section_id="S1",
                material_concrete="C100",
                material_steel="S400",
                n_homog=1.0,
                N=10.0,
                M=20.0,
                T=0.0,
                As_sup=1.2,
                As_inf=0.6,
                d_sup=5.0,
                d_inf=4.0,
                stirrup_step=20.0,
                stirrup_diameter=8.0,
                stirrup_material="B500",
                notes="note1",
            ),
            VerificationInput(
                section_id="S2",
                material_concrete="C90",
                material_steel="S500",
                n_homog=0.8,
                N=5.0,
                M=10.0,
                T=1.0,
                As_sup=2.0,
                As_inf=1.0,
                d_sup=6.0,
                d_inf=4.5,
                stirrup_step=15.0,
                stirrup_diameter=10.0,
                stirrup_material="B400",
                notes="note2",
            ),
        ]

    def test_export_import_roundtrip(self):
        app = VerificationTableApp(self.root, initial_rows=0)
        rows = self.make_sample_rows()
        app.set_rows(rows)

        tmp = tempfile.NamedTemporaryFile(suffix=".csv", delete=False)
        tmp.close()
        try:
            app.export_csv(tmp.name)

            app2 = VerificationTableApp(self.root, initial_rows=0)
            app2.import_csv(tmp.name)
            got = app2.get_rows()
            self.assertEqual(len(got), 2)
            for expected, actual in zip(rows, got):
                self.assertEqual(expected.section_id, actual.section_id)
                self.assertEqual(expected.material_concrete, actual.material_concrete)
                self.assertEqual(expected.material_steel, actual.material_steel)
                self.assertAlmostEqual(expected.N, actual.N)
                self.assertAlmostEqual(expected.M, actual.M)
                self.assertAlmostEqual(expected.As_sup, actual.As_sup)
                self.assertEqual(expected.notes, actual.notes)
        finally:
            os.unlink(tmp.name)

    def test_import_clears_existing_rows(self):
        app = VerificationTableApp(self.root, initial_rows=0)
        # start with one row
        initial = [self.make_sample_rows()[0]]
        app.set_rows(initial)

        # export a CSV with two rows
        exporter = VerificationTableApp(self.root, initial_rows=0)
        exporter.set_rows(self.make_sample_rows())
        tmp = tempfile.NamedTemporaryFile(suffix=".csv", delete=False)
        tmp.close()
        try:
            exporter.export_csv(tmp.name)
            # import into the first app (should replace existing rows)
            app.import_csv(tmp.name, clear=True)
            got = app.get_rows()
            self.assertEqual(len(got), 2)
        finally:
            os.unlink(tmp.name)


if __name__ == "__main__":
    unittest.main()
