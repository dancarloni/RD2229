"""Verifiche per elementi secondari/non strutturali — NTC2018 §7.2.3.

Check SLU: forza inerziale sugli elementi non strutturali (§7.2.3)
  F_a = (S_a * W_a * gamma_a) / q_a
  dove S_a = spettro al piano, W_a = peso elemento, gamma_a e q_a da norma.

Check SLE: compatibilità con gli spostamenti interpiano (drift).
  Verifica che l'elemento tolleri il drift di progetto senza danno.
"""

from __future__ import annotations

import uuid
from typing import Any


def _base_contract() -> dict[str, Any]:
    """Restituisce un risultato base con campi obbligatori."""
    return {
        "esito": "OK",
        "decision_log": [],
        "norm_references": ["NTC2018 §7.2.3"],
        "trace": {"run_id": str(uuid.uuid4())},
    }


def check_slu(inputs: dict[str, Any]) -> dict[str, Any]:
    """Verifica SLU forza inerziale su elemento non strutturale (NTC2018 §7.2.3).

    Args:
        inputs: dizionario con chiavi:
            - W_a: peso dell'elemento [kN]
            - S_a: accelerazione spettrale al piano (rapporto a g)
            - gamma_a: coefficiente di importanza (default 1.0)
            - q_a: fattore di comportamento (default 2.0)
            - F_Rd: resistenza di progetto dell'ancoraggio [kN] (opzionale)
    """
    result = _base_contract()

    W_a = float(inputs.get("W_a", 0))
    S_a = float(inputs.get("S_a", 0))
    gamma_a = float(inputs.get("gamma_a", 1.0))
    q_a = float(inputs.get("q_a", 2.0))

    if q_a <= 0:
        q_a = 2.0

    F_a = S_a * W_a * gamma_a / q_a
    result["F_a_kN"] = round(F_a, 3)
    result["decision_log"].append(
        f"F_a = S_a({S_a}) * W_a({W_a}) * gamma_a({gamma_a}) / q_a({q_a}) = {F_a:.3f} kN"
    )

    F_Rd = inputs.get("F_Rd")
    if F_Rd is not None:
        F_Rd = float(F_Rd)
        utilisation = F_a / F_Rd if F_Rd > 0 else 999.0
        ok = F_a <= F_Rd
        result.update({
            "ok": ok,
            "utilisation": round(utilisation, 4),
            "F_Rd_kN": F_Rd,
        })
        result["decision_log"].append(
            f"F_a/F_Rd = {utilisation:.4f} → {'OK' if ok else 'NON OK'}"
        )
        if not ok:
            result["esito"] = "NON OK"
    else:
        result.update({"ok": True, "utilisation": 0.0})
        result["decision_log"].append("F_Rd non fornita: solo calcolo F_a")

    return result


def check_sle(inputs: dict[str, Any]) -> dict[str, Any]:
    """Verifica SLE compatibilità spostamenti interpiano (drift).

    Args:
        inputs: dizionario con chiavi:
            - drift: dict con source, value, limit
            - drift.source: GLOBAL | ESTIMATED | USER
            - drift.value: spostamento interpiano relativo (adimensionale)
            - drift.limit: limite ammissibile (default 0.005 per elem. fragili)
    """
    result = _base_contract()

    drift = inputs.get("drift") or {}
    src = drift.get("source")
    drift_value = drift.get("value")
    drift_limit = drift.get("limit", 0.005)  # h/200 tipico per elem. fragili

    if src == "ESTIMATED":
        result.setdefault("messages", []).append(
            "Drift stimato; confidence forzata a LOW"
        )
        result["decision_log"].append("drift source=ESTIMATED, confidence=LOW")
        result["confidence"] = "LOW"
    else:
        result["decision_log"].append(f"drift source={src}")

    if drift_value is not None and drift_limit is not None:
        drift_value = float(drift_value)
        drift_limit = float(drift_limit)
        utilisation = drift_value / drift_limit if drift_limit > 0 else 999.0
        ok = drift_value <= drift_limit
        result.update({
            "ok": ok,
            "utilisation": round(utilisation, 4),
            "drift_value": drift_value,
            "drift_limit": drift_limit,
        })
        result["decision_log"].append(
            f"drift = {drift_value:.5f}, limit = {drift_limit:.5f}, "
            f"util = {utilisation:.4f} → {'OK' if ok else 'NON OK'}"
        )
        if not ok:
            result["esito"] = "NON OK"
    else:
        result.update({"ok": True, "utilisation": 0.0})
        result["decision_log"].append("Drift value non fornito: verifica non eseguita")

    return result


# Alias legacy
check_parapet = check_slu
check_partition = check_sle
