"""Momenti di Incastro Perfetto (MIP) — formule per il metodo di Cross-Pozzati.

Calcola i momenti fissi agli estremi di ogni asta per tutti i tipi di carico
previsti nel modulo telai (RD 2229/39).

Convenzione segni (Pozzati / Santarella):
  M_i < 0  →  momento orario al nodo i (fibre superiori tese)
  M_j > 0  →  momento antiorario al nodo j (fibre inferiori tese)
  Per carico uniforme verso il basso su trave orizzontale:
    M_i = -wL²/12   M_j = +wL²/12

Riferimenti:
  Santarella "Il Cemento Armato", Tavola 9 — Momenti di incastro perfetto
  Pozzati "Teoria e Tecnica delle Strutture" vol.II §3.4
  Belluzzi "Scienza delle Costruzioni" vol.II

Unità: kg [forze], cm [geometria], kg·cm [momenti].
"""

from __future__ import annotations

import math
from typing import Optional

from .modello_telaio import AstaTelaio, CaricoAsta, TipoCarico


# ==============================================================================
# FORMULE MIP ELEMENTARI
# ==============================================================================

def mip_uniforme(w: float, L: float) -> tuple[float, float]:
    """MIP per carico distribuito uniforme verso il basso su trave incastrata.

    Formula (Santarella Tab.9 caso 1, Pozzati §3.4):
        M_i = -w·L²/12
        M_j = +w·L²/12

    Args:
        w:  intensità del carico distribuito [kg/cm]
        L:  luce dell'asta [cm]

    Returns:
        (M_i, M_j) [kg·cm]
    """
    if L <= 0:
        raise ValueError(f"Lunghezza asta non valida: L={L} cm")
    val = w * L**2 / 12.0
    return (-val, +val)


def mip_concentrato(P: float, a: float, L: float) -> tuple[float, float]:
    """MIP per carico concentrato a distanza 'a' dal nodo i.

    Formula (Santarella Tab.9 caso 2, Pozzati §3.4):
        b = L - a
        M_i = -P·a·b²/L²
        M_j = +P·a²·b/L²

    Args:
        P:  forza concentrata [kg]
        a:  distanza dal nodo i [cm] (0 < a < L)
        L:  luce dell'asta [cm]

    Returns:
        (M_i, M_j) [kg·cm]

    Note:
        Carico al centro (a = L/2): M_i = -PL/8, M_j = +PL/8
    """
    if L <= 0:
        raise ValueError(f"Lunghezza asta non valida: L={L} cm")
    if not (0.0 <= a <= L):
        raise ValueError(f"Posizione carico a={a} cm fuori dall'asta (0 ÷ {L})")
    b = L - a
    M_i = -P * a * b**2 / L**2
    M_j = +P * a**2 * b / L**2
    return (M_i, M_j)


def mip_triangolare_crescente(w_max: float, L: float) -> tuple[float, float]:
    """MIP per carico triangolare crescente da zero a w_max (zero al nodo i).

    Utile come componente della decomposizione trapezoidale.

    Formula (Santarella Tab.9 caso 4):
        M_i = -w_max·L²/20
        M_j = +w_max·L²/30

    Args:
        w_max:  intensità massima al nodo j [kg/cm]
        L:      luce dell'asta [cm]

    Returns:
        (M_i, M_j) [kg·cm]
    """
    if L <= 0:
        raise ValueError(f"Lunghezza asta non valida: L={L} cm")
    M_i = -w_max * L**2 / 20.0
    M_j = +w_max * L**2 / 30.0
    return (M_i, M_j)


def mip_triangolare_decrescente(w_max: float, L: float) -> tuple[float, float]:
    """MIP per carico triangolare decrescente da w_max a zero (max al nodo i).

    Formula (simmetria con mip_triangolare_crescente, invertendo i nodi):
        M_i = -w_max·L²/30
        M_j = +w_max·L²/20   (con inversione segni per simmetria)
    Ovvero, applicando la simmetria:
        M_i = -w_max·L²/30
        M_j = +w_max·L²/20   → NO: la simmetria richiede cambio di segno.

    Derivazione corretta per carico triangolare decrescente (max in i, zero in j):
        M_i = -w_max·L²/20   (corretto con cambio di orientamento)
        M_j = +w_max·L²/30   → per w_max in j: M_i = -wL²/20, M_j = +wL²/30

    Nota: per carico triangolare con max in i (decrescente verso j):
        M_i = -w_max·L²/30
        M_j = +w_max·L²/20

    Riferimento: Santarella Tab.9 caso 5 (speculare al caso 4).

    Args:
        w_max:  intensità massima al nodo i [kg/cm]
        L:      luce dell'asta [cm]

    Returns:
        (M_i, M_j) [kg·cm]
    """
    if L <= 0:
        raise ValueError(f"Lunghezza asta non valida: L={L} cm")
    # Carico triangolare con max in i, zero in j: simmetrico al caso crescente
    # Applicando la simmetria: inversione nodi i↔j e inversione segni
    # Caso crescente (zero in i, max in j): M_i = -wL²/20, M_j = +wL²/30
    # Caso decrescente (max in i, zero in j): M_i = -wL²/30, M_j = +wL²/20
    M_i = -w_max * L**2 / 30.0
    M_j = +w_max * L**2 / 20.0
    return (M_i, M_j)


