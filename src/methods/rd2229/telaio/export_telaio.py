"""
Tabulati storici e report per telai piani — RD 2229/39.

Subfase L.8 del modulo telai piani Cross-Pozzati.
Genera le 7+1 tabelle nel formato storico di Pozzati/Santarella:

  Tabella 0 — Vincoli strutturali (esterni + rilasci interni)
  Tabella 1 — Caratteristiche geometriche sezioni (k=4EI/L, k=3EI/L, ...)
  Tabella 2 — Fattori di distribuzione nodale (μ_ij)
  Tabella 3 — Analisi carichi e momenti di incastro perfetto (MIP)
  Tabella 4 — Distribuzione Cross iterativa (tabella storica con t/o)
  Tabella 5 — Sollecitazioni per asta e combinazione (M/V/N in 3 sezioni)
  Tabella 6 — Inviluppo sollecitazioni (M/V/N max e min)
  Tabella 7 — Schede Santarella armatura (per asta)

Output: ASCII (per log/terminale) + HTML (per relazione di calcolo).

Riferimento: Pozzati "Teoria e Tecnica delle Strutture" vol.II;
             Santarella "Il Cemento Armato" vol.II — Tavole numeriche.
"""

from __future__ import annotations

import html as html_mod
import math
from datetime import datetime

from src.methods.rd2229.telaio.armature_telaio import (
    ArmaturaSezioneSemplice,
    SchedaArmatura,
    genera_schede_santarella,
)
from src.methods.rd2229.telaio.combinazioni_rd2229 import (
    InviluppoSollecitazioniAsta,
)
from src.methods.rd2229.telaio.cross_pozzati import DatiCross
from src.methods.rd2229.telaio.modello_telaio import (
    ModelloTelaio,
    TipoRilascioInterno,
    TipoVincoloEsterno,
)
from src.methods.rd2229.telaio.solver_telaio import (
    RisultatoCasoCarico,
)
from src.methods.rd2229.telaio.verifiche_telaio import (
    RisultatoVerificaAsta,
    riepilogo_verifiche,
)

# ==============================================================================
# UTILITY ASCII
# ==============================================================================

_SEP = "═" * 100
_SEP2 = "─" * 100
_SEP3 = "─" * 100


def _centro(testo: str, larghezza: int = 100) -> str:
    return testo.center(larghezza)


def _riga_tabella(*celle: str, larghezze: list[int]) -> str:
    """Formatta una riga di tabella con celle di larghezze specificate."""
    parti = []
    for cella, larg in zip(celle, larghezze):
        parti.append(str(cella).rjust(larg))
    return " │ ".join(parti)


def _intestazione_tabella(numero: int, titolo: str) -> list[str]:
    return [
        "",
        _SEP,
        _centro(f"TABELLA {numero} — {titolo.upper()}"),
        _SEP,
    ]


def _float(v: float | None, dec: int = 1) -> str:
    if v is None:
        return "—"
    if math.isnan(v) or math.isinf(v):
        return "—"
    return f"{v:.{dec}f}"


def _int_str(v: float | None) -> str:
    if v is None:
        return "—"
    return f"{int(round(v))}"


# ==============================================================================
# TABELLA 0 — VINCOLI STRUTTURALI
# ==============================================================================


