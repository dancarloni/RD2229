"""
Comprehensive tests for NTC 2018 check implementations.

Tests:
- Flessione semplice SLU (neutral axis calculation)
- Minimi armatura flessione (f_ctm extraction + NTC formula)
- Taglio SLU (V_Rd calculation with stirrups)
- Minimi armatura taglio
- LC/FC integration
- Full verification pipeline
"""

from __future__ import annotations

from dataclasses import dataclass

from src.core_calculus.contracts import CalcInput
from src.core_calculus.normative_registry import get_ntc2018_templates
from src.methods.ntc2018.checks import (
    check_flessione_slu_rett,
    check_minimi_armatura_flessione_slu,
    check_minimi_armatura_taglio_slu,
    check_taglio_slu,
)


# Mock section and material classes for testing
@dataclass
class MockRectangularSection:
    """Mock rectangular section for testing."""

    section_type: str = "RECTANGULAR"
    b: float = 300.0  # mm - width
    h: float = 500.0  # mm - height

    # For compatibility with older code
    @property
    def width(self) -> float:
        return self.b

    @property
    def height(self) -> float:
        return self.h


@dataclass
class MockConcreteMaterial:
    """Mock concrete material for testing."""

    f_ck: float = 25.0  # MPa
    f_yk: float = 450.0  # MPa
    f_ctm: float | None = None  # Will be computed if None


# ============================================================================
# Tests for Flessione SLU
# ============================================================================


def test_flessione_slu_singly_reinforced_ok():
    """Test flexural check for singly reinforced section - OK case."""
    section = MockRectangularSection(b=300.0, h=500.0)
    material = MockConcreteMaterial(f_ck=25.0, f_yk=450.0)

    calc_input = CalcInput(
        element_name="Trave Test Flessione",
        section=section,
        material=material,
        norm_code="NTC2018",
        limit_states_enabled=["SLU"],
        Mx=100.0,  # kNm - moderate moment
        As=15.0,  # cm² - adequate reinforcement (4φ22)
        d=45.0,  # cm
    )

    # Get template
    templates = get_ntc2018_templates()
    template_flex = [t for t in templates if t.template_id == "ntc2018_slu_flessione_rett"][0]

    # Run check
    result = check_flessione_slu_rett(calc_input, template_flex)

    assert result.ok, f"Check should pass. Messages: {result.messages_it}"
    assert result.utilisation is not None
    assert 0.0 < result.utilisation < 1.0, "Utilisation should be reasonable"
    assert "M_Rd_kNm" in result.details
    assert result.details["M_Rd_kNm"] > calc_input.Mx, "M_Rd should exceed M_Ed"


def test_flessione_slu_singly_reinforced_non_ok():
    """Test flexural check for singly reinforced section - NON OK case."""
    section = MockRectangularSection(b=300.0, h=500.0)
    material = MockConcreteMaterial(f_ck=25.0, f_yk=450.0)

    calc_input = CalcInput(
        element_name="Trave Test Flessione NON OK",
        section=section,
        material=material,
        norm_code="NTC2018",
        limit_states_enabled=["SLU"],
        Mx=200.0,  # kNm - high moment
        As=8.0,  # cm² - insufficient reinforcement
        d=45.0,  # cm
    )

    templates = get_ntc2018_templates()
    template_flex = [t for t in templates if t.template_id == "ntc2018_slu_flessione_rett"][0]

    result = check_flessione_slu_rett(calc_input, template_flex)

    assert not result.ok, "Check should fail with insufficient reinforcement"
    assert result.utilisation > 1.0, "Utilisation should exceed 1.0"


