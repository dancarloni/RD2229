"""RD2229/39 seismic actions provider (STEP 3B - MVP).

Questo modulo è pensato per essere altamente modulare.
Non hardcodare assunzioni: usare policies e config.

TODO: integrare con registry/capabilities del progetto se/come presente.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .models.inputs import FloorForcesRequest
from .models.outputs import FloorForcesResult
from .methods.ondulatory_mass_percent import compute_ondulatory_floor_forces
from .methods.sussultory_factor import compute_sussultory_from_ondulatory


@dataclass(frozen=True)
class RD2229ProviderConfig:
    """Configurazioni del provider."""

    sussultory_factor: float = 1.25


class RD2229SeismicProvider:
    """Entry point per calcoli sismici RD2229/39 (MVP)."""

    norm_code: str = "RD2229_39"

    def __init__(self, config: Optional[RD2229ProviderConfig] = None):
        self.config = config or RD2229ProviderConfig()

    def compute_floor_forces(self, request: FloorForcesRequest) -> FloorForcesResult:
        ond = compute_ondulatory_floor_forces(request)
        sus = compute_sussultory_from_ondulatory(ond, factor=self.config.sussultory_factor)
        return FloorForcesResult.combine([ond, sus])
