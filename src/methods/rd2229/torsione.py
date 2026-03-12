"""
Verifica a torsione — Metodo Tensioni Ammissibili (RD 2229/39).

Traduzione da VB: Sub Torsione() (PrincipCA_TA.bas, riga 3818).

Calcola la tensione tangenziale massima τ_xz per torsione e confronta
con le tensioni ammissibili τ_c0 e τ_c1. Progetta o verifica l'armatura
a torsione longitudinale e trasversale.

Formule per sezione:
    Rettangolare:  Ψ = 3 + 2.6/(0.45 + a/b),  τ_max = Ψ·|Mx|/(a·b²)
    Circolare:     τ_max = 2·|Mx|·Re / (π·(Re⁴ - Ri⁴))
    T / T rovescia: τ_max = 3·|Mx|·b_max / (a1·b1³ + a2·b2³)
    Doppio T:      τ_max = 3·|Mx|·b_max / (2·a1·b1³ + a2·b2³)
    Scatolare:     τ_max = |Mx| / (2·Am·s_min)

Tre casi di verifica:
    1. τ_max ≤ τ_c0        → non occorre armatura specifica
    2. τ_c0 < τ_max ≤ τ_c1 → armatura a torsione necessaria
    3. τ_max > τ_c1         → riprogettare la sezione

Quando taglio è presente: τ_c1,t = τ_c1 × 1.1

Unità: kg/cm² per tensioni, cm per geometria, kg·cm per momenti torcenti.

Riferimenti:
    - RD 2229/39 art. 5, 6, 7
    - Santarella, "Il cemento armato", Vol. I, Cap. 7
    - Giangreco, "Teoria e Tecnica delle Costruzioni", Cap. 12
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class TipoSezione(str, Enum):
    """Tipi di sezione supportati per la verifica a torsione TA."""

    RETTANGOLARE = "Rettangolare"
    CIRCOLARE = "Circolare"
    T = "a T"
    T_ROVESCIA = "a T rovescia"
    DOPPIO_T = "a doppio T"
    SCATOLARE = "Scatolare"


class EsitoTorsione(str, Enum):
    """Esito della verifica a torsione."""

    NESSUNA_ARMATURA = "nessuna_armatura"  # τ ≤ τ_c0
    ARMATURA_NECESSARIA = "armatura_necessaria"  # τ_c0 < τ ≤ τ_c1
    SEZIONE_INSUFFICIENTE = "sezione_insufficiente"  # τ > τ_c1
    NESSUN_MOMENTO = "nessun_momento"  # Mx = 0
    SEZIONE_NON_SUPPORTATA = "sezione_non_supportata"


@dataclass
class InputTorsione:
    """Dati di input per la verifica a torsione TA.

    Geometria in cm, forze in kg, momenti in kg·cm, tensioni in kg/cm².
    """

    # Momento torcente
    Mx: float  # kg·cm

    # Tipo sezione
    tipo_sezione: TipoSezione

    # Tensioni ammissibili del calcestruzzo
    tau_c0: float  # kg/cm² — tensione tangenziale ammissibile senza armatura
    tau_c1: float  # kg/cm² — tensione tangenziale limite

    # Tensione ammissibile dell'acciaio
    sigma_s_adm: float  # kg/cm²

    # Geometria rettangolare / base per T e doppio T
    B: float = 0.0  # cm — larghezza (anima per T)
    H: float = 0.0  # cm — altezza totale

    # Geometria T
    Bo: float = 0.0  # cm — larghezza ala (flangia)
    S: float = 0.0  # cm — spessore ala (flangia)

    # Geometria circolare
    D: float = 0.0  # cm — diametro esterno
    Di: float = 0.0  # cm — diametro interno (0 per piena)

    # Geometria scatolare
    # S usato come spessore parete (s_min)

    # Copriferro e diametro barre
    copriferro: float = 3.0  # cm
    diametro_barra: float = 1.4  # cm (φ14)

    # Taglio concomitante (per interazione T+V)
    Ty: float = 0.0  # kg — taglio in y
    Tz: float = 0.0  # kg — taglio in z

    # Armatura a torsione (per verifica)
    Al_to: float = 0.0  # cm² — armatura longitudinale dedicata
    Asw_to: float = 0.0  # cm² — area braccio staffa dedicata
    Pst_to: float = 0.0  # cm — passo staffe dedicato

    # Angoli traliccio
    theta_to: float = math.pi / 4  # rad — inclinazione bielle cls (45°)
    alpha_to: float = math.pi / 2  # rad — inclinazione staffe (90°)


@dataclass
class RisultatoTorsione:
    """Risultato della verifica a torsione TA."""

    esito: EsitoTorsione
    tau_max: float = 0.0  # kg/cm² — tensione tangenziale massima
    tau_c0: float = 0.0  # kg/cm² — limite senza armatura
    tau_c1_t: float = 0.0  # kg/cm² — limite con interazione T+V
    psi: float = 0.0  # coefficiente di forma (rettangolare)

    # Geometria tubolare equivalente (per SLU truss model)
    A_k: float = 0.0  # cm² — area tubolare equivalente
    p_k: float = 0.0  # cm — perimetro tubolare equivalente

    # Armatura (progetto)
    Al_to: float = 0.0  # cm² — armatura longitudinale
    Pst_to: float = 0.0  # cm — passo staffe
    n_barre: int = 0  # numero barre longitudinali

    # Tensioni armatura (verifica)
    sigma_l: float = 0.0  # kg/cm² — tensione armatura longitudinale
    sigma_st: float = 0.0  # kg/cm² — tensione armatura trasversale
    verifica_soddisfatta: bool = False

    # Dettagli calcolo
    passaggi: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Serializza il risultato per report."""
        return {
            "esito": self.esito.value,
            "tau_max_kg_cm2": round(self.tau_max, 2),
            "tau_c0_kg_cm2": round(self.tau_c0, 2),
            "tau_c1_t_kg_cm2": round(self.tau_c1_t, 2),
            "psi": round(self.psi, 4),
            "A_k_cm2": round(self.A_k, 2),
            "p_k_cm": round(self.p_k, 2),
            "Al_to_cm2": round(self.Al_to, 2),
            "Pst_to_cm": round(self.Pst_to, 1),
            "n_barre": self.n_barre,
            "sigma_l_kg_cm2": round(self.sigma_l, 2),
            "sigma_st_kg_cm2": round(self.sigma_st, 2),
            "verifica_soddisfatta": self.verifica_soddisfatta,
            "passaggi": self.passaggi,
        }


