"""Generatore di schemi reticolari piani per cordoli metallici.

Genera topologie Howe e Pratt con montanti verticali a ogni nodo di pannello.
Entrambi gli schemi sono cinematicamente stabili per qualsiasi numero di campate
e qualsiasi condizione di vincolo alle estremità.

Topologia comune (n campate):
  Corrente inferiore: n+1 nodi a y=0, x = k*a
  Corrente superiore: n+1 nodi a y=h, x = k*a
  Montanti verticali: n+1 barre (uno per ogni nodo di pannello, inclusi gli estremi)
  Diagonali:          n barre (direzione diversa per Howe vs Pratt)

  Howe:  diagonale di pannello k → corrente inf[k] → corrente sup[k+1]  (ascendente →)
  Pratt: diagonale di pannello k → corrente sup[k] → corrente inf[k+1]  (discendente →)

Verifica Maxwell per schema con n+1 montanti + n diagonali:
  b = n + n + (n+1) + n = 4n+1  barre
  n_nodi = 2*(n+1) = 2n+2
  r (cerniera) = 6  →  b+r = 4n+7 > 4n+4 = 2*n_nodi  ✓  (indeterminato di 3)

Condizioni di vincolo alle estremità (tipo_estremi):
  "cerniera":     CERNIERA a x=0 (entrambi i correnti), CARRELLO_X a x=L (uy fisso, ux libero)
  "incastro":     CERNIERA a x=0 (entrambi), CERNIERA a x=L (entrambi)
  "semi_incastro": analogo a "cerniera" con nota di incastro parziale (fattore via percentuale_incastro)

Coordinate: X = direzione correnti (span), Y = profondità traliccio (spessore muro).
Il traliccio giace nel piano XY orizzontale. F_sismica in direzione Y.

Unità: cm per geometria, kg per forze.
"""

from __future__ import annotations

import math

from .sezione_asta import SezioneAsta
from .traliccio_2d import Asta, Nodo, TipoVincolo

# ═══════════════════════════════════════════════════════════
#  Topologia base comune a Howe e Pratt
# ═══════════════════════════════════════════════════════════


def _genera_topologia_base(
    L: float,
    h: float,
    n_campate: int,
    sezione_corrente: SezioneAsta,
) -> tuple[list[Nodo], list[Asta], int, int, float]:
    """Genera nodi, correnti e montanti comuni a Howe e Pratt.

    Returns:
        (nodi, aste, id_nodo_next, id_asta_next, a_pannello)
    """
    if n_campate < 1:
        raise ValueError(f"n_campate deve essere >= 1, ricevuto {n_campate}")
    if L <= 0 or h <= 0:
        raise ValueError(f"L e h devono essere > 0: L={L}, h={h}")

    n = n_campate
    a = L / n  # lunghezza pannello [cm]
    A_c = sezione_corrente.A
    nome_c = sezione_corrente.nome

    nodi: list[Nodo] = []
    aste: list[Asta] = []
    id_nodo = 0
    id_asta = 0

    # Nodi corrente inferiore (y=0): id 0..n
    for k in range(n + 1):
        nodi.append(Nodo(id=id_nodo, x=k * a, y=0.0))
        id_nodo += 1

    # Nodi corrente superiore (y=h): id n+1..2n+1
    for k in range(n + 1):
        nodi.append(Nodo(id=id_nodo, x=k * a, y=h))
        id_nodo += 1

    # Corrente inferiore: 0→1→...→n
    for k in range(n):
        aste.append(Asta(id=id_asta, nodo_i=k, nodo_j=k + 1, A=A_c, nome_profilo=nome_c))
        id_asta += 1

    # Corrente superiore: (n+1)→(n+2)→...→(2n+1)
    for k in range(n):
        aste.append(
            Asta(
                id=id_asta,
                nodo_i=n + 1 + k,
                nodo_j=n + 1 + k + 1,
                A=A_c,
                nome_profilo=nome_c,
            )
        )
        id_asta += 1

    # Montanti verticali: inf[k]→sup[k] per k=0..n  (n+1 montanti, inclusi gli estremi)
    for k in range(n + 1):
        aste.append(
            Asta(
                id=id_asta,
                nodo_i=k,
                nodo_j=n + 1 + k,
                A=A_c,
                nome_profilo=nome_c,
            )
        )
        id_asta += 1

    return nodi, aste, id_nodo, id_asta, a


