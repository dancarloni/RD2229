"""Tipi, dataclass e sezione omogenizzata biassiale (FASE J).

Fornisce:
  - PressoflessSpec: input verifica pressoflessione deviata
  - PressoflessResult: output verifica
  - DominioNMy: dominio 3D N-Mx-My
  - calcola_omogenizzata_biassiale(): A_om, I_x_om, I_y_om, I_xy_om, Wx, Wy
  - crea_armatura_rettangolare(): helper per layout barre con coordinate (x, y)

Unita': cm (geometria), kg/cm² (tensioni), kg (forze), kg·cm (momenti).
"""

from __future__ import annotations

import math
import uuid
from dataclasses import dataclass, field
from typing import Any

from src.codes.section_params.omogenizzata import BarraArmatura

# ---------------------------------------------------------------------------
# Dataclass di input/output
# ---------------------------------------------------------------------------

@dataclass
class PressoflessSpec:
    """Input per verifica pressoflessione deviata multinorma."""

    section: Any              # duck-typed (section_type + attributi geometrici)
    barre: list[BarraArmatura]
    N_kg: float               # sforzo normale [kg], positivo = compressione
    Mx_kgcm: float            # momento attorno asse x [kg·cm]
    My_kgcm: float            # momento attorno asse y [kg·cm]
    sigma_c_adm_kgcm2: float  # tensione ammissibile cls [kg/cm²] (TA)
    sigma_s_adm_kgcm2: float = 0.0  # tensione ammissibile acciaio [kg/cm²]
    n: float = 15.0           # rapporto di omogeneizzazione
    norma: str = "RD2229"
    metodo: str = "SOVRAPPOSIZIONE_ELASTICA"  # | "BRESLER_TA"
    alpha_bresler: float = 1.0  # esponente Bresler (1.0 TA, 4/3 Giangreco)
    # Instabilita' (opzionale)
    amplifica_instabilita: bool = False
    l0_x_cm: float | None = None
    l0_y_cm: float | None = None
    E_c_kgcm2: float = 250000.0
    # SLU (per NTC2018/NTC2008/EC2)
    f_ck_MPa: float | None = None
    f_yk_MPa: float | None = None


@dataclass
class DominioNMy:
    """Dominio di interazione 3D N-Mx-My."""

    N_levels_kg: list[float]
    theta_rad: list[float]
    Mx_Rd_kgcm: list[list[float]]   # shape (n_N, n_theta)
    My_Rd_kgcm: list[list[float]]   # shape (n_N, n_theta)
    metodo: str                      # "TA_ELASTICO" | "SLU_BRESLER"
    norma: str


@dataclass
class PressoflessResult:
    """Risultato verifica pressoflessione deviata."""

    esito: str          # "OK" | "NON_OK"
    utilisation: float
    metodo: str         # "SOVRAPPOSIZIONE_ELASTICA" | "BRESLER_TA" | "BRESLER_SLU"
    norma: str
    # TA
    sigma_c_max_kgcm2: float | None = None
    sigma_c_adm_kgcm2: float | None = None
    # Bresler
    bresler_value: float | None = None
    alpha_bresler: float | None = None
    M_Rdx_kgcm: float | None = None
    M_Rdy_kgcm: float | None = None
    # Instabilita'
    omega_x: float | None = None
    omega_y: float | None = None
    Mx_amplificato_kgcm: float | None = None
    My_amplificato_kgcm: float | None = None
    # Dominio
    dominio: DominioNMy | None = None
    # Contratto standard
    norm_references: list = field(default_factory=list)
    decision_log: list = field(default_factory=list)
    passaggi_calcolo: list[str] = field(default_factory=list)
    details: dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Helper armatura
# ---------------------------------------------------------------------------

