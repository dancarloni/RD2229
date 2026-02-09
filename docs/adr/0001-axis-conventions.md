# ADR 0001 — Axis rotation and sign conventions

Status: Proposed

Decision: Use stress-sign based convention for shading compression regions by default. Provide configuration option to switch to moment-sign heuristic or top-center heuristic.

Rationale:
- Stress-sign based convention maps directly to physical stress distributions and minimizes surprises for users migrating legacy spreadsheets.
- Moment-sign heuristics are provided for compat with historical workflows.

Consequences:
- Implementations must expose configuration and document choice in UI and docs.
