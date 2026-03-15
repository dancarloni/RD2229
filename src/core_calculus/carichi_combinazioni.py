"""Fase X2 - Carichi e combinazioni NTC2018.

Modulo orchestratore per:
- normalizzazione carichi (legacy kgf/m2 o SI kN/m2)
- generazione combinazioni SLU/SLE
- applicazione opzionale LC/FC su materiali esistenti
- emissione warning codificati X2
"""

from __future__ import annotations

import dataclasses
import json
import pkgutil
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from src.core.combinations.ntc2018_combinations import (
    DEFAULT_GAMMA,
    DEFAULT_PSI,
    generate_all_combinations,
)
from src.core.registro_log import registro
from src.core_calculus.lc_fc_adjustments import apply_lc_fc_adjustments
from src.core_calculus.units import kgf_m2_to_kn_m2

_MODULO_LOG = "core_calculus.carichi_combinazioni"
_DEFAULT_CATEGORY = "cat_A"


def _repo_data_path(relative_path: str) -> Path:
    return Path(__file__).resolve().parents[2] / relative_path


def _load_json_data(relative_path: str) -> Any:
    package_name = __name__.split(".")[0]
    try:
        raw = pkgutil.get_data(package_name, relative_path)
    except FileNotFoundError:
        raw = None
    if raw is not None:
        return json.loads(raw.decode("utf-8"))

    path = _repo_data_path(relative_path)
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))

    raise RuntimeError(f"File dati non trovato: {relative_path}")


def _warn(code: str, field: str, message_it: str) -> dict[str, Any]:
    return {
        "severity": "warning",
        "code": code,
        "field": field,
        "message_it": message_it,
    }


def _looks_legacy_load(value: float) -> bool:
    # Soglia pratica: in kN/m2 i valori tipici d'uso sono spesso << 20,
    # mentre in kgf/m2 carichi tipici (200-500) sono molto maggiori.
    return value > 20.0


def _detect_unit_system(data: dict[str, Any]) -> str:
    unit_system = str(data.get("unit_system", "auto") or "auto").strip().lower()
    if unit_system in {"legacy_kgf_m2", "si"}:
        return unit_system

    values: list[float] = []
    for key in ("G1", "G2", "Q"):
        val = data.get(key)
        if val is not None:
            values.append(float(val))

    for q in data.get("variable_loads", []) or []:
        values.append(float((q or {}).get("value", 0.0)))

    if not values:
        return "si"
    return "legacy_kgf_m2" if max(values) > 20.0 else "si"


def _coerce_category(value: str | None, warnings: list[dict[str, Any]], field: str) -> str:
    allowed = set(DEFAULT_PSI.keys())

    if value is None or not str(value).strip():
        warnings.append(
            _warn(
                "X2-COMB-001",
                field,
                "Categoria d'uso assente: applicata categoria di default cat_A.",
            )
        )
        return _DEFAULT_CATEGORY

    raw = str(value).strip()
    if raw in allowed:
        return raw

    upper = raw.upper()
    if len(upper) == 1 and upper in "ABCDEFGH":
        mapped = f"cat_{upper}"
        if mapped in allowed:
            return mapped

    warnings.append(
        _warn(
            "X2-COMB-002",
            field,
            f"Categoria '{raw}' non mappata: applicata categoria di fallback cat_A.",
        )
    )
    return _DEFAULT_CATEGORY


def _build_psi_gamma_from_params() -> tuple[dict[str, dict[str, float]], dict[str, float]]:
    try:
        raw = _load_json_data("src/codes/params/NTC2018.json")
    except RuntimeError:
        return DEFAULT_PSI.copy(), DEFAULT_GAMMA.copy()

    psi_out = DEFAULT_PSI.copy()
    gamma_out = DEFAULT_GAMMA.copy()

    coeffs = raw.get("combination_coefficients", {}) if isinstance(raw, dict) else {}
    if isinstance(coeffs, dict):
        for key, values in coeffs.items():
            if not isinstance(values, dict):
                continue
            canonical = _canonical_category_key(key)
            if canonical:
                psi_out[canonical] = {
                    "psi_0": float(
                        values.get("psi_0", psi_out.get(canonical, {}).get("psi_0", 0.7))
                    ),
                    "psi_1": float(
                        values.get("psi_1", psi_out.get(canonical, {}).get("psi_1", 0.5))
                    ),
                    "psi_2": float(
                        values.get("psi_2", psi_out.get(canonical, {}).get("psi_2", 0.3))
                    ),
                }

    partial = raw.get("partial_factors", {}) if isinstance(raw, dict) else {}
    if isinstance(partial, dict):
        for gamma_key in DEFAULT_GAMMA:
            if gamma_key in partial:
                gamma_out[gamma_key] = float(partial[gamma_key])

    return psi_out, gamma_out


def _canonical_category_key(raw_key: str) -> str | None:
    if raw_key.startswith("cat_"):
        letter = raw_key.split("_", maxsplit=2)[1].upper()
        if letter in "ABCDEFGH":
            return f"cat_{letter}"
    mapping = {
        "vento": "vento",
        "neve_quota_leq_1000": "neve_leq_1000",
        "neve_quota_gt_1000": "neve_gt_1000",
        "temperatura": "temperatura",
    }
    return mapping.get(raw_key)


