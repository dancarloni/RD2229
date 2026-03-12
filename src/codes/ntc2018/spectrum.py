"""Calcolo spettro di risposta NTC2018 §3.2.3.

Catena completa dal sito ai parametri spettrali pronti per le verifiche:
  cat_suolo + cat_topografica + hazard (ag, F0, TC*)
    -> SS, ST, S, CC, TB, TC, TD, alpha_S, Se(T), Sd(T), S_d(T_1)

Unita' interne:
  ag   in [g] (adimensionale, es. 0.168)
  Se   in [m/s^2]
  S_d  in [m]
  T    in [s]

Riferimenti normativi:
  NTC2018 §3.2.3   — Azione sismica: spettro di risposta
  NTC2018 Tab. 3.2.IV — Coefficiente CC per categoria suolo
  NTC2018 Tab. 3.2.V  — Coefficiente SS per categoria suolo
  NTC2018 Tab. 3.2.VI — Coefficiente ST per categoria topografica
  NTC2018 Tab. 2.4.II — Coefficiente Cu per classe d'uso
  NTC2018 §2.4.1   — Vita di riferimento VR = VN * Cu
"""

from __future__ import annotations

import math
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .spectrum_paste_service import Ntc2018HazardRow


# ---------------------------------------------------------------------------
# Enumerazioni NTC2018
# ---------------------------------------------------------------------------


class CategoriaSuolo(Enum):
    """Categoria di sottosuolo NTC2018 Tab. 3.2.II."""

    A = "A"  # Roccia o terreni molto rigidi
    B = "B"  # Rocce tenere, depositi molto addensati
    C = "C"  # Depositi di sabbie o ghiaie mediamente addensate
    D = "D"  # Depositi di terreni coesivi molli
    E = "E"  # Profilo con strati superficiali alluvionali su roccia


class CategoriaTopografica(Enum):
    """Categoria topografica NTC2018 Tab. 3.2.VI."""

    T1 = "T1"  # Superficie pianeggiante, pendii <= 15deg; ST = 1.0
    T2 = "T2"  # Pendii > 15deg; ST = 1.2
    T3 = "T3"  # Rilievi isolati, inclinazione 15-30deg; ST = 1.2
    T4 = "T4"  # Rilievi isolati, inclinazione > 30deg; ST = 1.4


class ClasseUso(Enum):
    """Classe d'uso NTC2018 Tab. 2.4.II."""

    I = "I"  # noqa: E741 — nome normativo NTC2018; Agricole/industriali; Cu = 0.7
    II = "II"  # Edifici ordinari; Cu = 1.0
    III = "III"  # Affollamento significativo; Cu = 1.5
    IV = "IV"  # Funzioni pubbliche essenziali; Cu = 2.0


# ---------------------------------------------------------------------------
# Costanti
# ---------------------------------------------------------------------------

_CU: dict[ClasseUso, float] = {
    ClasseUso.I: 0.7,
    ClasseUso.II: 1.0,
    ClasseUso.III: 1.5,
    ClasseUso.IV: 2.0,
}

_ST: dict[CategoriaTopografica, float] = {
    CategoriaTopografica.T1: 1.0,
    CategoriaTopografica.T2: 1.2,
    CategoriaTopografica.T3: 1.2,
    CategoriaTopografica.T4: 1.4,
}

# Coefficiente CC: formula power-law (esponente, fattore).
# CC = fattore * tc_star ^ esponente  (NTC2018 Tab. 3.2.IV)
_CC_PARAMS: dict[CategoriaSuolo, tuple[float, float]] = {
    CategoriaSuolo.A: (0.00, 1.000),  # 1.0 costante
    CategoriaSuolo.B: (-0.20, 1.100),  # 1.1  * tc*^(-0.20)
    CategoriaSuolo.C: (-0.33, 1.050),  # 1.05 * tc*^(-0.33)
    CategoriaSuolo.D: (-0.50, 1.250),  # 1.25 * tc*^(-0.50)
    CategoriaSuolo.E: (-0.40, 1.150),  # 1.15 * tc*^(-0.40)
}

# Parametri SS Tab. 3.2.V: (soglia_ag_g, cap_oltre_soglia, a0, a1)
# Formula se ag_g <= soglia: SS = a0 + a1 * (F0 * ag_g - 0.22)
# Cap se ag_g > soglia:      SS = cap
_SS_PARAMS: dict[CategoriaSuolo, tuple[float, float, float, float]] = {
    CategoriaSuolo.A: (99.0, 1.0, 1.0, 0.00),
    CategoriaSuolo.B: (0.25, 1.0, 1.0, 0.40),
    CategoriaSuolo.C: (0.25, 1.5, 1.0, 0.50),
    CategoriaSuolo.D: (0.35, 1.8, 0.9, 0.90),
    CategoriaSuolo.E: (0.20, 1.6, 1.0, 0.60),
}