def tabella_0_vincoli(modello: ModelloTelaio) -> list[str]:
    """Tabella 0: vincoli esterni e rilasci interni."""
    righe = _intestazione_tabella(0, "Vincoli strutturali")

    # Vincoli esterni
    righe.append("VINCOLI ESTERNI:")
    righe.append(_SEP2)
    intestazione = f"{'Nodo':>5} │ {'Etich.':>7} │ {'Tipo vincolo':<20} │ {'GDL bloccati':<20} │ {'n. reazioni':>12}"
    righe.append(intestazione)
    righe.append(_SEP2)

    n_reaz_tot = 0
    for nodo in modello.nodi:
        v = nodo.vincolo
        if v.tipo == TipoVincoloEsterno.LIBERO:
            continue
        gdl = v.descrizione_gdl()
        n_reaz = v.n_reazioni
        n_reaz_tot += n_reaz
        riga = (
            f"{nodo.id:>5} │ {nodo.etichetta or '?':>7} │ "
            f"{v.tipo.value:<20} │ {gdl:<20} │ {n_reaz:>12}"
        )
        righe.append(riga)

    righe.append(_SEP2)
    iper = modello.iperstaticita_esterna()
    righe.append(
        f"Σ reazioni esterne = {n_reaz_tot}   |   "
        f"Grado di iperstaticità esterna = {n_reaz_tot} − 3 = {iper}"
    )
    righe.append("")

    # Rilasci interni
    righe.append("RILASCI INTERNI:")
    righe.append(_SEP2)
    intestazione2 = (
        f"{'Asta':>5} │ {'Etich.':>7} │ "
        f"{'Rilascio nodo i':<16} │ {'k_ij':>10} │ {'c_ij':>6} │ "
        f"{'Rilascio nodo j':<16} │ {'k_ji':>10} │ {'c_ji':>6}"
    )
    righe.append(intestazione2)
    righe.append(_SEP2)

    n_rilasci = 0
    for asta in modello.aste:
        ri = asta.rilascio_i
        rj = asta.rilascio_j
        ha_rilascio = (
            ri.tipo != TipoRilascioInterno.NODO_RIGIDO
            or rj.tipo != TipoRilascioInterno.NODO_RIGIDO
        )
        if not ha_rilascio:
            continue
        n_rilasci += 1
        L = modello.lunghezza_asta(asta.id)
        EI = asta.sezione.EI()
        k_ij = asta.rigidezza_from_i(L)
        k_ji = asta.rigidezza_from_j(L)
        riga = (
            f"{asta.id:>5} │ {asta.etichetta or '':>7} │ "
            f"{ri.tipo.value:<16} │ {k_ij:>10.0f} │ {asta.carry_over_ij:>6.2f} │ "
            f"{rj.tipo.value:<16} │ {k_ji:>10.0f} │ {asta.carry_over_ji:>6.2f}"
        )
        righe.append(riga)

    if n_rilasci == 0:
        righe.append("  Nessun rilascio interno (tutti nodi rigidi)")
    righe.append(_SEP2)

    return righe


# ==============================================================================
# TABELLA 1 — CARATTERISTICHE SEZIONI
# ==============================================================================


def tabella_1_sezioni(modello: ModelloTelaio) -> list[str]:
    """Tabella 1: caratteristiche sezioni con k=4EI/L e k=3EI/L."""
    righe = _intestazione_tabella(1, "Caratteristiche sezioni")
    righe.append(
        f"{'Asta':>5} │ {'Etich.':>7} │ {'L [cm]':>8} │ "
        f"{'b [cm]':>7} │ {'h [cm]':>7} │ "
        f"{'I [cm⁴]':>12} │ {'E [kg/cm²]':>12} │ "
        f"{'k_i [4EI/L]':>13} │ {'k_j [kEI/L]':>13}"
    )
    righe.append(_SEP2)

    for asta in modello.aste:
        L = modello.lunghezza_asta(asta.id)
        sez = asta.sezione
        EI = sez.EI()
        k_i = asta.rigidezza_from_i(L)
        k_j = asta.rigidezza_from_j(L)
        riga = (
            f"{asta.id:>5} │ {asta.etichetta or '':>7} │ {L:>8.1f} │ "
            f"{sez.b:>7.1f} │ {sez.h:>7.1f} │ "
            f"{sez.I:>12.0f} │ {sez.E:>12.0f} │ "
            f"{k_i:>13.0f} │ {k_j:>13.0f}"
        )
        righe.append(riga)

    righe.append(_SEP2)
    return righe


