"""Assemblaggio matrice di rigidezza globale sparsa (M.2).

Costruisce la matrice di rigidezza globale K_G e il vettore dei carichi F_G
per un telaio piano 2D con elementi beam Euler-Bernoulli.

Struttura dati:
- NodoFEM: posizione (x, y) e indice GDL base (3 GDL per nodo: u, v, θ)
- ElementoFEM: riferimento ai nodi i/j + elemento beam locale
- Assemblatore: costruisce K_G (scipy.sparse.lil_matrix) e F_G

Unità attese (coerenti con elemento_beam.py):
- coordinate nodali: cm
- K_G: kg/cm, kg, kg·cm (dipende dal GDL)
- F_G: kg, kg·cm
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Sequence

import numpy as np
import scipy.sparse as sp

from .elemento_beam import BaseCaricoBeam, ElementoBeam

logger = logging.getLogger("rd2229.fem.assemblaggio")


@dataclass
class NodoFEM:
    """Nodo di un telaio piano 2D.

    Attributi
    ---------
    id : int
        Identificatore univoco del nodo (0-based).
    x : float
        Coordinata x [cm].
    y : float
        Coordinata y [cm].
    """

    id: int
    x: float
    y: float

    @property
    def gdl_base(self) -> int:
        """Indice del primo GDL del nodo nel vettore globale (3 GDL per nodo)."""
        return self.id * 3

    @property
    def indici_gdl(self) -> tuple[int, int, int]:
        """Indici (u, v, θ) del nodo nel vettore globale."""
        b = self.gdl_base
        return (b, b + 1, b + 2)


@dataclass
class ElementoFEM:
    """Elemento beam nel contesto del telaio globale.

    Attributi
    ---------
    id : int
        Identificatore univoco dell'elemento (0-based).
    nodo_i : NodoFEM
        Nodo iniziale.
    nodo_j : NodoFEM
        Nodo finale.
    beam : ElementoBeam
        Elemento locale con proprietà meccaniche.
    carichi : list[BaseCaricoBeam]
        Carichi applicati a questo elemento.
    """

    id: int
    nodo_i: NodoFEM
    nodo_j: NodoFEM
    beam: ElementoBeam
    carichi: list[BaseCaricoBeam] = field(default_factory=list)

    @property
    def indici_gdl_globali(self) -> list[int]:
        """I 6 indici GDL globali dell'elemento [u_i, v_i, θ_i, u_j, v_j, θ_j]."""
        ui, vi, ti = self.nodo_i.indici_gdl
        uj, vj, tj = self.nodo_j.indici_gdl
        return [ui, vi, ti, uj, vj, tj]

    @staticmethod
    def da_nodi(
        id: int,
        nodo_i: NodoFEM,
        nodo_j: NodoFEM,
        E: float,
        A: float,
        I: float,
        carichi: list[BaseCaricoBeam] | None = None,
        etichetta: str = "",
    ) -> "ElementoFEM":
        """Costruisce un ElementoFEM dai due nodi, calcolando L e angolo automaticamente."""
        dx = nodo_j.x - nodo_i.x
        dy = nodo_j.y - nodo_i.y
        import math

        L = math.hypot(dx, dy)
        if L == 0.0:
            raise ValueError(
                f"Elemento {id}: i nodi {nodo_i.id} e {nodo_j.id} coincidono."
            )
        angolo = math.atan2(dy, dx)
        beam = ElementoBeam(
            E=E,
            A=A,
            I=I,
            L=L,
            angolo=angolo,
            unita_angolo="rad",
            id_nodo_iniziale=nodo_i.id,
            id_nodo_finale=nodo_j.id,
            etichetta=etichetta,
        )
        return ElementoFEM(
            id=id,
            nodo_i=nodo_i,
            nodo_j=nodo_j,
            beam=beam,
            carichi=carichi or [],
        )


