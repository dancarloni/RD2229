"""Widget Qt per verifiche di scale - Fase V."""

from __future__ import annotations

try:
    from PyQt6.QtWidgets import (
        QCheckBox,
        QComboBox,
        QDoubleSpinBox,
        QFormLayout,
        QGroupBox,
        QHBoxLayout,
        QLabel,
        QPushButton,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )
except ImportError:  # pragma: no cover
    from PySide6.QtWidgets import (
        QCheckBox,
        QComboBox,
        QDoubleSpinBox,
        QFormLayout,
        QGroupBox,
        QHBoxLayout,
        QLabel,
        QPushButton,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )

from src.scale.scale import (
    GeometriaRampa,
    profilo_ipe200_s275,
    verifica_scala_ca,
    verifica_scala_metallica,
)


class ScalaWidget(QWidget):
    """Interfaccia minima per input e verifica scale."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._ultimo_risultato = None
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)

        box = QGroupBox("Input scala")
        form = QFormLayout(box)

        self.combo_tipo = QComboBox()
        self.combo_tipo.addItems(["CA", "Acciaio"])
        form.addRow("Tipologia", self.combo_tipo)

        self.combo_categoria = QComboBox()
        self.combo_categoria.addItems(
            [
                "residenziale",
                "uffici",
                "pubblico",
                "affollamento_elevato",
            ]
        )
        form.addRow("Categoria d'uso", self.combo_categoria)

        self.spin_alpha = self._spin(15.0, 45.0, 30.0, 1)
        self.spin_luce = self._spin(1.0, 8.0, 3.0, 2)
        self.spin_spessore = self._spin(0.10, 0.30, 0.15, 3)
        self.spin_larghezza = self._spin(0.60, 3.00, 1.20, 2)
        self.spin_q = self._spin(0.0, 20.0, 0.0, 2)
        self.spin_neve = self._spin(0.0, 10.0, 0.0, 2)
        self.spin_qp = self._spin(0.0, 5.0, 0.0, 2)
        self.spin_area = self._spin(0.0, 100.0, 0.0, 2)

        form.addRow("Angolo α [deg]", self.spin_alpha)
        form.addRow("Luce orizzontale [m]", self.spin_luce)
        form.addRow("Spessore [m]", self.spin_spessore)
        form.addRow("Larghezza [m]", self.spin_larghezza)
        form.addRow("Carico variabile override [kN/m²]", self.spin_q)
        form.addRow("Neve s_k [kN/m²]", self.spin_neve)
        form.addRow("Vento q_p [kN/m²]", self.spin_qp)
        form.addRow("Area influenza manuale [m²]", self.spin_area)

        self.check_esterna = QCheckBox("Scala esterna")
        form.addRow("", self.check_esterna)

        # ==== Sezione: Casi avanzati (schema incastrato, pianerottolo, segmenti) ====
        advanced_box = QGroupBox("Opzioni avanzate")
        adv_form = QFormLayout(advanced_box)

        self.combo_schema = QComboBox()
        self.combo_schema.addItems(["appoggiata", "incastrata"])
        adv_form.addRow("Schema statico", self.combo_schema)

        self.combo_vinc_sx = QComboBox()
        self.combo_vinc_sx.addItems(["libero", "cerniera", "incastro"])
        adv_form.addRow("Vincolo sinistro", self.combo_vinc_sx)

        self.combo_vinc_dx = QComboBox()
        self.combo_vinc_dx.addItems(["libero", "cerniera", "incastro"])
        adv_form.addRow("Vincolo destro", self.combo_vinc_dx)

        self.check_pianerottolo = QCheckBox("Pianerottolo intermedio")
        adv_form.addRow("", self.check_pianerottolo)

        self.combo_piano_tipo = QComboBox()
        self.combo_piano_tipo.addItems(["autonomo", "continuita", "ibrido"])
        adv_form.addRow("Modelo pianerottolo", self.combo_piano_tipo)

        self.spin_piano_largh = self._spin(0.0, 5.0, 0.0, 2)
        adv_form.addRow("Larghezza pianerottolo [m]", self.spin_piano_largh)

        self.spin_piano_alt = self._spin(0.0, 1.0, 0.0, 2)
        adv_form.addRow("Altezza pianerottolo [m]", self.spin_piano_alt)

        root.addWidget(box)
        root.addWidget(advanced_box)

        row = QHBoxLayout()
        self.btn_calcola = QPushButton("Calcola")
        self.btn_calcola.clicked.connect(self._on_calcola)
        row.addWidget(self.btn_calcola)
        row.addWidget(QLabel("Output tabulato ASCII"))
        root.addLayout(row)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        root.addWidget(self.output, 1)

    def _spin(self, minimum: float, maximum: float, value: float, decimals: int) -> QDoubleSpinBox:
        spin = QDoubleSpinBox()
        spin.setRange(minimum, maximum)
        spin.setDecimals(decimals)
        spin.setValue(value)
        return spin

    def _costruisci_geometria(self) -> GeometriaRampa:
        area = self.spin_area.value()
        carico_variabile = self.spin_q.value()
        return GeometriaRampa(
            tipologia=self.combo_tipo.currentText().lower(),
            alpha_deg=self.spin_alpha.value(),
            luce_orizzontale_m=self.spin_luce.value(),
            spessore_m=self.spin_spessore.value(),
            larghezza_m=self.spin_larghezza.value(),
            scala_esterna=self.check_esterna.isChecked(),
            categoria_uso=self.combo_categoria.currentText(),
            area_influenza_m2=area if area > 0.0 else None,
            carico_variabile_kN_m2=carico_variabile if carico_variabile > 0.0 else None,
            neve_sk_kN_m2=self.spin_neve.value(),
            vento_qp_kN_m2=self.spin_qp.value(),
            area_parapetto_m2=max(self.spin_luce.value(), 0.0),
            # Campi avanzati
            schema_statico=self.combo_schema.currentText(),
            vincolo_sinistra=self.combo_vinc_sx.currentText(),
            vincolo_destra=self.combo_vinc_dx.currentText(),
            pianerottolo_presente=self.check_pianerottolo.isChecked(),
            pianerottolo_tipo=self.combo_piano_tipo.currentText(),
            pianerottolo_larghezza_m=self.spin_piano_largh.value(),
            pianerottolo_altezza_m=self.spin_piano_alt.value(),
        )

    def _on_calcola(self) -> None:
        risultato = self._calcola_corrente()
        self.output.setPlainText(risultato.tabulato_ascii)

    def _calcola_corrente(self):
        geometria = self._costruisci_geometria()
        if self.combo_tipo.currentText() == "CA":
            risultato = verifica_scala_ca(geometria)
        else:
            risultato = verifica_scala_metallica(geometria, profilo=profilo_ipe200_s275())
        self._ultimo_risultato = risultato
        return risultato


MODULE_SPEC = {
    "key": "scala_widget",
    "name": "Scale",
    "description": "Verifica rampe in c.a. e metalliche.",
}


def create_module(master=None, **context):
    return ScalaWidget(parent=master)
