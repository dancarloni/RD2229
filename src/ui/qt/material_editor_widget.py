"""Editor Materiali Strutturali (Qt6).

Editor completo per la gestione dei materiali strutturali con:
- ComboBox selezione famiglia (calcestruzzo / acciaio / muratura)
- ComboBox selezione norma di riferimento
- Campi dinamici in base alla famiglia selezionata
- Parametri derivati con calcolo automatico e mini-bottone ricalcolo singolo
- Override manuale dei parametri derivati (sovrascrivibili dall'utente)
- Bottone "Ricalcola tutti i derivati" in bulk
- Dropdown da archivio + input manuale sempre possibile
- Integrazione con registro_log per tracciamento operazioni

SOLO Qt (PySide6/PyQt6). Nessun Tkinter. Tutto italiano.
"""

from __future__ import annotations

import logging
from typing import Any

try:
    from PyQt6.QtCore import Qt  # noqa: F401
    from PyQt6.QtCore import pyqtSignal as Signal
    from PyQt6.QtWidgets import (
        QComboBox,
        QDoubleSpinBox,
        QFormLayout,
        QGroupBox,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QPushButton,
        QScrollArea,
        QSizePolicy,
        QToolButton,
        QVBoxLayout,
        QWidget,
    )
except ImportError:  # pragma: no cover
    from PySide6.QtCore import Signal
    from PySide6.QtWidgets import (
        QComboBox,
        QDoubleSpinBox,
        QFormLayout,
        QGroupBox,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QPushButton,
        QScrollArea,
        QSizePolicy,
        QToolButton,
        QVBoxLayout,
        QWidget,
    )

from src.core.registro_log import registro
from src.materials.material_model import (
    Material,
    crea_acciaio_ntc2018,
    crea_calcestruzzo_ntc2018,
    crea_muratura_ntc2018,
)

logger = logging.getLogger(__name__)

_FAMIGLIE = ["calcestruzzo", "acciaio", "muratura"]

_NORME_PER_FAMIGLIA: dict[str, list[str]] = {
    "calcestruzzo": ["NTC2018", "RD2229", "DM92", "DM96", "EC2"],
    "acciaio": ["NTC2018", "RD2229", "DM92", "DM96", "EC2"],
    "muratura": ["NTC2018", "DM87", "Circ81", "EC6"],
}

_CLASSI_CLS = [
    "C12/15",
    "C16/20",
    "C20/25",
    "C25/30",
    "C28/35",
    "C30/37",
    "C32/40",
    "C35/45",
    "C40/50",
    "C45/55",
    "C50/60",
]

_TIPI_ACCIAIO = ["B450C", "B450A", "B500B"]

_TIPI_BLOCCO = [
    "mattoni_pieni",
    "mattoni_semipieni",
    "blocchi_cls",
    "tufo",
    "pietra_squadrata",
]

_TIPI_MALTA = ["M2.5", "M5", "M10", "M15", "M20"]