def _delta(copriferro: float, diametro_barra: float) -> float:
    """Distanza asse barra dal bordo = copriferro + φ/2."""
    return copriferro + diametro_barra / 2.0


def calcola_tau_max_rettangolare(Mx: float, B: float, H: float) -> tuple[float, float]:
    """τ_max per sezione rettangolare piena.

    Ψ = 3 + 2.6 / (0.45 + a/b) dove a ≥ b.
    τ_max = Ψ · |Mx| / (a · b²)

    Returns:
        (tau_max, psi)
    """
    if B <= H:
        a, b = H, B
    else:
        a, b = B, H
    if b <= 0 or a <= 0:
        return 0.0, 0.0
    psi = 3.0 + 2.6 / (0.45 + a / b)
    tau_max = psi * abs(Mx) / (a * b**2)
    return tau_max, psi


def calcola_tau_max_circolare(Mx: float, D: float, Di: float = 0.0) -> float:
    """τ_max per sezione circolare piena o cava.

    τ_max = 2·|Mx|·Re / (π·(Re⁴ - Ri⁴))
    """
    Re = D / 2.0
    Ri = Di / 2.0
    denom = math.pi * (Re**4 - Ri**4)
    if denom <= 0:
        return 0.0
    return 2.0 * abs(Mx) * Re / denom


