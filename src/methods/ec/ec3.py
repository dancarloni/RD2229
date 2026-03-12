"""Verifiche EC3 (EN 1993-1-1) per elementi in acciaio."""

from __future__ import annotations

from math import sqrt
from typing import Any


def classifica_sezione_ec3(
    fy: float,
    b: float,
    d: float,
    tf: float,
    tw: float,
) -> dict[str, Any]:
    """Classificazione semplificata classe 1-4 su rapporti c/t."""
    if min(fy, b, d, tf, tw) <= 0:
        raise ValueError("Parametri geometrici e fy devono essere > 0")

    epsilon = sqrt(235.0 / fy)
    ratio_flange = b / (2.0 * tf)
    ratio_web = d / tw

    if ratio_flange <= 9.0 * epsilon and ratio_web <= 72.0 * epsilon:
        classe = 1
    elif ratio_flange <= 10.0 * epsilon and ratio_web <= 83.0 * epsilon:
        classe = 2
    elif ratio_flange <= 14.0 * epsilon and ratio_web <= 124.0 * epsilon:
        classe = 3
    else:
        classe = 4

    return {
        "classe": classe,
        "epsilon": epsilon,
        "ratio_flange": ratio_flange,
        "ratio_web": ratio_web,
        "riferimento_normativo": "EC3 EN1993-1-1 §5.5",
    }


def verifica_flessione_ec3(
    fy: float,
    Wpl: float,
    d: float,
    b: float,
    tf: float,
    tw: float,
    M_d: float,
    gamma_m0: float = 1.0,
) -> dict[str, Any]:
    """Verifica a flessione EC3 con modulo resistente dipendente dalla classe."""
    if min(fy, Wpl, d, b, tf, tw, gamma_m0) <= 0:
        raise ValueError("Parametri devono essere > 0")

    classificazione = classifica_sezione_ec3(fy=fy, b=b, d=d, tf=tf, tw=tw)
    classe = classificazione["classe"]

    if classe <= 2:
        w_eff = Wpl
    elif classe == 3:
        w_eff = 0.9 * Wpl
    else:
        w_eff = 0.7 * Wpl

    M_Rd = w_eff * fy / gamma_m0
    rateo = M_d / M_Rd if M_Rd > 0 else 0.0

    return {
        "esito": M_d <= M_Rd * 1.001,
        "rateo": rateo,
        "M_d": M_d,
        "M_Rd": M_Rd,
        "classe_sezione": classe,
        "W_eff": w_eff,
        "riferimento_normativo": "EC3 EN1993-1-1 §6.2.5",
    }


def verifica_instabilita_flessotorsionale_ec3(
    M_cr: float,
    M_pl_Rd: float,
    alpha_lt: float = 0.34,
) -> dict[str, Any]:
    """Calcolo coefficiente χ_LT e momento resistente M_b,Rd."""
    if min(M_cr, M_pl_Rd) <= 0:
        raise ValueError("M_cr e M_pl_Rd devono essere > 0")

    lambda_lt = sqrt(M_pl_Rd / M_cr)
    phi = 0.5 * (1.0 + alpha_lt * (lambda_lt - 0.2) + lambda_lt**2)
    radicando = max(phi**2 - lambda_lt**2, 0.0)
    chi_lt = min(1.0, 1.0 / (phi + sqrt(radicando)))
    M_b_Rd = chi_lt * M_pl_Rd

    return {
        "chi_lt": chi_lt,
        "lambda_lt": lambda_lt,
        "M_b_Rd": M_b_Rd,
        "riferimento_normativo": "EC3 EN1993-1-1 §6.3.2",
    }


def verifica_taglio_ec3(
    fy: float,
    A_v: float,
    V_d: float,
    gamma_m0: float = 1.0,
) -> dict[str, Any]:
    """Resistenza a taglio §6.2.6: V_Rd = A_v*fy/(sqrt(3)*gamma_M0)."""
    if min(fy, A_v, gamma_m0) <= 0:
        raise ValueError("fy, A_v e gamma_m0 devono essere > 0")

    V_Rd = A_v * fy / (sqrt(3.0) * gamma_m0)
    return {
        "esito": V_d <= V_Rd * 1.001,
        "rateo": V_d / V_Rd if V_Rd > 0 else 0.0,
        "V_d": V_d,
        "V_Rd": V_Rd,
        "riferimento_normativo": "EC3 EN1993-1-1 §6.2.6",
    }


def verifica_compressione_ec3(
    fy: float,
    A: float,
    N_d: float,
    gamma_m0: float = 1.0,
) -> dict[str, Any]:
    """Resistenza a compressione di sezione §6.2.4."""
    if min(fy, A, gamma_m0) <= 0:
        raise ValueError("fy, A e gamma_m0 devono essere > 0")

    N_Rd = A * fy / gamma_m0
    return {
        "esito": N_d <= N_Rd * 1.001,
        "rateo": N_d / N_Rd if N_Rd > 0 else 0.0,
        "N_d": N_d,
        "N_Rd": N_Rd,
        "riferimento_normativo": "EC3 EN1993-1-1 §6.2.4",
    }


def verifica_instabilita_flessionale_ec3(
    N_cr: float,
    N_pl_Rd: float,
    alpha: float = 0.34,
) -> dict[str, Any]:
    """Instabilita flessionale con coefficiente chi (§6.3.1)."""
    if min(N_cr, N_pl_Rd) <= 0:
        raise ValueError("N_cr e N_pl_Rd devono essere > 0")

    lambda_rel = sqrt(N_pl_Rd / N_cr)
    phi = 0.5 * (1.0 + alpha * (lambda_rel - 0.2) + lambda_rel**2)
    radicando = max(phi**2 - lambda_rel**2, 0.0)
    chi = min(1.0, 1.0 / (phi + sqrt(radicando)))
    N_b_Rd = chi * N_pl_Rd

    return {
        "chi": chi,
        "lambda_rel": lambda_rel,
        "N_b_Rd": N_b_Rd,
        "riferimento_normativo": "EC3 EN1993-1-1 §6.3.1",
    }
