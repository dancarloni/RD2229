"""
validation.py

Modulo dedicato alla validazione dei materiali.

Questo modulo centralizza:
- Controlli su densità (valori positivi).
- Controlli su parametri (fck, fyk, E).
- Controlli logici (es. una muratura non deve avere fyk).
- Controlli normativi (da introdurre in blocchi successivi
  tramite il package `codes`).

NOTA:
Questo è uno STUB S2: struttura completa, TODO attivi, niente logica.

"""

from .material_model import Material


class MaterialValidationError(Exception):
    """Errore di validazione dei materiali."""

    pass


def validate_material(material: Material) -> list[str]:
    """
    Valida un materiale e restituisce la lista di errori riscontrati.

    Comportamenti previsti:
    - Nessuna eccezione (eccetto errori interni)
    - Ritorno di una lista di messaggi testuali

    TODO Copilot:
    - Implementare controlli sulle unità di misura.
    - Verificare che E, fck, fyk siano coerenti con family.
    - Integrare controlli con normative tramite codes/code_registry.

    """
    errors: list[str] = []

    # Esempi di controlli minimi da completare
    if material.density_kg_m3 <= 0:
        errors.append("La densità deve essere positiva (kg/m^3).")

    if not material.material_id:
        errors.append("material_id mancante.")

    # TODO Copilot:
    # - Validare parametri in material.params.

    return errors


# ======================================================================
# FINE FILE
# ======================================================================