def calcola_tau_max_T(Mx: float, B: float, H: float, Bo: float, S: float) -> float:
    """τ_max per sezione a T o T rovescia.

    La sezione viene scomposta in due rettangoli:
        Rettangolo 1 (ala):  dimensioni B × S
        Rettangolo 2 (anima): dimensioni Bo × (H - S)

    Per ciascuno, a = max(dim), b = min(dim).
    τ_max = 3·|Mx|·b_max / (a1·b1³ + a2·b2³)
    """
    # Rettangolo 1 — ala
    if S <= B:
        a1, b1 = B, S
    else:
        a1, b1 = S, B

    # Rettangolo 2 — anima
    h_anima = H - S
    if Bo <= h_anima:
        a2, b2 = h_anima, Bo
    else:
        a2, b2 = Bo, h_anima

    b_max = max(b1, b2)
    denom = a1 * b1**3 + a2 * b2**3
    if denom <= 0:
        return 0.0
    return 3.0 * abs(Mx) * b_max / denom


def calcola_tau_max_doppio_T(Mx: float, B: float, H: float, Bo: float, S: float) -> float:
    """τ_max per sezione a doppio T (I).

    Come T ma con due ali: denom = 2·a1·b1³ + a2·b2³.
    """
    if S <= B:
        a1, b1 = B, S
    else:
        a1, b1 = S, B

    h_anima = H - 2 * S
    if Bo <= h_anima:
        a2, b2 = h_anima, Bo
    else:
        a2, b2 = Bo, h_anima

    b_max = max(b1, b2)
    denom = 2.0 * a1 * b1**3 + a2 * b2**3
    if denom <= 0:
        return 0.0
    return 3.0 * abs(Mx) * b_max / denom


def calcola_tau_max_scatolare(Mx: float, B: float, H: float, S: float) -> float:
    """τ_max per sezione scatolare (box).

    Am = (B - s)·(H - s), area racchiusa dalla linea mediana.
    s_min = S (spessore minimo parete).
    τ_max = |Mx| / (2·Am·s_min)
    """
    Am = (B - S) * (H - S)
    s_min = S
    if Am <= 0 or s_min <= 0:
        return 0.0
    return abs(Mx) / (2.0 * Am * s_min)


def _calcola_area_perimetro_tubolare(
    inp: InputTorsione,
) -> tuple[float, float]:
    """Calcola area A e perimetro p del tubolare resistente.

    Il tubolare è definito con bordo a distanza δ = copriferro + φ/2
    dal contorno esterno.
    """
    delta = _delta(inp.copriferro, inp.diametro_barra)

    if inp.tipo_sezione == TipoSezione.CIRCOLARE:
        D1 = inp.D - 2 * delta
        A = math.pi * D1**2 / 4.0
        p = math.pi * D1
    elif inp.tipo_sezione == TipoSezione.RETTANGOLARE:
        b1 = inp.B - 2 * delta
        H1 = inp.H - 2 * delta
        A = b1 * H1
        p = 2 * b1 + 2 * H1
    elif inp.tipo_sezione in (TipoSezione.T, TipoSezione.T_ROVESCIA):
        b1 = inp.B - 2 * delta
        s1 = inp.S - 2 * delta
        Bo1 = inp.Bo - 2 * delta
        A = b1 * s1 + Bo1 * (inp.H - inp.S)
        p = b1 + 2 * s1 + Bo1 + 2 * (inp.H - inp.S) + (inp.B - inp.Bo)
    elif inp.tipo_sezione == TipoSezione.DOPPIO_T:
        b1 = inp.B - 2 * delta
        s1 = inp.S - 2 * delta
        Bo1 = inp.Bo - 2 * delta
        A = 2 * b1 * s1 + Bo1 * (inp.H - 2 * inp.S + 2 * delta)
        p = 2 * b1 + 4 * s1 + 2 * (inp.H - 2 * inp.S + 2 * delta) + 2 * (inp.B - inp.Bo)
    elif inp.tipo_sezione == TipoSezione.SCATOLARE:
        b1 = inp.B - 2 * delta
        H1 = inp.H - 2 * delta
        A = b1 * H1
        p = 2 * b1 + 2 * H1
    else:
        A, p = 0.0, 0.0

    return max(A, 0.0), max(p, 0.0)


