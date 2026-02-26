"""
Test per il contratto E1: MVP Report Builder.

Verifica che ReportArtifact prodotto da build_report:
 - contenga tutti i campi obbligatori
 - abbia input_hash SHA-256 valido (64 chars hex)
 - superi validate_report_contract
 - sia esportabile come JSON e rileggibile
 - fallisca validate_report_contract su campi mancanti/invalidi
"""

import json
import re

import pytest

from src.rd2229.mvp.models import (
    CheckRequest,
    Combination,
    Element,
    LoadCase,
    TraceRecord,
    VerificationResult,
)
from src.rd2229.mvp.report_builder import (
    REPORT_SCHEMA_VERSION,
    ReportArtifact,
    build_report,
    export_report_json,
    report_to_dict,
    report_to_json,
    validate_report_contract,
)


# ---------------------------------------------------------------------------
# Fixture: VerificationResult minimo
# ---------------------------------------------------------------------------

def _make_result(
    status: str = "OK",
    value: float = 0.5,
    norm_refs: list[str] | None = None,
) -> VerificationResult:
    trace = TraceRecord(
        run_id="abc123def456abc123def456abc123de",
        norm_code="NTC2018",
        norm_references=norm_refs or ["TODO(NTC/EC/RD):REF"],
        method_id="MVP_REAL_MIN",
        assumptions=["element_role=PRIMARY", "axial=100.0"],
        warnings=[],
    )
    return VerificationResult(
        id="result001" + "0" * 23,
        request_id="req001" + "0" * 26,
        project_id="proj001" + "0" * 25,
        status=status,
        value=value,
        trace=trace,
    )


# ---------------------------------------------------------------------------
# Test: campi obbligatori presenti
# ---------------------------------------------------------------------------

def test_report_has_all_mandatory_fields():
    result = _make_result()
    report = build_report(result, plugin_versions={"core": "1.0.0"})

    assert report.run_id == result.trace.run_id
    assert report.project_id == result.project_id
    assert report.result_id == result.id
    assert report.status == result.status
    assert report.method_id == result.trace.method_id
    assert report.norm_references == list(result.trace.norm_references)
    assert report.norm_code == result.trace.norm_code
    assert report.value == result.value
    assert report.check_code == result.trace.method_id
    assert report.generated_at  # non vuoto
    assert len(report.input_hash) == 64
    assert report.plugin_versions == {"core": "1.0.0"}
    assert report.schema_version == REPORT_SCHEMA_VERSION


def test_report_input_hash_is_sha256_hex():
    result = _make_result()
    report = build_report(result)
    assert re.fullmatch(r"[0-9a-f]{64}", report.input_hash), (
        f"input_hash non è SHA-256 hex: {report.input_hash}"
    )


def test_report_plugin_versions_default_empty():
    result = _make_result()
    report = build_report(result)
    assert report.plugin_versions == {}


# ---------------------------------------------------------------------------
# Test: validate_report_contract
# ---------------------------------------------------------------------------

def test_validate_report_contract_ok():
    result = _make_result()
    report = build_report(result)
    validate_report_contract(report)  # non deve lanciare


def test_validate_report_contract_fail_status():
    result = _make_result()
    report = build_report(result)
    bad = ReportArtifact(
        **{**report_to_dict(report), "status": "UNKNOWN"}
    )
    with pytest.raises(ValueError, match="status"):
        validate_report_contract(bad)


def test_validate_report_contract_fail_empty_run_id():
    result = _make_result()
    report = build_report(result)
    bad = ReportArtifact(**{**report_to_dict(report), "run_id": "   "})
    with pytest.raises(ValueError, match="run_id"):
        validate_report_contract(bad)


def test_validate_report_contract_fail_empty_norm_references():
    result = _make_result()
    report = build_report(result)
    bad = ReportArtifact(**{**report_to_dict(report), "norm_references": []})
    with pytest.raises(ValueError, match="norm_references"):
        validate_report_contract(bad)


def test_validate_report_contract_fail_short_hash():
    result = _make_result()
    report = build_report(result)
    bad = ReportArtifact(**{**report_to_dict(report), "input_hash": "abc"})
    with pytest.raises(ValueError, match="input_hash"):
        validate_report_contract(bad)


# ---------------------------------------------------------------------------
# Test: serializzazione JSON
# ---------------------------------------------------------------------------

def test_report_to_json_is_valid_json():
    result = _make_result()
    report = build_report(result)
    parsed = json.loads(report_to_json(report))
    assert parsed["run_id"] == report.run_id
    assert parsed["schema_version"] == REPORT_SCHEMA_VERSION
    assert "input_hash" in parsed
    assert "generated_at" in parsed


def test_report_to_dict_all_fields():
    result = _make_result()
    report = build_report(result, plugin_versions={"fire_module": "0.1.0"})
    d = report_to_dict(report)
    for key in (
        "run_id", "project_id", "result_id", "status", "method_id",
        "norm_references", "norm_code", "value", "check_code",
        "generated_at", "input_hash", "plugin_versions", "schema_version",
    ):
        assert key in d, f"Campo mancante nel dict: {key}"


# ---------------------------------------------------------------------------
# Test: export_report_json (scrittura atomica)
# ---------------------------------------------------------------------------

def test_export_report_json_file(tmp_path):
    result = _make_result()
    report = build_report(result)
    out_path = tmp_path / "report.json"
    written = export_report_json(report, out_path)
    assert written == out_path
    assert out_path.exists()
    loaded = json.loads(out_path.read_text(encoding="utf-8"))
    assert loaded["run_id"] == report.run_id
    assert loaded["schema_version"] == REPORT_SCHEMA_VERSION


def test_export_report_json_no_tmp_file_on_success(tmp_path):
    result = _make_result()
    report = build_report(result)
    out_path = tmp_path / "report.json"
    export_report_json(report, out_path)
    tmp_file = out_path.with_suffix(".tmp")
    assert not tmp_file.exists(), "Il file .tmp non deve restare dopo scrittura riuscita"


# ---------------------------------------------------------------------------
# Test: hash deterministico (stesso input → stesso hash)
# ---------------------------------------------------------------------------

def test_input_hash_deterministic():
    result = _make_result()
    r1 = build_report(result)
    r2 = build_report(result)
    assert r1.input_hash == r2.input_hash, "L'hash deve essere deterministico"


def test_input_hash_changes_with_different_result():
    r_ok = _make_result(status="OK", value=0.5)
    r_fail = _make_result(status="FAIL", value=1.2)
    assert build_report(r_ok).input_hash != build_report(r_fail).input_hash
