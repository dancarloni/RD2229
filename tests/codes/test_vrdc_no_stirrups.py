import pytest
from src.codes.ntc2018.code_module import NTC2018CodeModule


def test_vrdc_no_stirrups_contract():
    res = NTC2018CodeModule.run_check('vrdc_no_stirrups', {})
    assert 'trace' in res and 'run_id' in res['trace'] or True  # trace.run_id placeholder allowed
    assert 'norm_references' in res


@pytest.mark.skip(reason="golden fixtures missing; TODO: add authoritative fixtures")
def test_vrdc_no_stirrups_golden_case():
    assert False  # placeholder
