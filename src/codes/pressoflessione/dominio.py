"""Dominio 3D N-Mx-My e visualizzazione matplotlib (FASE J).

Fornisce:
  - calcola_dominio_3d(): genera il dominio di interazione N-Mx-My
  - disegna_dominio_3d(): surface plot 3D con mplot3d
  - disegna_dominio_2d_mxmy(): curva Mx-My a N costante
  - disegna_dominio_2d_nm(): curva N-M per theta fissato

Metodo TA analitico (chiuso):
  M_Rd(N, theta) = 1 / (|cos(theta)|/M_Rdx + |sin(theta)|/M_Rdy)  [alpha=1]
  Generalizzato: (|cos|/M_Rdx)^alpha + (|sin|/M_Rdy)^alpha = (1/M_Rd)^alpha

Metodo SLU: parametrico Bresler da M_Rdx(N) e M_Rdy(N) uniassiali.

Unita': cm, kg/cm², kg, kg·cm.
"""

from __future__ import annotations

import math
from typing import Any

import numpy as np

from .base import DominioNMy, PressoflessSpec, calcola_omogenizzata_biassiale
from .ta_cls import calcola_M_Rd_ta


def _m_rd_bresler(
    M_Rdx: float,
    M_Rdy: float,
    theta: float,
    alpha: float,
) -> float:
    """Calcola M_Rd in direzione theta con formula di Bresler.

    Risolve: (M_Rd*|cos(theta)|/M_Rdx)^alpha + (M_Rd*|sin(theta)|/M_Rdy)^alpha = 1
    -> M_Rd = 1 / ((|cos|/M_Rdx)^alpha + (|sin|/M_Rdy)^alpha)^(1/alpha)
    """
    ct = abs(math.cos(theta))
    st = abs(math.sin(theta))

    if M_Rdx <= 0 and M_Rdy <= 0:
        return 0.0

    # Casi degeneri
    if ct < 1e-12:
        return M_Rdy if M_Rdy > 0 else 0.0
    if st < 1e-12:
        return M_Rdx if M_Rdx > 0 else 0.0

    if M_Rdx <= 0 or M_Rdy <= 0:
        return 0.0

    term = (ct / M_Rdx) ** alpha + (st / M_Rdy) ** alpha
    if term <= 0:
        return 0.0
    return 1.0 / term ** (1.0 / alpha)


def calcola_dominio_3d(
    spec: PressoflessSpec,
    n_N: int = 16,
    n_theta: int = 36,
    N_min_kg: float | None = None,
    N_max_kg: float | None = None,
) -> DominioNMy:
    """Genera il dominio di interazione 3D N-Mx-My.

    Per ogni livello di N e per ogni theta, calcola M_Rd con Bresler.

    TA: M_Rdx(N) e M_Rdy(N) analitici da (sigma_adm - N/A_om) * W.
    SLU: stub — restituisce M_Rdx = M_Rdy = 0 (da implementare con fiber).

    Args:
        spec: input pressoflessione deviata
        n_N: numero livelli di N
        n_theta: numero angoli theta in [0, 2*pi]
        N_min_kg: sforzo normale minimo (default: 0)
        N_max_kg: sforzo normale massimo (default: sigma_c_adm * A_om)

    Returns:
        DominioNMy con griglie Mx_Rd, My_Rd.
    """
    props = calcola_omogenizzata_biassiale(spec.section, spec.barre, spec.n)
    if props.get("esito") != "OK":
        return DominioNMy(
            N_levels_kg=[],
            theta_rad=[],
            Mx_Rd_kgcm=[],
            My_Rd_kgcm=[],
            metodo="TA_ELASTICO",
            norma=spec.norma,
        )

    A_om = props["A_om_cm2"]
    Wx = min(props["Wx_sup_cm3"], props["Wx_inf_cm3"])
    Wy = min(props["Wy_sx_cm3"], props["Wy_dx_cm3"])
    sigma_adm = spec.sigma_c_adm_kgcm2
    alpha = spec.alpha_bresler

    if N_min_kg is None:
        N_min_kg = 0.0
    if N_max_kg is None:
        N_max_kg = sigma_adm * A_om

    N_levels = np.linspace(N_min_kg, N_max_kg, n_N).tolist()
    theta_list = np.linspace(0.0, 2.0 * math.pi, n_theta, endpoint=False).tolist()

    Mx_Rd_grid: list[list[float]] = []
    My_Rd_grid: list[list[float]] = []

    for N_lev in N_levels:
        M_Rdx = calcola_M_Rd_ta(A_om, Wx, N_lev, sigma_adm)
        M_Rdy = calcola_M_Rd_ta(A_om, Wy, N_lev, sigma_adm)

        Mx_row: list[float] = []
        My_row: list[float] = []
        for theta in theta_list:
            M_Rd = _m_rd_bresler(M_Rdx, M_Rdy, theta, alpha)
            Mx_row.append(round(M_Rd * math.cos(theta), 4))
            My_row.append(round(M_Rd * math.sin(theta), 4))
        Mx_Rd_grid.append(Mx_row)
        My_Rd_grid.append(My_row)

    return DominioNMy(
        N_levels_kg=[round(n, 4) for n in N_levels],
        theta_rad=[round(t, 6) for t in theta_list],
        Mx_Rd_kgcm=Mx_Rd_grid,
        My_Rd_kgcm=My_Rd_grid,
        metodo="TA_ELASTICO",
        norma=spec.norma,
    )


