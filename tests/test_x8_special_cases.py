from __future__ import annotations

import json

from src.x8_special_cases import SpecialCaseInput, evaluate_special_case
from src.x8_special_cases.x8_benchmarks import benchmark_cases
from src.x8_special_cases.x8_models import SpecialCaseType
from src.x8_special_cases.x8_warnings import X8WarningCode, make_warning


def test_make_warning_format():
    w = make_warning(
        X8WarningCode.OUT_OF_V1_SCOPE,
        message="Caso fuori V1",
        norm_ref="EN13747",
    )
    assert w.startswith("X8-SPC-001:WARN::EN13747::")


def test_predalles_strict_blocking_returns_spc003():
    data = SpecialCaseInput(
        case_type=SpecialCaseType.PREDALLES,
        norm_code="EN13747",
        span_m=5.5,
        gk_kg_m2=250,
        qk_kg_m2=200,
        height_cm=25,
    )
    result = evaluate_special_case(data, strict_blocking=True)
    assert result.blocked is True
    assert any("X8-SPC-003" in w for w in result.warnings)


def test_predalles_fallback_returns_spc002_and_values():
    data = SpecialCaseInput(
        case_type=SpecialCaseType.PREDALLES,
        span_m=5.5,
        gk_kg_m2=250,
        qk_kg_m2=200,
        height_cm=25,
    )
    result = evaluate_special_case(data, strict_blocking=False)
    assert result.blocked is False
    assert any("X8-SPC-002" in w for w in result.warnings)
    assert result.benchmark_values["q_tot_kg_m2"] == 450


def test_collaborante_strict_blocking_returns_spc003():
    data = SpecialCaseInput(
        case_type=SpecialCaseType.COLLABORANTE,
        span_m=7.2,
        gk_kg_m2=280,
        qk_kg_m2=350,
        advanced_inputs={"n_equiv": 6.0},
    )
    result = evaluate_special_case(data, strict_blocking=True)
    assert result.blocked is True
    assert any("X8-SPC-003" in w for w in result.warnings)


def test_collaborante_fallback_e_eq():
    data = SpecialCaseInput(
        case_type=SpecialCaseType.COLLABORANTE,
        span_m=7.2,
        gk_kg_m2=280,
        qk_kg_m2=350,
        advanced_inputs={"n_equiv": 7.0},
    )
    result = evaluate_special_case(data, strict_blocking=False)
    assert result.blocked is False
    assert any("X8-SPC-002" in w for w in result.warnings)
    assert result.benchmark_values["e_eq_kg_cm2"] > 0


def test_clt_strict_blocking_returns_spc003():
    data = SpecialCaseInput(
        case_type=SpecialCaseType.CLT,
        span_m=5.0,
        gk_kg_m2=160,
        qk_kg_m2=200,
        advanced_inputs={"E0_mean": 110000.0, "k_ortho": 0.35},
    )
    result = evaluate_special_case(data, strict_blocking=True)
    assert result.blocked is True
    assert any("X8-SPC-003" in w for w in result.warnings)


def test_clt_fallback_values():
    data = SpecialCaseInput(
        case_type=SpecialCaseType.CLT,
        span_m=5.0,
        gk_kg_m2=160,
        qk_kg_m2=200,
        advanced_inputs={"E0_mean": 100000.0, "k_ortho": 0.4},
    )
    result = evaluate_special_case(data, strict_blocking=False)
    assert result.blocked is False
    assert any("X8-SPC-002" in w for w in result.warnings)
    assert result.benchmark_values["e_eq_kg_cm2"] == 40000.0


def test_all_case_types_have_normative_refs():
    for case_type in (
        SpecialCaseType.PREDALLES,
        SpecialCaseType.COLLABORANTE,
        SpecialCaseType.CLT,
    ):
        data = SpecialCaseInput(case_type=case_type)
        result = evaluate_special_case(data, strict_blocking=True)
        assert len(result.normative_refs) >= 2


def test_result_to_dict_json_serializable():
    data = SpecialCaseInput(case_type=SpecialCaseType.PREDALLES)
    result = evaluate_special_case(data, strict_blocking=False)
    dumped = json.dumps(result.to_dict(), ensure_ascii=False)
    assert "predalles" in dumped