def verifica_torsione_ta(inp: InputTorsione, modo_verifica: bool = True) -> RisultatoTorsione:
    """Esegue la verifica (o il progetto) a torsione con il metodo TA.

    Args:
        inp: dati di input (geometria, sollecitazioni, materiali).
        modo_verifica: True = verifica armatura esistente,
                       False = progetto armatura necessaria.

    Returns:
        RisultatoTorsione con esito, tensioni, armature.
    """
    ris = RisultatoTorsione(esito=EsitoTorsione.NESSUN_MOMENTO)

    # Nessun momento torcente
    if abs(inp.Mx) < 1e-6:
        ris.passaggi.append("Mx = 0 → verifica a torsione non necessaria.")
        return ris

    # Sezione non supportata
    if inp.tipo_sezione == TipoSezione.SCATOLARE and (inp.B <= 0 or inp.H <= 0 or inp.S <= 0):
        ris.esito = EsitoTorsione.SEZIONE_NON_SUPPORTATA
        ris.passaggi.append("Geometria scatolare incompleta.")
        return ris

    # Interazione torsione + taglio: τ_c1,t = τ_c1 × 1.1
    ha_taglio = abs(inp.Ty) > 1e-6 or abs(inp.Tz) > 1e-6
    tau_c1_t = inp.tau_c1 * 1.1 if ha_taglio else inp.tau_c1
    ris.tau_c0 = inp.tau_c0
    ris.tau_c1_t = tau_c1_t

    # 1. Calcolo τ_max
    passaggi = ris.passaggi
    passaggi.append(f"Mx = {inp.Mx:.2f} kg·cm")
    if ha_taglio:
        passaggi.append(f"Interazione T+V: τ_c1,t = τ_c1 × 1.1 = {tau_c1_t:.2f} kg/cm²")

    tau_max = 0.0
    psi = 0.0

    if inp.tipo_sezione == TipoSezione.RETTANGOLARE:
        tau_max, psi = calcola_tau_max_rettangolare(inp.Mx, inp.B, inp.H)
        ris.psi = psi
        passaggi.append(
            f"Sez. rettangolare {inp.B:.1f}×{inp.H:.1f} cm: "
            f"Ψ = {psi:.4f}, τ_max = {tau_max:.2f} kg/cm²"
        )

    elif inp.tipo_sezione == TipoSezione.CIRCOLARE:
        tau_max = calcola_tau_max_circolare(inp.Mx, inp.D, inp.Di)
        passaggi.append(
            f"Sez. circolare D={inp.D:.1f} Di={inp.Di:.1f} cm: " f"τ_max = {tau_max:.2f} kg/cm²"
        )

    elif inp.tipo_sezione in (TipoSezione.T, TipoSezione.T_ROVESCIA):
        tau_max = calcola_tau_max_T(inp.Mx, inp.B, inp.H, inp.Bo, inp.S)
        passaggi.append(
            f"Sez. a T: B={inp.B:.1f} H={inp.H:.1f} Bo={inp.Bo:.1f} S={inp.S:.1f} cm: "
            f"τ_max = {tau_max:.2f} kg/cm²"
        )

    elif inp.tipo_sezione == TipoSezione.DOPPIO_T:
        tau_max = calcola_tau_max_doppio_T(inp.Mx, inp.B, inp.H, inp.Bo, inp.S)
        passaggi.append(
            f"Sez. a doppio T: B={inp.B:.1f} H={inp.H:.1f} Bo={inp.Bo:.1f} S={inp.S:.1f} cm: "
            f"τ_max = {tau_max:.2f} kg/cm²"
        )

    elif inp.tipo_sezione == TipoSezione.SCATOLARE:
        tau_max = calcola_tau_max_scatolare(inp.Mx, inp.B, inp.H, inp.S)
        passaggi.append(
            f"Sez. scatolare {inp.B:.1f}×{inp.H:.1f} s={inp.S:.1f} cm: "
            f"τ_max = {tau_max:.2f} kg/cm²"
        )

    else:
        ris.esito = EsitoTorsione.SEZIONE_NON_SUPPORTATA
        passaggi.append(f"Tipo sezione '{inp.tipo_sezione}' non supportato per torsione TA.")
        return ris

    ris.tau_max = tau_max

    # 2. Area e perimetro tubolare equivalente
    A_k, p_k = _calcola_area_perimetro_tubolare(inp)
    ris.A_k = A_k
    ris.p_k = p_k
    passaggi.append(f"Tubolare equivalente: A_k = {A_k:.2f} cm², p = {p_k:.2f} cm")

    # 3. Confronto con tensioni ammissibili
    if tau_max <= inp.tau_c0:
        ris.esito = EsitoTorsione.NESSUNA_ARMATURA
        ris.verifica_soddisfatta = True
        passaggi.append(
            f"τ_max = {tau_max:.2f} ≤ τ_c0 = {inp.tau_c0:.2f} kg/cm² → "
            "non occorre specifica armatura a torsione."
        )
        return ris

    if tau_max > tau_c1_t:
        ris.esito = EsitoTorsione.SEZIONE_INSUFFICIENTE
        ris.verifica_soddisfatta = False
        passaggi.append(
            f"τ_max = {tau_max:.2f} > τ_c1,t = {tau_c1_t:.2f} kg/cm² → "
            "occorre riprogettare la sezione."
        )
        return ris

    # τ_c0 < τ_max ≤ τ_c1 → armatura necessaria
    ris.esito = EsitoTorsione.ARMATURA_NECESSARIA
    passaggi.append(
        f"τ_c0 = {inp.tau_c0:.2f} < τ_max = {tau_max:.2f} ≤ τ_c1,t = {tau_c1_t:.2f} → "
        "occorre armatura a torsione."
    )

    abs_Mx = abs(inp.Mx)
    theta = inp.theta_to
    alpha = inp.alpha_to

    if modo_verifica and inp.Al_to > 0 and A_k > 0:
        # Verifica armatura esistente
        sigma_l = abs_Mx * p_k / (2.0 * A_k * inp.Al_to * math.tan(theta))
        ris.sigma_l = sigma_l
        passaggi.append(f"σ_l = |Mx|·p / (2·A·Al·tan θ) = {sigma_l:.2f} kg/cm²")

        if inp.Asw_to > 0 and inp.Pst_to > 0:
            sigma_st = (
                abs_Mx * inp.Pst_to / (2.0 * A_k * inp.Asw_to * math.sin(math.pi - theta - alpha))
            )
            ris.sigma_st = sigma_st
            passaggi.append(f"σ_st = |Mx|·p_st / (2·A·Asw·sin(π-θ-α)) = {sigma_st:.2f} kg/cm²")
        else:
            sigma_st = 0.0
            ris.sigma_st = 0.0

        if sigma_l <= inp.sigma_s_adm and sigma_st <= inp.sigma_s_adm:
            ris.verifica_soddisfatta = True
            passaggi.append("Verifica a torsione soddisfatta!")
        else:
            ris.verifica_soddisfatta = False
            passaggi.append(
                f"Verifica NON soddisfatta: σ_l={sigma_l:.2f}, "
                f"σ_st={sigma_st:.2f} > σ_s_adm={inp.sigma_s_adm:.2f} kg/cm²"
            )
    else:
        # Progetto armatura
        if A_k > 0 and inp.sigma_s_adm > 0:
            Al_to = abs_Mx * p_k / (2.0 * A_k * inp.sigma_s_adm * math.tan(theta))
            ris.Al_to = Al_to
            passaggi.append(f"Al progetto = |Mx|·p / (2·A·σ_adm·tan θ) = {Al_to:.2f} cm²")

            if inp.Asw_to > 0:
                Pst_to = (
                    2.0
                    * A_k
                    * inp.Asw_to
                    * inp.sigma_s_adm
                    * math.sin(math.pi - theta - alpha)
                    / abs_Mx
                )
                ris.Pst_to = Pst_to
                passaggi.append(f"Passo staffe progetto = {Pst_to:.1f} cm")

            # Numero barre
            Af1 = math.pi * inp.diametro_barra**2 / 4.0
            if Af1 > 0:
                n = Al_to / Af1
                ris.n_barre = math.ceil(n)
                passaggi.append(
                    f"n barre φ{inp.diametro_barra:.0f} = {ris.n_barre} "
                    f"(Al_eff = {ris.n_barre * Af1:.2f} cm²)"
                )
            ris.verifica_soddisfatta = True

    return ris
