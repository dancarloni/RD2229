import verification_table as _vt
from verification_table import VerificationInput, VerificationTableApp

print("VerificationInput annotations:", _vt.VerificationInput.__annotations__)
print("VerificationInput class dict has Mx:", "Mx" in _vt.VerificationInput.__dict__)
print("VerificationInput class Mx attr:", _vt.VerificationInput.__dict__.get("Mx"))
import inspect

print("VerificationInput __init__ signature:", inspect.signature(_vt.VerificationInput))
print("\n--- __init__ source ---")
print(inspect.getsource(_vt.VerificationInput.__init__))


class Dummy:
    def __init__(self, rows):
        self._rows = rows

        class Tree:
            def get_children(self):
                return []

            def delete(self, _):
                pass

        self.tree = Tree()
        self._set_rows_called = False
        self._models_set = None

    def get_rows(self):
        return self._rows

    def _col_to_attr(self, col):
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

    def set_rows(self, models):
        self._set_rows_called = True
        self._models_set = models

    def _show_error(self, *a, **k):
        raise AssertionError("_show_error called unexpectedly")


rows = [
    VerificationInput(element_name="e1", section_id="S1", Mx=1.23, As_sup=2.5),
    VerificationInput(element_name="e2", section_id="S2", Mx=3.45, As_sup=1.0),
]
print("INITIAL ROWS:", rows)

dummy = Dummy(rows)
path = "tmp_test.csv"

VerificationTableApp.export_csv(dummy, path)
print("--- FILE CONTENT ---")
with open(path, encoding="utf-8") as fh:
    print(fh.read())

# import into fresh dummy
dummy2 = Dummy([])
imported, skipped, errors = VerificationTableApp.import_csv(dummy2, path, clear=True)
print("imported, skipped, errors ->", imported, skipped, errors)
print("models set:", dummy2._models_set)
if dummy2._models_set:
    print("first Mx:", dummy2._models_set[0].Mx)

print("\n--- DEBUG MANUAL EXPORT LOG ---")
import verification_table as _vt

keys = [c[0] for c in _vt.COLUMNS]
for r in rows:
    for k in keys:
        try:
            attr = dummy._col_to_attr(k)
        except KeyError:
            attr = {"M": "Mx", "T": "Ty"}.get(k, k)
        try:
            raw = getattr(r, attr)
        except Exception as e:
            raw = f"<ERR {e}>"
        print("key=", k, "-> attr=", attr, "raw=", raw)
