"""
Tests for structural verification adapters (NTC2018 + RD2229).

Unit tests for each adapter and integration test for VerifierManager.
"""
from __future__ import annotations

import json
from dataclasses import dataclass

import pytest

from src.core_calculus.contracts import CalcInput, CalcOutput, ElementRole
from src.core_calculus.core.adapters.base import NormAdapter
from src.core_calculus.core.adapters.ntc2018_adapter import Ntc2018Adapter
from src.core_calculus.core.adapters.rd2229_adapter import Rd2229Adapter
from src.core_calculus.core.classification import classify_element, ClassificationResult
from src.core_calculus.core.verifier_manager import VerifierManager, calc_output_to_dict


# ── Mock objects ──────────────────────────────────────────────────────


@dataclass
class MockSection:
    """Mock rectangular section (mm)."""
    b: float = 300.0
    h: float = 500.0

    @property
    def width(self) -> float:
        return self.b

    @property
    def height(self) -> float:
        return self.h


@dataclass
class MockMaterial:
    """Mock modern material (MPa)."""
    fck: float = 25.0
    fyk: float = 450.0


@dataclass
class MockRD2229Material:
    """Mock RD2229 material (kg/cm²)."""
    sigma_c28: float = 160.0
    sigma_sn: float = 3800.0
    n: float = 15.0


# ── Classification tests ─────────────────────────────────────────────


class TestClassification:
    def test_beam_is_primary(self):
        result = classify_element("beam")
        assert result.role == ElementRole.PRIMARY
        assert len(result.rationale) > 0

    def test_column_is_primary(self):
        result = classify_element("column")
        assert result.role == ElementRole.PRIMARY

    def test_wall_is_secondary(self):
        result = classify_element("wall")
        assert result.role == ElementRole.SECONDARY

    def test_partition_is_secondary(self):
        result = classify_element("partition")
        assert result.role == ElementRole.SECONDARY

    def test_unknown_is_undetermined(self):
        result = classify_element("unknown_type")
        assert result.role == ElementRole.UNDETERMINED

    def test_classification_has_norm_references(self):
        result = classify_element("beam")
        assert len(result.norm_references) > 0
        assert result.norm_references[0].norm_code == "NTC2018"

    def test_case_insensitive(self):
        r1 = classify_element("BEAM")
        r2 = classify_element("beam")
        assert r1.role == r2.role


# ── NTC2018 Adapter tests ────────────────────────────────────────────


class TestNtc2018Adapter:
    def setup_method(self):
        self.adapter = Ntc2018Adapter()

    def test_norm_code(self):
        assert self.adapter.norm_code == "NTC2018"

    def test_applicability_correct_norm(self):
        ci = CalcInput(
            element_name="test",
            norm_code="NTC2018",
            section=MockSection(),
            material=MockMaterial(),
        )
        elig = self.adapter.applicability(ci)
        assert elig.eligible is True

    def test_applicability_wrong_norm(self):
        ci = CalcInput(element_name="test", norm_code="DM96")
        elig = self.adapter.applicability(ci)
        assert elig.eligible is False

    def test_applicability_no_section(self):
        ci = CalcInput(element_name="test", norm_code="NTC2018", material=MockMaterial())
        elig = self.adapter.applicability(ci)
        assert elig.eligible is False

    def test_verify_bending_ok(self):
        ci = CalcInput(
            element_name="Beam 1",
            norm_code="NTC2018",
            section=MockSection(),
            material=MockMaterial(),
            Mx=50.0,
            As=500.0,
            d=460.0,
            element_role=ElementRole.PRIMARY,
        )
        result = self.adapter.verify(ci)
        assert isinstance(result, CalcOutput)
        assert result.ok is True
        assert result.norm_code == "NTC2018"
        assert "ntc2018_slu_pressoflessione" in result.per_template_results

    def test_verify_shear_present(self):
        ci = CalcInput(
            element_name="Beam 1",
            norm_code="NTC2018",
            section=MockSection(),
            material=MockMaterial(),
            Tx=20.0,
            As=500.0,
            d=460.0,
        )
        result = self.adapter.verify(ci)
        assert "ntc2018_slu_taglio" in result.per_template_results

    def test_verify_has_norm_references(self):
        ci = CalcInput(
            element_name="Beam 1",
            norm_code="NTC2018",
            section=MockSection(),
            material=MockMaterial(),
            Mx=50.0,
            As=500.0,
            d=460.0,
        )
        result = self.adapter.verify(ci)
        for scr in result.per_template_results.values():
            assert len(scr.norm_references) > 0
            assert scr.norm_references[0].norm_code == "NTC2018"

    def test_verify_secondary_profile(self):
        ci = CalcInput(
            element_name="Wall 1",
            norm_code="NTC2018",
            section=MockSection(),
            material=MockMaterial(),
            Mx=10.0,
            As=200.0,
            d=460.0,
            element_role=ElementRole.SECONDARY,
        )
        result = self.adapter.verify(ci)
        assert result.profile_used == "PROFILE_SECONDARY_STABILITY"


