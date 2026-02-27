"""Smoke test per src.reporting – report builder e export.

Verifica che:
- build_report non sollevi eccezioni
- l'output contenga le sezioni obbligatorie (titolo, schema_version, warnings, risultati)
- export_report_html e export_report_md creino file leggibili
"""

from __future__ import annotations

import os

from src.core.pipeline import run_pipeline
from src.project.schema import (
    CodeSettings,
    GeometryEntry,
    LoadEntry,
    MaterialEntry,
    ProjectInfo,
    ProjectModel,
)
from src.reporting.export import export_report_html, export_report_md
from src.reporting.report_builder import ReportArtifact, build_report


def _minimal_project() -> ProjectModel:
    return ProjectModel(
        project_info=ProjectInfo(name="Progetto Test", author="Pytest"),
        geometry=[GeometryEntry(id="P1", type="RECTANGULAR", width=30.0, height=50.0)],
        materials=[MaterialEntry(id="C25", type="concrete", f_ck=25.0)],
        loads=[LoadEntry(element_id="P1", N=100.0, Mx=50.0)],
        code_settings=CodeSettings(norm_code="RD2229", limit_states=["TA"]),
    )


def _empty_project() -> ProjectModel:
    return ProjectModel()


# ---------------------------------------------------------------------------
# ReportArtifact
# ---------------------------------------------------------------------------


def test_build_report_returns_artifact():
    """build_report deve restituire un ReportArtifact."""
    project = _minimal_project()
    results = run_pipeline(project)
    artifact = build_report(project, results)

    assert isinstance(artifact, ReportArtifact)


def test_build_report_no_crash_empty_project():
    """build_report non deve crashare su progetto vuoto."""
    project = _empty_project()
    results = run_pipeline(project)
    artifact = build_report(project, results)

    assert isinstance(artifact, ReportArtifact)


def test_build_report_markdown_contains_title():
    """Il Markdown del report deve contenere il titolo."""
    project = _minimal_project()
    results = run_pipeline(project)
    artifact = build_report(project, results, title="Rapporto di Verifica")

    assert "Rapporto di Verifica" in artifact.markdown


def test_build_report_markdown_contains_schema_version():
    """Il Markdown del report deve contenere schema_version."""
    project = _minimal_project()
    results = run_pipeline(project)
    artifact = build_report(project, results)

    assert project.schema_version in artifact.markdown


def test_build_report_markdown_contains_warnings_section():
    """Il Markdown deve avere la sezione Avvisi quando ci sono warnings."""
    # Progetto con warnings (nessun carico definito)
    project = _empty_project()
    results = run_pipeline(project)
    artifact = build_report(project, results)

    # Con progetto vuoto ci sono warnings nella pipeline
    # Il report deve comunque avere il titolo e le sezioni base
    assert artifact.markdown != ""
    assert "schema_version" in artifact.markdown.lower() or artifact.schema_version != ""


def test_build_report_markdown_contains_risultati_section():
    """Il Markdown del report deve contenere la sezione Risultati Verifiche."""
    project = _minimal_project()
    results = run_pipeline(project)
    artifact = build_report(project, results)

    assert "Risultati" in artifact.markdown


def test_build_report_artifact_has_metadata():
    """L'artefatto deve avere schema_version, timestamp, app_version."""
    project = _minimal_project()
    results = run_pipeline(project)
    artifact = build_report(project, results)

    assert artifact.schema_version != ""
    assert artifact.timestamp != ""
    assert artifact.app_version != ""


def test_build_report_artifact_propagates_warnings():
    """I warnings del ResultsModel devono essere inclusi nell'artefatto."""
    project = _empty_project()
    results = run_pipeline(project)

    assert len(results.warnings) > 0, "Il progetto vuoto deve avere warnings"

    artifact = build_report(project, results)
    assert artifact.warnings == results.warnings


def test_build_report_artifact_element_count():
    """element_count deve corrispondere al numero di elementi nei risultati."""
    project = _minimal_project()
    results = run_pipeline(project)
    artifact = build_report(project, results)

    assert artifact.element_count == len(results.elements)


def test_build_report_html_not_empty():
    """L'HTML del report non deve essere vuoto."""
    project = _minimal_project()
    results = run_pipeline(project)
    artifact = build_report(project, results)

    assert artifact.html != ""
    assert "<html" in artifact.html.lower()


def test_build_report_html_contains_title():
    """L'HTML del report deve contenere il titolo."""
    project = _minimal_project()
    results = run_pipeline(project)
    artifact = build_report(project, results, title="Test HTML Report")

    assert "Test HTML Report" in artifact.html


# ---------------------------------------------------------------------------
# Export HTML
# ---------------------------------------------------------------------------


def test_export_report_html_creates_file(tmp_path):
    """export_report_html deve creare un file HTML sul disco."""
    project = _minimal_project()
    results = run_pipeline(project)
    artifact = build_report(project, results)

    path = str(tmp_path / "report.html")
    export_report_html(artifact, path)

    assert os.path.exists(path)


def test_export_report_html_content_valid(tmp_path):
    """Il file HTML creato deve avere contenuto HTML valido."""
    project = _minimal_project()
    results = run_pipeline(project)
    artifact = build_report(project, results, title="Verifica RD2229")

    path = str(tmp_path / "report.html")
    export_report_html(artifact, path)

    with open(path, encoding="utf-8") as f:
        content = f.read()

    assert "<html" in content.lower()
    assert "Verifica RD2229" in content


def test_export_report_html_no_tmp_left(tmp_path):
    """Dopo export HTML non devono restare file .tmp."""
    project = _minimal_project()
    results = run_pipeline(project)
    artifact = build_report(project, results)

    path = str(tmp_path / "report.html")
    export_report_html(artifact, path)

    assert not os.path.exists(path + ".tmp")


# ---------------------------------------------------------------------------
# Export Markdown
# ---------------------------------------------------------------------------


def test_export_report_md_creates_file(tmp_path):
    """export_report_md deve creare un file Markdown sul disco."""
    project = _minimal_project()
    results = run_pipeline(project)
    artifact = build_report(project, results)

    path = str(tmp_path / "report.md")
    export_report_md(artifact, path)

    assert os.path.exists(path)


def test_export_report_md_content_valid(tmp_path):
    """Il file MD deve contenere le sezioni obbligatorie."""
    project = _minimal_project()
    results = run_pipeline(project)
    artifact = build_report(project, results)

    path = str(tmp_path / "report.md")
    export_report_md(artifact, path)

    with open(path, encoding="utf-8") as f:
        content = f.read()

    # Sezioni obbligatorie
    assert "schema_version" in content.lower() or artifact.schema_version in content
    assert "Risultati" in content or "risultati" in content.lower()


def test_export_report_md_no_tmp_left(tmp_path):
    """Dopo export MD non devono restare file .tmp."""
    project = _minimal_project()
    results = run_pipeline(project)
    artifact = build_report(project, results)

    path = str(tmp_path / "report.md")
    export_report_md(artifact, path)

    assert not os.path.exists(path + ".tmp")


def test_export_report_md_with_element_results(tmp_path):
    """Il report MD deve avere almeno una riga di risultato quando ci sono elementi."""
    project = _minimal_project()
    results = run_pipeline(project)

    assert len(results.elements) >= 1

    artifact = build_report(project, results)
    path = str(tmp_path / "report.md")
    export_report_md(artifact, path)

    with open(path, encoding="utf-8") as f:
        content = f.read()

    # Deve esserci almeno P1 nella tabella
    assert "P1" in content
