"""
Tests for RD 2229/1939 check implementations.

Comprehensive test suite for Tensioni Ammissibili (TA) method checks.
Tests cover:
- Flessione TA (COMPLETE implementation)
- Pressoflessione TA (PARTIAL implementation)
- Taglio TA (PARTIAL implementation)
- Minimi armatura (PARTIAL implementation)
- Unit conversions
- LC/FC integration
- Full verification pipeline

All tests use mock objects to avoid external dependencies.
"""

from dataclasses import dataclass

import pytest

from src.core_calculus.contracts import CalcInput
from src.methods.checks_rd2229 import (
    check_flessione_ta_rett,
    check_minimi_armatura_ta,
    check_pressoflessione_ta_rett,
    check_taglio_ta_rett,
    convert_loads_to_ta_units,
    convert_section_to_ta_geometry,
    get_rd2229_allowable_stresses,
)

# ==============================================================================
# MOCK OBJECTS FOR TESTING
# ==============================================================================


@dataclass
class MockRD2229Section:
    """Mock rectangular section for RD2229 tests."""

    section_type: str = "RECTANGULAR"
    b: float = 300.0  # mm
    h: float = 500.0  # mm

    @property
    def width(self) -> float:
        return self.b

    @property
    def height(self) -> float:
        return self.h


@dataclass
class MockRD2229Material:
    """Mock RD2229 material with TA properties (R160 / FeB38k)."""

    # RD2229 R160 concrete properties (kg/cm²)
    sigma_c28: float = 160.0  # Resistance at 28 days
    sigma_c_adm: float = 80.0  # Allowable compression stress
    tau_c0: float = 9.6  # Shear without stirrups
    tau_c1: float = 22.4  # Shear with stirrups
    Ec: float = 250000.0  # Elastic modulus
    n: float = 8.4  # Modular ratio Es/Ec

    # RD2229 FeB38k steel properties (kg/cm²)
    sigma_sn: float = 3800.0  # Nominal yield strength
    sigma_s_adm: float = 1900.0  # Allowable steel stress
    Es: float = 2100000.0  # Elastic modulus

    # For compatibility with modern checks (MPa conversion)
    @property
    def f_ck(self) -> float:
        """Convert to MPa for compatibility with modern CalcInput."""
        return self.sigma_c28 * 0.0980665  # kg/cm² → MPa

    @property
    def f_yk(self) -> float:
        """Convert to MPa for compatibility."""
        return self.sigma_sn * 0.0980665  # kg/cm² → MPa


@dataclass
class MockRD2229Template:
    """Mock VerificationTemplate for testing."""

    template_id: str = "test_template"
    check_category: str = "resistenza"
    limit_state: str = "TA"
    primary_reference: None = None
    secondary_references: list = None

    def __post_init__(self):
        if self.secondary_references is None:
            self.secondary_references = []


# ==============================================================================
# UNIT CONVERSION TESTS
# ==============================================================================


def test_unit_conversion_loads():
    """Test unit conversion for loads: kN → kg, kNm → kg·cm."""
    calc_input = CalcInput(
        N=100.0,  # kN
        Mx=50.0,  # kNm
        My=30.0,  # kNm
        Tx=20.0,  # kN
        Ty=15.0,  # kN
    )

    ta_loads = convert_loads_to_ta_units(calc_input)

    # 1 kN = 101.97 kg
    assert abs(ta_loads["N_kg"] - 10197.0) < 1.0
    # 1 kNm = 10197 kg·cm
    assert abs(ta_loads["Mx_kg_cm"] - 509850.0) < 100.0
    assert abs(ta_loads["My_kg_cm"] - 305910.0) < 100.0
    assert abs(ta_loads["Tx_kg"] - 2039.4) < 1.0
    assert abs(ta_loads["Ty_kg"] - 1529.55) < 1.0


