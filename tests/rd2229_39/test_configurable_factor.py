from src.rd2229.seismic.rd2229_39.models.inputs import FloorForcesRequest, FloorMassBreakdown
from src.rd2229.seismic.rd2229_39.provider import RD2229ProviderConfig, RD2229SeismicProvider


def test_custom_sussultory_factor_affects_forces_and_trace():
    req = FloorForcesRequest(
        floors=[FloorMassBreakdown(level_id="L1", elevation_m=0.0, m_floor=50.0)],
        p=0.2,
        g=9.81,
    )
    # use non-default factor
    provider = RD2229SeismicProvider(config=RD2229ProviderConfig(sussultory_factor=1.5))
    res = provider.compute_floor_forces(req)
    ond = res.components["ONDULATORY"].forces_by_level["L1"]
    sus = res.components["SUSSULTORY"].forces_by_level["L1"]
    assert abs(sus - 1.5 * ond) < 1e-9
    # trace record should include correct factor
    trace = res.components["SUSSULTORY"].trace
    assert trace.factor == 1.5
    assert "derived_from" in trace.__dict__ and trace.derived_from == "ONDULATORY"