def test_benchmark_cases_count():
    cases = benchmark_cases()
    assert len(cases) == 6


def test_benchmark_cases_have_all_types():
    cases = benchmark_cases()
    types = {c.case_type for c in cases}
    assert SpecialCaseType.PREDALLES in types
    assert SpecialCaseType.COLLABORANTE in types
    assert SpecialCaseType.CLT in types


def test_snapshot_predalles_strict_output_shape():
    data = SpecialCaseInput(
        case_type=SpecialCaseType.PREDALLES,
        span_m=5.5,
        gk_kg_m2=250,
        qk_kg_m2=200,
        height_cm=25,
    )
    result = evaluate_special_case(data, strict_blocking=True)
    snap = result.to_dict()
    assert snap["case_type"] == "predalles"
    assert snap["blocked"] is True
    assert snap["benchmark_values"] == {}


def test_snapshot_clt_fallback_output_shape():
    data = SpecialCaseInput(
        case_type=SpecialCaseType.CLT,
        gk_kg_m2=160,
        qk_kg_m2=200,
        advanced_inputs={"E0_mean": 100000.0, "k_ortho": 0.4},
    )
    snap = evaluate_special_case(data, strict_blocking=False).to_dict()
    assert snap["case_type"] == "clt"
    assert snap["blocked"] is False
    assert "e_eq_kg_cm2" in snap["benchmark_values"]


def test_x8_t01_quick_reference():
    data = SpecialCaseInput(
        case_type=SpecialCaseType.PREDALLES,
        span_m=5.5,
        gk_kg_m2=250,
        qk_kg_m2=200,
    )
    result = evaluate_special_case(data, strict_blocking=True)
    assert any("X8-SPC-001" in w for w in result.warnings)


def test_x8_t02_quick_reference():
    data = SpecialCaseInput(
        case_type=SpecialCaseType.COLLABORANTE,
        span_m=7.5,
        gk_kg_m2=300,
        qk_kg_m2=300,
    )
    result = evaluate_special_case(data, strict_blocking=True)
    assert any("X8-SPC-003" in w for w in result.warnings)


def test_x8_t03_quick_reference():
    data = SpecialCaseInput(
        case_type=SpecialCaseType.CLT,
        span_m=5.5,
        gk_kg_m2=190,
        qk_kg_m2=250,
    )
    result = evaluate_special_case(data, strict_blocking=True)
    assert any("X8-SPC-003" in w for w in result.warnings)


def test_strict_mode_excludes_from_final_results_by_block_flag():
    for case_type in (
        SpecialCaseType.PREDALLES,
        SpecialCaseType.COLLABORANTE,
        SpecialCaseType.CLT,
    ):
        result = evaluate_special_case(SpecialCaseInput(case_type=case_type), strict_blocking=True)
        assert result.blocked is True


def test_fallback_mode_not_blocked_all_types():
    for case_type in (
        SpecialCaseType.PREDALLES,
        SpecialCaseType.COLLABORANTE,
        SpecialCaseType.CLT,
    ):
        result = evaluate_special_case(SpecialCaseInput(case_type=case_type), strict_blocking=False)
        assert result.blocked is False


def test_warning_spc001_present_for_all_types():
    for case_type in (
        SpecialCaseType.PREDALLES,
        SpecialCaseType.COLLABORANTE,
        SpecialCaseType.CLT,
    ):
        result = evaluate_special_case(SpecialCaseInput(case_type=case_type), strict_blocking=True)
        assert any("X8-SPC-001" in w for w in result.warnings)


def test_assumptions_non_empty_when_fallback_used():
    result = evaluate_special_case(
        SpecialCaseInput(case_type=SpecialCaseType.PREDALLES), strict_blocking=False
    )
    assert len(result.assumptions) > 0


def test_recommended_actions_non_empty_when_blocked():
    result = evaluate_special_case(
        SpecialCaseInput(case_type=SpecialCaseType.CLT), strict_blocking=True
    )
    assert len(result.recommended_actions) > 0


def test_case_notes_round_trip_in_input_object():
    data = SpecialCaseInput(
        case_type=SpecialCaseType.PREDALLES,
        notes="caso benchmark predalles",
    )
    assert data.notes == "caso benchmark predalles"
