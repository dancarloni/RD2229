"""Stub for anchors capacity logic in secondary elements.

STEP2 only requires an interface for ETA‑first manual input.  No calculations
are performed in this phase; the function simply echoes the provided capacity.
"""

from typing import Any


def get_anchor_capacity(spec: dict[str, Any]) -> float:
    """Return the declared anchor capacity from the input spec.

    Args:
        spec: element specification dictionary which may contain a
              key ``anchor_capacity`` supplied manually by the user/ETA.
    Returns:
        The numeric capacity if available, otherwise zero.
    """
    return spec.get("anchor_capacity", 0.0)
