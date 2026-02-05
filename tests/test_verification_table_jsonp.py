import unittest
import tkinter as tk
import tempfile
import os
import json
from unittest.mock import patch

from verification_table import VerificationTableApp, VerificationInput


class TestVerificationTableJSONP(unittest.TestCase):
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

    def make_project_file(self, path, elems=None, mats=None, secs=None):
        data = {
            "file_type": "RD_VerificaSezioni_Project",
            "module": "VerificationTable",
            "version": 1,
            "created_at": "2026-01-01T00:00:00",
            "materials": {
                "cls": mats or [],
                "steel": [],
            },
            "sections": secs or [],
            "elements": elems or [],
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def test_load_project_populates_table_and_updates_project(self):
        tmp = tempfile.NamedTemporaryFile(suffix=".jsonp", delete=False)
        tmp.close()
        try:
            elems = [
                {"id": "E1", "section_id": "SEC1", "cls_id": "C25_30", "steel_id": "B450C", "method": "TA", "N": 0, "M": 0},
                {"id": "E2", "section_id": "SEC2", "cls_id": "C30_37", "steel_id": "B500C", "method": "SLU", "N": 10, "M": 5},
            ]
            self.make_project_file(tmp.name, elems=elems)

            app = VerificationTableApp(self.root, initial_rows=0)
            with patch('tkinter.filedialog.askopenfilename', return_value=tmp.name):
                app._on_load_project()

            rows = app.get_rows()
            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[0].section_id, 'SEC1')
            self.assertEqual(rows[1].verification_method, 'SLU')
            # project path should be set and dirty False
            self.assertIsNotNone(app.project.path)
            self.assertFalse(app.project.dirty)

        finally:
            os.unlink(tmp.name)

    def test_add_list_elements_appends_and_marks_project(self):
        tmp = tempfile.NamedTemporaryFile(suffix=".jsonp", delete=False)
        tmp.close()
        try:
            elems = [
                {"id": "E10", "section_id": "SEC10", "cls_id": "C50", "steel_id": "S50", "method": "TA", "N": 1, "M": 1},
            ]
            self.make_project_file(tmp.name, elems=elems)

            app = VerificationTableApp(self.root, initial_rows=1)
            initial_count = len(app.get_rows())
            with patch('tkinter.filedialog.askopenfilename', return_value=tmp.name):
                app._on_add_list_elements()

            new_count = len(app.get_rows())
            self.assertEqual(new_count, initial_count + 1)
            self.assertTrue(app.project.last_action_was_add_list)

        finally:
            os.unlink(tmp.name)

    def test_save_project_uses_saveas_after_add_list_and_writes_header(self):
        # create app and add one row
        app = VerificationTableApp(self.root, initial_rows=0)
        r = VerificationInput(section_id="SX", material_concrete="C25_30", material_steel="B450C")
        app.set_rows([r])

        # simulate that last action was add-list so save must ask
        app.project.last_action_was_add_list = True

        tmp_save = tempfile.NamedTemporaryFile(suffix=".jsonp", delete=False)
        tmp_save.close()
        try:
            with patch('tkinter.filedialog.asksaveasfilename', return_value=tmp_save.name):
                app._on_save_project()

            # verify file exists and header
            with open(tmp_save.name, 'r', encoding='utf-8') as fh:
                data = json.load(fh)
            self.assertEqual(data.get('file_type'), 'RD_VerificaSezioni_Project')
            self.assertEqual(data.get('module'), 'VerificationTable')
            self.assertIn('elements', data)
            self.assertEqual(len(data['elements']), 1)
        finally:
            os.unlink(tmp_save.name)


if __name__ == '__main__':
    unittest.main()
