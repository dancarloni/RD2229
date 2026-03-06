"""Widget Qt per anteprima in tempo reale della sezione in c.a. (FASE I).

Incorpora una figura matplotlib in un widget PySide6/PyQt6 tramite
FigureCanvasQTAgg.

Uso tipico:
    canvas = SezioneSLECanvas(parent=None)
    canvas.aggiorna(section, barre, dati_sle)

Richiede: PySide6 o PyQt6 + matplotlib[backend_qt]
"""

from __future__ import annotations

from typing import Any

# Importazione opzionale Qt + matplotlib backend
try:
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure

    try:
        from PySide6.QtWidgets import QSizePolicy, QVBoxLayout, QWidget
        _QT_AVAILABLE = True
    except ImportError:
        try:
            from PyQt6.QtWidgets import QSizePolicy, QVBoxLayout, QWidget
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
            "SezioneSLECanvas richiede PySide6 (o PyQt6) e matplotlib con backend Qt. "
            "Installa con: pip install PySide6 matplotlib"
        )


if _QT_AVAILABLE and _MPL_QT_AVAILABLE:

    class SezioneSLECanvas(QWidget):
        """Widget Qt che mostra il disegno aggiornabile della sezione c.a.

        Aggiorna il grafico in tempo reale quando cambiano i dati.
        """

        def __init__(self, parent=None) -> None:
            super().__init__(parent)
            self._fig: Figure = Figure(figsize=(10, 7))
            self._canvas = FigureCanvas(self._fig)
            self._canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

            layout = QVBoxLayout(self)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.addWidget(self._canvas)
            self.setLayout(layout)

            self._sezione: Any = None
            self._barre: list[Any] = []
            self._dati_sle: dict[str, Any] = {}

        def aggiorna(
            self,
            section: Any,
            barre: list[Any],
            dati_sle: dict[str, Any],
            *,
            norma: str = "",
            titolo: str | None = None,
        ) -> None:
            """Aggiorna il canvas con nuovi dati.

            Args:
                section:  oggetto sezione (duck-typed)
                barre:    lista BarraArmatura
                dati_sle: dict da calcola_parametri_sezione_completi
                norma:    codice norma (per titolo)
                titolo:   titolo personalizzato
            """
            self._fig.clear()
            try:
                from src.codes.section_params.disegno_sezione import (
                    crea_figura_sezione_sle,
                )
                fig_new = crea_figura_sezione_sle(
                    section, barre, dati_sle,
                    norma=norma, titolo=titolo,
                    figsize=self._fig.get_size_inches().tolist(),
                )
                # Copia gli axes nella figura interna
                self._fig.clear()
                for ax in fig_new.axes:
                    ax.figure = self._fig
                    self._fig.axes.append(ax)
                    self._fig.add_axes(ax)
                import matplotlib.pyplot as plt
                plt.close(fig_new)
            except Exception as exc:
                ax = self._fig.add_subplot(111)
                ax.text(
                    0.5, 0.5,
                    f"Errore disegno sezione:\n{exc}",
                    transform=ax.transAxes,
                    ha="center", va="center",
                    color="red", fontsize=10,
                )

            self._canvas.draw()

        def salva(self, percorso: str, dpi: int = 150) -> None:
            """Salva la figura corrente su file."""
            self._fig.savefig(percorso, dpi=dpi, bbox_inches="tight")

else:
    # Stub quando Qt non e' disponibile (es. in ambienti CI/test headless)
    class SezioneSLECanvas:  # type: ignore[no-redef]
        """Stub non-Qt: usato in ambienti senza PySide6."""

        def __init__(self, parent=None) -> None:
            _check_available()

        def aggiorna(self, *args: Any, **kwargs: Any) -> None:
            _check_available()

        def salva(self, *args: Any, **kwargs: Any) -> None:
            _check_available()
