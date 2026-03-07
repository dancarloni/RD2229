"""Meccanismi locali fuori piano muratura — analisi cinematica.

Analisi cinematica lineare e non lineare di meccanismi locali
di collasso per edifici in muratura secondo:
- NTC2018 §C8A.4 (Circolare n.7/2019)
- NTC2018 §7.8.1.5.2 (verifica elementi non strutturali)

Meccanismi implementati:
1. Ribaltamento semplice (parete ruota alla base)
2. Ribaltamento composto (parete + cuneo sovrastante)
3. Flessione verticale (cerniera a metà altezza)
4. Flessione orizzontale (arco orizzontale)

Unità: cm per geometria, kg per forze, kg/cm² per tensioni, cm/s² per accelerazioni.

Riferimenti:
- Circolare n.7/2019 §C8A.4.1 (cinematica lineare)
- Circolare n.7/2019 §C8A.4.2 (cinematica non lineare)
- D'Ayala & Speranza (2003): meccanismi per muratura storica
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Optional  # noqa: F401 (Optional usato nel file)

if TYPE_CHECKING:
    from src.codes.ntc2018.spectrum import CategoriaSuolo, CategoriaTopografica


G = 981.0  # accelerazione di gravità [cm/s²]


class TipoMeccanismo(str, Enum):
    """Tipo di meccanismo locale di collasso."""
    RIBALTAMENTO_SEMPLICE = "ribaltamento_semplice"
    RIBALTAMENTO_COMPOSTO = "ribaltamento_composto"
    FLESSIONE_VERTICALE = "flessione_verticale"
    FLESSIONE_ORIZZONTALE = "flessione_orizzontale"


class PosizioneParete(str, Enum):
    """Posizione della parete nell'edificio."""
    A_TERRA = "a_terra"          # base dell'edificio
    IN_QUOTA = "in_quota"        # piano intermedio o ultimo


# ═══════════════════════════════════════════════════════════
#  Input comune
# ═══════════════════════════════════════════════════════════

@dataclass
class PareteMuraria:
    """Geometria e proprietà parete per analisi cinematica."""
    h: float                     # altezza parete [cm]
    t: float                     # spessore parete [cm]
    L: float                     # lunghezza parete [cm]
    gamma: float = 0.0018        # peso specifico muratura [kg/cm³] (≈1800 kg/m³)

    # Sovraccarico in sommità
    N_sommita: float = 0.0       # carico verticale in sommità [kg/m lineare]

    # Posizione nell'edificio
    Z: float = 0.0               # quota della cerniera rispetto alla fondazione [cm]
    H_edificio: float = 0.0      # altezza totale edificio [cm]

    @property
    def peso_proprio(self) -> float:
        """Peso proprio della parete [kg]."""
        return self.h * self.t * self.L * self.gamma

    @property
    def peso_per_m(self) -> float:
        """Peso proprio per metro lineare [kg/m]."""
        return self.h * self.t * self.gamma * 100  # *100 per m

    @property
    def baricentro_h(self) -> float:
        """Altezza baricentro dal piede [cm]."""
        return self.h / 2.0


@dataclass
class ParametriSismici:
    """Parametri sismici per la verifica."""
    a_g: float = 0.0             # accelerazione al suolo a_g/g [adimensionale]
    S: float = 1.0               # coefficiente amplificazione stratigrafica S
    T1: float = 0.0              # primo periodo proprio dell'edificio [s]
    q: float = 2.0               # fattore di struttura per meccanismi locali
    FC: float = 1.35             # fattore di confidenza (LC1=1.35, LC2=1.20, LC3=1.00)

    # Per verifica in quota
    psi_Z: float = 0.0           # primo modo normalizzato alla quota Z
    gamma_modal: float = 1.0     # coefficiente di partecipazione modale

    # Per cinematica non lineare
    S_De_Ts: float = 0.0         # domanda di spostamento spettrale S_De(T_s) [cm]


