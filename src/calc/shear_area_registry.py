"""
shear_area_registry.py

Questo modulo definisce:
- Il registry per il calcolo dell'area a taglio A_sx e A_sy,
  applicato a TUTTE le sezioni del software.
- Un sistema estensibile per aggiungere strategie di calcolo
  specifiche per tipologia di sezione.
- Fallback universale basato su kappa (metodo Timoshenko).
- Interfaccia coerente per integrarsi con il motore
  elementi → risoluzione input → verifiche strutturali.

UNITÀ di MISURA:
- Tutte le lunghezze devono essere considerate in cm.
- Le aree devono essere restituite in cm^2.
- Nessuna conversione implicita deve essere introdotta
  in questo modulo.

NOTE:
- Questo file è uno STUB S2: contiene docstring esaustive,
  TODO chiari, e struttura definita, ma NON implementazione
  di calcoli complessi.
- Continue / Copilot Plan aggiungerà la logica quando richiesto.
"""

from typing import Callable, Dict, Tuple, Optional, Any


# ======================================================================
# TIPOLOGIE DI ALIAS
# ======================================================================
ShearAreaFunction = Callable[[Any], Tuple[float, float]]
"""
Funzione che accetta un oggetto sezione (Section)
e restituisce una tupla:

    (A_sx_cm2: float, A_sy_cm2: float)

Unità: cm^2.
"""


# ======================================================================
# COSTANTI DI BASE (VALORI CLASSICI PER SEZIONI PIENE)
# ======================================================================

DEFAULT_KAPPA: float = 5.0 / 6.0
"""
Valore kappa classico per sezioni rettangolari piene.

Questo valore è da considerarsi fallback.
ATTENZIONE:
- Non va usato come verità normativa.
- È un valore standard della teoria della trave di Timoshenko.
- Il software può sovrascriverlo tramite config o registry.

TODO Copilot:
- Aggiungere supporto configurazione kappa da file YAML
  (es. src/config/app.yml)
"""


CIRCLE_KAPPA: float = 0.9
"""
Valore classico approssimato per sezioni circolari piene.

TODO Copilot:
- Verificare eventuale ref. interna ai parametri materiali.
"""


# ======================================================================
# REGISTRY DELLE STRATEGIE DI CALCOLO
# ======================================================================

SHEAR_AREA_STRATEGIES: Dict[str, ShearAreaFunction] = {}
"""
Mappa:

    shape_id: str → funzione calcolo A_sx, A_sy

shape_id è l'identificatore univoco di una sezione
nel repository delle sezioni (src/sections o src/elements).

TODO Copilot:
- Riempire il registry in fase di bootstrap
  leggendo dal registry delle sezioni.
"""


# ======================================================================
# FUNZIONI DI UTILITÀ PER REGISTRAZIONE
# ======================================================================

def register_shear_area_strategy(shape_id: str, func: ShearAreaFunction) -> None:
    """
    Registra una strategia di calcolo dell'area a taglio.

    Parametri:
    - shape_id: identificatore univoco della sezione.
    - func: funzione che implementa il calcolo.

    TODO Copilot:
    - Validazioni: shape_id non vuoto, func callable.
    """
    SHEAR_AREA_STRATEGIES[shape_id] = func


# ======================================================================
# STRATEGIE STANDARD (rettangolo & cerchio)
# ======================================================================

def _rectangular_shear_area(section: Any) -> Tuple[float, float]:
    """
    Calcolo A_sx e A_sy per una sezione rettangolare piena.

    Formula classica:
        A_s = kappa * A

    TODO Copilot:
    - Recuperare area reale della sezione.
    - Validare tipo 'rectangle'.
    """
    A = getattr(section, "area_cm2", 0.0)
    As = DEFAULT_KAPPA * A
    return (As, As)


def _circular_shear_area(section: Any) -> Tuple[float, float]:
    """
    Calcolo A_sx e A_sy per sezione circolare piena.

    TODO Copilot:
    - Validare tipo 'circle'.
    """
    A = getattr(section, "area_cm2", 0.0)
    As = CIRCLE_KAPPA * A
    return (As, As)


# ======================================================================
# REGISTRAZIONE DELLE STRATEGIE STANDARD
# ======================================================================

# TODO Copilot:
# - In futuro questi id saranno letti dal registry sezione.
register_shear_area_strategy("rectangle", _rectangular_shear_area)
register_shear_area_strategy("circle", _circular_shear_area)


# ======================================================================
# FUNZIONE GENERALE DI CALCOLO
# ======================================================================

def compute_shear_area(section: Any) -> Tuple[float, float]:
    """
    Calcola (A_sx, A_sy) in cm^2 per una sezione arbitraria.

    Comportamento:
    - Se esiste una strategia registrata → usarla.
    - Se *NON* esiste strategia → fallback a:
            A_sx = kappa_x * A
            A_sy = kappa_y * A
      dove kappa_x / kappa_y sono attributi opzionali della sezione.
      Se assenti → uso DEFAULT_KAPPA.

    ATTENZIONE:
    - Nessun calcolo normativo avviene qui.
    - Nessuna conversione automatica di unità.
    - Il fallback viene applicato a tutte le sezioni
      non coperte dal registry.

    TODO Copilot:
    - Estrarre kappa_x e kappa_y dalla sezione,
      con fallback DEFAULT_KAPPA.
    - Loggare strategia usata.
    - Integrare con config/numerics.yml se presente.
    """
    shape_id: Optional[str] = getattr(section, "shape_id", None)

    if shape_id in SHEAR_AREA_STRATEGIES:
        func = SHEAR_AREA_STRATEGIES[shape_id]
        return func(section)

    # --- Fallback universale ---
    A = getattr(section, "area_cm2", 0.0)
    kappa_x = getattr(section, "kappa_x", DEFAULT_KAPPA)
    kappa_y = getattr(section, "kappa_y", DEFAULT_KAPPA)

    return (kappa_x * A, kappa_y * A)


# ======================================================================
# FINE FILE
# ======================================================================
