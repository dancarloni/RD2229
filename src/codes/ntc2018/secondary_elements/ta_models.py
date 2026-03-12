"""Modelli di stima del periodo fondamentale T_a per elementi secondari.

NTC2018 §7.2.3 richiede la conoscenza del periodo proprio dell'elemento
non strutturale T_a per calcolare l'accelerazione spettrale al piano S_a.

Modelli disponibili:
  * RIGID         — elemento rigido, T_a = 0 (nessuna amplificazione dinamica)
  * CANTILEVER_EQ — mensola equivalente, T_a = 2*pi*sqrt(m*H^3 / (3*E*I))
  * SDOF_EQ       — oscillatore semplice equivalente, T_a = 2*pi*sqrt(m/k)
  * MANUAL        — valore fornito dall'utente

Funzione aggiuntiva:
  * spectral_acceleration_floor — S_a al piano secondo NTC2018 eq. 7.2.5
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..spectrum import CategoriaSuolo, CategoriaTopografica


def estimate_ta(spec: dict[str, Any]) -> dict[str, Any]:
    """Stima il periodo fondamentale T_a dell'elemento secondario.

    Args:
        spec: dizionario con almeno ``ta_model`` e i parametri richiesti
              dal modello scelto.

    Returns:
        dict con chiavi:
            - T_a: periodo fondamentale [s]
            - ta_model: modello utilizzato
            - decision_log: lista passaggi di calcolo

    Raises:
        ValueError: se ta_model non e' riconosciuto o mancano parametri.
    """
    model = spec.get("ta_model", "").upper()
    decision_log: list[str] = []

    if model == "RIGID":
        T_a = _ta_rigid()
        decision_log.append("Modello RIGID: T_a = 0.0 s (elemento rigido)")

    elif model == "CANTILEVER_EQ":
        T_a = _ta_cantilever_eq(spec)
        decision_log.append(f"Modello CANTILEVER_EQ: T_a = 2*pi*sqrt(m*H^3/(3*E*I)) = {T_a:.4f} s")

    elif model == "SDOF_EQ":
        T_a = _ta_sdof_eq(spec)
        decision_log.append(f"Modello SDOF_EQ: T_a = 2*pi*sqrt(m/k) = {T_a:.4f} s")

    elif model == "MANUAL":
        T_a = _ta_manual(spec)
        decision_log.append(f"Modello MANUAL: T_a = {T_a:.4f} s (utente)")

    else:
        raise ValueError(
            f"ta_model '{spec.get('ta_model')}' non riconosciuto. "
            "Valori ammessi: RIGID, CANTILEVER_EQ, SDOF_EQ, MANUAL"
        )

    return {"T_a": T_a, "ta_model": model, "decision_log": decision_log}


def _ta_rigid() -> float:
    """Elemento rigido: T_a = 0."""
    return 0.0


def _ta_cantilever_eq(spec: dict[str, Any]) -> float:
    """Mensola equivalente: T_a = 2*pi*sqrt(m*H^3 / (3*E*I)).

    Parametri richiesti nello spec:
        massa_kg:   massa dell'elemento [kg]
        altezza_m:  altezza libera della mensola [m]
        E_Pa:       modulo elastico [Pa]
        I_m4:       momento d'inerzia della sezione [m^4]
    """
    m = _require_positive(spec, "massa_kg", "massa dell'elemento [kg]")
    H = _require_positive(spec, "altezza_m", "altezza mensola [m]")
    E = _require_positive(spec, "E_Pa", "modulo elastico [Pa]")
    I = _require_positive(spec, "I_m4", "momento d'inerzia [m^4]")

    return 2.0 * math.pi * math.sqrt(m * H**3 / (3.0 * E * I))


def _ta_sdof_eq(spec: dict[str, Any]) -> float:
    """Oscillatore semplice equivalente: T_a = 2*pi*sqrt(m/k).

    Parametri richiesti nello spec:
        massa_kg:       massa dell'elemento [kg]
        rigidezza_N_m:  rigidezza laterale [N/m]
    """
    m = _require_positive(spec, "massa_kg", "massa dell'elemento [kg]")
    k = _require_positive(spec, "rigidezza_N_m", "rigidezza laterale [N/m]")

    return 2.0 * math.pi * math.sqrt(m / k)


def _ta_manual(spec: dict[str, Any]) -> float:
    """Valore manuale dall'utente: T_a = spec['T_a_manual']."""
    val = spec.get("T_a_manual")
    if val is None:
        raise ValueError("T_a_manual richiesto per modello MANUAL")
    val = float(val)
    if val < 0:
        raise ValueError(f"T_a_manual deve essere >= 0, ricevuto {val}")
    return val