_G = 9.81  # m/s^2


# ---------------------------------------------------------------------------
# Vita di riferimento
# ---------------------------------------------------------------------------


def calcola_VR(vita_nominale: int, classe_uso: ClasseUso) -> int:
    """Vita di riferimento VR = VN * Cu (NTC2018 §2.4.1).

    NTC2018 prescrive VR >= 35 anni.

    Args:
        vita_nominale: vita nominale della struttura [anni].
        classe_uso: classe d'uso dell'edificio.

    Returns:
        Vita di riferimento VR [anni] (intero, minimo 35).
    """
    cu = _CU[classe_uso]
    vr = int(vita_nominale * cu)
    return max(vr, 35)


# ---------------------------------------------------------------------------
# Coefficienti di sito
# ---------------------------------------------------------------------------


def calcola_CC(cat_suolo: CategoriaSuolo, tc_star: float) -> float:
    """Coefficiente CC da categoria suolo e TC* (NTC2018 Tab. 3.2.IV).

    Formula power-law:
      A: 1.0  |  B: 1.1*TC*^-0.20  |  C: 1.05*TC*^-0.33
      D: 1.25*TC*^-0.50  |  E: 1.15*TC*^-0.40

    Args:
        cat_suolo: categoria di sottosuolo.
        tc_star: periodo caratteristico TC* [s].

    Returns:
        Coefficiente CC (adimensionale).
    """
    if tc_star <= 0:
        raise ValueError(f"TC* deve essere > 0, ricevuto {tc_star}")
    esp, fatt = _CC_PARAMS[cat_suolo]
    return fatt * (tc_star**esp)


def calcola_SS(ag_g: float, F0: float, cat_suolo: CategoriaSuolo) -> float:
    """Coefficiente di amplificazione stratigrafica SS (NTC2018 Tab. 3.2.V).

    Metodo a 1 iterazione: condizione valutata con SS_0 = 1.0,
    poi calcolo del valore finale.

    Args:
        ag_g: accelerazione al suolo a_g/g [adimensionale].
        F0: fattore di amplificazione spettrale.
        cat_suolo: categoria di sottosuolo.

    Returns:
        Coefficiente SS (adimensionale).
    """
    soglia, cap, a0, a1 = _SS_PARAMS[cat_suolo]

    # Prima iterazione: condizione su ag_g * SS_0 con SS_0 = 1.0
    if ag_g <= soglia:
        ss = a0 + a1 * (F0 * ag_g - 0.22)
        # Seconda iterazione: verifica che ag_g * ss non superi la soglia
        if ag_g * ss > soglia:
            ss = cap
    else:
        ss = cap

    # Categoria D: SS puo' essere < 1 per ag molto basso (es. 0.05g)
    # Altre categorie: fisicamente SS >= 1.0
    if cat_suolo != CategoriaSuolo.D:
        ss = max(ss, 1.0)

    return ss


def calcola_ST(cat_topografica: CategoriaTopografica) -> float:
    """Coefficiente topografico ST (NTC2018 Tab. 3.2.VI).

    T1=1.0, T2=1.2, T3=1.2, T4=1.4.

    Args:
        cat_topografica: categoria topografica.

    Returns:
        Coefficiente ST (adimensionale).
    """
    return _ST[cat_topografica]


# ---------------------------------------------------------------------------
# Periodi caratteristici
# ---------------------------------------------------------------------------


def calcola_periodi(TC_star: float, CC: float, ag_g: float) -> tuple[float, float, float]:
    """Calcola i periodi caratteristici TB, TC, TD dello spettro.

    TC = CC * TC*
    TB = TC / 3
    TD = 4 * ag_g + 1.6  (NTC2018 eq. 3.2.5)

    Args:
        TC_star: periodo caratteristico da griglia INGV [s].
        CC: coefficiente di categoria (da calcola_CC).
        ag_g: accelerazione al suolo a_g/g [adimensionale].

    Returns:
        Tupla (TB, TC, TD) in secondi.
    """
    TC = CC * TC_star
    TB = TC / 3.0
    TD = 4.0 * ag_g + 1.6
    return TB, TC, TD


# ---------------------------------------------------------------------------
# Accelerazione spettrale di piano
# ---------------------------------------------------------------------------


