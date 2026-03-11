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
from .models import CategoriaImpianto


class ImiantiWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        cat_layout = QHBoxLayout()
        cat_layout.addWidget(QLabel("Categoria:"))
        self.cat_combo = QComboBox()
        self.cat_combo.addItems([c.value for c in CategoriaImpianto])
        cat_layout.addWidget(self.cat_combo)
        layout.addLayout(cat_layout)

        mass_layout = QHBoxLayout()
        mass_layout.addWidget(QLabel("Massa (kg):"))
        self.mass_spin = QDoubleSpinBox()
        self.mass_spin.setRange(1.0, 500.0)
        self.mass_spin.setValue(50.0)
        mass_layout.addWidget(self.mass_spin)
        layout.addLayout(mass_layout)

        anc_layout = QHBoxLayout()
        anc_layout.addWidget(QLabel("Ancoraggi:"))
        self.anc_spinbox = QDoubleSpinBox()
        self.anc_spinbox.setRange(1, 10)
        self.anc_spinbox.setValue(2)
        anc_layout.addWidget(self.anc_spinbox)
        layout.addLayout(anc_layout)

        self.giunto_check = QCheckBox("Giunto flessibile")
        self.giunto_check.setChecked(True)
        layout.addWidget(self.giunto_check)

        self.run_button = QPushButton("Verifica")
        self.run_button.clicked.connect(self.run_verification)
        layout.addWidget(self.run_button)

        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        layout.addWidget(self.output_text)

        self.setLayout(layout)

    def run_verification(self):
        inputs = {
            "categoria": self.cat_combo.currentText(),
            "massa_kg": float(self.mass_spin.value()),
            "numero_ancoraggi": int(self.anc_spinbox.value()),
            "presenza_giunto_flessibile": self.giunto_check.isChecked(),
        }
        slu = check_slu(inputs)
        sle = check_sle(inputs)
        output = f"SLU: {slu['esito']}\nSLE: {sle['esito']}\n\nContinuità funzionale: {slu.get('continuita_funzionale', False)}"
        self.output_text.setText(output)
