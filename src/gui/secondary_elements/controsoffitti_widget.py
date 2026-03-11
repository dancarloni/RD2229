from __future__ import annotations

try:
    from PyQt5.QtWidgets import (
        QCheckBox,
        QComboBox,
        QDoubleSpinBox,
        QHBoxLayout,
        QLabel,
        QPushButton,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )
except ImportError:
    from PySide6.QtWidgets import (
        QCheckBox,
        QComboBox,
        QDoubleSpinBox,
        QHBoxLayout,
        QLabel,
        QPushButton,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )

from . import check_sle, check_slu
from .models import TipoControsoffitto


class ControsoffitiWidget(QWidget):
    """Qt widget for controsoffitto verification."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Type
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Tipo:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems([t.value for t in TipoControsoffitto])
        type_layout.addWidget(self.type_combo)
        layout.addLayout(type_layout)

        # Area
        area_layout = QHBoxLayout()
        area_layout.addWidget(QLabel("Area (m²):"))
        self.area_spin = QDoubleSpinBox()
        self.area_spin.setRange(1.0, 500.0)
        self.area_spin.setValue(50.0)
        area_layout.addWidget(self.area_spin)
        layout.addLayout(area_layout)

        # Mass
        mass_layout = QHBoxLayout()
        mass_layout.addWidget(QLabel("Massa superficiale (kg/m²):"))
        self.mass_spin = QDoubleSpinBox()
        self.mass_spin.setRange(1.0, 50.0)
        self.mass_spin.setValue(15.0)
        mass_layout.addWidget(self.mass_spin)
        layout.addLayout(mass_layout)

        # Passo pendini
        passo_layout = QHBoxLayout()
        passo_layout.addWidget(QLabel("Passo pendini (cm):"))
        self.passo_spin = QDoubleSpinBox()
        self.passo_spin.setRange(50.0, 200.0)
        self.passo_spin.setValue(100.0)
        passo_layout.addWidget(self.passo_spin)
        layout.addLayout(passo_layout)

        # Controventi
        self.controventi_check = QCheckBox("Controventi presenti")
        self.controventi_check.setChecked(True)
        layout.addWidget(self.controventi_check)

        # Run
        self.run_button = QPushButton("Verifica")
        self.run_button.clicked.connect(self.run_verification)
        layout.addWidget(self.run_button)

        # Output
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        layout.addWidget(self.output_text)

        self.setLayout(layout)

    def run_verification(self):
        inputs = {
            "tipo": self.type_combo.currentText(),
            "area_m2": float(self.area_spin.value()),
            "massa_superficiale_kg_m2": float(self.mass_spin.value()),
            "passo_pendini_cm": float(self.passo_spin.value()),
            "presenza_controventi": self.controventi_check.isChecked(),
        }
        slu_result = check_slu(inputs)
        sle_result = check_sle(inputs)

        output = f"SLU: {slu_result['esito']}\n"
        output += f"SLE: {sle_result['esito']}\n"
        output += f"Rischio perdita appoggio: {sle_result.get('perdita_appoggio_rischio', False)}\n"
        self.output_text.setText(output)
