"""Mixin per l'esportazione di figure matplotlib da widget Qt.

Aggiunge esporta_png() e esporta_svg() a qualsiasi QWidget
che abbia self._fig (matplotlib.figure.Figure).
"""

from __future__ import annotations


class ExportMixin:
    """Mixin che aggiunge export PNG/SVG a widget Qt con self._fig."""

    def esporta_png(self, percorso: str, dpi: int = 150) -> None:
        """Esporta la figura corrente in formato PNG.

        Parametri
        ---------
        percorso : str
            Percorso del file di destinazione (es. "/tmp/figura.png").
        dpi : int
            Risoluzione in DPI (default 150).
        """
        if not hasattr(self, "_fig") or self._fig is None:
            raise RuntimeError("Nessuna figura disponibile per l'export.")
        self._fig.savefig(percorso, dpi=dpi, bbox_inches="tight", format="png")

    def esporta_svg(self, percorso: str) -> None:
        """Esporta la figura corrente in formato SVG (vettoriale).

        Parametri
        ---------
        percorso : str
            Percorso del file di destinazione (es. "/tmp/figura.svg").
        """
        if not hasattr(self, "_fig") or self._fig is None:
            raise RuntimeError("Nessuna figura disponibile per l'export.")
        self._fig.savefig(percorso, bbox_inches="tight", format="svg")
