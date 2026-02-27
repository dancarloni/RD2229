from core.verification_core import (
    LoadCase,
    MaterialProperties,
    ReinforcementLayer,
    SectionGeometry,
    estimate_required_torsion_reinforcement,
)
from core.verification_engine import create_verification_engine


def test_estimate_at_required_and_engine_messages():
    sec = SectionGeometry(width=30.0, height=50.0)
    top = ReinforcementLayer(area=1.0, distance=4.0)
    bot = ReinforcementLayer(area=2.0, distance=46.0)
    mat = MaterialProperties(fck=25.0, Ec=31000.0, fyk=450.0)

    # Torsion moment 20 kg·m
    loads = LoadCase(N=0.0, Mx=0.0, My=0.0, Mz=20.0, Tx=0.0, Ty=0.0, At=0.0)

    At_req = estimate_required_torsion_reinforcement(sec, bot, loads, mat)
    assert At_req > 0.0

    # Now use engine to run verification and check messages include torsion note
    engine = create_verification_engine("SLU")
    result = engine.perform_verification(sec, bot, top, mat, loads)
    # One of messages should contain "torsione" (Italian messages created earlier)
    msgs = "\n".join(result.messages)
    assert "torsione" in msgs.lower() or "torsion" in msgs.lower()
