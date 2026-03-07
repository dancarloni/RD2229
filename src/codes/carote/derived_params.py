"""Parametri derivati del calcestruzzo a partire da f_ck in situ.

Formule EC2 EN 1992-1-1 §3.1:
  f_cm = f_ck + 8 [MPa]
  E_cm = 22000 * (f_cm/10)^0.3 [MPa]
  f_ctm = 0.30 * f_ck^(2/3) [MPa] per f_ck <= 50
  f_ctm = 2.12 * ln(1 + f_cm/10) [MPa] per f_ck > 50
  f_ctk,0.05 = 0.70 * f_ctm
  f_ctk,0.95 = 1.30 * f_ctm

Rck = f_ck / 0.83 [MPa] (NTC2018 §11.2.10.1)
sigma_c_adm storica: da Rck in kg/cm² secondo tabella RD2229.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

# Fattore conversione MPa -> kg/cm²
_MPA_TO_KG_CM2 = 1.0 / 0.0980665  # ~10.197


@dataclass
class DerivedConcreteParams:
    """Parametri derivati del calcestruzzo in situ."""

    f_ck_is_mpa: float
    f_cm_is_mpa: float
    E_cm_mpa: float
    f_ctm_mpa: float
    f_ctk_005_mpa: float
    f_ctk_095_mpa: float
    Rck_mpa: float
    sigma_c_adm_kgcm2: float
    classification: str
    passaggi_calcolo: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Serializza per report/export."""
        return {
            "f_ck_is_mpa": round(self.f_ck_is_mpa, 3),
            "f_cm_is_mpa": round(self.f_cm_is_mpa, 3),
            "E_cm_mpa": round(self.E_cm_mpa, 0),
            "f_ctm_mpa": round(self.f_ctm_mpa, 3),
            "f_ctk_005_mpa": round(self.f_ctk_005_mpa, 3),
            "f_ctk_095_mpa": round(self.f_ctk_095_mpa, 3),
            "Rck_mpa": round(self.Rck_mpa, 2),
            "sigma_c_adm_kgcm2": round(self.sigma_c_adm_kgcm2, 1),
            "classification": self.classification,
        }


# ---------------------------------------------------------------------------
# Tabella sigma_c_adm storica da Rck (kg/cm²)
# RD2229 e norme storiche: sigma_c_adm = Rck / (n * gamma)
# Valori tabulati approssimati per cls storici.
# ---------------------------------------------------------------------------

_SIGMA_ADM_TABLE: list[tuple[float, float]] = [
    # (Rck_kgcm2, sigma_c_adm_kgcm2) — valori standard storici
    (150, 18.0),
    (200, 25.0),
    (250, 32.0),
    (300, 37.5),
    (350, 43.5),
    (400, 50.0),
    (450, 56.0),
    (500, 62.5),
]


def _sigma_c_adm_storica(Rck_kgcm2: float) -> float:
    """Calcola sigma_c_adm storica da Rck [kg/cm²] per interpolazione."""
    table = _SIGMA_ADM_TABLE
    if Rck_kgcm2 <= table[0][0]:
        # Proporzione lineare dal primo valore
        return table[0][1] * Rck_kgcm2 / table[0][0]
    if Rck_kgcm2 >= table[-1][0]:
        return table[-1][1] * Rck_kgcm2 / table[-1][0]
    for i in range(len(table) - 1):
        r0, s0 = table[i]
        r1, s1 = table[i + 1]
        if r0 <= Rck_kgcm2 <= r1:
            return s0 + (s1 - s0) * (Rck_kgcm2 - r0) / (r1 - r0)
    return Rck_kgcm2 / 8.0  # fallback conservativo  # pragma: no cover


def calcola_parametri_derivati(
    f_ck_is_mpa: float,
    classification: str = "",
) -> DerivedConcreteParams:
    """Calcola tutti i parametri derivati da f_ck,is.

    Args:
        f_ck_is_mpa: resistenza caratteristica in situ [MPa]
        classification: classe calcestruzzo (se gia' nota)

    Returns:
        DerivedConcreteParams con tutti i valori
    """
    if f_ck_is_mpa <= 0:
        raise ValueError(f"f_ck_is_mpa deve essere > 0, ricevuto {f_ck_is_mpa}")

    passaggi: list[str] = []

    # f_cm
    f_cm = f_ck_is_mpa + 8.0
    passaggi.append(f"f_cm = f_ck + 8 = {f_ck_is_mpa:.3f} + 8 = {f_cm:.3f} MPa")

    # E_cm (EC2 §3.1.3 Tab. 3.1)
    E_cm = 22000.0 * (f_cm / 10.0) ** 0.3
    passaggi.append(f"E_cm = 22000*(f_cm/10)^0.3 = 22000*({f_cm:.3f}/10)^0.3 = {E_cm:.0f} MPa")

    # f_ctm (EC2 §3.1.2)
    if f_ck_is_mpa <= 50.0:
        f_ctm = 0.30 * f_ck_is_mpa ** (2.0 / 3.0)
        passaggi.append(
            f"f_ctm = 0.30*f_ck^(2/3) = 0.30*{f_ck_is_mpa:.3f}^0.667 = {f_ctm:.3f} MPa"
        )
    else:
        f_ctm = 2.12 * math.log(1.0 + f_cm / 10.0)
        passaggi.append(
            f"f_ctm = 2.12*ln(1+f_cm/10) = 2.12*ln(1+{f_cm:.3f}/10) = {f_ctm:.3f} MPa"
        )

    # Frattili trazione
    f_ctk_005 = 0.70 * f_ctm
    f_ctk_095 = 1.30 * f_ctm
    passaggi.append(f"f_ctk,0.05 = 0.70*{f_ctm:.3f} = {f_ctk_005:.3f} MPa")
    passaggi.append(f"f_ctk,0.95 = 1.30*{f_ctm:.3f} = {f_ctk_095:.3f} MPa")

    # Rck
    Rck = f_ck_is_mpa / 0.83
    passaggi.append(f"Rck = f_ck/0.83 = {f_ck_is_mpa:.3f}/0.83 = {Rck:.2f} MPa")

    # sigma_c_adm storica
    Rck_kgcm2 = Rck * _MPA_TO_KG_CM2
    sigma_adm = _sigma_c_adm_storica(Rck_kgcm2)
    passaggi.append(
        f"Rck = {Rck_kgcm2:.1f} kg/cm² -> σ_c_adm = {sigma_adm:.1f} kg/cm² (storica)"
    )

    return DerivedConcreteParams(
        f_ck_is_mpa=f_ck_is_mpa,
        f_cm_is_mpa=f_cm,
        E_cm_mpa=E_cm,
        f_ctm_mpa=f_ctm,
        f_ctk_005_mpa=f_ctk_005,
        f_ctk_095_mpa=f_ctk_095,
        Rck_mpa=Rck,
        sigma_c_adm_kgcm2=sigma_adm,
        classification=classification,
        passaggi_calcolo=passaggi,
    )
