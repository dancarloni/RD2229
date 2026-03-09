"""Diagrammi di spostamento v(x) e u(x) lungo un elemento strutturale.

Unità:
- x   : cm  (ascissa lungo l'asse)
- v   : cm  (spostamento trasversale/verticale, freccia — positivo verso il basso)
- u   : cm  (spostamento orizzontale — positivo verso destra)
- M   : kg·cm (momento flettente in ingresso al solutore)
- EI  : kg·cm² (rigidezza flessionale)

Provider pattern (ISolutoreSpostamenti):
- SolutoreAnalitico : doppia integrazione numerica di M(x)/EI con scipy
- SolutoreFEM       : stub — implementazione delegata alla Fase M (FEM beam 2D)
"""

from __future__ import annotations

import abc
from dataclasses import dataclass
from typing import Sequence

import numpy as np


@dataclass
class DiagrammaSpostamenti:
    """Distribuzione degli spostamenti lungo un elemento strutturale.

    Attributi
    ---------
    x_cm : list[float]
        Ascissa lungo l'asse dell'elemento [cm].
    v_cm : list[float]
        Spostamento verticale (freccia) [cm], positivo verso il basso.
    u_cm : list[float]
        Spostamento orizzontale [cm], positivo verso destra.
    etichetta : str
        Nome del caso di carico o combinazione.
    solutore : str
        Tipo di solutore usato (es. "analitico", "FEM").
    """

    x_cm: list[float]
    v_cm: list[float]
    u_cm: list[float]
    etichetta: str = ""
    solutore: str = ""

    def __post_init__(self) -> None:
        n = len(self.x_cm)
        if len(self.v_cm) != n or len(self.u_cm) != n:
            raise ValueError("v_cm e u_cm devono avere la stessa lunghezza di x_cm.")

    @property
    def v_max_cm(self) -> float:
        """Freccia massima in valore assoluto [cm]."""
        return float(np.max(np.abs(self.v_cm))) if self.v_cm else 0.0

    @property
    def u_max_cm(self) -> float:
        """Spostamento orizzontale massimo in valore assoluto [cm]."""
        return float(np.max(np.abs(self.u_cm))) if self.u_cm else 0.0


class ISolutoreSpostamenti(abc.ABC):
    """Interfaccia astratta per il calcolo degli spostamenti."""

    @abc.abstractmethod
    def calcola(
        self,
        x_cm: Sequence[float],
        M_kgcm: Sequence[float],
        EI_kgcm2: float,
        *,
        etichetta: str = "",
    ) -> DiagrammaSpostamenti:
        """Calcola gli spostamenti v(x) e u(x) per un elemento piano.

        Parametri
        ---------
        x_cm : array-like
            Ascissa [cm] — deve essere monotona crescente.
        M_kgcm : array-like
            Diagramma del momento flettente [kg·cm], stessa lunghezza di x_cm.
        EI_kgcm2 : float
            Rigidezza flessionale EI [kg·cm²] (costante lungo la trave).
        etichetta : str
            Etichetta del caso di carico.

        Ritorna
        -------
        DiagrammaSpostamenti
        """
        ...


class SolutoreAnalitico(ISolutoreSpostamenti):
    """Spostamenti per doppia integrazione numerica di M(x)/EI.

    Metodo: integrazione con scipy.integrate.cumulative_trapezoid.
    Condizioni al contorno configurabili:
    - "semplicemente_appoggiata" : v(0)=0, v(L)=0
    - "incastro_appoggio"        : v(0)=0, v'(0)=0 (rotazione nulla all'incastro)
    - "doppio_incastro"          : v(0)=0, v(L)=0 (approssimato, come s.a.)

    Per telai con spostamento orizzontale, u(x) = 0 (calcolato da FEM in Fase M).
    """

    def __init__(self, bc: str = "semplicemente_appoggiata") -> None:
        """
        Parametri
        ---------
        bc : str
            Condizioni al contorno.
            Valori: "semplicemente_appoggiata" | "incastro_appoggio" | "doppio_incastro"
        """
        _bc_validi = {"semplicemente_appoggiata", "incastro_appoggio", "doppio_incastro"}
        if bc not in _bc_validi:
            raise ValueError(f"bc '{bc}' non valido. Scegliere tra: {_bc_validi}")
        self.bc = bc

    def calcola(
        self,
        x_cm: Sequence[float],
        M_kgcm: Sequence[float],
        EI_kgcm2: float,
        *,
        etichetta: str = "",
    ) -> DiagrammaSpostamenti:
        """Doppia integrazione numerica: φ(x) = M(x)/EI → θ(x) → v(x)."""
        try:
            from scipy.integrate import cumulative_trapezoid
        except ImportError as exc:
            raise ImportError("scipy richiesto per SolutoreAnalitico.") from exc

        x = np.asarray(x_cm, dtype=float)
        M = np.asarray(M_kgcm, dtype=float)

        if len(x) < 2:
            raise ValueError("x_cm deve contenere almeno 2 punti.")
        if len(x) != len(M):
            raise ValueError("x_cm e M_kgcm devono avere la stessa lunghezza.")
        if EI_kgcm2 <= 0.0:
            raise ValueError(f"EI deve essere positivo, ricevuto {EI_kgcm2}.")

        curvatura = M / EI_kgcm2  # φ(x) = M(x)/EI [1/cm]

        # Prima integrazione: rotazione θ(x) = ∫φ dx + C₁
        theta_raw = cumulative_trapezoid(curvatura, x, initial=0.0)

        # Seconda integrazione: freccia v(x) = ∫θ dx + C₂
        v_raw = cumulative_trapezoid(theta_raw, x, initial=0.0)

        v_cm = self._applica_bc(x, theta_raw, v_raw)

        # u(x) = 0 per trave piana (spostamento orizzontale dal FEM in Fase M)
        u_cm = np.zeros_like(x)

        return DiagrammaSpostamenti(
            x_cm=list(x),
            v_cm=list(v_cm),
            u_cm=list(u_cm),
            etichetta=etichetta,
            solutore="analitico",
        )

    def _applica_bc(
        self,
        x: np.ndarray,
        theta_raw: np.ndarray,
        v_raw: np.ndarray,
    ) -> np.ndarray:
        """Corregge v(x) imponendo le condizioni al contorno."""
        if self.bc == "semplicemente_appoggiata":
            # v(0)=0, v(L)=0 → correzione lineare
            L = x[-1] - x[0]
            if L == 0.0:
                return v_raw
            t = (x - x[0]) / L
            correzione = v_raw[0] * (1.0 - t) + v_raw[-1] * t
            return v_raw - correzione

        if self.bc == "incastro_appoggio":
            # v(0)=0, θ(0)=0 → sottrai il valore iniziale di v e la rampa da θ(0)
            return v_raw - v_raw[0]

        # doppio_incastro: stessa correzione semplicemente appoggiata (approssimato)
        return self._applica_bc(x, theta_raw, v_raw)


