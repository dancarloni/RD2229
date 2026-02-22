"""Metodo RD2229/39: forze ondulatorie da percentuale masse di piano."""

from __future__ import annotations

from typing import Dict, List

from ..models.inputs import FloorForcesRequest
from ..models.outputs import FloorForceComponent, TraceRecord
from ..policies.mass_attribution_policy import compute_lumped_floor_mass
from ..validators.rd2229_validators import validate_floor_forces_request
from ..docs_ref.norm_refs import ONDULATORY_REF


METHOD_ID = "RD2229_39_FLOOR_FORCES_MASS_PERCENT"
COMPONENT = "ONDULATORY"


def compute_ondulatory_floor_forces(request: FloorForcesRequest) -> FloorForceComponent:
    warnings = validate_floor_forces_request(request)

    forces: Dict[str, float] = {}
    assumptions: List[str] = [
        "M_i = M_floor + split_above*(cols_above+walls_above) + split_below*(cols_below+walls_below)",
        f"split_above={request.mass_policy.split_above}, split_below={request.mass_policy.split_below}",
        (
            f"edge_policy: missing_above_as_zero={request.edge_policy.treat_missing_above_as_zero}, "
            f"missing_below_as_zero={request.edge_policy.treat_missing_below_as_zero}"
        ),
    ]

    base_shear = 0.0
    for fl in request.floors:
        Mi = compute_lumped_floor_mass(fl, request.mass_policy, request.edge_policy)
        Fi = request.p * Mi * request.g
        forces[fl.level_id] = Fi
        base_shear += Fi

    trace = TraceRecord(
        norm_code="RD2229_39",
        method_id=METHOD_ID,
        component=COMPONENT,
        norm_ref=[ONDULATORY_REF],
        assumptions=assumptions,
        warnings=warnings,
    )

    return FloorForceComponent(component=COMPONENT, forces_by_level=forces, base_shear=base_shear, trace=trace)