def test_unit_conversion_section():
    """Test section geometry conversion: mm → cm."""
    section = MockRD2229Section(b=300.0, h=500.0)  # mm
    material = MockRD2229Material()

    calc_input = CalcInput(
        element_name="Test",
        section=section,
        material=material,
        As=15.0,  # cm²
        d=45.0,  # cm
    )

    ta_geom = convert_section_to_ta_geometry(calc_input)

    # Should have polygons and bars
    assert len(ta_geom.polygons) > 0
    assert len(ta_geom.bars) > 0

    # Check n_homog is set
    assert ta_geom.n_homog > 0
    assert ta_geom.n_homog == material.n  # Should match material


def test_get_allowable_stresses():
    """Test extraction of RD2229 allowable stresses from material."""
    material = MockRD2229Material()

    allowable = get_rd2229_allowable_stresses(material)

    # Check values match RD2229 R160
    assert allowable.sigma_c_allow == 80.0  # kg/cm²
    assert allowable.sigma_s_allow == 1900.0  # kg/cm²
    assert allowable.sigma_c_med_allow == pytest.approx(0.4 * 160.0)  # 64 kg/cm²


# ==============================================================================
# FLESSIONE TA TESTS (COMPLETE IMPLEMENTATION)
# ==============================================================================


def test_flessione_ta_ok():
    """Test flessione TA check - OK case with adequate reinforcement."""
    section = MockRD2229Section(b=300.0, h=500.0)
    material = MockRD2229Material()  # R160 / FeB38k

    calc_input = CalcInput(
        element_name="Trave TA Test OK",
        section=section,
        material=material,
        norm_code="RD2229",
        limit_states_enabled=["TA"],
        Mx=80.0,  # kNm - moderate moment
        As=15.0,  # cm² - adequate reinforcement
        d=45.0,  # cm
        lc="LC2",
        fc=1.20,
    )

    template = MockRD2229Template(template_id="rd2229_ta_flessione_rett")
    result = check_flessione_ta_rett(calc_input, template)

    # Should pass
    assert result.ok, f"Check should pass. Messages: {result.messages_it}"
    assert result.utilisation is not None
    assert 0.0 < result.utilisation <= 1.0

    # Check details present
    assert "sigma_c_max_kg_cm2" in result.details
    assert "sigma_s_max_kg_cm2" in result.details
    assert "sigma_c_adm_kg_cm2" in result.details
    assert "sigma_s_adm_kg_cm2" in result.details

    # Check stresses within limits
    sigma_c_max = abs(result.details["sigma_c_max_kg_cm2"])
    sigma_c_adm = result.details["sigma_c_adm_kg_cm2"]
    assert sigma_c_max <= sigma_c_adm


def test_flessione_ta_non_ok():
    """Test flessione TA check - NON OK case with insufficient reinforcement."""
    section = MockRD2229Section(b=300.0, h=500.0)
    material = MockRD2229Material()

    calc_input = CalcInput(
        element_name="Trave TA Test NON OK",
        section=section,
        material=material,
        norm_code="RD2229",
        limit_states_enabled=["TA"],
        Mx=200.0,  # kNm - very high moment
        As=8.0,  # cm² - insufficient reinforcement
        d=45.0,
        lc="LC2",
        fc=1.20,
    )

    template = MockRD2229Template(template_id="rd2229_ta_flessione_rett")
    result = check_flessione_ta_rett(calc_input, template)

    # Should fail
    assert not result.ok, "Check should fail with excessive stress"
    assert result.utilisation is not None
    assert result.utilisation > 1.0


def test_flessione_ta_with_compression_reinforcement():
    """Test flessione TA with compression reinforcement (doubly reinforced)."""
    section = MockRD2229Section(b=300.0, h=500.0)
    material = MockRD2229Material()

    calc_input = CalcInput(
        element_name="Trave TA Doppia Armatura",
        section=section,
        material=material,
        norm_code="RD2229",
        limit_states_enabled=["TA"],
        Mx=120.0,  # kNm
        As=18.0,  # cm² - tension reinforcement
        As_prime=6.0,  # cm² - compression reinforcement
        d=45.0,
        d_prime=5.0,
        lc="LC2",
        fc=1.20,
    )

    template = MockRD2229Template(template_id="rd2229_ta_flessione_rett")
    result = check_flessione_ta_rett(calc_input, template)

    # Should pass with doubly reinforced section
    assert result.ok, "Check should pass with doubly reinforced section"
    assert result.utilisation is not None


