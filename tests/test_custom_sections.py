"""Test sezioni personalizzate report (Q.8)."""

from src.core.results import ElementResult, ResultsModel
from src.project.schema import ProjectModel
from src.report.custom import (
    clear_custom_sections,
    load_section_profile,
    register_custom_section,
    save_section_profile,
)
from src.report.report_builder import ReportConfig, build_report


def test_custom_section_is_included_in_report():
    clear_custom_sections()

    def generator(project, results):
        return "## Sezione custom\n\nContenuto utente"

    register_custom_section("sezione_custom", generator, order=900)

    artifact = build_report(
        ProjectModel(),
        ResultsModel(elements=[ElementResult(element_id="E1", ok=True)]),
        config=ReportConfig(include_custom_sections=True),
    )

    assert "sezione_custom" in artifact.section_order
    assert "Contenuto utente" in artifact.markdown
    clear_custom_sections()


def test_custom_section_can_be_disabled():
    clear_custom_sections()

    register_custom_section("disabled_custom", lambda p, r: "## C")
    artifact = build_report(
        ProjectModel(),
        ResultsModel(),
        config=ReportConfig(include_custom_sections=False),
    )

    assert "disabled_custom" not in artifact.section_order
    clear_custom_sections()


def test_section_profile_roundtrip(tmp_path):
    target = tmp_path / "profile.json"
    saved = save_section_profile(target, ["dati_generali", "verifiche"])
    loaded = load_section_profile(saved)

    assert saved.exists()
    assert loaded == ["dati_generali", "verifiche"]
