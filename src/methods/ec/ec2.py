"""Verifiche EC2 (EN 1992-1-1) per CA in forma compatta e tracciabile."""

from __future__ import annotations

from math import sqrt
from typing import Any

GAMMA_C_EC2 = 1.5
GAMMA_S_EC2 = 1.15
MATERIAL_ALPHA_CC = 0.85

# Fattore di conversione centralizzato — importato dall'adapter ufficiale
try:
    from src.core.adapter_unita_misura import _MPA_TO_KG_CM2 as MPA_TO_KGCM2
except ImportError:
    MPA_TO_KGCM2 = 10.19716  # Fallback (valore preciso)


def _ensure_positive(name: str, value: float) -> None:
    if value <= 0:
        raise ValueError(f"{name} deve essere > 0")


def verifica_flessione_ec2(
    fck: float,
    b: float,
    d: float,
    As: float,
    c_nom: float,
    M_d: float,
    fyk: float = 450.0,
) -> dict[str, Any]:
    """Verifica SLU a flessione retta (§6.1 EC2)."""
    _ensure_positive("fck", fck)
    _ensure_positive("b", b)
    _ensure_positive("d", d)
    _ensure_positive("As", As)
    _ensure_positive("fyk", fyk)
    _ensure_positive("c_nom", c_nom + 1.0)

    f_cd = MATERIAL_ALPHA_CC * fck / GAMMA_C_EC2 * MPA_TO_KGCM2
    f_yd = fyk / GAMMA_S_EC2 * MPA_TO_KGCM2

    x = As * f_yd / (0.8 * b * f_cd)
    x_lim = 0.45 * d
    x_eff = min(x, x_lim)
    z = d - 0.4 * x_eff
    z = max(0.01, z)

    M_Rd = As * f_yd * z
    rateo = M_d / M_Rd if M_Rd > 0 else 0.0
    esito = M_d <= M_Rd * 1.001

    return {
        "esito": esito,
        "rateo": rateo,
        "M_d": M_d,
        "M_Rd": M_Rd,
        "f_cd": f_cd,
        "f_yd": f_yd,
        "x": x_eff,
        "x_lim": x_lim,
        "z": z,
        "riferimento_normativo": "EC2 EN1992-1-1 §6.1",
    }


def verifica_taglio_ec2(
    fck: float,
    b_w: float,
    d: float,
    rho_l: float,
    V_d: float,
    sigma_cp: float = 0.0,
) -> dict[str, Any]:
    """Verifica taglio senza armatura trasversale (§6.2.2 EC2)."""
    _ensure_positive("fck", fck)
    _ensure_positive("b_w", b_w)
    _ensure_positive("d", d)
    _ensure_positive("rho_l", rho_l)

    d_mm = d * 10.0
    k = min(1.0 + sqrt(200.0 / d_mm), 2.0)
    c_rdc = 0.18 / GAMMA_C_EC2
    k1 = 0.15

    v_formula_mpa = c_rdc * k * (100.0 * rho_l * fck) ** (1.0 / 3.0) + k1 * sigma_cp
    v_min_mpa = 0.035 * (k**1.5) * sqrt(fck) + k1 * sigma_cp
    v_rdc_mpa = max(v_formula_mpa, v_min_mpa)
    v_rdc_kgcm2 = v_rdc_mpa * MPA_TO_KGCM2

    V_Rd = v_rdc_kgcm2 * b_w * d
    rateo = V_d / V_Rd if V_Rd > 0 else 0.0

    return {
        "esito": V_d <= V_Rd * 1.001,
        "rateo": rateo,
        "V_d": V_d,
        "V_Rd": V_Rd,
        "k": k,
        "v_rdc_mpa": v_rdc_mpa,
        "riferimento_normativo": "EC2 EN1992-1-1 §6.2.2",
    }


def verifica_torsione_ec2(
    fck: float,
    A_k: float,
    t_ef: float,
    T_d: float,
) -> dict[str, Any]:
    """Verifica semplificata a torsione (§6.3 EC2, analogia parete sottile)."""
    _ensure_positive("fck", fck)
    _ensure_positive("A_k", A_k)
    _ensure_positive("t_ef", t_ef)

    f_cd = MATERIAL_ALPHA_CC * fck / GAMMA_C_EC2 * MPA_TO_KGCM2
    nu = 0.6 * (1.0 - fck / 250.0)
    nu = max(0.35, nu)
    T_Rd = 0.5 * nu * f_cd * A_k * t_ef

    return {
        "esito": T_d <= T_Rd * 1.001,
        "rateo": T_d / T_Rd if T_Rd > 0 else 0.0,
        "T_d": T_d,
        "T_Rd": T_Rd,
        "nu": nu,
        "riferimento_normativo": "EC2 EN1992-1-1 §6.3",
    }


def verifica_fessurazione_ec2(
    sigma_s: float,
    f_ctm: float,
    limite_wk_mm: float = 0.3,
) -> dict[str, Any]:
    """Check SLE semplificato su ampiezza caratteristica fessura w_k."""
    _ensure_positive("sigma_s", sigma_s)
    _ensure_positive("f_ctm", f_ctm)

    # Relazione semplificata: w_k proporzionale a sigma_s/f_ctm.
    w_k_mm = 0.08 * (sigma_s / f_ctm)
    esito = w_k_mm <= limite_wk_mm

    return {
        "esito": esito,
        "rateo": w_k_mm / limite_wk_mm,
        "w_k_mm": w_k_mm,
        "limite_wk_mm": limite_wk_mm,
        "riferimento_normativo": "EC2 EN1992-1-1 §7.3.4",
    }


