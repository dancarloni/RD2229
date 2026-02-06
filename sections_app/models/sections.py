from __future__ import annotations

from dataclasses import dataclass, field
from math import pi, sqrt, radians, degrees
from typing import Dict, Optional, Tuple
from uuid import uuid4

import logging

from sections_app.services.calculations import rotate_inertia, compute_principal_inertia

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
    "t_horizontal",
    "t_vertical",
    "outer_diameter",
    "thickness",
    "rotation_angle_deg",
    "area",
    "A_y",
    "A_z",
    "kappa_y",
    "kappa_z",
    "x_G",
    "y_G",
    "Ix",
    "Iy",
    "Ixy",
    "I1",
    "I2",
    "principal_angle_deg",
    "principal_rx",
    "principal_ry",
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

# Default shear correction factors (kappa) for common section types
# Centralized values (literature-based / engineering practice approximations):
# - RECTANGULAR: 5/6
# - CIRCULAR (solid): 10/9
# - HOLLOW circular/rectangular: 1.0 (approx)
# - T/I: web-dominated shear -> kappa_y ~ 1.0 on web direction
DEFAULT_SHEAR_KAPPAS = {
    "RECTANGULAR": (5.0 / 6.0, 5.0 / 6.0),
    "CIRCULAR": (10.0 / 9.0, 10.0 / 9.0),
    "CIRCULAR_HOLLOW": (1.0, 1.0),
    "RECTANGULAR_HOLLOW": (5.0 / 6.0, 5.0 / 6.0),
    "T_SECTION": (1.0, 0.9),
    "I_SECTION": (1.0, 0.9),
    "INVERTED_T_SECTION": (1.0, 0.9),
    "C_SECTION": (1.0, 0.9),
}

# Tutte le possibili chiavi dimensionali supportate (garantire presenza nella dict dimensions)
DIMENSION_KEYS = [
    "width",
    "height",
    "diameter",
    "flange_width",
    "flange_thickness",
    "web_thickness",
    "web_height",
    "t_horizontal",
    "t_vertical",
    "outer_diameter",
    "thickness",
]


@dataclass
class SectionProperties:
    """Proprietà geometriche calcolate della sezione.

    Tutti i campi sono opzionali per permettere la serializzazione anche se
    compute_properties() non è stata ancora chiamata. Se un valore non è
    applicabile, resta None.
    """

    area: Optional[float] = None
    centroid_x: Optional[float] = None
    centroid_y: Optional[float] = None
    ix: Optional[float] = None  # Momento d'inerzia rispetto all'asse x
    iy: Optional[float] = None  # Momento d'inerzia rispetto all'asse y
    ixy: Optional[float] = None  # Prodotto d'inerzia
    qx: Optional[float] = None
    qy: Optional[float] = None
    rx: Optional[float] = None
    ry: Optional[float] = None
    core_x: Optional[float] = None
    core_y: Optional[float] = None
    ellipse_a: Optional[float] = None
    ellipse_b: Optional[float] = None

    # Principal inertia results
    principal_ix: Optional[float] = None
    principal_iy: Optional[float] = None
    principal_angle_deg: Optional[float] = None
    principal_rx: Optional[float] = None
    principal_ry: Optional[float] = None

    # Timoshenko effective shear areas (A_y, A_z) in cm²
    # These are computed as A_y = kappa_y * A_ref_y and A_z = kappa_z * A_ref_z
    shear_area_y: Optional[float] = None
    shear_area_z: Optional[float] = None