def crea_armatura_rettangolare(
    b_cm: float,
    h_cm: float,
    copriferro_cm: float,
    n_barre_inf: int,
    diam_inf_mm: float,
    n_barre_sup: int = 0,
    diam_sup_mm: float = 0.0,
) -> list[BarraArmatura]:
    """Genera layout barre con coordinate (x, y) reali per sezione rettangolare.

    Le barre sono distribuite uniformemente nella larghezza, centrate su x=0.
    y = 0 al lembo superiore compresso.

    Args:
        b_cm: larghezza sezione [cm]
        h_cm: altezza sezione [cm]
        copriferro_cm: copriferro al baricentro barre [cm]
        n_barre_inf: numero barre inferiori (tese)
        diam_inf_mm: diametro barre inferiori [mm]
        n_barre_sup: numero barre superiori (compresse)
        diam_sup_mm: diametro barre superiori [mm]

    Returns:
        Lista BarraArmatura con coordinate (x, y) per ogni barra.
    """
    barre: list[BarraArmatura] = []
    A_bar_inf = math.pi * (diam_inf_mm / 10.0) ** 2 / 4.0  # cm²

    y_inf = h_cm - copriferro_cm
    if n_barre_inf > 0:
        if n_barre_inf == 1:
            barre.append(BarraArmatura(y=y_inf, A=A_bar_inf, zona="tesa", x=0.0))
        else:
            x_min = -b_cm / 2.0 + copriferro_cm
            x_max = b_cm / 2.0 - copriferro_cm
            passo = (x_max - x_min) / (n_barre_inf - 1)
            for i in range(n_barre_inf):
                x_i = x_min + i * passo
                barre.append(BarraArmatura(y=y_inf, A=A_bar_inf, zona="tesa", x=x_i))

    if n_barre_sup > 0 and diam_sup_mm > 0:
        A_bar_sup = math.pi * (diam_sup_mm / 10.0) ** 2 / 4.0
        y_sup = copriferro_cm
        if n_barre_sup == 1:
            barre.append(BarraArmatura(y=y_sup, A=A_bar_sup, zona="compressa", x=0.0))
        else:
            x_min = -b_cm / 2.0 + copriferro_cm
            x_max = b_cm / 2.0 - copriferro_cm
            passo = (x_max - x_min) / (n_barre_sup - 1)
            for i in range(n_barre_sup):
                x_i = x_min + i * passo
                barre.append(BarraArmatura(y=y_sup, A=A_bar_sup, zona="compressa", x=x_i))

    return barre


# ---------------------------------------------------------------------------
# Sezione omogenizzata biassiale
# ---------------------------------------------------------------------------

def _width_at(section: Any, y: float) -> float:
    from src.methods.section_fiber import width_at_depth
    return width_at_depth(section, y)


def _get_height(section: Any) -> float:
    from src.methods.section_fiber import get_section_height
    return get_section_height(section)


def _get_width(section: Any) -> float:
    from src.methods.section_fiber import get_section_width
    return get_section_width(section)