def test_flessione_slu_doubly_reinforced():
    """Test flexural check for doubly reinforced section."""
    section = MockRectangularSection(b=300.0, h=500.0)
    material = MockConcreteMaterial(f_ck=25.0, f_yk=450.0)

    calc_input = CalcInput(
        element_name="Trave Test Doppia Armatura",
        section=section,
        material=material,
        norm_code="NTC2018",
        limit_states_enabled=["SLU"],
        Mx=150.0,  # kNm
        As=18.0,  # cm² - tensile reinforcement
        As_prime=6.0,  # cm² - compression reinforcement
        d=45.0,  # cm
        d_prime=5.0,  # cm
    )

    templates = get_ntc2018_templates()
    template_flex = [t for t in templates if t.template_id == "ntc2018_slu_flessione_rett"][0]

    result = check_flessione_slu_rett(calc_input, template_flex)

    assert result.ok, "Check should pass with doubly reinforced section"
    assert "x_mm" in result.details
    assert "M_Rd_kNm" in result.details


def test_flessione_slu_ductility_warning():
    """Test that ductility warning is triggered for x/d > 0.45."""
    section = MockRectangularSection(b=300.0, h=500.0)
    material = MockConcreteMaterial(f_ck=25.0, f_yk=450.0)

    calc_input = CalcInput(
        element_name="Trave Test Duttilità",
        section=section,
        material=material,
        norm_code="NTC2018",
        limit_states_enabled=["SLU"],
        Mx=80.0,  # kNm
        As=50.0,  # cm² - very high reinforcement to trigger x/d > 0.45
        d=45.0,  # cm
    )

    templates = get_ntc2018_templates()
    template_flex = [t for t in templates if t.template_id == "ntc2018_slu_flessione_rett"][0]

    result = check_flessione_slu_rett(calc_input, template_flex)

    # Check that x_over_d is in details
    assert "x_over_d" in result.details
    # The warning should appear in messages
    messages_text = "\n".join(result.messages_it)
    if result.details["x_over_d"] > 0.45:
        assert "duttilità" in messages_text.lower() or "0.45" in messages_text


# ============================================================================
# Tests for Minimi Armatura Flessione
# ============================================================================


def test_minimi_armatura_flessione_ok():
    """Test minimum flexural reinforcement check - OK case."""
    section = MockRectangularSection(b=300.0, h=500.0)
    material = MockConcreteMaterial(f_ck=25.0, f_yk=450.0)

    calc_input = CalcInput(
        element_name="Trave Test Minimi OK",
        section=section,
        material=material,
        norm_code="NTC2018",
        limit_states_enabled=["SLU"],
        As=8.0,  # cm² - should be above minimum for 30x50 section
        d=45.0,  # cm
    )

    templates = get_ntc2018_templates()
    template_min = [t for t in templates if t.template_id == "ntc2018_slu_minimi_armatura_fless"][0]

    result = check_minimi_armatura_flessione_slu(calc_input, template_min)

    assert result.ok, f"Check should pass. Messages: {result.messages_it}"
    assert "As_min_cm2" in result.details
    assert result.details["As_min_cm2"] <= calc_input.As * 100  # As in cm², details in mm²


def test_minimi_armatura_flessione_non_ok():
    """Test minimum flexural reinforcement check - NON OK case."""
    section = MockRectangularSection(b=300.0, h=500.0)
    material = MockConcreteMaterial(f_ck=25.0, f_yk=450.0)

    calc_input = CalcInput(
        element_name="Trave Test Minimi NON OK",
        section=section,
        material=material,
        norm_code="NTC2018",
        limit_states_enabled=["SLU"],
        As=1.0,  # cm² - too low
        d=45.0,  # cm
    )

    templates = get_ntc2018_templates()
    template_min = [t for t in templates if t.template_id == "ntc2018_slu_minimi_armatura_fless"][0]

    result = check_minimi_armatura_flessione_slu(calc_input, template_min)

    assert not result.ok, "Check should fail with insufficient As"
    assert result.utilisation > 1.0