@dataclass
class Section:
    """Classe base per una sezione piana."""

    name: str
    section_type: str
    note: str = ""
    rotation_angle_deg: float = 0.0  # Angolo di rotazione della sezione nel suo piano (gradi)
    id: str = field(default_factory=lambda: str(uuid4()))

    # Shear form factors (kappa) for Timoshenko shear areas.
    # These are user-editable and persisted in the archive as 'kappa_y' and 'kappa_z'.
    # Defaults are assigned based on section type when computing properties if not set.
    shear_factor_y: Optional[float] = None
    shear_factor_z: Optional[float] = None

    properties: Optional[SectionProperties] = None

    def compute_properties(self) -> SectionProperties:
        """Calcola e ritorna le proprietà geometriche.

        Se rotation_angle_deg != 0, i momenti di inerzia saranno ruotati
        rispetto agli assi principali della sezione.

        In questa implementazione, dopo il calcolo popoliamo anche `self.dimensions`
        con tutte le chiavi possibili (preservando None quando non applicabile)
        per soddisfare il requisito che `self.dimensions` esista sempre.

        Inoltre si calcolano le aree efficaci a taglio A_y e A_z usando i fattori
        di forma a taglio kappa_y e kappa_z (Timoshenko shear correction).
        """
        # Calcola le proprietà geometriche specifiche di ogni sottoclasse
        self.properties = self._compute()

        # Calcola principali inerzie (I1, I2, angolo) se possibile
        props = self.properties
        if props is not None:
            try:
                if props.ix is not None and props.iy is not None and props.ixy is not None:
                    I1, I2, angle_rad = compute_principal_inertia(props.ix, props.iy, props.ixy)
                    props.principal_ix = I1
                    props.principal_iy = I2
                    props.principal_angle_deg = degrees(angle_rad)

                    area = props.area or 0.0
                    if area and area > 0:
                        props.principal_rx = sqrt(I1 / area)
                        props.principal_ry = sqrt(I2 / area)
                    else:
                        props.principal_rx = None
                        props.principal_ry = None
            except Exception:
                # Non blocchiamo il calcolo principale se qualcosa va storto
                logger.exception("Errore nel calcolo delle inerzie principali")

        # Costruisci il dizionario delle dimensioni (tutte le chiavi presenti)
        self.dimensions = self._collect_dimensions()

        # --- SHEAR: assegna default per kappa se mancanti e calcola A_y / A_z ---
        # Default centralizzati per tipologie comuni
        def default_kappas(section_type: str) -> tuple:
            # Read from centralized mapping DEFAULT_SHEAR_KAPPAS with fallback 5/6
            return DEFAULT_SHEAR_KAPPAS.get(section_type, (5.0 / 6.0, 5.0 / 6.0))

        # Assicurati che props esista
        props = self.properties
        if props is None:
            logger.debug("No properties to compute shear areas for %s", self.section_type)
            return self.properties

        # Se user non ha fornito i fattori, assegna i default
        if self.shear_factor_y is None or self.shear_factor_y <= 0:
            self.shear_factor_y = default_kappas(self.section_type)[0]
        if self.shear_factor_z is None or self.shear_factor_z <= 0:
            self.shear_factor_z = default_kappas(self.section_type)[1]

        # Determina le aree di riferimento A_ref_y/A_ref_z
        def reference_areas(section: Section, props: SectionProperties) -> tuple:
            # Per T/I e sezioni con anima: A_ref_y è principalmente l'area dell'anima (web)
            # Se i parametri dell'anima sono presenti, usali; altrimenti usa l'area totale
            if section.section_type in ("T_SECTION", "I_SECTION", "INVERTED_T_SECTION", "C_SECTION", "PI_SECTION"):
                web_area = 0.0
                if hasattr(section, "web_thickness") and hasattr(section, "web_height"):
                    web_area = float(getattr(section, "web_thickness") or 0.0) * float(getattr(section, "web_height") or 0.0)
                if web_area > 0:
                    A_ref_y = web_area
                else:
                    A_ref_y = props.area or 0.0
                A_ref_z = props.area or 0.0
                return A_ref_y, A_ref_z
            # Predefinito: uso area totale per entrambe le direzioni
            return (props.area or 0.0, props.area or 0.0)

        A_ref_y, A_ref_z = reference_areas(self, props)

        # Calcola le aree efficaci a taglio
        props.shear_area_y = (self.shear_factor_y or 0.0) * A_ref_y
        props.shear_area_z = (self.shear_factor_z or 0.0) * A_ref_z

        logger.debug(
            "Shear areas for %s: kappa_y=%s, kappa_z=%s, A_ref_y=%s, A_ref_z=%s => A_y=%s, A_z=%s",
            self.section_type,
            self.shear_factor_y,
            self.shear_factor_z,
            A_ref_y,
            A_ref_z,
            props.shear_area_y,
            props.shear_area_z,
        )

        logger.debug("Proprietà calcolate per %s: %s", self.section_type, self.properties)
        return self.properties

    def _collect_dimensions(self) -> Dict[str, Optional[float]]:
        """Raccoglie tutte le dimensioni possibili in un dizionario con chiavi fisse.

        Se l'attributo non esiste, il valore sarà None.
        """
        dims = {k: None for k in DIMENSION_KEYS}
        for k in dims:
            if hasattr(self, k):
                dims[k] = getattr(self, k)
        return dims

    def _compute(self) -> SectionProperties:
        raise NotImplementedError

    def _apply_rotation_to_inertia(self, ix_local: float, iy_local: float, ixy_local: float) -> Tuple[float, float, float]:
        """Applica la rotazione alle inerzie locali (assi principali non ruotati).
        
        Args:
            ix_local: Inerzia rispetto all'asse x locale (cm⁴)
            iy_local: Inerzia rispetto all'asse y locale (cm⁴)
            ixy_local: Prodotto di inerzia locale (cm⁴)
        
        Returns:
            Tuple (Ix_global, Iy_global, Ixy_global) dopo rotazione
        """
        if self.rotation_angle_deg == 0:
            return ix_local, iy_local, ixy_local
        
        theta_rad = radians(self.rotation_angle_deg)
        return rotate_inertia(ix_local, iy_local, ixy_local, theta_rad)

    def to_dict(self) -> Dict[str, Optional[float]]:
        """Serializza la sezione in un dizionario completo (dimensioni + proprietà).

        Restituisce valori numerici (float) o None quando il valore non è applicabile.
        Non converte in stringhe: la serializzazione (CSV) si occupa della conversione.
        """
        # Base del dizionario
        data: Dict[str, Optional[float]] = {}
        data.update(
            {
                "id": self.id,
                "name": self.name,
                "section_type": self.section_type,
                "rotation_angle_deg": self.rotation_angle_deg,
                "note": self.note or "",
            }
        )

        # Dimensioni: garantiamo tutte le chiavi tramite self.dimensions o raccolta dinamica
        dims = getattr(self, "dimensions", None) or self._collect_dimensions()
        data.update(dims)

        # Proprietà calcolate: mantenere None se non valorizzate
        props = self.properties
        data.update(
            {
                "area": getattr(props, "area", None) if props else None,
                "A_y": getattr(props, "shear_area_y", None) if props else None,
                "A_z": getattr(props, "shear_area_z", None) if props else None,
                "kappa_y": getattr(self, "shear_factor_y", None),
                "kappa_z": getattr(self, "shear_factor_z", None),
                "x_G": getattr(props, "centroid_x", None) if props else None,
                "y_G": getattr(props, "centroid_y", None) if props else None,
                "Ix": getattr(props, "ix", None) if props else None,
                "Iy": getattr(props, "iy", None) if props else None,
                "Ixy": getattr(props, "ixy", None) if props else None,
                "I1": getattr(props, "principal_ix", None) if props else None,
                "I2": getattr(props, "principal_iy", None) if props else None,
                "principal_angle_deg": getattr(props, "principal_angle_deg", None) if props else None,
                "principal_rx": getattr(props, "principal_rx", None) if props else None,
                "principal_ry": getattr(props, "principal_ry", None) if props else None,
                "Qx": getattr(props, "qx", None) if props else None,
                "Qy": getattr(props, "qy", None) if props else None,
                "rx": getattr(props, "rx", None) if props else None,
                "ry": getattr(props, "ry", None) if props else None,
                "core_x": getattr(props, "core_x", None) if props else None,
                "core_y": getattr(props, "core_y", None) if props else None,
                "ellipse_a": getattr(props, "ellipse_a", None) if props else None,
                "ellipse_b": getattr(props, "ellipse_b", None) if props else None,
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

    def __init__(self, name: str, width: float, height: float, note: str = "", rotation_angle_deg: float = 0.0):
        super().__init__(name=name, section_type="RECTANGULAR", note=note, rotation_angle_deg=rotation_angle_deg)
        self.width = width
        self.height = height

    def _compute(self) -> SectionProperties:
        if self.width <= 0 or self.height <= 0:
            raise ValueError("Dimensioni non valide per la sezione rettangolare")
        area = self.width * self.height
        centroid_x = self.width / 2
        centroid_y = self.height / 2
        
        # Inerzie locali (assi non ruotati)
        ix_local = (self.width * self.height**3) / 12
        iy_local = (self.height * self.width**3) / 12
        ixy_local = 0.0
        
        # Applica rotazione se necessario
        ix, iy, ixy = self._apply_rotation_to_inertia(ix_local, iy_local, ixy_local)
        
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

    def __init__(self, name: str, diameter: float, note: str = "", rotation_angle_deg: float = 0.0):
        super().__init__(name=name, section_type="CIRCULAR", note=note, rotation_angle_deg=rotation_angle_deg)
        self.diameter = diameter

    def _compute(self) -> SectionProperties:
        if self.diameter <= 0:
            raise ValueError("Diametro non valido per la sezione circolare")
        radius = self.diameter / 2
        area = pi * radius**2
        centroid_x = radius
        centroid_y = radius
        
        # Inerzie locali (circolare è simmetrica, rotazione non cambia ix/iy)
        ix_local = (pi * radius**4) / 4
        iy_local = ix_local
        ixy_local = 0.0
        
        # Applica rotazione (per circolare non cambia, ma manteniamo coerenza)
        ix, iy, ixy = self._apply_rotation_to_inertia(ix_local, iy_local, ixy_local)
        
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
        rotation_angle_deg: float = 0.0,
    ):
        super().__init__(name=name, section_type="T_SECTION", note=note, rotation_angle_deg=rotation_angle_deg)
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

        # Inerzie locali (assi non ruotati)
        ix_flange_local = (self.flange_width * self.flange_thickness**3) / 12
        ix_web_local = (self.web_thickness * self.web_height**3) / 12
        ix_local = ix_flange_local + area_flange * (y_flange - centroid_y) ** 2 + ix_web_local + area_web * (y_web - centroid_y) ** 2

        iy_flange_local = (self.flange_thickness * self.flange_width**3) / 12
        iy_web_local = (self.web_height * self.web_thickness**3) / 12
        iy_local = iy_flange_local + iy_web_local

        ixy_local = 0.0
        
        # Applica rotazione se necessario
        ix, iy, ixy = self._apply_rotation_to_inertia(ix_local, iy_local, ixy_local)
        
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


@dataclass
class LSection(Section):
    """Sezione ad L (angolare)."""

    width: float = 0.0  # Larghezza ala orizzontale (cm)
    height: float = 0.0  # Altezza ala verticale (cm)
    t_horizontal: float = 0.0  # Spessore ala orizzontale (cm)
    t_vertical: float = 0.0  # Spessore ala verticale (cm)

    def __init__(
        self,
        name: str,
        width: float,
        height: float,
        t_horizontal: float,
        t_vertical: float,
        note: str = "",
        rotation_angle_deg: float = 0.0,
    ):
        super().__init__(name=name, section_type="L_SECTION", note=note, rotation_angle_deg=rotation_angle_deg)
        self.width = width
        self.height = height
        self.t_horizontal = t_horizontal
        self.t_vertical = t_vertical

    def _compute(self) -> SectionProperties:
        from sections_app.services.calculations import combine_rectangular_elements, RectangleElement

        if min(self.width, self.height, self.t_horizontal, self.t_vertical) <= 0:
            raise ValueError("Dimensioni non valide per la sezione ad L")

        # Scomposizione in due rettangoli
        # Rettangolo orizzontale: larghezza = width, altezza = t_horizontal
        # Rettangolo verticale: larghezza = t_vertical, altezza = height - t_horizontal

        h_vert = self.height - self.t_horizontal
        if h_vert < 0:
            raise ValueError("Altezza verticale insufficiente rispetto allo spessore orizzontale")

        elements = [
            RectangleElement(
                width=self.width,
                height=self.t_horizontal,
                x_center=self.width / 2,
                y_center=self.height - self.t_horizontal / 2,  # in alto
            ),
            RectangleElement(
                width=self.t_vertical,
                height=h_vert,
                x_center=self.t_vertical / 2,
                y_center=h_vert / 2,
            ),
        ]

        area, x_G, y_G, ix_local, iy_local, ixy_local = combine_rectangular_elements(elements)
        
        # Applica rotazione
        ix, iy, ixy = self._apply_rotation_to_inertia(ix_local, iy_local, ixy_local)

        qx = area * y_G
        qy = area * x_G
        rx = sqrt(ix / area) if area > 0 else 0.0
        ry = sqrt(iy / area) if area > 0 else 0.0
        
        ex = max(x_G, self.width - x_G)
        ey = max(y_G, self.height - y_G)
        core_x = iy / (area * ex) if area > 0 and ex > 0 else 0.0
        core_y = ix / (area * ey) if area > 0 and ey > 0 else 0.0
        
        return SectionProperties(
            area=area,
            centroid_x=x_G,
            centroid_y=y_G,
            ix=ix,
            iy=iy,
            ixy=ixy,
            qx=qx,
            qy=qy,
            rx=rx,
            ry=ry,
            core_x=core_x,
            core_y=core_y,
            ellipse_a=rx,
            ellipse_b=ry,
        )

    def _fill_dimension_fields(self, data: Dict[str, str]) -> None:
        data.update({
            "width": f"{self.width:.6g}",
            "height": f"{self.height:.6g}",
            "flange_thickness": f"{self.t_horizontal:.6g}",
            "web_thickness": f"{self.t_vertical:.6g}",
        })

    def _dimension_key(self) -> Tuple:
        return (
            round(self.width, 6),
            round(self.height, 6),
            round(self.t_horizontal, 6),
            round(self.t_vertical, 6),
        )


@dataclass
class CircularHollowSection(Section):
    """Sezione circolare cava (tubo)."""

    outer_diameter: float = 0.0  # Diametro esterno (cm)
    thickness: float = 0.0  # Spessore parete (cm)

    def __init__(
        self,
        name: str,
        outer_diameter: float,
        thickness: float,
        note: str = "",
        rotation_angle_deg: float = 0.0,
    ):
        super().__init__(name=name, section_type="CIRCULAR_HOLLOW", note=note, rotation_angle_deg=rotation_angle_deg)
        self.outer_diameter = outer_diameter
        self.thickness = thickness

    def _compute(self) -> SectionProperties:
        if self.outer_diameter <= 0 or self.thickness <= 0:
            raise ValueError("Dimensioni non valide per la sezione circolare cava")
        
        inner_diameter = self.outer_diameter - 2 * self.thickness
        if inner_diameter < 0:
            raise ValueError("Spessore troppo grande rispetto al diametro esterno")

        r_out = self.outer_diameter / 2
        r_in = inner_diameter / 2

        area = pi * (r_out**2 - r_in**2)
        centroid_x = r_out
        centroid_y = r_out

        # Inerzie locali (cava = esterna - interna)
        ix_local = (pi / 4) * (r_out**4 - r_in**4)
        iy_local = ix_local
        ixy_local = 0.0

        # Applica rotazione (circolare non cambia, ma manteniamo coerenza)
        ix, iy, ixy = self._apply_rotation_to_inertia(ix_local, iy_local, ixy_local)

        qx = area * centroid_y
        qy = area * centroid_x
        rx = sqrt(ix / area) if area > 0 else 0.0
        ry = rx
        
        core_x = r_out / 4
        core_y = r_out / 4

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
            ellipse_a=rx,
            ellipse_b=ry,
        )

    def _fill_dimension_fields(self, data: Dict[str, str]) -> None:
        data.update({
            "diameter": f"{self.outer_diameter:.6g}",
            "web_thickness": f"{self.thickness:.6g}",
        })

    def _dimension_key(self) -> Tuple:
        return (round(self.outer_diameter, 6), round(self.thickness, 6))