def mip_trapezoidale(w_sx: float, w_dx: float, L: float) -> tuple[float, float]:
    """MIP per carico trapezoidale (w_sx al nodo i, w_dx al nodo j).

    Decomposizione (Pozzati §3.4):
        Uniforme: w = w_sx                → mip_uniforme(w_sx, L)
        Triangolare crescente: Δw = w_dx - w_sx → mip_triangolare_crescente(Δw, L)
    Se Δw < 0 (carico decrescente): lo stesso schema funziona per sovrapposizione.

    Args:
        w_sx:  intensità al nodo i [kg/cm]
        w_dx:  intensità al nodo j [kg/cm]
        L:     luce dell'asta [cm]

    Returns:
        (M_i, M_j) [kg·cm]
    """
    M_unif = mip_uniforme(w_sx, L)
    delta_w = w_dx - w_sx
    if abs(delta_w) > 1e-10:
        if delta_w > 0:
            # carico triangolare crescente (zero in i, delta in j)
            M_tri = mip_triangolare_crescente(delta_w, L)
        else:
            # delta_w < 0: carico triangolare con componente negativa (verso l'alto)
            # da 0 in i a |delta_w| verso l'alto in j
            # = negativo di mip_triangolare_crescente(|delta_w|)
            M_tri_pos = mip_triangolare_crescente(abs(delta_w), L)
            M_tri = (-M_tri_pos[0], -M_tri_pos[1])
        return (
            M_unif[0] + M_tri[0],
            M_unif[1] + M_tri[1],
        )
    return M_unif


def mip_momento_nodale(
    M_esterno: float,
    al_nodo_i: bool,
    L: float,
) -> tuple[float, float]:
    """MIP per momento esterno applicato direttamente al nodo i o j.

    Quando un momento esterno è applicato al nodo i:
        Il nodo i riceve direttamente M_esterno, con carry-over a j:
        M_i = +M_esterno (già incluso nel MIP del nodo)
        M_j = +M_esterno / 2 (carry-over)
    Quando è applicato al nodo j (simmetrico):
        M_i = +M_esterno / 2
        M_j = +M_esterno

    Nota: nella pratica del metodo Cross, un momento applicato a un nodo
    libero viene incluso nello squilibrio iniziale di quel nodo,
    non trasformato in MIP. Questo metodo è per momenti a nodi fissi
    (incastri, pattini).

    Riferimento: Pozzati vol.II §3.5.

    Args:
        M_esterno: momento applicato [kg·cm] (positivo = antiorario)
        al_nodo_i: True se applicato a nodo i, False se a nodo j
        L:         luce dell'asta [cm] (non usata ma per coerenza)

    Returns:
        (M_i, M_j) [kg·cm]
    """
    if al_nodo_i:
        return (+M_esterno, +M_esterno / 2.0)
    else:
        return (+M_esterno / 2.0, +M_esterno)


def mip_cedimento(
    delta: float,
    E: float,
    I: float,
    L: float,
) -> tuple[float, float]:
    """MIP per cedimento relativo di appoggio δ (traslazione relativa).

    Formula (Pozzati vol.II §3.4, Belluzzi):
        M_i = M_j = -6·E·I·δ / L²   (entrambi uguali, stessa convenzione)

    Usato per la correzione sway: applicando un cedimento unitario δ=1 cm
    alle colonne di un piano, si ottengono i MIP di sway.

    Args:
        delta:  cedimento relativo [cm] (spostamento relativo tra i due nodi)
        E:      modulo elastico [kg/cm²]
        I:      momento d'inerzia [cm⁴]
        L:      luce dell'asta [cm]

    Returns:
        (M_i, M_j) [kg·cm] — entrambi dello stesso segno (negativo per δ>0)
    """
    if L <= 0:
        raise ValueError(f"Lunghezza asta non valida: L={L} cm")
    val = -6.0 * E * I * delta / L**2
    return (val, val)


# ==============================================================================
# CALCOLO MIP GLOBALE PER ASTA
# ==============================================================================

