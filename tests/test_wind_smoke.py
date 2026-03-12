"""Smoke test per il modulo wind.

Verifica:
- Calcolo NTC2018: profilo monotono, valori positivi
- Calcolo EN1991-1-4: profilo coerente
- WindActionService: orchestrazione multi-metodo
- iso834_temperature: non direttamente qui, ma in test_fire_selection_eligibility
"""

from __future__ import annotations

import pytest

from src.wind.ec1991_1_4 import compute_mean_wind_velocity, run_en1991_1_4_wind
from src.wind.models import BuildingGeom, StructureGeom, WindSite
from src.wind.ntc2018 import (
    compute_kinetic_pressure,
    compute_reference_wind_speed,
    compute_velocity_profile_ntc2018,
    run_ntc2018_wind,
)
from src.wind.outputs import WindResults
from src.wind.service import WindActionService, WindConfig

# ---------------------------------------------------------------------------
# Fixture helpers
# ---------------------------------------------------------------------------


def _default_site() -> WindSite:
    return WindSite(altitude_m=100.0, terrain_category="II")


def _default_building() -> BuildingGeom:
    return BuildingGeom(height_m=20.0, width_m=15.0, depth_m=12.0)


# ---------------------------------------------------------------------------
# NTC2018
# ---------------------------------------------------------------------------


def test_ntc2018_reference_speed_positive():
    """La velocità di riferimento deve essere positiva."""
    site = _default_site()
    v_ref = compute_reference_wind_speed(site)
    assert v_ref > 0


def test_ntc2018_reference_speed_override():
    """Se reference_wind_speed_ms è impostato, deve essere usato direttamente."""
    site = WindSite(altitude_m=0, terrain_category="II", reference_wind_speed_ms=30.0)
    v_ref = compute_reference_wind_speed(site)
    assert v_ref == pytest.approx(30.0)


def test_ntc2018_kinetic_pressure_positive():
    """La pressione cinetica deve essere positiva."""
    q = compute_kinetic_pressure(25.0)
    assert q > 0


def test_ntc2018_kinetic_pressure_formula():
    """q = 0.5 * 1.25 * v² / 1000 deve corrispondere al valore atteso."""
    v = 25.0
    expected_q = 0.5 * 1.25 * v**2 / 1000.0
    q = compute_kinetic_pressure(v)
    assert q == pytest.approx(expected_q)


def test_ntc2018_velocity_profile_positive():
    """Il profilo NTC2018 deve avere velocità positive."""
    site = _default_site()
    z_values = [2.0, 5.0, 10.0, 15.0, 20.0]
    profile = compute_velocity_profile_ntc2018(site, 25.0, z_values)
    assert all(pt.v_m_s > 0 for pt in profile)


def test_ntc2018_velocity_profile_monotonic():
    """Il profilo di velocità NTC2018 deve essere monotono crescente."""
    site = _default_site()
    z_values = [2.0, 5.0, 10.0, 15.0, 20.0]
    profile = compute_velocity_profile_ntc2018(site, 25.0, z_values)
    for i in range(1, len(profile)):
        assert profile[i].v_m_s >= profile[i - 1].v_m_s * 0.99, (
            f"Non monotono: z={profile[i].z_m}, v={profile[i].v_m_s} "
            f"< v_prev={profile[i - 1].v_m_s}"
        )


def test_ntc2018_profile_pressure_positive():
    """Il profilo NTC2018 deve avere pressioni cinetiche positive."""
    site = _default_site()
    z_values = [2.0, 5.0, 10.0, 15.0, 20.0]
    profile = compute_velocity_profile_ntc2018(site, 25.0, z_values)
    assert all(pt.q_kN_m2 > 0 for pt in profile)


def test_ntc2018_run_returns_wind_results():
    """run_ntc2018_wind deve restituire un WindResults valido."""
    site = _default_site()
    building = _default_building()
    results = run_ntc2018_wind(site, building)
    assert isinstance(results, WindResults)


def test_ntc2018_run_profile_not_empty():
    """Il profilo calcolato da run_ntc2018_wind non deve essere vuoto."""
    results = run_ntc2018_wind(_default_site(), _default_building())
    assert len(results.velocity_profile) >= 1


def test_ntc2018_run_q_b_positive():
    """Pressione cinetica di base qb deve essere positiva."""
    results = run_ntc2018_wind(_default_site(), _default_building())
    assert results.q_b_kN_m2 > 0


def test_ntc2018_unknown_terrain_category():
    """Categoria terreno sconosciuta deve usare il default senza crash."""
    site = WindSite(altitude_m=0, terrain_category="UNKNOWN")
    building = _default_building()
    results = run_ntc2018_wind(site, building)
    assert isinstance(results, WindResults)
    assert len(results.velocity_profile) >= 1


# ---------------------------------------------------------------------------
# EN 1991-1-4
# ---------------------------------------------------------------------------


def test_en1991_mean_velocity_positive():
    """La velocità media EN1991 deve essere positiva."""
    v = compute_mean_wind_velocity(10.0, 25.0, "II")
    assert v > 0


def test_en1991_velocity_increases_with_height():
    """La velocità media deve aumentare con la quota."""
    v5 = compute_mean_wind_velocity(5.0, 25.0, "II")
    v20 = compute_mean_wind_velocity(20.0, 25.0, "II")
    assert v20 > v5


def test_en1991_run_returns_wind_results():
    """run_en1991_1_4_wind deve restituire un WindResults valido."""
    results = run_en1991_1_4_wind(_default_site(), _default_building())
    assert isinstance(results, WindResults)
    assert results.method == "EN1991_1_4"


