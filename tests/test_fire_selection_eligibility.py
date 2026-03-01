"""Test per il modulo fire: selezione elementi, eleggibilità, pipeline, report.

Verifica:
- evaluate_fire_eligibility restituisce (bool, reasons) corretto
- run_rc_fire_check produce ElementResultFire con status atteso
- iso834_temperature implementa la curva standard
- La pipeline include i risultati fire in results.extra["fire"]
- Il report include sezione incendio quando fire.enabled=True
"""

from __future__ import annotations

import pytest

pytest.importorskip("pydantic")

from src.core.pipeline import run_pipeline
from src.fire.curves import iso834_profile, iso834_temperature
from src.fire.eligibility import evaluate_fire_eligibility
from src.fire.rc_fire_check import run_rc_fire_check
from src.project.schema import (
    CodeSettings,
    FireSettings,
    GeometryEntry,
    LoadEntry,
    MaterialEntry,
    ProjectModel,
)
from src.reporting.report_builder import build_report

# ---------------------------------------------------------------------------
# Fixture helpers
# ---------------------------------------------------------------------------


def _minimal_fire_project(
    *,
    fire_enabled: bool = True,
    cover_mm: float = 40.0,
    exposure_sides: int = 3,
    required_min: int = 60,
) -> ProjectModel:
    """Progetto minimale con impostazioni fire valide."""
    return ProjectModel(
        geometry=[
            GeometryEntry(
                id="P1",
                type="RECTANGULAR",
                width=30.0,
                height=50.0,
                fire_selected=True,
            )
        ],
        materials=[MaterialEntry(id="C25", type="concrete", f_ck=25.0)],
        loads=[LoadEntry(element_id="P1", N=100.0, Mx=50.0)],
        code_settings=CodeSettings(norm_code="RD2229", limit_states=["TA"], existing_structure=True, lc="LC3"),
        fire=FireSettings(
            enabled=fire_enabled,
            scenario="ISO_834",
            required_rating_minutes=required_min,
            cover_mm_default=cover_mm,
            exposure_sides_default=exposure_sides,
        ),
    )


def _element_ok() -> GeometryEntry:
    return GeometryEntry(id="E1", type="RECTANGULAR", width=30.0, height=50.0, fire_selected=True)


def _element_unsupported_type() -> GeometryEntry:
    return GeometryEntry(id="E2", type="CIRCULAR", width=30.0, height=30.0, fire_selected=True)


def _element_zero_width() -> GeometryEntry:
    return GeometryEntry(id="E3", type="RECTANGULAR", width=0.0, height=50.0, fire_selected=True)


# ---------------------------------------------------------------------------
# ISO 834 curve
# ---------------------------------------------------------------------------


def test_iso834_temperature_at_0():
    """T(0) deve essere 20°C (temperatura iniziale)."""
    assert iso834_temperature(0) == pytest.approx(20.0)


def test_iso834_temperature_at_30():
    """T(30) deve essere circa 842°C (valore noto dalla letteratura)."""
    t30 = iso834_temperature(30)
    assert 830 < t30 < 860


def test_iso834_temperature_at_60():
    """T(60) deve essere circa 945°C."""
    t60 = iso834_temperature(60)
    assert 930 < t60 < 960


def test_iso834_temperature_monotonic():
    """La curva ISO 834 deve essere monotona crescente."""
    times = [0, 5, 10, 20, 30, 60, 90, 120]
    temps = [iso834_temperature(t) for t in times]
    for i in range(1, len(temps)):
        assert temps[i] > temps[i - 1], f"Non monotona tra t={times[i-1]} e t={times[i]}"


def test_iso834_temperature_negative_raises():
    """iso834_temperature deve sollevare ValueError per t_min < 0."""
    with pytest.raises(ValueError):
        iso834_temperature(-1)


def test_iso834_profile_returns_correct_length():
    """iso834_profile deve restituire il numero di punti richiesti."""
    profile = iso834_profile(60, n_points=10)
    assert len(profile) == 10


def test_iso834_profile_starts_at_zero():
    """Il primo punto del profilo deve essere a t=0."""
    profile = iso834_profile(60, n_points=5)
    assert profile[0][0] == 0.0


# ---------------------------------------------------------------------------
# Eligibility
# ---------------------------------------------------------------------------


