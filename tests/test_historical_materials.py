import json
import tempfile
import unittest
from pathlib import Path

from historical_materials import HistoricalMaterial, HistoricalMaterialLibrary, HistoricalMaterialType
from core_models.materials import MaterialRepository


class TestHistoricalMaterials(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.base = Path(self.tmpdir.name)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_library_save_and_load(self):
        lib_path = self.base / "hist_materials.json"
        lib = HistoricalMaterialLibrary(path=lib_path)
        hm = HistoricalMaterial(id="HM-001", code="C25/30", name="Calcestruzzo C25/30", source="RD 2229/39", type=HistoricalMaterialType.CONCRETE, fck=25.0)
        lib.add(hm)
        # ensure file written
        self.assertTrue(lib_path.exists())

        # load fresh instance
        lib2 = HistoricalMaterialLibrary(path=lib_path)
        lib2.load_from_file()
        items = lib2.get_all()
        # The library may include default examples; verify our added material exists
        codes = {m.code for m in items}
        self.assertIn("C25/30", codes)
        found = next((m for m in items if m.code == "C25/30"), None)
        self.assertIsNotNone(found)
        self.assertEqual(found.name, "Calcestruzzo C25/30")

    def test_defaults_populated_when_missing(self):
        lib_path = self.base / "defaults.json"
        # Ensure no file exists
        try:
            lib_path.unlink(missing_ok=True)
        except Exception:
            pass
        lib = HistoricalMaterialLibrary(path=lib_path)
        # calling load should populate defaults and write file
        lib.load_from_file()
        items = lib.get_all()
        # Should have multiple default materials (CLS + acciai)
        self.assertTrue(len(items) >= 6)
        # Check that RD2229 base materials are present
        codes = {m.code for m in items}
        # Calcestruzzi
        self.assertIn("RD2229_CLS_120_N", codes)
        self.assertIn("RD2229_CLS_160_AR", codes)
        # Acciai
        self.assertIn("RD2229_ACC_DOLCE", codes)
        self.assertIn("RD2229_ACC_DURO", codes)

    def test_import_historical_material_to_material(self):
        hist = HistoricalMaterial(id="HM-002", code="C30/37", name="C30/37", source="RD 2229/39", type=HistoricalMaterialType.CONCRETE, fck=30.0, fcd=20.0, gamma_c=1.4)
        repo = MaterialRepository(json_file=str(self.base / "materials.json"))
        mat = repo.import_historical_material(hist)
        self.assertEqual(mat.name, "C30/37")
        self.assertIn("fck", mat.properties)
        self.assertEqual(mat.properties.get("fck"), 30.0)
        self.assertEqual(mat.properties.get("gamma_c"), 1.4)


if __name__ == "__main__":
    unittest.main()
