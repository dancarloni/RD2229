"""Dialog per importare materiali dal `MaterialRepository`.

Restituisce l'oggetto `Material` selezionato o `None` se annullato.
Dialog minimale: lista materiali + pulsante Importa/Annulla.
"""

from __future__ import annotations

try:
    from PyQt6.QtWidgets import QDialog, QHBoxLayout, QLabel, QListWidget, QPushButton, QVBoxLayout
except ImportError:  # pragma: no cover
    from PySide6.QtWidgets import (
        QDialog,
        QVBoxLayout,
        QListWidget,
        QHBoxLayout,
        QPushButton,
        QLabel,
    )

from typing import Optional

from src.materials.material_repo import MaterialRepository


class MaterialImportDialog(QDialog):
    def __init__(self, material_repo: MaterialRepository, parent=None):  # pragma: no cover - UI
        super().__init__(parent)
        self.setWindowTitle("Importa materiale da archivio")
        self._repo = material_repo
        self._selected = None

        root = QVBoxLayout(self)
        self._list = QListWidget(self)
        for m in self._repo.list_all():
            self._list.addItem(f"{m.material_id} — {m.descrizione}")
        root.addWidget(self._list)

        row = QHBoxLayout()
        self._lbl_info = QLabel("")
        row.addWidget(self._lbl_info)
        row.addStretch(1)
        self._btn_cancel = QPushButton("Annulla")
        self._btn_import = QPushButton("Importa")
        row.addWidget(self._btn_cancel)
        row.addWidget(self._btn_import)
        root.addLayout(row)

        self._btn_cancel.clicked.connect(self.reject)
        self._btn_import.clicked.connect(self._on_import)

    def _on_import(self) -> None:
        idx = self._list.currentRow()
        if idx < 0:
            self._lbl_info.setText("Seleziona un materiale da importare")
            return
        items = self._repo.list_all()
        if idx >= len(items):
            self._lbl_info.setText("Selezione non valida")
            return
        self._selected = items[idx]
        self.accept()

    @staticmethod
    def select_material(parent, material_repo: Optional[MaterialRepository]):
        if material_repo is None:
            return None
        dlg = MaterialImportDialog(material_repo, parent=parent)
        code = dlg.exec()
        try:
            from PyQt6.QtWidgets import QDialog as _QDlg

            accepted = _QDlg.DialogCode.Accepted
        except ImportError:
            from PySide6.QtWidgets import QDialog as _QDlg  # type: ignore

            accepted = _QDlg.DialogCode.Accepted

        if code == accepted:
            return getattr(dlg, "_selected", None)
        return None
