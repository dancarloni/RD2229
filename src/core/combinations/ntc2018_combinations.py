"""Generatore combinazioni di carico NTC2018 (§2.5.3).

Genera combinazioni SLU e SLE a partire da carichi permanenti (G)
e variabili (Q) con i coefficienti parziali e di combinazione della norma.

Combinazioni implementate:
- SLU fondamentale (§2.5.3, eq. 2.5.1)
- SLE rara (§2.5.3, eq. 2.5.2)
- SLE frequente (§2.5.3, eq. 2.5.3)
- SLE quasi permanente (§2.5.3, eq. 2.5.4)
- SLU sismica (§2.5.3, eq. 2.5.5)

Coefficienti psi da Tab. 2.5.I NTC2018.
Coefficienti gamma da Tab. 2.6.I NTC2018.
"""

from __future__ import annotations

from typing import Any


# Coefficienti parziali NTC2018 Tab. 2.6.I (valori default, sovrascrivibili)
DEFAULT_GAMMA = {
    "gamma_G1": 1.3,       # permanenti strutturali (sfavorevole)
    "gamma_G1_fav": 1.0,   # permanenti strutturali (favorevole)
    "gamma_G2": 1.5,       # permanenti non strutturali (sfavorevole)
    "gamma_G2_fav": 0.0,   # permanenti non strutturali (favorevole)
    "gamma_Q": 1.5,        # variabili (sfavorevole)
    "gamma_Q_fav": 0.0,    # variabili (favorevole)
}

# Coefficienti psi NTC2018 Tab. 2.5.I
DEFAULT_PSI = {
    "cat_A": {"psi_0": 0.7, "psi_1": 0.5, "psi_2": 0.3},
    "cat_B": {"psi_0": 0.7, "psi_1": 0.5, "psi_2": 0.3},
    "cat_C": {"psi_0": 0.7, "psi_1": 0.7, "psi_2": 0.6},
    "cat_D": {"psi_0": 0.7, "psi_1": 0.7, "psi_2": 0.6},
    "cat_E": {"psi_0": 1.0, "psi_1": 0.9, "psi_2": 0.8},
    "cat_F": {"psi_0": 0.7, "psi_1": 0.7, "psi_2": 0.6},
    "cat_G": {"psi_0": 0.7, "psi_1": 0.5, "psi_2": 0.3},
    "cat_H": {"psi_0": 0.0, "psi_1": 0.0, "psi_2": 0.0},
    "vento": {"psi_0": 0.6, "psi_1": 0.2, "psi_2": 0.0},
    "neve_leq_1000": {"psi_0": 0.5, "psi_1": 0.2, "psi_2": 0.0},
    "neve_gt_1000": {"psi_0": 0.7, "psi_1": 0.5, "psi_2": 0.2},
    "temperatura": {"psi_0": 0.6, "psi_1": 0.5, "psi_2": 0.0},
}


def _get_psi(category: str, psi_key: str) -> float:
    """Restituisce il coefficiente psi per una categoria di azione variabile."""
    cat_psi = DEFAULT_PSI.get(category, DEFAULT_PSI.get("cat_A", {}))
    return cat_psi.get(psi_key, 0.7)


def generate_slu_combinations(inputs: dict[str, Any]) -> list[dict[str, Any]]:
    """Genera combinazioni SLU fondamentali (NTC2018 §2.5.3 eq. 2.5.1).

    gamma_G1*G1 + gamma_G2*G2 + gamma_Q*(Q_k1 + sum(psi_0i*Q_ki))

    Args:
        inputs: dizionario con chiavi:
            - G1: carichi permanenti strutturali [qualsiasi unità]
            - G2: carichi permanenti non strutturali (default 0)
            - variable_loads: lista di dict con {name, value, category}
            - gamma: dict di override per coefficienti gamma (opzionale)

    Returns:
        lista di combinazioni, ciascuna con name, factors, total
    """
    G1 = float(inputs.get("G1", 0))
    G2 = float(inputs.get("G2", 0))
    variable_loads = inputs.get("variable_loads", [])
    gamma = {**DEFAULT_GAMMA, **(inputs.get("gamma", {}) or {})}

    combinations: list[dict[str, Any]] = []

    if not variable_loads:
        # Solo permanenti
        total = gamma["gamma_G1"] * G1 + gamma["gamma_G2"] * G2
        combinations.append({
            "name": "SLU_PERM",
            "type": "SLU",
            "factors": {"G1": gamma["gamma_G1"], "G2": gamma["gamma_G2"]},
            "total": round(total, 4),
        })
        return combinations

    # Ogni carico variabile come dominante
    for i, q_dom in enumerate(variable_loads):
        name_dom = q_dom.get("name", f"Q{i + 1}")
        val_dom = float(q_dom.get("value", 0))
        cat_dom = q_dom.get("category", "cat_A")

        factors: dict[str, float] = {
            "G1": gamma["gamma_G1"],
            "G2": gamma["gamma_G2"],
            name_dom: gamma["gamma_Q"],
        }
        total = gamma["gamma_G1"] * G1 + gamma["gamma_G2"] * G2 + gamma["gamma_Q"] * val_dom

        for j, q_acc in enumerate(variable_loads):
            if j == i:
                continue
            name_acc = q_acc.get("name", f"Q{j + 1}")
            val_acc = float(q_acc.get("value", 0))
            cat_acc = q_acc.get("category", "cat_A")
            psi_0 = _get_psi(cat_acc, "psi_0")
            factors[name_acc] = round(gamma["gamma_Q"] * psi_0, 4)
            total += gamma["gamma_Q"] * psi_0 * val_acc

        combinations.append({
            "name": f"SLU_{name_dom}_dom",
            "type": "SLU",
            "dominant_action": name_dom,
            "factors": factors,
            "total": round(total, 4),
        })

    return combinations


