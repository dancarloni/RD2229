"""Combinazioni di carico e inviluppo delle sollecitazioni — RD 2229/39.

Genera le combinazioni di carico previste dalla normativa RD 2229/39
e calcola l'inviluppo delle sollecitazioni su tutte le combinazioni.

Combinazioni attive per zona sismica:
    LC1: G              (peso proprio)                     — sempre
    LC2: G + Q          (permanente + variabile)            — sempre
    LC3: G + Q + E_x+   (+ sisma ondulatorio +X)           — zone bassa/media/alta
    LC4: G + Q + E_x-   (+ sisma ondulatorio -X)           — zone bassa/media/alta
    LC5: G + Q + E_z+   (+ sisma sussultorio +Z)           — zone media/alta
    LC6: G + Q + E_z-   (+ sisma sussultorio -Z)           — zone media/alta
    LC7: G + Q + W      (+ vento)                          — opzionale

Per il progetto delle armature (indicazione utente):
    Per ogni asta, per ogni sezione (3 per asta), la coppia (M, N) governante
    è il massimo |M| tra LC3, LC4 (ondulatorio ±X) e LC5, LC6 (sussultorio ±Z),
    con il corrispondente N dello stesso caso.

Unità: kg [forze], cm [geometria], kg·cm [momenti].
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from .modello_telaio import CaricoAsta, ModelloTelaio, TipoCarico
from .sisma_telaio import ForzeSismicheTelaio, calcola_forze_sismiche
from .solver_telaio import RisultatoCasoCarico, calcola_caso_carico

# ==============================================================================
# STRUTTURE DATI
# ==============================================================================

@dataclass
class InviluppoSollecitazioniAsta:
    """Inviluppo delle sollecitazioni per un'asta su tutte le combinazioni.

    Per ogni sezione (0=estremo i, 1=mezzeria, 2=estremo j):
    - M_max/M_min: massimo positivo/negativo assoluto
    - combo_gov:   id combinazione che governa
    - M_N_gov:     coppia (M, N) governante per pressoflessione

    La coppia (M, N) governante per armature si ottiene da:
        max |M| tra LC3, LC4 (sisma ondulatorio ±X) e LC5, LC6 (sussultorio ±Z)
    con il corrispondente N dello stesso caso.
    """
    id_asta: int
    etichetta: str

    # Sezione 0 = estremo i
    M_max_i: float = 0.0;   combo_M_max_i: str = ""
    M_min_i: float = 0.0;   combo_M_min_i: str = ""
    V_max_i: float = 0.0;   combo_V_max_i: str = ""
    V_min_i: float = 0.0;   combo_V_min_i: str = ""
    N_max_i: float = 0.0;   combo_N_max_i: str = ""
    N_min_i: float = 0.0;   combo_N_min_i: str = ""
    M_gov_i: float = 0.0;   N_gov_i: float = 0.0;  combo_gov_i: str = ""

    # Sezione 1 = mezzeria
    M_max_m: float = 0.0;   combo_M_max_m: str = ""
    M_min_m: float = 0.0;   combo_M_min_m: str = ""
    V_max_m: float = 0.0;   combo_V_max_m: str = ""
    V_min_m: float = 0.0;   combo_V_min_m: str = ""
    N_max_m: float = 0.0;   combo_N_max_m: str = ""
    N_min_m: float = 0.0;   combo_N_min_m: str = ""
    M_gov_m: float = 0.0;   N_gov_m: float = 0.0;  combo_gov_m: str = ""

    # Sezione 2 = estremo j
    M_max_j: float = 0.0;   combo_M_max_j: str = ""
    M_min_j: float = 0.0;   combo_M_min_j: str = ""
    V_max_j: float = 0.0;   combo_V_max_j: str = ""
    V_min_j: float = 0.0;   combo_V_min_j: str = ""
    N_max_j: float = 0.0;   combo_N_max_j: str = ""
    N_min_j: float = 0.0;   combo_N_min_j: str = ""
    M_gov_j: float = 0.0;   N_gov_j: float = 0.0;  combo_gov_j: str = ""

    def M_gov(self, sezione: int) -> tuple[float, float, str]:
        """Ritorna (M_gov, N_gov, combo) per la sezione data (0, 1, 2)."""
        if sezione == 0:
            return self.M_gov_i, self.N_gov_i, self.combo_gov_i
        elif sezione == 1:
            return self.M_gov_m, self.N_gov_m, self.combo_gov_m
        else:
            return self.M_gov_j, self.N_gov_j, self.combo_gov_j

    def V_gov(self, sezione: int) -> float:
        """Taglio massimo assoluto alla sezione (governa per taglio)."""
        if sezione == 0:
            return max(abs(self.V_max_i), abs(self.V_min_i))
        elif sezione == 1:
            return max(abs(self.V_max_m), abs(self.V_min_m))
        else:
            return max(abs(self.V_max_j), abs(self.V_min_j))

    def to_dict(self) -> dict:
        return {
            "id_asta": self.id_asta,
            "etichetta": self.etichetta,
            "sezione_i": {
                "M_max": round(self.M_max_i, 1), "combo": self.combo_M_max_i,
                "M_min": round(self.M_min_i, 1),
                "M_gov": round(self.M_gov_i, 1), "N_gov": round(self.N_gov_i, 1),
                "combo_gov": self.combo_gov_i,
                "V_max": round(self.V_max_i, 1),
            },
            "sezione_mid": {
                "M_max": round(self.M_max_m, 1), "combo": self.combo_M_max_m,
                "M_min": round(self.M_min_m, 1),
                "M_gov": round(self.M_gov_m, 1), "N_gov": round(self.N_gov_m, 1),
                "combo_gov": self.combo_gov_m,
                "V_max": round(self.V_max_m, 1),
            },
            "sezione_j": {
                "M_max": round(self.M_max_j, 1), "combo": self.combo_M_max_j,
                "M_min": round(self.M_min_j, 1),
                "M_gov": round(self.M_gov_j, 1), "N_gov": round(self.N_gov_j, 1),
                "combo_gov": self.combo_gov_j,
                "V_max": round(self.V_max_j, 1),
            },
        }


@dataclass
class RisultatoCombinazioni:
    """Risultato completo di tutte le combinazioni di carico."""
    zona_sismica: str
    combinazioni_attive: list[str]
    risultati_per_caso: dict[str, RisultatoCasoCarico]
    inviluppo: dict[int, InviluppoSollecitazioniAsta]
    forze_sismiche: Optional[ForzeSismicheTelaio]
    passaggi: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "zona_sismica": self.zona_sismica,
            "combinazioni_attive": self.combinazioni_attive,
            "inviluppo": {
                str(k): v.to_dict() for k, v in self.inviluppo.items()
            },
        }


# ==============================================================================
# GENERAZIONE COMBINAZIONI
# ==============================================================================

def combinazioni_attive(zona_sismica: str) -> list[str]:
    """Restituisce le combinazioni attive per la zona sismica data."""
    base = ["LC1", "LC2"]
    if zona_sismica in ("bassa", "media", "alta"):
        base += ["LC3", "LC4"]
    if zona_sismica in ("media", "alta"):
        base += ["LC5", "LC6"]
    return base


_COMBO_SISMICI = {"LC3", "LC4", "LC5", "LC6"}


def _descrizione_caso(id_caso: str) -> str:
    descrizioni = {
        "LC1": "G — Peso proprio",
        "LC2": "G + Q — Permanente + variabile",
        "LC3": "G + Q + E_x+ — Sisma ondulatorio +X",
        "LC4": "G + Q + E_x- — Sisma ondulatorio -X",
        "LC5": "G + Q + E_z+ — Sisma sussultorio +Z",
        "LC6": "G + Q + E_z- — Sisma sussultorio -Z",
        "LC7": "G + Q + W — Vento",
    }
    return descrizioni.get(id_caso, id_caso)


# ==============================================================================
# INVILUPPO
# ==============================================================================

def _aggiorna_inviluppo_sezione(
    inv: InviluppoSollecitazioniAsta,
    sezione: int,
    M: float, V: float, N: float,
    id_caso: str,
    e_sismico: bool,
) -> None:
    """Aggiorna i valori max/min di una sezione nell'inviluppo."""
    if sezione == 0:
        if M > inv.M_max_i:
            inv.M_max_i = M; inv.combo_M_max_i = id_caso
        if M < inv.M_min_i:
            inv.M_min_i = M; inv.combo_M_min_i = id_caso
        if V > inv.V_max_i:
            inv.V_max_i = V; inv.combo_V_max_i = id_caso
        if V < inv.V_min_i:
            inv.V_min_i = V; inv.combo_V_min_i = id_caso
        if N > inv.N_max_i:
            inv.N_max_i = N; inv.combo_N_max_i = id_caso
        if N < inv.N_min_i:
            inv.N_min_i = N; inv.combo_N_min_i = id_caso
        if e_sismico and abs(M) > abs(inv.M_gov_i):
            inv.M_gov_i = M; inv.N_gov_i = N; inv.combo_gov_i = id_caso
    elif sezione == 1:
        if M > inv.M_max_m:
            inv.M_max_m = M; inv.combo_M_max_m = id_caso
        if M < inv.M_min_m:
            inv.M_min_m = M; inv.combo_M_min_m = id_caso
        if V > inv.V_max_m:
            inv.V_max_m = V; inv.combo_V_max_m = id_caso
        if V < inv.V_min_m:
            inv.V_min_m = V; inv.combo_V_min_m = id_caso
        if N > inv.N_max_m:
            inv.N_max_m = N; inv.combo_N_max_m = id_caso
        if N < inv.N_min_m:
            inv.N_min_m = N; inv.combo_N_min_m = id_caso
        if e_sismico and abs(M) > abs(inv.M_gov_m):
            inv.M_gov_m = M; inv.N_gov_m = N; inv.combo_gov_m = id_caso
    else:
        if M > inv.M_max_j:
            inv.M_max_j = M; inv.combo_M_max_j = id_caso
        if M < inv.M_min_j:
            inv.M_min_j = M; inv.combo_M_min_j = id_caso
        if V > inv.V_max_j:
            inv.V_max_j = V; inv.combo_V_max_j = id_caso
        if V < inv.V_min_j:
            inv.V_min_j = V; inv.combo_V_min_j = id_caso
        if N > inv.N_max_j:
            inv.N_max_j = N; inv.combo_N_max_j = id_caso
        if N < inv.N_min_j:
            inv.N_min_j = N; inv.combo_N_min_j = id_caso
        if e_sismico and abs(M) > abs(inv.M_gov_j):
            inv.M_gov_j = M; inv.N_gov_j = N; inv.combo_gov_j = id_caso