def verifica_pressoflessione_ec2(
    fck: float,
    b: float,
    d: float,
    As: float,
    N_d: float,
    M_d: float,
    fyk: float = 450.0,
) -> dict[str, Any]:
    """Verifica semplificata N-M: incremento M_Rd con compressione assiale."""
    _ensure_positive("fck", fck)
    _ensure_positive("b", b)
    _ensure_positive("d", d)
    _ensure_positive("As", As)
    _ensure_positive("fyk", fyk)

    base = verifica_flessione_ec2(fck=fck, b=b, d=d, As=As, c_nom=3.0, M_d=M_d, fyk=fyk)
    f_cd = base["f_cd"]
    f_yd = base["f_yd"]

    N_Rd_max = b * d * f_cd + As * f_yd
    if N_d >= 0:
        incremento = 1.0 + min(N_d / max(0.5 * N_Rd_max, 1e-9), 1.0)
    else:
        incremento = max(0.5, 1.0 + N_d / max(N_Rd_max, 1e-9))

    M_Rd = base["M_Rd"] * incremento
    rateo_M = M_d / M_Rd if M_Rd > 0 else 0.0
    rateo_N = abs(N_d) / N_Rd_max if N_Rd_max > 0 else 0.0

    return {
        "esito": (M_d <= M_Rd * 1.001) and (abs(N_d) <= N_Rd_max * 1.001),
        "rateo": max(rateo_M, rateo_N),
        "N_d": N_d,
        "N_Rd": N_Rd_max,
        "M_d": M_d,
        "M_Rd": M_Rd,
        "incremento_M": incremento,
        "riferimento_normativo": "EC2 EN1992-1-1 §6.1",
    }


def verifica_taglio_con_armatura_ec2(
    fck: float,
    b_w: float,
    d: float,
    Asw: float,
    s: float,
    V_d: float,
    fyk: float = 450.0,
    theta_deg: float = 45.0,
) -> dict[str, Any]:
    """Verifica taglio con staffe (§6.2.3 EC2, schema semplificato)."""
    _ensure_positive("fck", fck)
    _ensure_positive("b_w", b_w)
    _ensure_positive("d", d)
    _ensure_positive("Asw", Asw)
    _ensure_positive("s", s)
    _ensure_positive("fyk", fyk)

    if not 21.8 <= theta_deg <= 45.0:
        raise ValueError("theta_deg deve essere tra 21.8 e 45.0")

    from math import radians, tan

    theta = radians(theta_deg)
    cot_theta = 1.0 / tan(theta)
    z = 0.9 * d
    f_ywd = fyk / GAMMA_S_EC2 * MPA_TO_KGCM2
    f_cd = MATERIAL_ALPHA_CC * fck / GAMMA_C_EC2 * MPA_TO_KGCM2
    nu1 = 0.6 * (1.0 - fck / 250.0)
    nu1 = max(0.35, nu1)

    V_Rd_s = (Asw / s) * z * f_ywd * cot_theta
    V_Rd_max = b_w * z * nu1 * f_cd / (cot_theta + tan(theta))
    V_Rd = min(V_Rd_s, V_Rd_max)

    return {
        "esito": V_d <= V_Rd * 1.001,
        "rateo": V_d / V_Rd if V_Rd > 0 else 0.0,
        "V_d": V_d,
        "V_Rd": V_Rd,
        "V_Rd_s": V_Rd_s,
        "V_Rd_max": V_Rd_max,
        "theta_deg": theta_deg,
        "riferimento_normativo": "EC2 EN1992-1-1 §6.2.3",
    }


def verifica_interazione_taglio_torsione_ec2(
    V_d: float,
    V_Rd: float,
    T_d: float,
    T_Rd: float,
) -> dict[str, Any]:
    """Interazione semplificata T-V con criterio ellittico."""
    _ensure_positive("V_Rd", V_Rd)
    _ensure_positive("T_Rd", T_Rd)

    indice = (V_d / V_Rd) ** 2 + (T_d / T_Rd) ** 2
    return {
        "esito": indice <= 1.0,
        "indice_interazione": indice,
        "riferimento_normativo": "EC2 EN1992-1-1 §6.3.2 (semplificato)",
    }


def verifica_deformazione_ec2(
    M_s: float,
    E_cm: float,
    I_gross: float,
    I_cr: float,
    lunghezza_cm: float,
    limite_freccia: float = 250.0,
) -> dict[str, Any]:
    """Stima freccia con inerzia efficace interpolata (§7.4.3, semplificata)."""
    _ensure_positive("E_cm", E_cm)
    _ensure_positive("I_gross", I_gross)
    _ensure_positive("I_cr", I_cr)
    _ensure_positive("lunghezza_cm", lunghezza_cm)
    _ensure_positive("limite_freccia", limite_freccia)

    I_eff = 0.5 * (I_gross + I_cr)
    # Trave semplicemente appoggiata, carico equivalente da momento M_s.
    freccia_cm = (5.0 * M_s * lunghezza_cm**2) / (48.0 * E_cm * I_eff)
    freccia_limite_cm = lunghezza_cm / limite_freccia

    return {
        "esito": freccia_cm <= freccia_limite_cm,
        "rateo": freccia_cm / freccia_limite_cm,
        "freccia_cm": freccia_cm,
        "freccia_limite_cm": freccia_limite_cm,
        "I_eff": I_eff,
        "riferimento_normativo": "EC2 EN1992-1-1 §7.4.3 (semplificato)",
    }
