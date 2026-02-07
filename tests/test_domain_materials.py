import pytest

from verification_table import VerificationInput, get_concrete_properties, get_steel_properties


class FakeMaterial:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


class FakeRepo:
    def __init__(self, mat=None):
        self.mat = mat

    def find_by_name(self, name):
        return self.mat


def test_get_concrete_properties_from_repo():
    repo = FakeRepo(mat=FakeMaterial(fck_MPa=30.0))
    inp = VerificationInput(material_concrete="C1")
    fck_mpa, fck_kgcm2, sigma_ca = get_concrete_properties(inp, repo)
    assert pytest.approx(fck_mpa) == 30.0
    assert fck_kgcm2 == pytest.approx(30.0 * 10.197)
    assert sigma_ca == pytest.approx(0.5 * fck_kgcm2)


def test_get_concrete_properties_fallback():
    repo = FakeRepo(mat=None)
    inp = VerificationInput(material_concrete="UNKNOWN")
    fck_mpa, _, _ = get_concrete_properties(inp, repo)
    assert fck_mpa == pytest.approx(25.0)


def test_get_steel_properties_from_repo():
    repo = FakeRepo(mat=FakeMaterial(fyk_MPa=500.0))
    inp = VerificationInput(material_steel="S1")
    fyk_mpa, fyk_kgcm2, sigma_fa = get_steel_properties(inp, repo)
    assert pytest.approx(fyk_mpa) == 500.0
    assert fyk_kgcm2 == pytest.approx(500.0 * 10.197)
    assert sigma_fa == pytest.approx((500.0 * 10.197) / 1.5)


def test_get_steel_properties_fallback():
    repo = FakeRepo(mat=None)
    inp = VerificationInput(material_steel="UNKNOWN")
    fyk_mpa, _, _ = get_steel_properties(inp, repo)
    assert fyk_mpa == pytest.approx(450.0)