@dataclass
class RectangularHollowSection(Section):
    """Sezione rettangolare cava (tubo rettangolare)."""

    width: float = 0.0  # Larghezza esterna (cm)
    height: float = 0.0  # Altezza esterna (cm)
    thickness: float = 0.0  # Spessore parete (cm)

    def __init__(
        self,
        name: str,
        width: float,
        height: float,
        thickness: float,
        note: str = "",
        rotation_angle_deg: float = 0.0,
    ):
        super().__init__(name=name, section_type="RECTANGULAR_HOLLOW", note=note, rotation_angle_deg=rotation_angle_deg)
        self.width = width
        self.height = height
        self.thickness = thickness

    def _compute(self) -> SectionProperties:
        if min(self.width, self.height, self.thickness) <= 0:
            raise ValueError("Dimensioni non valide per la sezione rettangolare cava")

        w_in = self.width - 2 * self.thickness
        h_in = self.height - 2 * self.thickness

        if w_in < 0 or h_in < 0:
            raise ValueError("Spessore troppo grande rispetto alle dimensioni esterne")

        area = self.width * self.height - w_in * h_in
        centroid_x = self.width / 2
        centroid_y = self.height / 2

        # Inerzie locali (esterna - interna)
        ix_local = (self.width * self.height**3 - w_in * h_in**3) / 12
        iy_local = (self.height * self.width**3 - h_in * w_in**3) / 12
        ixy_local = 0.0

        # Applica rotazione
        ix, iy, ixy = self._apply_rotation_to_inertia(ix_local, iy_local, ixy_local)

        qx = area * centroid_y
        qy = area * centroid_x
        rx = sqrt(ix / area) if area > 0 else 0.0
        ry = sqrt(iy / area) if area > 0 else 0.0
        
        core_x = iy / (area * (self.width / 2)) if area > 0 else 0.0
        core_y = ix / (area * (self.height / 2)) if area > 0 else 0.0

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
            ellipse_a=rx,
            ellipse_b=ry,
        )

    def _fill_dimension_fields(self, data: Dict[str, str]) -> None:
        data.update({
            "width": f"{self.width:.6g}",
            "height": f"{self.height:.6g}",
            "web_thickness": f"{self.thickness:.6g}",
        })

    def _dimension_key(self) -> Tuple:
        return (
            round(self.width, 6),
            round(self.height, 6),
            round(self.thickness, 6),
        )