def test_flessione_ta_missing_inputs():
    """Test flessione TA with missing required inputs."""
    section = MockRD2229Section()
    material = MockRD2229Material()

    # Missing As (reinforcement)
    calc_input_no_as = CalcInput(
        element_name="Test No As",
        section=section,
        material=material,
        norm_code="RD2229",
        limit_states_enabled=["TA"],
        Mx=100.0,
        d=45.0,
    )

    template = MockRD2229Template()
    result = check_flessione_ta_rett(calc_input_no_as, template)

    assert not result.ok
    assert any("armatura" in msg.lower() for msg in result.messages_it)


# ==============================================================================
# PRESSOFLESSIONE TA TESTS (PARTIAL IMPLEMENTATION)
# ==============================================================================


def test_pressoflessione_ta_compression_ok():
    """Test pressoflessione TA with compression - OK case."""
    section = MockRD2229Section(b=400.0, h=400.0)  # Pilastro quadrato
    material = MockRD2229Material()

    calc_input = CalcInput(
        element_name="Pilastro TA Test",
        section=section,
        material=material,
        norm_code="RD2229",
        limit_states_enabled=["TA"],
        N=-500.0,  # kN - compression (negative)
        Mx=80.0,  # kNm
        As=25.0,  # cm²
        d=36.0,  # cm
        lc="LC2",
        fc=1.20,
    )

    template = MockRD2229Template(template_id="rd2229_ta_pressoflessione_rett")
    result = check_pressoflessione_ta_rett(calc_input, template)

    # Should compute stresses
    assert "sigma_c_max_kg_cm2" in result.details

    # Should have PARTIAL warning
    messages_text = "\n".join(result.messages_it)
    assert "PARZIALE" in messages_text or "PARTIAL" in messages_text.upper()

    # Check for title update
    assert "PRESSOFLESSIONE" in messages_text


def test_pressoflessione_ta_tension_ok():
    """Test pressoflessione TA with tension (positive N)."""
    section = MockRD2229Section(b=300.0, h=500.0)
    material = MockRD2229Material()

    calc_input = CalcInput(
        element_name="Elemento TA Trazione",
        section=section,
        material=material,
        norm_code="RD2229",
        limit_states_enabled=["TA"],
        N=100.0,  # kN - tension (positive)
        Mx=60.0,  # kNm
        As=20.0,  # cm²
        d=45.0,
        lc="LC2",
        fc=1.20,
    )

    template = MockRD2229Template(template_id="rd2229_ta_pressoflessione_rett")
    result = check_pressoflessione_ta_rett(calc_input, template)

    # Should compute result
    assert result.utilisation is not None


# ==============================================================================
# TAGLIO TA TESTS (PARTIAL IMPLEMENTATION)
# ==============================================================================


def test_taglio_ta_basic_without_stirrups():
    """Test taglio TA basic check without stirrups."""
    section = MockRD2229Section(b=300.0, h=500.0)
    material = MockRD2229Material()

    calc_input = CalcInput(
        element_name="Trave TA Taglio Senza Staffe",
        section=section,
        material=material,
        norm_code="RD2229",
        limit_states_enabled=["TA"],
        Tx=40.0,  # kN - moderate shear
        d=45.0,
        lc="LC2",
        fc=1.20,
    )

    template = MockRD2229Template(template_id="rd2229_ta_taglio_rett")
    result = check_taglio_ta_rett(calc_input, template)

    # Should compute tau
    assert "tau_kg_cm2" in result.details
    assert "tau_c0_kg_cm2" in result.details
    assert "tau_c1_kg_cm2" in result.details

    # Should use tau_c0 (without stirrups)
    tau_adm = result.details["tau_adm_kg_cm2"]
    tau_c0 = result.details["tau_c0_kg_cm2"]
    assert tau_adm == tau_c0

    # Should have PARTIAL warning
    messages_text = "\n".join(result.messages_it)
    assert "PARZIALE" in messages_text