def normalize_loads(data: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]], str]:
    """Normalizza carichi e categorie in formato atteso dal generatore combinazioni."""

    warnings: list[dict[str, Any]] = []
    unit_system = _detect_unit_system(data)
    converter = kgf_m2_to_kn_m2 if unit_system == "legacy_kgf_m2" else float

    g1 = converter(float(data.get("G1", 0.0)))
    g2 = converter(float(data.get("G2", 0.0)))

    variable_loads_raw = data.get("variable_loads")
    variable_loads_norm: list[dict[str, Any]] = []

    if isinstance(variable_loads_raw, list) and variable_loads_raw:
        for idx, item in enumerate(variable_loads_raw, start=1):
            row = item or {}
            name = str(row.get("name") or f"Q{idx}")
            val = converter(float(row.get("value", 0.0)))
            cat = _coerce_category(
                row.get("category"), warnings, f"variable_loads[{idx - 1}].category"
            )
            variable_loads_norm.append({"name": name, "value": val, "category": cat})
    elif data.get("Q") is not None:
        q_value = converter(float(data.get("Q", 0.0)))
        cat = _coerce_category(data.get("categoria"), warnings, "categoria")
        variable_loads_norm.append({"name": "Q", "value": q_value, "category": cat})
    else:
        warnings.append(
            _warn(
                "X2-COMB-003",
                "Q|variable_loads",
                "Nessun carico variabile fornito: generate combinazioni con soli permanenti.",
            )
        )

    if data.get("area_influenza_m2") is None:
        warnings.append(
            _warn(
                "X2-AREA-001",
                "area_influenza_m2",
                "Area di influenza non fornita: uso input manuale rimandato a Fase Y.",
            )
        )

    normalized = {
        "G1_kN_m2": g1,
        "G2_kN_m2": g2,
        "variable_loads": variable_loads_norm,
        "area_influenza_m2": data.get("area_influenza_m2"),
    }
    return normalized, warnings, unit_system


def _apply_optional_lc_fc(
    data: dict[str, Any], warnings: list[dict[str, Any]]
) -> dict[str, Any] | None:
    lc = data.get("lc")
    fc = data.get("fc")
    if lc is None or fc is None:
        return None

    materiali = data.get("materiali") if isinstance(data.get("materiali"), dict) else {}
    f_ck = materiali.get("f_ck")
    f_yk = materiali.get("f_yk")
    if f_ck is None or f_yk is None:
        warnings.append(
            _warn(
                "X2-LC-002",
                "materiali",
                "LC/FC presenti ma materiali incompleti (f_ck, f_yk): applicazione LC/FC non eseguita.",
            )
        )
        return None

    material_proxy = SimpleNamespace(f_ck=float(f_ck), f_yk=float(f_yk))
    try:
        adjusted = apply_lc_fc_adjustments(material_proxy, lc=str(lc), fc=float(fc))
    except ValueError as exc:
        warnings.append(_warn("X2-LC-002", "lc_fc", f"LC/FC non applicato: {exc}"))
        return None

    warnings.append(
        _warn(
            "X2-LC-001",
            "lc_fc",
            f"Applicato fattore di confidenza FC={float(fc):.2f} per livello {lc}.",
        )
    )
    return dataclasses.asdict(adjusted)


def process_carichi_combinazioni(data: dict[str, Any]) -> dict[str, Any]:
    """Esegue il flusso X2 completo e restituisce payload pronto per pipeline X3."""

    registro.debug(_MODULO_LOG, "Avvio processazione carichi e combinazioni (X2)")

    normalized, warnings, unit_system = normalize_loads(data)
    psi_table, gamma_table = _build_psi_gamma_from_params()

    combo_input = {
        "G1": normalized["G1_kN_m2"],
        "G2": normalized["G2_kN_m2"],
        "variable_loads": normalized["variable_loads"],
        "gamma": gamma_table,
        "psi": psi_table,
    }
    combinations = generate_all_combinations(combo_input)

    lc_fc_data = _apply_optional_lc_fc(data, warnings)

    result = {
        "meta": {
            "norma": "NTC2018",
            "unit_system_input": str(data.get("unit_system", "auto") or "auto"),
            "unit_system_detected": unit_system,
        },
        "normalized": normalized,
        "combinations": combinations,
        "lc_fc": lc_fc_data,
        "warnings": warnings,
    }

    registro.calcolo(
        modulo=_MODULO_LOG,
        operazione="Generazione combinazioni carico X2",
        input_dati={
            "G1": data.get("G1"),
            "G2": data.get("G2"),
            "has_variable_loads": bool(normalized["variable_loads"]),
        },
        output_dati={
            "n_combinations": len(combinations),
            "n_warnings": len(warnings),
            "unit_system_detected": unit_system,
        },
        normativa="NTC2018 §2.5.3, Tab. 2.5.I, Tab. 2.6.I; NTC2018 §8.5.4",
        passaggi=[
            "Carichi normalizzati",
            "Coefficienti psi/gamma caricati",
            "Combinazioni SLU/SLE generate",
            "LC/FC opzionale valutato",
        ],
        esito="VERIFICATO",
    )
    return result
