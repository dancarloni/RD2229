from src.rd2229.seismic.rd2229_39.provider import RD2229SeismicProvider
from src.rd2229.seismic.rd2229_39.models.inputs import FloorForcesRequest, FloorMassBreakdown
from src.rd2229.seismic.rd2229_39.docs_ref.norm_refs import ONDULATORY_REF, SUSSULTORY_REF


def test_trace_present_for_components():
    req = FloorForcesRequest(
        floors=[FloorMassBreakdown(level_id="L1", elevation_m=0.0, m_floor=100.0)],
        p=0.10,
    )
    res = RD2229SeismicProvider().compute_floor_forces(req)
    assert "ONDULATORY" in res.components
    assert "SUSSULTORY" in res.components
    ond_trace = res.components["ONDULATORY"].trace
    sus_trace = res.components["SUSSULTORY"].trace
    assert ond_trace.norm_code == "RD2229_39"
    assert sus_trace.derived_from == "ONDULATORY"
    # normative references come from centralized constants
    assert ond_trace.norm_ref == [ONDULATORY_REF]
    assert sus_trace.norm_ref == [SUSSULTORY_REF]