def calcola_omogenizzata_biassiale(
    section: Any,
    barre: list[BarraArmatura],
    n: float,
    n_strips: int = 400,
) -> dict[str, Any]:
    """Calcola proprieta' sezione omogenizzata per flessione biassiale.

    Estende FASE I alla direzione y (orizzontale).

    Formule (sezioni simmetriche rispetto all'asse verticale):
        I_y_c = integrate_0^h [b(y)^3 / 12] dy
        I_y_om = I_y_c + (n-1) * sum(A_si * x_i^2)
        I_xy_om = (n-1) * sum(A_si * (x_i - x_G) * (y_i - y_G_om))

    Per I_x_om riusa la stessa logica di FASE I (integrazione verticale).

    Args:
        section: oggetto sezione (duck-typed)
        barre: lista livelli di armatura (con campo x per biassiale)
        n: rapporto di omogeneizzazione
        n_strips: strisce per integrazione numerica

    Returns:
        dict con A_om, y_G_om, I_x_om, I_y_om, I_xy_om,
        Wx_sup, Wx_inf, Wy_sx, Wy_dx, h, w.
    """
    result: dict[str, Any] = {
        "esito": "OK",
        "norm_references": [],
        "decision_log": [],
        "trace": {"run_id": str(uuid.uuid4())},
    }
    log = result["decision_log"]

    h = _get_height(section)
    w = _get_width(section)
    dy = h / n_strips

    # --- Integrazione cls: A_c, y_G_c, I_x_c, I_y_c ---
    A_c = 0.0
    Q_c = 0.0
    I_y_c = 0.0  # momento d'inerzia rispetto all'asse verticale

    for i in range(n_strips):
        y_mid = (i + 0.5) * dy
        b = _width_at(section, y_mid)
        dA = b * dy
        A_c += dA
        Q_c += dA * y_mid
        # Contributo alla I_y: ∫x² dA = b³/12 * dy (sezione simmetrica centrata)
        I_y_c += (b ** 3 / 12.0) * dy

    if A_c <= 0.0:
        result["esito"] = "ERRORE"
        log.append("Area sezione nulla")
        return result

    y_G_c = Q_c / A_c

    # I_x_c baricentrico
    I_x_c = 0.0
    for i in range(n_strips):
        y_mid = (i + 0.5) * dy
        b = _width_at(section, y_mid)
        I_x_c += b * dy * (y_mid - y_G_c) ** 2

    # --- Sezione omogenizzata ---
    sum_As = sum(bar.A for bar in barre)
    sum_As_y = sum(bar.A * bar.y for bar in barre)

    A_om = A_c + (n - 1.0) * sum_As
    if A_om <= 0.0:
        result["esito"] = "ERRORE"
        log.append("Area omogenizzata nulla")
        return result

    y_G_om = (A_c * y_G_c + (n - 1.0) * sum_As_y) / A_om
    # x_G_om = 0 per sezioni simmetriche + barre distribuite simmetricamente
    sum_As_x = sum(bar.A * bar.x for bar in barre)
    x_G_om = (n - 1.0) * sum_As_x / A_om  # cls centrata su x=0

    # I_x omogenizzata (attorno asse x passante per y_G_om)
    I_x_om = (
        I_x_c
        + A_c * (y_G_c - y_G_om) ** 2
        + (n - 1.0) * sum(bar.A * (bar.y - y_G_om) ** 2 for bar in barre)
    )

    # I_y omogenizzata (attorno asse y passante per x_G_om)
    I_y_om = (
        I_y_c
        + A_c * (0.0 - x_G_om) ** 2  # cls centrata su x=0
        + (n - 1.0) * sum(bar.A * (bar.x - x_G_om) ** 2 for bar in barre)
    )

    # I_xy (prodotto d'inerzia) — 0 per sezioni + armature simmetriche
    # Per il cls simmetrico: I_xy_c = 0
    I_xy_om = (n - 1.0) * sum(
        bar.A * (bar.x - x_G_om) * (bar.y - y_G_om) for bar in barre
    )

    # Moduli resistenti
    y_sup = y_G_om
    y_inf = h - y_G_om
    Wx_sup = I_x_om / y_sup if y_sup > 1e-9 else 0.0
    Wx_inf = I_x_om / y_inf if y_inf > 1e-9 else 0.0

    x_sx = w / 2.0 + x_G_om   # distanza dal baricentro al lembo sinistro
    x_dx = w / 2.0 - x_G_om   # distanza dal baricentro al lembo destro
    Wy_sx = I_y_om / x_sx if x_sx > 1e-9 else 0.0
    Wy_dx = I_y_om / x_dx if x_dx > 1e-9 else 0.0

    log.append(
        f"Biassiale: A_om={A_om:.2f}, y_G={y_G_om:.4f}, x_G={x_G_om:.4f}, "
        f"I_x={I_x_om:.2f}, I_y={I_y_om:.2f}, I_xy={I_xy_om:.2f}"
    )

    result.update({
        "A_om_cm2": round(A_om, 4),
        "y_G_om_cm": round(y_G_om, 6),
        "x_G_om_cm": round(x_G_om, 6),
        "I_x_om_cm4": round(I_x_om, 4),
        "I_y_om_cm4": round(I_y_om, 4),
        "I_xy_om_cm4": round(I_xy_om, 4),
        "Wx_sup_cm3": round(Wx_sup, 4),
        "Wx_inf_cm3": round(Wx_inf, 4),
        "Wy_sx_cm3": round(Wy_sx, 4),
        "Wy_dx_cm3": round(Wy_dx, 4),
        "h_cm": round(h, 4),
        "w_cm": round(w, 4),
        "n": n,
    })
    return result
