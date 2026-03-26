"""Test integrazione pipeline per i moduli muratura (P04-P05-P06)."""

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


def test_pipeline_no_muratura_without_config():
    project = _minimal_project()
    results = run_pipeline(project)

    assert "muratura" not in results.extra
    assert any(t == "muratura:skip(configured)" for t in results.trace)


def test_pipeline_muratura_all_modules_enabled():
    project = _minimal_project()
    project.plugins = {
        "muratura": {
            "enabled": True,
            "cinematica": {
                "enabled": True,
                "h": 300.0,
                "t": 30.0,
                "L": 400.0,
                "a_g": 0.25,
                "S": 1.2,
            },
            "scorrimento": {
                "enabled": True,
                "L": 300.0,
                "t": 30.0,
                "h": 300.0,
                "V": 3000.0,
                "N": 12000.0,
                "fvk0": 1.5,
            },
            "cantonale": {
                "enabled": True,
                "h_cm": 300.0,
                "t1_cm": 30.0,
                "t2_cm": 30.0,
                "L1_dist_cm": 120.0,
                "L2_dist_cm": 120.0,
            },
        }
    }

    results = run_pipeline(project)

    assert "muratura" in results.extra
    mur = results.extra["muratura"]
    assert "cinematica" in mur
    assert "scorrimento" in mur
    assert "cantonale" in mur
    assert any(t.startswith("muratura:done") for t in results.trace)


def test_pipeline_muratura_step_requested_but_missing_config():
    project = _minimal_project()
    project.pipeline_steps = ["validate", "checks", "muratura"]

    results = run_pipeline(project)

    assert "muratura" not in results.extra
    assert any(t == "muratura:skip(no_config)" for t in results.trace)


def test_pipeline_muratura_invalid_cantonale_keeps_running():
    project = _minimal_project()
    project.plugins = {
        "muratura": {
            "enabled": True,
            "cantonale": {
                "enabled": True,
                "h_cm": -10.0,
                "t1_cm": 30.0,
                "t2_cm": 30.0,
                "L1_dist_cm": 120.0,
                "L2_dist_cm": 120.0,
            },
        }
    }

    results = run_pipeline(project)

    assert "muratura" not in results.extra
    assert any("Errore pipeline muratura cantonale" in w for w in results.warnings)
    assert any(t == "muratura:cantonale:error" for t in results.trace)
