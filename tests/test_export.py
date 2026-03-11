"""Test export multi-formato modulo report."""

from __future__ import annotations

from pathlib import Path

from src.core.results import ElementResult, ResultsModel
from src.project.schema import ProjectInfo, ProjectModel
from src.report.export import export_ascii, export_docx, export_html, export_md, export_pdf
from src.report.report_builder import build_report


def _artifact():
    project = ProjectModel(project_info=ProjectInfo(name="Export Test"))
    results = ResultsModel(elements=[ElementResult(element_id="E1", ok=True)])
    return build_report(project, results)


def test_export_html_md_ascii(tmp_path: Path):
    artifact = _artifact()
    html_path = export_html(artifact, tmp_path / "report.html")
    md_path = export_md(artifact, tmp_path / "report.md")
    ascii_path = export_ascii(artifact, tmp_path / "report.txt")

    assert html_path.exists()
    assert md_path.exists()
    assert ascii_path.exists()
    assert "<html" in html_path.read_text(encoding="utf-8").lower()
    assert "# Relazione di calcolo" in md_path.read_text(encoding="utf-8")


def test_export_pdf_optional_dependency(tmp_path: Path):
    artifact = _artifact()
    pdf_path = tmp_path / "report.pdf"
    try:
        out = export_pdf(artifact, pdf_path)
        assert out.exists()
    except RuntimeError as exc:
        assert "weasyprint" in str(exc).lower()


def test_export_docx_optional_dependency(tmp_path: Path):
    artifact = _artifact()
    docx_path = tmp_path / "report.docx"
    try:
        out = export_docx(artifact, docx_path)
        assert out.exists()
    except RuntimeError as exc:
        assert "python-docx" in str(exc).lower()


def test_export_rejects_missing_attribute(tmp_path: Path):
    class Incomplete:
        html = ""

    broken = Incomplete()
    try:
        export_md(broken, tmp_path / "missing.md")
        assert False, "Expected ValueError for missing markdown"
    except ValueError:
        assert True
