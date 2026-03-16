"""Code settings editor for multi-norm workflows (Qt6)."""

from __future__ import annotations

from typing import Any

try:
    from PyQt6.QtCore import pyqtSignal as Signal
    from PyQt6.QtWidgets import (
        QCheckBox,
        QComboBox,
        QDoubleSpinBox,
        QFormLayout,
        QGroupBox,
        QLabel,
        QPushButton,
        QSizePolicy,
        QVBoxLayout,
        QWidget,
    )
except ImportError:  # pragma: no cover
    from PySide6.QtCore import Signal
    from PySide6.QtWidgets import (
        QCheckBox,
        QComboBox,
        QDoubleSpinBox,
        QFormLayout,
        QGroupBox,
        QLabel,
        QPushButton,
        QSizePolicy,
        QVBoxLayout,
        QWidget,
    )


class CodeSettingsWindow(QWidget):
    settings_changed = Signal(dict)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle("RD2229 - Impostazioni normativa")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.addWidget(QLabel("<b>Impostazioni normative e coefficienti</b>"))

        from src.core_calculus.normative_registry import list_norm_codes

        group = QGroupBox("Norma e stati limite")
        form = QFormLayout(group)

        self.cmb_norm = QComboBox()
        self.cmb_norm.addItems(list_norm_codes())
        form.addRow("Norma:", self.cmb_norm)

        self.cmb_limit_state = QComboBox()
        self.cmb_limit_state.addItems(["TA", "SLU", "SLE"])
        form.addRow("Stato limite:", self.cmb_limit_state)

        self.chk_existing = QCheckBox("Struttura esistente")
        form.addRow("Tipologia:", self.chk_existing)

        self.cmb_lc = QComboBox()
        self.cmb_lc.addItems(["", "LC1", "LC2", "LC3"])
        form.addRow("Livello conoscenza:", self.cmb_lc)

        gamma_group = QGroupBox("Coefficienti gamma (override opzionale)")
        gamma_form = QFormLayout(gamma_group)
        self.spn_gamma_c = QDoubleSpinBox()
        self.spn_gamma_c.setRange(0.5, 3.0)
        self.spn_gamma_c.setValue(1.5)
        self.spn_gamma_c.setSingleStep(0.05)
        gamma_form.addRow("gamma_c:", self.spn_gamma_c)

        self.spn_gamma_s = QDoubleSpinBox()
        self.spn_gamma_s.setRange(0.5, 3.0)
        self.spn_gamma_s.setValue(1.15)
        self.spn_gamma_s.setSingleStep(0.05)
        gamma_form.addRow("gamma_s:", self.spn_gamma_s)

        btn_apply = QPushButton("Applica")
        btn_apply.clicked.connect(self._emit_settings)

        root.addWidget(group)
        root.addWidget(gamma_group)
        root.addWidget(btn_apply)
        root.addStretch(1)

    def _emit_settings(self) -> None:
        payload = {
            "norm_code": self.cmb_norm.currentText(),
            "limit_state": self.cmb_limit_state.currentText(),
            "existing_structure": self.chk_existing.isChecked(),
            "lc": self.cmb_lc.currentText() or None,
            "gamma_c": float(self.spn_gamma_c.value()),
            "gamma_s": float(self.spn_gamma_s.value()),
        }
        self.settings_changed.emit(payload)

    def get_settings(self) -> dict[str, Any]:
        return {
            "norm_code": self.cmb_norm.currentText(),
            "limit_state": self.cmb_limit_state.currentText(),
            "existing_structure": self.chk_existing.isChecked(),
            "lc": self.cmb_lc.currentText() or None,
            "gamma_c": float(self.spn_gamma_c.value()),
            "gamma_s": float(self.spn_gamma_s.value()),
        }


MODULE_SPEC = {
    "key": "code_settings",
    "name": "Code Settings Dialog",
    "description": "Dialog di configurazione codici (Qt6)",
}


def create_module(master=None, **context):
    # Return the window class implemented above. Some factories pass project_service.
    return CodeSettingsWindow(parent=master)
