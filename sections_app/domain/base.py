"""Modelli di dominio base per le sezioni."""

import math
from abc import ABC, abstractmethod
from dataclasses import dataclass

from ..config import DEFAULT_SHEAR_KAPPAS


@dataclass(frozen=True, slots=True)
class SectionProperties:
    """Proprietà geometriche e meccaniche di una sezione."""

    # Proprietà geometriche
    area: float = 0.0
    A_y: float = 0.0  # Area shear y
    A_z: float = 0.0  # Area shear z
    kappa_y: float = 0.0  # Shear correction factor y
    kappa_z: float = 0.0  # Shear correction factor z

    # Centro di gravità
    x_g: float = 0.0
    y_g: float = 0.0

    # Momenti di inerzia
    Ix: float = 0.0
    Iy: float = 0.0
    Ixy: float = 0.0

    # Momenti di inerzia principali
    I1: float = 0.0
    I2: float = 0.0
    principal_angle_deg: float = 0.0

    # Raggi di inerzia principali
    principal_rx: float = 0.0
    principal_ry: float = 0.0

    # Proprietà shear
    Qx: float = 0.0
    Qy: float = 0.0

    # Raggi di inerzia
    rx: float = 0.0
    ry: float = 0.0

    # Core section
    core_x: float = 0.0
    core_y: float = 0.0

    # Ellisse di inerzia
    ellipse_a: float = 0.0
    ellipse_b: float = 0.0

    def compute_derived_properties(self) -> 'SectionProperties':
        """Calcola proprietà derivate e restituisce una nuova istanza."""
        # Raggi di inerzia
        rx = math.sqrt(self.Ix / self.area) if self.Ix > 0 and self.area > 0 else 0.0
        ry = math.sqrt(self.Iy / self.area) if self.Iy > 0 and self.area > 0 else 0.0

        # Momenti di inerzia principali e angolo
        I1, I2, principal_angle_deg = self.I1, self.I2, self.principal_angle_deg
        principal_rx, principal_ry = self.principal_rx, self.principal_ry

        if self.Ix > 0 and self.Iy > 0:
            # Formula per momenti principali
            I_avg = (self.Ix + self.Iy) / 2
            I_diff = (self.Ix - self.Iy) / 2
            I_xy_term = self.Ixy**2

            discriminant = I_diff**2 + I_xy_term
            if discriminant >= 0:
                sqrt_disc = math.sqrt(discriminant)
                I1 = I_avg + sqrt_disc
                I2 = I_avg - sqrt_disc

                # Angolo principale
                if abs(self.Ixy) < 1e-10:
                    principal_angle_deg = 0.0
                else:
                    tan_2theta = 2 * self.Ixy / (self.Ix - self.Iy)
                    theta_rad = math.atan(tan_2theta) / 2
                    principal_angle_deg = math.degrees(theta_rad)

                # Raggi di inerzia principali
                principal_rx = math.sqrt(I1 / self.area) if I1 > 0 and self.area > 0 else 0.0
                principal_ry = math.sqrt(I2 / self.area) if I2 > 0 and self.area > 0 else 0.0

        # Ellisse di inerzia
        ellipse_a = math.sqrt(I1 / self.area) if I1 > 0 and self.area > 0 else 0.0
        ellipse_b = math.sqrt(I2 / self.area) if I2 > 0 and self.area > 0 else 0.0

        return SectionProperties(
            area=self.area,
            A_y=self.A_y,
            A_z=self.A_z,
            kappa_y=self.kappa_y,
            kappa_z=self.kappa_z,
            x_g=self.x_g,
            y_g=self.y_g,
            Ix=self.Ix,
            Iy=self.Iy,
            Ixy=self.Ixy,
            I1=I1,
            I2=I2,
            principal_angle_deg=principal_angle_deg,
            principal_rx=principal_rx,
            principal_ry=principal_ry,
            Qx=self.Qx,
            Qy=self.Qy,
            rx=rx,
            ry=ry,
            core_x=self.core_x,
            core_y=self.core_y,
            ellipse_a=ellipse_a,
            ellipse_b=ellipse_b,
        )


class Section(ABC):
    """Classe base astratta per tutte le sezioni."""

    def __init__(
        self,
        section_id: str,
        name: str,
        dimensions: dict[str, float],
        rotation_angle_deg: float = 0.0,
        note: str = "",
    ):
        """Inizializza una sezione.

        Args:
            section_id: Identificatore univoco della sezione
            name: Nome della sezione
            dimensions: Dizionario delle dimensioni geometriche
            rotation_angle_deg: Angolo di rotazione in gradi
            note: Note aggiuntive
        """
        self.id = section_id
        self.name = name
        self.dimensions = dimensions.copy()
        self.rotation_angle_deg = rotation_angle_deg
        self.note = note

        # Calcola proprietà geometriche base
        base_properties = self._compute_geometric_properties()

        # Calcola proprietà derivate e crea istanza finale
        self.properties = base_properties.compute_derived_properties()

    @property
    @abstractmethod
    def section_type(self) -> str:
        """Tipo della sezione (es. 'RECTANGULAR', 'CIRCULAR')."""

    @abstractmethod
    def _compute_geometric_properties(self) -> SectionProperties:
        """Calcola le proprietà geometriche specifiche della sezione.

        Returns:
            SectionProperties con le proprietà geometriche calcolate.
        """

    def get_default_shear_kappas(self) -> tuple[float, float]:
        """Restituisce i fattori di correzione shear di default per il tipo di sezione.

        Returns:
            Tupla (kappa_y, kappa_z)
        """
        return DEFAULT_SHEAR_KAPPAS.get(self.section_type, (1.0, 1.0))

    def to_dict(self) -> dict:
        """Converte la sezione in dizionario per serializzazione.

        Returns:
            Dizionario con tutti i dati della sezione
        """
        result = {
            "id": self.id,
            "name": self.name,
            "section_type": self.section_type,
            "rotation_angle_deg": self.rotation_angle_deg,
            "note": self.note,
        }

        # Aggiungi dimensioni
        result.update(self.dimensions)

        # Aggiungi proprietà calcolate
        props_dict = {
            "area": self.properties.area,
            "A_y": self.properties.A_y,
            "A_z": self.properties.A_z,
            "kappa_y": self.properties.kappa_y,
            "kappa_z": self.properties.kappa_z,
            "x_G": self.properties.x_g,
            "y_G": self.properties.y_g,
            "Ix": self.properties.Ix,
            "Iy": self.properties.Iy,
            "Ixy": self.properties.Ixy,
            "I1": self.properties.I1,
            "I2": self.properties.I2,
            "principal_angle_deg": self.properties.principal_angle_deg,
            "principal_rx": self.properties.principal_rx,
            "principal_ry": self.properties.principal_ry,
            "Qx": self.properties.Qx,
            "Qy": self.properties.Qy,
            "rx": self.properties.rx,
            "ry": self.properties.ry,
            "core_x": self.properties.core_x,
            "core_y": self.properties.core_y,
            "ellipse_a": self.properties.ellipse_a,
            "ellipse_b": self.properties.ellipse_b,
        }
        result.update(props_dict)

        return result

    def __repr__(self) -> str:
        """Rappresentazione stringa della sezione."""
        return f"{self.__class__.__name__}(id='{self.id}', name='{self.name}')"
