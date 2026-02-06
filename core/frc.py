"""Modulo per il comportamento semplificato delle fibre composite (FRC).

NOTE:
- Implementazione iniziale semplice: modello lineare troncato per la relazione stress-strain
  delle fibre. Il comportamento preciso sarà aggiornato per raggiungere la parità numerica
  con le formule VB in iterazioni successive.
"""

from __future__ import annotations

from typing import Tuple

from core_models.materials import Material


def frc_stress(material: Material, strain: float) -> float:
    """Calcola la tensione delle fibre data la deformazione (strain).

    Behaviour (MVP):
    - Se material.frc_enabled è False → 0.0
    - Se non sono specificati fFtu o frc_eps_fu → 0.0
    - Modello: linear up to eps_fu, capped at fFtu.

    Returns:
        stress in same units as material.frc_fFtu (float)
    """
    if not getattr(material, "frc_enabled", False):
        return 0.0
    fFtu = getattr(material, "frc_fFtu", None)
    eps_fu = getattr(material, "frc_eps_fu", None)

    if fFtu is None or eps_fu is None or eps_fu == 0:
        return 0.0

    # linear proportional up to eps_fu
    sigma = fFtu * (strain / eps_fu)
    if sigma > fFtu:
        sigma = fFtu
    if sigma < 0.0:
        sigma = 0.0
    return sigma


def apply_frc_to_section(
    section, material: Material, strain_distribution
) -> Tuple[float, float, float]:
    """Placeholder: applica il contributo FRC alla sezione e ritorna (N, My, Mz).

    Implementazione completa verrà aggiunta nelle iterazioni successive.
    """
    # Per ora ritorna contributo nullo; API pronta per integrazione successiva
    return 0.0, 0.0, 0.0
