"""Visualizzatore Debug Log (Qt6).

Finestra Qt per la visualizzazione in tempo reale del registro di log
centralizzato. Collegato a src.core.registro_log.registro.

Funzionalità:
- Visualizzazione in tempo reale di tutte le voci del registro
- Filtri per modulo, livello (INFO/AVVISO/ERRORE/CALCOLO/DEBUG)
- Ricerca testuale nel log
- Esportazione log come file .txt o .csv
- Aggiornamento automatico via listener
"""

from __future__ import annotations

import logging
from typing import Any

try:
    from PyQt6.QtCore import Qt, QTimer  # noqa: F401
    from PyQt6.QtWidgets import QSplitter  # noqa: F401
    from PyQt6.QtWidgets import (
        QComboBox,
        QFileDialog,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QPushButton,
        QSizePolicy,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )
except ImportError:  # pragma: no cover
    from PySide6.QtCore import QTimer
    from PySide6.QtWidgets import (
        QComboBox,
        QFileDialog,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QPushButton,
        QSizePolicy,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )

from src.core.registro_log import LivelloLog, VoceLog, registro

logger = logging.getLogger(__name__)

# Mappa livello → colore per evidenziazione
_COLORI_LIVELLO: dict[LivelloLog, str] = {
    LivelloLog.INFO: "#2196F3",  # Blu
    LivelloLog.AVVISO: "#FF9800",  # Arancione
    LivelloLog.ERRORE: "#F44336",  # Rosso
    LivelloLog.CALCOLO: "#4CAF50",  # Verde
    LivelloLog.DEBUG: "#9E9E9E",  # Grigio
}


