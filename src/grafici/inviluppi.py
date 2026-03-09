"""Inviluppi (buste) delle sollecitazioni su più combinazioni di carico.

Calcola il massimo e il minimo puntuale di M, T, N per una lista di
DiagrammaSollecitazioni che condividono la stessa ascissa x.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field

import numpy as np

from .sollecitazioni import DiagrammaSollecitazioni


@dataclass
class InviluppoSollecitazioni:
    """Busta superiore e inferiore di una serie di combinazioni di carico.

    Attributi
    ---------
    x_cm : list[float]
        Ascissa di riferimento [cm].
    M_max_kgcm, M_min_kgcm : list[float]
        Busta superiore/inferiore del momento [kg·cm].
    T_max_kg, T_min_kg : list[float]
        Busta superiore/inferiore del taglio [kg].
    N_max_kg, N_min_kg : list[float]
        Busta superiore/inferiore dello sforzo normale [kg].
    n_combinazioni : int
        Numero di diagrammi usati per costruire l'inviluppo.
    etichette : list[str]
        Etichette delle singole combinazioni.
    """

    x_cm: list[float]
    M_max_kgcm: list[float]
    M_min_kgcm: list[float]
    T_max_kg: list[float]
    T_min_kg: list[float]
    N_max_kg: list[float]
    N_min_kg: list[float]
    n_combinazioni: int = 0
    etichette: list[str] = field(default_factory=list)


def inviluppo_sollecitazioni(
    diagrammi: Sequence[DiagrammaSollecitazioni],
) -> InviluppoSollecitazioni:
    """Calcola l'inviluppo (busta max/min) di una sequenza di DiagrammaSollecitazioni.

    Tutti i diagrammi devono avere la stessa ascissa x_cm (stessa lunghezza).

    Ritorna un InviluppoSollecitazioni con max e min puntuali per M, T, N.
    """
    if not diagrammi:
        raise ValueError("Serve almeno un DiagrammaSollecitazioni.")

    x_ref = np.asarray(diagrammi[0].x_cm)
    n = len(x_ref)

    M_stack = np.zeros((len(diagrammi), n))
    T_stack = np.zeros((len(diagrammi), n))
    N_stack = np.zeros((len(diagrammi), n))

    for i, d in enumerate(diagrammi):
        if len(d.x_cm) != n:
            raise ValueError(
                f"Diagramma {i} ('{d.etichetta}') ha {len(d.x_cm)} punti, "
                f"atteso {n}. Tutti i diagrammi devono condividere la stessa ascissa."
            )
        M_stack[i] = np.asarray(d.M_kgcm)
        T_stack[i] = np.asarray(d.T_kg)
        N_stack[i] = np.asarray(d.N_kg)

    return InviluppoSollecitazioni(
        x_cm=list(x_ref),
        M_max_kgcm=list(np.max(M_stack, axis=0)),
        M_min_kgcm=list(np.min(M_stack, axis=0)),
        T_max_kg=list(np.max(T_stack, axis=0)),
        T_min_kg=list(np.min(T_stack, axis=0)),
        N_max_kg=list(np.max(N_stack, axis=0)),
        N_min_kg=list(np.min(N_stack, axis=0)),
        n_combinazioni=len(diagrammi),
        etichette=[d.etichetta for d in diagrammi],
    )


def grafico_inviluppo(
    inviluppo: InviluppoSollecitazioni,
    ax_M=None,
    ax_T=None,
    ax_N=None,
    fig=None,
    diagrammi: Sequence[DiagrammaSollecitazioni] | None = None,
) -> tuple:
    """Disegna la busta di inviluppo con riempimento tra max e min.

    Se ax_M/ax_T/ax_N non forniti, crea una figura con 3 subplot.
    Se ``diagrammi`` forniti, sovrappone anche i singoli diagrammi in grigio chiaro.

    Unità visualizzate: [t·m] per M, [t] per T e N.

    Ritorna (fig, (ax_M, ax_T, ax_N)).
    """
    try:
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise ImportError("matplotlib richiesto per grafico_inviluppo.") from exc

    crea_fig = ax_M is None or ax_T is None or ax_N is None
    if crea_fig:
        fig, (ax_M, ax_T, ax_N) = plt.subplots(3, 1, figsize=(10, 8), sharex=True)

    if fig is not None:
        fig.suptitle(
            f"Inviluppo sollecitazioni ({inviluppo.n_combinazioni} combinazioni)",
            fontsize=11,
            fontweight="bold",
        )

    x = np.asarray(inviluppo.x_cm)

    def _banda(ax, sup_raw, inf_raw, etichetta_y, colore):
        sup = np.asarray(sup_raw)
        inf = np.asarray(inf_raw)
        ax.fill_between(x, sup, inf, alpha=0.25, color=colore, label="Busta")
        ax.plot(x, sup, color=colore, linewidth=1.5, linestyle="--")
        ax.plot(x, inf, color=colore, linewidth=1.5, linestyle="--")
        ax.axhline(0, color="black", linewidth=0.6)
        ax.set_ylabel(etichetta_y)
        ax.grid(True, linestyle="--", alpha=0.4)
        ax.legend(fontsize=8)

    _banda(
        ax_M,
        np.asarray(inviluppo.M_max_kgcm) / 1e4,
        np.asarray(inviluppo.M_min_kgcm) / 1e4,
        "M [t·m]",
        "steelblue",
    )
    _banda(
        ax_T,
        np.asarray(inviluppo.T_max_kg) / 1e3,
        np.asarray(inviluppo.T_min_kg) / 1e3,
        "T [t]",
        "tomato",
    )
    _banda(
        ax_N,
        np.asarray(inviluppo.N_max_kg) / 1e3,
        np.asarray(inviluppo.N_min_kg) / 1e3,
        "N [t]",
        "seagreen",
    )
    ax_N.set_xlabel("x [cm]")

    # Sovrappone singoli diagrammi in grigio (opzionale)
    if diagrammi:
        for d in diagrammi:
            x_d = np.asarray(d.x_cm)
            ax_M.plot(x_d, np.asarray(d.M_kgcm) / 1e4, color="gray", alpha=0.3, linewidth=0.8)
            ax_T.plot(x_d, np.asarray(d.T_kg) / 1e3, color="gray", alpha=0.3, linewidth=0.8)
            ax_N.plot(x_d, np.asarray(d.N_kg) / 1e3, color="gray", alpha=0.3, linewidth=0.8)

    return fig, (ax_M, ax_T, ax_N)