def calcola_alpha_S(ag_g: float, SS: float, ST: float) -> float:
    """Calcola alpha_S = (ag/g) * SS * ST.

    Usato da spectral_acceleration_floor (NTC2018 eq. 7.2.5).

    Args:
        ag_g: accelerazione al suolo a_g/g [adimensionale].
        SS: coefficiente stratigrafico.
        ST: coefficiente topografico.

    Returns:
        alpha_S (adimensionale).
    """
    return ag_g * SS * ST


# ---------------------------------------------------------------------------
# Spettro elastico e di progetto
# ---------------------------------------------------------------------------


def spettro_elastico(
    ag_g: float,
    F0: float,
    SS: float,
    ST: float,
    TB: float,
    TC: float,
    TD: float,
    xi: float,
    T: float,
) -> float:
    """Spettro di risposta elastico orizzontale Se(T) — NTC2018 §3.2.3.2.1.

    4 rami (S = SS * ST, eta = sqrt(10/(5+xi)) >= 0.55, ag = ag_g * g):
      0 <= T < TB:  Se = ag*S * [1 + T/TB * (eta*F0 - 1)]
      TB <= T < TC: Se = ag*S * eta * F0
      TC <= T < TD: Se = ag*S * eta * F0 * (TC/T)
      T >= TD:      Se = ag*S * eta * F0 * (TC*TD/T^2)

    Args:
        ag_g: accelerazione al suolo a_g/g [adimensionale].
        F0: fattore di amplificazione spettrale.
        SS: coefficiente stratigrafico.
        ST: coefficiente topografico.
        TB, TC, TD: periodi caratteristici [s] (da calcola_periodi).
        xi: smorzamento viscoso [%].
        T: periodo di calcolo [s].

    Returns:
        Se(T) in [m/s^2].
    """
    if T < 0:
        raise ValueError(f"T deve essere >= 0, ricevuto {T}")

    S = SS * ST
    ag = ag_g * _G
    eta = max(math.sqrt(10.0 / (5.0 + xi)), 0.55)

    if T < TB:
        if TB == 0:
            Se = ag * S * eta * F0
        else:
            Se = ag * S * (1.0 + (T / TB) * (eta * F0 - 1.0))
    elif T < TC:
        Se = ag * S * eta * F0
    elif T < TD:
        Se = ag * S * eta * F0 * (TC / T)
    else:
        Se = ag * S * eta * F0 * (TC * TD / T**2)

    return Se


def spettro_progetto(
    ag_g: float,
    F0: float,
    SS: float,
    ST: float,
    TB: float,
    TC: float,
    TD: float,
    q: float,
    T: float,
) -> float:
    """Spettro di progetto Sd(T) = Se(T) / q (con smorzamento 5%).

    Args:
        q: fattore di comportamento strutturale.
        (altri parametri: vedi spettro_elastico)

    Returns:
        Sd(T) in [m/s^2].
    """
    if q <= 0:
        raise ValueError(f"q deve essere > 0, ricevuto {q}")
    return spettro_elastico(ag_g, F0, SS, ST, TB, TC, TD, 5.0, T) / q


