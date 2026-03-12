"""Amplificazione omega biassiale per pressoflessione deviata (FASE J).

Calcola omega_x, omega_y e amplifica Mx, My usando:
  - omega_ca() da src/methods/rd2229/instabilita.py
  - Carico critico Euleriano per ciascun piano
  - Coefficiente alpha_M = 1/(1 - |N|/Pcr)

Unita': cm, kg/cm², kg, kg·cm.
"""

from __future__ import annotations

import math
from typing import Any

from src.codes.section_params.omogenizzata import BarraArmatura
from src.methods.rd2229.instabilita import omega_ca

from .base import calcola_omogenizzata_biassiale


def amplifica_momenti_biassiale(
    N_kg: float,
    Mx_kgcm: float,
    My_kgcm: float,
    section: Any,
    barre: list[BarraArmatura],
    n: float,
    l0_x_cm: float,
    l0_y_cm: float,
    sigma_c_adm: float,
    E_c_kgcm2: float = 250000.0,
) -> tuple[float, float, float, float, dict[str, Any]]:
    """Calcola omega e amplifica momenti per instabilita' biassiale.

    1. Calcola I_x_om, I_y_om, A_om tramite calcola_omogenizzata_biassiale
    2. r_x = sqrt(I_x/A_om), r_y = sqrt(I_y/A_om)
    3. lambda_x = l0_x / r_x, lambda_y = l0_y / r_y
    4. omega_x = omega_ca(lambda_x), omega_y = omega_ca(lambda_y)
    5. Pcr_x = pi² * 0.4*Ec * I_x / l0_x², Pcr_y analoga
    6. alpha_Mx = 1/(1 - |N|/Pcr_x), alpha_My analoga
    7. Mx_amp = alpha_Mx * |Mx|, My_amp = alpha_My * |My|

    Args:
        N_kg: sforzo normale [kg] (positivo = compressione)
        Mx_kgcm: momento attorno x [kg·cm]
        My_kgcm: momento attorno y [kg·cm]
        section: oggetto sezione
        barre: lista armature
        n: rapporto di omogeneizzazione
        l0_x_cm: lunghezza libera di inflessione piano xz [cm]
        l0_y_cm: lunghezza libera di inflessione piano xy [cm]
        sigma_c_adm: tensione ammissibile [kg/cm²]
        E_c_kgcm2: modulo elastico cls [kg/cm²]

    Returns:
        (omega_x, omega_y, Mx_amplificato, My_amplificato, details)
    """
    props = calcola_omogenizzata_biassiale(section, barre, n)
    if props.get("esito") != "OK":
        return 1.0, 1.0, abs(Mx_kgcm), abs(My_kgcm), {"errore": "props non calcolabili"}

    A_om = props["A_om_cm2"]
    I_x = props["I_x_om_cm4"]
    I_y = props["I_y_om_cm4"]

    # Raggi d'inerzia
    r_x = math.sqrt(I_x / A_om) if A_om > 0 and I_x > 0 else 1.0
    r_y = math.sqrt(I_y / A_om) if A_om > 0 and I_y > 0 else 1.0

    # Snellezze
    lambda_x = l0_x_cm / r_x if r_x > 0 else 0.0
    lambda_y = l0_y_cm / r_y if r_y > 0 else 0.0

    # Coefficienti omega
    w_x = omega_ca(lambda_x)
    w_y = omega_ca(lambda_y)

    # Carichi critici Euleriani (0.4*Ec per viscosita')
    E_rid = 0.4 * E_c_kgcm2
    Pcr_x = math.pi**2 * E_rid * I_x / l0_x_cm**2 if l0_x_cm > 0 else float("inf")
    Pcr_y = math.pi**2 * E_rid * I_y / l0_y_cm**2 if l0_y_cm > 0 else float("inf")

    # Coefficienti amplificazione momento
    N_abs = abs(N_kg)
    if N_abs < Pcr_x and Pcr_x > 0:
        alpha_Mx = 1.0 / (1.0 - N_abs / Pcr_x)
    else:
        alpha_Mx = 10.0  # sezione da riprogettare

    if N_abs < Pcr_y and Pcr_y > 0:
        alpha_My = 1.0 / (1.0 - N_abs / Pcr_y)
    else:
        alpha_My = 10.0

    Mx_amp = alpha_Mx * abs(Mx_kgcm)
    My_amp = alpha_My * abs(My_kgcm)

    details = {
        "lambda_x": round(lambda_x, 1),
        "lambda_y": round(lambda_y, 1),
        "omega_x": round(w_x, 4),
        "omega_y": round(w_y, 4),
        "Pcr_x_kg": round(Pcr_x, 0) if Pcr_x != float("inf") else None,
        "Pcr_y_kg": round(Pcr_y, 0) if Pcr_y != float("inf") else None,
        "alpha_Mx": round(alpha_Mx, 4),
        "alpha_My": round(alpha_My, 4),
        "r_x_cm": round(r_x, 4),
        "r_y_cm": round(r_y, 4),
    }

    return w_x, w_y, Mx_amp, My_amp, details