# ═══════════════════════════════════════════════════════════
#  Schema Howe
# ═══════════════════════════════════════════════════════════


def genera_howe(
    L: float,
    h: float,
    n_campate: int,
    sezione_corrente: SezioneAsta,
    sezione_diagonale: SezioneAsta,
) -> tuple[list[Nodo], list[Asta]]:
    """Genera schema Howe con n_campate pannelli.

    Topologia (n=4, ad esempio):
      Corrente inf (y=0):  0─1─2─3─4
      Corrente sup (y=h):  5─6─7─8─9
      Montanti verticali:  0-5, 1-6, 2-7, 3-8, 4-9  (n+1 barre)
      Diagonali Howe:      0→6, 1→7, 2→8, 3→9        (ascendenti, inf[k]→sup[k+1])

    Totale barre = n + n + (n+1) + n = 4n+1.
    Per n=4: 17 barre.

    Args:
        L:                 lunghezza totale traliccio [cm]
        h:                 profondità = spessore muro [cm]
        n_campate:         numero di pannelli
        sezione_corrente:  SezioneAsta per correnti e montanti
        sezione_diagonale: SezioneAsta per le diagonali

    Returns:
        (nodi, aste) — senza vincoli e senza forze esterne
    """
    nodi, aste, _, id_asta, _ = _genera_topologia_base(
        L,
        h,
        n_campate,
        sezione_corrente,
    )
    n = n_campate
    A_d = sezione_diagonale.A
    nome_d = sezione_diagonale.nome

    # Diagonali Howe: inf[k] → sup[k+1]  (ascendenti da sinistra a destra)
    for k in range(n):
        aste.append(
            Asta(
                id=id_asta,
                nodo_i=k,  # inf[k]
                nodo_j=n + 1 + k + 1,  # sup[k+1]
                A=A_d,
                nome_profilo=nome_d,
            )
        )
        id_asta += 1

    return nodi, aste


# ═══════════════════════════════════════════════════════════
#  Schema Pratt
# ═══════════════════════════════════════════════════════════


def genera_pratt(
    L: float,
    h: float,
    n_campate: int,
    sezione_corrente: SezioneAsta,
    sezione_diagonale: SezioneAsta,
    sezione_montante: SezioneAsta | None = None,
) -> tuple[list[Nodo], list[Asta]]:
    """Genera schema Pratt con n_campate pannelli.

    Topologia (n=4, ad esempio):
      Corrente inf (y=0):  0─1─2─3─4
      Corrente sup (y=h):  5─6─7─8─9
      Montanti verticali:  0-5, 1-6, 2-7, 3-8, 4-9  (n+1 barre)
      Diagonali Pratt:     5→1, 6→2, 7→3, 8→4        (discendenti, sup[k]→inf[k+1])

    Totale barre = n + n + (n+1) + n = 4n+1.
    Per n=4: 17 barre.

    Args:
        L:                 lunghezza totale traliccio [cm]
        h:                 profondità = spessore muro [cm]
        n_campate:         numero di pannelli
        sezione_corrente:  SezioneAsta per correnti
        sezione_diagonale: SezioneAsta per le diagonali
        sezione_montante:  SezioneAsta per i montanti (default = sezione_corrente)

    Returns:
        (nodi, aste) — senza vincoli e senza forze esterne
    """
    nodi, aste, _, id_asta, _ = _genera_topologia_base(
        L,
        h,
        n_campate,
        sezione_montante if sezione_montante is not None else sezione_corrente,
    )
    n = n_campate

    # Sostituisce le correnti e i montanti con sezione_corrente se diversa dal montante
    # (la base usa sezione_corrente passata come primo arg; i montanti usano lo stesso profilo)
    A_d = sezione_diagonale.A
    nome_d = sezione_diagonale.nome

    # Diagonali Pratt: sup[k] → inf[k+1]  (discendenti da sinistra a destra)
    for k in range(n):
        aste.append(
            Asta(
                id=id_asta,
                nodo_i=n + 1 + k,  # sup[k]
                nodo_j=k + 1,  # inf[k+1]
                A=A_d,
                nome_profilo=nome_d,
            )
        )
        id_asta += 1

    return nodi, aste


