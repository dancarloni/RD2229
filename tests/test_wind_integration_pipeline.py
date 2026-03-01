"""Test integrazione pipeline per il modulo vento.

Verifica che la pipeline includa risultati wind in results.extra['wind']
quando è configurato un WindConfig nel progetto.
"""

from __future__ import annotations

# Third-party
import pytest

from src.core.pipeline import run_pipeline
from src.project.schema import CodeSettings, GeometryEntry, LoadEntry, MaterialEntry, ProjectModel
from src.wind.models import BuildingGeom, WindSite
from src.wind.service import WindConfig

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _project_with_wind(method: str = "NTC2018") -> ProjectModel:
    """Progetto con WindConfig aggiunto come attributo dinamico."""
    project = ProjectModel(
        geometry=[GeometryEntry(id="P1", type="RECTANGULAR", width=30.0, height=50.0)],
        materials=[MaterialEntry(id="C25", type="concrete", f_ck=25.0)],
        loads=[LoadEntry(element_id="P1", N=100.0, Mx=50.0)],
        code_settings=CodeSettings(norm_code="RD2229"),
    )
    # Aggiungi wind come attributo aggiuntivo (pipeline lo gestisce via getattr)
    project.wind = WindConfig(  # type: ignore[attr-defined]
        method=method,
        site=WindSite(altitude_m=50.0, terrain_category="II"),
        building=BuildingGeom(height_m=20.0),
    )
    return project


def _project_without_wind() -> ProjectModel:
    return ProjectModel(
        geometry=[GeometryEntry(id="P1", type="RECTANGULAR", width=30.0, height=50.0)],
        materials=[MaterialEntry(id="C25", type="concrete", f_ck=25.0)],
        loads=[LoadEntry(element_id="P1", N=100.0, Mx=50.0)],
    )


# ---------------------------------------------------------------------------
# Pipeline integration
# ---------------------------------------------------------------------------


def test_pipeline_wind_in_extra():
    """Pipeline con wind config deve avere results.extra['wind']."""
    project = _project_with_wind()
    results = run_pipeline(project)

    assert "wind" in results.extra, (
        "Risultati vento mancanti in results.extra; " f"extra keys: {list(results.extra.keys())}"
    )


def test_pipeline_wind_has_profile():
    """Risultati wind devono avere un profilo velocità."""
    project = _project_with_wind()
    results = run_pipeline(project)

    wind = results.extra.get("wind", {})
    assert "velocity_profile" in wind, f"velocity_profile mancante in wind: {wind}"
    assert len(wind["velocity_profile"]) >= 1


def test_pipeline_wind_q_b_positive():
    """Pressione cinetica base deve essere positiva."""
    project = _project_with_wind()
    results = run_pipeline(project)

    wind = results.extra.get("wind", {})
    q_b = wind.get("q_b_kN_m2", 0)
    assert q_b > 0, f"q_b non positiva: {q_b}"


def test_pipeline_wind_method_recorded():
    """Il metodo usato deve essere registrato nei risultati."""
    project = _project_with_wind(method="EN1991_1_4")
    results = run_pipeline(project)

    wind = results.extra.get("wind", {})
    assert wind.get("method") == "EN1991_1_4"


def test_pipeline_no_wind_without_config():
    """Senza wind config non ci devono essere risultati wind."""
    project = _project_without_wind()
    results = run_pipeline(project)

    assert "wind" not in results.extra


def test_pipeline_ok_not_affected_by_wind():
    """Il campo ok non deve essere modificato dalla pipeline vento."""
    project_no_wind = _project_without_wind()
    project_wind = _project_with_wind()

    r_no_wind = run_pipeline(project_no_wind)
    r_wind = run_pipeline(project_wind)

    # ok dipende solo dalle verifiche strutturali
    assert r_no_wind.ok == r_wind.ok


def test_pipeline_wind_profile_monotonic():
    """Il profilo di velocità nella pipeline deve essere monotono."""
    project = _project_with_wind()
    results = run_pipeline(project)

    wind = results.extra.get("wind", {})
    profile = wind.get("velocity_profile", [])
    if len(profile) < 2:
        pytest.skip("Profilo con meno di 2 punti: skip monotonia")

    for i in range(1, len(profile)):
        v_prev = profile[i - 1].get("v_m_s", 0)
        v_curr = profile[i].get("v_m_s", 0)
        assert v_curr >= v_prev * 0.95, f"Profilo non monotono: v[{i}]={v_curr} < v[{i-1}]={v_prev}"
