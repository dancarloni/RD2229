"""Verifiche muratura — compressione, taglio nel piano, snellezza, spanciamento.

Verifiche secondo:
- NTC2018 §4.5 + Circolare n.7/2019 §C4.5
- DM 20/11/1987 (muratura nuova e esistente)
- Circ. 30/07/1981 n.21745 (muratura esistente)

Unità: kg/cm² per tensioni, cm per geometria, kg per forze.

Riferimenti:
- NTC2018 Tab. 4.5.V: coefficiente Φ di riduzione per snellezza
- NTC2018 §4.5.6.2: compressione centrata e eccentrica
- Turnšek-Čačovič (1970): criterio diagonale per taglio
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum


class TipoMuratura(str, Enum):
    """Tipo di muratura."""
    MATTONI_PIENI = "mattoni_pieni"
    MATTONI_FORATI = "mattoni_forati"
    BLOCCHI_CLS = "blocchi_cls"
    BLOCCHI_LATERIZIO = "blocchi_laterizio"
    PIETRA_SQUADRATA = "pietra_squadrata"
    PIETRA_SBOZZATA = "pietra_sbozzata"
    TUFO = "tufo"


class NormaMuratura(str, Enum):
    """Norma di riferimento per le verifiche."""
    NTC2018 = "NTC2018"
    DM87 = "DM87"
    CIRC81 = "Circ81"


# ═══════════════════════════════════════════════════════════
#  Tabella Φ — coefficiente riduzione per snellezza
#  NTC2018 Tab. 4.5.V
# ═══════════════════════════════════════════════════════════

# Φ in funzione di λ = h_eff/t e e/t (eccentricità relativa)
# Colonne: e/t = 0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.33
PHI_TABLE_LAMBDA = [0, 5, 10, 15, 20, 25, 27]
PHI_TABLE_ET = [0.0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.33]

PHI_TABLE: list[list[float]] = [
    # λ=0
    [1.00, 0.87, 0.73, 0.60, 0.47, 0.33, 0.20, 0.13],
    # λ=5
    [1.00, 0.87, 0.73, 0.60, 0.47, 0.33, 0.20, 0.13],
    # λ=10
    [0.97, 0.84, 0.71, 0.58, 0.45, 0.32, 0.19, 0.13],
    # λ=15
    [0.89, 0.77, 0.65, 0.53, 0.41, 0.29, 0.17, 0.11],
    # λ=20
    [0.78, 0.67, 0.56, 0.45, 0.34, 0.24, 0.14, 0.09],
    # λ=25
    [0.65, 0.55, 0.46, 0.36, 0.27, 0.18, 0.09, 0.06],
    # λ=27
    [0.57, 0.48, 0.39, 0.31, 0.22, 0.14, 0.06, 0.03],
]


def interpola_phi(lam: float, e_t: float) -> float:
    """Interpola Φ dalla tabella NTC2018 Tab 4.5.V.

    Args:
        lam: snellezza λ = h_eff/t
        e_t: eccentricità relativa e/t

    Returns:
        Φ coefficiente di riduzione (0 < Φ ≤ 1)
    """
    # Clamp valori
    lam = max(0, min(lam, 27))
    e_t = max(0, min(e_t, 0.33))

    # Trova indici per interpolazione bilineare
    li = 0
    for i in range(len(PHI_TABLE_LAMBDA) - 1):
        if PHI_TABLE_LAMBDA[i] <= lam <= PHI_TABLE_LAMBDA[i + 1]:
            li = i
            break
    else:
        li = len(PHI_TABLE_LAMBDA) - 2

    ei = 0
    for i in range(len(PHI_TABLE_ET) - 1):
        if PHI_TABLE_ET[i] <= e_t <= PHI_TABLE_ET[i + 1]:
            ei = i
            break
    else:
        ei = len(PHI_TABLE_ET) - 2

    # Interpolazione bilineare
    l0, l1 = PHI_TABLE_LAMBDA[li], PHI_TABLE_LAMBDA[li + 1]
    e0, e1 = PHI_TABLE_ET[ei], PHI_TABLE_ET[ei + 1]

    tl = (lam - l0) / (l1 - l0) if l1 != l0 else 0.0
    te = (e_t - e0) / (e1 - e0) if e1 != e0 else 0.0

    f00 = PHI_TABLE[li][ei]
    f10 = PHI_TABLE[li + 1][ei]
    f01 = PHI_TABLE[li][ei + 1]
    f11 = PHI_TABLE[li + 1][ei + 1]

    phi = (
        f00 * (1 - tl) * (1 - te)
        + f10 * tl * (1 - te)
        + f01 * (1 - tl) * te
        + f11 * tl * te
    )
    return max(phi, 0.0)


# ═══════════════════════════════════════════════════════════
#  E.1 — Compressione + snellezza
# ═══════════════════════════════════════════════════════════

@dataclass
class InputCompressione:
    """Input verifica a compressione muratura."""
    # Geometria parete
    L: float                     # lunghezza parete [cm]
    t: float                     # spessore parete [cm]
    h: float                     # altezza piano [cm]

    # Vincoli per lunghezza libera
    rho: float = 1.0             # fattore vincolo (0.75 incastro-incastro, 1.0 appoggio)

    # Sollecitazioni
    N: float = 0.0               # sforzo normale compressione [kg] (positivo = compressione)
    M: float = 0.0               # momento flettente [kg·cm]

    # Materiale
    fd: float = 0.0              # resistenza di calcolo a compressione [kg/cm²]
    gamma_M: float = 3.0         # coefficiente parziale materiale

    # Normativa
    norma: str = "NTC2018"


@dataclass
class RisultatoCompressione:
    """Risultato verifica compressione muratura."""
    N: float                     # carico [kg]
    A: float                     # area sezione [cm²]
    sigma: float                 # tensione σ = N/A [kg/cm²]
    e: float                     # eccentricità [cm]
    e_t: float                   # eccentricità relativa e/t
    h_eff: float                 # altezza efficace [cm]
    lam: float                   # snellezza λ = h_eff/t
    phi: float                   # coefficiente Φ
    N_Rd: float                  # resistenza di calcolo [kg]
    sfruttamento: float          # N/N_Rd
    verificato: bool
    passaggi: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "N": round(self.N, 1),
            "sigma": round(self.sigma, 2),
            "e": round(self.e, 2),
            "e_t": round(self.e_t, 4),
            "h_eff": round(self.h_eff, 1),
            "lambda": round(self.lam, 1),
            "phi": round(self.phi, 4),
            "N_Rd": round(self.N_Rd, 1),
            "sfruttamento": round(self.sfruttamento, 4),
            "verificato": self.verificato,
            "passaggi": self.passaggi,
        }


def verifica_compressione(inp: InputCompressione) -> RisultatoCompressione:
    """Verifica a compressione centrata/eccentrica muratura.

    NTC2018 §4.5.6.2:
    N_Rd = Φ × fd × A
    dove Φ = Φ(λ, e/t) dalla Tab. 4.5.V

    Args:
        inp: dati di input

    Returns:
        RisultatoCompressione
    """
    passaggi: list[str] = []

    A = inp.L * inp.t
    sigma = inp.N / A if A > 0 else 0.0

    # Eccentricità
    e = abs(inp.M / inp.N) if inp.N > 0 else 0.0
    e_t = e / inp.t if inp.t > 0 else 0.0

    # Altezza efficace e snellezza
    h_eff = inp.rho * inp.h
    lam = h_eff / inp.t if inp.t > 0 else 0.0

    passaggi.append(f"Parete: L={inp.L:.0f} cm, t={inp.t:.0f} cm, h={inp.h:.0f} cm")
    passaggi.append(f"A = L×t = {A:.0f} cm²")
    passaggi.append(f"σ = N/A = {inp.N:.0f}/{A:.0f} = {sigma:.2f} kg/cm²")
    passaggi.append(f"Eccentricità: e = M/N = {e:.2f} cm, e/t = {e_t:.4f}")
    passaggi.append(f"h_eff = ρ×h = {inp.rho}×{inp.h:.0f} = {h_eff:.0f} cm")
    passaggi.append(f"Snellezza: λ = h_eff/t = {h_eff:.0f}/{inp.t:.0f} = {lam:.1f}")

    # Limite snellezza
    if lam > 27:
        passaggi.append(f"ATTENZIONE: λ = {lam:.1f} > 27 — oltre limite tabella NTC2018")

    # Coefficiente Φ
    phi = interpola_phi(lam, e_t)
    passaggi.append(f"Φ(λ={lam:.1f}, e/t={e_t:.4f}) = {phi:.4f}")

    # Resistenza
    N_Rd = phi * inp.fd * A
    sfruttamento = inp.N / N_Rd if N_Rd > 0 else float("inf")

    verificato = inp.N <= N_Rd and lam <= 27

    passaggi.append(
        f"N_Rd = Φ×fd×A = {phi:.4f}×{inp.fd:.1f}×{A:.0f} = {N_Rd:.0f} kg"
    )
    passaggi.append(
        f"N = {inp.N:.0f} {'≤' if verificato else '>'} N_Rd = {N_Rd:.0f} "
        f"→ {'OK' if verificato else 'NON VERIFICATO'} "
        f"(sfruttamento {sfruttamento:.1%})"
    )

    return RisultatoCompressione(
        N=inp.N, A=A, sigma=sigma,
        e=e, e_t=e_t,
        h_eff=h_eff, lam=lam, phi=phi,
        N_Rd=N_Rd,
        sfruttamento=sfruttamento,
        verificato=verificato,
        passaggi=passaggi,
    )


# ═══════════════════════════════════════════════════════════
#  E.2 — Taglio nel piano
# ═══════════════════════════════════════════════════════════

class CriterioTaglio(str, Enum):
    """Criterio di rottura a taglio."""
    DIAGONALE = "diagonale"         # Turnšek-Čačovič (fessurazione diagonale)
    SCORRIMENTO = "scorrimento"     # attrito + coesione (Mohr-Coulomb)
    PRESSOFLESSIONE = "pressoflessione"  # rottura per schiacciamento


@dataclass
class InputTaglio:
    """Input verifica taglio nel piano muratura."""
    # Geometria pannello murario
    L: float                     # lunghezza pannello [cm]
    t: float                     # spessore [cm]
    h: float                     # altezza pannello [cm]

    # Sollecitazioni
    V: float = 0.0               # taglio [kg]
    N: float = 0.0               # sforzo normale (compressione positiva) [kg]

    # Materiale
    tau_0: float = 0.0           # resistenza a taglio senza compressione [kg/cm²]
    fd: float = 0.0              # resistenza a compressione [kg/cm²]
    fvk0: float = 0.0            # resistenza caratteristica a taglio [kg/cm²]
    mu: float = 0.4              # coefficiente d'attrito

    # Coefficienti
    gamma_M: float = 3.0
    b_coeff: float = 1.0         # coefficiente distribuzione tensioni (1.0÷1.5)

    # Condizioni di vincolo
    psi: float = 1.0             # ψ = h₀/L rapporto di taglio (1.0 = doppio incastro)


@dataclass
class RisultatoTaglio:
    """Risultato verifica taglio nel piano."""
    criterio: str
    V: float                     # taglio applicato [kg]
    V_Rd: float                  # resistenza a taglio [kg]
    sigma_0: float               # tensione media compressione [kg/cm²]
    sfruttamento: float
    verificato: bool
    passaggi: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "criterio": self.criterio,
            "V": round(self.V, 1),
            "V_Rd": round(self.V_Rd, 1),
            "sigma_0": round(self.sigma_0, 2),
            "sfruttamento": round(self.sfruttamento, 4),
            "verificato": self.verificato,
            "passaggi": self.passaggi,
        }


def taglio_diagonale(inp: InputTaglio) -> RisultatoTaglio:
    """Verifica taglio con criterio diagonale (Turnšek-Čačovič).

    NTC2018 §7.8.2.2.1 (edifici esistenti) e §C8.7.1.3.1.1 Circ. n.7/2019:
    V_t = L × t × (1.5 × τ₀d / b) × √(1 + σ₀/(1.5 × τ₀d))

    dove:
    - τ₀d = τ₀ / γ_M (resistenza a taglio di riferimento)
    - σ₀ = N / (L×t) (tensione media di compressione)
    - b = 1.0÷1.5 (distribuzione tensioni tangenziali, dipende da h/L)
    """
    passaggi: list[str] = []

    A = inp.L * inp.t
    sigma_0 = inp.N / A if A > 0 else 0.0
    tau_0d = inp.tau_0 / inp.gamma_M

    passaggi.append("Criterio diagonale (Turnšek-Čačovič)")
    passaggi.append(f"Pannello: L={inp.L:.0f}×t={inp.t:.0f}×h={inp.h:.0f} cm")
    passaggi.append(f"σ₀ = N/(L×t) = {inp.N:.0f}/{A:.0f} = {sigma_0:.2f} kg/cm²")
    passaggi.append(f"τ₀d = τ₀/γ_M = {inp.tau_0:.2f}/{inp.gamma_M:.1f} = {tau_0d:.3f} kg/cm²")

    # Coefficiente b (distribuzione tensioni)
    h_L = inp.h / inp.L if inp.L > 0 else 1.0
    b = max(1.0, min(h_L, 1.5))
    passaggi.append(f"b = min(h/L, 1.5) = min({h_L:.2f}, 1.5) = {b:.2f}")

    # Resistenza a taglio
    if tau_0d > 0:
        radicando = 1 + sigma_0 / (1.5 * tau_0d)
        radicando = max(radicando, 0)  # evita radice negativa
        V_Rd = inp.L * inp.t * (1.5 * tau_0d / b) * math.sqrt(radicando)
    else:
        V_Rd = 0.0

    sfruttamento = abs(inp.V) / V_Rd if V_Rd > 0 else float("inf")
    verificato = abs(inp.V) <= V_Rd

    passaggi.append(
        f"V_t = L×t×(1.5τ₀d/b)×√(1+σ₀/(1.5τ₀d)) = "
        f"{inp.L:.0f}×{inp.t:.0f}×({1.5*tau_0d:.3f}/{b:.2f})×√(1+{sigma_0:.2f}/{1.5*tau_0d:.3f})"
    )
    passaggi.append(
        f"V_t = {V_Rd:.0f} kg"
    )
    passaggi.append(
        f"|V| = {abs(inp.V):.0f} {'≤' if verificato else '>'} V_t = {V_Rd:.0f} "
        f"→ {'OK' if verificato else 'NON VERIFICATO'} (sfruttamento {sfruttamento:.1%})"
    )

    return RisultatoTaglio(
        criterio="diagonale",
        V=abs(inp.V), V_Rd=V_Rd, sigma_0=sigma_0,
        sfruttamento=sfruttamento, verificato=verificato,
        passaggi=passaggi,
    )


def taglio_scorrimento(inp: InputTaglio) -> RisultatoTaglio:
    """Verifica taglio con criterio di scorrimento (attrito + coesione).

    NTC2018 §4.5.6.1.2:
    fvd = fvk / γ_M
    fvk = fvk0 + μ × σ_n

    V_Rd = fvd × L' × t

    dove L' = L (sezione compressa), σ_n = N/(L×t)
    """
    passaggi: list[str] = []

    A = inp.L * inp.t
    sigma_n = inp.N / A if A > 0 else 0.0

    # fvk = fvk0 + μ × σ_n  (con limite fvk ≤ 0.065 × fb, semplificato)
    fvk = inp.fvk0 + inp.mu * sigma_n
    fvd = fvk / inp.gamma_M

    passaggi.append("Criterio scorrimento (Mohr-Coulomb)")
    passaggi.append(f"σ_n = N/(L×t) = {sigma_n:.2f} kg/cm²")
    passaggi.append(f"fvk = fvk0 + μ×σ_n = {inp.fvk0:.3f} + {inp.mu}×{sigma_n:.2f} = {fvk:.3f} kg/cm²")
    passaggi.append(f"fvd = fvk/γ_M = {fvk:.3f}/{inp.gamma_M:.1f} = {fvd:.4f} kg/cm²")

    # Lunghezza compressa (semplificazione: tutta la sezione)
    L_compr = inp.L
    V_Rd = fvd * L_compr * inp.t

    sfruttamento = abs(inp.V) / V_Rd if V_Rd > 0 else float("inf")
    verificato = abs(inp.V) <= V_Rd

    passaggi.append(
        f"V_Rd = fvd×L×t = {fvd:.4f}×{L_compr:.0f}×{inp.t:.0f} = {V_Rd:.0f} kg"
    )
    passaggi.append(
        f"|V| = {abs(inp.V):.0f} {'≤' if verificato else '>'} V_Rd = {V_Rd:.0f} "
        f"→ {'OK' if verificato else 'NON VERIFICATO'} (sfruttamento {sfruttamento:.1%})"
    )

    return RisultatoTaglio(
        criterio="scorrimento",
        V=abs(inp.V), V_Rd=V_Rd, sigma_0=sigma_n,
        sfruttamento=sfruttamento, verificato=verificato,
        passaggi=passaggi,
    )


def taglio_pressoflessione(inp: InputTaglio) -> RisultatoTaglio:
    """Verifica taglio con criterio di pressoflessione (schiacciamento).

    NTC2018 §C8.7.1.3.1.1:
    V_pf = (L²×t×σ₀) / (2×h₀) × (1 - σ₀/(0.85×fd))

    dove h₀ = ψ×L (altezza di taglio: ψ=1 doppio incastro, ψ=0.5 mensola)
    """
    passaggi: list[str] = []

    A = inp.L * inp.t
    sigma_0 = inp.N / A if A > 0 else 0.0
    h0 = inp.psi * inp.h  # altezza di taglio

    passaggi.append("Criterio pressoflessione (schiacciamento)")
    passaggi.append(f"σ₀ = {sigma_0:.2f} kg/cm², fd = {inp.fd:.1f} kg/cm²")
    passaggi.append(f"h₀ = ψ×h = {inp.psi}×{inp.h:.0f} = {h0:.0f} cm")

    fd_ridotto = 0.85 * inp.fd
    if fd_ridotto > 0 and h0 > 0 and sigma_0 > 0:
        rapporto = sigma_0 / fd_ridotto
        rapporto = min(rapporto, 1.0)  # non può superare 1
        V_Rd = (inp.L ** 2 * inp.t * sigma_0) / (2 * h0) * (1 - rapporto)
    else:
        V_Rd = 0.0

    sfruttamento = abs(inp.V) / V_Rd if V_Rd > 0 else float("inf")
    verificato = abs(inp.V) <= V_Rd

    passaggi.append(
        f"V_pf = (L²×t×σ₀)/(2h₀)×(1-σ₀/(0.85fd)) = "
        f"({inp.L:.0f}²×{inp.t:.0f}×{sigma_0:.2f})/(2×{h0:.0f})×(1-{sigma_0:.2f}/{fd_ridotto:.1f})"
    )
    passaggi.append(f"V_pf = {V_Rd:.0f} kg")
    passaggi.append(
        f"|V| = {abs(inp.V):.0f} {'≤' if verificato else '>'} V_pf = {V_Rd:.0f} "
        f"→ {'OK' if verificato else 'NON VERIFICATO'} (sfruttamento {sfruttamento:.1%})"
    )

    return RisultatoTaglio(
        criterio="pressoflessione",
        V=abs(inp.V), V_Rd=V_Rd, sigma_0=sigma_0,
        sfruttamento=sfruttamento, verificato=verificato,
        passaggi=passaggi,
    )


def verifica_taglio_piano(inp: InputTaglio) -> list[RisultatoTaglio]:
    """Esegue tutte e tre le verifiche a taglio e ritorna la più restrittiva.

    Returns:
        Lista di 3 risultati (diagonale, scorrimento, pressoflessione)
        ordinati per V_Rd crescente (il primo è il più critico).
    """
    risultati = []

    if inp.tau_0 > 0:
        risultati.append(taglio_diagonale(inp))

    if inp.fvk0 > 0:
        risultati.append(taglio_scorrimento(inp))

    if inp.fd > 0 and inp.N > 0:
        risultati.append(taglio_pressoflessione(inp))

    return sorted(risultati, key=lambda r: r.V_Rd)


# ═══════════════════════════════════════════════════════════
#  E.4 — Spanciamento (verifica snellezza)
# ═══════════════════════════════════════════════════════════

@dataclass
class InputSpanciamento:
    """Input verifica spanciamento (instabilità fuori piano)."""
    h: float                     # altezza parete [cm]
    t: float                     # spessore parete [cm]
    rho: float = 1.0             # fattore vincolo
    lambda_max: float = 20.0     # snellezza massima ammissibile


@dataclass
class RisultatoSpanciamento:
    """Risultato verifica spanciamento."""
    h_eff: float                 # altezza efficace [cm]
    t: float                     # spessore [cm]
    lam: float                   # snellezza λ = h_eff/t
    lam_max: float               # limite snellezza
    verificato: bool
    passaggi: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "h_eff": round(self.h_eff, 1),
            "t": round(self.t, 1),
            "lambda": round(self.lam, 1),
            "lambda_max": round(self.lam_max, 1),
            "verificato": self.verificato,
            "passaggi": self.passaggi,
        }


def verifica_spanciamento(inp: InputSpanciamento) -> RisultatoSpanciamento:
    """Verifica di snellezza per spanciamento fuori piano.

    NTC2018 §4.5.6.2:
    λ = h_eff / t ≤ λ_max

    λ_max tipici:
    - 20 per muratura ordinaria (NTC2018)
    - 15 per muratura storica / esistente
    - 12 per muratura in zona sismica (NTC2018 §7.8.1.6)

    Args:
        inp: dati di input

    Returns:
        RisultatoSpanciamento
    """
    passaggi: list[str] = []

    h_eff = inp.rho * inp.h
    lam = h_eff / inp.t if inp.t > 0 else float("inf")
    verificato = lam <= inp.lambda_max

    passaggi.append("Verifica spanciamento (snellezza fuori piano)")
    passaggi.append(f"h_eff = ρ×h = {inp.rho}×{inp.h:.0f} = {h_eff:.0f} cm")
    passaggi.append(f"λ = h_eff/t = {h_eff:.0f}/{inp.t:.0f} = {lam:.1f}")
    passaggi.append(
        f"λ = {lam:.1f} {'≤' if verificato else '>'} λ_max = {inp.lambda_max:.0f} "
        f"→ {'OK' if verificato else 'NON VERIFICATO'}"
    )

    return RisultatoSpanciamento(
        h_eff=h_eff, t=inp.t, lam=lam, lam_max=inp.lambda_max,
        verificato=verificato, passaggi=passaggi,
    )