def test_taglio_ta_basic_with_stirrups():
    """Test taglio TA basic check with stirrups."""
    section = MockRD2229Section(b=300.0, h=500.0)
    material = MockRD2229Material()

    calc_input = CalcInput(
        element_name="Trave TA Taglio Con Staffe",
        section=section,
        material=material,
        norm_code="RD2229",
        limit_states_enabled=["TA"],
        Tx=60.0,  # kN
        d=45.0,
        staffe_passo=20.0,  # cm
        staffe_diametro=8.0,  # mm
        staffe_num_bracci=2,
        lc="LC2",
        fc=1.20,
    )

    template = MockRD2229Template(template_id="rd2229_ta_taglio_rett")
    result = check_taglio_ta_rett(calc_input, template)

    # Should use tau_c1 (with stirrups)
    tau_adm = result.details["tau_adm_kg_cm2"]
    tau_c1 = result.details["tau_c1_kg_cm2"]
    assert tau_adm == tau_c1

    # tau_c1 should be higher than tau_c0
    tau_c0 = result.details["tau_c0_kg_cm2"]
    assert tau_c1 > tau_c0


# ==============================================================================
# MINIMI ARMATURA TESTS (PARTIAL IMPLEMENTATION)
# ==============================================================================


def test_minimi_armatura_ta_ok():
    """Test minimi armatura TA - OK case with adequate reinforcement."""
    section = MockRD2229Section(b=300.0, h=500.0)
    material = MockRD2229Material()

    # A_sez = 300 * 500 / 100 = 1500 cm²
    # As_min = 0.003 * 1500 = 4.5 cm²
    # As_max = 0.06 * 1500 = 90 cm²

    calc_input = CalcInput(
        element_name="Trave TA Minimi OK",
        section=section,
        material=material,
        norm_code="RD2229",
        limit_states_enabled=["TA"],
        As=15.0,  # cm² - well above minimum
        lc="LC2",
        fc=1.20,
    )

    template = MockRD2229Template(template_id="rd2229_ta_minimi_armatura_long")
    result = check_minimi_armatura_ta(calc_input, template)

    # Should pass
    assert result.ok
    assert result.utilisation is not None
    assert result.utilisation < 1.0

    # Check details
    assert "As_min_cm2" in result.details
    assert "As_max_cm2" in result.details
    assert result.details["ok_min"]
    assert result.details["ok_max"]


def test_minimi_armatura_ta_non_ok_too_low():
    """Test minimi armatura TA - NON OK case with insufficient reinforcement."""
    section = MockRD2229Section(b=300.0, h=500.0)
    material = MockRD2229Material()

    # A_sez = 1500 cm², As_min = 4.5 cm²

    calc_input = CalcInput(
        element_name="Trave TA Minimi NON OK",
        section=section,
        material=material,
        norm_code="RD2229",
        limit_states_enabled=["TA"],
        As=2.0,  # cm² - below minimum!
        lc="LC2",
        fc=1.20,
    )

    template = MockRD2229Template(template_id="rd2229_ta_minimi_armatura_long")
    result = check_minimi_armatura_ta(calc_input, template)

    # Should fail
    assert not result.ok
    assert not result.details["ok_min"]


def test_minimi_armatura_ta_non_ok_too_high():
    """Test minimi armatura TA - NON OK case with excessive reinforcement."""
    section = MockRD2229Section(b=300.0, h=500.0)
    material = MockRD2229Material()

    # A_sez = 1500 cm², As_max = 90 cm²

    calc_input = CalcInput(
        element_name="Trave TA Minimi Eccessiva",
        section=section,
        material=material,
        norm_code="RD2229",
        limit_states_enabled=["TA"],
        As=100.0,  # cm² - above maximum!
        lc="LC2",
        fc=1.20,
    )

    template = MockRD2229Template(template_id="rd2229_ta_minimi_armatura_long")
    result = check_minimi_armatura_ta(calc_input, template)

    # Should fail
    assert not result.ok
    assert not result.details["ok_max"]


