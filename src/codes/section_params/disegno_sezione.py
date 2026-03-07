"""Disegno sezione in c.a. con matplotlib (FASE I).

Genera figure matplotlib con:
  - Profilo sezione (contorno poligonale)
  - Barre di armatura (cerchi)
  - Asse neutro (linea orizzontale tratteggiata)
  - Zone di tensione (campiture)
  - Diagramma tensioni (triangolare/trapezoidale laterale)
  - Risultanti N e M (frecce con annotazioni)
  - Legenda con n, sigma_c_max, sigma_s_max

Usa matplotlib puro (nessun import Qt). Per l'integrazione Qt
vedi src/gui/widgets/sezione_canvas.py.

Unita' di input: cm (geometria), kg/cm² (tensioni).
"""

from __future__ import annotations

from typing import Any

import numpy as np

# Importazione lazy di matplotlib per evitare problemi in ambienti headless
try:
    import matplotlib.patches as mpatches
    import matplotlib.pyplot as plt
    from matplotlib.figure import Figure
    _HAS_MPL = True
except ImportError:  # pragma: no cover
    _HAS_MPL = False
    Figure = None


def _section_outline_xy(
    section: Any,
    n_strips: int = 300,
) -> tuple[list[float], list[float]]:
    """Restituisce le coordinate (x, y_flipped) del profilo sezione.

    y_flipped: asse y con 0 in basso (convenzione grafica),
               cioe' y_grafic = h - y_calc dove y_calc e' misurato
               dal lembo superiore compresso.
    """
    from src.methods.section_fiber import get_section_height, width_at_depth

    h = get_section_height(section)
    dy = h / n_strips
    x_left: list[float] = []
    x_right: list[float] = []
    y_pts: list[float] = []

    for i in range(n_strips + 1):
        y_c = i * dy
        b = width_at_depth(section, y_c)
        y_g = h - y_c  # flip: y=0 in basso
        cx = 0.0  # sezione centrata su x=0
        half = b / 2.0
        x_left.append(cx - half)
        x_right.append(cx + half)
        y_pts.append(y_g)

    # Profilo chiuso: lato sinistro + lato destro invertito
    xs = x_left + x_right[::-1] + [x_left[0]]
    ys = y_pts + y_pts[::-1] + [y_pts[0]]
    return xs, ys


def disegna_sezione(
    section: Any,
    barre: list[Any],                   # lista BarraArmatura
    *,
    y_na: float | None = None,          # asse neutro dal lembo compresso [cm]
    sigma_c_max: float | None = None,   # tensione max cls [kg/cm²]
    barre_sigma: list[dict] | None = None,  # output calcola_tensioni_sle
    n: float | None = None,
    titolo: str = "Sezione in c.a.",
    mostra_legenda: bool = True,
    diam_barra_cm: float = 1.2,
    figsize: tuple[float, float] = (10.0, 7.0),
) -> "Figure":
    """Genera una figura matplotlib con il disegno della sezione in c.a.

    Args:
        section:     oggetto sezione (duck-typed)
        barre:       lista BarraArmatura (y, A)
        y_na:        posizione asse neutro dal lembo compresso [cm]
        sigma_c_max: tensione massima cls [kg/cm²]
        barre_sigma: lista da calcola_tensioni_sle (sigma_s per barra)
        n:           rapporto di omogeneizzazione
        titolo:      titolo figura
        mostra_legenda: aggiunge legenda
        diam_barra_cm: diametro grafico barre [cm]
        figsize:     dimensioni figura (larghezza, altezza) in pollici

    Returns:
        matplotlib Figure (pronta per save o embed in Qt).
    """
    if not _HAS_MPL:
        raise ImportError("matplotlib non disponibile; installa con: pip install matplotlib")

    from src.methods.section_fiber import get_section_height, width_at_depth

    h = get_section_height(section)

    fig, axes = plt.subplots(1, 2, figsize=figsize, gridspec_kw={"width_ratios": [2, 1]})
    ax_sez = axes[0]
    ax_stress = axes[1]

    fig.suptitle(titolo, fontsize=12, fontweight="bold")

    # --- Profilo sezione ---
    xs, ys = _section_outline_xy(section)
    ax_sez.fill(xs, ys, color="#E8E8E8", linewidth=1.5)
    ax_sez.plot(xs, ys, color="#333333", linewidth=1.5)

    # --- Zona compressa (campita se y_na noto) ---
    if y_na is not None:
        n_c = 200
        dy_c = y_na / max(n_c, 1)
        x_comp_l: list[float] = []
        x_comp_r: list[float] = []
        y_comp: list[float] = []
        for i in range(n_c + 1):
            y_calc = i * dy_c
            if y_calc > y_na:
                y_calc = y_na
            b = width_at_depth(section, y_calc)
            y_g = h - y_calc
            x_comp_l.append(-b / 2.0)
            x_comp_r.append(b / 2.0)
            y_comp.append(y_g)
        xs_c = x_comp_l + x_comp_r[::-1] + [x_comp_l[0]]
        ys_c = y_comp + y_comp[::-1] + [y_comp[0]]
        ax_sez.fill(xs_c, ys_c, color="#A8C4E0", alpha=0.6, label="Zona compressa")

    # --- Barre di armatura ---
    sigma_map: dict[float, float] = {}
    if barre_sigma:
        for bs in barre_sigma:
            sigma_map[bs["y_cm"]] = bs["sigma_s_kgcm2"]

    from math import pi, sqrt
    for bar in barre:
        y_g = h - bar.y  # flip
        r_bar = sqrt(bar.A / pi)  # raggio equivalente
        r_plot = max(diam_barra_cm / 2.0, r_bar)
        sigma_s = sigma_map.get(bar.y, None)
        color = "#CC0000" if (sigma_s is not None and sigma_s > 0) else "#0044CC"
        circle = mpatches.Circle((0.0, y_g), r_plot, color=color, zorder=5)
        ax_sez.add_patch(circle)

    # --- Asse neutro ---
    if y_na is not None:
        y_na_g = h - y_na
        max_hw = max(abs(x) for x in xs) * 1.2
        ax_sez.axhline(y=y_na_g, color="#FF6600", linestyle="--", linewidth=1.5,
                       label=f"Asse neutro (y_na={y_na:.2f} cm)")

    # Assi e etichette sezione
    ax_sez.set_aspect("equal")
    ax_sez.set_xlabel("x [cm]")
    ax_sez.set_ylabel("y [cm]")
    ax_sez.set_title("Sezione")
    if mostra_legenda:
        ax_sez.legend(fontsize=8, loc="upper right")

    # --- Diagramma tensioni ---
    if sigma_c_max is not None and y_na is not None:
        _disegna_diagramma_tensioni(
            ax_stress, h, y_na, sigma_c_max, barre, barre_sigma, n
        )
    else:
        ax_stress.set_visible(False)

    fig.tight_layout()
    return fig


