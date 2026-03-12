"""Verifiche per elementi secondari/non strutturali — DM 09/01/1996.

Check SLU: forza sismica orizzontale sugli elementi non strutturali.
  F_h = C * beta * W
  dove C = coefficiente sismico da zona (DM96 §3.2),
       beta = fattore di amplificazione per piano,
       W = peso dell'elemento.

Check SLE: compatibilita con gli spostamenti interpiano (drift).
  Limite tipico: h/300 (piu permissivo di NTC2018 h/200).

Rif. normativo: DM 09/01/1996 §3.2, §7.7
"""

from __future__ import annotations

import uuid
from typing import Any

from src.codes.dm96.secondary_elements.models import (
    COEFFICIENTE_SISMICO_C,
    SecondaryElementSpecDM96,
)


def _base_contract() -> dict[str, Any]:
    """Restituisce un risultato base con campi obbligatori."""
    return {
        "esito": "OK",
        "decision_log": [],
        "norm_references": ["DM 09/01/1996 §3.2", "DM 09/01/1996 §7.7"],
        "trace": {"run_id": str(uuid.uuid4())},
    }


def check_slu_dm96(inputs: dict[str, Any]) -> dict[str, Any]:
    """Verifica SLU forza sismica su elemento non strutturale (DM96).

    Args:
        inputs: dizionario con chiavi:
            - W_a o W_kN: peso dell'elemento [kN]
            - zona_sismica: 1, 2 o 3
            - piano: numero del piano (default 1)
            - n_piani: numero totale piani (default 1)
            - beta_piano: fattore amplificazione (opzionale, calcolato se assente)
            - F_Rd: resistenza di progetto dell'ancoraggio [kN] (opzionale)

    Returns:
        Dizionario risultato con campi contratto base + F_h_kN, utilisation.

    Rif.: DM 09/01/1996 §3.2 — F_h = C * beta * W
    """
    result = _base_contract()

    W = float(inputs.get("W_a", inputs.get("W_kN", 0)))
    zona = int(inputs.get("zona_sismica", 2))
    piano = int(inputs.get("piano", 1))
    n_piani = int(inputs.get("n_piani", 1))
    beta_override = inputs.get("beta_piano")

    C = COEFFICIENTE_SISMICO_C.get(zona, 0.07)

    # Fattore di amplificazione per piano
    if beta_override is not None:
        beta = float(beta_override)
    else:
        spec = SecondaryElementSpecDM96(piano=piano, n_piani=n_piani)
        beta = spec.calcola_beta_piano()

    F_h = C * beta * W

    result["F_h_kN"] = round(F_h, 3)
    result["C"] = C
    result["beta_piano"] = round(beta, 4)
    result["decision_log"].append(
        f"F_h = C({C}) * beta({beta:.4f}) * W({W}) = {F_h:.3f} kN "
        f"[DM96 §3.2, zona={zona}, piano={piano}/{n_piani}]"
    )

    F_Rd = inputs.get("F_Rd")
    if F_Rd is not None:
        F_Rd = float(F_Rd)
        utilisation = F_h / F_Rd if F_Rd > 0 else 999.0
        ok = F_h <= F_Rd
        result.update(
            {
                "ok": ok,
                "utilisation": round(utilisation, 4),
                "F_Rd_kN": F_Rd,
            }
        )
        result["decision_log"].append(f"F_h/F_Rd = {utilisation:.4f} -> {'OK' if ok else 'NON OK'}")
        if not ok:
            result["esito"] = "NON OK"
    else:
        result.update({"ok": True, "utilisation": 0.0})
        result["decision_log"].append("F_Rd non fornita: solo calcolo F_h")

    return result


def check_sle_dm96(inputs: dict[str, Any]) -> dict[str, Any]:
    """Verifica SLE compatibilita spostamenti interpiano — DM96.

    Args:
        inputs: dizionario con chiavi:
            - drift: dict con source, value, limit
            - drift.value: spostamento interpiano relativo (adimensionale)
            - drift.limit: limite ammissibile (default 0.00333 = h/300)

    Returns:
        Dizionario risultato con campi contratto base + drift_value, utilisation.

    Rif.: DM 09/01/1996 §7.7 — limite drift h/300 per elementi fragili
    """
    result = _base_contract()

    drift = inputs.get("drift") or {}
    src = drift.get("source")
    drift_value = drift.get("value")
    drift_limit = drift.get("limit", 0.00333)  # h/300

    result["decision_log"].append(f"drift source={src}, limit=h/300={drift_limit}")

    if src == "ESTIMATED":
        result.setdefault("messages", []).append("Drift stimato; confidence forzata a LOW")
        result["decision_log"].append("drift source=ESTIMATED, confidence=LOW")
        result["confidence"] = "LOW"

    if drift_value is not None and drift_limit is not None:
        drift_value = float(drift_value)
        drift_limit = float(drift_limit)
        utilisation = drift_value / drift_limit if drift_limit > 0 else 999.0
        ok = drift_value <= drift_limit
        result.update(
            {
                "ok": ok,
                "utilisation": round(utilisation, 4),
                "drift_value": drift_value,
                "drift_limit": drift_limit,
            }
        )
        result["decision_log"].append(
            f"drift = {drift_value:.5f}, limit = {drift_limit:.5f}, "
            f"util = {utilisation:.4f} -> {'OK' if ok else 'NON OK'}"
        )
        if not ok:
            result["esito"] = "NON OK"
    else:
        result.update({"ok": True, "utilisation": 0.0})
        result["decision_log"].append("Drift value non fornito: verifica non eseguita")

    return result
