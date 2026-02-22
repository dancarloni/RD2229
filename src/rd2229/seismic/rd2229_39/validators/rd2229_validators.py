"""Validazioni minime per metodi sismici RD2229/39 (MVP)."""

from __future__ import annotations

from typing import List

from ..models.inputs import FloorForcesRequest


def validate_floor_forces_request(request: FloorForcesRequest) -> List[str]:
    warnings: List[str] = []

    if request.p <= 0:
        raise ValueError("p deve essere > 0")
    if request.g <= 0:
        raise ValueError("g deve essere > 0")
    if not request.floors:
        raise ValueError("Deve essere presente almeno un piano")

    for fl in request.floors:
        for name, val in (
            ("m_floor", fl.m_floor),
            ("m_cols_above", fl.m_cols_above),
            ("m_cols_below", fl.m_cols_below),
            ("m_walls_above", fl.m_walls_above),
            ("m_walls_below", fl.m_walls_below),
        ):
            if val < 0:
                raise ValueError(f"{name} negativo per livello {fl.level_id}")

    elevations = [f.elevation_m for f in request.floors]
    if elevations != sorted(elevations):
        warnings.append("Quote piani non ordinate: usare ordine crescente per coerenza")

    return warnings
