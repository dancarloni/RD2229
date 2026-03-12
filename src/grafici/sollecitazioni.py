"""Grafici delle sollecitazioni interne (M, T, N) lungo l'asse di un elemento.

Unità interne:
- x      : cm  (ascissa lungo l'asse)
- M      : kg·cm (momento flettente)
- T      : kg  (taglio)
- N      : kg  (sforzo normale, positivo = trazione)

Le funzioni di visualizzazione convertono automaticamente in t·m e t per leggibilità.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass
class DiagrammaSollecitazioni:
    """Distribuzione delle sollecitazioni interne lungo un elemento.

    Attributi
    ---------
    x_cm : list[float]
        Ascissa lungo l'asse dell'elemento [cm].
    M_kgcm : list[float]
        Momento flettente [kg·cm].
    T_kg : list[float]
        Taglio [kg].
    N_kg : list[float]
        Sforzo normale [kg], positivo = trazione.
    etichetta : str
        Nome della combinazione o caso di carico.
    norma : str
        Norma di riferimento (es. "NTC2018", "RD2229").
    """

    x_cm: list[float]
    M_kgcm: list[float]
    T_kg: list[float]
    N_kg: list[float]
    etichetta: str = ""
    norma: str = ""

    def __post_init__(self) -> None:
        n = len(self.x_cm)
        if len(self.M_kgcm) != n or len(self.T_kg) != n or len(self.N_kg) != n:
            raise ValueError("M_kgcm, T_kg e N_kg devono avere la stessa lunghezza di x_cm.")

    @classmethod
    def da_valori_estremi(
        cls,
        L_cm: float,
        M_sx_kgcm: float,
        M_dx_kgcm: float,
        T_sx_kg: float,
        T_dx_kg: float,
        N_kg: float = 0.0,
        n_punti: int = 20,
        etichetta: str = "",
        norma: str = "",
    ) -> DiagrammaSollecitazioni:
        """Costruisce un diagramma lineare dagli estremi (per trave).

        Valido per carichi distribuiti uniformi o con variazione lineare.
        Per diagrammi non lineari usare il costruttore diretto.
        """
        x = list(np.linspace(0.0, L_cm, n_punti))
        t = np.linspace(0.0, 1.0, n_punti)
        M = list((1.0 - t) * M_sx_kgcm + t * M_dx_kgcm)
        T = list((1.0 - t) * T_sx_kg + t * T_dx_kg)
        N_arr = [N_kg] * n_punti
        return cls(
            x_cm=x,
            M_kgcm=M,
            T_kg=T,
            N_kg=N_arr,
            etichetta=etichetta,
            norma=norma,
        )

    @classmethod
    def da_risultato_checks(
        cls,
        risultato: dict[str, Any],
        L_cm: float,
        n_punti: int = 20,
    ) -> DiagrammaSollecitazioni:
        """Adapter: estrae domanda (M_Ed, T_Ed, N_Ed) da un risultato checks.

        Compatibile con il contratto standard dei moduli checks_*:
        - chiavi accettate: M_Ed_kgcm / Med_kgcm / M_kgcm
        - chiavi accettate: T_Ed_kg / Ted_kg / T_kg
        - chiavi accettate: N_Ed_kg / Ned_kg / N_kg

        Il diagramma risultante è costante lungo la luce (domanda uniforme).
        Per diagrammi variabili, usare il costruttore diretto.
        """

        def _prendi(d: dict, *chiavi: str, default: float = 0.0) -> float:
            for k in chiavi:
                if k in d and d[k] is not None:
                    return float(d[k])
            return default

        M_Ed = _prendi(risultato, "M_Ed_kgcm", "Med_kgcm", "M_kgcm")
        T_Ed = _prendi(risultato, "T_Ed_kg", "Ted_kg", "T_kg")
        N_Ed = _prendi(risultato, "N_Ed_kg", "Ned_kg", "N_kg")
        norma = risultato.get("norma", "")
        etichetta = risultato.get("etichetta", "") or risultato.get("modulo", "")

        x = list(np.linspace(0.0, L_cm, n_punti))
        return cls(
            x_cm=x,
            M_kgcm=[M_Ed] * n_punti,
            T_kg=[T_Ed] * n_punti,
            N_kg=[N_Ed] * n_punti,
            etichetta=str(etichetta),
            norma=str(norma),
        )


def grafico_sollecitazioni(
    diagramma: DiagrammaSollecitazioni,
    ax_M=None,
    ax_T=None,
    ax_N=None,
    fig=None,
    colore: str = "steelblue",
    riempimento: bool = True,
) -> tuple:
    """Disegna i tre diagrammi M / T / N su assi matplotlib.

    Se ax_M/ax_T/ax_N non forniti, crea una figura con 3 subplot.
    Le unità visualizzate sono [t·m] per M e [t] per T e N
    (conversione da kg·cm e kg per leggibilità).

    Ritorna (fig, (ax_M, ax_T, ax_N)).
    """
    try:
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise ImportError("matplotlib richiesto per grafico_sollecitazioni.") from exc

    x = np.asarray(diagramma.x_cm)
    M = np.asarray(diagramma.M_kgcm) / 1e4  # kg·cm → t·m
    T = np.asarray(diagramma.T_kg) / 1e3  # kg → t
    N = np.asarray(diagramma.N_kg) / 1e3  # kg → t
    zeros = np.zeros_like(x)

    crea_fig = ax_M is None or ax_T is None or ax_N is None
    if crea_fig:
        fig, (ax_M, ax_T, ax_N) = plt.subplots(3, 1, figsize=(10, 8), sharex=True)

    titolo = diagramma.etichetta or "Sollecitazioni"
    if diagramma.norma:
        titolo = f"{titolo} — {diagramma.norma}"
    if fig is not None:
        fig.suptitle(titolo, fontsize=11, fontweight="bold")

    # --- Momento flettente ---
    ax_M.plot(x, M, color=colore, linewidth=1.8, label="M [t·m]")
    if riempimento:
        ax_M.fill_between(x, M, zeros, alpha=0.18, color=colore)
    ax_M.axhline(0, color="black", linewidth=0.6)
    ax_M.set_ylabel("M [t·m]")
    ax_M.grid(True, linestyle="--", alpha=0.4)
    ax_M.legend(fontsize=8)

    # --- Taglio ---
    ax_T.plot(x, T, color="tomato", linewidth=1.8, label="T [t]")
    if riempimento:
        ax_T.fill_between(x, T, zeros, alpha=0.18, color="tomato")
    ax_T.axhline(0, color="black", linewidth=0.6)
    ax_T.set_ylabel("T [t]")
    ax_T.grid(True, linestyle="--", alpha=0.4)
    ax_T.legend(fontsize=8)

    # --- Sforzo normale ---
    ax_N.plot(x, N, color="seagreen", linewidth=1.8, label="N [t]")
    if riempimento:
        ax_N.fill_between(x, N, zeros, alpha=0.18, color="seagreen")
    ax_N.axhline(0, color="black", linewidth=0.6)
    ax_N.set_xlabel("x [cm]")
    ax_N.set_ylabel("N [t]")
    ax_N.grid(True, linestyle="--", alpha=0.4)
    ax_N.legend(fontsize=8)

    return fig, (ax_M, ax_T, ax_N)
