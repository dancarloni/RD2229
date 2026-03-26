"""MaterialAddWizard — Dialog wizard per aggiungere un nuovo materiale.

Passaggi:
    1. Famiglia, norma, ID, descrizione
    2. Parametri fondamentali con calcolo live dei derivati + formule/riferimenti
    3. Riepilogo finale del materiale
"""

from __future__ import annotations

from typing import Any

try:
    from PyQt6.QtCore import Qt
    from PyQt6.QtWidgets import (
        QCheckBox,
        QComboBox,
        QDialog,
        QFormLayout,
        QGridLayout,
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
except ImportError:
    from PySide6.QtCore import Qt  # type: ignore
    from PySide6.QtWidgets import (  # type: ignore
        QCheckBox,
        QComboBox,
        QDialog,
        QFormLayout,
        QGridLayout,
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
    """Wizard a 3 pagine per creare un nuovo materiale.

    Passo 1: selezione famiglia/norma + identificazione (ID, descrizione).
    Passo 2: inserimento parametri fondamentali con calcolo live dei derivati,
             override manuale e note formula/riferimenti normativi.
    Passo 3: riepilogo finale del materiale.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Aggiungi materiale — Wizard")
        self.setMinimumSize(720, 600)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self._loader = MaterialConfigLoader()
        self._families: list[dict] = self._loader.load_families()
        self._current_schema: dict | None = None

        # Campi input fondamentali (es. f_ck, nu, densita)
        self._param_fields: dict[str, QLineEdit] = {}
        # Campi derivati (readonly, con override)
        self._derived_fields: dict[str, QLineEdit] = {}
        # Checkbox override per ogni derivato
        self._override_checks: dict[str, QCheckBox] = {}

        self._result_material: dict | None = None
        self._summary_mat: dict | None = None

        # ── layout principale ────────────────────────────────────────────────
        outer = QVBoxLayout(self)
        outer.setSpacing(8)

        self._page_title = QLabel("")
        self._page_title.setStyleSheet("font-weight: bold; font-size: 13px;")
        outer.addWidget(self._page_title)

        self._stack = QStackedWidget()
        self._page_identity = self._build_page_identity()
        self._page_params = self._build_page_params()
        self._page_summary = self._build_page_summary()
        self._stack.addWidget(self._page_identity)
        self._stack.addWidget(self._page_params)
        self._stack.addWidget(self._page_summary)
        outer.addWidget(self._stack, stretch=1)

        # Navigazione
        nav = QHBoxLayout()
        self._btn_cancel = QPushButton("Annulla")
        self._btn_back = QPushButton("← Indietro")
        self._btn_next = QPushButton("Avanti →")
        self._btn_create = QPushButton("Fine")
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

    def _build_page_identity(self) -> QWidget:
        """Passo 1: selezione famiglia, norma, ID e descrizione."""
        page = QWidget()
        page_layout = QVBoxLayout(page)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.setSpacing(10)

        info_box = QGroupBox("Identificazione materiale")
        info_box.setStyleSheet("QGroupBox { font-weight: bold; margin-top: 6px; }")
        form = QFormLayout(info_box)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        form.setVerticalSpacing(10)

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

        page_layout.addWidget(info_box)
        page_layout.addStretch()

        # Connessioni
        self._combo_famiglia.currentIndexChanged.connect(self._on_famiglia_changed)
        self._on_famiglia_changed()

        return page

    def _build_page_params(self) -> QWidget:
        """Passo 2: parametri fondamentali + derivati live + formule HTML a lato."""
        page = QWidget()
        page_layout = QVBoxLayout(page)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.setSpacing(6)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._params_container = QWidget()
        self._params_layout = QVBoxLayout(self._params_container)
        self._params_layout.setContentsMargins(0, 0, 0, 0)
        self._params_layout.setSpacing(4)
        scroll.setWidget(self._params_container)
        page_layout.addWidget(scroll, stretch=1)

        return page

    def _build_page_summary(self) -> QWidget:
        """Passo 3: riepilogo finale."""
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
            "Passo 1 — Famiglia, norma e identificazione",
            "Passo 2 — Parametri e calcolo derivati",
            "Passo 3 — Riepilogo materiale",
        ]
        self._page_title.setText(titles[idx])
        self._btn_back.setEnabled(idx > 0)
        self._btn_next.setVisible(idx < 2)
        self._btn_create.setVisible(idx == 2)

    def _go_next(self) -> None:
        idx = self._stack.currentIndex()
        if idx == 0:
            # Costruisce la pagina parametri in base a famiglia+norma scelti
            self._rebuild_params_section()
            self._go_to_page(1)
        elif idx == 1:
            self._populate_summary_page()
            self._go_to_page(2)

    def _go_back(self) -> None:
        idx = self._stack.currentIndex()
        if idx > 0:
            self._go_to_page(idx - 1)

    # ── event handlers ───────────────────────────────────────────────────────

    def _on_famiglia_changed(self) -> None:
        famiglia = self._combo_famiglia.currentData()
        self._combo_norma.blockSignals(True)
        self._combo_norma.clear()
        if not famiglia:
            self._combo_norma.blockSignals(False)
            return
        try:
            norms = self._loader.get_norms_for_family(famiglia)
            for n in norms:
                self._combo_norma.addItem(n.get("label", n["key"]), n["key"])
            if norms:
                self._edit_material_id.setPlaceholderText(
                    f"es. {norms[0].get('key', famiglia).upper()}-001"
                )
        except Exception:
            pass
        self._combo_norma.blockSignals(False)

    def _rebuild_params_section(self) -> None:
        """Ricostruisce la sezione parametri in base a famiglia+norma correnti."""
        famiglia = self._combo_famiglia.currentData()
        norma = self._combo_norma.currentData()
        self._current_schema = None
        self._param_fields.clear()
        self._derived_fields.clear()
        self._override_checks.clear()

        _clear_layout(self._params_layout)

        if not famiglia or not norma:
            return

        try:
            schema = self._loader.get_norm_schema(famiglia, norma)
            self._current_schema = schema
        except Exception as exc:
            self._params_layout.addWidget(QLabel(f"Schema non trovato: {exc}"))
            return

        if not schema:
            self._params_layout.addWidget(
                QLabel(f"Nessuno schema disponibile per {famiglia}/{norma}.")
            )
            return

        input_fields: list[dict] = schema.get("parametri_input", [])
        derived_fields: list[dict] = schema.get("parametri_derivati", [])
        if not input_fields and not derived_fields:
            self._params_layout.addWidget(
                QLabel("Nessun parametro definito in questo schema norma.")
            )
            return

        # Raggruppa i campi per gruppo
        gruppi: list[dict] = schema.get("gruppi") or [{"key": "general", "label": "Parametri"}]
        input_by_group: dict[str, list[dict]] = {}
        derived_by_group: dict[str, list[dict]] = {}
        for f in input_fields:
            gk = f.get("gruppo", "general")
            input_by_group.setdefault(gk, []).append(f)
        for f in derived_fields:
            gk = f.get("gruppo", "general")
            derived_by_group.setdefault(gk, []).append(f)

        # Evita schermate vuote quando i campi usano gruppi non dichiarati nello schema.
        known_group_keys = [g.get("key", "general") for g in gruppi]
        dynamic_group_keys = sorted(set(input_by_group.keys()) | set(derived_by_group.keys()))
        for gk in dynamic_group_keys:
            if gk not in known_group_keys:
                gruppi.append({"key": gk, "label": gk.replace("_", " ").capitalize()})

        rendered_sections = 0

        for grp in gruppi:
            gk = grp["key"]
            inp_fields = input_by_group.get(gk, [])
            drv_fields = derived_by_group.get(gk, [])
            if not inp_fields and not drv_fields:
                continue

            box = QGroupBox(grp.get("label", gk))
            box.setStyleSheet("QGroupBox { font-weight: bold; margin-top: 6px; }")
            grid = QGridLayout(box)
            grid.setColumnStretch(1, 1)
            grid.setColumnStretch(2, 2)
            grid.setHorizontalSpacing(8)
            grid.setVerticalSpacing(4)

            row_idx = 0

            # Campi input fondamentali
            for field in inp_fields:
                key = field["key"]
                label_text = _field_label(field)
                lbl = QLabel(label_text)
                lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                edit = QLineEdit()
                default = field.get("default", "")
                edit.setText(str(default) if default != "" else "")
                edit.setToolTip(field.get("descrizione", ""))
                if field.get("obbligatorio", False):
                    edit.setPlaceholderText("(obbligatorio)")
                self._param_fields[key] = edit
                edit.textChanged.connect(self._live_compute_derived)

                grid.addWidget(lbl, row_idx, 0)
                grid.addWidget(edit, row_idx, 1)

                note = _build_formula_note(field)
                if note:
                    note_lbl = QLabel(note)
                    note_lbl.setTextFormat(Qt.TextFormat.RichText)
                    note_lbl.setWordWrap(True)
                    note_lbl.setStyleSheet("color: #555; font-size: 10px;")
                    grid.addWidget(note_lbl, row_idx, 2)
                row_idx += 1

            # Separatore visivo
            if inp_fields and drv_fields:
                sep = QLabel("── derivati (calcolati automaticamente) ──")
                sep.setStyleSheet("color: #888; font-size: 10px;")
                grid.addWidget(sep, row_idx, 0, 1, 3)
                row_idx += 1

            # Campi derivati con override checkbox e formula HTML a lato
            for fd in drv_fields:
                key = fd["key"]
                label_text = _field_label(fd)

                lbl = QLabel(label_text)
                lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

                # Container: edit + checkbox
                container = QWidget()
                h = QHBoxLayout(container)
                h.setContentsMargins(0, 0, 0, 0)
                h.setSpacing(2)

                edit = QLineEdit()
                edit.setReadOnly(True)
                edit.setStyleSheet("background: #f5f5f5; color: #555;")
                edit.setToolTip(fd.get("descrizione", ""))
                self._derived_fields[key] = edit

                cb = QCheckBox()
                cb.setToolTip("Override manuale: attiva per modificare il valore calcolato")
                cb.setFixedWidth(18)
                self._override_checks[key] = cb

                def _on_override(checked: bool, _e: QLineEdit = edit) -> None:
                    _e.setReadOnly(not checked)
                    _e.setStyleSheet("" if checked else "background: #f5f5f5; color: #555;")

                cb.toggled.connect(_on_override)
                h.addWidget(edit, stretch=1)
                h.addWidget(cb)

                grid.addWidget(lbl, row_idx, 0)
                grid.addWidget(container, row_idx, 1)

                # Formula HTML a lato (col 2)
                note = _build_formula_note(fd)
                if note:
                    formula_lbl = QLabel(note)
                    formula_lbl.setTextFormat(Qt.TextFormat.RichText)
                    formula_lbl.setWordWrap(True)
                    formula_lbl.setStyleSheet("color: #555; font-size: 10px;")
                    grid.addWidget(formula_lbl, row_idx, 2)

                row_idx += 1

            self._params_layout.addWidget(box)
            rendered_sections += 1

        if rendered_sections == 0:
            self._params_layout.addWidget(
                QLabel("Schema presente ma nessun gruppo valido da visualizzare.")
            )
            self._params_layout.addStretch()
            return

        self._params_layout.addStretch()

        # Calcola subito i derivati con i valori default
        self._live_compute_derived()

    def _live_compute_derived(self) -> None:
        """Ricalcola i derivati in real-time e aggiorna i campi non-override."""
        if not self._current_schema:
            return
        mat = self._collect_material()
        try:
            derived = self._loader.compute_derived(
                mat, self._current_schema, famiglia=mat.get("famiglia")
            )
            derived.pop("_formula_warnings", None)
        except Exception:
            return
        for key, val in derived.items():
            if key not in self._derived_fields:
                continue
            cb = self._override_checks.get(key)
            if cb and cb.isChecked():
                continue  # override attivo, non sovrascrivere
            edit = self._derived_fields[key]
            edit.setText("" if val is None else str(round(val, 4)) if isinstance(val, float) else str(val))

    def _populate_summary_page(self) -> None:
        """Ricostruisce il riepilogo con i valori finali del materiale."""
        _clear_layout(self._summary_layout)

        mat = self._collect_material()

        # Calcola derivati finali (tenendo conto degli override)
        if self._current_schema:
            try:
                derived = self._loader.compute_derived(
                    mat, self._current_schema, famiglia=mat.get("famiglia")
                )
                warnings = derived.pop("_formula_warnings", [])
                for key, val in derived.items():
                    cb = self._override_checks.get(key)
                    if cb and cb.isChecked():
                        pass  # mantieni il valore manuale già nel dict
                    else:
                        mat[key] = val
                if warnings:
                    warn_label = QLabel("⚠ " + "; ".join(warnings))
                    warn_label.setStyleSheet("color: #b35f00; font-size: 10px;")
                    warn_label.setWordWrap(True)
                    self._summary_layout.addWidget(warn_label)
            except Exception as exc:
                self._summary_layout.addWidget(QLabel(f"Errore calcolo derivati: {exc}"))

        self._summary_mat = mat

        # Valori del materiale
        box_vals = QGroupBox("Materiale da creare")
        box_vals.setStyleSheet("QGroupBox { font-weight: bold; margin-top: 6px; }")
        form_vals = QFormLayout(box_vals)
        form_vals.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        for k, v in mat.items():
            if k.startswith("_") or k == "id":
                continue
            val_str = str(round(v, 4)) if isinstance(v, float) else str(v) if v is not None else ""
            form_vals.addRow(QLabel(f"{k}:"), QLabel(val_str))
        self._summary_layout.addWidget(box_vals)

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
        # Includi i derivati override
        for key, edit in self._derived_fields.items():
            cb = self._override_checks.get(key)
            if cb and cb.isChecked():
                text = edit.text().strip()
                mat[key] = _try_float(text)
                mat[f"{key}_override"] = True
        return mat

    def _on_create(self) -> None:
        self._result_material = self._summary_mat or self._collect_material()
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


def _build_formula_note(field: dict) -> str:
    """Ritorna una nota compatta con formula/riferimento in formato rich-text."""
    formula_html = field.get("formula_html", "")
    formula_plain = field.get("formula", "")
    rif_norm = field.get("rif_norm", "")

    formula_text = ""
    if formula_html:
        formula_text = f"<i>{formula_html}</i>"
    elif formula_plain:
        formula_text = f"<code>{formula_plain}</code>"

    if not formula_text and not rif_norm:
        return ""

    out = f"<small>{formula_text}"
    if rif_norm and rif_norm != "—":
        out += f" <span style='color:#888'>[{rif_norm}]</span>"
    out += "</small>"
    return out


def _make_formula_widget(latex_str: str, plain_formula: str) -> QWidget:
    """Crea un widget che mostra la formula: immagine LaTeX o testo plain come fallback."""
    if latex_str:
        pix = _render_latex_to_pixmap(latex_str)
        if pix is not None and not pix.isNull():
            lbl = QLabel()
            lbl.setPixmap(pix)
            lbl.setWordWrap(False)
            return lbl

    # Fallback: testo plain
    lbl = QLabel(plain_formula)
    lbl.setStyleSheet("color: #555; font-style: italic; font-size: 10px; font-family: monospace;")
    lbl.setWordWrap(True)
    return lbl


def _render_latex_to_pixmap(latex_str: str, fontsize: int = 11, dpi: int = 120):
    """Renderizza una stringa LaTeX/mathtext in un QPixmap via matplotlib.

    Usa il renderer mathtext interno (usetex=False): non richiede LaTeX di sistema.
    Restituisce None in caso di errore.
    """
    try:
        import io

        import matplotlib
        if matplotlib.get_backend().lower() != "agg":
            matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        try:
            from PyQt6.QtGui import QPixmap
        except ImportError:
            from PySide6.QtGui import QPixmap  # type: ignore

        fig, ax = plt.subplots(figsize=(5.5, 0.6))
        ax.axis("off")
        ax.text(
            0.02, 0.5, latex_str,
            fontsize=fontsize, ha="left", va="center",
            transform=ax.transAxes, usetex=False,
        )
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=dpi, bbox_inches="tight",
                    transparent=True, pad_inches=0.03)
        plt.close(fig)
        buf.seek(0)
        pix = QPixmap()
        pix.loadFromData(buf.read())
        return pix
    except Exception:
        return None
