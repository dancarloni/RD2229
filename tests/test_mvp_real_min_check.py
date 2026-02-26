from src.rd2229.mvp.engine import PlaceholderVerificationEngine
from src.rd2229.mvp.jsoncode_loader import load_jsoncode_config
from src.rd2229.mvp.models import CheckRequest, Combination, Element, LoadCase


def test_real_min_check_returns_fail_over_threshold(tmp_path):
    config_path = tmp_path / "real_min.jsoncode"
    config_path.write_text(
        (
            '{\n'
            '  "id": "MVP_PLACEHOLDER",\n'
            '  "version": "1.0.0",\n'
            '  "namespace": "NTC2018",\n'
            '  "payload": {\n'
            '    "check_code": "MVP_REAL_MIN",\n'
            '    "threshold": 100.0,\n'
            '    "norm_references": ["TODO(NTC/EC/RD):REF"]\n'
            '  }\n'
            '}\n'
        ),
        encoding="utf-8",
    )

    config = load_jsoncode_config(str(config_path))
    engine = PlaceholderVerificationEngine()

    request = CheckRequest(
        id="req1",
        project_id="p1",
        element_id="e1",
        combination_id="c1",
        check_code="MVP_REAL_MIN",
    )
    element = Element(
        id="e1",
        project_id="p1",
        section_id="s1",
        material_id="m1",
    )
    load_case = LoadCase(
        id="lc1",
        project_id="p1",
        name="LC1",
        category="PERMANENT",
        actions={"N": 120.0},
    )
    combination = Combination(
        id="c1",
        project_id="p1",
        name="C1",
        factors={"lc1": 1.0},
    )

    result = engine.run(
        request=request,
        element=element,
        load_case=load_case,
        combination=combination,
        config=config,
    )

    assert result.status == "FAIL"
    assert result.value > 1.0
    assert result.trace.method_id == "MVP_REAL_MIN"
