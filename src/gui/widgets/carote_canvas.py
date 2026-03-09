"""Widget Qt per visualizzazione interattiva analisi carote (FASE N).

Quattro viste selezionabili: Istogramma, Scatter, Boxplot, Barre f_ck.
Combo formulazione per selezionare la formulazione di riferimento.

Richiede: PySide6 o PyQt6 + matplotlib[backend_qt]
"""

from __future__ import annotations

from typing import Any

# Importazione opzionale Qt + matplotlib backend
try:
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure

    try:
        from PySide6.QtWidgets import (
            QComboBox,
            QHBoxLayout,
            QLabel,
            QSizePolicy,
            QVBoxLayout,
            QWidget,
        )
        _QT_AVAILABLE = True
    except ImportError:
        try:
            from PyQt6.QtWidgets import (
                QComboBox,
                QHBoxLayout,
                QLabel,
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


def _check_available() -> None:
    if not _QT_AVAILABLE or not _MPL_QT_AVAILABLE:
        raise ImportError(
            "CaroteCanvas richiede PySide6/PyQt6 e matplotlib. "
            "Installa con: pip install PySide6 matplotlib"
        )


if _QT_AVAILABLE and _MPL_QT_AVAILABLE:

    class CaroteCanvas(QWidget):
        """Widget per visualizzazione interattiva analisi carote.

        Quattro viste:
          - Istogramma + gaussiana
          - Scatter f_core vs f_is
          - Boxplot comparativo
          - Barre f_ck,is
        """

        _VISTE = ["Istogramma", "Scatter", "Boxplot", "Barre f_ck"]

        def __init__(self, parent: QWidget | None = None) -> None:
            _check_available()
            super().__init__(parent)

            self._analysis: Any = None
            self._fig = Figure(figsize=(8, 6), dpi=100)
            self._canvas = FigureCanvas(self._fig)
            self._canvas.setSizePolicy(QSizePolicy.Policy.Expanding,
                                       QSizePolicy.Policy.Expanding)

            # Controlli
            self._combo_vista = QComboBox()
            self._combo_vista.addItems(self._VISTE)
            self._combo_vista.currentIndexChanged.connect(self._ridisegna)

            self._combo_formula = QComboBox()
            self._combo_formula.currentIndexChanged.connect(self._ridisegna)

            # Layout
            ctrl_layout = QHBoxLayout()
            ctrl_layout.addWidget(QLabel("Vista:"))
            ctrl_layout.addWidget(self._combo_vista)
            ctrl_layout.addWidget(QLabel("Formulazione:"))
            ctrl_layout.addWidget(self._combo_formula)

            main_layout = QVBoxLayout(self)
            main_layout.addLayout(ctrl_layout)
            main_layout.addWidget(self._canvas)

        def aggiorna(self, analysis: Any) -> None:
            """Aggiorna l'analisi e ridisegna."""
            self._analysis = analysis
            self._combo_formula.blockSignals(True)
            self._combo_formula.clear()
            if analysis and analysis.conversions:
                self._combo_formula.addItems(sorted(analysis.conversions.keys()))
            self._combo_formula.blockSignals(False)
            self._ridisegna()

        def _ridisegna(self) -> None:
            """Ridisegna in base alla vista e formulazione selezionate."""
            self._fig.clear()
            analysis = self._analysis
            if analysis is None or not analysis.conversions:
                ax = self._fig.add_subplot(111)
                ax.text(0.5, 0.5, "Nessuna analisi", ha="center", va="center")
                self._canvas.draw()
                return

            vista = self._combo_vista.currentIndex()
            formula = self._combo_formula.currentText()

            if vista == 0:
                self._draw_istogramma(analysis, formula)
            elif vista == 1:
                self._draw_scatter(analysis, formula)
            elif vista == 2:
                self._draw_boxplot(analysis)
            else:
                self._draw_barre(analysis)

            self._canvas.draw()

        def _draw_istogramma(self, analysis: Any, formula: str) -> None:
            from src.codes.carote.plots import grafico_istogramma_gaussiana

            fig_src = grafico_istogramma_gaussiana(analysis, formula)
            self._copy_figure(fig_src)

        def _draw_scatter(self, analysis: Any, formula: str) -> None:
            from src.codes.carote.plots import grafico_scatter_conversione

            fig_src = grafico_scatter_conversione(analysis, formula)
            self._copy_figure(fig_src)

        def _draw_boxplot(self, analysis: Any) -> None:
            from src.codes.carote.plots import grafico_boxplot_comparativo

            fig_src = grafico_boxplot_comparativo(analysis)
            self._copy_figure(fig_src)

        def _draw_barre(self, analysis: Any) -> None:
            from src.codes.carote.plots import grafico_barre_fck

            fig_src = grafico_barre_fck(analysis)
            self._copy_figure(fig_src)

        def _copy_figure(self, fig_src: Figure) -> None:
            """Copia contenuto da figura sorgente a self._fig."""
            import io
            import pickle

            # Metodo robusto: salva/carica via pickle buffer
            buf = io.BytesIO()
            pickle.dump(fig_src, buf)
            buf.seek(0)
            fig_copy = pickle.load(buf)  # noqa: S301

            self._fig.clear()
            for ax_src in fig_copy.axes:
                ax_dst = self._fig.add_subplot(111)
                ax_dst.set_title(ax_src.get_title())
                ax_dst.set_xlabel(ax_src.get_xlabel())
                ax_dst.set_ylabel(ax_src.get_ylabel())
                for line in ax_src.get_lines():
                    ax_dst.plot(line.get_xdata(), line.get_ydata(),
                                color=line.get_color(), linewidth=line.get_linewidth(),
                                linestyle=line.get_linestyle(), label=line.get_label())
                break  # Solo primo axes

        def salva(self, percorso: str, dpi: int = 150) -> None:
            """Salva la figura corrente su file."""
            self._fig.savefig(percorso, dpi=dpi, bbox_inches="tight")
