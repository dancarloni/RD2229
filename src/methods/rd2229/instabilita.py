"""
Verifica di stabilità (carico di punta) — Metodo Tensioni Ammissibili (RD 2229/39).

Traduzione da VB: Sub VerifStabilitàAstaCA() (PrincipCA_TA.bas, riga 4057)
                   Function f_OmegaCA(Lam) (riga 4272)
                   Function f_Sigcar() (riga 4262)

Metodo ω per pilastri in c.a. compressi o pressoinflessi:
    1. Calcolo snellezza λ = L₀/i (in ciascun piano)
    2. Determinazione coefficiente ω da tabella interpolata
    3. Verifica:
       - Compressione semplice: σ_c = ω·N/A_ci ≤ σ_c_adm
       - Pressoflessione: 3 verifiche combinate con amplificazione momento

Coefficiente ω (tabella RD2229 / Santarella):
    λ ≤ 50:   ω = 1.00
    λ = 70:   ω = 1.08
    λ = 85:   ω = 1.32
    λ = 100:  ω = 1.62
    λ = 120:  ω = 2.28
    λ = 140:  ω = 3.00
    λ > 140:  ω = 10 (sezione da riprogettare)

Tensione ammissibile ridotta per sezioni snelle (a < 25 cm):
    σ_c_adm,r = 0.7·σ_c_adm·(1 - 0.03·(25 - a))

Unità: kg/cm² per tensioni, cm per geometria, kg per forze, kg·cm per momenti.

Riferimenti:
    - RD 2229/39 art. 14, 36
    - DM 1972 §7 (tabella ω)
    - Santarella, "Il cemento armato", Vol. I, Cap. 9
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class EsitoStabilita(str, Enum):
    """Esito della verifica di stabilità."""

    VERIFICATA = "verificata"
    NON_VERIFICATA = "non_verificata"
    NON_COMPRESSA = "non_compressa"  # Nr ≥ 0 (trazione)
    SNELLEZZA_ECCESSIVA = "snellezza_eccessiva"  # λ > 140


@dataclass
class InputStabilita:
    """Dati di input per la verifica di stabilità TA.

    Geometria in cm, forze in kg, momenti in kg·cm, tensioni in kg/cm².
    """

    # Sollecitazioni
    Nr: float  # kg — sforzo normale (negativo = compressione)
    Mr: float  # kg·cm — momento flettente risultante

    # Geometria sezione
    B: float  # cm — larghezza
    H: float  # cm — altezza

    # Proprietà sezione omogenizzata
    A_sez: float  # cm² — area cls sezione lorda
    I_yp: float  # cm⁴ — inerzia y (sezione omogenizzata)
    I_zp: float  # cm⁴ — inerzia z (sezione omogenizzata)
    A_ci: float  # cm² — area cls ideale (cls + n·A_s)
    r_yp: float  # cm — raggio d'inerzia y (sezione omogenizzata)
    r_zp: float  # cm — raggio d'inerzia z (sezione omogenizzata)

    # Armatura totale
    A_ft: float  # cm² — area totale armatura

    # Materiali
    sigma_c_adm: float  # kg/cm² — σ_c ammissibile (compressione semplice)
    sigma_s_adm: float  # kg/cm² — σ_s ammissibile acciaio
    E_c: float  # kg/cm² — modulo elastico cls
    n: float = 15.0  # coefficiente di omogenizzazione

    # Lunghezza asta e vincoli
    L: float = 0.0  # cm — lunghezza asta
    beta_y: float = 1.0  # coefficiente lunghezza libera piano xz
    beta_z: float = 1.0  # coefficiente lunghezza libera piano xy


@dataclass
class RisultatoStabilita:
    """Risultato della verifica di stabilità TA."""

    esito: EsitoStabilita
    lambda_y: float = 0.0  # snellezza piano xz
    lambda_z: float = 0.0  # snellezza piano xy
    lambda_max: float = 0.0  # snellezza massima
    L0_y: float = 0.0  # cm — lunghezza libera y
    L0_z: float = 0.0  # cm — lunghezza libera z
    Pcr_y: float = 0.0  # kg — carico critico Euleriano y
    Pcr_z: float = 0.0  # kg — carico critico Euleriano z
    Pcr: float = 0.0  # kg — carico critico minimo
    sigma_cr: float = 0.0  # kg/cm² — tensione critica Euleriana
    omega: float = 1.0  # coefficiente ω
    alpha_M: float = 1.0  # coefficiente amplificazione momento

    # Tensioni verifica 1 (compressione semplice amplificata)
    sigma_c_1: float = 0.0  # kg/cm²
    sigma_s_1: float = 0.0  # kg/cm²
    verifica_1: bool = False

    # Tensioni verifica 2 (N e M amplificati)
    sigma_c_2: float = 0.0
    sigma_s_2: float = 0.0
    verifica_2: bool = False

    # Tensioni verifica 3 (solo M amplificato)
    sigma_c_3: float = 0.0
    sigma_s_3: float = 0.0
    verifica_3: bool = False

    verifica_soddisfatta: bool = False
    passaggi: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Serializza il risultato per report."""
        return {
            "esito": self.esito.value,
            "lambda_y": round(self.lambda_y, 1),
            "lambda_z": round(self.lambda_z, 1),
            "lambda_max": round(self.lambda_max, 1),
            "L0_y_cm": round(self.L0_y, 1),
            "L0_z_cm": round(self.L0_z, 1),
            "Pcr_kg": round(self.Pcr, 0),
            "sigma_cr_kg_cm2": round(self.sigma_cr, 2),
            "omega": round(self.omega, 4),
            "alpha_M": round(self.alpha_M, 4),
            "sigma_c_1_kg_cm2": round(self.sigma_c_1, 2),
            "sigma_s_1_kg_cm2": round(self.sigma_s_1, 2),
            "verifica_1": self.verifica_1,
            "sigma_c_2_kg_cm2": round(self.sigma_c_2, 2),
            "sigma_s_2_kg_cm2": round(self.sigma_s_2, 2),
            "verifica_2": self.verifica_2,
            "sigma_c_3_kg_cm2": round(self.sigma_c_3, 2),
            "sigma_s_3_kg_cm2": round(self.sigma_s_3, 2),
            "verifica_3": self.verifica_3,
            "verifica_soddisfatta": self.verifica_soddisfatta,
            "passaggi": self.passaggi,
        }


