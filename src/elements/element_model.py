"""Modello dati degli elementi strutturali.

Un elemento strutturale è l'unità tecnica minima su cui si svolgono
calcoli, verifiche, assegnazione materiali/sezioni e report.

Tipi supportati: beam, column, wall, slab, steel_beam, timber_beam.

Unità di misura:
- Lunghezze → cm
- Aree → cm²
- Inerzie → cm⁴
- Carichi → kg, kg/m
- Densità → kg/m³
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ..calc.shear_area_registry import compute_shear_area
from ..materials.material_model import Material


@dataclass
class LoadCase:
    """Caso di carico associato a un elemento."""

    name: str = ""
    N: float = 0.0       # Sforzo normale [kg]
    Mx: float = 0.0      # Momento flettente x [kg·m]
    My: float = 0.0      # Momento flettente y [kg·m]
    Tx: float = 0.0      # Taglio x [kg]
    Ty: float = 0.0      # Taglio y [kg]
    Mz: float = 0.0      # Momento torcente [kg·m]

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "N": self.N, "Mx": self.Mx, "My": self.My,
            "Tx": self.Tx, "Ty": self.Ty, "Mz": self.Mz,
        }


@dataclass
class Constraint:
    """Vincolo a un estremo dell'elemento."""

    type: str = "fixed"   # "fixed" | "pinned" | "roller" | "free"
    position: str = "start"  # "start" | "end"

    def to_dict(self) -> dict[str, str]:
        return {"type": self.type, "position": self.position}


@dataclass
class Element:
    """Modello base di un elemento strutturale.

    Attributes:
        element_id: identificatore univoco.
        type: categoria (es. "beam", "column", "wall", "slab").
        length_cm: lunghezza in cm.
        material: oggetto Material assegnato.
        section: dizionario metadata della sezione (da section_registry).
        constraints: vincoli agli estremi.
        load_cases: casi di carico.
        additional_params: parametri variabili (copriferro, armatura, ecc.).
    """

    element_id: str
    type: str
    length_cm: float
    material: Material | None = None
    section: dict[str, Any] | None = None
    constraints: list[Constraint] = field(default_factory=list)
    load_cases: list[LoadCase] = field(default_factory=list)
    additional_params: dict[str, Any] = field(default_factory=dict)

    def get_section_area(self) -> float | None:
        """Restituisce l'area della sezione in cm²."""
        if self.section:
            return self.section.get("area_cm2")
        return None

    def get_inertia(self) -> dict[str, float] | None:
        """Restituisce la mappa delle inerzie: {"Ix": ..., "Iy": ...}."""
        if self.section:
            return self.section.get("inertia_cm4")
        return None

    def get_shear_area(self) -> tuple[float, float]:
        """Restituisce (A_sx, A_sy) tramite shear_area_registry."""
        if not self.section:
            return (0.0, 0.0)

        class _Sec:
            def __init__(self, md: dict):
                self.shape_id = md.get("id")
                self.area_cm2 = md.get("area_cm2")
                self.kappa_x = md.get("kappa_x", None)
                self.kappa_y = md.get("kappa_y", None)

        return compute_shear_area(_Sec(self.section))

    def get_material_param(self, name: str) -> float | None:
        """Recupera un parametro materiale (es. f_ck, f_yk, E)."""
        if self.material:
            return self.material.get_param(name)
        return None

    def get_width_cm(self) -> float:
        """Larghezza della sezione in cm."""
        if self.section and "width_cm" in self.section:
            return float(self.section["width_cm"])
        return self.additional_params.get("b", 0.0)

    def get_height_cm(self) -> float:
        """Altezza della sezione in cm."""
        if self.section and "height_cm" in self.section:
            return float(self.section["height_cm"])
        return self.additional_params.get("h", 0.0)

    def get_effective_depth_cm(self) -> float:
        """Altezza utile d [cm] = h - copriferro."""
        h = self.get_height_cm()
        cover = self.additional_params.get("cover_cm", 4.0)
        return h - cover

    def to_verification_dict(self) -> dict[str, Any]:
        """Converte l'elemento in dict per action_repo.run().

        Include geometria, armatura e carichi dal primo LoadCase.
        """
        d: dict[str, Any] = {
            "element_id": self.element_id,
            "type": self.type,
            "b": self.get_width_cm(),
            "h": self.get_height_cm(),
            "d": self.get_effective_depth_cm(),
        }
        d.update(self.additional_params)

        if self.load_cases:
            lc = self.load_cases[0]
            d.setdefault("N", lc.N)
            d.setdefault("Mx", lc.Mx)
            d.setdefault("My", lc.My)
            d.setdefault("Tx", lc.Tx)
            d.setdefault("Ty", lc.Ty)
            d.setdefault("Mz", lc.Mz)

        return d

    def to_dict(self) -> dict[str, Any]:
        """Serializzazione completa per JSON."""
        result: dict[str, Any] = {
            "element_id": self.element_id,
            "type": self.type,
            "length_cm": self.length_cm,
            "material": self.material.material_id if self.material else None,
            "section_id": self.section.get("id") if self.section else None,
        }
        if self.constraints:
            result["constraints"] = [c.to_dict() for c in self.constraints]
        if self.load_cases:
            result["load_cases"] = [lc.to_dict() for lc in self.load_cases]
        if self.additional_params:
            result["additional_params"] = self.additional_params
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any], material: Material | None = None) -> Element:
        """Crea un Element da dizionario."""
        constraints = [
            Constraint(type=c.get("type", "fixed"), position=c.get("position", "start"))
            for c in data.get("constraints", [])
        ]
        load_cases = [
            LoadCase(**{k: v for k, v in lc.items() if k in LoadCase.__dataclass_fields__})
            for lc in data.get("load_cases", [])
        ]
        return cls(
            element_id=data["element_id"],
            type=data.get("type", "beam"),
            length_cm=data.get("length_cm", 0.0),
            material=material,
            section=data.get("section"),
            constraints=constraints,
            load_cases=load_cases,
            additional_params=data.get("additional_params", {}),
        )