def profilo_spettrale_completo(
    ag_g: float,
    F0: float,
    SS: float,
    ST: float,
    TB: float,
    TC: float,
    TD: float,
    xi: float = 5.0,
    T_max: float | None = None,
    n_punti: int = 200,
) -> list[tuple[float, float]]:
    """Profilo spettrale completo Se(T) per T in [0, T_max] — NTC2018 §3.2.3.2.1.

    Genera una lista di punti (T, Se) che copre tutti e 4 i rami dello spettro
    elastico orizzontale, con punti aggiuntivi sulle discontinuita' TB, TC, TD.

    Distribuzione punti:
      - 0 a TB:   n/5 punti  (ramo crescente)
      - TB a TC:  n/10 punti (plateau)
      - TC a TD:  n/3 punti  (ramo decrescente 1/T)
      - TD a T_max: n/3 punti (ramo decrescente 1/T^2)
      - Punti esatti: 0, TB, TC, TD, T_max

    Args:
        ag_g: accelerazione al suolo a_g/g [adimensionale].
        F0: fattore di amplificazione spettrale.
        SS: coefficiente stratigrafico.
        ST: coefficiente topografico.
        TB, TC, TD: periodi caratteristici [s] (da calcola_periodi).
        xi: smorzamento viscoso [%] (default 5.0).
        T_max: periodo massimo [s] (default: max(4.0, 2*TD)).
        n_punti: numero totale di punti (default 200).

    Returns:
        Lista di tuple (T [s], Se [m/s^2]) ordinata per T crescente.
    """
    import numpy as _np

    if T_max is None:
        T_max = max(4.0, 2.0 * TD)

    n = max(n_punti, 20)

    # Costruzione punti T con densita' variabile per ciascun ramo
    n1 = max(4, n // 5)
    n2 = max(3, n // 10)
    n3 = max(n // 3, 10)
    n4 = max(n // 3, 10)

    t_ramo0 = _np.linspace(0.0, TB, n1, endpoint=False).tolist()
    t_ramo1 = _np.linspace(TB, TC, n2, endpoint=False).tolist()
    t_ramo2 = _np.linspace(TC, TD, n3, endpoint=False).tolist()
    t_ramo3 = _np.linspace(TD, T_max, n4).tolist()

    # Aggiungi punti esatti di transizione + T=0
    t_speciali = [0.0, TB, TC, TD, T_max]

    tutti = t_ramo0 + t_ramo1 + t_ramo2 + t_ramo3 + t_speciali
    t_all = sorted({round(t, 8) for t in tutti if 0.0 <= t <= T_max})

    return [(t, spettro_elastico(ag_g, F0, SS, ST, TB, TC, TD, xi, t)) for t in t_all]


def calcola_S_d_T1(
    T_1: float,
    ag_g: float,
    F0: float,
    SS: float,
    ST: float,
    TB: float,
    TC: float,
    TD: float,
    q: float,
) -> float:
    """Spostamento spettrale di progetto S_d(T_1) [m].

    S_d(T_1) = Sd(T_1) [m/s^2] * (T_1 / (2*pi))^2 [s^2]

    Utilizzato per il drift Metodo B (NTC2018 §7.2.3).

    Args:
        T_1: periodo fondamentale dell'edificio [s].
        (altri parametri: vedi spettro_progetto)

    Returns:
        S_d(T_1) in [m].
    """
    if T_1 <= 0:
        raise ValueError(f"T_1 deve essere > 0, ricevuto {T_1}")
    Sd = spettro_progetto(ag_g, F0, SS, ST, TB, TC, TD, q, T_1)
    return Sd * (T_1 / (2.0 * math.pi)) ** 2


# ---------------------------------------------------------------------------
# Funzione end-to-end
# ---------------------------------------------------------------------------


def spettro_da_hazard_row(
    row: Ntc2018HazardRow,
    cat_suolo: CategoriaSuolo,
    cat_topografica: CategoriaTopografica,
    xi: float = 5.0,
) -> dict:
    """Funzione end-to-end: HazardRow + sito -> dizionario spettrale completo.

    Args:
        row: riga di pericolosita' da spectrum_paste_service o ingv_hazard.
        cat_suolo: categoria di sottosuolo.
        cat_topografica: categoria topografica.
        xi: smorzamento viscoso [%] (default 5.0).

    Returns:
        Dizionario con chiavi:
          SS, ST, S, CC, TB, TC, TD, alpha_S,
          Se_func: callable(T) -> Se [m/s^2]
          Sd_func: callable(T, q=2.0) -> Sd [m/s^2]
          decision_log: list[str]
    """
    ag_g = row.ag_g
    F0 = row.f0
    TC_star = row.tc_star_s

    SS = calcola_SS(ag_g, F0, cat_suolo)
    ST = calcola_ST(cat_topografica)
    CC = calcola_CC(cat_suolo, TC_star)
    TB, TC, TD = calcola_periodi(TC_star, CC, ag_g)
    S = SS * ST
    alpha_S = calcola_alpha_S(ag_g, SS, ST)

    def Se_func(T: float) -> float:
        return spettro_elastico(ag_g, F0, SS, ST, TB, TC, TD, xi, T)

    def Sd_func(T: float, q: float = 2.0) -> float:
        return spettro_progetto(ag_g, F0, SS, ST, TB, TC, TD, q, T)

    decision_log = [
        f"ag_g={ag_g:.4f}g, F0={F0:.3f}, TC*={TC_star:.3f}s",
        f"cat. suolo={cat_suolo.value}: SS={SS:.4f}, "
        f"cat. topogr.={cat_topografica.value}: ST={ST:.1f}",
        f"CC={CC:.4f} -> TC={TC:.4f}s, TB={TB:.4f}s, TD={TD:.4f}s",
        f"S=SS*ST={S:.4f}, alpha_S=ag_g*S={alpha_S:.4f}",
    ]

    return {
        "SS": SS,
        "ST": ST,
        "S": S,
        "CC": CC,
        "TB": TB,
        "TC": TC,
        "TD": TD,
        "alpha_S": alpha_S,
        "Se_func": Se_func,
        "Sd_func": Sd_func,
        "decision_log": decision_log,
    }