def parametri_sismici_da_sito(
    ag_g: float,
    F0: float,
    TC_star: float,
    cat_suolo: "CategoriaSuolo",
    cat_topografica: "CategoriaTopografica",
    T1: float = 0.0,
    q: float = 2.0,
    FC: float = 1.35,
) -> "ParametriSismici":
    """Crea ParametriSismici calcolando S = SS * ST da spectrum.py.

    Evita che il chiamante debba calcolare SS e ST manualmente.
    Il dataclass ParametriSismici NON viene modificato.

    Args:
        ag_g:            accelerazione al suolo a_g/g [adimensionale]
        F0:              fattore di amplificazione spettrale
        TC_star:         periodo caratteristico TC* da griglia INGV [s]
        cat_suolo:       CategoriaSuolo (da src.codes.ntc2018.spectrum)
        cat_topografica: CategoriaTopografica (da src.codes.ntc2018.spectrum)
        T1:              periodo fondamentale edificio [s] (default 0.0)
        q:               fattore di struttura [adim.] (default 2.0)
        FC:              fattore di confidenza (default 1.35 = LC1)

    Returns:
        ParametriSismici con a_g=ag_g, S=SS*ST calcolato da sito.
        I campi psi_Z, gamma_modal, S_De_Ts devono essere impostati manualmente.
    """
    from src.codes.ntc2018.spectrum import calcola_SS, calcola_ST
    SS = calcola_SS(ag_g, F0, cat_suolo)
    ST = calcola_ST(cat_topografica)
    return ParametriSismici(a_g=ag_g, S=SS * ST, T1=T1, q=q, FC=FC)


@dataclass
class ForzaCatena:
    """Forza stabilizzante di una catena/tirante."""
    F: float = 0.0               # forza nella catena [kg]
    h_applicazione: float = 0.0  # quota di applicazione rispetto alla cerniera [cm]
    angolo: float = 0.0          # angolo rispetto all'orizzontale [gradi]


# ═══════════════════════════════════════════════════════════
#  Risultati
# ═══════════════════════════════════════════════════════════

@dataclass
class RisultatoCinematica:
    """Risultato analisi cinematica (lineare e/o non lineare)."""
    meccanismo: str = ""

    # Cinematica lineare
    alpha_0: float = 0.0          # moltiplicatore di collasso α₀
    M_star: float = 0.0           # massa partecipante M* [kg]
    e_star: float = 0.0           # frazione massa partecipante e*
    a_0_star: float = 0.0         # accelerazione spettrale a₀* [g]

    # Domanda sismica
    a_domanda: float = 0.0        # accelerazione di domanda [g]
    verifica_lineare: bool = False

    # Cinematica non lineare
    d_0_star: float = 0.0         # spostamento spettrale a₀=0 [cm]
    d_u_star: float = 0.0         # spostamento ultimo d*_u = 0.4·d*_0 [cm]
    d_domanda: float = 0.0        # domanda di spostamento [cm]
    verifica_non_lineare: bool = False

    # Dettaglio forze
    forze_stabilizzanti: float = 0.0   # momento stabilizzante [kg·cm]
    forze_ribaltanti: float = 0.0      # momento ribaltante [kg·cm]
    contributo_catene: float = 0.0     # momento stabilizzante catene [kg·cm]

    passaggi: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "meccanismo": self.meccanismo,
            "alpha_0": round(self.alpha_0, 4),
            "M_star": round(self.M_star, 1),
            "e_star": round(self.e_star, 4),
            "a_0_star": round(self.a_0_star, 4),
            "a_domanda": round(self.a_domanda, 4),
            "verifica_lineare": self.verifica_lineare,
            "d_u_star": round(self.d_u_star, 3),
            "d_domanda": round(self.d_domanda, 3),
            "verifica_non_lineare": self.verifica_non_lineare,
            "passaggi": self.passaggi,
        }


# ═══════════════════════════════════════════════════════════
#  1. Ribaltamento semplice
# ═══════════════════════════════════════════════════════════

