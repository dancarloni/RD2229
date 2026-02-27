"""Drift estimation models for secondary elements (stub).

Currently only "Metodo B" (shear-building proxy + soft_storey_factor) is
required by STEP2.  The real calculation will be added later; here we
simply document the signature and return a dummy value.
"""

from typing import Any


def estimate_drift_metodo_b(spec: dict[str, Any], soft_storey_factor: float) -> float:
    """Estimate drift according to the simplified Metodo B proxy.

    Args:
        spec: element specification dictionary, may include mass and height
        soft_storey_factor: factor (>1) amplifying drift for soft storey
    Returns:
        Placeholder drift value (zero) and the function must preserve
        metadata for decision_log in the calling code.
    """
    # actual implementation deferred to future phase
    return 0.0