def generate_sle_combinations(inputs: dict[str, Any]) -> list[dict[str, Any]]:
    """Genera combinazioni SLE (rara, frequente, quasi permanente).

    NTC2018 §2.5.3:
    - Rara:             G1 + G2 + Q_k1 + sum(psi_0i * Q_ki)
    - Frequente:        G1 + G2 + psi_11 * Q_k1 + sum(psi_2i * Q_ki)
    - Quasi permanente: G1 + G2 + sum(psi_2i * Q_ki)

    Args:
        inputs: dizionario con chiavi G1, G2, variable_loads (come SLU)

    Returns:
        lista di combinazioni SLE
    """
    G1 = float(inputs.get("G1", 0))
    G2 = float(inputs.get("G2", 0))
    variable_loads = inputs.get("variable_loads", [])

    combinations: list[dict[str, Any]] = []

    # --- Quasi permanente (sempre una sola) ---
    factors_qp: dict[str, float] = {"G1": 1.0, "G2": 1.0}
    total_qp = G1 + G2
    for q in variable_loads:
        name = q.get("name", "Q")
        val = float(q.get("value", 0))
        cat = q.get("category", "cat_A")
        psi_2 = _get_psi(cat, "psi_2")
        factors_qp[name] = psi_2
        total_qp += psi_2 * val
    combinations.append({
        "name": "SLE_QP",
        "type": "SLE_quasi_permanente",
        "factors": factors_qp,
        "total": round(total_qp, 4),
    })

    if not variable_loads:
        return combinations

    # --- Rara e Frequente (una per ogni carico dominante) ---
    for i, q_dom in enumerate(variable_loads):
        name_dom = q_dom.get("name", f"Q{i + 1}")
        val_dom = float(q_dom.get("value", 0))
        cat_dom = q_dom.get("category", "cat_A")

        # Rara
        factors_r: dict[str, float] = {"G1": 1.0, "G2": 1.0, name_dom: 1.0}
        total_r = G1 + G2 + val_dom
        for j, q_acc in enumerate(variable_loads):
            if j == i:
                continue
            name_acc = q_acc.get("name", f"Q{j + 1}")
            val_acc = float(q_acc.get("value", 0))
            cat_acc = q_acc.get("category", "cat_A")
            psi_0 = _get_psi(cat_acc, "psi_0")
            factors_r[name_acc] = psi_0
            total_r += psi_0 * val_acc
        combinations.append({
            "name": f"SLE_RARA_{name_dom}_dom",
            "type": "SLE_rara",
            "dominant_action": name_dom,
            "factors": factors_r,
            "total": round(total_r, 4),
        })

        # Frequente
        psi_1_dom = _get_psi(cat_dom, "psi_1")
        factors_f: dict[str, float] = {"G1": 1.0, "G2": 1.0, name_dom: psi_1_dom}
        total_f = G1 + G2 + psi_1_dom * val_dom
        for j, q_acc in enumerate(variable_loads):
            if j == i:
                continue
            name_acc = q_acc.get("name", f"Q{j + 1}")
            val_acc = float(q_acc.get("value", 0))
            cat_acc = q_acc.get("category", "cat_A")
            psi_2 = _get_psi(cat_acc, "psi_2")
            factors_f[name_acc] = psi_2
            total_f += psi_2 * val_acc
        combinations.append({
            "name": f"SLE_FREQ_{name_dom}_dom",
            "type": "SLE_frequente",
            "dominant_action": name_dom,
            "factors": factors_f,
            "total": round(total_f, 4),
        })

    return combinations


def generate_serviceability_combinations(inputs: dict[str, Any]) -> list[dict[str, Any]]:
    """Genera tutte le combinazioni SLE (rara + frequente + quasi permanente).

    Wrapper di compatibilità con l'interfaccia originale skeleton.
    """
    return generate_sle_combinations(inputs)


def generate_all_combinations(inputs: dict[str, Any]) -> list[dict[str, Any]]:
    """Genera tutte le combinazioni (SLU + SLE)."""
    return generate_slu_combinations(inputs) + generate_sle_combinations(inputs)
