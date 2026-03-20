"""
MaterialCoefficientsSettingsWidget — Widget per la gestione globale dei coefficienti normativi.

Integra la scheda "Materiali" nelle Impostazioni Generali del software.
Permette all'utente di visualizzare e sovrascrivere globalmente i coefficienti
normativi (gamma_c, gamma_s, gamma_M, alpha_cc, ecc.) per ogni norma/famiglia.

Architettura (Level 2 override):
  docs/ARCHITECTURE_MATERIAL_GOVERNANCE.md
"""

from __future__ import annotations

import logging

from PySide6.QtCore import Signal
from PySide6.QtGui import QDoubleValidator
from PySide6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

logger = logging.getLogger(__name__)

# Importa i moduli di governance
try:
    from src.core.normative_defaults import NormativeDefaultsLoader
    from src.core.material_global_config import GlobalMaterialCoefficientsManager
except ImportError:
    NormativeDefaultsLoader = None  # type: ignore[assignment,misc]
    GlobalMaterialCoefficientsManager = None  # type: ignore[assignment,misc]

# Famiglie da mostrare per ogni norma (ordine preferito)
_FAMIGLIE_ORDER = ["calcestruzzo", "acciaio", "muratura", "legno"]


class MaterialCoefficientsSettingsWidget(QWidget):
    """Widget scheda "Materiali" per le Impostazioni Generali.

    Mostra un tab per ogni norma disponibile. In ogni tab, una sezione per famiglia
    con i coefficienti normativi come spin box. I valori mostrati includono gli
    override globali (Level 2) se presenti.

    Signals:
        coefficients_changed: Emesso quando l'utente salva un override.
            Argomenti: norm_key (str), famiglia (str), coeff_key (str), value (float).
    """

    coefficients_changed = Signal(str, str, str, float)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._loader: NormativeDefaultsLoader | None = (
            NormativeDefaultsLoader.instance() if NormativeDefaultsLoader else None
        )
        self._mgr: GlobalMaterialCoefficientsManager | None = (
            GlobalMaterialCoefficientsManager.instance() if GlobalMaterialCoefficientsManager else None
        )
        # {norm_key: {famiglia: {coeff_key: QLineEdit}}}
        self._value_inputs: dict[str, dict[str, dict[str, QLineEdit]]] = {}

        self._build_ui()

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(4, 4, 4, 4)

        header = QLabel(
            "Imposta i coefficienti normativi globali per ogni norma e famiglia di materiali. "
            "I valori inseriti qui sovrascrivono i default normativi (Level 2) per tutti i materiali. "
            "Per ripristinare i default, usare i pulsanti 'Ripristina default'."
        )
        header.setWordWrap(True)
        header.setStyleSheet("color: #555; font-size: 11px; margin-bottom: 4px;")
        outer.addWidget(header)

        if self._loader is None or self._mgr is None:
            outer.addWidget(QLabel("⚠ Modulo governance non disponibile."))
            return

        self._tabs = QTabWidget()
        outer.addWidget(self._tabs, stretch=1)

        for norm_key in self._loader.get_all_norms():
            tab_widget = self._build_norm_tab(norm_key)
            norm_label = self._loader.get_norm_label(norm_key)
            self._tabs.addTab(tab_widget, norm_key)
            self._tabs.setTabToolTip(self._tabs.count() - 1, norm_label)

        # Pulsanti globali
        btn_row = QHBoxLayout()
        btn_reset_all = QPushButton("Ripristina tutti i default")
        btn_reset_all.setToolTip("Rimuove tutti gli override globali per tutte le norme")
        btn_reset_all.clicked.connect(self._on_reset_all)
        btn_row.addWidget(btn_reset_all)
        btn_row.addStretch()
        outer.addLayout(btn_row)

    def _build_norm_tab(self, norm_key: str) -> QWidget:
        """Costruisce il tab per una norma con le sezioni per famiglia."""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        vbox = QVBoxLayout(container)
        vbox.setSpacing(8)

        norm_data = self._loader.load_norm_defaults(norm_key)  # type: ignore[union-attr]
        materiali = norm_data.get("materiali", {})

        self._spinboxes[norm_key] = {}

        # Ordina famiglie: prima quelle in _FAMIGLIE_ORDER, poi le altre alfabeticamente
        all_famiglie = list(materiali.keys())
        ordered = [f for f in _FAMIGLIE_ORDER if f in all_famiglie]
        ordered += sorted(f for f in all_famiglie if f not in _FAMIGLIE_ORDER)

        for famiglia in ordered:
            fam_data = materiali[famiglia]
            group = self._build_famiglia_group(norm_key, famiglia, fam_data)
            if group is not None:
                vbox.addWidget(group)

        vbox.addStretch()

        # Pulsante "Ripristina default norma"
        btn_reset_norm = QPushButton(f"Ripristina default {norm_key}")
        btn_reset_norm.clicked.connect(lambda checked=False, nk=norm_key: self._on_reset_norm(nk))
        vbox.addWidget(btn_reset_norm)

        scroll.setWidget(container)
        return scroll

    def _build_famiglia_group(self, norm_key: str, famiglia: str, fam_data: dict) -> QGroupBox | None:
        """Costruisce un QGroupBox con i coefficienti per una famiglia."""
        # Filtra solo i coefficienti con valore numerico
        coeffs = {}
        for k, v in fam_data.items():
            if isinstance(v, dict) and "valore" in v and isinstance(v["valore"], (int, float)):
                coeffs[k] = v
            elif isinstance(v, (int, float)) and not k.endswith(("_min", "_max")) and "formula" not in k:
                coeffs[k] = {"valore": v, "label": k}

        if not coeffs:
            return None

        group = QGroupBox(famiglia.capitalize())
        form = QFormLayout(group)
        form.setLabelAlignment(form.labelAlignment())

        self._value_inputs[norm_key][famiglia] = {}

        for coeff_key, coeff_info in coeffs.items():
            default_val = float(coeff_info.get("valore", 1.0))
            label_text = coeff_info.get("label", coeff_key)
            descrizione = coeff_info.get("descrizione", "")
            riferimento = coeff_info.get("riferimento", "")

            # Valore corrente (Level 2 override se presente, altrimenti Level 1 default)
            current_val, source = self._mgr.get_coefficient_with_source(  # type: ignore[union-attr]
                norm_key, famiglia, coeff_key
            )
            if current_val is None:
                current_val = default_val

            value_input = QLineEdit()
            value_input.setText(_format_value(float(current_val)))
            value_input.setPlaceholderText("0.0000")
            value_input.setValidator(QDoubleValidator(0.0001, 100.0, 4, value_input))
            value_input.setToolTip(
                f"{descrizione}\nDefault: {default_val}"
                + (f"\nRif: {riferimento}" if riferimento else "")
            )

            # Evidenzia se override attivo
            self._update_input_style(value_input, source == "override", default_val)

            # Aggiorna stile on-change
            value_input.textChanged.connect(
                lambda _txt, inp=value_input, dv=default_val: self._refresh_input_style(inp, dv)
            )

            # Label con default a fianco
            label_widget = QLabel(f"{label_text}  <span style='color:#888;font-size:9px'>(def: {default_val})</span>")
            label_widget.setTextFormat(label_widget.textFormat().RichText)

            form.addRow(label_widget, value_input)
            self._value_inputs[norm_key][famiglia][coeff_key] = value_input

        # Pulsante save + reset per questa famiglia
        btn_row_fam = QHBoxLayout()
        btn_save_fam = QPushButton("Salva")
        btn_reset_fam = QPushButton("Ripristina default")
        btn_save_fam.clicked.connect(
            lambda checked=False, nk=norm_key, fam=famiglia: self._on_save_famiglia(nk, fam)
        )
        btn_reset_fam.clicked.connect(
            lambda checked=False, nk=norm_key, fam=famiglia: self._on_reset_famiglia(nk, fam)
        )
        btn_row_fam.addWidget(btn_save_fam)
        btn_row_fam.addWidget(btn_reset_fam)
        btn_row_fam.addStretch()
        form.addRow(btn_row_fam)

        return group

    @staticmethod
    def _update_input_style(value_input: QLineEdit, is_override: bool, default_val: float) -> None:
        if is_override:
            value_input.setStyleSheet("QLineEdit { background-color: #fffbe6; border: 1px solid #f0c040; }")
            value_input.setToolTip(
                value_input.toolTip().split("\nOverride")[0] + f"\nOverride attivo (default: {default_val})"
            )
        else:
            value_input.setStyleSheet("")

    def _refresh_input_style(self, value_input: QLineEdit, default_val: float) -> None:
        current_val = _parse_float(value_input.text())
        is_override = current_val is not None and abs(current_val - float(default_val)) > 1e-9
        self._update_input_style(value_input, is_override, default_val)

    # ------------------------------------------------------------------
    # Handlers
    # ------------------------------------------------------------------

    def _on_save_famiglia(self, norm_key: str, famiglia: str) -> None:
        """Salva i valori modificati per una famiglia come override Level 2."""
        if self._mgr is None:
            return
        inputs = self._value_inputs.get(norm_key, {}).get(famiglia, {})
        invalid_fields: list[str] = []

        for coeff_key, value_input in inputs.items():
            default_val = self._mgr.get_default_coefficient(norm_key, famiglia, coeff_key)
            current_val = _parse_float(value_input.text())
            if current_val is None:
                invalid_fields.append(coeff_key)
                continue
            if default_val is not None and abs(current_val - float(default_val)) > 1e-9:
                self._mgr.set_coefficient_override(norm_key, famiglia, coeff_key, current_val)
                self.coefficients_changed.emit(norm_key, famiglia, coeff_key, current_val)
            else:
                # Valore uguale al default → rimuovi override se presente
                self._mgr.reset_coefficient_to_default(norm_key, famiglia, coeff_key)

        if invalid_fields:
            QMessageBox.warning(
                self,
                "Valori non validi",
                "I seguenti coefficienti non sono numerici e non sono stati salvati:\n"
                + ", ".join(invalid_fields),
            )
        logger.info("Override salvati: %s/%s", norm_key, famiglia)

    def _on_reset_famiglia(self, norm_key: str, famiglia: str) -> None:
        """Ripristina i default Level 1 per una famiglia e aggiorna i campi."""
        if self._mgr is None:
            return
        inputs = self._value_inputs.get(norm_key, {}).get(famiglia, {})
        for coeff_key, value_input in inputs.items():
            self._mgr.reset_coefficient_to_default(norm_key, famiglia, coeff_key, save=False)
            default_val = self._mgr.get_default_coefficient(norm_key, famiglia, coeff_key)
            if default_val is not None:
                value_input.blockSignals(True)
                value_input.setText(_format_value(float(default_val)))
                value_input.blockSignals(False)
                self._update_input_style(value_input, False, float(default_val))
        self._mgr._save_config()

    def _on_reset_norm(self, norm_key: str) -> None:
        """Ripristina tutti i default per una norma intera."""
        if self._mgr is None:
            return
        reply = QMessageBox.question(
            self,
            f"Ripristina default {norm_key}",
            f"Ripristinare tutti i coefficienti di default per la norma {norm_key}?\n"
            "Tutti gli override globali per questa norma saranno rimossi.",
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        self._mgr.reset_all_norm(norm_key)
        # Aggiorna UI
        for famiglia, inputs in self._value_inputs.get(norm_key, {}).items():
            for coeff_key, value_input in inputs.items():
                default_val = self._mgr.get_default_coefficient(norm_key, famiglia, coeff_key)
                if default_val is not None:
                    value_input.blockSignals(True)
                    value_input.setText(_format_value(float(default_val)))
                    value_input.blockSignals(False)
                    self._update_input_style(value_input, False, float(default_val))

    def _on_reset_all(self) -> None:
        """Ripristina tutti i default per tutte le norme."""
        if self._mgr is None:
            return
        reply = QMessageBox.question(
            self,
            "Ripristina tutti i default",
            "Ripristinare tutti i coefficienti di default per tutte le norme?\n"
            "Tutti gli override globali saranno rimossi.",
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        self._mgr.reset_all()
        # Aggiorna tutti i campi
        for norm_key, famiglie in self._value_inputs.items():
            for famiglia, inputs in famiglie.items():
                for coeff_key, value_input in inputs.items():
                    default_val = self._mgr.get_default_coefficient(norm_key, famiglia, coeff_key)
                    if default_val is not None:
                        value_input.blockSignals(True)
                        value_input.setText(_format_value(float(default_val)))
                        value_input.blockSignals(False)
                        self._update_input_style(value_input, False, float(default_val))


def _parse_float(text: str) -> float | None:
    """Converte input utente in float, accettando anche la virgola decimale."""
    normalized = text.strip().replace(",", ".")
    if not normalized:
        return None
    try:
        return float(normalized)
    except (TypeError, ValueError):
        return None


def _format_value(value: float) -> str:
    """Formatta un coefficiente con precisione stabile senza zeri inutili finali."""
    return f"{value:.4f}".rstrip("0").rstrip(".") if "." in f"{value:.4f}" else f"{value:.4f}"
