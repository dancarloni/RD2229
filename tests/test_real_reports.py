"""Test E2E report su casi reali semplificati (Q.9)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.core.pipeline import run_pipeline
from src.project.schema import ProjectModel
from src.report.report_builder import build_report

REAL_PROJECTS = [
    "trave_ca_ntc2018.json",
    "pilastro_ca_dm96.json",
    "telaio_piano_rd2229.json",
]


@pytest.mark.parametrize("filename", REAL_PROJECTS)
def test_real_project_report_generation(filename: str, tmp_path: Path):
    base = Path(__file__).parent / "real_projects"
    payload = json.loads((base / filename).read_text(encoding="utf-8"))
    project = ProjectModel.from_dict(payload)
    results = run_pipeline(project)
    artifact = build_report(project, results)

    assert artifact.markdown.startswith("# Relazione di calcolo")
    assert "## 1. Dati generali" in artifact.markdown
    assert "## 5. Verifiche" in artifact.markdown
    assert "<html" in artifact.html.lower()
    assert len(artifact.html.encode("utf-8")) < 5 * 1024 * 1024

    out_md = tmp_path / f"{filename}.md"
    out_md.write_text(artifact.markdown, encoding="utf-8")
    assert out_md.exists()
