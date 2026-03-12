"""Diagrammi di interazione N-M per tutte le norme del progetto.

Estende src/codes/pressoflessione/dominio.py aggiungendo:
- PuntoLavoro: punto di lavoro (N_Ed, M_Ed) da sovrapporre al dominio
- DominioFactory: registry multinorma (TA e SLU per tutte le norme coperte)
- sovrapponi_punto_lavoro: overlay punto su asse matplotlib 2D N-M

Norme TA (tensioni ammissibili): RD2229, DM72, DM87, DM96, OPCM3274, CIRC1981
Norme SLU (stati limite ultimi):  NTC2008, NTC2018
"""

from __future__ import annotations

import dataclasses
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass
class PuntoLavoro:
    """Punto di lavoro da sovrapporre al diagramma di interazione.

    Attributi
    ---------
    N_Ed_kg : float
        Sforzo normale di progetto [kg], positivo = compressione (conv. strutturale).
    Mx_Ed_kgcm : float
        Momento di progetto attorno all'asse x [kg·cm].
    My_Ed_kgcm : float
        Momento di progetto attorno all'asse y [kg·cm].
    etichetta : str
        Descrizione del punto (es. "SLU — Comb. 1").
    norma : str
        Norma di verifica (informativa).
    """

    N_Ed_kg: float
    Mx_Ed_kgcm: float = 0.0
    My_Ed_kgcm: float = 0.0
    etichetta: str = ""
    norma: str = ""


# ---------------------------------------------------------------------------
# Norme supportate
# ---------------------------------------------------------------------------

_NORME_TA: frozenset[str] = frozenset(
    {
        "RD2229",
        "RD2229/1939",
        "DM72",
        "DM30/05/1972",
        "DM87",
        "DM20/11/1987",
        "DM96",
        "DM09/01/1996",
        "CIRC1981",
        "CIRC30/07/1981",
        "OPCM3274",
    }
)

_NORME_SLU: frozenset[str] = frozenset(
    {
        "NTC2008",
        "NTC 2008",
        "NTC2018",
        "NTC 2018",
    }
)


def _normalizza_norma(norma: str) -> str:
    """Rimuove spazi e porta in maiuscolo per confronto uniforme."""
    return norma.upper().replace(" ", "")


def _calcola_dominio_ta(spec: Any, **kwargs) -> Any:
    """Wrapper: calcolo dominio TA (tensioni ammissibili) via dominio.py."""
    from src.codes.pressoflessione.dominio import calcola_dominio_3d

    spec_ta = dataclasses.replace(spec, metodo="SOVRAPPOSIZIONE_ELASTICA")
    return calcola_dominio_3d(spec_ta, **kwargs)


def _calcola_dominio_slu(spec: Any, **kwargs) -> Any:
    """Wrapper: calcolo dominio SLU Bresler via dominio.py."""
    from src.codes.pressoflessione.dominio import calcola_dominio_3d

    spec_slu = dataclasses.replace(spec, metodo="BRESLER_SLU")
    return calcola_dominio_3d(spec_slu, **kwargs)


# ---------------------------------------------------------------------------
# DominioFactory
# ---------------------------------------------------------------------------