def omega_ca(lam: float) -> float:
    """Coefficiente ω per c.a. in funzione della snellezza λ.

    Interpolazione lineare sulla tabella RD2229/DM72/Santarella.
    Traduzione da VB: Function f_OmegaCA(Lam)

    Tabella:
        λ ≤ 50:    ω = 1.00
        λ = 70:    ω = 1.08
        λ = 85:    ω = 1.32
        λ = 100:   ω = 1.62
        λ = 120:   ω = 2.28
        λ = 140:   ω = 3.00
        λ > 140:   ω = 10 (penalizzazione forte)
    """
    if lam <= 50:
        return 1.0
    elif lam <= 70:
        return 1.0 + (1.08 - 1.0) * (lam - 50) / (70 - 50)
    elif lam <= 85:
        return 1.08 + (1.32 - 1.08) * (lam - 70) / (85 - 70)
    elif lam <= 100:
        return 1.32 + (1.62 - 1.32) * (lam - 85) / (100 - 85)
    elif lam <= 120:
        return 1.62 + (2.28 - 1.62) * (lam - 100) / (120 - 100)
    elif lam <= 140:
        return 2.28 + (3.0 - 2.28) * (lam - 120) / (140 - 120)
    else:
        return 10.0


def sigma_c_adm_ridotta(sigma_c_adm: float, B: float, H: float) -> float:
    """σ_c ammissibile ridotta per sezioni snelle (dimensione minima < 25 cm).

    σ_c_adm,r = 0.7·σ_c_adm·(1 - 0.03·(25 - a))   se a < 25 cm
    σ_c_adm,r = 0.7·σ_c_adm                          se a ≥ 25 cm

    dove a = min(B, H).

    Traduzione da VB: Function f_Sigcar()
    """
    a = min(B, H)
    if a < 25.0:
        return 0.7 * sigma_c_adm * (1.0 - 0.03 * (25.0 - a))
    else:
        return 0.7 * sigma_c_adm


