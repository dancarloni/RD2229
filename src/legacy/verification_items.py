from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

try:
    from verification_table import VerificationInput
except Exception:  # pragma: no cover - evita import circolari a runtime
    if TYPE_CHECKING:
        from verification_table import VerificationInput
    else:
        VerificationInput = object  # type: ignore


@dataclass
class VerificationItem:
    """Rappresenta un elemento soggetto a verifica separato dalla UI.

    - id: identificativo univoco (es. "E001")
    - name: descrizione leggibile
    - input: dati di tipo VerificationInput
    - group: opzionale categoria per raggruppamenti (es. piano, telaio, ecc.)
    """

    id: str
    name: str
    input: VerificationInput
    group: str | None = None