def ribaltamento_semplice(
    parete: PareteMuraria,
    sismica: ParametriSismici,
    catene: list[ForzaCatena] | None = None,
) -> RisultatoCinematica:
    """Meccanismo di ribaltamento semplice — parete che ruota alla base.

    Circolare n.7/2019 §C8A.4.1:
    α₀ = (M_stabilizzante - M_catene_vert) / M_ribaltante

    Stabilizzante: W × t/2 + N_s × t/2
    Ribaltante: α₀ × (W × h/2 + N_s × h)
    Catene: F_cat × h_cat (stabilizzante orizzontale)

    La cerniera è alla base della parete.
    """
    passaggi: list[str] = []
    passaggi.append("═══ RIBALTAMENTO SEMPLICE ═══")

    W = parete.peso_proprio
    h = parete.h
    t = parete.t
    N_s = parete.N_sommita * parete.L / 100  # kg/m → kg (su tutta la lunghezza)

    passaggi.append(f"Parete: h={h:.0f} cm, t={t:.0f} cm, L={parete.L:.0f} cm")
    passaggi.append(f"W (peso proprio) = {W:.0f} kg")
    passaggi.append(f"N_sommità = {N_s:.0f} kg")

    # Momento stabilizzante (rispetto alla cerniera alla base, bordo esterno)
    M_stab = W * t / 2 + N_s * t / 2

    # Momento ribaltante (forze d'inerzia × braccio verticale)
    # α₀ × (W × h/2 + N_s × h)
    M_rib_coeff = W * h / 2 + N_s * h

    # Contributo catene
    M_catene = 0.0
    if catene:
        for i, cat in enumerate(catene):
            F_oriz = cat.F * math.cos(math.radians(cat.angolo))
            M_cat_i = F_oriz * cat.h_applicazione
            M_catene += M_cat_i
            passaggi.append(
                f"Catena {i+1}: F={cat.F:.0f} kg, h={cat.h_applicazione:.0f} cm, "
                f"M_cat = {M_cat_i:.0f} kg·cm"
            )

    passaggi.append(f"M_stabilizzante = W×t/2 + N_s×t/2 = {M_stab:.0f} kg·cm")
    passaggi.append(f"M_ribaltante (coeff.) = W×h/2 + N_s×h = {M_rib_coeff:.0f} kg·cm")
    if M_catene > 0:
        passaggi.append(f"M_catene (stabilizzante) = {M_catene:.0f} kg·cm")

    # α₀ = (M_stab + M_catene) / M_rib_coeff
    alpha_0 = (M_stab + M_catene) / M_rib_coeff if M_rib_coeff > 0 else 0.0
    passaggi.append(f"α₀ = (M_stab + M_catene) / M_rib = {alpha_0:.4f}")

    # Cinematica lineare
    res = _cinematica_lineare(alpha_0, parete, sismica, passaggi)
    res.meccanismo = TipoMeccanismo.RIBALTAMENTO_SEMPLICE.value
    res.forze_stabilizzanti = M_stab
    res.forze_ribaltanti = M_rib_coeff
    res.contributo_catene = M_catene

    # Cinematica non lineare
    _cinematica_non_lineare(alpha_0, parete, sismica, res, passaggi)

    res.passaggi = passaggi
    return res


# ═══════════════════════════════════════════════════════════
#  2. Ribaltamento composto
# ═══════════════════════════════════════════════════════════

