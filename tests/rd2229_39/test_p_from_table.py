from pathlib import Path

from src.rd2229.seismic.rd2229_39.provider import RD2229SeismicProvider
from src.rd2229.seismic.rd2229_39.models.inputs import (
    FloorForcesRequest,
    FloorMassBreakdown,
)


def test_p_resolved_from_table(tmp_path):
    # create temporary JSON table
    table = {"zoneA": 0.08, "zoneB": 0.12}
    data_file = tmp_path / "p.json"
    import json

    data_file.write_text(json.dumps(table), encoding="utf-8")

    req = FloorForcesRequest(
        floors=[FloorMassBreakdown(level_id="L1", elevation_m=0.0, m_floor=100.0)],
        p=0.0,
        p_mode="TABLE",
        p_table_path=str(data_file),
        p_table_key="zoneB",
    )
    res = RD2229SeismicProvider().compute_floor_forces(req)
    ond = res.components["ONDULATORY"].forces_by_level["L1"]
    expected = 0.12 * 100.0 * 9.81
    assert abs(ond - expected) < 1e-6
    sus = res.components["SUSSULTORY"].forces_by_level["L1"]
    assert abs(sus - 1.25 * ond) < 1e-9