def test_eligibility_ok_for_valid_rc():
    """Elemento RC rettangolare con dati completi deve essere eleggibile."""
    project = _minimal_fire_project()
    elem = _element_ok()
    eligible, reasons = evaluate_fire_eligibility(project, elem)
    assert eligible is True
    assert reasons == []


def test_eligibility_ko_unsupported_type():
    """Tipo sezione non supportato deve rendere l'elemento non eleggibile."""
    project = _minimal_fire_project()
    elem = _element_unsupported_type()
    eligible, reasons = evaluate_fire_eligibility(project, elem)
    assert eligible is False
    assert any("CIRCULAR" in r or "supportat" in r.lower() for r in reasons)


def test_eligibility_ko_zero_width():
    """Larghezza zero deve rendere l'elemento non eleggibile."""
    project = _minimal_fire_project()
    elem = _element_zero_width()
    eligible, reasons = evaluate_fire_eligibility(project, elem)
    assert eligible is False
    assert any("larghezza" in r.lower() or "positiv" in r.lower() for r in reasons)


def test_eligibility_ko_no_concrete():
    """Senza materiale calcestruzzo, elemento non eleggibile."""
    project = ProjectModel(
        geometry=[_element_ok()],
        materials=[MaterialEntry(id="S1", type="steel", f_yk=450.0)],
        loads=[],
        fire=FireSettings(enabled=True, cover_mm_default=40.0, exposure_sides_default=3),
    )
    elem = _element_ok()
    eligible, reasons = evaluate_fire_eligibility(project, elem)
    assert eligible is False
    assert any("calcestruzzo" in r.lower() for r in reasons)


def test_eligibility_ko_no_cover():
    """Senza copriferro, elemento non eleggibile."""
    project = ProjectModel(
        geometry=[_element_ok()],
        materials=[MaterialEntry(id="C25", type="concrete", f_ck=25.0)],
        loads=[],
        fire=FireSettings(enabled=True, cover_mm_default=None, exposure_sides_default=3),
    )
    elem = _element_ok()
    eligible, reasons = evaluate_fire_eligibility(project, elem)
    assert eligible is False
    assert any("copriferro" in r.lower() for r in reasons)


def test_eligibility_ok_with_fire_override():
    """fire_override su elemento deve sovrascrivere il default del progetto."""
    project = ProjectModel(
        geometry=[],
        materials=[MaterialEntry(id="C25", type="concrete", f_ck=25.0)],
        loads=[],
        fire=FireSettings(enabled=True, cover_mm_default=None, exposure_sides_default=None),
    )
    elem = GeometryEntry(
        id="E_override",
        type="RECTANGULAR",
        width=30.0,
        height=50.0,
        fire_override={"cover_mm": 40.0, "exposure_sides": 3},
    )
    eligible, reasons = evaluate_fire_eligibility(project, elem)
    assert eligible is True, f"Atteso eleggibile ma reasons={reasons}"


# ---------------------------------------------------------------------------
# RC fire check
# ---------------------------------------------------------------------------


def test_rc_fire_check_ok():
    """Elemento con dimensioni adeguate deve avere status OK."""
    project = _minimal_fire_project(cover_mm=40.0, exposure_sides=3, required_min=60)
    elem = GeometryEntry(id="P1", type="RECTANGULAR", width=30.0, height=50.0)
    # b_mm=300, b_min=120: OK; cover=40, a_min=35: OK
    result = run_rc_fire_check(project, elem)
    assert result.status == "OK", f"Atteso OK, messages={result.messages}"


def test_rc_fire_check_ko_small_width():
    """Sezione troppo stretta deve avere status KO."""
    project = _minimal_fire_project(cover_mm=40.0, exposure_sides=3, required_min=60)
    elem = GeometryEntry(id="P1", type="RECTANGULAR", width=5.0, height=50.0)
    # b_mm=50, b_min=120: KO
    result = run_rc_fire_check(project, elem)
    assert result.status == "KO", f"Atteso KO, messages={result.messages}"


def test_rc_fire_check_not_verified_no_cover():
    """Senza copriferro il check deve dare NOT_VERIFIED."""
    project = ProjectModel(
        geometry=[GeometryEntry(id="P1", type="RECTANGULAR", width=30.0, height=50.0)],
        materials=[MaterialEntry(id="C25", type="concrete", f_ck=25.0)],
        loads=[],
        fire=FireSettings(enabled=True, cover_mm_default=None, exposure_sides_default=3, required_rating_minutes=60),
    )
    elem = GeometryEntry(id="P1", type="RECTANGULAR", width=30.0, height=50.0)
    result = run_rc_fire_check(project, elem)
    # cover=None → NOT_VERIFIED
    assert result.status in ("NOT_VERIFIED", "KO")