# ═══════════════════════════════════════════════════════════
#  Vincoli alle estremità
# ═══════════════════════════════════════════════════════════


def applica_vincoli_cordolo(
    nodi: list[Nodo],
    n_campate: int,
    schema: str = "howe",
    tipo_estremi: str = "cerniera",
    percentuale_incastro: float = 0.0,
) -> list[Nodo]:
    """Applica vincoli per cordolo di sommità muro.

    Schema di vincolo alle estremità (x=0 e x=L):
      x=0: CERNIERA per entrambi i correnti (inf e sup) — sempre
      x=L:
        "cerniera"     → CARRELLO_X (uy fisso, ux libero)  per entrambi
        "incastro"     → CERNIERA   (uy e ux fissi)         per entrambi
        "semi_incastro"→ come "cerniera" (ux libero); la rigidezza parziale
                         è modellabile con molle (TODO: Winkler esteso D.3.2-ext)

    Args:
        nodi:                lista nodi dal generatore
        n_campate:           numero pannelli
        schema:              "howe" o "pratt" (attualmente non usato)
        tipo_estremi:        "cerniera", "incastro" o "semi_incastro"
        percentuale_incastro: 0.0–1.0 (usato solo per "semi_incastro", riservato)

    Returns:
        Lista nodi aggiornata (copia, senza modifica in-place).
    """
    n = n_campate
    nodi_out = [
        Nodo(id=nd.id, x=nd.x, y=nd.y, vincolo=nd.vincolo, Fx=nd.Fx, Fy=nd.Fy) for nd in nodi
    ]

    if tipo_estremi == "incastro":
        vincolo_destra = TipoVincolo.CERNIERA
    else:
        # "cerniera" e "semi_incastro": carrello in Y a x=L
        vincolo_destra = TipoVincolo.CARRELLO_X

    for nd in nodi_out:
        if nd.id == 0:
            nd.vincolo = TipoVincolo.CERNIERA  # inf, x=0
        elif nd.id == n + 1:
            nd.vincolo = TipoVincolo.CERNIERA  # sup, x=0
        elif nd.id == n:
            nd.vincolo = vincolo_destra  # inf, x=L
        elif nd.id == 2 * n + 1:
            nd.vincolo = vincolo_destra  # sup, x=L

    return nodi_out


# ═══════════════════════════════════════════════════════════
#  Utilità
# ═══════════════════════════════════════════════════════════


def n_campate_default(L: float, h: float) -> int:
    """Numero di campate di default per schema Howe/Pratt.

    Regola: n = round_pari(L / (2*h)), minimo 2.
    Es. L=400 cm, h=30 cm → n = round_pari(400/60) = round_pari(6.67) = 6.
    """
    n_raw = L / (2 * h)
    n = max(2, round(n_raw))
    if n % 2 != 0:
        n += 1  # arrotonda al pari
    return n


def valida_geometria(
    nodi: list[Nodo],
    aste: list[Asta],
    theta_min: float = 20.0,
    theta_max: float = 70.0,
) -> list[str]:
    """Valida la geometria del traliccio.

    Controlla:
    - Angoli diagonali: theta_min ≤ θ ≤ theta_max (solo per aste oblique)
    - Aste di lunghezza zero

    Returns:
        Lista di messaggi warning/errore (vuota = geometria OK)
    """
    nodi_map = {n.id: n for n in nodi}
    messaggi: list[str] = []

    for asta in aste:
        ni = nodi_map.get(asta.nodo_i)
        nj = nodi_map.get(asta.nodo_j)
        if ni is None or nj is None:
            messaggi.append(f"ERRORE: Asta {asta.id} — nodo non trovato")
            continue

        dx = nj.x - ni.x
        dy = nj.y - ni.y
        L_asta = math.sqrt(dx**2 + dy**2)

        if L_asta < 1e-6:
            messaggi.append(f"ERRORE: Asta {asta.id} — lunghezza zero")
            continue

        # Controlla angolo solo per aste oblique (non orizzontali, non verticali)
        if abs(dx) > 1e-6 and abs(dy) > 1e-6:
            theta = math.degrees(math.atan2(abs(dy), abs(dx)))
            if theta < theta_min:
                messaggi.append(
                    f"WARNING: Asta {asta.id} — angolo {theta:.1f}° < {theta_min}° "
                    f"(diagonale troppo piatta)"
                )
            elif theta > theta_max:
                messaggi.append(
                    f"WARNING: Asta {asta.id} — angolo {theta:.1f}° > {theta_max}° "
                    f"(diagonale troppo ripida)"
                )

    return messaggi


