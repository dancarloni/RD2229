from __future__ import annotations

from dataclasses import dataclass
from math import atan2, cos, sin, sqrt
from typing import List, Tuple


@dataclass
class RectangleElement:
    """Elemento rettangolare per calcoli di sezioni composte."""

    width: float  # Larghezza (cm)
    height: float  # Altezza (cm)
    x_center: float  # Coordinata x del baricentro rispetto a un'origine locale (cm)
    y_center: float  # Coordinata y del baricentro rispetto a un'origine locale (cm)


def rotate_inertia(Ix: float, Iy: float, Ixy: float, theta_rad: float) -> Tuple[float, float, float]:
    """Ruota il tensore di inerzia di un angolo theta_rad (radianti) attorno al baricentro.

    Formule di rototrasformazione del tensore di inerzia:
    - Ix' = Ix * cos²θ + Iy * sin²θ - 2 * Ixy * sinθ * cosθ
    - Iy' = Ix * sin²θ + Iy * cos²θ + 2 * Ixy * sinθ * cosθ
    - Ixy' = (Ix - Iy) * sinθ * cosθ + Ixy * (cos²θ - sin²θ)

    Args:
        Ix: Momento di inerzia rispetto all'asse x non ruotato (cm⁴)
        Iy: Momento di inerzia rispetto all'asse y non ruotato (cm⁴)
        Ixy: Prodotto di inerzia non ruotato (cm⁴)
        theta_rad: Angolo di rotazione in radianti

    Returns:
        Tuple (Ix_rot, Iy_rot, Ixy_rot) - inerzie ruotate (cm⁴)

    """
    c = cos(theta_rad)
    s = sin(theta_rad)
    c2 = c * c
    s2 = s * s
    cs = c * s

    Ix_rot = Ix * c2 + Iy * s2 - 2 * Ixy * cs
    Iy_rot = Ix * s2 + Iy * c2 + 2 * Ixy * cs
    Ixy_rot = (Ix - Iy) * cs + Ixy * (c2 - s2)

    return Ix_rot, Iy_rot, Ixy_rot


def translate_inertia(I_local: float, area: float, distance: float) -> float:
    """Teorema di trasporto (Steiner) per momenti di inerzia.

    I_global = I_local + A * d²

    Args:
        I_local: Momento di inerzia rispetto al baricentro locale (cm⁴)
        area: Area dell'elemento (cm²)
        distance: Distanza tra i due assi paralleli (cm)

    Returns:
        Momento di inerzia rispetto all'asse traslato (cm⁴)

    """
    return I_local + area * distance * distance


def compute_principal_inertia(Ix: float, Iy: float, Ixy: float) -> tuple:
    """Compute principal inertias and principal angle (in radians).

    Uses standard formulas:
      Imean = (Ix + Iy) / 2
      R = sqrt(((Ix - Iy) / 2)**2 + Ixy**2)
      I1 = Imean + R
      I2 = Imean - R
      angle = 0.5 * atan2(2 * Ixy, Ix - Iy)

    Returns (I1, I2, angle_rad)
    """
    Imean = (Ix + Iy) / 2.0
    R = sqrt(((Ix - Iy) / 2.0) ** 2 + (Ixy) ** 2)
    I1 = Imean + R
    I2 = Imean - R
    angle = 0.5 * atan2(2.0 * Ixy, Ix - Iy)
    return I1, I2, angle


def combine_rectangular_elements(
    elements: List[RectangleElement],
) -> Tuple[float, float, float, float, float, float]:
    """Combina elementi rettangolari per calcolare le proprietà globali di una sezione composta.

    Calcola:
    - Area totale
    - Baricentro globale (x_G, y_G)
    - Momenti di inerzia globali (Ix, Iy, Ixy) rispetto al baricentro globale

    Args:
        elements: Lista di elementi rettangolari con dimensioni e posizioni

    Returns:
        Tuple (area_tot, x_G, y_G, Ix, Iy, Ixy)

    """
    if not elements:
        return 0.0, 0.0, 0.0, 0.0, 0.0, 0.0

    # Calcola area totale e baricentro globale
    area_tot = 0.0
    sum_ax = 0.0
    sum_ay = 0.0

    for elem in elements:
        a = elem.width * elem.height
        area_tot += a
        sum_ax += a * elem.x_center
        sum_ay += a * elem.y_center

    if area_tot == 0:
        return 0.0, 0.0, 0.0, 0.0, 0.0, 0.0

    x_G = sum_ax / area_tot
    y_G = sum_ay / area_tot

    # Calcola momenti di inerzia rispetto al baricentro globale
    Ix_tot = 0.0
    Iy_tot = 0.0
    Ixy_tot = 0.0

    for elem in elements:
        a = elem.width * elem.height
        # Inerzie locali dell'elemento rettangolare rispetto al suo baricentro
        Ix_local = (elem.width * elem.height**3) / 12
        Iy_local = (elem.height * elem.width**3) / 12

        # Distanze dal baricentro globale
        dx = elem.x_center - x_G
        dy = elem.y_center - y_G

        # Teorema di trasporto (Steiner)
        Ix_tot += Ix_local + a * dy * dy
        Iy_tot += Iy_local + a * dx * dx
        # Prodotto di inerzia: Ixy_local per rettangolo simmetrico = 0, quindi solo trasporto
        Ixy_tot += a * dx * dy

    return area_tot, x_G, y_G, Ix_tot, Iy_tot, Ixy_tot


@dataclass
class CanvasTransform:
    """Trasformazione per mappare coordinate reali su canvas Tkinter."""

    scale: float
    offset_x: float
    offset_y: float

    def to_canvas(self, x: float, y: float, height: float) -> Tuple[float, float]:
        """Converte coordinate con origine in basso a sinistra (x,y) al canvas."""
        cx = self.offset_x + x * self.scale
        cy = self.offset_y + (height - y) * self.scale
        return cx, cy


def compute_transform(
    width: float, height: float, canvas_width: int, canvas_height: int, padding: int = 20
) -> CanvasTransform:
    """Calcola il fattore di scala per adattare la sezione al canvas."""
    if width <= 0 or height <= 0:
        return CanvasTransform(scale=1.0, offset_x=padding, offset_y=padding)
    scale = min((canvas_width - 2 * padding) / width, (canvas_height - 2 * padding) / height)
    offset_x = (canvas_width - width * scale) / 2
    offset_y = (canvas_height - height * scale) / 2
    return CanvasTransform(scale=scale, offset_x=offset_x, offset_y=offset_y)
