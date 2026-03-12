"""Cordolo metallico reticolare in sommità a pareti in muratura.

Verifica e dimensionamento di un cordolo reticolare piano (Warren o Pratt)
da disporre orizzontalmente in sommità ai muri. Fornisce un ritegno H
che aumenta alpha_0 nei meccanismi di ribaltamento fuori piano.

Schema strutturale:
  - Il traliccio giace nel piano XY orizzontale
  - X = direzione muro (span), Y = spessore muro (profondità traliccio h)
  - F_sismica agisce in Y (direzione forte del Warren)
  - Cerniera a x=0, Carrello_X a x=L (alle pareti trasversali)

Unità: cm per geometria, kg per forze, kg/cm² per tensioni.

Riferimenti:
  - NTC2018 §8.7 (interventi su edifici esistenti)
  - Circolare n.7/2019 §C8.7 (rinforzo muratura)
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum

from ..steel.connessioni import InputSaldatura, verifica_saldatura_ta
from ..steel.sezione_asta import SezioneAsta
from ..steel.traliccio_2d import (
    distribuisci_carico_corrente,
    risolvi_traliccio,
    verifica_aste_traliccio,
)
from ..steel.traliccio_generatore import (
    applica_vincoli_cordolo,
    genera_howe,
    genera_pratt,
    valida_geometria,
)
from ..steel.verifiche_ta import SIGMA_ADM_TA


class SchemaReticolare(str, Enum):
    """Schema geometrico del traliccio."""

    HOWE = "howe"
    PRATT = "pratt"


class TipoCollegamentoMuro(str, Enum):
    """Tipo di collegamento traliccio-muro."""

    INGHISAGGIO = "inghisaggio"  # barre inghisate nella muratura
    TASSELLO_CHIMICO = "tassello_chimico"  # tassello chimico (F_Rd da utente — TODO)
    CONNETTORE = "connettore"  # connettore meccanico


@dataclass
class CordoloReticolare:
    """Dati geometrici e meccanici del cordolo reticolare."""

    schema: SchemaReticolare
    n_campate: int
    L: float  # lunghezza [cm]
    h: float  # profondità = spessore muro [cm]
    sezione_corrente: SezioneAsta
    sezione_diagonale: SezioneAsta
    tipo_acciaio: str = "Fe430"
    tipo_estremi: str = "cerniera"  # "cerniera" (appoggio libero) o "incastro" (fine fissa)
    tipo_collegamento_muro: TipoCollegamentoMuro = TipoCollegamentoMuro.INGHISAGGIO
    n_ancoraggi_per_nodo: int = 2
    phi_ancoraggio: float = 1.6  # diametro ancoraggio [cm]
    schema_chiusura: str = "muro_singolo"
    # TODO: schema_chiusura "anello_c1" / "anello_c2" (D.3.2-ext)
    # TODO: rigidezza_collegamento_muro: float | None = None  (Winkler)

    def to_dict(self) -> dict:
        return {
            "schema": self.schema.value,
            "n_campate": self.n_campate,
            "L": self.L,
            "h": self.h,
            "sezione_corrente": self.sezione_corrente.nome,
            "sezione_diagonale": self.sezione_diagonale.nome,
            "tipo_acciaio": self.tipo_acciaio,
            "tipo_estremi": self.tipo_estremi,
            "tipo_collegamento_muro": self.tipo_collegamento_muro.value,
            "n_ancoraggi_per_nodo": self.n_ancoraggi_per_nodo,
            "phi_ancoraggio": self.phi_ancoraggio,
        }


@dataclass
class RisultatoCordoloReticolare:
    """Risultato completo della verifica del cordolo reticolare."""

    convergenza: bool
    K_globale: float  # rigidezza [kg/cm]
    delta_max: float  # spostamento max [cm]
    N_max_compressione: float  # sforzo max compressione [kg] (negativo)
    N_max_trazione: float  # sforzo max trazione [kg] (positivo)
    verifiche_aste: list[dict]
    verifica_collegamento: dict  # F3: tau_nodo vs tau_adm
    verifica_nodi: list[dict]  # H1: nodi d'angolo e nodi più sollecitati
    F_ritegno_disponibile: float  # F massima che il cordolo può fornire [kg]
    avvisi_geometria: list[str] = field(default_factory=list)
    fatica: None = None  # TODO placeholder fatica ciclica sismica
    passaggi: list[str] = field(default_factory=list)

    @property
    def verificato(self) -> bool:
        """True se tutte le verifiche sono soddisfatte."""
        if not self.convergenza:
            return False
        if not all(v.get("verificato", False) for v in self.verifiche_aste):
            return False
        if not self.verifica_collegamento.get("verificato", False):
            return False
        return True

    def to_dict(self) -> dict:
        return {
            "convergenza": self.convergenza,
            "K_globale": round(self.K_globale, 2),
            "delta_max": round(self.delta_max, 4),
            "N_max_compressione": round(self.N_max_compressione, 1),
            "N_max_trazione": round(self.N_max_trazione, 1),
            "F_ritegno_disponibile": round(self.F_ritegno_disponibile, 1),
            "verifiche_aste": self.verifiche_aste,
            "verifica_collegamento": self.verifica_collegamento,
            "verifica_nodi": self.verifica_nodi,
            "avvisi_geometria": self.avvisi_geometria,
            "verificato": self.verificato,
            "passaggi": self.passaggi,
        }


def calcola_F_ritegno(
    risultato_cin: object,
    alpha_0_target: float,
    h_sommita: float,
    metodo: str = "D1",
) -> float:
    """Calcola la forza di ritegno H necessaria per raggiungere alpha_0_target.

    D1 (rigoroso): F = (alpha_0_target * M_rib_coeff - M_stab) / h_sommita
    D3 (lineare):  F = (alpha_0_target - alpha_0_att) * M_rib_coeff / h_sommita

    Args:
        risultato_cin:  RisultatoCinematica dalla cinematica.py
        alpha_0_target: moltiplicatore target
        h_sommita:      braccio del ritegno = altezza parete [cm]
        metodo:         "D1" (default) o "D3"

    Returns:
        Forza di ritegno H [kg]
    """
    M_stab = getattr(risultato_cin, "forze_stabilizzanti", 0.0)
    M_rib_coeff = getattr(risultato_cin, "forze_ribaltanti", 0.0)
    alpha_0_att = getattr(risultato_cin, "alpha_0", 0.0)

    if h_sommita <= 0 or M_rib_coeff <= 0:
        return 0.0

    if metodo == "D1":
        M_ritegno = alpha_0_target * M_rib_coeff - M_stab
        return max(0.0, M_ritegno / h_sommita)
    else:  # D3
        delta_alpha = alpha_0_target - alpha_0_att
        return max(0.0, delta_alpha * M_rib_coeff / h_sommita)


def _verifica_collegamento_f3(
    cordolo: CordoloReticolare,
    F_nodo_max: float,
    sigma_adm: float,
) -> dict:
    """F3 — Verifica collegamento traliccio-muro a taglio.

    tau = F_nodo / A_ancoraggi ≤ tau_adm = sigma_adm / sqrt(3)
    """
    phi = cordolo.phi_ancoraggio
    n = cordolo.n_ancoraggi_per_nodo
    A_tot = n * math.pi * (phi / 2) ** 2
    tau_adm = sigma_adm / math.sqrt(3)
    tau = abs(F_nodo_max) / A_tot if A_tot > 0 else 0.0
    return {
        "F_nodo_max": F_nodo_max,
        "n_ancoraggi": n,
        "phi_ancoraggio": phi,
        "A_tot": A_tot,
        "tau": tau,
        "tau_adm": tau_adm,
        "sfruttamento": tau / tau_adm if tau_adm > 0 else 0.0,
        "verificato": tau <= tau_adm,
    }


def verifica_cordolo_reticolare(
    cordolo: CordoloReticolare,
    F_y: float,
    sigma_adm: float | None = None,
) -> RisultatoCordoloReticolare:
    """Verifica completa cordolo reticolare sotto forza sismica F_y.

    Sequenza:
    1. Genera schema (Warren o Pratt)
    2. Applica vincoli
    3. Distribuisce F_y come carico uniforme sul corrente sup (y=h)
    4. Risolve traliccio
    5. Verifica aste (trazione/compressione + instabilità biassiale)
    6. Verifica collegamento muro F3
    7. Calcola F_ritegno_disponibile

    Args:
        cordolo:   dati geometrici e meccanici
        F_y:       forza sismica totale in Y [kg]
        sigma_adm: tensione ammissibile override [kg/cm²]
    """
    passaggi: list[str] = []
    sigma_adm_val = sigma_adm or SIGMA_ADM_TA.get(cordolo.tipo_acciaio, 1900.0)

    passaggi.append("═══ VERIFICA CORDOLO RETICOLARE ═══")
    passaggi.append(
        f"Schema: {cordolo.schema.value}, n={cordolo.n_campate}, "
        f"L={cordolo.L:.0f} cm, h={cordolo.h:.0f} cm"
    )
    passaggi.append(
        f"Corrente: {cordolo.sezione_corrente.nome}, "
        f"Diagonale: {cordolo.sezione_diagonale.nome}"
    )
    passaggi.append(f"F_y = {F_y:.0f} kg, σ_adm = {sigma_adm_val:.0f} kg/cm²")

    # 1. Genera schema
    if cordolo.schema == SchemaReticolare.HOWE:
        nodi, aste = genera_howe(
            cordolo.L,
            cordolo.h,
            cordolo.n_campate,
            cordolo.sezione_corrente,
            cordolo.sezione_diagonale,
        )
    else:
        nodi, aste = genera_pratt(
            cordolo.L,
            cordolo.h,
            cordolo.n_campate,
            cordolo.sezione_corrente,
            cordolo.sezione_diagonale,
        )

    # Validazione geometria
    avvisi = valida_geometria(nodi, aste)
    if avvisi:
        for av in avvisi:
            passaggi.append(f"  {av}")

    # 2. Vincoli standard cordolo
    nodi = applica_vincoli_cordolo(
        nodi,
        cordolo.n_campate,
        tipo_estremi=cordolo.tipo_estremi,
    )

    # 3. Carico distribuito F_y sul corrente superiore (y=h)
    n = cordolo.n_campate
    id_sup = list(range(n + 1, 2 * n + 2))  # nodi n+1..2n+1
    q_y = F_y / cordolo.L  # [kg/cm]
    nodi = distribuisci_carico_corrente(nodi, id_sup, q_y)
    passaggi.append(f"Carico distribuito: q_y = {q_y:.4f} kg/cm sul corrente sup")

    # 4. Soluzione
    risultato = risolvi_traliccio(nodi, aste)
    if not risultato.convergenza:
        return RisultatoCordoloReticolare(
            convergenza=False,
            K_globale=0.0,
            delta_max=0.0,
            N_max_compressione=0.0,
            N_max_trazione=0.0,
            verifiche_aste=[],
            verifica_collegamento={"verificato": False},
            verifica_nodi=[],
            F_ritegno_disponibile=0.0,
            avvisi_geometria=avvisi,
            passaggi=passaggi + [f"ERRORE: {risultato.errore}"],
        )

    passaggi.append(
        f"K_globale = {risultato.K_globale:.1f} kg/cm, " f"δ_max = {risultato.delta_max:.4f} cm"
    )

    # 5. Verifica aste
    sezioni = {
        a.id: (
            cordolo.sezione_corrente
            if a.nome_profilo == cordolo.sezione_corrente.nome
            else cordolo.sezione_diagonale
        )
        for a in aste
    }
    verifiche = verifica_aste_traliccio(
        risultato,
        sigma_adm_traz=sigma_adm_val,
        sigma_adm_comp=sigma_adm_val,
        aste_input=aste,
        sezioni=sezioni,
    )

    N_vals = [ra.N for ra in risultato.aste]
    N_max_comp = min(N_vals) if N_vals else 0.0
    N_max_traz = max(N_vals) if N_vals else 0.0

    # Sfruttamento massimo
    sfr_max = max((v.get("sfruttamento", 0.0) for v in verifiche), default=0.0)
    passaggi.append(f"N_max_comp = {N_max_comp:.0f} kg, N_max_traz = {N_max_traz:.0f} kg")
    passaggi.append(f"Sfruttamento max aste = {sfr_max:.3f}")

    # 6. Verifica collegamento muro (F3)
    # Reazione massima al nodo: max delle reazioni vincolari in Y
    reaz_y = [abs(r[1]) for r in risultato.reazioni.values()]
    F_nodo_max = max(reaz_y) if reaz_y else 0.0
    ver_colleg = _verifica_collegamento_f3(cordolo, F_nodo_max, sigma_adm_val)
    passaggi.append(
        f"Collegamento: F_nodo={F_nodo_max:.0f} kg, "
        f"τ={ver_colleg['tau']:.1f} kg/cm², τ_adm={ver_colleg['tau_adm']:.1f} kg/cm² "
        f"→ {'OK' if ver_colleg['verificato'] else 'NON OK'}"
    )

    # 7. F_ritegno_disponibile: max F_y per cui tutte le verifiche sono soddisfatte
    # Approssimazione lineare: scala F_y per 1/sfr_max
    if sfr_max > 0:
        F_ritegno = F_y / sfr_max
    else:
        F_ritegno = F_y
    # Limita anche dalla verifica collegamento
    if ver_colleg["sfruttamento"] > 0:
        F_colleg = F_y / ver_colleg["sfruttamento"]
        F_ritegno = min(F_ritegno, F_colleg)
    passaggi.append(f"F_ritegno_disponibile ≈ {F_ritegno:.0f} kg")

    return RisultatoCordoloReticolare(
        convergenza=True,
        K_globale=risultato.K_globale,
        delta_max=risultato.delta_max,
        N_max_compressione=N_max_comp,
        N_max_trazione=N_max_traz,
        verifiche_aste=verifiche,
        verifica_collegamento=ver_colleg,
        verifica_nodi=[],  # H1 popolato da verifica_nodi_angolo se chiamata
        F_ritegno_disponibile=F_ritegno,
        avvisi_geometria=avvisi,
        passaggi=passaggi,
    )


def dimensiona_cordolo_reticolare(
    schema: SchemaReticolare,
    n_campate: int,
    L: float,
    h: float,
    F_y: float,
    tipo_acciaio: str = "Fe430",
    famiglia_corrente: str = "PIATTO",
    famiglia_diagonale: str = "PIATTO",
) -> CordoloReticolare | None:
    """G1 — Dimensionamento automatico del cordolo reticolare.

    Cerca il profilo minimo (per A crescente) per corrente e diagonale
    che verifica tutte le condizioni sotto F_y.

    Args:
        schema:            Warren o Pratt
        n_campate:         numero pannelli
        L:                 lunghezza [cm]
        h:                 profondità [cm]
        F_y:               forza sismica [kg]
        tipo_acciaio:      "Fe430", "Fe360", etc.
        famiglia_corrente: "PIATTO" o "ANGOLARE"
        famiglia_diagonale: "PIATTO" o "ANGOLARE"

    Returns:
        CordoloReticolare dimensionato, oppure None se nessuna combinazione verifica
    """
    from ..steel.sezione_asta import carica_catalogo_angolari, carica_catalogo_piatti

    cat_c = (
        carica_catalogo_angolari()
        if famiglia_corrente.upper() == "ANGOLARE"
        else carica_catalogo_piatti()
    )
    cat_d = (
        carica_catalogo_angolari()
        if famiglia_diagonale.upper() == "ANGOLARE"
        else carica_catalogo_piatti()
    )

    for sez_c in cat_c.tutti():
        for sez_d in cat_d.tutti():
            cordolo = CordoloReticolare(
                schema=schema,
                n_campate=n_campate,
                L=L,
                h=h,
                sezione_corrente=sez_c,
                sezione_diagonale=sez_d,
                tipo_acciaio=tipo_acciaio,
            )
            res = verifica_cordolo_reticolare(cordolo, F_y)
            if res.verificato:
                return cordolo

    return None


# ═══════════════════════════════════════════════════════════
#  D.3.6 — Nodo d'angolo (cantonali)
# ═══════════════════════════════════════════════════════════


@dataclass
class InputNodoAngolo:
    """Input per verifica nodo d'angolo tra due cordoli."""

    F_muro1: float  # forza dal muro 1 [kg]
    F_muro2: float  # forza dal muro 2 [kg]
    angolo_giunzione: float = 90.0  # angolo tra i muri [gradi]
    a_saldatura: float = 0.6  # gola cordone saldatura [cm]
    L_saldatura: float = 10.0  # lunghezza efficace saldatura [cm]
    n_cordoni: int = 2  # numero cordoni saldatura
    tipo_acciaio: str = "Fe430"