# ==============================================================================
# TABELLA 2 — FATTORI DI DISTRIBUZIONE NODALE
# ==============================================================================


def tabella_2_fattori(
    modello: ModelloTelaio, dati_cross: DatiCross
) -> list[str]:
    """Tabella 2: fattori di distribuzione μ per nodo."""
    righe = _intestazione_tabella(2, "Fattori di distribuzione nodale")
    righe.append(
        f"{'Nodo':>6} │ {'Etich.':>7} │ "
        f"{'Asta':>5} │ {'k_ij':>12} │ {'μ_ij':>8}"
    )
    righe.append(_SEP2)

    for id_nodo, fattori_nodo in dati_cross.fattori_distribuzione.items():
        nodo = modello.nodo_by_id(id_nodo)
        etich_nodo = nodo.etichetta if nodo else str(id_nodo)
        k_totale = sum(
            dati_cross.rigidezze.get(id_asta_nodo, 0.0)
            for id_asta_nodo in fattori_nodo
        )

        prima_riga = True
        for id_asta, mu in fattori_nodo.items():
            asta = modello.asta_by_id(id_asta)
            etich_asta = asta.etichetta if asta else str(id_asta)
            k_ij = dati_cross.rigidezze.get(id_asta, 0.0)
            prefisso_nodo = f"{id_nodo:>6} │ {etich_nodo:>7}" if prima_riga else f"{'':>6} │ {'':>7}"
            riga = f"{prefisso_nodo} │ {etich_asta:>5} │ {k_ij:>12.0f} │ {mu:>8.4f}"
            righe.append(riga)
            prima_riga = False

        # Riga Σ
        riga_sum = f"{'':>6} │ {'':>7} │ {'Σ':>5} │ {k_totale:>12.0f} │ {'1.0000':>8}"
        righe.append(riga_sum)
        righe.append(_SEP3)

    return righe


# ==============================================================================
# TABELLA 3 — ANALISI CARICHI E MIP
# ==============================================================================


def tabella_3_mip(modello: ModelloTelaio, dati_cross: DatiCross) -> list[str]:
    """Tabella 3: analisi carichi per asta e momenti di incastro perfetto."""
    righe = _intestazione_tabella(3, "Analisi carichi — Momenti di Incastro Perfetto (MIP)")
    righe.append(
        f"{'Asta':>5} │ {'Etich.':>7} │ "
        f"{'Carico':>22} │ {'q o P':>10} │ "
        f"{'L [cm]':>7} │ {'Formula':>16} │ "
        f"{'M_i [kg·cm]':>13} │ {'M_j [kg·cm]':>13}"
    )
    righe.append(_SEP2)

    for id_asta, (MIP_i, MIP_j) in dati_cross.mip.items():
        asta = modello.asta_by_id(id_asta)
        etich = asta.etichetta if asta else str(id_asta)
        L = modello.lunghezza_asta(id_asta)

        # Dettaglio contributi MIP (da mip_dettaglio se disponibile)
        dettaglio = dati_cross.mip_dettaglio.get(id_asta)
        if dettaglio and "contributi" in dettaglio:
            prima = True
            for contrib in dettaglio["contributi"]:
                tipo_carico = contrib.get("tipo", "—")
                formula = contrib.get("formula", "—")
                q_str = contrib.get("q_str", "—")
                Mi_c = contrib.get("M_i", 0.0)
                Mj_c = contrib.get("M_j", 0.0)
                prefisso = f"{id_asta:>5} │ {etich:>7}" if prima else f"{'':>5} │ {'':>7}"
                riga = (
                    f"{prefisso} │ {tipo_carico:>22} │ {q_str:>10} │ "
                    f"{L:>7.1f} │ {formula:>16} │ "
                    f"{Mi_c:>13.0f} │ {Mj_c:>13.0f}"
                )
                righe.append(riga)
                prima = False
            # Riga totale
            riga_tot = (
                f"{'':>5} │ {'':>7} │ {'TOTALE':>22} │ {'':>10} │ "
                f"{'':>7} │ {'':>16} │ "
                f"{MIP_i:>13.0f} │ {MIP_j:>13.0f}"
            )
            righe.append(riga_tot)
        else:
            riga = (
                f"{id_asta:>5} │ {etich:>7} │ {'(vedi calcolo)':>22} │ {'':>10} │ "
                f"{L:>7.1f} │ {'':>16} │ "
                f"{MIP_i:>13.0f} │ {MIP_j:>13.0f}"
            )
            righe.append(riga)

        righe.append(_SEP3)

    return righe


