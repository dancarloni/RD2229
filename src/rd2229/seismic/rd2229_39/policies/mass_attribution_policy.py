"""Policy: attribuzione delle masse verticali ai piani (lumping)."""

from __future__ import annotations

from ..models.inputs import EdgeFloorsPolicySpec, FloorMassBreakdown, MassAttributionPolicySpec


def compute_lumped_floor_mass(
    floor: FloorMassBreakdown,
    mass_policy: MassAttributionPolicySpec,
    edge_policy: EdgeFloorsPolicySpec,
) -> float:
    # MVP: i valori mancanti sono già 0 nel breakdown.
    m_vert_above = floor.m_cols_above + floor.m_walls_above
    m_vert_below = floor.m_cols_below + floor.m_walls_below
    return floor.m_floor + mass_policy.split_above * m_vert_above + mass_policy.split_below * m_vert_below
