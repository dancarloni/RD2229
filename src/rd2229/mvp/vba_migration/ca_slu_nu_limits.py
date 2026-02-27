"""
Migration: CA_SLU::VerifResistCA_SLU_TensNorm (sub-calcolo Nu_max / Nu_min)

Sub-calcolo pilota del modulo VBA `CA_SLU` (visual_basic/CA_SLU.bas).
Implementa il calcolo dei limiti assiali di resistenza per sezione rettangolare
in c.a. ordinario senza FRP e senza confinamento.

Formule (caso semplificato):
    fcd = fck / gamma_c          [MPa]  (resistenza di progetto cls)
    fyd = fyk / gamma_s          [MPa]  (resistenza di progetto acciaio)
    Asez = B_cm * H_cm * 1e2     [mm²]  (area lorda sezione)
    Nu_max = Aft_mm2 * fyd       [N]    (max trazione)
    Nu_min = -fcd * Asez - Aft_mm2 * fyd  [N]  (max compressione)

Unità input/output: mm, MPa, N (SI puro) per evitare conversioni.
Conversione da/verso kN esposta tramite helper.

TODO(NTC/EC/RD): Verificare che la formula Nu_min = -(fcd*Asez + Aft*fyd) corrisponda
    all'equazione del cap. 4.1.2.1.2 NTC2018 per sezione rettangolare in compressione
    assiale semplice (confirmare riferimento normativo puntuale).
TODO(EC2): Verificare coerenza con EN1992-1-1 §6.1 (interaction domain method):
    la formula semplificata ipotizza acciaio a fyd sia in trazione sia in compressione.
TODO(NTC/EC/RD): Per acciai con Eps_yd significativamente diverso da Eps_c2 (es. alta
    resistenza), implementare funzione bilineare completa f_Sigf(Eps_c2) come nel VBA.
"""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class RectSectionInput:
    """Input per sezione rettangolare c.a. ordinario.

    Args:
        b_mm: Larghezza sezione [mm].
        h_mm: Altezza sezione [mm].
        aft_mm2: Area totale armatura longitudinale [mm²].
        fck_mpa: Resistenza caratteristica cilindrica calcestruzzo [MPa].
        fyk_mpa: Resistenza caratteristica acciaio [MPa].
        gamma_c: Coefficiente parziale calcestruzzo (default 1.5 per NTC2018/EC2).
        gamma_s: Coefficiente parziale acciaio (default 1.15 per NTC2018/EC2).
    """

    b_mm: float
    h_mm: float
    aft_mm2: float
    fck_mpa: float
    fyk_mpa: float
    gamma_c: float = 1.5
    gamma_s: float = 1.15

    def __post_init__(self) -> None:
        if self.b_mm <= 0 or self.h_mm <= 0:
            raise ValueError("Le dimensioni della sezione devono essere positive.")
        if self.aft_mm2 < 0:
            raise ValueError("L'area dell'armatura non può essere negativa.")
        if self.fck_mpa <= 0 or self.fyk_mpa <= 0:
            raise ValueError("Le resistenze dei materiali devono essere positive.")
        if self.gamma_c <= 0 or self.gamma_s <= 0:
            raise ValueError("I coefficienti parziali devono essere positivi.")


@dataclass(frozen=True)
class AxialCapacityResult:
    """Risultato del calcolo dei limiti assiali di resistenza.

    Args:
        nu_max_n: Resistenza massima a trazione [N] (positivo).
        nu_min_n: Resistenza massima a compressione [N] (negativo).
        fcd_mpa: Resistenza di progetto calcestruzzo [MPa].
        fyd_mpa: Resistenza di progetto acciaio [MPa].
        asez_mm2: Area lorda sezione [mm²].
    """

    nu_max_n: float
    nu_min_n: float
    fcd_mpa: float
    fyd_mpa: float
    asez_mm2: float

    @property
    def nu_max_kn(self) -> float:
        """Resistenza massima a trazione [kN]."""
        return self.nu_max_n / 1000.0

    @property
    def nu_min_kn(self) -> float:
        """Resistenza massima a compressione [kN]."""
        return self.nu_min_n / 1000.0

    def check_axial(self, ned_n: float) -> tuple[bool, float]:
        """Verifica che Ned sia nel dominio [Nu_min, Nu_max].

        Args:
            ned_n: Sforzo normale di progetto [N] (positivo = trazione).

        Returns:
            (ok_axial, eta) dove eta = |Ned| / |limite| applicabile.
        """
        ok_axial = self.nu_min_n <= ned_n <= self.nu_max_n
        limit = abs(self.nu_min_n) if ned_n <= 0 else self.nu_max_n
        eta = abs(ned_n) / limit if limit != 0 else float("inf")
        return ok_axial, eta


def compute_axial_capacity(inp: RectSectionInput) -> AxialCapacityResult:
    """Calcola i limiti assiali di resistenza per sezione rettangolare c.a.

    Implementa il sub-calcolo Nu_max / Nu_min di CA_SLU::VerifResistCA_SLU_TensNorm
    per il caso: c.a. ordinario, nessun FRP, nessun confinamento.

    Args:
        inp: Parametri di input della sezione.

    Returns:
        AxialCapacityResult con Nu_max, Nu_min e parametri derivati.
    """
    fcd = inp.fck_mpa / inp.gamma_c  # [MPa]
    fyd = inp.fyk_mpa / inp.gamma_s  # [MPa]
    asez = inp.b_mm * inp.h_mm  # [mm²]

    nu_max = inp.aft_mm2 * fyd  # [N]
    nu_min = -(fcd * asez + inp.aft_mm2 * fyd)  # [N]

    return AxialCapacityResult(
        nu_max_n=nu_max,
        nu_min_n=nu_min,
        fcd_mpa=fcd,
        fyd_mpa=fyd,
        asez_mm2=asez,
    )


def bar_area_mm2(diameter_mm: float, n_bars: int) -> float:
    """Calcola l'area totale di n_bars barre di diametro diameter_mm [mm²]."""
    return n_bars * math.pi * diameter_mm**2 / 4.0