def ribaltamento_composto(
    parete: PareteMuraria,
    cuneo_h: float,
    cuneo_angolo: float = 45.0,
    sismica: ParametriSismici = ParametriSismici(),
    catene: list[ForzaCatena] | None = None,
) -> RisultatoCinematica:
    """Meccanismo di ribaltamento composto — parete + cuneo muratura.

    Il cuneo è un triangolo di muratura che si forma sopra la parete
    per effetto dell'ingranamento dei blocchi.

    Args:
        parete: geometria parete
        cuneo_h: altezza del cuneo sovrastante [cm]
        cuneo_angolo: angolo del cuneo [gradi] (45° tipico)
        sismica: parametri sismici
        catene: eventuali catene stabilizzanti
    """
    passaggi: list[str] = []
    passaggi.append("═══ RIBALTAMENTO COMPOSTO ═══")

    W = parete.peso_proprio
    h = parete.h
    t = parete.t
    N_s = parete.N_sommita * parete.L / 100

    # Peso cuneo triangolare
    L_cuneo = cuneo_h / math.tan(math.radians(cuneo_angolo))
    W_cuneo = 0.5 * cuneo_h * L_cuneo * t * parete.gamma
    # Baricentro cuneo: a 1/3 dall'alto, 2/3 dalla base del cuneo
    h_bar_cuneo = h + cuneo_h / 3  # dal piede della parete
    d_bar_cuneo = t / 2 + L_cuneo / 3  # dal bordo esterno

    passaggi.append(f"Cuneo: h={cuneo_h:.0f} cm, angolo={cuneo_angolo:.0f}°")
    passaggi.append(f"W_cuneo = {W_cuneo:.0f} kg, h_bar={h_bar_cuneo:.0f} cm")

    # Momento stabilizzante
    M_stab = W * t / 2 + N_s * t / 2 + W_cuneo * d_bar_cuneo

    # Momento ribaltante
    M_rib_coeff = W * h / 2 + N_s * h + W_cuneo * h_bar_cuneo

    # Catene
    M_catene = 0.0
    if catene:
        for cat in catene:
            F_oriz = cat.F * math.cos(math.radians(cat.angolo))
            M_catene += F_oriz * cat.h_applicazione

    alpha_0 = (M_stab + M_catene) / M_rib_coeff if M_rib_coeff > 0 else 0.0

    passaggi.append(f"M_stab = {M_stab:.0f} kg·cm")
    passaggi.append(f"M_rib (coeff.) = {M_rib_coeff:.0f} kg·cm")
    passaggi.append(f"α₀ = {alpha_0:.4f}")

    res = _cinematica_lineare(alpha_0, parete, sismica, passaggi)
    res.meccanismo = TipoMeccanismo.RIBALTAMENTO_COMPOSTO.value
    res.forze_stabilizzanti = M_stab
    res.forze_ribaltanti = M_rib_coeff
    res.contributo_catene = M_catene

    _cinematica_non_lineare(alpha_0, parete, sismica, res, passaggi)

    res.passaggi = passaggi
    return res


# ═══════════════════════════════════════════════════════════
#  3. Flessione verticale
# ═══════════════════════════════════════════════════════════

def flessione_verticale(
    parete: PareteMuraria,
    h_cerniera: float | None = None,
    sismica: ParametriSismici = ParametriSismici(),
    catene: list[ForzaCatena] | None = None,
) -> RisultatoCinematica:
    """Meccanismo di flessione verticale — cerniera a metà altezza.

    La parete si divide in due parti con una cerniera intermedia.
    La parte superiore ruota rispetto alla cerniera.

    NTC2018 §C8A.4.1: meccanismo a due corpi.

    Args:
        parete: geometria parete
        h_cerniera: quota della cerniera intermedia [cm] (default h/2)
        sismica: parametri sismici
        catene: catene stabilizzanti
    """
    passaggi: list[str] = []
    passaggi.append("═══ FLESSIONE VERTICALE ═══")

    h = parete.h
    t = parete.t

    if h_cerniera is None:
        h_cerniera = h / 2

    h_inf = h_cerniera          # altezza parte inferiore
    h_sup = h - h_cerniera      # altezza parte superiore

    passaggi.append(f"Cerniera intermedia a h = {h_cerniera:.0f} cm")
    passaggi.append(f"Parte inferiore: h₁ = {h_inf:.0f} cm")
    passaggi.append(f"Parte superiore: h₂ = {h_sup:.0f} cm")

    # Pesi delle due parti
    W_inf = h_inf * t * parete.L * parete.gamma
    W_sup = h_sup * t * parete.L * parete.gamma
    N_s = parete.N_sommita * parete.L / 100

    passaggi.append(f"W_inf = {W_inf:.0f} kg, W_sup = {W_sup:.0f} kg")

    # Per la flessione verticale, consideriamo il meccanismo della parte superiore
    # che ruota rispetto alla cerniera intermedia.
    # La parte inferiore ruota in senso opposto.

    # Momento stabilizzante (gravità della parte superiore)
    M_stab = (W_sup * t / 2 + N_s * t / 2)

    # Momento ribaltante (forze inerziali)
    # La parte superiore ha baricentro a h_sup/2 dalla cerniera
    M_rib_coeff = W_sup * h_sup / 2 + N_s * h_sup

    # Catene
    M_catene = 0.0
    if catene:
        for cat in catene:
            # Solo catene sopra la cerniera contribuiscono
            if cat.h_applicazione > h_cerniera:
                h_rel = cat.h_applicazione - h_cerniera
                F_oriz = cat.F * math.cos(math.radians(cat.angolo))
                M_catene += F_oriz * h_rel
                passaggi.append(
                    f"Catena a h={cat.h_applicazione:.0f} → h_rel={h_rel:.0f}, "
                    f"M_cat = {F_oriz * h_rel:.0f} kg·cm"
                )

    alpha_0 = (M_stab + M_catene) / M_rib_coeff if M_rib_coeff > 0 else 0.0

    passaggi.append(f"M_stab = {M_stab:.0f} kg·cm, M_rib = {M_rib_coeff:.0f} kg·cm")
    passaggi.append(f"α₀ = {alpha_0:.4f}")

    res = _cinematica_lineare(alpha_0, parete, sismica, passaggi)
    res.meccanismo = TipoMeccanismo.FLESSIONE_VERTICALE.value
    res.forze_stabilizzanti = M_stab
    res.forze_ribaltanti = M_rib_coeff
    res.contributo_catene = M_catene

    # Per la non lineare, usiamo h_sup come altezza di riferimento
    parete_equiv = PareteMuraria(
        h=h_sup, t=t, L=parete.L, gamma=parete.gamma,
        N_sommita=parete.N_sommita,
        Z=parete.Z + h_cerniera,
        H_edificio=parete.H_edificio,
    )
    _cinematica_non_lineare(alpha_0, parete_equiv, sismica, res, passaggi)

    res.passaggi = passaggi
    return res