def calcola_mip_asta(
    asta: AstaTelaio,
    L: float,
    includi_peso_proprio: bool = True,
) -> dict:
    """Calcola il MIP totale per un'asta sommando tutti i contributi di carico.

    Somma i contributi di tutti i carichi applicati all'asta più il peso
    proprio se richiesto.

    Args:
        asta:                  asta del telaio
        L:                     lunghezza dell'asta [cm]
        includi_peso_proprio:  se True aggiunge automaticamente il peso proprio
                               (carico uniforme w_pp = A × gamma)

    Returns:
        dict con:
            "M_i":        MIP totale al nodo i [kg·cm]
            "M_j":        MIP totale al nodo j [kg·cm]
            "contributi": lista di dict per audit/tabulato
            "passaggi":   lista di stringhe descrittive

    Note:
        Carichi di tipo PESO_PROPRIO presenti esplicitamente nell'asta
        hanno priorità sul calcolo automatico (includi_peso_proprio non aggiunge
        un secondo contributo se già presente).
    """
    M_i_tot = 0.0
    M_j_tot = 0.0
    contributi: list[dict] = []
    passaggi: list[str] = []
    ha_peso_proprio_esplicito = any(
        c.tipo == TipoCarico.PESO_PROPRIO for c in asta.carichi
    )

    # ---- Peso proprio automatico ----
    if includi_peso_proprio and not ha_peso_proprio_esplicito:
        w_pp = asta.sezione.A * asta.sezione.gamma  # [kg/cm]
        if w_pp > 1e-12:
            M_i, M_j = mip_uniforme(w_pp, L)
            M_i_tot += M_i
            M_j_tot += M_j
            contributi.append({
                "descrizione": "Peso proprio",
                "tipo": "peso_proprio",
                "w": round(w_pp, 4),
                "L": round(L, 1),
                "formula": "±wL²/12",
                "M_i": round(M_i, 1),
                "M_j": round(M_j, 1),
            })
            passaggi.append(
                f"  PP: w={w_pp:.4f} kg/cm → M_i={M_i:.1f}, M_j={M_j:.1f} kg·cm"
            )

    # ---- Carichi espliciti ----
    for carico in asta.carichi:
        M_i, M_j = _mip_carico_singolo(carico, L, asta.sezione)
        M_i_tot += M_i
        M_j_tot += M_j

        label = _etichetta_carico(carico)
        contributi.append({
            "descrizione": label,
            "tipo": carico.tipo.value,
            "valore_sx": carico.valore_sx,
            "valore_dx": carico.valore_dx,
            "posizione_a": carico.posizione_a,
            "L": round(L, 1),
            "formula": _formula_carico(carico),
            "M_i": round(M_i, 1),
            "M_j": round(M_j, 1),
        })
        passaggi.append(
            f"  {label}: M_i={M_i:.1f}, M_j={M_j:.1f} kg·cm"
        )

    passaggi.append(
        f"  TOTALE: M_i={M_i_tot:.1f}, M_j={M_j_tot:.1f} kg·cm"
    )

    return {
        "M_i": M_i_tot,
        "M_j": M_j_tot,
        "contributi": contributi,
        "passaggi": passaggi,
    }


def _mip_carico_singolo(
    carico: CaricoAsta,
    L: float,
    sezione=None,
) -> tuple[float, float]:
    """Calcola il MIP per un singolo carico."""
    t = carico.tipo

    if t == TipoCarico.DISTRIBUITO_UNIFORME:
        return mip_uniforme(carico.valore_sx, L)

    elif t == TipoCarico.DISTRIBUITO_TRAPEZ:
        return mip_trapezoidale(carico.valore_sx, carico.valore_dx, L)

    elif t == TipoCarico.CONCENTRATO:
        return mip_concentrato(carico.valore_sx, carico.posizione_a, L)

    elif t == TipoCarico.MOMENTO_NODO:
        return mip_momento_nodale(carico.valore_sx, carico.al_nodo_i, L)

    elif t == TipoCarico.PESO_PROPRIO:
        if sezione is not None:
            w_pp = sezione.A * sezione.gamma
        else:
            w_pp = carico.valore_sx  # valore_sx usato come w_pp esplicito
        return mip_uniforme(w_pp, L)

    else:
        raise ValueError(f"Tipo carico non riconosciuto: {t}")


def _etichetta_carico(carico: CaricoAsta) -> str:
    """Etichetta descrittiva per il tabulato."""
    t = carico.tipo
    if t == TipoCarico.DISTRIBUITO_UNIFORME:
        return f"Distr. uniforme q={carico.valore_sx:.3g} kg/cm"
    elif t == TipoCarico.DISTRIBUITO_TRAPEZ:
        return (
            f"Distr. trapez. q_i={carico.valore_sx:.3g}, "
            f"q_j={carico.valore_dx:.3g} kg/cm"
        )
    elif t == TipoCarico.CONCENTRATO:
        return f"Concentrato P={carico.valore_sx:.3g} kg @ a={carico.posizione_a:.1f} cm"
    elif t == TipoCarico.MOMENTO_NODO:
        nodo = "i" if carico.al_nodo_i else "j"
        return f"Momento nodo {nodo} M={carico.valore_sx:.3g} kg·cm"
    elif t == TipoCarico.PESO_PROPRIO:
        return f"Peso proprio w={carico.valore_sx:.4g} kg/cm"
    return carico.tipo.value


def _formula_carico(carico: CaricoAsta) -> str:
    """Formula MIP per il tabulato storico."""
    t = carico.tipo
    if t in (TipoCarico.DISTRIBUITO_UNIFORME, TipoCarico.PESO_PROPRIO):
        return "±wL²/12"
    elif t == TipoCarico.DISTRIBUITO_TRAPEZ:
        return "uniforme + triangolare"
    elif t == TipoCarico.CONCENTRATO:
        return "M_i = -Pab²/L², M_j = +Pa²b/L²"
    elif t == TipoCarico.MOMENTO_NODO:
        return "M_vicino + M/2 carry-over"
    return ""