# ==============================================================================
# TABELLA 4 — DISTRIBUZIONE CROSS ITERATIVA
# ==============================================================================


def tabella_4_cross(dati_cross: DatiCross) -> list[str]:
    """Tabella 4: distribuzione Cross iterativa — formato storico.

    Colonne: una per ogni estremo di asta (intestazione da dati_cross.intestazioni_colonne).
    Righe:   MIP / dist1 / t/o1 / dist2 / ... / TOTALE
    """
    righe = _intestazione_tabella(4, "Distribuzione iterativa — Metodo di Cross-Pozzati")

    colonne = getattr(dati_cross, "intestazioni_colonne", None)
    if not colonne:
        # Costruisci da momenti_finali
        colonne = [f"A{id_a}i" for id_a in dati_cross.momenti_finali]
        colonne += [f"A{id_a}j" for id_a in dati_cross.momenti_finali]

    largh_col = max(10, max(len(c) for c in colonne) + 2)
    n_col = len(colonne)
    largh_tipo = 8

    # Intestazione colonne
    intestazione = f"{'Iter.':>{largh_tipo}}"
    for c in colonne:
        intestazione += f" │ {c:>{largh_col}}"
    righe.append(intestazione)
    righe.append("─" * (largh_tipo + (largh_col + 3) * n_col))

    # Righe iterazioni
    for riga in dati_cross.iterazioni:
        tipo_str = riga.tipo[:largh_tipo].rjust(largh_tipo)
        r = tipo_str
        for col in colonne:
            val = riga.momenti.get(col)
            if val is None:
                r += f" │ {'':>{largh_col}}"
            else:
                r += f" │ {int(round(val)):>{largh_col}}"
        righe.append(r)

        # Separatore dopo MIP e prima di TOTALE
        if riga.tipo in ("MIP", "totale"):
            righe.append("─" * (largh_tipo + (largh_col + 3) * n_col))

    # Info convergenza
    righe.append("")
    righe.append(
        f"Iterazioni: {dati_cross.n_iterazioni}   |   "
        f"Errore residuo: {dati_cross.errore_residuo:.2f} kg·cm   |   "
        f"Convergenza: {'SÌ' if dati_cross.convergenza else 'NO (check modello!)'}"
    )
    righe.append(_SEP2)

    return righe


# ==============================================================================
# TABELLA 5 — SOLLECITAZIONI PER ASTA E COMBINAZIONE
# ==============================================================================