# ═══════════════════════════════════════════════════════════
#  4. Flessione orizzontale
# ═══════════════════════════════════════════════════════════

def flessione_orizzontale(
    parete: PareteMuraria,
    L_libera: float | None = None,
    sismica: ParametriSismici = ParametriSismici(),
    catene: list[ForzaCatena] | None = None,
) -> RisultatoCinematica:
    """Meccanismo di flessione orizzontale — arco orizzontale.

    La parete, vincolata lateralmente, si flette orizzontalmente
    formando un meccanismo ad arco tra i vincoli laterali.

    α₀ = (2 × t) / L_libera  (approssimazione ad arco a 3 cerniere)

    Args:
        parete: geometria parete
        L_libera: luce libera tra vincoli laterali [cm] (default = L)
        sismica: parametri sismici
        catene: catene stabilizzanti
    """
    passaggi: list[str] = []
    passaggi.append("═══ FLESSIONE ORIZZONTALE ═══")

    t = parete.t
    h = parete.h
    if L_libera is None:
        L_libera = parete.L

    passaggi.append(f"Parete: t={t:.0f} cm, L_libera={L_libera:.0f} cm")

    # Meccanismo ad arco a 3 cerniere
    # La spinta dell'arco è: H = q·L²/(8·f) dove f ≈ t/2
    # Il collasso avviene quando la cerniera raggiunge il bordo
    # α₀ = 2t / L_libera (formula semplificata)
    alpha_0_base = 2 * t / L_libera if L_libera > 0 else 0.0

    # Peso della parete per metro lineare
    W = parete.peso_proprio

    # Catene
    M_catene = 0.0
    if catene:
        for cat in catene:
            F_oriz = cat.F * math.cos(math.radians(cat.angolo))
            M_catene += F_oriz * cat.h_applicazione

    # Con catene: le catene confinano lateralmente e aumentano α₀
    if M_catene > 0 and W > 0:
        # Contributo catene: incremento proporzionale
        alpha_0 = alpha_0_base + M_catene / (W * h / 2)
    else:
        alpha_0 = alpha_0_base

    passaggi.append(f"α₀ (arco) = 2t/L = 2×{t:.0f}/{L_libera:.0f} = {alpha_0_base:.4f}")
    if M_catene > 0:
        passaggi.append(f"α₀ (con catene) = {alpha_0:.4f}")

    res = _cinematica_lineare(alpha_0, parete, sismica, passaggi)
    res.meccanismo = TipoMeccanismo.FLESSIONE_ORIZZONTALE.value
    res.contributo_catene = M_catene

    _cinematica_non_lineare(alpha_0, parete, sismica, res, passaggi)

    res.passaggi = passaggi
    return res


# ═══════════════════════════════════════════════════════════
#  Cinematica lineare
# ═══════════════════════════════════════════════════════════

