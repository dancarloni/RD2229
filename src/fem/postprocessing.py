"""Post-processing: diagrammi continui M(x), V(x), N(x) per elementi beam 2D.

Metodo di calcolo:
- Con carichi (opzionale): formula equilibrio esatta (equilibrium-based).
  V(x) = V₀ + ∫₀ˣ q(t) dt
  M(x) = M₀ + V₀·x + ∫₀ˣ q(t)·(x-t) dt
  dove V₀, M₀ sono calcolati dalle forze nodali di fine elemento.
- Senza carichi: polinomi di Hermite cubici (esatto per elementi senza carichi distribuiti).

Convenzione dei segni (equilibrio FEM):
- M(x) positivo: fibra inferiore tesa (momento sagging per carico gravitazionale)
- V(x) positivo: taglio verso l'alto sulla faccia sinistra
- N(x) positivo: trazione

Unità:
- x  : cm
- M  : kg·cm
- V  : kg
- N  : kg
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import numpy as np

from .elemento_beam import (
    BaseCaricoBeam,
    CaricoConcentrato,
    CaricoDistribuitoGenerico,
    CaricoDistribuitoUniforme,
    CaricoTrapezoidale,
    CaricoTriangolare,
    CaricoTriangolareInverso,
    ElementoBeam,
)

if TYPE_CHECKING:
    pass


# ---------------------------------------------------------------------------
# Funzioni ausiliarie per l'integrale del carico (V e M da equilibrio)
# ---------------------------------------------------------------------------

def _shear_moment_distributed(carico: BaseCaricoBeam, x: float, L: float) -> tuple[float, float]:
    """∫₀ˣ q(t) dt  e  ∫₀ˣ q(t)·(x-t) dt per carichi distribuiti trasversali.

    Ritorna (taglio_cumulato, momento_cumulato).
    Per carichi concentrati o assiali ritorna (0, 0).
    """
    if isinstance(carico, CaricoDistribuitoUniforme):
        if carico.direzione_locale != "y":
            return 0.0, 0.0
        q = carico.intensita
        return q * x, q * x**2 / 2.0

    if isinstance(carico, CaricoTriangolare):
        qm = carico.intensita_massima  # q(t) = qm * t / L
        return qm * x**2 / (2.0 * L), qm * x**3 / (6.0 * L)

    if isinstance(carico, CaricoTriangolareInverso):
        qm = carico.intensita_massima  # q(t) = qm * (1 - t/L)
        return qm * (x - x**2 / (2.0 * L)), qm * (x**2 / 2.0 - x**3 / (6.0 * L))

    if isinstance(carico, CaricoTrapezoidale):
        qi, qj = carico.intensita_i, carico.intensita_j  # q(t) = qi + (qj-qi)*t/L
        shear = qi * x + (qj - qi) * x**2 / (2.0 * L)
        moment = qi * x**2 / 2.0 + (qj - qi) * x**3 / (6.0 * L)
        return shear, moment

    if isinstance(carico, CaricoDistribuitoGenerico):
        func = carico.funzione_intensita
        n = 12
        pts, wts = np.polynomial.legendre.leggauss(n)
        t_pts = 0.5 * x * (pts + 1.0)
        q_vals = np.array([func(float(t), L) for t in t_pts])
        shear = 0.5 * x * float(np.dot(wts, q_vals))
        moment = 0.5 * x * float(np.dot(wts, q_vals * (x - t_pts)))
        return shear, moment

    return 0.0, 0.0


def _shear_moment_concentrated(carico: BaseCaricoBeam, x: float, L: float) -> tuple[float, float]:
    """Contributo al taglio e momento da CaricoConcentrato interno (0 < a < L).

    Ritorna (taglio_cumulato, momento_cumulato) per la sezione a posizione x.
    Carichi ai nodi (a=0 o a=L) non contribuiscono all'interno dell'elemento.
    """
    if isinstance(carico, CaricoConcentrato) and carico.tipo == "forza_y":
        a = carico.posizione_x
        if 0.0 < a < L and x > a:
            P = carico.valore
            return P, P * (x - a)
    return 0.0, 0.0


@dataclass
class DiagrammiElemento:
    """Diagrammi M, V, N continui lungo un elemento beam.

    Attributi
    ---------
    x : np.ndarray
        Ascissa locale [cm], da 0 a L.
    M : np.ndarray
        Momento flettente [kg·cm].
    V : np.ndarray
        Taglio [kg].
    N : np.ndarray
        Sforzo normale [kg].
    etichetta : str
        Nome o identificatore dell'elemento.
    passaggi_calcolo : list[str]
        Log dei passaggi di calcolo.
    """

    x: np.ndarray
    M: np.ndarray
    V: np.ndarray
    N: np.ndarray
    etichetta: str = ""
    passaggi_calcolo: list[str] = field(default_factory=list)

    @property
    def M_max(self) -> float:
        """Valore massimo assoluto del momento [kg·cm]."""
        return float(np.max(np.abs(self.M)))

    @property
    def V_max(self) -> float:
        """Valore massimo assoluto del taglio [kg]."""
        return float(np.max(np.abs(self.V)))

    @property
    def N_max(self) -> float:
        """Valore massimo assoluto dello sforzo normale [kg]."""
        return float(np.max(np.abs(self.N)))

    def to_dict(self) -> dict[str, object]:
        return {
            "etichetta": self.etichetta,
            "x": list(self.x),
            "M_kgcm": list(self.M),
            "V_kg": list(self.V),
            "N_kg": list(self.N),
            "M_max_kgcm": self.M_max,
            "V_max_kg": self.V_max,
            "N_max_kg": self.N_max,
            "passaggi_calcolo": self.passaggi_calcolo,
        }


def _hermite_N(xi: float) -> np.ndarray:
    """Funzioni di forma di Hermite cubiche normalizzate in [0, 1].

    N = [N1, N2, N3, N4] valutate in ξ = x/L.

    N1(ξ) = 1 - 3ξ² + 2ξ³
    N2(ξ) = ξ - 2ξ² + ξ³   (scala L implicita nell'uso)
    N3(ξ) = 3ξ² - 2ξ³
    N4(ξ) = -ξ² + ξ³         (scala L implicita nell'uso)
    """
    xi2 = xi * xi
    xi3 = xi2 * xi
    return np.array(
        [
            1.0 - 3.0 * xi2 + 2.0 * xi3,
            xi - 2.0 * xi2 + xi3,
            3.0 * xi2 - 2.0 * xi3,
            -xi2 + xi3,
        ],
        dtype=float,
    )


def _hermite_N2(xi: float, L: float) -> np.ndarray:
    """Derivata seconda delle funzioni di Hermite rispetto a x (non ξ).

    d²N/dx² = (1/L²) · d²N/dξ²

    d²N1/dξ² = -6 + 12ξ
    d²N2/dξ² = -4 + 6ξ       → d²N2/dx² = (-4 + 6ξ)/L
    d²N3/dξ² = 6 - 12ξ
    d²N4/dξ² = -2 + 6ξ       → d²N4/dx² = (-2 + 6ξ)/L
    """
    L2 = L * L
    return np.array(
        [
            (-6.0 + 12.0 * xi) / L2,
            (-4.0 + 6.0 * xi) / L,  # nota: scala dimensionale
            (6.0 - 12.0 * xi) / L2,
            (-2.0 + 6.0 * xi) / L,
        ],
        dtype=float,
    )


def _hermite_N3(xi: float, L: float) -> np.ndarray:
    """Derivata terza delle funzioni di Hermite rispetto a x.

    d³N1/dx³ = 12/L³
    d³N2/dx³ = 6/L²
    d³N3/dx³ = -12/L³
    d³N4/dx³ = 6/L²
    """
    L3 = L * L * L
    L2 = L * L
    return np.array(
        [
            12.0 / L3,
            6.0 / L2,
            -12.0 / L3,
            6.0 / L2,
        ],
        dtype=float,
    )


def calcola_diagrammi_elemento(
    elemento: ElementoBeam,
    spostamenti_globali: np.ndarray,
    id_nodo_iniziale: int,
    id_nodo_finale: int,
    n_punti: int = 20,
    carichi: list[BaseCaricoBeam] | None = None,
) -> DiagrammiElemento:
    """Calcola i diagrammi M, V, N continui per un elemento beam.

    Parametri
    ---------
    elemento : ElementoBeam
        Proprietà geometriche e meccaniche dell'elemento.
    spostamenti_globali : np.ndarray
        Vettore spostamenti completo (tutti i GDL della struttura).
    id_nodo_iniziale : int
        Indice del nodo iniziale.
    id_nodo_finale : int
        Indice del nodo finale.
    n_punti : int
        Numero di punti di campionamento lungo l'elemento.
    carichi : list[BaseCaricoBeam] | None
        Se forniti, usa il metodo equilibrio (esatto anche per carichi distribuiti).
        Se None, usa i polinomi di Hermite (approssimato per carichi distribuiti).

    Ritorna
    -------
    DiagrammiElemento
    """
    dof_i = [3 * id_nodo_iniziale, 3 * id_nodo_iniziale + 1, 3 * id_nodo_iniziale + 2]
    dof_j = [3 * id_nodo_finale, 3 * id_nodo_finale + 1, 3 * id_nodo_finale + 2]
    dof_e = dof_i + dof_j

    d_glob = spostamenti_globali[dof_e]
    T = elemento.matrice_trasformazione()
    d_loc = T @ d_glob

    u_i, v_i, theta_i, u_j, v_j, theta_j = d_loc
    L = elemento.L
    EI = elemento.E * elemento.I
    EA = elemento.E * elemento.A

    x_arr = np.linspace(0.0, L, n_punti)
    M_arr = np.empty(n_punti, dtype=float)
    V_arr = np.empty(n_punti, dtype=float)
    N_arr = np.full(n_punti, EA * (u_j - u_i) / L, dtype=float)

    if carichi:
        # Metodo equilibrio: V₀ e M₀ da forze di estremità, poi integrazione
        f_equiv = elemento.combina_carichi(carichi).vettore_locale
        f_e = elemento.matrice_rigidezza_locale() @ d_loc
        V_0 = float(f_e[1] - f_equiv[1])
        M_0 = float(f_equiv[2] - f_e[2])

        for k, x in enumerate(x_arr):
            shear_d = 0.0
            moment_d = 0.0
            for carico in carichi:
                s, m = _shear_moment_distributed(carico, x, L)
                shear_d += s
                moment_d += m
                sc, mc = _shear_moment_concentrated(carico, x, L)
                shear_d += sc
                moment_d += mc
            V_arr[k] = V_0 + shear_d
            M_arr[k] = M_0 + V_0 * x + moment_d

        metodo = "equilibrio"
    else:
        # Metodo Hermite: esatto per elementi senza carichi distribuiti
        d_flex_raw = np.array([v_i, theta_i, v_j, theta_j], dtype=float)
        for k, x in enumerate(x_arr):
            xi = x / L
            M_arr[k] = EI * float(_hermite_N2(xi, L) @ d_flex_raw)
            V_arr[k] = -EI * float(_hermite_N3(xi, L) @ d_flex_raw)

        metodo = "Hermite"

    passaggi = [
        f"Elemento '{elemento.etichetta}' L={L:.1f} cm — metodo: {metodo}",
        f"Spost. locali: u_i={u_i:.4f}, v_i={v_i:.4f}, θ_i={theta_i:.6f}",
        f"  u_j={u_j:.4f}, v_j={v_j:.4f}, θ_j={theta_j:.6f}",
        f"M_max={np.max(np.abs(M_arr)):.3f} kg·cm, V_max={np.max(np.abs(V_arr)):.3f} kg",
    ]

    return DiagrammiElemento(
        x=x_arr,
        M=M_arr,
        V=V_arr,
        N=N_arr,
        etichetta=elemento.etichetta,
        passaggi_calcolo=passaggi,
    )


@dataclass
class RisultatoPostProcessing:
    """Diagrammi M, V, N per tutti gli elementi della struttura.

    Attributi
    ---------
    elementi : list[DiagrammiElemento]
        Diagrammi per ogni elemento, nell'ordine della lista di input.
    passaggi_calcolo : list[str]
        Log riassuntivo del post-processing.
    """

    elementi: list[DiagrammiElemento]
    passaggi_calcolo: list[str] = field(default_factory=list)

    @property
    def M_max_globale(self) -> float:
        """Massimo momento flettente assoluto su tutti gli elementi [kg·cm]."""
        if not self.elementi:
            return 0.0
        return float(max(e.M_max for e in self.elementi))

    @property
    def V_max_globale(self) -> float:
        """Massimo taglio assoluto su tutti gli elementi [kg]."""
        if not self.elementi:
            return 0.0
        return float(max(e.V_max for e in self.elementi))

    @property
    def N_max_globale(self) -> float:
        """Massimo sforzo normale assoluto su tutti gli elementi [kg]."""
        if not self.elementi:
            return 0.0
        return float(max(e.N_max for e in self.elementi))


def calcola_postprocessing(
    elementi_struttura: list,  # list[ElementoStruttura]
    spostamenti_globali: np.ndarray,
    n_punti: int = 20,
) -> RisultatoPostProcessing:
    """Calcola i diagrammi M, V, N per tutti gli elementi.

    Usa il metodo equilibrio per elementi con carichi, Hermite altrimenti.

    Parametri
    ---------
    elementi_struttura : list[ElementoStruttura]
        Lista degli elementi con relative proprietà.
    spostamenti_globali : np.ndarray
        Vettore spostamenti globale.
    n_punti : int
        Punti di campionamento per elemento.

    Ritorna
    -------
    RisultatoPostProcessing
    """
    diagrammi: list[DiagrammiElemento] = []
    passaggi_globali: list[str] = []

    for es in elementi_struttura:
        elem = es.elemento
        if elem.id_nodo_iniziale is None or elem.id_nodo_finale is None:
            passaggi_globali.append(
                f"WARN: elemento '{elem.etichetta}' senza id nodo, saltato"
            )
            continue
        # Passa i carichi per usare il metodo equilibrio quando disponibili
        carichi = es.carichi if es.carichi else None
        diagr = calcola_diagrammi_elemento(
            elemento=elem,
            spostamenti_globali=spostamenti_globali,
            id_nodo_iniziale=int(elem.id_nodo_iniziale),
            id_nodo_finale=int(elem.id_nodo_finale),
            n_punti=n_punti,
            carichi=carichi,
        )
        diagrammi.append(diagr)

    passaggi_globali.append(
        f"Post-processing: {len(diagrammi)} elementi, {n_punti} punti/elemento"
    )

    return RisultatoPostProcessing(
        elementi=diagrammi,
        passaggi_calcolo=passaggi_globali,
    )
