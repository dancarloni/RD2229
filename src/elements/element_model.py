"""
element_model.py

Questo modulo definisce il MODELLO dati degli elementi strutturali
gestiti dal software.

Un elemento strutturale è l'unità tecnica minima su cui si svolgono:
- calcoli antisismici
- verifiche statiche
- assegnazione materiali
- assegnazione sezione
- mapping verso normative e coefficienti
- generazione report

ESEMPI DI ELEMENTI:
- Trave in c.a.
- Pilastro in c.a.
- Parete in c.a.
- Trave acciaio
- Trave legno
- Elemento murario

Questo STUB S2 definisce:

1. Interfaccia principale `Element`.
2. Parametri geometrici essenziali.
3. Collegamento a:
    - materiali/material_repo
    - calc/shear_area_registry
    - codes per parametri normativi
4. Metodi placeholder pronti per essere implementati da Copilot Plan.

UNITÀ DI MISURA:
- Lunghezze → cm
- Aree → cm²
- Inerzie → cm⁴
- Carichi → kg
- Densità → kg/m³

"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from ..materials.material_model import Material
from ..calc.shear_area_registry import compute_shear_area


@dataclass
class Element:
    """
    Modello base di un elemento strutturale.

    Attributi:
    - element_id: identificatore univoco dell'elemento.
    - type: categoria (es. "beam", "column", "wall", "steel_beam").
    - length_cm: lunghezza in cm.
    - material: oggetto Material assegnato.
    - section: dizionario metadata della sezione (da section_registry).
    - additional_params: parametri variabili (forze, vincoli, etc.)

    TODO Copilot:
    - Aggiungere sistema vincoli (fixed, hinge, ecc.)
    - Collegamento con verifica sezioni (modulo future).
    """

    element_id: str
    type: str
    length_cm: float
    material: Optional[Material] = None
    section: Optional[Dict[str, Any]] = None
    additional_params: Dict[str, Any] = field(default_factory=dict)

    # ------------------------------------------------------------
    # GEOMETRIA SEZIONE
    # ------------------------------------------------------------
    def get_section_area(self) -> Optional[float]:
        """
        Restituisce l'area della sezione in cm^2.

        TODO Copilot:
        - Validare che section contenga area_cm2.
        """
        if self.section:
            return self.section.get("area_cm2")
        return None

    def get_inertia(self) -> Optional[Dict[str, float]]:
        """
        Restituisce la mappa delle inerzie, es.:

            { "Ix": ..., "Iy": ... }

        TODO:
        - Validare presenza valori.
        """
        if self.section:
            return self.section.get("inertia_cm4")
        return None

    # ------------------------------------------------------------
    # AREA A TAGLIO
    # ------------------------------------------------------------
    def get_shear_area(self):
        """
        Restituisce A_sx e A_sy.

        NOTE:
        - Utilizza compute_shear_area(section_obj-like).
        - Qui la sezione è un dict, non un oggetto → serve bridging.

        TODO Copilot:
        - Implementare un wrapper Section minimal per compatibilità.
        """
        if not self.section:
            return (0.0, 0.0)

        class _Sec:
            """Mini-adapter per compatibilità compute_shear_area."""
            def __init__(self, md):
                self.shape_id = md.get("id")
                self.area_cm2 = md.get("area_cm2")
                self.kappa_x = md.get("kappa_x", None)
                self.kappa_y = md.get("kappa_y", None)

        return compute_shear_area(_Sec(self.section))

    # ------------------------------------------------------------
    # MATERIALI
    # ------------------------------------------------------------
    def get_material_param(self, name: str) -> Optional[float]:
        """
        Recupera il parametro materiale (es. fck, fyk, E).

        TODO:
        - Validare self.material.
        """
        if self.material:
            return self.material.get_param(name)
        return None

    # ------------------------------------------------------------
    # SERIALIZZAZIONE
    # ------------------------------------------------------------
    def to_dict(self) -> Dict[str, Any]:
        """
        Serializzazione base, pronta per JSON.

        TODO:
        - Integrare parametri aggiuntivi.
        """
        return {
            "element_id": self.element_id,
            "type": self.type,
            "length_cm": self.length_cm,
            "material": self.material.material_id if self.material else None,
            "section_id": self.section.get("id") if self.section else None,
            "additional_params": self.additional_params,
        }


# ======================================================================
# FINE FILE
# ======================================================================
