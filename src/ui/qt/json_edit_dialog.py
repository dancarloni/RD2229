"""Dialog per modificare campi JSON (campo `extra`) con validazione minima.

Modulare e riutilizzabile in altri editor di tabella.
"""

from __future__ import annotations

try:
    from PyQt6.QtWidgets import QDialog, QHBoxLayout, QLabel, QPushButton, QTextEdit, QVBoxLayout
except ImportError:  # pragma: no cover - fallback PySide6
    from PySide6.QtWidgets import (
        QDialog,
        QVBoxLayout,
        QTextEdit,
        QHBoxLayout,
        QPushButton,
        QLabel,
    )

import json


class JsonEditDialog(QDialog):
    """Semplice dialog per editare una stringa JSON con validazione.

    Use:
        new_json = JsonEditDialog.edit_json(parent, current_json)
    Restituisce la stringa JSON canonica (ensure_ascii=False) o None se annullato.
    """

    def __init__(self, parent=None, initial: str = "{}"):  # pragma: no cover - UI
        super().__init__(parent)
        self.setWindowTitle("Modifica JSON")
        self._result: str | None = None

        root = QVBoxLayout(self)
        self._edit = QTextEdit(self)
        self._edit.setPlainText(initial)
        root.addWidget(self._edit)

        row = QHBoxLayout()
        self._lbl_error = QLabel("")
        self._lbl_error.setStyleSheet("color: red;")
        row.addWidget(self._lbl_error)
        row.addStretch(1)
        self._btn_cancel = QPushButton("Annulla")
        self._btn_ok = QPushButton("OK")
        row.addWidget(self._btn_cancel)
        row.addWidget(self._btn_ok)
        root.addLayout(row)

        self._btn_cancel.clicked.connect(self.reject)
        self._btn_ok.clicked.connect(self._on_ok)

    def _on_ok(self) -> None:
        txt = self._edit.toPlainText()
        try:
            parsed = json.loads(txt) if txt.strip() else {}
            self._result = json.dumps(parsed, ensure_ascii=False)
            self.accept()
        except Exception as exc:
            # Mostra errore di parsing senza chiudere il dialog
            self._lbl_error.setText(str(exc))

    @staticmethod
    def edit_json(parent, current: str | None) -> str | None:
        dlg = JsonEditDialog(parent=parent, initial=current or "{}")
        code = dlg.exec()
        try:
            from PyQt6.QtWidgets import QDialog as _QDlg

            accepted = _QDlg.DialogCode.Accepted
        except ImportError:
            from PySide6.QtWidgets import QDialog as _QDlg  # type: ignore

            accepted = _QDlg.DialogCode.Accepted

        if code == accepted:
            return getattr(dlg, "_result", current)
        return None
