"""Metodo RD2229/39: componente sussultoria derivata dall'ondulatorio."""

from __future__ import annotations

from ..docs_ref.norm_refs import SUSSULTORY_REF
from ..models.outputs import FloorForceComponent, TraceRecord

METHOD_ID = "RD2229_39_SUSSULTORY_DERIVED_125"
COMPONENT = "SUSSULTORY"


def compute_sussultory_from_ondulatory(
    ondulatory: FloorForceComponent, factor: float = 1.25
) -> FloorForceComponent:
    forces: dict[str, float] = {k: factor * v for k, v in ondulatory.forces_by_level.items()}
    base_shear = sum(forces.values())

    assumptions: list[str] = [
        "Componente sussultoria derivata dall'ondulatorio (non calcolo indipendente)",
        f"factor={factor}",
    ]

    trace = TraceRecord(
        norm_code="RD2229_39",
        method_id=METHOD_ID,
        component=COMPONENT,
        norm_ref=[SUSSULTORY_REF],
        assumptions=assumptions,
        warnings=[],
        derived_from="ONDULATORY",
        factor=factor,
    )

    return FloorForceComponent(
        component=COMPONENT, forces_by_level=forces, base_shear=base_shear, trace=trace
    )