@dataclass
class ISection(Section):
    """Sezione ad I (doppio T simmetrico)."""

    flange_width: float = 0.0  # Larghezza ali (cm)
    flange_thickness: float = 0.0  # Spessore ali (cm)
    web_height: float = 0.0  # Altezza anima (cm)
    web_thickness: float = 0.0  # Spessore anima (cm)

    def __init__(
        self,
        name: str,
        flange_width: float,
        flange_thickness: float,
        web_height: float,
        web_thickness: float,
        note: str = "",
        rotation_angle_deg: float = 0.0,
    ):
        super().__init__(name=name, section_type="I_SECTION", note=note, rotation_angle_deg=rotation_angle_deg)
        self.flange_width = flange_width
        self.flange_thickness = flange_thickness
        self.web_height = web_height
        self.web_thickness = web_thickness

    @property
    def total_height(self) -> float:
        return 2 * self.flange_thickness + self.web_height

    def _compute(self) -> SectionProperties:
        from sections_app.services.calculations import combine_rectangular_elements, RectangleElement

        if min(self.flange_width, self.flange_thickness, self.web_height, self.web_thickness) <= 0:
            raise ValueError("Dimensioni non valide per la sezione ad I")

        # Tre rettangoli: ala superiore, anima, ala inferiore
        total_h = self.total_height

        elements = [
            # Ala superiore
            RectangleElement(
                width=self.flange_width,
                height=self.flange_thickness,
                x_center=self.flange_width / 2,
                y_center=total_h - self.flange_thickness / 2,
            ),
            # Anima centrale
            RectangleElement(
                width=self.web_thickness,
                height=self.web_height,
                x_center=self.flange_width / 2,
                y_center=self.flange_thickness + self.web_height / 2,
            ),
            # Ala inferiore
            RectangleElement(
                width=self.flange_width,
                height=self.flange_thickness,
                x_center=self.flange_width / 2,
                y_center=self.flange_thickness / 2,
            ),
        ]

        area, x_G, y_G, ix_local, iy_local, ixy_local = combine_rectangular_elements(elements)

        # Applica rotazione
        ix, iy, ixy = self._apply_rotation_to_inertia(ix_local, iy_local, ixy_local)

        qx = area * y_G
        qy = area * x_G
        rx = sqrt(ix / area) if area > 0 else 0.0
        ry = sqrt(iy / area) if area > 0 else 0.0

        ex = self.flange_width / 2
        ey = total_h / 2
        core_x = iy / (area * ex) if area > 0 and ex > 0 else 0.0
        core_y = ix / (area * ey) if area > 0 and ey > 0 else 0.0

        return SectionProperties(
            area=area,
            centroid_x=x_G,
            centroid_y=y_G,
            ix=ix,
            iy=iy,
            ixy=ixy,
            qx=qx,
            qy=qy,
            rx=rx,
            ry=ry,
            core_x=core_x,
            core_y=core_y,
            ellipse_a=rx,
            ellipse_b=ry,
        )

    def _fill_dimension_fields(self, data: Dict[str, str]) -> None:
        data.update({
            "flange_width": f"{self.flange_width:.6g}",
            "flange_thickness": f"{self.flange_thickness:.6g}",
            "web_height": f"{self.web_height:.6g}",
            "web_thickness": f"{self.web_thickness:.6g}",
        })

    def _dimension_key(self) -> Tuple:
        return (
            round(self.flange_width, 6),
            round(self.flange_thickness, 6),
            round(self.web_height, 6),
            round(self.web_thickness, 6),
        )


