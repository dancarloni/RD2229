import tempfile
import unittest
from pathlib import Path

from historical_materials import HistoricalMaterialLibrary


class TestHistoricalImportCSV(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.base = Path(self.tmpdir.name)
        self.lib_path = self.base / "hist_csv.json"
        self.lib = HistoricalMaterialLibrary(path=self.lib_path)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_import_csv_basic(self):
        csv_path = self.base / "import.csv"
        csv_path.write_text(
            "code;name;type;source;fck;fcd;fctm;Ec;fyk;fyd;Es;gamma_c;gamma_s;notes\n"
            "RDCSV1;CLS CSV 1;concrete;ReLUIS;18;12;;300000;;;320000;1.4;;Example from ReLUIS\n"
            "RDCSV2;STEEL CSV 1;steel;STIL;;; ; ;450;385;;2100000;1.15;;Example steel\n"
            "BADROW;;;",
            encoding="utf-8",
        )
        count = self.lib.import_from_csv(csv_path)
        self.assertEqual(count, 2)
        items = {m.code for m in self.lib.get_all()}
        self.assertIn("RDCSV1", items)
        self.assertIn("RDCSV2", items)

    def test_import_updates_existing(self):
        # create existing
        from historical_materials import HistoricalMaterial, HistoricalMaterialType

        self.lib.add(
            HistoricalMaterial(
                id="RDCSV1",
                code="RDCSV1",
                name="Old",
                source="X",
                type=HistoricalMaterialType.CONCRETE,
                fck=10.0,
            )
        )
        csv_path = self.base / "import2.csv"
        csv_path.write_text(
            "code;name;type;source;fck;fcd;fctm;Ec;fyk;fyd;Es;gamma_c;gamma_s;notes\n"
            "RDCSV1;CLS CSV 1 Updated;concrete;ReLUIS;20;13;;;;;;1.4;;Updated\n",
            encoding="utf-8",
        )
        count = self.lib.import_from_csv(csv_path)
        self.assertEqual(count, 1)
        found = next((m for m in self.lib.get_all() if m.code == "RDCSV1"), None)
        self.assertIsNotNone(found)
        self.assertEqual(found.name, "CLS CSV 1 Updated")


if __name__ == "__main__":
    unittest.main()