class DominioFactory:
    """Factory per il calcolo del dominio di interazione multinorma.

    Supporta automaticamente le norme TA e SLU del progetto.
    Consente la registrazione di funzioni personalizzate per norme aggiuntive.

    Uso
    ---
    >>> factory = DominioFactory()
    >>> dominio = factory.calcola(spec, norma="NTC2018")
    >>> dominio = factory.calcola(spec)  # usa spec.norma
    """

    _registry: dict[str, Callable] = {}

    @classmethod
    def registra(cls, norma: str, funzione: Callable) -> None:
        """Registra una funzione di calcolo personalizzata per una norma.

        Parametri
        ---------
        norma : str
            Identificatore norma (case-insensitive, spazi rimossi).
        funzione : Callable
            Funzione con firma ``f(spec, **kwargs) -> DominioNMy``.
        """
        cls._registry[_normalizza_norma(norma)] = funzione

    @classmethod
    def calcola(cls, spec: Any, norma: str | None = None, **kwargs) -> Any:
        """Calcola il dominio di interazione per la norma indicata.

        Se ``norma`` non specificata, usa ``spec.norma``.

        Precedenza: registry custom → norme TA predefinite → norme SLU predefinite.

        Solleva ValueError se la norma non è supportata.
        """
        norma_eff = _normalizza_norma(norma or getattr(spec, "norma", "RD2229"))

        if norma_eff in cls._registry:
            return cls._registry[norma_eff](spec, **kwargs)

        norme_ta_norm = {_normalizza_norma(n) for n in _NORME_TA}
        norme_slu_norm = {_normalizza_norma(n) for n in _NORME_SLU}

        if norma_eff in norme_ta_norm:
            spec_norma = dataclasses.replace(spec, norma=norma or getattr(spec, "norma", "RD2229"))
            return _calcola_dominio_ta(spec_norma, **kwargs)

        if norma_eff in norme_slu_norm:
            spec_norma = dataclasses.replace(spec, norma=norma or getattr(spec, "norma", "NTC2018"))
            return _calcola_dominio_slu(spec_norma, **kwargs)

        raise ValueError(
            f"Norma '{norma_eff}' non supportata da DominioFactory.\n"
            f"Norme TA: {sorted(_NORME_TA)}\n"
            f"Norme SLU: {sorted(_NORME_SLU)}\n"
            f"Norme custom registrate: {sorted(cls._registry.keys())}"
        )

    @classmethod
    def norme_disponibili(cls) -> list[str]:
        """Ritorna l'elenco ordinato di tutte le norme supportate."""
        return sorted(
            _NORME_TA | _NORME_SLU | set(cls._registry.keys()),
            key=str.upper,
        )


# ---------------------------------------------------------------------------
# Sovrapposizione punto di lavoro
# ---------------------------------------------------------------------------


def sovrapponi_punto_lavoro(
    ax,
    punto: PuntoLavoro,
    theta_fisso_rad: float = 0.0,
    colore: str = "crimson",
    simbolo: str = "X",
    dimensione: int = 120,
) -> None:
    """Sovrappone il punto di lavoro (N_Ed, M_Ed) su un asse matplotlib 2D N-M.

    Il momento viene proiettato lungo la direzione θ:
        M_proiettato = |Mx·cos(θ)| + |My·sin(θ)|

    Le unità visualizzate sono [t·m] per M e [t] per N,
    coerentemente con gli assi prodotti da dominio.py.

    Parametri
    ---------
    ax : matplotlib.axes.Axes
        Asse 2D N-M su cui disegnare (prodotto da _draw_2d_nm di dominio.py).
    punto : PuntoLavoro
        Punto di lavoro da visualizzare.
    theta_fisso_rad : float
        Angolo θ [rad] usato per la proiezione del momento.
    colore : str
        Colore del marcatore.
    simbolo : str
        Marcatore matplotlib (default "X").
    dimensione : int
        Dimensione del marcatore in punti² (scatter s=).
    """
    M_proiettato_kgcm = punto.Mx_Ed_kgcm * abs(
        float(np.cos(theta_fisso_rad))
    ) + punto.My_Ed_kgcm * abs(float(np.sin(theta_fisso_rad)))
    # Converti in t·m e t (coerente con _draw_2d_nm che usa kg·cm e kg sugli assi)
    # NOTA: dominio_canvas._draw_2d_nm usa direttamente kg·cm e kg sull'asse.
    # sovrapponi_punto_lavoro usa le stesse unità degli assi esistenti.
    M_plot = M_proiettato_kgcm  # kg·cm (asse X del dominio N-M)
    N_plot = punto.N_Ed_kg  # kg (asse Y del dominio N-M)

    ax.scatter(
        M_plot,
        N_plot,
        color=colore,
        marker=simbolo,
        s=dimensione,
        zorder=10,
        label=punto.etichetta or "Punto di lavoro",
    )
    ax.annotate(
        punto.etichetta or "Ed",
        xy=(M_plot, N_plot),
        xytext=(8, 8),
        textcoords="offset points",
        fontsize=8,
        color=colore,
    )
    ax.legend(fontsize=8)