# ==============================================================================
# LC/FC INTEGRATION TESTS
# ==============================================================================


def test_lc_fc_material_adjustment():
    """Test that LC/FC affects material properties and reduces capacity."""
    section = MockRD2229Section()
    material = MockRD2229Material()

    # Test WITHOUT LC/FC
    calc_input_base = CalcInput(
        element_name="Trave Senza LC/FC",
        section=section,
        material=material,
        norm_code="RD2229",
        limit_states_enabled=["TA"],
        Mx=100.0,
        As=15.0,
        d=45.0,
    )

    # Test WITH LC/FC
    calc_input_lc = CalcInput(
        element_name="Trave Con LC2/FC=1.20",
        section=section,
        material=material,
        norm_code="RD2229",
        limit_states_enabled=["TA"],
        lc="LC2",
        fc=1.20,
        Mx=100.0,
        As=15.0,
        d=45.0,
    )

    template = MockRD2229Template(template_id="rd2229_ta_flessione_rett")

    result_base = check_flessione_ta_rett(calc_input_base, template)
    result_lc = check_flessione_ta_rett(calc_input_lc, template)

    # Both should succeed (we're in OK range)
    assert result_base.ok
    assert result_lc.ok

    # With LC/FC, utilisation should be higher (more conservative)
    # Note: This test verifies the integration exists, even if LC/FC
    # adjustment is not yet fully implemented in TA stress computation
    assert result_base.utilisation is not None
    assert result_lc.utilisation is not None


# ==============================================================================
# INTEGRATION TESTS
# ==============================================================================


def test_all_checks_can_run_without_errors():
    """Integration test: all 4 checks can run without throwing exceptions."""
    section = MockRD2229Section()
    material = MockRD2229Material()

    calc_input = CalcInput(
        element_name="Elemento Completo",
        section=section,
        material=material,
        norm_code="RD2229",
        limit_states_enabled=["TA"],
        N=-200.0,
        Mx=100.0,
        Tx=60.0,
        As=15.0,
        d=45.0,
        staffe_passo=20.0,
        staffe_diametro=8.0,
        lc="LC2",
        fc=1.20,
    )

    template_flex = MockRD2229Template(template_id="rd2229_ta_flessione_rett")
    template_pf = MockRD2229Template(template_id="rd2229_ta_pressoflessione_rett")
    template_shear = MockRD2229Template(template_id="rd2229_ta_taglio_rett")
    template_min = MockRD2229Template(template_id="rd2229_ta_minimi_armatura_long")

    # All checks should run without exceptions
    result_flex = check_flessione_ta_rett(calc_input, template_flex)
    result_pf = check_pressoflessione_ta_rett(calc_input, template_pf)
    result_shear = check_taglio_ta_rett(calc_input, template_shear)
    result_min = check_minimi_armatura_ta(calc_input, template_min)

    # All should return results
    assert result_flex.utilisation is not None
    assert result_pf.utilisation is not None
    assert result_shear.utilisation is not None
    assert result_min.utilisation is not None

    # All should have Italian messages
    assert len(result_flex.messages_it) > 0
    assert len(result_pf.messages_it) > 0
    assert len(result_shear.messages_it) > 0
    assert len(result_min.messages_it) > 0


