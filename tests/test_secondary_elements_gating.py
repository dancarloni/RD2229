from __future__ import annotations

from typing import Any

from verifications.secondary_elements import dispatcher


class DummyProjectModel:
    def __init__(self, norma: str) -> None:
        self.norma_attiva = norma


def make_base_input() -> dict[str, Any]:
    # minimal valid spec according to STEP2
    return {
        "element_type": "partition",
        "ta_model": "MANUAL",
        "drift": {
            "source": "GLOBAL",
            "method": "ANY",
            "soft_storey_factor": 1.0,
            "confidence": "HIGH",
        },
        "influence_on_global_model": False,
    }


def test_dispatcher_contract_fields():
    inp = make_base_input()
    proj = DummyProjectModel("NTC2018")
    res = dispatcher.run(inp, proj, "SLU")
    assert "trace" in res and "run_id" in res["trace"], "trace.run_id missing"
    assert res.get("norm_references") == ["NTC2018"]
    assert res.get("decision_log"), "decision_log should not be empty"


def test_estimated_drift_warning():
    inp = make_base_input()
    inp["drift"]["source"] = "ESTIMATED"
    proj = DummyProjectModel("NTC2018")
    res = dispatcher.run(inp, proj, "SLE")
    assert any("confidence=LOW" in msg for msg in res.get("decision_log", []))
    assert res.get("confidence") == "LOW"


def test_influence_on_global_model_gating():
    inp = make_base_input()
    inp["influence_on_global_model"] = True
    proj = DummyProjectModel("NTC2018")
    res = dispatcher.run(inp, proj, "SLU")
    assert res.get("esito") == "NOT_APPLICABLE"


def test_spec_validation_errors_for_missing_fields():
    from src.codes.ntc2018.secondary_elements.models import SecondaryElementSpec

    spec = SecondaryElementSpec(element_type="foo")
    errors = spec.validate()
    assert errors, "validation should report missing required fields"
    assert any("ta_model" in e for e in errors)


def test_config_loader_reads_secondary_elements():
    from config.calculation_codes_loader import load_code

    cfg = load_code("SECONDARY_ELEMENTS")
    assert isinstance(cfg, dict)
    assert "checks" in cfg
    assert "NS_SLU_InertialForce" in cfg["checks"]
    # component should appear in the list of available codes as well
    from config.calculation_codes_loader import list_available_codes

    assert "SECONDARY_ELEMENTS" in list_available_codes()