def test_rc_fire_check_has_metrics():
    """Il risultato deve contenere metriche numeriche."""
    project = _minimal_fire_project()
    elem = GeometryEntry(id="P1", type="RECTANGULAR", width=30.0, height=50.0)
    result = run_rc_fire_check(project, elem)
    assert "b_mm" in result.metrics
    assert "required_rating_minutes" in result.metrics
    assert "iso834_temp_end_celsius" in result.metrics


# ---------------------------------------------------------------------------
# Pipeline integration
# ---------------------------------------------------------------------------


def test_pipeline_fire_results_in_extra():
    """Pipeline con fire.enabled=True deve avere risultati in results.extra['fire']."""
    project = _minimal_fire_project()
    results = run_pipeline(project)

    assert "fire" in results.extra, "results.extra deve contenere chiave 'fire'"
    fire_list = results.extra["fire"]
    assert isinstance(fire_list, list)
    assert len(fire_list) >= 1


def test_pipeline_fire_only_selected_elements():
    """Solo gli elementi fire_selected devono avere risultati incendio."""
    project = ProjectModel(
        geometry=[
            GeometryEntry(id="P1", type="RECTANGULAR", width=30.0, height=50.0, fire_selected=True),
            GeometryEntry(id="P2", type="RECTANGULAR", width=30.0, height=50.0, fire_selected=False),
        ],
        materials=[MaterialEntry(id="C25", type="concrete", f_ck=25.0)],
        loads=[
            LoadEntry(element_id="P1", N=100.0, Mx=50.0),
            LoadEntry(element_id="P2", N=100.0, Mx=50.0),
        ],
        fire=FireSettings(enabled=True, cover_mm_default=40.0, exposure_sides_default=3),
    )
    results = run_pipeline(project)

    fire_ids = {item["element_id"] for item in results.extra.get("fire", [])}
    assert "P1" in fire_ids
    assert "P2" not in fire_ids


def test_pipeline_fire_disabled_no_fire_results():
    """Con fire.enabled=False non ci devono essere risultati fire."""
    project = _minimal_fire_project(fire_enabled=False)
    results = run_pipeline(project)
    assert "fire" not in results.extra


def test_pipeline_fire_not_eligible_skipped():
    """Elementi non eleggibili devono essere SKIPPED con reasons."""
    project = ProjectModel(
        geometry=[
            GeometryEntry(id="P1", type="CIRCULAR", width=30.0, height=30.0, fire_selected=True),
        ],
        materials=[MaterialEntry(id="C25", type="concrete", f_ck=25.0)],
        loads=[LoadEntry(element_id="P1", N=100.0)],
        fire=FireSettings(enabled=True, cover_mm_default=40.0, exposure_sides_default=3),
    )
    results = run_pipeline(project)

    fire_list = results.extra.get("fire", [])
    assert len(fire_list) >= 1
    assert fire_list[0]["status"] == "SKIPPED"


def test_pipeline_ok_not_affected_by_fire():
    """Il campo ok globale non deve essere modificato dai risultati fire."""
    project_no_fire = _minimal_fire_project(fire_enabled=False)
    project_fire = _minimal_fire_project(fire_enabled=True)

    results_no_fire = run_pipeline(project_no_fire)
    results_fire = run_pipeline(project_fire)

    # ok deve dipendere solo dalle verifiche strutturali normali, non dal fuoco
    assert results_no_fire.ok == results_fire.ok


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------


def test_report_includes_fire_section_when_enabled():
    """Il report deve includere la sezione incendio quando fire.enabled=True."""
    project = _minimal_fire_project()
    results = run_pipeline(project)
    report = build_report(project, results)

    assert "Incendio" in report.markdown or "🔥" in report.markdown


def test_report_no_fire_section_when_disabled():
    """Il report non deve avere sezione incendio quando fire.enabled=False."""
    project = _minimal_fire_project(fire_enabled=False)
    results = run_pipeline(project)
    report = build_report(project, results)

    # Nessuna intestazione fuoco nella sezione principale
    # (può esserci menzione in traccia ma non sezione dedicata)
    assert "🔥 Verifiche Incendio" not in report.markdown