def test_minimi_armatura_flessione_f_ctm_computation():
    """Test that f_ctm is computed correctly when not provided."""
    section = MockRectangularSection(b=300.0, h=500.0)
    material = MockConcreteMaterial(f_ck=30.0, f_yk=450.0, f_ctm=None)

    calc_input = CalcInput(
        element_name="Trave Test f_ctm",
        section=section,
        material=material,
        norm_code="NTC2018",
        limit_states_enabled=["SLU"],
        As=8.0,  # cm²
        d=45.0,  # cm
    )

    templates = get_ntc2018_templates()
    template_min = [t for t in templates if t.template_id == "ntc2018_slu_minimi_armatura_fless"][0]

    result = check_minimi_armatura_flessione_slu(calc_input, template_min)

    # Check that f_ctm was computed
    assert "f_ctm_MPa" in result.details
    f_ctm_computed = result.details["f_ctm_MPa"]
    # For C30, f_ctm ≈ 2.9 MPa (using formula 0.30 * f_ck^(2/3))
    assert 2.5 < f_ctm_computed < 3.5, f"f_ctm should be around 2.9 MPa, got {f_ctm_computed}"


# ============================================================================
# Tests for Taglio SLU
# ============================================================================


def test_taglio_slu_ok():
    """Test shear check with adequate stirrups - OK case."""
    section = MockRectangularSection(b=300.0, h=500.0)
    material = MockConcreteMaterial(f_ck=25.0, f_yk=450.0)

    calc_input = CalcInput(
        element_name="Trave Test Taglio OK",
        section=section,
        material=material,
        norm_code="NTC2018",
        limit_states_enabled=["SLU"],
        Tx=80.0,  # kN - moderate shear
        d=45.0,  # cm
        staffe_diametro=8.0,  # mm - φ8
        staffe_passo=20.0,  # cm
        staffe_num_bracci=2,
    )

    templates = get_ntc2018_templates()
    template_shear = [t for t in templates if t.template_id == "ntc2018_slu_taglio"][0]

    result = check_taglio_slu(calc_input, template_shear)

    assert result.ok, f"Check should pass. Messages: {result.messages_it}"
    assert "V_Rd_kN" in result.details
    assert result.details["V_Rd_kN"] > calc_input.Tx, "V_Rd should exceed V_Ed"
    assert "V_Rd_s_kN" in result.details
    assert "V_Rd_max_kN" in result.details


def test_taglio_slu_non_ok():
    """Test shear check with insufficient stirrups - NON OK case."""
    section = MockRectangularSection(b=300.0, h=500.0)
    material = MockConcreteMaterial(f_ck=25.0, f_yk=450.0)

    calc_input = CalcInput(
        element_name="Trave Test Taglio NON OK",
        section=section,
        material=material,
        norm_code="NTC2018",
        limit_states_enabled=["SLU"],
        Tx=150.0,  # kN - high shear
        d=45.0,  # cm
        staffe_diametro=6.0,  # mm - φ6 (small)
        staffe_passo=30.0,  # cm (wide spacing)
        staffe_num_bracci=2,
    )

    templates = get_ntc2018_templates()
    template_shear = [t for t in templates if t.template_id == "ntc2018_slu_taglio"][0]

    result = check_taglio_slu(calc_input, template_shear)

    assert not result.ok, "Check should fail with insufficient stirrups"
    assert result.utilisation > 1.0


def test_taglio_slu_missing_stirrups():
    """Test shear check with missing stirrup data."""
    section = MockRectangularSection(b=300.0, h=500.0)
    material = MockConcreteMaterial(f_ck=25.0, f_yk=450.0)

    calc_input = CalcInput(
        element_name="Trave Test Taglio Senza Staffe",
        section=section,
        material=material,
        norm_code="NTC2018",
        limit_states_enabled=["SLU"],
        Tx=80.0,  # kN
        d=45.0,  # cm
        # No stirrup data
    )

    templates = get_ntc2018_templates()
    template_shear = [t for t in templates if t.template_id == "ntc2018_slu_taglio"][0]

    result = check_taglio_slu(calc_input, template_shear)

    # Should return error result
    assert not result.ok
    messages_text = "\n".join(result.messages_it)
    assert "staffe" in messages_text.lower() or "mancant" in messages_text.lower()


