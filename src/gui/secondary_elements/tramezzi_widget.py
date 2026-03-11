from __future__ import annotations

import sys

try:
    from PyQt5 import QtWidgets
    from PyQt5.QtWidgets import (
        QCheckBox,
        QComboBox,
        QDoubleSpinBox,
        QFormLayout,
        QLabel,
        QPushButton,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )
except ImportError:
    from PySide6 import QtWidgets
    from PySide6.QtWidgets import (
        QCheckBox,
        QComboBox,
        QDoubleSpinBox,
        QFormLayout,
        QLabel,
        QPushButton,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )

from src.codes.ntc2018.secondary_elements.tramezzi import (
    check_sle,
    check_slu,
    lista_preset_disponibili,
)


class TramezziWidget(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Fase S2 — Tramezzi secondari")
        layout = QVBoxLayout()
        form = QFormLayout()

        self.combo_preset = QComboBox()
        self.combo_preset.addItems(lista_preset_disponibili())
        form.addRow("Preset", self.combo_preset)

        self.combo_sistema = QComboBox()
        self.combo_sistema.addItems(
            [
                "cartongesso_standard",
                "cartongesso_doppia_lastra",
                "laterizio_forato",
                "sistema_misto",
            ]
        )
        form.addRow("Sistema", self.combo_sistema)

        self.altezza = QDoubleSpinBox()
        self.altezza.setRange(100, 600)
        self.altezza.setValue(300.0)
        form.addRow("Altezza (cm)", self.altezza)

        self.lunghezza = QDoubleSpinBox()
        self.lunghezza.setRange(100, 800)
        self.lunghezza.setValue(400.0)
        form.addRow("Lunghezza (cm)", self.lunghezza)

        self.spessore = QDoubleSpinBox()
        self.spessore.setRange(5, 30)
        self.spessore.setValue(10.0)
        form.addRow("Spessore (cm)", self.spessore)

        self.peso_lineare = QDoubleSpinBox()
        self.peso_lineare.setRange(10, 200)
        self.peso_lineare.setValue(55.0)
        form.addRow("Peso lineare (kg/m)", self.peso_lineare)

        self.accelerazione = QDoubleSpinBox()
        self.accelerazione.setRange(0.1, 5.0)
        self.accelerazione.setValue(1.5)
        form.addRow("S_a (g)", self.accelerazione)

        self.drift = QDoubleSpinBox()
        self.drift.setRange(0.0, 5.0)
        self.drift.setValue(0.6)
        form.addRow("Drift calcolato (%)", self.drift)

        self.guida = QCheckBox("Guida superiore scorrevole")
        self.guida.setChecked(True)
        form.addRow(self.guida)

        self.impianti = QCheckBox("Impianti integrati")
        form.addRow(self.impianti)

        layout.addWidget(QLabel("Widget dedicato S2 — backend NTC2018, output SLU/SLE e warning."))
        layout.addLayout(form)

        button = QPushButton("Esegui verifica")
        button.clicked.connect(self._run)
        layout.addWidget(button)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        layout.addWidget(self.output)
        self.setLayout(layout)

    def _inputs(self) -> dict:
        return {
            "element_type": "partition",
            "sistema": self.combo_sistema.currentText(),
            "altezza_cm": self.altezza.value(),
            "lunghezza_cm": self.lunghezza.value(),
            "spessore_cm": self.spessore.value(),
            "peso_lineare_kg_m": self.peso_lineare.value(),
            "S_a": self.accelerazione.value(),
            "guida_superiore_scorrimento": self.guida.isChecked(),
            "impianti_integrati": self.impianti.isChecked(),
            "ta_model": "MANUAL",
            "drift": {"source": "USER", "method": "INPUT", "value": self.drift.value()},
        }

    def _run(self) -> None:
        inputs = self._inputs()
        slu = check_slu(inputs)
        sle = check_sle(inputs)
        lines = [
            "SLU:",
            f"  esito={slu['esito']} util={slu['utilisation']}",
            f"  meccanismo={slu['meccanismo_critico']}",
            "SLE:",
            f"  esito={sle['esito']} util={sle['utilisation']}",
            f"  stato_danno={sle['stato_danno']}",
            "Decision log:",
            *[f"  - {item}" for item in (slu["decision_log"] + sle["decision_log"])],
        ]
        self.output.setPlainText("\n".join(lines))


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    widget = TramezziWidget()
    widget.show()
    sys.exit(app.exec())
