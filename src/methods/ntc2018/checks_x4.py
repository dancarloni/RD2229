"""Check X4 SLE per solai (deformabilita, tensioni/fessurazione, vibrazioni).

Implementazione dict-based coerente con `NTC2018CodeModule.run_check`.
Unita principali:
- X4.1/X4.2: cm, cm2, cm4, kgf/cm2
- X4.3: m, N*m2, kg/m
"""

from __future__ import annotations

import math
import uuid
from typing import Any

from src.core.registro_log import registro

_KGF_CM2_TO_MPA = 0.0980665
_MODULO_LOG = "methods.ntc2018.checks_x4"


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


def _push_warning(warnings: list[str], steps: list[str], code: str, detail: str) -> None:
    warnings.append(code)
    steps.append(f"Warning {code}: {detail}")
    registro.avviso(_MODULO_LOG, code, detail)


def _schema_coeff_deformabilita(schema: str) -> tuple[str, float]:
    coeffs = {
        "appoggio_appoggio": 5.0 / 384.0,
        "incastro_incastro": 1.0 / 384.0,
        "incastro_appoggio": 1.0 / 185.0,
    }
    schema_norm = schema.strip().lower()
    if schema_norm not in coeffs:
        return "appoggio_appoggio", coeffs["appoggio_appoggio"]
    return schema_norm, coeffs[schema_norm]


def _lambda_sq_vibrazione(schema: str) -> tuple[str, float]:
    lambdas = {
        "appoggio_appoggio": math.pi**2,
        "incastro_incastro": 4.730**2,
        "incastro_appoggio": 3.927**2,
    }
    schema_norm = schema.strip().lower()
    if schema_norm not in lambdas:
        return "appoggio_appoggio", lambdas["appoggio_appoggio"]
    return schema_norm, lambdas[schema_norm]