class SolutoreFEM(ISolutoreSpostamenti):
    """Stub per il solutore FEM — implementazione delegata alla Fase M.

    Sarà integrato con il modulo FEM beam 2D (scipy sparse) sviluppato
    nella Fase M del piano di lavoro (assemblaggio matrice di rigidezza globale).

    Produce anche u(x) (spostamento orizzontale per telai piani) a differenza
    di SolutoreAnalitico che restituisce u(x)=0.
    """

    def calcola(
        self,
        x_cm: Sequence[float],
        M_kgcm: Sequence[float],
        EI_kgcm2: float,
        *,
        etichetta: str = "",
    ) -> DiagrammaSpostamenti:
        raise NotImplementedError(
            "SolutoreFEM sarà implementato nella Fase M (FEM beam 2D — scipy sparse). "
            "Usare SolutoreAnalitico nel frattempo per travi isolate."
        )


def grafico_spostamenti(
    diagramma: DiagrammaSpostamenti,
    ax_v=None,
    ax_u=None,
    fig=None,
    colore: str = "darkorchid",
    scala: float = 1.0,
) -> tuple:
    """Disegna i diagrammi v(x) e u(x) su assi matplotlib.

    Se ax_v/ax_u non forniti, crea una figura con 2 subplot.

    Parametri
    ---------
    scala : float
        Fattore di scala visivo applicato agli spostamenti (solo per display,
        non modifica i dati in DiagrammaSpostamenti).

    Ritorna (fig, (ax_v, ax_u)).
    """
    try:
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise ImportError("matplotlib richiesto per grafico_spostamenti.") from exc

    x = np.asarray(diagramma.x_cm)
    v = np.asarray(diagramma.v_cm) * scala
    u = np.asarray(diagramma.u_cm) * scala
    zeros = np.zeros_like(x)

    crea_fig = ax_v is None or ax_u is None
    if crea_fig:
        fig, (ax_v, ax_u) = plt.subplots(2, 1, figsize=(10, 6), sharex=True)

    titolo = diagramma.etichetta or "Spostamenti"
    if diagramma.solutore:
        titolo = f"{titolo} [{diagramma.solutore}]"
    if scala != 1.0:
        titolo = f"{titolo} — scala ×{scala:.1f}"
    if fig is not None:
        fig.suptitle(titolo, fontsize=11, fontweight="bold")

    # --- Freccia v(x) ---
    ax_v.plot(x, v, color=colore, linewidth=1.8, label="v(x) [cm]")
    ax_v.fill_between(x, v, zeros, alpha=0.18, color=colore)
    ax_v.axhline(0, color="black", linewidth=0.6)
    ax_v.set_ylabel("v [cm]")
    ax_v.invert_yaxis()  # convenzione: freccia positiva verso il basso
    ax_v.grid(True, linestyle="--", alpha=0.4)
    ax_v.legend(fontsize=8)

    # Annotazione freccia massima
    v_orig = np.asarray(diagramma.v_cm)
    idx_max = int(np.argmax(np.abs(v_orig)))
    ax_v.annotate(
        f"v_max = {diagramma.v_max_cm:.3f} cm",
        xy=(x[idx_max], v[idx_max]),
        xytext=(8, -16),
        textcoords="offset points",
        fontsize=8,
        color=colore,
        arrowprops={"arrowstyle": "->", "color": colore, "lw": 0.8},
    )

    # --- Spostamento orizzontale u(x) ---
    ax_u.plot(x, u, color="darkorange", linewidth=1.8, label="u(x) [cm]")
    ax_u.fill_between(x, u, zeros, alpha=0.18, color="darkorange")
    ax_u.axhline(0, color="black", linewidth=0.6)
    ax_u.set_xlabel("x [cm]")
    ax_u.set_ylabel("u [cm]")
    ax_u.grid(True, linestyle="--", alpha=0.4)
    ax_u.legend(fontsize=8)

    return fig, (ax_v, ax_u)
