"""Test integrazione pipeline per il modulo pushover (P12)."""

from __future__ import annotations

from src.core.pipeline import run_pipeline
from src.project.schema import CodeSettings, GeometryEntry, LoadEntry, MaterialEntry, ProjectModel


def _minimal_project() -> ProjectModel:
    return ProjectModel(
        geometry=[GeometryEntry(id="P1", type="RECTANGULAR", width=30.0, height=50.0)],
        materials=[MaterialEntry(id="C25", type="concrete", f_ck=25.0)],
        loads=[LoadEntry(element_id="P1", N=100.0, Mx=50.0)],
        code_settings=CodeSettings(norm_code="RD2229"),
    )


def test_pipeline_no_pushover_without_config():
    project = _minimal_project()
    results = run_pipeline(project)

    assert "pushover" not in results.extra
    assert any(t == "pushover:skip(configured)" for t in results.trace)


def test_pipeline_pushover_in_extra_when_enabled():
    project = _minimal_project()
    project.plugins = {
        "pushover": {
            "enabled": True,
            "k_iniziale": 1800.0,
            "delta_y": 1.0,
            "delta_u": 8.0,
            "n_step": 30,
        }
    }

    results = run_pipeline(project)

    assert "pushover" in results.extra
    pushover = results.extra["pushover"]
    assert "spostamenti" in pushover
    assert "tagli_base" in pushover
    assert pushover["alpha_u_alpha_1"] > 0
    assert any(t.startswith("pushover:done") for t in results.trace)


def test_pipeline_pushover_step_requested_but_missing_config():
    project = _minimal_project()
    project.pipeline_steps = ["validate", "checks", "pushover"]

    results = run_pipeline(project)

    assert "pushover" not in results.extra
    assert any(t == "pushover:skip(no_config)" for t in results.trace)


def test_pipeline_pushover_invalid_config_generates_warning():
    project = _minimal_project()
    project.plugins = {
        "pushover": {
            "enabled": True,
            "k_iniziale": 1800.0,
            "delta_y": 4.0,
            "delta_u": 2.0,
        }
    }

    results = run_pipeline(project)

    assert "pushover" not in results.extra
    assert any("Errore pipeline pushover" in w for w in results.warnings)
    assert any(t == "pushover:error" for t in results.trace)
