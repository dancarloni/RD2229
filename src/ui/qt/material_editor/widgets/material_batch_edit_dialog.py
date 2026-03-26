"""
MaterialBatchEditDialog — Dialog batch editing per modifica multipla di materiali.

Permette di applicare lo stesso valore a un campo su N materiali selezionati.
Mostra una preview dei materiali che saranno modificati prima dell'applicazione.
"""

from __future__ import annotations

from typing import Any, Dict, List

try:
    from PyQt6.QtCore import Qt
    from PyQt6.QtWidgets import (
        QComboBox,
        QDialog,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QListWidget,
        QListWidgetItem,
        QPushButton,
        QVBoxLayout,
        QWidget,
    )
except ImportError:
    from PySide6.QtCore import Qt  # type: ignore
    from PySide6.QtWidgets import (  # type: ignore
        QComboBox,
        QDialog,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QListWidget,
        QListWidgetItem,
        QPushButton,
        QVBoxLayout,
        QWidget,
    )


class MaterialBatchEditDialog(QDialog):
    """Dialog per batch editing: stesso valore su N materiali selezionati.

    Uso::

        dlg = MaterialBatchEditDialog(
            materials=[...],
            selected_indices=[0, 2, 5],
            available_fields=["gamma_c", "alpha_cc", "f_ck"],
            parent=self,
        )
        if dlg.exec() == QDialog.DialogCode.Accepted:
            field, value = dlg.get_result()
    """

    def __init__(
        self,
        materials: List[Dict[str, Any]],
        selected_indices: List[int],
        available_fields: List[str] | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Modifica batch materiali")
        self.resize(480, 380)

        self._materials = materials
        self._selected_indices = selected_indices
        self._available_fields = available_fields or []
        self._result_field: str = ""
        self._result_value: Any = None

        self._build_ui()

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        # Intestazione
        n = len(self._selected_indices)
        header = QLabel(f"Applica stesso valore a <b>{n} materiale/i selezionato/i</b>:")
        header.setWordWrap(True)
        layout.addWidget(header)

        # Lista materiali selezionati (preview)
        self._list_preview = QListWidget()
        self._list_preview.setMaximumHeight(120)
        for idx in self._selected_indices:
            mat = self._materials[idx] if idx < len(self._materials) else {}
            label = mat.get("material_id") or mat.get("descrizione") or f"materiale #{idx}"
            norma = mat.get("norma_riferimento") or mat.get("norma", "")
            item_text = f"[{idx}] {label}" + (f"  ({norma})" if norma else "")
            self._list_preview.addItem(QListWidgetItem(item_text))
        layout.addWidget(self._list_preview)

        # Selezione campo
        row_field = QHBoxLayout()
        row_field.addWidget(QLabel("Campo da modificare:"))
        self._combo_field = QComboBox()
        if self._available_fields:
            for f in self._available_fields:
                self._combo_field.addItem(f)
        else:
            # Campi comuni da tutti i materiali selezionati
            common = self._infer_common_fields()
            for f in common:
                self._combo_field.addItem(f)
        row_field.addWidget(self._combo_field, stretch=1)
        layout.addLayout(row_field)

        # Valore
        row_val = QHBoxLayout()
        row_val.addWidget(QLabel("Nuovo valore:"))
        self._edit_value = QLineEdit()
        self._edit_value.setPlaceholderText("es. 1.60")
        row_val.addWidget(self._edit_value, stretch=1)
        layout.addLayout(row_val)

        # Nota
        note = QLabel("⚠ Il valore sarà applicato a tutti i materiali selezionati. L'operazione è reversibile con Ctrl+Z.")
        note.setWordWrap(True)
        note.setStyleSheet("color: #666; font-size: 10px;")
        layout.addWidget(note)

        layout.addStretch()

        # Bottoni
        btn_row = QHBoxLayout()
        self._btn_apply = QPushButton("Applica a tutti")
        self._btn_apply.setDefault(True)
        self._btn_cancel = QPushButton("Annulla")
        btn_row.addWidget(self._btn_apply)
        btn_row.addStretch()
        btn_row.addWidget(self._btn_cancel)
        layout.addLayout(btn_row)

        self._btn_apply.clicked.connect(self._on_apply)
        self._btn_cancel.clicked.connect(self.reject)

    # ------------------------------------------------------------------
    # Logica
    # ------------------------------------------------------------------

    def _infer_common_fields(self) -> List[str]:
        """Restituisce i campi presenti in almeno un materiale selezionato."""
        seen: dict[str, int] = {}
        for idx in self._selected_indices:
            if idx < len(self._materials):
                for k in self._materials[idx]:
                    if not k.endswith("_override") and not k.startswith("_"):
                        seen[k] = seen.get(k, 0) + 1
        # Ordina per frequenza decrescente
        return [k for k, _ in sorted(seen.items(), key=lambda x: -x[1])]

    def _on_apply(self) -> None:
        self._result_field = self._combo_field.currentText().strip()
        raw = self._edit_value.text().strip()
        if not self._result_field:
            return
        if not raw:
            return
        # Converti in numero se possibile
        try:
            self._result_value = float(raw)
        except ValueError:
            self._result_value = raw
        self.accept()

    # ------------------------------------------------------------------
    # Risultato
    # ------------------------------------------------------------------

    def get_result(self) -> tuple[str, Any]:
        """Restituisce (field_name, value) scelti dall'utente."""
        return self._result_field, self._result_value

    # Retrocompatibilità con versione stub
    def get_value(self) -> str:
        return str(self._result_value) if self._result_value is not None else ""
