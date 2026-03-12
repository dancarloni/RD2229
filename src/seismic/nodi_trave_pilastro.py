"""Fase U.4 - Verifica nodi trave-pilastro.

Implementa:
- V_jhd (taglio orizzontale nodo)
- eta per resistenza diagonale (con fallback conservativo)
- verifica compressione diagonale
- stima armatura orizzontale minima A_sh
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class RisultatoNodoTravePilastro:
    """Esito verifica nodo trave-pilastro."""

    v_jhd: float
    v_rd: float
    verificato: bool
    eta: float
    a_sh_min: float
    warning_fck_alto: bool
    warning_nu_d_alto: bool
    passaggi: list[str] = field(default_factory=list)


def calcola_v_jhd(a_s1: float, f_yd: float, n_g: float, v_c: float) -> float:
    """Calcola il taglio orizzontale nel nodo.

    V_jhd = A_s1 * f_yd * (1 + N_G / (A_s1 * f_yd)) - V_C
    """

    if a_s1 <= 0.0 or f_yd <= 0.0:
        raise ValueError("a_s1 e f_yd devono essere > 0")

    return a_s1 * f_yd * (1.0 + n_g / (a_s1 * f_yd)) - v_c


def calcola_eta(f_ck: float, eta_min_fallback: float = 0.05) -> tuple[float, bool]:
    """Calcola parametro eta per verifica diagonale.

    Formula EC8: eta = 0.6 * (1 - f_ck / 250)
    Se valore non fisico (<=0), applica fallback conservativo.
    """

    if f_ck <= 0.0:
        raise ValueError("f_ck deve essere > 0")

    eta = 0.6 * (1.0 - f_ck / 250.0)
    warning_fck_alto = eta <= 0.0
    if warning_fck_alto:
        eta = eta_min_fallback
    return eta, warning_fck_alto


def calcola_v_rd_diagonale(eta: float, f_cd: float, b_j: float, h_jc: float, nu_d: float) -> float:
    """Calcola resistenza diagonale del nodo."""

    if eta <= 0.0:
        raise ValueError("eta deve essere > 0")
    if f_cd <= 0.0 or b_j <= 0.0 or h_jc <= 0.0:
        raise ValueError("f_cd, b_j, h_jc devono essere > 0")
    if nu_d < 0.0:
        raise ValueError("nu_d deve essere >= 0")

    rad = 1.0 - nu_d / eta
    if rad <= 0.0:
        return 0.0

    return eta * f_cd * b_j * h_jc * (rad**0.5)


def stima_a_sh_min(v_jhd: float, f_yd: float, braccio: float = 1.0) -> float:
    """Stima semplificata armatura orizzontale minima A_sh.

    A_sh >= V_jhd / (f_yd * braccio)
    """

    if f_yd <= 0.0 or braccio <= 0.0:
        raise ValueError("f_yd e braccio devono essere > 0")

    return max(v_jhd / (f_yd * braccio), 0.0)


def verifica_nodo_trave_pilastro(
    *,
    a_s1: float,
    f_yd: float,
    n_g: float,
    v_c: float,
    f_ck: float,
    f_cd: float,
    b_j: float,
    h_jc: float,
    nu_d: float,
    braccio_a_sh: float = 1.0,
) -> RisultatoNodoTravePilastro:
    """Esegue verifica nodo completa con warning edge-cases."""

    passaggi: list[str] = []

    v_jhd = calcola_v_jhd(a_s1=a_s1, f_yd=f_yd, n_g=n_g, v_c=v_c)
    passaggi.append(f"V_jhd = {v_jhd:.3f}")

    eta, warning_fck_alto = calcola_eta(f_ck=f_ck)
    passaggi.append(f"eta = {eta:.3f}")

    v_rd = calcola_v_rd_diagonale(eta=eta, f_cd=f_cd, b_j=b_j, h_jc=h_jc, nu_d=nu_d)
    passaggi.append(f"V_rd = {v_rd:.3f}")

    verificato = v_jhd <= v_rd
    passaggi.append("Verifica nodo: OK" if verificato else "Verifica nodo: NON OK")

    a_sh_min = stima_a_sh_min(v_jhd=max(v_jhd, 0.0), f_yd=f_yd, braccio=braccio_a_sh)
    passaggi.append(f"A_sh,min = {a_sh_min:.3f}")

    warning_nu_d_alto = nu_d > 0.8
    if warning_fck_alto:
        passaggi.append("Warning: f_ck elevato, applicato fallback conservativo su eta")
    if warning_nu_d_alto:
        passaggi.append("Warning: nu_d > 0.8, nodo molto sollecitato")

    return RisultatoNodoTravePilastro(
        v_jhd=v_jhd,
        v_rd=v_rd,
        verificato=verificato,
        eta=eta,
        a_sh_min=a_sh_min,
        warning_fck_alto=warning_fck_alto,
        warning_nu_d_alto=warning_nu_d_alto,
        passaggi=passaggi,
    )
