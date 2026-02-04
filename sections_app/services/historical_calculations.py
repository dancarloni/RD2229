from __future__ import annotations

import logging
from typing import Any

from sections_app.models.sections import Section

logger = logging.getLogger(__name__)


def verify_flexure_allowable_stress(section: Section, N: float, Mx: float, My: float) -> str:
    """Stub per verifica a tensioni ammissibili (RD 2229 / Santarella).

    Al momento ritorna un testo che indica che questa è una funzione stub. In futuro questa funzione
    dovrà tradurre le routine dal codice .bas e restituire risultati strutturati.
    """
    logger.debug("Running historical flexure check for section %s: N=%s, Mx=%s, My=%s", section.id, N, Mx, My)
    # TODO: implementare le formule storiche, traducendo i .bas e documentando le fonti.
    return (
        f"TODO: historical flexure verification for section {section.name}\n"
        f"Inputs: N={N}, Mx={Mx}, My={My}\n"
        "Result: NOT IMPLEMENTED - see services/historical_calculations.py for TODOs\n"
    )