def x4_sle_deformabilita(inputs: dict[str, Any]) -> dict[str, Any]:
    """Verifica deformabilita SLE con freccia istantanea e lungo termine."""

    q_s = float(inputs.get("q_s_kgf_m2", 0.0))
    i_cm = float(inputs.get("i_cm", 0.0))
    l_cm = float(inputs.get("L_cm", 0.0))
    e_kgf_cm2 = float(inputs.get("E_kgf_cm2", 0.0))
    inertia_cm4 = float(inputs.get("I_cm4", 0.0))
    ratio = float(inputs.get("f_lim_ratio", 250.0))
    phi = float(inputs.get("phi_viscosita", 2.5))
    include_long_term = bool(inputs.get("include_long_term", True))
    schema_in = str(inputs.get("schema", "appoggio_appoggio"))

    norm_refs = ["NTC2018 §4.1.2.2.4", "EN 1992-1-1 §7.4.1", "NTC2018 §11.2.10.7"]
    if min(q_s, i_cm, l_cm, e_kgf_cm2, inertia_cm4, ratio) <= 0:
        use_fallback = bool(inputs.get("use_fallback", False))
        h_cm = float(inputs.get("h_cm", 0.0))
        k_predim = float(inputs.get("k_predim", 80.0))
        if use_fallback and h_cm > 0 and k_predim > 0 and l_cm > 0:
            run_id = str(uuid.uuid4())
            steps: list[str] = []
            warnings: list[str] = []
            f_fallback_cm = l_cm**2 / (k_predim * h_cm)
            f_lim_cm = l_cm / ratio if ratio > 0 else 0.0
            ok = f_lim_cm > 0 and f_fallback_cm <= f_lim_cm
            utilisation = (f_fallback_cm / f_lim_cm) if f_lim_cm > 0 else 999.0
            _push_warning(
                warnings,
                steps,
                "X4-DEF-FALL-001",
                "Attivata formula semplificata f≈L^2/(k*h) per predimensionamento.",
            )
            if not ok:
                _push_warning(warnings, steps, "X4-DEF-001", "Freccia oltre il limite ammissibile.")

            return {
                "ok": ok,
                "value": round(f_fallback_cm, 4),
                "utilisation": round(utilisation, 4),
                "details": {
                    "schema": "fallback",
                    "f_tot_cm": round(f_fallback_cm, 4),
                    "f_tot_mm": round(f_fallback_cm * 10.0, 4),
                    "f_lim_cm": round(f_lim_cm, 4),
                    "f_lim_mm": round(f_lim_cm * 10.0, 4),
                },
                "steps": steps,
                "warnings": warnings,
                "trace": {"run_id": run_id},
                "norm_references": norm_refs,
            }

        return _error_result(
            "Errore: parametri richiesti mancanti o non validi (q_s_kgf_m2, i_cm, L_cm, E_kgf_cm2, I_cm4).",
            norm_refs,
        )

    run_id = str(uuid.uuid4())
    steps: list[str] = []
    warnings: list[str] = []

    schema_norm, coeff_k = _schema_coeff_deformabilita(schema_in)
    if schema_norm != schema_in.strip().lower():
        _push_warning(
            warnings,
            steps,
            "X4-DEF-004",
            f"Schema '{schema_in}' non riconosciuto: usato appoggio_appoggio.",
        )

    q_l = q_s * i_cm / 10_000.0
    f_ist_cm = coeff_k * q_l * (l_cm**4) / (e_kgf_cm2 * inertia_cm4)
    f_tot_cm = f_ist_cm * (1.0 + phi) if include_long_term else f_ist_cm
    f_lim_cm = l_cm / ratio
    utilisation = f_tot_cm / f_lim_cm if f_lim_cm > 0 else 999.0
    ok = f_tot_cm <= f_lim_cm

    steps.append(f"q_l = q_s*i/10^4 = {q_s:.3f}*{i_cm:.3f}/10000 = {q_l:.6f} kgf/cm")
    steps.append(
        f"f_ist = k*q_l*L^4/(E*I) = {coeff_k:.6f}*{q_l:.6f}*{l_cm:.3f}^4/"
        f"({e_kgf_cm2:.3f}*{inertia_cm4:.3f}) = {f_ist_cm:.6f} cm"
    )
    if include_long_term:
        steps.append(f"f_tot = f_ist*(1+phi) = {f_ist_cm:.6f}*(1+{phi:.3f}) = {f_tot_cm:.6f} cm")
    else:
        steps.append("f_tot = f_ist (senza viscosita)")
    steps.append(f"f_lim = L/{ratio:.1f} = {l_cm:.3f}/{ratio:.1f} = {f_lim_cm:.6f} cm")
    steps.append(
        f"UC_f = f_tot/f_lim = {f_tot_cm:.6f}/{f_lim_cm:.6f} = {utilisation:.4f} -> "
        f"{'OK' if ok else 'NON OK'}"
    )

    e_ref = float(inputs.get("E_ref_kgf_cm2", 0.0))
    riduzione_documentata = bool(inputs.get("riduzione_e_documentata", False))
    if e_ref > 0 and e_kgf_cm2 < 0.5 * e_ref and not riduzione_documentata:
        _push_warning(
            warnings,
            steps,
            "X4-DEF-002",
            "Modulo elastico ridotto oltre il 50% senza documentazione.",
        )

    if phi > 3.0:
        _push_warning(warnings, steps, "X4-DEF-003", "Coefficiente viscosita phi anomalo (>3.0).")

    if not ok:
        _push_warning(warnings, steps, "X4-DEF-001", "Freccia totale oltre il limite ammissibile.")

    return {
        "ok": ok,
        "value": round(f_tot_cm, 4),
        "f_ist_cm": round(f_ist_cm, 4),
        "f_tot_cm": round(f_tot_cm, 4),
        "f_lim_cm": round(f_lim_cm, 4),
        "utilisation": round(utilisation, 4),
        "details": {
            "schema": schema_norm,
            "k_schema": round(coeff_k, 6),
            "q_l_kgf_cm": round(q_l, 6),
            "f_ist_cm": round(f_ist_cm, 6),
            "f_tot_cm": round(f_tot_cm, 6),
            "f_lim_cm": round(f_lim_cm, 6),
            "f_ist_mm": round(f_ist_cm * 10.0, 6),
            "f_tot_mm": round(f_tot_cm * 10.0, 6),
            "f_lim_mm": round(f_lim_cm * 10.0, 6),
        },
        "steps": steps,
        "warnings": warnings,
        "trace": {"run_id": run_id},
        "norm_references": norm_refs,
    }