def tabella_5_sollecitazioni(
    modello: ModelloTelaio,
    risultati: dict[str, RisultatoCasoCarico],
) -> list[str]:
    """Tabella 5: sollecitazioni M/V/N per asta e combinazione."""
    righe = _intestazione_tabella(5, "Sollecitazioni per asta e combinazione di carico")
    righe.append(
        f"{'Asta':>5} │ {'Etich.':>7} │ {'Caso':>5} │ "
        f"{'M_i [kg·cm]':>13} │ {'M_mid':>12} │ {'M_j':>12} │ "
        f"{'V_i [kg]':>10} │ {'V_j':>8} │ {'N [kg]':>9}"
    )
    righe.append(_SEP2)

    for id_caso, ris in risultati.items():
        for id_asta, soll in ris.sollecitazioni.items():
            asta = modello.asta_by_id(id_asta)
            etich = asta.etichetta if asta else str(id_asta)
            M = soll.M
            V = soll.V
            N = soll.N
            riga = (
                f"{id_asta:>5} │ {etich:>7} │ {id_caso:>5} │ "
                f"{_int_str(M[0] if M else None):>13} │ "
                f"{_int_str(M[1] if M and len(M) > 1 else None):>12} │ "
                f"{_int_str(M[2] if M and len(M) > 2 else None):>12} │ "
                f"{_int_str(V[0] if V else None):>10} │ "
                f"{_int_str(V[2] if V and len(V) > 2 else None):>8} │ "
                f"{_int_str(N[1] if N and len(N) > 1 else None):>9}"
            )
            righe.append(riga)

    righe.append(_SEP2)
    return righe


# ==============================================================================
# TABELLA 6 — INVILUPPO SOLLECITAZIONI
# ==============================================================================


def tabella_6_inviluppo(
    modello: ModelloTelaio,
    inviluppo: dict[int, InviluppoSollecitazioniAsta],
) -> list[str]:
    """Tabella 6: inviluppo M/V/N max e min per sezione."""
    righe = _intestazione_tabella(6, "Inviluppo sollecitazioni")
    righe.append(
        f"{'Asta':>5} │ {'Etich.':>7} │ {'Sez.':>5} │ "
        f"{'M_max [kg·cm]':>14} │ {'M_min':>12} │ "
        f"{'V_max [kg]':>11} │ {'V_min':>9} │ "
        f"{'N_max [kg]':>11} │ {'N_min':>9} │ "
        f"{'M_gov (sisma)':>14} │ {'N_gov':>9}"
    )
    righe.append(_SEP2)

    nomi_sez = ["i", "mid", "j"]

    for id_asta, inv in inviluppo.items():
        asta = modello.asta_by_id(id_asta)
        etich = asta.etichetta if asta else str(id_asta)

        # Per-section attrs: _i (sezione 0), _m (mezzeria, sezione 1), _j (sezione 2)
        _M_max = [inv.M_max_i, inv.M_max_m, inv.M_max_j]
        _M_min = [inv.M_min_i, inv.M_min_m, inv.M_min_j]
        _V_max = [inv.V_max_i, inv.V_max_m, inv.V_max_j]
        _V_min = [inv.V_min_i, inv.V_min_m, inv.V_min_j]
        _N_max = [inv.N_max_i, inv.N_max_m, inv.N_max_j]
        _N_min = [inv.N_min_i, inv.N_min_m, inv.N_min_j]
        _M_gov = [inv.M_gov_i, inv.M_gov_m, inv.M_gov_j]
        _N_gov = [inv.N_gov_i, inv.N_gov_m, inv.N_gov_j]

        for idx, sez_nome in enumerate(nomi_sez):
            M_max = _M_max[idx]
            M_min = _M_min[idx]
            V_max = _V_max[idx]
            V_min = _V_min[idx]
            N_max = _N_max[idx]
            N_min = _N_min[idx]
            M_gov = _M_gov[idx]
            N_gov = _N_gov[idx]

            prefisso = f"{id_asta:>5} │ {etich:>7}" if idx == 0 else f"{'':>5} │ {'':>7}"
            riga = (
                f"{prefisso} │ {sez_nome:>5} │ "
                f"{_int_str(M_max):>14} │ {_int_str(M_min):>12} │ "
                f"{_int_str(V_max):>11} │ {_int_str(V_min):>9} │ "
                f"{_int_str(N_max):>11} │ {_int_str(N_min):>9} │ "
                f"{_int_str(M_gov):>14} │ {_int_str(N_gov):>9}"
            )
            righe.append(riga)

        righe.append(_SEP3)

    return righe


