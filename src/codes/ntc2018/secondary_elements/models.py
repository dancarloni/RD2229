"""
Data model skeletons for secondary elements (SPEC only).
Do not hardcode normative values here; keep TODO markers where CHAT_PLAN left them.
"""
from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class SecondaryElementInput:
    element_type: str
    width: Optional[float] = None
    height: Optional[float] = None
    thickness: Optional[float] = None
    material: Optional[str] = None
    metadata: Dict[str, Any] = None

    # NOTE: validation and units conversion belong to engine layer (not GUI)