# ── RD2229 Adapter tests ─────────────────────────────────────────────


class TestRd2229Adapter:
    def setup_method(self):
        self.adapter = Rd2229Adapter()

    def test_norm_code(self):
        assert self.adapter.norm_code == "RD2229"

    def test_applicability_correct_norm(self):
        ci = CalcInput(
            element_name="test",
            norm_code="RD2229",
            section=MockSection(),
            material=MockRD2229Material(),
        )
        elig = self.adapter.applicability(ci)
        assert elig.eligible is True

    def test_applicability_wrong_norm(self):
        ci = CalcInput(element_name="test", norm_code="NTC2018")
        elig = self.adapter.applicability(ci)
        assert elig.eligible is False

    def test_verify_produces_output(self):
        ci = CalcInput(
            element_name="Pilastro P1",
            norm_code="RD2229",
            section=MockSection(),
            material=MockRD2229Material(),
            Mx=30.0,
            As=12.0,  # cm²
            d=460.0,  # mm
            element_role=ElementRole.PRIMARY,
        )
        result = self.adapter.verify(ci)
        assert isinstance(result, CalcOutput)
        assert result.norm_code == "RD2229"
        assert "rd2229_ta_pressoflessione" in result.per_template_results
        assert "rd2229_ta_taglio" in result.per_template_results

    def test_verify_has_utilisation(self):
        ci = CalcInput(
            element_name="Trave T1",
            norm_code="RD2229",
            section=MockSection(),
            material=MockRD2229Material(),
            Mx=30.0,
            As=12.0,
            d=460.0,
        )
        result = self.adapter.verify(ci)
        for scr in result.per_template_results.values():
            assert scr.utilisation is not None
            assert scr.utilisation >= 0


# ── VerifierManager tests ────────────────────────────────────────────


class TestVerifierManager:
    def setup_method(self):
        self.vm = VerifierManager()

    def test_available_norms(self):
        norms = self.vm.available_norms
        assert "NTC2018" in norms
        assert "RD2229" in norms

    def test_get_adapter(self):
        adapter = self.vm.get_adapter("NTC2018")
        assert adapter is not None
        assert adapter.norm_code == "NTC2018"

    def test_verify_selects_correct_adapter(self):
        ci = CalcInput(
            element_name="Test",
            norm_code="NTC2018",
            section=MockSection(),
            material=MockMaterial(),
            Mx=50.0,
            As=500.0,
            d=460.0,
        )
        result = self.vm.verify(ci)
        assert result.norm_code == "NTC2018"

    def test_verify_auto_classifies(self):
        ci = CalcInput(
            element_name="Test",
            norm_code="NTC2018",
            section=MockSection(),
            material=MockMaterial(),
            Mx=10.0,
            As=200.0,
            d=460.0,
            extra={"element_type": "wall"},
        )
        result = self.vm.verify(ci)
        assert result.element_role == ElementRole.SECONDARY

    def test_verify_unknown_norm(self):
        ci = CalcInput(element_name="Test", norm_code="NONEXISTENT")
        result = self.vm.verify(ci)
        assert result.ok is False

    def test_verify_bulk(self):
        inputs = [
            CalcInput(
                element_name=f"Element {i}",
                norm_code="NTC2018",
                section=MockSection(),
                material=MockMaterial(),
                Mx=50.0,
                As=500.0,
                d=460.0,
            )
            for i in range(3)
        ]
        results = self.vm.verify_bulk(inputs)
        assert len(results) == 3
        assert all(isinstance(r, CalcOutput) for r in results)


