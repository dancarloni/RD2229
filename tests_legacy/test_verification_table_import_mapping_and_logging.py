import csv
import os
import tempfile
import tkinter as tk
import unittest
from unittest.mock import patch

from verification_table import VerificationInput, VerificationTableApp, logger


class TestImportMappingAndLogging(unittest.TestCase):
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
                verification_method="TA",
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
                verification_method="TA",
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

    def test_permuted_header_imports_with_mapping(self):
        tmp = tempfile.NamedTemporaryFile(suffix=".csv", delete=False)
        tmp.close()
        try:
            header = [c[1] for c in __import__("verification_table").COLUMNS]
            # permuto header (spostiamo la prima all'ultimo)
            perm = header[1:] + [header[0]]
            with open(tmp.name, "w", newline="", encoding="utf-8") as fh:
                w = csv.writer(fh, delimiter=";")
                w.writerow(perm)
                for r in self.make_sample_rows():
                    # costruiamo i valori in base all'header permutato (file con header riorganizzato)
                    mapping = {
                        header[0]: r.section_id,
                        header[1]: r.verification_method,
                        header[2]: r.material_concrete,
                        header[3]: r.material_steel,
                        header[4]: r.n_homog,
                        header[5]: r.N,
                        header[6]: r.M,
                        header[7]: r.T,
                        header[8]: r.As_inf,
                        header[9]: r.As_sup,
                        header[10]: r.d_inf,
                        header[11]: r.d_sup,
                        header[12]: r.stirrup_step,
                        header[13]: r.stirrup_diameter,
                        header[14]: r.stirrup_material,
                        header[15]: r.notes,
                    }
                    row_values = [mapping[col] for col in perm]
                    w.writerow(row_values)

            app = VerificationTableApp(self.root, initial_rows=0)
            # patch filedialog to return our file
            with patch("tkinter.filedialog.askopenfilename", return_value=tmp.name):
                with patch("verification_table.notify_info") as mock_info:
                    with patch.object(logger, "info") as mock_log_info:
                        app._on_import_csv()
                        mock_info.assert_called()
                        # il mapping automatico dovrebbe essere loggato come info
                        mock_log_info.assert_called()
            got = app.get_rows()
            self.assertEqual(len(got), 2)
            self.assertEqual(got[0].section_id, "S1")
            self.assertEqual(got[1].section_id, "S2")
        finally:
            os.unlink(tmp.name)

    def test_malformed_row_logs_detailed_error(self):
        tmp = tempfile.NamedTemporaryFile(suffix=".csv", delete=False)
        tmp.close()
        try:
            header = [c[1] for c in __import__("verification_table").COLUMNS]
            with open(tmp.name, "w", newline="", encoding="utf-8") as fh:
                w = csv.writer(fh, delimiter=";")
                w.writerow(header)
                rows = self.make_sample_rows()
                # prima riga valida
                r = rows[0]
                w.writerow(
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
                # seconda riga malformata: N è 'not_a_number'
                r2 = rows[1]
                w.writerow(
                    [
                        r2.section_id,
                        r2.material_concrete,
                        r2.material_steel,
                        r2.n_homog,
                        "not_a_number",
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
                    with patch.object(logger, "error") as mock_log_error:
                        app._on_import_csv()
                        mock_err.assert_called()
                        # il messaggio mostrato all'utente deve contenere il dettaglio dell'errore
                        title, text = mock_err.call_args[0]
                        self.assertEqual(title, "Importa CSV")
                        self.assertIn("not_a_number", text)
                        # logger.error should be called with a message containing our bad value
                        called = any("not_a_number" in str(args) for args, _ in mock_log_error.call_args_list)
                        self.assertTrue(
                            called,
                            f"Expected logger.error to contain 'not_a_number', got {mock_log_error.call_args_list}",
                        )
            got = app.get_rows()
            self.assertEqual(len(got), 1)
        finally:
            os.unlink(tmp.name)


if __name__ == "__main__":
    unittest.main()
