"""Test suite completa per Fase X6 — Report & Tracciabilità.

Copre:
- x6_warning_codes (normalize, make, infer)
- x6_audit_trail (SHA-256, deterministicità)
- x6_multi_norm_comparator (mapping, tabella, estratti, comparazione doppia colonna)
- x6_report_pipeline (payload, auto-popolamento, json)
- report_builder (ReportArtifact X6 fields, markdown, html)
- export (HTML, MD, JSON)
- snapshot stability (formato payload stabile tra run)
- benchmark doppia colonna storico vs NTC2018
"""

from __future__ import annotations

import datetime
import hashlib
import json

import pytest

from src.core.results import ElementResult, ResultsModel
from src.project.schema import CodeSettings, ProjectInfo, ProjectModel
from src.reporting.export import export_report_html, export_report_json, export_report_md
from src.reporting.report_builder import build_report
from src.reporting.x6_audit_trail import build_audit_trail
from src.reporting.x6_multi_norm_comparator import (
    build_formula_table,
    compare_norms,
    get_formula_table_entry,
    get_norm_refs_for,
    get_normative_extracts,
    list_all_check_types,
)
from src.reporting.x6_report_pipeline import (
    _DEFAULT_CHECK_TYPES,
    build_report_payload,
    build_report_payload_json,
)
from src.reporting.x6_warning_codes import (
    infer_contract_warnings,
    make_warning_code,
    normalize_warnings,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_project(
    *,
    name: str = "Solaio X6",
    norm: str = "NTC2018",
    existing: bool = True,
    lc: str = "LC2",
) -> ProjectModel:
    return ProjectModel(
        project_info=ProjectInfo(name=name, author="Studio Test"),
        code_settings=CodeSettings(
            norm_code=norm,
            limit_states=["SLU", "SLE"],
            existing_structure=existing,
            lc=lc,
        ),
    )


def _make_results(
    *,
    ok: bool = True,
    n_elements: int = 1,
    warnings: list[str] | None = None,
    extra: dict | None = None,
) -> ResultsModel:
    elements = [
        ElementResult(
            element_id=f"SOL-{i+1}",
            ok=ok,
            metrics={"utilizzazione_massima": round(0.5 + i * 0.1, 2)},
        )
        for i in range(n_elements)
    ]
    return ResultsModel(
        ok=ok,
        elements=elements,
        warnings=warnings or ["Fallback DM96 disponibile"],
        trace=["pipeline:validate", "pipeline:checks", "step5:aggregate"],
        timestamp="2026-03-16T10:00:00+00:00",
        extra=extra or {},
    )


def _make_project_with_extra() -> tuple[ProjectModel, ResultsModel]:
    project = _make_project()
    results = _make_results(
        extra={
            "formula_table": [
                {
                    "sezione": "flessione",
                    "formula_usata": "NTC2018 §4.1.2.4",
                    "fallback": "DM 9/1/96",
                    "motivo_selezione": "Norma primaria",
                }
            ],
            "normative_extracts": ["NTC2018 §4.1.2.4 — La verifica di resistenza a flessione..."],
        }
    )
    return project, results


# ===========================================================================
# 1. x6_warning_codes
# ===========================================================================


class TestWarningCodes:
    def test_make_warning_code_format(self):
        w = make_warning_code("REP", 1, severity="WARN", norm_ref="NTC2018-§4.1", message="test")
        assert w == "X6-REP-001:WARN::NTC2018-§4.1::test"

    def test_make_warning_code_info_severity(self):
        w = make_warning_code("AUD", 5, severity="INFO", norm_ref="X6-CONTRACT", message="ok")
        assert w.startswith("X6-AUD-005:INFO::")

    def test_make_warning_code_error_severity(self):
        w = make_warning_code("NORM", 999, severity="ERROR", norm_ref="EC2-§6.1", message="errore")
        assert w.startswith("X6-NORM-999:ERROR::")

    def test_normalize_warnings_keeps_x6_coded(self):
        coded = make_warning_code("REP", 7, message="già codificato")
        normalized = normalize_warnings([coded])
        assert normalized[0] == coded

    def test_normalize_warnings_converts_legacy(self):
        normalized = normalize_warnings(["warning generico"])
        assert normalized[0].startswith("X6-REP-001:WARN::")
        assert "warning generico" in normalized[0]

    def test_normalize_warnings_mixed(self):
        coded = make_warning_code("REP", 7, norm_ref="NTC2018", message="precod")
        result = normalize_warnings([coded, "plain", coded])
        assert result[0] == coded
        assert result[1].startswith("X6-REP-002:")
        assert result[2] == coded

    def test_infer_contract_warnings_no_elements(self):
        w = infer_contract_warnings(
            element_count=0, has_trace=True, existing_structure=False, lc=None
        )
        assert any("X6-REP-901" in x for x in w)

    def test_infer_contract_warnings_no_trace(self):
        w = infer_contract_warnings(
            element_count=2, has_trace=False, existing_structure=False, lc=None
        )
        assert any("X6-AUD-001" in x for x in w)

    def test_infer_contract_warnings_existing_no_lc(self):
        w = infer_contract_warnings(
            element_count=1, has_trace=True, existing_structure=True, lc=None
        )
        assert any("X6-NORM-001" in x for x in w)

    def test_infer_contract_warnings_clean(self):
        w = infer_contract_warnings(
            element_count=3, has_trace=True, existing_structure=False, lc=None
        )
        assert w == []

    def test_warning_codes_stable_across_calls(self):
        """I codici warning devono essere deterministici."""
        w1 = make_warning_code("REP", 1, message="msg")
        w2 = make_warning_code("REP", 1, message="msg")
        assert w1 == w2


# ===========================================================================
# 2. x6_audit_trail
# ===========================================================================


class TestAuditTrail:
    def test_build_audit_trail_has_required_keys(self):
        project = _make_project()
        results = _make_results()
        trail = build_audit_trail(project, results)
        assert "input_hash" in trail
        assert "output_hash" in trail
        assert "phase_id" in trail
        assert trail["phase_id"] == "X6"

    def test_audit_trail_hashes_are_hex64(self):
        trail = build_audit_trail(_make_project(), _make_results())
        assert len(trail["input_hash"]) == 64
        assert len(trail["output_hash"]) == 64
        assert all(c in "0123456789abcdef" for c in trail["input_hash"])

    def test_audit_trail_deterministic(self):
        project = _make_project()
        results = _make_results()
        t1 = build_audit_trail(project, results)
        t2 = build_audit_trail(project, results)
        assert t1["input_hash"] == t2["input_hash"]
        assert t1["output_hash"] == t2["output_hash"]

    def test_audit_trail_different_for_different_input(self):
        t1 = build_audit_trail(_make_project(name="A"), _make_results())
        t2 = build_audit_trail(_make_project(name="B"), _make_results())
        assert t1["input_hash"] != t2["input_hash"]

    def test_audit_trail_decision_trace_in_output(self):
        project = _make_project()
        results = _make_results()
        trace = ["Fase X6 avviata", "Norma selezionata: NTC2018"]
        trail = build_audit_trail(project, results, decision_trace=trace)
        assert trail["decision_trace"] == trace


# ===========================================================================
# 3. x6_multi_norm_comparator
# ===========================================================================


class TestMultiNormComparator:
    def test_list_all_check_types_not_empty(self):
        types = list_all_check_types()
        assert len(types) >= 10
        assert "flessione" in types
        assert "taglio" in types

    def test_get_norm_refs_flessione_ntc2018(self):
        refs = get_norm_refs_for("flessione")
        assert "NTC2018" in refs
        assert refs["NTC2018"].section == "§4.1.2.4"
        assert "MRd" in refs["NTC2018"].formula_symbol

    def test_get_norm_refs_taglio_multiple_norms(self):
        refs = get_norm_refs_for("taglio")
        assert len(refs) >= 3
        assert "NTC2018" in refs
        assert "RD2229" in refs

    def test_get_norm_refs_unknown_returns_empty(self):
        refs = get_norm_refs_for("tipo_sconosciuto_xyz")
        assert refs == {}

    def test_get_formula_table_entry_ntc2018(self):
        entry = get_formula_table_entry("flessione", "NTC2018")
        assert entry["norma"] == "NTC2018"
        assert "§4.1.2.4" in entry["sezione_normativa"]
        assert "estratto" in entry
        assert len(entry["estratto"]) > 10

    def test_get_formula_table_entry_unknown_check(self):
        entry = get_formula_table_entry("tipo_xyz", "NTC2018")
        assert entry["formula_usata"] == "N/D"

    def test_get_formula_table_entry_fallback_provided(self):
        entry = get_formula_table_entry("flessione", "NTC2018")
        # deve avere un fallback dalla norma storica
        assert entry["fallback"] != "N/D"

    def test_build_formula_table_length(self):
        table = build_formula_table(["flessione", "taglio", "deformazione"], "NTC2018")
        assert len(table) == 3
        assert all("sezione" in e for e in table)

    def test_build_formula_table_with_dm96(self):
        table = build_formula_table(["flessione", "taglio"], "DM96")
        assert table[0]["norma"] == "DM 9/1/96"

    def test_get_normative_extracts_not_empty(self):
        extracts = get_normative_extracts(["flessione", "taglio"], "NTC2018")
        assert len(extracts) == 2
        assert all("NTC2018" in e for e in extracts)

    def test_compare_norms_flessione_doppia_colonna(self):
        """Test benchmark: raffronto storico (RD2229) vs vigente (NTC2018)."""
        rows = compare_norms("flessione")
        norms = [r["norma"] for r in rows]
        assert "NTC2018" in norms
        assert "RD 2229/1939" in norms
        # Ogni riga ha formula e estratto
        for row in rows:
            assert "formula" in row
            assert "estratto" in row
            assert len(row["estratto"]) > 10

    def test_compare_norms_taglio_ec2_vs_rd2229(self):
        rows = compare_norms("taglio")
        norms = [r["norma"] for r in rows]
        assert len(norms) >= 3

    def test_compare_norms_unknown_returns_empty(self):
        rows = compare_norms("tipo_xyz")
        assert rows == []

    def test_norm_refs_are_frozen_dataclasses(self):
        refs = get_norm_refs_for("flessione")
        ntc = refs["NTC2018"]
        with pytest.raises((AttributeError, TypeError)):
            ntc.norm = "modify"  # type: ignore[misc]


# ===========================================================================
# 4. x6_report_pipeline
# ===========================================================================


class TestReportPipeline:
    def test_build_report_payload_required_keys(self):
        payload = build_report_payload(_make_project(), _make_results())
        for key in (
            "phase_id",
            "project_name",
            "norm_code",
            "formula_table",
            "normative_extracts",
            "warnings",
            "audit_trail",
            "checks_summary",
        ):
            assert key in payload, f"Chiave mancante: {key}"

    def test_build_report_payload_auto_populates_formula_table(self):
        """Senza extra, deve auto-popolare formula_table via comparatore."""
        payload = build_report_payload(_make_project(), _make_results())
        assert len(payload["formula_table"]) == len(_DEFAULT_CHECK_TYPES)
        assert payload["formula_table"][0]["sezione"] == _DEFAULT_CHECK_TYPES[0]

    def test_build_report_payload_auto_populates_normative_extracts(self):
        """Senza extra, deve auto-popolare normative_extracts via comparatore."""
        payload = build_report_payload(_make_project(), _make_results())
        assert len(payload["normative_extracts"]) > 0
        assert all(isinstance(e, str) for e in payload["normative_extracts"])

    def test_build_report_payload_uses_provided_formula_table(self):
        """Se extra contiene formula_table, deve essere usata senza override."""
        project, results = _make_project_with_extra()
        payload = build_report_payload(project, results)
        assert payload["formula_table"][0]["sezione"] == "flessione"
        assert len(payload["formula_table"]) == 1

    def test_build_report_payload_audit_trail_hashes(self):
        payload = build_report_payload(_make_project(), _make_results())
        assert len(payload["audit_trail"]["input_hash"]) == 64
        assert len(payload["audit_trail"]["output_hash"]) == 64

    def test_build_report_payload_decision_trace(self):
        trace = ["Decisione A", "Decisione B"]
        payload = build_report_payload(_make_project(), _make_results(), decision_trace=trace)
        assert payload["decision_trace"] == trace

    def test_build_report_payload_json_is_valid_json(self):
        j = build_report_payload_json(_make_project(), _make_results())
        data = json.loads(j)
        assert data["phase_id"] == "X6"

    def test_build_report_payload_multi_elements(self):
        results = _make_results(n_elements=5, ok=False)
        payload = build_report_payload(_make_project(), results)
        assert payload["checks_summary"]["element_count"] == 5
        assert payload["checks_summary"]["global_ok"] is False

    def test_build_report_payload_dm96_norm(self):
        project = _make_project(norm="DM96")
        payload = build_report_payload(project, _make_results())
        assert payload["norm_code"] == "DM96"
        # formula_table deve usare DM96 come norma primaria dove disponibile
        fless = next((e for e in payload["formula_table"] if e["sezione"] == "flessione"), None)
        assert fless is not None
        assert "DM" in fless.get("norma", "") or "DM" in fless.get("formula_usata", "")


# ===========================================================================
# 5. report_builder (ReportArtifact con X6 fields)
# ===========================================================================


class TestReportBuilder:
    def test_build_report_returns_artifact(self):
        artifact = build_report(_make_project(), _make_results())
        assert artifact.title != ""
        assert artifact.markdown != ""
        assert artifact.html != ""

    def test_build_report_has_json_payload(self):
        artifact = build_report(_make_project(), _make_results())
        assert artifact.json_payload != ""
        payload = json.loads(artifact.json_payload)
        assert payload["phase_id"] == "X6"

    def test_build_report_has_audit_trail(self):
        artifact = build_report(_make_project(), _make_results())
        assert len(artifact.audit_trail) > 0
        assert "input_hash" in artifact.audit_trail

    def test_build_report_markdown_contains_audit_section(self):
        artifact = build_report(_make_project(), _make_results())
        assert "## Audit Trail X6" in artifact.markdown

    def test_build_report_md_snapshot_structure(self):
        """Snapshot: struttura Markdown deve contenere le sezioni attese."""
        artifact = build_report(_make_project(name="Edificio Test"), _make_results())
        md = artifact.markdown
        assert "# Edificio Test" in md
        assert "## Informazioni Progetto" in md
        assert "## Risultati Verifiche" in md
        assert "## Audit Trail X6" in md

    def test_build_report_html_is_valid_html_fragment(self):
        artifact = build_report(_make_project(), _make_results())
        assert "<html" in artifact.html.lower()
        assert "</html>" in artifact.html.lower()

    def test_build_report_warnings_are_x6_coded(self):
        artifact = build_report(_make_project(), _make_results())
        assert all(w.startswith("X6-") for w in artifact.warnings)

    def test_build_report_global_ok_propagated(self):
        a_ok = build_report(_make_project(), _make_results(ok=True))
        a_nok = build_report(_make_project(), _make_results(ok=False))
        assert a_ok.global_ok is True
        assert a_nok.global_ok is False

    def test_build_report_custom_title(self):
        artifact = build_report(_make_project(), _make_results(), title="Report Personalizzato")
        assert "# Report Personalizzato" in artifact.markdown


# ===========================================================================
# 6. export (HTML / MD / JSON)
# ===========================================================================


class TestExport:
    def test_export_report_json_writes_file(self, tmp_path):
        artifact = build_report(_make_project(), _make_results())
        out = tmp_path / "report.json"
        export_report_json(artifact, str(out))
        assert out.exists()
        data = json.loads(out.read_text(encoding="utf-8"))
        assert data["project_name"] == "Solaio X6"

    def test_export_report_html_writes_file(self, tmp_path):
        artifact = build_report(_make_project(), _make_results())
        out = tmp_path / "report.html"
        export_report_html(artifact, str(out))
        assert out.exists()
        content = out.read_text(encoding="utf-8")
        assert "<html" in content.lower()

    def test_export_report_md_writes_file(self, tmp_path):
        artifact = build_report(_make_project(), _make_results())
        out = tmp_path / "report.md"
        export_report_md(artifact, str(out))
        assert out.exists()
        content = out.read_text(encoding="utf-8")
        assert "## Risultati Verifiche" in content

    def test_export_json_roundtrip(self, tmp_path):
        """Il JSON esportato deve essere un roundtrip fedele di json_payload."""
        artifact = build_report(_make_project(), _make_results())
        out = tmp_path / "rt.json"
        export_report_json(artifact, str(out))
        from_file = json.loads(out.read_text("utf-8"))
        from_payload = json.loads(artifact.json_payload)
        assert from_file == from_payload


# ===========================================================================
# 7. Benchmark doppia colonna storico vs NTC2018
# ===========================================================================


class TestBenchmarkDoppiaColonna:
    """Benchmark: confronto passaggi di calcolo NTC2018 vs norma storica (RD2229/DM96)."""

    @pytest.mark.parametrize(
        "check_type,storica,vigente",
        [
            ("flessione", "RD 2229/1939", "NTC2018"),
            ("taglio", "RD 2229/1939", "NTC2018"),
            ("deformazione", "DM 9/1/96", "NTC2018"),
            ("aperture", "DM 9/1/96", "NTC2018"),
            ("acciaio", "DM 14/02/92", "NTC2018"),
        ],
    )
    def test_compare_norms_has_storica_e_vigente(self, check_type, storica, vigente):
        rows = compare_norms(check_type)
        norms = [r["norma"] for r in rows]
        assert vigente in norms, f"Norma vigente '{vigente}' mancante per '{check_type}'"
        assert storica in norms, f"Norma storica '{storica}' mancante per '{check_type}'"

    def test_benchmark_flessione_formule_diverse(self):
        """Le formule di flessione NTC2018 e RD2229 devono essere distinte."""
        refs = get_norm_refs_for("flessione")
        ntc = refs["NTC2018"].formula_symbol
        rd = refs["RD2229"].formula_symbol
        assert ntc != rd

    def test_benchmark_payload_ha_estratti_vigenti(self):
        """Il payload generato per NTC2018 deve contenere estratti di §4.1.2.4."""
        payload = build_report_payload(_make_project(norm="NTC2018"), _make_results())
        extracts_text = " ".join(payload["normative_extracts"])
        assert "§4.1.2.4" in extracts_text

    def test_benchmark_lc2_flag_in_payload(self):
        """Per strutture esistenti LC2, il payload deve registrare lc=LC2."""
        payload = build_report_payload(_make_project(existing=True, lc="LC2"), _make_results())
        assert payload["lc"] == "LC2"
        assert payload["existing_structure"] is True

    def test_benchmark_report_with_multiple_elements(self):
        """Report con 10 elementi deve restituire artifact completo."""
        results = _make_results(n_elements=10, ok=True)
        artifact = build_report(_make_project(), results)
        payload = json.loads(artifact.json_payload)
        assert payload["checks_summary"]["element_count"] == 10
        assert len(payload["formula_table"]) >= 8