# ── JSON serialization test ──────────────────────────────────────────


class TestJsonSerialization:
    def test_calc_output_to_dict(self):
        vm = VerifierManager()
        ci = CalcInput(
            element_name="Beam B1",
            norm_code="NTC2018",
            section=MockSection(),
            material=MockMaterial(),
            Mx=50.0,
            As=500.0,
            d=460.0,
            element_role=ElementRole.PRIMARY,
        )
        result = vm.verify(ci)
        d = calc_output_to_dict(result)

        assert d["element_name"] == "Beam B1"
        assert d["element_role"] == "PRIMARY"
        assert d["profile_used"] == "PROFILE_PRIMARY_FULL"
        assert "checks" in d
        assert len(d["checks"]) >= 2

        # Verify JSON serializable
        json_str = json.dumps(d, ensure_ascii=False)
        assert len(json_str) > 0

        # Verify roundtrip
        parsed = json.loads(json_str)
        assert parsed["ok"] == d["ok"]

    def test_serialization_includes_norm_references(self):
        vm = VerifierManager()
        ci = CalcInput(
            element_name="Test",
            norm_code="NTC2018",
            section=MockSection(),
            material=MockMaterial(),
            Mx=30.0,
            As=400.0,
            d=460.0,
        )
        result = vm.verify(ci)
        d = calc_output_to_dict(result)
        for check in d["checks"].values():
            assert len(check["norm_references"]) > 0
            assert check["norm_references"][0]["norm_code"] == "NTC2018"


# ── Integration test: engine → results ───────────────────────────────


class TestEngineIntegration:
    """End-to-end integration test: input → engine → JSON output."""

    def test_full_pipeline_ntc2018(self):
        vm = VerifierManager()
        ci = CalcInput(
            element_name="Trave T1 - Piano 2",
            norm_code="NTC2018",
            section=MockSection(b=300, h=500),
            material=MockMaterial(fck=25.0, fyk=450.0),
            Mx=80.0,
            Tx=40.0,
            As=600.0,
            d=460.0,
            element_role=ElementRole.PRIMARY,
        )
        result = vm.verify(ci)

        # Verify output structure
        assert isinstance(result, CalcOutput)
        assert result.element_name == "Trave T1 - Piano 2"
        assert result.norm_code == "NTC2018"
        assert result.element_role == ElementRole.PRIMARY
        assert result.profile_used == "PROFILE_PRIMARY_FULL"
        assert len(result.per_template_results) >= 2

        # Verify JSON serialization
        d = calc_output_to_dict(result)
        json_str = json.dumps(d, ensure_ascii=False, indent=2)
        parsed = json.loads(json_str)
        assert parsed["element_role"] == "PRIMARY"
        assert parsed["profile_used"] == "PROFILE_PRIMARY_FULL"
        assert len(parsed["checks"]) >= 2

    def test_full_pipeline_rd2229(self):
        vm = VerifierManager()
        ci = CalcInput(
            element_name="Pilastro P3",
            norm_code="RD2229",
            section=MockSection(b=300, h=400),
            material=MockRD2229Material(),
            Mx=20.0,
            N=-100.0,
            As=8.0,
            d=360.0,
            element_role=ElementRole.PRIMARY,
        )
        result = vm.verify(ci)
        assert isinstance(result, CalcOutput)
        assert result.norm_code == "RD2229"
        d = calc_output_to_dict(result)
        json_str = json.dumps(d)
        assert len(json_str) > 0

    def test_secondary_wall_classification_and_verification(self):
        """Test: wall element auto-classified as SECONDARY and verified."""
        vm = VerifierManager()
        ci = CalcInput(
            element_name="Muro M1",
            norm_code="NTC2018",
            section=MockSection(b=200, h=3000),
            material=MockMaterial(fck=20.0, fyk=450.0),
            Mx=5.0,
            As=200.0,
            d=2960.0,
            extra={"element_type": "wall"},
        )
        result = vm.verify(ci)
        assert result.element_role == ElementRole.SECONDARY
        assert result.profile_used == "PROFILE_SECONDARY_STABILITY"
        d = calc_output_to_dict(result)
        assert d["element_role"] == "SECONDARY"
