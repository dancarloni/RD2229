"""Check X3 SLU per solai (flessione, taglio, punzonamento, fallback DM96/DM16).

Implementazione in stile dict-based coerente con `NTC2018CodeModule.run_check`.
Unità attese: mm, mm^2, MPa, kN, kNm.
"""

from __future__ import annotations

import math
import uuid
from typing import Any


def _error_result(message: str, norm_refs: list[str]) -> dict[str, Any]:
    run_id = str(uuid.uuid4())
    return {
        "ok": False,
        "value": None,
        "steps": [message],
        "trace": {"run_id": run_id},
        "norm_references": norm_refs,
        "warnings": [],
    }


def x3_slu_flessione(inputs: dict[str, Any]) -> dict[str, Any]:
    """Verifica SLU a flessione (sezione rettangolare, semplice armatura).

    Formula base:
    - f_cd = f_ck / gamma_c
    - f_yd = f_yk / gamma_s
    - x = As*f_yd / (0.85*b*f_cd)
    - z = d - 0.4*x
    - M_Rd = As*f_yd*z
    """

    b = float(inputs.get("b_mm", 0.0))
    d = float(inputs.get("d_mm", 0.0))
    as_mm2 = float(inputs.get("As_mm2", 0.0))
    f_ck = float(inputs.get("f_ck_MPa", 0.0))
    f_yk = float(inputs.get("f_yk_MPa", 0.0))
    gamma_c = float(inputs.get("gamma_c", 1.5))
    gamma_s = float(inputs.get("gamma_s", 1.15))
    m_ed = inputs.get("M_Ed_kNm", None)
    x_lim_over_d = float(inputs.get("x_lim_over_d", 0.45))

    if min(b, d, as_mm2, f_ck, f_yk, gamma_c, gamma_s) <= 0:
        return _error_result(
            "Errore: parametri richiesti mancanti o non validi (b_mm, d_mm, As_mm2, f_ck_MPa, f_yk_MPa).",
            ["NTC2018 §4.1.2.4", "EN 1992-1-1 §6.1.2"],
        )

    run_id = str(uuid.uuid4())
    steps: list[str] = []
    warnings: list[str] = []

    f_cd = f_ck / gamma_c
    f_yd = f_yk / gamma_s
    x = as_mm2 * f_yd / (0.85 * b * f_cd)
    z = d - 0.4 * x

    steps.append(f"f_cd = f_ck/gamma_c = {f_ck:.3f}/{gamma_c:.3f} = {f_cd:.3f} MPa")
    steps.append(f"f_yd = f_yk/gamma_s = {f_yk:.3f}/{gamma_s:.3f} = {f_yd:.3f} MPa")
    steps.append(f"x = As*f_yd/(0.85*b*f_cd) = {x:.3f} mm")
    steps.append(f"z = d - 0.4*x = {d:.3f} - 0.4*{x:.3f} = {z:.3f} mm")

    x_lim = x_lim_over_d * d
    if x > x_lim:
        warnings.append("X3-FLEX-001")
        steps.append(f"Warning X3-FLEX-001: x = {x:.3f} mm > x_lim = {x_lim:.3f} mm")

    if z <= 0 or x >= d:
        warnings.append("X3-FLEX-002")
        steps.append("Warning X3-FLEX-002: sezione fuori dominio semplificato")

    m_rd_nmm = as_mm2 * f_yd * z
    m_rd_knm = m_rd_nmm / 1_000_000.0
    steps.append(f"M_Rd = As*f_yd*z = {m_rd_nmm:.3f} Nmm = {m_rd_knm:.3f} kNm")

    utilisation = None
    ok = True
    if m_ed is not None:
        m_ed_val = float(m_ed)
        utilisation = m_ed_val / m_rd_knm if m_rd_knm > 0 else 999.0
        ok = m_ed_val <= m_rd_knm and "X3-FLEX-002" not in warnings
        steps.append(
            f"UC_M = M_Ed/M_Rd = {m_ed_val:.3f}/{m_rd_knm:.3f} = {utilisation:.4f} -> {'OK' if ok else 'NON OK'}"
        )
    else:
        ok = "X3-FLEX-002" not in warnings
        steps.append("M_Ed_kNm non fornito: calcolato solo M_Rd")

    return {
        "ok": ok,
        "value": round(m_rd_knm, 4),
        "M_Rd_kNm": round(m_rd_knm, 4),
        "utilisation": round(utilisation, 4) if utilisation is not None else None,
        "details": {
            "f_cd_MPa": round(f_cd, 4),
            "f_yd_MPa": round(f_yd, 4),
            "x_mm": round(x, 4),
            "x_lim_mm": round(x_lim, 4),
            "z_mm": round(z, 4),
        },
        "steps": steps,
        "warnings": warnings,
        "trace": {"run_id": run_id},
        "norm_references": ["NTC2018 §4.1.2.4", "EN 1992-1-1 §6.1.2"],
    }


