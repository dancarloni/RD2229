"""Metodo di Cross-Pozzati — distribuzione dei momenti (RD 2229/39).

Implementa l'algoritmo iterativo di Hardy Cross (1930) nella trattazione italiana
di Pozzati per il calcolo di telai piani iperstatici in c.a.:

1. Calcolo rigidezze k e fattori di distribuzione μ
2. Calcolo momenti di incastro perfetto (MIP) per ogni asta caricata
3. Distribuzione iterativa No-Sway (frame bloccato alla traslazione)
4. Correzione Sway multi-piano (Pozzati vol.II §3.8):
   - Analisi sway unitario per ogni piano → sistema n×n
   - Risoluzione e sovrapposizione dei contributi
5. Produzione tabelle storiche complete (formato Santarella/Pozzati)

Convenzione segni (Pozzati):
    M > 0  →  momento antiorario al nodo (tende fibre inferiori per trave)
    M < 0  →  momento orario al nodo (tende fibre superiori per trave)
    MIP: M_i < 0, M_j > 0 per carico verticale verso il basso su trave

Unità: kg [forze], cm [geometria], kg·cm [momenti].

Riferimenti:
    Pozzati, C. "Teoria e Tecnica delle Strutture" vol.II, §3.3–3.8, UTET
    Santarella, L. "Il Cemento Armato" vol.I, cap. Telai, Hoepli
    Hardy Cross, "Analysis of Continuous Frames by Distributing Fixed-End Moments",
    ASCE Transactions, 1930
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .carichi_fissi import calcola_mip_asta, mip_cedimento
from .modello_telaio import AstaTelaio, ModelloTelaio

# ==============================================================================
# STRUTTURE DATI RISULTATO
# ==============================================================================


@dataclass
class RigaIterazioneCross:
    """Singola riga nella tabella storica del metodo di Cross.

    Rappresenta una riga della classica tabella a colonne (una per fine asta):
        - tipo "MIP":   momenti di incastro perfetto iniziali
        - tipo "dist":  incrementi di distribuzione
        - tipo "t/o":   incrementi di trasporto (carry-over)
        - tipo "totale": somma finale
    """

    numero: int  # 0 = MIP, 1,2,... = iterazione, -1 = totale
    tipo: str  # "MIP", "dist", "t/o", "totale"
    # Momenti per ogni fine asta — chiave: "{etichetta_asta}_{i|j}"
    # es. {"AB_i": -6250.0, "AB_j": +3125.0, "BA_i": 0.0, ...}
    momenti: dict[str, float]

    def to_dict(self) -> dict:
        return {
            "numero": self.numero,
            "tipo": self.tipo,
            "momenti": {k: round(v, 1) for k, v in self.momenti.items()},
        }


@dataclass
class DatiCross:
    """Tabelle complete del metodo di Cross — tutto auditabile dall'utente.

    Contiene:
    - Tabella rigidezze k per ogni asta
    - Tabella fattori di distribuzione μ per ogni nodo
    - Tabella MIP con dettaglio contributi per carico
    - Tabella iterazioni Cross (formato storico Santarella)
    - Momenti finali agli estremi di ogni asta

    Corrisponde esattamente alle tabelle presentate nel Santarella e nel Pozzati.
    """

    # Chiave riga: id_asta
    rigidezze_from_i: dict[int, float]  # k vista da nodo_i [kg·cm/rad]
    rigidezze_from_j: dict[int, float]  # k vista da nodo_j [kg·cm/rad]
    lunghezze: dict[int, float]  # L per ogni asta [cm]

    # {id_nodo: {id_asta: μ}}
    fattori_distribuzione: dict[int, dict[int, float]]

    # MIP: {id_asta: (M_i, M_j)} [kg·cm]
    mip: dict[int, tuple[float, float]]
    mip_dettaglio: dict[int, dict]  # audit contributi per asta

    # Tabella iterazioni storiche (da visualizzare)
    iterazioni: list[RigaIterazioneCross]

    # Momenti finali agli estremi: {id_asta: (M_i, M_j)} [kg·cm]
    momenti_finali: dict[int, tuple[float, float]]

    # Diagnostica
    n_iterazioni: int
    errore_residuo: float  # max|momento_squilibrato| all'ultima iterazione
    convergenza: bool
    passaggi: list[str]

    # Intestazione colonne per la tabella storica
    # Lista di str tipo ["AB_i", "AB_j", "BA_i", "BA_j", ...]
    intestazioni_colonne: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "rigidezze_from_i": {str(k): round(v, 0) for k, v in self.rigidezze_from_i.items()},
            "rigidezze_from_j": {str(k): round(v, 0) for k, v in self.rigidezze_from_j.items()},
            "fattori_distribuzione": {
                str(nodo): {str(asta): round(mu, 4) for asta, mu in aste.items()}
                for nodo, aste in self.fattori_distribuzione.items()
            },
            "mip": {str(k): [round(v, 1) for v in vv] for k, vv in self.mip.items()},
            "momenti_finali": {
                str(k): [round(v, 1) for v in vv] for k, vv in self.momenti_finali.items()
            },
            "n_iterazioni": self.n_iterazioni,
            "errore_residuo": round(self.errore_residuo, 2),
            "convergenza": self.convergenza,
            "iterazioni": [r.to_dict() for r in self.iterazioni],
        }


# ==============================================================================
# STEP 1 — RIGIDEZZE
# ==============================================================================


def calcola_rigidezze(
    modello: ModelloTelaio,
) -> tuple[dict[int, float], dict[int, float], dict[int, float]]:
    """Calcola le rigidezze k per ogni asta e le lunghezze.

    k dipende dal nodo LONTANO (far end):
        k_from_i = rilascio_j.k_factor × E × I / L   (vista dal nodo i)
        k_from_j = rilascio_i.k_factor × E × I / L   (vista dal nodo j)

    Se TipoAsta.PENDOLO: k = 0 per entrambi i lati.

    Args:
        modello: modello del telaio

    Returns:
        (k_from_i, k_from_j, lunghezze) — dict con chiave id_asta
    """
    k_i: dict[int, float] = {}
    k_j: dict[int, float] = {}
    lunghezze: dict[int, float] = {}

    for asta in modello.aste:
        L = modello.lunghezza_asta(asta.id)
        lunghezze[asta.id] = L
        if L < 1e-10:
            raise ValueError(f"Asta {asta.etichetta} (id={asta.id}): lunghezza nulla")
        k_i[asta.id] = asta.rigidezza_from_i(L)
        k_j[asta.id] = asta.rigidezza_from_j(L)

    return k_i, k_j, lunghezze


# ==============================================================================
# STEP 2 — FATTORI DI DISTRIBUZIONE
# ==============================================================================


def calcola_fattori_distribuzione(
    modello: ModelloTelaio,
    k_from_i: dict[int, float],
    k_from_j: dict[int, float],
) -> dict[int, dict[int, float]]:
    """Calcola i fattori di distribuzione μ per ogni nodo libero.

    Per ogni nodo J libero (rotazione non bloccata):
        k_J   = Σ k_Ji  (somma rigidezze di tutte le aste convergenti in J)
        μ_Ji  = k_Ji / k_J   per ogni asta Ji

    Verifica: Σ μ_Ji = 1 per ogni nodo libero.

    Nodi con vincolo INCASTRO o PATTINO: rotazione bloccata → non partecipano.
    Nodi con CERNIERA, CARRELLO, BIPENDOLO, LIBERO: rotazione libera → partecipano.

    Args:
        modello:    modello del telaio
        k_from_i:   rigidezze viste dal nodo i (per ogni asta)
        k_from_j:   rigidezze viste dal nodo j

    Returns:
        {id_nodo: {id_asta: μ}}  solo per nodi liberi (θ non bloccato)
    """
    # Mappa: id_nodo → {id_asta: k_contributo}
    k_per_nodo: dict[int, dict[int, float]] = {}

    for asta in modello.aste:
        # Contributo al nodo i (usando k vista dal nodo i)
        ni = modello.nodo_by_id(asta.nodo_i)
        if not ni.vincolo.blocca_rotazione:
            if ni.id not in k_per_nodo:
                k_per_nodo[ni.id] = {}
            k_per_nodo[ni.id][asta.id] = k_from_i[asta.id]

        # Contributo al nodo j (usando k vista dal nodo j)
        nj = modello.nodo_by_id(asta.nodo_j)
        if not nj.vincolo.blocca_rotazione:
            if nj.id not in k_per_nodo:
                k_per_nodo[nj.id] = {}
            k_per_nodo[nj.id][asta.id] = k_from_j[asta.id]

    # Calcola μ = k_Ji / Σk_J
    fattori: dict[int, dict[int, float]] = {}
    for id_nodo, aste_k in k_per_nodo.items():
        k_tot = sum(aste_k.values())
        if k_tot < 1e-10:
            # Nodo con tutte aste pendolo o k=0
            fattori[id_nodo] = {id_asta: 0.0 for id_asta in aste_k}
        else:
            fattori[id_nodo] = {id_asta: k / k_tot for id_asta, k in aste_k.items()}

    return fattori


# ==============================================================================
# STEP 3 — ALGORITMO CROSS NO-SWAY
# ==============================================================================


def esegui_cross_no_sway(
    modello: ModelloTelaio,
    mip: dict[int, tuple[float, float]],
    fattori: dict[int, dict[int, float]],
    k_from_i: dict[int, float],
    k_from_j: dict[int, float],
    tolleranza: float = 0.5,
    max_iter: int = 200,
) -> DatiCross:
    """Algoritmo iterativo di Cross per frame senza traslazione (no-sway).

    Algoritmo (Pozzati vol.II §3.6):
    ─────────────────────────────────────────────────────────────────
    INIZIALIZZAZIONE:
      Per ogni asta: M_corrente_i = MIP_i, M_corrente_j = MIP_j
    ITERAZIONE (finché max|squilibrio| > tolleranza):
      Per ogni nodo libero J:
        squilibrio_J = Σ M_corrente_Ji  (somma dei momenti agli estremi in J)
        Per ogni asta Ji convergente in J:
          ΔM_Ji = -μ_Ji × squilibrio_J    (distribuzione)
          M_corrente_Ji += ΔM_Ji
          M_corrente_ij += c_ij × ΔM_Ji  (carry-over al nodo lontano)
    CONVERGENZA: max|squilibrio_J| < tolleranza
    ─────────────────────────────────────────────────────────────────

    La tabella Cross storica registra ogni iterazione nel formato classico
    Santarella/Pozzati.

    Args:
        modello:     modello del telaio
        mip:         {id_asta: (MIP_i, MIP_j)} da calcola_mip_asta
        fattori:     {id_nodo: {id_asta: μ}} da calcola_fattori_distribuzione
        k_from_i:    rigidezze viste da nodo i
        k_from_j:    rigidezze viste da nodo j
        tolleranza:  convergenza [kg·cm] — default 0.5 kg·cm
        max_iter:    numero massimo di iterazioni

    Returns:
        DatiCross con tabella iterazioni completa e momenti finali
    """
    passaggi: list[str] = []

    # ---- Costruzione intestazioni colonne (formato storico) ----
    # Una colonna per ogni fine asta: "AB_i", "AB_j", "BA_i", "BA_j", ...
    # Ordine: per ogni asta, prima i poi j
    intestazioni: list[str] = []
    for asta in modello.aste:
        intestazioni.append(f"{asta.etichetta}_i")
        intestazioni.append(f"{asta.etichetta}_j")

    def _chiave_i(asta: AstaTelaio) -> str:
        return f"{asta.etichetta}_i"

    def _chiave_j(asta: AstaTelaio) -> str:
        return f"{asta.etichetta}_j"

    # ---- Inizializzazione: M corrente = MIP ----
    # M_cur[id_asta] = [M_i, M_j]
    M_cur: dict[int, list[float]] = {}
    for asta in modello.aste:
        M_i_mip, M_j_mip = mip.get(asta.id, (0.0, 0.0))
        M_cur[asta.id] = [M_i_mip, M_j_mip]

    # Riga 0: MIP
    mip_riga_momenti: dict[str, float] = {}
    for asta in modello.aste:
        mip_riga_momenti[_chiave_i(asta)] = M_cur[asta.id][0]
        mip_riga_momenti[_chiave_j(asta)] = M_cur[asta.id][1]
    iterazioni: list[RigaIterazioneCross] = [
        RigaIterazioneCross(numero=0, tipo="MIP", momenti=dict(mip_riga_momenti))
    ]
    passaggi.append("Riga 0 — MIP iniziali inseriti")

    # ---- Mappa nodo → aste + lato (i o j) per carry-over ----
    # Per ogni nodo e asta, quale lato (0=i, 1=j) è verso il nodo
    # e quale è il lato lontano con il suo carry-over
    # nodo_aste_lato[id_nodo] = [(id_asta, lato_vicino, lato_lontano, c)]
    nodo_aste_info: dict[int, list[tuple[int, int, int, float]]] = {}
    for asta in modello.aste:
        ni = asta.nodo_i
        nj = asta.nodo_j
        c_ij = asta.carry_over_ij  # carry-over da i verso j
        c_ji = asta.carry_over_ji  # carry-over da j verso i

        if ni not in nodo_aste_info:
            nodo_aste_info[ni] = []
        nodo_aste_info[ni].append((asta.id, 0, 1, c_ij))  # lato_vicino=i(0), lontano=j(1)

        if nj not in nodo_aste_info:
            nodo_aste_info[nj] = []
        nodo_aste_info[nj].append((asta.id, 1, 0, c_ji))  # lato_vicino=j(1), lontano=i(0)

    # ---- Iterazioni ----
    n_iter = 0
    errore_residuo = float("inf")
    nodi_liberi = [n for n in modello.nodi if not n.vincolo.blocca_rotazione]

    for n_iter in range(1, max_iter + 1):
        riga_dist_momenti: dict[str, float] = {k: 0.0 for k in intestazioni}
        riga_to_momenti: dict[str, float] = {k: 0.0 for k in intestazioni}
        max_squilibrio = 0.0

        for nodo in nodi_liberi:
            # Calcola squilibrio: somma dei momenti agli estremi convergenti in J
            squilibrio = 0.0
            aste_info = nodo_aste_info.get(nodo.id, [])
            for id_asta, lato_vicino, lato_lontano, c_carry in aste_info:
                squilibrio += M_cur[id_asta][lato_vicino]

            max_squilibrio = max(max_squilibrio, abs(squilibrio))
            if abs(squilibrio) < 1e-10:
                continue

            # Distribuisci
            mu_nodo = fattori.get(nodo.id, {})
            for id_asta, lato_vicino, lato_lontano, c_carry in aste_info:
                mu = mu_nodo.get(id_asta, 0.0)
                delta_M_vicino = -mu * squilibrio

                # Aggiorna momento al lato vicino
                M_cur[id_asta][lato_vicino] += delta_M_vicino

                # Aggiorna momento al lato lontano (carry-over)
                delta_M_lontano = c_carry * delta_M_vicino
                M_cur[id_asta][lato_lontano] += delta_M_lontano

                # Registra per la riga storica
                asta = modello.asta_by_id(id_asta)
                chiave_vicino = _chiave_i(asta) if lato_vicino == 0 else _chiave_j(asta)
                chiave_lontano = _chiave_i(asta) if lato_lontano == 0 else _chiave_j(asta)
                riga_dist_momenti[chiave_vicino] += delta_M_vicino
                riga_to_momenti[chiave_lontano] += delta_M_lontano

        # Registra riga iterazione (dist + t/o su righe separate)
        iterazioni.append(
            RigaIterazioneCross(
                numero=n_iter,
                tipo="dist",
                momenti={k: v for k, v in riga_dist_momenti.items() if abs(v) > 0.01},
            )
        )
        iterazioni.append(
            RigaIterazioneCross(
                numero=n_iter,
                tipo="t/o",
                momenti={k: v for k, v in riga_to_momenti.items() if abs(v) > 0.01},
            )
        )

        passaggi.append(f"Iter {n_iter}: max|squilibrio| = {max_squilibrio:.2f} kg·cm")
        errore_residuo = max_squilibrio

        if max_squilibrio <= tolleranza:
            passaggi.append(f"Convergenza raggiunta in {n_iter} iterazioni.")
            break
    else:
        passaggi.append(
            f"ATTENZIONE: non convergenza dopo {max_iter} iterazioni. "
            f"Errore residuo = {errore_residuo:.2f} kg·cm"
        )

    convergenza = errore_residuo <= tolleranza

    # ---- Riga finale: momenti totali ----
    totale_momenti: dict[str, float] = {}
    for asta in modello.aste:
        totale_momenti[_chiave_i(asta)] = M_cur[asta.id][0]
        totale_momenti[_chiave_j(asta)] = M_cur[asta.id][1]
    iterazioni.append(RigaIterazioneCross(numero=-1, tipo="totale", momenti=totale_momenti))

    # ---- Momenti finali ----
    momenti_finali: dict[int, tuple[float, float]] = {
        asta.id: (M_cur[asta.id][0], M_cur[asta.id][1]) for asta in modello.aste
    }

    return DatiCross(
        rigidezze_from_i=k_from_i,
        rigidezze_from_j=k_from_j,
        lunghezze={asta.id: modello.lunghezza_asta(asta.id) for asta in modello.aste},
        fattori_distribuzione=fattori,
        mip={asta.id: mip.get(asta.id, (0.0, 0.0)) for asta in modello.aste},
        mip_dettaglio={},
        iterazioni=iterazioni,
        momenti_finali=momenti_finali,
        n_iterazioni=n_iter,
        errore_residuo=errore_residuo,
        convergenza=convergenza,
        passaggi=passaggi,
        intestazioni_colonne=intestazioni,
    )


# ==============================================================================
# STEP 4 — CORREZIONE SWAY MULTI-PIANO (POZZATI §3.8)
# ==============================================================================


def calcola_taglio_piano_da_momenti(
    modello: ModelloTelaio,
    momenti: dict[int, tuple[float, float]],
    id_piano: int,
) -> float:
    """Calcola il taglio risultante al piano id_piano dai momenti delle colonne.

    Taglio_piano = Σ (M_top + M_bot) / h_col  per tutte le colonne del piano.

    Args:
        modello:    modello del telaio
        momenti:    {id_asta: (M_i, M_j)} momenti agli estremi
        id_piano:   piano per cui calcolare il taglio

    Returns:
        Taglio orizzontale totale al piano [kg]
    """
    taglio = 0.0
    for asta in modello.colonne_piano(id_piano):
        M_i, M_j = momenti.get(asta.id, (0.0, 0.0))
        L = modello.lunghezza_asta(asta.id)
        if L > 1e-10:
            # Convenzione: M_top = momento al nodo superiore
            # Per pilastro con nodo_i in basso e nodo_j in alto:
            # V = (M_j_superiore + M_i_inferiore) / h
            # (entrambi sommati con segno: equilibrio mensola verticale)
            taglio += (M_i + M_j) / L
    return taglio


def analisi_sway_unitario_piano(
    modello: ModelloTelaio,
    id_piano: int,
    fattori: dict[int, dict[int, float]],
    k_from_i: dict[int, float],
    k_from_j: dict[int, float],
    tolleranza: float = 0.5,
    max_iter: int = 200,
) -> DatiCross:
    """Analisi di Cross per sway unitario del piano id_piano.

    Applica un cedimento relativo δ = 1 cm alle colonne del piano id_piano
    (spostamento orizzontale relativo tra piano id_piano-1 e id_piano).

    Questo genera MIP di sway nelle colonne:
        M_top = M_bot = -6·E·I / h²   (Pozzati vol.II §3.8, formula sway FEM)

    Le travi non ricevono MIP di sway diretto.

    Args:
        modello:   modello del telaio
        id_piano:  piano a cui applicare lo sway unitario
        fattori:   fattori di distribuzione già calcolati
        k_from_i:  rigidezze già calcolate
        k_from_j:  rigidezze già calcolate
        tolleranza, max_iter: parametri di convergenza

    Returns:
        DatiCross per il caso sway unitario del piano id_piano
    """
    # MIP di sway: solo per colonne del piano id_piano
    mip_sway: dict[int, tuple[float, float]] = {}
    for asta in modello.aste:
        mip_sway[asta.id] = (0.0, 0.0)

    colonne = modello.colonne_piano(id_piano)
    for col in colonne:
        L = modello.lunghezza_asta(col.id)
        # δ = 1 cm (spostamento unitario)
        M_top, M_bot = mip_cedimento(
            delta=1.0,
            E=col.sezione.E,
            I=col.sezione.I,
            L=L,
        )
        # Convenzione: M_i = M al nodo inferiore, M_j = M al nodo superiore
        # mip_cedimento ritorna (M_i, M_j) entrambi dello stesso segno
        mip_sway[col.id] = (M_top, M_bot)

    return esegui_cross_no_sway(
        modello=modello,
        mip=mip_sway,
        fattori=fattori,
        k_from_i=k_from_i,
        k_from_j=k_from_j,
        tolleranza=tolleranza,
        max_iter=max_iter,
    )


def _risolvi_gauss(A: list[list[float]], b: list[float]) -> list[float] | None:
    """Risolve sistema lineare A·x = b con eliminazione di Gauss (pivoting parziale).

    Args:
        A: matrice n×n
        b: vettore n

    Returns:
        vettore soluzione x, oppure None se la matrice è singolare
    """
    n = len(b)
    M = [row[:] + [b[i]] for i, row in enumerate(A)]  # matrice aumentata

    for col in range(n):
        # Pivoting parziale
        max_val = abs(M[col][col])
        max_row = col
        for row in range(col + 1, n):
            if abs(M[row][col]) > max_val:
                max_val = abs(M[row][col])
                max_row = row
        if max_val < 1e-12:
            return None  # singolare
        if max_row != col:
            M[col], M[max_row] = M[max_row], M[col]

        pivot = M[col][col]
        for row in range(col + 1, n):
            f = M[row][col] / pivot
            for j in range(col, n + 1):
                M[row][j] -= f * M[col][j]

    x = [0.0] * n
    for i in range(n - 1, -1, -1):
        if abs(M[i][i]) < 1e-12:
            return None
        s = M[i][n]
        for j in range(i + 1, n):
            s -= M[i][j] * x[j]
        x[i] = s / M[i][i]
    return x


def esegui_correzione_sway(
    modello: ModelloTelaio,
    risultato_no_sway: DatiCross,
    forze_esterne_per_piano: dict[int, float],
    fattori: dict[int, dict[int, float]],
    k_from_i: dict[int, float],
    k_from_j: dict[int, float],
    tolleranza: float = 0.5,
    max_iter: int = 200,
) -> DatiCross:
    """Correzione sway multi-piano con metodo di Pozzati (sistema n×n).

    Metodo (Pozzati vol.II §3.8):
    ─────────────────────────────────────────────────────────────────
    1. Per ogni piano h (h = 1 … n_piani):
       a. Calcola forza di bloccaggio R_h:
          R_h = F_esterno_h - Taglio_piano_h(no-sway)
       b. Esegui analisi sway unitario per piano h → M_sway_h, Q_sway_h
          dove Q_sway_h[k] = taglio al piano k da sway unitario del piano h

    2. Assembla matrice H[i,j] = Q_sway_j al piano i per sway unitario del piano j
       (rigidezza di piano)

    3. Risolvi H · λ = R  → λ_h = magnitudine dello sway al piano h

    4. Momenti finali:
       M_finale = M_no_sway + Σ(λ_h × M_sway_h)
    ─────────────────────────────────────────────────────────────────

    Generale per qualsiasi numero di piani n.

    Args:
        modello:                  modello del telaio
        risultato_no_sway:        DatiCross dal calcolo no-sway
        forze_esterne_per_piano:  {id_piano: forza_orizz [kg]}
        fattori, k_from_i, k_from_j: già calcolati
        tolleranza, max_iter:     parametri di convergenza

    Returns:
        DatiCross con momenti corretti per sway
    """
    passaggi: list[str] = list(risultato_no_sway.passaggi)
    piani = sorted(modello.piani, key=lambda p: p.id_piano)
    n_piani = len(piani)

    if n_piani == 0:
        # Nessun piano definito: nessuna correzione sway
        passaggi.append("Nessun piano definito — correzione sway non applicata.")
        return risultato_no_sway

    passaggi.append(f"\n=== CORREZIONE SWAY ({n_piani} piani) ===")

    # ---- Step 1: Forze di bloccaggio ----
    R: list[float] = []
    for piano in piani:
        h = piano.id_piano
        Q_ns = calcola_taglio_piano_da_momenti(modello, risultato_no_sway.momenti_finali, h)
        F_est = forze_esterne_per_piano.get(h, 0.0)
        R_h = F_est - Q_ns
        R.append(R_h)
        passaggi.append(
            f"  Piano {h}: F_est={F_est:.1f} kg, Q_no_sway={Q_ns:.1f} kg, "
            f"R_bloccaggio={R_h:.1f} kg"
        )

    # ---- Step 2: Analisi sway unitario per ogni piano ----
    risultati_sway: list[DatiCross] = []
    H_matrix: list[list[float]] = [[0.0] * n_piani for _ in range(n_piani)]

    for j, piano_j in enumerate(piani):
        passaggi.append(f"  Sway unitario piano {piano_j.id_piano}...")
        res_sway = analisi_sway_unitario_piano(
            modello=modello,
            id_piano=piano_j.id_piano,
            fattori=fattori,
            k_from_i=k_from_i,
            k_from_j=k_from_j,
            tolleranza=tolleranza,
            max_iter=max_iter,
        )
        risultati_sway.append(res_sway)

        # Calcola taglio in ogni piano per questo sway unitario
        for i, piano_i in enumerate(piani):
            Q_ij = calcola_taglio_piano_da_momenti(
                modello, res_sway.momenti_finali, piano_i.id_piano
            )
            H_matrix[i][j] = Q_ij
            passaggi.append(f"    H[{piano_i.id_piano},{piano_j.id_piano}] = {Q_ij:.2f} kg/cm")

    # ---- Step 3: Risolvi H · λ = R ----
    lambda_vals = _risolvi_gauss(H_matrix, R)
    if lambda_vals is None:
        passaggi.append(
            "ERRORE: matrice sway singolare. Struttura labile o non-sway. "
            "Restituzione risultato no-sway."
        )
        return risultato_no_sway

    passaggi.append("  Soluzione λ (sway per piano):")
    for j, piano_j in enumerate(piani):
        passaggi.append(f"    λ_{piano_j.id_piano} = {lambda_vals[j]:.4f} cm")

    # ---- Step 4: Momenti finali = no-sway + Σ(λ_h × M_sway_h) ----
    momenti_finali_corretti: dict[int, tuple[float, float]] = {}
    for asta in modello.aste:
        M_i_ns, M_j_ns = risultato_no_sway.momenti_finali[asta.id]
        M_i_tot = M_i_ns
        M_j_tot = M_j_ns
        for j in range(n_piani):
            lam = lambda_vals[j]
            M_i_sw, M_j_sw = risultati_sway[j].momenti_finali[asta.id]
            M_i_tot += lam * M_i_sw
            M_j_tot += lam * M_j_sw
        momenti_finali_corretti[asta.id] = (M_i_tot, M_j_tot)

    # ---- Crea DatiCross finale ----
    # Aggiunge una riga "sway" nella tabella iterazioni per ogni piano
    iterazioni_finali = list(risultato_no_sway.iterazioni)
    for j, piano_j in enumerate(piani):
        lam = lambda_vals[j]
        momenti_sway_scalati: dict[str, float] = {}
        for asta in modello.aste:
            M_i, M_j = risultati_sway[j].momenti_finali[asta.id]
            momenti_sway_scalati[f"{asta.etichetta}_i"] = lam * M_i
            momenti_sway_scalati[f"{asta.etichetta}_j"] = lam * M_j
        iterazioni_finali.append(
            RigaIterazioneCross(
                numero=1000 + piano_j.id_piano,
                tipo=f"sway_piano_{piano_j.id_piano} (λ={lam:.4f})",
                momenti={k: v for k, v in momenti_sway_scalati.items() if abs(v) > 0.01},
            )
        )

    # Aggiorna riga totale finale
    totale_corretti: dict[str, float] = {}
    for asta in modello.aste:
        M_i, M_j = momenti_finali_corretti[asta.id]
        totale_corretti[f"{asta.etichetta}_i"] = M_i
        totale_corretti[f"{asta.etichetta}_j"] = M_j
    iterazioni_finali.append(
        RigaIterazioneCross(numero=-2, tipo="totale_con_sway", momenti=totale_corretti)
    )

    n_iter_totali = risultato_no_sway.n_iterazioni + sum(r.n_iterazioni for r in risultati_sway)

    return DatiCross(
        rigidezze_from_i=risultato_no_sway.rigidezze_from_i,
        rigidezze_from_j=risultato_no_sway.rigidezze_from_j,
        lunghezze=risultato_no_sway.lunghezze,
        fattori_distribuzione=risultato_no_sway.fattori_distribuzione,
        mip=risultato_no_sway.mip,
        mip_dettaglio=risultato_no_sway.mip_dettaglio,
        iterazioni=iterazioni_finali,
        momenti_finali=momenti_finali_corretti,
        n_iterazioni=n_iter_totali,
        errore_residuo=risultato_no_sway.errore_residuo,
        convergenza=risultato_no_sway.convergenza,
        passaggi=passaggi,
        intestazioni_colonne=risultato_no_sway.intestazioni_colonne,
    )


# ==============================================================================
# ENTRY POINT PRINCIPALE
# ==============================================================================


def calcola_cross_pozzati(
    modello: ModelloTelaio,
    forze_orizzontali_per_piano: dict[int, float] | None = None,
    includi_peso_proprio: bool = True,
    tolleranza: float = 0.5,
    max_iter: int = 200,
) -> DatiCross:
    """Entry point principale — esegue il calcolo completo Cross-Pozzati.

    Sequenza:
    1. Calcola rigidezze k e lunghezze
    2. Calcola fattori di distribuzione μ
    3. Calcola MIP per tutte le aste
    4. Esegui Cross no-sway
    5. Se forze_orizzontali_per_piano: esegui correzione sway
    6. Ritorna DatiCross completo

    Args:
        modello:                     modello del telaio
        forze_orizzontali_per_piano: {id_piano: F_orizz [kg]}
                                     None = calcolo statico (no sway forzato)
        includi_peso_proprio:        aggiunge automaticamente il peso proprio
        tolleranza:                  convergenza [kg·cm]
        max_iter:                    iterazioni massime

    Returns:
        DatiCross con tutto l'audit del calcolo
    """
    passaggi_pre: list[str] = []

    # ---- Verifica connettività ----
    problemi = modello.verifica_connettivita()
    if problemi:
        raise ValueError("Modello non valido:\n" + "\n".join(problemi))

    # ---- Step 1: Rigidezze ----
    k_from_i, k_from_j, lunghezze = calcola_rigidezze(modello)
    passaggi_pre.append(f"Rigidezze calcolate per {len(modello.aste)} aste")

    # ---- Step 2: Fattori di distribuzione ----
    fattori = calcola_fattori_distribuzione(modello, k_from_i, k_from_j)
    passaggi_pre.append(f"Fattori di distribuzione calcolati per {len(fattori)} nodi liberi")

    # ---- Step 3: MIP per tutte le aste ----
    mip: dict[int, tuple[float, float]] = {}
    mip_dettaglio: dict[int, dict] = {}
    for asta in modello.aste:
        L = lunghezze[asta.id]
        det = calcola_mip_asta(asta, L, includi_peso_proprio)
        mip[asta.id] = (det["M_i"], det["M_j"])
        mip_dettaglio[asta.id] = det
        passaggi_pre.extend(det["passaggi"])

    passaggi_pre.append(f"MIP calcolati per {len(modello.aste)} aste")

    # ---- Step 4: Cross no-sway ----
    risultato = esegui_cross_no_sway(
        modello=modello,
        mip=mip,
        fattori=fattori,
        k_from_i=k_from_i,
        k_from_j=k_from_j,
        tolleranza=tolleranza,
        max_iter=max_iter,
    )
    # Inserisce i dettagli MIP nel risultato
    risultato.mip_dettaglio.update(mip_dettaglio)
    risultato.passaggi = passaggi_pre + risultato.passaggi

    # ---- Step 5: Correzione sway (se richiesta) ----
    if forze_orizzontali_per_piano and len(modello.piani) > 0:
        forze_non_nulle = {k: v for k, v in forze_orizzontali_per_piano.items() if abs(v) > 0.1}
        if forze_non_nulle:
            risultato = esegui_correzione_sway(
                modello=modello,
                risultato_no_sway=risultato,
                forze_esterne_per_piano=forze_orizzontali_per_piano,
                fattori=fattori,
                k_from_i=k_from_i,
                k_from_j=k_from_j,
                tolleranza=tolleranza,
                max_iter=max_iter,
            )

    return risultato