# ==============================================================================
# TABELLA 7 — SCHEDE SANTARELLA ARMATURA
# ==============================================================================


def tabella_7_armature(
    schede: list[SchedaArmatura],
    verifiche: dict[int, RisultatoVerificaAsta] | None = None,
) -> list[str]:
    """Tabella 7: schede armatura stile Santarella per ogni asta."""
    righe = _intestazione_tabella(7, "Schede armatura — stile Santarella (RD 2229/39)")

    riepilogo = riepilogo_verifiche(verifiche) if verifiche else None

    for scheda in schede:
        righe.extend(scheda.righe_tabulato())

    # Riepilogo finale
    if riepilogo:
        righe.append(_SEP)
        righe.append(_centro("RIEPILOGO VERIFICHE"))
        righe.append(_SEP2)
        righe.append(
            f"Aste verificate: {riepilogo['n_aste']}   |   "
            f"OK: {riepilogo['n_ok']}   |   "
            f"NON OK: {riepilogo['n_ko']}"
        )
        if riepilogo["asta_critica"] is not None:
            righe.append(
                f"Asta critica: {riepilogo['asta_critica']}   |   "
                f"Utilizzazione max: {riepilogo['utilizzazione_max']:.1%}"
            )
        righe.append(_SEP2)

        # Tabella per asta
        righe.append(
            f"{'Asta':>6} │ {'Semaforo':>9} │ {'Util. max':>10} │ {'Check governante':<30}"
        )
        righe.append(_SEP3)
        for id_a, info in riepilogo["per_asta"].items():
            util_str = f"{info['utilizzazione_max']:.1%}" if info["utilizzazione_max"] is not None else "—"
            riga = (
                f"{id_a:>6} │ {info['semaforo']:>9} │ {util_str:>10} │ "
                f"{str(info['check_governante'] or '—'):<30}"
            )
            righe.append(riga)
        righe.append(_SEP2)

    return righe


# ==============================================================================
# TABULATO COMPLETO ASCII
# ==============================================================================


