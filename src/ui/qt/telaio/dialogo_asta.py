"""Dialog per inserimento e modifica asta del telaio."""

from __future__ import annotations

try:
    from PyQt6.QtWidgets import QSpinBox  # noqa: F401
    from PyQt6.QtWidgets import (
        QComboBox,
        QDialog,
        QDialogButtonBox,
        QDoubleSpinBox,
        QFormLayout,
        QGroupBox,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QListWidget,
        QPushButton,
        QTabWidget,
        QVBoxLayout,
        QWidget,
    )
except ImportError:
    from PySide6.QtWidgets import (
        QComboBox,
        QDialog,
        QDialogButtonBox,
        QDoubleSpinBox,
        QFormLayout,
        QGroupBox,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QListWidget,
        QPushButton,
        QTabWidget,
        QVBoxLayout,
        QWidget,
    )

from src.methods.rd2229.telaio.modello_telaio import (
    AstaTelaio,
    CaricoAsta,
    RilascioEstremita,
    SezioneTelaio,
    TipoAsta,
    TipoCarico,
    TipoRilascioInterno,
)

_DESCRIZIONI_RILASCIO = {
    TipoRilascioInterno.NODO_RIGIDO: "Nodo rigido   (k=4EI/L, c=0.50)",
    TipoRilascioInterno.CERNIERA: "Cerniera      (k=3EI/L, c=0.00)",
    TipoRilascioInterno.MANICOTTO: "Manicotto     (N=0, k=4EI/L, c=0.50)",
    TipoRilascioInterno.PATTINO: "Pattino       (k=EI/L, c=−1.00)",
    TipoRilascioInterno.BIPENDOLO: "Bipendolo     (k=3EI/L, c=0.00)",
}


