"""Verifica V_Rd,c (resistenza a taglio senza armatura trasversale).

Formula NTC2018 §4.1.2.1.3.1 / EC2 §6.2.2:
  V_Rd,c = [C_Rd,c * k * (100 * rho_l * f_ck)^(1/3) + k_1 * sigma_cp] * b_w * d
  V_Rd,c >= (v_min + k_1 * sigma_cp) * b_w * d

Parametri:
  - C_Rd,c = 0.18 / gamma_c
  - k = min(1 + sqrt(200/d), 2.0) con d in mm
  - rho_l = A_sl / (b_w * d) <= 0.02
  - sigma_cp = N_Ed / A_c  (> 0 se compressione)
  - k_1 = 0.15
  - v_min = 0.035 * k^1.5 * f_ck^0.5

Unità: forze in N, lunghezze in mm, tensioni in MPa.
"""

from __future__ import annotations

import math
import uuid


def vrdc_no_stirrups(inputs: dict) -> dict:
    """Calcola V_Rd,c (senza staffe) secondo NTC2018 §4.1.2.1.3.1.

    Args:
        inputs: dizionario con chiavi:
            - b_w_mm: larghezza anima [mm]
            - d_mm: altezza utile [mm]
            - A_sl_mm2: area armatura longitudinale tesa [mm²]
            - f_ck_MPa: resistenza caratteristica calcestruzzo [MPa]
            - N_Ed_N: sforzo normale di progetto [N] (positivo = compressione)
            - A_c_mm2: area lorda della sezione [mm²]
            - gamma_c: coefficiente parziale calcestruzzo (default 1.5)
            - V_Ed_N: taglio agente di progetto [N] (opzionale, per calcolo utilizzazione)

    Returns:
        dict con: ok, value (V_Rd_c in N), steps, utilisation, details, trace, norm_references
    """
    run_id = str(uuid.uuid4())
    steps: list[str] = []

    # Estrazione parametri
    b_w = float(inputs.get("b_w_mm", 0))
    d = float(inputs.get("d_mm", 0))
    A_sl = float(inputs.get("A_sl_mm2", 0))
    f_ck = float(inputs.get("f_ck_MPa", 25))
    N_Ed = float(inputs.get("N_Ed_N", 0))
    A_c = float(inputs.get("A_c_mm2", 0))
    gamma_c = float(inputs.get("gamma_c", 1.5))
    V_Ed = float(inputs.get("V_Ed_N", 0))

    if b_w <= 0 or d <= 0:
        return {
            "ok": False,
            "value": None,
            "steps": ["Errore: b_w e d devono essere > 0"],
            "trace": {"run_id": run_id},
            "norm_references": ["NTC2018 §4.1.2.1.3.1"],
        }

    # C_Rd,c
    C_Rd_c = 0.18 / gamma_c
    steps.append(f"C_Rd,c = 0.18 / {gamma_c} = {C_Rd_c:.4f}")

    # k
    k = min(1.0 + math.sqrt(200.0 / d), 2.0)
    steps.append(f"k = min(1 + sqrt(200/{d:.0f}), 2.0) = {k:.4f}")

    # rho_l
    rho_l = A_sl / (b_w * d) if (b_w * d) > 0 else 0.0
    rho_l = min(rho_l, 0.02)
    steps.append(f"rho_l = min(A_sl/(b_w*d), 0.02) = {rho_l:.5f}")

    # sigma_cp
    k_1 = 0.15
    sigma_cp = N_Ed / A_c if A_c > 0 else 0.0
    sigma_cp = min(sigma_cp, 0.2 * f_ck)  # EC2 limit
    steps.append(f"sigma_cp = min(N_Ed/A_c, 0.2*f_ck) = {sigma_cp:.3f} MPa")

    # V_Rd,c
    V_Rd_c_1 = (C_Rd_c * k * (100.0 * rho_l * f_ck) ** (1.0 / 3.0) + k_1 * sigma_cp) * b_w * d
    steps.append(f"V_Rd,c (formula) = {V_Rd_c_1:.1f} N")

    # v_min
    v_min = 0.035 * k**1.5 * f_ck**0.5
    V_Rd_c_min = (v_min + k_1 * sigma_cp) * b_w * d
    steps.append(f"V_Rd,c,min (v_min={v_min:.4f}) = {V_Rd_c_min:.1f} N")

    V_Rd_c = max(V_Rd_c_1, V_Rd_c_min)
    steps.append(f"V_Rd,c = max({V_Rd_c_1:.1f}, {V_Rd_c_min:.1f}) = {V_Rd_c:.1f} N")

    # Utilizzazione
    utilisation = None
    ok = True
    if V_Ed > 0:
        utilisation = V_Ed / V_Rd_c if V_Rd_c > 0 else 999.0
        ok = V_Ed <= V_Rd_c
        steps.append(
            f"V_Ed = {V_Ed:.1f} N, utilisation = {utilisation:.4f} → {'OK' if ok else 'NON OK'}"
        )
    else:
        steps.append("V_Ed non fornito: solo calcolo V_Rd,c")

    return {
        "ok": ok,
        "value": round(V_Rd_c, 1),
        "V_Rd_c_N": round(V_Rd_c, 1),
        "V_Rd_c_kN": round(V_Rd_c / 1000.0, 2),
        "utilisation": round(utilisation, 4) if utilisation is not None else None,
        "steps": steps,
        "details": {
            "C_Rd_c": round(C_Rd_c, 4),
            "k": round(k, 4),
            "rho_l": round(rho_l, 5),
            "sigma_cp_MPa": round(sigma_cp, 3),
            "v_min_MPa": round(v_min, 4),
        },
        "trace": {"run_id": run_id},
        "norm_references": ["NTC2018 §4.1.2.1.3.1", "EC2 §6.2.2"],
    }
