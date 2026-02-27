"""Stubs for period estimation models for secondary elements.

These functions do not contain any normative calculations in STEP2; they
serve only to establish the interface contract.  Real implementations will
appear in later phases.
"""

from typing import Any


def estimate_ta(spec: dict[str, Any]) -> float:
    """Estimate the fundamental period Ta for the element.

    Args:
        spec: dictionary containing element properties (mass, geometry, etc.)
    Returns:
        A placeholder numeric value (currently zero).

    NOTE: the contract requires the calling code to log the ``ta_model``
    method chosen; this stub does not perform any computation.
    """
    return 0.0
