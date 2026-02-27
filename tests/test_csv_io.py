from pathlib import Path
from typing import cast

from verification_table import VerificationInput, VerificationTableApp


class Dummy:
    def __init__(self, rows: list[VerificationInput]):
        self._rows = rows

        # dummy tree with minimal interface
        class Tree:
            def get_children(self):
                return []

            def delete(self, _):
                pass

        self.tree = Tree()
        self._set_rows_called = False
        self._models_set: list[VerificationInput] | None = None

    def get_rows(self):
        return self._rows

    def _col_to_attr(self, col: str) -> str:
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
        return mapping[col]

    def _format_value_for_csv(self, value):
        # mimic VerificationTableApp behaviour
        if value is None or value == "":
            return ""
        if isinstance(value, (int, float)):
            return str(value).replace(".", ",")
        if isinstance(value, str):
            s = value.strip()
            if not s:
                return ""
            try:
                f = float(s.replace(",", "."))
                return str(f).replace(".", ",")
            except Exception:
                return s
        return str(value)

    def set_rows(self, models: list[VerificationInput]):
        self._set_rows_called = True
        self._models_set = models

    def _show_error(self, *a, **k):
        raise AssertionError("_show_error called unexpectedly")


def test_export_import_csv_roundtrip(tmp_path: Path):
    rows = [
        VerificationInput(element_name="e1", section_id="S1", Mx=1.23, As_sup=2.5),
        VerificationInput(element_name="e2", section_id="S2", Mx=3.45, As_sup=1.0),
    ]
    dummy = Dummy(rows)
    path = tmp_path / "test.csv"

    # Export
    VerificationTableApp.export_csv(cast(VerificationTableApp, dummy), str(path))
    assert path.exists()

    # Check delimiter and decimal comma in file content
    with open(path, encoding="utf-8") as fh:
        content = fh.read()
    assert ";" in content
    assert "," in content

    # Import into a fresh dummy and verify models are set
    dummy2 = Dummy([])
    imported, skipped, errors = VerificationTableApp.import_csv(
        cast(VerificationTableApp, dummy2), str(path), clear=True
    )
    assert imported == 2
    assert skipped == 0
    assert errors == []
    assert dummy2._set_rows_called
    assert dummy2._models_set is not None
    assert len(dummy2._models_set) == 2
    # Verify numeric conversion worked (Mx originally in kg·m, retained as float)
    assert abs(dummy2._models_set[0].Mx - 1.23) < 1e-6