def x3_slu_taglio(inputs: dict[str, Any]) -> dict[str, Any]:
    """Verifica SLU a taglio con formulazione V_Rd,c (senza armatura trasversale)."""

    bw = float(inputs.get("bw_mm", 0.0))
    d = float(inputs.get("d_mm", 0.0))
    asl = float(inputs.get("Asl_mm2", 0.0))
    f_ck = float(inputs.get("f_ck_MPa", 0.0))
    gamma_c = float(inputs.get("gamma_c", 1.5))
    v_ed = inputs.get("V_Ed_kN", None)

    if min(bw, d, asl, f_ck, gamma_c) <= 0:
        return _error_result(
            "Errore: parametri richiesti mancanti o non validi (bw_mm, d_mm, Asl_mm2, f_ck_MPa).",
            ["NTC2018 §4.1.2.5", "EN 1992-1-1 §6.2.2"],
        )

    run_id = str(uuid.uuid4())
    steps: list[str] = []
    warnings: list[str] = []

    k = min(1.0 + math.sqrt(200.0 / d), 2.0)
    rho_l = asl / (bw * d)
    rho_use = min(max(rho_l, 1e-9), 0.02)
    c_rd_c = 0.18 / gamma_c
    v_rd_c_n = c_rd_c * k * (100.0 * rho_use * f_ck) ** (1.0 / 3.0) * bw * d
    v_rd_c_kn = v_rd_c_n / 1000.0

    steps.append(f"k = min(1 + sqrt(200/d), 2) = {k:.4f}")
    steps.append(f"rho_l = Asl/(bw*d) = {rho_l:.6f}")
    steps.append(f"C_Rd,c = 0.18/gamma_c = 0.18/{gamma_c:.3f} = {c_rd_c:.5f}")
    steps.append(f"V_Rd,c = {v_rd_c_kn:.4f} kN")

    if rho_l <= 0.0 or rho_l > 0.02:
        warnings.append("X3-TAG-001")
        steps.append("Warning X3-TAG-001: rho_l fuori range di validita")

    utilisation = None
    ok = True
    if v_ed is not None:
        v_ed_val = float(v_ed)
        utilisation = v_ed_val / v_rd_c_kn if v_rd_c_kn > 0 else 999.0
        if utilisation > 0.6:
            warnings.append("X3-TAG-002")
            steps.append("Warning X3-TAG-002: V_Ed/V_Rd,c > 0.6")
        ok = v_ed_val <= v_rd_c_kn
        steps.append(
            f"UC_V = V_Ed/V_Rd,c = {v_ed_val:.4f}/{v_rd_c_kn:.4f} = {utilisation:.4f} -> {'OK' if ok else 'NON OK'}"
        )
    else:
        steps.append("V_Ed_kN non fornito: calcolato solo V_Rd,c")

    return {
        "ok": ok,
        "value": round(v_rd_c_kn, 4),
        "V_Rd_c_kN": round(v_rd_c_kn, 4),
        "utilisation": round(utilisation, 4) if utilisation is not None else None,
        "details": {
            "k": round(k, 4),
            "rho_l": round(rho_l, 6),
            "C_Rd_c": round(c_rd_c, 6),
        },
        "steps": steps,
        "warnings": warnings,
        "trace": {"run_id": run_id},
        "norm_references": ["NTC2018 §4.1.2.5", "EN 1992-1-1 §6.2.2"],
    }