def verifica_nodo_angolo(inp: InputNodoAngolo) -> dict:
    """H1 — Verifica nodo d'angolo tra due cordoli reticolari.

    Calcola la risultante delle forze dai due muri e verifica la
    saldatura di giunzione con verifica_saldatura_ta().

    F_risultante = sqrt(F1² + F2² + 2·F1·F2·cos(angolo))
    """
    theta = math.radians(inp.angolo_giunzione)
    F_ris = math.sqrt(
        inp.F_muro1**2 + inp.F_muro2**2 + 2 * inp.F_muro1 * inp.F_muro2 * math.cos(theta)
    )

    # Verifica saldatura
    inp_sald = InputSaldatura(
        a=inp.a_saldatura,
        L=inp.L_saldatura,
        n_cordoni=inp.n_cordoni,
        N=F_ris,
        tipo_acciaio=inp.tipo_acciaio,
    )
    res_sald = verifica_saldatura_ta(inp_sald)

    return {
        "F_muro1": inp.F_muro1,
        "F_muro2": inp.F_muro2,
        "angolo_giunzione": inp.angolo_giunzione,
        "F_risultante": F_ris,
        "a_saldatura": inp.a_saldatura,
        "L_saldatura": inp.L_saldatura,
        "verifica_saldatura": res_sald.to_dict() if hasattr(res_sald, "to_dict") else res_sald,
        "verificato": res_sald.verificato if hasattr(res_sald, "verificato") else False,
    }
