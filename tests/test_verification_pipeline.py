"""
Integration test for verification pipeline.

Tests the complete flow:
CalcInput → validate_calc_input → run_verifications_for_element → CalcOutput
"""

from __future__ import annotations

from dataclasses import dataclass

from src.core_calculus.contracts import CalcInput
from src.core_calculus.normative_registry import get_all_templates
from src.core_calculus.validation_engine import validate_calc_input
from src.core_calculus.verification_service import run_verifications_for_element


# Mock section and material classes for testing
@dataclass
class MockRectangularSection:
    """Mock rectangular section for testing."""

    section_type: str = "RECTANGULAR"
    width: float = 300.0  # mm
    height: float = 500.0  # mm


@dataclass
class MockConcreteMaterial:
    """Mock concrete material for testing."""

    f_ck: float = 25.0  # MPa
    f_yk: float = 450.0  # MPa


def test_validation_engine_basic():
    """Test validation engine with valid input."""
    calc_input = CalcInput(
        element_name="Trave 1",
        section=MockRectangularSection(),
        material=MockConcreteMaterial(),
        norm_code="NTC2018",
        limit_states_enabled=["SLU"],
        Mx=100.0,  # kNm
        As=12.0,  # cm²
        d=45.0,  # cm
    )

    validation_result = validate_calc_input(calc_input, "NTC2018")
    assert not validation_result.has_errors, "Valid input should not have errors"


def test_validation_engine_missing_section():
    """Test validation engine catches missing section."""
    calc_input = CalcInput(
        element_name="Trave 1",
        section=None,  # Missing!
        material=MockConcreteMaterial(),
        norm_code="NTC2018",
        limit_states_enabled=["SLU"],
    )

    validation_result = validate_calc_input(calc_input, "NTC2018")
    assert validation_result.has_errors, "Missing section should cause error"


def test_validation_engine_invalid_d():
    """Test validation engine catches invalid d."""
    calc_input = CalcInput(
        element_name="Trave 1",
        section=MockRectangularSection(),
        material=MockConcreteMaterial(),
        norm_code="NTC2018",
        limit_states_enabled=["SLU"],
        d=-5.0,  # Invalid!
    )

    validation_result = validate_calc_input(calc_input, "NTC2018")
    assert validation_result.has_errors, "Negative d should cause error"


def test_validation_engine_lc_fc():
    """Test validation engine validates LC/FC for existing structures."""
    # Valid LC/FC
    calc_input_valid = CalcInput(
        element_name="Pilastro esistente",
        section=MockRectangularSection(),
        material=MockConcreteMaterial(),
        norm_code="NTC2018",
        limit_states_enabled=["SLU"],
        lc="LC2",
        fc=1.20,
    )

    validation_result = validate_calc_input(calc_input_valid, "NTC2018")
    assert not validation_result.has_errors, "Valid LC/FC should not have errors"

    # Invalid LC
    calc_input_invalid_lc = CalcInput(
        element_name="Pilastro esistente",
        section=MockRectangularSection(),
        material=MockConcreteMaterial(),
        norm_code="NTC2018",
        limit_states_enabled=["SLU"],
        lc="LC99",  # Invalid!
        fc=1.20,
    )

    validation_result = validate_calc_input(calc_input_invalid_lc, "NTC2018")
    assert validation_result.has_errors, "Invalid LC should cause error"


def test_verification_service_full_pipeline():
    """Test complete verification pipeline: validation + check execution."""
    calc_input = CalcInput(
        element_name="Trave T1",
        section=MockRectangularSection(width=300.0, height=500.0),
        material=MockConcreteMaterial(f_ck=25.0, f_yk=450.0),
        norm_code="NTC2018",
        limit_states_enabled=["SLU"],
        Mx=80.0,  # kNm
        As=15.0,  # cm²
        d=45.0,  # cm
    )

    templates = get_all_templates()
    calc_output = run_verifications_for_element(
        calc_input=calc_input,
        active_norm="NTC2018",
        templates_registry=templates,
    )

    # Check output structure
    assert calc_output.element_name == "Trave T1"
    assert calc_output.norm_code == "NTC2018"
    assert calc_output.validation_result is not None
    assert not calc_output.validation_result.has_errors

    # Should have executed at least one template (flessione or minimi armatura)
    assert len(calc_output.per_template_results) > 0

    # Check summary metrics
    assert "status" in calc_output.summary_metrics
    assert "num_verifiche_eseguite" in calc_output.summary_metrics


def test_verification_service_with_validation_errors():
    """Test that verification service does not run checks if validation fails."""
    calc_input = CalcInput(
        element_name="Trave errata",
        section=None,  # Missing - will cause validation error
        material=MockConcreteMaterial(),
        norm_code="NTC2018",
        limit_states_enabled=["SLU"],
    )

    templates = get_all_templates()
    calc_output = run_verifications_for_element(
        calc_input=calc_input,
        active_norm="NTC2018",
        templates_registry=templates,
    )

    # Should have validation errors
    assert calc_output.validation_result.has_errors

    # Should NOT have run any checks
    assert len(calc_output.per_template_results) == 0

    # Status should indicate input errors
    assert calc_output.summary_metrics["status"] == "NON_VERIFICATO_PER_ERRORI_INPUT"


def test_verification_result_details():
    """Test that check results include proper details."""
    calc_input = CalcInput(
        element_name="Trave dettagliata",
        section=MockRectangularSection(width=300.0, height=500.0),
        material=MockConcreteMaterial(f_ck=30.0, f_yk=450.0),
        norm_code="NTC2018",
        limit_states_enabled=["SLU"],
        Mx=120.0,  # kNm
        As=20.0,  # cm²
        d=45.0,  # cm
    )

    templates = get_all_templates()
    calc_output = run_verifications_for_element(
        calc_input=calc_input,
        active_norm="NTC2018",
        templates_registry=templates,
    )

    # Find flessione check result
    flessione_result = None
    for template_id, result in calc_output.per_template_results.items():
        if "flessione" in template_id:
            flessione_result = result
            break

    if flessione_result is not None:
        # Should have utilisation
        assert flessione_result.utilisation is not None

        # Should have details (M_Ed, M_Rd, etc.)
        assert "M_Ed_kNm" in flessione_result.details
        assert "M_Rd_kNm" in flessione_result.details

        # Should have Italian messages
        assert len(flessione_result.messages_it) > 0

        # Should have norm references
        assert len(flessione_result.norm_references) > 0