def verifica_stabilita_ta(inp: InputStabilita) -> RisultatoStabilita:
    """Esegue la verifica di stabilità (carico di punta) con metodo TA.

    Tre verifiche per pressoflessione:
        1ª: σ_c = ω·N / A_ci ≤ σ_c_adm   (compressione pura amplificata)
        2ª: Pressoflessione con N amplificato (ω·N) e M amplificato (α_M·M)
        3ª: Pressoflessione con N non amplificato e M amplificato (α_M·M)

    Per compressione semplice (Mr=0): solo verifica 1.

    Args:
        inp: dati di input (geometria, sollecitazioni, materiali).

    Returns:
        RisultatoStabilita con esito, tensioni, passaggi.
    """
    ris = RisultatoStabilita(esito=EsitoStabilita.NON_COMPRESSA)
    passaggi = ris.passaggi

    # Asta non compressa (Nr ≥ 0 → trazione)
    if inp.Nr >= 0:
        passaggi.append(
            "Sforzo normale non di compressione → verifica a carico di punta non necessaria."
        )
        ris.verifica_soddisfatta = True
        return ris

    # Lunghezze libere di inflessione
    L0_y = inp.beta_y * inp.L
    L0_z = inp.beta_z * inp.L
    ris.L0_y = L0_y
    ris.L0_z = L0_z

    # Snellezza
    if inp.r_yp > 0:
        lambda_y = L0_y / inp.r_yp
    else:
        lambda_y = 0.0
    if inp.r_zp > 0:
        lambda_z = L0_z / inp.r_zp
    else:
        lambda_z = 0.0
    lambda_max = max(lambda_y, lambda_z)
    ris.lambda_y = lambda_y
    ris.lambda_z = lambda_z
    ris.lambda_max = lambda_max

    passaggi.append(f"L₀,y = β_y·L = {inp.beta_y}×{inp.L:.1f} = {L0_y:.1f} cm")
    passaggi.append(f"L₀,z = β_z·L = {inp.beta_z}×{inp.L:.1f} = {L0_z:.1f} cm")
    passaggi.append(f"λ_y = L₀,y/r_y = {lambda_y:.1f}")
    passaggi.append(f"λ_z = L₀,z/r_z = {lambda_z:.1f}")
    passaggi.append(f"λ = max(λ_y, λ_z) = {lambda_max:.1f}")

    # Snellezza eccessiva
    if lambda_max > 140:
        ris.esito = EsitoStabilita.SNELLEZZA_ECCESSIVA
        ris.omega = 10.0
        passaggi.append("λ > 140 → snellezza eccessiva, sezione da riprogettare.")
        return ris

    if lambda_max > 100:
        passaggi.append("⚠ Attenzione: λ > 100 (limite opportuno da non superare).")

    # Carico critico Euleriano
    # Pcr = π²·(0.4·Ec)·I / L₀²
    # Nota: 0.4·Ec tiene conto della viscosità del cls (RD2229/Santarella)
    E_rid = 0.4 * inp.E_c
    if L0_y > 0:
        Pcr_y = math.pi**2 * E_rid * inp.I_yp / L0_y**2
    else:
        Pcr_y = float("inf")
    if L0_z > 0:
        Pcr_z = math.pi**2 * E_rid * inp.I_zp / L0_z**2
    else:
        Pcr_z = float("inf")
    Pcr = min(Pcr_y, Pcr_z)

    ris.Pcr_y = Pcr_y
    ris.Pcr_z = Pcr_z
    ris.Pcr = Pcr
    passaggi.append(f"Pcr = π²·0.4·Ec·I / L₀² = {Pcr:.0f} kg")

    # Tensione critica
    if inp.A_ci > 0:
        sigma_cr = Pcr / inp.A_ci
    else:
        sigma_cr = 0.0
    ris.sigma_cr = sigma_cr
    passaggi.append(f"σ_cr = Pcr/A_ci = {sigma_cr:.2f} kg/cm²")

    # Coefficiente ω
    w = omega_ca(lambda_max)
    ris.omega = w
    passaggi.append(f"ω({lambda_max:.0f}) = {w:.4f}")

    # Tensione ammissibile ridotta per sezioni snelle
    sigma_car = sigma_c_adm_ridotta(inp.sigma_c_adm, inp.B, inp.H)
    passaggi.append(f"σ_c,adm ridotta = {sigma_car:.2f} kg/cm²")

    Nr = inp.Nr  # negativo (compressione)
    Mr = inp.Mr

    if abs(Mr) < 1e-6:
        # Compressione semplice
        if inp.A_ci > 0:
            sigma_c_1 = w * abs(Nr) / inp.A_ci
        else:
            sigma_c_1 = 0.0
        sigma_s_1 = inp.n * sigma_c_1
        ris.sigma_c_1 = sigma_c_1
        ris.sigma_s_1 = sigma_s_1

        passaggi.append(f"Compressione semplice: σ_c = ω·|N|/A_ci = {sigma_c_1:.2f} kg/cm²")
        passaggi.append(f"σ_s = n·σ_c = {sigma_s_1:.2f} kg/cm²")

        if sigma_c_1 <= sigma_car and sigma_s_1 <= inp.sigma_s_adm:
            ris.verifica_1 = True
            ris.verifica_soddisfatta = True
            ris.esito = EsitoStabilita.VERIFICATA
            passaggi.append("Verifica a carico di punta soddisfatta.")
        else:
            ris.verifica_1 = False
            ris.verifica_soddisfatta = False
            ris.esito = EsitoStabilita.NON_VERIFICATA
            passaggi.append("Verifica a carico di punta NON soddisfatta.")
    else:
        # Pressoflessione
        # Coefficiente amplificazione momento
        if Pcr_y > 0:
            alpha_M = 1.0 / (1.0 - abs(Nr) / Pcr_y)
        else:
            alpha_M = 10.0
        ris.alpha_M = alpha_M
        passaggi.append(f"α_M = 1/(1 - |N|/Pcr_y) = {alpha_M:.4f}")

        # 1ª verifica: compressione semplice con N amplificato
        if inp.A_ci > 0:
            sigma_c_1 = w * abs(Nr) / inp.A_ci
        else:
            sigma_c_1 = 0.0
        sigma_s_1 = inp.n * sigma_c_1
        ris.sigma_c_1 = sigma_c_1
        ris.sigma_s_1 = sigma_s_1
        ris.verifica_1 = sigma_c_1 <= sigma_car and sigma_s_1 <= inp.sigma_s_adm
        passaggi.append(
            f"1ª verifica (N amplificato): σ_c = {sigma_c_1:.2f}, σ_s = {sigma_s_1:.2f} kg/cm² "
            f"→ {'OK' if ris.verifica_1 else 'NON OK'}"
        )

        # 2ª verifica: pressoflessione con N e M amplificati (ω·N, α_M·M)
        # La verifica completa richiederebbe il calcolo tensioni normali
        # per pressoflessione. Qui calcoliamo con Navier per sez. omogenizzata.
        N_amp = w * abs(Nr)
        M_amp = alpha_M * abs(Mr)
        sigma_c_2, sigma_s_2 = _tensioni_pressoflessione(
            N_amp, M_amp, inp.A_ci, inp.I_yp, inp.H, inp.n
        )
        ris.sigma_c_2 = sigma_c_2
        ris.sigma_s_2 = sigma_s_2
        ris.verifica_2 = sigma_c_2 <= sigma_car and sigma_s_2 <= inp.sigma_s_adm
        passaggi.append(
            f"2ª verifica (ω·N + α_M·M): σ_c = {sigma_c_2:.2f}, σ_s = {sigma_s_2:.2f} kg/cm² "
            f"→ {'OK' if ris.verifica_2 else 'NON OK'}"
        )

        # 3ª verifica: N non amplificato, M amplificato
        N_3 = abs(Nr)
        M_3 = alpha_M * abs(Mr)
        sigma_c_3, sigma_s_3 = _tensioni_pressoflessione(N_3, M_3, inp.A_ci, inp.I_yp, inp.H, inp.n)
        ris.sigma_c_3 = sigma_c_3
        ris.sigma_s_3 = sigma_s_3
        ris.verifica_3 = sigma_c_3 <= sigma_car and sigma_s_3 <= inp.sigma_s_adm
        passaggi.append(
            f"3ª verifica (N + α_M·M): σ_c = {sigma_c_3:.2f}, σ_s = {sigma_s_3:.2f} kg/cm² "
            f"→ {'OK' if ris.verifica_3 else 'NON OK'}"
        )

        # Verifica complessiva
        if ris.verifica_1 and ris.verifica_2 and ris.verifica_3:
            ris.verifica_soddisfatta = True
            ris.esito = EsitoStabilita.VERIFICATA
            passaggi.append("Verifica a carico di punta soddisfatta (tutte e 3 le verifiche OK).")
        else:
            ris.verifica_soddisfatta = False
            ris.esito = EsitoStabilita.NON_VERIFICATA
            passaggi.append("Verifica a carico di punta NON soddisfatta.")

    return ris


def _tensioni_pressoflessione(
    N: float, M: float, A_ci: float, I_y: float, H: float, n: float
) -> tuple[float, float]:
    """Calcola tensioni cls e acciaio per pressoflessione (Navier semplificato).

    σ_c = N/A_ci + M·y_max/I_y   (massima compressione cls)
    σ_s = n · σ_c                (approssimazione conservativa per acciaio)

    N è assunto positivo (compressione), M positivo.

    Returns:
        (sigma_c, sigma_s) in kg/cm²
    """
    if A_ci <= 0 or I_y <= 0:
        return 0.0, 0.0
    y_max = H / 2.0
    sigma_c = N / A_ci + M * y_max / I_y
    sigma_s = n * abs(N / A_ci) + n * M * y_max / I_y
    return abs(sigma_c), abs(sigma_s)