class DialogoAsta(QDialog):
    """Dialog per inserimento o modifica di un'asta del telaio."""

    def __init__(
        self,
        asta: AstaTelaio | None = None,
        nodi_disponibili: list[tuple[int, str]] | None = None,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self.setWindowTitle("Asta — Proprietà")
        self.setMinimumWidth(480)
        self.setMinimumHeight(520)
        self._asta = asta
        self._nodi = nodi_disponibili or []
        self._init_ui()
        if asta:
            self._popola(asta)

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)

        tabs = QTabWidget()

        # --- Tab Generale ---
        tab_gen = QWidget()
        form_gen = QFormLayout(tab_gen)

        self._combo_nodo_i = QComboBox()
        self._combo_nodo_j = QComboBox()
        for id_n, etich in self._nodi:
            label = f"{id_n} — {etich}" if etich else str(id_n)
            self._combo_nodo_i.addItem(label, id_n)
            self._combo_nodo_j.addItem(label, id_n)
        form_gen.addRow("Nodo i:", self._combo_nodo_i)
        form_gen.addRow("Nodo j:", self._combo_nodo_j)

        self._combo_tipo = QComboBox()
        for t in TipoAsta:
            self._combo_tipo.addItem(t.value, t)
        form_gen.addRow("Tipo asta:", self._combo_tipo)

        self._edit_etichetta = QLineEdit()
        self._edit_etichetta.setPlaceholderText("es. AB, T1, P2")
        form_gen.addRow("Etichetta:", self._edit_etichetta)

        tabs.addTab(tab_gen, "Generale")

        # --- Tab Sezione ---
        tab_sez = QWidget()
        form_sez = QFormLayout(tab_sez)

        self._spin_b = QDoubleSpinBox()
        self._spin_b.setRange(5, 1000)
        self._spin_b.setDecimals(1)
        self._spin_b.setSuffix(" cm")
        self._spin_b.setValue(30.0)
        form_sez.addRow("Larghezza b:", self._spin_b)

        self._spin_h = QDoubleSpinBox()
        self._spin_h.setRange(5, 2000)
        self._spin_h.setDecimals(1)
        self._spin_h.setSuffix(" cm")
        self._spin_h.setValue(50.0)
        form_sez.addRow("Altezza h:", self._spin_h)

        self._spin_E = QDoubleSpinBox()
        self._spin_E.setRange(1000, 10000000)
        self._spin_E.setDecimals(0)
        self._spin_E.setSuffix(" kg/cm²")
        self._spin_E.setValue(300000.0)
        self._spin_E.setSingleStep(10000)
        form_sez.addRow("Modulo E:", self._spin_E)

        self._spin_gamma = QDoubleSpinBox()
        self._spin_gamma.setRange(0, 0.01)
        self._spin_gamma.setDecimals(5)
        self._spin_gamma.setSuffix(" kg/cm³")
        self._spin_gamma.setValue(0.0025)
        self._spin_gamma.setSingleStep(0.0001)
        form_sez.addRow("Peso spec. γ:", self._spin_gamma)

        self._spin_sigma_c = QDoubleSpinBox()
        self._spin_sigma_c.setRange(10, 500)
        self._spin_sigma_c.setDecimals(1)
        self._spin_sigma_c.setSuffix(" kg/cm²")
        self._spin_sigma_c.setValue(80.0)
        form_sez.addRow("σ_c,adm:", self._spin_sigma_c)

        self._spin_sigma_s = QDoubleSpinBox()
        self._spin_sigma_s.setRange(100, 5000)
        self._spin_sigma_s.setDecimals(0)
        self._spin_sigma_s.setSuffix(" kg/cm²")
        self._spin_sigma_s.setValue(1400.0)
        form_sez.addRow("σ_s,adm:", self._spin_sigma_s)

        tabs.addTab(tab_sez, "Sezione")

        # --- Tab Rilasci ---
        tab_rilasci = QWidget()
        form_rilasci = QFormLayout(tab_rilasci)

        self._combo_rilascio_i = QComboBox()
        self._combo_rilascio_j = QComboBox()
        for tipo, descr in _DESCRIZIONI_RILASCIO.items():
            self._combo_rilascio_i.addItem(descr, tipo)
            self._combo_rilascio_j.addItem(descr, tipo)
        self._combo_rilascio_i.currentIndexChanged.connect(self._aggiorna_info_rilasci)
        self._combo_rilascio_j.currentIndexChanged.connect(self._aggiorna_info_rilasci)

        form_rilasci.addRow("Rilascio nodo i:", self._combo_rilascio_i)
        form_rilasci.addRow("Rilascio nodo j:", self._combo_rilascio_j)

        self._lbl_info_rilasci = QLabel()
        self._lbl_info_rilasci.setStyleSheet("color: #555; font-style: italic; font-size: 10px;")
        self._lbl_info_rilasci.setWordWrap(True)
        form_rilasci.addRow("Info:", self._lbl_info_rilasci)

        tabs.addTab(tab_rilasci, "Rilasci")

        # --- Tab Carichi ---
        tab_carichi = QWidget()
        lay_car = QVBoxLayout(tab_carichi)

        self._lista_carichi = QListWidget()
        lay_car.addWidget(QLabel("Carichi sull'asta:"))
        lay_car.addWidget(self._lista_carichi)

        # Form aggiungi carico
        grp_add = QGroupBox("Aggiungi carico")
        form_add = QFormLayout(grp_add)

        self._combo_tipo_carico = QComboBox()
        for tc in TipoCarico:
            self._combo_tipo_carico.addItem(tc.value, tc)
        form_add.addRow("Tipo:", self._combo_tipo_carico)

        self._spin_valore_sx = QDoubleSpinBox()
        self._spin_valore_sx.setRange(-100000, 100000)
        self._spin_valore_sx.setDecimals(2)
        self._spin_valore_sx.setSuffix(" kg/cm o kg")
        form_add.addRow("Valore sx/P:", self._spin_valore_sx)

        self._spin_valore_dx = QDoubleSpinBox()
        self._spin_valore_dx.setRange(-100000, 100000)
        self._spin_valore_dx.setDecimals(2)
        self._spin_valore_dx.setSuffix(" kg/cm (trapez.)")
        form_add.addRow("Valore dx:", self._spin_valore_dx)

        self._spin_pos_a = QDoubleSpinBox()
        self._spin_pos_a.setRange(0, 10000)
        self._spin_pos_a.setDecimals(1)
        self._spin_pos_a.setSuffix(" cm (da nodo i)")
        form_add.addRow("Posizione a:", self._spin_pos_a)

        self._combo_dir = QComboBox()
        self._combo_dir.addItems(["Y (verticale)", "X (orizzontale)"])
        form_add.addRow("Direzione:", self._combo_dir)

        btn_aggiungi = QPushButton("+ Aggiungi")
        btn_aggiungi.clicked.connect(self._aggiungi_carico)
        btn_rimuovi = QPushButton("− Rimuovi sel.")
        btn_rimuovi.clicked.connect(self._rimuovi_carico)

        btn_row = QHBoxLayout()
        btn_row.addWidget(btn_aggiungi)
        btn_row.addWidget(btn_rimuovi)
        btn_row.addStretch()

        lay_car.addWidget(grp_add)
        lay_car.addLayout(btn_row)

        tabs.addTab(tab_carichi, "Carichi")

        layout.addWidget(tabs)

        self._carichi_interni: list[CaricoAsta] = []

        # Bottoni
        bottoni = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        bottoni.accepted.connect(self.accept)
        bottoni.rejected.connect(self.reject)
        layout.addWidget(bottoni)

        self._aggiorna_info_rilasci()

    def _aggiorna_info_rilasci(self) -> None:
        ti = self._combo_rilascio_i.currentData()
        tj = self._combo_rilascio_j.currentData()
        if ti is None or tj is None:
            return
        ri = RilascioEstremita(tipo=ti)
        rj = RilascioEstremita(tipo=tj)
        info = (
            f"Dal nodo i: k = {ri.k_factor:.0f}·EI/L, c_ij = {rj.carry_over:+.2f}\n"
            f"Dal nodo j: k = {rj.k_factor:.0f}·EI/L, c_ji = {ri.carry_over:+.2f}"
        )
        self._lbl_info_rilasci.setText(info)

    def _aggiungi_carico(self) -> None:
        tc = self._combo_tipo_carico.currentData()
        direzione = "X" if "X" in self._combo_dir.currentText() else "Y"
        carico = CaricoAsta(
            tipo=tc,
            valore_sx=self._spin_valore_sx.value(),
            valore_dx=self._spin_valore_dx.value(),
            posizione_a=self._spin_pos_a.value(),
            direzione=direzione,
        )
        self._carichi_interni.append(carico)
        self._lista_carichi.addItem(
            f"{tc.value}: {carico.valore_sx:.1f} | a={carico.posizione_a:.0f}cm | {direzione}"
        )

    def _rimuovi_carico(self) -> None:
        row = self._lista_carichi.currentRow()
        if 0 <= row < len(self._carichi_interni):
            self._carichi_interni.pop(row)
            self._lista_carichi.takeItem(row)

    def _popola(self, asta: AstaTelaio) -> None:
        # Nodi
        for i in range(self._combo_nodo_i.count()):
            if self._combo_nodo_i.itemData(i) == asta.nodo_i:
                self._combo_nodo_i.setCurrentIndex(i)
            if self._combo_nodo_j.itemData(i) == asta.nodo_j:
                self._combo_nodo_j.setCurrentIndex(i)

        # Tipo
        for i in range(self._combo_tipo.count()):
            if self._combo_tipo.itemData(i) == asta.tipo:
                self._combo_tipo.setCurrentIndex(i)
                break

        self._edit_etichetta.setText(asta.etichetta)

        # Sezione
        sez = asta.sezione
        self._spin_b.setValue(sez.b)
        self._spin_h.setValue(sez.h)
        self._spin_E.setValue(sez.E)
        self._spin_gamma.setValue(sez.gamma)
        self._spin_sigma_c.setValue(getattr(sez, "sigma_c_adm", 80.0))
        self._spin_sigma_s.setValue(getattr(sez, "sigma_s_adm", 1400.0))

        # Rilasci
        for i in range(self._combo_rilascio_i.count()):
            if self._combo_rilascio_i.itemData(i) == asta.rilascio_i.tipo:
                self._combo_rilascio_i.setCurrentIndex(i)
            if self._combo_rilascio_j.itemData(i) == asta.rilascio_j.tipo:
                self._combo_rilascio_j.setCurrentIndex(i)

        # Carichi
        self._carichi_interni = list(asta.carichi)
        for c in asta.carichi:
            self._lista_carichi.addItem(
                f"{c.tipo.value}: {c.valore_sx:.1f} | a={c.posizione_a:.0f}cm | {c.direzione}"
            )

        self._aggiorna_info_rilasci()

    def get_dati(self) -> dict:
        """Ritorna i dati inseriti come dizionario."""
        b = self._spin_b.value()
        h = self._spin_h.value()
        E = self._spin_E.value()
        gamma = self._spin_gamma.value()
        I = b * h**3 / 12.0
        A = b * h
        Wx = b * h**2 / 6.0
        sez = SezioneTelaio(tipo="RECTANGULAR", b=b, h=h, I=I, A=A, Wx=Wx, E=E, gamma=gamma)
        # Aggiunge tensioni ammissibili come attributi extra
        sez.extra["sigma_c_adm"] = self._spin_sigma_c.value()
        sez.extra["sigma_s_adm"] = self._spin_sigma_s.value()

        return {
            "nodo_i": self._combo_nodo_i.currentData(),
            "nodo_j": self._combo_nodo_j.currentData(),
            "tipo": self._combo_tipo.currentData(),
            "etichetta": self._edit_etichetta.text().strip(),
            "sezione": sez,
            "rilascio_i": RilascioEstremita(tipo=self._combo_rilascio_i.currentData()),
            "rilascio_j": RilascioEstremita(tipo=self._combo_rilascio_j.currentData()),
            "carichi": list(self._carichi_interni),
        }