def x3_slu_punzonamento(inputs: dict[str, Any]) -> dict[str, Any]:
    """Verifica SLU a punzonamento con formulazione EC2/NTC."""

    b0 = float(inputs.get("b0_mm", 0.0))
    d = float(inputs.get("d_mm", 0.0))
    rho_l = float(inputs.get("rho_l", 0.0))
    sigma_cp = float(inputs.get("sigma_cp_MPa", 0.0))
    gamma_c = float(inputs.get("gamma_c", 1.5))
    gamma_s = float(inputs.get("gamma_s", 1.15))
    v_ed = inputs.get("V_Ed_kN", None)
    c1 = float(inputs.get("c1_mm", 0.0))
    c2 = float(inputs.get("c2_mm", 0.0))
    perimeter_factor = float(inputs.get("perimeter_reduction_factor", 1.0))

    f_ck = float(inputs.get("f_ck_MPa", 0.0))
    f_cd = inputs.get("f_cd_MPa", None)
    if f_ck <= 0.0 and f_cd is None:
        return _error_result(
            "Errore: fornire f_ck_MPa valido oppure f_cd_MPa.",
            ["NTC2018 §4.1.2.5", "EN 1992-1-1 §6.4"],
        )
    if f_ck <= 0.0:
        f_cd_val = float(f_cd)
        f_ck = f_cd_val * gamma_c
    else:
        f_cd_val = float(f_cd) if f_cd is not None else f_ck / gamma_c

    if b0 <= 0.0 and min(c1, c2, d) > 0.0:
        b0 = (2.0 * (c1 + c2) + 4.0 * math.pi * d) * perimeter_factor

    if min(b0, d, rho_l, f_cd_val) <= 0:
        return _error_result(
            "Errore: parametri richiesti mancanti o non validi (b0_mm, d_mm, rho_l, f_cd_MPa/f_ck_MPa).",
            ["NTC2018 §4.1.2.5", "EN 1992-1-1 §6.4"],
        )

    run_id = str(uuid.uuid4())
    steps: list[str] = []
    warnings: list[str] = []

    c_rd_c = float(inputs.get("C_Rd_c", 0.18 / gamma_c))
    k_1 = float(inputs.get("k1", 0.15))
    k = min(1.0 + math.sqrt(200.0 / d), 2.0)
    rho_use = min(max(rho_l, 1e-9), 0.02)

    term = c_rd_c * k * (100.0 * rho_use * f_ck) ** (1.0 / 3.0) + k_1 * sigma_cp
    v_rd_c_n = term * b0 * d
    v_rd_c_kn = v_rd_c_n / 1000.0

    asw_over_s = float(inputs.get("A_sw_per_s_mm2_per_mm", 0.0))
    if asw_over_s <= 0.0:
        a_sw = float(inputs.get("A_sw_mm2", 0.0))
        s_mm = float(inputs.get("s_mm", 0.0))
        if a_sw > 0.0 and s_mm > 0.0:
            asw_over_s = a_sw / s_mm
    f_ywd = float(inputs.get("f_ywd_MPa", 0.0))
    if f_ywd <= 0.0:
        f_yk = float(inputs.get("f_yk_MPa", 0.0))
        if f_yk > 0.0:
            f_ywd = f_yk / gamma_s
    alpha_deg = float(inputs.get("alpha_deg", 90.0))
    alpha_rad = math.radians(alpha_deg)
    v_rd_s_n = (
        asw_over_s * f_ywd * d * math.sin(alpha_rad) if asw_over_s > 0.0 and f_ywd > 0.0 else 0.0
    )
    v_rd_s_kn = v_rd_s_n / 1000.0
    v_rd_total_kn = v_rd_c_kn + v_rd_s_kn

    steps.append(f"k = min(1 + sqrt(200/d), 2) = {k:.4f}")
    steps.append(f"rho_l,eff = min(max(rho_l, 0), 0.02) = {rho_use:.6f}")
    steps.append(f"u_1 = b0 = {b0:.3f} mm")
    steps.append(f"term = C_Rd,c*k*(100*rho_l*f_ck)^(1/3) + k1*sigma_cp = {term:.6f}")
    steps.append(f"V_Rd,c = term*b0*d = {v_rd_c_kn:.4f} kN")
    if v_rd_s_kn > 0.0:
        steps.append(f"V_Rd,s = (A_sw/s)*f_ywd*d*sin(alpha) = {v_rd_s_kn:.4f} kN")
    steps.append(f"V_Rd = V_Rd,c + V_Rd,s = {v_rd_total_kn:.4f} kN")

    if rho_l > 0.02:
        warnings.append("X3-PUNZ-002")
        steps.append("Warning X3-PUNZ-002: rho_l > 0.02, applicato clamp normativo")

    utilisation = None
    ok = True
    if v_ed is not None:
        v_ed_val = float(v_ed)
        utilisation = v_ed_val / v_rd_total_kn if v_rd_total_kn > 0 else 999.0
        if v_ed_val > 0.8 * v_rd_total_kn:
            warnings.append("X3-PUNZ-001")
            steps.append("Warning X3-PUNZ-001: V_Ed > 0.8*V_Rd")
        ok = v_ed_val <= v_rd_total_kn
        steps.append(
            f"UC_P = V_Ed/V_Rd = {v_ed_val:.4f}/{v_rd_total_kn:.4f} = {utilisation:.4f} -> {'OK' if ok else 'NON OK'}"
        )
    else:
        steps.append("V_Ed_kN non fornito: calcolata solo la capacita' V_Rd")

    return {
        "ok": ok,
        "value": round(v_rd_total_kn, 4),
        "V_Rd_c_kN": round(v_rd_c_kn, 4),
        "V_Rd_s_kN": round(v_rd_s_kn, 4),
        "V_Rd_kN": round(v_rd_total_kn, 4),
        "utilisation": round(utilisation, 4) if utilisation is not None else None,
        "details": {
            "k": round(k, 4),
            "C_Rd_c": round(c_rd_c, 4),
            "k1": round(k_1, 4),
            "term": round(term, 6),
            "b0_mm": round(b0, 4),
            "rho_l_eff": round(rho_use, 6),
            "f_cd_MPa": round(f_cd_val, 4),
            "f_ck_MPa": round(f_ck, 4),
            "A_sw_per_s_mm2_per_mm": round(asw_over_s, 6),
            "f_ywd_MPa": round(f_ywd, 4),
            "alpha_deg": round(alpha_deg, 4),
        },
        "steps": steps,
        "warnings": warnings,
        "trace": {"run_id": run_id},
        "norm_references": ["NTC2018 §4.1.2.5", "EN 1992-1-1 §6.4"],
    }