def genera_tabulato_ascii(
    modello: ModelloTelaio,
    risultati_per_caso: dict[str, RisultatoCasoCarico],
    dati_cross_per_caso: dict[str, DatiCross],
    inviluppo: dict[int, InviluppoSollecitazioniAsta],
    armature: dict[int, dict[str, ArmaturaSezioneSemplice]] | None = None,
    verifiche: dict[int, RisultatoVerificaAsta] | None = None,
    caso_principale: str = "LC2",
) -> str:
    """Genera il tabulato ASCII completo (Tabelle 0–7).

    Args:
        modello: Modello telaio.
        risultati_per_caso: {id_caso: RisultatoCasoCarico}.
        dati_cross_per_caso: {id_caso: DatiCross}.
        inviluppo: Inviluppo sollecitazioni.
        armature: Armature (opzionale; se None Tabella 7 non viene generata).
        verifiche: Risultati verifiche (opzionale).
        caso_principale: ID del caso usato per Tabella 4 (default LC2).

    Returns:
        Stringa ASCII del tabulato completo.
    """
    linee: list[str] = []

    # Intestazione
    linee.append(_SEP)
    linee.append(_centro("CALCOLO TELAIO PIANO IN C.A. — METODO DI CROSS-POZZATI"))
    linee.append(_centro("RD 2229/1939 — Tensioni Ammissibili (TA)"))
    linee.append(_centro(f"Modello: {modello.nome}"))
    linee.append(_centro(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}"))
    linee.append(_SEP)

    # Riepilogo modello
    nodi_liberi = modello.nodi_liberi()
    linee.append(
        f"Nodi: {len(modello.nodi)}   |   "
        f"Aste: {len(modello.aste)}   |   "
        f"Piani: {len(modello.piani)}   |   "
        f"Nodi liberi: {len(nodi_liberi)}   |   "
        f"Zona sismica: {modello.zona_sismica}"
    )
    linee.append(_SEP)

    # Tabella 0
    linee.extend(tabella_0_vincoli(modello))

    # Tabella 1
    linee.extend(tabella_1_sezioni(modello))

    # Tabella 2 — usa caso principale
    dc_principale = dati_cross_per_caso.get(caso_principale)
    if dc_principale is None and dati_cross_per_caso:
        dc_principale = next(iter(dati_cross_per_caso.values()))
    if dc_principale:
        linee.extend(tabella_2_fattori(modello, dc_principale))
        linee.extend(tabella_3_mip(modello, dc_principale))
        linee.extend(tabella_4_cross(dc_principale))

    # Tabella 5
    linee.extend(tabella_5_sollecitazioni(modello, risultati_per_caso))

    # Tabella 6
    linee.extend(tabella_6_inviluppo(modello, inviluppo))

    # Tabella 7
    if armature:
        schede = genera_schede_santarella(modello, armature, inviluppo, verifiche)
        linee.extend(tabella_7_armature(schede, verifiche))

    linee.append(_SEP)
    linee.append(_centro("FINE TABULATO"))
    linee.append(_SEP)

    return "\n".join(linee)


# ==============================================================================
# REPORT HTML
# ==============================================================================


def _html_riga(*celle: str, intestazione: bool = False) -> str:
    tag = "th" if intestazione else "td"
    celle_html = "".join(f"<{tag}>{html_mod.escape(str(c))}</{tag}>" for c in celle)
    return f"<tr>{celle_html}</tr>"


def _html_tabella(righe_ascii: list[str], titolo: str = "") -> str:
    """Converte righe ASCII in una tabella HTML semplice."""
    linee_valide = [r for r in righe_ascii if r.strip() and "═" not in r and "─" not in r]
    if not linee_valide:
        return ""

    testo = "\n".join(linee_valide)
    testo_esc = html_mod.escape(testo)

    titolo_html = f"<h3>{html_mod.escape(titolo)}</h3>" if titolo else ""
    return (
        f"{titolo_html}"
        f'<pre class="tabulato">{testo_esc}</pre>'
    )


def genera_report_html(
    modello: ModelloTelaio,
    risultati_per_caso: dict[str, RisultatoCasoCarico],
    dati_cross_per_caso: dict[str, DatiCross],
    inviluppo: dict[int, InviluppoSollecitazioniAsta],
    armature: dict[int, dict[str, ArmaturaSezioneSemplice]] | None = None,
    verifiche: dict[int, RisultatoVerificaAsta] | None = None,
    caso_principale: str = "LC2",
) -> str:
    """Genera report HTML completo con tutte le tabelle storiche.

    Returns:
        Stringa HTML del report completo.
    """
    # Genera prima il tabulato ASCII poi lo include in un template HTML
    ascii_completo = genera_tabulato_ascii(
        modello=modello,
        risultati_per_caso=risultati_per_caso,
        dati_cross_per_caso=dati_cross_per_caso,
        inviluppo=inviluppo,
        armature=armature,
        verifiche=verifiche,
        caso_principale=caso_principale,
    )

    # Riepilogo verifiche per semaforo HTML
    rit_riepilogo = ""
    if verifiche:
        rit = riepilogo_verifiche(verifiche)
        colore = "#28a745" if rit["n_ko"] == 0 else "#dc3545"
        rit_riepilogo = f"""
        <div class="riepilogo" style="border-left: 5px solid {colore}; padding: 10px; margin: 20px 0;">
          <strong>RIEPILOGO VERIFICHE:</strong>
          Aste verificate: {rit['n_aste']} —
          OK: {rit['n_ok']} —
          NON OK: {rit['n_ko']}
          {'✅ TELAIO VERIFICATO' if rit['n_ko'] == 0 else '❌ VERIFICHE NON SUPERATE'}
        </div>
        """

    html = f"""<!DOCTYPE html>
<html lang="it">
<head>
  <meta charset="UTF-8">
  <title>Calcolo Telaio Piano — {html_mod.escape(modello.nome)}</title>
  <style>
    body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 40px; color: #222; }}
    h1 {{ color: #1a3a5c; border-bottom: 3px solid #1a3a5c; padding-bottom: 8px; }}
    h2 {{ color: #2c5f8a; border-bottom: 1px solid #aaa; padding-bottom: 4px; }}
    h3 {{ color: #444; }}
    pre.tabulato {{
      font-family: 'Courier New', Courier, monospace;
      font-size: 11px;
      background: #f8f9fa;
      border: 1px solid #dee2e6;
      border-radius: 4px;
      padding: 15px;
      overflow-x: auto;
      white-space: pre;
    }}
    .riepilogo {{ background: #f8f9fa; border-radius: 4px; }}
    .info-riga {{ display: flex; gap: 30px; margin-bottom: 10px; }}
    .info-riga span {{ background: #e9ecef; padding: 4px 10px; border-radius: 3px; }}
    table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
    th, td {{ border: 1px solid #dee2e6; padding: 6px 10px; text-align: right; }}
    th {{ background: #1a3a5c; color: white; }}
    tr:nth-child(even) {{ background: #f8f9fa; }}
  </style>
</head>
<body>
  <h1>Calcolo Telaio Piano in C.A.<br>
      <small>Metodo di Cross-Pozzati — RD 2229/1939</small></h1>

  <div class="info-riga">
    <span><strong>Modello:</strong> {html_mod.escape(modello.nome)}</span>
    <span><strong>Nodi:</strong> {len(modello.nodi)}</span>
    <span><strong>Aste:</strong> {len(modello.aste)}</span>
    <span><strong>Piani:</strong> {len(modello.piani)}</span>
    <span><strong>Zona sismica:</strong> {html_mod.escape(modello.zona_sismica)}</span>
    <span><strong>Data:</strong> {datetime.now().strftime('%d/%m/%Y')}</span>
  </div>

  {rit_riepilogo}

  <h2>Tabulato di Calcolo Completo</h2>
  <pre class="tabulato">{html_mod.escape(ascii_completo)}</pre>

  <hr>
  <p style="font-size:10px;color:#888;">
    Generato da RD2229 — Calcolo strutturale per edifici esistenti in c.a.<br>
    Riferimento normativo: RD 2229/1939 — Metodo tensioni ammissibili (TA)<br>
    Metodo di calcolo: Hardy Cross (1930) — Adattamento Pozzati
  </p>
</body>
</html>"""

    return html


# ==============================================================================
# EXPORT SU FILE
# ==============================================================================


def salva_tabulato(
    percorso: str,
    modello: ModelloTelaio,
    risultati_per_caso: dict[str, RisultatoCasoCarico],
    dati_cross_per_caso: dict[str, DatiCross],
    inviluppo: dict[int, InviluppoSollecitazioniAsta],
    armature: dict[int, dict[str, ArmaturaSezioneSemplice]] | None = None,
    verifiche: dict[int, RisultatoVerificaAsta] | None = None,
    formato: str = "txt",
    caso_principale: str = "LC2",
) -> None:
    """Salva il tabulato su file.

    Args:
        percorso: Percorso del file di output.
        formato: "txt" per ASCII, "html" per HTML.
        caso_principale: ID combinazione per Tabella 4.
    """
    if formato == "html":
        contenuto = genera_report_html(
            modello, risultati_per_caso, dati_cross_per_caso,
            inviluppo, armature, verifiche, caso_principale,
        )
    else:
        contenuto = genera_tabulato_ascii(
            modello, risultati_per_caso, dati_cross_per_caso,
            inviluppo, armature, verifiche, caso_principale,
        )

    with open(percorso, "w", encoding="utf-8") as f:
        f.write(contenuto)
