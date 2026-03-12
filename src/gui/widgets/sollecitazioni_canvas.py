"""Widget Qt per la visualizzazione interattiva dei diagrammi M/T/N.

Supporta:
- Una singola combinazione di carico
- Inviluppo di più combinazioni (busta max/min)
- Toggle combinazione / inviluppo
- Export PNG/SVG

Richiede: PySide6 o PyQt6 + matplotlib[backend_qt]
"""

from __future__ import annotations

from collections.abc import Sequence

try:
    from matplotlib.backends.backend_qtagg import (
        FigureCanvasQTAgg as FigureCanvas,
        NavigationToolbar2QT as NavigationToolbar,
    )
    from matplotlib.figure import Figure

    try:
        from PySide6.QtWidgets import (
            QCheckBox,
            QComboBox,
            QFileDialog,
            QHBoxLayout,
            QLabel,
            QPushButton,
            QSizePolicy,
            QVBoxLayout,
            QWidget,
        )

        _QT_AVAILABLE = True
    except ImportError:
        try:
            from PyQt6.QtWidgets import (
                QCheckBox,
                QComboBox,
                QFileDialog,
                QHBoxLayout,
                QLabel,
                QPushButton,
                QSizePolicy,
                QVBoxLayout,
                QWidget,
            )

            _QT_AVAILABLE = True
        except ImportError:
            _QT_AVAILABLE = False

    _MPL_QT_AVAILABLE = True
except ImportError:
    _MPL_QT_AVAILABLE = False
    _QT_AVAILABLE = False

from src.grafici.inviluppi import (
    InviluppoSollecitazioni,
    grafico_inviluppo,
    inviluppo_sollecitazioni,
)
from src.grafici.sollecitazioni import DiagrammaSollecitazioni, grafico_sollecitazioni
from src.gui.widgets._export_mixin import ExportMixin


def _check_disponibile() -> None:
    if not _QT_AVAILABLE or not _MPL_QT_AVAILABLE:
        raise ImportError(
            "SollecitazioniCanvas richiede PySide6/PyQt6 e matplotlib. "
            "Installa con: pip install PySide6 matplotlib"
        )


if _QT_AVAILABLE and _MPL_QT_AVAILABLE:

    class SollecitazioniCanvas(ExportMixin, QWidget):
        """Widget Qt per la visualizzazione interattiva dei diagrammi M/T/N.

        Carica una lista di DiagrammaSollecitazioni e permette di:
        - Visualizzare una singola combinazione tramite combo
        - Attivare la vista inviluppo (busta max/min su tutte le combinazioni)
        - Esportare in PNG o SVG
        """

        def __init__(self, parent=None) -> None:
            _check_disponibile()
            super().__init__(parent)

            self._diagrammi: list[DiagrammaSollecitazioni] = []
            self._inviluppo: InviluppoSollecitazioni | None = None
            self._costruisci_ui()

        def _costruisci_ui(self) -> None:
            layout = QVBoxLayout(self)

            # --- Barra controlli ---
            barra = QHBoxLayout()
            barra.addWidget(QLabel("Combinazione:"))

            self._combo_comb = QComboBox()
            self._combo_comb.addItem("— nessuna —")
            self._combo_comb.currentIndexChanged.connect(self._ridisegna)
            barra.addWidget(self._combo_comb)

            self._check_inviluppo = QCheckBox("Mostra inviluppo")
            self._check_inviluppo.setEnabled(False)
            self._check_inviluppo.stateChanged.connect(self._ridisegna)
            barra.addWidget(self._check_inviluppo)

            barra.addStretch()

            btn_export = QPushButton("Esporta…")
            btn_export.clicked.connect(self._dialogo_esporta)
            barra.addWidget(btn_export)

            layout.addLayout(barra)

            # --- Canvas matplotlib ---
            self._fig = Figure(figsize=(10, 8), tight_layout=True)
            self._canvas = FigureCanvas(self._fig)
            self._canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            layout.addWidget(self._canvas)

            # --- Toolbar navigazione ---
            self._toolbar = NavigationToolbar(self._canvas, self)
            layout.addWidget(self._toolbar)

        def aggiorna(self, diagrammi: Sequence[DiagrammaSollecitazioni]) -> None:
            """Carica i diagrammi e ridisegna.

            Parametri
            ---------
            diagrammi : sequenza di DiagrammaSollecitazioni
                Tutti devono condividere la stessa ascissa x_cm.
            """
            self._diagrammi = list(diagrammi)
            self._inviluppo = (
                inviluppo_sollecitazioni(self._diagrammi) if len(self._diagrammi) > 1 else None
            )

            self._combo_comb.blockSignals(True)
            self._combo_comb.clear()
            self._combo_comb.addItem("— nessuna —")
            for i, d in enumerate(self._diagrammi):
                etichetta = d.etichetta or f"Comb. {i + 1}"
                self._combo_comb.addItem(etichetta)
            self._combo_comb.blockSignals(False)

            self._check_inviluppo.setEnabled(self._inviluppo is not None)
            if self._inviluppo is None:
                self._check_inviluppo.setChecked(False)

            self._ridisegna()

        def _ridisegna(self) -> None:
            self._fig.clear()

            if not self._diagrammi:
                ax = self._fig.add_subplot(111)
                ax.text(0.5, 0.5, "Nessun diagramma caricato", ha="center", va="center")
                self._canvas.draw()
                return

            if self._check_inviluppo.isChecked() and self._inviluppo is not None:
                ax_M = self._fig.add_subplot(3, 1, 1)
                ax_T = self._fig.add_subplot(3, 1, 2, sharex=ax_M)
                ax_N = self._fig.add_subplot(3, 1, 3, sharex=ax_M)
                grafico_inviluppo(
                    self._inviluppo,
                    ax_M=ax_M,
                    ax_T=ax_T,
                    ax_N=ax_N,
                    fig=self._fig,
                    diagrammi=self._diagrammi,
                )
            else:
                idx = self._combo_comb.currentIndex() - 1  # offset per "nessuna"
                if idx < 0:
                    idx = 0
                idx = min(idx, len(self._diagrammi) - 1)
                diag = self._diagrammi[idx]
                ax_M = self._fig.add_subplot(3, 1, 1)
                ax_T = self._fig.add_subplot(3, 1, 2, sharex=ax_M)
                ax_N = self._fig.add_subplot(3, 1, 3, sharex=ax_M)
                grafico_sollecitazioni(diag, ax_M=ax_M, ax_T=ax_T, ax_N=ax_N, fig=self._fig)

            self._canvas.draw()

        def _dialogo_esporta(self) -> None:
            percorso, filtro = QFileDialog.getSaveFileName(
                self,
                "Esporta diagramma sollecitazioni",
                "",
                "PNG (*.png);;SVG (*.svg)",
            )
            if not percorso:
                return
            if filtro.startswith("SVG"):
                self.esporta_svg(percorso)
            else:
                self.esporta_png(percorso)

else:

    class SollecitazioniCanvas:  # type: ignore[no-redef]
        """Stub usato quando PySide6/matplotlib non sono disponibili."""

        def __init__(self, *args, **kwargs) -> None:
            raise ImportError("SollecitazioniCanvas richiede PySide6/PyQt6 e matplotlib.")
