"""Modelli materiali per il core di calcolo.

Classi base per calcestruzzo e acciaio strutturale, con parametri
caratteristici e di progetto secondo le normative italiane.

Unità: MPa (moduli, resistenze), kg/m³ (densità).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Material:
    """Materiale generico strutturale."""

    name: str = ""
    material_type: str = ""  # "concrete", "steel"
    E: float = 0.0           # Modulo elastico [MPa]
    nu: float = 0.0          # Coefficiente di Poisson
    density: float = 0.0     # Densità [kg/m³]

    def __repr__(self) -> str:
        return f"Material(name={self.name!r}, type={self.material_type!r})"


@dataclass
class Concrete(Material):
    """Calcestruzzo strutturale.

    Attributi principali:
        f_ck: Resistenza caratteristica cilindrica a compressione [MPa].
        f_ck_cube: Resistenza caratteristica cubica [MPa].
        gamma_c: Coefficiente parziale di sicurezza (1.50 NTC2018).
        alpha_cc: Coefficiente effetti lungo termine (0.85 NTC2018).
    """

    material_type: str = "concrete"
    f_ck: float = 25.0
    f_ck_cube: float = 30.0
    gamma_c: float = 1.50
    alpha_cc: float = 0.85
    density: float = 2500.0

    @property
    def f_cd(self) -> float:
        """Resistenza di calcolo a compressione [MPa]."""
        return self.alpha_cc * self.f_ck / self.gamma_c

    @property
    def f_ctm(self) -> float:
        """Resistenza media a trazione [MPa] (EC2 Table 3.1)."""
        if self.f_ck <= 50.0:
            return 0.30 * self.f_ck ** (2.0 / 3.0)
        return 2.12 * (1.0 + self.f_ck / 10.0) ** 0.1  # pragma: no cover

    def __repr__(self) -> str:
        return f"Concrete(name={self.name!r}, f_ck={self.f_ck})"


@dataclass
class Steel(Material):
    """Acciaio per armatura strutturale.

    Attributi principali:
        f_yk: Resistenza caratteristica a snervamento [MPa].
        f_tk: Resistenza caratteristica a rottura [MPa].
        gamma_s: Coefficiente parziale di sicurezza (1.15 NTC2018).
    """

    material_type: str = "steel"
    f_yk: float = 450.0
    f_tk: float = 540.0
    gamma_s: float = 1.15
    E: float = 200000.0
    density: float = 7850.0

    @property
    def f_yd(self) -> float:
        """Resistenza di calcolo a snervamento [MPa]."""
        return self.f_yk / self.gamma_s

    def __repr__(self) -> str:
        return f"Steel(name={self.name!r}, f_yk={self.f_yk})"
