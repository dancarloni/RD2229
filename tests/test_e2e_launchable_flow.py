"""End-to-end checks for the first launchable workflow (CLI + modern UI bootstrap)."""

from __future__ import annotations

from pathlib import Path

from src.core.pipeline import run_pipeline
from src.project.repository import load_project, save_project
from src.project.schema import CodeSettings, GeometryEntry, LoadEntry, MaterialEntry, ProjectModel
from src.reporting.export import export_report_html, export_report_md
from src.reporting.report_builder import build_report
from src.ui.modern.app import run_bootstrap_workflow


def _project_for_e2e() -> ProjectModel:
    return ProjectModel(
        geometry=[GeometryEntry(id="E1", type="RECTANGULAR", width=30.0, height=50.0)],
        materials=[MaterialEntry(id="C30", type="concrete", f_ck=30.0, f_yk=450.0)],
        loads=[
            LoadEntry(
                element_id="E1",
                N=80.0,
                Mx=45.0,
                Tx=25.0,
                description="combinazione SLU base",
                extra={
                    "As": 12.0,
                    "As_p": 8.0,
                    "d": 45.0,
                    "d_p": 5.0,
                    "staffe_diametro": 8.0,
                    "staffe_num_bracci": 2,
                    "staffe_passo": 20.0,
                },
            )
        ],
        code_settings=CodeSettings(norm_code="NTC2018", limit_states=["SLU"]),
    )


def test_e2e_file_to_pipeline_to_report(tmp_path: Path):
    project_path = tmp_path / "project_e2e.json"
    md_path = tmp_path / "project_e2e_report.md"
    html_path = tmp_path / "project_e2e_report.html"

    save_project(_project_for_e2e(), str(project_path))

    project = load_project(str(project_path))
    results = run_pipeline(project)
    artifact = build_report(project, results, title="E2E Launchable Flow")

    export_report_md(artifact, str(md_path))
    export_report_html(artifact, str(html_path))

    assert any(t.startswith("step5:done") for t in results.trace)
    assert any(k.startswith("step5.") for k in results.elements[0].metrics)
    assert md_path.exists()
    assert html_path.exists()
    assert "E2E Launchable Flow" in md_path.read_text(encoding="utf-8")
    assert "<html" in html_path.read_text(encoding="utf-8").lower()


def test_modern_ui_bootstrap_workflow_exports_reports(tmp_path: Path):
    project_path = tmp_path / "project_ui_bootstrap.json"
    save_project(_project_for_e2e(), str(project_path))

    outcome = run_bootstrap_workflow(str(project_path), str(tmp_path))

    assert "report_md" in outcome
    assert "report_html" in outcome
    assert Path(str(outcome["report_md"])).exists()
    assert Path(str(outcome["report_html"])).exists()
