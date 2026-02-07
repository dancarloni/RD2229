"""Routines basate sui valori estratti da COPILOT_SEARCH_2229.md (R.D. 2229/1939)
Fornisce funzioni utili per calcoli elementari secondo la norma storica.
Unità: kg/cm2 per tensioni, cm per copriferri.
"""

from typing import Any, Dict, Optional


def sigma_c_amm_from_r28(sigma_r28: Optional[float], mode: str = "compression") -> float:
    """Calcola la tensione ammissibile del calcestruzzo data la resistenza a 28gg (sigma_r28).
    mode: 'compression' o 'flexure'
    Regola: sigma_c_amm = sigma_r28 / 3
    Massimi: compression -> 60 kg/cm2, flexure -> 75 kg/cm2.
    """
    if sigma_r28 is None:
        raise ValueError("sigma_r28 required")
    sigma: float = float(sigma_r28) / 3.0
    if mode == "compression":
        return min(sigma, 60.0)
    if mode == "flexure":
        return min(sigma, 75.0)
    raise ValueError("mode must be 'compression' or 'flexure'")


def steel_sigma_amm(category: str = "soft") -> float:
    """Restituisce la tensione ammissibile per l'acciaio in kg/cm2.
    category: 'soft' -> 1400, 'hard' -> 2000.
    """
    if category == "soft":
        return 1400.0
    if category == "hard":
        return 2000.0
    raise ValueError("category must be 'soft' or 'hard'")


def n_modulus_ratio(concrete_type: str = "common") -> float:
    """Restituisce il coefficiente n = Es/Ec in funzione del tipo di conglomerato.
    concrete_type: 'common'->10, 'high'->8, 'aluminous'->6.
    """
    mapping: dict[str, float] = {"common": 10.0, "high": 8.0, "aluminous": 6.0}
    return mapping.get(concrete_type, 10.0)


def shear_allowable(with_stirrups: bool = False, concrete_type: str = "ordinary") -> float:
    """Ritorna la tensione tangenziale ammissibile del calcestruzzo (kg/cm2).
    without stirrups: tau_c0 = 4 (ordinary) or 6 (high)
    with stirrups: tau_c1 = 14 (ordinary) or 16 (high).
    """
    if with_stirrups:
        return 16.0 if concrete_type == "high" else 14.0
    return 6.0 if concrete_type == "high" else 4.0


def check_cube_requirement(f_cub28: float | None, sigma_c_amm: float | None) -> tuple[bool, str]:
    """Verifica la prescrizione f_cub28 >= 3 * sigma_c_amm e i minimi assoluti (120/160).
    Restituisce una tuple (ok_bool, message).
    """
    if f_cub28 is None or sigma_c_amm is None:
        return (False, "Inputs required")
    req: float = 3.0 * float(sigma_c_amm)
    min_abs: float = 160.0 if float(sigma_c_amm) > 40.0 else 120.0
    if float(f_cub28) >= req and float(f_cub28) >= min_abs:
        return (True, f"f_cub28={f_cub28} OK (>= {req} and >= {min_abs})")
    return (False, f"f_cub28={f_cub28} NOT OK (required >= {req} and >= {min_abs})")


