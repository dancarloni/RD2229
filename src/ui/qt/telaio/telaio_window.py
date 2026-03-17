"""
TelaioWindow — Finestra principale per il calcolo di telai piani Cross-Pozzati.

Architettura Qt:
  - QMainWindow con MenuBar + ToolBar
  - DockLeft  (280px): input nodi/aste/carichi/sisma
  - Central:  CanvasTelaio
  - DockRight (300px): risultati/verifiche/armatura
  - DockBottom (150px): anteprima tabulato

Subfase L.9 del modulo telai piani RD 2229/39.
"""

from __future__ import annotations

import json

try:
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QAction, QIcon  # noqa: F401
    from PyQt6.QtWidgets import QGroupBox  # noqa: F401
    from PyQt6.QtWidgets import QMenu  # noqa: F401
    from PyQt6.QtWidgets import QMenuBar  # noqa: F401
    from PyQt6.QtWidgets import QScrollArea  # noqa: F401
    from PyQt6.QtWidgets import QSizePolicy  # noqa: F401
    from PyQt6.QtWidgets import QSplitter  # noqa: F401
    from PyQt6.QtWidgets import (
        QComboBox,
        QDialog,
        QDockWidget,
        QFileDialog,
        QHBoxLayout,
        QLabel,
        QMainWindow,
        QMessageBox,
        QPushButton,
        QStatusBar,
        QTableWidget,
        QTableWidgetItem,
        QTabWidget,
        QTextEdit,
        QToolBar,
        QVBoxLayout,
        QWidget,
    )
except ImportError:
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QAction
    from PySide6.QtWidgets import (
        QComboBox,
        QDialog,
        QDockWidget,
        QFileDialog,
        QHBoxLayout,
        QLabel,
        QMainWindow,
        QMessageBox,
        QPushButton,
        QStatusBar,
        QTableWidget,
        QTableWidgetItem,
        QTabWidget,
        QTextEdit,
        QToolBar,
        QVBoxLayout,
        QWidget,
    )

from src.methods.rd2229.telaio.armature_telaio import proponi_armature_telaio
from src.ui.qt.telaio.canvas_telaio import CanvasTelaio, ModalitaCanvas
from src.methods.rd2229.telaio.combinazioni_rd2229 import calcola_tutte_le_combinazioni
from src.ui.qt.telaio.dialogo_asta import DialogoAsta
from src.ui.qt.telaio.dialogo_nodo import DialogoNodo
from src.methods.rd2229.telaio.export_telaio import genera_tabulato_ascii, salva_tabulato
from src.methods.rd2229.telaio.modello_telaio import (
    AstaTelaio,
    ModelloTelaio,
    NodoTelaio,
    PianoTelaio,
    TipoVincoloEsterno,
    VincoloEsterno,
)
from src.methods.rd2229.telaio.solver_telaio import calcola_caso_carico
from src.methods.rd2229.telaio.verifiche_telaio import verifica_completa_telaio