def calcola_inviluppo(
    aste_ids: list[int],
    aste_etichette: dict[int, str],
    risultati: dict[str, RisultatoCasoCarico],
    combinazioni: list[str],
) -> dict[int, InviluppoSollecitazioniAsta]:
    """Calcola l'inviluppo delle sollecitazioni su tutte le combinazioni.

    Per armature (indicazione utente):
        La coppia (M, N) governante è max |M| tra casi sismici
        (LC3, LC4, LC5, LC6) con N del medesimo caso.
    """
    inviluppo: dict[int, InviluppoSollecitazioniAsta] = {}

    for id_asta in aste_ids:
        inv = InviluppoSollecitazioniAsta(
            id_asta=id_asta,
            etichetta=aste_etichette.get(id_asta, str(id_asta)),
        )
        for id_caso in combinazioni:
            res = risultati.get(id_caso)
            if res is None:
                continue
            sol = res.sollecitazioni.get(id_asta)
            if sol is None:
                continue
            e_sismico = id_caso in _COMBO_SISMICI
            for s in range(3):
                _aggiorna_inviluppo_sezione(
                    inv, s,
                    sol.M[s], sol.V[s], sol.N[s],
                    id_caso, e_sismico,
                )
        inviluppo[id_asta] = inv

    return inviluppo


