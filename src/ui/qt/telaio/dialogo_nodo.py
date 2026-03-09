"""Dialog per inserimento e modifica nodo del telaio."""

from __future__ import annotations

try:
    from PyQt6.QtCore import Qt
    from PyQt6.QtWidgets import (
        QComboBox,
        QDialog,
        QDialogButtonBox,
        QDoubleSpinBox,
        QFormLayout,
        QGroupBox,
        QLabel,
        QLineEdit,
        QSpinBox,
        QVBoxLayout,
        QWidget,
    )
except ImportError:
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import (
        QComboBox,
        QDialog,
        QDialogButtonBox,
        QDoubleSpinBox,
        QFormLayout,
        QGroupBox,
        QLabel,
        QLineEdit,
        QSpinBox,
        QVBoxLayout,
        QWidget,
    )

from src.methods.rd2229.telaio.modello_telaio import (
    NodoTelaio,
    TipoVincoloEsterno,
    VincoloEsterno,
)

# Descrizioni UI per i tipi di vincolo
_DESCRIZIONI_VINCOLO = {
    TipoVincoloEsterno.INCASTRO:    "[▪] Incastro         (ux=0, uy=0, θ=0)",
    TipoVincoloEsterno.CERNIERA:    "[○] Cerniera         (ux=0, uy=0, θ libero)",
    TipoVincoloEsterno.CARRELLO_X:  "[⊥] Carrello orizz.  (uy=0, scorre X)",
    TipoVincoloEsterno.CARRELLO_Y:  "[∥] Carrello vert.   (ux=0, scorre Y)",
    TipoVincoloEsterno.PATTINO_X:   "[⊟] Pattino orizz.   (uy=0, θ=0, scorre X)",
    TipoVincoloEsterno.PATTINO_Y:   "[⊞] Pattino vert.    (ux=0, θ=0, scorre Y)",
    TipoVincoloEsterno.PENDOLO:     "[/] Pendolo          (1 reaz. assiale)",
    TipoVincoloEsterno.BIPENDOLO:   "[//] Bipendolo       (ux=0, uy=0, θ libero)",
    TipoVincoloEsterno.LIBERO:      "[◯] Libero           (nodo interno)",
}


class DialogoNodo(QDialog):
    """Dialog per inserimento o modifica di un nodo del telaio."""

    def __init__(self, nodo: NodoTelaio | None = None, parent: QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle("Nodo — Proprietà")
        self.setMinimumWidth(420)
        self._nodo = nodo
        self._init_ui()
        if nodo:
            self._popola(nodo)

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)

        # Coordinate e identificazione
        grp_geo = QGroupBox("Geometria")
        form_geo = QFormLayout(grp_geo)

        self._spin_x = QDoubleSpinBox()
        self._spin_x.setRange(-100000, 100000)
        self._spin_x.setDecimals(1)
        self._spin_x.setSuffix(" cm")
        form_geo.addRow("X:", self._spin_x)

        self._spin_y = QDoubleSpinBox()
        self._spin_y.setRange(-100000, 100000)
        self._spin_y.setDecimals(1)
        self._spin_y.setSuffix(" cm")
        form_geo.addRow("Y:", self._spin_y)

        self._spin_piano = QSpinBox()
        self._spin_piano.setRange(0, 50)
        self._spin_piano.setSpecialValueText("0 (fondazione)")
        form_geo.addRow("Piano:", self._spin_piano)

        self._edit_etichetta = QLineEdit()
        self._edit_etichetta.setPlaceholderText("es. A, B, C1")
        form_geo.addRow("Etichetta:", self._edit_etichetta)

        layout.addWidget(grp_geo)

        # Vincolo esterno
        grp_vinc = QGroupBox("Vincolo esterno")
        form_vinc = QFormLayout(grp_vinc)

        self._combo_vincolo = QComboBox()
        for tipo, descr in _DESCRIZIONI_VINCOLO.items():
            self._combo_vincolo.addItem(descr, tipo)
        self._combo_vincolo.currentIndexChanged.connect(self._aggiorna_info_vincolo)
        form_vinc.addRow("Tipo:", self._combo_vincolo)

        self._spin_angolo_pendolo = QDoubleSpinBox()
        self._spin_angolo_pendolo.setRange(0, 180)
        self._spin_angolo_pendolo.setDecimals(1)
        self._spin_angolo_pendolo.setSuffix("°")
        self._spin_angolo_pendolo.setValue(90.0)
        form_vinc.addRow("Angolo pendolo:", self._spin_angolo_pendolo)

        self._lbl_gdl = QLabel()
        self._lbl_gdl.setStyleSheet("color: #555; font-style: italic;")
        form_vinc.addRow("GDL bloccati:", self._lbl_gdl)

        self._lbl_reazioni = QLabel()
        self._lbl_reazioni.setStyleSheet("color: #555; font-style: italic;")
        form_vinc.addRow("Reazioni:", self._lbl_reazioni)

        layout.addWidget(grp_vinc)

        self._aggiorna_info_vincolo()

        # Bottoni
        bottoni = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        bottoni.accepted.connect(self.accept)
        bottoni.rejected.connect(self.reject)
        layout.addWidget(bottoni)

    def _aggiorna_info_vincolo(self) -> None:
        tipo = self._combo_vincolo.currentData()
        if tipo is None:
            return
        v = VincoloEsterno(tipo=tipo)
        ux, uy, th = v.gdl_bloccati
        gdl_str = ", ".join(
            ([" ux"] if ux else [])
            + ([" uy"] if uy else [])
            + ([" θ"] if th else [])
        ) or "nessuno"
        self._lbl_gdl.setText(gdl_str.strip())
        self._lbl_reazioni.setText(f"{v.n_reazioni}")
        self._spin_angolo_pendolo.setVisible(tipo == TipoVincoloEsterno.PENDOLO)

    def _popola(self, nodo: NodoTelaio) -> None:
        self._spin_x.setValue(nodo.x)
        self._spin_y.setValue(nodo.y)
        self._spin_piano.setValue(nodo.piano)
        self._edit_etichetta.setText(nodo.etichetta)

        # Seleziona il tipo di vincolo
        for i in range(self._combo_vincolo.count()):
            if self._combo_vincolo.itemData(i) == nodo.vincolo.tipo:
                self._combo_vincolo.setCurrentIndex(i)
                break
        self._spin_angolo_pendolo.setValue(nodo.vincolo.angolo_pendolo_deg)
        self._aggiorna_info_vincolo()

    def get_dati(self) -> dict:
        """Ritorna i dati inseriti come dizionario."""
        tipo_vincolo = self._combo_vincolo.currentData()
        return {
            "x": self._spin_x.value(),
            "y": self._spin_y.value(),
            "piano": self._spin_piano.value(),
            "etichetta": self._edit_etichetta.text().strip(),
            "vincolo_tipo": tipo_vincolo,
            "angolo_pendolo_deg": self._spin_angolo_pendolo.value(),
        }