def flexural_resistance_rectangular(
    b: float,
    d: float,
    A_s: float,
    sigma_s_amm: Optional[float] = None,
    sigma_c_amm: Optional[float] = None,
) -> Dict[str, Any]:
    """Calcolo della resistenza a flessione di una sezione rettangolare semplicemente armata.

    Approccio: tensioni ammissibili semplificato.

    Parametri:
    - b: larghezza della sezione (cm)
    - d: braccio utile (cm) distanza dall'estremità compressa all'asse delle armature tese
    - A_s: area totale delle armature tese (cm^2)
    - sigma_s_amm: tensione ammissibile acciaio (kg/cm^2). Default: acciaio dolce 1400
    - sigma_c_amm: tensione ammissibile calcestruzzo in flessione (kg/cm^2). Default: 40 (Portland)

    Metodo (semplificato, coerente con R.D. 2229):
    - si assume che l'acciaio lavori alla σ_s,amm e il calcestruzzo in compressione alla σ_c,amm;
    - si equilibra la forza di trazione dell'acciaio con la forza di compressione equivalente nel calcestruzzo;
    - si calcola il braccio interno z = d - a/2 con a = area_comp/b;
    - momento resistente M = T * z (unità kg·cm se input in cm e kg/cm^2).
    """
    if sigma_s_amm is None:
        sigma_s_amm = steel_sigma_amm("soft")
    if sigma_c_amm is None:
        sigma_c_amm = 40.0
    # Forza in acciaio (kg)
    T: float = float(A_s) * float(sigma_s_amm)
    # area di calcestruzzo compressa richiesta (cm2)
    A_comp: float = T / float(sigma_c_amm)
    a: float = A_comp / float(b)
    if a <= 0:
        raise ValueError("Computed compression depth non-positive")
    if a > d:
        # compression block beyond neutral axis -> sezione sovraarmata o carico eccessivo
        return {
            "ok": False,
            "message": f"Compression block depth a={a:.3f} cm exceeds d={d} cm (section may be overreinforced)",
            "a": a,
            "M_res_kgcm": None,
        }
    z = d - a / 2.0
    M_res = T * z
    return {
        "ok": True,
        "a": a,
        "T_kg": T,
        "z_cm": z,
        "M_res_kgcm": M_res,
        "M_res_kNm": M_res * 9.80665e-6,  # convert kg*cm to kN·m (approx)
    }


def shear_verification(
    V_applied: float,
    b: float,
    d: float,
    concrete_type: str = "ordinary",
    with_stirrups: bool = False,
    A_v: float = 0.0,
    s: float = 0.0,
    sigma_s_amm: Optional[float] = None,
) -> Dict[str, Any]:
    """Verifica a taglio secondo valori e semplificazioni del R.D. 2229.

    Parametri:
    - V_applied: taglio agente (kg)
    - b: larghezza sezione (cm)
    - d: braccio utile (cm)
    - concrete_type: 'ordinary' or 'high' (influisce su tau_c0/tau_c1)
    - with_stirrups: se True, si considera contributo staffe
    - A_v: area totale dei ferri attivi a taglio (cm^2) per ogni piede di staffa (somma gambe che lavorano)
    - s: passo delle staffe (cm)
    - sigma_s_amm: tensione ammissibile acciaio (kg/cm^2). Default: 1400

    Metodo semplificato:
    - Capacità del calcestruzzo Vc = tau_c * b * d (kg), dove tau_c dipende da presenza staffe e tipo calcestruzzo.
    - Capacità staffe Vs = A_v * sigma_s_amm * d / s (kg) (semplificazione classica)
    - V_total = Vc + Vs
    - Confronto con V_applied
    """
    if sigma_s_amm is None:
        sigma_s_amm = steel_sigma_amm("soft")
    tau: float = shear_allowable(with_stirrups, concrete_type)
    Vc: float = float(tau) * float(b) * float(d)
    Vs = 0.0
    if with_stirrups:
        if s <= 0 or A_v <= 0:
            raise ValueError("A_v and s must be > 0 when with_stirrups is True")
        Vs: float = float(A_v) * float(sigma_s_amm) * float(d) / float(s)
    Vtot: float = Vc + Vs
    ok: bool = float(V_applied) <= Vtot
    return {
        "ok": ok,
        "V_applied_kg": float(V_applied),
        "Vc_kg": Vc,
        "Vs_kg": Vs,
        "Vtot_kg": Vtot,
        "tau_used_kg_cm2": tau,
        "notes": "Units: cm, kg, kg/cm2. Convert to SI if needed.",
    }


if __name__ == "__main__":
    # Esempi rapidi
    print(
        "Esempio: sigma_c_amm da sigma_r28=180 (compression):",
        sigma_c_amm_from_r28(180, "compression"),
    )
    print("Esempio: steel sigma amm (soft):", steel_sigma_amm("soft"))
    print("Esempio: shear without stirrups (ordinary):", shear_allowable(False, "ordinary"))
    print("Check cube 200 vs sigma amm 60:", check_cube_requirement(200, 60))
    # Esempio: resistenza sezionale
    res = flexural_resistance_rectangular(b=30, d=40, A_s=10)  # b=30cm, d=40cm, As=10cm2
    print("Flexural example:", res)
    # Esempio: verifica taglio
    shear = shear_verification(V_applied=12000, b=30, d=40, concrete_type="ordinary", with_stirrups=False)
    print("Shear example:", shear)