def predimensiona_sezione(
    N_max: float,
    L_asta: float,
    tipo_acciaio: str = "Fe430",
    famiglia: str = "PIATTO",
    lambda_max: float = 200.0,
) -> SezioneAsta | None:
    """Cerca il profilo minimo (G1) per N_max e L_asta dati.

    Itera su piatti.json o angolari.json in ordine di A crescente.
    Trova il primo che verifica sia tensione che snellezza.

    Args:
        N_max:        sforzo assiale massimo (negativo = compressione) [kg]
        L_asta:       lunghezza libera asta [cm]
        tipo_acciaio: "Fe430", "Fe360", etc.
        famiglia:     "PIATTO" o "ANGOLARE"
        lambda_max:   snellezza massima ammissibile

    Returns:
        SezioneAsta minima verificante, oppure None
    """
    from .sezione_asta import carica_catalogo_angolari, carica_catalogo_piatti
    from .verifiche_ta import verifica_asta_ta

    if famiglia.upper() == "ANGOLARE":
        cat = carica_catalogo_angolari()
    else:
        cat = carica_catalogo_piatti()

    for sez in cat.tutti():  # ordinate per A crescente
        r = verifica_asta_ta(sez, N=N_max, L=L_asta, tipo_acciaio=tipo_acciaio)
        if not r.get("verificato", False):
            continue
        lam = r.get("lambda_max", r.get("lambda_fp", 0.0))
        if lam <= lambda_max:
            return sez

    return None


def disegna_schema_traliccio(
    nodi: list[Nodo],
    aste: list[Asta],
    N_aste: dict[int, float] | None = None,
) -> object:
    """Genera anteprima matplotlib del traliccio (headless).

    Colori aste: rosso = compressione, blu = trazione, grigio = scarica.
    Intensità proporzionale allo sforzo.

    Returns:
        matplotlib.figure.Figure (None se matplotlib non disponibile)
    """
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.patches as mpatches
        import matplotlib.pyplot as plt
    except ImportError:
        return None

    nodi_map = {n.id: n for n in nodi}
    fig, ax = plt.subplots(figsize=(max(10, len(nodi) * 0.5), 4))

    N_max_abs = 1.0
    if N_aste:
        valori = [abs(v) for v in N_aste.values() if abs(v) > 0]
        N_max_abs = max(valori) if valori else 1.0

    for asta in aste:
        ni = nodi_map[asta.nodo_i]
        nj = nodi_map[asta.nodo_j]
        N = N_aste.get(asta.id, 0.0) if N_aste else 0.0

        if N < 0:
            colore = "red"
            lw = 1.0 + 2.0 * abs(N) / N_max_abs
        elif N > 0:
            colore = "blue"
            lw = 1.0 + 2.0 * N / N_max_abs
        else:
            colore = "gray"
            lw = 1.0

        ax.plot([ni.x, nj.x], [ni.y, nj.y], color=colore, lw=lw)

    for n in nodi:
        ax.plot(n.x, n.y, "ko", ms=4)
        ax.annotate(str(n.id), (n.x, n.y), textcoords="offset points", xytext=(2, 4), fontsize=7)

    legenda = [
        mpatches.Patch(color="blue", label="Trazione"),
        mpatches.Patch(color="red", label="Compressione"),
    ]
    ax.legend(handles=legenda, loc="upper right", fontsize=8)
    ax.set_aspect("equal")
    ax.set_xlabel("X [cm]")
    ax.set_ylabel("Y [cm]")
    ax.set_title("Schema traliccio")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    return fig
