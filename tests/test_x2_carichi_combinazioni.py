import json
from pathlib import Path
from typing import Any, cast

import pytest

from src.core_calculus.carichi_combinazioni import process_carichi_combinazioni


def load_fixture() -> dict[str, Any]:
    fixture = Path(__file__).resolve().parent / "fixtures" / "carichi_combinazioni_valid.json"
    data = cast(dict[str, Any], json.loads(fixture.read_text(encoding="utf-8")))
    return data


def _has_warning(payload: dict, code: str) -> bool:
    return any(w.get("code") == code for w in payload.get("warnings", []))


def test_x2_t01_generate_slu_sle_base():
    data = load_fixture()
    out = process_carichi_combinazioni(data)

    assert out["meta"]["unit_system_detected"] == "legacy_kgf_m2"
    assert out["normalized"]["G1_kN_m2"] == pytest.approx(2.942, rel=1e-3)

    combo_types = {item["type"] for item in out["combinations"]}
    assert "SLU" in combo_types
    assert "SLE_rara" in combo_types
    assert "SLE_frequente" in combo_types
    assert "SLE_quasi_permanente" in combo_types


def test_x2_t02_lc_fc_is_applied():
    data = load_fixture()
    out = process_carichi_combinazioni(data)

    assert out["lc_fc"] is not None
    assert out["lc_fc"]["f_ck_adjusted"] == pytest.approx(25.0 / 1.2, rel=1e-9)
    assert _has_warning(out, "X2-LC-001")


def test_x2_t03_unknown_category_fallback_warning():
    data = load_fixture()
    data["categoria"] = "cat_Z"
    out = process_carichi_combinazioni(data)

    assert _has_warning(out, "X2-COMB-002")
    assert out["normalized"]["variable_loads"][0]["category"] == "cat_A"


def test_x2_t04_missing_area_warning():
    data = load_fixture()
    data.pop("area_influenza_m2", None)
    out = process_carichi_combinazioni(data)

    assert _has_warning(out, "X2-AREA-001")


def test_x2_t05_missing_variable_loads_fallback_permanenti_warning():
    data = load_fixture()
    data.pop("Q", None)
    out = process_carichi_combinazioni(data)

    assert _has_warning(out, "X2-COMB-003")
    combo_names = {item["name"] for item in out["combinations"]}
    assert "SLU_PERM" in combo_names
    assert "SLE_QP" in combo_names


def test_multi_variable_loads_supported():
    data = load_fixture()
    data.pop("Q", None)
    data["variable_loads"] = [
        {"name": "Q_uso", "value": 2.0, "category": "cat_A"},
        {"name": "neve", "value": 0.8, "category": "neve_leq_1000"},
    ]
    out = process_carichi_combinazioni(data)

    assert not _has_warning(out, "X2-COMB-003")
    assert len(out["normalized"]["variable_loads"]) == 2
    assert len(out["combinations"]) >= 5


def test_si_input_is_not_converted_again():
    data = load_fixture()
    data.update({"unit_system": "si", "G1": 2.5, "G2": 1.2, "Q": 3.0})
    out = process_carichi_combinazioni(data)

    assert out["meta"]["unit_system_detected"] == "si"
    assert out["normalized"]["G1_kN_m2"] == pytest.approx(2.5, rel=1e-12)


def test_lc_fc_missing_materials_warns_not_fails():
    data = load_fixture()
    data["lc"] = "LC2"
    data["fc"] = 1.2
    data.pop("materiali", None)
    out = process_carichi_combinazioni(data)

    assert out["lc_fc"] is None
    assert _has_warning(out, "X2-LC-002")