class TelaioWindow(QMainWindow):
    """Finestra principale per il calcolo di telai piani Cross-Pozzati."""

    def __init__(self, parent: QWidget | None = None, **context):
        super().__init__(parent)
        self.setWindowTitle("Telai Piani — Cross-Pozzati (RD 2229/39)")
        self.setMinimumSize(1200, 700)

        # Stato applicazione
        self._modello: ModelloTelaio = self._nuovo_modello()
        self._risultati_per_caso: dict = {}
        self._dati_cross_per_caso: dict = {}
        self._inviluppo: dict = {}
        self._armature: dict = {}
        self._verifiche: dict = {}
        self._id_nodo_corrente: int = 0
        self._id_asta_corrente: int = 0

        self._init_ui()
        self._aggiorna_tabelle_input()

    # ------------------------------------------------------------------
    # INIZIALIZZAZIONE UI
    # ------------------------------------------------------------------

    def _init_ui(self) -> None:
        self._crea_menubar()
        self._crea_toolbar()
        self._crea_dock_sinistra()
        self._crea_canvas_centrale()
        self._crea_dock_destra()
        self._crea_dock_basso()
        self._crea_statusbar()

    def _crea_menubar(self) -> None:
        mb = self.menuBar()

        # Modello
        m_modello = mb.addMenu("&Modello")
        m_modello.addAction("Nuovo modello", self._nuovo_modello_ui)
        m_modello.addAction("Apri...", self._apri_modello)
        m_modello.addAction("Salva...", self._salva_modello)
        m_modello.addSeparator()
        m_modello.addAction("Proprietà modello...", self._proprieta_modello)

        # Calcola
        m_calc = mb.addMenu("&Calcola")
        m_calc.addAction("Esegui calcolo (LC1+LC2)", self._esegui_calcolo)
        m_calc.addAction("Calcolo completo (tutte le combinazioni)", self._esegui_calcolo_completo)

        # Armature
        m_arm = mb.addMenu("&Armature")
        m_arm.addAction("Proposta automatica armature", self._proponi_armature)
        m_arm.addAction("Verifica armature correnti", self._verifica_armature)

        # Report
        m_rep = mb.addMenu("&Report")
        m_rep.addAction("Tabulato ASCII...", self._esporta_ascii)
        m_rep.addAction("Report HTML...", self._esporta_html)

        # ?
        m_aiuto = mb.addMenu("&?")
        m_aiuto.addAction("Informazioni", self._mostra_info)

    def _crea_toolbar(self) -> None:
        tb = QToolBar("Strumenti")
        self.addToolBar(tb)

        self._act_sel = QAction("↖ Selezione", self)
        self._act_sel.setCheckable(True)
        self._act_sel.setChecked(True)
        self._act_sel.triggered.connect(lambda: self._imposta_modalita(ModalitaCanvas.SELEZIONE))
        tb.addAction(self._act_sel)

        self._act_nodo = QAction("● Nodo", self)
        self._act_nodo.setCheckable(True)
        self._act_nodo.triggered.connect(
            lambda: self._imposta_modalita(ModalitaCanvas.AGGIUNGI_NODO)
        )
        tb.addAction(self._act_nodo)

        self._act_asta = QAction("━ Asta", self)
        self._act_asta.setCheckable(True)
        self._act_asta.triggered.connect(
            lambda: self._imposta_modalita(ModalitaCanvas.AGGIUNGI_ASTA)
        )
        tb.addAction(self._act_asta)

        tb.addSeparator()

        act_calcola = QAction("▶ Calcola", self)
        act_calcola.triggered.connect(self._esegui_calcolo)
        tb.addAction(act_calcola)

        tb.addSeparator()

        # Overlay diagrammi
        tb.addWidget(QLabel(" Vista: "))
        self._combo_overlay = QComboBox()
        self._combo_overlay.addItems(["Telaio", "Diag. M", "Diag. V", "Diag. N"])
        self._combo_overlay.currentTextChanged.connect(self._cambia_overlay)
        tb.addWidget(self._combo_overlay)

    def _crea_dock_sinistra(self) -> None:
        dock = QDockWidget("Input", self)
        dock.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea
        )
        dock.setMinimumWidth(280)

        container = QWidget()
        lay = QVBoxLayout(container)

        tabs = QTabWidget()

        # --- Tab Nodi ---
        tab_nodi = QWidget()
        lay_nodi = QVBoxLayout(tab_nodi)

        self._tabella_nodi = QTableWidget(0, 5)
        self._tabella_nodi.setHorizontalHeaderLabels(
            ["ID", "Etich.", "X [cm]", "Y [cm]", "Vincolo"]
        )
        self._tabella_nodi.horizontalHeader().setStretchLastSection(True)
        self._tabella_nodi.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        lay_nodi.addWidget(self._tabella_nodi)

        btn_row_n = QHBoxLayout()
        btn_add_n = QPushButton("+ Nodo")
        btn_add_n.clicked.connect(self._aggiungi_nodo)
        btn_edit_n = QPushButton("Modifica")
        btn_edit_n.clicked.connect(self._modifica_nodo)
        btn_del_n = QPushButton("Elimina")
        btn_del_n.clicked.connect(self._elimina_nodo)
        for b in (btn_add_n, btn_edit_n, btn_del_n):
            btn_row_n.addWidget(b)
        lay_nodi.addLayout(btn_row_n)

        tabs.addTab(tab_nodi, "Nodi")

        # --- Tab Aste ---
        tab_aste = QWidget()
        lay_aste = QVBoxLayout(tab_aste)

        self._tabella_aste = QTableWidget(0, 6)
        self._tabella_aste.setHorizontalHeaderLabels(
            ["ID", "Etich.", "i→j", "Tipo", "b×h", "Carichi"]
        )
        self._tabella_aste.horizontalHeader().setStretchLastSection(True)
        self._tabella_aste.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        lay_aste.addWidget(self._tabella_aste)

        btn_row_a = QHBoxLayout()
        btn_add_a = QPushButton("+ Asta")
        btn_add_a.clicked.connect(self._aggiungi_asta)
        btn_edit_a = QPushButton("Modifica")
        btn_edit_a.clicked.connect(self._modifica_asta)
        btn_del_a = QPushButton("Elimina")
        btn_del_a.clicked.connect(self._elimina_asta)
        for b in (btn_add_a, btn_edit_a, btn_del_a):
            btn_row_a.addWidget(b)
        lay_aste.addLayout(btn_row_a)

        tabs.addTab(tab_aste, "Aste")

        # --- Tab Sisma ---
        tab_sisma = QWidget()
        form_sisma = QVBoxLayout(tab_sisma)

        from PyQt6.QtWidgets import QFormLayout

        fl = QFormLayout()
        self._combo_zona = QComboBox()
        for zona in ("non_sismico", "bassa", "media", "alta"):
            self._combo_zona.addItem(zona)
        self._combo_zona.setCurrentText("media")
        self._combo_zona.currentTextChanged.connect(self._aggiorna_zona_sismica)
        fl.addRow("Zona sismica:", self._combo_zona)
        form_sisma.addLayout(fl)

        self._lbl_info_sisma = QLabel(
            "Coefficienti RD2229:\n"
            "  non_sismico: Cs=0\n"
            "  bassa: Cs=0.05\n"
            "  media: Cs=0.07\n"
            "  alta:  Cs=0.10"
        )
        self._lbl_info_sisma.setStyleSheet("font-size: 10px; color: #555;")
        form_sisma.addWidget(self._lbl_info_sisma)
        form_sisma.addStretch()

        tabs.addTab(tab_sisma, "Sisma")

        lay.addWidget(tabs)
        dock.setWidget(container)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, dock)

    def _crea_canvas_centrale(self) -> None:
        self._canvas = CanvasTelaio(self)
        self._canvas.nodo_richiesto.connect(self._on_nodo_richiesto_canvas)
        self._canvas.asta_richiesta.connect(self._on_asta_richiesta_canvas)
        self._canvas.nodo_cliccato.connect(self._on_nodo_selezionato)
        self._canvas.asta_cliccata.connect(self._on_asta_selezionata)
        self.setCentralWidget(self._canvas)

    def _crea_dock_destra(self) -> None:
        dock = QDockWidget("Risultati", self)
        dock.setMinimumWidth(300)

        container = QWidget()
        lay = QVBoxLayout(container)

        self._lbl_elem_selezionato = QLabel("<i>Nessun elemento selezionato</i>")
        lay.addWidget(self._lbl_elem_selezionato)

        tabs_res = QTabWidget()

        # Sollecitazioni
        tab_soll = QWidget()
        lay_soll = QVBoxLayout(tab_soll)
        self._tabella_soll = QTableWidget(0, 4)
        self._tabella_soll.setHorizontalHeaderLabels(["Combo", "M_i", "M_mid", "M_j"])
        lay_soll.addWidget(QLabel("Sollecitazioni (3 sezioni):"))
        lay_soll.addWidget(self._tabella_soll)
        tabs_res.addTab(tab_soll, "Sollecitazioni")

        # Verifiche
        tab_ver = QWidget()
        lay_ver = QVBoxLayout(tab_ver)
        self._tabella_ver = QTableWidget(0, 3)
        self._tabella_ver.setHorizontalHeaderLabels(["Sezione", "Check", "Esito"])
        lay_ver.addWidget(QLabel("Verifiche TA:"))
        lay_ver.addWidget(self._tabella_ver)
        tabs_res.addTab(tab_ver, "Verifiche")

        # Armatura
        tab_arm = QWidget()
        lay_arm = QVBoxLayout(tab_arm)
        self._tabella_arm = QTableWidget(0, 4)
        self._tabella_arm.setHorizontalHeaderLabels(["Sezione", "As_inf", "As_sup", "Staffe"])
        lay_arm.addWidget(QLabel("Armatura corrente:"))
        lay_arm.addWidget(self._tabella_arm)
        tabs_res.addTab(tab_arm, "Armatura")

        lay.addWidget(tabs_res)
        dock.setWidget(container)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock)

    def _crea_dock_basso(self) -> None:
        dock = QDockWidget("Tabulato", self)
        dock.setMaximumHeight(200)

        container = QWidget()
        lay = QVBoxLayout(container)

        self._testo_tabulato = QTextEdit()
        self._testo_tabulato.setReadOnly(True)
        self._testo_tabulato.setFont(
            __import__("PyQt6.QtGui", fromlist=["QFont"]).QFont("Courier New", 8) if True else None
        )
        lay.addWidget(self._testo_tabulato)

        btn_row = QHBoxLayout()
        btn_ascii = QPushButton("Tabulato ASCII")
        btn_ascii.clicked.connect(self._aggiorna_anteprima)
        btn_html = QPushButton("Salva HTML...")
        btn_html.clicked.connect(self._esporta_html)
        btn_row.addWidget(btn_ascii)
        btn_row.addWidget(btn_html)
        btn_row.addStretch()
        lay.addLayout(btn_row)

        dock.setWidget(container)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, dock)

    def _crea_statusbar(self) -> None:
        self._statusbar = QStatusBar()
        self.setStatusBar(self._statusbar)
        self._statusbar.showMessage("Pronto. Aggiungi nodi e aste per costruire il telaio.")

    # ------------------------------------------------------------------
    # STATO MODELLO
    # ------------------------------------------------------------------

    def _nuovo_modello(self, nome: str = "Telaio") -> ModelloTelaio:
        return ModelloTelaio(nome=nome, nodi=[], aste=[], piani=[], zona_sismica="media")

    def _nuovo_modello_ui(self) -> None:
        if (
            QMessageBox.question(
                self,
                "Nuovo modello",
                "Perdere le modifiche non salvate e creare un nuovo modello?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            == QMessageBox.StandardButton.Yes
        ):
            self._modello = self._nuovo_modello()
            self._risultati_per_caso = {}
            self._inviluppo = {}
            self._armature = {}
            self._verifiche = {}
            self._id_nodo_corrente = 0
            self._id_asta_corrente = 0
            self._aggiorna_tutto()

    # ------------------------------------------------------------------
    # GESTIONE NODI
    # ------------------------------------------------------------------

    def _aggiungi_nodo(self, x_cm: float = 0.0, y_cm: float = 0.0) -> None:
        # Crea nodo provvisorio
        self._id_nodo_corrente += 1
        nodo_tmp = NodoTelaio(
            id=self._id_nodo_corrente,
            x=x_cm,
            y=y_cm,
            vincolo=VincoloEsterno(TipoVincoloEsterno.LIBERO),
        )
        dlg = DialogoNodo(nodo=nodo_tmp, parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            dati = dlg.get_dati()
            nodo = NodoTelaio(
                id=self._id_nodo_corrente,
                x=dati["x"],
                y=dati["y"],
                piano=dati["piano"],
                etichetta=dati["etichetta"],
                vincolo=VincoloEsterno(
                    tipo=dati["vincolo_tipo"],
                    angolo_pendolo_deg=dati["angolo_pendolo_deg"],
                ),
            )
            self._modello.nodi.append(nodo)
            self._aggiorna_piani()
            self._aggiorna_tutto()
            self._statusbar.showMessage(f"Nodo {nodo.id} aggiunto in ({nodo.x}, {nodo.y}) cm")
        else:
            self._id_nodo_corrente -= 1

    def _modifica_nodo(self) -> None:
        riga = self._tabella_nodi.currentRow()
        if riga < 0 or riga >= len(self._modello.nodi):
            return
        nodo = self._modello.nodi[riga]
        dlg = DialogoNodo(nodo=nodo, parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            dati = dlg.get_dati()
            nodo.x = dati["x"]
            nodo.y = dati["y"]
            nodo.piano = dati["piano"]
            nodo.etichetta = dati["etichetta"]
            nodo.vincolo = VincoloEsterno(
                tipo=dati["vincolo_tipo"],
                angolo_pendolo_deg=dati["angolo_pendolo_deg"],
            )
            self._aggiorna_tutto()

    def _elimina_nodo(self) -> None:
        riga = self._tabella_nodi.currentRow()
        if riga < 0 or riga >= len(self._modello.nodi):
            return
        nodo = self._modello.nodi[riga]
        # Verifica se aste dipendono dal nodo
        aste_collegate = [
            a for a in self._modello.aste if a.nodo_i == nodo.id or a.nodo_j == nodo.id
        ]
        if aste_collegate:
            QMessageBox.warning(
                self,
                "Nodo in uso",
                f"Il nodo {nodo.id} è connesso a {len(aste_collegate)} aste. "
                "Rimuovi prima le aste.",
            )
            return
        self._modello.nodi.pop(riga)
        self._aggiorna_tutto()

    def _on_nodo_richiesto_canvas(self, x_cm: float, y_cm: float) -> None:
        self._aggiungi_nodo(x_cm, y_cm)

    def _on_nodo_selezionato(self, id_nodo: int) -> None:
        nodo = self._modello.nodo_by_id(id_nodo)
        if nodo:
            self._lbl_elem_selezionato.setText(
                f"<b>Nodo {id_nodo}</b> — {nodo.etichetta or '?'}  "
                f"({nodo.x:.0f}, {nodo.y:.0f}) cm  |  {nodo.vincolo.tipo.value}"
            )

    # ------------------------------------------------------------------
    # GESTIONE ASTE
    # ------------------------------------------------------------------

    def _aggiungi_asta(self, id_i: int = 0, id_j: int = 0) -> None:
        if len(self._modello.nodi) < 2:
            QMessageBox.information(self, "Aste", "Aggiungi almeno 2 nodi prima.")
            return
        nodi_disp = [(n.id, n.etichetta) for n in self._modello.nodi]
        self._id_asta_corrente += 1

        # Preseleziona i nodi se passati dal canvas
        dlg = DialogoAsta(nodi_disponibili=nodi_disp, parent=self)
        if id_i and id_j:
            for i in range(dlg._combo_nodo_i.count()):
                if dlg._combo_nodo_i.itemData(i) == id_i:
                    dlg._combo_nodo_i.setCurrentIndex(i)
                if dlg._combo_nodo_j.itemData(i) == id_j:
                    dlg._combo_nodo_j.setCurrentIndex(i)

        if dlg.exec() == QDialog.DialogCode.Accepted:
            dati = dlg.get_dati()
            sez = dati["sezione"]
            # Salva sigma_c/s_adm come attributi diretti sulla sezione
            sez.sigma_c_adm = dati["sezione"].extra.get("sigma_c_adm", 80.0)
            sez.sigma_s_adm = dati["sezione"].extra.get("sigma_s_adm", 1400.0)
            asta = AstaTelaio(
                id=self._id_asta_corrente,
                nodo_i=dati["nodo_i"],
                nodo_j=dati["nodo_j"],
                tipo=dati["tipo"],
                sezione=sez,
                carichi=dati["carichi"],
                rilascio_i=dati["rilascio_i"],
                rilascio_j=dati["rilascio_j"],
                etichetta=dati["etichetta"],
            )
            self._modello.aste.append(asta)
            self._aggiorna_tutto()
            self._statusbar.showMessage(
                f"Asta {asta.id} ({asta.etichetta}) aggiunta: nodo {asta.nodo_i} → {asta.nodo_j}"
            )
        else:
            self._id_asta_corrente -= 1

    def _modifica_asta(self) -> None:
        riga = self._tabella_aste.currentRow()
        if riga < 0 or riga >= len(self._modello.aste):
            return
        asta = self._modello.aste[riga]
        nodi_disp = [(n.id, n.etichetta) for n in self._modello.nodi]
        dlg = DialogoAsta(asta=asta, nodi_disponibili=nodi_disp, parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            dati = dlg.get_dati()
            sez = dati["sezione"]
            sez.sigma_c_adm = dati["sezione"].extra.get("sigma_c_adm", 80.0)
            sez.sigma_s_adm = dati["sezione"].extra.get("sigma_s_adm", 1400.0)
            asta.nodo_i = dati["nodo_i"]
            asta.nodo_j = dati["nodo_j"]
            asta.tipo = dati["tipo"]
            asta.sezione = sez
            asta.carichi = dati["carichi"]
            asta.rilascio_i = dati["rilascio_i"]
            asta.rilascio_j = dati["rilascio_j"]
            asta.etichetta = dati["etichetta"]
            self._aggiorna_tutto()

    def _elimina_asta(self) -> None:
        riga = self._tabella_aste.currentRow()
        if riga < 0 or riga >= len(self._modello.aste):
            return
        self._modello.aste.pop(riga)
        self._aggiorna_tutto()

    def _on_asta_richiesta_canvas(self, id_i: int, id_j: int) -> None:
        self._aggiungi_asta(id_i, id_j)

    def _on_asta_selezionata(self, id_asta: int) -> None:
        asta = self._modello.asta_by_id(id_asta)
        if not asta:
            return
        L = self._modello.lunghezza_asta(id_asta)
        self._lbl_elem_selezionato.setText(
            f"<b>Asta {id_asta}</b> — {asta.etichetta or '?'}  "
            f"|  {asta.tipo.value}  |  L={L:.1f} cm  |  "
            f"{asta.sezione.b:.0f}×{asta.sezione.h:.0f} cm"
        )
        self._aggiorna_dock_risultati(id_asta)

    # ------------------------------------------------------------------
    # AGGIORNAMENTO UI
    # ------------------------------------------------------------------

    def _aggiorna_tutto(self) -> None:
        self._aggiorna_tabelle_input()
        self._canvas.carica_modello(self._modello)

    def _aggiorna_tabelle_input(self) -> None:
        # Nodi
        self._tabella_nodi.setRowCount(len(self._modello.nodi))
        for i, nodo in enumerate(self._modello.nodi):
            self._tabella_nodi.setItem(i, 0, QTableWidgetItem(str(nodo.id)))
            self._tabella_nodi.setItem(i, 1, QTableWidgetItem(nodo.etichetta))
            self._tabella_nodi.setItem(i, 2, QTableWidgetItem(f"{nodo.x:.1f}"))
            self._tabella_nodi.setItem(i, 3, QTableWidgetItem(f"{nodo.y:.1f}"))
            self._tabella_nodi.setItem(i, 4, QTableWidgetItem(nodo.vincolo.tipo.value))

        # Aste
        self._tabella_aste.setRowCount(len(self._modello.aste))
        for i, asta in enumerate(self._modello.aste):
            self._tabella_aste.setItem(i, 0, QTableWidgetItem(str(asta.id)))
            self._tabella_aste.setItem(i, 1, QTableWidgetItem(asta.etichetta))
            self._tabella_aste.setItem(i, 2, QTableWidgetItem(f"{asta.nodo_i}→{asta.nodo_j}"))
            self._tabella_aste.setItem(i, 3, QTableWidgetItem(asta.tipo.value))
            self._tabella_aste.setItem(
                i, 4, QTableWidgetItem(f"{asta.sezione.b:.0f}×{asta.sezione.h:.0f}")
            )
            self._tabella_aste.setItem(i, 5, QTableWidgetItem(str(len(asta.carichi))))

    def _aggiorna_dock_risultati(self, id_asta: int) -> None:
        """Aggiorna il dock destro con i risultati dell'asta selezionata."""
        # Sollecitazioni
        self._tabella_soll.setRowCount(0)
        for id_caso, ris in self._risultati_per_caso.items():
            soll = ris.sollecitazioni.get(id_asta)
            if soll and soll.M:
                row = self._tabella_soll.rowCount()
                self._tabella_soll.insertRow(row)
                self._tabella_soll.setItem(row, 0, QTableWidgetItem(id_caso))
                self._tabella_soll.setItem(row, 1, QTableWidgetItem(f"{soll.M[0]:.0f}"))
                self._tabella_soll.setItem(
                    row, 2, QTableWidgetItem(f"{soll.M[1]:.0f}" if len(soll.M) > 1 else "—")
                )
                self._tabella_soll.setItem(
                    row, 3, QTableWidgetItem(f"{soll.M[2]:.0f}" if len(soll.M) > 2 else "—")
                )

        # Verifiche
        self._tabella_ver.setRowCount(0)
        if id_asta in self._verifiche:
            ris_v = self._verifiche[id_asta]
            for posizione, sez in ris_v.sezioni.items():
                for check_nome, check_res in [
                    ("Fless./Press.", sez.flessione),
                    ("Taglio", sez.taglio),
                    ("Minimi", sez.minimi),
                ]:
                    if check_res is None:
                        continue
                    row = self._tabella_ver.rowCount()
                    self._tabella_ver.insertRow(row)
                    self._tabella_ver.setItem(row, 0, QTableWidgetItem(posizione))
                    self._tabella_ver.setItem(row, 1, QTableWidgetItem(check_nome))
                    esito = "✅" if check_res.ok else "❌"
                    util = (
                        f"{check_res.utilisation:.1%}" if check_res.utilisation is not None else "—"
                    )
                    self._tabella_ver.setItem(row, 2, QTableWidgetItem(f"{esito} {util}"))

        # Armatura
        self._tabella_arm.setRowCount(0)
        if id_asta in self._armature:
            for pos, arm in self._armature[id_asta].items():
                row = self._tabella_arm.rowCount()
                self._tabella_arm.insertRow(row)
                self._tabella_arm.setItem(row, 0, QTableWidgetItem(pos))
                self._tabella_arm.setItem(row, 1, QTableWidgetItem(f"{arm.As_inf:.2f} cm²"))
                self._tabella_arm.setItem(row, 2, QTableWidgetItem(f"{arm.As_sup:.2f} cm²"))
                st_str = (
                    f"Ø{arm.diam_staffa_mm:.0f}/{arm.passo_staffe_cm:.0f}cm {arm.n_bracci_staffe}br"
                    if arm.diam_staffa_mm > 0
                    else "—"
                )
                self._tabella_arm.setItem(row, 3, QTableWidgetItem(st_str))

    # ------------------------------------------------------------------
    # CALCOLO
    # ------------------------------------------------------------------

    def _valida_modello(self) -> bool:
        if len(self._modello.nodi) < 2:
            QMessageBox.warning(self, "Modello incompleto", "Il telaio deve avere almeno 2 nodi.")
            return False
        if len(self._modello.aste) < 1:
            QMessageBox.warning(self, "Modello incompleto", "Il telaio deve avere almeno 1 asta.")
            return False
        return True

    def _esegui_calcolo(self) -> None:
        if not self._valida_modello():
            return
        try:
            self._statusbar.showMessage("Calcolo in corso...")
            # LC1: solo peso proprio
            ris_lc1 = calcola_caso_carico(
                modello=self._modello,
                id_caso="LC1",
                descrizione="G — Peso proprio",
            )
            # LC2: G + Q (Q = carichi variabili su aste)
            ris_lc2 = calcola_caso_carico(
                modello=self._modello,
                id_caso="LC2",
                descrizione="G + Q — Permanente + variabile",
            )
            self._risultati_per_caso = {"LC1": ris_lc1, "LC2": ris_lc2}
            self._dati_cross_per_caso = {
                "LC1": ris_lc1.dati_cross,
                "LC2": ris_lc2.dati_cross,
            }
            n_iter = ris_lc2.dati_cross.n_iterazioni
            conv = "✅" if ris_lc2.dati_cross.convergenza else "❌"
            self._statusbar.showMessage(
                f"Calcolo completato — {n_iter} iterazioni Cross (LC2) {conv}"
            )
            self._canvas.aggiorna()
        except Exception as e:
            QMessageBox.critical(self, "Errore calcolo", str(e))
            self._statusbar.showMessage(f"Errore: {e}")

    def _esegui_calcolo_completo(self) -> None:
        if not self._valida_modello():
            return
        try:
            self._statusbar.showMessage("Calcolo completo in corso (tutte le combinazioni)...")
            ris_comb = calcola_tutte_le_combinazioni(
                modello=self._modello,
                zona_sismica=self._modello.zona_sismica,
            )
            self._risultati_per_caso = ris_comb.risultati_per_caso
            self._dati_cross_per_caso = {
                k: v.dati_cross for k, v in ris_comb.risultati_per_caso.items()
            }
            self._inviluppo = ris_comb.inviluppo
            n_combo = len(self._risultati_per_caso)
            self._statusbar.showMessage(
                f"Calcolo completato — {n_combo} combinazioni — "
                f"Inviluppo su {len(self._inviluppo)} aste"
            )
            self._canvas.aggiorna()
        except Exception as e:
            QMessageBox.critical(self, "Errore calcolo completo", str(e))
            self._statusbar.showMessage(f"Errore: {e}")

    # ------------------------------------------------------------------
    # ARMATURE E VERIFICHE
    # ------------------------------------------------------------------

    def _proponi_armature(self) -> None:
        if not self._inviluppo:
            QMessageBox.information(
                self,
                "Armature",
                "Esegui prima il calcolo completo (tutte le combinazioni) per ottenere l'inviluppo.",
            )
            return
        try:
            self._armature = proponi_armature_telaio(self._modello, self._inviluppo)
            self._statusbar.showMessage(f"Armature proposte per {len(self._armature)} aste")
        except Exception as e:
            QMessageBox.critical(self, "Errore armature", str(e))

    def _verifica_armature(self) -> None:
        if not self._inviluppo:
            QMessageBox.information(self, "Verifiche", "Esegui prima il calcolo completo.")
            return
        if not self._armature:
            QMessageBox.information(self, "Verifiche", "Proponi o inserisci armature prima.")
            return
        try:
            self._verifiche = verifica_completa_telaio(
                modello=self._modello,
                inviluppo=self._inviluppo,
                armature=self._armature,
            )
            n_ok = sum(1 for r in self._verifiche.values() if r.ok)
            n_tot = len(self._verifiche)
            self._statusbar.showMessage(f"Verifiche: {n_ok}/{n_tot} aste OK")
        except Exception as e:
            QMessageBox.critical(self, "Errore verifiche", str(e))

    # ------------------------------------------------------------------
    # MODALITÀ CANVAS
    # ------------------------------------------------------------------

    def _imposta_modalita(self, modalita: ModalitaCanvas) -> None:
        self._canvas.modalita = modalita
        self._act_sel.setChecked(modalita == ModalitaCanvas.SELEZIONE)
        self._act_nodo.setChecked(modalita == ModalitaCanvas.AGGIUNGI_NODO)
        self._act_asta.setChecked(modalita == ModalitaCanvas.AGGIUNGI_ASTA)
        nomi = {
            ModalitaCanvas.SELEZIONE: "Modalità: Selezione",
            ModalitaCanvas.AGGIUNGI_NODO: "Modalità: Aggiungi nodo — click sul canvas",
            ModalitaCanvas.AGGIUNGI_ASTA: "Modalità: Aggiungi asta — click su 2 nodi",
        }
        self._statusbar.showMessage(nomi[modalita])

    def _cambia_overlay(self, testo: str) -> None:
        mappa = {
            "Telaio": None,
            "Diag. M": "M",
            "Diag. V": "V",
            "Diag. N": "N",
        }
        self._canvas.imposta_overlay(mappa.get(testo))

    # ------------------------------------------------------------------
    # PIANI
    # ------------------------------------------------------------------

    def _aggiorna_piani(self) -> None:
        """Aggiorna la lista PianoTelaio dal modello."""
        quote = sorted(set(n.y for n in self._modello.nodi if n.y > 0))
        self._modello.piani = [PianoTelaio(id_piano=i + 1, quota=q) for i, q in enumerate(quote)]

    def _aggiorna_zona_sismica(self, zona: str) -> None:
        self._modello.zona_sismica = zona

    # ------------------------------------------------------------------
    # TABULATO
    # ------------------------------------------------------------------

    def _aggiorna_anteprima(self) -> None:
        if not self._risultati_per_caso:
            self._testo_tabulato.setText("Nessun risultato disponibile. Esegui prima il calcolo.")
            return
        try:
            testo = genera_tabulato_ascii(
                modello=self._modello,
                risultati_per_caso=self._risultati_per_caso,
                dati_cross_per_caso=self._dati_cross_per_caso,
                inviluppo=self._inviluppo,
                armature=self._armature if self._armature else None,
                verifiche=self._verifiche if self._verifiche else None,
            )
            self._testo_tabulato.setText(testo)
        except Exception as e:
            self._testo_tabulato.setText(f"Errore generazione tabulato: {e}")

    # ------------------------------------------------------------------
    # SALVATAGGIO / APERTURA
    # ------------------------------------------------------------------

    def _salva_modello(self) -> None:
        percorso, _ = QFileDialog.getSaveFileName(self, "Salva modello telaio", "", "JSON (*.json)")
        if percorso:
            try:
                with open(percorso, "w", encoding="utf-8") as f:
                    json.dump(self._modello.to_dict(), f, ensure_ascii=False, indent=2)
                self._statusbar.showMessage(f"Modello salvato: {percorso}")
            except Exception as e:
                QMessageBox.critical(self, "Errore salvataggio", str(e))

    def _apri_modello(self) -> None:
        percorso, _ = QFileDialog.getOpenFileName(self, "Apri modello telaio", "", "JSON (*.json)")
        if percorso:
            try:
                with open(percorso, encoding="utf-8") as f:
                    dati = json.load(f)
                self._modello = ModelloTelaio.from_dict(dati)
                # Aggiorna contatori id
                if self._modello.nodi:
                    self._id_nodo_corrente = max(n.id for n in self._modello.nodi)
                if self._modello.aste:
                    self._id_asta_corrente = max(a.id for a in self._modello.aste)
                self._aggiorna_tutto()
                self._statusbar.showMessage(f"Modello caricato: {percorso}")
            except Exception as e:
                QMessageBox.critical(self, "Errore apertura", str(e))

    def _esporta_ascii(self) -> None:
        if not self._risultati_per_caso:
            QMessageBox.information(self, "Export", "Esegui prima il calcolo.")
            return
        percorso, _ = QFileDialog.getSaveFileName(self, "Salva tabulato ASCII", "", "Testo (*.txt)")
        if percorso:
            try:
                salva_tabulato(
                    percorso=percorso,
                    modello=self._modello,
                    risultati_per_caso=self._risultati_per_caso,
                    dati_cross_per_caso=self._dati_cross_per_caso,
                    inviluppo=self._inviluppo,
                    armature=self._armature if self._armature else None,
                    verifiche=self._verifiche if self._verifiche else None,
                    formato="txt",
                )
                self._statusbar.showMessage(f"Tabulato salvato: {percorso}")
            except Exception as e:
                QMessageBox.critical(self, "Errore export", str(e))

    def _esporta_html(self) -> None:
        if not self._risultati_per_caso:
            QMessageBox.information(self, "Export HTML", "Esegui prima il calcolo.")
            return
        percorso, _ = QFileDialog.getSaveFileName(self, "Salva report HTML", "", "HTML (*.html)")
        if percorso:
            try:
                salva_tabulato(
                    percorso=percorso,
                    modello=self._modello,
                    risultati_per_caso=self._risultati_per_caso,
                    dati_cross_per_caso=self._dati_cross_per_caso,
                    inviluppo=self._inviluppo,
                    armature=self._armature if self._armature else None,
                    verifiche=self._verifiche if self._verifiche else None,
                    formato="html",
                )
                self._statusbar.showMessage(f"Report HTML salvato: {percorso}")
            except Exception as e:
                QMessageBox.critical(self, "Errore export HTML", str(e))

    def _proprieta_modello(self) -> None:
        from PyQt6.QtWidgets import QInputDialog

        nome, ok = QInputDialog.getText(self, "Nome modello", "Nome:", text=self._modello.nome)
        if ok and nome:
            self._modello.nome = nome
            self.setWindowTitle(f"Telai Piani — {nome}")

    def _mostra_info(self) -> None:
        QMessageBox.about(
            self,
            "Telai Piani — Cross-Pozzati",
            "Calcolo di telai piani in c.a.\n"
            "Metodo di Hardy Cross (1930) — adattamento Pozzati\n"
            "Norma: RD 2229/1939 — Tensioni Ammissibili (TA)\n\n"
            "Subfase L del progetto RD2229.",
        )


# ==============================================================================
# MODULE_SPEC e factory — auto-discovery da ModuleRegistry
# ==============================================================================

MODULE_SPEC = {
    "key": "telaio_rd2229",
    "name": "Telai Piani — Cross-Pozzati (RD 2229/39)",
    "description": (
        "Calcolo di telai piani in c.a. con il metodo di Cross-Pozzati. "
        "Supporta qualsiasi numero di piani e campate. "
        "Verifiche TA, progetto armature, tabulati storici Santarella."
    ),
    "category": "calcolo",
}


def create_module(master=None, **context):
    """Factory function per auto-discovery da ModuleRegistry."""
    return TelaioWindow(parent=master, **context)
