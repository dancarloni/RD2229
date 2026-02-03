from __future__ import annotations

from dataclasses import dataclass, field
from math import pi, sqrt
from typing import Dict, Optional, Tuple
from uuid import uuid4

import logging

logger = logging.getLogger(__name__)

CSV_HEADERS = [
    "id",
    "name",
    "section_type",
    "width",
    "height",
    "diameter",
    "flange_width",
    "flange_thickness",
    "web_thickness",
    "web_height",
    "area",
    "x_G",
    "y_G",
    "Ix",
    "Iy",
    "Ixy",
    "Qx",
    "Qy",
    "rx",
    "ry",
    "core_x",
    "core_y",
    "ellipse_a",
    "ellipse_b",
    "note",
]


@dataclass
class SectionProperties:
    """Proprietà geometriche calcolate della sezione."""

    area: float
    centroid_x: float
    centroid_y: float
    ix: float
    iy: float
    ixy: float
    qx: float
    qy: float
    rx: float
    ry: float
    core_x: float
    core_y: float
    ellipse_a: float
    ellipse_b: float


@dataclass
class Section:
    """Classe base per una sezione piana."""

    name: str
    section_type: str
    note: str = ""
    id: str = field(default_factory=lambda: str(uuid4()))
    properties: Optional[SectionProperties] = None

    def compute_properties(self) -> SectionProperties:
        """Calcola e ritorna le proprietà geometriche."""
        self.properties = self._compute()
        logger.debug("Proprietà calcolate per %s: %s", self.section_type, self.properties)
        return self.properties

    def _compute(self) -> SectionProperties:
        raise NotImplementedError

    def to_dict(self) -> Dict[str, str]:
        """Serializza la sezione in un dizionario per il CSV."""
        data = {header: "" for header in CSV_HEADERS}
        data.update(
            {
                "id": self.id,
                "name": self.name,
                "section_type": self.section_type,
                "note": self.note,
            }
        )
        self._fill_dimension_fields(data)
        if self.properties:
            data.update(
                {
                    "area": f"{self.properties.area:.6g}",
                    "x_G": f"{self.properties.centroid_x:.6g}",
                    "y_G": f"{self.properties.centroid_y:.6g}",
                    "Ix": f"{self.properties.ix:.6g}",
                    "Iy": f"{self.properties.iy:.6g}",
                    "Ixy": f"{self.properties.ixy:.6g}",
                    "Qx": f"{self.properties.qx:.6g}",
                    "Qy": f"{self.properties.qy:.6g}",
                    "rx": f"{self.properties.rx:.6g}",
                    "ry": f"{self.properties.ry:.6g}",
                    "core_x": f"{self.properties.core_x:.6g}",
                    "core_y": f"{self.properties.core_y:.6g}",
                    "ellipse_a": f"{self.properties.ellipse_a:.6g}",
                    "ellipse_b": f"{self.properties.ellipse_b:.6g}",
                }
            )
        return data

    def _fill_dimension_fields(self, data: Dict[str, str]) -> None:
        raise NotImplementedError

    def logical_key(self) -> Tuple:
        """Chiave logica per prevenire duplicati in archivio."""
        return (self.section_type, self._dimension_key())

    def _dimension_key(self) -> Tuple:
        raise NotImplementedError


@dataclass
class RectangularSection(Section):
    """Sezione rettangolare."""

    width: float = 0.0
    height: float = 0.0

    def __init__(self, name: str, width: float, height: float, note: str = ""):
        super().__init__(name=name, section_type="RECTANGULAR", note=note)
        self.width = width
        self.height = height

    def _compute(self) -> SectionProperties:
        if self.width <= 0 or self.height <= 0:
            raise ValueError("Dimensioni non valide per la sezione rettangolare")
        area = self.width * self.height
        centroid_x = self.width / 2
        centroid_y = self.height / 2
        ix = (self.width * self.height**3) / 12
        iy = (self.height * self.width**3) / 12
        ixy = 0.0
        qx = area * centroid_y
        qy = area * centroid_x
        rx = sqrt(ix / area)
        ry = sqrt(iy / area)
        core_x = iy / (area * (self.width / 2))
        core_y = ix / (area * (self.height / 2))
        ellipse_a = rx
        ellipse_b = ry
        return SectionProperties(
            area=area,
            centroid_x=centroid_x,
            centroid_y=centroid_y,
            ix=ix,
            iy=iy,
            ixy=ixy,
            qx=qx,
            qy=qy,
            rx=rx,
            ry=ry,
            core_x=core_x,
            core_y=core_y,
            ellipse_a=ellipse_a,
            ellipse_b=ellipse_b,
        )

    def _fill_dimension_fields(self, data: Dict[str, str]) -> None:
        data.update({"width": f"{self.width:.6g}", "height": f"{self.height:.6g}"})

    def _dimension_key(self) -> Tuple:
        return (round(self.width, 6), round(self.height, 6))


@dataclass
class CircularSection(Section):
    """Sezione circolare piena."""

    diameter: float = 0.0

    def __init__(self, name: str, diameter: float, note: str = ""):
        super().__init__(name=name, section_type="CIRCULAR", note=note)
        self.diameter = diameter

    def _compute(self) -> SectionProperties:
        if self.diameter <= 0:
            raise ValueError("Diametro non valido per la sezione circolare")
        radius = self.diameter / 2
        area = pi * radius**2
        centroid_x = radius
        centroid_y = radius
        ix = (pi * radius**4) / 4
        iy = ix
        ixy = 0.0
        qx = area * centroid_y
        qy = area * centroid_x
        rx = sqrt(ix / area)
        ry = rx
        core_x = radius / 4
        core_y = radius / 4
        ellipse_a = rx
        ellipse_b = ry
        return SectionProperties(
            area=area,
            centroid_x=centroid_x,
            centroid_y=centroid_y,
            ix=ix,
            iy=iy,
            ixy=ixy,
            qx=qx,
            qy=qy,
            rx=rx,
            ry=ry,
            core_x=core_x,
            core_y=core_y,
            ellipse_a=ellipse_a,
            ellipse_b=ellipse_b,
        )

    def _fill_dimension_fields(self, data: Dict[str, str]) -> None:
        data.update({"diameter": f"{self.diameter:.6g}"})

    def _dimension_key(self) -> Tuple:
        return (round(self.diameter, 6),)