def _cinematica_lineare(
    alpha_0: float,
    parete: PareteMuraria,
    sismica: ParametriSismici,
    passaggi: list[str],
) -> RisultatoCinematica:
    """Cinematica lineare — Circolare n.7/2019 §C8A.4.1.

    a₀* = α₀ × g × ΣPᵢ / (M* × FC)

    Verifica a terra: a₀* ≥ a_g × S / q
    Verifica in quota: a₀* ≥ S_e(T₁) × ψ(Z) × γ / q
    """
    passaggi.append("--- Cinematica lineare ---")

    W = parete.peso_proprio
    N_s = parete.N_sommita * parete.L / 100

    # Massa partecipante M* (approssimazione: massa totale del meccanismo)
    # Per ribaltamento semplice: M* ≈ W + N_s (se spostamento lineare)
    P_tot = W + N_s  # peso totale coinvolto
    M_star = P_tot / G  # massa [kg·s²/cm]

    # Frazione massa partecipante e*
    # e* = M* × g / ΣPᵢ (per meccanismo a un grado di libertà ≈ 1.0)
    # Approssimazione: per ribaltamento semplice con distribuzione lineare
    # degli spostamenti, e* ≈ 0.75 (Circ. §C8A.4.1)
    e_star = 0.75  # valore conservativo tipico

    # Accelerazione spettrale a₀*
    # a₀* = α₀ × g / (e* × FC)   — dove g cancella con M*
    a_0_star = alpha_0 / (e_star * sismica.FC) if (e_star * sismica.FC) > 0 else 0.0

    passaggi.append(f"P_tot = W + N_s = {P_tot:.0f} kg")
    passaggi.append(f"M* = P/g = {M_star:.2f} kg·s²/cm")
    passaggi.append(f"e* = {e_star:.2f}")
    passaggi.append(f"a₀* = α₀/(e*×FC) = {alpha_0:.4f}/({e_star}×{sismica.FC}) = {a_0_star:.4f} g")

    # Domanda sismica
    if parete.Z <= 0 or parete.H_edificio <= 0:
        # Verifica a terra (§C8A.4.1, eq. C8A.4.1)
        a_domanda = sismica.a_g * sismica.S / sismica.q
        passaggi.append(f"Verifica A TERRA: a_domanda = a_g×S/q = {sismica.a_g}×{sismica.S}/{sismica.q} = {a_domanda:.4f} g")
    else:
        # Verifica in quota (§C8A.4.1, eq. C8A.4.2)
        # ψ(Z) = Z/H per primo modo lineare
        psi_Z = parete.Z / parete.H_edificio if parete.H_edificio > 0 else 0
        # S_e(T₁) approssimato come a_g × S × η × F₀ (semplificazione)
        S_e_T1 = sismica.a_g * sismica.S * 2.5  # F₀ ≈ 2.5 plateau spettrale
        a_domanda = S_e_T1 * psi_Z * sismica.gamma_modal / sismica.q
        passaggi.append(
            f"Verifica IN QUOTA: Z={parete.Z:.0f} cm, H={parete.H_edificio:.0f} cm, "
            f"ψ(Z)={psi_Z:.3f}"
        )
        passaggi.append(f"a_domanda = S_e×ψ×γ/q = {a_domanda:.4f} g")

    verifica = a_0_star >= a_domanda

    passaggi.append(
        f"a₀* = {a_0_star:.4f} {'≥' if verifica else '<'} a_domanda = {a_domanda:.4f} "
        f"→ {'VERIFICATO' if verifica else 'NON VERIFICATO'}"
    )

    return RisultatoCinematica(
        alpha_0=alpha_0,
        M_star=M_star * G,  # riconvertito in kg
        e_star=e_star,
        a_0_star=a_0_star,
        a_domanda=a_domanda,
        verifica_lineare=verifica,
    )


# ═══════════════════════════════════════════════════════════
#  Cinematica non lineare
# ═══════════════════════════════════════════════════════════

