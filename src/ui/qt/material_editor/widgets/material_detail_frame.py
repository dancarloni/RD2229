"""
MaterialDetailFrame — Frame dettaglio materiale con layout 2 colonne.

Layout a griglia (4 colonne: etichetta | campo | etichetta | campo) per
mostrare tutti i parametri senza scroll verticale.

Supporta due modalità:
- Schema-aware: `set_fields(material, norm_schema)` genera campi da schema norma.
  Input principali: editabili; derivati: readonly (a meno di override checkbox).
- Fallback flat: `set_fields(material)` senza schema, crea una riga per ogni campo.
"""

from typing import Any, Dict, List, Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


class MaterialDetailFrame(QWidget):
    """Frame laterale di dettaglio/editing per un materiale. Layout 2 colonne, no scroll."""

    # Emesso quando un campo input principale cambia valore
    inputChanged = Signal()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._fields: Dict[str, QLineEdit] = {}
        self._overrides: Dict[str, QCheckBox] = {}
        self._is_derived: Dict[str, bool] = {}

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(4)

        # ── area warning ──────────────────────────────────────────────────────
        self.warning_label = QLabel("")
        self.warning_label.setStyleSheet("color: #b35f00; font-size: 11px;")
        self.warning_label.setWordWrap(True)
        self.warning_label.setVisible(False)
        outer.addWidget(self.warning_label)

        # ── area campi (no scroll) ────────────────────────────────────────────
        self._fields_widget = QWidget()
        self._fields_widget.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self._fields_container = QVBoxLayout(self._fields_widget)
        self._fields_container.setContentsMargins(4, 4, 4, 4)
        self._fields_container.setSpacing(4)
        outer.addWidget(self._fields_widget, stretch=1)

        # ── pulsanti ──────────────────────────────────────────────────────────
        btn_layout = QHBoxLayout()
        self.reset_derived_button = QPushButton("Reset derivati")
        self.reset_derived_button.setToolTip(
            "Riporta tutti i campi derivati al calcolo automatico (rimuove override)"
        )
        self.save_button = QPushButton("Salva")
        self.cancel_button = QPushButton("Annulla")
        btn_layout.addWidget(self.reset_derived_button)
        btn_layout.addStretch()
        btn_layout.addWidget(self.save_button)
        btn_layout.addWidget(self.cancel_button)
        outer.addLayout(btn_layout)

    # ── API pubblica ─────────────────────────────────────────────────────────

    def set_fields(
        self,
        material: Dict[str, Any],
        norm_schema: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Popola il frame con i campi del materiale.

        Se `norm_schema` è fornito, genera la UI in gruppi secondo lo schema
        (input principali editabili, derivati readonly con override checkbox).
        Altrimenti genera una lista flat di campi editabili per tutti i valori.
        """
        self._clear_fields()

        if norm_schema:
            self._build_from_schema(material, norm_schema)
        else:
            self._build_flat(material)

        self._fields_container.addStretch(1)

    def get_field_values(self) -> Dict[str, Any]:
        """Restituisce i valori correnti di tutti i campi (stringa grezza)."""
        result: Dict[str, Any] = {}
        for key, widget in self._fields.items():
            text = widget.text().strip()
            result[key] = _try_float(text)
        return result

    def get_overrides(self) -> Dict[str, bool]:
        """Restituisce lo stato degli override per i campi derivati."""
        return {k: cb.isChecked() for k, cb in self._overrides.items()}

    def reset_all_overrides(self) -> None:
        """Deseleziona tutti gli override e rende readonly i campi derivati."""
        for key, cb in self._overrides.items():
            cb.setChecked(False)
            if key in self._fields:
                self._fields[key].setReadOnly(True)
                self._fields[key].setStyleSheet(_DERIVED_STYLE)

    def update_derived_values(self, derived: Dict[str, Any]) -> None:
        """Aggiorna solo i campi derivati non-override con i valori calcolati."""
        for key, val in derived.items():
            if key == "_formula_warnings":
                continue
            if key in self._fields and self._is_derived.get(key, False):
                cb = self._overrides.get(key)
                if cb and cb.isChecked():
                    continue  # override attivo, non sovrascrivere
                self._fields[key].setText("" if val is None else str(round(val, 4)))

    def set_warning(self, text: str) -> None:
        if text:
            self.warning_label.setText(text)
            self.warning_label.setVisible(True)
        else:
            self.warning_label.setText("")
            self.warning_label.setVisible(False)

    # ── internals ────────────────────────────────────────────────────────────

    def _clear_fields(self) -> None:
        """Rimuove tutti i widget dal container."""
        while self._fields_container.count():
            item = self._fields_container.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()
        self._fields.clear()
        self._overrides.clear()
        self._is_derived.clear()

    def _build_from_schema(self, material: Dict[str, Any], norm_schema: Dict[str, Any]) -> None:
        """Costruisce i campi da schema norma con layout 2 colonne per gruppo."""
        gruppi_schema: List[Dict] = norm_schema.get("gruppi") or []

        # Determina i gruppi usati
        used_groups: set[str] = set()
        for f in norm_schema.get("parametri_input", []):
            used_groups.add(f.get("gruppo", "general"))
        for f in norm_schema.get("parametri_derivati", []):
            used_groups.add(f.get("gruppo", "general"))

        groups_ordered: List[Dict] = [g for g in gruppi_schema if g["key"] in used_groups]
        keys_already = {g["key"] for g in groups_ordered}
        for g in used_groups:
            if g not in keys_already:
                groups_ordered.append({"key": g, "label": g.capitalize()})

        # Raggruppa i campi per gruppo
        input_by_group: Dict[str, List[Dict]] = {}
        derived_by_group: Dict[str, List[Dict]] = {}
        for f in norm_schema.get("parametri_input", []):
            gk = f.get("gruppo", "general")
            input_by_group.setdefault(gk, []).append(f)
        for f in norm_schema.get("parametri_derivati", []):
            gk = f.get("gruppo", "general")
            derived_by_group.setdefault(gk, []).append(f)

        # Coefficienti normativi → gruppo speciale con griglia 2 colonne
        spec: Dict[str, Any] = norm_schema.get("parametri_specifici", {})
        if spec:
            box = _make_group_box("Coefficienti normativi")
            grid = QGridLayout()
            grid.setSpacing(3)
            grid.setColumnStretch(1, 1)
            grid.setColumnStretch(3, 1)
            grid_row = 0
            col_pair = 0
            for pkey, pinfo in spec.items():
                if not isinstance(pinfo, dict):
                    continue
                lbl = pinfo.get("label", pkey)
                unit = pinfo.get("unita", "")
                val = material.get(pkey, pinfo.get("valore", ""))
                label_text = f"{lbl} [{unit}]:" if unit else f"{lbl}:"
                edit = _make_display_line(str(val) if val != "" else str(pinfo.get("valore", "")))
                edit.setToolTip(pinfo.get("descrizione", ""))
                self._fields[pkey] = edit
                self._is_derived[pkey] = False
                col_offset = col_pair * 2
                grid.addWidget(QLabel(label_text), grid_row, col_offset, Qt.AlignRight)
                grid.addWidget(edit, grid_row, col_offset + 1)
                if col_pair == 1:
                    grid_row += 1
                col_pair ^= 1
            if col_pair == 1:  # riga parziale: avanza
                grid_row += 1
            box.setLayout(grid)
            self._fields_container.addWidget(box)

        # Crea un QGroupBox con griglia 2 colonne per ogni gruppo
        for grp in groups_ordered:
            gk = grp["key"]
            gl = grp.get("label", gk)
            inp_fields = input_by_group.get(gk, [])
            drv_fields = derived_by_group.get(gk, [])
            if not inp_fields and not drv_fields:
                continue

            box = _make_group_box(gl)
            grid = QGridLayout()
            grid.setSpacing(3)
            # Colonne: 0=label_sx, 1=field_sx, 2=label_dx, 3=field_dx
            grid.setColumnStretch(1, 1)
            grid.setColumnStretch(3, 1)
            grid_row = 0
            col_pair = 0  # 0 = colonna sinistra, 1 = colonna destra

            # Input principali
            for field in inp_fields:
                label_text = _field_label(field)
                edit = self._make_input_edit(field, material)
                col_offset = col_pair * 2
                grid.addWidget(QLabel(label_text), grid_row, col_offset, Qt.AlignRight)
                grid.addWidget(edit, grid_row, col_offset + 1)
                if col_pair == 1:
                    grid_row += 1
                col_pair ^= 1

            # Separatore tra input e derivati (span 4 colonne)
            if inp_fields and drv_fields:
                if col_pair == 1:
                    grid_row += 1
                    col_pair = 0
                sep = QLabel("── derivati ──")
                sep.setStyleSheet("color: #888; font-size: 10px;")
                grid.addWidget(sep, grid_row, 0, 1, 4)
                grid_row += 1

            # Derivati: label + (field + checkbox) per coppia
            for field in drv_fields:
                label_text = _field_label(field)
                field_w, edit = self._make_derived_widget(field, material)
                col_offset = col_pair * 2
                grid.addWidget(QLabel(label_text), grid_row, col_offset, Qt.AlignRight)
                grid.addWidget(field_w, grid_row, col_offset + 1)
                if col_pair == 1:
                    grid_row += 1
                col_pair ^= 1

            box.setLayout(grid)
            self._fields_container.addWidget(box)

    def _build_flat(self, material: Dict[str, Any]) -> None:
        """Fallback: griglia 2 colonne per ogni chiave del dict."""
        box = _make_group_box("Parametri")
        grid = QGridLayout()
        grid.setSpacing(3)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(3, 1)
        grid_row = 0
        col_pair = 0
        for key, value in material.items():
            if key in ("id",):
                continue
            edit = QLineEdit()
            edit.setText(str(value) if value is not None else "")
            edit.textChanged.connect(self.inputChanged)
            self._fields[key] = edit
            self._is_derived[key] = False
            col_offset = col_pair * 2
            grid.addWidget(QLabel(f"{key}:"), grid_row, col_offset, Qt.AlignRight)
            grid.addWidget(edit, grid_row, col_offset + 1)
            if col_pair == 1:
                grid_row += 1
            col_pair ^= 1
        box.setLayout(grid)
        self._fields_container.addWidget(box)

    def _make_input_edit(self, field: Dict, material: Dict[str, Any]) -> QLineEdit:
        """Crea un QLineEdit editabile per un campo input principale."""
        key = field["key"]
        val = material.get(key, field.get("default", ""))
        edit = QLineEdit()
        edit.setText(str(val) if val is not None and val != "" else "")
        edit.setToolTip(field.get("descrizione", ""))
        edit.textChanged.connect(self.inputChanged)
        self._fields[key] = edit
        self._is_derived[key] = False
        return edit

    def _make_derived_widget(self, field: Dict, material: Dict[str, Any]) -> tuple:
        """Crea un widget (field + checkbox override) per un campo derivato.

        Restituisce (container_widget, QLineEdit).
        """
        key = field["key"]
        val = material.get(key, "")
        has_override = bool(material.get(f"{key}_override", False))

        container = QWidget()
        h = QHBoxLayout(container)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(2)

        edit = QLineEdit()
        edit.setText(
            str(round(val, 4)) if isinstance(val, (int, float)) else str(val) if val else ""
        )
        edit.setToolTip(field.get("descrizione", ""))
        edit.setReadOnly(not has_override)
        edit.setStyleSheet(_DERIVED_OVERRIDE_STYLE if has_override else _DERIVED_STYLE)
        self._fields[key] = edit
        self._is_derived[key] = True

        cb = QCheckBox()
        cb.setToolTip("Personalizza (sovrascrive calcolo automatico)")
        cb.setChecked(has_override)
        cb.setFixedSize(14, 14)
        cb.setStyleSheet("QCheckBox { margin: 0px; padding: 0px; }")
        self._overrides[key] = cb

        def _on_override_toggled(checked: bool, _key: str = key, _edit: QLineEdit = edit) -> None:
            _edit.setReadOnly(not checked)
            _edit.setStyleSheet(_DERIVED_OVERRIDE_STYLE if checked else _DERIVED_STYLE)

        cb.toggled.connect(_on_override_toggled)
        h.addWidget(edit, stretch=1)
        h.addWidget(cb)
        return container, edit


# ── helpers ───────────────────────────────────────────────────────────────────

_DERIVED_STYLE = "background-color: #f0f0f0; color: #555;"
_DERIVED_OVERRIDE_STYLE = "background-color: #fffbe6; border: 1px solid #f0a500; color: #333;"
_INPUT_STYLE = ""


def _make_group_box(title: str) -> QGroupBox:
    box = QGroupBox(title)
    box.setStyleSheet("QGroupBox { font-weight: bold; margin-top: 6px; }")
    box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    return box


def _field_label(field: Dict) -> str:
    lbl = field.get("label", field.get("key", "?"))
    unit = field.get("unita", "")
    return f"{lbl} [{unit}]:" if unit else f"{lbl}:"


def _try_float(text: str) -> Any:
    try:
        return float(text)
    except (ValueError, TypeError):
        return text if text else None


def _make_display_line(text: str) -> QLineEdit:
    edit = QLineEdit(text)
    edit.setReadOnly(True)
    edit.setStyleSheet(_DERIVED_STYLE)
    return edit


# ── standalone ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys

    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    frame = MaterialDetailFrame()
    frame.set_fields({"f_ck": 254.9, "E": 310000, "gamma_c": 1.5})
    frame.show()
    sys.exit(app.exec())