@dataclass
class TSection(Section):
    """Sezione a T con anima centrale."""

    flange_width: float = 0.0
    flange_thickness: float = 0.0
    web_thickness: float = 0.0
    web_height: float = 0.0

    def __init__(
        self,
        name: str,
        flange_width: float,
        flange_thickness: float,
        web_thickness: float,
        web_height: float,
        note: str = "",
    ):
        super().__init__(name=name, section_type="T_SECTION", note=note)
        self.flange_width = flange_width
        self.flange_thickness = flange_thickness
        self.web_thickness = web_thickness
        self.web_height = web_height

    @property
    def total_height(self) -> float:
        return self.flange_thickness + self.web_height

    def _compute(self) -> SectionProperties:
        if min(self.flange_width, self.flange_thickness, self.web_thickness, self.web_height) <= 0:
            raise ValueError("Dimensioni non valide per la sezione a T")
        area_flange = self.flange_width * self.flange_thickness
        area_web = self.web_thickness * self.web_height
        area = area_flange + area_web

        centroid_x = self.flange_width / 2
        y_flange = self.web_height + self.flange_thickness / 2
        y_web = self.web_height / 2
        centroid_y = (area_flange * y_flange + area_web * y_web) / area

        ix_flange = (self.flange_width * self.flange_thickness**3) / 12
        ix_web = (self.web_thickness * self.web_height**3) / 12
        ix = ix_flange + area_flange * (y_flange - centroid_y) ** 2 + ix_web + area_web * (y_web - centroid_y) ** 2

        iy_flange = (self.flange_thickness * self.flange_width**3) / 12
        iy_web = (self.web_height * self.web_thickness**3) / 12
        iy = iy_flange + iy_web

        ixy = 0.0
        qx = area * centroid_y
        qy = area * centroid_x
        rx = sqrt(ix / area)
        ry = sqrt(iy / area)

        ex = self.flange_width / 2
        ey = max(centroid_y, self.total_height - centroid_y)
        core_x = iy / (area * ex)
        core_y = ix / (area * ey)
        ellipse_a = rx
        ellipse_b = ry

        return SectionProperties(
            area=area,
            centroid_x=centroid_x,
            centroid_y=centroid_y,
            ix=ix,
            iy=iy,
            ixy=ixy,
            qx=qx,
            qy=qy,
            rx=rx,
            ry=ry,
            core_x=core_x,
            core_y=core_y,
            ellipse_a=ellipse_a,
            ellipse_b=ellipse_b,
        )

    def _fill_dimension_fields(self, data: Dict[str, str]) -> None:
        data.update(
            {
                "flange_width": f"{self.flange_width:.6g}",
                "flange_thickness": f"{self.flange_thickness:.6g}",
                "web_thickness": f"{self.web_thickness:.6g}",
                "web_height": f"{self.web_height:.6g}",
            }
        )

    def _dimension_key(self) -> Tuple:
        return (
            round(self.flange_width, 6),
            round(self.flange_thickness, 6),
            round(self.web_thickness, 6),
            round(self.web_height, 6),
        )


SECTION_CLASS_MAP = {
    "RECTANGULAR": RectangularSection,
    "CIRCULAR": CircularSection,
    "T_SECTION": TSection,
}


def create_section_from_dict(data: Dict[str, str]) -> Section:
    """Factory per creare una sezione da un dizionario letto dal CSV."""
    section_type = (data.get("section_type") or "").strip().upper()
    name = (data.get("name") or "").strip() or section_type
    note = (data.get("note") or "").strip()

    if section_type == "RECTANGULAR":
        width = float(data.get("width") or 0)
        height = float(data.get("height") or 0)
        _ensure_positive(width, "width")
        _ensure_positive(height, "height")
        section = RectangularSection(name=name, width=width, height=height, note=note)
    elif section_type == "CIRCULAR":
        diameter = float(data.get("diameter") or 0)
        _ensure_positive(diameter, "diameter")
        section = CircularSection(name=name, diameter=diameter, note=note)
    elif section_type == "T_SECTION":
        flange_width = float(data.get("flange_width") or 0)
        flange_thickness = float(data.get("flange_thickness") or 0)
        web_thickness = float(data.get("web_thickness") or 0)
        web_height = float(data.get("web_height") or 0)
        _ensure_positive(flange_width, "flange_width")
        _ensure_positive(flange_thickness, "flange_thickness")
        _ensure_positive(web_thickness, "web_thickness")
        _ensure_positive(web_height, "web_height")
        section = TSection(
            name=name,
            flange_width=flange_width,
            flange_thickness=flange_thickness,
            web_thickness=web_thickness,
            web_height=web_height,
            note=note,
        )
    else:
        raise ValueError(f"Tipo di sezione non riconosciuto: {section_type}")

    section.id = (data.get("id") or "").strip() or section.id
    return section


def _ensure_positive(value: float, label: str) -> None:
    if value <= 0:
        raise ValueError(f"{label} deve essere positivo")
