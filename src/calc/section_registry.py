"""
section_registry.py

Questo modulo gestisce il registry delle sezioni geometriche
(e.g. rettangolo, cerchio, profili vari). Non contiene calcoli,
ma memorizza info di base utili nelle fasi successive.

Utilizzi:
- Copilot Plan potrà popolare automaticamente il registry
  leggendo da un file JSON/CSV (es. sections.json in legacy).
- Il registry faciliterà:
    - selezione sezione nella configurazione elementi
    - reperimento area, inerzia, parametri aggiuntivi
    - collegamento con shear_area_registry

Questo file è uno STUB S2:
- molto commentato
- nessuna implementazione reale

UNITÀ DI MISURA:
- Tutti i valori geometrici memorizzati devono rispettare:
    lunghezze: cm
    aree: cm^2
    inerzie: cm^4
"""

from typing import Any

# ======================================================================
# REGISTRY DELLE SEZIONI
# ======================================================================

SECTION_REGISTRY: dict[str, Any] = {}
"""
Mappa:

    shape_id: str  ->  section_metadata: Dict[str, Any]

La struttura interna section_metadata è a discrezione del progetto:
tipicamente:
{
    "id": "rectangle",
    "description": "...",
    "parameters": {...},
    "area_cm2": float,
    "inertia_cm4": {...},
    "kappa_x": float,
    "kappa_y": float,
    ...
}

TODO Copilot:
- Definire struttura finale leggendo sections.json in legacy.
- Aggiungere validazioni.
"""


# ======================================================================
# FUNZIONI DI REGISTRAZIONE E RECUPERO
# ======================================================================


def register_section(shape_id: str, metadata: dict[str, Any]) -> None:
    """
    Registra una sezione nel registry.

    TODO:
    - Validare shape_id non vuoto
    - Validare metadata conforme al progetto
    - Aggiungere logging
    """
    SECTION_REGISTRY[shape_id] = metadata


def get_section_metadata(shape_id: str) -> dict[str, Any] | None:
    """
    Restituisce il metadata associato alla sezione.

    TODO:
    - Gestire eccezioni o shape non trovata
    """
    return SECTION_REGISTRY.get(shape_id)


# ======================================================================
# FUNZIONE DI BOOTSTRAP (stub)
# ======================================================================


def load_sections_from_legacy() -> None:
    """
    Carica le sezioni dal file legacy (ad es. sections.json
    nella cartella src/legacy/).

    TODO Copilot:
    - Leggere src/legacy/sections.json
    - Popolare SECTION_REGISTRY
    - Collegare shape_id al shear_area_registry
    """
    pass


# ======================================================================
# FINE FILE
# ======================================================================