@dataclass
class PiSection(Section):
    """Sezione a Π (pi greco)."""

    flange_width: float = 0.0  # Larghezza ala superiore (cm)
    flange_thickness: float = 0.0  # Spessore ala superiore (cm)
    web_height: float = 0.0  # Altezza totale anime (cm)
    web_thickness: float = 0.0  # Spessore anime laterali (cm)

    def __init__(
        self,
        name: str,
        flange_width: float,
        flange_thickness: float,
        web_height: float,
        web_thickness: float,
        note: str = "",
        rotation_angle_deg: float = 0.0,
    ):
        super().__init__(name=name, section_type="PI_SECTION", note=note, rotation_angle_deg=rotation_angle_deg)
        self.flange_width = flange_width
        self.flange_thickness = flange_thickness
        self.web_height = web_height
        self.web_thickness = web_thickness

    @property
    def total_height(self) -> float:
        return self.flange_thickness + self.web_height

    def _compute(self) -> SectionProperties:
        from sections_app.services.calculations import combine_rectangular_elements, RectangleElement

        if min(self.flange_width, self.flange_thickness, self.web_height, self.web_thickness) <= 0:
            raise ValueError("Dimensioni non valide per la sezione a Π")

        total_h = self.total_height

        elements = [
            # Ala superiore orizzontale
            RectangleElement(
                width=self.flange_width,
                height=self.flange_thickness,
                x_center=self.flange_width / 2,
                y_center=total_h - self.flange_thickness / 2,
            ),
            # Anima sinistra
            RectangleElement(
                width=self.web_thickness,
                height=self.web_height,
                x_center=self.web_thickness / 2,
                y_center=self.web_height / 2,
            ),
            # Anima destra
            RectangleElement(
                width=self.web_thickness,
                height=self.web_height,
                x_center=self.flange_width - self.web_thickness / 2,
                y_center=self.web_height / 2,
            ),
        ]

        area, x_G, y_G, ix_local, iy_local, ixy_local = combine_rectangular_elements(elements)

        # Applica rotazione
        ix, iy, ixy = self._apply_rotation_to_inertia(ix_local, iy_local, ixy_local)

        qx = area * y_G
        qy = area * x_G
        rx = sqrt(ix / area) if area > 0 else 0.0
        ry = sqrt(iy / area) if area > 0 else 0.0

        ex = max(x_G, self.flange_width - x_G)
        ey = max(y_G, total_h - y_G)
        core_x = iy / (area * ex) if area > 0 and ex > 0 else 0.0
        core_y = ix / (area * ey) if area > 0 and ey > 0 else 0.0

        return SectionProperties(
            area=area,
            centroid_x=x_G,
            centroid_y=y_G,
            ix=ix,
            iy=iy,
            ixy=ixy,
            qx=qx,
            qy=qy,
            rx=rx,
            ry=ry,
            core_x=core_x,
            core_y=core_y,
            ellipse_a=rx,
            ellipse_b=ry,
        )

    def _fill_dimension_fields(self, data: Dict[str, str]) -> None:
        data.update({
            "flange_width": f"{self.flange_width:.6g}",
            "flange_thickness": f"{self.flange_thickness:.6g}",
            "web_height": f"{self.web_height:.6g}",
            "web_thickness": f"{self.web_thickness:.6g}",
        })

    def _dimension_key(self) -> Tuple:
        return (
            round(self.flange_width, 6),
            round(self.flange_thickness, 6),
            round(self.web_height, 6),
            round(self.web_thickness, 6),
        )


@dataclass
class InvertedTSection(Section):
    """Sezione a T rovescia."""

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
        rotation_angle_deg: float = 0.0,
    ):
        super().__init__(name=name, section_type="INVERTED_T_SECTION", note=note, rotation_angle_deg=rotation_angle_deg)
        self.flange_width = flange_width
        self.flange_thickness = flange_thickness
        self.web_thickness = web_thickness
        self.web_height = web_height

    @property
    def total_height(self) -> float:
        return self.flange_thickness + self.web_height

    def _compute(self) -> SectionProperties:
        from sections_app.services.calculations import combine_rectangular_elements, RectangleElement

        if min(self.flange_width, self.flange_thickness, self.web_thickness, self.web_height) <= 0:
            raise ValueError("Dimensioni non valide per la sezione a T rovescia")

        total_h = self.total_height

        elements = [
            # Ala inferiore
            RectangleElement(
                width=self.flange_width,
                height=self.flange_thickness,
                x_center=self.flange_width / 2,
                y_center=self.flange_thickness / 2,
            ),
            # Anima verticale sopra l'ala
            RectangleElement(
                width=self.web_thickness,
                height=self.web_height,
                x_center=self.flange_width / 2,
                y_center=self.flange_thickness + self.web_height / 2,
            ),
        ]

        area, x_G, y_G, ix_local, iy_local, ixy_local = combine_rectangular_elements(elements)

        # Applica rotazione
        ix, iy, ixy = self._apply_rotation_to_inertia(ix_local, iy_local, ixy_local)

        qx = area * y_G
        qy = area * x_G
        rx = sqrt(ix / area) if area > 0 else 0.0
        ry = sqrt(iy / area) if area > 0 else 0.0

        ex = self.flange_width / 2
        ey = max(y_G, total_h - y_G)
        core_x = iy / (area * ex) if area > 0 and ex > 0 else 0.0
        core_y = ix / (area * ey) if area > 0 and ey > 0 else 0.0

        return SectionProperties(
            area=area,
            centroid_x=x_G,
            centroid_y=y_G,
            ix=ix,
            iy=iy,
            ixy=ixy,
            qx=qx,
            qy=qy,
            rx=rx,
            ry=ry,
            core_x=core_x,
            core_y=core_y,
            ellipse_a=rx,
            ellipse_b=ry,
        )

    def _fill_dimension_fields(self, data: Dict[str, str]) -> None:
        data.update({
            "flange_width": f"{self.flange_width:.6g}",
            "flange_thickness": f"{self.flange_thickness:.6g}",
            "web_thickness": f"{self.web_thickness:.6g}",
            "web_height": f"{self.web_height:.6g}",
        })

    def _dimension_key(self) -> Tuple:
        return (
            round(self.flange_width, 6),
            round(self.flange_thickness, 6),
            round(self.web_thickness, 6),
            round(self.web_height, 6),
        )


