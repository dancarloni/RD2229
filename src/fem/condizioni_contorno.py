"""Applicazione condizioni al contorno (M.3).

Implementa l'applicazione delle condizioni al contorno (vincoli) per il
sistema FEM globale, con due metodi alternativi:

1. **Eliminazione diretta**: rimozione esatta di righe/colonne dei GDL vincolati.
   Produce una matrice ridotta non singolare. Metodo predefinito.
2. **Penalty**: sostituzione del termine diagonale con un valore elevato.
   Più semplice ma peggiora il numero di condizionamento.

Unità coerenti con il resto del modulo fem/:
- GDL assiali (u): cm, kg, kg/cm
- GDL trasversali (v): cm, kg, kg/cm
- GDL rotazionali (θ): rad, kg·cm, kg·cm/rad
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Sequence

import numpy as np
import scipy.sparse as sp

logger = logging.getLogger("rd2229.fem.condizioni_contorno")


class TipoVincolo(Enum):
    """Tipi di vincolo per un nodo del telaio piano 2D."""

    LIBERO = auto()
    """Nessun vincolo: tutti e 3 i GDL sono liberi."""

    INCASTRO = auto()
    """Incastro: u=0, v=0, θ=0 (3 GDL vincolati)."""

    CERNIERA = auto()
    """Cerniera: u=0, v=0 (traslazioni vincolate, rotazione libera)."""

    CARRELLO_V = auto()
    """Carrello con guida verticale: v=0 (traslazione verticale vincolata)."""

    CARRELLO_U = auto()
    """Carrello con guida orizzontale: u=0 (traslazione orizzontale vincolata)."""


@dataclass(frozen=True)
class VincoloNodo:
    """Vincolo applicato a un nodo specifico.

    Attributi
    ---------
    id_nodo : int
        Indice del nodo vincolato (0-based).
    tipo : TipoVincolo
        Tipo di vincolo da applicare.
    gdl_base : int
        Indice del primo GDL del nodo nel vettore globale (= id_nodo * 3).
    """

    id_nodo: int
    tipo: TipoVincolo

    @property
    def gdl_base(self) -> int:
        return self.id_nodo * 3

    @property
    def gdl_vincolati(self) -> list[int]:
        """Lista degli indici GDL globali vincolati da questo vincolo."""
        b = self.gdl_base
        if self.tipo == TipoVincolo.INCASTRO:
            return [b, b + 1, b + 2]
        if self.tipo == TipoVincolo.CERNIERA:
            return [b, b + 1]
        if self.tipo == TipoVincolo.CARRELLO_V:
            return [b + 1]
        if self.tipo == TipoVincolo.CARRELLO_U:
            return [b]
        return []


@dataclass
class ApplicatoreBC:
    """Applica le condizioni al contorno a K_G e F_G.

    Parametri
    ---------
    vincoli : list[VincoloNodo]
        Lista dei vincoli da applicare.
    metodo : str
        "eliminazione" (default) o "penalty".
    penalty_factor : float
        Fattore moltiplicativo per il metodo penalty (default 1e12).
    """

    vincoli: list[VincoloNodo]
    metodo: str = "eliminazione"
    penalty_factor: float = 1.0e12

    def __post_init__(self) -> None:
        if self.metodo not in {"eliminazione", "penalty"}:
            raise ValueError(
                f"metodo deve essere 'eliminazione' o 'penalty', ricevuto '{self.metodo}'."
            )

    @property
    def gdl_vincolati(self) -> list[int]:
        """Lista ordinata e senza duplicati di tutti i GDL vincolati."""
        tutti: set[int] = set()
        for vincolo in self.vincoli:
            tutti.update(vincolo.gdl_vincolati)
        return sorted(tutti)

    def applica(
        self, K: sp.csr_matrix, F: np.ndarray
    ) -> tuple[sp.csr_matrix, np.ndarray, list[int], list[int]]:
        """Applica le condizioni al contorno.

        Ritorna
        -------
        K_rid : sp.csr_matrix
            Matrice ridotta (o penalizzata) pronta per spsolve.
        F_rid : np.ndarray
            Vettore carichi ridotto (o penalizzato).
        gdl_liberi : list[int]
            Indici GDL liberi (presenti in K_rid) — solo per metodo "eliminazione".
        gdl_vincolati : list[int]
            Indici GDL vincolati rimossi (o penalizzati).
        """
        vincolati = self.gdl_vincolati
        n = K.shape[0]
        liberi = [i for i in range(n) if i not in set(vincolati)]

        logger.debug(
            "BC %s: %d GDL totali, %d vincolati, %d liberi.",
            self.metodo,
            n,
            len(vincolati),
            len(liberi),
        )

        if self.metodo == "eliminazione":
            return self._eliminazione(K, F, liberi, vincolati)
        return self._penalty(K, F, liberi, vincolati)

    def _eliminazione(
        self,
        K: sp.csr_matrix,
        F: np.ndarray,
        liberi: list[int],
        vincolati: list[int],
    ) -> tuple[sp.csr_matrix, np.ndarray, list[int], list[int]]:
        """Eliminazione diretta: estrae la sottomatrice dei GDL liberi."""
        idx = np.array(liberi, dtype=int)
        K_rid = K[idx[:, None], idx]
        if not sp.issparse(K_rid):
            K_rid = sp.csr_matrix(K_rid)
        else:
            K_rid = K_rid.tocsr()
        F_rid = F[idx]
        return K_rid, F_rid, liberi, vincolati

    def _penalty(
        self,
        K: sp.csr_matrix,
        F: np.ndarray,
        liberi: list[int],
        vincolati: list[int],
    ) -> tuple[sp.csr_matrix, np.ndarray, list[int], list[int]]:
        """Metodo penalty: sostituisce la diagonale dei GDL vincolati."""
        K_lil = K.tolil()
        F_out = F.copy()
        pf = self.penalty_factor
        for gdl in vincolati:
            K_lil[gdl, :] = 0.0
            K_lil[:, gdl] = 0.0
            K_lil[gdl, gdl] = pf
            F_out[gdl] = 0.0
        K_rid = K_lil.tocsr()
        n = K_rid.shape[0]
        return K_rid, F_out, list(range(n)), vincolati

    def ricostruisci_spostamenti(
        self, u_rid: np.ndarray, gdl_liberi: list[int], n_totale: int
    ) -> np.ndarray:
        """Ricostruisce il vettore spostamenti completo (GDL vincolati = 0).

        Parametri
        ---------
        u_rid : np.ndarray
            Vettore soluzione ridotto (solo GDL liberi).
        gdl_liberi : list[int]
            Indici dei GDL liberi.
        n_totale : int
            Numero totale di GDL del sistema originale.

        Ritorna
        -------
        u_completo : np.ndarray
            Vettore spostamenti [n_totale], con zero ai GDL vincolati.
        """
        u_completo = np.zeros(n_totale, dtype=float)
        for i_rid, i_glob in enumerate(gdl_liberi):
            u_completo[i_glob] = u_rid[i_rid]
        return u_completo
