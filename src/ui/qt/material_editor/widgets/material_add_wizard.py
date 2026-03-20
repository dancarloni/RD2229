"""
MaterialAddWizard — Dialog wizard per aggiungere un nuovo materiale.

Passaggi:
  1. Seleziona famiglia + norma di riferimento + info base (ID, descrizione)
  2. Compila i parametri input da schema norma
  3. Riepilogo con anteprima campi derivati calcolati
"""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from src.ui.qt.material_editor.logic.material_config import MaterialConfigLoader


class MaterialAddWizard(QDialog):
    """Wizard a 3 pagine per creare un nuovo materiale."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Aggiungi materiale — Wizard")
        self.setMinimumSize(520, 540)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self._loader = MaterialConfigLoader()
        self._families: list[dict] = self._loader.load_families()
        self._current_schema: dict | None = None
        self._param_fields: dict[str, QLineEdit] = {}
        self._result_material: dict | None = None

        # ── layout principale ────────────────────────────────────────────────
        outer = QVBoxLayout(self)
        outer.setSpacing(8)

        # Titolo pagina
        self._page_title = QLabel("")
        self._page_title.setStyleSheet("font-weight: bold; font-size: 13px;")
        outer.addWidget(self._page_title)

        # Stack
        self._stack = QStackedWidget()
        self._page_basic = self._build_page_basic()
        self._page_params = self._build_page_params()
        self._page_summary = self._build_page_summary()
        self._stack.addWidget(self._page_basic)
        self._stack.addWidget(self._page_params)
        self._stack.addWidget(self._page_summary)
        outer.addWidget(self._stack, stretch=1)

        # Navigazione
        nav = QHBoxLayout()
        self._btn_cancel = QPushButton("Annulla")
        self._btn_back = QPushButton("← Indietro")
        self._btn_next = QPushButton("Avanti →")
        self._btn_create = QPushButton("Crea materiale")
        self._btn_create.setDefault(True)
        nav.addWidget(self._btn_cancel)
        nav.addStretch()
        nav.addWidget(self._btn_back)
        nav.addWidget(self._btn_next)
        nav.addWidget(self._btn_create)
        outer.addLayout(nav)

        self._btn_cancel.clicked.connect(self.reject)
        self._btn_back.clicked.connect(self._go_back)
        self._btn_next.clicked.connect(self._go_next)
        self._btn_create.clicked.connect(self._on_create)

        self._go_to_page(0)

    # ── build pages ──────────────────────────────────────────────────────────

    def _build_page_basic(self) -> QWidget:
        page = QWidget()
        form = QFormLayout(page)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)

        self._combo_famiglia = QComboBox()
        for f in self._families:
            self._combo_famiglia.addItem(f.get("label", f["key"]), f["key"])
        form.addRow("Famiglia:", self._combo_famiglia)

        self._combo_norma = QComboBox()
        form.addRow("Norma di riferimento:", self._combo_norma)

        self._edit_material_id = QLineEdit()
        self._edit_material_id.setPlaceholderText("es. C25/30")
        form.addRow("ID Materiale:", self._edit_material_id)

        self._edit_descrizione = QLineEdit()
        self._edit_descrizione.setPlaceholderText("Descrizione estesa del materiale")
        form.addRow("Descrizione:", self._edit_descrizione)

        self._combo_famiglia.currentIndexChanged.connect(self._on_famiglia_changed)
        self._on_famiglia_changed()

        return page

    def _build_page_params(self) -> QWidget:
        page = QWidget()
        page_layout = QVBoxLayout(page)
        page_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._params_container = QWidget()
        self._params_layout = QVBoxLayout(self._params_container)
        self._params_layout.setContentsMargins(4, 4, 4, 4)
        scroll.setWidget(self._params_container)
        page_layout.addWidget(scroll)

        return page

    def _build_page_summary(self) -> QWidget:
        page = QWidget()
        page_layout = QVBoxLayout(page)
        page_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._summary_container = QWidget()
        self._summary_layout = QVBoxLayout(self._summary_container)
        self._summary_layout.setContentsMargins(4, 4, 4, 4)
        scroll.setWidget(self._summary_container)
        page_layout.addWidget(scroll)

        return page

    # ── navigation ───────────────────────────────────────────────────────────

    def _go_to_page(self, idx: int) -> None:
        self._stack.setCurrentIndex(idx)
        titles = [
            "Passo 1 — Selezione famiglia e norma",
            "Passo 2 — Parametri del materiale",
            "Passo 3 — Riepilogo e conferma",
        ]
        self._page_title.setText(titles[idx])
        self._btn_back.setEnabled(idx > 0)
        self._btn_next.setVisible(idx < 2)
        self._btn_create.setVisible(idx == 2)

    def _go_next(self) -> None:
        current = self._stack.currentIndex()
        if current == 0:
            self._populate_params_page()
            self._go_to_page(1)
        elif current == 1:
            self._populate_summary_page()
            self._go_to_page(2)

    def _go_back(self) -> None:
        current = self._stack.currentIndex()
        if current > 0:
            self._go_to_page(current - 1)

    # ── event handlers ───────────────────────────────────────────────────────

    def _on_famiglia_changed(self) -> None:
        famiglia = self._combo_famiglia.currentData()
        self._combo_norma.clear()
        if not famiglia:
            return
        try:
            norms = self._loader.get_norms_for_family(famiglia)
            for n in norms:
                self._combo_norma.addItem(n.get("label", n["key"]), n["key"])
            # Auto-suggest material_id prefix
            if norms:
                self._edit_material_id.setPlaceholderText(
                    f"es. {norms[0].get('key', famiglia).upper()}-001"
                )
        except Exception:
            pass

    def _populate_params_page(self) -> None:
        """Ricostruisce il form con i campi input dalla schema norma scelta."""
        famiglia = self._combo_famiglia.currentData()
        norma = self._combo_norma.currentData()
        self._current_schema = None
        self._param_fields.clear()

        # Svuota il container
        _clear_layout(self._params_layout)

        if not famiglia or not norma:
            self._params_layout.addWidget(QLabel("Selezionare una norma valida al passo 1."))
            return

        try:
            schema = self._loader.get_norm_schema(famiglia, norma)
            self._current_schema = schema
        except Exception as exc:
            self._params_layout.addWidget(QLabel(f"Schema non trovato: {exc}"))
            return

        if not schema:
            self._params_layout.addWidget(QLabel("Nessun parametro definito per questa norma."))
            return

        # Raggruppa i campi per gruppo
        gruppi: list[dict] = schema.get("gruppi") or [{"key": "general", "label": "Parametri"}]
        input_by_group: dict[str, list[dict]] = {}
        for f in schema.get("parametri_input", []):
            gk = f.get("gruppo", "general")
            input_by_group.setdefault(gk, []).append(f)

        for grp in gruppi:
            gk = grp["key"]
            fields = input_by_group.get(gk, [])
            if not fields:
                continue
            box = QGroupBox(grp.get("label", gk))
            box.setStyleSheet("QGroupBox { font-weight: bold; margin-top: 6px; }")
            form = QFormLayout(box)
            form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
            for field in fields:
                key = field["key"]
                label = _field_label(field)
                edit = QLineEdit()
                default = field.get("default", "")
                edit.setText(str(default) if default != "" else "")
                edit.setToolTip(field.get("descrizione", ""))
                if field.get("obbligatorio", False):
                    edit.setPlaceholderText("(obbligatorio)")
                self._param_fields[key] = edit
                form.addRow(QLabel(label), edit)
            self._params_layout.addWidget(box)

        # Campi derivati: mostra in sola lettura (calcolati nel riepilogo)
        derived = schema.get("parametri_derivati", [])
        if derived:
            box_drv = QGroupBox("Campi derivati (calcolati automaticamente)")
            box_drv.setStyleSheet("QGroupBox { font-weight: bold; margin-top: 6px; color: #555; }")
            form_drv = QFormLayout(box_drv)
            form_drv.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
            for fd in derived:
                label = _field_label(fd)
                formula = fd.get("formula", "")
                info = QLabel(f"= {formula}" if formula else "(formula non definita)")
                info.setStyleSheet("color: #777; font-style: italic; font-size: 10px;")
                form_drv.addRow(QLabel(label), info)
            self._params_layout.addWidget(box_drv)

        self._params_layout.addStretch()

    def _populate_summary_page(self) -> None:
        """Ricostruisce il riepilogo con valori inseriti + derivati calcolati."""
        _clear_layout(self._summary_layout)

        mat = self._collect_material()

        # Calcola derivati
        if self._current_schema:
            try:
                derived = self._loader.compute_derived(mat, self._current_schema)
                warnings = derived.pop("_formula_warnings", [])
                mat.update(derived)
                if warnings:
                    warn_label = QLabel("⚠ " + "; ".join(warnings))
                    warn_label.setStyleSheet("color: #b35f00; font-size: 10px;")
                    warn_label.setWordWrap(True)
                    self._summary_layout.addWidget(warn_label)
            except Exception as exc:
                self._summary_layout.addWidget(QLabel(f"Errore calcolo derivati: {exc}"))

        self._summary_mat = mat

        # Mostra riepilogo in un form
        box = QGroupBox("Materiale da creare")
        box.setStyleSheet("QGroupBox { font-weight: bold; margin-top: 6px; }")
        form = QFormLayout(box)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        for k, v in mat.items():
            if k.startswith("_") or k == "id":
                continue
            val_str = str(round(v, 4)) if isinstance(v, float) else str(v) if v is not None else ""
            form.addRow(QLabel(f"{k}:"), QLabel(val_str))
        self._summary_layout.addWidget(box)
        self._summary_layout.addStretch()

    def _collect_material(self) -> dict[str, Any]:
        mat: dict[str, Any] = {}
        mat["famiglia"] = self._combo_famiglia.currentData() or ""
        mat["norma_riferimento"] = self._combo_norma.currentData() or ""
        mat["material_id"] = self._edit_material_id.text().strip()
        mat["descrizione"] = self._edit_descrizione.text().strip()
        for key, edit in self._param_fields.items():
            text = edit.text().strip()
            mat[key] = _try_float(text)
        return mat

    def _on_create(self) -> None:
        self._result_material = getattr(self, "_summary_mat", None) or self._collect_material()
        self.accept()

    def get_result_material(self) -> dict[str, Any] | None:
        """Restituisce il materiale creato dopo che il wizard è stato accettato."""
        return self._result_material


# ── helpers ───────────────────────────────────────────────────────────────────


def _field_label(field: dict) -> str:
    lbl = field.get("label", field.get("key", "?"))
    unit = field.get("unita", "")
    return f"{lbl} [{unit}]:" if unit else f"{lbl}:"


def _try_float(text: str) -> Any:
    if not text:
        return None
    try:
        return float(text)
    except (ValueError, TypeError):
        return text


def _clear_layout(layout: QVBoxLayout) -> None:
    while layout.count():
        item = layout.takeAt(0)
        if item is None:
            continue
        w = item.widget()
        if w is not None:
            w.deleteLater()
