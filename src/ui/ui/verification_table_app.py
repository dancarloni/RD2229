"""Compatibility shim for verification table functionality using Qt-friendly
headless implementations for tests.

This module provides a minimal `VerificationTableApp` class with the
subset of methods the test-suite expects (CSV import/export, navigation
helpers, result application) without depending on Tkinter.
"""

from __future__ import annotations

from typing import Any


class VerificationTableApp:
    # Minimal column order expected by CSV routines. Tests use dummy objects
    # that map column keys to model attributes via `_col_to_attr`.
    COLUMNS: list[str] = [
        "element",
        "section",
        "verif_method",
        "mat_concrete",
        "mat_steel",
        "n",
        "N",
        "Mx",
        "My",
        "Mz",
        "Tx",
        "Ty",
        "At",
        "As_p",
        "As",
        "d_p",
        "d",
        "stirrups_step",
        "stirrups_diam",
        "stirrups_mat",
        "notes",
    ]

    @staticmethod
    def export_csv(app: Any, path: str) -> None:
        rows = app.get_rows()
        # Build header using column keys and semicolon delimiter
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(";".join(VerificationTableApp.COLUMNS) + "\n")
            for r in rows:
                cols = []
                for c in VerificationTableApp.COLUMNS:
                    attr = app._col_to_attr(c)
                    val = getattr(r, attr, "")
                    # Use dummy's formatter if available
                    if hasattr(app, "_format_value_for_csv"):
                        cols.append(app._format_value_for_csv(val))
                    else:
                        cols.append("" if val in (None, "") else str(val))
                fh.write(";".join(cols) + "\n")

    @staticmethod
    def import_csv(app: Any, path: str, clear: bool = False) -> tuple[int, int, list[str]]:
        imported = 0
        skipped = 0
        errors: list[str] = []
        models: list[Any] = []
        with open(path, encoding="utf-8") as fh:
            header = fh.readline().strip().split(";")
            for line in fh:
                if not line.strip():
                    continue
                parts = line.strip().split(";")
                obj = {}
                for key, val in zip(header, parts):
                    # convert decimal comma to dot for numeric parsing
                    s = val.strip()
                    if s == "":
                        parsed = None
                    else:
                        if "," in s and s.replace(",", "").replace(".", "").isdigit():
                            try:
                                parsed = float(s.replace(",", "."))
                            except Exception:
                                parsed = s
                        else:
                            # try numeric conversion
                            try:
                                parsed = float(s.replace(",", "."))
                            except Exception:
                                parsed = s
                    # map to model attr using app helper
                    try:
                        attr = app._col_to_attr(key)
                    except Exception:
                        attr = key
                    obj[attr] = parsed
                # Build a VerificationInput-like namespace if a constructor is available
                try:
                    Model = getattr(app, "VerificationInput", None)
                    if Model:
                        instance = Model(**obj)  # type: ignore[misc]
                    else:
                        instance = obj
                    models.append(instance)
                    imported += 1
                except Exception as exc:
                    errors.append(str(exc))
                    skipped += 1
        if hasattr(app, "set_rows"):
            app.set_rows(models)
        return imported, skipped, errors

    def _compute_target_cell(
        self, item: str, col: str, col_idx: int, row_delta: int
    ) -> tuple[str, str, bool]:
        # Determine current row index
        order = list(self.tree.get_children())
        try:
            idx = order.index(item)
        except ValueError:
            idx = 0
        target_idx = idx + row_delta
        created = False
        if target_idx >= len(order):
            # create a new row via add_row_from_previous (expected to be provided)
            new_id = self.add_row_from_previous(item)
            target_item = new_id
            created = True
        else:
            target_item = order[target_idx]
        # target column remains same key
        target_col = col
        return target_item, target_col, created

    @staticmethod
    def _apply_result_to_item(app: Any, item: str, res: Any) -> None:
        # Write a notes summary into the 'notes' column using tree.set
        notes = []
        if hasattr(res, "esito"):
            notes.append(str(res.esito))
        if hasattr(res, "sigma_c_max") and getattr(res, "sigma_c_max") is not None:
            notes.append(f"σc_max={getattr(res, 'sigma_c_max')}")
        if hasattr(res, "sigma_c_min") and getattr(res, "sigma_c_min") is not None:
            notes.append(f"σc_min={getattr(res, 'sigma_c_min')}")
        text = " | ".join(notes)
        try:
            app.tree.set(item, "notes", text)
        except Exception:
            # Fallback for fake trees that expose set-like interface
            try:
                app.tree.set(item, "notes", text)
            except Exception:
                pass


# Backwards-compatible module-level exports expected by legacy shims
COLUMNS = VerificationTableApp.COLUMNS


# Minimal window class alias for code importing VerificationTableWindow
class VerificationTableWindow(VerificationTableApp):
    pass


# Legacy-compatible COLUMNS structure: list of tuples (key, label, width, align)
# Some legacy modules expect this exact shape; build it from the simple COLUMNS
# list above so CSV and other utilities work without importing Tk-based code.
LEGACY_COLUMNS = [(c, c.replace("_", " ").title(), 120, "w") for c in COLUMNS]
# Export under the historical name
COLUMNS = LEGACY_COLUMNS