# ============================================================================
# Tests for Minimi Armatura Taglio
# ============================================================================


def test_minimi_armatura_taglio_ok():
    """Test minimum shear reinforcement check - OK case."""
    section = MockRectangularSection(b=300.0, h=500.0)
    material = MockConcreteMaterial(f_ck=25.0, f_yk=450.0)

    calc_input = CalcInput(
        element_name="Trave Test Minimi Taglio OK",
        section=section,
        material=material,
        norm_code="NTC2018",
        limit_states_enabled=["SLU"],
        staffe_diametro=8.0,  # mm
        staffe_passo=20.0,  # cm
        staffe_num_bracci=2,
    )

    templates = get_ntc2018_templates()
    template_min_shear = [
        t for t in templates if t.template_id == "ntc2018_slu_minimi_armatura_taglio"
    ][0]

    result = check_minimi_armatura_taglio_slu(calc_input, template_min_shear)

    assert result.ok, f"Check should pass. Messages: {result.messages_it}"
    assert "Asw_over_s_actual_mm2_mm" in result.details
    assert "Asw_min_over_s_mm2_mm" in result.details


def test_minimi_armatura_taglio_non_ok():
    """Test minimum shear reinforcement check - NON OK case."""
    section = MockRectangularSection(b=300.0, h=500.0)
    material = MockConcreteMaterial(f_ck=25.0, f_yk=450.0)

    calc_input = CalcInput(
        element_name="Trave Test Minimi Taglio NON OK",
        section=section,
        material=material,
        norm_code="NTC2018",
        limit_states_enabled=["SLU"],
        staffe_diametro=6.0,  # mm - small diameter
        staffe_passo=40.0,  # cm - wide spacing
        staffe_num_bracci=2,
    )

    templates = get_ntc2018_templates()
    template_min_shear = [
        t for t in templates if t.template_id == "ntc2018_slu_minimi_armatura_taglio"
    ][0]

    result = check_minimi_armatura_taglio_slu(calc_input, template_min_shear)

    assert not result.ok, "Check should fail with insufficient Asw/s"
    assert result.utilisation > 1.0


# ============================================================================
# Tests for LC/FC Integration
# ============================================================================


def test_lc_fc_integration_in_checks():
    """Test that LC/FC adjustments are properly used in checks."""
    section = MockRectangularSection(b=300.0, h=500.0)
    material = MockConcreteMaterial(f_ck=25.0, f_yk=450.0)

    # Create calc_input with LC/FC - the check function will handle adjustment internally
    calc_input = CalcInput(
        element_name="Trave Test LC/FC",
        section=section,
        material=material,
        norm_code="NTC2018",
        limit_states_enabled=["SLU"],
        lc="LC2",
        fc=1.20,
        Mx=100.0,  # kNm
        As=15.0,  # cm²
        d=45.0,  # cm
    )

    templates = get_ntc2018_templates()
    template_flex = [t for t in templates if t.template_id == "ntc2018_slu_flessione_rett"][0]

    # Run check - LC/FC handled internally
    result = check_flessione_slu_rett(calc_input, template_flex)

    # Check that adjusted values were used
    assert "f_cd_MPa" in result.details
    # f_cd should be lower due to FC adjustment
    # Expected: f_cd = 0.85 * (f_ck/FC) / gamma_c = 0.85 * (25/1.20) / 1.5
    expected_f_cd_reduced = 0.85 * (25.0 / 1.20) / 1.5
    assert abs(result.details["f_cd_MPa"] - expected_f_cd_reduced) < 0.5


