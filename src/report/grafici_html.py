"""Integrazione grafici matplotlib nel sistema di tabulati HTML.

Converte figure matplotlib in immagini base64 embedded nei report HTML,
compatibili con TabulatoCalcolo.come_html() di src/report/tabulati_calcolo.py.
"""

from __future__ import annotations

import base64
import io
from typing import Any


def figura_a_base64(fig: Any, formato: str = "png", dpi: int = 120) -> str:
    """Converte una Figure matplotlib in stringa data-URI base64.

    Parametri
    ---------
    fig : matplotlib.figure.Figure
        Figura da convertire.
    formato : str
        Formato immagine: "png" | "svg".
    dpi : int
        Risoluzione in DPI (ignorata per SVG).

    Ritorna
    -------
    str
        Stringa data-URI: ``data:image/png;base64,...``
        pronta per embedding in un attributo HTML src.
    """
    buf = io.BytesIO()
    if formato == "svg":
        fig.savefig(buf, format="svg", bbox_inches="tight")
        mime = "image/svg+xml"
    else:
        fig.savefig(buf, format="png", dpi=dpi, bbox_inches="tight")
        mime = "image/png"
    buf.seek(0)
    dati = base64.b64encode(buf.read()).decode("utf-8")
    return f"data:{mime};base64,{dati}"


def html_grafico(
    fig: Any,
    titolo: str = "",
    formato: str = "png",
    dpi: int = 120,
    larghezza: str = "100%",
) -> str:
    """Genera un blocco HTML con il grafico incorporato come immagine base64.

    Parametri
    ---------
    fig : matplotlib.figure.Figure
        Figura da inserire.
    titolo : str
        Titolo del grafico (visualizzato sopra l'immagine).
    formato : str
        Formato immagine: "png" | "svg".
    dpi : int
        Risoluzione in DPI (solo PNG).
    larghezza : str
        Larghezza CSS dell'immagine (es. "100%", "800px").

    Ritorna
    -------
    str
        Blocco HTML ``<figure>...</figure>`` pronto per l'inserimento nel report.
    """
    src = figura_a_base64(fig, formato=formato, dpi=dpi)
    titolo_html = (
        f"<p style='font-weight:bold;margin:4px 0;font-family:monospace'>{titolo}</p>"
        if titolo
        else ""
    )
    return (
        f"<figure style='margin:16px 0;text-align:center;page-break-inside:avoid'>"
        f"{titolo_html}"
        f"<img src='{src}' style='max-width:{larghezza};height:auto;"
        f"border:1px solid #ccc;border-radius:3px'>"
        f"</figure>"
    )


def aggiungi_grafico_a_tabulato(
    tabulato_html: str,
    fig: Any,
    titolo: str = "",
    posizione: str = "fine",
    formato: str = "png",
    dpi: int = 120,
) -> str:
    """Inserisce un blocco grafico in un tabulato HTML esistente.

    Parametri
    ---------
    tabulato_html : str
        HTML prodotto da TabulatoCalcolo.come_html().
    fig : matplotlib.figure.Figure
        Figura da inserire.
    titolo : str
        Titolo del grafico.
    posizione : str
        "fine" → inserisce prima di ``</body>``.
        "inizio" → inserisce subito dopo il tag ``<body...>``.
    formato : str
        Formato immagine: "png" | "svg".
    dpi : int
        Risoluzione in DPI (solo PNG).

    Ritorna
    -------
    str
        Tabulato HTML con il grafico inserito.
    """
    blocco = html_grafico(fig, titolo=titolo, formato=formato, dpi=dpi)

    if posizione == "inizio" and "<body" in tabulato_html:
        idx_body = tabulato_html.index("<body")
        idx_chiusura = tabulato_html.index(">", idx_body) + 1
        return tabulato_html[:idx_chiusura] + "\n" + blocco + tabulato_html[idx_chiusura:]

    if "</body>" in tabulato_html:
        return tabulato_html.replace("</body>", blocco + "\n</body>", 1)

    # Fallback: appende alla fine del documento
    return tabulato_html + "\n" + blocco
