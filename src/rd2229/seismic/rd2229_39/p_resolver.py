"""Utility for resolving seismic coefficient p from request and optionally a table."""

from __future__ import annotations

from pathlib import Path

from .models.inputs import FloorForcesRequest

DEFAULT_TABLE_PATH = Path("data/rd2229/seismic/p_coeff_table.json")


def resolve_p(request: FloorForcesRequest) -> float:
    """Return the `p` value based on the request.

    The original MVP assumed a manual `p` provided by the caller.  To support
    tabulated coefficients we add a ``p_mode`` switch:

    * ``MANUAL`` – simply return ``request.p``; ``p_table_*`` fields are
      ignored.
    * ``TABLE`` – load a JSON mapping from ``p_table_path`` (or the default)
      and look up ``p_table_key``.  A missing key or file raises ValueError.

    The mapping is expected to be ``dict[str, float]``; values are converted to
    ``float`` in case the JSON parser returns ints.
    """

    if request.p_mode != "TABLE" or not request.p_table_path:
        # backward-compatible behaviour
        return request.p

    # p_mode == "TABLE" and a path has been provided
    path = Path(request.p_table_path) if request.p_table_path else DEFAULT_TABLE_PATH
    if not path.is_file():
        raise ValueError(f"p table file not found: {path}")

    import json

    with path.open(encoding="utf-8") as fp:
        mapping = json.load(fp)

    if not isinstance(mapping, dict):
        raise ValueError(f"p table JSON must be an object, got {type(mapping)}")

    # ensure float conversion
    coeffs: dict[str, float] = {}
    for k, v in mapping.items():
        try:
            coeffs[k] = float(v)
        except Exception as exc:  # pragma: no cover - defensive
            raise ValueError(f"invalid p value for key {k}: {v}") from exc

    key = request.p_table_key
    if key is None:
        raise ValueError("p_table_key must be provided when p_mode == 'TABLE'")
    if key not in coeffs:
        raise ValueError(f"key '{key}' not found in p table")

    return coeffs[key]
