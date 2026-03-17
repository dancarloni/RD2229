"""Dialog per gestire campi JSON di tipo key/value.

Questo dialog permette di aggiungere/rimuovere coppie chiave/valore.
Viene usato per il campo `extra` nei moduli di ProjectEditor.
"""

from __future__ import annotations

try:
    from PyQt6.QtCore import Qt
    from PyQt6.QtWidgets import (
        QAbstractItemView,
        QDialog,
        QHBoxLayout,
        QLabel,
        QPushButton,
        QTableWidget,
        QTableWidgetItem,
        QVBoxLayout,
    )
except ImportError:  # pragma: no cover
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import (
        QAbstractItemView,
        QDialog,
        QHBoxLayout,
        QLabel,
        QPushButton,
        QTableWidget,
        QTableWidgetItem,
        QVBoxLayout,
    )

import json


class KeyValueDialog(QDialog):
    """Dialog per editare un oggetto JSON come elenco chiave/valore."""

    def __init__(self, parent=None, data: dict | None = None):
        super().__init__(parent)
        self.setWindowTitle("Modifica extra")
        self._result: dict | None = None

        self._table = QTableWidget(0, 2, self)
        self._table.setHorizontalHeaderLabels(["Key", "Value"])
        self._table.horizontalHeader().setStretchLastSection(True)
        # Use a stable enum reference that works in PyQt6 and PySide6
        self._table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.SingleSelection)

        self._lbl_error = QLabel("")
        self._lbl_error.setStyleSheet("color: red;")

        btn_add = QPushButton("Aggiungi")
        btn_remove = QPushButton("Rimuovi")
        btn_ok = QPushButton("OK")
        btn_cancel = QPushButton("Annulla")

        btn_add.clicked.connect(self._add_row)
        btn_remove.clicked.connect(self._remove_selected)
        btn_ok.clicked.connect(self._on_ok)
        btn_cancel.clicked.connect(self.reject)

        btn_row = QHBoxLayout()
        btn_row.addWidget(btn_add)
        btn_row.addWidget(btn_remove)
        btn_row.addStretch(1)
        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(btn_ok)

        layout = QVBoxLayout(self)
        layout.addWidget(self._table)
        layout.addWidget(self._lbl_error)
        layout.addLayout(btn_row)

        if data:
            self._load_data(data)

    def _load_data(self, data: dict) -> None:
        self._table.setRowCount(0)
        for k, v in data.items():
            self._add_row(key=str(k), value=str(v))

    def _add_row(self, key: str = "", value: str = "") -> None:
        row = self._table.rowCount()
        self._table.insertRow(row)
        self._table.setItem(row, 0, QTableWidgetItem(key))
        self._table.setItem(row, 1, QTableWidgetItem(value))

    def _remove_selected(self) -> None:
        row = self._table.currentRow()
        if row >= 0:
            self._table.removeRow(row)

    def _on_ok(self) -> None:
        data: dict = {}
        for row in range(self._table.rowCount()):
            key_item = self._table.item(row, 0)
            val_item = self._table.item(row, 1)
            if not key_item:
                continue
            key = key_item.text().strip()
            if not key:
                continue
            val = val_item.text() if val_item else ""
            # Keep as string; conversion performed by caller if needed
            data[key] = val
        try:
            # Validate JSON serializability
            json.dumps(data, ensure_ascii=False)
        except Exception as exc:
            self._lbl_error.setText(str(exc))
            return
        self._result = data
        self.accept()

    @staticmethod
    def edit(parent, current: dict | None) -> dict | None:
        dlg = KeyValueDialog(parent=parent, data=current or {})
        code = dlg.exec()
        try:
            from PyQt6.QtWidgets import QDialog as _QDialog

            accepted = _QDialog.Accepted
        except Exception:
            from PySide6.QtWidgets import QDialog as _QDialog  # type: ignore

            accepted = _QDialog.Accepted

        if code == accepted:
            return dlg._result
        return None
