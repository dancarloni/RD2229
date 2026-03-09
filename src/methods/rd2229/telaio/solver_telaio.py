"""Calcolo delle sollecitazioni (M, V, N) per ogni asta del telaio.

Partendo dai momenti agli estremi prodotti dall'algoritmo di Cross-Pozzati,
calcola le sollecitazioni alle 3 sezioni critiche di ogni asta:
    - Sezione 0: estremo i  (M_i, V_i, N_i)
    - Sezione 1: mezzeria   (M_mid, V_mid, N_mid)
    - Sezione 2: estremo j  (M_j, V_j, N_j)

e il diagramma completo M(x), V(x), N(x) su n_punti.

Unità: kg [forze], cm [geometria], kg·cm [momenti].

Riferimenti:
    Pozzati vol.II §3.9 — Determinazione degli sforzi nei telai risolti con Cross
    Santarella cap. Telai — Diagrammi M, T, N
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from .modello_telaio import (
    AstaTelaio,
    CaricoAsta,
    ModelloTelaio,
    TipoAsta,
    TipoCarico,
)
from .cross_pozzati import DatiCross, calcola_cross_pozzati


# ==============================================================================
# STRUTTURE DATI RISULTATO
# ==============================================================================

@dataclass
class SollecitazioniAsta:
    """Sollecitazioni di un'asta nelle 3 sezioni critiche + diagramma completo.

    Sezioni critiche:
        indice 0 = estremo i  (nodo_i dell'asta)
        indice 1 = mezzeria   (x = L/2)
        indice 2 = estremo j  (nodo_j dell'asta)

    Convenzione segni:
        M > 0: momento antiorario (tende fibre inferiori trave)
        V > 0: taglio verso il basso (convenzione trave, lato sinistro)
        N > 0: sforzo normale di trazione; N < 0: compressione

    Unità: kg·cm [M], kg [V, N]
    """
    id_asta: int
    etichetta: str
    L: float                            # lunghezza [cm]

    # Momenti finali da Cross (dati di base per i calcoli)
    M_cross_i: float                    # momento Cross all'estremo i [kg·cm]
    M_cross_j: float                    # momento Cross all'estremo j [kg·cm]

    # 3 sezioni critiche: (estremo_i, mezzeria, estremo_j)
    M: tuple[float, float, float]       # momenti flettenti [kg·cm]
    V: tuple[float, float, float]       # tagli [kg]
    N: tuple[float, float, float]       # sforzi normali [kg]

    # Diagramma completo (n_punti punti da x=0 a x=L)
    x_cm: list[float]
    M_kgcm: list[float]
    V_kg: list[float]
    N_kg: list[float]

    passaggi: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "id_asta": self.id_asta,
            "etichetta": self.etichetta,
            "L": round(self.L, 1),
            "M_cross_i": round(self.M_cross_i, 1),
            "M_cross_j": round(self.M_cross_j, 1),
            "M_i": round(self.M[0], 1),
            "M_mid": round(self.M[1], 1),
            "M_j": round(self.M[2], 1),
            "V_i": round(self.V[0], 1),
            "V_mid": round(self.V[1], 1),
            "V_j": round(self.V[2], 1),
            "N_i": round(self.N[0], 1),
            "N_mid": round(self.N[1], 1),
            "N_j": round(self.N[2], 1),
        }


@dataclass
class RisultatoCasoCarico:
    """Risultato completo per un caso di carico.

    Contiene i dati Cross (tabelle complete) e le sollecitazioni per ogni asta.
    """
    id_caso: str
    descrizione: str
    dati_cross: DatiCross
    sollecitazioni: dict[int, SollecitazioniAsta]   # {id_asta: SollecitazioniAsta}
    reazioni: dict[int, tuple[float, float, float]]  # {id_nodo: (H, V, M)} [kg, kg, kg·cm]
    passaggi: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "id_caso": self.id_caso,
            "descrizione": self.descrizione,
            "sollecitazioni": {
                str(k): v.to_dict() for k, v in self.sollecitazioni.items()
            },
            "convergenza": self.dati_cross.convergenza,
            "n_iterazioni": self.dati_cross.n_iterazioni,
        }


# ==============================================================================
# CALCOLO SOLLECITAZIONI PER TRAVE ORIZZONTALE
# ==============================================================================

def _carico_intensita_y(carico: CaricoAsta, x: float, L: float) -> float:
    """Intensità del carico verticale all'ascissa x [kg/cm]."""
    t = carico.tipo
    if t == TipoCarico.DISTRIBUITO_UNIFORME:
        return carico.valore_sx if carico.direzione == "Y" else 0.0
    elif t == TipoCarico.DISTRIBUITO_TRAPEZ:
        if carico.direzione != "Y":
            return 0.0
        w = carico.valore_sx + (carico.valore_dx - carico.valore_sx) * x / L
        return w
    elif t in (TipoCarico.PESO_PROPRIO,):
        return carico.valore_sx
    return 0.0


def _reazione_sinistra_trave(
    M_i: float, M_j: float, carichi: list[CaricoAsta], L: float,
    A: float, gamma: float, includi_pp: bool,
) -> float:
    """Calcola la reazione verticale al nodo i (V_i) da equilibrio globale.

    Equilibrio ΣM intorno a j = 0:
    V_i · L - M_i + M_j - Σ F_k · (L - a_k) - Σ q_k·L²/2 = 0
    V_i = [M_i - M_j + Σ F_k·(L - a_k) + Σ q_k·L²/2] / L

    Args:
        M_i, M_j:   momenti Cross agli estremi [kg·cm]
        carichi:    carichi sull'asta
        L:          lunghezza [cm]
        A, gamma:   per peso proprio automatico
        includi_pp: aggiunge peso proprio automatico
    """
    somma_mom_j = 0.0  # contributo dei carichi nel momento intorno a j

    # Peso proprio
    if includi_pp:
        w_pp = A * gamma
        somma_mom_j += w_pp * L**2 / 2.0

    for c in carichi:
        if c.tipo == TipoCarico.DISTRIBUITO_UNIFORME and c.direzione == "Y":
            w = c.valore_sx
            somma_mom_j += w * L**2 / 2.0
        elif c.tipo == TipoCarico.DISTRIBUITO_TRAPEZ and c.direzione == "Y":
            # Integrale ∫ q(x) · x_from_j dx = ∫ q(x) · (L-x) dx
            # q(x) = w_sx + (w_dx - w_sx) * x/L
            # ∫₀ᴸ [w_sx + Δw·x/L] · (L-x) dx = w_sx·L²/2 + Δw·L²/6
            delta_w = c.valore_dx - c.valore_sx
            somma_mom_j += c.valore_sx * L**2 / 2.0 + delta_w * L**2 / 6.0
        elif c.tipo == TipoCarico.CONCENTRATO and c.direzione == "Y":
            P = c.valore_sx
            a = c.posizione_a
            somma_mom_j += P * a  # braccio da j = a (da nodo i), forza intorno a j
        elif c.tipo == TipoCarico.PESO_PROPRIO:
            w_pp2 = c.valore_sx if c.valore_sx > 0 else A * gamma
            somma_mom_j += w_pp2 * L**2 / 2.0
            if includi_pp:
                # Evita doppio conteggio se già sommato sopra
                somma_mom_j -= A * gamma * L**2 / 2.0

    # Equilibrio: V_i · L - M_i + M_j - somma_mom_j = 0
    V_i = (M_i - M_j + somma_mom_j) / L
    return V_i


def _momento_trave_a_x(
    x: float, M_i: float, V_i: float,
    carichi: list[CaricoAsta], L: float,
    A: float, gamma: float, includi_pp: bool,
) -> float:
    """Momento flettente alla posizione x (da nodo i) per trave orizzontale.

    M(x) = M_i + V_i·x - Σ contributi_carichi(x)
    """
    M = M_i + V_i * x

    # Peso proprio
    if includi_pp:
        w_pp = A * gamma
        M -= w_pp * x**2 / 2.0

    for c in carichi:
        if c.tipo == TipoCarico.DISTRIBUITO_UNIFORME and c.direzione == "Y":
            M -= c.valore_sx * x**2 / 2.0
        elif c.tipo == TipoCarico.DISTRIBUITO_TRAPEZ and c.direzione == "Y":
            # q(x') = w_sx + Δw·x'/L  per 0 ≤ x' ≤ x
            # ∫₀ˣ q(x')·(x-x') dx' = w_sx·x²/2 + Δw·x³/(6L)
            delta_w = c.valore_dx - c.valore_sx
            M -= c.valore_sx * x**2 / 2.0 + delta_w * x**3 / (6.0 * L)
        elif c.tipo == TipoCarico.CONCENTRATO and c.direzione == "Y":
            a = c.posizione_a
            if x > a:
                M -= c.valore_sx * (x - a)
        elif c.tipo == TipoCarico.PESO_PROPRIO:
            w_pp2 = c.valore_sx if c.valore_sx > 0 else A * gamma
            M -= w_pp2 * x**2 / 2.0
            if includi_pp:
                M += A * gamma * x**2 / 2.0  # evita doppio conteggio

    return M


def calcola_sollecitazioni_trave(
    asta: AstaTelaio,
    M_i: float,
    M_j: float,
    N_i: float = 0.0,
    includi_pp: bool = True,
    n_punti: int = 21,
) -> SollecitazioniAsta:
    """Calcola sollecitazioni per trave orizzontale o inclinata.

    Per trave in c.a. monolitica, l'assiale è solitamente trascurabile
    (assunto N costante = N_i lungo tutta la trave).

    Args:
        asta:       asta (tipo TRAVE, MENSOLA, INCLINATA)
        M_i, M_j:  momenti Cross agli estremi [kg·cm]
        N_i:        sforzo normale [kg] (default 0 per travi)
        includi_pp: aggiunge peso proprio automatico
        n_punti:    punti per il diagramma

    Returns:
        SollecitazioniAsta con 3 sezioni + diagramma
    """
    passaggi: list[str] = []
    L = _lunghezza_asta(asta)

    V_i = _reazione_sinistra_trave(
        M_i, M_j, asta.carichi, L,
        asta.sezione.A, asta.sezione.gamma, includi_pp,
    )
    V_j = -V_i  # equilibrio: V_i + V_j + Σ carichi = 0 (approssimazione segni)

    # Correzione V_j per equilibrio verticale
    carico_tot = 0.0
    if includi_pp:
        carico_tot += asta.sezione.A * asta.sezione.gamma * L
    for c in asta.carichi:
        if c.tipo == TipoCarico.DISTRIBUITO_UNIFORME and c.direzione == "Y":
            carico_tot += c.valore_sx * L
        elif c.tipo == TipoCarico.DISTRIBUITO_TRAPEZ and c.direzione == "Y":
            carico_tot += (c.valore_sx + c.valore_dx) / 2.0 * L
        elif c.tipo == TipoCarico.CONCENTRATO and c.direzione == "Y":
            carico_tot += c.valore_sx
        elif c.tipo == TipoCarico.PESO_PROPRIO:
            w_pp = c.valore_sx if c.valore_sx > 0 else asta.sezione.A * asta.sezione.gamma
            carico_tot += w_pp * L
            if includi_pp:
                carico_tot -= asta.sezione.A * asta.sezione.gamma * L

    V_j = carico_tot - V_i  # equilibrio verticale

    # ---- Mezzeria ----
    x_mid = L / 2.0
    M_mid = _momento_trave_a_x(
        x_mid, M_i, V_i, asta.carichi, L,
        asta.sezione.A, asta.sezione.gamma, includi_pp,
    )
    V_mid = V_i  # costante tra carichi concentrati; approssimazione mezzeria
    # Taglio a mezzeria: V_i - carico distribuito fino a L/2
    V_mid = V_i
    if includi_pp:
        V_mid -= asta.sezione.A * asta.sezione.gamma * x_mid
    for c in asta.carichi:
        if c.tipo == TipoCarico.DISTRIBUITO_UNIFORME and c.direzione == "Y":
            V_mid -= c.valore_sx * x_mid
        elif c.tipo == TipoCarico.DISTRIBUITO_TRAPEZ and c.direzione == "Y":
            delta_w = c.valore_dx - c.valore_sx
            V_mid -= c.valore_sx * x_mid + delta_w * x_mid**2 / (2 * L)
        elif c.tipo == TipoCarico.CONCENTRATO and c.direzione == "Y":
            if c.posizione_a <= x_mid:
                V_mid -= c.valore_sx
        elif c.tipo == TipoCarico.PESO_PROPRIO:
            w_pp2 = c.valore_sx if c.valore_sx > 0 else asta.sezione.A * asta.sezione.gamma
            V_mid -= w_pp2 * x_mid
            if includi_pp:
                V_mid += asta.sezione.A * asta.sezione.gamma * x_mid

    passaggi.append(
        f"Trave {asta.etichetta}: M_i={M_i:.1f}, M_j={M_j:.1f} kg·cm, "
        f"V_i={V_i:.1f}, V_j={V_j:.1f} kg, M_mid={M_mid:.1f} kg·cm"
    )

    # ---- Diagramma ----
    xs = [i * L / (n_punti - 1) for i in range(n_punti)]
    Ms = [
        _momento_trave_a_x(x, M_i, V_i, asta.carichi, L,
                           asta.sezione.A, asta.sezione.gamma, includi_pp)
        for x in xs
    ]
    # Taglio: V(x) = V_i - ∫₀ˣ q(x')dx'
    Vs = []
    for x in xs:
        V_x = V_i
        if includi_pp:
            V_x -= asta.sezione.A * asta.sezione.gamma * x
        for c in asta.carichi:
            if c.tipo == TipoCarico.DISTRIBUITO_UNIFORME and c.direzione == "Y":
                V_x -= c.valore_sx * x
            elif c.tipo == TipoCarico.DISTRIBUITO_TRAPEZ and c.direzione == "Y":
                dw = c.valore_dx - c.valore_sx
                V_x -= c.valore_sx * x + dw * x**2 / (2 * L)
            elif c.tipo == TipoCarico.CONCENTRATO and c.direzione == "Y":
                if c.posizione_a < x:
                    V_x -= c.valore_sx
            elif c.tipo == TipoCarico.PESO_PROPRIO:
                w_pp2 = c.valore_sx if c.valore_sx > 0 else asta.sezione.A * asta.sezione.gamma
                V_x -= w_pp2 * x
                if includi_pp:
                    V_x += asta.sezione.A * asta.sezione.gamma * x
        Vs.append(V_x)

    Ns = [N_i] * n_punti

    return SollecitazioniAsta(
        id_asta=asta.id,
        etichetta=asta.etichetta,
        L=L,
        M_cross_i=M_i,
        M_cross_j=M_j,
        M=(M_i, M_mid, M_j),
        V=(V_i, V_mid, V_j),
        N=(N_i, N_i, N_i),
        x_cm=xs,
        M_kgcm=Ms,
        V_kg=Vs,
        N_kg=Ns,
        passaggi=passaggi,
    )


# ==============================================================================
# CALCOLO SOLLECITAZIONI PER PILASTRO VERTICALE
# ==============================================================================

def calcola_sollecitazioni_pilastro(
    asta: AstaTelaio,
    M_i: float,
    M_j: float,
    N_cumulativo: float,
    includi_pp: bool = True,
    n_punti: int = 21,
) -> SollecitazioniAsta:
    """Calcola sollecitazioni per pilastro verticale.

    Per pilastro verticale senza carichi trasversali:
        V = (M_j + M_i) / h  (taglio costante da equilibrio)
        N = N_cumulativo (da carichi dei piani superiori + peso proprio)
        M(y) = M_i + V · y  (lineare da base a sommità)

    Args:
        asta:           asta tipo PILASTRO o SETTO
        M_i, M_j:      momenti Cross (M_i = base, M_j = sommità) [kg·cm]
        N_cumulativo:  sforzo assiale cumulativo dal piano superiore [kg]
                       (positivo = compressione per pilastri)
        includi_pp:     aggiunge peso proprio del pilastro a N
        n_punti:        punti per il diagramma

    Returns:
        SollecitazioniAsta con 3 sezioni + diagramma
    """
    passaggi: list[str] = []
    L = _lunghezza_asta(asta)

    # Taglio costante nel pilastro: equilibrio del nodo
    # (M_base + M_sommità) / h
    V = (M_i + M_j) / L if L > 1e-10 else 0.0

    # Sforzo normale (compressione negativa per convenzione colonna)
    N_base = N_cumulativo
    if includi_pp:
        # Peso proprio pilastro aggiunto alla compressione alla base
        w_pp = asta.sezione.A * asta.sezione.gamma  # [kg/cm]
        N_pp = w_pp * L                              # [kg]
        N_base = N_cumulativo + N_pp

    N_sommita = N_cumulativo  # senza peso proprio del pilastro stesso

    # Momento a mezzeria
    M_mid = M_i + V * (L / 2.0)

    passaggi.append(
        f"Pilastro {asta.etichetta}: M_i={M_i:.1f}, M_j={M_j:.1f} kg·cm, "
        f"V={V:.1f} kg, N_base={N_base:.1f} kg"
    )

    # ---- Diagramma ----
    xs = [i * L / (n_punti - 1) for i in range(n_punti)]
    Ms = [M_i + V * x for x in xs]
    Vs = [V] * n_punti
    # N decresce dalla base alla sommità (si scarica il peso proprio)
    Ns = [N_base - asta.sezione.A * asta.sezione.gamma * x * (1 if includi_pp else 0)
          for x in xs]

    return SollecitazioniAsta(
        id_asta=asta.id,
        etichetta=asta.etichetta,
        L=L,
        M_cross_i=M_i,
        M_cross_j=M_j,
        M=(M_i, M_mid, M_j),
        V=(V, V, V),
        N=(N_base, (N_base + N_sommita) / 2, N_sommita),
        x_cm=xs,
        M_kgcm=Ms,
        V_kg=Vs,
        N_kg=Ns,
        passaggi=passaggi,
    )


# ==============================================================================
# CALCOLO SFORZI NORMALI (EQUILIBRIO VERTICALE GLOBALE)
# ==============================================================================

def calcola_sforzi_normali_colonne(
    modello: ModelloTelaio,
    sollecitazioni_travi: dict[int, SollecitazioniAsta],
) -> dict[int, float]:
    """Calcola lo sforzo normale cumulativo per ogni colonna, piano per piano.

    Per ogni colonna, N = somma dei carichi verticali trasmessi dalle travi
    ai nodi superiori della colonna, accumulati dall'alto verso il basso.

    Args:
        modello:               modello del telaio
        sollecitazioni_travi:  {id_asta: SollecitazioniAsta} per le travi

    Returns:
        {id_asta_colonna: N_cumulativo [kg]}  (positivo = compressione)
    """
    N_col: dict[int, float] = {}

    # Per ogni colonna, la reazione verticale delle travi al nodo superiore
    # è V_j della trave a destra + V_i della trave a sinistra del nodo
    # (pesi delle travi già inclusi nelle V dei singoli elementi)
    piani = sorted(modello.piani, key=lambda p: p.id_piano, reverse=True)

    # Accumulo dall'alto verso il basso
    # N_nodo[id_nodo] = sforzo verticale cumulativo al nodo
    N_nodo: dict[int, float] = {n.id: 0.0 for n in modello.nodi}

    for piano in piani:
        # Travi di questo piano: i loro V trasmettono carichi ai nodi
        for asta in modello.travi_piano(piano.id_piano):
            sol = sollecitazioni_travi.get(asta.id)
            if sol is None:
                continue
            # V_i agisce verso il basso sul nodo i (reazione = V_i verso l'alto)
            # V_j agisce verso il basso sul nodo j
            N_nodo[asta.nodo_i] += sol.V[0]   # contributo reazione al nodo i
            N_nodo[asta.nodo_j] += sol.V[2]   # contributo reazione al nodo j

    # Assegna N alle colonne (dalla somma al nodo superiore della colonna)
    for piano in piani:
        for col in modello.colonne_piano(piano.id_piano):
            # Nodo superiore della colonna
            ni = modello.nodo_by_id(col.nodo_i)
            nj = modello.nodo_by_id(col.nodo_j)
            # Il nodo superiore è quello con quota maggiore
            nodo_sup = nj if nj.y >= ni.y else ni
            N_col[col.id] = N_nodo.get(nodo_sup.id, 0.0)
            # Trasmetti al nodo inferiore per accumulare con piani sottostanti
            nodo_inf = ni if nodo_sup == nj else nj
            N_nodo[nodo_inf.id] += N_col[col.id]

    return N_col


# ==============================================================================
# ORCHESTRATORE PRINCIPALE
# ==============================================================================

def calcola_sollecitazioni_da_cross(
    modello: ModelloTelaio,
    dati_cross: DatiCross,
    includi_pp: bool = True,
    n_punti: int = 21,
) -> dict[int, SollecitazioniAsta]:
    """Calcola le sollecitazioni (M, V, N) per ogni asta dai momenti di Cross.

    Args:
        modello:    modello del telaio
        dati_cross: risultato dell'algoritmo Cross-Pozzati
        includi_pp: include peso proprio nelle reazioni
        n_punti:    punti per il diagramma

    Returns:
        {id_asta: SollecitazioniAsta}
    """
    sollecitazioni: dict[int, SollecitazioniAsta] = {}

    # ---- Fase 1: Travi ----
    for asta in modello.aste:
        if asta.tipo not in (TipoAsta.TRAVE, TipoAsta.MENSOLA, TipoAsta.INCLINATA):
            continue
        M_i, M_j = dati_cross.momenti_finali[asta.id]
        sol = calcola_sollecitazioni_trave(
            asta=asta, M_i=M_i, M_j=M_j,
            N_i=0.0, includi_pp=includi_pp, n_punti=n_punti,
        )
        sollecitazioni[asta.id] = sol

    # ---- Fase 2: Sforzi normali colonne (da reazioni travi) ----
    N_colonne = calcola_sforzi_normali_colonne(modello, sollecitazioni)

    # ---- Fase 3: Pilastri / Setti ----
    for asta in modello.aste:
        if asta.tipo not in (TipoAsta.PILASTRO, TipoAsta.SETTO):
            continue
        M_i, M_j = dati_cross.momenti_finali[asta.id]
        N_cum = N_colonne.get(asta.id, 0.0)
        sol = calcola_sollecitazioni_pilastro(
            asta=asta, M_i=M_i, M_j=M_j,
            N_cumulativo=N_cum, includi_pp=includi_pp, n_punti=n_punti,
        )
        sollecitazioni[asta.id] = sol

    return sollecitazioni


def _lunghezza_asta(asta: AstaTelaio) -> float:
    """Calcola la lunghezza di un'asta dai nodi (richiede il modello).
    Wrapper: la lunghezza è calcolata esternamente e passata all'asta.
    Qui è usata una stima da b/h come fallback."""
    # Il modello non è passato direttamente qui per semplicità
    # La lunghezza viene recuperata dalla SezioneTelaio.extra se disponibile
    L = asta.sezione.extra.get("L_asta", None)
    if L is not None:
        return float(L)
    # Fallback: non dovrebbe mai arrivare qui se il modello è corretto
    raise ValueError(
        f"Lunghezza non disponibile per asta {asta.etichetta}. "
        "Usare calcola_sollecitazioni_da_cross con ModelloTelaio."
    )


# ==============================================================================
# CALCOLO CASO DI CARICO COMPLETO
# ==============================================================================

def calcola_caso_carico(
    modello: ModelloTelaio,
    id_caso: str,
    descrizione: str,
    forze_orizzontali_per_piano: dict[int, float] | None = None,
    includi_pp: bool = True,
    tolleranza: float = 0.5,
    max_iter: int = 200,
    n_punti: int = 21,
) -> RisultatoCasoCarico:
    """Calcola un caso di carico completo: Cross + sollecitazioni + reazioni.

    Args:
        modello:                     modello del telaio
        id_caso:                     identificatore del caso (es. "LC1", "LC3")
        descrizione:                 descrizione testuale
        forze_orizzontali_per_piano: {id_piano: F_orizz [kg]} per sisma ondulatorio
                                     None = caso statico (no sway forzato)
        includi_pp:                  include peso proprio
        tolleranza, max_iter:        parametri di convergenza Cross
        n_punti:                     punti diagramma

    Returns:
        RisultatoCasoCarico con dati Cross + sollecitazioni + reazioni
    """
    passaggi: list[str] = [f"=== Caso {id_caso}: {descrizione} ==="]

    # ---- Cross ----
    dati_cross = calcola_cross_pozzati(
        modello=modello,
        forze_orizzontali_per_piano=forze_orizzontali_per_piano,
        includi_peso_proprio=includi_pp,
        tolleranza=tolleranza,
        max_iter=max_iter,
    )

    # ---- Sollecitazioni ----
    # Patch: inietta L nelle sezioni per il calcolo delle sollecitazioni
    for asta in modello.aste:
        asta.sezione.extra["L_asta"] = modello.lunghezza_asta(asta.id)

    # Calcolo sollecitazioni travi
    sollecitazioni_travi: dict[int, SollecitazioniAsta] = {}
    for asta in modello.aste:
        if asta.tipo not in (TipoAsta.TRAVE, TipoAsta.MENSOLA, TipoAsta.INCLINATA):
            continue
        M_i, M_j = dati_cross.momenti_finali[asta.id]
        L = modello.lunghezza_asta(asta.id)
        sol = calcola_sollecitazioni_trave(
            asta=asta, M_i=M_i, M_j=M_j, N_i=0.0,
            includi_pp=includi_pp, n_punti=n_punti,
        )
        sollecitazioni_travi[asta.id] = sol

    # Sforzi normali colonne
    N_colonne = calcola_sforzi_normali_colonne(modello, sollecitazioni_travi)

    # Sollecitazioni colonne
    sollecitazioni_colonne: dict[int, SollecitazioniAsta] = {}
    for asta in modello.aste:
        if asta.tipo not in (TipoAsta.PILASTRO, TipoAsta.SETTO):
            continue
        M_i, M_j = dati_cross.momenti_finali[asta.id]
        N_cum = N_colonne.get(asta.id, 0.0)
        sol = calcola_sollecitazioni_pilastro(
            asta=asta, M_i=M_i, M_j=M_j,
            N_cumulativo=N_cum, includi_pp=includi_pp, n_punti=n_punti,
        )
        sollecitazioni_colonne[asta.id] = sol

    sollecitazioni_all = {**sollecitazioni_travi, **sollecitazioni_colonne}

    # ---- Reazioni ----
    reazioni = _calcola_reazioni(modello, sollecitazioni_all, dati_cross)

    passaggi.extend(dati_cross.passaggi)
    passaggi.append(f"Sollecitazioni calcolate per {len(sollecitazioni_all)} aste")

    return RisultatoCasoCarico(
        id_caso=id_caso,
        descrizione=descrizione,
        dati_cross=dati_cross,
        sollecitazioni=sollecitazioni_all,
        reazioni=reazioni,
        passaggi=passaggi,
    )


def _calcola_reazioni(
    modello: ModelloTelaio,
    sollecitazioni: dict[int, SollecitazioniAsta],
    dati_cross: DatiCross,
) -> dict[int, tuple[float, float, float]]:
    """Calcola le reazioni ai vincoli (H, V, M) per ogni nodo vincolato."""
    reazioni: dict[int, tuple[float, float, float]] = {}

    for nodo in modello.nodi:
        bx, by, bt = nodo.vincolo.gdl_bloccati
        if not (bx or by or bt):
            continue

        H = 0.0
        V = 0.0
        M_reaz = 0.0

        # Somma contributi delle aste convergenti al nodo
        for asta in modello.aste_per_nodo(nodo.id):
            sol = sollecitazioni.get(asta.id)
            if sol is None:
                continue
            if asta.nodo_i == nodo.id:
                # Nodo è l'estremo i: le reazioni sono V_i e N_i
                V += sol.V[0]
                H += sol.N[0]  # approssimazione: N non contribuisce a H per travi orizz.
                M_reaz += dati_cross.momenti_finali[asta.id][0]
            else:
                # Nodo è l'estremo j
                V += sol.V[2]
                H += sol.N[2]
                M_reaz += dati_cross.momenti_finali[asta.id][1]

        reazioni[nodo.id] = (round(H, 1), round(V, 1), round(M_reaz, 1))

    return reazioni
