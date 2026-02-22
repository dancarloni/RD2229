from src.rd2229.seismic.rd2229_39.provider import RD2229SeismicProvider
from src.rd2229.seismic.rd2229_39.models.inputs import FloorForcesRequest, FloorMassBreakdown


def test_trace_present_for_components():
    req = FloorForcesRequest(
        floors=[FloorMassBreakdown(level_id="L1", elevation_m=0.0, m_floor=100.0)],
        p=0.10,
    )
    res = RD2229SeismicProvider().compute_floor_forces(req)
    assert "ONDULATORY" in res.components
    assert "SUSSULTORY" in res.components
    assert res.components["ONDULATORY"].trace.norm_code == "RD2229_39"
    assert res.components["SUSSULTORY"].trace.derived_from == "ONDULATORY"
