"""Post-processing spostamenti e sollecitazioni FEM (M.5).

Calcola le distribuzioni continue M(x), V(x), N(x) e v(x) a partire
dagli spostamenti nodali globali.

**Metodo per M(x) e V(x) — equilibrio statico (esatto anche con 1 elemento):**

Per ogni elemento:
1. Calcola forze nodali da rigidezza:   f_stiff = k_loc · d_loc
2. Calcola carichi nodali equivalenti:  f_eq   = f_eq_loc dai carichi
3. Reazione effettiva al nodo sinistro: F_v = f_stiff[1] − f_eq[1]
                                        F_M = f_stiff[2] − f_eq[2]
4. Integra per V(x) e M(x):
   V(x) = F_v + ∫₀ˣ q(t) dt
   M(x) = F_M + ∫₀ˣ V(t) dt

**Metodo per v(x) — polinomio di Hermite cubico:**
   v(x) = N(ξ) · [v_i, L·θ_i, v_j, L·θ_j]
   (approssimazione cubica; converge all'esatto con raffinamento della mesh)

Convenzione dei segni (FEM classica locale):
- M positivo: forza le fibre inferiori in trazione (convenzionale)
- V positivo: taglio positivo al nodo sinistro (upward on left face)
- N positivo: trazione

Unità:
- x: cm
- v, u: cm
- M: kg·cm
- V: kg
- N: kg
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

import numpy as np
import scipy.integrate as scint

from .assemblaggio import ElementoFEM
from .elemento_beam import BaseCaricoBeam, CaricoConcentrato

logger = logging.getLogger("rd2229.fem.postprocessing")


@dataclass
class DiagrammaElemento:
    """Distribuzione delle grandezze interne lungo un elemento beam.

    Attributi
    ---------
    id_elemento : int
        Identificatore dell'elemento.
    etichetta : str
        Etichetta dell'elemento (opzionale).
    x_glob : np.ndarray
        Ascissa globale dei punti di campionamento [cm].
    v_cm : np.ndarray
        Spostamento trasversale locale v(x) [cm].
    u_cm : np.ndarray
        Spostamento assiale locale u(x) [cm].
    M_kgcm : np.ndarray
        Momento flettente M(x) [kg·cm].
    V_kg : np.ndarray
        Taglio V(x) [kg].
    N_kg : np.ndarray
        Sforzo normale N(x) [kg].
    passaggi_calcolo : list[str]
        Traccia passaggi per tabulato.
    """

    id_elemento: int
    etichetta: str
    x_glob: np.ndarray
    v_cm: np.ndarray
    u_cm: np.ndarray
    M_kgcm: np.ndarray
    V_kg: np.ndarray
    N_kg: np.ndarray
    passaggi_calcolo: list[str]

    def to_dict(self) -> dict[str, object]:
        return {
            "id_elemento": self.id_elemento,
            "etichetta": self.etichetta,
            "x_glob": [round(float(v), 6) for v in self.x_glob],
            "v_cm": [round(float(v), 8) for v in self.v_cm],
            "u_cm": [round(float(v), 8) for v in self.u_cm],
            "M_kgcm": [round(float(v), 4) for v in self.M_kgcm],
            "V_kg": [round(float(v), 4) for v in self.V_kg],
            "N_kg": [round(float(v), 4) for v in self.N_kg],
            "passaggi_calcolo": self.passaggi_calcolo,
        }


def _hermite_v(xi: float) -> np.ndarray:
    """Funzioni di forma di Hermite per lo spostamento trasversale v.

    Parametri
    ---------
    xi : float
        Coordinata locale normalizzata xi = x/L in [0, 1].

    Ritorna
    -------
    np.ndarray shape (4,)
        [N1(xi), N2(xi), N3(xi), N4(xi)] per [v_i, L*θ_i, v_j, L*θ_j].
    """
    n1 = 1.0 - 3.0 * xi**2 + 2.0 * xi**3
    n2 = xi - 2.0 * xi**2 + xi**3
    n3 = 3.0 * xi**2 - 2.0 * xi**3
    n4 = -(xi**2) + xi**3
    return np.array([n1, n2, n3, n4], dtype=float)


class PostProcessorFEM:
    """Calcola M(x), V(x), N(x), v(x) per ogni elemento dal vettore u globale.

    Parametri
    ---------
    elementi : list[ElementoFEM]
        Elementi del modello.
    u_globale : np.ndarray
        Vettore spostamenti globale [n_gdl] dal solutore.
    n_punti : int
        Numero di punti di campionamento per elemento (default 20).
    """

    def __init__(
        self,
        elementi: list[ElementoFEM],
        u_globale: np.ndarray,
        n_punti: int = 20,
    ) -> None:
        self.elementi = elementi
        self.u_globale = u_globale
        self.n_punti = n_punti

    def calcola_tutti(self) -> list[DiagrammaElemento]:
        """Calcola i diagrammi per tutti gli elementi."""
        return [self._calcola_elemento(elem) for elem in self.elementi]

    def _calcola_elemento(self, elem: ElementoFEM) -> DiagrammaElemento:
        """Calcola i diagrammi per un singolo elemento."""
        beam = elem.beam
        L = beam.L
        EI = beam.E * beam.I
        EA = beam.E * beam.A
        passaggi: list[str] = [
            f"Elemento {elem.id} ('{beam.etichetta}'): L={L:.2f} cm, "
            f"E={beam.E:.1f} kg/cm², A={beam.A:.2f} cm², I={beam.I:.2f} cm⁴",
            "V(x) = F_v + ∫₀ˣ q(t) dt  [equilibrio statico]",
            "M(x) = F_M + ∫₀ˣ V(t) dt  [equilibrio statico]",
            "v(x) = polinomio Hermite cubico da (v_i, θ_i, v_j, θ_j) locali",
            "N(x) = EA · (u_j - u_i) / L  [costante per elemento]",
        ]

        # Spostamenti nodali locali
        indici = elem.indici_gdl_globali
        u6_glob = self.u_globale[indici]
        T_e = beam.matrice_trasformazione()
        d_loc = T_e @ u6_glob
        u_i_loc, v_i_loc, theta_i, u_j_loc, v_j_loc, theta_j = d_loc

        # Forze di rigidezza dell'elemento (in coordinate locali)
        k_loc = beam.matrice_rigidezza_locale()
        f_stiff = k_loc @ d_loc

        # Carichi equivalenti nodali (in coordinate locali)
        f_eq = np.zeros(6, dtype=float)
        if elem.carichi:
            f_eq = beam.combina_carichi(elem.carichi).vettore_locale

        # Reazione effettiva al nodo sinistro (equilibrio globale del nodo)
        # F_left_v = f_stiff[1] - f_eq[1]  (taglio netto al nodo i)
        # F_left_M = f_stiff[2] - f_eq[2]  (momento netto al nodo i)
        F_left_v = float(f_stiff[1] - f_eq[1])
        F_left_M = float(f_stiff[2] - f_eq[2])

        passaggi.append(
            f"Reazione al nodo i: V_i={F_left_v:.4f} kg, M_i={F_left_M:.4f} kg·cm"
        )

        # Punti di campionamento
        xi_arr = np.linspace(0.0, 1.0, self.n_punti)
        x_arr = xi_arr * L

        # Profilo del carico trasversale distribuito q(x) locale
        q_arr = np.zeros(self.n_punti, dtype=float)
        carichi_concentrati: list[tuple[float, float]] = []

        for carico in elem.carichi:
            if isinstance(carico, CaricoConcentrato) and carico.tipo == "forza_y":
                carichi_concentrati.append((carico.valore, carico.posizione_x))
            else:
                for k_idx, x_k in enumerate(x_arr):
                    q_arr[k_idx] += carico.intensita_trasversale(x_k, L)

        # V_distrib(x) = F_left_v + ∫₀ˣ q_distr(t) dt  (solo carichi distribuiti)
        cum_q = np.concatenate(
            [[0.0], scint.cumulative_trapezoid(q_arr, x_arr)]
        )
        V_distrib = F_left_v + cum_q

        # M_distrib(x) = F_left_M + ∫₀ˣ V_distrib(t) dt
        cum_V_distrib = np.concatenate(
            [[0.0], scint.cumulative_trapezoid(V_distrib, x_arr)]
        )
        M_distrib = F_left_M + cum_V_distrib

        # Carichi concentrati: contributi esatti a V e M (step function + ramp)
        V_conc = np.zeros(self.n_punti, dtype=float)
        M_conc = np.zeros(self.n_punti, dtype=float)
        for P, a in carichi_concentrati:
            mask = x_arr >= a - 1e-12
            V_conc += P * mask.astype(float)
            M_conc += P * np.maximum(x_arr - a, 0.0)

        V_arr = V_distrib + V_conc
        M_arr = M_distrib + M_conc

        # Sforzo normale N (costante per elemento lineare)
        N_val = EA * (u_j_loc - u_i_loc) / L
        N_arr = np.full(self.n_punti, N_val, dtype=float)

        passaggi.append(f"N (sforzo normale) = EA·(u_j-u_i)/L = {N_val:.4f} kg (costante)")

        # Spostamento trasversale v(x) con polinomio di Hermite
        d_herm = np.array([v_i_loc, L * theta_i, v_j_loc, L * theta_j], dtype=float)
        v_loc = np.array(
            [float(_hermite_v(xi) @ d_herm) for xi in xi_arr], dtype=float
        )

        # Spostamento assiale u(x) interpolato linearmente
        u_loc = u_i_loc + (u_j_loc - u_i_loc) * xi_arr

        logger.debug(
            "Elemento %d: v_max=%.4f cm, M_max=%.2f kg·cm, V_max=%.2f kg, N=%.2f kg",
            elem.id,
            float(np.max(np.abs(v_loc))),
            float(np.max(np.abs(M_arr))),
            float(np.max(np.abs(V_arr))),
            abs(N_val),
        )

        # Coordinate globali dei punti di campionamento
        c = beam.coseno
        x_glob = elem.nodo_i.x + xi_arr * L * c

        return DiagrammaElemento(
            id_elemento=elem.id,
            etichetta=beam.etichetta,
            x_glob=x_glob,
            v_cm=v_loc,
            u_cm=u_loc,
            M_kgcm=M_arr,
            V_kg=V_arr,
            N_kg=N_arr,
            passaggi_calcolo=passaggi,
        )

