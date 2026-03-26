"""Dialog specifici per ProjectEditor (geometry/material/load)."""

from __future__ import annotations

import json
from typing import Any, Dict, Optional

try:
    from PyQt6.QtCore import Qt
    from PyQt6.QtWidgets import (
        QDialog,
        QDialogButtonBox,
        QFormLayout,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QVBoxLayout,
    )
except ImportError:  # pragma: no cover
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import (
        QDialog,
        QDialogButtonBox,
        QFormLayout,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QVBoxLayout,
    )

from .key_value_dialog import KeyValueDialog


class RowEditDialog(QDialog):
    """Base dialog per modificare una singola voce di tabella."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Modifica voce")
        self._result: dict[str, Any] | None = None
        self._form = QFormLayout()
        try:
            # PyQt6 requires .StandardButton path for enum access
            btns = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        except Exception:
            # PySide6 fallback: direct enum access (legacy)
            btns = QDialogButtonBox.Ok | QDialogButtonBox.Cancel  # type: ignore[attr-defined]
        self._buttons = QDialogButtonBox(btns)
        self._buttons.accepted.connect(self._on_ok)
        self._buttons.rejected.connect(self.reject)
        root = QVBoxLayout(self)
        root.addLayout(self._form)
        root.addWidget(self._buttons)

    def _on_ok(self) -> None:
        try:
            self._result = self._collect()
            self.accept()
        except Exception as exc:
            # mostra errore semplice (es. invalid float)
            self._set_error(str(exc))

    def _set_error(self, message: str) -> None:
        # Implementazione minima: usa QLabel in fondo
        self._error_label = getattr(self, "_error_label", None)
        if self._error_label is None:
            self._error_label = QLabel("")
            self.layout().insertWidget(1, self._error_label)
        self._error_label.setText(message)

    def _collect(self) -> dict[str, Any]:
        raise NotImplementedError()

    @staticmethod
    def edit(parent, initial: dict | None = None) -> dict | None:
        dlg = RowEditDialog(parent=parent)
        return dlg._result


class GeometryDialog(RowEditDialog):
    def __init__(self, parent=None, initial: Optional[Dict[str, Any]] = None):
        super().__init__(parent)
        self.setWindowTitle("Modifica geometria")
        self.txt_id = QLineEdit()
        self.txt_type = QLineEdit()
        self.txt_width = QLineEdit()
        self.txt_height = QLineEdit()
        self.txt_extra = QLineEdit()
        self.btn_extra = QLabel("[modifica extra]")
        self.btn_extra.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_extra.mousePressEvent = self._on_edit_extra

        self._form.addRow("ID", self.txt_id)
        self._form.addRow("Tipo", self.txt_type)
        self._form.addRow("Larghezza", self.txt_width)
        self._form.addRow("Altezza", self.txt_height)
        row = QHBoxLayout()
        row.addWidget(self.txt_extra)
        row.addWidget(self.btn_extra)
        self._form.addRow("Extra", row)

        if initial:
            self.txt_id.setText(str(initial.get("id", "")))
            self.txt_type.setText(str(initial.get("type", "")))
            self.txt_width.setText(str(initial.get("width", "")))
            self.txt_height.setText(str(initial.get("height", "")))
            self.txt_extra.setText(str(initial.get("extra", "")))

    def _on_edit_extra(self, event):
        try:
            current = self.txt_extra.text().strip()
            current_dict = {}
            if current:
                current_dict = json.loads(current)
        except Exception:
            current_dict = {}
        out = KeyValueDialog.edit(self, current_dict)
        if out is not None:
            self.txt_extra.setText(json.dumps(out, ensure_ascii=False))

    def _collect(self) -> dict[str, Any]:
        return {
            "id": self.txt_id.text().strip(),
            "type": self.txt_type.text().strip(),
            "width": float(self.txt_width.text().strip() or 0),
            "height": float(self.txt_height.text().strip() or 0),
            "extra": json.loads(self.txt_extra.text()) if self.txt_extra.text().strip() else {},
        }

    @staticmethod
    def edit(parent, initial: dict | None = None) -> dict | None:
        dlg = GeometryDialog(parent=parent, initial=initial or {})
        code = dlg.exec()
        try:
            from PyQt6.QtWidgets import QDialog as _QDialog

            accepted = _QDialog.DialogCode.Accepted
        except ImportError:
            from PySide6.QtWidgets import QDialog as _QDialog  # type: ignore

            accepted = _QDialog.DialogCode.Accepted
        return dlg._result if code == accepted else None


class MaterialDialog(RowEditDialog):
    def __init__(self, parent=None, initial: Optional[Dict[str, Any]] = None):
        super().__init__(parent)
        self.setWindowTitle("Modifica materiale")
        self.txt_id = QLineEdit()
        self.txt_type = QLineEdit()
        self.txt_class = QLineEdit()
        self.txt_fck = QLineEdit()
        self.txt_fyk = QLineEdit()
        self.txt_extra = QLineEdit()
        self.btn_extra = QLabel("[modifica extra]")
        self.btn_extra.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_extra.mousePressEvent = self._on_edit_extra

        self._form.addRow("ID", self.txt_id)
        self._form.addRow("Tipo", self.txt_type)
        self._form.addRow("Classe", self.txt_class)
        self._form.addRow("f_ck", self.txt_fck)
        self._form.addRow("f_yk", self.txt_fyk)
        row = QHBoxLayout()
        row.addWidget(self.txt_extra)
        row.addWidget(self.btn_extra)
        self._form.addRow("Extra", row)

        if initial:
            self.txt_id.setText(str(initial.get("id", "")))
            self.txt_type.setText(str(initial.get("type", "")))
            self.txt_class.setText(str(initial.get("material_class", "")))
            self.txt_fck.setText(str(initial.get("f_ck", "")))
            self.txt_fyk.setText(str(initial.get("f_yk", "")))
            self.txt_extra.setText(str(initial.get("extra", "")))

    def _on_edit_extra(self, event):
        try:
            current = self.txt_extra.text().strip()
            current_dict = {}
            if current:
                current_dict = json.loads(current)
        except Exception:
            current_dict = {}
        out = KeyValueDialog.edit(self, current_dict)
        if out is not None:
            self.txt_extra.setText(json.dumps(out, ensure_ascii=False))

    def _collect(self) -> dict[str, Any]:
        return {
            "id": self.txt_id.text().strip(),
            "type": self.txt_type.text().strip(),
            "material_class": self.txt_class.text().strip(),
            "f_ck": float(self.txt_fck.text().strip() or 0),
            "f_yk": float(self.txt_fyk.text().strip() or 0),
            "extra": json.loads(self.txt_extra.text()) if self.txt_extra.text().strip() else {},
        }

    @staticmethod
    def edit(parent, initial: dict | None = None) -> dict | None:
        dlg = MaterialDialog(parent=parent, initial=initial or {})
        code = dlg.exec()
        try:
            from PyQt6.QtWidgets import QDialog as _QDialog

            accepted = _QDialog.DialogCode.Accepted
        except ImportError:
            from PySide6.QtWidgets import QDialog as _QDialog  # type: ignore

            accepted = _QDialog.DialogCode.Accepted
        return dlg._result if code == accepted else None


class LoadDialog(RowEditDialog):
    def __init__(self, parent=None, initial: Optional[Dict[str, Any]] = None):
        super().__init__(parent)
        self.setWindowTitle("Modifica carico")
        self.txt_element_id = QLineEdit()
        self.txt_N = QLineEdit()
        self.txt_Mx = QLineEdit()
        self.txt_My = QLineEdit()
        self.txt_Tx = QLineEdit()
        self.txt_Ty = QLineEdit()
        self.txt_desc = QLineEdit()
        self.txt_extra = QLineEdit()
        self.btn_extra = QLabel("[modifica extra]")
        self.btn_extra.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_extra.mousePressEvent = self._on_edit_extra

        self._form.addRow("Elemento", self.txt_element_id)
        self._form.addRow("N", self.txt_N)
        self._form.addRow("Mx", self.txt_Mx)
        self._form.addRow("My", self.txt_My)
        self._form.addRow("Tx", self.txt_Tx)
        self._form.addRow("Ty", self.txt_Ty)
        self._form.addRow("Descrizione", self.txt_desc)
        row = QHBoxLayout()
        row.addWidget(self.txt_extra)
        row.addWidget(self.btn_extra)
        self._form.addRow("Extra", row)

        if initial:
            self.txt_element_id.setText(str(initial.get("element_id", "")))
            self.txt_N.setText(str(initial.get("N", "")))
            self.txt_Mx.setText(str(initial.get("Mx", "")))
            self.txt_My.setText(str(initial.get("My", "")))
            self.txt_Tx.setText(str(initial.get("Tx", "")))
            self.txt_Ty.setText(str(initial.get("Ty", "")))
            self.txt_desc.setText(str(initial.get("description", "")))
            self.txt_extra.setText(str(initial.get("extra", "")))

    def _on_edit_extra(self, event):
        try:
            current = self.txt_extra.text().strip()
            current_dict = {}
            if current:
                current_dict = json.loads(current)
        except Exception:
            current_dict = {}
        out = KeyValueDialog.edit(self, current_dict)
        if out is not None:
            self.txt_extra.setText(json.dumps(out, ensure_ascii=False))

    def _collect(self) -> dict[str, Any]:
        return {
            "element_id": self.txt_element_id.text().strip(),
            "N": float(self.txt_N.text().strip() or 0),
            "Mx": float(self.txt_Mx.text().strip() or 0),
            "My": float(self.txt_My.text().strip() or 0),
            "Tx": float(self.txt_Tx.text().strip() or 0),
            "Ty": float(self.txt_Ty.text().strip() or 0),
            "description": self.txt_desc.text().strip(),
            "extra": json.loads(self.txt_extra.text()) if self.txt_extra.text().strip() else {},
        }

    @staticmethod
    def edit(parent, initial: dict | None = None) -> dict | None:
        dlg = LoadDialog(parent=parent, initial=initial or {})
        code = dlg.exec()
        try:
            from PyQt6.QtWidgets import QDialog as _QDialog

            accepted = _QDialog.DialogCode.Accepted
        except ImportError:
            from PySide6.QtWidgets import QDialog as _QDialog  # type: ignore

            accepted = _QDialog.DialogCode.Accepted
        return dlg._result if code == accepted else None