def _cinematica_non_lineare(
    alpha_0: float,
    parete: PareteMuraria,
    sismica: ParametriSismici,
    res: RisultatoCinematica,
    passaggi: list[str],
) -> None:
    """Cinematica non lineare — Circolare n.7/2019 §C8A.4.2.

    Curva di capacità a*-d*:
    - a*(d=0) = a₀*
    - d*(a=0) = d₀*
    - d*_u = 0.4 × d₀*

    Verifica: d*_u ≥ S_De(T_s) oppure d*_u ≥ domanda spostamento
    """
    passaggi.append("--- Cinematica non lineare ---")

    h = parete.h
    t = parete.t

    # Spostamento d₀* al collasso (α₀ = 0)
    # Per ribaltamento semplice: d₀ = t (la parete ruota finché il
    # baricentro supera il bordo)
    # In termini spettrali: d₀* = d_k / (e* × Σδ²ₓ,ᵢ)
    # Approssimazione: d₀* ≈ t × (2/3) per distribuzione lineare spostamenti
    d_0_star = t * 2 / 3

    # Spostamento ultimo (40% del collasso per sicurezza)
    d_u_star = 0.4 * d_0_star

    passaggi.append(f"d₀* = t × 2/3 = {t:.0f} × 0.667 = {d_0_star:.2f} cm")
    passaggi.append(f"d*_u = 0.4 × d₀* = 0.4 × {d_0_star:.2f} = {d_u_star:.2f} cm")

    # Periodo secante T_s
    # T_s = 2π × √(d₀* / (a₀* × g)) con a₀* in cm/s²
    a_0_star_cms2 = res.a_0_star * G  # da g a cm/s²
    if a_0_star_cms2 > 0 and d_0_star > 0:
        T_s = 2 * math.pi * math.sqrt(d_0_star / a_0_star_cms2)
    else:
        T_s = 0.0

    passaggi.append(f"T_s = 2π√(d₀*/a₀*) = {T_s:.3f} s")

    # Domanda di spostamento
    # S_De(T_s) = S_De fornito dall'utente, oppure stima
    if sismica.S_De_Ts > 0:
        d_domanda = sismica.S_De_Ts
    else:
        # Stima: S_De = S_D1 × T_s / (4π²) con S_D1 ≈ a_g × S × 2.5
        # In realtà S_De(T) = a_g × S × η × T_C × T_D / (4π²) per T > T_D
        # Approssimazione semplificata
        S_D1 = sismica.a_g * sismica.S * G * 2.5  # cm/s²
        d_domanda = S_D1 * T_s ** 2 / (4 * math.pi ** 2) if T_s > 0 else 0.0

    # Per verifica in quota:
    if parete.Z > 0 and parete.H_edificio > 0:
        psi_Z = parete.Z / parete.H_edificio
        d_domanda *= psi_Z  # riduzione per quota

    res.d_0_star = d_0_star
    res.d_u_star = d_u_star
    res.d_domanda = d_domanda
    res.verifica_non_lineare = d_u_star >= d_domanda

    passaggi.append(f"d_domanda = {d_domanda:.3f} cm")
    passaggi.append(
        f"d*_u = {d_u_star:.3f} {'≥' if res.verifica_non_lineare else '<'} "
        f"d_domanda = {d_domanda:.3f} → "
        f"{'VERIFICATO' if res.verifica_non_lineare else 'NON VERIFICATO'}"
    )


# ═══════════════════════════════════════════════════════════
#  Funzione di analisi completa
# ═══════════════════════════════════════════════════════════

def analisi_meccanismi_locali(
    parete: PareteMuraria,
    sismica: ParametriSismici,
    catene: list[ForzaCatena] | None = None,
    cuneo_h: float = 0.0,
    cuneo_angolo: float = 45.0,
    h_cerniera: float | None = None,
    L_libera: float | None = None,
) -> list[RisultatoCinematica]:
    """Esegue tutti e 4 i meccanismi e ritorna risultati ordinati per α₀.

    Returns:
        Lista di risultati ordinata per α₀ crescente (il primo è il più critico).
    """
    risultati: list[RisultatoCinematica] = []

    # 1. Ribaltamento semplice (sempre)
    risultati.append(ribaltamento_semplice(parete, sismica, catene))

    # 2. Ribaltamento composto (se cuneo specificato)
    if cuneo_h > 0:
        risultati.append(ribaltamento_composto(parete, cuneo_h, cuneo_angolo, sismica, catene))

    # 3. Flessione verticale (sempre)
    risultati.append(flessione_verticale(parete, h_cerniera, sismica, catene))

    # 4. Flessione orizzontale (sempre)
    risultati.append(flessione_orizzontale(parete, L_libera, sismica, catene))

    return sorted(risultati, key=lambda r: r.alpha_0)
