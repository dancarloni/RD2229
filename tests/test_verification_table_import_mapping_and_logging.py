import unittest
import tkinter as tk
import tempfile
import os
import csv
from unittest.mock import patch

from verification_table import VerificationTableApp, VerificationInput, logger


def _col_to_attr(col: str) -> str:
    mapping = {
        "element": "element_name",
        "section": "section_id",
        "verif_method": "verification_method",
        "mat_concrete": "material_concrete",
        "mat_steel": "material_steel",
        "n": "n_homog",
        "N": "N",
        "Mx": "Mx",
        "My": "My",
        "Mz": "Mz",
        "Tx": "Tx",
        "Ty": "Ty",
        "At": "At",
        "As_p": "As_inf",
        "As": "As_sup",
        "d_p": "d_inf",
        "d": "d_sup",
        "stirrups_step": "stirrup_step",
        "stirrups_diam": "stirrup_diameter",
        "stirrups_mat": "stirrup_material",
        "notes": "notes",
    }
    return mapping.get(col, col)


def _row_values_for_input(header: list[str], inp: VerificationInput) -> list[object]:
    from verification_table import COLUMNS
    key_by_label = {label: key for key, label, _w, _a in COLUMNS}
    out = []
    for label in header:
        key = key_by_label.get(label)
        if key is None:
            out.append("")
            continue
        attr = _col_to_attr(key)
        out.append(getattr(inp, attr, ""))
    return out


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
                Mx=20.0,
                Ty=0.0,
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
                Mx=10.0,
                Ty=1.0,
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
        tmp = tempfile.NamedTemporaryFile(suffix='.csv', delete=False)
        tmp.close()
        try:
            header = [c[1] for c in __import__('verification_table').COLUMNS]
            # permuto header (spostiamo la prima all'ultimo)
            perm = header[1:] + [header[0]]
            with open(tmp.name, 'w', newline='', encoding='utf-8') as fh:
                w = csv.writer(fh, delimiter=';')
                w.writerow(perm)
                for r in self.make_sample_rows():
                    mapping = {h: v for h, v in zip(header, _row_values_for_input(header, r))}
                    row_values = [mapping[col] for col in perm]
                    w.writerow(row_values)

            app = VerificationTableApp(self.root, initial_rows=0)
            # patch filedialog to return our file
            with patch('tkinter.filedialog.askopenfilename', return_value=tmp.name):
                with patch('verification_table.notify_info') as mock_info:
                    with patch.object(logger, 'info') as mock_log_info:
                        app._on_import_csv()
                        mock_info.assert_called()
                        # il mapping automatico dovrebbe essere loggato come info
                        mock_log_info.assert_called()
            got = app.get_rows()
            self.assertEqual(len(got), 2)
            self.assertEqual(got[0].section_id, 'S1')
            self.assertEqual(got[1].section_id, 'S2')
        finally:
            os.unlink(tmp.name)

    def test_malformed_row_logs_detailed_error(self):
        tmp = tempfile.NamedTemporaryFile(suffix='.csv', delete=False)
        tmp.close()
        try:
            header = [c[1] for c in __import__('verification_table').COLUMNS]
            with open(tmp.name, 'w', newline='', encoding='utf-8') as fh:
                w = csv.writer(fh, delimiter=';')
                w.writerow(header)
                rows = self.make_sample_rows()
                # prima riga valida
                r = rows[0]
                w.writerow(_row_values_for_input(header, r))
                # seconda riga malformata: N è 'not_a_number'
                r2 = rows[1]
                malformed = _row_values_for_input(header, r2)
                n_idx = header.index("N [kg]") if "N [kg]" in header else None
                if n_idx is not None:
                    malformed[n_idx] = 'not_a_number'
                w.writerow(malformed)

            app = VerificationTableApp(self.root, initial_rows=0)
            with patch('tkinter.filedialog.askopenfilename', return_value=tmp.name):
                with patch('verification_table.notify_error') as mock_err:
                    with patch.object(logger, 'error') as mock_log_error:
                        app._on_import_csv()
                        mock_err.assert_called()
                        # il messaggio mostrato all'utente deve contenere il dettaglio dell'errore
                        title, text = mock_err.call_args[0]
                        self.assertEqual(title, 'Importa CSV')
                        self.assertIn('not_a_number', text)
                        # logger.error should be called with a message containing our bad value
                        called = any('not_a_number' in str(args) for args, _ in mock_log_error.call_args_list)
                        self.assertTrue(called, f"Expected logger.error to contain 'not_a_number', got {mock_log_error.call_args_list}")
            got = app.get_rows()
            self.assertEqual(len(got), 1)
        finally:
            os.unlink(tmp.name)


if __name__ == '__main__':
    unittest.main()