@dataclass
class CSection(Section):
    """Sezione a C (canale)."""

    width: float = 0.0  # Larghezza totale (cm)
    height: float = 0.0  # Altezza totale (cm)
    flange_thickness: float = 0.0  # Spessore ali orizzontali (cm)
    web_thickness: float = 0.0  # Spessore anima verticale (cm)

    def __init__(
        self,
        name: str,
        width: float,
        height: float,
        flange_thickness: float,
        web_thickness: float,
        note: str = "",
        rotation_angle_deg: float = 0.0,
    ):
        super().__init__(name=name, section_type="C_SECTION", note=note, rotation_angle_deg=rotation_angle_deg)
        self.width = width
        self.height = height
        self.flange_thickness = flange_thickness
        self.web_thickness = web_thickness

    def _compute(self) -> SectionProperties:
        from sections_app.services.calculations import combine_rectangular_elements, RectangleElement

        if min(self.width, self.height, self.flange_thickness, self.web_thickness) <= 0:
            raise ValueError("Dimensioni non valide per la sezione a C")

        h_web = self.height - 2 * self.flange_thickness
        if h_web < 0:
            raise ValueError("Altezza insufficiente rispetto agli spessori delle ali")

        elements = [
            # Ala superiore
            RectangleElement(
                width=self.width,
                height=self.flange_thickness,
                x_center=self.width / 2,
                y_center=self.height - self.flange_thickness / 2,
            ),
            # Anima verticale sinistra
            RectangleElement(
                width=self.web_thickness,
                height=h_web,
                x_center=self.web_thickness / 2,
                y_center=self.flange_thickness + h_web / 2,
            ),
            # Ala inferiore
            RectangleElement(
                width=self.width,
                height=self.flange_thickness,
                x_center=self.width / 2,
                y_center=self.flange_thickness / 2,
            ),
        ]

        area, x_G, y_G, ix_local, iy_local, ixy_local = combine_rectangular_elements(elements)

        # Applica rotazione
        ix, iy, ixy = self._apply_rotation_to_inertia(ix_local, iy_local, ixy_local)

        qx = area * y_G
        qy = area * x_G
        rx = sqrt(ix / area) if area > 0 else 0.0
        ry = sqrt(iy / area) if area > 0 else 0.0

        ex = max(x_G, self.width - x_G)
        ey = self.height / 2
        core_x = iy / (area * ex) if area > 0 and ex > 0 else 0.0
        core_y = ix / (area * ey) if area > 0 and ey > 0 else 0.0

        return SectionProperties(
            area=area,
            centroid_x=x_G,
            centroid_y=y_G,
            ix=ix,
            iy=iy,
            ixy=ixy,
            qx=qx,
            qy=qy,
            rx=rx,
            ry=ry,
            core_x=core_x,
            core_y=core_y,
            ellipse_a=rx,
            ellipse_b=ry,
        )

    def _fill_dimension_fields(self, data: Dict[str, str]) -> None:
        data.update({
            "width": f"{self.width:.6g}",
            "height": f"{self.height:.6g}",
            "flange_thickness": f"{self.flange_thickness:.6g}",
            "web_thickness": f"{self.web_thickness:.6g}",
        })

    def _dimension_key(self) -> Tuple:
        return (
            round(self.width, 6),
            round(self.height, 6),
            round(self.flange_thickness, 6),
            round(self.web_thickness, 6),
        )


@dataclass
class VSection(Section):
    """Sezione a V."""

    width: float = 0.0  # Larghezza alla base (cm)
    height: float = 0.0  # Altezza (cm)
    thickness: float = 0.0  # Spessore pareti (cm)

    def __init__(
        self,
        name: str,
        width: float,
        height: float,
        thickness: float,
        note: str = "",
        rotation_angle_deg: float = 0.0,
    ):
        super().__init__(name=name, section_type="V_SECTION", note=note, rotation_angle_deg=rotation_angle_deg)
        self.width = width
        self.height = height
        self.thickness = thickness

    def _compute(self) -> SectionProperties:
        # Approssimazione semplificata: due rettangoli inclinati
        # Per semplicità, consideriamo una sezione a V simmetrica con due pareti
        if min(self.width, self.height, self.thickness) <= 0:
            raise ValueError("Dimensioni non valide per la sezione a V")

        # Calcolo semplificato: area approssimata
        # Lunghezza di ogni lato inclinato
        half_width = self.width / 2
        length = sqrt(half_width**2 + self.height**2)
        area = 2 * length * self.thickness

        # Baricentro approssimato (simmetrico sull'asse verticale)
        centroid_x = self.width / 2
        centroid_y = self.height / 3  # Approssimazione per forma triangolare

        # Inerzie approssimate (formula semplificata)
        ix_local = area * (self.height / 3) ** 2  # Approssimazione
        iy_local = area * (self.width / 4) ** 2  # Approssimazione
        ixy_local = 0.0  # Simmetrica

        # Applica rotazione
        ix, iy, ixy = self._apply_rotation_to_inertia(ix_local, iy_local, ixy_local)

        qx = area * centroid_y
        qy = area * centroid_x
        rx = sqrt(ix / area) if area > 0 else 0.0
        ry = sqrt(iy / area) if area > 0 else 0.0

        ex = half_width
        ey = self.height
        core_x = iy / (area * ex) if area > 0 and ex > 0 else 0.0
        core_y = ix / (area * ey) if area > 0 and ey > 0 else 0.0

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
            ellipse_a=rx,
            ellipse_b=ry,
        )

    def _fill_dimension_fields(self, data: Dict[str, str]) -> None:
        data.update({
            "width": f"{self.width:.6g}",
            "height": f"{self.height:.6g}",
            "web_thickness": f"{self.thickness:.6g}",
        })

    def _dimension_key(self) -> Tuple:
        return (
            round(self.width, 6),
            round(self.height, 6),
            round(self.thickness, 6),
        )


