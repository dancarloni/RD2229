"""
Golden test per la migrazione VBA → Python: CA_SLU::VerifResistCA_SLU_TensNorm
sub-calcolo Nu_max / Nu_min.

I valori di riferimento sono calcolati analiticamente a partire dai parametri
di input dichiarati nella scheda macro (docs/specs/VBA_MACRO_SCHEDA_CA_SLU.md).
Tolleranza: ≤ 0.5% per Nu_max/Nu_min (come da scheda macro).

Caso di riferimento (golden baseline):
    Sezione rettangolare: B=300 mm, H=500 mm
    Calcestruzzo C25/30: fck=25 MPa, γc=1.5
    Acciaio B450C: fyk=450 MPa, γs=1.15
    Armatura: 4φ16, Aft = 4 * π * 16²/4 = 804.25 mm²
    Ned = -800 kN (compressione)
"""

import math

import pytest

from src.rd2229.mvp.vba_migration.ca_slu_nu_limits import (
    AxialCapacityResult,
    RectSectionInput,
    bar_area_mm2,
    compute_axial_capacity,
)

# ---------------------------------------------------------------------------
# Dati golden baseline (scheda macro VBA_MACRO_SCHEDA_CA_SLU.md)
# ---------------------------------------------------------------------------
B_MM = 300.0  # mm
H_MM = 500.0  # mm
FCK = 25.0  # MPa  (C25/30)
FYK = 450.0  # MPa  (B450C)
GAMMA_C = 1.5
GAMMA_S = 1.15
DIAM_BAR = 16.0  # mm  (φ16)
N_BARS = 4

AFT_MM2 = bar_area_mm2(DIAM_BAR, N_BARS)  # 4 * π * 16² / 4

TOLERANCE_REL = 0.005  # 0.5%

# Valori attesi calcolati analiticamente
_FCD = FCK / GAMMA_C  # 16.667 MPa
_FYD = FYK / GAMMA_S  # 391.304 MPa
_ASEZ = B_MM * H_MM  # 150000 mm²
_NU_MAX_N = AFT_MM2 * _FYD  # N
_NU_MIN_N = -(_FCD * _ASEZ + AFT_MM2 * _FYD)  # N


def _rel_err(computed: float, expected: float) -> float:
    """Errore relativo assoluto."""
    if abs(expected) < 1e-9:
        return abs(computed)
    return abs(computed - expected) / abs(expected)


# ---------------------------------------------------------------------------
# Test: bar_area_mm2 helper
# ---------------------------------------------------------------------------


def test_bar_area_helper_4phi16():
    """4 barre φ16: area attesa = 4 * π * 256/4 = 804.25 mm²."""
    expected = 4 * math.pi * 16**2 / 4
    assert abs(bar_area_mm2(16.0, 4) - expected) < 0.01


def test_bar_area_single_phi12():
    """1 barra φ12: area attesa = π * 144/4 = 113.10 mm²."""
    expected = math.pi * 12**2 / 4
    assert abs(bar_area_mm2(12.0, 1) - expected) < 0.01


# ---------------------------------------------------------------------------
# Test: validazione input
# ---------------------------------------------------------------------------


def test_invalid_section_dimensions():
    with pytest.raises(ValueError, match="dimensioni"):
        RectSectionInput(b_mm=0.0, h_mm=500.0, aft_mm2=800.0, fck_mpa=25.0, fyk_mpa=450.0)


def test_invalid_negative_area():
    with pytest.raises(ValueError, match="armatura"):
        RectSectionInput(b_mm=300.0, h_mm=500.0, aft_mm2=-1.0, fck_mpa=25.0, fyk_mpa=450.0)


# ---------------------------------------------------------------------------
# Test golden: Nu_max
# ---------------------------------------------------------------------------


def test_golden_nu_max():
    """Nu_max golden: 4φ16 B450C → ≈ 314.7 kN (tolleranza ≤ 0.5%)."""
    inp = RectSectionInput(
        b_mm=B_MM,
        h_mm=H_MM,
        aft_mm2=AFT_MM2,
        fck_mpa=FCK,
        fyk_mpa=FYK,
        gamma_c=GAMMA_C,
        gamma_s=GAMMA_S,
    )
    result = compute_axial_capacity(inp)
    assert (
        _rel_err(result.nu_max_n, _NU_MAX_N) <= TOLERANCE_REL
    ), f"Nu_max: calcolato={result.nu_max_kn:.2f} kN, atteso={_NU_MAX_N/1000:.2f} kN"


