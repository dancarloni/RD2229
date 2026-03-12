"""Widget Qt per la visualizzazione interattiva degli spostamenti v(x) e u(x).

Supporta:
- Caricamento di un DiagrammaSpostamenti
- Fattore di scala visivo (deformata amplificata)
- Export PNG/SVG

Richiede: PySide6 o PyQt6 + matplotlib[backend_qt]
"""

from __future__ import annotations

try:
    from matplotlib.backends.backend_qtagg import (
        FigureCanvasQTAgg as FigureCanvas,
        NavigationToolbar2QT as NavigationToolbar,
    )
    from matplotlib.figure import Figure

    try:
        from PySide6.QtWidgets import (
            QDoubleSpinBox,
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
                QDoubleSpinBox,
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

from src.grafici.spostamenti import DiagrammaSpostamenti, grafico_spostamenti
from src.gui.widgets._export_mixin import ExportMixin


def _check_disponibile() -> None:
    if not _QT_AVAILABLE or not _MPL_QT_AVAILABLE:
        raise ImportError(
            "SpostamentiCanvas richiede PySide6/PyQt6 e matplotlib. "
            "Installa con: pip install PySide6 matplotlib"
        )


if _QT_AVAILABLE and _MPL_QT_AVAILABLE:

    class SpostamentiCanvas(ExportMixin, QWidget):
        """Widget Qt per visualizzare v(x) e u(x) in modo interattivo.

        Permette di:
        - Caricare un DiagrammaSpostamenti
        - Regolare il fattore di scala (visualizzazione deformata amplificata)
        - Esportare in PNG o SVG
        """

        def __init__(self, parent=None) -> None:
            _check_disponibile()
            super().__init__(parent)

            self._diagramma: DiagrammaSpostamenti | None = None
            self._costruisci_ui()

        def _costruisci_ui(self) -> None:
            layout = QVBoxLayout(self)

            # --- Barra controlli ---
            barra = QHBoxLayout()
            barra.addWidget(QLabel("Scala visualizzazione:"))

            self._spin_scala = QDoubleSpinBox()
            self._spin_scala.setRange(0.1, 10000.0)
            self._spin_scala.setValue(1.0)
            self._spin_scala.setSingleStep(1.0)
            self._spin_scala.setSuffix(" ×")
            self._spin_scala.setDecimals(1)
            self._spin_scala.valueChanged.connect(self._ridisegna)
            barra.addWidget(self._spin_scala)

            barra.addStretch()

            btn_export = QPushButton("Esporta…")
            btn_export.clicked.connect(self._dialogo_esporta)
            barra.addWidget(btn_export)

            layout.addLayout(barra)

            # --- Canvas matplotlib ---
            self._fig = Figure(figsize=(10, 6), tight_layout=True)
            self._canvas = FigureCanvas(self._fig)
            self._canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            layout.addWidget(self._canvas)

            # --- Toolbar navigazione ---
            self._toolbar = NavigationToolbar(self._canvas, self)
            layout.addWidget(self._toolbar)

        def aggiorna(self, diagramma: DiagrammaSpostamenti) -> None:
            """Carica un DiagrammaSpostamenti e ridisegna."""
            self._diagramma = diagramma
            self._ridisegna()

        def _ridisegna(self) -> None:
            self._fig.clear()

            if self._diagramma is None:
                ax = self._fig.add_subplot(111)
                ax.text(0.5, 0.5, "Nessun diagramma caricato", ha="center", va="center")
                self._canvas.draw()
                return

            scala = self._spin_scala.value()
            ax_v = self._fig.add_subplot(2, 1, 1)
            ax_u = self._fig.add_subplot(2, 1, 2, sharex=ax_v)
            grafico_spostamenti(self._diagramma, ax_v=ax_v, ax_u=ax_u, fig=self._fig, scala=scala)
            self._canvas.draw()

        def _dialogo_esporta(self) -> None:
            percorso, filtro = QFileDialog.getSaveFileName(
                self,
                "Esporta diagramma spostamenti",
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

    class SpostamentiCanvas:  # type: ignore[no-redef]
        """Stub usato quando PySide6/matplotlib non sono disponibili."""

        def __init__(self, *args, **kwargs) -> None:
            raise ImportError("SpostamentiCanvas richiede PySide6/PyQt6 e matplotlib.")
