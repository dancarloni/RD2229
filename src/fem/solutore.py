"""Soluzione del sistema lineare FEM con scipy.sparse.linalg.spsolve.

Ricostruisce il vettore spostamento completo (tutti i GDL) dopo la soluzione
sul sistema ridotto. Registra norma del residuo e, facoltativamente, numero
di condizionamento.

Unità:
- spostamenti assiali/trasversali : cm
- rotazioni                       : rad
- residuo                         : [stessa unità del vettore F]
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field

import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import MatrixRankWarning, spsolve

from .condizioni_contorno import RisultatoBC

_logger = logging.getLogger(__name__)


@dataclass
class RisultatoSoluzione:
    """Risultato della soluzione del sistema lineare FEM.

    Attributi
    ---------
    spostamenti : np.ndarray
        Vettore spostamenti completo (tutti i GDL, con zeri per i vincolati).
    norma_residuo : float
        ||K · u - F||₂ (sul sistema ridotto) — misura dell'errore numerico.
    converged : bool
        True se la norma del residuo è sotto la soglia di tolleranza.
    n_gdl_totale : int
        Dimensione del vettore spostamenti completo.
    n_gdl_liberi : int
        Dimensione del sistema ridotto effettivamente risolto.
    tempo_soluzione_s : float
        Tempo di CPU impiegato da spsolve [s].
    numero_condizionamento : float | None
        Numero di condizionamento stimato (None se non richiesto).
    passaggi_calcolo : list[str]
        Log dei passaggi della soluzione.
    """

    spostamenti: np.ndarray
    norma_residuo: float
    converged: bool
    n_gdl_totale: int
    n_gdl_liberi: int
    tempo_soluzione_s: float
    numero_condizionamento: float | None = None
    passaggi_calcolo: list[str] = field(default_factory=list)


def risolvi(
    ris_bc: RisultatoBC,
    n_gdl_totale: int,
    *,
    tolleranza_residuo: float = 1e-6,
    calcola_condizionamento: bool = False,
) -> RisultatoSoluzione:
    """Risolve il sistema lineare K_rid · u_rid = F_rid con spsolve.

    Parametri
    ---------
    ris_bc : RisultatoBC
        Risultato dell'applicazione delle condizioni al contorno.
    n_gdl_totale : int
        Numero totale di GDL (dimensione vettore soluzione completo).
    tolleranza_residuo : float
        Soglia relativa per il flag `converged`: converged se
        ||residuo|| < tolleranza_residuo * (||F_rid|| + 1).
    calcola_condizionamento : bool
        Se True, stima il numero di condizionamento (costoso per matrici grandi).

    Ritorna
    -------
    RisultatoSoluzione

    Eccezioni
    ---------
    ValueError
        Se la matrice ridotta è singolare (struttura labile o BC insufficienti).
    """
    K_rid = ris_bc.K_ridotta
    F_rid = ris_bc.F_ridotta
    gdl_liberi = ris_bc.gdl_liberi
    passaggi: list[str] = []

    if K_rid.shape[0] == 0:
        raise ValueError(
            "Sistema ridotto vuoto: tutti i GDL sono vincolati. "
            "Verificare le condizioni al contorno."
        )

    passaggi.append(f"Sistema ridotto: {K_rid.shape[0]} × {K_rid.shape[1]} GDL liberi")

    cond = None
    if calcola_condizionamento:
        try:
            from scipy.sparse.linalg import norm as spnorm

            norm_K = float(spnorm(K_rid, "fro"))
            norm_Kinv = float(spnorm(spsolve(K_rid, np.eye(K_rid.shape[0])), "fro"))
            cond = norm_K * norm_Kinv
        except Exception:  # noqa: BLE001
            pass
        if cond is not None:
            passaggi.append(f"Numero condizionamento stimato: {cond:.3e}")
            if cond > 1e12:
                _logger.warning(
                    "Numero di condizionamento elevato (%.3e): struttura con "
                    "rigidezze molto diverse o mal condizionata.",
                    cond,
                )

    t0 = time.perf_counter()
    try:
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("error", MatrixRankWarning)
            u_rid = spsolve(K_rid, F_rid)
    except MatrixRankWarning as exc:
        raise ValueError(
            "Matrice di rigidezza singolare: la struttura è labile o le "
            "condizioni al contorno sono insufficienti."
        ) from exc
    tempo = time.perf_counter() - t0

    # Ricostruisci vettore completo con zeri per GDL vincolati
    spostamenti = np.zeros(n_gdl_totale, dtype=float)
    for k, gdl in enumerate(gdl_liberi):
        spostamenti[gdl] = float(u_rid[k])

    # Calcolo norma residuo sul sistema ridotto
    residuo = float(np.linalg.norm(K_rid @ u_rid - F_rid))
    converged = residuo < tolleranza_residuo * (float(np.linalg.norm(F_rid)) + 1.0)

    passaggi.append(f"Soluzione: tempo={tempo*1000:.2f} ms, ||residuo||={residuo:.3e}")
    passaggi.append(f"Converged: {converged}")

    _logger.debug(
        "Soluzione FEM: %d GDL liberi, residuo=%.3e, tempo=%.2f ms",
        len(gdl_liberi),
        residuo,
        tempo * 1000,
    )

    return RisultatoSoluzione(
        spostamenti=spostamenti,
        norma_residuo=residuo,
        converged=converged,
        n_gdl_totale=n_gdl_totale,
        n_gdl_liberi=len(gdl_liberi),
        tempo_soluzione_s=tempo,
        numero_condizionamento=cond,
        passaggi_calcolo=passaggi,
    )
