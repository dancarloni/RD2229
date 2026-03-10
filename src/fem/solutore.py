"""Soluzione del sistema lineare FEM (M.4).

Risolve il sistema K_G · u = F_G ridotto con `scipy.sparse.linalg.spsolve`.
Fornisce logging diagnostico (tempo, norma residuo) e gestione degli errori.

Utilizzo tipico::

    from src.fem.solutore import SolutoreFEMSparso, RisultatoSoluzione

    risultato = SolutoreFEMSparso().risolvi(K_rid, F_rid, gdl_liberi, n_totale)
    u_completo = risultato.spostamenti_completi
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass

import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla

logger = logging.getLogger("rd2229.fem.solutore")


@dataclass
class RisultatoSoluzione:
    """Risultato della soluzione del sistema FEM.

    Attributi
    ---------
    spostamenti_completi : np.ndarray
        Vettore spostamenti nodali globale [n_gdl_totale].
        GDL vincolati sono impostati a zero.
    norma_residuo : float
        ||K·u_rid - F_rid|| (norma L2 del residuo sulla parte ridotta).
    tempo_soluzione_s : float
        Tempo di soluzione in secondi.
    n_gdl_totale : int
        Numero totale di GDL del sistema originale.
    n_gdl_liberi : int
        Numero di GDL liberi usati nella soluzione.
    passaggi_calcolo : list[str]
        Traccia dei passaggi principali per il tabulato di calcolo.
    """

    spostamenti_completi: np.ndarray
    norma_residuo: float
    tempo_soluzione_s: float
    n_gdl_totale: int
    n_gdl_liberi: int
    passaggi_calcolo: list[str]

    def to_dict(self) -> dict[str, object]:
        return {
            "n_gdl_totale": self.n_gdl_totale,
            "n_gdl_liberi": self.n_gdl_liberi,
            "norma_residuo": round(float(self.norma_residuo), 12),
            "tempo_soluzione_s": round(self.tempo_soluzione_s, 6),
            "passaggi_calcolo": self.passaggi_calcolo,
        }


class SolutoreFEMSparso:
    """Risolve il sistema FEM sparso ridotto K_rid · u_rid = F_rid.

    Parametri
    ---------
    calcola_condizionamento : bool
        Se True calcola il numero di condizionamento (costoso, solo per debug).
    """

    def __init__(self, *, calcola_condizionamento: bool = False) -> None:
        self.calcola_condizionamento = calcola_condizionamento

    def risolvi(
        self,
        K_rid: sp.csr_matrix,
        F_rid: np.ndarray,
        gdl_liberi: list[int],
        n_gdl_totale: int,
    ) -> RisultatoSoluzione:
        """Risolve il sistema lineare ridotto e ricostruisce il vettore completo.

        Parametri
        ---------
        K_rid : sp.csr_matrix
            Matrice di rigidezza ridotta (GDL vincolati già rimossi).
        F_rid : np.ndarray
            Vettore carichi ridotto.
        gdl_liberi : list[int]
            Indici GDL liberi nel sistema globale.
        n_gdl_totale : int
            Numero totale di GDL (inclusi quelli vincolati).

        Ritorna
        -------
        RisultatoSoluzione
        """
        passaggi: list[str] = []
        n_lib = K_rid.shape[0]

        logger.info(
            "Soluzione sistema FEM: %d GDL liberi su %d totali.",
            n_lib,
            n_gdl_totale,
        )

        if n_lib == 0:
            raise ValueError(
                "Nessun GDL libero: la struttura è completamente vincolata. "
                "Verificare i vincoli applicati."
            )

        passaggi.append(f"Sistema lineare: {n_lib} × {n_lib}")
        passaggi.append("Solver: scipy.sparse.linalg.spsolve")

        # Verifica che la matrice non sia singolare (rango pieno)
        # Controllo leggero: diagonale vicina a zero indica problemi
        diagonale = K_rid.diagonal()
        diag_max = float(np.max(np.abs(diagonale))) + 1e-30
        if np.any(np.abs(diagonale) < 1e-10 * diag_max):
            raise ValueError(
                "Matrice K_G ridotta ha elementi diagonali nulli o quasi-nulli. "
                "Verificare che le condizioni al contorno siano sufficienti "
                "a eliminare i modi rigidi della struttura."
            )

        if self.calcola_condizionamento:
            try:
                cond = np.linalg.cond(K_rid.toarray())
                logger.info("Numero di condizionamento K_G ridotta: %.3e", cond)
                passaggi.append(f"Numero di condizionamento: {cond:.3e}")
            except Exception:
                logger.warning("Calcolo condizionamento fallito.")

        t_start = time.perf_counter()
        try:
            u_rid = spla.spsolve(K_rid, F_rid)
        except Exception as exc:
            raise RuntimeError(
                f"spsolve fallito: {exc}. "
                "Probabile causa: matrice singolare (struttura labille o BC insufficienti)."
            ) from exc
        t_fine = time.perf_counter()
        tempo = t_fine - t_start

        # Norma residuo
        residuo = np.asarray(K_rid @ u_rid - F_rid, dtype=float).ravel()
        norma_residuo = float(np.linalg.norm(residuo))

        logger.info(
            "Soluzione completata in %.4f s — ||r|| = %.3e",
            tempo,
            norma_residuo,
        )
        passaggi.append(f"Tempo soluzione: {tempo:.4f} s")
        passaggi.append(f"Norma residuo ||K·u - F||: {norma_residuo:.3e}")

        # Ricostruzione vettore completo
        u_completo = np.zeros(n_gdl_totale, dtype=float)
        for i_rid, i_glob in enumerate(gdl_liberi):
            u_completo[i_glob] = u_rid[i_rid]

        return RisultatoSoluzione(
            spostamenti_completi=u_completo,
            norma_residuo=norma_residuo,
            tempo_soluzione_s=tempo,
            n_gdl_totale=n_gdl_totale,
            n_gdl_liberi=n_lib,
            passaggi_calcolo=passaggi,
        )