@dataclass
class InvertedVSection(Section):
    """Sezione a V rovescia."""

    width: float = 0.0  # Larghezza alla base superiore (cm)
    height: float = 0.0  # Altezza (cm)
    thickness: float = 0.0  # Spessore pareti (cm)

    def __init__(
        self,
        name: str,
        width: float,
        height: float,
        thickness: float,
        note: str = "",
        rotation_angle_deg: float = 0.0,
    ):
        super().__init__(name=name, section_type="INVERTED_V_SECTION", note=note, rotation_angle_deg=rotation_angle_deg)
        self.width = width
        self.height = height
        self.thickness = thickness

    def _compute(self) -> SectionProperties:
        # Simile a VSection ma rovesciata
        if min(self.width, self.height, self.thickness) <= 0:
            raise ValueError("Dimensioni non valide per la sezione a V rovescia")

        half_width = self.width / 2
        length = sqrt(half_width**2 + self.height**2)
        area = 2 * length * self.thickness

        centroid_x = self.width / 2
        centroid_y = self.height * 2 / 3  # Rovesciata: baricentro più in alto

        ix_local = area * (self.height / 3) ** 2
        iy_local = area * (self.width / 4) ** 2
        ixy_local = 0.0

        # Applica rotazione
        ix, iy, ixy = self._apply_rotation_to_inertia(ix_local, iy_local, ixy_local)

        qx = area * centroid_y
        qy = area * centroid_x
        rx = sqrt(ix / area) if area > 0 else 0.0
        ry = sqrt(iy / area) if area > 0 else 0.0

        ex = half_width
        ey = self.height
        core_x = iy / (area * ex) if area > 0 and ex > 0 else 0.0
        core_y = ix / (area * ey) if area > 0 and ey > 0 else 0.0

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
            ellipse_a=rx,
            ellipse_b=ry,
        )

    def _fill_dimension_fields(self, data: Dict[str, str]) -> None:
        data.update({
            "width": f"{self.width:.6g}",
            "height": f"{self.height:.6g}",
            "web_thickness": f"{self.thickness:.6g}",
        })

    def _dimension_key(self) -> Tuple:
        return (
            round(self.width, 6),
            round(self.height, 6),
            round(self.thickness, 6),
        )


SECTION_CLASS_MAP = {
    "RECTANGULAR": RectangularSection,
    "CIRCULAR": CircularSection,
    "T_SECTION": TSection,
    "L_SECTION": LSection,
    "I_SECTION": ISection,
    "PI_SECTION": PiSection,
    "INVERTED_T_SECTION": InvertedTSection,
    "C_SECTION": CSection,
    "CIRCULAR_HOLLOW": CircularHollowSection,
    "RECTANGULAR_HOLLOW": RectangularHollowSection,
    "V_SECTION": VSection,
    "INVERTED_V_SECTION": InvertedVSection,
}


