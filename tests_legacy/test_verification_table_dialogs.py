import csv
import os
import tempfile
import tkinter as tk
import unittest
from unittest.mock import patch

from verification_table import VerificationInput, VerificationTableApp


class TestVerificationTableDialogs(unittest.TestCase):
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

    def test_export_csv_dialog_saves_file_and_shows_info(self):
        app = VerificationTableApp(self.root, initial_rows=0)
        rows = self.make_sample_rows()
        app.set_rows(rows)

        tmp = tempfile.NamedTemporaryFile(suffix=".csv", delete=False)
        tmp.close()
        try:
            with patch("tkinter.filedialog.asksaveasfilename", return_value=tmp.name):
                with patch("verification_table.notify_info") as mock_info:
                    app._on_export_csv()
                    mock_info.assert_called()
            # verify file content (uso ';' come separatore)
            with open(tmp.name, newline="", encoding="utf-8") as fh:
                reader = csv.reader(fh, delimiter=";")
                rows_read = list(reader)
            # first row should be header with same number of columns
            self.assertTrue(len(rows_read) >= 3)
            self.assertEqual(len(rows_read[0]), len(app.columns))
        finally:
            os.unlink(tmp.name)

    def test_import_csv_dialog_loads_file_and_shows_info(self):
        # prepare csv file
        tmp = tempfile.NamedTemporaryFile(suffix=".csv", delete=False)
        tmp.close()
        try:
            keys = [c[0] for c in app_columns()]  # header friendly names
            header = [c[1] for c in app_columns()]
            # write header and two rows (usiamo ';' come separatore per rispecchiare export)
            with open(tmp.name, "w", newline="", encoding="utf-8") as fh:
                writer = csv.writer(fh, delimiter=";")
                writer.writerow(header)
                for r in self.make_sample_rows():
                    writer.writerow(
                        [
                            r.section_id,
                            r.material_concrete,
                            r.material_steel,
                            r.n_homog,
                            r.N,
                            r.M,
                            r.T,
                            r.As_inf,
                            r.As_sup,
                            r.d_inf,
                            r.d_sup,
                            r.stirrup_step,
                            r.stirrup_diameter,
                            r.stirrup_material,
                            r.notes,
                        ]
                    )

            app = VerificationTableApp(self.root, initial_rows=0)
            with patch("tkinter.filedialog.askopenfilename", return_value=tmp.name):
                with patch("verification_table.notify_info") as mock_info:
                    app._on_import_csv()
                    mock_info.assert_called()
            got = app.get_rows()
            self.assertEqual(len(got), 2)
        finally:
            os.unlink(tmp.name)

    def test_import_csv_bad_header_shows_error_and_skips(self):
        tmp = tempfile.NamedTemporaryFile(suffix=".csv", delete=False)
        tmp.close()
        try:
            header = [c[1] for c in app_columns()]
            bad_header = header.copy()
            # rendiamo l'header non valido cambiando il nome della prima colonna
            bad_header[0] = bad_header[0] + "_INVALID"
            with open(tmp.name, "w", newline="", encoding="utf-8") as fh:
                writer = csv.writer(fh, delimiter=";")
                writer.writerow(bad_header)
                for r in self.make_sample_rows():
                    writer.writerow(
                        [
                            r.section_id,
                            r.material_concrete,
                            r.material_steel,
                            r.n_homog,
                            r.N,
                            r.M,
                            r.T,
                            r.As_inf,
                            r.As_sup,
                            r.d_inf,
                            r.d_sup,
                            r.stirrup_step,
                            r.stirrup_diameter,
                            r.stirrup_material,
                            r.notes,
                        ]
                    )

            app = VerificationTableApp(self.root, initial_rows=0)
            with patch("tkinter.filedialog.askopenfilename", return_value=tmp.name):
                with patch("verification_table.notify_error") as mock_err:
                    app._on_import_csv()
                    mock_err.assert_called()
                    # Verifica il formato del messaggio di errore centralizzato
                    title, text = mock_err.call_args[0]
                    self.assertEqual(title, "Importa CSV")
                    self.assertIn("Intestazione CSV non corrisponde", text)
                    self.assertIn("Atteso:", text)
                    self.assertIn("Trovato:", text)
            self.assertEqual(len(app.get_rows()), 0)
        finally:
            os.unlink(tmp.name)

    def test_import_csv_malformed_row_shows_error_and_skips(self):
        tmp = tempfile.NamedTemporaryFile(suffix=".csv", delete=False)
        tmp.close()
        try:
            header = [c[1] for c in app_columns()]
            with open(tmp.name, "w", newline="", encoding="utf-8") as fh:
                writer = csv.writer(fh, delimiter=";")
                writer.writerow(header)
                rows = self.make_sample_rows()
                # prima riga valida
                r = rows[0]
                writer.writerow(
                    [
                        r.section_id,
                        r.material_concrete,
                        r.material_steel,
                        r.n_homog,
                        r.N,
                        r.M,
                        r.T,
                        r.As_inf,
                        r.As_sup,
                        r.d_inf,
                        r.d_sup,
                        r.stirrup_step,
                        r.stirrup_diameter,
                        r.stirrup_material,
                        r.notes,
                    ]
                )
                # seconda riga con valore numerico malformato (es. 'N')
                r2 = rows[1]
                writer.writerow(
                    [
                        r2.section_id,
                        r2.material_concrete,
                        r2.material_steel,
                        r2.n_homog,
                        "not_a_number",  # N malformato
                        r2.M,
                        r2.T,
                        r2.As_inf,
                        r2.As_sup,
                        r2.d_inf,
                        r2.d_sup,
                        r2.stirrup_step,
                        r2.stirrup_diameter,
                        r2.stirrup_material,
                        r2.notes,
                    ]
                )

            app = VerificationTableApp(self.root, initial_rows=0)
            with patch("tkinter.filedialog.askopenfilename", return_value=tmp.name):
                with patch("verification_table.notify_error") as mock_err:
                    with patch("verification_table.notify_info") as mock_info:
                        app._on_import_csv()
                        mock_err.assert_called()
                        mock_info.assert_called()
                        # Verifica che il messaggio contenga il riepilogo e il dettaglio
                        title, text = mock_err.call_args[0]
                        self.assertEqual(title, "Importa CSV")
                        self.assertIn("Si sono verificati errori durante l'import", text)
                        self.assertIn("not_a_number", text)
            got = app.get_rows()
            self.assertEqual(len(got), 1)
        finally:
            os.unlink(tmp.name)

    def test_import_cancel_does_nothing(self):
        app = VerificationTableApp(self.root, initial_rows=0)
        with patch("tkinter.filedialog.askopenfilename", return_value=""):
            with patch("verification_table.notify_info") as mock_info:
                app._on_import_csv()
                mock_info.assert_not_called()
        self.assertEqual(len(app.get_rows()), 0)

    def test_home_end_navigation(self):
        app = VerificationTableApp(self.root, initial_rows=1)
        self.root.update_idletasks()
        self.root.update()
        item = list(app.tree.get_children())[0]
        app.tree.focus(item)
        # Home should call _start_edit on the first column (bbox may be empty in headless tests)
        with patch.object(app, "_start_edit") as mock_start:
            app._on_tree_home(None)
            mock_start.assert_called_with(item, app.columns[0])
        # End should call _start_edit on the last column
        with patch.object(app, "_start_edit") as mock_start2:
            app._on_tree_end(None)
            mock_start2.assert_called_with(item, app.columns[-1])


def app_columns():
    from verification_table import COLUMNS

    return COLUMNS


if __name__ == "__main__":
    unittest.main()
