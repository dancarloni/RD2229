"""
Data model skeletons for secondary elements (SPEC only).
Do not hardcode normative values here; keep TODO markers where CHAT_PLAN left them.

This file is part of STEP2 implementation.  A more complete
SecondaryElementSpec is defined below with fields required by the
contract (ta_model, drift information, gating flags, etc.).  Backward
compatibility is preserved with an alias for the original class.
"""
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List

@dataclass
class SecondaryElementInput:
    element_type: str
    width: Optional[float] = None
    height: Optional[float] = None
    thickness: Optional[float] = None
    material: Optional[str] = None
    metadata: Dict[str, Any] = None

    # NOTE: validation and units conversion belong to engine layer (not GUI)


# ---------------------------------------------------------------------------
# STEP2 additions: richer specification with contractual fields
# ---------------------------------------------------------------------------

@dataclass
class DriftSpec:
    source: Optional[str] = None  # GLOBAL | ESTIMATED | USER
    method: Optional[str] = None
    soft_storey_factor: Optional[float] = None
    confidence: Optional[str] = None
    assumptions: List[str] = field(default_factory=list)


@dataclass
class SecondaryElementSpec:
    """Complete input schema for a secondary/non‑structural element.

    Fields are intentionally additive compared to the legacy
    ``SecondaryElementInput``.  Consumer code should be able to accept
    either class via ``SecondaryElementInput = SecondaryElementSpec``
    alias if necessary.
    """

    element_type: str
    width: Optional[float] = None
    height: Optional[float] = None
    thickness: Optional[float] = None
    material: Optional[str] = None

    # contractual fields required by STEP2
    ta_model: Optional[str] = None
    drift: DriftSpec = field(default_factory=DriftSpec)
    influence_on_global_model: bool = False

    # soft_storey_factor and confidence are maintained on the ``drift``
    # object as per the plan; they are also available directly for
    # convenience in some callers (not used in this minimal implementation).
    soft_storey_factor: Optional[float] = None
    confidence: Optional[str] = None

    metadata: Dict[str, Any] = field(default_factory=dict)

    def validate(self) -> List[str]:
        """Perform minimal structural validation on the spec.

        Returns a list of error messages (empty if valid).
        """
        errs: List[str] = []
        if self.ta_model is None:
            errs.append("ta_model must be provided")
        dr = self.drift
        if dr.source is None:
            errs.append("drift.source must be provided")
        if dr.method is None:
            errs.append("drift.method must be provided")
        # confidence may be None when source=GLOBAL
        if dr.source == "ESTIMATED" and dr.confidence is None:
            errs.append("drift.confidence required when source is ESTIMATED")
        return errs


# keep alias to avoid breaking any existing import
SecondaryElementInput = SecondaryElementSpec