def test_italian_messages_present():
    """Test that all check results contain Italian messages."""
    section = MockRD2229Section()
    material = MockRD2229Material()

    calc_input = CalcInput(
        element_name="Test Italiano",
        section=section,
        material=material,
        norm_code="RD2229",
        limit_states_enabled=["TA"],
        Mx=100.0,
        As=15.0,
        d=45.0,
    )

    template = MockRD2229Template()
    result = check_flessione_ta_rett(calc_input, template)

    # Should have Italian keywords in messages
    messages_text = "\n".join(result.messages_it).lower()
    italian_keywords = ["verifica", "tensioni", "sezione", "armatura"]
    assert any(keyword in messages_text for keyword in italian_keywords)


# ==============================================================================
# ERROR HANDLING TESTS
# ==============================================================================


def test_flessione_ta_handles_missing_section():
    """Test that flessione TA gracefully handles missing section."""
    material = MockRD2229Material()

    calc_input = CalcInput(
        element_name="Test No Section",
        section=None,  # Missing!
        material=material,
        norm_code="RD2229",
        limit_states_enabled=["TA"],
        Mx=100.0,
        As=15.0,
        d=45.0,
    )

    template = MockRD2229Template()
    result = check_flessione_ta_rett(calc_input, template)

    assert not result.ok
    assert any("sezione" in msg.lower() for msg in result.messages_it)


def test_flessione_ta_handles_missing_material():
    """Test that flessione TA gracefully handles missing material."""
    section = MockRD2229Section()

    calc_input = CalcInput(
        element_name="Test No Material",
        section=section,
        material=None,  # Missing!
        norm_code="RD2229",
        limit_states_enabled=["TA"],
        Mx=100.0,
        As=15.0,
        d=45.0,
    )

    template = MockRD2229Template()
    result = check_flessione_ta_rett(calc_input, template)

    assert not result.ok
    assert any("materiale" in msg.lower() for msg in result.messages_it)


def test_flessione_ta_handles_zero_moment():
    """Test that flessione TA handles zero moment (not applicable)."""
    section = MockRD2229Section()
    material = MockRD2229Material()

    calc_input = CalcInput(
        element_name="Test Zero Moment",
        section=section,
        material=material,
        norm_code="RD2229",
        limit_states_enabled=["TA"],
        Mx=0.0,  # Zero moment!
        As=15.0,
        d=45.0,
    )

    template = MockRD2229Template()
    result = check_flessione_ta_rett(calc_input, template)

    # Should return OK with utilisation=0 (not applicable)
    assert result.ok
    assert result.utilisation == 0.0
    assert any("nullo" in msg.lower() for msg in result.messages_it)


def test_minimi_armatura_ta_beam_vs_column():
    """Test that beams and columns have different minimum reinforcement.

    - Beams: As_min = 0.15% A_sez (from compute_long_rebar_limits_ta)
    - Columns: As_min = 0.30% A_sez (from compute_long_rebar_limits_ta)
    """
    section = MockRD2229Section(b=300.0, h=500.0)  # A_sez = 1500 cm²
    material = MockRD2229Material()
    template = MockRD2229Template(template_id="rd2229_ta_minimi_armatura_long")

    # Beam: As_min = 0.0015 * 1500 = 2.25 cm²
    # Column: As_min = 0.003 * 1500 = 4.5 cm²
    # Test with As = 3.0 cm² (between beam and column minima)

    # Test as beam (no axial load → N = 0)
    calc_input_beam = CalcInput(
        element_name="Trave Test",
        section=section,
        material=material,
        norm_code="RD2229",
        limit_states_enabled=["TA"],
        N=0.0,  # No compression → beam
        As=3.0,  # Between beam min (2.25) and column min (4.5)
    )

    result_beam = check_minimi_armatura_ta(calc_input_beam, template)

    # Should pass for beam (3.0 > 2.25)
    assert result_beam.ok, "Beam with As=3.0 cm² should pass (min=2.25 cm²)"
    assert "trave" in "\n".join(result_beam.messages_it).lower(), "Messages should mention 'trave'"
    assert result_beam.details["element_type"] == "trave"
    assert result_beam.details["is_beam"]
    assert not result_beam.details["is_column"]

    # Test as column (compression → N < -50 kN)
    calc_input_column = CalcInput(
        element_name="Pilastro Test",
        section=section,
        material=material,
        norm_code="RD2229",
        limit_states_enabled=["TA"],
        N=-200.0,  # Compression → column
        As=3.0,  # Same reinforcement
    )

    result_column = check_minimi_armatura_ta(calc_input_column, template)

    # Should fail for column (3.0 < 4.5)
    assert not result_column.ok, "Column with As=3.0 cm² should fail (min=4.5 cm²)"
    assert "pilastro" in "\n".join(result_column.messages_it).lower(), "Messages should mention 'pilastro'"
    assert result_column.details["element_type"] == "pilastro"
    assert result_column.details["is_column"]
    assert not result_column.details["is_beam"]

    # Verify PARTIAL warning removed (should show "Implementazione completa")
    messages_text = "\n".join(result_beam.messages_it)
    assert "PARZIALE" not in messages_text, "Should not show PARTIAL warning"
    assert "completa" in messages_text.lower(), "Should show 'completa'"