def _disegna_diagramma_tensioni(
    ax: Any,
    h: float,
    y_na: float,
    sigma_c_max: float,
    barre: list[Any],
    barre_sigma: list[dict] | None,
    n: float | None,
) -> None:
    """Disegna diagramma lineare delle tensioni sulla sezione."""
    # Asse y: 0 in basso
    y_na_g = h - y_na

    # Distribuzione lineare cls
    # Nel dominio compresso: sigma(y) = sigma_c_max * (y_na - y_calc) / y_na
    #   y_calc in [0, y_na] → y_g in [h, h-y_na]
    n_pt = 50
    y_cls = np.linspace(0.0, y_na, n_pt)
    sigma_cls = sigma_c_max * (y_na - y_cls) / y_na if y_na > 0 else np.zeros(n_pt)
    y_cls_g = h - y_cls

    # Traccia diagramma cls (positivo verso destra = compressione)
    ax.plot(sigma_cls, y_cls_g, color="#0055AA", linewidth=2)
    ax.fill_betweenx(y_cls_g, 0, sigma_cls, color="#A8C4E0", alpha=0.5, label="σ_c")

    # Asse neutro
    ax.axhline(y=y_na_g, color="#FF6600", linestyle="--", linewidth=1)

    # Tensioni nelle barre
    if barre_sigma:
        for bs in barre_sigma:
            y_g = h - bs["y_cm"]
            sigma_s = bs["sigma_s_kgcm2"]
            marker = "o" if sigma_s > 0 else "s"
            color = "#CC0000" if sigma_s > 0 else "#0055AA"
            ax.plot(sigma_s, y_g, marker=marker, color=color, markersize=8, zorder=5)
            ax.annotate(
                f"{sigma_s:.1f}",
                (sigma_s, y_g),
                textcoords="offset points",
                xytext=(5, 0),
                fontsize=7,
            )

    ax.axvline(x=0, color="black", linewidth=0.8)
    ax.set_xlim(left=min(0, ax.get_xlim()[0]) * 1.3)
    ax.set_xlabel("σ [kg/cm²]")
    ax.set_ylabel("y [cm]")
    ax.set_title("Diagramma tensioni")
    _title = []
    if sigma_c_max is not None:
        _title.append(f"σ_c_max = {sigma_c_max:.2f} kg/cm²")
    if n is not None:
        _title.append(f"n = {n}")
    if _title:
        ax.set_title("\n".join(_title), fontsize=8)

    ax.legend(fontsize=7)


def salva_figura(fig: "Figure", percorso: str, dpi: int = 150) -> None:
    """Salva la figura in un file (PNG, PDF, SVG, ...)."""
    if not _HAS_MPL:
        raise ImportError("matplotlib non disponibile")
    fig.savefig(percorso, dpi=dpi, bbox_inches="tight")
    plt.close(fig)


def crea_figura_sezione_sle(
    section: Any,
    barre: list[Any],
    dati_sle: dict[str, Any],
    *,
    norma: str = "",
    titolo: str | None = None,
    figsize: tuple[float, float] = (10.0, 7.0),
) -> "Figure":
    """Crea figura completa da output di calcola_parametri_sezione_completi.

    Args:
        section:   oggetto sezione
        barre:     lista BarraArmatura
        dati_sle:  dict restituito da calcola_parametri_sezione_completi
        norma:     codice norma (per titolo)
        titolo:    titolo personalizzato
        figsize:   dimensioni figura

    Returns:
        matplotlib Figure.
    """
    fess = dati_sle.get("fessurata", {})
    sle = dati_sle.get("tensioni_sle", {})

    y_na = fess.get("y_na_cm")
    sigma_c = sle.get("sigma_c_max_kgcm2")
    barre_sigma = sle.get("barre_sigma")
    n = fess.get("n") or dati_sle.get("integra", {}).get("n")

    _titolo = titolo or f"Sezione in c.a. — SLE {norma}".strip(" —")

    return disegna_sezione(
        section=section,
        barre=barre,
        y_na=y_na,
        sigma_c_max=sigma_c,
        barre_sigma=barre_sigma,
        n=n,
        titolo=_titolo,
        figsize=figsize,
    )
