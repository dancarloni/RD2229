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
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].code, "C25/30")
        self.assertEqual(items[0].name, "Calcestruzzo C25/30")

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