def spectral_acceleration_floor(
    z: float, H: float, T_a: float, T_1: float, alpha_S: float
) -> float:
    """Accelerazione spettrale al piano — NTC2018 eq. 7.2.5.

    S_a = alpha_S * max(3*(1 + z/H) / (1 + (1 - T_a/T_1)^2) - 0.5, 1.0)

    Args:
        z:       quota dell'elemento rispetto alla base [m]
        H:       altezza totale dell'edificio [m]
        T_a:     periodo fondamentale dell'elemento [s]
        T_1:     periodo fondamentale dell'edificio [s]
        alpha_S: prodotto alpha * S (da spettro elastico NTC2018)

    Returns:
        S_a: accelerazione spettrale adimensionale (rapporto a g)
    """
    if H <= 0:
        raise ValueError(f"H deve essere > 0, ricevuto {H}")
    if T_1 <= 0:
        raise ValueError(f"T_1 deve essere > 0, ricevuto {T_1}")
    if alpha_S < 0:
        raise ValueError(f"alpha_S deve essere >= 0, ricevuto {alpha_S}")

    ratio_z = z / H
    ratio_T = T_a / T_1

    amplification = 3.0 * (1.0 + ratio_z) / (1.0 + (1.0 - ratio_T) ** 2) - 0.5
    S_a = alpha_S * max(amplification, 1.0)

    return S_a


def spectral_acceleration_floor_from_site(
    z: float,
    H: float,
    T_a: float,
    T_1: float,
    ag_g: float,
    F0: float,
    TC_star: float,
    cat_suolo: CategoriaSuolo,
    cat_topografica: CategoriaTopografica,
) -> float:
    """Calcola S_a al piano computando alpha_S dai parametri di sito.

    Wrapper di spectral_acceleration_floor che riceve i parametri di sito
    invece di alpha_S pre-calcolato. Delega il calcolo di SS, ST, alpha_S
    al modulo spectrum.py.

    Args:
        z:               quota dell'elemento rispetto alla base [m]
        H:               altezza totale dell'edificio [m]
        T_a:             periodo fondamentale dell'elemento [s]
        T_1:             periodo fondamentale dell'edificio [s]
        ag_g:            accelerazione al suolo a_g/g [adimensionale]
        F0:              fattore di amplificazione spettrale
        TC_star:         periodo caratteristico TC* da griglia INGV [s]
        cat_suolo:       categoria di sottosuolo (CategoriaSuolo)
        cat_topografica: categoria topografica (CategoriaTopografica)

    Returns:
        S_a: accelerazione spettrale al piano (adimensionale, rapporto a g)
    """
    from ..spectrum import calcola_alpha_S, calcola_SS, calcola_ST  # lazy import

    SS = calcola_SS(ag_g, F0, cat_suolo)
    ST = calcola_ST(cat_topografica)
    alpha_S = calcola_alpha_S(ag_g, SS, ST)
    return spectral_acceleration_floor(z, H, T_a, T_1, alpha_S)


# ---------------------------------------------------------------------------
# Utilita' interne
# ---------------------------------------------------------------------------


def _require_positive(spec: dict[str, Any], key: str, label: str) -> float:
    """Estrae e valida un parametro positivo dallo spec."""
    val = spec.get(key)
    if val is None:
        raise ValueError(f"Parametro '{key}' ({label}) mancante nello spec")
    val = float(val)
    if val <= 0:
        raise ValueError(f"'{key}' ({label}) deve essere > 0, ricevuto {val}")
    return val