def test_lc_fc_reduces_capacity():
    """Test that LC/FC adjustment reduces capacity (more conservative)."""
    section = MockRectangularSection(b=300.0, h=500.0)
    material = MockConcreteMaterial(f_ck=25.0, f_yk=450.0)

    calc_input_base = CalcInput(
        element_name="Trave Senza LC/FC",
        section=section,
        material=material,
        norm_code="NTC2018",
        limit_states_enabled=["SLU"],
        Mx=100.0,
        As=15.0,
        d=45.0,
    )

    calc_input_lc = CalcInput(
        element_name="Trave Con LC2/FC=1.20",
        section=section,
        material=material,
        norm_code="NTC2018",
        limit_states_enabled=["SLU"],
        lc="LC2",
        fc=1.20,
        Mx=100.0,
        As=15.0,
        d=45.0,
    )

    templates = get_ntc2018_templates()
    template_flex = [t for t in templates if t.template_id == "ntc2018_slu_flessione_rett"][0]

    # Run without LC/FC
    result_base = check_flessione_slu_rett(calc_input_base, template_flex)

    # Run with LC/FC - adjustment handled internally by check function
    result_lc = check_flessione_slu_rett(calc_input_lc, template_flex)

    # M_Rd should be lower with LC/FC adjustment
    M_Rd_base = result_base.details["M_Rd_kNm"]
    M_Rd_lc = result_lc.details["M_Rd_kNm"]
    assert M_Rd_lc < M_Rd_base, "M_Rd should be reduced by LC/FC adjustment"


# ============================================================================
# Integration Tests
# ============================================================================


def test_full_verification_pipeline():
    """Test complete verification pipeline with multiple checks."""
    from src.core_calculus.verification_service import run_verifications_for_element

    section = MockRectangularSection(b=300.0, h=500.0)
    material = MockConcreteMaterial(f_ck=25.0, f_yk=450.0)

    calc_input = CalcInput(
        element_name="Trave Test Pipeline Completo",
        section=section,
        material=material,
        norm_code="NTC2018",
        limit_states_enabled=["SLU"],
        Mx=100.0,  # kNm
        Tx=80.0,  # kN
        As=15.0,  # cm²
        d=45.0,  # cm
        staffe_diametro=8.0,  # mm
        staffe_passo=20.0,  # cm
        staffe_num_bracci=2,
    )

    templates = get_ntc2018_templates()

    # Run full verification
    calc_output = run_verifications_for_element(
        calc_input=calc_input,
        active_norm="NTC2018",
        templates_registry=templates,
        enabled_limit_states=["SLU"],
    )

    # Check that multiple checks were run
    assert len(calc_output.per_template_results) >= 3, "Should run at least 3 checks"

    # Check for expected template IDs
    template_ids = list(calc_output.per_template_results.keys())
    assert "ntc2018_slu_flessione_rett" in template_ids
    assert "ntc2018_slu_minimi_armatura_fless" in template_ids
    assert "ntc2018_slu_taglio" in template_ids

    # Check that all checks passed (with adequate reinforcement)
    assert calc_output.ok, "All checks should pass with adequate design"

    # Check summary metrics
    assert "num_verifiche_eseguite" in calc_output.summary_metrics
    assert calc_output.summary_metrics["num_verifiche_eseguite"] >= 3


def test_template_registry_completeness():
    """Test that all NTC 2018 templates are properly configured."""
    templates = get_ntc2018_templates()

    # Should have at least 4 templates (flex, min_flex, shear, min_shear)
    assert len(templates) >= 4, f"Expected at least 4 templates, got {len(templates)}"

    # Check that all templates have required fields
    for template in templates:
        assert template.template_id
        assert template.norm_code == "NTC2018"
        assert template.function_path
        assert template.primary_reference
        assert template.description_it
        assert "implementation_status" in template.extra_params

        # Check that none are placeholders
        status = template.extra_params.get("implementation_status")
        assert status in [
            "complete",
            "partial",
        ], f"Template {template.template_id} has invalid status: {status}"
