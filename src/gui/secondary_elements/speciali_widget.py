from __future__ import annotations

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

from .speciali import check_sle, check_slu


class SpecialiWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Famiglia Componente Speciale:"))
        self.famiglia_combo = QComboBox()
        self.famiglia_combo.addItems(
            [
                "insegna_bandiera",
                "cancello_scorrevole",
                "pannello_sospeso",
                "mensola_leggera",
                "chiusura_tecnica",
            ]
        )
        layout.addWidget(self.famiglia_combo)

        layout.addWidget(QLabel("Massa (kg):"))
        self.massa_spin = QDoubleSpinBox()
        self.massa_spin.setRange(0.0, 10000.0)
        self.massa_spin.setValue(75.0)
        layout.addWidget(self.massa_spin)

        layout.addWidget(QLabel("Grado Mobilità:"))
        self.mobilita_combo = QComboBox()
        self.mobilita_combo.addItems(["fisso", "mobile", "semi_mobile"])
        layout.addWidget(self.mobilita_combo)

        layout.addWidget(QLabel("Numero Supporti:"))
        self.supporti_spin = QSpinBox()
        self.supporti_spin.setMinimum(1)
        self.supporti_spin.setValue(1)
        layout.addWidget(self.supporti_spin)

        self.esposizione_check = QCheckBox("Esposizione Esterna")
        self.esposizione_check.setChecked(True)
        layout.addWidget(self.esposizione_check)

        hbox = QHBoxLayout()
        self.run_button = QPushButton("Verifica SLU")
        self.run_button_sle = QPushButton("Verifica SLE")
        hbox.addWidget(self.run_button)
        hbox.addWidget(self.run_button_sle)
        layout.addLayout(hbox)

        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        layout.addWidget(self.output_text)

        self.run_button.clicked.connect(self.run_slu)
        self.run_button_sle.clicked.connect(self.run_sle)

        self.setLayout(layout)

    def run_slu(self):
        inputs = {
            "famiglia": self.famiglia_combo.currentText(),
            "massa_kg": self.massa_spin.value(),
            "grado_mobilita": self.mobilita_combo.currentText(),
            "esposizione_esterna": self.esposizione_check.isChecked(),
            "supporti_numero": self.supporti_spin.value(),
            "S_a": 1.5,
        }
        result = check_slu(inputs)
        self.output_text.setText(
            f"SLU: {result['esito']}\nUtilizzazione: {result['utilisation']:.4f}"
        )

    def run_sle(self):
        inputs = {
            "famiglia": self.famiglia_combo.currentText(),
            "massa_kg": self.massa_spin.value(),
            "grado_mobilita": self.mobilita_combo.currentText(),
            "spostamento_relativo_cm": 0.8,
        }
        result = check_sle(inputs)
        self.output_text.setText(f"SLE: {result['esito']}\nStato danno: {result['stato_danno']}")
