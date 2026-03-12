"""Verifiche FRP secondo CNR-DT 200 (ed. 2004 e R1/2013 semplificate)."""

from __future__ import annotations

from typing import Any

FRP_MATERIALI_DEFAULT: dict[str, dict[str, float]] = {
    "CFRP": {"E_f": 170000.0, "f_fu": 2800.0, "gamma_f": 1.25},
    "GFRP": {"E_f": 70000.0, "f_fu": 1500.0, "gamma_f": 1.35},
    "AFRP": {"E_f": 120000.0, "f_fu": 2000.0, "gamma_f": 1.30},
}


def _get_mat(tipo_frp: str) -> dict[str, float]:
    key = tipo_frp.upper()
    if key not in FRP_MATERIALI_DEFAULT:
        raise ValueError(f"Tipo FRP non supportato: {tipo_frp}")
    return FRP_MATERIALI_DEFAULT[key]


def calcola_fattori_riduzione_frp(
    tipo_frp: str,
    classe_esposizione: str = "interna",
) -> dict[str, float]:
    """Restituisce fattori di riduzione gamma_f e eta_a in forma semplificata CNR-DT 200."""
    mat = _get_mat(tipo_frp)
    gamma_f = mat["gamma_f"]

    eta_map = {
        "interna": 1.00,
        "esterna": 0.90,
        "aggressiva": 0.80,
    }
    key = classe_esposizione.lower()
    if key not in eta_map:
        raise ValueError(f"Classe esposizione non supportata: {classe_esposizione}")

    eta_a = eta_map[key]
    return {
        "gamma_f": gamma_f,
        "eta_a": eta_a,
        "fattore_globale": eta_a / gamma_f,
    }


def verifica_rinforzo_flessione_frp(
    tipo_frp: str,
    A_f_cm2: float,
    z_cm: float,
    eps_fd: float,
    M_d: float,
    M_rd_base: float,
    eta_a: float = 1.0,
    gamma_f: float | None = None,
) -> dict[str, Any]:
    """Incremento a flessione con lamine FRP: DeltaM_Rd = A_f*f_fd*z."""
    if min(A_f_cm2, z_cm, eps_fd, M_rd_base, eta_a) <= 0:
        raise ValueError("Parametri FRP devono essere > 0")

    mat = _get_mat(tipo_frp)
    E_f = mat["E_f"]
    gamma_f_eff = mat["gamma_f"] if gamma_f is None else gamma_f
    eps_fu = mat["f_fu"] / E_f

    eps_eff = min(eps_fd, eps_fu / gamma_f_eff)
    f_fd = E_f * eps_eff * eta_a
    delta_M_Rd = A_f_cm2 * f_fd * z_cm
    M_Rd = M_rd_base + delta_M_Rd

    return {
        "esito": M_d <= M_Rd * 1.001,
        "rateo": M_d / M_Rd if M_Rd > 0 else 0.0,
        "M_d": M_d,
        "M_rd_base": M_rd_base,
        "delta_M_Rd": delta_M_Rd,
        "M_Rd": M_Rd,
        "eps_eff": eps_eff,
        "gamma_f": gamma_f_eff,
        "eta_a": eta_a,
        "riferimento_normativo": "CNR-DT 200 R1/2013 §4",
    }


def verifica_delaminazione_frp(
    tau_b: float,
    f_ctm: float,
    gamma_f: float = 1.25,
) -> dict[str, Any]:
    """Verifica semplificata delaminazione FRP-cls."""
    if min(tau_b, f_ctm, gamma_f) <= 0:
        raise ValueError("Parametri delaminazione devono essere > 0")

    f_bd = 1.8 * f_ctm / gamma_f
    return {
        "esito": tau_b <= f_bd * 1.001,
        "rateo": tau_b / f_bd if f_bd > 0 else 0.0,
        "tau_b": tau_b,
        "f_bd": f_bd,
        "riferimento_normativo": "CNR-DT 200 R1/2013 §5",
    }


def verifica_rinforzo_taglio_frp(
    A_fv_cm2: float,
    f_fd: float,
    s_cm: float,
    d_cm: float,
    V_d: float,
    V_rd_base: float,
    wrapping_totale: bool = True,
) -> dict[str, Any]:
    """Incremento a taglio con tessuti FRP (wrapping totale/parziale)."""
    if min(A_fv_cm2, f_fd, s_cm, d_cm, V_rd_base) <= 0:
        raise ValueError("Parametri taglio FRP devono essere > 0")

    k_wrap = 1.0 if wrapping_totale else 0.65
    delta_V_Rd = k_wrap * (A_fv_cm2 / s_cm) * f_fd * d_cm
    V_Rd = V_rd_base + delta_V_Rd

    return {
        "esito": V_d <= V_Rd * 1.001,
        "rateo": V_d / V_Rd if V_Rd > 0 else 0.0,
        "V_d": V_d,
        "V_rd_base": V_rd_base,
        "delta_V_Rd": delta_V_Rd,
        "V_Rd": V_Rd,
        "wrapping_totale": wrapping_totale,
        "riferimento_normativo": "CNR-DT 200 R1/2013 §6",
    }


def verifica_confinamento_frp(
    f_c: float,
    f_l: float,
    k1: float = 3.3,
) -> dict[str, Any]:
    """Confinamento colonna: f_cc = f_c + k1*f_l (Mander semplificato)."""
    if min(f_c, f_l, k1) <= 0:
        raise ValueError("Parametri confinamento devono essere > 0")

    f_cc = f_c + k1 * f_l
    incremento = f_cc / f_c
    return {
        "f_c": f_c,
        "f_l": f_l,
        "f_cc": f_cc,
        "incremento": incremento,
        "riferimento_normativo": "CNR-DT 200 R1/2013 §7",
    }