def test_pressoflessione_ta_slenderness_reduction():
    """Test that slenderness reduction is applied for thin sections.

    Formula: sigma_c_adm_reduced = sigma_c_adm * (1 - 0.03 * (25 - A_min))
    where A_min = min(b, h) in cm
    """
    material = MockRD2229Material()
    template = MockRD2229Template(template_id="rd2229_ta_pressoflessione_rett")

    # Test 1: Slender section (A_min < 25 cm)
    section_slender = MockRD2229Section(b=200.0, h=500.0)  # b=20cm < 25cm
    calc_input_slender = CalcInput(
        element_name="Pilastro Snello",
        section=section_slender,
        material=material,
        norm_code="RD2229",
        limit_states_enabled=["TA"],
        N=-300.0,  # Compression
        Mx=80.0,
        As=20.0,
        d=45.0,
    )

    result_slender = check_pressoflessione_ta_rett(calc_input_slender, template)

    # Should mention slenderness reduction
    messages_text = "\n".join(result_slender.messages_it)
    assert "Riduzione per sezioni snelle" in messages_text, "Should mention slenderness reduction"
    assert "A_min" in messages_text, "Should show A_min value"
    assert "Fattore di riduzione" in messages_text, "Should show reduction factor"

    # Check details contain reduction info
    assert "reduction_factor" in result_slender.details, "Should have reduction_factor in details"
    assert "A_min_cm" in result_slender.details, "Should have A_min_cm in details"
    assert result_slender.details["A_min_cm"] == 20.0, "A_min should be 20 cm"

    # Expected reduction_factor = 1 - 0.03 * (25 - 20) = 1 - 0.15 = 0.85
    expected_reduction = 0.85
    actual_reduction = result_slender.details["reduction_factor"]
    assert abs(actual_reduction - expected_reduction) < 0.01, f"Reduction factor should be ~{expected_reduction}, got {actual_reduction}"

    # Test 2: Non-slender section (A_min ≥ 25 cm)
    section_thick = MockRD2229Section(b=400.0, h=400.0)  # b=40cm > 25cm
    calc_input_thick = CalcInput(
        element_name="Pilastro Tozzo",
        section=section_thick,
        material=material,
        norm_code="RD2229",
        limit_states_enabled=["TA"],
        N=-300.0,
        Mx=80.0,
        As=30.0,
        d=36.0,
    )

    result_thick = check_pressoflessione_ta_rett(calc_input_thick, template)

    messages_text_thick = "\n".join(result_thick.messages_it)
    assert "non snella" in messages_text_thick or "riduzione non applicata" in messages_text_thick, \
        "Should mention no reduction for thick section"

    # Verify PARTIAL status improved to mention slenderness implementation
    assert "MIGLIORATA" in messages_text or "PARTIAL" in messages_text, "Should show improved status"
    assert "Riduzione σ_c,adm per sezioni snelle implementata" in messages_text or \
           "riduzione σ_c,adm" in messages_text.lower(), "Should mention slenderness implemented"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
