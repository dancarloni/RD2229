"""
material_repo.py

Repository dei materiali.

Obiettivi:
- Gestire caricamento materiali da file legacy.
- Gestire caricamento materiali da file JSON/YAML moderni.
- Permettere recupero per material_id.
- Fornire strumenti per validazione automatica.
- Essere integrato con src/elements per assegnare materiali
  agli elementi strutturali.
- Essere integrato con src/codes per coefficienti normativi.

NOTE:
Questo file è uno STUB S2:
- Contiene struttura, docstring, TODO
- Nessuna implementazione completa

"""

from typing import Dict, Optional, List
from .material_model import Material
from .validation import validate_material


class MaterialRepository:
    """
    Repository per i materiali.

    Funzionalità previste:
    - add_material(material)
    - get(material_id)
    - load_from_legacy_json(path)
    - validate_all()
    - list_all()

    TODO Copilot:
    - Implementare caricamento da src/legacy/materials.json.
    - Aggiungere logging.
    - Integrare con config/app.yml per selezione materiali attivi.
    """

    def __init__(self) -> None:
        self._materials: Dict[str, Material] = {}

    # ------------------------------------------------------------------

    def add_material(self, material: Material) -> None:
        """
        Aggiunge un materiale.

        TODO:
        - Validare duplicati.
        """
        self._materials[material.material_id] = material

    # ------------------------------------------------------------------

    def get(self, material_id: str) -> Optional[Material]:
        """
        Restituisce il materiale richiesto.

        TODO:
        - Gestire eccezioni.
        - Logging del materiale recuperato.
        """
        return self._materials.get(material_id)

    # ------------------------------------------------------------------

    def list_all(self) -> List[Material]:
        """
        Restituisce tutti i materiali caricati.
        """
        return list(self._materials.values())

    # ------------------------------------------------------------------

    def validate_all(self) -> Dict[str, List[str]]:
        """
        Valida tutti i materiali nel repository.

        Ritorna:
            { material_id: [lista errori] }

        TODO:
        - Logging per ogni materiale.
        """
        results: Dict[str, List[str]] = {}

        for m in self._materials.values():
            errors = validate_material(m)
            results[m.material_id] = errors

        return results

    # ------------------------------------------------------------------

    def load_from_legacy_json(self, path: str) -> None:
        """
        Carica i materiali da un file JSON legacy.

        TODO Copilot:
        - Implementare lettura JSON.
        - Create Material(...) a partire dai dati caricati.
        - Chiamare add_material().
        - Integrare con validate_all().
        """
        pass



# ======================================================================
# FINE FILE material_repo.py
# ======================================================================
