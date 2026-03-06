"""Modelli di stima del drift interpiano per elementi secondari.

NTC2018 §7.2.3 richiede la verifica di compatibilita' dell'elemento
non strutturale con gli spostamenti interpiano (drift).

Metodi disponibili:
  * METODO_B   — shear-building proxy semplificato (confidence=LOW)
  * USER       — valore fornito dall'utente (confidence=HIGH)
  * GLOBAL     — valore da analisi globale FEM (confidence=HIGH)
"""

from __future__ import annotations

from typing import Any


def estimate_drift_metodo_b(
    spec: dict[str, Any], soft_storey_factor: float = 1.0
) -> dict[str, Any]:
    """Stima drift interpiano con Metodo B (shear-building proxy).

    Formula:
        delta_r = S_d_T1 * (z_m / H_m) * soft_storey_factor / h_interpiano_m

    dove:
        S_d_T1:             spostamento spettrale di progetto a T_1 [m]
        z_m:                quota interpiano considerato [m]
        H_m:                altezza totale edificio [m]
        h_interpiano_m:     altezza interpiano [m]
        soft_storey_factor: fattore amplificazione piano debole (>= 1.0)

    Args:
        spec: dizionario con le chiavi sopra elencate.
        soft_storey_factor: fattore piano debole (default 1.0).

    Returns:
        dict con chiavi:
            - drift_value: spostamento interpiano relativo (adimensionale)
            - confidence: "LOW" (stima semplificata)
            - source: "ESTIMATED"
            - method: "METODO_B"
            - decision_log: lista passaggi di calcolo
    """
    S_d = _require_positive(spec, "S_d_T1", "spostamento spettrale S_d(T_1) [m]")
    z = _require_non_negative(spec, "z_m", "quota interpiano [m]")
    H = _require_positive(spec, "H_m", "altezza totale edificio [m]")
    h = _require_positive(spec, "h_interpiano_m", "altezza interpiano [m]")

    if soft_storey_factor < 1.0:
        soft_storey_factor = 1.0

    delta_r = S_d * (z / H) * soft_storey_factor / h

    decision_log = [
        f"Metodo B: delta_r = S_d({S_d:.4f}) * (z/H)({z:.2f}/{H:.2f}) "
        f"* ssf({soft_storey_factor:.2f}) / h({h:.2f}) = {delta_r:.6f}",
        "Confidence: LOW (stima semplificata shear-building proxy)",
    ]

    return {
        "drift_value": delta_r,
        "confidence": "LOW",
        "source": "ESTIMATED",
        "method": "METODO_B",
        "decision_log": decision_log,
    }


def estimate_drift_user(value: float) -> dict[str, Any]:
    """Drift fornito dall'utente.

    Args:
        value: spostamento interpiano relativo (adimensionale, >= 0).

    Returns:
        dict con drift_value, confidence="HIGH", source="USER".
    """
    if value < 0:
        raise ValueError(f"drift_value deve essere >= 0, ricevuto {value}")

    return {
        "drift_value": value,
        "confidence": "HIGH",
        "source": "USER",
        "method": "USER",
        "decision_log": [f"Drift fornito dall'utente: {value:.6f}"],
    }


def estimate_drift_global(value: float) -> dict[str, Any]:
    """Drift da analisi globale (FEM).

    Args:
        value: spostamento interpiano relativo da analisi globale (>= 0).

    Returns:
        dict con drift_value, confidence="HIGH", source="GLOBAL".
    """
    if value < 0:
        raise ValueError(f"drift_value deve essere >= 0, ricevuto {value}")

    return {
        "drift_value": value,
        "confidence": "HIGH",
        "source": "GLOBAL",
        "method": "GLOBAL",
        "decision_log": [f"Drift da analisi globale: {value:.6f}"],
    }


# ---------------------------------------------------------------------------
# Utilita' interne
# ---------------------------------------------------------------------------

def _require_positive(spec: dict[str, Any], key: str, label: str) -> float:
    """Estrae e valida un parametro positivo dallo spec."""
    val = spec.get(key)
    if val is None:
        raise ValueError(f"Parametro '{key}' ({label}) mancante nello spec")
    val = float(val)
    if val <= 0:
        raise ValueError(f"'{key}' ({label}) deve essere > 0, ricevuto {val}")
    return val


def _require_non_negative(spec: dict[str, Any], key: str, label: str) -> float:
    """Estrae e valida un parametro non negativo dallo spec."""
    val = spec.get(key)
    if val is None:
        raise ValueError(f"Parametro '{key}' ({label}) mancante nello spec")
    val = float(val)
    if val < 0:
        raise ValueError(f"'{key}' ({label}) deve essere >= 0, ricevuto {val}")
    return val
