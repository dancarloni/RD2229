from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class ActionReport:
    """Esito serializzabile di una azione GUI."""

    name: str
    ok: bool
    summary: str
    details: dict[str, Any]
