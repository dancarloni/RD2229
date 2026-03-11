from __future__ import annotations

try:
    from PyQt5.QtCore import Qt
    from PyQt5.QtWidgets import (
        QCheckBox,
        QComboBox,
        QDoubleSpinBox,
        QHBoxLayout,
        QLabel,
        QPushButton,
        QSpinBox,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )
except ImportError:
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import (
        QCheckBox,
        QComboBox,
        QDoubleSpinBox,
        QHBoxLayout,
        QLabel,
        QPushButton,
        QSpinBox,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )

from . import check_sle, check_slu, lista_preset_disponibili
from .models import TipoAncoraggio, TipoParapetto


class ParapettiWidget(QWidget):
    """Qt widget for parapetto verification."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        """Initialize UI."""
        layout = QVBoxLayout()

        # Preset selection
        preset_layout = QHBoxLayout()
        preset_layout.addWidget(QLabel("Preset:"))
        self.preset_combo = QComboBox()
        self.preset_combo.addItems(lista_preset_disponibili() or ["custom"])
        preset_layout.addWidget(self.preset_combo)
        layout.addLayout(preset_layout)

        # Type selection
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Tipo:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems([t.value for t in TipoParapetto])
        type_layout.addWidget(self.type_combo)
        layout.addLayout(type_layout)

        # Height input
        height_layout = QHBoxLayout()
        height_layout.addWidget(QLabel("Altezza (cm):"))
        self.height_spin = QSpinBox()
        self.height_spin.setRange(50, 300)
        self.height_spin.setValue(120)
        height_layout.addWidget(self.height_spin)
        layout.addLayout(height_layout)

        # Length input
        length_layout = QHBoxLayout()
        length_layout.addWidget(QLabel("Lunghezza (cm):"))
        self.length_spin = QSpinBox()
        self.length_spin.setRange(100, 2000)
        self.length_spin.setValue(500)
        length_layout.addWidget(self.length_spin)
        layout.addLayout(length_layout)

        # Linear mass input
        mass_layout = QHBoxLayout()
        mass_layout.addWidget(QLabel("Massa lineare (kg/m):"))
        self.mass_spin = QDoubleSpinBox()
        self.mass_spin.setRange(50.0, 500.0)
        self.mass_spin.setValue(200.0)
        mass_layout.addWidget(self.mass_spin)
        layout.addLayout(mass_layout)

        # Anchorage type
        anc_layout = QHBoxLayout()
        anc_layout.addWidget(QLabel("Tipo ancoraggio:"))
        self.anc_combo = QComboBox()
        self.anc_combo.addItems([t.value for t in TipoAncoraggio])
        anc_layout.addWidget(self.anc_combo)
        layout.addLayout(anc_layout)

        # Spectral acceleration
        sa_layout = QHBoxLayout()
        sa_layout.addWidget(QLabel("S_a (g):"))
        self.sa_spin = QDoubleSpinBox()
        self.sa_spin.setRange(0.1, 5.0)
        self.sa_spin.setValue(1.5)
        sa_layout.addWidget(self.sa_spin)
        layout.addLayout(sa_layout)

        # Service load
        pserv_layout = QHBoxLayout()
        pserv_layout.addWidget(QLabel("P_servizio (kg):"))
        self.pserv_spin = QDoubleSpinBox()
        self.pserv_spin.setRange(0.0, 500.0)
        self.pserv_spin.setValue(100.0)
        pserv_layout.addWidget(self.pserv_spin)
        layout.addLayout(pserv_layout)

        # Displacement
        disp_layout = QHBoxLayout()
        disp_layout.addWidget(QLabel("Spostamento (cm):"))
        self.disp_spin = QDoubleSpinBox()
        self.disp_spin.setRange(0.0, 5.0)
        self.disp_spin.setValue(0.5)
        disp_layout.addWidget(self.disp_spin)
        layout.addLayout(disp_layout)

        # Fragile behavior checkbox
        self.fragile_check = QCheckBox("Comportamento fragile")
        layout.addWidget(self.fragile_check)

        # Run button
        self.run_button = QPushButton("Verifica")
        self.run_button.clicked.connect(self.run_verification)
        layout.addWidget(self.run_button)

        # Output display
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        layout.addWidget(self.output_text)

        self.setLayout(layout)

    def run_verification(self):
        """Run verification and display results."""
        inputs = {
            "tipo": self.type_combo.currentText(),
            "altezza_cm": float(self.height_spin.value()),
            "lunghezza_cm": float(self.length_spin.value()),
            "massa_lineare_kg_m": float(self.mass_spin.value()),
            "tipo_ancoraggio": self.anc_combo.currentText(),
            "S_a": float(self.sa_spin.value()),
            "P_servizio": float(self.pserv_spin.value()),
            "spostamento_bordo_cm": float(self.disp_spin.value()),
            "comportamento_fragile": self.fragile_check.isChecked(),
        }

        slu_result = check_slu(inputs)
        sle_result = check_sle(inputs)

        output = "=== Risultati SLU ===\n"
        output += f"Esito: {slu_result['esito']}\n"
        output += f"Utilisation: {slu_result['utilisation']:.3f}\n\n"
        output += "=== Risultati SLE ===\n"
        output += f"Esito: {sle_result['esito']}\n"
        output += f"Stato danno: {sle_result['stato_danno']}\n\n"
        output += "=== Decision Log ===\n"
        output += "\n".join(slu_result["decision_log"] + sle_result["decision_log"])

        self.output_text.setText(output)
