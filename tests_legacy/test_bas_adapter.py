from core.verification_bas_adapter import bas_torsion_verification

from core.verification_core import LoadCase, MaterialProperties, ReinforcementLayer, SectionGeometry


def test_bas_torsion_basic():
    sec = SectionGeometry(width=30.0, height=50.0)
    top = ReinforcementLayer(area=1.0, distance=4.0)
    bot = ReinforcementLayer(area=2.0, distance=46.0)
    mat = MaterialProperties(fck=25.0, Ec=31000.0, fyk=450.0)
    loads = LoadCase(N=0.0, Mx=20.0, My=0.0, Mz=0.0, Tx=0.0, Ty=0.0, At=0.0)
    res = bas_torsion_verification(sec, bot, top, mat, loads, method="TA")
    assert "Taux_max" in res
    assert isinstance(res["ok"], bool)
