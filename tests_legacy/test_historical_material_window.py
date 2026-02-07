import tempfile
import tkinter as tk
import unittest
from pathlib import Path

from sections_app.ui.historical_material_window import HistoricalMaterialWindow

from core_models.materials import MaterialRepository
from historical_materials import (
    HistoricalMaterial,
    HistoricalMaterialLibrary,
    HistoricalMaterialType,
)


class TestHistoricalMaterialWindow(unittest.TestCase):
    def setUp(self):
        try:
            self.root = tk.Tk()
            self.root.withdraw()
        except tk.TclError:
            self.skipTest("Tkinter not available in this environment")
        self.tmpdir = tempfile.TemporaryDirectory()
        self.base = Path(self.tmpdir.name)
        self.lib_path = self.base / "historical.json"
        self.lib = HistoricalMaterialLibrary(path=self.lib_path)
        # Add some items
        hm1 = HistoricalMaterial(
            id="HM1",
            code="HM1",
            name="CLS R 160",
            source="RD 2229/39",
            type=HistoricalMaterialType.CONCRETE,
            fck=16.0,
        )
        hm2 = HistoricalMaterial(
            id="HM2",
            code="HM2",
            name="Acciaio B450C",
            source="SomeStd",
            type=HistoricalMaterialType.STEEL,
            fyk=450.0,
        )
        self.lib.add(hm1)
        self.lib.add(hm2)
        self.mat_repo = MaterialRepository(json_file=str(self.base / "materials.json"))

    def tearDown(self):
        try:
            self.root.destroy()
        except Exception:
            pass
        self.tmpdir.cleanup()

    def test_window_loads_and_shows_items(self):
        win = HistoricalMaterialWindow(
            self.root, library=self.lib, material_repository=self.mat_repo
        )
        # check the tree contains our codes
        codes = [win.tree.set(i, "code") for i in win.tree.get_children()]
        self.assertIn("HM1", codes)
        self.assertIn("HM2", codes)
        win.destroy()

    def test_import_to_material_repo(self):
        win = HistoricalMaterialWindow(
            self.root, library=self.lib, material_repository=self.mat_repo
        )
        # select HM1
        win.tree.selection_set("HM1")
        win._on_import_selected()
        # materials repo should now have one material
        mats = self.mat_repo.get_all()
        self.assertTrue(any(m.name == "CLS R 160" for m in mats))
        win.destroy()

    def test_add_and_delete(self):
        win = HistoricalMaterialWindow(
            self.root, library=self.lib, material_repository=self.mat_repo
        )
        # Add new via library directly then refresh
        new = HistoricalMaterial(
            id="HM_NEW",
            code="HM_NEW",
            name="New Mat",
            source="RD",
            type=HistoricalMaterialType.OTHER,
        )
        self.lib.add(new)
        win._refresh_table()
        codes = [win.tree.set(i, "code") for i in win.tree.get_children()]
        self.assertIn("HM_NEW", codes)
        # Delete
        win.tree.selection_set("HM_NEW")

        # simulate user confirming delete by invoking ask_confirm callback immediately
        def _fake_ask_confirm(title, message, callback=None, **kwargs):
            if callback:
                callback(True)
            return lambda ans: None

        from unittest.mock import patch

        with patch("sections_app.services.notification.ask_confirm", side_effect=_fake_ask_confirm):
            win._on_delete()
        win._refresh_table()
        codes = [win.tree.set(i, "code") for i in win.tree.get_children()]
        self.assertNotIn("HM_NEW", codes)
        win.destroy()


if __name__ == "__main__":
    unittest.main()
