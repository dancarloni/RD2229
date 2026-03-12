"""Utility NTC2008: combinazioni di carico e amplificazione dinamica (§2.5, §3.2)."""

from __future__ import annotations

from typing import Any, cast

PSI_NTC2008: dict[str, dict[str, float]] = {
    "cat_A": {"psi_0": 0.7, "psi_1": 0.5, "psi_2": 0.3},
    "cat_B": {"psi_0": 0.7, "psi_1": 0.5, "psi_2": 0.3},
    "cat_C": {"psi_0": 0.7, "psi_1": 0.7, "psi_2": 0.6},
    "cat_D": {"psi_0": 0.7, "psi_1": 0.7, "psi_2": 0.6},
    "cat_E": {"psi_0": 1.0, "psi_1": 0.9, "psi_2": 0.8},
    "vento": {"psi_0": 0.6, "psi_1": 0.2, "psi_2": 0.0},
    "neve": {"psi_0": 0.5, "psi_1": 0.2, "psi_2": 0.0},
    "temperatura": {"psi_0": 0.6, "psi_1": 0.5, "psi_2": 0.0},
}

GAMMA_NTC2008 = {
    "gamma_G1": 1.3,
    "gamma_G2": 1.5,
    "gamma_Q": 1.5,
}


def _psi(categoria: str, key: str) -> float:
    return PSI_NTC2008.get(categoria, PSI_NTC2008["cat_A"]).get(key, 0.0)


def coefficiente_spettro_elastico_ntc2008(
    ag: float,
    T: float,
    F0: float,
    Tc_star: float,
    S: float = 1.0,
    eta: float = 1.0,
) -> float:
    """Coefficiente spettrale elastico Se(T)/g in forma semplificata NTC2008 §3.2."""
    if min(ag, F0, Tc_star, S, eta) <= 0 or T < 0:
        raise ValueError("Parametri spettrali non validi")

    Tb = Tc_star / 3.0
    Tc = Tc_star
    Td = 4.0 * Tc_star

    if T <= Tb:
        Se = ag * S * eta * (1.0 + (T / Tb) * (F0 - 1.0))
    elif T <= Tc:
        Se = ag * S * eta * F0
    elif T <= Td:
        Se = ag * S * eta * F0 * (Tc / T)
    else:
        Se = ag * S * eta * F0 * (Tc * Td / (T * T))
    return Se


def fattore_amplificazione_dinamica_ntc2008(
    ag: float,
    T: float,
    F0: float,
    Tc_star: float,
    S: float = 1.0,
    eta: float = 1.0,
) -> float:
    """Restituisce Se(T)/ag utile per confronto NTC2008-NTC2018 in workflow semplificati."""
    Se = coefficiente_spettro_elastico_ntc2008(ag=ag, T=T, F0=F0, Tc_star=Tc_star, S=S, eta=eta)
    return Se / ag


def genera_combinazioni_ntc2008(inputs: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    """Genera combinazioni SLU e SLE (rara/frequente/quasi-permanente) NTC2008 §2.5."""
    G1 = float(inputs.get("G1", 0.0))
    G2 = float(inputs.get("G2", 0.0))
    variable_loads_raw = inputs.get("variable_loads", [])
    variable_loads: list[dict[str, Any]] = [q for q in variable_loads_raw if isinstance(q, dict)]

    gamma_overrides_raw = inputs.get("gamma", {})
    gamma_overrides: dict[str, float] = {}
    if isinstance(gamma_overrides_raw, dict):
        typed_overrides = cast(dict[str, float], gamma_overrides_raw)
        gamma_overrides = {key: float(value) for key, value in typed_overrides.items()}

    gamma: dict[str, float] = {**GAMMA_NTC2008, **gamma_overrides}

    if not variable_loads:
        base = G1 + G2
        return {
            "SLU": [{"name": "SLU_PERM", "total": gamma["gamma_G1"] * G1 + gamma["gamma_G2"] * G2}],
            "SLE_rara": [{"name": "SLE_RARA_PERM", "total": base}],
            "SLE_frequente": [{"name": "SLE_FREQ_PERM", "total": base}],
            "SLE_quasi_permanente": [{"name": "SLE_QP_PERM", "total": base}],
        }

    out: dict[str, list[dict[str, Any]]] = {
        "SLU": [],
        "SLE_rara": [],
        "SLE_frequente": [],
        "SLE_quasi_permanente": [],
    }

    total_qp = G1 + G2
    for q in variable_loads:
        total_qp += _psi(q.get("category", "cat_A"), "psi_2") * float(q.get("value", 0.0))
    out["SLE_quasi_permanente"].append({"name": "SLE_QP", "total": round(total_qp, 4)})

    for i, q_dom in enumerate(variable_loads):
        name_dom = str(q_dom.get("name", f"Q{i + 1}"))
        val_dom = float(q_dom.get("value", 0.0))
        cat_dom = q_dom.get("category", "cat_A")

        total_slu = gamma["gamma_G1"] * G1 + gamma["gamma_G2"] * G2 + gamma["gamma_Q"] * val_dom
        total_rara = G1 + G2 + val_dom
        total_freq = G1 + G2 + _psi(cat_dom, "psi_1") * val_dom

        for j, q_acc in enumerate(variable_loads):
            if j == i:
                continue
            val_acc = float(q_acc.get("value", 0.0))
            cat_acc = q_acc.get("category", "cat_A")
            total_slu += gamma["gamma_Q"] * _psi(cat_acc, "psi_0") * val_acc
            total_rara += _psi(cat_acc, "psi_0") * val_acc
            total_freq += _psi(cat_acc, "psi_2") * val_acc

        out["SLU"].append({"name": f"SLU_{name_dom}_dom", "total": round(total_slu, 4)})
        out["SLE_rara"].append({"name": f"SLE_RARA_{name_dom}_dom", "total": round(total_rara, 4)})
        out["SLE_frequente"].append(
            {"name": f"SLE_FREQ_{name_dom}_dom", "total": round(total_freq, 4)}
        )

    return out