def x3_dm96_laterocemento(inputs: dict[str, Any]) -> dict[str, Any]:
    """Fallback tabellare DM96 per laterocemento (estratto minimo)."""

    luce = float(inputs.get("luce_m", 0.0))
    interasse = float(inputs.get("interasse_cm", 0.0))
    altezza = float(inputs.get("altezza_cm", 0.0))

    if min(luce, interasse, altezza) <= 0:
        return _error_result(
            "Errore: parametri richiesti mancanti o non validi (luce_m, interasse_cm, altezza_cm).",
            ["DM 9/1/1996"],
        )

    run_id = str(uuid.uuid4())
    warnings: list[str] = []
    steps: list[str] = []

    table = [
        ("LC-01", (3.5, 4.5), 50.0, (20.0, 24.0), (0.15, 0.17)),
        ("LC-02", (4.5, 5.5), 50.0, (24.0, 28.0), (0.16, 0.18)),
        ("LC-03", (5.5, 6.5), 60.0, (28.0, 32.0), (0.17, 0.20)),
    ]

    for case_id, luce_rng, interasse_req, alt_rng, k_rng in table:
        if (
            luce_rng[0] <= luce <= luce_rng[1]
            and abs(interasse - interasse_req) < 1e-9
            and alt_rng[0] <= altezza <= alt_rng[1]
        ):
            k_mid = (k_rng[0] + k_rng[1]) / 2.0
            steps.append(f"Caso tabellare {case_id} individuato")
            steps.append(
                f"k_DM96 adottato (medio range) = ({k_rng[0]:.3f}+{k_rng[1]:.3f})/2 = {k_mid:.3f}"
            )
            return {
                "ok": True,
                "value": round(k_mid, 4),
                "k_dm96": round(k_mid, 4),
                "case_id": case_id,
                "warnings": warnings,
                "steps": steps,
                "trace": {"run_id": run_id},
                "norm_references": ["DM 9/1/1996"],
            }

    warnings.append("X3-DM96-001")
    steps.append("Warning X3-DM96-001: caso fuori tabella DM96")
    return {
        "ok": False,
        "value": None,
        "k_dm96": None,
        "case_id": None,
        "warnings": warnings,
        "steps": steps,
        "trace": {"run_id": run_id},
        "norm_references": ["DM 9/1/1996"],
    }


def x3_dm16_legno(inputs: dict[str, Any]) -> dict[str, Any]:
    """Fallback tabellare DM16 legno (estratto minimo)."""

    run_id = str(uuid.uuid4())
    steps: list[str] = []
    warnings: list[str] = []

    f_mk = inputs.get("f_mk_MPa", None)
    gamma_m = max(float(inputs.get("gamma_m", 1.5)), 1.5)
    classe_legno = str(inputs.get("classe_legno", "")).strip() or "non_specificata"
    classe_servizio = str(inputs.get("classe_servizio", "")).strip() or "non_specificata"

    if f_mk is None or float(f_mk) <= 0:
        warnings.append("X3-DM16-001")
        return {
            "ok": False,
            "value": None,
            "f_md_MPa": None,
            "warnings": warnings,
            "steps": ["Warning X3-DM16-001: f_m,k assente o non valido"],
            "details": {
                "classe_legno": classe_legno,
                "classe_servizio": classe_servizio,
                "gamma_m": gamma_m,
            },
            "trace": {"run_id": run_id},
            "norm_references": ["DM 16/1/1996"],
        }

    f_mk_val = float(f_mk)
    f_md = f_mk_val / gamma_m
    steps.append(f"f_md = f_m,k/gamma_m = {f_mk_val:.3f}/{gamma_m:.3f} = {f_md:.3f} MPa")

    return {
        "ok": True,
        "value": round(f_md, 4),
        "f_md_MPa": round(f_md, 4),
        "warnings": warnings,
        "steps": steps,
        "details": {
            "classe_legno": classe_legno,
            "classe_servizio": classe_servizio,
            "gamma_m": gamma_m,
        },
        "trace": {"run_id": run_id},
        "norm_references": ["DM 16/1/1996"],
    }