def x4_sle_tensioni(inputs: dict[str, Any]) -> dict[str, Any]:
    """Verifica tensioni SLE e apertura fessure w_k (approccio sezione fessurata)."""

    m_rara = float(inputs.get("M_rara_kgf_cm", 0.0))
    m_qp = float(inputs.get("M_qp_kgf_cm", 0.0))
    b_cm = float(inputs.get("b_cm", 0.0))
    d_cm = float(inputs.get("d_cm", 0.0))
    as_cm2 = float(inputs.get("As_cm2", 0.0))
    f_ck = float(inputs.get("f_ck_kgf_cm2", 0.0))
    f_yk = float(inputs.get("f_yk_kgf_cm2", 0.0))
    e_c = float(inputs.get("E_c_kgf_cm2", 0.0))
    e_s = float(inputs.get("E_s_kgf_cm2", 2_100_000.0))

    norm_refs = ["NTC2018 §4.1.2.2.5", "NTC2018 §4.1.2.2.4", "EN 1992-1-1 §7.3.4"]

    required_ok = min(m_rara, m_qp, b_cm, d_cm, as_cm2, f_ck, f_yk, e_c, e_s) > 0
    if not required_ok:
        use_fallback = bool(inputs.get("use_fallback", False))
        w_cm3 = float(inputs.get("W_cm3", 0.0))
        if use_fallback and w_cm3 > 0 and m_rara > 0 and m_qp > 0 and f_ck > 0:
            run_id = str(uuid.uuid4())
            steps: list[str] = []
            warnings: list[str] = []
            sigma_rara = m_rara / w_cm3
            sigma_qp = m_qp / w_cm3
            sigma_lim_rara = 0.60 * f_ck
            sigma_lim_qp = 0.45 * f_ck
            util = max(sigma_rara / sigma_lim_rara, sigma_qp / sigma_lim_qp)
            ok = sigma_rara <= sigma_lim_rara and sigma_qp <= sigma_lim_qp
            _push_warning(
                warnings,
                steps,
                "X4-SLE-FALL-001",
                "Attivata verifica elastica semplificata sigma=M/W.",
            )
            if sigma_rara > sigma_lim_rara:
                _push_warning(
                    warnings, steps, "X4-SLE-001", "Superata tensione cls in combinazione rara."
                )
            if sigma_qp > sigma_lim_qp:
                _push_warning(
                    warnings,
                    steps,
                    "X4-SLE-002",
                    "Superata tensione cls in combinazione quasi-permanente.",
                )
            return {
                "ok": ok,
                "value": round(util, 4),
                "utilisation": round(util, 4),
                "details": {
                    "sigma_c_rara_kgf_cm2": round(sigma_rara, 4),
                    "sigma_c_qp_kgf_cm2": round(sigma_qp, 4),
                },
                "steps": steps,
                "warnings": warnings,
                "trace": {"run_id": run_id},
                "norm_references": norm_refs,
            }

        return _error_result(
            "Errore: parametri richiesti mancanti o non validi (M_rara_kgf_cm, M_qp_kgf_cm, b_cm, d_cm, As_cm2, f_ck_kgf_cm2, f_yk_kgf_cm2, E_c_kgf_cm2).",
            norm_refs,
        )

    run_id = str(uuid.uuid4())
    steps: list[str] = []
    warnings: list[str] = []

    ratio_rara = float(inputs.get("sigma_c_ratio_rara", 0.60))
    ratio_qp = float(inputs.get("sigma_c_ratio_qp", 0.45))
    ratio_s = float(inputs.get("sigma_s_ratio", 0.80))
    classe_esposizione = str(inputs.get("classe_esposizione", "ordinaria")).strip().lower()
    w_lim_map = {
        "ordinaria": float(inputs.get("w_lim_ordinaria_mm", 0.4)),
        "aggressiva": float(inputs.get("w_lim_aggressiva_mm", 0.3)),
        "molto_aggressiva": float(inputs.get("w_lim_molto_aggressiva_mm", 0.2)),
    }
    if classe_esposizione not in w_lim_map:
        classe_esposizione = "ordinaria"

    n = e_s / e_c
    radicand = 1.0 + (2.0 * b_cm * d_cm) / (n * as_cm2)
    if radicand <= 0:
        return _error_result("Errore: radicando asse neutro non valido.", norm_refs)

    x_n = (n * as_cm2 / b_cm) * (-1.0 + math.sqrt(radicand))
    i_fess = b_cm * (x_n**3) / 3.0 + n * as_cm2 * (d_cm - x_n) ** 2
    if i_fess <= 0:
        return _error_result("Errore: inerzia fessurata non valida.", norm_refs)

    sigma_c_rara = m_rara * x_n / i_fess
    sigma_c_qp = m_qp * x_n / i_fess
    sigma_s_rara = n * m_rara * (d_cm - x_n) / i_fess

    sigma_c_rara_lim = ratio_rara * f_ck
    sigma_c_qp_lim = ratio_qp * f_ck
    sigma_s_lim = ratio_s * f_yk

    util_c_rara = sigma_c_rara / sigma_c_rara_lim
    util_c_qp = sigma_c_qp / sigma_c_qp_lim
    util_s = sigma_s_rara / sigma_s_lim

    # Stima semplificata EN 1992-1-1 §7.3.4 per w_k.
    copriferro_cm = float(inputs.get("copriferro_cm", 3.0))
    phi_barra_mm = float(inputs.get("phi_barra_mm", 16.0))
    b_mm = b_cm * 10.0
    d_mm = d_cm * 10.0
    x_n_mm = x_n * 10.0
    as_mm2 = as_cm2 * 100.0
    c_mm = copriferro_cm * 10.0
    h_ceff = min(
        2.5 * max(d_mm - x_n_mm, 1.0),
        max((d_mm - x_n_mm) / 3.0 + c_mm + phi_barra_mm / 2.0, 1.0),
        d_mm / 2.0,
    )
    a_ceff = b_mm * max(h_ceff, 1.0)
    rho_p_eff = as_mm2 / a_ceff

    k1 = 0.8
    k2 = 0.5
    k3 = 3.4
    k4 = 0.425
    s_r_max_mm = k3 * c_mm + (k1 * k2 * k4 * phi_barra_mm) / max(rho_p_eff, 1e-6)
    eps_sm_minus_cm = sigma_s_rara / e_s
    w_k_mm = s_r_max_mm * eps_sm_minus_cm
    w_lim_mm = w_lim_map[classe_esposizione]
    util_w = w_k_mm / w_lim_mm

    steps.append(f"n = E_s/E_c = {e_s:.1f}/{e_c:.1f} = {n:.6f}")
    steps.append(f"x_n = {x_n:.6f} cm")
    steps.append(f"I_fess = {i_fess:.6f} cm4")
    steps.append(f"sigma_c,rara = {sigma_c_rara:.4f} kgf/cm2")
    steps.append(f"sigma_c,qp = {sigma_c_qp:.4f} kgf/cm2")
    steps.append(f"sigma_s = {sigma_s_rara:.4f} kgf/cm2")
    steps.append(f"w_k = {w_k_mm:.4f} mm (limite {w_lim_mm:.3f} mm)")

    if sigma_c_rara > sigma_c_rara_lim:
        _push_warning(warnings, steps, "X4-SLE-001", "Superata tensione cls in combinazione rara.")
    if sigma_c_qp > sigma_c_qp_lim:
        _push_warning(
            warnings,
            steps,
            "X4-SLE-002",
            "Superata tensione cls in combinazione quasi-permanente.",
        )
    if w_k_mm > w_lim_mm:
        _push_warning(warnings, steps, "X4-SLE-003", "Apertura fessura superiore al limite.")
    if sigma_s_rara > sigma_s_lim:
        _push_warning(warnings, steps, "X4-SLE-004", "Superata tensione acciaio in esercizio.")

    utilisation = max(util_c_rara, util_c_qp, util_s, util_w)
    ok = utilisation <= 1.0

    return {
        "ok": ok,
        "value": round(utilisation, 4),
        "utilisation": round(utilisation, 4),
        "details": {
            "x_n_cm": round(x_n, 6),
            "I_fess_cm4": round(i_fess, 6),
            "sigma_c_rara_kgf_cm2": round(sigma_c_rara, 6),
            "sigma_c_qp_kgf_cm2": round(sigma_c_qp, 6),
            "sigma_s_rara_kgf_cm2": round(sigma_s_rara, 6),
            "sigma_c_rara_MPa": round(sigma_c_rara * _KGF_CM2_TO_MPA, 6),
            "sigma_c_qp_MPa": round(sigma_c_qp * _KGF_CM2_TO_MPA, 6),
            "sigma_s_rara_MPa": round(sigma_s_rara * _KGF_CM2_TO_MPA, 6),
            "w_k_mm": round(w_k_mm, 6),
            "w_lim_mm": round(w_lim_mm, 6),
            "util_sigma_c_rara": round(util_c_rara, 6),
            "util_sigma_c_qp": round(util_c_qp, 6),
            "util_sigma_s": round(util_s, 6),
            "util_w_k": round(util_w, 6),
        },
        "steps": steps,
        "warnings": warnings,
        "trace": {"run_id": run_id},
        "norm_references": norm_refs,
    }


