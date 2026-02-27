from src.rd2229.seismic.rd2229_39.models.inputs import FloorForcesRequest, FloorMassBreakdown
from src.rd2229.seismic.rd2229_39.provider import RD2229SeismicProvider


def test_sussultory_is_125_percent_of_ondulatory():
    req = FloorForcesRequest(
        floors=[
            FloorMassBreakdown(level_id="L1", elevation_m=0.0, m_floor=100.0),
            FloorMassBreakdown(level_id="L2", elevation_m=3.0, m_floor=100.0),
        ],
        p=0.10,
        g=9.81,
    )
    res = RD2229SeismicProvider().compute_floor_forces(req)
    ond = res.components["ONDULATORY"].forces_by_level
    sus = res.components["SUSSULTORY"].forces_by_level
    for k in ond:
        assert abs(sus[k] - 1.25 * ond[k]) < 1e-9