class DebugViewerWindow(QWidget):
    """Finestra di visualizzazione del registro di debug.

    Si collega al registro centralizzato (src.core.registro_log.registro)
    e mostra le voci in tempo reale con filtri e ricerca.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("RD2229 — Registro Debug")
        self.setMinimumSize(800, 500)
        self._voci_buffer: list[VoceLog] = []
        self._inizializza_interfaccia()
        self._collega_registro()
        self._aggiorna_visualizzazione()

    def _inizializza_interfaccia(self) -> None:
        """Crea l'interfaccia utente del visualizzatore debug."""
        layout_principale = QVBoxLayout(self)

        # --- Barra filtri ---
        barra_filtri = QHBoxLayout()

        barra_filtri.addWidget(QLabel("Livello:"))
        self._combo_livello = QComboBox()
        self._combo_livello.addItem("Tutti", None)
        self._combo_livello.addItem("CALCOLO", LivelloLog.CALCOLO)
        self._combo_livello.addItem("INFO", LivelloLog.INFO)
        self._combo_livello.addItem("AVVISO", LivelloLog.AVVISO)
        self._combo_livello.addItem("ERRORE", LivelloLog.ERRORE)
        self._combo_livello.addItem("DEBUG", LivelloLog.DEBUG)
        self._combo_livello.currentIndexChanged.connect(self._aggiorna_visualizzazione)
        barra_filtri.addWidget(self._combo_livello)

        barra_filtri.addWidget(QLabel("Modulo:"))
        self._campo_modulo = QLineEdit()
        self._campo_modulo.setPlaceholderText("Filtra per modulo...")
        self._campo_modulo.textChanged.connect(self._aggiorna_visualizzazione)
        barra_filtri.addWidget(self._campo_modulo)

        barra_filtri.addWidget(QLabel("Cerca:"))
        self._campo_ricerca = QLineEdit()
        self._campo_ricerca.setPlaceholderText("Ricerca testo...")
        self._campo_ricerca.textChanged.connect(self._aggiorna_visualizzazione)
        barra_filtri.addWidget(self._campo_ricerca)

        layout_principale.addLayout(barra_filtri)

        # --- Area log ---
        self._area_log = QTextEdit()
        self._area_log.setReadOnly(True)
        self._area_log.setFontFamily("Courier New")
        self._area_log.setFontPointSize(9)
        self._area_log.setStyleSheet(
            "QTextEdit { background-color: #1E1E1E; color: #D4D4D4; " "border: 1px solid #333; }"
        )
        layout_principale.addWidget(self._area_log)

        # --- Barra inferiore ---
        barra_inferiore = QHBoxLayout()

        self._etichetta_conteggio = QLabel("Voci: 0")
        barra_inferiore.addWidget(self._etichetta_conteggio)

        barra_inferiore.addStretch()

        btn_svuota = QPushButton("Svuota log")
        btn_svuota.clicked.connect(self._svuota_log)
        barra_inferiore.addWidget(btn_svuota)

        btn_esporta_txt = QPushButton("Esporta .txt")
        btn_esporta_txt.clicked.connect(self._esporta_txt)
        barra_inferiore.addWidget(btn_esporta_txt)

        btn_esporta_csv = QPushButton("Esporta .csv")
        btn_esporta_csv.clicked.connect(self._esporta_csv)
        barra_inferiore.addWidget(btn_esporta_csv)

        layout_principale.addLayout(barra_inferiore)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def _collega_registro(self) -> None:
        """Collega il listener al registro centralizzato."""
        registro.aggiungi_listener(self._su_nuova_voce)

    def _su_nuova_voce(self, voce: VoceLog) -> None:
        """Callback chiamato dal registro per ogni nuova voce.

        Accumula le voci nel buffer e schedula un aggiornamento
        tramite QTimer per garantire thread-safety nella GUI.
        """
        self._voci_buffer.append(voce)
        # Aggiornamento differito per coalescing
        QTimer.singleShot(50, self._processa_buffer)

    def _processa_buffer(self) -> None:
        """Processa le voci accumulate nel buffer."""
        if not self._voci_buffer:
            return
        self._voci_buffer.clear()
        self._aggiorna_visualizzazione()

    def _aggiorna_visualizzazione(self) -> None:
        """Aggiorna l'area di log con le voci filtrate."""
        # Raccogli filtri
        indice_livello = self._combo_livello.currentIndex()
        livello_filtro = self._combo_livello.itemData(indice_livello)
        modulo_filtro = self._campo_modulo.text().strip() or None
        testo_filtro = self._campo_ricerca.text().strip() or None

        # Recupera voci filtrate dal registro
        voci = registro.ottieni_voci(
            modulo=modulo_filtro,
            livello=livello_filtro,
            testo_ricerca=testo_filtro,
            limite=500,  # Limita per prestazioni GUI
        )

        # Costruisci HTML per la visualizzazione
        html_righe = []
        for voce in voci:
            colore = _COLORI_LIVELLO.get(voce.livello, "#D4D4D4")
            # Riga principale
            html_righe.append(
                f'<span style="color:#808080">[{voce.timestamp}]</span> '
                f'<span style="color:{colore}"><b>[{voce.livello.value}]</b></span> '
                f'<span style="color:#569CD6">[{voce.modulo}]</span> '
                f"{_escape_html(voce.operazione)}"
            )
            # Dettagli aggiuntivi (se presenti)
            if voce.normativa:
                html_righe.append(
                    f'  <span style="color:#CE9178">Normativa: {_escape_html(voce.normativa)}</span>'
                )
            if voce.formula:
                html_righe.append(
                    f'  <span style="color:#DCDCAA">Formula: {_escape_html(voce.formula)}</span>'
                )
            if voce.input_dati:
                html_righe.append(
                    f'  <span style="color:#9CDCFE">Input: {_escape_html(str(voce.input_dati))}</span>'
                )
            if voce.output_dati:
                html_righe.append(
                    f'  <span style="color:#B5CEA8">Output: {_escape_html(str(voce.output_dati))}</span>'
                )
            if voce.esito:
                colore_esito = (
                    "#4EC9B0"
                    if "VERIFICATO" in voce.esito.upper() and "NON" not in voce.esito.upper()
                    else "#F44336"
                )
                html_righe.append(
                    f'  <span style="color:{colore_esito}"><b>Esito: {_escape_html(voce.esito)}</b></span>'
                )
            if voce.passaggi:
                for i, passo in enumerate(voce.passaggi, 1):
                    html_righe.append(
                        f'  <span style="color:#C586C0">  {i}. {_escape_html(passo)}</span>'
                    )
            html_righe.append("")  # Riga vuota di separazione

        contenuto_html = "<pre>" + "<br>".join(html_righe) + "</pre>"
        self._area_log.setHtml(contenuto_html)

        # Aggiorna conteggio
        totale = registro.numero_voci()
        filtrate = len(voci)
        self._etichetta_conteggio.setText(f"Voci: {filtrate}/{totale}")

    def _svuota_log(self) -> None:
        """Svuota il registro e aggiorna la visualizzazione."""
        registro.svuota()
        self._aggiorna_visualizzazione()

    def _esporta_txt(self) -> None:
        """Esporta il log in formato testo."""
        percorso, _ = QFileDialog.getSaveFileName(
            self, "Esporta Log TXT", "rd2229_log.txt", "File di testo (*.txt)"
        )
        if percorso:
            with open(percorso, "w", encoding="utf-8") as f:
                f.write(registro.esporta_testo())

    def _esporta_csv(self) -> None:
        """Esporta il log in formato CSV."""
        percorso, _ = QFileDialog.getSaveFileName(
            self, "Esporta Log CSV", "rd2229_log.csv", "File CSV (*.csv)"
        )
        if percorso:
            with open(percorso, "w", encoding="utf-8") as f:
                f.write(registro.esporta_csv())

    def closeEvent(self, event: Any) -> None:
        """Rimuove il listener dal registro alla chiusura."""
        registro.rimuovi_listener(self._su_nuova_voce)
        super().closeEvent(event)


def _escape_html(testo: str) -> str:
    """Escapa caratteri speciali HTML."""
    return testo.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


MODULE_SPEC = {
    "key": "debug_viewer",
    "name": "Registro Debug",
    "description": "Visualizzatore log e debug in tempo reale con filtri, ricerca ed esportazione (Qt6)",
}


def create_module(master: QWidget | None = None, **context: Any) -> DebugViewerWindow:
    """Factory per il modulo selettore."""
    return DebugViewerWindow(parent=master)
