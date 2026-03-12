"""Fase U.6 - Analisi pushover statica non lineare (base operativa)."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class CurvaPushover:
    spostamenti: np.ndarray
    tagli_base: np.ndarray
    indice_prima_plasticizzazione: int
    indice_collasso: int


def pattern_triangolare(masse: np.ndarray, altezze: np.ndarray, forza_totale: float) -> np.ndarray:
    """Distribuzione forze triangolare f_i ~ m_i * z_i."""

    m = np.asarray(masse, dtype=float)
    z = np.asarray(altezze, dtype=float)
    if len(m) != len(z):
        raise ValueError("masse e altezze devono avere stessa dimensione")
    if forza_totale < 0.0:
        raise ValueError("forza_totale deve essere >= 0")

    pesi = m * z
    somma = float(np.sum(pesi))
    if somma <= 0.0:
        raise ValueError("Somma pesi triangolare nulla")
    return forza_totale * pesi / somma


def pattern_uniforme(n_piani: int, forza_totale: float) -> np.ndarray:
    """Distribuzione forze uniforme."""

    if n_piani <= 0:
        raise ValueError("n_piani deve essere >= 1")
    if forza_totale < 0.0:
        raise ValueError("forza_totale deve essere >= 0")
    return np.full(n_piani, forza_totale / n_piani, dtype=float)


def pushover_simplificata(
    *,
    k_iniziale: float,
    delta_y: float,
    delta_u: float,
    n_step: int = 60,
    k_post_ratio: float = 0.1,
    collasso_ratio: float = 0.85,
) -> CurvaPushover:
    """Costruisce curva pushover bilineare con ramo degradato.

    - elastico fino a delta_y
    - post-elastico con pendenza k_iniziale * k_post_ratio
    - collasso quando V < collasso_ratio * V_max
    """

    if k_iniziale <= 0.0:
        raise ValueError("k_iniziale deve essere > 0")
    if not (0.0 < delta_y < delta_u):
        raise ValueError("Serve 0 < delta_y < delta_u")
    if n_step < 5:
        raise ValueError("n_step deve essere >= 5")

    delta = np.linspace(0.0, delta_u, n_step)
    v = np.zeros_like(delta)

    k_post = k_iniziale * k_post_ratio
    v_y = k_iniziale * delta_y

    for i, d in enumerate(delta):
        if d <= delta_y:
            v[i] = k_iniziale * d
        else:
            v[i] = v_y + k_post * (d - delta_y)

    # Applica softening artificiale in coda per simulare degrado avanzato
    tail_start = int(0.8 * n_step)
    for i in range(tail_start, n_step):
        fatt = 1.0 - 0.3 * ((i - tail_start) / max(1, (n_step - tail_start - 1)))
        v[i] *= fatt

    idx_y = int(np.argmax(delta >= delta_y))
    idx_vmax = int(np.argmax(v))
    v_max = float(v[idx_vmax])

    idx_collasso = n_step - 1
    for i in range(idx_vmax, n_step):
        if v[i] <= collasso_ratio * v_max:
            idx_collasso = i
            break

    return CurvaPushover(
        spostamenti=delta,
        tagli_base=v,
        indice_prima_plasticizzazione=idx_y,
        indice_collasso=idx_collasso,
    )


def calcola_alpha_u_alpha_1_da_curva(curva: CurvaPushover) -> float:
    """alpha_u/alpha_1 = V_max / V_prima_plasticizzazione."""

    v = curva.tagli_base
    v_max = float(np.max(v))
    v_1 = float(v[curva.indice_prima_plasticizzazione])
    if v_1 <= 0.0:
        raise ValueError("V alla prima plasticizzazione deve essere > 0")
    return v_max / v_1


def converti_adrs(tagli_base: np.ndarray, spostamenti_top: np.ndarray, m_eff: float, gamma_1: float, g: float = 9.81) -> tuple[np.ndarray, np.ndarray]:
    """Converte curva F-delta in Sa-Sd (ADRS)."""

    if m_eff <= 0.0 or gamma_1 <= 0.0 or g <= 0.0:
        raise ValueError("m_eff, gamma_1 e g devono essere > 0")

    v = np.asarray(tagli_base, dtype=float)
    d = np.asarray(spostamenti_top, dtype=float)
    if len(v) != len(d):
        raise ValueError("tagli_base e spostamenti_top devono avere stessa dimensione")

    sa = v / (m_eff * g)
    sd = d / gamma_1
    return sa, sd


def punto_prestazione_intersezione(sd_cap: np.ndarray, sa_cap: np.ndarray, sd_dom: np.ndarray, sa_dom: np.ndarray) -> tuple[float, float]:
    """Stima intersezione tra curva capacita e domanda su griglia comune."""

    sdc = np.asarray(sd_cap, dtype=float)
    sac = np.asarray(sa_cap, dtype=float)
    sdd = np.asarray(sd_dom, dtype=float)
    sad = np.asarray(sa_dom, dtype=float)

    sd_min = max(float(np.min(sdc)), float(np.min(sdd)))
    sd_max = min(float(np.max(sdc)), float(np.max(sdd)))
    if sd_max <= sd_min:
        raise ValueError("Intervallo Sd comune nullo")

    grid = np.linspace(sd_min, sd_max, 400)
    cap_i = np.interp(grid, sdc, sac)
    dom_i = np.interp(grid, sdd, sad)
    diff = cap_i - dom_i

    sign = np.sign(diff)
    chg = np.where(np.diff(sign) != 0)[0]
    if len(chg) == 0:
        idx = int(np.argmin(np.abs(diff)))
        return float(grid[idx]), float(cap_i[idx])

    i = int(chg[0])
    return float(grid[i]), float(cap_i[i])