def create_section_from_dict(data: Dict[str, str]) -> Section:
    """Factory per creare una sezione da un dizionario letto dal CSV."""
    section_type = (data.get("section_type") or "").strip().upper()
    name = (data.get("name") or "").strip() or section_type
    note = (data.get("note") or "").strip()
    rotation_angle_deg = float(data.get("rotation_angle_deg") or 0)

    def _pick_value(*keys: str) -> Optional[str]:
        for key in keys:
            value = data.get(key)
            if value is not None and value != "":
                return value
        return None

    if section_type == "RECTANGULAR":
        width = float(data.get("width") or 0)
        height = float(data.get("height") or 0)
        _ensure_positive(width, "width")
        _ensure_positive(height, "height")
        section = RectangularSection(name=name, width=width, height=height, note=note, rotation_angle_deg=rotation_angle_deg)
    
    elif section_type == "CIRCULAR":
        diameter = float(data.get("diameter") or 0)
        _ensure_positive(diameter, "diameter")
        section = CircularSection(name=name, diameter=diameter, note=note, rotation_angle_deg=rotation_angle_deg)
    
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
            rotation_angle_deg=rotation_angle_deg,
        )
    
    elif section_type == "L_SECTION":
        width = float(data.get("width") or 0)
        height = float(data.get("height") or 0)
        # Use explicit L-section specific fields: t_horizontal and t_vertical.
        # For backward compatibility only: if t_horizontal/t_vertical are missing,
        # fall back to flange_thickness/web_thickness respectively, but log a
        # warning because these are conceptually different quantities.
        t_horizontal_val = data.get("t_horizontal")
        t_vertical_val = data.get("t_vertical")
        if (t_horizontal_val is None or t_horizontal_val == "") and (data.get("flange_thickness") is not None and data.get("flange_thickness") != ""):
            logger.warning(
                "Campo 'flange_thickness' trovato per L_SECTION: usato come 't_horizontal' per compatibilità. Considera l'aggiornamento dei dati."
            )
            t_horizontal_val = data.get("flange_thickness")
        if (t_vertical_val is None or t_vertical_val == "") and (data.get("web_thickness") is not None and data.get("web_thickness") != ""):
            logger.warning(
                "Campo 'web_thickness' trovato per L_SECTION: usato come 't_vertical' per compatibilità. Considera l'aggiornamento dei dati."
            )
            t_vertical_val = data.get("web_thickness")
        t_horizontal = float(t_horizontal_val or 0)
        t_vertical = float(t_vertical_val or 0)
        _ensure_positive(width, "width")
        _ensure_positive(height, "height")
        _ensure_positive(t_horizontal, "t_horizontal")
        _ensure_positive(t_vertical, "t_vertical")
        section = LSection(
            name=name,
            width=width,
            height=height,
            t_horizontal=t_horizontal,
            t_vertical=t_vertical,
            note=note,
            rotation_angle_deg=rotation_angle_deg,
        )
    
    elif section_type == "I_SECTION":
        flange_width = float(data.get("flange_width") or 0)
        flange_thickness = float(data.get("flange_thickness") or 0)
        web_height = float(data.get("web_height") or 0)
        web_thickness = float(data.get("web_thickness") or 0)
        _ensure_positive(flange_width, "flange_width")
        _ensure_positive(flange_thickness, "flange_thickness")
        _ensure_positive(web_height, "web_height")
        _ensure_positive(web_thickness, "web_thickness")
        section = ISection(
            name=name,
            flange_width=flange_width,
            flange_thickness=flange_thickness,
            web_height=web_height,
            web_thickness=web_thickness,
            note=note,
            rotation_angle_deg=rotation_angle_deg,
        )
    
    elif section_type == "PI_SECTION":
        flange_width = float(data.get("flange_width") or 0)
        flange_thickness = float(data.get("flange_thickness") or 0)
        web_height = float(data.get("web_height") or 0)
        web_thickness = float(data.get("web_thickness") or 0)
        _ensure_positive(flange_width, "flange_width")
        _ensure_positive(flange_thickness, "flange_thickness")
        _ensure_positive(web_height, "web_height")
        _ensure_positive(web_thickness, "web_thickness")
        section = PiSection(
            name=name,
            flange_width=flange_width,
            flange_thickness=flange_thickness,
            web_height=web_height,
            web_thickness=web_thickness,
            note=note,
            rotation_angle_deg=rotation_angle_deg,
        )
    
    elif section_type == "INVERTED_T_SECTION":
        flange_width = float(data.get("flange_width") or 0)
        flange_thickness = float(data.get("flange_thickness") or 0)
        web_thickness = float(data.get("web_thickness") or 0)
        web_height = float(data.get("web_height") or 0)
        _ensure_positive(flange_width, "flange_width")
        _ensure_positive(flange_thickness, "flange_thickness")
        _ensure_positive(web_thickness, "web_thickness")
        _ensure_positive(web_height, "web_height")
        section = InvertedTSection(
            name=name,
            flange_width=flange_width,
            flange_thickness=flange_thickness,
            web_thickness=web_thickness,
            web_height=web_height,
            note=note,
            rotation_angle_deg=rotation_angle_deg,
        )
    
    elif section_type == "C_SECTION":
        width = float(data.get("width") or 0)
        height = float(data.get("height") or 0)
        flange_thickness = float(data.get("flange_thickness") or 0)
        web_thickness = float(data.get("web_thickness") or 0)
        _ensure_positive(width, "width")
        _ensure_positive(height, "height")
        _ensure_positive(flange_thickness, "flange_thickness")
        _ensure_positive(web_thickness, "web_thickness")
        section = CSection(
            name=name,
            width=width,
            height=height,
            flange_thickness=flange_thickness,
            web_thickness=web_thickness,
            note=note,
            rotation_angle_deg=rotation_angle_deg,
        )
    
    elif section_type == "CIRCULAR_HOLLOW":
        outer_diameter = float(_pick_value("outer_diameter", "diameter") or 0)
        thickness = float(_pick_value("thickness", "web_thickness") or 0)
        _ensure_positive(outer_diameter, "outer_diameter")
        _ensure_positive(thickness, "thickness")
        section = CircularHollowSection(
            name=name,
            outer_diameter=outer_diameter,
            thickness=thickness,
            note=note,
            rotation_angle_deg=rotation_angle_deg,
        )
    
    elif section_type == "RECTANGULAR_HOLLOW":
        width = float(data.get("width") or 0)
        height = float(data.get("height") or 0)
        thickness = float(_pick_value("thickness", "web_thickness") or 0)
        _ensure_positive(width, "width")
        _ensure_positive(height, "height")
        _ensure_positive(thickness, "thickness")
        section = RectangularHollowSection(
            name=name,
            width=width,
            height=height,
            thickness=thickness,
            note=note,
            rotation_angle_deg=rotation_angle_deg,
        )
    
    elif section_type == "V_SECTION":
        width = float(data.get("width") or 0)
        height = float(data.get("height") or 0)
        thickness = float(_pick_value("thickness", "web_thickness") or 0)
        _ensure_positive(width, "width")
        _ensure_positive(height, "height")
        _ensure_positive(thickness, "thickness")
        section = VSection(
            name=name,
            width=width,
            height=height,
            thickness=thickness,
            note=note,
            rotation_angle_deg=rotation_angle_deg,
        )
    
    elif section_type == "INVERTED_V_SECTION":
        width = float(data.get("width") or 0)
        height = float(data.get("height") or 0)
        thickness = float(_pick_value("thickness", "web_thickness") or 0)
        _ensure_positive(width, "width")
        _ensure_positive(height, "height")
        _ensure_positive(thickness, "thickness")
        section = InvertedVSection(
            name=name,
            width=width,
            height=height,
            thickness=thickness,
            note=note,
            rotation_angle_deg=rotation_angle_deg,
        )
    
    else:
        raise ValueError(f"Tipo di sezione non riconosciuto: {section_type}")

    # Optional persisted shear values: kappa_y/kappa_z and A_y/A_z.
    # If kappa values are present, set them on the section so compute_properties
    # will use the persisted values. If only A_y/A_z are present, derive kappa
    # from A_y/area to preserve the exported value when re-importing.
    def _safe_float(key: str):
        v = data.get(key)
        if v is None or v == "":
            return None
        try:
            return float(v)
        except Exception:
            logger.debug("Invalid float for %s: %r", key, v)
            return None

    k_y = _safe_float("kappa_y")
    k_z = _safe_float("kappa_z")
    A_y_csv = _safe_float("A_y")
    A_z_csv = _safe_float("A_z")

    if k_y is not None:
        section.shear_factor_y = k_y
    if k_z is not None:
        section.shear_factor_z = k_z

    # If only A_y/A_z provided in CSV, and area is present, derive kappa to preserve
    # the imported effective areas upon re-saving (compatibility with older CSVs).
    try:
        area_csv = float(data.get("area")) if (data.get("area") is not None and data.get("area") != "") else None
    except Exception:
        area_csv = None

    if k_y is None and A_y_csv is not None and area_csv and area_csv > 0:
        section.shear_factor_y = A_y_csv / area_csv
    if k_z is None and A_z_csv is not None and area_csv and area_csv > 0:
        section.shear_factor_z = A_z_csv / area_csv

    section.id = (data.get("id") or "").strip() or section.id
    return section


def _ensure_positive(value: float, label: str) -> None:
    if value <= 0:
        raise ValueError(f"{label} deve essere positivo")