# ==============================================================================
# ENTRY POINT PRINCIPALE
# ==============================================================================

def calcola_tutte_le_combinazioni(
    modello: ModelloTelaio,
    carichi_variabili: dict[int, list[CaricoAsta]] | None = None,
    tolleranza: float = 0.5,
    max_iter: int = 200,
    n_punti: int = 21,
) -> RisultatoCombinazioni:
    """Calcola tutte le combinazioni di carico attive e l'inviluppo.

    Args:
        modello:           modello del telaio (zona_sismica usata per combinazioni)
        carichi_variabili: {id_asta: [carichi Q]} — carichi variabili da aggiungere
                           a LC2..LC7. None = nessun carico variabile.
        tolleranza, max_iter, n_punti: parametri calcolo Cross

    Returns:
        RisultatoCombinazioni con tutti i casi e l'inviluppo
    """
    passaggi: list[str] = [
        f"=== COMBINAZIONI RD2229/39 — Zona: {modello.zona_sismica} ==="
    ]

    combos = combinazioni_attive(modello.zona_sismica)
    passaggi.append(f"Combinazioni attive: {', '.join(combos)}")

    # ---- Forze sismiche ----
    forze_sismiche: Optional[ForzeSismicheTelaio] = None
    if any(c in combos for c in _COMBO_SISMICI):
        forze_sismiche = calcola_forze_sismiche(modello)
        passaggi.extend(forze_sismiche.passaggi)

    # ---- Calcolo per ogni combinazione ----
    risultati: dict[str, RisultatoCasoCarico] = {}

    for id_caso in combos:
        desc = _descrizione_caso(id_caso)
        passaggi.append(f"\nCalcolo {id_caso}: {desc}")

        forze_orizz: dict[int, float] | None = None
        carichi_aggiuntivi_caso: dict[int, list[CaricoAsta]] | None = None

        # Aggiunge carichi Q a LC2..LC7
        if id_caso != "LC1" and carichi_variabili:
            carichi_aggiuntivi_caso = carichi_variabili

        # Forze sismiche
        if id_caso == "LC3" and forze_sismiche:
            forze_orizz = {k: +v for k, v in forze_sismiche.ondulatorio_x.items()}

        elif id_caso == "LC4" and forze_sismiche:
            forze_orizz = {k: -v for k, v in forze_sismiche.ondulatorio_x.items()}

        elif id_caso in ("LC5", "LC6") and forze_sismiche:
            # Sussultorio: aggiunge carichi verticali alle travi
            # F_suss per piano → distribuito sulle travi del piano
            # LC5: +Z (verso l'alto, riduce peso), LC6: -Z (verso il basso, aumenta peso)
            segno = +1.0 if id_caso == "LC5" else -1.0
            carichi_suss: dict[int, list[CaricoAsta]] = {}
            for piano in modello.piani:
                F_z = forze_sismiche.sussultorio_z.get(piano.id_piano, 0.0)
                travi_p = modello.travi_piano(piano.id_piano)
                if not travi_p:
                    continue
                # Distribuisce F_z uniformemente sulle travi del piano
                F_per_trave = F_z * segno / len(travi_p)
                for trave in travi_p:
                    L = modello.lunghezza_asta(trave.id)
                    q_suss = F_per_trave / L if L > 1e-10 else 0.0
                    if trave.id not in carichi_suss:
                        carichi_suss[trave.id] = []
                    carichi_suss[trave.id].append(CaricoAsta(
                        tipo=TipoCarico.DISTRIBUITO_UNIFORME,
                        valore_sx=q_suss,
                        descrizione=f"Sussultorio {id_caso}",
                    ))

            # Unisci con carichi variabili
            if carichi_variabili:
                for id_a, cl in carichi_variabili.items():
                    if id_a in carichi_suss:
                        carichi_suss[id_a] = carichi_suss[id_a] + cl
                    else:
                        carichi_suss[id_a] = cl
            carichi_aggiuntivi_caso = carichi_suss if carichi_suss else carichi_variabili

        # Modello con carichi variabili aggiunti
        modello_caso = _aggiungi_carichi(modello, carichi_aggiuntivi_caso)

        risultato = calcola_caso_carico(
            modello=modello_caso,
            id_caso=id_caso,
            descrizione=desc,
            forze_orizzontali_per_piano=forze_orizz,
            tolleranza=tolleranza,
            max_iter=max_iter,
            n_punti=n_punti,
        )
        risultati[id_caso] = risultato
        passaggi.append(
            f"  {id_caso}: convergenza={risultato.dati_cross.convergenza}, "
            f"iter={risultato.dati_cross.n_iterazioni}"
        )

    # ---- Inviluppo ----
    aste_ids = [a.id for a in modello.aste]
    aste_etichette = {a.id: a.etichetta for a in modello.aste}
    inviluppo = calcola_inviluppo(aste_ids, aste_etichette, risultati, combos)
    passaggi.append(f"\nInviluppo calcolato per {len(inviluppo)} aste")

    return RisultatoCombinazioni(
        zona_sismica=modello.zona_sismica,
        combinazioni_attive=combos,
        risultati_per_caso=risultati,
        inviluppo=inviluppo,
        forze_sismiche=forze_sismiche,
        passaggi=passaggi,
    )


def _aggiungi_carichi(
    modello: ModelloTelaio,
    carichi_extra: dict[int, list[CaricoAsta]] | None,
) -> ModelloTelaio:
    """Crea una copia del modello con carichi extra aggiunti alle aste."""
    if not carichi_extra:
        return modello

    from copy import deepcopy
    aste_nuove = []
    for asta in modello.aste:
        extra = carichi_extra.get(asta.id, [])
        if extra:
            asta_copia = deepcopy(asta)
            asta_copia.carichi = asta_copia.carichi + extra
            aste_nuove.append(asta_copia)
        else:
            aste_nuove.append(asta)

    return ModelloTelaio(
        nome=modello.nome,
        nodi=modello.nodi,
        aste=aste_nuove,
        piani=modello.piani,
        zona_sismica=modello.zona_sismica,
        note=modello.note,
    )
