"""Assemblaggio matrice di rigidezza globale sparsa per struttura beam 2D.

Ogni nodo ha 3 GDL: traslazione assiale u, traslazione trasversale v, rotazione θ.
Per un nodo con indice i, i GDL globali sono [3i, 3i+1, 3i+2].

Matrice globale costruita con scipy.sparse.lil_matrix durante il riempimento,
poi convertita a csr_matrix per l'efficienza della soluzione.

Unità attese:
- coordinate nodi : cm
- E : kg/cm²
- A : cm²
- I : cm⁴
- carichi distribuiti : kg/cm
- forze concentrate  : kg
- momenti           : kg·cm
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import numpy as np
from scipy.sparse import csr_matrix, lil_matrix

from .elemento_beam import BaseCaricoBeam, ElementoBeam

if TYPE_CHECKING:
    pass

_logger = logging.getLogger(__name__)


@dataclass
class Nodo:
    """Nodo della struttura piano con coordinate cartesiane.

    Attributi
    ---------
    id : int
        Indice del nodo (0-based). Deve essere unico nella struttura.
    x : float
        Coordinata X globale [cm].
    y : float
        Coordinata Y globale [cm].
    """

    id: int
    x: float
    y: float


@dataclass
class ElementoStruttura:
    """Elemento beam con eventuali carichi applicati.

    Attributi
    ---------
    elemento : ElementoBeam
        Geometria e proprietà dell'elemento (deve avere id_nodo_iniziale e id_nodo_finale).
    carichi : list[BaseCaricoBeam]
        Carichi applicati sull'elemento (default: vuoto).
    """

    elemento: ElementoBeam
    carichi: list[BaseCaricoBeam] = field(default_factory=list)


@dataclass
class RisultatoAssemblaggio:
    """Risultato dell'assemblaggio della matrice di rigidezza globale.

    Attributi
    ---------
    K_globale : csr_matrix
        Matrice di rigidezza globale sparsa (n_gdl × n_gdl) [kg/cm].
    F_globale : np.ndarray
        Vettore dei carichi globale (n_gdl,) [kg, kg·cm].
    n_gdl : int
        Numero totale di gradi di libertà (3 × n_nodi).
    n_nodi : int
        Numero di nodi della struttura.
    n_elementi : int
        Numero di elementi della struttura.
    non_zero : int
        Numero di elementi non-zero nella matrice globale.
    sparsita : float
        Percentuale di zeri sulla matrice (0–1).
    passaggi_calcolo : list[str]
        Log dei passaggi di assemblaggio.
    """

    K_globale: csr_matrix
    F_globale: np.ndarray
    n_gdl: int
    n_nodi: int
    n_elementi: int
    non_zero: int
    sparsita: float
    passaggi_calcolo: list[str]


def _dof_nodo(id_nodo: int) -> list[int]:
    """Ritorna i 3 GDL globali (u, v, θ) per un nodo con indice dato."""
    base = 3 * id_nodo
    return [base, base + 1, base + 2]


class Assemblatore:
    """Assembla la matrice di rigidezza globale sparsa e il vettore carichi.

    Esempio
    -------
    >>> nodi = [Nodo(0, 0.0, 0.0), Nodo(1, 600.0, 0.0)]
    >>> elem = ElementoBeam(E=30000.0, A=25.0, I=1000.0, L=600.0,
    ...                     id_nodo_iniziale=0, id_nodo_finale=1)
    >>> es = ElementoStruttura(elem, [CaricoDistribuitoUniforme(-2.0)])
    >>> ass = Assemblatore(nodi, [es])
    >>> ris = ass.assembla()
    """

    def __init__(
        self,
        nodi: list[Nodo],
        elementi: list[ElementoStruttura],
    ) -> None:
        self._nodi = list(nodi)
        self._elementi = list(elementi)
        self._valida_connettivita()

    def _valida_connettivita(self) -> None:
        """Verifica che tutti gli elementi abbiano id_nodo validi."""
        ids_nodi = {n.id for n in self._nodi}
        for es in self._elementi:
            elem = es.elemento
            if elem.id_nodo_iniziale is None or elem.id_nodo_finale is None:
                raise ValueError(
                    f"Elemento '{elem.etichetta}': id_nodo_iniziale e id_nodo_finale "
                    "devono essere impostati per l'assemblaggio."
                )
            if elem.id_nodo_iniziale not in ids_nodi:
                raise ValueError(
                    f"id_nodo_iniziale={elem.id_nodo_iniziale} non trovato tra i nodi."
                )
            if elem.id_nodo_finale not in ids_nodi:
                raise ValueError(
                    f"id_nodo_finale={elem.id_nodo_finale} non trovato tra i nodi."
                )

    def assembla(self) -> RisultatoAssemblaggio:
        """Assembla K_G (sparsa) e F_G, ritorna RisultatoAssemblaggio."""
        n_nodi = len(self._nodi)
        n_gdl = 3 * n_nodi
        passaggi: list[str] = []

        K = lil_matrix((n_gdl, n_gdl), dtype=float)
        F = np.zeros(n_gdl, dtype=float)

        passaggi.append(f"Struttura: {n_nodi} nodi, {len(self._elementi)} elementi")
        passaggi.append(f"GDL totali: {n_gdl} (3 per nodo: u, v, θ)")

        for es in self._elementi:
            elem = es.elemento
            i = int(elem.id_nodo_iniziale)  # type: ignore[arg-type]
            j = int(elem.id_nodo_finale)  # type: ignore[arg-type]

            dof_e = _dof_nodo(i) + _dof_nodo(j)  # 6 GDL dell'elemento

            # Matrice rigidezza globale dell'elemento (T^T k T)
            K_e = elem.matrice_rigidezza_globale()

            # Assemblaggio con scatter
            for r, gr in enumerate(dof_e):
                for s, gs in enumerate(dof_e):
                    K[gr, gs] += K_e[r, s]

            # Vettore carichi equivalenti in coordinate globali
            if es.carichi:
                f_loc = elem.combina_carichi(es.carichi).vettore_locale
                T = elem.matrice_trasformazione()
                f_glob = T.T @ f_loc
                for r, gr in enumerate(dof_e):
                    F[gr] += f_glob[r]

            passaggi.append(
                f"Elemento '{elem.etichetta}' nodi {i}→{j}: "
                f"DOF {dof_e}, {len(es.carichi)} carico/i"
            )

        K_csr = K.tocsr()
        non_zero = int(K_csr.nnz)
        sparsita = 1.0 - non_zero / (n_gdl * n_gdl) if n_gdl > 0 else 1.0

        passaggi.append(f"K_G assembla: {non_zero} nnz, sparsità {sparsita:.1%}")
        passaggi.append(f"Simmetria K_G: {_verifica_simmetria(K_csr)}")

        _logger.debug(
            "Assemblaggio completato: %d GDL, %d nnz, sparsità %.1f%%",
            n_gdl,
            non_zero,
            sparsita * 100,
        )

        return RisultatoAssemblaggio(
            K_globale=K_csr,
            F_globale=F,
            n_gdl=n_gdl,
            n_nodi=n_nodi,
            n_elementi=len(self._elementi),
            non_zero=non_zero,
            sparsita=sparsita,
            passaggi_calcolo=passaggi,
        )


def _verifica_simmetria(K: csr_matrix, tol: float = 1e-8) -> str:
    """Verifica che la matrice sia simmetrica (sola per diagnostica)."""
    diff = abs(K - K.T).max()
    if diff is None or diff < tol:
        return f"OK (|K - K^T|_max = {diff:.2e})"
    return f"NON SIMMETRICA (|K - K^T|_max = {diff:.2e})"
