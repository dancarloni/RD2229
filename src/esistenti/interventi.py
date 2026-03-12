"""Catalogo interventi di miglioramento/adeguamento sismico.

Fornisce:
- Catalogo di interventi strutturali (preset + estendibile dall'utente)
- Calcolo dello stato post-intervento (riduzione vulnerabilità)
- Combinazione moltiplicativa di interventi multipli con cap normativo
- Ranking per rapporto miglioramento/costo
- Stima costi in doppia modalità (EUR/m² o funzione geometria)

Riferimenti:
- NTC2018 §8.4.3: miglioramento sismico vs adeguamento
- NTC2018 §8.6: interventi sulle strutture esistenti
- Circ. 7/2019 §C8.6: criteri di intervento

Nota: i fattori di miglioramento sono indicativi e basati su letteratura
tecnica (Dolce et al., 2017; RELUIS, 2019). Non sostituiscono una
valutazione strutturale dettagliata.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

_MODULO_LOG = "esistenti.interventi"


# ═══════════════════════════════════════════════════════════
#  Enumerazioni
# ═══════════════════════════════════════════════════════════

class TipoIntervento(str, Enum):
    """Categoria di intervento strutturale."""
    ARMATURA_CA = "armatura_ca"             # c.a.: aggiunta ferri, ringbeam
    INCAMICIATURA = "incamiciatura"         # c.a.: incamiciatura pilastri/travi
    FRP = "frp"                             # compositi FRP (sia c.a. che muratura)
    PARETE_TAGLIO = "parete_taglio"         # c.a.: parete di taglio
    DISSIPATORE = "dissipatore"             # c.a./misto: dissipatori passivi
    RINGBEAM_MUR = "ringbeam_mur"           # muratura: cordolo in c.a.
    INIEZIONI_MUR = "iniezioni"             # muratura: iniezioni di boiacca
    INTONACO_ARMATO = "intonaco_armato"     # muratura: intonaco armato
    CONSOLIDAMENTO_FOND = "consolidamento_fond"  # fondazioni: sottofondazione
    ALTRO = "altro"


class ObiettivoRanking(str, Enum):
    """Obiettivo usato per il ranking degli interventi."""
    MIGLIORAMENTO_MASSIMO = "miglioramento_massimo"
    COSTO_MINIMO = "costo_minimo"
    RAPPORTO_MIGLIORA_COSTO = "rapporto_migliora_costo"   # default


# ═══════════════════════════════════════════════════════════
#  Dataclass Intervento
# ═══════════════════════════════════════════════════════════

@dataclass
class Intervento:
    """Intervento strutturale singolo nel catalogo.

    I fattori di miglioramento si applicano moltiplicativamente
    all'indice di vulnerabilità attuale (ρ o α).

    Esempio:
        fattore_rho = 1.3 → ρ_post = min(ρ_pre × 1.3, cap_rho)
        fattore_alpha = 1.5 → α_post = min(α_pre × 1.5, cap_alpha)
    """
    id: str
    nome: str
    tipo: TipoIntervento

    # Fattori di miglioramento (adimensionali, > 1.0)
    fattore_rho: float = 1.0      # incremento indice ρ c.a. (1.0 = nessun effetto)
    fattore_alpha: float = 1.0    # incremento indice α muratura (1.0 = nessun effetto)

    # Limiti di applicabilità (max ρ o α raggiungibile con questo intervento)
    cap_rho: float = 2.0          # cap massimo ρ post-intervento
    cap_alpha: float = 2.0        # cap massimo α post-intervento

    # Costi
    costo_eur_m2: float = 0.0     # EUR/m² (di area netta intervento)
    # Funzione geometria: costo_fisso + coeff_volume * volume_m3
    costo_fisso_eur: float = 0.0
    coeff_volume: float = 0.0     # EUR/m³

    # Combinabilità con altri interventi
    combinabile: bool = True
    # Cap moltiplicativo globale quando combinato con altri interventi
    cap_combinato_rho: float = 3.0
    cap_combinato_alpha: float = 3.0

    # Riferimento normativo dove applicabile
    riferimento: str = "NTC2018 §8.6"

    # Note tecniche
    note: str = ""

    def stima_costo(
        self,
        area_m2: float = 0.0,
        volume_m3: float = 0.0,
    ) -> float:
        """Stima il costo totale dell'intervento [EUR].

        Uses:
         - costo_eur_m2 × area_m2  (se area_m2 > 0)
         - costo_fisso_eur + coeff_volume × volume_m3  (se volume > 0)
        """
        c1 = self.costo_eur_m2 * area_m2 if area_m2 > 0 else 0.0
        c2 = self.costo_fisso_eur + self.coeff_volume * volume_m3 if volume_m3 > 0 else 0.0
        return max(c1, c2)


# ═══════════════════════════════════════════════════════════
#  Catalogo preset
# ═══════════════════════════════════════════════════════════

CATALOGO_BASE: list[Intervento] = [
    # ── C.A. ──────────────────────────────────────────────
    Intervento(
        id="CA_INCAM_PIL",
        nome="Incamiciatura pilastri in c.a.",
        tipo=TipoIntervento.INCAMICIATURA,
        fattore_rho=1.50,
        fattore_alpha=1.0,
        cap_rho=2.5,
        costo_eur_m2=300.0,
        coeff_volume=250.0,
        riferimento="NTC2018 §8.6.3, RELUIS (2019) Tab. 3.2",
        note="Incremento duttilità e resistenza taglio +30–50%. "
             "Richiede rimozione tramezze adiacenti.",
    ),
    Intervento(
        id="CA_FRP_PIL",
        nome="Confinamento FRP pilastri",
        tipo=TipoIntervento.FRP,
        fattore_rho=1.30,
        fattore_alpha=1.0,
        cap_rho=2.0,
        costo_eur_m2=180.0,
        riferimento="NTC2018 §4.6.2, CNR DT 200 R1/2013",
        note="Aumento duttilità confino. Meno invasivo di incamiciatura.",
    ),
    Intervento(
        id="CA_PARETE_TAGLIO",
        nome="Aggiunta parete di taglio in c.a.",
        tipo=TipoIntervento.PARETE_TAGLIO,
        fattore_rho=1.60,
        fattore_alpha=1.0,
        cap_rho=2.8,
        costo_eur_m2=450.0,
        costo_fisso_eur=5_000.0,
        riferimento="NTC2018 §8.6.3",
        note="Riduce deriva interpiano. Richiede nuove fondazioni.",
    ),
    Intervento(
        id="CA_DISSIPATORI",
        nome="Dissipatori passivi (viscosi/isteretici)",
        tipo=TipoIntervento.DISSIPATORE,
        fattore_rho=1.40,
        fattore_alpha=1.20,
        cap_rho=2.2,
        cap_alpha=1.8,
        costo_eur_m2=0.0,
        costo_fisso_eur=8_000.0,
        coeff_volume=0.0,
        riferimento="NTC2018 §7.10, Dolce et al. (2017)",
        note="Alta efficacia su edifici con periodo naturale intermedio. "
             "Costo per piano (stima).",
    ),
    # ── MURATURA ──────────────────────────────────────────
    Intervento(
        id="MUR_RINGBEAM",
        nome="Cordolo in c.a. sommitale (ringbeam)",
        tipo=TipoIntervento.RINGBEAM_MUR,
        fattore_rho=1.0,
        fattore_alpha=1.50,
        cap_alpha=2.5,
        costo_eur_m2=120.0,
        costo_fisso_eur=2_000.0,
        riferimento="NTC2018 §8.6.1, Circ.7/2019 §C8.6.4",
        note="Riduce ribaltamento fuori piano del 40–60%. "
             "Presuppone ammorsamento delle pareti.",
    ),
    Intervento(
        id="MUR_FRP_FASCIATURA",
        nome="Fasciatura FRP pareti",
        tipo=TipoIntervento.FRP,
        fattore_rho=1.0,
        fattore_alpha=1.35,
        cap_alpha=2.2,
        costo_eur_m2=90.0,
        riferimento="NTC2018 §4.6.2, CNR DT 200 R1/2013",
        note="Incremento resistenza taglio nel piano.",
    ),
    Intervento(
        id="MUR_INIEZIONI",
        nome="Iniezioni di boiacca muratuta",
        tipo=TipoIntervento.INIEZIONI_MUR,
        fattore_rho=1.0,
        fattore_alpha=1.20,
        cap_alpha=1.8,
        costo_eur_m2=60.0,
        riferimento="Circ. 7/2019 §C8.6.1",
        note="Incremento coesione e resistenza a compressione. "
             "Efficace su muratura in cattivo stato.",
    ),
    Intervento(
        id="MUR_INTONACO_ARMATO",
        nome="Intonaco armato con rete d'acciaio",
        tipo=TipoIntervento.INTONACO_ARMATO,
        fattore_rho=1.0,
        fattore_alpha=1.45,
        cap_alpha=2.4,
        costo_eur_m2=110.0,
        riferimento="NTC2018 §8.6.1, Circ. 7/2019 §C8.6.2",
        note="Doppio intonaco armato su entrambe le facce. "
             "Molto efficace ma pesante (aumento massa ~5%).",
    ),
    # ── FONDAZIONI ────────────────────────────────────────
    Intervento(
        id="FOND_CONSOLID",
        nome="Consolidamento fondazioni",
        tipo=TipoIntervento.CONSOLIDAMENTO_FOND,
        fattore_rho=1.10,
        fattore_alpha=1.10,
        cap_rho=1.5,
        cap_alpha=1.5,
        costo_fisso_eur=15_000.0,
        coeff_volume=300.0,
        riferimento="NTC2018 §8.6.4",
        note="Riduzione cedimenti differenziali. Effetto indiretto su vulnerabilità.",
    ),
]


def get_intervento_by_id(intervento_id: str) -> Intervento | None:
    """Cerca un intervento nel catalogo base per ID."""
    for i in CATALOGO_BASE:
        if i.id == intervento_id:
            return i
    return None


# ═══════════════════════════════════════════════════════════
#  Applicazione interventi: stato post
# ═══════════════════════════════════════════════════════════

@dataclass
class ScenarioIntervento:
    """Risultato di uno scenario di intervento su un edificio."""
    interventi_applicati: list[str]        # ID interventi
    rho_pre: float                         # ρ indice vulnerabilità c.a. prima
    rho_post: float                        # ρ dopo intervento
    alpha_pre: float                       # α iniziale muratura
    alpha_post: float                      # α dopo intervento

    delta_rho: float = 0.0                 # variazione assoluta ρ
    delta_alpha: float = 0.0              # variazione assoluta α
    delta_rho_perc: float = 0.0           # variazione % ρ
    delta_alpha_perc: float = 0.0         # variazione % α

    costo_totale_eur: float = 0.0
    cap_raggiunto: bool = False            # se il cap combinato è stato attivato

    note: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "interventi": self.interventi_applicati,
            "rho_pre": round(self.rho_pre, 3),
            "rho_post": round(self.rho_post, 3),
            "alpha_pre": round(self.alpha_pre, 3),
            "alpha_post": round(self.alpha_post, 3),
            "delta_rho_perc": round(self.delta_rho_perc, 1),
            "delta_alpha_perc": round(self.delta_alpha_perc, 1),
            "costo_totale_eur": round(self.costo_totale_eur, 0),
            "cap_raggiunto": self.cap_raggiunto,
            "note": self.note,
        }


def applica_interventi(
    interventi: list[Intervento],
    rho_pre: float,
    alpha_pre: float,
    area_m2: float = 0.0,
    volume_m3: float = 0.0,
) -> ScenarioIntervento:
    """Applica una combinazione di interventi all'edificio.

    Composizione moltiplicativa:
    ρ_post = min(ρ_pre × Π(fattore_rho_i), cap_combinato_rho_max)
    α_post = min(α_pre × Π(fattore_alpha_i), cap_combinato_alpha_max)

    Il cap è il minimo dei cap_combinato tra gli interventi selezionati.

    Args:
        interventi: lista interventi selezionati
        rho_pre: indice ρ c.a. attuale
        alpha_pre: indice α muratura attuale
        area_m2, volume_m3: geometria per stima costi

    Returns:
        ScenarioIntervento con pre/post, variazioni e costo
    """
    note: list[str] = []
    cap_raggiunto = False

    # Prodotto moltiplicativo fattori
    prod_rho = 1.0
    prod_alpha = 1.0
    cap_rho_eff = max((i.cap_combinato_rho for i in interventi), default=3.0)
    cap_alpha_eff = max((i.cap_combinato_alpha for i in interventi), default=3.0)
    costo_totale = 0.0

    non_combinabili = [i for i in interventi if not i.combinabile]
    if len(non_combinabili) > 1:
        note.append(
            "ATTENZIONE: più di un intervento non combinabile selezionato. "
            "Considerare solo quello più efficace."
        )

    for i_int in interventi:
        prod_rho *= i_int.fattore_rho
        prod_alpha *= i_int.fattore_alpha
        # Cap individuale
        if rho_pre * prod_rho > i_int.cap_rho:
            prod_rho = i_int.cap_rho / rho_pre if rho_pre > 0 else 1.0
            cap_raggiunto = True
        if alpha_pre * prod_alpha > i_int.cap_alpha:
            prod_alpha = i_int.cap_alpha / alpha_pre if alpha_pre > 0 else 1.0
            cap_raggiunto = True
        costo_totale += i_int.stima_costo(area_m2, volume_m3)

    rho_post = rho_pre * prod_rho
    alpha_post = alpha_pre * prod_alpha

    # Cap combinato globale
    if rho_post > cap_rho_eff:
        rho_post = cap_rho_eff
        cap_raggiunto = True
        note.append(f"Cap combinato ρ attivato (max {cap_rho_eff:.1f})")
    if alpha_post > cap_alpha_eff:
        alpha_post = cap_alpha_eff
        cap_raggiunto = True
        note.append(f"Cap combinato α attivato (max {cap_alpha_eff:.1f})")

    # Variazioni
    delta_rho = rho_post - rho_pre
    delta_alpha = alpha_post - alpha_pre
    delta_rho_perc = (delta_rho / rho_pre * 100.0) if rho_pre > 0 else 0.0
    delta_alpha_perc = (delta_alpha / alpha_pre * 100.0) if alpha_pre > 0 else 0.0

    return ScenarioIntervento(
        interventi_applicati=[i.id for i in interventi],
        rho_pre=rho_pre,
        rho_post=rho_post,
        alpha_pre=alpha_pre,
        alpha_post=alpha_post,
        delta_rho=delta_rho,
        delta_alpha=delta_alpha,
        delta_rho_perc=delta_rho_perc,
        delta_alpha_perc=delta_alpha_perc,
        costo_totale_eur=costo_totale,
        cap_raggiunto=cap_raggiunto,
        note=note,
    )


# ═══════════════════════════════════════════════════════════
#  Ranking interventi
# ═══════════════════════════════════════════════════════════

@dataclass
class VoceRanking:
    """Voce nel ranking degli interventi."""
    id_intervento: str
    nome: str
    scenario: ScenarioIntervento
    score: float    # punteggio secondo obiettivo selezionato

    def to_dict(self) -> dict[str, Any]:
        return {
            "id_intervento": self.id_intervento,
            "nome": self.nome,
            "score": round(self.score, 3),
            "delta_rho_perc": round(self.scenario.delta_rho_perc, 1),
            "delta_alpha_perc": round(self.scenario.delta_alpha_perc, 1),
            "costo_eur": round(self.scenario.costo_totale_eur, 0),
        }


def _score_intervento(
    scenario: ScenarioIntervento,
    obiettivo: ObiettivoRanking,
) -> float:
    """Calcola il punteggio per il ranking secondo l'obiettivo scelto."""
    migliora = abs(scenario.delta_rho_perc) + abs(scenario.delta_alpha_perc)
    costo = max(scenario.costo_totale_eur, 1.0)

    if obiettivo == ObiettivoRanking.MIGLIORAMENTO_MASSIMO:
        return migliora
    elif obiettivo == ObiettivoRanking.COSTO_MINIMO:
        return -costo  # negativo: ranking du min
    else:  # RAPPORTO_MIGLIORA_COSTO
        return migliora / math.log1p(costo) if costo > 0 else migliora