# ---------------------------------------------------------------------------
# Test golden: Nu_min
# ---------------------------------------------------------------------------


def test_golden_nu_min():
    """Nu_min golden: C25/30 + 4φ16 B450C → ≈ -2814.7 kN (tolleranza ≤ 0.5%)."""
    inp = RectSectionInput(
        b_mm=B_MM,
        h_mm=H_MM,
        aft_mm2=AFT_MM2,
        fck_mpa=FCK,
        fyk_mpa=FYK,
        gamma_c=GAMMA_C,
        gamma_s=GAMMA_S,
    )
    result = compute_axial_capacity(inp)
    assert (
        _rel_err(result.nu_min_n, _NU_MIN_N) <= TOLERANCE_REL
    ), f"Nu_min: calcolato={result.nu_min_kn:.2f} kN, atteso={_NU_MIN_N/1000:.2f} kN"


# ---------------------------------------------------------------------------
# Test: verifica assiale per Ned nel dominio
# ---------------------------------------------------------------------------


def test_check_axial_within_domain():
    """Ned = -800 kN → ok_axial True, eta ≈ 0.284."""
    inp = RectSectionInput(
        b_mm=B_MM,
        h_mm=H_MM,
        aft_mm2=AFT_MM2,
        fck_mpa=FCK,
        fyk_mpa=FYK,
        gamma_c=GAMMA_C,
        gamma_s=GAMMA_S,
    )
    result = compute_axial_capacity(inp)
    ned_n = -800_000.0  # -800 kN in N
    ok_axial, eta = result.check_axial(ned_n)
    assert ok_axial, "Ned=-800kN deve essere nel dominio"
    assert 0.0 < eta < 1.0, f"eta={eta:.4f} deve essere in (0, 1)"
    expected_eta = abs(ned_n) / abs(_NU_MIN_N)
    assert _rel_err(eta, expected_eta) <= 0.01


def test_check_axial_outside_domain_compression():
    """Ned oltre Nu_min → ok_axial False."""
    inp = RectSectionInput(
        b_mm=B_MM,
        h_mm=H_MM,
        aft_mm2=AFT_MM2,
        fck_mpa=FCK,
        fyk_mpa=FYK,
        gamma_c=GAMMA_C,
        gamma_s=GAMMA_S,
    )
    result = compute_axial_capacity(inp)
    ned_n = -5_000_000.0  # -5000 kN, molto oltre Nu_min
    ok_axial, eta = result.check_axial(ned_n)
    assert not ok_axial
    assert eta > 1.0


# ---------------------------------------------------------------------------
# Test: proprietà AxialCapacityResult
# ---------------------------------------------------------------------------


def test_result_properties():
    """Verifica coerenza proprietà kN e parametri derivati."""
    inp = RectSectionInput(
        b_mm=B_MM,
        h_mm=H_MM,
        aft_mm2=AFT_MM2,
        fck_mpa=FCK,
        fyk_mpa=FYK,
        gamma_c=GAMMA_C,
        gamma_s=GAMMA_S,
    )
    result: AxialCapacityResult = compute_axial_capacity(inp)
    # nu_max_kn = nu_max_n / 1000
    assert abs(result.nu_max_kn - result.nu_max_n / 1000.0) < 1e-9
    # nu_min_kn = nu_min_n / 1000
    assert abs(result.nu_min_kn - result.nu_min_n / 1000.0) < 1e-9
    # fcd e fyd corretti
    assert abs(result.fcd_mpa - FCK / GAMMA_C) < 1e-6
    assert abs(result.fyd_mpa - FYK / GAMMA_S) < 1e-6
    # Asez = B * H
    assert abs(result.asez_mm2 - B_MM * H_MM) < 1e-9
    # Nu_min deve essere negativo
    assert result.nu_min_n < 0
    # Nu_max deve essere positivo per armatura ≥ 0
    assert result.nu_max_n >= 0