@dataclass
class Assemblatore:
    """Assembla la matrice di rigidezza globale K_G e il vettore carichi F_G.

    Utilizzo::

        asm = Assemblatore(nodi, elementi)
        K_csr, F_g = asm.assembla()

    La matrice K_G viene costruita in formato lil_matrix per efficienza
    di riempimento, poi convertita a csr_matrix prima della soluzione.
    """

    nodi: list[NodoFEM]
    elementi: list[ElementoFEM]

    @property
    def n_gdl(self) -> int:
        """Numero totale di GDL.

        Dimensionato in base al massimo id di NodoFEM, assumendo che gli
        indici di GDL siano derivati come ``NodoFEM.id * 3 + {0,1,2}``.
        """
        if not self.nodi:
            return 0

        max_id = max(nodo.id for nodo in self.nodi)
        n_gdl = 3 * (max_id + 1)

        # Se gli id non sono contigui, il numero effettivo di nodi può essere
        # diverso da max_id + 1. In tal caso dimensioniamo comunque sui GDL
        # effettivamente utilizzati, evitando accessi fuori range.
        if max_id + 1 != len(self.nodi):
            logger.debug(
                "Assemblatore.n_gdl: nodi non contigui (len(nodi)=%d, max_id=%d); "
                "dimensione GDL calcolata come %d.",
                len(self.nodi),
                max_id,
                n_gdl,
            )

        return n_gdl
    def assembla(self) -> tuple[sp.csr_matrix, np.ndarray]:
        """Assembla K_G (csr_matrix) e F_G (array 1D).

        Ritorna
        -------
        K_csr : scipy.sparse.csr_matrix
            Matrice di rigidezza globale simmetrica [n_gdl × n_gdl].
        F_g : np.ndarray
            Vettore dei carichi globale [n_gdl].
        """
        n = self.n_gdl
        K_lil: sp.lil_matrix = sp.lil_matrix((n, n), dtype=float)
        F_g = np.zeros(n, dtype=float)

        logger.debug(
            "Assemblaggio: %d nodi, %d elementi, %d GDL totali.",
            len(self.nodi),
            len(self.elementi),
            n,
        )

        for elem in self.elementi:
            K_e_glob = elem.beam.matrice_rigidezza_globale()
            indici = elem.indici_gdl_globali

            # Assemblaggio K_G
            for i_loc, i_glob in enumerate(indici):
                for j_loc, j_glob in enumerate(indici):
                    K_lil[i_glob, j_glob] += K_e_glob[i_loc, j_loc]

            # Assemblaggio F_G dai carichi equivalenti locali
            if elem.carichi:
                f_eq_loc = elem.beam.combina_carichi(elem.carichi).vettore_locale
                T_e = elem.beam.matrice_trasformazione()
                # Trasformazione in coordinate globali: f_glob = T_e^T * f_loc
                f_eq_glob = T_e.T @ f_eq_loc
                for i_loc, i_glob in enumerate(indici):
                    F_g[i_glob] += f_eq_glob[i_loc]

        K_csr = K_lil.tocsr()

        nnz = K_csr.nnz
        sparsita = 1.0 - nnz / (n * n) if n > 0 else 1.0
        logger.info(
            "K_G assemblata: shape=%s, nnz=%d, sparsità=%.2f%%",
            K_csr.shape,
            nnz,
            sparsita * 100.0,
        )

        return K_csr, F_g

    def aggiungi_carico_nodale(
        self, F_g: np.ndarray, id_nodo: int, forze: Sequence[float]
    ) -> None:
        """Aggiunge un carico nodale diretto a F_G.

        Parametri
        ---------
        F_g : np.ndarray
            Vettore globale da modificare in-place.
        id_nodo : int
            Identificatore del nodo ricevente.
        forze : sequence di 3 float
            [Fx, Fy, M] nel sistema globale.
        """
        nodo = self.nodi[id_nodo]
        ui, vi, ti = nodo.indici_gdl
        F_g[ui] += float(forze[0])
        F_g[vi] += float(forze[1])
        F_g[ti] += float(forze[2])
