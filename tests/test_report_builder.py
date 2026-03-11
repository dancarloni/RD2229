"""Test builder relazione professionale (Fase Q)."""

from __future__ import annotations

from src.core.results import ElementResult, ResultsModel
from src.project.schema import (
    CodeSettings,
    GeometryEntry,
    LoadEntry,
    MaterialEntry,
    ProjectInfo,
    ProjectModel,
)
from src.report.decorators import contribuisce_report
from src.report.pipeline import clear_report_registry
from src.report.report_builder import ReportConfig, build_report


def _make_project() -> ProjectModel:
    return ProjectModel(
        project_info=ProjectInfo(name="Edificio Q", author="Studio Tecnico"),
        geometry=[GeometryEntry(id="P1", type="RECT", width=30.0, height=50.0)],
        materials=[MaterialEntry(id="C25", type="cls", material_class="C25/30", f_ck=250.0)],
        loads=[LoadEntry(element_id="P1", N=100.0, Mx=35.0, Ty=12.0)],
        code_settings=CodeSettings(norm_code="NTC2018", limit_states=["SLU", "SLE"]),
    )


def _make_results() -> ResultsModel:
    return ResultsModel(
        ok=True,
        elements=[ElementResult(element_id="P1", ok=True, metrics={"util": 0.67})],
        warnings=["Nessun warning critico"],
        trace=["pipeline:validate", "pipeline:checks"],
        timestamp="2026-03-11T12:00:00",
        extra={
            "checks_by_element": {
                "P1": [
                    {
                        "norm_references": [
                            {
                                "norm_code": "NTC2018",
                                "paragraph": "4.1.2.1.3",
                            }
                        ]
                    }
                ]
            }
        },
    )


def test_build_report_contains_mandatory_chapters():
    artifact = build_report(_make_project(), _make_results())

    assert "## 1. Dati generali" in artifact.markdown
    assert "## 2. Materiali" in artifact.markdown
    assert "## 3. Azioni" in artifact.markdown
    assert "## 4. Analisi strutturale" in artifact.markdown
    assert "## 5. Verifiche" in artifact.markdown
    assert "## 7. Conclusioni" in artifact.markdown
    assert 'class="a4-page"' in artifact.html


def test_build_report_includes_appendix_and_citations():
    artifact = build_report(_make_project(), _make_results())

    assert "NTC2018 §4.1.2.1.3" in artifact.citations
    assert "## Appendice normativa" in artifact.markdown


def test_selected_sections_filter():
    config = ReportConfig(selected_sections=["dati_generali", "conclusioni"])
    artifact = build_report(_make_project(), _make_results(), config=config)

    assert artifact.section_order == ["dati_generali", "conclusioni"]
    assert "## 2. Materiali" not in artifact.markdown


def test_registry_contributions_are_appended():
    clear_report_registry()

    @contribuisce_report(key="appendice_tecnica", order=900)
    def appendice(project, results):
        return "## Appendice tecnica\n\nContenuto extra"

    artifact = build_report(_make_project(), _make_results())

    assert "appendice_tecnica" in artifact.section_order
    assert "Contenuto extra" in artifact.markdown
    clear_report_registry()


def test_comparison_section_enabled_with_flag():
    results = _make_results()
    results.extra["norm_comparison"] = {
        "P1": {
            "NTC2018": {"M_Rd": 100.0, "V_Rd": 55.0, "N_Rd": 230.0, "ok": True},
            "DM96": {"M_Rd": 92.0, "V_Rd": 50.0, "N_Rd": 210.0, "ok": True},
        }
    }

    artifact = build_report(
        _make_project(),
        results,
        config=ReportConfig(include_comparison=True),
    )

    assert "## Confronto multi-norma" in artifact.markdown