class EditorMaterialeWidget(QWidget):
    """Widget Qt per l'editing completo di un materiale strutturale."""

    materiale_modificato = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("RD2229 — Editor Materiali")
        self.setMinimumSize(550, 600)
        self._materiale: Material | None = None
        self._campi_derivati: dict[str, QDoubleSpinBox] = {}
        self._bottoni_ricalcolo: dict[str, QToolButton] = {}
        self._aggiornamento_in_corso = False
        self._inizializza_interfaccia()
        self._su_cambia_famiglia(0)

    def _inizializza_interfaccia(self) -> None:
        """Crea l'interfaccia dell'editor materiali."""
        layout_principale = QVBoxLayout(self)

        # --- Intestazione ---
        intestazione = QHBoxLayout()
        intestazione.addWidget(QLabel("<b>Editor Materiale</b>"))
        intestazione.addStretch()
        btn_nuovo = QPushButton("Nuovo")
        btn_nuovo.clicked.connect(self._su_nuovo)
        intestazione.addWidget(btn_nuovo)
        layout_principale.addLayout(intestazione)

        # --- Identificazione ---
        gruppo_id = QGroupBox("Identificazione")
        form_id = QFormLayout(gruppo_id)

        self._campo_id = QLineEdit()
        self._campo_id.setPlaceholderText("ID univoco (es. cls_C25_30)")
        form_id.addRow("ID Materiale:", self._campo_id)

        self._campo_descrizione = QLineEdit()
        self._campo_descrizione.setPlaceholderText("Descrizione (es. Calcestruzzo C25/30)")
        form_id.addRow("Descrizione:", self._campo_descrizione)

        self._combo_famiglia = QComboBox()
        self._combo_famiglia.addItems(["Calcestruzzo", "Acciaio", "Muratura"])
        self._combo_famiglia.currentIndexChanged.connect(self._su_cambia_famiglia)
        form_id.addRow("Famiglia:", self._combo_famiglia)

        self._combo_norma = QComboBox()
        form_id.addRow("Norma:", self._combo_norma)

        layout_principale.addWidget(gruppo_id)

        # --- Selezione rapida ---
        self._gruppo_rapido = QGroupBox("Selezione rapida da archivio")
        layout_rapido = QHBoxLayout(self._gruppo_rapido)

        self._combo_classe = QComboBox()
        layout_rapido.addWidget(QLabel("Classe/Tipo:"))
        layout_rapido.addWidget(self._combo_classe)

        self._label_malta = QLabel("Malta:")
        self._combo_malta = QComboBox()
        self._combo_malta.addItems(_TIPI_MALTA)
        layout_rapido.addWidget(self._label_malta)
        layout_rapido.addWidget(self._combo_malta)

        btn_carica = QPushButton("Carica valori")
        btn_carica.setToolTip("Carica i valori standard dalla norma e dalla classe selezionata")
        btn_carica.clicked.connect(self._su_carica_valori)
        layout_rapido.addWidget(btn_carica)

        layout_principale.addWidget(self._gruppo_rapido)

        # --- Area parametri (scroll) ---
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self._contenitore_parametri = QWidget()
        self._layout_parametri = QVBoxLayout(self._contenitore_parametri)
        scroll.setWidget(self._contenitore_parametri)
        layout_principale.addWidget(scroll)

        self._gruppo_primari = QGroupBox("Parametri primari")
        self._form_primari = QFormLayout(self._gruppo_primari)
        self._layout_parametri.addWidget(self._gruppo_primari)

        self._gruppo_derivati = QGroupBox("Parametri derivati (calcolo automatico)")
        self._form_derivati = QFormLayout(self._gruppo_derivati)
        self._layout_parametri.addWidget(self._gruppo_derivati)

        btn_ricalcola = QPushButton("↻ Ricalcola tutti i derivati")
        btn_ricalcola.setToolTip("Ricalcola tutti i parametri derivati dalle formule automatiche")
        btn_ricalcola.clicked.connect(self._su_ricalcola_tutti)
        self._layout_parametri.addWidget(btn_ricalcola)

        self._layout_parametri.addStretch()

        # --- Barra inferiore ---
        barra_inf = QHBoxLayout()
        self._label_stato = QLabel("")
        barra_inf.addWidget(self._label_stato)
        barra_inf.addStretch()
        layout_principale.addLayout(barra_inf)

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def _su_cambia_famiglia(self, indice: int) -> None:
        """Gestisce il cambio di famiglia materiale."""
        famiglia = _FAMIGLIE[indice] if indice < len(_FAMIGLIE) else "calcestruzzo"

        self._combo_norma.clear()
        self._combo_norma.addItems(_NORME_PER_FAMIGLIA.get(famiglia, []))

        self._combo_classe.clear()
        if famiglia == "calcestruzzo":
            self._combo_classe.addItems(_CLASSI_CLS)
            self._label_malta.hide()
            self._combo_malta.hide()
        elif famiglia == "acciaio":
            self._combo_classe.addItems(_TIPI_ACCIAIO)
            self._label_malta.hide()
            self._combo_malta.hide()
        elif famiglia == "muratura":
            self._combo_classe.addItems(_TIPI_BLOCCO)
            self._label_malta.show()
            self._combo_malta.show()

        self._su_carica_valori()

    def _su_carica_valori(self) -> None:
        """Carica i valori standard dalla classe/tipo selezionato."""
        famiglia = _FAMIGLIE[self._combo_famiglia.currentIndex()]
        classe = self._combo_classe.currentText()
        if not classe:
            return

        if famiglia == "calcestruzzo":
            self._materiale = crea_calcestruzzo_ntc2018(classe)
        elif famiglia == "acciaio":
            self._materiale = crea_acciaio_ntc2018(classe)
        elif famiglia == "muratura":
            malta = self._combo_malta.currentText()
            self._materiale = crea_muratura_ntc2018(classe, malta)
        else:
            return

        self._aggiorna_campi_da_materiale()

        registro.operazione(
            modulo="editor_materiali",
            azione="Caricamento materiale da archivio",
            dettagli=f"{famiglia} {classe} — {self._combo_norma.currentText()}",
        )

    def _aggiorna_campi_da_materiale(self) -> None:
        """Aggiorna tutti i campi dell'interfaccia dal materiale corrente."""
        if not self._materiale:
            return

        self._aggiornamento_in_corso = True
        m = self._materiale

        self._campo_id.setText(m.material_id)
        self._campo_descrizione.setText(m.descrizione)

        self._svuota_form(self._form_primari)
        self._svuota_form(self._form_derivati)
        self._campi_derivati.clear()
        self._bottoni_ricalcolo.clear()

        # Parametri comuni
        self._aggiungi_campo_primario("E", "Modulo elastico E", m.E, "kg/cm²")
        self._aggiungi_campo_primario("nu", "Coeff. Poisson ν", m.nu, "—", decimali=3, massimo=0.5)
        self._aggiungi_campo_primario(
            "densita_kg_m3", "Densità", m.densita_kg_m3, "kg/m³", massimo=10000
        )

        if m.famiglia == "calcestruzzo":
            self._aggiungi_campo_primario("f_ck", "f_ck (car. cilindrica)", m.f_ck, "kg/cm²")
            self._aggiungi_campo_primario("gamma_c", "γ_c", m.gamma_c, "—", decimali=2, massimo=3.0)
            self._aggiungi_campo_primario(
                "alpha_cc", "α_cc", m.alpha_cc, "—", decimali=2, massimo=1.0
            )
            self._aggiungi_campo_primario(
                "sigma_c28", "σ_c28 (cubica 28gg TA)", m.sigma_c28, "kg/cm²"
            )
            self._aggiungi_campo_primario("sigma_c_adm", "σ_c,adm (TA)", m.sigma_c_adm, "kg/cm²")
            self._aggiungi_campo_primario(
                "n_omogenizzazione", "n (omogenizz. TA)", m.n_omogenizzazione, "—", massimo=30
            )
            for nome, etichetta in [
                ("f_cd", "f_cd (calcolo)"),
                ("f_cm", "f_cm (media)"),
                ("f_ctm", "f_ctm (traz. media)"),
                ("f_ctk_005", "f_ctk,0.05 (5%)"),
                ("E_cm", "E_cm (modulo)"),
                ("G", "G (taglio)"),
            ]:
                self._aggiungi_campo_derivato(nome, etichetta, "kg/cm²")

        elif m.famiglia == "acciaio":
            self._aggiungi_campo_primario("f_yk", "f_yk (snervamento)", m.f_yk, "kg/cm²")
            self._aggiungi_campo_primario("gamma_s", "γ_s", m.gamma_s, "—", decimali=2, massimo=3.0)
            self._aggiungi_campo_primario("sigma_s_adm", "σ_s,adm (TA)", m.sigma_s_adm, "kg/cm²")
            for nome, etichetta in [("f_yd", "f_yd (calcolo)"), ("G", "G (taglio)")]:
                self._aggiungi_campo_derivato(nome, etichetta, "kg/cm²")

        elif m.famiglia == "muratura":
            self._aggiungi_campo_primario("f_k", "f_k (compress. car.)", m.f_k, "kg/cm²")
            self._aggiungi_campo_primario("f_vk0", "f_vk0 (taglio senza σ)", m.f_vk0, "kg/cm²")
            self._aggiungi_campo_primario("gamma_M", "γ_M", m.gamma_M, "—", decimali=2, massimo=5.0)
            for nome, etichetta in [
                ("f_d", "f_d (calcolo compr.)"),
                ("f_vd", "f_vd (calcolo taglio)"),
                ("G", "G (taglio)"),
            ]:
                self._aggiungi_campo_derivato(nome, etichetta, "kg/cm²")

        self._label_stato.setText(f"Materiale: {m.material_id}")
        self._aggiornamento_in_corso = False

    def _aggiungi_campo_primario(
        self,
        nome_attr: str,
        etichetta: str,
        valore: float,
        unita: str,
        decimali: int = 1,
        massimo: float = 9999999.0,
    ) -> None:
        """Aggiunge un campo editabile per un parametro primario."""
        spin = QDoubleSpinBox()
        spin.setDecimals(decimali)
        spin.setRange(0, massimo)
        spin.setValue(valore)
        spin.setSuffix(f" {unita}")
        spin.setToolTip(f"{etichetta} [{unita}]")
        spin.valueChanged.connect(lambda v, n=nome_attr: self._su_modifica_primario(n, v))
        self._form_primari.addRow(f"{etichetta}:", spin)

    def _aggiungi_campo_derivato(self, nome: str, etichetta: str, unita: str) -> None:
        """Aggiunge un campo derivato con mini-bottone ↻ per ricalcolo."""
        layout_riga = QHBoxLayout()

        spin = QDoubleSpinBox()
        spin.setDecimals(1)
        spin.setRange(0, 9999999)
        valore = self._materiale.ottieni_derivato(nome) if self._materiale else 0.0
        spin.setValue(valore)
        spin.setSuffix(f" {unita}")

        pd = self._materiale._derivati.get(nome) if self._materiale else None
        formula = pd.formula if pd else ""
        spin.setToolTip(f"{etichetta}\nFormula: {formula}")
        spin.valueChanged.connect(lambda v, n=nome: self._su_modifica_derivato(n, v))
        layout_riga.addWidget(spin)

        btn = QToolButton()
        btn.setText("↻")
        btn.setToolTip(f"Ricalcola {nome} dalla formula automatica")
        btn.setFixedSize(24, 24)
        btn.clicked.connect(lambda _, n=nome: self._su_ricalcola_singolo(n))
        layout_riga.addWidget(btn)

        contenitore = QWidget()
        contenitore.setLayout(layout_riga)

        label_riga = f"⚠ {etichetta}:" if (pd and pd.override) else f"{etichetta}:"
        self._form_derivati.addRow(label_riga, contenitore)
        self._campi_derivati[nome] = spin
        self._bottoni_ricalcolo[nome] = btn

    def _su_modifica_primario(self, nome: str, valore: float) -> None:
        """Gestisce la modifica di un parametro primario."""
        if not self._materiale or self._aggiornamento_in_corso:
            return
        if hasattr(self._materiale, nome):
            setattr(self._materiale, nome, valore)
            self._materiale.aggiorna_da_primario(nome)
            self._aggiorna_valori_derivati()
            registro.operazione(
                modulo="editor_materiali",
                azione=f"Modifica parametro primario {nome}",
                dettagli=f"{nome} = {valore}",
            )

    def _su_modifica_derivato(self, nome: str, valore: float) -> None:
        """Gestisce l'override manuale di un parametro derivato."""
        if not self._materiale or self._aggiornamento_in_corso:
            return
        valore_auto = self._materiale.ottieni_derivato(nome)
        if abs(valore - valore_auto) > 0.05:
            self._materiale.imposta_derivato_manuale(nome, valore)

    def _su_ricalcola_singolo(self, nome: str) -> None:
        """Ricalcola un singolo parametro derivato."""
        if not self._materiale:
            return
        nuovo_valore = self._materiale.ricalcola_singolo_derivato(nome)
        if nome in self._campi_derivati:
            self._aggiornamento_in_corso = True
            self._campi_derivati[nome].setValue(nuovo_valore)
            self._aggiornamento_in_corso = False

    def _su_ricalcola_tutti(self) -> None:
        """Ricalcola tutti i parametri derivati (bulk)."""
        if not self._materiale:
            return
        self._materiale.ricalcola_tutti_derivati()
        self._aggiorna_valori_derivati()
        registro.operazione(
            modulo="editor_materiali",
            azione="Ricalcolo bulk tutti i derivati",
            dettagli=f"Materiale {self._materiale.material_id}",
        )

    def _aggiorna_valori_derivati(self) -> None:
        """Aggiorna i valori visualizzati nei campi derivati."""
        if not self._materiale:
            return
        self._aggiornamento_in_corso = True
        for nome, spin in self._campi_derivati.items():
            valore = self._materiale.ottieni_derivato(nome)
            spin.setValue(valore)
        self._aggiornamento_in_corso = False

    def _su_nuovo(self) -> None:
        """Crea un nuovo materiale vuoto."""
        self._combo_famiglia.setCurrentIndex(0)
        self._su_carica_valori()

    def _svuota_form(self, form: QFormLayout) -> None:
        """Rimuove tutte le righe da un QFormLayout."""
        while form.rowCount() > 0:
            form.removeRow(0)

    def ottieni_materiale(self) -> Material | None:
        """Restituisce il materiale correntemente editato."""
        if self._materiale:
            self._materiale.material_id = self._campo_id.text()
            self._materiale.descrizione = self._campo_descrizione.text()
        return self._materiale


MODULE_SPEC = {
    "key": "material_editor",
    "name": "Editor Materiali",
    "description": "Editor completo materiali strutturali con parametri derivati e ricalcolo automatico (Qt6)",
}


def create_module(master: QWidget | None = None, **context: Any) -> EditorMaterialeWidget:
    """Factory per il modulo editor materiali."""
    return EditorMaterialeWidget(parent=master)