def test_en1991_profile_monotonic():
    """Il profilo EN1991 deve essere monotono."""
    results = run_en1991_1_4_wind(_default_site(), _default_building())
    profile = results.velocity_profile
    for i in range(1, len(profile)):
        assert profile[i].v_m_s >= profile[i - 1].v_m_s * 0.99


# ---------------------------------------------------------------------------
# WindActionService
# ---------------------------------------------------------------------------


def test_service_ntc2018():
    """WindActionService con NTC2018 deve restituire WindResults."""
    service = WindActionService()
    config = WindConfig(method="NTC2018", site=_default_site(), building=_default_building())
    results = service.compute(config)
    assert isinstance(results, WindResults)
    assert results.method == "NTC2018"


def test_service_en1991():
    """WindActionService con EN1991_1_4 deve restituire WindResults."""
    service = WindActionService()
    config = WindConfig(method="EN1991_1_4", site=_default_site(), building=_default_building())
    results = service.compute(config)
    assert isinstance(results, WindResults)
    assert results.method == "EN1991_1_4"


def test_service_cnr_dt207():
    """WindActionService con CNR_DT207 deve restituire WindResults arricchiti."""
    service = WindActionService()
    config = WindConfig(method="CNR_DT207", site=_default_site(), building=_default_building())
    results = service.compute(config)
    assert isinstance(results, WindResults)
    assert "cnr_dt207" in results.extra


def test_service_hybrid():
    """WindActionService con hybrid deve restituire WindResults."""
    service = WindActionService()
    config = WindConfig(method="hybrid", site=_default_site(), building=_default_building())
    results = service.compute(config)
    assert isinstance(results, WindResults)
    assert results.method == "hybrid"


def test_service_unknown_method_no_crash():
    """Metodo sconosciuto non deve crashare; usa NTC2018 con warning."""
    service = WindActionService()
    config = WindConfig(method="UNKNOWN_METHOD", site=_default_site(), building=_default_building())
    results = service.compute(config)
    assert isinstance(results, WindResults)
    assert any("non riconosciuto" in w or "UNKNOWN" in w for w in results.warnings)


def test_service_zero_height_no_crash():
    """Edificio con altezza zero non deve crashare."""
    service = WindActionService()
    config = WindConfig(
        method="NTC2018",
        site=_default_site(),
        building=BuildingGeom(height_m=0.0),
    )
    results = service.compute(config)
    assert isinstance(results, WindResults)
    assert len(results.velocity_profile) >= 1


def test_service_apply_cnr_dt207():
    """apply_cnr_dt207=True deve arricchire i risultati NTC2018."""
    service = WindActionService()
    config = WindConfig(
        method="NTC2018",
        site=_default_site(),
        building=_default_building(),
        apply_cnr_dt207=True,
    )
    results = service.compute(config)
    assert "cnr_dt207" in results.extra


def test_service_profile_consistent():
    """Il profilo deve avere le stesse quote per NTC e EN."""
    service = WindActionService()
    ntc_cfg = WindConfig(method="NTC2018", site=_default_site(), building=_default_building())
    en_cfg = WindConfig(method="EN1991_1_4", site=_default_site(), building=_default_building())

    ntc_r = service.compute(ntc_cfg)
    en_r = service.compute(en_cfg)

    # Stessa altezza edificio → stesso numero punti profilo
    assert len(ntc_r.velocity_profile) == len(en_r.velocity_profile)


# ---------------------------------------------------------------------------
# Service — strutture speciali (insegne con zone pressioni)
# ---------------------------------------------------------------------------


def test_service_sign_global_force():
    """Service con SIGN deve calcolare forza globale."""
    service = WindActionService()
    config = WindConfig(
        method="NTC2018",
        site=_default_site(),
        structure=StructureGeom(
            structure_type="SIGN",
            width_m=4.0,
            height_m=2.0,
            ground_clearance_m=3.0,
        ),
    )
    results = service.compute(config)
    assert len(results.pressure_zones) >= 1
    assert results.pressure_zones[0].zone_id == "sign"
    assert results.extra.get("sign_eccentricity_m", 0) == pytest.approx(1.0)


def test_service_sign_zone_pressures():
    """Service con sign_zone_pressures=True deve generare zone A/B/C/D."""
    service = WindActionService()
    config = WindConfig(
        method="NTC2018",
        site=_default_site(),
        structure=StructureGeom(
            structure_type="SIGN",
            width_m=6.0,
            height_m=2.0,
            ground_clearance_m=3.0,
        ),
        extra={"sign_zone_pressures": True},
    )
    results = service.compute(config)
    zone_ids = [pz.zone_id for pz in results.pressure_zones]
    assert "sign_A" in zone_ids
    assert "sign_B" in zone_ids
    assert "sign_D" in zone_ids
    # b/h = 3 > 2 → zona C presente
    assert "sign_C" in zone_ids


def test_service_sign_zone_global_force_stored():
    """Service con zone deve comunque salvare la forza globale in extra."""
    service = WindActionService()
    config = WindConfig(
        method="NTC2018",
        site=_default_site(),
        structure=StructureGeom(
            structure_type="SIGN",
            width_m=6.0,
            height_m=2.0,
            ground_clearance_m=3.0,
        ),
        extra={"sign_zone_pressures": True},
    )
    results = service.compute(config)
    assert results.extra.get("sign_global_force_kN", 0) > 0
