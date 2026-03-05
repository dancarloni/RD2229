"""
element_repo.py

Questo modulo definisce il REPOSITORY degli elementi strutturali.

Responsabilità del repository:
- Creazione e registrazione elementi.
- Caricamento da file JSON/XML/YAML moderni.
- Caricamento da file legacy (se esiste un corrispettivo).
- Collegamento con repository materiali.
- Collegamento con registry sezioni.
- Collegamento con funzioni di risoluzione input (resolve_inputs).

STUB S2:
- Struttura completa
- Docstring lunghe
- TODO per Copilot
"""

from ..calc.section_registry import get_section_metadata
from ..materials.material_repo import MaterialRepository
from .element_model import Element


class ElementRepository:
    """
    Repository per la gestione degli elementi strutturali.

    Funzioni previste:
    - add_element()
    - get()
    - list_all()
    - load_from_json()
    - assign_material()
    - assign_section()

    TODO Copilot:
    - Collegare a resolve_inputs.
    """

    def __init__(self) -> None:
        self._elements: dict[str, Element] = {}

    # --------------------------------------------------------------

    def add_element(self, element: Element) -> None:
        """
        Aggiunge un elemento.

        TODO:
        - Validare duplicati id.
        """
        self._elements[element.element_id] = element

    # --------------------------------------------------------------

    def get(self, element_id: str) -> Element | None:
        """
        Recupera un elemento.
        """
        return self._elements.get(element_id)

    # --------------------------------------------------------------

    def list_all(self) -> list[Element]:
        """
        Restituisce tutti gli elementi.
        """
        return list(self._elements.values())

    # --------------------------------------------------------------

    def assign_material(
        self, element_id: str, material_id: str, material_repo: MaterialRepository
    ) -> None:
        """
        Assegna un materiale a un elemento, recuperandolo dal repository.

        TODO:
        - Validare esistenza materiale
        - Logging
        """
        el = self.get(element_id)
        mat = material_repo.get(material_id)
        if el and mat:
            el.material = mat

    # --------------------------------------------------------------

    def assign_section(self, element_id: str, section_id: str) -> None:
        """
        Assegna la sezione tramite registry globale.

        TODO:
        - Validare esistenza sezione
        """
        el = self.get(element_id)
        metadata = get_section_metadata(section_id)
        if el and metadata:
            el.section = metadata

    # --------------------------------------------------------------

    def load_from_json(self, path: str, material_repo: MaterialRepository) -> None:
        """
        Carica elementi da file JSON.

        TODO Copilot:
        - Implementare lettura JSON.
        - Creare Element(...).
        - Assegnare materiali e sezioni.
        - Aggiungere logging.
        """
        pass


# ======================================================================
# FINE FILE
# ======================================================================
