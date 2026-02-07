from src.core_calculus.verification_engine import VerificationEngine
from src.methods.ta import TangentialAreaMethod


def test_ta_compute_basic():
    method = TangentialAreaMethod()
    engine = VerificationEngine(method)
    res = engine.compute({"width": 0.3, "height": 0.5, "M": 10.0})
    assert "NA_depth" in res
    assert isinstance(res["NA_depth"], float)