# ---------------------------------------------------------------------------
# Visualizzazione matplotlib
# ---------------------------------------------------------------------------


def disegna_dominio_3d(dominio: DominioNMy, **kwargs: Any) -> Any:
    """Surface plot 3D N-Mx-My con mplot3d.

    Args:
        dominio: DominioNMy calcolato
        **kwargs: passati a plot_surface (alpha, cmap, ecc.)

    Returns:
        matplotlib.figure.Figure
    """
    import matplotlib.pyplot as plt

    Mx = np.array(dominio.Mx_Rd_kgcm)
    My = np.array(dominio.My_Rd_kgcm)
    N_levels = np.array(dominio.N_levels_kg)

    # Griglia N per ogni theta
    N_grid = np.tile(N_levels[:, np.newaxis], (1, Mx.shape[1]))

    fig = plt.figure(figsize=kwargs.pop("figsize", (10, 8)))
    ax = fig.add_subplot(111, projection="3d")

    cmap = kwargs.pop("cmap", "viridis")
    alpha = kwargs.pop("alpha", 0.7)
    ax.plot_surface(Mx, My, N_grid, cmap=cmap, alpha=alpha, **kwargs)

    ax.set_xlabel("Mx [kg·cm]")
    ax.set_ylabel("My [kg·cm]")
    ax.set_zlabel("N [kg]")
    ax.set_title(f"Dominio N-Mx-My ({dominio.norma} — {dominio.metodo})")

    return fig


def disegna_dominio_2d_mxmy(
    dominio: DominioNMy,
    N_fisso_kg: float | None = None,
    **kwargs: Any,
) -> Any:
    """Curva Mx-My a N costante (sezione del dominio 3D).

    Se N_fisso non specificato, usa il primo livello.

    Args:
        dominio: DominioNMy calcolato
        N_fisso_kg: livello N per la sezione [kg]

    Returns:
        matplotlib.figure.Figure
    """
    import matplotlib.pyplot as plt

    N_levels = dominio.N_levels_kg
    if not N_levels:
        fig, ax = plt.subplots()
        ax.text(0.5, 0.5, "Dominio vuoto", ha="center", va="center")
        return fig

    # Trova livello piu' vicino
    if N_fisso_kg is None:
        idx = 0
    else:
        idx = int(np.argmin(np.abs(np.array(N_levels) - N_fisso_kg)))

    Mx_row = dominio.Mx_Rd_kgcm[idx]
    My_row = dominio.My_Rd_kgcm[idx]
    N_val = N_levels[idx]

    # Chiudi la curva
    mx = list(Mx_row) + [Mx_row[0]]
    my = list(My_row) + [My_row[0]]

    fig, ax = plt.subplots(figsize=kwargs.pop("figsize", (8, 8)))
    ax.plot(mx, my, "b-", linewidth=1.5, label=f"N = {N_val:.0f} kg")
    ax.fill(mx, my, alpha=0.15, color="blue")
    ax.set_xlabel("Mx [kg·cm]")
    ax.set_ylabel("My [kg·cm]")
    ax.set_title(f"Dominio Mx-My a N={N_val:.0f} kg ({dominio.norma})")
    ax.legend()
    ax.set_aspect("equal")
    ax.grid(True, alpha=0.3)
    ax.axhline(0, color="k", linewidth=0.5)
    ax.axvline(0, color="k", linewidth=0.5)

    return fig


def disegna_dominio_2d_nm(
    dominio: DominioNMy,
    theta_fisso_rad: float = 0.0,
    **kwargs: Any,
) -> Any:
    """Curva N-M per theta fissato (sezione del dominio 3D).

    Args:
        dominio: DominioNMy calcolato
        theta_fisso_rad: angolo theta [rad] (0 = puro Mx)

    Returns:
        matplotlib.figure.Figure
    """
    import matplotlib.pyplot as plt

    if not dominio.N_levels_kg or not dominio.theta_rad:
        fig, ax = plt.subplots()
        ax.text(0.5, 0.5, "Dominio vuoto", ha="center", va="center")
        return fig

    # Trova theta piu' vicino
    theta_arr = np.array(dominio.theta_rad)
    j = int(np.argmin(np.abs(theta_arr - theta_fisso_rad)))
    theta_val = dominio.theta_rad[j]

    N_vals = dominio.N_levels_kg
    Mx_arr = np.array(dominio.Mx_Rd_kgcm)
    My_arr = np.array(dominio.My_Rd_kgcm)

    M_vals = [math.sqrt(Mx_arr[i, j] ** 2 + My_arr[i, j] ** 2) for i in range(len(N_vals))]

    fig, ax = plt.subplots(figsize=kwargs.pop("figsize", (8, 6)))
    ax.plot(M_vals, N_vals, "r-", linewidth=1.5, label=f"theta = {math.degrees(theta_val):.0f} deg")
    ax.fill_betweenx(N_vals, 0, M_vals, alpha=0.15, color="red")
    ax.set_xlabel("M [kg·cm]")
    ax.set_ylabel("N [kg]")
    ax.set_title(f"Dominio N-M a theta={math.degrees(theta_val):.0f} deg ({dominio.norma})")
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.axhline(0, color="k", linewidth=0.5)
    ax.axvline(0, color="k", linewidth=0.5)

    return fig