def ranking_interventi(
    catalogo: list[Intervento],
    rho_pre: float,
    alpha_pre: float,
    obiettivo: ObiettivoRanking = ObiettivoRanking.RAPPORTO_MIGLIORA_COSTO,
    area_m2: float = 0.0,
    volume_m3: float = 0.0,
    top_n: int = 10,
) -> list[VoceRanking]:
    """Valuta ogni intervento del catalogo singolarmente e li ordina.

    Ogni intervento è valutato da solo (scenario unitario), poi ordinato
    secondo l'obiettivo selezionato dall'utente.

    Args:
        catalogo: lista (preset o personalizzata) di Intervento
        rho_pre: indice ρ c.a. attuale
        alpha_pre: indice α muratura attuale
        obiettivo: criterio di ordinamento
        area_m2, volume_m3: geometria per stima costi
        top_n: numero di voci da restituire

    Returns:
        Lista VoceRanking ordinata dal migliore al peggiore
    """
    voci: list[VoceRanking] = []
    for intervento in catalogo:
        scenario = applica_interventi(
            [intervento], rho_pre, alpha_pre, area_m2, volume_m3
        )
        score = _score_intervento(scenario, obiettivo)
        voci.append(VoceRanking(
            id_intervento=intervento.id,
            nome=intervento.nome,
            scenario=scenario,
            score=score,
        ))

    # Ordina dal migliore (score più alto)
    voci.sort(key=lambda v: v.score, reverse=True)
    return voci[:top_n]
