"""Verifiche per elementi secondari — RD 2229/1939.

Il RD 2229/39 non prevede il concetto moderno di "elemento secondario"
ne di azione sismica. Per gli elementi snelli sotto carichi gravitazionali
(tramezzi, parapetti, etc.) si applica la verifica di stabilita con il
metodo delle Tensioni Ammissibili (coefficiente omega).

Check SLU (TA): verifica stabilita per elementi snelli sotto gravita.
    sigma_c = omega * N / A <= sigma_c_adm
    Riutilizza `src/methods/rd2229/instabilita.py` per lambda > 50.

Check SLE: NOT_APPLICABLE — norma pre-sismica, nessun concetto di drift.

Rif. normativo: RD 2229/39 art. 14, art. 36
"""

from __future__ import annotations

import uuid
from typing import Any


def _base_contract() -> dict[str, Any]:
    """Restituisce un risultato base con campi obbligatori."""
    return {
        "esito": "OK",
        "decision_log": [],
        "norm_references": ["RD 2229/39 art. 14", "RD 2229/39 art. 36"],
        "trace": {"run_id": str(uuid.uuid4())},
    }


def check_stabilita_ta(inputs: dict[str, Any]) -> dict[str, Any]:
    """Verifica di stabilita TA per elemento snello sotto gravita (RD2229).

    Per elementi con snellezza lambda > 50, il coefficiente omega amplifica
    la tensione di compressione. Per lambda <= 50, omega = 1.0 (nessuna
    amplificazione).

    Args:
        inputs: dizionario con chiavi:
            - N_kg: carico assiale [kg] (positivo = compressione)
            - A_cm2: area della sezione [cm2]
            - sigma_c_adm: tensione ammissibile calcestruzzo [kg/cm2]
            - lambda_snellezza: snellezza dell'elemento (opzionale)
            - h_cm: altezza libera dell'elemento [cm] (opzionale, per calcolo lambda)
            - i_min_cm: raggio d'inerzia minimo [cm] (opzionale, per calcolo lambda)

    Returns:
        Dizionario risultato con campi contratto base + sigma_c, omega, utilisation.

    Rif.: RD 2229/39 art. 14 (compressione), art. 36 (instabilita)
    """
    result = _base_contract()

    N = float(inputs.get("N_kg", 0))
    A = float(inputs.get("A_cm2", 0))
    sigma_c_adm = float(inputs.get("sigma_c_adm", 0))

    if N <= 0:
        result["esito"] = "NOT_APPLICABLE"
        result["decision_log"].append(
            "N <= 0: elemento non compresso, verifica stabilita non necessaria"
        )
        result.update({"ok": True, "utilisation": 0.0})
        return result

    if A <= 0 or sigma_c_adm <= 0:
        result["esito"] = "ERROR"
        result["decision_log"].append(
            f"Dati insufficienti: A={A} cm2, sigma_c_adm={sigma_c_adm} kg/cm2"
        )
        result.update({"ok": False, "utilisation": 999.0})
        return result

    # Calcolo snellezza
    lam = inputs.get("lambda_snellezza")
    if lam is None:
        h = float(inputs.get("h_cm", 0))
        i_min = float(inputs.get("i_min_cm", 0))
        if h > 0 and i_min > 0:
            lam = h / i_min
            result["decision_log"].append(f"lambda = h/i_min = {h}/{i_min} = {lam:.1f}")
        else:
            lam = 0.0
            result["decision_log"].append(
                "Snellezza non calcolabile (h o i_min mancanti), assunto lambda=0"
            )
    else:
        lam = float(lam)

    # Coefficiente omega — riutilizza la funzione dal modulo instabilita
    from src.methods.rd2229.instabilita import omega_ca

    omega = omega_ca(lam)
    result["omega"] = omega
    result["lambda"] = round(lam, 1)

    if lam > 140:
        result["esito"] = "NON OK"
        result["decision_log"].append(
            f"lambda = {lam:.1f} > 140: snellezza eccessiva, sezione da riprogettare"
        )
        result.update({"ok": False, "utilisation": 999.0})
        return result

    # Verifica: sigma_c = omega * N / A <= sigma_c_adm
    sigma_c = omega * N / A
    utilisation = sigma_c / sigma_c_adm

    ok = sigma_c <= sigma_c_adm
    result.update(
        {
            "ok": ok,
            "sigma_c_kgcm2": round(sigma_c, 2),
            "sigma_c_adm_kgcm2": sigma_c_adm,
            "utilisation": round(utilisation, 4),
        }
    )
    result["decision_log"].append(
        f"omega({omega:.2f}) * N({N:.0f}) / A({A:.1f}) = "
        f"sigma_c = {sigma_c:.2f} kg/cm2 "
        f"{'<=' if ok else '>'} sigma_c_adm = {sigma_c_adm:.2f} kg/cm2 "
        f"[util = {utilisation:.4f}] -> {'OK' if ok else 'NON OK'} "
        f"[RD 2229/39 art. 14]"
    )
    if not ok:
        result["esito"] = "NON OK"

    return result


def check_slu_rd2229(inputs: dict[str, Any]) -> dict[str, Any]:
    """Alias per check_stabilita_ta — interfaccia compatibile col dispatcher."""
    return check_stabilita_ta(inputs)


def check_sle_rd2229(inputs: dict[str, Any]) -> dict[str, Any]:
    """Verifica SLE — NOT_APPLICABLE per RD 2229/39.

    Il RD 2229/39 e una norma pre-sismica e non prevede verifiche SLE
    per elementi non strutturali ne compatibilita con spostamenti interpiano.
    """
    result = _base_contract()
    result["esito"] = "NOT_APPLICABLE"
    result["decision_log"].append(
        "RD 2229/39: norma pre-sismica, verifica SLE non prevista " "per elementi non strutturali"
    )
    result.update({"ok": True, "utilisation": 0.0})
    return result
