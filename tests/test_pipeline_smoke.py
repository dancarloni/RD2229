"""Smoke test della pipeline di calcolo.

Verifica che:
- run_pipeline non sollevi eccezioni su un project minimale
- il risultato sia un ResultsModel valido
- export_results crei il file JSON corretto
"""

from __future__ import annotations

import pytest

pytest.importorskip("pydantic")

import json
import os

from src.core.pipeline import run_pipeline
from src.core.results import ResultsModel, export_results
from src.project.schema import (
    CodeSettings,
    GeometryEntry,
    LoadEntry,
    MaterialEntry,
    ProjectModel,
)


def _minimal_project() -> ProjectModel:
    """Progetto minimale con un elemento e un carico."""
    return ProjectModel(
        geometry=[GeometryEntry(id="P1", type="RECTANGULAR", width=30.0, height=50.0)],
        materials=[MaterialEntry(id="C25", type="concrete", f_ck=25.0)],
        loads=[LoadEntry(element_id="P1", N=100.0, Mx=50.0)],
        code_settings=CodeSettings(norm_code="RD2229", limit_states=["TA"]),
    )


def _empty_project() -> ProjectModel:
    """Progetto senza elementi né carichi."""
    return ProjectModel()


def test_pipeline_smoke_returns_results_model():
    """run_pipeline deve restituire un ResultsModel senza eccezioni."""
    project = _minimal_project()
    results = run_pipeline(project)

    assert isinstance(results, ResultsModel)


def test_pipeline_smoke_minimal_project_ok():
    """Pipeline su progetto minimale completo deve avere ok=True."""
    project = _minimal_project()
    results = run_pipeline(project)

    assert results.ok is True
    assert len(results.elements) == 1
    assert results.elements[0].element_id == "P1"
    assert results.elements[0].ok is True


def test_pipeline_smoke_has_timestamp():
    """ResultsModel deve avere un timestamp non vuoto."""
    project = _minimal_project()
    results = run_pipeline(project)

    assert results.timestamp != ""


def test_pipeline_smoke_schema_version_propagated():
    """ResultsModel deve riportare la schema_version del progetto in input."""
    project = _minimal_project()
    results = run_pipeline(project)

    assert results.schema_version_input == project.schema_version


def test_pipeline_smoke_empty_project_no_crash():
    """Pipeline su progetto vuoto non deve crashare e deve avere warnings."""
    project = _empty_project()
    results = run_pipeline(project)

    assert isinstance(results, ResultsModel)
    assert results.ok is False
    assert len(results.warnings) > 0


def test_pipeline_smoke_missing_geometry_produces_warning():
    """Carico senza geometria corrispondente deve generare un warning."""
    project = ProjectModel(
        loads=[LoadEntry(element_id="MISSING", N=100.0)],
    )
    results = run_pipeline(project)

    assert any("MISSING" in w or "Geometria" in w for w in results.warnings)


def test_pipeline_smoke_trace_not_empty():
    """La traccia della pipeline deve contenere almeno i passi principali."""
    project = _minimal_project()
    results = run_pipeline(project)

    assert any("start" in t for t in results.trace)
    assert any("complete" in t for t in results.trace)


def test_export_results_creates_file(tmp_path):
    """export_results deve creare un file JSON valido."""
    project = _minimal_project()
    results = run_pipeline(project)

    path = str(tmp_path / "results.json")
    export_results(results, path)

    assert os.path.exists(path)
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    assert "ok" in data
    assert "elements" in data
    assert "warnings" in data
    assert "timestamp" in data


def test_export_results_no_tmp_left(tmp_path):
    """Dopo export non devono restare file .tmp."""
    project = _minimal_project()
    results = run_pipeline(project)

    path = str(tmp_path / "results.json")
    export_results(results, path)

    assert not os.path.exists(path + ".tmp")
