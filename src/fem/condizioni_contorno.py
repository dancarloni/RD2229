"""Applicazione delle condizioni al contorno a una struttura beam 2D.

Supporta due metodi:
- Eliminazione diretta : righe e colonne dei GDL vincolati vengono rimosse.
  Risulta in una matrice ridotta di rango pieno (se i vincoli sono sufficienti).
- Metodo penalty      : grandi valori sulla diagonale impongono il vincolo.
  Più semplice da implementare ma può peggiorare il numero di condizionamento.

GDL per nodo: [3i] = u (assiale), [3i+1] = v (trasversale), [3i+2] = θ (rotazione).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Literal

import numpy as np
from scipy.sparse import csr_matrix

_logger = logging.getLogger(__name__)

# Fattore penalty (dimensionalmente coerente, deve dominare la rigidezza)
_PENALTY_DEFAULT = 1.0e18


class TipoVincolo(Enum):
    """Tipo di vincolo nodale.

    Valori
    ------
    INCASTRO    : u=0, v=0, θ=0 (3 GDL bloccati)
    CERNIERA    : u=0, v=0  (libera rotazione)
    CARRELLO_V  : v=0  (bloccato in direzione trasversale; libero assiale)
    CARRELLO_U  : u=0  (bloccato in direzione assiale; libero trasversale)
    LIBERO      : nessun vincolo (nodo interno o estremità libera)
    """

    INCASTRO = "incastro"
    CERNIERA = "cerniera"
    CARRELLO_V = "carrello_v"
    CARRELLO_U = "carrello_u"
    LIBERO = "libero"


@dataclass
class Vincolo:
    """Vincolo applicato a un nodo della struttura.

    Attributi
    ---------
    id_nodo : int
        Indice del nodo (0-based).
    tipo : TipoVincolo
        Tipo di vincolo cinematico.
    """

    id_nodo: int
    tipo: TipoVincolo


@dataclass
class RisultatoBC:
    """Risultato dell'applicazione delle condizioni al contorno.

    Attributi
    ---------
    K_ridotta : csr_matrix
        Matrice di rigidezza ridotta (solo GDL liberi).
    F_ridotta : np.ndarray
        Vettore carichi ridotto (solo GDL liberi).
    gdl_liberi : list[int]
        Indici globali dei GDL liberi (non vincolati), ordinati.
    gdl_vincolati : list[int]
        Indici globali dei GDL vincolati (= 0 nella soluzione finale).
    metodo : str
        Metodo usato: "eliminazione" | "penalty".
    passaggi_calcolo : list[str]
        Log dei passaggi di applicazione BC.
    """

    K_ridotta: csr_matrix
    F_ridotta: np.ndarray
    gdl_liberi: list[int]
    gdl_vincolati: list[int]
    metodo: str
    passaggi_calcolo: list[str]


def _gdl_vincolati_da_vincolo(id_nodo: int, tipo: TipoVincolo) -> list[int]:
    """Ritorna i GDL globali bloccati da un vincolo."""
    base = 3 * id_nodo
    u, v, theta = base, base + 1, base + 2
    if tipo == TipoVincolo.INCASTRO:
        return [u, v, theta]
    if tipo == TipoVincolo.CERNIERA:
        return [u, v]
    if tipo == TipoVincolo.CARRELLO_V:
        return [v]
    if tipo == TipoVincolo.CARRELLO_U:
        return [u]
    return []  # LIBERO


def applica_condizioni_contorno(
    K: csr_matrix,
    F: np.ndarray,
    vincoli: list[Vincolo],
    *,
    metodo: Literal["eliminazione", "penalty"] = "eliminazione",
    penalty: float = _PENALTY_DEFAULT,
) -> RisultatoBC:
    """Applica le condizioni al contorno alla matrice globale.

    Parametri
    ---------
    K : csr_matrix
        Matrice di rigidezza globale assemblata.
    F : np.ndarray
        Vettore carichi globale.
    vincoli : list[Vincolo]
        Lista dei vincoli nodali.
    metodo : {"eliminazione", "penalty"}
        Metodo di applicazione BC.
    penalty : float
        Valore penalty da porre sulla diagonale (solo metodo "penalty").

    Ritorna
    -------
    RisultatoBC
    """
    n_gdl = K.shape[0]
    passaggi: list[str] = []

    gdl_vincolati_set: set[int] = set()
    for vincolo in vincoli:
        gdl_v = _gdl_vincolati_da_vincolo(vincolo.id_nodo, vincolo.tipo)
        gdl_vincolati_set.update(gdl_v)
        passaggi.append(
            f"Nodo {vincolo.id_nodo} {vincolo.tipo.value}: GDL {gdl_v} vincolati"
        )

    gdl_vincolati = sorted(gdl_vincolati_set)
    gdl_liberi = [g for g in range(n_gdl) if g not in gdl_vincolati_set]

    passaggi.append(
        f"GDL liberi: {len(gdl_liberi)}, vincolati: {len(gdl_vincolati)}"
    )

    if metodo == "eliminazione":
        K_ridotta, F_ridotta = _elimina_gdl(K, F, gdl_liberi)
        passaggi.append("Metodo: eliminazione diretta (righe/colonne rimosse)")
    else:
        K_ridotta, F_ridotta = _applica_penalty(K, F, gdl_vincolati, penalty)
        gdl_liberi = list(range(n_gdl))  # tutti i GDL rimangono
        passaggi.append(f"Metodo: penalty (valore = {penalty:.2e})")

    _logger.debug(
        "BC applicate: %d GDL liberi, %d vincolati, metodo=%s",
        len(gdl_liberi),
        len(gdl_vincolati),
        metodo,
    )

    return RisultatoBC(
        K_ridotta=K_ridotta,
        F_ridotta=F_ridotta,
        gdl_liberi=gdl_liberi,
        gdl_vincolati=gdl_vincolati,
        metodo=metodo,
        passaggi_calcolo=passaggi,
    )


def _elimina_gdl(
    K: csr_matrix,
    F: np.ndarray,
    gdl_liberi: list[int],
) -> tuple[csr_matrix, np.ndarray]:
    """Estrae la sotto-matrice e sotto-vettore relativi ai GDL liberi."""
    idx = np.array(gdl_liberi, dtype=int)
    K_denso = K.toarray()
    K_rid = K_denso[np.ix_(idx, idx)]
    F_rid = F[idx]
    return csr_matrix(K_rid), F_rid


def _applica_penalty(
    K: csr_matrix,
    F: np.ndarray,
    gdl_vincolati: list[int],
    penalty: float,
) -> tuple[csr_matrix, np.ndarray]:
    """Impone i vincoli con il metodo penalty."""
    K_lil = K.tolil()
    F_pen = F.copy()
    for gdl in gdl_vincolati:
        K_lil[gdl, gdl] += penalty
        F_pen[gdl] = 0.0  # spostamento vincolato = 0
    return K_lil.tocsr(), F_pen
