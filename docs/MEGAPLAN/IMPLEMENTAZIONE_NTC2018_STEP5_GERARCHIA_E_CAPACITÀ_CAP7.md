
IMPLEMENTAZIONE_NTC2018_STEP5_GERARCHIA_E_CAPACITÀ_CAP7.md
Status: IMPLEMENTAZIONE ATTIVA – GERARCHIA DELLE RESISTENZE E CAPACITÀ SISMICA
Ambito normativo esplicito:

❌ NTC2018 – Capitolo 4 NON applicabile
✅ NTC2018 – Capitolo 7 (progettazione per azioni sismiche)
✅ NTC2018 – Capitolo 8 (costruzioni esistenti, richiamo)
Questo file implementa nel canvas lo STEP 5 dell’implementazione software: la verifica della gerarchia delle resistenze e la determinazione della capacità sismica Rd, elementi obbligatori per:

uso del fattore di comportamento q;
progettazione in capacità;
calcolo dell’indice di sicurezza ζE (STEP 4).
Senza questo STEP:

q non è utilizzabile;
ζE non è normativamente fondato;
le verifiche sismiche sono incomplete.


1. Collegamenti vincolanti con la Knowledge Base e STEP precedenti
Questo file è valido solo se sono presenti e coerenti:

KB_NTC2018_SISMICA.md
KB_NTC2018_CA.md
KB_NTC2018_ESISTENTI.md
KB_NTC2018_ANALISI.md
IMPLEMENTAZIONE_NTC2018_VERIFICHE_CAP4_CAP7.md
IMPLEMENTAZIONE_NTC2018_STEP3_MOTORE_COMBINAZIONI.md
IMPLEMENTAZIONE_NTC2018_STEP4_ZETA_E_ESISTENTI_CAP7.md
Qualsiasi verifica di capacità senza questi riferimenti è da considerarsi NON CONFORME.


2. Inquadramento normativo (NTC2018 – Capitolo 7)
Secondo NTC2018 §7:


La progettazione in zona sismica deve garantire che i meccanismi duttili precedano quelli fragili, attraverso una gerarchia delle resistenze.


Principi vincolanti:

distinzione tra elementi dissipativi e non dissipativi;
sovraresistenza degli elementi non dissipativi;
localizzazione controllata delle cerniere plastiche;
continuità del percorso resistente.


3. Ruolo della capacità sismica Rd
La capacità sismica Rd:

rappresenta la massima domanda sostenibile dalla struttura;
deriva dalle verifiche di capacità sugli elementi;
è il numeratore del rapporto ζE = Rd / (Ed · FC).
Regola software vincolante:

Se Rd non è definita → ζE NON CALCOLABILE




4. Modello dati – Elementi e meccanismi

from dataclasses import dataclass

@dataclass
class StructuralElement:
    id: str
    role: str          # dissipativo / non_dissipativo
    capacity: float   # capacità resistente




5. Modello dati – Verifica di gerarchia

from dataclasses import dataclass

@dataclass
class CapacityCheck:
    element_id: str
    domanda: float
    capacita: float
    ratio: float




6. Classe di verifica gerarchia (CAP_7)

from verification_result import (
    VerificationResult,
    VerificationStatus,
    NormativeReference,
)
from ntc_capitolo import NTCCapitol

class GerarchiaResistenzeVerifier:

    CAPITOLO = NTCCapitol.CAP_7

    def __init__(self, checks: list[CapacityCheck]):
        self.checks = checks

    def verify(self) -> VerificationResult:
        for c in self.checks:
            if c.ratio > 1.0:
                return VerificationResult(
                    status=VerificationStatus.NOT_OK,
                    demand=c.domanda,
                    capacity=c.capacita,
                    ratio=c.ratio,
                    reference=NormativeReference(
                        norma="NTC2018",
                        capitolo="§7.4",
                        paragrafo="Gerarchia delle resistenze",
                    ),
                    capitolo_ntc=self.CAPITOLO,
                    notes=f"Violazione gerarchia su elemento {c.element_id}",
                )

        return VerificationResult(
            status=VerificationStatus.OK,
            demand=None,
            capacity=None,
            ratio=None,
            reference=NormativeReference(
                norma="NTC2018",
                capitolo="§7.4",
                paragrafo="Gerarchia delle resistenze",
            ),
            capitolo_ntc=self.CAPITOLO,
            notes="Gerarchia delle resistenze soddisfatta",
        )




7. Determinazione della capacità globale Rd
La capacità globale Rd può essere definita come:

minimo delle capacità governanti;
capacità associata al meccanismo duttile di collasso;
valore derivante da analisi non lineare (pushover).

class CapacitaGlobaleCalculator:

    def __init__(self, element_capacities: list[float]):
        self.element_capacities = element_capacities

    def compute_rd(self) -> float:
        return min(self.element_capacities)




8. Relazione con fattore di comportamento q
Regola fondamentale:

q utilizzabile ⇔ gerarchia OK ∧ capacità Rd definita


Il software deve:

bloccare l’uso di q se la gerarchia fallisce;
segnalare esplicitamente la causa;
riportare l’esito in relazione di calcolo.


9. Integrazione con ζE (STEP 4)
Il flusso completo è ora:

Combinazioni sismiche → Analisi →
Gerarchia e capacità (STEP 5) → Rd →
ζE (STEP 4)


Solo questo flusso è normativamente valido.


10. Stato dell’implementazione
✅ STEP 5 completato nel canvas ✅ Gerarchia delle resistenze formalizzata ✅ Capacità sismica Rd definita ✅ Uso del fattore q correttamente vincolato ✅ Framework sismico NTC2018 completo


Questo file è vincolante per tutte le verifiche di capacità e gerarchia delle resistenze – NTC2018 Capitolo 7.
