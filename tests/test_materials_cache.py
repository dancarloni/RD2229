from src.core_calculus.core.verification_engine import VerificationEngine


def test_get_material_properties_cached():
    engine = VerificationEngine("TA")
    p1 = engine.get_material_properties("R160", "FeB38k", "RD2229")
    p2 = engine.get_material_properties("R160", "FeB38k", "RD2229")
    assert p1.fck == p2.fck
    assert p1.fyk == p2.fyk
    assert p1.Ec == p2.Ec
    assert p1.Es == p2.Es