def x4_sle_vibrazioni(inputs: dict[str, Any]) -> dict[str, Any]:
    """Verifica vibrazioni/comfort con frequenza fondamentale e accelerazione RMS."""

    l_m = float(inputs.get("L_m", 0.0))
    ei_n_m2 = float(inputs.get("EI_Nm2", 0.0))
    m_kg_m = float(inputs.get("m_kg_m", 0.0))
    schema_in = str(inputs.get("schema", "appoggio_appoggio"))
    destinazione_in = str(inputs.get("destinazione", "residenziale"))
    f_ped_n = float(inputs.get("F_ped_N", 700.0))
    xi = float(inputs.get("xi", 0.02))

    norm_refs = ["NTC2018 §C7.10.5", "EN ISO 10137 §7.1", "EN ISO 10137 §C.2.1"]
    if min(l_m, ei_n_m2, m_kg_m, xi) <= 0:
        use_fallback = bool(inputs.get("use_fallback", False))
        delta_cm = float(inputs.get("delta_cm", 0.0))
        if use_fallback and delta_cm > 0:
            run_id = str(uuid.uuid4())
            steps: list[str] = []
            warnings: list[str] = []
            f_1 = 18.0 / math.sqrt(delta_cm)
            _push_warning(
                warnings,
                steps,
                "X4-VIB-FALL-001",
                "Attivata stima empirica f1≈18/sqrt(delta_cm).",
            )
            return {
                "ok": True,
                "value": round(f_1, 4),
                "utilisation": None,
                "details": {"f1_Hz": round(f_1, 6), "a_RMS_m_s2": None},
                "steps": steps,
                "warnings": warnings,
                "trace": {"run_id": run_id},
                "norm_references": norm_refs,
            }

        return _error_result(
            "Errore: parametri richiesti mancanti o non validi (L_m, EI_Nm2, m_kg_m, xi).",
            norm_refs,
        )

    run_id = str(uuid.uuid4())
    steps: list[str] = []
    warnings: list[str] = []

    schema_norm, lambda_sq = _lambda_sq_vibrazione(schema_in)
    if schema_norm != schema_in.strip().lower():
        _push_warning(
            warnings,
            steps,
            "X4-VIB-004",
            f"Schema '{schema_in}' non riconosciuto: usato appoggio_appoggio.",
        )

    soglie_hz = {
        "residenziale": 4.0,
        "uffici": 4.0,
        "palestre": 5.0,
        "passerelle": 8.0,
    }
    destinazione = destinazione_in.strip().lower()
    if destinazione not in soglie_hz:
        destinazione = "residenziale"

    f_1_hz = (lambda_sq / (2.0 * math.pi * (l_m**2))) * math.sqrt(ei_n_m2 / m_kg_m)
    soglia_f_hz = soglie_hz[destinazione]

    a_peak = f_ped_n / (xi * m_kg_m * l_m)
    a_rms = a_peak / math.sqrt(2.0)
    a_rms_lim = float(inputs.get("a_rms_lim_m_s2", 0.5))

    util_freq = soglia_f_hz / f_1_hz if f_1_hz > 0 else 999.0
    util_acc = a_rms / a_rms_lim if a_rms_lim > 0 else 999.0
    utilisation = max(util_freq, util_acc)

    steps.append(
        f"f1 = (lambda^2/(2*pi*L^2))*sqrt(EI/m) = ({lambda_sq:.6f}/(2*pi*{l_m:.3f}^2))*"
        f"sqrt({ei_n_m2:.3e}/{m_kg_m:.3f}) = {f_1_hz:.6f} Hz"
    )
    steps.append(
        f"a_peak = F/(xi*m*L) = {f_ped_n:.3f}/({xi:.4f}*{m_kg_m:.3f}*{l_m:.3f}) = {a_peak:.6f} m/s2"
    )
    steps.append(f"a_RMS = a_peak/sqrt(2) = {a_rms:.6f} m/s2")

    if f_1_hz < soglia_f_hz:
        _push_warning(
            warnings,
            steps,
            "X4-VIB-001",
            f"Frequenza fondamentale inferiore alla soglia ({soglia_f_hz:.1f} Hz).",
        )
    if a_rms > a_rms_lim:
        _push_warning(
            warnings,
            steps,
            "X4-VIB-002",
            f"Accelerazione RMS superiore al limite ({a_rms_lim:.3f} m/s2).",
        )
    if m_kg_m < float(inputs.get("m_min_kg_m", 50.0)):
        _push_warning(
            warnings, steps, "X4-VIB-003", "Massa lineare molto bassa, input da verificare."
        )

    ok = f_1_hz >= soglia_f_hz and a_rms <= a_rms_lim
    steps.append(
        f"UC_vib = max(f_lim/f1, a_RMS/a_lim) = max({util_freq:.4f}, {util_acc:.4f}) = {utilisation:.4f}"
        f" -> {'OK' if ok else 'NON OK'}"
    )

    return {
        "ok": ok,
        "value": round(f_1_hz, 4),
        "utilisation": round(utilisation, 4),
        "details": {
            "schema": schema_norm,
            "destinazione": destinazione,
            "lambda_sq": round(lambda_sq, 6),
            "f1_Hz": round(f_1_hz, 6),
            "f1_lim_Hz": round(soglia_f_hz, 6),
            "a_peak_m_s2": round(a_peak, 6),
            "a_RMS_m_s2": round(a_rms, 6),
            "a_RMS_lim_m_s2": round(a_rms_lim, 6),
            "util_freq": round(util_freq, 6),
            "util_acc": round(util_acc, 6),
        },
        "steps": steps,
        "warnings": warnings,
        "trace": {"run_id": run_id},
        "norm_references": norm_refs,
    }
